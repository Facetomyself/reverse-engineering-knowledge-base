---
schema_version: 2
id: replace-procedure-id
document_type: procedure
original_date: unknown
archived_date: unknown
scope:
  targets: [replace-problem-class]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./replace-source.md#replace-anchor
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 整理的行动建议，不代表所有目标或工具版本均实测通过。
relations:
  - type: derived_from
    target: ./replace-source.md#replace-anchor
tags: []
---

# 替换为方法流程标题

说明目标问题、适用条件与明确不适用范围。

<a id="prerequisites"></a>
## 前提与输入

列出必需输入、环境、证据和应先满足的条件，未知不视为通过。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 替换为实际动作 | 可检查的产物 | 依据闭合走 S2，否则 F1 |
| S2 | 验收结果 | 对照记录 | 满足验收退出，否则 F1 |

流程图节点沿用 S1/S2/F1；正文是行为真源，图必须有失败出口。

<a id="outputs"></a>
## 输出

定义交付内容及其证据定位，不只写“成功”。

<a id="acceptance"></a>
## 验收

逐项定义可观察的通过条件、范围和反例，编辑校验不代替技术验收。

<a id="failure-exits"></a>
## 失败出口

F1：缺材料或证据不闭合时停止相关结论，保留未知并明确补采、回退或换路线的条件。
