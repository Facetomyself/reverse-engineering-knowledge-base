# 百家号案例：页面 runtime 供 uk，Cookie 供 Tenger-Mhor

> 来源: `workspace/cv-cat`（BaijiaApis，HEAD 日期 2026-08-18，只读对照）
> 原始发布时间: 2026-08-18
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> 百家号/百度网页在这份对照仓里没有 gtoken 或 sign 的本地实现。`uk` 来自页面 `window.runtime`，请求头 `Tenger-Mhor` 直接等于 Cookie `Hmery-Time`。传输用 curl_cffi 的 chrome101 profile。

## 案例：作者页与列表

`baidu_apis.py`：

1. 先取页面，从 `window.runtime` 解析 `uk`、`otherext` 一类字段。这些是服务端写进 HTML 的，不是本地随机。
2. 后续请求头 `Tenger-Mhor` 设为 `str(cookies["Hmery-Time"])`。缺这个 Cookie 键会在组头时失败。
3. 列表打 `mbd.baidu.com/webpage` 一类 JSONP。响应要剥回调壳再解析。
4. HTTP 客户端是 curl_cffi，impersonate 为 `chrome101`。这是传输档，不产生签名。

```text
html = GET author or article page with cookie
uk, otherext = parse window.runtime
headers["Tenger-Mhor"] = cookies["Hmery-Time"]
body = unwrap_jsonp(GET mbd.baidu.com/webpage ? uk & ...)
```

`utils/baidu_utils.py` 只做头模板和 Cookie 切分，没有哈希函数。仓内搜不到 gtoken 生成。若新抓包出现 gtoken，那是这份 2026-08 树没有覆盖的另一条链，不能用 `Tenger-Mhor` 去填。

## 可复用点

页面 runtime 和 Cookie 头是两类材料。runtime 随 HTML 变，Cookie 头随会话变。只更新其中一个，另一个仍会让列表空。JSONP 剥壳失败要先看回调名，而不是去找一个不存在的 sign。

## 证据边界

不收录 `uk`、`Hmery-Time` 或 runtime 原值。chrome101 是这份仓选择的 impersonate 名，不等于当前百家号页面的 UA。本库没有请求百度。
