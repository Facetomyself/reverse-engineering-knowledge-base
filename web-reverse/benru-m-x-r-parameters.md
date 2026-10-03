---
schema_version: 2
id: web-reverse-benru-m-x-r-parameters
document_type: reference
original_date: '2026-06-12'
archived_date: '2026-10-01'
scope:
  targets: [mashangpa.com (source report; unverified)]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./benru-web-reverse-compilation/benru-web-20260612-01.md#二请求头参数-m-的生成逻辑
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 仅记录来源作者对题七参数位置和依赖的陈述；源文样例 m/x 数值与公式不符，集成 Python 多发 ts 头且无 HAR、bundle、response fixture 或运行结果；未确认当前站点、服务端接受或 parity。
relations:
  - type: derived_from
    target: ./benru-web-reverse-compilation/benru-web-20260612-01.md#二请求头参数-m-的生成逻辑
tags: [m, x, r, md5, sha256, aes-cbc]
---

# 码上爬题七 m/x/r 参数关系（来源报告）

本文是检索用参考卡，不是可直接运行的协议实现、服务端验收或 parity 结论。目标域来自来源正文，尚未独立复核。

<a id="parameters"></a>
## 参数角色与关系

来源将题七一个 Ajax 请求描述为：请求头有 `m`、URL query 有 `x`，响应 JSON 有 `r`。按原文片段，它们分属请求侧的两个 hash 参数和响应侧密文字段；`r` 未被描述为 `m/x` 的输入。

| claim_id | 来源报告的关系 | 来源与定位 | basis | 范围与限制 |
|---|---|---|---|---|
| C1 | 请求头 `m`：来源称其为 `MD5("xialuo" + 当前毫秒时间戳)` 的小写 hex；时间戳作为计算输入。 | s1，物理行 71–95 | source-report | 仅针对原文所述 problem-detail/7；没有原始 JS bundle、捕获值或重复样本。 |
| C2 | URL query `x`：来源称其为 `SHA256(m + "xxoo")`；JS 片段再调用 `encodeURIComponent`。依赖关系为 `m -> x`。 | s1，物理行 118–131 | source-report | 只记录算法与字段位置陈述，不确认实际 wire encoding 或服务端校验口径。 |
| C3 | 响应 JSON 字段 `r`：来源称其为 hex 密文，由前端按 AES-CBC/PKCS7 解密为 UTF-8，再 JSON.parse。原文列出占位 key 与 IV。 | s1，物理行 152–192 | source-report | 仅是来源描述的响应侧处理；无实际响应密文、明文 fixture 或 key/IV 独立核验。 |

### 关系边界

```text
request header: m = MD5("xialuo" + timestamp)
                         |
                         +--> query x = SHA256(m + "xxoo")

response JSON: r = source-reported hex ciphertext
               separate from the m -> x request-side derivation
```

上图只复述 s1 的字段角色与依赖，不表示请求已被服务端接受，也不证明 `m`、`x` 与 `r` 在运行时必然同时出现。

## 题六关联归档边界

`benru-web-20260525-01.md` 仅作为同站相邻题目的 archive/context locator。本切片没有对题六来源进行独立完整取证，因此不从该文引入 AES、Cookie、请求头或分页行为作为本卡结论；跨题共享字段、密钥、会话要求及接口行为均待单独审阅。不要把题六的材料外推成题七事实。

## 一致性与复用限制

- 原文展示的 `ts = 1749744000000`、`m = 5d41402abc4b2a76b9719d911017c592` 与所列 MD5 公式不匹配；按该公式计算得到 `753d091bc9a8c9eae000fbcc7537ca8f`。
- 原文展示的 `x = 7b3d979ca8330a940a7f7c9e2f0c6f0e6e2b5c9a8f4e1d2b3a4c5d6e7f8a9b0c` 也不等于对其示例 `m` 计算 `SHA256(m + "xxoo")` 的结果（`21fc1d840fe07d8f44410826e46d51eecdf6963fe7bbb604809e7407c1d0d795`）。示例数值不可当测试向量复用。
- 原文引用的 JS 赋值仅显示 `p926.headers.m = v67`；Python 集成代码另外把 `ts` 放进请求头。源文未解释该差异，因此不能据 Python 代码断定线上头集合。
- 没有 HAR、完整 `pagination7.js`、response fixture 或 Python 运行结果；不可宣称 local parity、server-accepted、当前可用或稳定复现。
- 本卡不登记 `validation`、`risk-control` 模块，不构成 procedure。状态、风控或服务端验收需要新的独立证据。
