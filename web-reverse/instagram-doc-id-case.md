# Instagram 案例：HTML 抽 app_id 与 doc_id

> 来源: `workspace/cv-cat`（InstagramApis，HEAD 日期 2026-08-18，只读对照）
> 原始发布时间: 2026-08-18
> 归档日期: 2026-09-23
> 分类: web-reverse
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
