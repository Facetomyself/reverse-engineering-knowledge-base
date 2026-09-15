# 微信公众号 HTTP 接口面：getmsg / 统计 / 评论 / 合集

> 来源: `workspace/weixin_download` Nuitka constants 恢复 + 协议复现
> 原始发布时间: 2026-07-16
> 归档日期: 2026-09-15
> 分类: protocols
>
> 公众号 Web 归档不是一个接口。历史列表是 `profile_ext?action=getmsg`，阅读量是 POST `getappmsgext`，评论是 `appmsg_comment`，合集是 `appmsgalbum?action=getalbum`。公开文章 URL 无登录可拉正文。会话平面见 [五套会话](./wechat-mp-session-planes.md)；本文只保留已实现的 HTTPS 形状和完成门。

## 定位

`weixin_download` 从 4.6 样本 constants 恢复、并用独立 Python 复现了下列 HTTPS 面。凭证仍是 WebView 短时 `uin/key/pass_ticket`（平面 2）。本文不讨论如何签发；签发对照见 [getmsg WebView 发证](../mobile-app-reverse/wechat-mp-oss-landscape/getmsg-webview-issuance.md)。

```text
已知文章 URL / 合集 URL     —— 无登录 source
profile_ext?action=getmsg  —— 历史翻页，要短时 key
getappmsgext               —— 阅读/点赞，要同一套 key
appmsg_comment             —— 精选评论/回复
appmsgalbum?action=getalbum —— 合集游标分页
```

Host 固定 `mp.weixin.qq.com`。样本 UA 是桌面 Chrome/Edge 形；不要和微信客户端 mmtls 头混用。

## `__biz` 提取（公开页）

输入文章链接，保留 `__biz/mid/idx/chksm` 一类稳定 query，GET 页面后从 URL 或 HTML 抽：

```text
__biz=(.*?)&
biz\s*=\s*"(.*?)"
window.biz\s*=\s*
```

实现侧还要丢掉 `${window.biz}` 模板占位，并接受 object 风格 `biz: "..."`。抽到后拼历史入口（给人在微信里打开，不是 HTTP 发证）：

```text
https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=<biz>&scene=124#wechat_redirect
```

文章主键是 `__biz + mid + idx`，`sn` 只是校验串。短链 `/s/<token>` 必须先还原 `__biz`。

## 历史：`getmsg`

样本拼出的 GET（`count` 固定 10，`scene=124`）：

```text
https://mp.weixin.qq.com/mp/profile_ext?action=getmsg
  &__biz=<biz>&f=json&offset=<offset>&count=10&is_ok=1&scene=124
  &uin=<uin>&key=<key>&pass_ticket=<pass_ticket>
```

响应要认：

| 字段 | 用途 |
|------|------|
| `ret` | `0` 才继续；`-3` 是无会话，禁止当成 0 篇成功 |
| `general_msg_list` | JSON 列表；样本里可能先切片再 `json.loads` |
| `next_offset` | 下一页；不要和读书 `synckey` 混 |
| `comm_msg_info` / `app_msg_ext_info` | 单条消息 |
| `multi_app_msg_item_list` | 多图文 flatten 成多篇 |
| `content_url` / `title` | 单篇入口 |
| `copyright_stat` / `copyright_type` | 原创过滤 |

`serverAccepted`：`ret=0` 且 flatten 后至少一篇带稳定身份。空 `list` 且 `ret=0` 才是真的没有更多；`ret!=0` 走 `AUTH_REQUIRED` / `PROTOCOL_INVALID`。当前复现器仍把 `ret!=0` 当空成功，这是 P0，不要学。

历史 live（凭证有效时）：第一页 10 条 message，flatten 16 篇，`ret=0`。该证据不等于当前 key 仍有效。

## 统计：`getappmsgext`

`POST https://mp.weixin.qq.com/mp/getappmsgext`。需要同一套 `uin/key/pass_ticket`，再加文章 `content_url` 一类 body。成功看 `base_resp.ret=0`。这是阅读/点赞，不是列表翻页。微信读书 token 打不了这个口。

## 评论：`appmsg_comment`

```text
GET .../mp/appmsg_comment?action=getcomment&...&appmsgid=&idx=&comment_id=&limit=100&uin=&__biz=&f=json
GET .../mp/appmsg_comment?action=getcommentreply&...&max_reply_id=
```

回复接口同样要带会话字段。全量分页在本实现里仍未补齐；基础 `getcomment` 在补 `key/pass_ticket` 后 live `base_resp.ret=0`。

## 合集：`getalbum`

```text
https://mp.weixin.qq.com/mp/appmsgalbum?action=getalbum
  &__biz=&album_id=&begin_msgid=&begin_itemidx=&count=&is_reverse=&f=json
```

响应：`getalbum_resp.article_list`，继续条件 `continue_flag === '1'`，游标是上一页最后一条的 `msgid` / `itemidx`。公开合集无登录可翻页（本仓库 live：连续两页各 3 条，`ret=0`）。逐篇保存复用单篇身份与 checkpoint。

## 公开正文

已知 `https://mp.weixin.qq.com/s/...` 无登录可抽标题、昵称、时间、图片 URL。工具 UA 可能 302 到 `wappoc_appmsgcaptcha`：按内容无效，禁止 checkpoint。媒体下载是后处理，缺文件不能把文章标 complete。

## 实现边界（写进复用合同）

| 已验证 | 不要当成已完成 |
|--------|----------------|
| 字段名、URL 形状、flatten、合集游标 | `getmsg` 纯 HTTP 续期 |
| 公开 URL / 公开合集无登录 | 验证页/空正文的 semantic gate（P0） |
| 有效 key 窗口内分页 | 永久零人工；PC 登录态当 key |
| 身份 `__biz+mid+idx` | 用标题去重 |

运行时 checkpoint / MCP 见 [HTTP 归档运行时](../collection-engineering/weixin-http-archive-runtime.md)。
