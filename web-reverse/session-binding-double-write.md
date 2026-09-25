# 技巧：会话材料双写，并且绑源

> 来源: `workspace/cv-cat`（微博 XSRF、领英 JSESSIONID、X 的 ct0、飞书 swp_csrf_token、抖音 uifid / creator CSRF）
> 原始发布时间: 2026-09-23
> 归档日期: 2026-09-24
> 分类: web-reverse
>
> 不少「签名头」只是把同一会话材料再写到一个头或 query 里。技巧是找出源字段、去掉包装、绑到正确的 origin。源变了，副本必须一起变。本地哈希出的另一串不能拿来填这个头。

## 双写对照

| 站点 | 源 | 副本 | 变换 |
|------|----|------|------|
| 微博 PC | Cookie `XSRF-TOKEN` | 头 `x-xsrf-token` | 原样 |
| 领英 | Cookie `JSESSIONID` | 头 `csrf-token` | 去掉引号 |
| X | Cookie `ct0` | 头 `x-csrf-token` | 原样，与 Bearer 并列 |
| 飞书 | POST `/accounts/csrf` 的 Set-Cookie `swp_csrf_token` | 头 `x-csrf-token` | 先换票再双写 |
| 抖音 | Cookie `UIFID` | query `uifid` 和头 `uifid` | 多数 XHR 两处都带 |
| 抖音创作者 | 向 creator origin HEAD 换到的 token | 头 `x-secsdk-csrf-token` | 必须打 creator，不能打 www |
| 币安 | Cookie `BNC_FV_KEY` | 头 `fvideo-id` | 原样。`BNC_FV_KEY_T` 是另一个字段，只做 `fvideo-token` 的输入 |
| 京东 | Cookie `3AB9D23F7A4B3CSS` | query `x-api-eid-token` | 原样，不进 h5st 摘要 |
| 百家号 | Cookie `Hmery-Time` | 头 `Tenger-Mhor` | 原样 |

```text
source = read_source(cookie or set_cookie or html)
copy = unwrap(source)              # strip quotes, take segment before '_', nothing else
write header_or_query = copy
if origin_of(source) != origin_of(request):
    fail                           # creator token from www is a known miss
```

## 绑源的真实失误

抖音创作者发布的注释写明：早先固定向 www 换 CSRF，token 和 creator 会话对不上。换票 origin、path、referer 都要和业务请求同一站点。

`_m_h5_tk` 的双写不是整段 Cookie。sign 用的是下划线前半段。后半段留在 Cookie 里。把整段拿去 MD5，和只取前半段不是同一个输入。

飞书的 `x-csrf-token` 和 frontier 的 `access_key` 不是双写关系。前者来自 `accounts/csrf`，后者来自页面 JS。长连失败不要去重算 CSRF。

## 不是双写的头

头里有「token」「sign」「csrf」不一定是双写。

- 抖音 `x-secsdk-web-signature` 是 MD5，不是 Cookie 副本。
- 微博上传的 `X-Up-Auth` 是上传凭证，和 `XSRF-TOKEN` 并列。
- 知乎 `x-zse-96` 吃 `d_c0`，但是整包 JS 的输出，不是把 `d_c0` 原样放进头。

判定：在组头函数里搜索这个值是否等于某个 Cookie 键。等于，就是双写，把算法搜索停在这里。不等于，再往哈希或 JS 导出追。
