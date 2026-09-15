# 微信公众号五套会话：登录态不是 getmsg

> 来源: `workspace/weixin_download` 开源库与协议对照
> 原始发布时间: 2026-07-16 至 2026-09-13
> 归档日期: 2026-09-15
> 分类: protocols
>
> 微信客户端在线、公众号 WebView、公众号后台、微信读书、原生 CGI（GetA8Key）是五套互不续期的会话。公开 GitHub 下载器失败的第一原因是把它们当成同一个 Cookie。本文只保留平面划分、字段边界和完成门；凭证原值与可执行客户端不收录。

## 定位

遇到「微信公众号历史 / 推文下载 / 内置浏览器 H5」时，先用本文把目标钉到一个平面，再去 [开源库对照合集](../mobile-app-reverse/wechat-mp-oss-landscape.md) 看具体仓库。不要从 [mmtls 协议分析](./mmtls-protocol-analysis.md) 直接跳到 `getmsg`：那篇还原的是应用宝 / WMPF 登录栈，不是个微 iPad 协议，也不是 `mp.weixin.qq.com` HTTPS。

```text
新 GitHub / 新接口
        ↓
钉到本文五套会话之一（禁止混用 Cookie / token / key）
        ↓
看该平面的开源实现是否还活、覆盖范围是什么
        ↓
才决定：公开 URL 归档 / 短时 getmsg / 读书列表 / CGI 发证 / 只做调试观察
```

## 五套会话

| # | 会话 | 载体 | 能做什么 | 不能做什么 | 公开续期 |
|---|------|------|----------|------------|----------|
| 1 | 客户端登录 | PC `Weixin.exe` / 手机 `com.tencent.mm`，原生多为 mmtls | 保持客户端在线，打开内置浏览器 | 直接当 `getmsg` 的 HTTP Cookie | 无；进程活着不等于已发证 |
| 2 | 公众号 WebView | 内置浏览器访问 `mp.weixin.qq.com` | 签发短时 `uin/key/pass_ticket`，调 `profile_ext/getmsg`、评论、阅读量 | 由客户端登录态自动续期 | 未发现纯 HTTP refresh；公开经验约 25 分钟，须 live 测 |
| 3 | 公众号后台 MP | `mp.weixin.qq.com/cgi-bin` Cookie + `token` | 本号管理、扫码登录；2026-07-30 前部分实现用 `searchbiz` + `appmsgpublish list_ex` 跨号列表 | 刷新 WebView 凭证；跨号 `list_ex` 默认 live-pending | 扫码会话；`tmwgsicp` issue 记录约 4 天仍须重新扫码 |
| 4 | 微信读书 | `i.weread.qq.com` 移动端 + `weread.qq.com` Web | QR 登录后 `vid/accessToken/refreshToken`；`/mp/chapters` 按 `MP_WXS_<BID>` 分页 | 任意未入库号的完整历史；替代 `getmsg` 拉阅读量/精选评论 | 有 HTTP RefreshToken（续的是读书会话，不是 `getmsg`） |
| 5 | 原生 CGI | iPad/Android 协议号的 `GetA8Key` / `MpGetA8Key` | 对一条 `mp.weixin.qq.com` URL 签发 A8Key，结果可喂 `getmsg` | 协议号本身不是历史翻页 API；type 10039 不是 `general_msg_list` | 协议会话不断时可反复 CGI；key 仍短时。商业栈闭源，Gewechat 已停 |

官方开放平台 OAuth `refresh_token` 是第六套授权域，不能续上面任何一套私有 session。

## 完成门（先于选库）

| 门槛 | 含义 | 不够格 |
|------|------|--------|
| `localReproduced` | 请求 URL/query/Cookie 形状与对照实现或 HAR 对齐 | 脚本不报错、字段「看起来像」 |
| `serverAccepted` | 独立 TLS 拿到非空业务 readback：`getmsg` 要 `ret=0` 且 `general_msg_list` 非空 | HTTP 200、空 JSON、空列表、验证页 |
| `issuanceComplete` | 凭证来自该平面自己的发证路径，并能过一次业务探针 | 磁盘里扫到过期 `uin/key`；客户端仍登录 |
| `sessionConsistent` | 列表、正文、统计用同一套会话 | WebView key 去打 MP `list_ex`；读书 token 去打 `getappmsgext` |

空成功是第一诊断对象：`getmsg ret=-3` 返回 0 篇、验证页当正文、`list_ex ret=200013` 当「这个号没有文章」。这些不是「再改一版签名」，而是钉错了平面或凭证已死。

## 平面 2：WebView `getmsg`

发证条件是 **内置浏览器对 `mp.weixin.qq.com` 发起请求**，不是微信进程还活着。

典型入口：

```text
https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=<biz>&scene=124#wechat_redirect
https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=<biz>&...
```

对照实现反复出现的短时参数：`uin`、`key`、`pass_ticket`，以及后续统计/评论用的 `poc_token` / `appmsg_token`。文章身份优先 `__biz + mid + idx`，不要用标题或目录名。列表字段要认 `general_msg_list`、`can_msg_continue`、`next_offset`；缺这三项就不是这条协议。

原工具 [qiye45/wechatDownload](https://github.com/qiye45/wechatDownload) 4.7（2026-08-16）仍是：把链接放到文件传输助手，人在内置浏览器打开，软件扫 `xwechat` 缓存。这不是纯协议 refresh。[wxdown-service](https://github.com/wechat-article/wxdown-service) 只 MITM 收证、不触发微信。细节见 [getmsg WebView 发证](../mobile-app-reverse/wechat-mp-oss-landscape/getmsg-webview-issuance.md)。

## 平面 3：MP 后台

登录主体不是任意个人微信：扫码号必须能进至少一个公众号后台（邮箱绑定、`acct_size`）。跨号历史曾经走：

```text
bizlogin startlogin
  -> scanloginqrcode getqrcode / ask
  -> bizlogin login
  -> searchbiz
  -> appmsgpublish list_ex
```

2026-07-30 起 [wechat-article-exporter issue #200](https://github.com/wechat-article/wechat-article-exporter/issues/200) 停更，跨号 `list_ex` 出现 `ret=200013`。`free_publish` 更像**本号已发表列表**，不能默认当成任意 `__biz` 历史。见 [MP 后台 list_ex](../mobile-app-reverse/wechat-mp-oss-landscape/mp-backend-list-ex.md)。

## 平面 4：微信读书

身份映射（开源已写清）：

```text
文章 URL 或页面 -> __biz（Base64）
  -> 十进制 BID
  -> bookId = "MP_WXS_" + BID
```

移动端列表互斥形状（[weread-omni](https://github.com/teng-lin/weread-omni) 源码硬约束）：

```text
GET https://i.weread.qq.com/mp/chapters
  首请求: bookId=&count=20&synckey=0     （不要带 offset）
  翻页:   bookId=&count=&offset=         （不要带 synckey）
```

RefreshToken 只在 HTTP `401/403` 或业务码 `-2012` 时续一次并重放；`-2041`、`-2010`、HTTP 429 是风控，禁止 refresh 循环。主键在读书侧是 `reviewId`，接归档仓时必须映射回 `__biz+mid+idx`，禁止第三套 identity。见 [微信读书 mp/chapters](../mobile-app-reverse/wechat-mp-oss-landscape/weread-mp-chapters.md)。

覆盖边界：能搜到并可 `shelf.add` 的号 ≠ 任意公开号完整历史。官方微信读书 Agent Skill（`wrk-`）不含公众号列表。

## 平面 5：GetA8Key

原生打开公众号页走 `NetSceneGetA8Key`。社区用协议号调同一 CGI 后，返回 URL / `X-WECHAT-KEY` / `X-WECHAT-UIN` 可喂 `profile_ext?action=getmsg`。结论是：**`getmsg` 的 `key` 是 A8Key 签发结果，不是页面 JS 算出来的。**

因此协议号只适合当**发证 sidecar**，不适合当下载器。商业实现闭源、Gewechat 已停，不能 vendoring。未 live 证明之前，不得把「任意未关注 `__biz` 的 home 发证」写成已验证。见 [GetA8Key 原生 CGI](../mobile-app-reverse/wechat-mp-oss-landscape/geta8key-native-cgi.md)。

## 调试平面不是第六套会话

[WeChat-H5-DevTools](https://github.com/xuange520/WeChat-H5-DevTools) / WMPFDebugger 打开的是 4.x 内置浏览器的 DevTools / vConsole。它们可以**观察**平面 2 的发证流量，不能**替代**发证。外部 Chrome 注入 `WeixinJSBridge` Mock 只能过「请在微信客户端打开」的 JS 门，签发不了真 key。见 [WMPF H5 调试面](../mobile-app-reverse/wechat-mp-oss-landscape/wmpf-h5-debug-plane.md)。

## 禁止混用的对照

| 错误做法 | 实际发生的事 |
|----------|----------------|
| PC/手机已登录 → 直接调 `getmsg` | 过期或空 `uin/key`，`ret=-3` |
| 用 OAuth `refresh_token` 续 `getmsg` 或 MP Cookie | 授权域不同，续不上 |
| 读书 `accessToken` 调 `getappmsgext` | 统计/精选评论仍要 WebView 凭证 |
| 把 type 10039「历史推送」当 `getmsg` 分页 | 没有 `general_msg_list` / `next_offset` |
| `wx-h5 open` 外部浏览器当登录态下载 | 验证页 / 空壳，P0 `CONTENT_INVALID` |
| 3.9 `WeChatWin.dll` 偏移套 4.x | 4.1.x 进程是 `WeixinExt.exe` / renderer，内核 RadiumWMPF 255xx |

## 证据边界

本文来自 `weixin_download` 对公开仓库与文档的源码审查（2026-07-16、2026-07-28、2026-08-23、2026-09-13），**不是** 2026-09 之后的 live probe。`list_ex` 跨号、GetA8Key 对未关注 home、`/mp/chapters` 截断页数均标 live-pending。后续 case 只复用平面划分和字段名，可用性以当时探针为准。

## 速查

| 题目 | 先看 |
|------|------|
| 这个 GitHub 到底在用哪套 Cookie | 本文五套表 |
| 具体仓库死活、接口形状 | [开源库对照](../mobile-app-reverse/wechat-mp-oss-landscape.md) |
| 已复现的 HTTPS 字段与完成门 | [HTTP 接口面](./wechat-mp-http-surface.md) |
| 身份 / claim / MCP job | [归档运行时](../collection-engineering/weixin-http-archive-runtime.md) |
| 腾讯私有 TLS / WMPF 登录 | [mmtls](./mmtls-protocol-analysis.md) |
| App 空壳 / 注册不等于激活 | [协议准入四关](../mobile-app-reverse/protocol-admission-four-gates.md) |
