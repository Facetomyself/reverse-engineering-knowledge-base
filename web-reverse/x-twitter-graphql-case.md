# X 案例：Bearer、ct0 双写与写死的 GraphQL features

> 来源: `workspace/cv-cat`（XApis，HEAD 日期 2026-08-18，只读对照）
> 原始发布时间: 2026-08-18
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> 这份对照仓不计算 X 的签名，也不刷新 guest token。调用方传入 Bearer 和 `ct0`，头里把 `ct0` 双写成 `x-csrf-token`。搜索参数里的 operation 特征和 features JSON 是源码里的快照。

## 案例：搜索

`utils/twitter_utils.py` 的 `get_common_headers(authorization, x_csrf_token)` 同时设置：

- `authorization`：调用方传入的 Bearer，本仓不生成
- `x-csrf-token`：应与 Cookie `ct0` 相同
- `x-twitter-auth-type: OAuth2Session`
- `x-twitter-active-user: yes`
- `x-twitter-client-language: en`

`get_search_params` 把 `rawQuery`、`count`、`product`（Top / Latest）和可选 `cursor` 拼进一个 JSON 字符串，放在 query 的 `variables` 里。`features` 是一大段写死的布尔开关 JSON。这是前端构建快照，不是算法。X 改 features 集合后，旧快照会在 GraphQL 层失败，即使 Bearer 仍然有效。

```text
headers = {
  authorization: caller_bearer,
  x-csrf-token: cookie.ct0,
  x-twitter-auth-type: "OAuth2Session"
}
query = {
  variables: json({ rawQuery, count: 20, product, cursor? }),
  features: FROZEN_FEATURE_SET
}
GET graphql search with headers and cookie
```

仓内没有 guest token 刷新，也没有 `x-client-transaction-id` 一类本地签名。缺 Bearer 或 `ct0` 时，失败在头装配之前。features 不匹配时，Bearer 仍然有效，不要把两类失败合成一个「签名错了」。

## 证据边界

不收录 Bearer、`ct0` 或完整 features 原文。features 快照会过期，复用时以当前网页请求的 features 键集合为准，而不是把 2026-08 的 JSON 当永久合同。本库没有请求 x.com。
