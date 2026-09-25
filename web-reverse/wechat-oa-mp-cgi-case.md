# 公众号后台案例：token 透传，不是 mmtls

> 来源: `workspace/cv-cat`（WechatOAApis，HEAD 日期 2026-08-18，只读对照）
> 原始发布时间: 2026-08-18
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> 这份对照仓打的是已登录的 `mp.weixin.qq.com` 后台 CGI。`token` 和 Cookie 由调用方从开发者工具复制，仓内不登录、不刷新、不算 fingerprint。它不是微信客户端 mmtls，也不是内置浏览器的 `getmsg`。

会话平面对照见 [微信公众号五套会话](../protocols/wechat-mp-session-planes.md)。

## 案例：搜号再拉发表列表

`apis/wx_apis.py`：

1. `get_fakeid`：GET `https://mp.weixin.qq.com/cgi-bin/searchbiz`。参数来自 `get_fakeid_params`：`action=search_biz`、`query`、`token`、`begin`、`count`、`lang=zh_CN`、`f=json`、`ajax=1`。
2. 成功看 `base_resp.ret == 0`，再从列表取 `fakeid`。`ret != 0` 用 `err_msg`，不能把 HTTP 200 当搜到了号。
3. `get_shop_works`：GET `https://mp.weixin.qq.com/cgi-bin/appmsgpublish`。参数含 `sub=list`、`fakeid`、`token`、`type=101_1`、`free_publish_type=1`、`sub_action=list_ex`。
4. `publish_page` 是字符串，要再 `json.loads` 一次。
5. 翻页 `begin` 步进 5，直到超过 `total_count`，中间 `sleep`。这是后台频控间隔，不是签名窗口。

```text
token, cookie = capture_from_mp_devtools()
biz = GET /cgi-bin/searchbiz ? action=search_biz & query & token
require base_resp.ret == 0
fakeid = biz.list[0].fakeid
begin = 0
while begin <= total:
    page = GET /cgi-bin/appmsgpublish ? sub=list & fakeid & token & begin & count=5
    works += json.loads(page.publish_page)
    begin += 5
```

头在 `wx_utils.get_common_headers`：AJAX 头，referer 指向后台编辑页形态。referer 模板里若写死了一个历史 token 数字，那是样例，不是运行时 fingerprint。全仓没有设备指纹计算。

## 文章 HTML 是另一面

`get_work_detail` 对调用方给的 `mp.weixin.qq.com/s?...` 做 GET，不传 token 和 Cookie。BeautifulSoup 取 `og:title`、作者、`#js_content`、图片 `data-src`，再用正则取 `createTime`。这条公开 HTML 面失败，不能用后台 `token` 过期来解释；反过来，后台 `ret != 0` 也不能靠重试这篇 HTML 修好。

## 证据边界

`token`、`slave_sid` 一类 Cookie 不入库。`list_ex` 的字段名以当前后台为准；2026 年后台收紧后，同一 URL 可能改返回验证页，届时 `ret != 0` 仍是失败。本库没有请求 mp.weixin.qq.com。
