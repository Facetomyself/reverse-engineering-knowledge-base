---
schema_version: 2
id: weixin-mcp-job-plane-reference
document_type: reference
original_date: '2026-07-17'
archived_date: '2026-09-15'
scope:
  targets:
    - weixin MCP job plane
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./headless-mcp-jobs.md#transport"
    basis: source-report
  - id: s2
    ref: "./headless-mcp-jobs.md#job-状态机"
    basis: source-report
  - id: s3
    ref: "./headless-mcp-jobs.md#假成功陷阱必修"
    basis: source-report
  - id: s4
    ref: "./headless-mcp-jobs.md#和文章-claim-的关系"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只整理来源对 stdio、loopback Streamable HTTP 和两类工具的描述。未重跑 client smoke，实现文件未随文公开。
  - name: decision-flow
    anchor: decision-flow
    sources: [s2]
    basis: source-report
    limits: 状态机、owner、heartbeat 和 cooperative cancel 是来源设计。未观察进程重启或丢失 owner 的更新行数。
  - name: validation
    anchor: validation
    sources: [s3, s4]
    basis: source-report
    limits: ok 为假仍标 completed 是来源指出的当前缺陷。typed outcome 是复用门，不是已修好的行为。未重跑下载。
relations:
  - type: derived_from
    target: "./headless-mcp-jobs.md#mcp-job-与文章状态分离"
tags:
  - MCP
  - stdio
  - Streamable HTTP
  - download_jobs
---

# MCP job 与文章 checkpoint 分离

这张卡只回答：headless MCP 的传输、长任务 job 状态机，以及 job 终态为什么不能代替文章 checkpoint。不提供可运行的 server 或下载器。公众号 HTTP 字段、会话平面、高并发代理控制和 NAS 交付不在这张卡里。

来源没有可公开的实现路径。成功与否只到作者自述。进度和 payload 里的秘密不进入本卡。

<a id="interfaces"></a>
## 传输与工具分面

默认单 client 用 stdio，由 client 拉起，不常驻。多个本机 client 共享时用 loopback 上的 Streamable HTTP。来源把远程 bind 放在 authentication 之前拒绝，GUI 和浏览器驱动不作为 MCP 依赖。

> 默认 loopback；远程 bind 在 authentication 之前拒绝

契约沿用官方 Python SDK 的 initialize、tools/list、tools/call。来源要求用真实 client 做 smoke，不要只测函数 import。

工具分成同步短操作和立即返回 job id 的 `start_*_job`。列表、进度、取消属于 job 面，不是文章面。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 多本机 client 共享默认 loopback，远程 bind 在 authentication 之前拒绝 | s1 第 40 行：默认 loopback；远程 bind 在 authentication 之前拒绝 | source-report | weixin MCP job plane | 未重跑绑定 |
| C2 | smoke 要用真实 client，不要只测函数 import | s1 第 43 行：用真实 client 做 smoke，不要只测函数 import。 | source-report | 来源点名的 Python SDK contract | 未执行 smoke |
| C3 | 列表、进度、取消是 job 面，不是文章面 | s1 第 45 行：列表、进度、取消是 job 面，不是文章面。 | source-report | start_*_job 与同步短操作的分面 | 短操作的具体工具名不全 |

<a id="decision-flow"></a>
## Job 状态机

job 使用独立的 `download_jobs` 表，不复用 `article_downloads`。`create_job` 时 sanitize payload。queued 进入 running 时写入 owner_id 和 heartbeat，终态是 completed、failed 或 cancelled。进程重启时，queued、running、cancel_requested 且 heartbeat 过期的行标成 interrupted，并清空 owner。interrupted 不等于自动重放，要另一次 retry 或 start。

后台线程周期性 heartbeat。丢失 owner 的 UPDATE 行数为 0 就停。cancel 必须是 cooperative：分页循环、逐篇循环、退避 sleep 都查 `cancel_check()`，不能只改状态位让下载继续。终态集合是 cancelled、completed、failed、interrupted。不要用线程还活着当成功。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 长任务用独立 download_jobs，不复用文章下载表 | s2 第 58 行：独立 `download_jobs` 表，不要复用 `article_downloads`。 | source-report | 来源的 job 表 | 表结构未对照源码 |
| C5 | cancel 必须在循环和 sleep 里合作检查 | s2 第 61 行：cancel 必须是 cooperative | source-report | 分页、逐篇和退避 sleep | 未观察取消时序 |
| C6 | heartbeat 过期的未终态标 interrupted，且不自动重放 | s2 第 62 行：interrupted ≠ 自动重放；要明确的 retry/start。 | source-report | 重启后的 queued/running/cancel_requested | 未观察重启 |

<a id="validation"></a>
## 假成功与文章 claim

来源写明当前 `_finish(..., "completed", result=result)` 只看 runner 有没有抛异常。因此业务 JSON 里 ok 为假仍是 job completed，`getmsg ret=-3` 变成 0 篇且 job 100%，CLI 结构化失败仍退出码 0。

复用时终态必须由 typed outcome 决定，来源点名 OK、IDEMPOTENT、AUTH_REQUIRED、CONTENT_INVALID、NETWORK_TRANSIENT，并以省略号结尾。Orchestrator 是唯一写 terminal 的组件。进度回调同样 sanitize，禁止把 key 打进 `progress_json`。

取消 job 不能留下永久 in-progress 文章 claim：要么 heartbeat 过期变 stale，要么 cancel 路径显式释放。同一 URL 再次出现应走文章 store 的 already_downloaded，而不是再开一个成功 job 重复写盘。job completed 不是文章 checkpoint。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | 业务 JSON 里 ok 为假仍会被标成 job completed | s3 第 70 行：业务 JSON `{"ok": false}` 仍是 job `completed` | source-report | 来源点名的当前 _finish | 这是缺陷，不是目标行为 |
| C8 | 只有 Orchestrator 可以写 job 终态 | s3 第 74 行：Orchestrator 是唯一写 terminal 的组件 | source-report | CLI、MCP、runner 不得各自解释成功 | 枚举未列全 |
| C9 | 取消 job 不能留下永久 in-progress 文章 claim | s4 第 89 行：取消 job 不能留下永久 in-progress 文章 claim | source-report | heartbeat 过期或 cancel 显式释放 | 文章 store 的实现不在本文 |

## 验证与限制

缺 typed outcome 的完整判定表，缺 authentication 的具体机制，缺公开实现和本轮 smoke。来源把假成功写成尚未修好的现状。不要把 job completed、线程仍在或退出码 0 当成文章已经落盘。
