---
schema_version: 2
id: collection-engineering-high-concurrency-http-collector-control-plane-procedure
document_type: procedure
scope:
  targets: [high-concurrency HTTP collector control plane]
  client: collection engineering
  version: unknown
  observed_at: unknown
sources:
  - id: control-model
    ref: ./high-concurrency-http-collector-control-plane.md#five-layer-control
    basis: source-report
  - id: recovery
    ref: ./high-concurrency-http-collector-control-plane.md#drain-half-open
    basis: source-report
  - id: capacity
    ref: ./high-concurrency-http-collector-control-plane.md#bounded-recovery-gates
    basis: source-report
modules:
  - name: request-chain
    anchor: steps
    sources: [control-model, recovery]
    basis: source-report
    limits: 只整理身份、连接、节奏、任务寿命和恢复状态的控制关系；并发、代理和容量参数不能直接外推。
  - name: decision-flow
    anchor: steps
    sources: [control-model, recovery, capacity]
    basis: source-report
    limits: drain/cooldown/probe、信号分流和逐 lane 晋级是来源方法，未在本轮运行 outage fixture 或 canary。
  - name: validation
    anchor: acceptance
    sources: [capacity]
    basis: source-report
    limits: 固定窗口、回归、compile、soak 和 server acceptance 均需当前项目另行取得 receipt。
relations:
  - type: derived_from
    target: ./high-concurrency-http-collector-control-plane.md#five-layer-control
tags: [collector, proxy-lease, sticky-session, aimd, deadline, checkpoint, recovery]
---

# 高并发 HTTP 采集控制面流程

本文把 [高并发 HTTP 采集控制面](./high-concurrency-http-collector-control-plane.md) 的五层状态模型整理为可审查流程。重点是让身份、连接、请求节奏、任务寿命和恢复状态各自有边界；本文不是某个站点的并发配置，也不把来源项目的短窗口结果升级为当前目标的容量结论。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 最低内容 | 不足时 |
|---|---|---|
| item 与完成标准 | item 唯一标识、终态集合、有效产物判据和固定观察窗口 | F1；不以进程存活或 requests/s 代替业务完成 |
| route/lease | route identity、SID、Cookie jar、worker owner、预算和健康状态 | F2；不能让身份、Cookie 与 tunnel 跨生命周期混用 |
| 控制面 | 页面/图片等分域 gate、`Retry-After`、AIMD/epoch、request timeout 与 item deadline | F2；不把 `concurrency` 当成全部控制 |
| 恢复材料 | append-only checkpoint、latest-wins 规则、分片策略和 route-policy 记录 | F3；恢复前不得扫描历史 failure 盲目重跑 |
| 观测与回滚 | queue/backlog、有效产出、429/403、连接、storage late operation 和停止条件 | F4；缺窗口数据不晋级 |

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 固化 item、终态、有效产物和固定健康窗口，区分页面、图片/附件及其 gate。 | manifest、outcome 分类、窗口基线。 | 完成标准可观察走 S2；否则 F1。 |
| S2 | 为 worker 分配 lease，把 route/SID、Cookie jar、连接复用策略和预算绑定；独立身份请求禁止旧 tunnel 复用，Sticky 身份保留合法复用。 | lease 状态、连接策略和 owner 记录。 | 生命周期一致走 S3；否则 F2。 |
| S3 | 将 `429`、`403/challenge`、transport error、timeout 和内容 marker 缺失分开分类；用 launch epoch 合并同批 `429`，不对每个迟到响应重复乘法惩罚。 | signal ledger、cooldown、retry budget 和动作记录。 | 反馈语义可追溯走 S4；否则 F2。 |
| S4 | 对 request、item、producer、HTTP、storage 和 remote verify 分别施加 timeout/deadline/queue 上限；记录 late operation，实际返回前不提前归还槽位。 | 队列深度、oldest item、超时和迟到操作计数。 | 所有队列有界走 S5；否则 F3。 |
| S5 | 以 append-only/latest-wins checkpoint 写入和读取；区分中断区间恢复与完成区间补失败，并在启动补采前做 route-policy parity check。 | checkpoint generation、分片、候选扫描和恢复清单。 | 路由策略一致且状态可定位走 S6；否则 F3。 |
| S6 | 连接池故障时停止新请求，等待活动请求归零，关闭旧池，指数冷却，重建 half-open pool，只放行一个真实业务 probe。 | drain 状态、cooldown、probe 结果和 session generation。 | probe 成功进入 S7；失败继续退避并走 F2。 |
| S7 | 一次只增加一个 shard/lane，观察至少两个同步健康窗口，比较有效产出边际增益与风控、连接、调度、存储指标。 | canary/扩容 receipt，包含 stop 条件。 | 有稳定边际增益且未越阈值才继续；否则 F4 或结束。 |
| S8 | 归档脱敏 signal ledger、checkpoint generation、健康窗口和失败出口；把来源方法与当前运行证据分开。 | 可复核的控制面 receipt。 | 证据闭合才报告限定范围；缺项保留 unknown。 |

<a id="outputs"></a>
## 输出

1. 五层控制面状态和 route/lease 生命周期记录。
2. `429`、`403/challenge`、transport、content-invalid 等信号的动作与 cooldown 记录。
3. 分层 deadline、有界队列、late operation 和 checkpoint generation 记录。
4. drain/half-open/probe 的状态迁移和恢复结果。
5. 固定窗口健康指标、扩容/停止决策及失败出口；公开稿不含 Cookie、代理凭据、URL 或请求体。

<a id="acceptance"></a>
## 验收

| 门 | 当前运行必须有的依据 | 不能代替它的东西 |
|---|---|---|
| A1 控制面完整 | identity、connection、rate、lifetime、recovery 五层均有状态与 owner | 只有 worker 数或 `maxInFlight` |
| A2 反馈可归因 | 429/403/transport/content 分流、launch epoch、cooldown 和动作可回溯 | 所有错误统一换 IP + retry |
| A3 恢复可收敛 | drain 等待归零、旧池关闭、cooldown、单 probe 和失败退避均有证据 | rebuild 后立即释放全部 worker |
| A4 状态可恢复 | checkpoint latest-wins、分片、局部查询、两类恢复和 route-policy parity 均有记录 | 扫描历史 failure 文件重跑 |
| A5 容量可晋级 | 固定窗口有效产出有边际增益，且 retry waste、backlog、连接、storage late operation 未越阈值 | requests/s、进程存活或短测通过 |

来源文章中的测试、比例和 evidence 文件只作为 `source-report`；本轮没有新增 collector、fixture、soak、runtime 或 server acceptance，因此 A1–A5 不标记为当前目标已通过。

<a id="failure-exits"></a>
## 失败出口

- **F1：完成标准或材料不足。** 停止启动并补 item、终态、有效产物和窗口定义；不把进程活跃当成业务产出。
- **F2：身份、反馈或连接恢复不一致。** 停止扩大并发，分别检查 lease/Cookie/tunnel、信号分类、epoch、drain 和 probe；没有新证据不盲目换身份重试。
- **F3：队列、deadline 或 checkpoint 不可控。** 停止扩容，保留 oldest item、late operation、checkpoint generation 和 route-policy 差异；先修复可恢复边界。
- **F4：健康窗口没有边际增益。** 停止增加 lane，记录有效产出、风控、连接、调度和存储指标；必要时拆分不重叠 shard，不继续抬高单进程并发。

来源：[高并发 HTTP 采集控制面](./high-concurrency-http-collector-control-plane.md)。本文仅整理 source-report 方法，不复制原始运行日志、代理凭据或目标数据，也不替代 Web 逆向的 browser fact、parity 和 server acceptance 门禁。
