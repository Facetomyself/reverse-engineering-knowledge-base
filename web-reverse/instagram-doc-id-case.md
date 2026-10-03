---
schema_version: 2
id: web-reverse-instagram-doc-id-case
document_type: archive
scope:
  targets:
  - instagram
  client: unknown
  version: unknown
  observed_at: unknown
sources:
- id: s1
  ref: null
  basis: source-report
  citation: '`本地项目分析材料（定位不公开）`（InstagramApis，HEAD 日期 2026-08-18，只读对照）'
  reason: 出处来自原归档来源字段；本地路径已省略，原始材料未随本文公开，本轮未重跑来源实验。
source_completeness: unknown
tags:
- doc_id
- x-ig-app-id
- web_profile_info
- graphql
original_date: '2026-08-18'
archived_date: '2026-09-23'
---

# Instagram 案例：HTML 抽 app_id 与 doc_id

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: `workspace/cv-cat`（InstagramApis，HEAD 日期 2026-08-18，只读对照）
> 原始发布时间: 2026-08-18
> 归档日期: 2026-09-23
> 分类: web-reverse
</details>
>
> 这份对照仓没有本地签名器。用户页 HTML 提供 `user_id`、`app_id` 和首页 GraphQL `doc_id`；后续请求把 `doc_id` 和 Cookie 一起发出。`x-csrftoken` 辅助函数存在，但资料和时间线调用点没有用它。

## 案例：从用户名到时间线

`InstagramAPI.get_info`：

1. GET `https://www.instagram.com/{username}/`，头来自 `get_common_headers()`。
2. 正则取 `"user_id":"..."` 和 `"app_id":"..."`。
3. `get_HomeProfileDocID` 从同一份 HTML 取首页用的 doc id。
4. 返回的 `XIgAppId` 交给 `get_requests_userinfo_headers`，写入 `x-ig-app-id`。
5. 资料接口是 `GET /api/v1/users/web_profile_info/?username=`，带 Cookie。

时间线 `get_user_videos`：

```text
variables = { id: user_id, first: 12, after: cursor }
GET /graphql/query/?doc_id=DocID&variables=json(variables)
headers = get_common_headers()
cookies = caller_cookie
next = data.user.edge_owner_to_timeline_media.page_info.end_cursor
```

成功口径是这条 JSON 路径存在，不是 HTTP 200。`doc_id` 来自当次 HTML，换前端构建后旧 doc_id 会让 `data.user` 缺失。

## csrf 辅助函数没有接上主路径

`ins_utils.py` 另有带 `x-csrftoken` 和 `x-ig-app-id` 的头模板。`get_info`、`get_user_info`、`get_user_videos` 分别调用 `get_common_headers` 或 `get_requests_userinfo_headers`，没有调用那个 csrf 模板。读到 `x-csrftoken` 不能推断当前时间线请求已经在发它。

## 伪代码

```text
html = GET /{username}/
user_id, app_id, home_doc = regex(html)
profile = GET /api/v1/users/web_profile_info/
          header x-ig-app-id = app_id
          cookie = session
page = GET /graphql/query/ ? doc_id=home_doc & variables={id, first, after}
```

## 证据边界

正则依赖页面内嵌 JSON 的键名。Instagram 改用纯客户端渲染后，这份抽取会空。本库没有登录或请求 Instagram，也不收录 sessionid。

<a id="extraction-reference"></a>
## 深度提炼

HTML 中的 `doc_id` / `app_id` 来源、profile-info 请求头映射与 timeline cursor 链路见[Instagram doc_id 请求链参考](./instagram-doc-id-reference.md)。Cookie/session 是来源中记录的请求输入；不能据此推断登录是必要条件。本文及参考均为 source-report，未做站点/runtime/parity/server 验证。

## 提炼说明（736）
retain_existing_reference。既有卡 web-reverse/instagram-doc-id-reference.md。
本轮不另建卡。不复制 Cookie/token/指纹原值。未审图片不作证据。
