# TikTok 旁路签名：frontierSign、ticket-guard、Shop BSID

> 来源: `workspace/cv-cat`（TiktokApis `signing/ticket_guard.py`、`builder/signer.py`、`signing/shop_bsid.py`）
> 原始发布时间: 2026-09-23
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> HTTP 查询签名闭合之后，直播/私信、Creator 写请求和 Shop 仍各有一条独立签名面。三条都不接受「把抓到的签名再贴回去」。本篇写进程合同和信封形状，不收录口令、盐、canvas 原值和 Cookie。

HTTP 两代 SDK 的路由见 [TikTok Web 签名面](./tiktok-web-signing-planes.md)。

## 案例：frontierSign 是独立 Node 进程

`TiktokSigner.frontier_sign` 不走 Python `encode_x_bogus`。它起 `signing/env/sign.js`：

```text
stdin = one JSON line {
  mode: "frontier_sign",
  url, cookie, user_agent, referer, metrics, headers
  stub?: 32-hex-lower-md5
}
stdout = last line that starts with {"ok":
require result.ok and result.values["X-Bogus"] is a string of length 16
```

stub 若提供，必须是 32 位小写 hex，否则 `SignerError`。进程失败、超时、没有合格行，都失败，不回放旧 token。

私信发送（`api/tiktok_web.py`）的真实顺序：

1. `build_ticket_guard("/ws/v2")` 先算票据头。
2. 构造 protobuf 外层请求字节。
3. `frontier_sign(..., stub=md5(request_bytes))` 得到 16 字符标记。
4. 标记放进帧，不放进这条 URL 的 query。注释写明 `Web-Sdk-Ms-Token` 在 Frame header map 里。

所以 IM 的 `X-Bogus` 长度是 16，legacy HTTP 的 `X-Bogus` 是字面量 `1`，Creator HTTP 的 `X-Bogus` 是 `encode_x_bogus` 的输出。三个同名不同合同。

## 案例：ticket-guard 只重算，不复放五头

`signing/ticket_guard.py` 的信封与抖音 bd-ticket-guard 同形，头名前缀是 `tt-ticket-guard-`：

```text
ticket = aes_gcm_decrypt(encrypt_ticket)
# 密文前 12 字节是 IV；密钥由 SDK 固定口令、盐和迭代次数经 PBKDF2-SHA256 得到 16 字节
# 口令与盐是 SDK 快照常量，不写入知识库
sign_input = "ticket=" + ticket + "&path=" + path + "&timestamp=" + ts
req_sign = ECDSA_P256_SHA256(private_key, sign_input)   # DER，再标准 Base64
client_data = b64(json_compact({
  ts_sign, req_content: "ticket,path,timestamp", req_sign, timestamp
}))
headers = {
  tt-ticket-guard-public-key: b64(uncompressed P-256 point),
  tt-ticket-guard-web-version: "1",
  tt-ticket-guard-version,
  tt-ticket-guard-iteration-version,
  tt-ticket-guard-client-data: client_data
}
```

公钥是 65 字节未压缩点的标准 Base64。`build_headers` 从 encrypt_ticket 解出 ticket，不接受已经发出去的 `client-data` 作为输入。

`TiktokAuth.build_ticket_guard` 在私钥、encrypt_ticket、ts_sign 任一缺失时抛 `BrowserEvidenceError`。`post_project` 把「调用方传入的五个已消费头」拒绝掉：只有 `private_key` + `encrypt_ticket` + `ts_sign` 才能重算。注释写明复放会破坏 ticket 的抗重放合同。

签名时间戳还要从刚算出的 `client-data` 里取出，交给同一次 HTTP 签名，避免头和 query 各用各的时钟。

## 案例：Shop BSID 是第三套 Node runner

`ShopBSIDSigner` 跑 `reverse/tiktok_shop_bsid/env/sign.js`，不复用 frontier 的 `sign.js`。

进入条件：

- Cookie 里要有浏览器生成的 `oec_lucifer`，形状是 160 个十六进制字符。没有就失败。
- Cookie 里要有长度落在 `(144, 152)` 的 `msToken`。
- body 必须是 UTF-8。UA 不能空。
- 预签 URL 把 msToken 用 `quote(..., safe="-._~=")` 接上。注释写明 Chrome 保留 Base64 填充的 `=`；若把 `==` 编成 `%3D%3D`，Lucifer 输入差四个字节，BSID 结构仍合法但会被拒绝。

进程合同：stdin 是一个 JSON（url、method、有序 headers、body、cookie、期望长度、本地算出的 x_bogus）。stdout 必须是 JSON，且含 `bsid`。失败日志只留异常类型行，不回显 stdin。期望长度常量是 `382`，这是这份对照的 wire 合同，换 SDK 要重测。

Shop 的 X-Bogus 走 `encode_x_bogus`，ubcode 用 14，和 Creator 的 136 不是同一档。canvas 槽是调用方画像，不跨会话复制。

## 三条旁路对照

| 面 | 运行时 | 成功形状 | 禁止 |
|----|--------|----------|------|
| frontierSign | Node WebMssdk | 16 字符 `X-Bogus` | 回放旧标记 |
| ticket-guard | Python ECDSA + AES-GCM | 五个 `tt-ticket-guard-*` 头 | 复放已消费的五头 |
| Shop BSID | 另一套 Node OEC loader | 定长 `bsid` | 用错误编码的 msToken 预签 URL |

HTTP legacy 的 `X-Bogus=1` 不能拿来填这三处。

## 伪代码

```text
send_im(frame_bytes):
    guard = ticket_guard(path="/ws/v2")          # fresh, not replay
    stub = md5_hex(frame_bytes)
    marker = node_frontier(cookie, ua, stub)     # len 16 or fail
    send_ws(frame_with(marker, guard))

post_project(raw_json_body):
    guard = ticket_guard(path=PROJECT_POST_PATH)
    ts = timestamp_inside(guard.client_data)
    values = project_sign(url_with_msToken, body=raw_json_body, ts=ts)
    POST to_query(values), headers=ordered(guard), data=raw_json_body

shop(url, ordered_headers, body, cookie):
    require oec_lucifer and browser msToken
    signing_url = url + msToken_kept_padding
    bsid = node_oec(signing_url, ordered_headers, body)
    require len(bsid) == EXPECTED
```
