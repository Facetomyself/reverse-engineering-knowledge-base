---
schema_version: 2
id: ruyi-20260429-genai-assistant-privacy-reference
document_type: reference
original_date: '2026-04-29'
archived_date: '2026-10-02'
scope:
  targets: [genai-browser-assistant]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260429-01.md#二追踪你在私密网站上做的一切它都看到了
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留该文对 9 款 Chrome 助手的架构、表单字段和声明不符的转述。不外推到 Firefox、Edge、Safari，也不记录任何表单内容。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留服务端抓取看不到登录页、跨标签页被写成持久画像、以及两款无画像对照。15 次重复未复核。
relations:
  - type: derived_from
    target: ./ruyi-20260429-01.md#二追踪你在私密网站上做的一切它都看到了
tags: [genai-browser-assistant, source-report]
---

# GenAI 浏览器助手隐私审计的来源边界

这篇卡检索的是：该文转述的 9 款助手里，哪些收集行为被写成和隐私声明不符，以及服务端抓取和跨标签页画像各自停在哪里。不收录审计抓包步骤，也不收录任何页面内容。

<a id="risk-control"></a>
## 收集面与声明

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 架构：8/9的插件使用服务端响应架构 | s1，源文件第 66 行 | source-report | 文中 Table 1 的 9 款 | 唯一客户端例外只在后文点名，未复现 |
| C2 | 表单字段：Merlin是唯一一个会提取表单input字段内容的插件。 | s1，源文件第 102 行 | source-report | 该文 20 个站点上的 9 款 | 不记录字段内容 |
| C3 | 声明原文：我们不收集你访问的网站或内容 | s1，源文件第 210 行 | source-report | 合规表里的 Monica 一行 | 同一行还写实际仍在抓取网页内容 |
| C4 | 实际行为：在几乎所有公共和私人站点抓取网页内容 | s1，源文件第 210 行 | source-report | 合规表里的 Monica 一行 | 站点名单不在本卡 |
| C5 | Shadow DOM 边界：missed capturing shadow elements from DOM | s1，源文件第 236 行 | source-report | 该文点名使用 Shadow DOM 的站点 | 不是通用隔离证明 |

<a id="decision-flow"></a>
## 来源写下的停点

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 登录页：如果页面需要登录才能看到（私人空间），服务端根本抓不到内容 | s1，源文件第 134 行 | source-report | 该文对 Perplexity 服务端抓取的描述 | 不外推到会读 DOM 的助手 |
| C7 | 跨标签页：存储在服务端的持久化用户画像中 | s1，源文件第 194 行 | source-report | Monica 与 Sider 的来源判断 | 没有服务端存储证据 |
| C8 | 阴性对照：Perplexity和TinaMind在所有场景中都没有展示任何画像或个性化行为。 | s1，源文件第 196 行 | source-report | 该文的搜索、浏览、总结和跨标签页场景 | 极端画像设计，推广有限 |

## 验证与限制

`genai-browser-assistant` 的 risk-control 与 decision-flow、以及 `browser-extension` 和 `chrome-extension` 的 risk-control，查询均为 0。第六节的抓包方法和扩展检测没有输出、验收和失败出口，不建流程。引言里的具体页面内容不进入本卡。所有行为描述保持 source-report。
