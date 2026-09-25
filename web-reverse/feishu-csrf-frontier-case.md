# 飞书案例：HTTP CSRF 与 frontier WebSocket 分链

> 来源: `workspace/cv-cat`（OpenFeiShuApis，HEAD 日期 2026-08-18，只读对照）
> 原始发布时间: 2026-08-18
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> 这份对照仓不是开放平台的 `tenant_access_token`。网页会话分成两条：HTTP 用 `accounts/csrf` 换 `swp_csrf_token`，长连用 JS 算出的 `access_key` 加 frontier ticket 去连 `msg-frontier`。

## 案例：CSRF 再取用户

`FlyBookApi.get_csrf_token`：

1. POST `https://internal-api-lark-api.feishu.cn/accounts/csrf`。
2. 头和 query 来自 `HeaderBuilder.build_get_csrf_token_header` 与 `ParamsBuilder.build_get_csrf_token_param`。
3. 返回 Cookie 里的 `swp_csrf_token` 作为后续头 `x-csrf-token`。
4. `get_user_info` 把这个值放进头，再请求用户信息。

Cookie 必须已经是登录会话。仓内示例文件写死过 Cookie 和 JWT，那些是捕获残留，不入库，也不能当算法输入。

```text
session_cookie = caller_login_cookie
_, x_csrf = POST /accounts/csrf with session_cookie
x_csrf = response.cookie["swp_csrf_token"]
user = GET user_info header x-csrf-token = x_csrf
```

## 案例：frontier 长连

`builder/params.py` 另有 `https://login.feishu.cn/suite/passport/frontier_ticket/`。`generate_access_key` 把一段材料交给 `static/fly_book.js` 的同名导出。JS 侧是 MD5 拼装，明文材料留在源码，不入库。

`FlyBookRec.py` 把参数 urlencode 后连接 `wss://msg-frontier.feishu.cn/ws/v2`。长连 query 里的 `access_key` 和 HTTP 的 `x-csrf-token` 不是同一个值。IM 网关 HTTP（`im/gateway/`，带 `x-command`）又是第三条面，不能用 frontier 的 ticket 去打。

```text
ticket = GET frontier_ticket with session
access_key = js.generate_access_key(material)
WS wss://msg-frontier.feishu.cn/ws/v2 ? access_key & ticket & ...
```

## 落地判断

没有开放平台 tenant token 的本地签发。可复用的是分链：CSRF 头来自一次 POST 的 Set-Cookie，长连 key 来自页面 JS，两者失败不能互相解释。`fly_book.js` 函数体不入库。

## 证据边界

本库没有连接飞书。示例 Cookie、JWT、did 不收录。`access_key` 的输入字段以当前 `generate_access_key` 调用点为准，换前端后要重看 JS 导出是否还在。
