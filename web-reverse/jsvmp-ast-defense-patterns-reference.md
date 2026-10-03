---
schema_version: 2
id: jsvmp-ast-defense-patterns
document_type: reference
original_date: unknown
archived_date: unknown
scope:
  targets: [jsvmp]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: notes
    ref: null
    basis: source-report
    citation: 本地教学笔记（定位不公开）
    reason: 正式入库不保留讲次与公开定位；原始材料未随本文公开。
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [notes]
    basis: source-report
    limits: 缺 locator，未复现。只保留会改变可见控制流和指令语义的机制。不写谓词公式、填充字节、密钥派生和变长编码格式。超级指令和自修改字节码不入结论。域名绑定、画布和无头指纹不是本模块。
relations:
  - type: supplements
    target: ./jsvmp-custom-isa-interpreter-reference.md#decision-flow
tags: [jsvmp, ast, decision-flow]
---

# JSVMP 与 AST 混淆的防御手段

这份参考说明哪些手段会改变分析 JSVMP 时能看见的控制流和指令语义。它不记录风控指纹，也不提供可复现的混淆器。没有这些手段的小解释器更容易被模型和工具解开。这是分析上的判断，不是测量结果。

<a id="decision-flow"></a>

## 可见性怎么被打散

能留下的手段只到机制层。

- 用索引间接查找，不直接露出目标。
- 数字和常量改成另一种编码，计算结果不变。这是 encoding，不是 encryption，也不是 signature 或 token。
- 布尔和算术缠在一起，用来增加开销。没有变换专名。
- 不透明谓词：状态在范围内才进真逻辑，否则走假分支。没有谓词公式。
- 死代码占用上下文。行号和比例互相冲突，不采用。
- 控制流压进状态之后，顺序、分支和循环不再局部可见，并回到选择式分发。
- 函数拆开会增加跨块追踪。合并会把有用逻辑和无关逻辑揉在一起。

指令集和编码是核心。可以有多套映射，可以按函数定制。语义少则弱，语义多则字节变长。未使用的操作码可以垫在后面。栈、寄存器、程序计数和跳转也都可以编码。字节可以变长。变长格式本身不写入本文。

基本块的逻辑顺序和物理顺序可以不同，靠指针接上。直线一次派发开销小，也更容易被顺着读穿。这没有样本验证。动态映射或每次下发不同的字节码压力大，副作用也明显。没有置换表。

完整性只留到这一层：长度或内容里如果被要求含有填充或假字节，对不上就不给正确结果。执行器也做同类检查。可以把它理解成：设计了多余动作，就要检查这个动作还在。不记录填充字节、校验算法或密钥。密钥派生和时间戳可以绑在一起，步骤和密钥不写入本文。

短生命周期字节码是一次性的，或很快失效，下次再动态执行。没有时限数字。

域名绑定和画布一类检查不属于 VMP，它们是别的安全检验。无头浏览器会被检查，指纹细节不在这里展开。因此本文不建 risk-control，也不把这些写成 fingerprint 参数。超级指令和自修改字节码缺少稳定观察，不进结论。异常、异步的语法名和冷热路径难度也不采用。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 间接索引、常量换编码但结果不变、布尔与算术缠绕、不透明谓词、死代码占上下文，会改变可见语义 | notes | source-report | 机制层 | 无公式、无比例、无样本；编码不是 encryption |
| C2 | 控制流压进状态后，顺序、分支和循环不再局部可见，并回到选择式分发 | notes | source-report | 与解释循环的分发衔接 | 不是已验证的分发实现 |
| C3 | 拆函数增加跨块追踪，合并函数把有用逻辑和无关逻辑揉在一起 | notes | source-report | 机制层 | 没有块边界或样本 |
| C4 | 可以多套映射、按函数定制；未使用操作码可以后置；栈、寄存器、程序计数和跳转也可编码 | notes | source-report | 指令集与编码 | 不写映射表和变长格式 |
| C5 | 基本块的逻辑顺序可以不同于物理顺序；直线一次派发开销小且更容易被读穿 | notes | source-report | 未在样本上验证 | 不能当成已攻破 |
| C6 | 完整性是多余动作还在才给正确结果；短生命周期字节码会很快失效 | notes | source-report | 机制层 | 无校验算法、无填充字节、无时限 |
| C7 | 域名绑定和画布检查不属于 VMP；超级指令与自修改字节码不采用 | notes | source-report | 排除项 | 不建 fingerprint 或 risk-control |

## 验证与限制

与 [自定义指令集](./jsvmp-custom-isa-interpreter-reference.md) 互相补充。本文不推出任何生产站点算法，也不从教学样本派生美团 `mtgsig`。没有 parameters 模块：这里没有 signature、token 或 fingerprint 字段。常量换编码只记成 encoding，算法未给出。

缺 locator，未复现。字母映射表、死代码行号、原生函数替换、插桩检测和无头产品名都不进入正文。不能声称这些手段对某个站点有效。
