---
schema_version: 2
id: web-reverse-baijiahao-runtime-header
document_type: reference
archived_date: '2026-10-01'
scope:
  targets: [baijiahao]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./baijiahao-runtime-header-case.md#案例作者页与列表
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 接口形态和传输档来自未公开对照仓的来源报告；未检查原始代码、请求或当前站点行为。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 仅记录字段名称、来源和粗略生命周期；不含 runtime、Cookie、账号或设备实际值，也没有字段 schema 或有效期证据。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅整理来源描述的页面到 JSONP 列表链；缺少完整参数、响应样本、重放和服务端验收证据，不是可执行 recipe。
relations:
  - type: supplements
    target: ./session-binding-double-write.md#技巧会话材料双写并且绑源
tags: [baijiahao, window-runtime, jsonp, request-chain]
---

# 百家号 Runtime 参数与 JSONP 列表链

本参考整理来源对照仓所述的页面参数来源、列表接口和传输上下文。这里的 `window.runtime` 是页面对象名称，不是本轮运行时观测；来源是无公开 locator 的本地报告，以下结论均为 `source-report`。

<a id="interfaces"></a>
## 接口与传输面

| 面 | 来源报告中的表面 | 已知关系 | 未知与边界 |
|---|---|---|---|
| 页面 | 作者页或文章页；来源示意为带现有 Cookie 的 GET | `window.runtime` 字段从返回 HTML 中解析 | 页面完整 URL、HTTP 头、重定向和登录流程未知 |
| 列表 | `mbd.baidu.com/webpage` 一类 JSONP；来源示意为 GET | query 至少使用字段名 `uk`；响应需剥除 JSONP callback 包装再解析 | 完整路径、其余参数、callback 生成、响应 schema 和错误码未知 |
| HTTP 客户端 | `curl_cffi`，`impersonate` 选项为 `chrome101` | 来源将其归为传输档，而非签名生成 | 不是当前网页 UA 的证据；本轮没有核验客户端版本或服务端兼容性 |

来源称列表请求头含 `Tenger-Mhor`，其字段来源与 Cookie `Hmery-Time` 的简短映射已在[会话材料双写参考](./session-binding-double-write.md#技巧会话材料双写并且绑源)记录；此处不重复展开，也不包含字段值。

<a id="parameters"></a>
## 页面字段与会话字段

| 字段 | 来源报告的来源/角色 | 生命周期线索 | 限制 |
|---|---|---|---|
| `uk` | 从页面 `window.runtime` 解析；被列入列表请求 query | 来源称由页面 HTML 提供，不是本地随机生成 | 值、类型、编码、完整依赖和有效期未知 |
| `otherext` | 同样从页面 `window.runtime` 解析 | 与本次页面 HTML 关联 | 来源仅举字段名，未给 schema 或列表接口使用细节 |
| `Tenger-Mhor` | 请求头字段名；来源称直接取 Cookie 字段 `Hmery-Time` | 页面 runtime 随 HTML 变化，Cookie 头随会话变化 | 具体双写映射见上方链接；Cookie 实际值不复制 |

<a id="request-chain"></a>
## 请求链

来源文章给出的链路可压缩为字段与阶段关系；它不包含可直接重放的请求值：

```text
existing page session
  -> GET author/article HTML
  -> parse window.runtime: uk, otherext
  -> build Tenger-Mhor header from Cookie field Hmery-Time
  -> GET mbd.baidu.com/webpage with uk and other fields
  -> unwrap JSONP callback -> parse list response
```

- 来源称页面 runtime 与 Cookie 头是两类材料，分别随 HTML 和会话变化；只刷新一侧时，列表仍可能为空。该诊断关系来自来源报告，未由本轮请求或 fixture 复现。
- JSONP 去壳失败时，来源建议先检查 callback 名称，而非假设存在本地 sign。来源没有公开完整 callback、响应结构或失败样本。
- `curl_cffi` 的 impersonation profile 只作为传输上下文记录；不把它写成签名、固定 UA 或当前服务端验收依据。

## 证据与边界

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | `uk`/`otherext` 由 HTML 内的 `window.runtime` 提供；header 字段取值来源是 Cookie 字段 | s1，来源 archive 第 38 行 | source-report | BaijiaApis 所述网页作者页/列表链 | 原始材料不可见；字段关系不等于当前服务行为 |
| C2 | 列表走 JSONP，解析前需要剥 callback；客户端使用 `curl_cffi` 的 `chrome101` profile | s1，第 44–45、48–51 行 | source-report | 来源报告的列表读取路径 | 缺少完整 endpoint、参数、响应和客户端版本 |
| C3 | HTML runtime 字段与会话 Cookie 头需分别考虑；来源文章建议 JSONP 去壳失败时检查 callback | s1，第 58 行 | source-report | 来源报告中的列表诊断经验 | 无本轮 runtime、parity、server-accepted 或失败 fixture |

原文未请求百度，也排除实际 runtime/Cookie 字段值；`2026-08-18` 是对照仓 HEAD 日期，不是观测时间或验证版本。当前接口、字段 schema、会话绑定、UA 以及服务端接受情况均未知。
