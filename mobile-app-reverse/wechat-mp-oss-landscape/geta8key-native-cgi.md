# GetA8Key 发证器，不是历史 API

> 来源: `workspace/weixin_download` 2026-09-13 iPad 协议审查
> 原始发布时间: 2026-09-13
> 归档日期: 2026-09-15
> 分类: mobile-app-reverse
>
> iPad/Android 协议号能调一部分公众号 CGI，但主业是关注、收推送、刷阅读。唯一可能接到 `getmsg` 的是 `GetA8Key` / `MpGetA8Key`：对 `mp.weixin.qq.com` URL 签发 `uin/key/pass_ticket`。type 10039「历史推送」没有 `general_msg_list`，不能当完整翻页。Gewechat 已停；商业栈闭源，最多本机 sidecar。

## 协议号是什么、不是什么

多端共用账号，协议栈不同。社区用 **MMTLS + protobuf 客户端模拟**（常称 iPad 协议）扫码后维持长连接：不跑官方 App，不 Hook `Weixin.dll`。

它不是：

- 网页版 `webwx*`（已残废；把 `synccheck/getmsg` 写成 iPad 的文章是张冠李戴）
- PC 4.x 注入 / UIA
- 公众号后台 `list_ex`
- [mmtls 应用宝/WMPF 分析](../../protocols/mmtls-protocol-analysis.md) 那套 iLink/ShortLink（知识库那篇不能当个微实现手册）

公开形态几乎全是商业闭源。Gewechat 停维，作者指向腾讯「违规获取及利用微信终端用户数据」打击公告。本知识库不收录租号价目、`.dll` 或 62 数据。

## 和公众号相关的 CGI（文档反复出现）

| CGI / 能力 | 实际覆盖 | 归档价值 |
|------------|----------|----------|
| 搜索 / 关注 / 取关 | `gh_` wxid | 前置条件，不是历史 |
| 长连接收推送 | 已关注号增量 | 不是翻页 API |
| 打开一篇：阅读/点赞 | 刷量 | 明确排除 |
| **GetA8Key / MpGetA8Key** | 对一条 URL 原生授权 | **唯一值得探针的发证器** |
| type 10039「获取历史推送」 | `gh_` + offset，返回标题/图标/链接/描述/阅读量 json | **没有** `general_msg_list` / `can_msg_continue` / `next_offset` |

PC 日志可见：`NetSceneGetA8Key Success srcurl:http://mp.weixin.qq.com/mp/getmasssendmsg?__biz=...`。社区用 Android 协议调 GetA8Key 后，返回 URL 里的 `key` 可喂 `profile_ext?action=getmsg`。结论：**`getmsg` 的 key 就是 A8Key 签发结果。**

Wecloud 一类文档给过文章短链成功包：`FullURL` 带 `pass_ticket`，头带 `X-WECHAT-KEY`、`X-WECHAT-UIN`。Apifox 标成 iPad `POST /OfficialAccounts/MpGetA8Key`，入参 `Url` + `Wxid`。

## 可规划形状（未 live）

```text
专用号 + 协议会话（扫码一次，会话重连）
  -> GetA8Key( profile_ext?action=home&__biz=...#wechat_redirect )
  -> 从 FullURL / 头取出 uin、key、pass_ticket
  -> 现有 getmsg HTTPS 管线
  -> key 过期或 ret=-3 再 GetA8Key，不必再扫码
```

这比在协议 SDK 里重写下载器干净：协议号只发证，归档、去重、空成功语义仍在 HTTP 半边。

未验证、且会直接决定能不能做的点：

1. 对历史主页 `action=home` 调 GetA8Key，还是只对单篇 `/s/` 有效。
2. 目标号必须先关注，还是任意公开 `__biz` 都能发证。
3. iPad 设备类型签发的 key，当前 `getmsg` 是否仍 `ret=0`（有的栈只在 Android 协议上验证过）。
4. 协议会话活着时能否反复发证；是否要滑块/人脸。
5. 批量换 `__biz` 的频控。

任一条失败，产品就从「任意公开号历史」降成「已关注号增量」或「已知单篇」。

## 工程边界

- 允许的知识复用：CGI 名、返回头字段、与 `getmsg` 的衔接关系。
- 不允许：把协议号当下载器、当阅读量刷手、把商业二进制纳入 Git。
- 号风险、版本锁、闭源不可审计、执法面，才是成本；月租广告不是可行性证明。
- `-2041` / 滑块 / 人脸一律认证挑战，禁止自动过。
