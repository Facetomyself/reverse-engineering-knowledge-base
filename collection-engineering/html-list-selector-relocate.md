---
schema_version: 2
id: html-list-selector-relocate
document_type: procedure
original_date: "2026-10-09"
archived_date: "2026-10-09"
scope:
  targets: [HTML list selector]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./scrapling-0.4.15-readout.md#relocate
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 只覆盖业务体已是 HTML 列表、且一行已有业务读回之后的选择器维护。阈值 75、body SHA-256 和失败即停是本仓库合同，不是 Scrapling 的默认 40。未对活页做 runtime、local-parity 或 server-accepted。
relations:
  - type: derived_from
    target: ./scrapling-0.4.15-readout.md#relocate
tags: [html-list, relocate, replay-frozen, decision-flow, source-report]
---

# HTML 列表选择器重定位

这份流程只处理一件事：业务响应体是 HTML，列表行已经有过一次业务读回，之后页面结构变了，或者有人要改选择器、改指纹。它不抓页面，不启动浏览器，也不把解析命中写成服务端接受。

工具是本仓库的 `tools/web-reverse/html_fingerprint.py`。不要 import Scrapling，不要写 `elements_storage.db` 或 `.scrapling_cache`。

<a id="prerequisites"></a>
## 前提与输入

必须已经有：一次业务读回通过的样例行、该次响应的原始字节、当时捕获的元素指纹（含 `body_sha256`）、以及请求所要求的字段集。响应体不是 HTML，或还没有任何一行被业务读回证明，就停在 F1。未知的字段集不能当成“列已经够”。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 在已读回的那一行上 `capture`，绑定当时的响应体字节 | 指纹字典，含 `body_sha256` | 字节和元素都在，走 S2；否则 F1 |
| S2 | 选择器或指纹要变更时，先对原响应字节 `replay_frozen` | `hit`、`miss` 或 `body-drift` | `hit` 才走 S3；`body-drift` 或 `miss` 走 F2，不进 `collector_canary` |
| S3 | 结构变化的新响应体上 `relocate`，阈值 75 | `hit` 且只含并列最高分，或 `below-threshold` / `empty` 且 `matches` 为空 | `hit` 只是解析候选，走 S4；低于阈值不采纳 top score，走 F3 |
| S4 | 用请求字段集核对候选列 | 列齐全，或列薄 | 列齐全才可以进入既有 canary 门；列薄走 F4，记 `content_invalid` |
| S5 | 仅当 S1 的那一行已有业务读回时，才 `find_similar` | 除源节点外、分数不低于 75 的节点 | 每个命中单独走 S4；没有读回就不要调用 |

`relocate` 的 `hit` 不是 `serverAccepted`。`find_similar` 不代替逐行字段核对。

<a id="outputs"></a>
## 输出

交付四样记录：捕获指纹和 `body_sha256`、`replay_frozen` 的状态、`relocate` 或 `find_similar` 的状态与 `matches`、字段集核对结果。不要交付“服务端已接受”或“可以放量”。

<a id="acceptance"></a>
## 验收

通过必须同时看到：指纹绑在捕获时的字节哈希上；选择器或指纹变更有一次原字节上的 `replay_frozen` `hit`；活页结构变化时阈值是 75，低于阈值的 `matches` 为空；相似节点搜索发生在一行业务读回之后；薄列记 `content_invalid`。编辑这篇文章或单测本地夹具，都不代替目标站的 canary。

<a id="failure-exits"></a>
## 失败出口

F1：没有原始字节，或没有一行业务读回。停止重定位，先补读回。

F2：`replay_frozen` 为 `body-drift` 或 `miss`。冻结体已不是这版选择器的依据。不要进 `collector_canary`，不要用新字节凑合打分。

F3：`relocate` 为 `below-threshold` 或 `empty`。不要收下最高分节点，不要把阈值降到上游的 40 来凑命中。

F4：候选列薄于请求字段集。记 `content_invalid`，不要写成 `serverAccepted`。
