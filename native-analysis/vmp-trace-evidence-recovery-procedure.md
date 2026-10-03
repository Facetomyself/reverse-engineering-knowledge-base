---
schema_version: 2
id: native-analysis-vmp-trace-evidence-recovery-procedure
document_type: procedure
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [ARM64 VMP trace evidence recovery]
  client: native analysis
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ai-assisted-vmp-trace-recovery.md#方法论从输出往回走
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 这是从来源复盘抽取的证据流程，不代表任意 VMP 样本、trace 工具或 MCP 实现均可直接复用。
  - name: validation
    anchor: acceptance
    sources: [s1]
    basis: source-report
    limits: 验收项是证据闭合定义；本轮未取得来源 trace、binary、脚本或运行回执。
relations:
  - type: derived_from
    target: ./ai-assisted-vmp-trace-recovery.md#方法论从输出往回走
tags: [ARM64, VMP, trace, tracedb, producer, dataflow, cross-run, source-report]
---

# ARM64 VMP Trace 证据闭环流程

这是一套从来源复盘中提炼的 Native trace 分析流程：把大体量执行轨迹变成可查询证据面，再从输出边界反向定位 producer，最后用前向断言和跨 run 对照收束结论。它适用于需要区分 transport/dispatch 与真实计算的 ARM64 VMP 分析；不适用于把单次 replay、局部常量命中或来源作者自述直接当作当前样本算法证明。

<a id="prerequisites"></a>
## 前提与输入

- 有明确的输出切片、调用入口和每次 run 的唯一标识；未知的输出边界不能作为流程已通过的前提。
- 原始 trace 保持只读，并能建立按 `trace_id`、地址、值、寄存器、PC 和调用层查询的索引。索引是检索工具，不替代原始证据。
- 有 producer/data-flow、PC 统计和外部调用定位能力；随机数、JNI、libc 或 syscall 等外部来源应单独记账。
- 有独立的前向断言环境，能对已识别的标准 primitive 做逐字节或逐字段比较；不能把“能 replay trace”当成算法实现。
- 不把算法名称、固定长度、ASCII 值或密码学常量当作先验结论；它们只能作为待验证假设。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 固化输出边界和 run manifest | 输出区间、入口、run ID、采集环境和完整性摘要 | 边界闭合走 S2；缺输出或 run 归属不清走 F1 |
| S2 | 将只读 trace 建成索引证据面 | 固定宽度记录、地址/值/寄存器/PC/调用索引及查询版本 | 查询可重复走 S3；只能全文滚动或索引与原文不一致走 F1 |
| S3 | 从输出切片反向追第一真实 producer | producer 链、operand 链、PC 计数、调用层和外部来源标记 | 计算链闭合走 S4；命中 transport/dispatch/外部返回值时记录边界后分支处理 |
| S4 | 对候选算法做结构与算术核验 | round/template/count、输入依赖、常量来源、候选淘汰记录 | 证据支持候选走 S5；只有值相似或单 run 命中走 F2 |
| S5 | 写独立前向断言 | primitive 输入、字段布局、标准库结果和目标输出的比较结果 | 逐字节/逐字段相等走 S6；只能复现中间状态或依赖 trace tape 走 F3 |
| S6 | 做跨 run 对照并分离固定项与随机项 | 固定/变化字段表、第二 run 结果、结论版本和残余未知项 | 变化解释与断言均闭合则输出；出现矛盾走 F4 |

### S3 的外部来源分支

如果 producer 链在 `rand`、JNI、libc 或 syscall 返回值处停止，不要用常量或最近一次 `mov` 填空。转到调用层记录函数、参数、返回值归属和 run ID，并把该字段标为外部输入；只有内部计算仍可追踪的部分继续进入 S4。

### S4 的候选淘汰规则

值相同不代表来源相同。候选至少要同时回答：谁写入、读了哪些 operand、在哪些 PC/模板中重复、计数是否与结构一致、跨 run 哪些项稳定，以及是否能被标准 primitive 的 I/O 解释。任何一项缺失都只能保留为 hypothesis，不能写成已还原算法。

<a id="outputs"></a>
## 输出

每次分析至少保留以下可定位产物：

1. `run manifest`：输出边界、run 归属、原始 trace 摘要和查询版本。
2. `lineage table`：输出字节/字段到真实 producer、operand、PC、调用层或外部来源的链路。
3. `hypothesis log`：候选、支持证据、反例、淘汰原因和当前状态。
4. `forward assertions`：输入、字段布局、算法 primitive 和结果比较；敏感常量与原始样本留在受限证据区，不写入 Public 文档。
5. `cross-run matrix`：固定项、输入相关项、随机项和尚未解释的变化。

<a id="acceptance"></a>
## 验收

- A1：同一查询在相同索引版本上能回到原始 trace 行，并保留 run ID；不能只给截图或口头摘要。
- A2：每个声称已还原的输出字段都有 producer/operand 边界；外部返回值明确标为外部输入。
- A3：结构计数、轮/模板和算术关系彼此一致；“像 AES/SHA/HMAC”不算通过。
- A4：独立前向实现能在不依赖 trace tape 的情况下，与目标字段逐字节或逐字段相等。
- A5：至少一次跨 run 对照能解释固定项与变化项；未解释的字段继续标记 unknown，不晋升结论。

上述验收是来源报告抽取的流程定义，不是本轮对任何目标 binary、trace、runtime、parity 或 server acceptance 的实测结果。

<a id="failure-exits"></a>
## 失败出口

**F1：采集或证据面不闭合。** 缺输出边界、run 归属、原始 trace 或可重放查询时，停止算法命名；补采或修复索引后重新从 S1 开始。

**F2：局部值相似。** 只有常量命中、ASCII 命中、单次长度匹配或单 run 公式时，保留 hypothesis 和反例，不生成算法 reference。

**F3：仅能 replay。** 如果结果依赖 trace tape、旧中间槽或不可解释的固定样本，不能称为前向实现；回到 S3 补 producer 或转为 archive-only。

**F4：跨 run 冲突。** 固定项/随机项与候选不一致时，冻结当前结论，记录冲突 run 和待查边界，不用新样本覆盖旧证据。

**F5：来源范围不足。** 来源没有公开 locator、binary、脚本或原始 fixture 时，只能以 `source-report` 记录流程和限制，不能升级为当前 runtime、parity 或 server-accepted 结论。
