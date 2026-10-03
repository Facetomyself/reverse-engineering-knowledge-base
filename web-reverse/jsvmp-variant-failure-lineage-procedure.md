---
schema_version: 2
id: web-reverse-jsvmp-variant-failure-lineage-procedure
document_type: procedure
original_date: "2026-06-22"
archived_date: "2026-10-02"
scope:
  targets: [jsvmp]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./jsvmp-variant-failure-lineage.md#真正修复的验收"
    basis: source-report
modules:
  - name: parameters
    anchor: prerequisites
    sources: [s1]
    basis: source-report
    limits: 绑定字段只按来源的最小记录要求整理。正文没有资源 hash、bytecode 或 opcode 表，本轮也没有补。
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 步骤是来源对“怎样才算修复”的记录顺序，不是提取器实现，也不是验证码求解。
  - name: validation
    anchor: acceptance
    sources: [s1]
    basis: source-report
    limits: 验收句子来自来源。来源写明独立运行复现本次为 0。本轮没有回放资源，也不把会话里的调用测试当成通过。
relations:
  - type: derived_from
    target: "./jsvmp-variant-failure-lineage.md#真正修复的验收"
tags: [jsvmp, variant-failure, source-report]
---

# JSVMP 变体失败谱系的记录与验收

这份流程只回答：旧样本能处理、新样本失败时，怎样记录失败阶段，以及怎样验收“提取器已修复”。它不重复 TDC 插桩、轮结构、动态 key、指纹或验证码求解。quote: 「本篇不重复算法、动态 key、指纹或验证码求解过程」。`kb_catalog.py query` 对 jsvmp、tencent、tdc 的 decision-flow、validation、parameters 都是 0。target unknown 上已有的决策卡和验收卡是 Frida、补环境、出处账本等无关题目，所以本卡不用 unknown。相关算法文和宿主原语文仍是 archive，不覆盖这些模块。

<a id="prerequisites"></a>
## 前提与输入

每次分析先绑定下面这些字段，再谈成功次数。quote: 每次分析绑定资源 hash 与来源时段，保留 bytecode/dispatcher 的版本线索、分析器版本、输入类型、目标边界以及失败阶段。

| 输入 | 来源要求 | 不足时 |
|---|---|---|
| 资源身份 | 资源 hash 与来源时段 | 不能把多次尝试算进同一组，停止“已修复” |
| 版本线索 | bytecode/dispatcher 的版本线索，加上分析器版本 | 无法判断是同一变体还是换了变体，走 F6 |
| 边界 | 输入类型、目标边界、失败阶段 | 失败阶段空着时，不能把最终成功次数当可靠性 |
| 原失败资源 | 保留原失败资源；公开报告只留结构和结论。quote: 公开报告仅留下结构和结论 | 没有原失败资源就不能做 S2 |

原始资源只放受控证据区。本流程不收集、不复述会话导出里的资源字节。

<a id="steps"></a>
## 步骤与分支

下表只整理来源已经写出的验收顺序。宿主原语若已有稳定观测点，可以先缩小问题，但更小的边界仍要绑定动态资源版本。quote: 「但更小的边界仍须绑定动态资源版本」。缩小范围不是跳过 S2 的理由。

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 保留原失败资源，定位缺失槽位来自哪个 handler、常量构造或控制流分支 | 槽位来源记录 | 定位到具体来源走 S2；资源内容缺失走 F1；opcode 或构造器对不上走 F2 |
| S2 | 修复后先用同一失败资源回放 | 同一资源是否仍失败 | 同一资源通过走 S3；换了另一份资源才通过走 F6 |
| S3 | 在多个独立资源变体上交叉验证，重点看结构差异而不是份数 | 结构差异覆盖记录 | 覆盖了结构差异走 S4；只增加同类样本走 F6 |
| S4 | 对齐候选与原始执行的输入、状态、位宽、输出和必要副作用；未知继续标未知 | 对拍记录或未知标记 | 对齐走 S5；执行不一致走 F4；槽位或位宽未确认走 F3 |
| S5 | 将解析兼容性、本地语义一致和下游业务结果分别报告 | 三份分开的结果 | 三份都有记录则进入验收；业务拒绝走 F5 |

<a id="outputs"></a>
## 输出

交付三样东西，不交付一个合并成功率。quote: 不合成一个模糊的「成功率」。

1. 按资源版本和失败阶段分组的记录。同一资源重试、同类新资源重试、换了变体重试分开统计。quote: 同一资源重试、同类新资源重试和换了变体重试必须分开统计。
2. 公开报告里的结构和结论。原始资源不进入公开报告。
3. 三份分开的结果：解析兼容性、本地语义一致、下游业务结果。

换了变体之后最终成功，只说明至少一种变体可处理。quote: 「也只说明至少一种变体可处理」。这不是本流程的完成输出。

<a id="acceptance"></a>
## 验收

通过要同时满足：

- 原失败资源还在，并且修复后用的是这一份，不是新样本。quote: 确认不是换样本掩盖问题。
- 缺失槽位已经指到 handler、常量构造或控制流分支之一。quote: 定位缺失槽位来自哪个 handler、常量构造或控制流分支。
- 交叉验证覆盖的是结构差异。quote: 资源数量本身不是充分条件，重点是覆盖结构差异。
- 未知 opcode 或未确认分支仍标未知，没有用默认值填上。quote: 未知 opcode 或未确认分支继续标未知。
- 解析兼容、本地语义一致、下游业务结果是三行记录，而不是一个成功率。

反例：会话称已建立 opcode 分析并做过调用测试，但来源把这一档标成未在本次重新执行。quote: 「这些成功声明未在本次重新执行」。来源同时写独立运行复现本次为 0。quote: 「本次为 0」。因此作者会话里的“任务完成”不是本流程的通过。

<a id="failure-exits"></a>
## 失败出口

F1：资源获取失败。内容缺失、截断或不是目标脚本时，结论是 acquisition failure，不能算算法失败。quote: 「acquisition failure，不能算算法失败」。补资源，不改提取器结论。

F2：解析与映射对不上。opcode 或构造器形态无法匹配时，当前变体不支持，并保存最小反例。quote: 「当前变体不支持；保存最小反例」。不要把异常捕获写成新 opcode 已被识别。

F3：语义提取不完整。预期槽位缺失、位宽或 signedness 未确认时，候选不完整，不填默认值继续。quote: 「候选不完整，不填默认值继续」。

F4：本地对拍不一致。保留首个分叉和对应输入。quote: 「保留首个分叉和对应输入」。不要用下游结果掩盖这一分叉。

F5：下游业务拒绝。本地已经一致时，与资源时效、会话和请求面分别分析。quote: 「与资源时效、会话和请求面分别分析」。不要把它记成算法失败，也不要把它记成算法通过。

F6：重试成功被当成修复。不能用「任务完成」「重试生效」覆盖更具体的未解决事实。quote: 「不能用「任务完成」「重试生效」覆盖更具体的未解决事实」。第三种重试即使成功，也回到输出里的“至少一种变体可处理”，不进入验收。
