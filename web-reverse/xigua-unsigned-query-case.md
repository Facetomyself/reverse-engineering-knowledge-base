# 西瓜案例：签名位是空占位，播放解密另算

> 来源: `workspace/cv-cat`（XiguaApis，HEAD 日期 2026-08-18，只读对照）
> 原始发布时间: 2026-08-18
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> 西瓜视频在这份对照仓里没有计算 `msToken`、`X-Bogus` 或 `_signature`。列表和评论把这三个键留空，`aid` 固定为 `1768`。播放地址解密是另一段 AES-CBC，而且当前 API 路径没有调用它。

## 案例：作品列表 query

`builder/params.py` 的作品、评论、搜索参数都写：

```text
aid = "1768"
msToken = ""
X-Bogus = ""
_signature = ""
```

`watermelon_api.py` 用 Cookie 和这组 query 去拉用户、作品、评论、搜索。没有 `with_a_bogus`，也没有 compile 头条的 `dy.js`。`utils/watermelon_utils.py` 虽然 `import execjs`，主路径没有用它做签名。

头里的 `x-secsdk-csrf-token` 在 `builder/header.py` 被设成空串。这是占位，不是已经换到的 CSRF。

```text
cookie = browser_cookie()
query = { aid: "1768", msToken: "", X-Bogus: "", _signature: "", ...biz }
GET ixigua API with cookie and query
parse JSON or HTML
```

和头条的边界：头条 feed 会调用 `get_ab` 和 `genserate_sign`，aid 是 `24`。西瓜这条路径三个签名位都是空的。不能把头条的 execjs 出参填进西瓜的空位，除非新的抓包证明服务端已经开始校验。

## 播放解密函数的形状

`aes_decrypt(data, key)`：

1. 对 `data` 做一次 Base64。
2. key 的 UTF-8 前 16 字节同时当 AES key 和 CBC IV。
3. 解密后 unpad，再做一次 Base64，按 UTF-8 解码。

`__main__` 里有一组捕获样本和 `ptk`。那是夹具，不是稳定协议常量，不入库。当前 `watermelon_api.py` 的列表/评论函数没有调用 `aes_decrypt`。看到这个函数不能推断列表接口已经在解密播放地址。

## 证据边界

空签名位是源码事实，不是「已经证明服务端不校验」。换版本后若抓包里这三个字段非空，这条结论就过期。本库没有打西瓜线上。
