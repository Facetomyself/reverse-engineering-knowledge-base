# 头条案例：a_bogus 与 _signature 是两包 execjs

> 来源: `workspace/cv-cat`（HeadlineApis，HEAD 日期 2026-08-18，只读对照）
> 原始发布时间: 2026-08-18
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> 头条信息流在这份对照仓里同时带 `a_bogus` 和 `_signature`。它们来自两个 JS 包，而且都不是抖音 `DouYin_Spider` 的 Python 纯算。feed 的 `aid` 是 `24`。

## 两个入口

`utils/tou_tiao_utils.py` 启动时编译两份脚本：

| 函数 | JS | 导出 |
|------|----|------|
| `generate_a_bogus(query, data="")` | `static/dy.js` | `get_ab` |
| `generate_sign(url)` | `static/sign.js` | `genserate_sign`（源码拼写就是少了一个 e） |

`generate_msToken` 是本地随机串，默认长度 107。它和抖音仓里的同名函数一样，不是 mssdk 签发值。把这个随机串当成已过服务端，会和抖音案例里的反面教材相同。

## 案例：信息流

`tou_tiao_api.py` 的 feed 路径：

1. query 写 `aid=24`。这不是抖音主站的 `6383`，也不是创作者的 `1128`。
2. `Params.with_a_bogus()` 用 `splice_url` 拼 query，再调用 `get_ab`。
3. 另一条请求在 URL 定下来之后调用 `generate_sign(url)`，把结果放进 `_signature`。

```text
query = ordered_pairs(aid="24", ...)
query.a_bogus = dy_js.get_ab(splice(query), data)
url = origin + path + "?" + query
query_or_header._signature = sign_js.genserate_sign(url)
send url
```

`sign.js` 文件里嵌有一份历史 Cookie 样例。那是作者捕获，不能抄进请求，也不能当成算法常量。

## 和抖音纯算的边界

| 项 | HeadlineApis | DouYin_Spider |
|----|--------------|---------------|
| `a_bogus` | execjs `dy.js` 的 `get_ab` | `ab_pure.ABogusPureSigner` |
| host / aid | feed `aid=24`，函数不吃 host | `app_ids_for(host)` |
| `_signature` | 第二包 `sign.js` | 主站查询链没有这个字段 |
| msToken | 本地随机 | 另有 mssdk `get_mstoken` |

头条算对 `a_bogus` 不能解释抖音 webSign 或 TicketGuard。反过来，把抖音纯算模块套到 `aid=24` 的 feed 上，也越出了这份仓的调用点。

## 证据边界

两包 JS 的函数体不入库。`aid=24` 只对当前 feed 调用点成立。本库没有重放头条接口。
