---
schema_version: 2
id: ruyi-20260611-ruishu-pack-parameters
document_type: reference
original_date: "2026-06-11"
archived_date: "2026-10-02"
scope:
  targets: [ruishu]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260611-01.md#加密和封包结构
    basis: source-report
  - id: s2
    ref: ./ruyi-20260611-01.md#key-wrapper
    basis: source-report
  - id: s3
    ref: ./ruyi-20260611-01.md#自定义-base64
    basis: source-report
  - id: s4
    ref: ./ruyi-20260611-01.md#7ibksfl8
    basis: source-report
  - id: s5
    ref: ./ruyi-20260611-01.md#p-cookie-字节布局
    basis: source-report
  - id: s6
    ref: ./ruyi-20260611-01.md#property57-编码
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s3, s4, s5, s6]
    basis: source-report
    limits: 只保留封包层次、key 归一化规则、CRC 多项式、自定义编码差异、状态明文依赖、P Cookie 外层差异、raw74 长度和 property57 补齐字节。不收录字母表、cookie 值、token 或 fresh 数字。
relations:
  - type: derived_from
    target: ./ruyi-20260611-01.md#加密和封包结构
tags: [ruishu, source-report]
---

# 瑞数企业版封包的参数层次

这篇卡检索的是：该文把这个理财页的外层封包拆成哪些层。不重复已有瑞数卡里的请求顺序和验收口径，也不提供字母表或会话材料。

<a id="parameters"></a>
## 封包参数

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 主体不是公钥算法：这个站点当前链路的核心不是 RSA/SM2，也不是 Wasm。 | s1，源文件第 167 行 | source-report | 文中这个页面 | 后面的层次才是可检索的参数 |
| C2 | 对称层写成 AES-128-CBC | s1，源文件第 191 行 | source-report | 文中 encrypt/decrypt 入口 | 没有 key 或 IV 样值 |
| C3 | wrapper 的尾部规则：尾部 5 字节中，最后 1 字节是 xor byte，中间 4 字节常被用作时间或状态字段。 | s2，源文件第 217 行 | source-report | key 不是 16 字节时 | 不复制 key 字节 |
| C4 | CRC 多项式写成 0xedb88320 | s1，源文件第 242 行 | source-report | 外层 CRC32 | 未重跑校验 |
| C5 | 编码层：外层不是标准 Base64，而是站点自定义字母表。 | s3，源文件第 253 行 | source-report | URL 参数、body 和 P Cookie 外层 | 字母表原文不在本卡 |
| C6 | URL 后缀还要有同一轮状态明文 | s4，源文件第 299 行 | source-report | 动态 URL 后缀 | 不展开状态明文 |
| C7 | P Cookie 外层停在版本号：这一层，而是版本号 | s5，源文件第 380 行 | source-report | P Cookie，不是 URL/body 那一层 | 上一句写明不再套 name 加 CRC；cookie 值不在本卡 |
| C8 | 第三段长度门：raw74.length === 74 | s6，源文件第 401 行 | source-report | cookie 第三段输入 | 字段表在正文中是空的 |
| C9 | 比特流补齐字节写成 fillByte=184 | s6，源文件第 410 行 | source-report | property57 编码 | 码表不在本篇 |

## 验证与限制

`../../web-reverse/products/ruishu-rs6-challenge.md` 和 `../../web-reverse/products/ruishu-rs6-hybrid.md` 已经覆盖 request-chain 与 validation，没有这组封包参数，所以不把本篇并进去，也不再拆一条链路卡。响应前缀长度、JSON 起点和“最终 JSON 要有 page/resultList”在正文第 329 到 336 行，仍属于同一参数层，不单独立项。fresh 验收数字保持 source-report。文末指向站外全文，PROPERTY57_TABLE 和字段含义表都没有出现。
