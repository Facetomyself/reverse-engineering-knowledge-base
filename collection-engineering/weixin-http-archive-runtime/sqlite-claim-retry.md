# SQLite 文章 claim 与 durable retry

> 来源: `workspace/weixin_download` `weixin_download_state.py`
> 原始发布时间: 2026-07-17
> 归档日期: 2026-09-15
> 分类: collection-engineering
>
> 本地 SQLite WAL 上用短 `BEGIN IMMEDIATE` 做文章占有：协议主键、owner token、heartbeat、缺文件重试、durable queue。网络请求不持有写锁。队列里的 URL 要剥掉临时凭证参数。

## 身份

稳定 query 只留 `__biz`、`mid`、`idx`、`sn`、`chksm`。canonical URL 必须丢掉 `uin/key/pass_ticket/poc_token/appmsg_token` 一类会话参数，否则同一篇文章会裂成多条。

主键优先 `__biz + mid + idx`。缺主键时 fallback 必须先清临时 credential，再考虑规范化 URL。标题、昵称、目录后缀都不是身份。

合集、单篇、账号批量下载共用同一 store，避免「合集 skip 了、单篇又下一次」。

## Claim

```text
BEGIN IMMEDIATE
  已 complete 且文件都在     -> claimed=false, already_downloaded
  in-progress 且 heartbeat 未过期 -> claimed=false, download_in_progress
  stale / failed / 缺文件    -> 占用：写入 claim_token + heartbeat_at
COMMIT
然后才 HTTP / 写盘
heartbeat 周期性刷新
完成前再核 claim_token；不匹配则 ClaimLostError，不得覆盖新 owner
```

连接：`PRAGMA journal_mode=WAL`、`busy_timeout`、`synchronous=NORMAL`。`os.replace` 原子文件替换解决不了多进程同时决策；决策必须进同一把 SQLite 写锁。

`complete` 条件：请求的格式和实际文件都存在。空目录、只有 JSON 没有 HTML、媒体任务失败，都不能 skip。旧 manifest 可以自动索引，但索引后仍要走文件存在检查。

## 重试分层

| 层 | 范围 | 禁止 |
|----|------|------|
| 即时有限次 | 临时网络、`408/425/429/5xx`，指数退避 | 认证失败、参数错误、验证页 |
| durable queue | 即时耗尽后的临时失败；重启可 `retry-downloads` drain | payload 含 key/Cookie；`AUTH_REQUIRED` |
| dead | 超 attempts 或业务不可恢复 | 再当 NETWORK_TRANSIENT |

retry / job 序列化前走同一套 sanitize：secret 键置空，URL 走 canonical。日志和异常文本同样脱敏。

## 可抄的不变量

- 同一 `article_key` 同时只有一个有效 claim_token。
- 丢失 lease 的旧 worker 不能把状态写成 complete。
- `AUTH_REQUIRED` / `CAPTCHA_REQUIRED` / `CONTENT_INVALID` 不进 retry queue（目标语义；当前代码对 `getmsg ret` 仍未完全分类，复用时先补）。
- 状态库路径跟输出目录走，不要全局一个 SQLite 混多个互不相干的目标站。
