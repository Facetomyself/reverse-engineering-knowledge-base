---
schema_version: 2
id: bilibili-comments-request-reference
document_type: reference
original_date: '2026-02-23'
archived_date: '2026-10-02'
scope:
  targets: [bilibili]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./benru-web-reverse-compilation/benru-web-20260223-01.md#comments-api-code
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 仅整理归档文章所载代码路径；原始出处没有公开 locator，未请求当前接口或验证服务端接受状态。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 字段和值来自来源代码描述；不包含运行样值，字段语义及当前有效性未经独立验证。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅描述来源代码中的顺序分页；不代表并发采集、登录 API、完整数据交付或当前服务端行为。
relations:
  - type: derived_from
    target: ./benru-web-reverse-compilation/benru-web-20260223-01.md#comments-api-code
tags: [bilibili, comments, pagination]
---

# Bilibili 视频评论 API：主评论游标与二级回复分页

本文只拆出来源文章可定位的评论 API 路径、参数映射和分页控制。来源是微信公众号文章的本地归档，原始文章没有公开 locator；本文内容仍是 `source-report`，不代表当前接口可用。

<a id="interfaces"></a>
## 接口

来源代码列出两类 GET 请求：

| 接口 | 用途（按来源代码） | 来源定位 |
|---|---|---|
| `/x/v2/reply/wbi/main` | 获取视频主评论页 | [接口定义](./benru-web-reverse-compilation/benru-web-20260223-01.md#comment-api-overview)、[完整实现](./benru-web-reverse-compilation/benru-web-20260223-01.md#comments-api-code) |
| `/x/v2/reply/reply` | 获取某条主评论下的二级回复页 | [接口定义](./benru-web-reverse-compilation/benru-web-20260223-01.md#comment-api-overview)、[完整实现](./benru-web-reverse-compilation/benru-web-20260223-01.md#comments-api-code) |

归档代码中的通用请求封装把 URI 与参数编码到 GET URL，再交给异步 HTTP 客户端。这里不复述或判定 WBI 签名构造：原文相关写回与[既有 WBI 记录](./bilibili-wbi-geetest-case.md)冲突，须按该冲突边界处理。

<a id="parameters"></a>
## 参数映射

下表只表达文章所载调用代码，不记录任何请求样值：

| 接口 | 字段 | 来源代码中的含义 |
|---|---|---|
| 主评论 | `oid` | 调用参数 `video_id` |
| 主评论 | `mode` | 评论排序枚举对应值 |
| 主评论 | `type` | 固定为视频类型标记 `1` |
| 主评论 | `ps` | 来源代码固定每页数量为 `20` |
| 主评论 | `next` | 首次从 `0` 开始，后续使用响应游标字段 |
| 二级回复 | `oid` | 调用参数 `video_id` |
| 二级回复 | `type` | 固定为视频类型标记 `1` |
| 二级回复 | `root` | 主评论标识参数 `root_comment_id` |
| 二级回复 | `pn` | 页码，来源代码从 `1` 开始递增 |
| 二级回复 | `ps` | 每页数量，来源代码默认 `20` |
| 二级回复 | `mode` | 评论排序枚举对应值 |

来源定位：[完整评论请求实现](./benru-web-reverse-compilation/benru-web-20260223-01.md#comments-api-code)。

<a id="request-chain"></a>
## 请求与分页链路

1. 主评论请求以首游标开始，读取响应中的 `cursor.is_end`、`cursor.next` 与 `replies`。
2. 来源代码在结束标记、空评论页或调用方设置的数量上限达到时退出主评论循环，并在页面之间等待配置的间隔。
3. 若启用二级回复收集，代码按主评论逐条检查回复计数；有回复时调用二级接口，从页码 `1` 递增，并以 `page.count` 判断是否到末页。
4. 评论数据通过回调交给调用方；来源代码的主评论返回列表不会自动把二级回复嵌入主评论对象。

此链路在来源代码中是逐次 `await`，没有展示并发调度。分页字段、终止条件与调用顺序的定位见[游标说明](./benru-web-reverse-compilation/benru-web-20260223-01.md#comment-pagination)及[完整实现](./benru-web-reverse-compilation/benru-web-20260223-01.md#comments-api-code)。

## 边界

- 来源把登录描述为人工扫码和本地 Cookie 存在性轮询；没有记录登录 HTTP API 请求链或服务端登录验收，因此本卡不描述登录接口。
- 原文 WBI 实现与既有 Bilibili WBI 记录冲突，签名算法和线上参数写回方式均不从该来源提炼。
- 原文末尾的远程图片未下载或视觉审阅，也未被本卡引用。
- 本文未运行来源代码、访问 Bilibili、发送请求或验证当前接口；目标版本、观测时间、响应稳定性与服务端接受状态均未知。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源代码列出主评论和二级回复两个 GET 路径 | s1：`#comment-api-overview`、`#comments-api-code` | source-report | 归档代码呈现的评论调用 | 未验证当前接口 |
| C2 | 主评论使用游标，二级回复使用页码与总数终止 | s1：`#comment-pagination`、`#comments-api-code` | source-report | 归档文章中的分页实现 | 未运行代码或服务端验收 |
| C3 | 来源代码描述的是逐次等待的分页调用，并非已证实的并发采集 | s1：`#comment-pagination`、`#comments-api-code` | source-report | 该文所载代码路径 | 不外推吞吐量、完整性或其他客户端 |
