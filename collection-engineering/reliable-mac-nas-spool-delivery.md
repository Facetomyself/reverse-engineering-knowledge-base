# Mac 热写与 NAS 交付：可重放 spool、mirror ACK 和非侵入式运维

> 来源: `workspace/psa`
> 原始发布时间: 2026-08-02
> 归档日期: 2026-08-02
> 分类: collection-engineering
>
> 提炼长时间采集任务在 Mac worker 与 NAS durability tier 之间的可靠交付模式：本地 SSD 热写、不可变 marker、SSH tar staging、幂等 ACK、灰度 GC、supervisor 完成门和低成本巡检，并明确它目前保证的是进程崩溃可重放，而不是目录事务或断电级 durability。

## 为什么 NAS 不应进入采集热路径

远程文件系统的平均延迟可能不高，但尾延迟、挂载阻塞和不可取消 syscall 会直接占住采集 worker。并发越高，远程存储越容易从“慢一点”演变成全局背压源。

PSA 的生产拓扑把职责拆成三层：

| 层 | 权威内容 | 不应承担 |
|---|---|---|
| 开发仓库 | 源码、测试、部署模板、脱敏 evidence | 生产进度与真实输出 |
| Mac worker | 活 checkpoint、进程状态、本地 SSD spool、mirror queue | 长期产品归档 |
| NAS | 已提交产品输出 | HTTP 热路径与任务调度 |

核心原则是：**采集成功不等待 NAS 热写，但交付完成必须有 NAS receipt。**

## 数据流

```text
collector
  |
  | put_many(front, back, metadata)
  v
local SSD spool
  |
  | fsync file + replace
  v
immutable pending marker
  |
  | batch files-from
  v
SSH tar -> NAS staging
  |
  | per-file replace into final root
  v
claim pending marker -> queue/gc
  |
  +--> optional local deletion
  |
  +--> append idempotent ACK + fsync
  |
  +--> remove GC marker
```

collector、mirror 与 GC 是三个独立故障域。解析器和 HTTP client 只依赖 `StorageBackend`，不知道 NAS、SSH 或 queue 细节。

## 热写路径：批量输出后再生成 marker

一个产品通常包含多个文件。正确顺序是：

```text
write all local outputs
    -> create immutable marker containing batch_id / keys / size / hash
    -> append success checkpoint
```

marker 必须在完整输出批次写完之后生成；checkpoint 又必须在 marker 成功生成之后写 `status=ok`。这样普通进程崩溃时：

- 输出未完成：没有 marker，也没有成功 checkpoint；下次重新处理。
- 输出完成但 marker 未生成：没有成功 checkpoint；下次校验/重写。
- marker 已生成但 checkpoint 未写：mirror 可继续交付；collector 下次通过本地输出或 receipt 恢复。
- checkpoint 已写：marker 已存在，正常 mirror 可重放。

单文件落地采用同目录临时文件、`fsync` 与 `os.replace`，避免读到半写文件；同名异内容默认应报冲突，不能静默覆盖。

### 已验证边界

`put_many()` 不是跨文件原子事务。多个文件会逐个完成；只有 marker 表示“这一批本地输出已完整”。此外，当前 marker 与输出 rename 后没有对父目录执行 `fsync`，所以已验证的是**普通进程崩溃后的重放**，不是断电或文件系统崩溃后的目录项持久性保证。

要升级为更强的 power-loss guarantee，需要在 rename 后 `fsync` 父目录，并加入 fault-injection 与断电恢复测试。

## 有界存储 executor

同步文件系统调用通过独立 daemon thread executor 执行，而不是占用 asyncio 默认 executor。每次操作分两个 timeout：

| 指标 | 含义 |
|---|---|
| queue timeout | 等不到 storage slot |
| operation timeout | 已进入线程/内核，但迟迟未返回 |
| late completion | 调用方已超时，底层后来成功 |
| late failure | 调用方已超时，底层后来失败 |

operation timeout 后，底层 syscall 未必能取消。slot 必须等真实调用结束才释放，否则固定并发会被 late task 突破。daemon worker 的作用是让永久挂死的 syscall 不阻止解释器退出，不是让它失去资源计数。

本地 spool 与 NAS resume fallback 应使用不同 executor。远端校验只给极少槽位，即使 NAS 变慢，也不能吃掉本地热写容量。

## mirror：at-least-once 传输，幂等效果

### 传输与提交

mirror 从 pending markers 选择有界批次，生成去重后的文件清单，然后：

1. 在 NAS 创建唯一 staging 目录。
2. 通过一个 tar stream 批量上传。
3. 在 NAS 本机把 staging 文件逐个 `os.replace` 到最终路径。
4. 远端步骤成功后，才把对应 pending marker 原子移动到 `queue/gc/`。

传输失败时 pending marker 保留，下次重放。由于同一批可能重复传输，协议是 **at-least-once**；通过稳定 key、原子 replace 与 `batch_id` ACK 去重得到幂等效果，不应称为 exactly-once。

### GC 与 ACK 顺序

```text
pending marker
    |
    | remote commit success
    v
GC marker
    |
    | optional safe local delete
    v
append ACK(batch_id) + fsync
    |
    v
remove GC marker
```

这个顺序让每个 crash window 都可重放：

| 崩溃点 | 重启后行为 |
|---|---|
| 上传前/中 | pending 仍在，重新上传 |
| 远端成功、claim 前 | pending 仍在，允许重复提交 |
| claim 后、GC 前 | GC marker 仍在，继续 finalize |
| 本地删除后、ACK 前 | GC marker 仍在，缺失文件按已删处理并补 ACK |
| ACK 后、marker 删除前 | `batch_id` 去重，不重复写 receipt，再删 marker |

ACK 文件采用 append-only JSONL；读取时忽略或修复尾部半行，写入后 `fsync`。receipt 应包含输出 key、size 与 hash，供 resume 快速判断，但是否真正重算远端 hash 要单独说明。

### 安全删除门禁

即时本地 GC 默认应关闭，并按 managed lane 灰度。删除前至少检查：

- 目标 key 未被任何 pending marker 引用；
- 路径没有越过 spool root；
- 中间路径不是 symlink；
- 目标是普通文件；
- 文件 mtime 不晚于当前 marker，避免删掉后续重写内容；
- 远端提交和 ACK 状态满足当前 lane 的完成门。

## 三层 resume

恢复一个历史成功项时，按成本从低到高检查：

1. 本地 spool 文件；
2. 本地 mirror receipt/ACK；
3. 有界 NAS exact-path 校验。

NAS 校验 timeout 不能把旧 `status=ok` 覆盖成 failed。更准确的状态是 `resume_verify_deferred`：历史成功仍保留，当前只是暂时无法完成远端复核。

## supervisor 的 block 完成门

长期任务由唯一 allocator 分配不重叠 block。领取顺序必须是：

```text
check active ranges / checkpoint
    -> atomically persist allocation
    -> generate isolated config/state paths
    -> start mirror
    -> start collector
```

每个 block 独立保存 config、progress、summary、log、failure、spool、mirror queue/status/ACK 与代理前缀。collector 崩溃只能在同一 config 上有界重启，不能跳到下一块再回来补洞。

完成不等于 collector 进程退出。至少要同时满足：

- collector progress 为 completed；
- pending、GC、invalid marker 都为 0；
- 本 block receipt 覆盖已入队产品；
- mirror 已排空并可安全停止。

随后才能清理该 block 的本地 spool，并领取下一块。

watchdog 应基于 progress/heartbeat 新鲜度，而不是只看 PID。启动后长期没有 progress 或 heartbeat 过期时，先优雅发送中断，宽限后仍存活才 kill；恢复仍使用原 block 和 checkpoint。

## 非侵入式巡检

### 活跃任务发现

历史 supervisor state 可能遗漏手工恢复或已重新接管的 lane。日常巡检应从新鲜 `progress.json` heartbeat 发现当前 active running block，并逐 lane 报告范围与进度。

### 收据计数不是 NAS 总库存

低成本巡检可以汇总当前新鲜 running block 的 mirror receipts，但它只表示**巡检范围内已收据的产品**：

- 不包含旧 completed block；
- 可能漏掉 completed-but-draining 或 quarantined mirror；
- 不能代替 NAS 全量 inventory。

字段名应明确写成 scoped receipt count，不能模糊称为“NAS 总商品数”。

### bounded tail + exact path

质量抽检应读取每 lane 有界 ACK tail，从 receipt 中取少量确定 key，再让 NAS 只 `stat` 这些精确路径。日常不遍历 NAS 根目录；全量 census 只能显式、低频执行。

如果远端只做 `stat`、非空与普通文件检查，就只能声称 existence/size smoke。ACK 中存在 SHA-256 字段不等于已经重算了 NAS 文件 hash。

## Mac 推送与服务交接

### 通用目录同步不是生产发布器

常见的 `tar + scp + extract` 项目同步脚本通常具有这些语义：

- 直接解包到既有目录；
- 不删除远端旧文件；
- 可能只排除 `.git`、build 等通用目录；
- 未必排除 `.env`、state、logs、downloads、spool、captures。

因此它适合新建临时 checkout，不适合覆盖正在运行的 stateful production root。后者会混合旧代码、覆盖运行文件，甚至把本机历史状态推到生产节点。

### 分级交付

| 等级 | 适用 | 边界 |
|---|---|---|
| L0 只读巡检 | 查询 progress/ACK | 不传文件，不发信号 |
| L1 单工具更新 | 更新纯只读 inspector | 只传精确脚本，离线校验；不重启 collector |
| L2 有限任务 | 一次性 backfill/audit | 唯一 job dir、PID、stdout/stderr、独立 runtime |
| L3 持久服务 | supervisor/collector | 独立 release/staging、配置外置、`launchd` 接管、heartbeat 回读 |

有限任务可用 `caffeinate -i` 与 job 日志跨 SSH 断线运行；持久服务必须交给 `launchd`。SSH shell、GUI session 与 `launchd` 环境不同，不能因为 SSH 命令成功就假设服务环境、Keychain 或挂载一致。

一个更安全的 L3 切换顺序是：

1. 只读记录当前 heartbeat、active ranges、pending/GC/invalid 与 receipt 水位。
2. 把代码上传到唯一 staging/release 目录，禁止覆盖 live runtime。
3. 校验配置、plist 与离线 `check`；不把 secret 写进 plist。
4. 精确确认旧 allocator 优雅退出，并让 mirror 有机会排空。
5. 由 `launchctl` 接管新服务。
6. 回读新 state、heartbeat、active ranges 与 mirror health。
7. 未通过时回到旧 release；不要复用被部分覆盖的 live checkout。

state owner root 与 code release root 应分离：前者稳定持有 checkpoint、queue、spool 与 live config，后者只承载可切换代码。服务升级只改变执行根，不搬动状态；如果重启后应继续同一任务，release 路径也不应进入 immutable job fingerprint。

PSA 已验证 LaunchAgent、绝对路径、`caffeinate` 与 heartbeat 接管流程；“versioned atomic release + 自动回滚”仍是建议方案，不能标成现有已验证能力。

## 当前 durability 边界与待补强项

| 项 | 当前边界 | 建议 |
|---|---|---|
| NAS 原子性 | 逐文件 `os.replace`，不是目录事务 | 用完成 marker 隔离读者，或引入目录级发布协议 |
| 断电一致性 | 未做本地/远端目录 `fsync` | rename 后 fsync parent，补 fault-injection |
| staging 清理 | finalize 失败可能留下孤儿 staging | 增加带年龄/owner 的 sweep |
| mirror lock | `mkdir` 锁可能在 SIGKILL 后残留 | 记录 PID/boot identity，验证后回收 stale lock |
| NAS 冲突 | 远端 replace 可能覆盖异内容同名文件 | 提交前校验 size/hash，冲突进入 quarantine |
| 完成覆盖 | 计数比较可能被旧 ACK 掩盖 | 持久化 expected batch-id ledger，做集合覆盖 |
| 质量抽检 | exact-path stat，不重算 hash | 增加小样本远端 SHA 验证 |
| inventory | active-running scoped receipts | completed ledger 或显式低频 census |

## 项目证据索引

| 主题 | PSA 证据 |
|---|---|
| 存储抽象、有界 executor、spool marker | `src/psa_crawler/storage.py`、`tests/test_storage.py` |
| marker claim、ACK、GC crash windows | `scripts/mirror_spool_gc.py`、`tests/test_mirror_spool_gc.py` |
| SSH tar staging 与远端提交 | `scripts/mirror_spool_to_nas.zsh` |
| block 分配、watchdog、完成门、lane 隔离 | `scripts/production_supervisor.py`、`tests/test_production_supervisor.py` |
| 只读 active discovery 与 bounded audit | `scripts/production_inspect.py`、`tests/test_production_inspect.py` |
| 脱敏运行时验证 | `evidence/item-deadline-storage-validation.json`、`evidence/spool-ssh-mirror-validation.json` |

## 快速检查表

- [ ] 开发仓库、worker runtime、NAS 输出的权威边界明确。
- [ ] 远程存储不占采集热写槽位。
- [ ] 完整本地批次后才生成不可变 marker，marker 后才写成功 checkpoint。
- [ ] mirror 是有界批次，失败保留可重放状态。
- [ ] ACK 按 `batch_id` 幂等，尾部半行可修复。
- [ ] 本地 GC 在 remote commit 与 receipt 后，且有路径/mtime/symlink 防护。
- [ ] supervisor 先持久化 block，再启动进程；完成门覆盖 mirror drain。
- [ ] 日常巡检使用新鲜 heartbeat、bounded ACK tail 与 exact-path NAS smoke。
- [ ] 通用同步脚本不覆盖运行中的 production root。
- [ ] 文档明确 process-crash、power-loss、逐文件原子与目录事务的区别。
