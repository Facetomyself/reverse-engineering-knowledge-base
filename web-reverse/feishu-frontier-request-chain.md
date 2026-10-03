---
schema_version: 2
id: web-reverse-feishu-frontier-request-chain
document_type: reference
archived_date: '2026-10-01'
scope:
  targets: [feishu]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./feishu-csrf-frontier-case.md#案例frontier-长连
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 仅整理本地对照文章报告的接口路径和字段名；来源未公开原始代码，本轮没有连接服务，也没有验证请求可接受性。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅记录来源描述的 frontier ticket、页面 JS 和 WebSocket 关系；缺少实际输入、完整 query、握手/帧语义与服务端响应，不代表可执行复现。
relations:
  - type: supplements
    target: ./session-binding-double-write.md#技巧会话材料双写并且绑源
tags: [feishu, frontier, websocket, request-chain]
---

# 飞书 Frontier WebSocket 请求链参考

本文聚焦来源文章报告的 frontier 长连接口和与之分开的 IM HTTP 面。它不是开放平台 `tenant_access_token` 参考，也不是一份已验证可执行请求。来源是无公开 locator 的本地对照报告；本稿只保留字段名、代码落点和路径关系。

<a id="interfaces"></a>
## 接口面

| 接口 | 来源报告的表面 | 可确定的关系 | 未知与边界 |
|---|---|---|---|
| Frontier ticket | `GET https://login.feishu.cn/suite/passport/frontier_ticket/` | 来源伪代码称以既有 session 请求，并将返回的 ticket 用于后续 frontier 长连 | 请求头/参数、响应 schema、ticket 生命周期与绑定条件未知；GET 与 session 仅为来源报告，不是本轮观测 |
| Frontier WebSocket | `wss://msg-frontier.feishu.cn/ws/v2` | query 至少提及字段名 `ticket`、`access_key`；来源称连接前对参数执行 `urlencode` | 其他 query 字段、握手要求、帧格式和响应语义未知 |
| IM gateway HTTP | 来源只给出路径 `im/gateway/` 和头字段名 `x-command` | 与 frontier 长连是不同接口面；来源明确不应把 frontier ticket 用于该接口 | Host、HTTP method、body、session 要求、`x-command` 取值和响应均未知 |

网页 HTTP 的 CSRF 头与 frontier `access_key` 是不同字段/路径，不是同一值的双写关系。CSRF 的字段来源与双写边界见[会话材料双写参考](./session-binding-double-write.md#技巧会话材料双写并且绑源)；这里不重复其主体。

<a id="request-chain"></a>
## Frontier 请求链

下面是来源文章描述的依赖关系，不是可直接执行的操作步骤：

```text
existing web session
  -> GET /suite/passport/frontier_ticket/ -> ticket
  -> generate_access_key(material) -> page JS export -> access_key
  -> urlencode(query fields) -> WSS /ws/v2
```

- 来源将 `generate_access_key` 描述为把未公开的材料交给 `static/fly_book.js` 的同名导出，并称 JS 侧为 MD5 拼装。函数体、输入材料和拼装细节不在归档中；本稿不据此声称恢复了算法。
- query 中只登记来源明确点名的 `ticket` 与 `access_key` 字段名，不录入或臆造其实际值。`access_key` 与网页 HTTP 的 `x-csrf-token` 不可互换；双写判断见上面的交叉引用。
- `im/gateway/` 是来源另行指出的 HTTP 面，不属于这条 WebSocket 链。来源没有说明它和 frontier 的后续交互或状态关系。

不单列 `parameters` 模块：目前只有字段名称和粗略角色；实际值、完整输入依赖、绑定、生命周期及变化机制均未知。把这些信息放在接口与链路定位中，避免制造一张看似完整的参数卡。

## 证据与边界

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | ticket endpoint、JS 导出和来源所称的 MD5 拼装关系 | s1，来源 archive 第 59 行 | source-report | OpenFeiShuApis 本地对照报告 | 原始代码及材料未随文章公开；MD5 描述未经本轮静态或运行时核验 |
| C2 | 参数经 `urlencode` 后用于 frontier WebSocket；可见字段名为 `ticket`、`access_key` | s1，来源 archive 第 61、63–67 行 | source-report | 来源报告的 `msg-frontier` 连接路径 | query 不完整，无握手、帧或服务端接受证据 |
| C3 | `im/gateway/` 是带 `x-command` 的另一 HTTP 面 | s1，来源 archive 第 61 行 | source-report | 来源报告所述本地对照仓 | Host、method、字段值和完整接口语义未知 |
| C4 | 本知识库未连接飞书；前端变化后应重新确认调用点与 JS 导出 | s1，来源 archive 第 75 行 | source-report | 本文取证边界 | version、observed_at、当前 runtime 与服务端行为均未知 |

来源日期中的 `2026-08-18` 是对照仓 HEAD 日期，不是本文的验证版本或运行时观测时间。来源没有公开 locator，原始对照材料不可由本稿读者直接复核；本文没有连接飞书、重放请求或验证 server-accepted 行为。实际凭证和 token 值不收录。
