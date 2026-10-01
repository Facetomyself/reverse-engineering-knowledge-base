---
schema_version: 2
id: replace-reference-id
document_type: reference
original_date: unknown
archived_date: unknown
scope:
  targets: [replace-target]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./replace-source.md#replace-anchor
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 仅整理来源描述，未独立复现，范围之外未知。
relations:
  - type: derived_from
    target: ./replace-source.md#replace-anchor
tags: []
---

# 替换为目标参考卡标题

明确这份参考卡解决哪个检索问题。仅保留实际有来源的模块，不预生成四个空壳。

<a id="parameters"></a>
## 参数机制

分开 signature、encryption、encoding、token、fingerprint。记录位置、来源、输入依赖、生命周期及未知项。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 替换为有范围的结论 | s1 与段落 | source-report | 与 scope 对齐 | 明确未验证项 |

## 验证与限制

记录缺失模块、不适用范围和需要重验的变化；不把某项局部自验当成全站已验证。
