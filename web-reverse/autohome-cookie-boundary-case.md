# 汽车之家案例：Cookie 加 JSONP，没有本地 sign

> 来源: `workspace/cv-cat`（AutohomeApis，HEAD 日期 2026-08-18，只读对照）
> 原始发布时间: 2026-08-18
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> 汽车之家在这份对照仓里没有签名函数。详情接口是带 Cookie 的 JSONP，创作者接口只追加时间戳和 `_appid`。案例价值是把「没有算法」写成明确的请求边界，避免以后把空响应误判成签名缺失。

## 案例：帖子详情

`CarApis.get_detail`：

1. `get_headers()` 取浏览器头，`trans_cookies` 解析调用方 Cookie。
2. GET `https://clubajax.autohome.com.cn/topic/rv`。
3. query：`fun=jsonprv`、`callback=jsonprv`、`ids` 为作品 id 加逗号、`r` 和 `_` 来自 `get_time()`。
4. 响应文本去掉前 8 个字符和最后 1 个字符，再 `json.loads`。这是剥 `jsonprv(...)` 外壳，不是解密。
5. 返回数组的第一项。

```text
cookie = caller_cookie
_, r = timestamps()
text = GET clubajax.../topic/rv
       ? fun=jsonprv & callback=jsonprv & ids={id}, & r & _
body = json.loads(text[8:-1])
return body[0]
```

用户主页 URL 用来切 `user_id`：含 `/club` 时取其前一段，否则取路径最后一段。这是路由解析，不是签名。

创作者侧 `car_home_creator_apis.py` 打 `club-open-api` / `sou.api` 一类 host，参数是时间戳和 `_appid`，源码里没有 encrypt/sign 调用。`_appid` 是端别常量，换接口要按该文件的字面量，不能从详情 JSONP 推断。

## 失败怎么读

JSONP 剥壳失败（长度不足、前缀不是 `jsonprv`）是响应形态变了。Cookie 缺失时更可能是登录墙或空列表。两件事都不是「缺 a_bogus」。时间戳只用于 cache-bust，源码没有把它哈希进某个头。

## 证据边界

本库没有请求 autohome。`_appid` 的具体数字以创作者文件为准，不在本篇展开成可直接打生产的客户端。
