---
schema_version: 2
id: web-reverse-yuanrenxue-match-31-aes-memory-scan-reference
document_type: reference
original_date: unknown
archived_date: "2026-10-13"
scope:
  targets: [yuanrenxue-match-31]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./yuanrenxue-match-31-source-archive.md#source-body
    basis: source-report
modules:
  - name: parameters
    anchor: key-schedule-method
    sources: [s1]
    basis: source-report
    limits: 仅提炼来源对公开练习题的算法定位方法；不收录原始 key、IV、token、样本明文或可直接生成目标 token 的代码，本轮未运行目标。
relations:
  - type: derived_from
    target: ./yuanrenxue-match-31-source-archive.md#source-body
tags: [yuanrenxue, match-31, WASM, AES-128, key-schedule, source-report]
---

# 猿人学 match/31：WASM AES 运行时材料定位参考

这张卡将来源文章的要点收敛为可检索的方法边界，不复制其可直接用于目标题目的 key、IV、token 样值或扫描代码。来源将目标描述为公开练习题；本文没有连接该目标或复现作者结果。

<a id="key-schedule-method"></a>
## 参数与算法定位

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源把 JavaScript 虚拟机壳与 WASM 加密实现分开：外层负责组织明文，WASM 导出函数处理加密。 | s1，WASM 包装段 | source-report | 猿人学 match/31 的来源样本 | 没有 WASM 文件或反汇编供本轮复核，不能推广到其他题目。 |
| C2 | 对标准 AES-128，运行时轮密钥扩展为 176 字节；来源建议在加密调用后检查线性内存中的候选区，并以 AES key-schedule 递推关系筛选，而不是只因静态数据段找不到 S-box 就认定算法已魔改。 | s1，内存扫描段 | source-report | 来源所述标准 AES 候选分析思路 | 候选位置、轮密钥是否仍驻留及误报情况取决于编译器、实现和断点时机，本轮未验证。 |
| C3 | 若已知一组明文 / 密文且加密模式确认为 CBC，来源用首块关系描述 IV 的反推方法：`IV = D_k(C0) ⊕ P0`。 | s1，IV 推导段 | source-report | 仅限合法持有的样本与已确认模式 | 未独立核对来源的模式判断、明文拼接或服务端结果；公式不是对目标算法的确认。 |
| C4 | 跨会话密文公共前缀可作为分组结构的初筛线索，但不能单独证明固定 IV、CBC 或固定明文首块。 | s1，token 形状段 | source-report | 来源展示的有限样本 | 原始 token 与明文样值已省略；来源样本数不构成普遍性证据。 |

## 验证与限制

- 原始 AES key、IV、token、明文模板和可运行内存扫描代码不进入本卡。
- 来源称其做过逐字节对拍与目标请求，但未提供原始夹具供本轮审计；上述结果均保持 `source-report`。
- 运行时内存扫描应限于被授权、可复现的样本；本参考不包含面向其他站点的通用 token 生成器或目标请求流程。
