# 抖音会话材料：msToken、票据、dtrait、acrawler

> 来源: `workspace/cv-cat`（DouYin_Spider，本地镜像只读对照）
> 原始发布时间: 2026-09-20
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> `a_bogus` 算对之后，请求仍会因材料出处错误失败。本篇按源码把四条材料链分开：服务端签发的 msToken、票据 HMAC/ECDSA、按 path 重算的 dtrait、页面 VM 写出的 `__ac_signature`。随机串不能占这些位置。

查询签名和 webSign 见 [抖音 Web 请求面](./douyin-web-request-planes.md) 与 [webSign 案例](./douyin-secsdk-websign-case.md)。本篇不收录私钥、证书、设备 blob、canvas data URL 和 Cookie。

## 材料出处

| 材料 | 出处 | 失败时源码做什么 |
|------|------|------------------|
| `msToken` | mssdk 响应头 `x-ms-token`，或 Set-Cookie | `get_mstoken` 失败返回空串，不造随机 token |
| `generate_msToken()` | 本地随机，默认长度 107 | 存在，但不是 mssdk 链 |
| ticket / `ts_sign` / 私钥 | 同一次登录 | `ticket_matches_session()` 失败则写接口不发 |
| `x-tt-session-dtrait` | 会话内复用的 RSA 包住的 AES key，按 path 重算第二段 | `require_dtrait=True` 时生成失败则不发 |
| `__ac_signature` | `__ac_nonce` + Node 页面 VM | strict 模式拒绝空签名；非 strict 不写入假签名 |
| 直播 `signature` | 本地 X-Bogus 族，输入是房间 stub | 与上面四条无关 |

## 案例：msToken 是签发值，不是随机串

`utils/dy_util.py` 里两个函数名很近：

- `generate_msToken(107)` 从本地字符表抽 107 位。这是未证明的合成值。
- `generate_dynamic_msToken` 调用 `mstoken.get_mstoken`。缓存命中且未过 TTL 就返回缓存；否则 POST 报告信封，读响应头 `x-ms-token`，没有再从 `set-cookie` 里抠 `msToken=`。异常返回空串。

登录页旋转走另一条 URL：`refresh_common_mstoken` POST `/web/common`，query 带 `ms_appid=6383`，续期时把旧 token 挂在 query 上。信封分 common report 和 behavior 两种，不能混用。

业务侧 `params.add_param("msToken", auth.msToken)` 走的是惰性动态 token。个别接口抓包确认后可以不带，例如收藏列表。省略必须有该接口的抓包，不能全局删。

```text
if cache fresh:
    return cache
envelope = report_body()          # 形状按 mssdk 实录，不含在本文
POST token_url [?msToken=old]
token = response.header["x-ms-token"] or set-cookie msToken
if token:
    cache it
else:
    return ""                      # 不降级成 generate_msToken()
```

## 案例：只读票据和写入票据不是同一组头

`Header.with_bd_readonly` 只放四个头：`ree-public-key`、`version=2`、`web-version`、`web-sign-type`。没有 `client-data`。评论、收藏、关注列表的实录是这四头。

`Header.with_bd` 额外放 `bd-ticket-guard-client-data`，并在需要时放 `x-tt-session-dtrait`。发布接口用这条。

`client-data` 的明文是紧凑 JSON，标准 Base64（`+/`，不是 urlsafe）：

```text
sign_input = "ticket=" + ticket + "&path=" + pathname + "&timestamp=" + ts
req_sign = HMAC_SHA256(ecdh_key, sign_input)    # 有 ECDH key
         or ECDSA_SHA256(private_key, sign_input)
envelope = {
  ts_sign, req_content: "ticket,path,timestamp",
  req_sign, timestamp
  [, t_trust]     # 仅当 _bd_ticket_crypt_cookie 已存在
}
client_data = btoa(json_compact(envelope))
```

`web-version` 由 `ts_sign` 前缀决定：`ts.1` 开头为 1，否则为 2。`web-sign-type` 在有 ECDH key 时为 hmac=`1`，否则 ECDSA=`0`。只读头用客户端证书是否以 `pub.` 开头做同一类判定，保证同一会话自洽。

换证书的 body 用逗号连接。dtrait 拉公钥的 body 用 `&` 连接，并且 query 带 `type=trait`。两条都打 passport 证书接口，键分隔符不同。

## 案例：dtrait 按 path 重算，第一段会话内复用

`build_session_dtrait` 的线上头是三段：`{pk1_version}_{b64(rsa(aes_key))}_{b64(iv || aes_cbc(payload))}`。

payload 是紧凑 JSON，键顺序固定为 `dtrait`、`timestamp`、`sdkVersion`、`path`。源码注释写明省略 `sdkVersion` 会让 challenge/check 的头短一个 AES 分组。`path` 是 pathname，不含 query。

同一页面会话复用已经 RSA 包住的 AES key（第一段）。每个请求重新生成 IV，并按当前 path 加密第二段。发布接口 `require_dtrait=True`，生成失败就不发请求。

设备 blob 本身是外来材料。本篇不描述 blob 字段，也不收录内置公钥。

## 案例：acrawler 失败不能写成随机 Cookie

`generate_ac_signature` 的合同：

1. 没有 `__ac_nonce`：strict 抛错；非 strict 返回空 `sig`，provenance 标 `unproven_synthetic`。
2. 没有 Node 或 runner：同样不造签名。
3. 通过环境变量把 nonce、Cookie、页面 URL、UA、时钟传给独立 runner。时钟要显式传入，避免 VM 里的 `Date` 走另一条分支。
4. stdout 最后一行 JSON 的 `sig` 必须以 `_` 开头，进程退出码为 0。否则 strict 抛错，且不把 stdout 打进异常（里面可能有 Cookie）。
5. 成功时 provenance 为 `node_page_js`，并记录 Cookie 相对输入的变更。

登录侧 `_apply_ac_signature`：已有且来源被接受的签名默认保留，这是 Cookie 交接，不是重新计算。严格登录缺 nonce 或 runner 失败则中断，不写空签名。

`check_risk_response` 仍把挑战页说成「尚未纯算」。那句文案滞后。当前实现是隔离页面 VM，不是零宿主纯算，也不能把失败降级成随机 `__ac_signature`。

## 直播 signature 不是这些材料

`generate_signature` 把 `room_id` 和 `user_unique_id` 嵌进一条固定字段的直播 SDK 字符串，MD5 成 stub，再交给 `XbogusSigner`。WS URL 的参数名是 `signature`。它不读 ticket，也不读 msToken。用 `a_bogus` 或随机 msToken 去解释直播长连失败，会看错链。

## 创作者上传的另一条签

图文/视频上传走 `imagex_sign.sign_request`：火山网关 V4，HMAC-SHA256，query 按 key 排序并做 RFC3986 编码，body 的 SHA256 进待签串，STS session token 进 `x-amz-security-token`。这和 `a_bogus`、ticket-guard 都不是同一把钥匙。密钥来自上传凭证接口，不在本文收录。

## 伪代码：材料就绪门

```text
before_send(plane, auth, path):
  if plane.needs_msToken and not auth.msToken:
      auth.msToken = get_mstoken()          # 空则失败，不随机
  if plane.ticket == "write":
      require same_login(ticket, ts_sign, cookie)
      require ecdh_or_ecdsa_material(auth)
      if plane.force_dtrait:
          require dtrait_header(path)
  if plane.needs_ac_signature:
      sig = acrawler(nonce, cookie, strict=True)
      require sig.provenance == "node_page_js"
  # 通过后才允许进入 a_bogus / webSign
```
