# 方法论：请求面切开，失败按面翻译

> 来源: `workspace/cv-cat`（DouYin_Spider、TiktokApis、KuaiShou-Spider、JdApis、TaoBaoApis 的失败分链）
> 原始发布时间: 2026-09-23
> 归档日期: 2026-09-24
> 分类: web-reverse
>
> 一条「平台请求」通常叠了查询签名、会话材料、完整性头、设备头和传输。一个组件正确不能解释整站失败。先画面，再把 HTTP 200、空 body、业务码翻译到具体的面，而不是统一归到签名算错。

抖音的七条链见 [请求面案例](./douyin-web-request-planes.md)。

## 画法

对一条抓包，按「谁生产、谁消费、失败时长什么样」拆行。生产函数不同，就是不同的面。同名参数如果生产函数不同，也是不同的面。

| 面 | 生产 | 消费位置 | 典型失败 |
|----|------|----------|----------|
| 查询签名 | `a_bogus` / `x-s` / `__NS_sig3` / h5st / MTOP `sign` | query 或头 | 空 body、403、业务码指向参数 |
| 会话 token | `msToken`、`_m_h5_tk`、`web_session` | query 或 Cookie | 登录失效、token 空 |
| 完整性 | TicketGuard、`x-secsdk-web-signature` | 头或 URL 尾 | 缺头即 403 空响应 |
| 设备 / 行为 | dtrait、`b1`、`kwfv1`、`tfstk` | 头或 Cookie | passport decision、验证码 |
| 传输 | TLS impersonate、头序、Cookie 拆分 | 连接层 | JS 对了仍挂 |
| 业务读回 | JSON 字段、`ret`、`status_code` | 响应 | HTTP 200 但不是成功 |

TikTok 把这套写成 `required_signature_keys(path)`：有的 path 四个字段，有的三个，有的明确零个。零个不是「还没签」，是浏览器本来就不签。给无签名 path 补上 `X-Bogus` 会改变请求哈希。

## 真实翻译

抖音 `check_risk_response` 在 `resp.json()` 之前看响应：

| 信号 | 翻译到哪一面 |
|------|----------------|
| body 以 `{` 或 `[` 开头 | 先当业务 JSON，再看内部码 |
| `X-Vc-Bdturing-Parameters` | 人机面。看 subtype，不要改 `a_bogus` |
| `X-Tt-Verify-Passport-Decision` | 二次验证。源码把它和缺 `x-tt-session-dtrait` 放在一起 |
| 空 body | 笼统。直播商品接口要先排除「未挂商品」 |
| HTML 含 `__ac_nonce` | acrawler 面，不是查询签名面 |

这段函数的文案仍写 acrawler「尚未纯算」。同仓已经有 Node 页面 VM。翻译表也要随代码更新，否则会把人带到不存在的缺口。

其它仓的分链：

- 创作者 `create_v2`：安全材料、CSRF、Cookie、dtrait 任一失败，请求不发出。403 空响应在注释里对应缺 `bd-ticket-guard`。
- 快手 `_get`：业务码 400002 转滑块，不回头改 hxfalcon。
- 京东搜索：h5st 的 `tk03`、eid Cookie、JCAP 的 `vt` 三条并行。`vt` 不是 h5st 算出来的。
- 淘宝：H5 `sign` 只换 IM token；私信是 LWP，帧里没有 `sign`。
- 公众号后台：`base_resp.ret != 0` 是 CGI 失败。公开文章 HTML 不带 token，两条面不要互解释。
- TikTok `post_project`：成功是 JSON `status_code == "0"`，不是 HTTP 200。

## 伪代码

```text
planes = [
  query_sign, session, integrity, device, transport, business
]

on_response(resp, planes):
    if resp.body empty:
        if plane_has_known_empty_success:          # live room without goods
            return business_empty
        return fail(integrity_or_sign, evidence=headers)
    if bdturing_header(resp):
        return fail(captcha, subtype)
    if passport_decision(resp):
        return fail(device_or_step_up)
    if acrawler_html(resp):
        return fail(acrawler_cookie)
    doc = parse_json(resp)
    if doc.ret != 0 or doc.status_code != "0":
        return fail(business, code=doc.code)
    return server_accepted

on_exception_before_send(err):
    # 材料门失败：请求没发出，不要去改签名算法
    return fail(plane_of(err))
```

## 同名不同面

| 名字 | 面 A | 面 B |
|------|------|------|
| `a_bogus` | 抖音查询签名，吃 host | 不是直播 WS 的 `signature`，也不是 `X-Bogus` |
| `X-Bogus` | TikTok legacy 字面量 `1` | Creator 的 `encode_x_bogus`；IM frontier 是 16 字符 |
| `sign` | 闲鱼/淘宝 H5 MD5 | 闲鱼 App 的 `x-sign`，网关和 appKey 都不同 |
| `msToken` | mssdk 响应头 | 本地 `generate_msToken()` 随机串 |

画表时写生产函数名，不写参数名。参数名会跨面复用。
