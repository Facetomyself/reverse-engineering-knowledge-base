---
schema_version: 2
id: web-reverse-instagram-doc-id-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [instagram]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./instagram-doc-id-case.md#extraction-reference
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 仅列出来源材料描述的资料与时间线接口；未请求 Instagram 或检查当前页面。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录字段来源与传递位置，不收录实际 doc_id、app_id、Cookie 或游标值。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 只归纳来源报告中的页面提取、请求和分页关系；Cookie 输入不证明登录为必要条件。
relations:
  - type: derived_from
    target: ./instagram-doc-id-case.md#extraction-reference
tags: [doc_id, app_id, web_profile_info, graphql, cursor, source-report]
---

# Instagram doc_id 与 profile timeline 请求链

这张卡归纳来源材料中用户页 HTML 的标识提取、profile-info header 映射及 timeline 游标链路。它与 LinkedIn Voyager 使用不同目标、接口及标识来源，不共享站点结论。

<a id="interfaces"></a>
## 接口

来源报告记录了用户页 HTML、资料查询 `/api/v1/users/web_profile_info/` 与 timeline `/graphql/query/` 三个接口边界。页面与请求结构是来源自述，当前可用性未知。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 资料查询与 timeline 查询是来源中分开的请求路径。 | s1，用户名到时间线章节 | source-report | 来源材料描述的 Instagram Web 路径 | 未核验当前站点或接口行为 |

<a id="parameters"></a>
## 参数来源

- 用户页 HTML 提供来源报告所称的 `user_id`、`app_id` 与首页 `doc_id`。
- `app_id` 经头部构造函数写入 profile-info 请求的 `x-ig-app-id`。
- timeline 使用 `doc_id` 与 `variables`；变量包含用户标识、分页大小和游标位置，响应继续从 `page_info.end_cursor` 取下一页游标。
- 来源记录请求携带 Cookie/session 输入，但没有说明会话建立方式；不能据此推出必须登录。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C2 | 页面提取的 app 标识进入资料请求头，页面 doc_id 与分页变量进入 timeline 请求。 | s1，HTML 提取及 timeline 章节 | source-report | 来源材料所述调用关系 | 未复现字段值、响应或当前前端构建 |

<a id="request-chain"></a>
## 请求链路

```text
GET 用户页
  -> 从 HTML 提取 user_id / app_id / home doc_id
  -> GET /api/v1/users/web_profile_info/
       x-ig-app-id = app_id；Cookie 为调用方输入
  -> GET /graphql/query/?doc_id=...&variables=...
       variables 含 id / first / after
  -> 从 page_info.end_cursor 继续分页
```

来源材料将 JSON 路径 `data.user` 存在作为资料结果口径，而非仅以 HTTP 状态码判断；前端构建变化可能导致旧 `doc_id` 对不上。该成功口径尚未独立复现。

## 验证与限制

来源只报告静态对照材料；未访问目标站点，未运行 runtime、parity 或 server 验收。Cookie/session 是输入记录，不足以得出登录要求、账户状态或会话有效性结论。相关 archive：[Instagram 案例](./instagram-doc-id-case.md#extraction-reference)。
