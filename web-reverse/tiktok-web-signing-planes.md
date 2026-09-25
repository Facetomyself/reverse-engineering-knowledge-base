# TikTok Web 签名面：端点合同、两代 SDK、fail-closed

> 来源: `workspace/cv-cat`（TiktokApis，本地镜像只读对照，仓说明写明 2026-09-23 去掉整包 execjs）
> 原始发布时间: 2026-09-23
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> TikTok HTTP 签名按 path 选择字段集和编码器。Creator Studio 5.1.0 与公开 Web 5.3.2 不能混用。缺 msToken、空 header、长度不匹配都直接失败，抓包签名不能回填。本篇只写路由和写回合同，不收录轮函数、字母表和 canvas 原值。

直播 frontierSign、ticket-guard 和 Shop BSID 是另外的进程合同，见 [TikTok 旁路签名面](./tiktok-frontier-ticket-shop-case.md)。

## 路由

`required_signature_keys(url)` 只看 path 子串。`TiktokSigner.sign` 再用 URL 字符串决定走 project 还是 legacy。

| path | 必需字段 | 编码器 |
|------|----------|--------|
| 反馈、screen time、popup、合规、分享设置等一列显式名单 | 无 | 不调用 WebMssdk。补上签名字段会改变请求哈希 |
| `/tiktok/web/project/post/v1/`、`post_retry`、`/api/v1/video/upload/auth/`、`/tiktok/creator/manage/item_list/v1/` | `msToken`、`X-Bogus`、`X-Gnarly` | `encode_x_bogus` + `encode_gnarly_project`，ubcode 136，SDK 面 5.1.0 |
| 其余默认 Web API | `X-Dynosaur`、`msToken`、`X-Bogus`、`X-Gnarly` | `encode_dynosaur_current` + `encode_gnarly_current`，payload 版本字面量 `5.3.2` |

无签名名单在 `builder/signer.py` 的 `required_signature_keys` 里逐条列出。它是 path 证据，不是「短了就补」的规则。

## 案例：legacy Web 的 X-Bogus 是字面量 `1`

`_sign_legacy_pure` 已经核对：

1. unsigned URL 的 query 里必须已有浏览器 `msToken`。没有则 `SignerError`。
2. 剥掉已有的 `X-Dynosaur` / `X-Bogus` / `X-Gnarly` / `msToken`，剩下的才是 Dynosaur 的 `base_query`。
3. 空 `user-agent` 直接失败。
4. Dynosaur 绑的是文档 URL，可以和 HTTP Referer 不同。调用方没给时，才用 referer 的 host+path。
5. `X-Gnarly` 的输入是已经拼上 Dynosaur 和 msToken 的 query，再加上 body 和 UA。
6. `X-Bogus` 写成字面量 `"1"`。注释写明这是当前 web API 的一字节标记，不是从抓包里垫出来的值。最终 query 也拼 `X-Bogus=1`。

```text
base = query without signature keys
require msToken in original query
require user-agent
dynosaur = encode_dynosaur_current(base, ua, page, runtime_slots)
gnarly = encode_gnarly_current(base + "&X-Dynosaur=" + dynosaur + "&" + msToken, body, ua)
values = {X-Dynosaur: dynosaur, msToken: token, X-Bogus: "1", X-Gnarly: gnarly}
if expected_lengths mismatch:
    raise SignerError
```

运行时槽（field8、field18、field19、rand_b）可以由当前浏览器快照传入。缺省时用 unsigned query 和 UA 在本地算出同形状的值，避免字面量 `0` 把 Dynosaur 缩成和 Chrome 不一样的长度。这些缺省值是形状占位，不是跨机器可复制的指纹。canvas / envcode 同样只作为调用方指标，不把作者机器的整数写进知识库。

## 案例：Creator project 吃整段 query，并且要重算 ticket

`_sign_project_pure`：

- `X-Bogus` 调用 `encode_x_bogus(整段 query, ua, body, ubcode=136)`。
- `X-Gnarly` 调用 `encode_gnarly_project`，query 仍含 msToken，尚未剥离。
- 不产生 `X-Dynosaur`。
- 返回的 `url` 仍是入参原串。字段在 `values` 里，由 API 层写回。

`post_project`（`api/tiktok_web.py`）把这条链和 ticket-guard 绑在一起：

1. body 必须是浏览器原样 JSON 字符串。重建对象会改键序，签名输入就变了。
2. 五个已发出的 ticket-guard 头不能复放。只接受私钥、encrypt_ticket、ts_sign，现场重算。
3. 头按 Chrome project POST 的顺序排成 `OrderedDict`，再交给签名函数。
4. unsigned query 先拼上 `msToken`，再 `sign_request`。
5. `params.update(signatures)` 后用 `to_query()` 发。`to_query()` 按键选择 `quote` 或 `quote_plus`，签名键有单独的 safe 集合。
6. 成功口径是 JSON `status_code == "0"`，不是 HTTP 200。

msToken 长度会从抓包样本变到当前 Cookie。长度检查用当前 token 的实际长度，同时仍检查 X-Bogus / X-Gnarly 的证据长度。

## 写回：API 不使用 signer 内部拼好的 URL

通用 `_request`：

```text
if signed:
    require_browser_profile()
    unsigned_query = params.to_query()
    if "msToken=" not in unsigned_query:
        unsigned_query += "&msToken=" + auth.ms_token
    signatures = auth.sign_request(path, url=origin+path+"?"+unsigned_query, headers, body)
    params.update(signatures)
url = origin + path + "?" + params.to_query()
request(method, url, headers, data=body)    # 不再传 params=
```

`signature_for` 按 `required_signature_keys` 的顺序取出字段。缺任一字段，或长度元数据对不上，抛 `BrowserEvidenceError`。注释写明浏览器追加顺序是 `X-Dynosaur`、`msToken`、`X-Bogus`、`X-Gnarly`。legacy 有 Dynosaur，project 的 required 元组里没有它，所以写回顺序跟着 required 走。

`require_browser_profile` 还拒绝：

- 缺 `s_v_web_id`
- 缺 msToken（它可能只在 storage 里，不在 Cookie 头里，所以检查解析后的属性）
- Tea cache 里多个 `device_id` 且调用方没指定
- 没有显式设备证据（`multi_sids` 或显式 device_id / odin_id）

静态抓包签名作为输入已经被禁用：`signature_for` 在没有完整 unsigned URL 时直接抛错。

## 伪代码

```text
sign_http(url, method, headers, body, ua):
    if path in UNSIGNED:
        return url unchanged
    require headers non-empty
    if method has body:
        require body is not None
    require msToken already on query
    if path in PROJECT:
        return project_values(query, body, ua)     # no X-Dynosaur
    return legacy_values(base_query, body, ua)     # X-Bogus literal "1"
writeback:
    params.update(values in required order)
    send to_query()                                # do not re-dict-encode
```

## 证据边界

- `X-Bogus="1"` 是这份 5.3.2 对照实现里的端点合同，不是所有历史 TikTok 接口的永久事实。换 SDK 要重新看浏览器 query。
- 编码器内部的轮函数、字母表、魔数表不收录。
- 本库没有对线上重放这些签名。
