# 高并发 HTTP 采集控制面：代理租约、AIMD 与故障恢复

> 来源: `workspace/psa`
> 原始发布时间: 2026-08-02
> 归档日期: 2026-08-02
> 分类: collection-engineering
>
> 从一个真实异步采集器中提炼代理身份生命周期、连接池复用、自适应限速、分层 deadline、checkpoint 与容量晋级门。重点不是复制某个站点的并发数字，而是解释高并发系统为什么会“进程还活着，产物却不再增长”，以及控制面如何收敛。

## 结论先行

生产采集器至少要同时控制五类状态：

1. **逻辑身份**：代理 route、SID、Cookie 与目标站会话。
2. **传输连接**：CONNECT、TLS、HTTP keep-alive 与客户端 connection pool。
3. **请求节奏**：目标域级 gate、`Retry-After`、AIMD 与 jitter。
4. **任务寿命**：单请求 timeout、单 item deadline、retry budget 与有界队列。
5. **恢复状态**：append-only checkpoint、分片、latest-wins 与局部补采。

把这五层揉成一个 `concurrency` 参数，系统短测可能很快，长跑通常会以连接堆积、重试风暴、错误身份轮换或 checkpoint 膨胀收场。

## 证据与版本边界

本文来自 `workspace/psa` 的 Git 历史、当前工作树、测试与脱敏 evidence：

- Git 已提交到 `v0.3.4`：可恢复采集、AIMD、streaming、Windows 并发门禁、连接池 drain/rebuild 与 half-open。
- 当前 `v0.4.0` 工作树继续实现：worker-scoped Sticky lease、SID 级 Cookie 隔离、congestion epoch、item deadline、有界存储 executor 与 supervisor recovery。
- `v0.3.5` 之后的设计在提取时尚未形成独立 release commit，因此本文称其为“当前工作树已验证设计”，不伪装成已发布版本历史。
- 文中比例来自同区间 A/B 或固定增量窗口，只用于证明机制方向，不是跨目标可直接套用的容量参数。

## 调试时间线：每次提速都先推翻一个错误假设

这套控制面不是先画架构图再一次性实现的。它是在真实运行中，按“症状 -> 可证伪假设 -> 最小改动 -> 对照验证”逐步长出来的。下面保留关键节点，避免把最终设计倒灌成一开始就知道答案。

| 时间 | 现象与被推翻的假设 | 修复与验证 | 留下的主线约束 |
|---|---|---|---|
| 2026-07-29 上午 | `concurrency=4` 的 500 SN 基线只有 `22.01 SN/min`。界面上长时间没有新图片，不等于 worker 停住：其中存在连续 `not_found` 段。 | 把页面与 CloudFront 图片拆成独立 gate，加入 live progress；同区间 `concurrency=20` 达到 `102.91 SN/min`，终态失败仍为 0。 | 产物数不能单独代表活性；每次状态必须同时展示 processed SN、状态分布、请求速率和队列/worker。 |
| 2026-07-29 下午 | 高并发下多个 worker 同时原子替换同一 `progress.json`，Windows 出现 `WinError 5`。网络仍通，状态却会被并发写击穿。 | worker 进度写与 heartbeat 写共用异步锁，并加入高频并发写回归测试。 | 对同一状态文件，`os.replace` 原子不等于多写者安全；写路径必须串行化。 |
| 2026-07-29 晚 | 双进程 `c220` 下，要求连续成功才恢复 AIMD 的策略被乱序完成的孤立失败长期钉在低速。 | 改成 success credit：成功完成累计恢复额度，只有真正拥塞调整才清空。5 分钟窗口从 `1,390.2` 提升到 `2,270.8 SN/min`。 | 并发反馈必须按事件语义建模，不能用“连续成功”这种隐含串行假设。 |
| 2026-07-29 晚 | Cliproxy 持续 `503` 时，drain-and-rebuild 本身会形成 reset storm；供应商恢复后旧 session 仍可能持续 transport failure。 | 连接池 reset 后指数冷却，采用一个 half-open probe；成功才放行全部 worker，失败继续退避。真实恢复路径和并发 fixture 都通过。 | circuit 不能只有 `open/close`；必须有冷却、单探针和等待者释放语义。 |
| 2026-07-30 | 单请求切换 SID 时，长生命周期 session 仍缓存失效 tunnel。进程活着、gate 正常，但两条 shard 分别积累 `1,163` 和 `1,466` 条 `ESTABLISHED` 连接。 | 独立 SID 模式设置 `CURLOPT_FORBID_REUSE`；本地 500 请求 fixture 的 retained connection 从 `182` 降至 `0`。Sticky pool 保留合法复用。 | session 生命周期和连接生命周期不是一回事，连接复用必须服从 route identity。 |
| 2026-07-30 | 同一批并发启动的请求同时返回 `429`，若每个响应都乘法惩罚，会把一个拥塞事件放大成长期过度退避。 | `wait()` 返回 launch epoch；只有该 epoch 的首个 `429` 调整 AIMD，迟到的同 epoch 响应只延长 cooldown。稳态窗口中 `1,700` 个 `429` 仅触发 `325` 次 penalty。 | 反馈必须携带“请求何时启动”的上下文，不能只看“响应现在到了什么”。 |

上述数据分别见 `workspace/psa/evidence/performance-research.json`、`sustained-concurrency-validation.json`、`outage-half-open-validation.json`、`proxy-connection-cache-validation.json`、`rate-limit-epoch-validation.json` 和 `sticky-pool-403-validation.json`。原始运行日志不进入 Git；这些脱敏 evidence 保留参数、摘要、hash 和结论边界。

### 从成功实验进入主线的准入清单

当前实现不该再用“并发数更大”作为合并理由。只有下列链路共同存在，才能把本案例当作主线能力：

1. `client.py`：长生命周期 `AsyncSession`、连接池 drain/rebuild、half-open、SID 与 Cookie/连接复用一致性。
2. `limiter.py`：页面与图片独立 gate、AIMD、`Retry-After` 与 congestion epoch coalescing。
3. `runner.py`：有界 item queue、单 item deadline、定向图片重试、progress/heartbeat 单写者。
4. `storage.py`：独立有界 storage executor；排队超时和操作超时分开统计，迟到 syscall 不提前归还槽位。
5. `production_supervisor.py`：一次只扩一个 lane，并以多个健康窗口、吞吐增量、mirror backlog 和 failure signal 共同决定扩缩容。

合并前必须同时通过单元/fixture 回归、`compileall`、`git diff --check`，并在目标环境完成固定窗口 canary。测试通过只证明控制逻辑没有回归；10 小时 100 万 SN 的完整长期产能仍需要独立 soak receipt，不能用短窗口线性外推冒充完成。

## 控制面总览

```text
target manifest
    |
    v
bounded item queue -----> worker pool -------------------------------+
                            |                                        |
                            +--> page gate ----+                      |
                            |                  |                      |
                            +--> image gate ---+--> long HTTP session |
                                                   |                 |
proxy lease <--> SID-scoped cookies <--> connection reuse policy     |
                                                   |                 |
                                                   v                 |
                                          parser / validator         |
                                                   |                 |
                                                   v                 |
                                         storage + checkpoint <------+
```

这里有三个经常被混淆的旋钮：

| 控制项 | 限制什么 | 不能替代什么 |
|---|---|---|
| worker 数 | 同时处理多少 item | 目标域请求速率 |
| request gate | 请求启动节奏与拥塞恢复 | 卡死 item 的最终回收 |
| deadline | 单请求或单 item 最长寿命 | 公平调度与容量控制 |

## 代理不是 URL，而是有生命周期的 lease

一个可用的代理 lease 至少应包含：

```text
lease = {
  route_identity,
  session_id,
  cookie_jar,
  worker_owner,
  created_at,
  request_budget,
  health_score,
  consecutive_blocks,
  consecutive_transport_errors
}
```

### 身份、Cookie 与连接必须同生命周期

| 场景 | SID / route | Cookie | CONNECT / TLS |
|---|---|---|---|
| 有状态 Sticky worker | 一个 worker 在预算内复用 | 按 SID 隔离并有界保存 | 允许复用 |
| 无状态、每请求独立身份 | 每次请求变化 | 不跨身份共享 | transfer 完成后关闭无复用价值的 tunnel |
| 直连 | 无代理身份 | 按业务会话管理 | 正常 keep-alive |

长生命周期 HTTP session 与“所有连接都永远复用”不是一回事。客户端 session 可以长寿，但当每次请求的代理用户名或 SID 都变化时，旧 tunnel 已经没有合法复用路径；若仍留在 multi-handle connection cache，中高并发下会积累大量 `ESTABLISHED` 连接。项目的本地 fixture 中，500 个独立身份请求在默认复用策略下曾保留 182 条连接，按 transfer 禁止复用后降为 0。

反过来，Sticky pool 若也一刀切关闭连接，会丢掉合法的 CONNECT/TLS 复用，增加握手成本并破坏会话稳定性。因此连接策略必须服从 route identity，而不是按“用了代理”这个布尔值统一处理。

### 不要第一次 `403` 就换身份

在绑定 IP、Cookie 与连接上下文的目标上，第一次 `403` 可能发生在会话冷启动、挑战同步或单个请求异常阶段。立即换 SID 会丢掉刚建立的上下文，并把短暂问题放大成持续抖动。

更稳的策略是失败迟滞：

```python
if status == 429:
    gate.on_congestion(retry_after)
elif status == 403:
    lease.consecutive_blocks += 1
    if lease.consecutive_blocks >= block_threshold:
        retire(lease)
elif transport_error:
    lease.consecutive_transport_errors += 1
    if lease.consecutive_transport_errors >= transport_threshold:
        retire(lease)
else:
    lease.mark_success()
```

PSA 的同区间 A/B 中，worker Sticky lease 相比“每次重试都换身份”让 `403` 与 retry 都下降约九成，终态失败从非零降到零。这个结果证明的是**会话一致性优于盲目轮换**，不是证明某个固定阈值适用于所有站点。

## 把 `429`、`403` 和 transport error 分开反馈

| 信号 | 更可能属于 | 默认动作 |
|---|---|---|
| `429` | 目标容量或速率拥塞 | 尊重 `Retry-After`，调整 gate；不直接判坏 lease |
| `403` / challenge | route、会话或目标风控 | 保留首次失败上下文，连续失败才轮换 lease |
| connect / TLS / timeout | 供应商、线路或连接池 | 请求级 retry；连续达到阈值才触发 session circuit |
| 内容 marker 缺失 | 业务响应不完整或软阻断 | 进入 parser/validator 失败分类，不冒充 HTTP 成功 |

如果所有失败都走“换 IP + 重试”，系统无法判断到底是目标拥塞、身份失效还是 connection pool 已坏，最终只会更快地烧代理流量。

## 分域 gate 与 AIMD

页面域和图片/CDN 域通常具有不同延迟、限速与错误面，应使用独立 gate。一个通用 gate 需要记录：

- 当前启动间隔、最小/最大间隔；
- 成功恢复额度；
- 连续失败与滑动失败率；
- cooldown 截止时间；
- EWMA latency；
- congestion epoch 与被合并的旧 epoch `429` 数。

### 为什么恢复额度不能要求严格连续成功

高并发响应天然乱序。若一个孤立失败把全部成功进度清零，处于最大退避的 gate 可能长期无法恢复，即使绝大多数请求已经成功。

更合理的是累计成功额度：达到阈值后做一次加性恢复；只有真正再次触发拥塞时，才清空恢复额度。

### 同一批 `429` 只能惩罚一次

假设 50 个请求在 interval 尚未调高前同时发出，它们随后陆续返回 `429`。若每个响应都再次乘法扩大 interval，同一个拥塞事件会被重复惩罚几十次。

解决办法是在请求启动时携带 epoch：

```python
launch_epoch = await gate.wait()
response = await request()

if response.status == 429:
    if launch_epoch < gate.congestion_epoch:
        gate.extend_cooldown_only(retry_after)
        gate.coalesced_rate_limits += 1
    else:
        gate.multiply_interval()
        gate.congestion_epoch += 1
```

真实固定窗口中，约八成 `429` 被识别为旧 epoch 响应并合并，避免了重复乘法惩罚；它们仍参与计数并延长 cooldown，没有被静默丢弃。

## 连接池故障恢复：drain，再 half-open

长生命周期 session 是正常路径，但供应商短时故障后，既有 connection pool 可能不再自愈。正确恢复顺序是：

```text
closed
  |
  v
stop new acquisitions
  |
  v
wait active requests == 0
  |
  v
close old pool
  |
  v
exponential cooldown
  |
  v
build new pool in half-open
  |
  v
allow exactly one real probe
  | success                 | failure
  v                         v
open                    close and back off again
```

关键约束：

- 先封住新请求，再等待旧请求退出，避免两代 socket 重叠。
- rebuild 后不能立刻放开全部 worker，否则持续供应商故障会形成 reset storm。
- half-open 使用真实业务请求，而不是只测 IP echo；探针成功才恢复批量。
- HTTP 已到达目标并返回 4xx/5xx 时，不应误记成纯 transport error。

## timeout、deadline 与有界背压

### 两层 deadline

| 层级 | 包围范围 | 失败后做什么 |
|---|---|---|
| request hard timeout | 一次真实 HTTP 请求 | 释放连接/worker 占用，进入对应阶段 retry |
| item deadline | resume、gate、页面、图片、存储、checkpoint | 写入当前 stage 与已有 evidence，终止本 item |

只给 libcurl 设置 timeout 不够：item 还可能卡在 gate、resume 校验、图片聚合或文件系统调用。反过来，request hard timeout 也不应包含 gate 等待，否则正常限速会被误判成网络失败。

### 每个队列都要有界

- producer queue：防止 manifest 一次性压满内存；
- HTTP clients：受进程 FD 与运行时 selector 能力限制；
- storage executor：区分排队 timeout 与操作 timeout；
- remote verify executor：不能抢占本地热写槽位。

不可取消的内核 syscall 在调用方 timeout 后仍可能继续执行。此时不能提前释放 slot，否则“有界 executor”会被迟到任务悄悄突破。应把它记为 late operation，等实际返回后再释放槽位。

## checkpoint 与两类恢复

生产 checkpoint 的最低契约：

- append-only，读取时同一 item 采用 latest-wins；
- 写入前修复尾部半行，append 后 `fsync`；
- 大范围按绝对 ID bucket 分 shard；
- 少量补采先做 bytes candidate scan，只解析命中行；
- `ok`、`filtered_out` 等恢复状态必须带与当前规则匹配的签名或输出证据。

恢复任务要区分两种语义：

1. **中断区间恢复**：正常 resume 跳过已有终态，处理从未写 checkpoint 的空洞，并重试最新失败。
2. **完成区间补失败**：只选择当前 latest 状态仍为 failed 的 item；历史失败若已被后续终态覆盖，不再入队。

把两者都实现成“扫描历史 failure 文件重跑”会重复消费流量，也会破坏 latest-wins 的权威状态。

恢复配置还必须显式固化当前的路由策略，尤其是页面与图片/附件是否使用同一代理。不要让 recovery 从历史模板隐式继承旧值；主链与恢复链的路由不一致时，网络错误很容易被写成新的业务失败。启动补采前应做 route-policy parity check，不一致就停止，而不是批量消耗 retry budget。

## 容量晋级门

不要从低并发直接跳到目标峰值。每次只增加一个 shard/lane，并至少观察两个同步健康窗口：

| 维度 | 必看指标 |
|---|---|
| 产出 | scanned/min、valid products/min、产出率 |
| 风控 | `429`、`403`、challenge、retry waste |
| 连接 | active requests、FD、TCP、session reset/half-open |
| 调度 | queue depth、oldest item、no-progress duration |
| 存储 | active/wait、queue timeout、operation timeout、late completion |

只有新增 lane 带来稳定边际增益且没有把 timeout、backlog 或失败率推过阈值，才继续扩容。worker 翻倍但有效产物不增，说明瓶颈不在 worker 数，继续加只会增加成本。

单进程的 selector/FD 上限也必须实测。达到运行时上限后，正确做法是拆成目标不重叠、状态文件隔离的 shard 进程，而不是继续抬高单进程并发。

## 常见反模式

| 反模式 | 后果 | 替代方案 |
|---|---|---|
| 每次请求创建 session | 无连接复用、握手成本高 | 一个长生命周期 session |
| 所有代理请求都 keep-alive | 独立 route 的旧 tunnel 堆积 | 连接策略服从 route identity |
| 第一次 `403` 就换 SID | 丢失 Cookie/IP 上下文，放大挑战 | 连续阈值 + score/age/budget |
| 每个并发 `429` 都乘法惩罚 | 同一拥塞事件被重复处罚 | launch epoch 合并 |
| rebuild 后立即放开 worker | reset storm | drain + cooldown + single probe |
| 只设置请求 timeout | item 卡在 gate/storage | 增加端到端 item deadline |
| 只看进程存活或 requests/s | 假吞吐 | 以有效产物固定窗口增量验收 |
| 一味抬单进程并发 | FD/selector 崩溃 | 不重叠 shard + 状态隔离 |

## 外部交叉检查

本地结论与以下开源证据方向一致，但外部项目不替代本地 A/B：

- [`curl_cffi` issue #338](https://github.com/lexiforest/curl_cffi/issues/338)：Windows selector/FD 上限相关故障。
- [`curl_cffi` issue #641](https://github.com/lexiforest/curl_cffi/issues/641)：AsyncCurl multi handle 与长生命周期 session 的连接池语义。
- [`curl_cffi` issue #308](https://github.com/lexiforest/curl_cffi/issues/308)：代理用户名变化与连接复用问题。
- [`Crawlee AutoscaledPool`](https://github.com/apify/crawlee/blob/master/packages/core/src/autoscaling/autoscaled_pool.ts)：按运行状态调节并发的成熟实现入口。

## 项目证据索引

| 主题 | PSA 证据 |
|---|---|
| 长 session、hard timeout、connection policy、circuit | `src/psa_crawler/client.py`、`tests/test_client.py` |
| AIMD、success credit、congestion epoch | `src/psa_crawler/limiter.py`、`tests/test_limiter.py` |
| worker Sticky lease 与反馈轮换 | `src/psa_crawler/proxy.py`、`tests/test_proxy.py` |
| item deadline、retry budget、bounded queue | `src/psa_crawler/runner.py`、`tests/test_runner.py` |
| checkpoint 分片与局部查询 | `src/psa_crawler/checkpoint.py`、`tests/test_checkpoint.py` |
| 脱敏运行时验证 | `evidence/high-concurrency-validation.json`、`evidence/sticky-pool-403-validation.json`、`evidence/rate-limit-epoch-validation.json` |

## 反哺 Web 逆向主线：已有边界与下一步强化点

PSA 的实现不能原样搬进逆向平台。采集器管理的是明确的下载 item，而 Web 逆向首先要守住证据、参数谱系和浏览器/本地 parity。两者可复用的是**控制面原则**，不是某个并发参数。

当前 `reverse_ENV` 的 Web 主线已经具备了最关键的一层：`risk-control-plan.v1` 把 account、client-owned cookie jar、sticky route、连接策略和 checkpoint owner 绑定为 lease；`risk-control-receipt.v1` 要求从单 lease、单 lane、单 in-flight canary 起步；`risk_control.py` 对 `rate_limited`、`challenge`、`blocked`、`contract_drift`、`session_expired` 与 `transport` 给出不同动作。这个边界是对的，尤其避免了把浏览器态偷渡给 HTTP client，或者碰到一个错误就自动横跳账号/出口。

要继续强化，优先级应是下面三项，而不是继续提高 `maxInFlight`：

1. **把 governor 变成有状态的运行期 receipt。** 现有 `risk_control.py` 是确定性的单次决策器，输入的 `inFlight`、`healthyWindows` 和 signal 来自调用方。后续应在 case 内持续记录 lane 的 launch epoch、`Retry-After`、cooldown 截止时间、half-open 状态和 checkpoint generation，让一次 `429` burst 能像 PSA 一样合并，而不是让外部调用方各自解释。
2. **把固定窗口健康指标写入 receipt。** 当前 receipt 能证明 canary 的 lane/lease/action，但不足以解释“进程还活着、产物却不增长”。建议后续版本增加脱敏计数：有效响应数、terminal outcome、retry waste、queue/backlog、oldest active、session reset、active connection/FD 与 storage late operation。只存计数和 evidence pointer，不存 Cookie、URL、请求体或代理凭据。
3. **把信号的并发语义保留下来。** 单个 dominant signal 适合给出即时动作，却会压扁同一窗口的 `rate_limited + transport`、`content_invalid + contract_drift` 等组合。运行期 ledger 应保留窗口内各信号计数、first/last occurrence 与采取的动作；全局 stop 仍按最高优先级执行，但诊断不能丢失次要信号。

这三项属于 Web `scaled-collection` 的后续 contract/runtime 演进，前提仍是 RequestShape、参数三层验证、RuyiTrace/V8Trace facts 与 vanilla client gate 已完成。它们不应反向降低普通分析 case 的门槛，也不把分析阶段变成批量采集器。

## 快速检查表

- [ ] proxy SID、Cookie jar 和 tunnel 复用策略一致。
- [ ] `429`、`403`、transport error 进入不同反馈路径。
- [ ] 页面与图片/附件使用独立 gate。
- [ ] 同批 `429` 不会重复乘法惩罚。
- [ ] session reset 会 drain，并通过 single probe 离开 half-open。
- [ ] request timeout 与 item deadline 分层。
- [ ] producer、HTTP、storage、remote verify 均有界且可观测。
- [ ] checkpoint append-only、latest-wins、可分片、可局部查询。
- [ ] 扩容以固定窗口有效产物和边际增益验收。
