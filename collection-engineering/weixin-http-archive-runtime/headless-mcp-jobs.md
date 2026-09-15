# MCP job 与文章状态分离

> 来源: `workspace/weixin_download` `weixin_job_manager.py` / `weixin_mcp_server.py`
> 原始发布时间: 2026-07-17
> 归档日期: 2026-09-15
> 分类: collection-engineering
>
> Headless MCP 可以没有 GUI：默认 stdio 由 client 拉起，本机共享再用 loopback Streamable HTTP。长任务要独立的 job 表、owner、heartbeat、cooperative cancel。job `completed` 不是文章 checkpoint。runner 返回 `{"ok": false}` 仍标 completed 是假成功。

## Transport

| 模式 | 用途 | 约束 |
|------|------|------|
| stdio | 单 client 自动拉起/关闭 | 不常驻 |
| Streamable HTTP `http://127.0.0.1:<port>/mcp` | 多本地 client 共享 | 默认 loopback；远程 bind 在 authentication 之前拒绝 |
| GUI / 浏览器驱动 | 不作为 MCP 依赖 | 本实现明确不引入 |

沿用官方 Python SDK 的 initialize / tools/list / tools/call contract，用真实 client 做 smoke，不要只测函数 import。

工具分成两类：同步短操作（抽 `__biz`、单篇、查询状态）和 `start_*_job` 立即返回 job id。列表、进度、取消是 job 面，不是文章面。

## Job 状态机

```text
queued
  -> running（写入 owner_id + heartbeat）
       -> completed | failed | cancelled
进程重启：queued/running/cancel_requested 且 heartbeat 过期 -> interrupted
```

实现要点：

- 独立 `download_jobs` 表，不要复用 `article_downloads`。
- `create_job` 时 sanitize payload。
- 后台线程周期性 heartbeat；丢失 owner 的 UPDATE 行数为 0 就停。
- cancel 必须是 cooperative：分页循环、逐篇循环、退避 `sleep` 都查 `cancel_check()`，不能只改状态位让下载继续。
- 重启把未终态且心跳过期的行标 `interrupted`，并清空 owner。interrupted ≠ 自动重放；要明确的 retry/start。

终态集合：`cancelled` / `completed` / `failed` / `interrupted`。不要用「线程还活着」当成功。

## 假成功陷阱（必修）

当前实现 `_finish(..., "completed", result=result)` 只看 runner 有没有抛异常。因此：

- 业务 JSON `{"ok": false}` 仍是 job `completed`
- `getmsg ret=-3` 变成 0 篇且 job 100%
- CLI 结构化失败仍退出码 0

复用时 job 终态必须由 **typed outcome** 决定：`OK` / `IDEMPOTENT` / `AUTH_REQUIRED` / `CONTENT_INVALID` / `NETWORK_TRANSIENT`…。Orchestrator 是唯一写 terminal 的组件；CLI、MCP、runner 不得各自解释成功。

进度回调同样 sanitize，禁止把 key 打进 `progress_json`。

## 和文章 claim 的关系

```text
MCP start_job
  -> job running
  -> 逐篇 DownloadStateStore.claim
  -> HTTP / 写盘
  -> 文章 complete 或 retry queue
  -> job terminal（必须反映是否有 AUTH/内容失败）
```

取消 job 不能留下永久 in-progress 文章 claim：要么 heartbeat 过期变 stale，要么 cancel 路径显式释放。二次相同 URL 应走文章 store 的 `already_downloaded`，而不是再开一个成功 job 重复写盘。
