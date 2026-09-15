# 微信公众号开源库对照：按会话平面读仓库

> 来源: `workspace/weixin_download` 开源库对照（2026-07 至 2026-09）
> 原始发布时间: 2026-07-16 至 2026-09-13
> 归档日期: 2026-09-15
> 分类: mobile-app-reverse
>
> 把公开微信公众号下载器、RSS、协议号和 H5 调试箱钉到五套会话上，记录接口形状、停更节点和可复用工程模式。不收录凭证、不 vendoring 闭源协议栈、不把死接口写成当前可用。平面定义见 [微信公众号五套会话](../protocols/wechat-mp-session-planes.md)。

## 怎么读一个新仓库

先回答三个问题，再看 Stars 和 README 承诺：

1. 它用的是哪一套会话（WebView `getmsg` / MP 后台 / 微信读书 / 原生 CGI / 只调试）？
2. 历史枚举的主键是 `__biz+mid+idx`、`reviewId` 还是标题？
3. 证据等级：源码形状、作者停更声明、还是本机 live `serverAccepted`？

README 写「全自动下载任意公众号」而实现是剪贴板 + 内置浏览器，按平面 2 收证器记录，不当纯 HTTP 客户端。

## 文章目录

| 平面 | 文章 |
|------|------|
| WebView `getmsg` 发证 | [getmsg WebView 发证与短时 key](wechat-mp-oss-landscape/getmsg-webview-issuance.md) |
| MP 后台 `list_ex` | [MP 后台跨号列表与 2026-07-30 收紧](wechat-mp-oss-landscape/mp-backend-list-ex.md) |
| 微信读书 `/mp/chapters` | [微信读书公众号列表与 RefreshToken](wechat-mp-oss-landscape/weread-mp-chapters.md) |
| 原生 `GetA8Key` | [GetA8Key 发证器，不是历史 API](wechat-mp-oss-landscape/geta8key-native-cgi.md) |
| WMPF / 内置浏览器调试 | [WMPF H5 调试面与 WeixinJSBridge Mock](wechat-mp-oss-landscape/wmpf-h5-debug-plane.md) |

## 仓库总表（2026-09-13 源码审查）

| 仓库 | 平面 | 许可证/状态 | 复用什么 | 不要复用什么 |
|------|------|-------------|----------|--------------|
| [qiye45/wechatDownload](https://github.com/qiye45/wechatDownload) | 2 WebView | 无识别 license；4.7 @ 2026-08-16 | 行为基线：内置浏览器发证 + 缓存扫 key | 仓库几乎无应用源码；不是 HTTP refresh |
| [wechat-article/wxdown-service](https://github.com/wechat-article/wxdown-service) | 2 收证 | 文档：MITM 收证 | 「只收证、不触发微信」的 sidecar 合同 | 不自动打开 WebView |
| [wechat-article/wechat-article-exporter](https://github.com/wechat-article/wechat-article-exporter) | 3 MP | MIT；2026-07-30 停更 | `bizlogin` / `list_ex` 纯 HTTP 形状；无后台账号/未绑邮箱状态机 | 停更后的跨号可用性 |
| [yangbuyiya/EasyWechatDownload](https://github.com/yangbuyiya/EasyWechatDownload) | 3 MP | 2026-07-14 release | 「平台模式」= MP 扫码 + 搜索 + 列表 | 收紧后的 live 证据 |
| [tmwgsicp/wechat-download-api](https://github.com/tmwgsicp/wechat-download-api) | 3 MP | AGPL-3.0；最后推送 2026-07-27 | issue：后台会话约 4 天，过期只能再扫码 | 收紧前快照 |
| [rachelos/we-mp-rss](https://github.com/rachelos/we-mp-rss) | 3 + 4 | 2026-09 仍改 | `free_publish` 降级链；读书 Web 列表 | 文档滞后于源码；跨号 `200013` 无反证 |
| [teng-lin/weread-omni](https://github.com/teng-lin/weread-omni) | 4 读书 | MIT；2026-09-11 仍提交 | `/mp/chapters` 首请求 `synckey`、翻页 `offset` 互斥 | CLI 100 篇产品上限 ≠ 协议上限 |
| [johamwon/wechrss](https://github.com/johamwon/wechrss) | 4 读书 | 指南 v4.1.0 | QR、RefreshToken 状态机、`__biz→MP_WXS_` | 默认同步不抓正文 |
| [cooderl/wewe-rss](https://github.com/cooderl/wewe-rss) | 4 中转 | 2026-05-11 归档 | 反面教材：自托管壳 + 闭源中转 | 不得再当读书可用性证据 |
| [HeartFlying/wechat-article-exporter](https://github.com/HeartFlying/wechat-article-exporter) | 工程 | MIT | 目录存在检查 + 持久化去重 index | 标题/URL 去重偏弱 |
| [Moore-developers/moore-wechat-article-downloader](https://github.com/Moore-developers/moore-wechat-article-downloader) | 工程 | MIT | SQLite `articles/runs`、URL identity | 身份应升到 `__biz+mid+idx` |
| [xuange520/WeChat-H5-DevTools](https://github.com/xuange520/WeChat-H5-DevTools) | 调试 | 2026 活跃 | 4.x 进程名、vConsole 代理、JSBridge Mock 边界 | Frida hook / 外部沙箱当下载器 |

未列入但同族：`Sunshiqisky/wechat_crawler`、`dzcdly/opencli-weixin-album` 出现在样本字符串里，只作历史线索。`funnymh12/wechat-article-exporter` 用 Playwright 扫码，属于浏览器自动化，不当纯协议对照。

## 身份与状态（跨平面复用）

归档侧可复用、与会话无关的工程结论：

- 文章主键优先 `__biz + mid + idx`；短链 `/s/<token>` 先还原 `__biz`，不要发明第三套 id。
- 读书侧主键是 `reviewId`，接入时必须映射，不能和 `getmsg` 列表混写一张「标题唯一」表。
- 去重不要只认标题或目录名；旧目录存在检查（HeartFlying）要加真实文件存在，避免空成功 checkpoint。
- SQLite 短 `BEGIN IMMEDIATE` claim、网络与写文件不持有写锁（Moore 的 runs 表是方向，不是现成依赖）。
- 有限次即时重试只覆盖临时网络和 `408/425/429/5xx`；认证失败、验证页、`ret!=0` 不得当空成功。

## 证据等级

| 等级 | 含义 | 本合集用法 |
|------|------|------------|
| 源码形状 | README / 固定 commit 的接口字段 | 可写进对照表 |
| 作者声明 | 停更、上游关闭、打击公告 | 默认 fail-closed |
| 外部复现 | 第三方博客/issue 同一 `ret` | 加强「不要当活接口」，仍非本机 live |
| live-pending | 本知识库未在 2026-09-13 后重打 | `list_ex` 跨号、GetA8Key 未关注 home、读书截断页数 |

本合集**没有**把任一平面标成当前 `serverAccepted`。后续项目要自己做探针，不要把 7 月的源码审查写成 9 月可用性。

## 不收录

- `uin` / `key` / `pass_ticket` / `vid` / `accessToken` 原值
- 可直接打生产的下载脚本、协议号二进制、闭源「62 数据」
- 刷阅读量、商业 puppet 租号价目当可行性证明
- 把 UIA / 无障碍点击原生订阅号写成历史枚举主路径

## 和 App 纯协议文档的关系

公众号 Web 历史是 **HTTPS + 短时 Web 凭证**，不是设备注册四关。空壳诊断仍适用（[准入四关](./protocol-admission-four-gates.md) 的 `serverAccepted`），但不要把 `hardware-fp` / InnerSign 套到 `getmsg` 上。
