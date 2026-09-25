# 领英案例：JSESSIONID 双写与页面 queryId

> 来源: `workspace/cv-cat`（LinkedinApis，HEAD 日期 2026-08-18，只读对照）
> 原始发布时间: 2026-08-18
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> 领英 Voyager 在这份对照仓里没有独立签名算法。鉴权是 Cookie 里的 `JSESSIONID` 去掉引号后双写到 `csrf-token`，GraphQL 的 `queryId` 从当前页面 JS 里抠。

## 案例：资料卡

`builder/header.py` 把 `auth.cookie["JSESSIONID"]` 去掉双引号，写入 `csrf-token`。`link_apis.py` 在另一处用正则 `JSESSIONID="..."` 从 Cookie 串提取同一值。两条路径都是双写，不是哈希。

页面流程：

1. 带着登录 Cookie 取资料页 HTML/JS。
2. 用正则从 `define("graphql-queries/queries/profile/...")` 附近抽出 `id:"..."`，作为 `queryId`。资料卡和 top card 是两段不同的 define，不能共用一个 queryId。
3. 请求 `https://www.linkedin.com/voyager/api/graphql`，query 里是已编码的 URN 或 `vanityName`，加上刚抽出的 `queryId`。
4. 头里带 `csrf-token`。缺 `JSESSIONID` 时正则或字典访问会失败，这是登录态缺失，不是 GraphQL 字段算错。

```text
js = GET profile page with cookie
query_id = extract_define_id(js, card_name)
headers["csrf-token"] = strip_quotes(cookie["JSESSIONID"])
GET /voyager/api/graphql?variables=(...)&queryId=query_id
```

`static/Linkein.js` 的文件名拼写是 Linkein。若 Python 路径没有 compile 它，就不能把这个文件当成现行 csrf 算法。csrf 的现行来源是 Cookie。

## 可复用点

Voyager 的 `queryId` 会随前端发布变化。把它写死在客户端里，页面一更新就 4xx。每次从当前 JS 提取，是这份仓的实际做法。CSRF 与 Cookie 必须同一会话：换了 Cookie 还用上一份 `csrf-token`，服务端会当成跨站。

## 证据边界

本库没有登录领英，也不收录 Cookie 或 li_at。queryId 正则依赖当前前端打包形状，换构建后要重看 `define(` 的位置。
