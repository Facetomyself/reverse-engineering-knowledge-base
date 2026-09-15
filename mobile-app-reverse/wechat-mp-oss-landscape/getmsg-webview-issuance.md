# getmsg WebView 发证与短时 key

> 来源: `workspace/weixin_download` 对照 qiye45/wechatDownload、wxdown-service
> 原始发布时间: 2026-07-16 / 2026-08-16 / 2026-08-23
> 归档日期: 2026-09-15
> 分类: mobile-app-reverse
>
> `profile_ext?action=getmsg` 的 `uin/key/pass_ticket` 只在内置浏览器访问 `mp.weixin.qq.com` 时签发。PC/手机登录态不会自动出现这组参数。原工具 4.7 仍靠人打开链接再扫缓存；MITM 服务只收证、不触发微信。

## 这条路是什么

公众号历史列表的 HTTPS 面：

```text
内置浏览器打开
  https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=<biz>&scene=124#wechat_redirect
        ↓ 签发短时 query / Cookie
  GET .../mp/profile_ext?action=getmsg&__biz=...&offset=...&uin=...&key=...&pass_ticket=...
        ↓
  ret=0 且 general_msg_list 非空 才算 serverAccepted
```

同一套会话上常见的后续接口：`getappmsgext`（阅读/点赞）、精选评论、`appmsgalbum` 合集分页。统计和评论不要用读书 token 或 MP 后台 Cookie 去打。

## 对照仓库

| 仓库 | 角色 | 证据 |
|------|------|------|
| [qiye45/wechatDownload](https://github.com/qiye45/wechatDownload) | 行为基线。GitHub 几乎无应用源码 | 4.7（2026-08-16）更新贴图/划线/筛选，发证步骤未变：链接进文件传输助手 → 内置浏览器打开 → 扫本地缓存 |
| [wechat-article/wxdown-service](https://github.com/wechat-article/wxdown-service) | 收证 sidecar | 文档：MITM 拦 WebView HTTPS 提取 credential；过期必须在微信里再打开/刷新一篇文章。不触发微信 |
| 样本「微信公众号批量下载工具 4.6」 | Nuitka 行为恢复 | `scan-keys` / `watch-accounts` 只扫盘；自动获取密钥仍依赖人打开复制的链接 |

公开经验寿命约 25 分钟，必须以 live probe 为准。磁盘里扫到的 candidate 在 2026-07-17 对照里可以全部 `ret=-3 / no session`。

## 字段与失败码

| 项 | 约定 |
|----|------|
| 发证参数 | `uin`、`key`、`pass_ticket`；后续可能出现 `poc_token`、`appmsg_token` |
| 列表成功 | `ret=0`，body 含 `general_msg_list`，翻页看 `can_msg_continue` / `next_offset` |
| 无会话 | `ret=-3`。不得解释成「0 篇成功」 |
| 文章身份 | `__biz + mid + idx`；`sn` 是校验串，不是主键 |
| 正文失败 | 验证页、`wappoc_appmsgcaptcha`、空 `#js_content`、错误 Content-Type → 内容无效，不是网络重试 |

未发现可验证的纯 HTTP refresh endpoint。官方 OAuth `refresh_token` 不在这个授权域。

## 手机 / 原生时间线不能绕过

手机登录仍是 mmtls。新版本「订阅号」时间线经常走私有通道，中间人只能看到封面图，看不到 `general_msg_list`。把 `profile_ext?action=home` 丢进内置浏览器，才会重新出现 `getmsg`。

因此：换手机 ≠ 换协议；无障碍点订阅号 UI ≠ 历史枚举；iPad 协议的推送增量 ≠ `getmsg` 翻页（发证 CGI 见 [GetA8Key](./geta8key-native-cgi.md)）。

## 可复用合同

```text
人（或独立 sidecar）负责让内置浏览器访问 mp.weixin.qq.com
  -> MITM 或缓存收证
  -> getmsg probe ret=0 才 VALID
  -> HTTPS 归档管线
  -> ret=-3 / TTL 到点进入 AUTH_REQUIRED，禁止空成功
```

收证器可以是 wxdown-service、本机代理 + 人手打开，或将来单独改仓规后的进程内打开 URL。**下载器本身不应声称能从客户端登录态续期。**

## 未验证

- 当前 4.x（审计时市场版本约 4.1.13）打开 home 后 key 的真实分钟数
- `poc_token` 与 `key` 是否同 TTL
- 验证码页的稳定 HTML marker 全集
