---
schema_version: 2
id: web-reverse-linkedin-voyager-request-chain
document_type: reference
archived_date: '2026-10-01'
scope:
  targets: [linkedin]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./linkedin-voyager-csrf-case.md#案例资料卡
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅整理未公开本地对照材料的来源报告；原始来源未随库公开，本稿未取当前页面或请求验证。版本、观察时间、完整查询参数和响应行为未知。
relations:
  - type: derived_from
    target: ./linkedin-voyager-csrf-case.md#案例资料卡
  - type: derived_from
    target: ./linkedin-voyager-csrf-case.md#可复用点
  - type: supplements
    target: ./session-binding-double-write.md#双写对照
tags: [linkedin, voyager, graphql, queryid]
---

# LinkedIn Voyager 资料卡 GraphQL 请求链

本文把 `linkedin-voyager-csrf-case.md` 的来源报告整理成可检索的目标请求链，不代表当前 LinkedIn 页面或服务已由本库验证。原报告指向未公开的 `LinkedinApis` 本地对照材料；原始材料未随库公开。文中引用的 `2026-08-18` 是对照仓 HEAD 日期，不是观测时间或目标版本。

<a id="request-chain"></a>
## 资料卡请求链

按来源报告，调用方先带已有登录态请求资料页 HTML/JS；随后按卡片类型定位页面中的 GraphQL query 定义，并从对应定义抽取 `id` 作为 `queryId`。资料卡与 top card 对应不同定义，不能把一个 `queryId` 套用到另一张卡片。之后请求 Voyager GraphQL 路由，query 包含已编码的 URN 或 `vanityName` 和该卡片的 `queryId`。来源还报告请求头包含 `csrf-token`；其会话材料映射统一见[会话材料双写对照](./session-binding-double-write.md#双写对照)，本文不复述字段变换。

```text
profile_js = GET profile page with existing login session
query_id = extract_define_id(profile_js, card_name)
GET /voyager/api/graphql?variables=(...)&queryId=query_id
```

这段仅表示来源报告中的顺序；`variables=(...)` 是省略占位符，不是实际参数或完整请求。来源称页面发布变化可能带来不同 `queryId`，其做法是从当前页面 JS 提取，而非在客户端固定旧值；这仍只是来源材料的做法，不是当前前端行为保证。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 先取资料页 HTML/JS，再按卡片对应的 define 区域抽取 `queryId`；资料卡和 top card 的定义不同。 | s1，来源归档“案例：资料卡”45-46 行：“1. 带着登录 Cookie 取资料页 HTML/JS。”；“2. 用正则从 `define("graphql-queries/queries/profile/...")` 附近抽出 `id:"..."`，作为 `queryId`。资料卡和 top card 是两段不同的 define，不能共用一个 queryId。” | source-report | 未公开对照材料所述的 Voyager 资料卡流程 | 未取得原始 JS、queryId 值或匹配样本；当前页面结构未知。 |
| C2 | 来源报告的 GraphQL 请求在 query 中带卡片对应的 `queryId` 与已编码的 URN 或 `vanityName`；请求头带 `csrf-token`。 | s1，来源归档“案例：资料卡”47-48 行。 | source-report | 同一来源报告的资料卡请求 | 不含完整变量 schema、完整头字段、响应或服务端接受证据；Cookie/header 映射见补充文档，不在此复写。 |
| C3 | 来源伪代码按“取页面、按卡片抽 queryId、请求 GraphQL”排列，并把请求 query 中的 `queryId` 接到抽取结果。 | s1，来源归档“案例：资料卡”51-52、54 行。 | source-report | 仅为来源材料描述的调用顺序 | 示例有省略项，不是可直接重放的请求；未提供完整变量、编码细节、错误处理或响应解析。 |
| C4 | 来源报告称 `queryId` 会随前端发布变化，并描述从当时页面 JS 提取，而不是固定写入客户端。 | s1，来源归档“可复用点”61 行。 | source-report | 仅限该对照材料记载的客户端做法 | 未检查当前站点构建、query 定义或兼容行为；变化频率和失败表现未经独立验证。 |

## 证据边界

- `basis` 为 `source-report`：原始对照材料未公开，本稿没有检查其源码、访问 LinkedIn、捕获请求或验证服务端响应。
- 目标版本、客户端版本和 `observed_at` 均未知；引用日期不代表运行时观测。
- query 的完整 `variables` 结构、必需头集合、响应/错误 schema、登录会话建立及生命周期均未知；因此不建立 `parameters`、`validation` 或 `procedure` 模块。
- 本文不对独立签名算法是否存在作当前服务结论，也不推导风控或服务端接受状态。
- 正文不含真实 Cookie、会话或 `queryId` 值。
