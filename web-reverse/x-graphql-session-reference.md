---
schema_version: 2
id: web-reverse-x-graphql-session-reference
document_type: reference
original_date: '2026-09-27'
archived_date: '2026-10-02'
scope:
  targets: [x-graphql]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./x-twitter-graphql-case.md#graphql-reference
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只整理 registry、feature/fieldToggles、ct0、guest/XCTID 等材料的来源与写入边界；不收录凭据、Cookie、token、账号、query ID 或 XCTID 样值。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 归纳 registry refresh、GraphQL 装配、登录和发布阶段关系；未运行 XApis、浏览器或目标服务。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 仅记录来源提出的完成门与部分成功边界，不等同 browser parity、当前前端匹配、业务读回或 server acceptance。
relations:
  - type: derived_from
    target: ./x-twitter-graphql-case.md#graphql-reference
tags: [x, graphql, registry, fieldToggles, XCTID, session-gates, partial-success, source-report]
---

# X GraphQL 注册表与会话完成门参考

这张卡提炼 [X GraphQL 来源归档](./x-twitter-graphql-case.md#graphql-reference)中的三个可检索边界：前端 registry 与字段开关的参数来源、XCTID/鉴权到请求的装配链，以及登录、CSRF、业务读回和发布部分成功的分层完成门。材料保持 `source-report`，不把登录成功标记或刷新命令成功当成线上可用。

<a id="parameters"></a>
## 参数来源与装配边界

- registry refresh 从 app shell 与前端 chunks 提取 `queryId`、`operationName`、`operationType`、`featureSwitches` 和 `fieldToggles`，写入本地快照并记录生成时间与 frontend 版本标识。快照可作为运行时材料，但可读不证明与当前页面一致。
- feature 值有未登录 shell defaults 与登录态 `user.config` 覆盖两层来源。应分别记录“声明了哪些开关”“账号解析出了什么值”“具体调用点实际发了哪些键”。
- `fieldToggles` 使用显式操作映射；`None` 表示该键不发送，`exact_field_toggles` 用于锁定观察到的子集。未登记操作回退 registry 全集只是实现兜底，不能当作浏览器字段全集。
- authenticated session 的 `ct0` 按来源报告需同时进入 Cookie 与 `x-csrf-token`。guest token 的来源与本地 XCTID 不同：前者属于 `server_issued`，后者属于 `local_computed`。本卡不复制任何值。

<a id="request-chain"></a>
## 请求链路与状态分层

```text
app shell / frontend chunks
  -> refresh registry + feature defaults
  -> GraphQLOperation 组装 URL / variables / features / fieldToggles
  -> ClientTransaction 按大写 method + 不含 query 的 pathname 生成 XCTID
  -> auth/session 材料注入
  -> GraphQL 请求

登录链：login/Castle -> ct0/CSRF 完成 -> 业务读回
发布链：media upload -> draft -> optional publish
```

来源报告还描述了两类降级：登录态解析失败可能回到未登录 defaults，部分 chunk 失败仍可能写出 registry；网络取材失败可能回退本地捕获的 transaction profile。因此“刷新命令成功”不等于 registry 完整，“本地产出 XCTID”也不等于当前前端匹配或请求被接受。

发布侧不是单事务：thread 逐条发布并返回已完成 ID，失败不回滚；article 默认先存草稿，后续失败可留下 draft ID；Markdown 转换可能先上传媒体再建草稿。恢复时应从已确认阶段继续，不能盲目重放整个链路。

<a id="validation"></a>
## 来源完成门与限制

来源报告建议把以下门分开记录：

| 门 | 只说明什么 | 不能推出什么 |
|---|---|---|
| registry coverage | 缺失 chunk、操作覆盖和当前页面 fixture 的对照状态 | 不推出 registry 与当前页面一致 |
| login/CSRF | 登录材料是否具备、`ct0` 是否处于应有位置 | 不推出登录成功标志等于业务可用 |
| business readback | 业务读回是否成立 | 不推出 token 或 auth_token 单独有效 |
| publish recovery | 已完成 thread/draft/media 阶段及可恢复点 | 不推出发布是事务或可安全全量重放 |

来源还保留一个实现矛盾：某些 login success 路径在缺 `ct0` 时会生成随机值，而 `prepare_auth()` 对 authenticated session 缺 `ct0` 会拒绝。该矛盾只能作为完成门风险提示，不能整理成随机化方案。

本卡没有执行登录、上传、发布、浏览器对拍、runtime、parity 或 server acceptance；版本、client 观察窗口和前端快照均保持来源未知。
