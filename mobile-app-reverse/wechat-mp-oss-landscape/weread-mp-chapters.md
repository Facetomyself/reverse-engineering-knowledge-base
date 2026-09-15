# 微信读书公众号列表与 RefreshToken

> 来源: `workspace/weixin_download` 对照 weread-omni、wechrss、we-mp-rss、wewe-rss
> 原始发布时间: 2026-08-23 / 2026-09-13
> 归档日期: 2026-09-15
> 分类: mobile-app-reverse
>
> 微信读书是第四套会话：个人微信开通读书后 QR 登录，用 `MP_WXS_<BID>` 调 `/mp/chapters` 分页。这是 `getmsg` 之外少见的、带 HTTP RefreshToken 的历史源。覆盖的是读书侧能上架/加书架的号，不是任意公开号完整历史。官方 `wrk-` Skill 不含公众号。

## 身份映射

短链 `https://mp.weixin.qq.com/s/<token>` 不含 `__biz`。开源路径：

```text
文章 URL
  -> query 或 HTML 拿到 __biz（Base64）
  -> 解码为十进制 BID
  -> bookId = "MP_WXS_" + BID
```

[johamwon/wechrss](https://github.com/johamwon/wechrss) `article_identity.py`：URL query → 普通 HTTP HTML → Playwright **仅添加订阅时**回退。周期同步不应依赖浏览器。已有公开页 `__biz` 提取的项目不必再引入 Playwright 主路径。

## 登录与续期

wechrss / weread-omni 同源形状：

```text
GET 微信读书 wxticket
  -> GET open.weixin.qq.com/connect/sdk/qrconnect
  -> 轮询 long.open.weixin.qq.com/connect/l/qrconnect
  -> POST i.weread.qq.com/login
  -> 保存 vid / accessToken / refreshToken / deviceId
```

操作者是「开通了微信读书的个人微信」，**不要求公众号后台资格**。扫码/确认仍不可消除。

RefreshToken 合同（wechrss 文档）：

| 条件 | 动作 |
|------|------|
| 读请求最少 | `vid + accessToken` |
| 自动续期还要 | `refreshToken + deviceId + 匹配的设备 profile` |
| HTTP 401/403 或业务码 `-2012` | refresh **一次**并重放原请求 |
| `-2041`、`-2010`、HTTP 429 | 风控。禁止用 refresh 循环撞 |

这续的是读书会话，不是 `profile_ext/getmsg`。公开实现常用 e-ink / BOOX 一类 header profile；探针必须锁定，禁止把 Web Cookie 和移动端 token 混用。

## 列表协议

[teng-lin/weread-omni](https://github.com/teng-lin/weread-omni) `src/api/resources/public-accounts.ts`（2026-09-11 仍更新）把两种 query **写成硬约束**，短页表示耗尽：

```text
GET https://i.weread.qq.com/mp/chapters
  首请求: bookId=MP_WXS_<BID>&count=20&synckey=0     （不要带 offset）
  翻页:   bookId=&count=&offset=                     （不要带 synckey）
```

CLI `public-accounts articles` 默认 20、`--limit` 最大 100，是产品上限，不是协议上限。

[rachelos/we-mp-rss](https://github.com/rachelos/we-mp-rss) 2026-09-04/10 把 Web 列表 `GET https://weread.qq.com/web/mp/articles?bookId=&offset=` 升回主路径，`/api/mp/cover` 只取最新一篇作失败兜底。仓库内旧文档曾写「cover 只返回最新一篇、`/web/mp/articles` 恒 -2041」，与 9 月源码不一致，以源码为准。

正文两条：读书 `GET weread.qq.com/web/mp/content?reviewId=` 抽 `#js_content`；或回填后的 `https://mp.weixin.qq.com/s/...`。工具 UA 可能 302 到 `wappoc_appmsgcaptcha`，按内容无效处理，不绕过。

主键在读书侧是 `reviewId`。接入归档仓必须映射到 `__biz+mid+idx`，禁止第三套 identity。

## 反面：wewe-rss

[cooderl/wewe-rss](https://github.com/cooderl/wewe-rss) 2026-05-11 归档。公开复盘指出它是自托管壳 + 闭源中转；中转可 502。不能再当微信读书可用性证据。活对照是直连 `weread.qq.com` / `i.weread.qq.com`。

## 覆盖边界

能做：读书搜得到、并可 `shelf.add` 的号；有效会话内分页、增量 `synckey`；过期 refresh 一次，失败再扫码。

不能声称：未入库号的完整历史；读书侧没有的旧文/删除文/付费私密文；永久零扫码；用官方 `wrk-` Skill 拉公众号；把 `-2041`/429 当临时网络错误轰炸。

`getmsg` 的阅读量和精选评论仍要 WebView 凭证，读书列表替代不了那两套接口。
