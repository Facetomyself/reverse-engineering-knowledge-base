---
schema_version: 2
id: while-switch-flattening-ast-reference
document_type: reference
original_date: '2025-10-13'
archived_date: '2026-10-02'
scope:
  targets:
    - while-switch-flattening
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./anti-crawler-web-20251013-01.md#12-控制流平坦化的核心思想打乱路线统一调度"
    basis: source-report
  - id: s2
    ref: "./anti-crawler-web-20251013-01.md#21-ast-反混淆的核心步骤通用"
    basis: source-report
  - id: s3
    ref: "./anti-crawler-web-20251013-01.md#32-用-babel-进行-ast-反混淆的具体实现"
    basis: source-report
  - id: s4
    ref: "./anti-crawler-web-20251013-01.md#42-实际场景的扩展应对复杂混淆"
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s2, s3, s4]
    basis: source-report
    limits: 四步是来源的概括。visitor 的初始状态和下一条边只按粘贴文本阅读：第一个 case，以及字面量赋值。加密 state、假 case 和动态跳转没有实现。没有运行 Babel。
relations:
  - type: derived_from
    target: "./anti-crawler-web-20251013-01.md#21-ast-反混淆的核心步骤通用"
tags:
  - control-flow-flattening
  - babel
  - source-report
---
# while(true) 加 switch 的平坦化形状

这张卡只回答两件事：来源把哪种结构叫控制流平坦化，以及粘贴的 Babel visitor 实际收集了哪些边。它不是某个站点的参数说明，也不是可以照跑的反混淆器。

<a id="decision-flow"></a>
## 调度器与四步

未混淆时，条件、循环和返回按书写顺序可读。平坦化之后，基本块放进 switch，下一块由 state 赋值决定。多层就是这层 case 里再套一个 switch。

> while(true)+switch(state)

> 用switch(state1)调度多个基本块

来源把还原概括成四步：认出调度器，记下 case 到下一 state 的映射，按映射串联，然后删掉 while、switch 和 state。这四步没有单独的验收样本，也没有写失败就停止的出口，所以不建流程。

> 识别调度器特征

> 删除混淆代码

### 粘贴 visitor 实际看的边

识别条件是 while 的测试为真，并且循环体里只有一个 switch。初始状态取 case 列表里的第一个值，不是状态变量声明式的初值。下一状态只从表达式语句里、左边是状态变量、右边是字面量的赋值读取。

> path.node.test.value === true

> initialState === null) initialState = caseValue

> nextState = stmt.expression.right.value

示例函数自己的奇偶分支把下一状态写在 if 里面。上面这个条件看不到那种赋值。来源稍后贴出的还原文本仍在 return 后面保留了外层语句。两处都只是文本对照。

> console.log("计算完成")

加密 state、没有逻辑的 case、用函数调用取下一状态，来源只说要另加逻辑，没有写进这个 visitor。

> state 变量加密：state 值不是固定数值

### 结论

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | `while(true)+switch(state)`。来源把单层平坦化的调度器写成 while(true) 加 switch(state)。 | ./anti-crawler-web-20251013-01.md:73 | source-report | decision-flow | 这是教学伪代码，不是某个站点的原脚本。 |
| C2 | `通过state变量控制下一个执行的case`。原来的跳转被换成对 state 的赋值。 | ./anti-crawler-web-20251013-01.md:75 | source-report | decision-flow | 未跟踪真实状态序列。 |
| C3 | `用switch(state1)调度多个基本块`。多层被写成外层 switch 的某个 case 里再套一层 switch。 | ./anti-crawler-web-20251013-01.md:84 | source-report | decision-flow | 没有给出层数上限。 |
| C4 | `识别调度器特征`。四步的第一步是认出循环、switch 和 state。 | ./anti-crawler-web-20251013-01.md:102 | source-report | decision-flow | 只是来源的概括。 |
| C5 | `收集基本块与 state 映射`。第二步收集 case，并记录执行后的下一个 state。 | ./anti-crawler-web-20251013-01.md:104 | source-report | decision-flow | 未定义映射缺失时怎么停。 |
| C6 | `还原控制流顺序`。第三步按 state 映射把基本块串起来。 | ./anti-crawler-web-20251013-01.md:106 | source-report | decision-flow | 没有验收样本。 |
| C7 | `删除混淆代码`。第四步删掉 while、switch 和多余的 state。 | ./anti-crawler-web-20251013-01.md:108 | source-report | decision-flow | 没有失败出口。 |
| C8 | `path.node.test.value === true`。粘贴的 visitor 只认条件为真且循环体里只有一个 switch 的 while。 | ./anti-crawler-web-20251013-01.md:164 | source-report | decision-flow | 对照的是粘贴文本，没有运行 Babel。 |
| C9 | `initialState === null) initialState = caseValue`。这段 visitor 把初始状态写成源码顺序上的第一个 case。 | ./anti-crawler-web-20251013-01.md:164 | source-report | decision-flow | 没有读取状态变量的初始化表达式。 |
| C10 | `nextState = stmt.expression.right.value`。下一个 state 只从对状态变量的字面量赋值读取。 | ./anti-crawler-web-20251013-01.md:164 | source-report | decision-flow | if 内部的状态赋值不在这个条件里。 |
| C11 | `state 变量加密：state 值不是固定数值`。来源把加密后的 state 列为需要另写逻辑的情况。 | ./anti-crawler-web-20251013-01.md:220 | source-report | decision-flow | 正文没有给出对应 visitor。 |
| C12 | `虚假 case：添加无实际逻辑的 case 节点`。来源把无逻辑 case 列为需要另写逻辑的情况。 | ./anti-crawler-web-20251013-01.md:222 | source-report | decision-flow | 覆盖率过滤没有实现。 |
| C13 | `动态跳转：通过函数调用获取下一个 state`。来源把函数调用产生的下一状态列为需要另写逻辑的情况。 | ./anti-crawler-web-20251013-01.md:224 | source-report | decision-flow | 没有符号执行步骤。 |
| C14 | `console.log("计算完成")`。来源打印的还原结果在 return 之后仍保留后续语句。 | ./anti-crawler-web-20251013-01.md:192 | source-report | decision-flow | 这是作者贴出的文本，不是本次运行结果。 |

## 验证与限制

近邻没有 while-switch-flattening 或 control-flow-flattening 的 decision-flow。另一篇来源的 24 位状态字是 for 循环里的打包整数，不是这里的 while(true) 加数字 case，所以不并进同一张卡。

没有运行 Babel，不能把作者贴出的还原文本当成这次复现。
