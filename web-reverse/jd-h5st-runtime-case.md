# 京东案例：h5st 5.3 运行时、body 预哈希、JCAP 分链

> 来源: `workspace/cv-cat`（JdApis，HEAD 日期 2026-09-19，只读对照）
> 原始发布时间: 2026-09-19
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> 京东 PC 搜索在这份对照仓里不是 execjs 喂整包 `JD.js`。它是常驻 Node：环境、未改的 js_security 库、一行协议的签名服务。业务 h5st 要等 cactus 返回 `tk03`。登录验证码是另一条 JCAP 链。

协议层见 [京东 h5st](./products/jd-h5st.md)。题型分流见 [JCAP](./products/jd-jcap-captcha.md)。本篇不抄 `ParamsSign` 函数体。

## 三段运行时

| 文件 | 职责 |
|------|------|
| `static/h5st5_env.js` | jsdom 指纹面、Cookie 注入、访问 cactus 的 XHR、token 缓存钩子 |
| `static/h5st5_lib.js` | 现网 `js_security_v3_0.1.6.js` 原文，不在 Python 里重写 |
| `static/h5st5_server.js` | 加载前两者，stdin JSON，`new ParamsSign({appId}).sign(params)`，stdout 回 h5st |
| `utils/h5st5.py` | 子进程门面。`_is_real_token` 要求 h5st 按 `;` 切开的第 4 段以 `tk03` 开头 |

`h5st5.py` 写明：`tk03` 是服务端真 token，`tk04` / `tk06` 是库的本地兜底，业务接口不认。`sign(..., warmup=True)` 若第一次不是 tk03，会按 0.35 / 0.6 / 1.0 秒重签。request_algo 没有单独的 Python 客户端，它发生在库内部，经 env 里的 XHR 打到 cactus。token 按画像 id 落在本地缓存文件，不能换 Cookie 还用旧缓存。

## 案例：搜索 searchWare

`JdAPI.search` 的 functionId 是 `pc_search_searchWare`。`call_api` 在签名前：

1. `h5st5.configure(cookie, origin, referer)`。签名进程换 token 用的 Cookie 必须和业务请求同域。
2. 从 Cookie `3AB9D23F7A4B3CSS` 取出 `x-api-eid-token`。它每个请求都带，但不进 h5st 摘要。
3. 头按 axios 或 fetch 两套顺序重排。判据是有没有 `x-rp-client`。
4. 每次重试重新取 `t`，再 `with_h5st`。重放同一个 h5st 没有意义。
5. query 用键值列表送到客户端。搜索 URL 有两个同名 `t`，普通 dict 会吞掉一个。`append_time` 时在列表末尾再追加一个 `t`。

`Params.with_h5st` 的合同：

- 参与签名的 body 是原 JSON 的 SHA-256。query 或表单仍发原 JSON。注释写明实网 A/B：原 JSON 直接参与签名会 403，预哈希版本返回 `code=0`。
- query 里的 `t` 必须是签名时用的那个 `t`。h5st 内部另一段时间戳差几毫秒，不能拿来覆盖 `t`。
- JSON 分隔符带空格会导致 SHA-256 不一致。

```text
configure(cookie, origin, referer)
body_json = compact_json(search_body)
sign_body = sha256_hex(body_json)
h5st = node_params_sign(appId="f06cc", body=sign_body, t=t, ...)
require h5st.split(";")[3] starts with "tk03"
POST /api
  query pairs include functionId, t, h5st, x-api-eid-token, and a second t
  form body = original body_json
```

搜索 appId 在源码里是 `f06cc`。这是抓包窗口的业务 appId，换页面要重核。

WebM 页指纹 Cookie 和 eid 票据是另外两条材料。`ensure_webm_token` 不能被 eid 或 h5st 替代。设备票据经本机管道生成，源码要求不写日志。

## 登录路径

短信/扫码登录在搜索链之外还要处理 JCAP。`vt` 来自验证码 check，不是 h5st 的产物。登录提交同时带 h5st 和验证码 token 时，两条失败不能互相解释。题型以响应里的 `tp` 为准，脚本名里出现 slide 不等于已经出了滑块。

## 和旧仓的差分

公开仓曾经用整包 `static/JD.js` 并写成 h5st 4.2。现行对照是 5.3，库文件名是 `js_security_v3_0.1.6.js`，并且必须经过 cactus。把 execjs 整包出参标成纯算，或把 request_algo 阶段的 tk06 填进业务 h5st，都会和这份源码的完成门不一致。

## 证据边界

`code=0` 的 A/B 是对照仓注释，本知识库没有重跑。js_security 正文不收录。
