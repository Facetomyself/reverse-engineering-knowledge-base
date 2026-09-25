# 签完即线上：query、头序与 HTTP/2 Cookie

> 来源: `workspace/cv-cat`（DouYin_Spider、TiktokApis、Spider_XHS、JdApis、KuaiShou-Spider 的 HTTP 出口对照）
> 原始发布时间: 2026-09-23
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> 签名算在某一串字节上，服务端也按收到的字节校验。把 dict 再交给 HTTP 客户端，会改顺序、改编码、合并同名键。本篇把各仓已经踩过的写回合同收成一条可复用流程。

各站签名算法见对应案例文。这里只写「签完之后怎么发」。

## 四条写回规则

1. 签名输入和线上 query 用同一次编码。需要二次规范化的链（抖音 webSign）必须发送签名函数返回的 URL，不再传 `params=`。
2. 排序如果只为了算签名，发出去的顺序仍按浏览器。B 站 WBI 是正面例子：`sorted` 只进 MD5，dict 保持原序，末尾追加 `w_rid` 再 `wts`。
3. 同名键不能进普通 dict。京东搜索的浏览器 URL 有两个 `t`，dict 会吞掉一个。`call_api` 用键值列表一路传到客户端，重试时再追加一个 `t`。
4. 头序和 Cookie 拆分是传输合同。`curl_cffi` 要 `default_headers=False`，否则它会把 `sec-ch-ua` 加回来，盖掉已经按抓包裁过的头。

## 案例：抖音两条编码函数不能混

| 函数 | 行为 | 用在哪 |
|------|------|--------|
| `splice_url` | `quote(value, safe='')`，`/` 也变成 `%2F` | `a_bogus` 的输入 |
| `Params.toString` | 不编码，只 `k=v&` | 交给 `sign_url` 的原始 query |
| `sign_url` | 内部再按 webSign 规则解码、重编码、追加 timestamp | 受保护 path 的最终 URL |

受保护接口：`GET sign_url(...)`，不传 `params=`。未受保护接口才可以把 dict 交给客户端。空值字段必须留在 dict 里；`parse_qsl` 会丢掉 `whale_cut_token=` 这类空值，不能用它核对抓包。

HTTP 出口：`impersonate` 选库里实际存在的 Chrome profile，请求的 UA 字符串是另一回事。`default_headers=False`，`http_version` 默认 `v2`。持久会话发 Cookie 时，若调用方已经把 Cookie 放进精确位置，就不能删掉再追加到末尾。`split_cookie_header=True` 时每个 pair 成为一条 HTTP/2 `cookie` 字段。

## 案例：TikTok 与小红书

TikTok `Params.to_query()` 按键选择 `quote` 或 `quote_plus`，签名键有单独的 safe 集合。API 层 `params.update(signatures)` 后只发 `to_query()` 的结果，不读 signer 内部拼好又没按这套 safe 集合编码的 URL。

Shop 预签 URL 用 `quote(msToken, safe="-._~=")`，保留 Base64 填充的 `=`。把 `==` 编成 `%3D%3D` 会让后续 BSID 结构合法但被拒绝。

小红书 body 在签名前 `json.dumps(..., separators=(",", ":"))` 定形成串，POST 用 `data=body.encode()`。搜索 keyword 只编码一次。`ordered_wire_headers` 缺键或多余键直接失败。

快手 `__NS_hxfalcon` 含 `$`。`to_query_string` 按 axios 口径保留 `$`。`requests` 默认把 `$` 编成 `%24`，签名串和线上字节就分叉。

## 传输层单独验收

| 仓 | 出口 | 刻意关掉的东西 |
|----|------|----------------|
| DouYin_Spider | curl_cffi，默认 HTTP/2 | 默认头；每次请求不让 Session 自动覆盖显式 Cookie |
| Spider_XHS | curl_cffi，`v2tls`，`discard_cookies=True` | 默认头；空 POST 的 form content-type |
| JdApis | curl_cffi；头按 fetch / axios 两套顺序重排 | dict 合并同名 `t` |
| KuaiShou-Spider | curl_cffi | `$` 被 percent-encode |
| BilibiliApis | curl_cffi，有序头 | 默认头 |

JS 里设置的头不等于网络层最终头。CDP 要看 ExtraInfo。HTTP 200 加空 body、挑战页、`status_code != 0`，都要先翻译再当成功。

## 伪代码

```text
sign_and_send(request):
    canonical = encode_once(request.query, request.body)   # the signer input
    signature = sign(canonical)
    wire = attach(signature, canonical)                    # same bytes
    if transport_would_reencode(wire):
        send prebuilt_url_or_pair_list(wire)
    else:
        send wire
    headers = ordered_tuple(capture)
    client = impersonate(profile, default_headers=False, http2=True)
    if h2_cookie_crumble:
        cookie_fields = split(cookie, ";")
    response = client.send(wire, headers)
    return classify(response)                              # not "HTTP 200 means ok"
```
