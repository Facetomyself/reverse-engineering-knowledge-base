---
schema_version: 2
id: ruyi-20260607-fingerprintjs-wrapper-reference
document_type: reference
original_date: '2026-06-07'
archived_date: '2026-10-02'
scope:
  targets: [fingerprintjs]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260607-01.md#常量定义
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留 marker、阈值、deflate-raw 和 text/plain。单次 body 摘要、随机字节和信号原值不在本卡。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留包装顺序和“明文不是纯常量”。作者的可逆结论保持 source-report，没有失败出口。
relations:
  - type: derived_from
    target: ./ruyi-20260607-01.md#常量定义
tags: [fingerprintjs, source-report]
---

# FingerprintJS demo POST 的包装边界

这篇卡检索的是：来源对 playground 上那一次 agent POST 的包装顺序，以及哪些部分不能从算法本身推出。不收录明文样本，也不收录单次随机字节。

<a id="parameters"></a>
## 包装参数

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 这个 POST body 的核心不是 RSA、ECC、AES 这类标准加密，也不是不可逆哈希。 | s1，源文件第 68 行 | source-report | 来源描述的这一次 agent POST | 不是对产品全部接口的定性 |
| C2 | 常量行同时标了未压缩 marker、已压缩 marker、padding 上限、XOR key 长度和压缩阈值。引文只截未压缩标记：// 未压缩 marker | s1，源文件第 100 行 | source-report | Ik 使用的那组常量 | 数值要读整行，不能只看这一截 |
| C3 | 是否压缩先看字节长度是否大于阈值，引文是 > qI，并且压缩能力可用。 | s1，源文件第 324 行 | source-report | Sk | ef() 没有展开 |
| C4 | 压缩点名 CompressionStream("deflate-raw") | s1，源文件第 331 行 | source-report | 超过阈值且压缩可用的支路 | 不是带 zlib 头的 deflate |
| C9 | 发出的请求体使用 "text/plain" | s1，源文件第 91 行 | source-report | Ik 的 POST | 不保留 URL 查询参数 |

<a id="decision-flow"></a>
## 顺序与不可纯算的部分

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | Vf 把未压缩 marker 和长度常量一起传入，引文是 QI, iI, uI | s1，源文件第 370 行 | source-report | Vf | 选择表达式与已压缩 marker 之间有不可见空白，不整段引用 |
| C6 | 载荷起点按 1 + marker.length + 1 + paddingLength + keyLength 累加。 | s1，源文件第 445 行 | source-report | of 的头部布局 | 该次 padding 长度是样本，不进入本卡 |
| C7 | 明文 JSON 本身是可读的、可解析的，但它不是纯常量。 | s1，源文件第 307 行 | source-report | 包装之前的采集结果 | 配置、会话和信号原值不抄 |
| C8 | 其中 wrapper 可逆，XOR 可逆，deflate-raw 可逆。 | s1，源文件第 77 行 | source-report | 来源的这一次 trace | 作者结论，本轮未复跑 |

## 验证与限制

`browser-fingerprint` 的既有卡只描述通用宿主对象，没有这层 marker 和 deflate-raw。明文生成依赖页面配置、会话、浏览器 API、图形、时间和随机源；本卡不保存这些取值。作者列出的四项对照没有失败时的停止条件，离线脚本也不在正文里，所以这里不是流程。
