# MP 后台跨号列表与 2026-07-30 收紧

> 来源: `workspace/weixin_download` 对照 wechat-article-exporter、EasyWechatDownload、we-mp-rss、wechat-download-api
> 原始发布时间: 2026-07-16 / 2026-07-30 / 2026-08-23
> 归档日期: 2026-09-15
> 分类: mobile-app-reverse
>
> 公众号后台扫码会话曾被用来 `searchbiz` + `appmsgpublish list_ex` 跨号枚举。2026-07-30 上游关闭、多项目 `ret=200013`，默认 fail-closed。`free_publish` 是本号已发表列表，不是任意 `__biz` 历史。操作者必须具备后台登录资格。

## 这条路是什么

登录主体是「能进公众号后台的微信」，不是任意个人号。纯 HTTP 出码、手机扫码/确认不可消除。典型链（停更前源码）：

```text
bizlogin startlogin
  -> scanloginqrcode getqrcode / ask
  -> bizlogin login
  -> searchbiz          （目标号 fakeid）
  -> appmsgpublish list_ex
```

[wechat-article/wechat-article-exporter](https://github.com/wechat-article/wechat-article-exporter)（MIT，对照提交 `55217d4f`）把「没有可登录账号」「未绑定邮箱」写成登录状态机，证明资格检查是协议的一部分：`acct_size < 1`、邮箱未绑定都应 `AUTH_REQUIRED`，不是临时网络错误。

## 2026-07-30 之后

| 证据 | 内容 |
|------|------|
| exporter [issue #200](https://github.com/wechat-article/wechat-article-exporter/issues/200)（2026-07-30） | 上游核心接口关闭，项目停更。作者：credential 旁路从未进主流程，不构成替代 |
| 独立复现（LovStudio 2026-08-01 等） | 跨号第一页零结果出现 `ret=200013` |
| exporter README | 在线域名曾写 2026-10-30 到期；停更声明与 8 月审计一致 |
| [yangbuyiya/EasyWechatDownload](https://github.com/yangbuyiya/EasyWechatDownload) | 「平台模式」仍是 MP 扫码 + 搜索 + 历史；最新 release 2026-07-14，收紧前两周，不能当 9 月可用性 |
| [tmwgsicp/wechat-download-api](https://github.com/tmwgsicp/wechat-download-api) | AGPL；最后推送 2026-07-27。issue #7/#8：后台登录态约 4 天，到期仍须扫码；监测只能提示过期 |
| [rachelos/we-mp-rss](https://github.com/rachelos/we-mp-rss) | `free_publish` → `appmsgpublish` → `appmsg` 降级。源码注释：新版**已发表列表**，优先本号，不是跨号任意历史 |

前端 bundle 里仍能扫到 `list_ex` 参数形状，不等于服务端对第三方开放。默认 **live-pending / protocol-invalid**，恢复前必须重测。

## 可复用的（仍然有效）

- MP QR 的 HTTP 传输形态：出码、轮询、扫码确认、session 过期进 `AUTH_REQUIRED`。
- 资格门：无后台账号、未绑邮箱、权限失败都是稳定 outcome，禁止当 5xx 重试。
- 本号 `free_publish` 若 live 通过，只承诺「操作者自己的已发表稿」，不要写进「任意公众号历史」。
- 后台 Cookie + `token` **不能**刷新 WebView `uin/key`。两套会话。

## 不要做的

- 把 7 月的源码审查写成当前跨号可用。
- 用 MP session 去调 `profile_ext/getmsg`。
- 把停更仓库的 Stars 当健康指标。
- 操作者没有后台资格时，对外说「扫个码就能拉任意号历史」。
