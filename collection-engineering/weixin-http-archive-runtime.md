# HTTP 归档运行时：文章身份、SQLite claim 与 MCP job

> 来源: `workspace/weixin_download` 落地实现
> 原始发布时间: 2026-07-16 至 2026-07-17
> 归档日期: 2026-09-15
> 分类: collection-engineering
>
> 公众号这类「短时会话 + 逐篇落盘」的 HTTP 归档，控制面不是 AIMD 并发，而是身份主键、短事务 claim、durable retry 和与文章状态分离的 MCP job。凭证不得进入队列或 job payload。进程还活着、job 标 completed，不等于文章 canonical 成功。

## 和 PSA 高并发文的分工

[高并发 HTTP 采集控制面](./high-concurrency-http-collector-control-plane.md) 管代理租约、连接池、AIMD。本文管 **单会话串行归档**：一篇文章只能被一个 worker 占有，失败要能重启后续跑，认证失败不能当 5xx 重试。

协议字段见 [微信公众号 HTTP 接口面](../protocols/wechat-mp-http-surface.md)。这里不重复 `getmsg` URL。

## 文章目录

| 主题 | 文章 |
|------|------|
| 身份、claim、heartbeat、retry | [SQLite 文章 claim 与 durable retry](weixin-http-archive-runtime/sqlite-claim-retry.md) |
| Headless MCP 长任务 | [MCP job 与文章状态分离](weixin-http-archive-runtime/headless-mcp-jobs.md) |

## 结论先行

1. 主键用协议身份（本域是 `__biz + mid + idx`），不要用标题或目录名。
2. `BEGIN IMMEDIATE` 里完成「看状态 + 占有」；HTTP 和写文件不得持有写锁。
3. `complete` 必须文件真实存在；缺格式、缺媒体不是 skip。
4. retry queue / job payload 只留 canonical URL 和脱敏状态，禁止 `uin/key/pass_ticket/Cookie`。
5. MCP job 的 `completed` 只表示 runner 返回；`{"ok": false}` 仍写成 completed 是假成功，后续实现必须拆 typed outcome。
6. 认证类失败进 `AUTH_REQUIRED`，不进 retry queue。

本实现有 33 个离线回归和 MCP transport smoke；`getmsg` 凭证窗口内的基础下载 live 过。P0 假成功（`ret!=0`、验证页、job `ok:false`）**尚未**修，复用时把这三条当必做门，不要复制旧终态。
