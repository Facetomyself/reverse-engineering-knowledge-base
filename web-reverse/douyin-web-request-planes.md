# 抖音 Web 请求面：七条链的真实装配

> 来源: `workspace/cv-cat`（DouYin_Spider，本地镜像只读对照，抓包窗口约 2026-08）
> 原始发布时间: 2026-09-20
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> 抖音一条「业务请求」同时叠了查询签名、会话 token、URL 完整性、票据、设备头和传输层。本篇用 DouYin_Spider 的真实调用点说明每条链在哪一步接上、哪一步必须停手，不收录字母表、盐或可执行签名器。

对照仓把这些链拆成不同模块。`a_bogus` 通过不能解释 TicketGuard 失败，直播长连的 `signature` 也不是主站 `a_bogus`。产品命中见 [抖音 a_bogus](./products/douyin-a-bogus.md) 与 [Ticket Guard](./products/douyin-ticket-guard.md)。落地选型见 [平台签名落地方法](./sign-landing-methods.md)。

## 链怎么切开

| 链 | 代码入口 | 产出 | 不负责 |
|----|----------|------|--------|
| 查询签名 | `Params.with_a_bogus` → `generate_a_bogus(query, data, host)` | query 里的 `a_bogus` | 不改 URL 编码后的线上字节 |
| 子域常数 | `ab_pure.app_ids_for(host)` | 签名内嵌的 `(aid, page_id)` | 不负责 query 里另一个 `aid` |
| 会话 token | `auth.msToken` → `get_mstoken` | 服务端 `x-ms-token` | 本地随机串不是这条链 |
| URL 完整性 | `Params.signed_url` → `secsdk_web_sign.sign_url` | `timestamp` + `x-secsdk-web-signature` | 只覆盖策略表里的 path |
| 票据只读 | `Header.with_bd_readonly` | 四个 `bd-ticket-guard-*`，无 `client-data` | 写接口不能用这组头 |
| 票据写入 | `Header.with_bd` | `client-data` + 可选 `x-tt-session-dtrait` | ticket 与 cookie 不同源则直接抛错 |
| 直播长连 | `generate_signature(room_id, user_unique_id)` | WS query 的 `signature`（X-Bogus 族） | 与 `a_bogus` 分轨 |
| 传输 | `http_client.request` | Chrome impersonate、HTTP/2、关掉默认头 | 不补业务签名 |

`a_bogus` 内嵌的子域表在 `utils/ab_pure.py`：`www` 为 `(6383, 11881)`，`live` 为 `(6383, 7571)`，`creator` 为 `(2906, 33638)`，`login` 为 `(6383, 6241)`。未知 host 退回主站一组。这张表会随 SDK 过期，复用的是「签名函数必须吃 host」。

创作者发布还同时出现三个不同的 aid，不能合并成一个常量：

| 用途 | 值 | 位置 |
|------|----|------|
| query `aid` | `1128` | `Params.with_creator_platform` |
| `read_aid`、换证书、`with_bd` | `2906` | `douyin_creator_api.py` 的 `CREATOR_READ_AID` |
| `a_bogus` 内嵌 | `(2906, 33638)` | `app_ids_for("creator.douyin.com")` |

## 案例 A：作品详情，签完的 URL 才是要发的 URL

`DouyinAPI.get_work_info`（`dy_apis/douyin_api.py`）走受保护 path `/aweme/v1/web/aweme/detail/`。

1. 公共 query 用 `with_platform`，但 `version_code` / `version_name` 必须改回该接口的 `190500` / `19.5.0`。源码注释写明：全站默认 `170400` 套到 detail 上是自己引入的回退。同文件还记录 search 为 `190600`，作品列表手写 `290100`。
2. `verifyFp` / `fp` 放在 `msToken` 之前。这个相对位置按接口抓包，不是全站固定。
3. `with_a_bogus()` 用 `splice_url` 生成签名输入：值用 `quote(..., safe='')`，`/` 也编码成 `%2F`。
4. `signed_url()` 再做 secsdk 规范化，返回带 `timestamp` 和 `x-secsdk-web-signature` 的完整 URL。
5. `requests.get(signed_url, headers=..., cookies=...)` 不传 `params=`。
6. `check_risk_response` 先看 body 是不是 JSON。HTTP 200 空 body、bdturing 头、passport decision 头都要翻译成失败，不能直接 `resp.json()`。

```text
biz keys
→ with_platform(version = 该接口实录版本)
→ webid / uifid / verifyFp / msToken   # 顺序按该接口抓包
→ a_bogus = sign(splice_url(query), body, host)
→ if path in PROTECTED:
      send sign_url(origin + path + "?" + toString())
      # 不再把 dict 交给 HTTP 客户端重编码
→ else:
      send origin + path with params=dict
→ translate non-JSON / empty / bdturing / passport-decision
```

`Params.toString()` 不 quote，只做 `k=v&...`。它和 `splice_url` 不是同一个函数。受保护接口必须发 `sign_url()` 的返回值，因为签名算在规范化 query 上，服务端也按收到的 query 校验。

## 案例 B：评论列表，只读票据，允许 params 重编码

`get_work_out_comment` 的 path `/aweme/v1/web/comment/list/` 不在 `PROTECTED_PATHS_GET` 里。

1. `Header.with_bd_readonly`：四个 `bd-ticket-guard-*`，不含 `client-data`。源码写明浏览器只读接口不发 `client-data`，多字段同样是与浏览器不一致。
2. 空值字段 `whale_cut_token=`、`rcFT=` 必须留下。`parse_qsl` 默认会丢掉空值，不能用它判断浏览器有没有发这些键。
3. `with_a_bogus()` 之后 `requests.get(..., params=params.get())`。这条链允许客户端再编码，因为没有 secsdk 去绑规范化 query。
4. 缺 `private_key` 时 `with_bd_readonly` 静默跳过。只读失败不一定能从异常里看出缺票据。

## 案例 C：直播电商，host 绑定 a_bogus，空 body 不是签名错误

`get_live_production` 打 `live.douyin.com` 的 `/live/promotions/pop/v3/`。

1. 先手写 `aid=6383`，再 `with_live_platform()`。直播公共组的 `version_code` 是 `320100` / `32.1.0`，`support_dash=0`，`round_trip_time` 默认 `50`。主站那组是 `170400` / `17.4.0`、`support_dash=1`、`round_trip_time` 默认 `0`。
2. `entrance_info` 是紧凑 JSON，发出去之前再整体 `quote`。
3. `with_a_bogus(host="live.douyin.com")`，内嵌 page_id 走 `7571`，不是主站 `11881`。
4. 响应体为空时直接返回 `{"promotions": []}`。源码注释：真实浏览器对未挂商品的房间也是 HTTP 200 空 body。有内容才走 `check_risk_response`。

直播长连是另一条链。`dy_live/server.py` 把 `generate_signature(room_id, user_id)` 放进 WS query 的 `signature`。它先拼一条固定字段的直播 SDK 字符串，MD5 成 stub，再交给 `XbogusSigner`。这不是 `a_bogus`。

## 案例 D：创作者发布，材料不齐就不发

`DouyinCreatorAPI._create_aweme` 打 `/web/api/media/aweme/create_v2/`。

1. `_require_publish_security` 失败则返回，请求不发出。
2. `Header.with_bd(..., aid=2906, require_dtrait=True)`。`ticket_matches_session()` 失败抛 `RuntimeError`：cookie 里的 `bd_ticket_guard_ts_sign_id` 对不上当前 `ts_sign`。dtrait 生成失败同样不发。
3. CSRF 必须向 `creator.douyin.com` 换。源码注释写明早先固定打 www，token 与会话对不上。
4. body 用 `json.dumps(..., separators=(",", ":"))` 定形成串，再把同一串交给 `generate_a_bogus(query, body, host="creator.douyin.com")`。
5. POST 带 `split_cookie_header=True`，按 Chromium HTTP/2 把 Cookie 拆成多条 `cookie` 字段。
6. 非 JSON 时提示 403 空响应基本等于缺 `bd-ticket-guard`，并要求 ticket / ts_sign / private_key 同源。

## 失败怎么读

`check_risk_response`（`douyin_api.py`）把非 JSON 分成四类：

| 信号 | 翻译 |
|------|------|
| `X-Vc-Bdturing-Parameters` | 人机验证，先看 subtype |
| `X-Tt-Verify-Passport-Decision` | 二次身份验证；源码把它和缺 `x-tt-session-dtrait` 放在同一提示里 |
| 空 body | 笼统失败：签名或风控。直播商品接口要先排除「未挂商品」 |
| HTML 含 `__ac_nonce` 或 `_$jsvmprt` | acrawler 挑战页 |

这条翻译函数的文案仍写「`__ac_signature` 尚未纯算实现」。同仓 `acrawler.py` 已经用 Node 页面 VM 出参，并在严格模式下拒绝空签名。文案滞后，不能据此判断 acrawler 链不存在。会话材料链见 [抖音会话材料案例](./douyin-session-materials-case.md)。secsdk 见 [webSign 纯算案例](./douyin-secsdk-websign-case.md)。

## 装配器伪代码

```text
assemble(plane, path, biz, auth, body):
  headers = browser_xhr_headers(plane)
  headers.uifid = cookie.UIFID
  if plane.ticket == "readonly":
      headers += bd_readonly(auth)          # 4 headers, no client-data
  if plane.ticket == "write":
      require ticket_matches_session(auth)
      headers += bd_write(path, aid=plane.cert_aid, require_dtrait=plane.force_dtrait)
  if plane.csrf:
      headers.csrf = csrf_from(plane.origin)   # origin 必须与业务同源

  query = ordered_pairs(biz, plane.platform_template)
  query.msToken = auth.msToken             # 个别接口抓包确认后可以省略
  signed = a_bogus(splice(query), splice_or_raw(body), host=plane.host)
  query.a_bogus = signed

  if path in webSign_policy(method):
      return GET sign_url(origin + path + "?" + raw_join(query), uifid)
  return REQUEST(origin + path, params=query, body=body, headers=headers)
```

## 证据边界

- 行号与分支来自本地 `DouYin_Spider` 源码，不是重新打线上的验收。
- `version_code`、`(aid, page_id)`、策略 path 表都是抓包窗口常量，换 SDK 要重核。
- 本篇不收录 `a_bogus` 字母表、RC4 键、secsdk 盐、设备画像原值和 Cookie。
