---
schema_version: 2
id: generic-spider-vs-bounded-collector
document_type: reference
original_date: "2026-10-09"
archived_date: "2026-10-09"
scope:
  targets: [Scrapling Spider]
  client: python
  version: "0.4.15"
  observed_at: unknown
sources:
  - id: s-spider
    ref: https://github.com/D4Vinci/Scrapling/blob/aa814a77d942678f1a44f68198a0c88550382d28/scrapling/spiders/spider.py
    basis: static-review
  - id: s-engine
    ref: https://github.com/D4Vinci/Scrapling/blob/aa814a77d942678f1a44f68198a0c88550382d28/scrapling/spiders/engine.py
    basis: static-review
  - id: s-readout
    ref: ./scrapling-0.4.15-readout.md#spider
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s-spider, s-engine, s-readout]
    basis: static-review
    limits: 只核对 0.4.15 的类默认值和阻塞重试分支。没有跑 Spider。407 记 transport、444 记 blocked 是本仓库既有信号，不是上游 is_blocked 的返回值。
relations:
  - type: derived_from
    target: ./scrapling-0.4.15-readout.md#spider
tags: [Scrapling, spider, risk-control, AIMD, static-review]
---

# 通用 Spider 与有界采集器

这张卡用来防止把 Scrapling Spider 的类默认值当成采集器合同。

<a id="risk-control"></a>
## 风控与并发边界

| 项 | 0.4.15 源码 | 本仓库采集器 |
|---|---|---|
| 全局并发 | `concurrent_requests = 4` | 有 `maxItems`；刻度默认关，直到单独的 AIMD 门 |
| 每域并发 | 默认 `0`，引擎只在该值非 0 时建每域限制 | 不靠这个默认值 |
| 下载间隔 | `download_delay = 0.0` | `minDelaySec` 不低于 0.2 |
| 会话 | 无 `oneSession` 合同 | `oneSession` |
| 页数 | 浏览器 `max_pages` 是 1–50 的标签页池；另有模板自己的页计数 | `maxPages` 是采集页上限 |
| robots | 默认 `robots_txt_obey = False` | 不把这个默认值引进来 |
| 阻塞 | `BLOCKED_CODES` 含 401、403、407、429、444 和 500、502、503、504；`is_blocked` 为真后，在次数小于默认 3 时重试同一请求 | 不收这三次重试 |
| 407 | 落在 `BLOCKED_CODES` | 记 `transport`，代理认证失败 |
| 444 | 落在 `BLOCKED_CODES` | 记 `blocked`，连接被关闭 |
| 缓存 | `development_mode` 打开且未给目录时使用 `.scrapling_cache/<name>` | 不写这个目录 |
| 自适应节流 | AutoThrottle 默认关闭，起始延迟 5 秒，上限 60 秒 | 不把它当成 AIMD 门 |

`retry_blocked_request` 默认把原请求返回去。源码没有把它实现成“换一个 IP”。429、challenge 和代理认证失败继续分开记，不要并进同一次换 IP 重试。

已有信号名保持为 `rate_limited`、`challenge`、`blocked`、`session_expired`、`contract_drift`、`transport`、`content_invalid`。本卡不新增 407 或 444 这两个信号名。
