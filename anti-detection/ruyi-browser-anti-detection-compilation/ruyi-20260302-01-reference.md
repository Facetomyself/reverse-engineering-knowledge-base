---
schema_version: 2
id: ruyi-20260302-imss-tracking-reference
document_type: reference
original_date: '2026-03-02'
archived_date: '2026-07-13'
scope:
  targets: [imss-tracking]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260302-01.md#2-指纹追踪远超cookie追踪
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留指纹相对第三方 Cookie 的比例、三条理由、广告网络间接合规，以及指纹计数分不清单站采集和跨站系统。不抄站点、分析标识或关键词表。
relations:
  - type: derived_from
    target: ./ruyi-20260302-01.md#2-指纹追踪远超cookie追踪
tags: [imss, fingerprint, source-report]
---

# IMSS 上指纹追踪相对 Cookie 的来源边界

这张卡只回答：来源为什么说盗版流媒体站更依赖指纹而不是第三方 Cookie，以及它所说的“指纹追踪”实际量到哪一层。它不提供站点名单或识别分类器。

<a id="risk-control"></a>
## 追踪边界

来源报告指纹追踪覆盖 66-93% 的 IMSS 站点，第三方 Cookie 为 38-49%。三条理由是：Cookie 可被清除，域名一换 Cookie 就失效而指纹无状态，以及主流浏览器还没有默认阻止指纹、Firefox 的 Canvas 随机化只覆盖 Canvas。EU 观测点追踪器更少被写成广告网络的间接合规，不是站点自己遵守法规。计数方法停在名单加 API 调用，分不清单次 Canvas 采集和跨站系统。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源写「使用指纹追踪的IMSS站点：66-93%」 | s1，ruyi-20260302-01.md:84 | source-report | 来源的七个观测点 | 不是本次测量；计数定义见 C7 |
| C2 | 来源写「使用第三方Cookie追踪的IMSS站点：38-49%」 | s1，ruyi-20260302-01.md:85 | source-report | 与 C1 同一组观测点 | 不是本次测量 |
| C3 | 来源写「第一，Cookie可以被用户清除，指纹不能。」 | s1，ruyi-20260302-01.md:92 | source-report | 来源给出的第一条理由 | 未区分清除与分区存储 |
| C4 | 来源写「Cookie绑定在域名上，域名一换Cookie就失效了。指纹是无状态的，不受域名更换影响。」 | s1，ruyi-20260302-01.md:95 | source-report | 来源给出的第二条理由 | 不展开重定向域名 |
| C5 | 来源写「但指纹追踪目前没有被任何主流浏览器默认阻止（Firefox的Canvas随机化是例外，但只覆盖Canvas一种指纹技术）。」 | s1，ruyi-20260302-01.md:98 | source-report | 来源对默认防护的边界 | 无浏览器版本 |
| C6 | 来源写「这是一种"间接合规"效应：法规不是直接约束了IMSS，而是通过约束广告网络间接影响了IMSS的追踪行为。」 | s1，ruyi-20260302-01.md:115 | source-report | 来源对 EU 差异的解释 | 来源写明没有因果推断 |
| C7 | 来源写「这个方法无法区分"采集了一个Canvas指纹"和"部署了完整的跨站指纹追踪系统"」 | s1，ruyi-20260302-01.md:203 | source-report | 来源自己的指纹计数 | 名单版本不在正文里 |

## 验证与限制

关键词、DOM 模式和人工验证只有示例，recall 与 precision 不能复现成分类器，所以不建 decision-flow。第五节没有验收和失败出口，不升为流程。Cloudflare 占比和广告标识不是这张卡的模块。`fingerprint-overview.md` 与 `canvas-webgl.md` 的 risk-control 只覆盖宿主对象，不覆盖上述测量边界。
