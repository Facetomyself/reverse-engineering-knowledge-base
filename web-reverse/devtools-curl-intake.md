---
schema_version: 2
id: devtools-curl-intake
document_type: reference
original_date: "2026-10-09"
archived_date: "2026-10-09"
scope:
  targets: [DevTools copy as cURL]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s-shell
    ref: https://github.com/D4Vinci/Scrapling/blob/aa814a77d942678f1a44f68198a0c88550382d28/scrapling/core/shell.py
    basis: static-review
  - id: s-readout
    ref: ../collection-engineering/scrapling-0.4.15-readout.md#curl
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s-shell, s-readout]
    basis: source-report
    limits: 只记录材料边界。上游 shell 有 CurlParser，本仓库没有采用，也没有新写解析器。不执行粘贴的 curl，不含样例头或 Cookie。
relations:
  - type: derived_from
    target: ../collection-engineering/scrapling-0.4.15-readout.md#curl
tags: [devtools, curl, HAR, request-chain, source-report]
---

# DevTools curl 只作为请求形状

这张卡回答：开发者工具里的 “Copy as cURL” 能不能当采集入口。不能。它只是一份请求形状材料。

<a id="request-chain"></a>
## 请求链上的位置

上游 0.4.15 的 shell 含 `CurlParser`。文件注释写明它面向开发者工具复制出的 curl，解析后交给 Fetcher。那是他们的交互壳，不是本仓库的采集器。

本仓库本批没有这个解析器，也不新写一个。HAR 仍是只读材料的主路径。若笔记里留下一条 curl，只登记四项：方法、URL、头、正文。不执行，不补 Cookie，不把它接进 `web_case.py next`。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | shell 内的 CurlParser 面向 DevTools curl，并把结果交给 Fetcher | s-shell | static-review | Scrapling 0.4.15 的 shell | 未运行该解析器 |
| C2 | 本仓库把粘贴的 curl 只当请求形状，不执行；HAR 仍是主材料 | s-readout | source-report | 本仓库采集笔记 | 没有新解析器，不能从这条笔记推出实现 |
