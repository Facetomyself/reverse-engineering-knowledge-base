---
schema_version: 2
id: web-phase3-static-coverage-runtime-boundary-case
document_type: case
original_date: unknown
archived_date: 2026-10-26
scope:
  targets: [jsvmp-purecalc-deliveries]
  client: web
  version: unknown
  observed_at: 2026-10-26 source review
sources:
  - id: s1
    ref: null
    basis: source-report
    citation: 三期私有案例归档（脱敏）：多份 JSVMP/纯算交付说明与对拍报告
    reason: 原始材料未提供可公开定位的链接
modules:
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 仅整理脱敏交付说明中的证据分层；未执行目标脚本、未重放请求，也未验证当前服务端接受。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 分支与快照边界来自来源自述；没有把静态产物推断为运行时等价实现。
tags: [jsvmp, coverage, validation, source-report]
---

# 从“覆盖率”到“可接受结果”：三期 JSVMP 交付的证据边界

## 问题与范围

三期的多个纯算/符号执行交付使用了不同的“完成”口径：有的统计静态字节码指令，有的统计单路径节点对拍，有的依赖固定环境快照后得到业务结果。本案例只讨论如何解释这些数字，**不**讨论任何目标站点的参数、密钥、指纹或可运行实现。

## 过程与关键证据

### validation

1. 先把证据拆成三类：静态覆盖（扫描到的 opcode/指令）、局部语义对拍（输入和节点输出的比较）、端到端结果（请求或业务响应）。
2. 静态覆盖只能说明产物包含对应 handler 或指令位置；它不说明每个状态都被执行，也不说明异常、分支合流和宿主输入成立。
3. 单路径对拍可证明给定输入下的局部一致性，但未覆盖状态、被吞掉的异常路径和缺少的宿主字段必须单独列出。
4. 快照驱动的成功结果只能绑定到该快照、版本和输入分布；换环境或换会话前，不能把它当作任意新输入的算法证明。

### decision-flow

把验收顺序固定为：`static-inventory -> path/branch-evidence -> changed-input-replay -> endpoint-acceptance`。任一层缺失时，结论降级到已有层级，并记录下一层的缺口；不能用更高层的文字自述补齐缺失证据。

## 结论与反例

- **C1（source-report）**：静态指令 100% 与语义交付完成不是同义词。适用于包含未执行 opcode、未覆盖状态或无差分对拍的交付；限制是本案例未独立运行来源实现。
- **C2（source-report）**：节点对拍比例较低时，局部一致不支持“全路径签名正确”；异常分支和宿主缺口需作为负结果保留。适用于报告明确列出跳过节点或环境缺失的交付。
- **C3（source-report）**：固定快照下的 endpoint 成功不能外推到全新会话。应同时记录快照来源、变更输入重放和服务端验收范围；缺一项就维持 source-report。

反例是：即使一个项目同时给出高静态覆盖和少量 endpoint 成功，也不能据此宣称所有 handler、分支和环境组合已恢复；需要新增输入、分支和版本的独立证据。

## 未决项与复用启示

复用时建议在报告中分别登记 `static_coverage`、`executed_paths`、`changed_input_replay` 和 `endpoint_acceptance` 四个字段，并为每个字段写证据定位与限制。这样可以把“产物存在”“局部可对拍”“当前服务端接受”分开检索，避免把历史成功自述升级为当前 runtime 事实。本篇没有提供任何目标代码、请求样本或敏感环境值。
