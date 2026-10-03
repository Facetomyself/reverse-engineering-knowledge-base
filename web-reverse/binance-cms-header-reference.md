---
schema_version: 2
id: web-reverse-binance-cms-header-reference
document_type: reference
original_date: '2026-08-18'
archived_date: '2026-09-23'
scope:
  targets: [binance]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./binance-cms-header-case.md#cms-request-chain
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只整理来源报告描述的公开 CMS 公告列表接口，不适用于交易、下单或其他 Binance API。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留字段角色与来源稿报告的输入关系；Cookie 值、设备画像原值和未公开 helper 实现不在本文，服务端是否校验未知。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 请求顺序和解析口径来自不可定位的本地对照稿；没有当前请求、响应或业务验收证据。
relations:
  - type: derived_from
    target: ./binance-cms-header-case.md#cms-request-chain
tags: [cms, headers, cookie-provenance, request-chain]
---

# Binance CMS 公告请求头参考

本条目整理来源报告中的公开 CMS 公告列表请求。它不是 Binance 交易签名说明，不能据此推断下单参数、交易 API secret 或其他接口行为。

<a id="interfaces"></a>
## 接口范围

来源稿描述一条公告列表 GET 请求，使用类型、页大小和页码一类分页条件，响应由本地代码直接按 JSON 解析。此处只登记该报告中的接口形状，不表示路径仍可用、无需会话或已由服务端接受。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 对照稿描述的是公开 CMS 公告列表，不是交易 API 的 HMAC 或下单路径。 | s1，来源 archive `#cms-request-chain` | source-report | Binance 公告列表对照稿 | 不外推至其他客户端、接口或当前服务。 |
| C2 | 对照稿描述以 GET 拉取分页列表并解析 JSON，再按首条文章差分。 | s1，来源 archive `#cms-request-chain` | source-report | 来源稿中的公告轮询逻辑 | 业务码与 HTTP status 未被该实现检查，差分口径不是已验证成功判据。 |

<a id="parameters"></a>
## 参数与头字段来源

| 字段 | 来源稿所述来源 | 使用边界 |
|---|---|---|
| `fvideo-id` | 从调用方提供的 Cookie 字段 `BNC_FV_KEY` 读取。 | 记录字段关系，不复制 Cookie 值。 |
| `fvideo-token` | 由另一个 Cookie 字段 `BNC_FV_KEY_T` 交给本地 JavaScript helper。 | helper 源码和具体变换未公开，不能据此实现或宣称 parity。 |
| `csrftoken` | 本地 helper 报告为对空字符串执行 JavaScript MD5。 | 来源稿没有证明服务端是否要求或校验该字段。 |
| `device-info` | 来源稿描述由硬编码设备画像及 JavaScript 指纹 helper 组装，再编码为头字段。 | 不复刻或复制作者设备画像；是否参与服务端风险判定未知。 |
| `bnc-uuid` / trace id | 来源稿描述为每次请求生成新的标识。 | 不推断服务端用途、生命周期或风控含义。 |

上述值的属性并不相同：有的来自 Cookie，有的由本地 helper 生成，有的是设备画像派生字段。仅凭字段名称相似或同时出现在请求头中，不能把它们合并成签名、加密参数或风险控制模块。

<a id="request-chain"></a>
## 请求链

来源稿描述的调用顺序为：调用方提供包含所需 FV 字段的 Cookie → 生成请求标识并组装头 → 发起公告列表 GET → 解析 JSON → 对文章列表执行轮询差分。以上是静态来源报告，不是可直接照搬的程序流程；Cookie 获取、业务错误处理和重试/失败出口未被证明完整。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C3 | 来源稿把两种 FV Cookie 字段映射到不同头字段，并描述本地组装其余头值。 | s1，来源 archive `#cms-request-chain` | source-report | 所引 BinanceApis 公告列表实现 | 源码不可用，字段是否必需或被接受未知。 |
| C4 | 来源稿称实现直接解析 JSON，没有检查 HTTP status 或业务 code。 | s1，来源 archive `#cms-request-chain` | source-report | 所引本地轮询实现 | 不将该薄封装口径当作正确性或 server-accepted 验收。 |

## 证据与限制

- 来源和可见范围见 [保留的来源案例](./binance-cms-header-case.md#cms-request-chain)；其本地项目材料不可公开定位，版本、客户端和观测时间未知。
- `News.js`、fvideo 变换细节及设备画像值不可见；本文不提供算法实现、Cookie/token 样值或可重放数据。
- `device-info` 的存在不能单独证明风险控制目的或服务端决策，因此不登记 `risk-control` 模块。
- 没有 runtime、local parity 或 server acceptance 证据；不据此建立可执行 procedure。
