---
schema_version: 2
id: anti-detection-ruyi-20251015-tls-score-boundary-reference
document_type: reference
original_date: '2025-10-15'
archived_date: '2026-07-13'
scope:
  targets: [tls-clienthello-score]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ruyi-20251015-01.md#对tls的迷信--爬虫人员对tls指纹的神话"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留 ClientHello 字段类别和来源对 JA3/JA4、BoringSSL 的说法。不收录指纹样值，也不把 JA4 等式当成定义。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 打分和“只是一票”是来源判断。百分比不是测得权重，没有产品名、阈值或抓包。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 三类选择只保留类别。没有输入、产物、通过条件或失败出口，因此不是 procedure。
relations:
  - type: derived_from
    target: "./ruyi-20251015-01.md#对tls的迷信--爬虫人员对tls指纹的神话"
tags: [TLS, ClientHello, JA3, source-report]
---

# TLS ClientHello 打分边界

这张卡只保留来源对 TLS 指纹组成、它在打分里的位置，以及“在意 TLS 时先选哪一类栈”的说法。它不记录指纹样值，也不把任何一类选择写成可执行步骤。

<a id="parameters"></a>
## ClientHello 字段类别

来源称浏览器发 HTTPS 前先发 ClientHello。它点名的组成是加密套件、TLS 版本、扩展、SNI 和 ALPN。这些字段的组合被它叫做 TLS 指纹或 JA3。下一句把 JA3 重排说成简单固定的 JA4；这是作者断言，本卡不把它写成 JA4 的定义。

来源又称 Chromium 侧特征来自它拼写的 borningssl，一个 UA 对应一个 TLS 指纹，检测是在看二者是否对应。版本和对应关系都没有在本轮核对。原文里的指纹样值不进入本卡。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 载体是 ClientHello | ClientHello | s1 :60 | source-report | 无抓包 |
| C2 | 组成含套件 | cipher suites | s1 :62 | source-report | 无套件清单 |
| C3 | 组成含扩展 | extensions | s1 :66 | source-report | 无扩展编号 |
| C4 | 组成含 SNI | SNI | s1 :68 | source-report | 无域名样值 |
| C5 | 组成含 ALPN | ALPN | s1 :70 | source-report | 无协商结果 |
| C6 | JA4 等式未核对 | JA3重新排序后实际上是简单的JA4（固定） | s1 :73 | source-report | 不是规范定义 |
| C7 | 来源归到 borningssl | borningssl这个项目的特征 | s1 :87 | source-report | 未对照源码 |

<a id="risk-control"></a>
## 一票而不是决定项

来源认为反爬不是看一个字段，而是综合打分，并按 HTTP、网络、行为、页面、上下文举例。它把 TLS 写成权重里的一票，后面的百分比只是修辞，不是测量。

它认为真正露馅的常常是其他层面不一致，例如 TLS 与头部不符、UA 相关的环境信息不符、缺少真人行为。从 DNS 到 Canvas 的“全层一致”同样是来源要求，不是已定位的检查表。开源自动化框架会被检测，也只是这篇文章的判断。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C8 | 来源称为综合打分 | 综合打分系统 | s1 :98 | source-report | 无权重表 |
| C9 | TLS 只是一票 | TLS 只是权重系统中的一票 | s1 :109 | source-report | 百分比不是测量 |
| C10 | 更强调跨层不一致 | 其他层面的不一致 | s1 :112 | source-report | 无产品规则 |

<a id="decision-flow"></a>
## 三类选择，不是流程

来源说如果在意 TLS，可以走真实浏览器堆栈，或走浏览器自动化框架，或在它认为确需自定义 TLS 时使用它点名的模板库。本卡只保留这三类的存在，不记录库的用法、模板或套件。

收束句是不要单点伪造，要么全链路一致，要么直接做浏览器自动化。来源没有定义怎样算一致，也没有失败后改走哪一类的条件，所以这里不是 procedure。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C11 | 第一类是真实浏览器堆栈 | 用真实浏览器堆栈 | s1 :146 | source-report | 无步骤 |
| C12 | 第三类只是条件标题 | 若确需自定义 TLS | s1 :152 | source-report | 不记录模板或调用 |
| C13 | 收束是否定单点伪造 | 不要单点伪造，要全链路一致。或者干脆浏览器自动化。 | s1 :158 | source-report | 无通过条件和失败出口 |

## 验证与限制

没有抓包，没有指名的风控产品，没有服务端结果。指纹样值和库的用法故意不在本卡。作者的成功或封禁解释保持 source-report。
