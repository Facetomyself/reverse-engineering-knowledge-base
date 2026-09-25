# 小红书装配案例：材料六桶、签完即发、端别切开

> 来源: `workspace/cv-cat`（Spider_XHS 现行 `xhs_core` / `xhs_pc` / `xhs_creator`，只读对照）
> 原始发布时间: 2026-09-08
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> 小红书签名头族的命中特征见 [x-s 产品文](./products/xiaohongshu-xs.md)。本篇补现行代码里的装配合同：参数按出处分桶、签参失败不降级、PC / Creator / 蒲公英 / 千帆切开，以及签完的 body 不再交给 HTTP 客户端重编码。不收录 mns keystream、字母表和 AES 材料。

## 材料六桶

`xhs_pc/auth.py` 的 `PC_PARAMETER_SOURCES` 把参数分成六类：本地算法、对齐覆盖、生命周期状态、远端程序锚、服务端下发、用户交互。Creator 有一张同构表。`parameter_sources()` 只读返回这张表，业务层不能「缺什么就随机一个」。

| 桶 | 例子 | 失败行为 |
|----|------|----------|
| 本地算法 | `a1`、`webId`、mns 档位、`x-s` | 允许按状态机生成，禁止每次随机 |
| 远端程序 | `_dsl`、`websectiga` | DS 失败时有缓存就用缓存，否则抛错 |
| 服务端下发 | `web_session`、`gid`、`sec_poison_id` | Cookie 登录缺 `a1` / `web_session` 直接 `ValueError` |
| 用户交互 | 扫码、短信 | 不能在代码里合成 |

DS 锚的 TTL 是 300 秒，和 ds 接口 `cache-control max-age=300` 对齐。`getdss()` 用正则从混淆 JS 里取出 13 位时间戳，不跑整段 Sabo VMP。

Creator 的 mns0101 在设备标签不是 nop 时，缺 `dsProgram` 直接 `ValueError`。程序通过临时 JSON 文件交给 Node，超时默认 30 秒，非 0 退出码失败。`websectiga` 走另一条合同：stdin JSON，出参必须是 64 位十六进制，否则无效。两者都记 runtime，不能标纯算。

## 案例：一次 PC 业务请求

```text
auth = XHSPcAuth.from_cookie(cookie)     # 直接构造被禁止
require a1 and web_session
dsl = DsFetcher.get_bundle()             # cache or raise, never random
body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
headers = generate_xs_and_common(...)    # fail closed, no short-sign fallback
headers = ordered_wire_headers(route)    # missing or extra key → RuntimeError
cookies = cookies_for_url(host)          # host-only acw_tc stays on that host
POST url, data=body.encode("utf-8")      # not json=
```

空 POST 显式传 `b""`，并去掉默认 `content-type`，避免 libcurl 补成 form-urlencoded。搜索 keyword 只 `urlencode` 一次，调用方不要预先 `quote`。

`HostCookieStore` 把 `acw_tc` 这类 host-only Cookie 和共享 Cookie 分桶。扁平 dict 会把 edith 的 `acw_tc` 带到 as/so。

传输层是 `curl_cffi`：`default_headers=False`，`discard_cookies=True`，`http_version=v2tls`。PC 子类 impersonate `chrome146`，Creator 子类 `chrome150`。注释写明抓包是更高的 Chrome，库里没有对应 profile 时用已发布的最近一档。这是传输档，不是把 UA 字符串当成 TLS 指纹。

## 四条端别

| 面 | 切开点 | 签名范围 |
|----|--------|----------|
| PC | `XHSPcAuth` + `appId=xhs-pc-web` | `x-s` / `x-t` / `x-s-common`，指纹就绪后 mns0301 |
| Creator | `XHSCreatorAuth`，可由 PC 登录懒创建 | `appId=ugc`，无 0301；0101 要 DS 程序 |
| 蒲公英 | `generate_pugongying_headers` | 只 `generate_xs`，不造 `x-s-common`；HTTP 仍走普通 `requests` |
| 千帆工具文件 | `xhs_qianfan_util.py` | 只有静态头模板；authority 仍指向蒲公英 host，没有独立 x-s 组装 |

`XHS_ALL_IN_ONE` 是运营壳，签名在仓内 `xhs_utils` 副本里，不是 import 另一份 Spider_XHS。`XhsSkills` 仍编译 `xhs_main_260411.js`，那是 2026-04 的 execjs 快照，XsCommon 没有现行的 `x12=dsl`。算法只认现行 `xhs_core`。

## 伪代码：provenance 门

```text
classify(name):
    return bucket_of(name) in {local, override, lifecycle, remote, server, user}

before_sign(auth):
    require login_source in {cookie, qrcode, phone}
    require server_issued keys present
    if dsl expired:
        refresh or raise
    if creator and mns0101 and device_tag != nop:
        require dsProgram

after_sign(headers, body):
    require ordered_wire_headers(headers)
    send bytes(body)                         # body already canonical
```

## 证据边界

行号对照的是本地 Spider_XHS 树。mns 档位和 `x12` 形状以现行源码为准，换前端包要重核。本篇不收录 keystream、RAP 密钥和指纹原值。
