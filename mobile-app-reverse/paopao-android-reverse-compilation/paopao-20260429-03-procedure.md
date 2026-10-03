---
schema_version: 2
id: unidbg-production-emulator-pool-procedure
document_type: procedure
original_date: '2026-04-29'
archived_date: '2026-10-02'
scope:
  targets: [unidbg-production-emulator-pool]
  client: Android
  version: source names Commons Pool 2.10+ and 2.12+ setters; unidbg revision unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./paopao-20260429-03.md#unidbg学习笔记十九生产化
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 只保留来源给出的隔离、借还和销毁顺序。倍数、事故内存和 100 个 case 都是作者自述，本轮未运行。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 池大小、内存分档、淘汰次数和 JVM 旗标是来源经验值，不是本轮测得的容量。
  - name: validation
    anchor: acceptance
    sources: [s1]
    basis: source-report
    limits: 验收口径来自来源的对照要求和告警示例。本轮没有压测、RSS 曲线或后端对照。
relations:
  - type: derived_from
    target: ./paopao-20260429-03.md#unidbg学习笔记十九生产化
tags: [unidbg, android-emulator, object-pool, dynarmic, source-report]
---

# Unidbg 生产服务：模拟器实例池与销毁边界

这份流程回答：来源如何把单次 Unidbg 调用收成可替换的实例池，以及哪些失败必须销毁实例而不是归还。它不还原某一条签名，也不把作者写下的倍数或事故数字当成已复核结果。来源是 [Unidbg 生产化归档](./paopao-20260429-03.md#unidbg学习笔记十九生产化)。

已有 unidbg 卡片分别覆盖 APK 签名数组和哈希明文扫描，目标都不是这个实例池。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 来源要求 | 不足时 |
|---|---|---|
| 并发模型 | `AndroidEmulator  ** 不是线程安全的  **`，所以 `每个并发请求必须用独立的 emulator 实例` | 继续共用一个实例则停止，不把偶发串结果当成业务 bug |
| 流量形态 | 全局锁只被来源留在 PoC，或每天调用很少的内部工具 | 对外或要吃满多核时，锁不是生产终点 |
| 后端 | 分析阶段留 Unicorn2；生产切 Dynarmic 之前必须同一批输入对照 | 对照不齐走 F1 |
| 内存账户 | `MaxDirectMemorySize` `约束不了 Unicorn/Dynarmic 通过 JNI 调到 native 层` 的 `malloc` / `mmap` | 只按堆上限报容量走 F3 |

<a id="parameters"></a>
## 参数口径

来源的池大小写法是 `池大小 = min(物理 CPU 数 x 2, 物理内存 GB / 单实例内存)`。它给的单实例量级是小 SO 100-200 MB、中 SO 200-500 MB、大 SO 500 MB-1 GB，并提醒先按公式再看 P99，不要把池子直接加到很大。

ThreadLocal 被否定的原因包括 `如果用 Tomcat 默认 200 线程池，你就有 200 个 emulator`。对象池被写成 `生产环境的标准方案`。按需创建被留在极低频率。

Dynarmic 相对 Unicorn2 的速度、以及 CodeHook、Trace、断点不可用，都是来源转述。切换条件是 `全对上才能上线`。淘汰经验值来源写成大约 1000-5000 次调用；复合判据表里的 2 倍 RSS、1000 次和最近 10 次里 3 次异常是示例阈值。`registerEmuCountHook(100000)` 只出现在来源点名的样例文件，不是通用验收常数。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 每个并发调用使用独立 emulator。不用一把全局锁冒充生产并发 | 来源写明线程不安全，以及独立实例是硬约束 | 只是演示或极低流量可停在锁上；否则走 S2 |
| S2 | 用固定上限的对象池，启动时预热并跑一次调用。不把 ThreadLocal 或每次新建当生产默认 | `生产环境的标准方案`；ThreadLocal 不能封顶总数 | 池能借还后走 S3 |
| S3 | 分析留 Unicorn2。切 Dynarmic 前用同一批 case 对照 | `全对上才能上线` | 不一致走 F1 |
| S4 | 借出时做已知输入校验；异常路径 `invalidateObject` 后把引用置空，避免 finally 再次归还 | `invalidateObject  ` 之后要把  ` e  ` 设为 null | 仍会归还坏实例走 F2 |
| S5 | 容器限额计入堆外模拟内存；glibc 链接的 backend 库不放在纯 musl 镜像里硬加载 | `Alpine 用 musl libc`；堆加直接内存顶满限额时 `K8s 会把你 OOMKilled` | 余量或 libc 不满足走 F3 |
| S6 | 同时看借还差、进程 RSS 和延迟告警 | `借出 1000 次 + 归还 990 次`；`P99 > 200ms 报警` | 借还差不回落走 F2；RSS 在堆稳定时仍上涨走 F3 |

<a id="outputs"></a>
## 输出

交付的是来源所描述的池化服务形态：实例 `短寿命的、可替换的、健康可监测的`，外加借还差、空闲数、堆、直接内存和进程 RSS 这些它点名的指标。不交付某条签名的计算结果，也不交付已经压测通过的容量数字。

<a id="acceptance"></a>
## 验收

1. 来源要求切换 Dynarmic 前，Unicorn2 与 Dynarmic 跑同一批 case，`全对上才能上线`。本轮没有这批 case。
2. 借出次数与归还次数的差要能解释。来源把 `借出 1000 次 + 归还 990 次` 当作泄漏信号，而不是成功。
3. 进程 RSS 不能只靠 JVM 堆来判健康。来源写明 NMT 看不到 Unicorn/Dynarmic 经 JNI 拿走的内存。
4. `P99 > 200ms 报警` 是来源表里的示例阈值，不是本卡测得的服务等级。

<a id="failure-exits"></a>
## 失败出口

F1：后端对照不齐，或异常后仍把实例放回池子。来源的事故结论是 `抛异常的实例必须销毁，不能归还`。停止切换或停止复用该实例。

F2：调用卡住。`future.cancel(true)` `不能真正打断卡在 native 层的 Unicorn`，此时立刻 `close` 可能打挂进程。来源把真正停住模拟的位置写成指令计数钩子触发 `emu_stop()`。在这条路径落地之前，不把超时取消写成已经回收。借不到实例时来源的等待上限示例是 `2 秒等不到实例就放弃`，返回空，而不是把请求堆进全局锁。

F3：容器限额没有给 native 留余量、镜像 libc 不匹配，或直接内存的清理把 Full GC 打成尖峰。`Alpine 用 musl libc` 对不上来源所说的 glibc 预编译库时，停止在该镜像上声称 backend 已加载。容量数字停止外推。
