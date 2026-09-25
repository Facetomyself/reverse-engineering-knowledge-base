# 币安案例：公告列表的设备头，不是交易签名

> 来源: `workspace/cv-cat`（BinanceApis，HEAD 日期 2026-08-18，只读对照）
> 原始发布时间: 2026-08-18
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> 这份对照仓轮询的是公开 CMS 公告列表，不是交易 API 的 HMAC。本地 JS 填 `csrftoken`、设备指纹和 `fvideo-token`；`fvideo-id` 直接来自 Cookie。

## 案例：一页公告

`BinanceApis.spider_one_page`：

1. Cookie 由调用方从浏览器复制。README 要求含 `BNC_FV_KEY` 和 `BNC_FV_KEY_T`。`trans_cookies` 只按 `; ` 切分。
2. 每次请求新的 `bnc-uuid` 和 trace id。
3. `device-info` 来自一份硬编码画像：`generate_canvas_code`、`generate_fingerprint`，再 `generate_deviceinfo` 做成 Base64。画像原值不入库。指纹是字段排序后的类 murmur，具体轮函数留在 `static/News.js`。
4. `csrftoken` 是 `news_utils.generate_csrftoken()`，即 JS `md5("")`。这是本地固定算法填头，本仓没有证明服务端强校验这个值。
5. `fvideo-id` 等于 Cookie 的 `BNC_FV_KEY`。`fvideo-token` 把 `BNC_FV_KEY_T` 交给 `generateFvideotoken`。两个 Cookie 字段职责不同，不能互换。
6. GET `https://www.binance.com/bapi/apex/v1/public/apex/cms/article/list/query`，query 为 `type=1`、`pageSize=20`、`pageNo`。
7. 代码直接 `response.json()`，没有看 HTTP status 或业务 `code`。轮询成功口径是 `data.catalogs[].articles[]` 相对上一轮首条的差分。

```text
cookies = parse(browser_cookie)            # BNC_FV_KEY, BNC_FV_KEY_T
headers = {
  bnc-uuid: uuid4(),
  csrftoken: js.md5(""),
  device-info: b64(json(profile_plus_canvas_and_fingerprint)),
  fvideo-id: cookies.BNC_FV_KEY,
  fvideo-token: js.fvideo(cookies.BNC_FV_KEY_T),
  clienttype: "web"
}
page = GET article/list/query
diff catalogs[0].articles against previous first item
```

## 落地判断

| 头 | 出处 |
|----|------|
| `fvideo-id` | 服务端/浏览器 Cookie，本地不造 |
| `fvideo-token` | execjs，输入是另一个 Cookie 字段 |
| `csrftoken` | 本地 `md5("")` |
| `device-info` | 硬编码画像 + JS 指纹，绑定这份捕获环境 |

交易签名、API secret、下单参数不在这个仓里。公告差分失败时先看 Cookie 是否还含两个 FV 字段，再看 JSON 形状，不要把它当成交易 HMAC 算错。

## 证据边界

`News.js` 的 fvideo 拼装和字母表不入库。画像里的分辨率、WebGL 字符串是作者机器捕获，不能贴到另一份 Cookie。本库没有请求币安。
