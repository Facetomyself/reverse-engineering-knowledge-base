---
schema_version: 2
id: web-reverse-x-twitter-graphql-case
document_type: archive
scope:
  targets:
  - unknown
  client: unknown
  version: unknown
  observed_at: unknown
sources:
- id: s1
  ref: null
  basis: source-report
  citation: '`本地项目分析材料（定位不公开）`，`a8bbd36f` → `3fe6ea7d`，公开源码静态对照'
  reason: 出处来自原归档来源字段；本地路径已省略，原始材料未随本文公开，本轮未重跑来源实验。
source_completeness: unknown
tags:
- GraphQL 注册表
- XCTID
- ct0
- fieldToggles
- 部分成功
original_date: 2026-09-27（本轮合并窗口）
archived_date: '2026-09-27'
---

# X 案例：GraphQL 注册表、XCTID 与会话状态分层

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: `workspace/cv-cat/XApis`，`a8bbd36f` → `3fe6ea7d`，公开源码静态对照
> 原始发布时间: 2026-09-27（本轮合并窗口）
> 归档日期: 2026-09-27
> 分类: web-reverse
</details>
>
> XApis 已不再是只透传 Bearer 与 ct0 的旧搜索壳。现行版本集中维护鉴权，使用可刷新 GraphQL 注册表、本地 XCTID 与独立登录链。可复用的是材料分层和请求形状合同，不是上游的长期可用性声明。

## 版本边界：旧结论为什么失效

旧 `apis/twitter_apis.py`、`utils/twitter_utils.py` 已删除。2026-08 的“仓内没有 guest 刷新和 XCTID”“features 写死在方法体”只描述 `a8bbd36f`，不能继续作为当前结论。

| 当前模块 | 职责 | 不应混同的验证门 |
|---|---|---|
| `builder/auth.py::XAuth` | Cookie、guest 生命周期、XCTID 实例 | 本地持有 auth_token 不证明登录态有效 |
| `utils/graphql_registry.py` | 操作 ID、开关声明、前端版本快照 | 注册表可读不证明与当前页面一致 |
| `builder/params.py::GraphQLOperation` | URL、variables、features、fieldToggles | 操作支持全集不等于浏览器实际发送子集 |
| `utils/transaction.py::ClientTransaction` | 方法和 pathname 绑定的 XCTID | 本地产出不等于请求被接受 |
| `x_apis/login_api.py` | 登录状态机与 Castle 调用 | 登录完成、CSRF 完整、业务读回分开验收 |

## GraphQL 注册表不是一张永久常量表

`refresh()` 从 app shell 与前端 chunk 提取 `queryId`、`operationName`、`operationType`、`featureSwitches` 和 `fieldToggles`，写入 `static/graphql.json`，记录 `generatedAt` 与 `frontendSha`。运行时读注册表，不在每个 API 内重复维护查询 ID。

开关值有两层来源：未登录 shell 的 `defaultConfig`，以及登录态 shell 的 `user.config` 覆盖。声明了什么开关、当前账号解析为什么值、当前调用点实际发哪些键，是三个问题。

`BROWSER_FIELD_TOGGLES` 使用显式映射；`None` 表示不发送该参数。未登记操作回退到注册表全集，只是实现的兜底，不是浏览器对齐证据。`exact_field_toggles` 用于锁定实际子集，不能用“全量开关都是 false”冒充缺省参数。

刷新器仍有两处降级：登录态解析失败回到未登录 defaults；部分 chunk 失败后仍能写出注册表。因此“刷新命令成功”不等于完整刷新。更严格的交付应记录缺失 chunk、要求操作覆盖不下降，并用当前页面 fixture 对拍后再切换版本；这些门禁是复用建议，非上游已实现能力。

## 鉴权材料不能靠统一随机化补齐

`prepare_auth()` 将 `ct0` 原样双写到 Cookie 与 `x-csrf-token`。若有 `auth_token` 而缺 `ct0`，直接报错；未登录态才允许本地产生候选 `ct0`。固定 Web Bearer 与用户身份不同，本文不收录其值。

guest token 由服务端激活接口签发，`XAuth` 内按 TTL 缓存；XCTID 则是本地生成。材料来源必须分别记为 `server_issued` 与 `local_computed`。

有一个必须保留的实现矛盾：`XJetfuelLoginApi.login()` 和旧 `XLoginApi.login()` 的成功收尾仍会在缺 `ct0` 时生成随机值，与 `prepare_auth()` 对已登录会话的拒绝策略不一致。不能将“拿到 auth_token”或 `is_logged_in` 的非空判断，当成 CSRF 正确和业务可用的证据。后续移植应统一完成门，而非复制这个降级。

## XCTID 的输入边界与缓存回退

`ClientTransaction` 从 shell 与前端分片取得公开动画材料；`generate()` 绑定大写 HTTP 方法和 **不含 query 的 pathname**。它提供显式时间与随机字节参数，便于固定输入做离线字节对拍。

`XAuth.transaction` 在网络取材失败时回退到本地捕获 profile。算法在本地执行，不意味着材料能永不过期；回退必须带来源、版本和采集窗口。不能把缓存可读写成“当前前端已匹配”。本文不搬动画材料、混合常量或可执行签名器。

## 传输层与发布生命周期要独立验收

`builder/client.py` 区分导航和 fetch/XHR 请求，移除导航专用头，按目标生成 fetch 元数据。但源码同时写明 TLS/HTTP2 使用 Chrome 150 模板，应用层画像按另一版本覆盖；改 UA 不会自动同步 TLS。`session()` 返回的 Session 也不能仅凭顶层 `get/post` 包装就推断完成相同处理。

发布侧提供了可复用的部分成功语义：

- `post_thread()` 每条回复上一条，失败时返回已经完成的 ID 列表；不是事务，也不回滚已发布内容。
- `post_article()` 默认只存草稿，显式开启才发布；支持传入已有 `article_id`，并在后续失败时保留 `info` 中已取得的草稿 ID。
- Markdown 转换阶段可能先上传正文图片，再创建草稿；因此失败可能留下媒体，而不是“完全没发生”。恢复应从已确认阶段继续，不能盲目重放整个工作流。

这些是状态机与恢复边界，不是新增业务 API 名称的罗列。本轮没有执行登录、上传或发布。

## 固定版本证据与限制

源码基线：[XApis @ 3fe6ea7d](https://github.com/cv-cat/XApis/tree/3fe6ea7d)。核对入口：

- `builder/auth.py::prepare_auth / transaction`。
- `utils/graphql_registry.py::refresh / _parse_feature_defaults`。
- `builder/params.py::GraphQLOperation`、`utils/transaction.py::generate`。
- `builder/client.py`、`x_apis/login_api.py::login`。
- `x_apis/x_write_api.py::post_thread`、`x_apis/x_article_api.py::post_article`。

本篇是静态调用边界分析，没有重跑上游 SDK，没有新 browser fact、parity 或 `serverAccepted` 证据。Castle 的输入完整性、压缩后端和“纯算”限定见 [Castle 字节对齐边界](./castle-profile-compression-parity.md)。
