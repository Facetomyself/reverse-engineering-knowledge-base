---
schema_version: 2
id: xfq-undated-08-sequence-extract
document_type: reference
original_date: unknown
archived_date: '2026-09-04'
scope:
  targets: [babel-sequence-expression-extract]
  client: node
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./xfq-undated-08.md#逗号表达式js
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只读脚本文本。示例打开了字面量和成员过滤、关掉了标识符过滤，但没有印出的结果可对照。for 的 test/update、二元和逻辑的右侧、成员表达式的 object 不在列出的父节点里。未处理的父节点只剩注释掉的 debugger。
relations:
  - type: derived_from
    target: ./xfq-undated-08.md#逗号表达式js
tags: [babel, sequence-expression]
---

# 逗号表达式按父节点外提还是只删纯值

这张卡回答 `FixSequenceExpression` 怎样处理 `SequenceExpression`：一类父节点把除最后一个以外的表达式外提或丢掉，另一类父节点只删除被过滤的纯值。三个开关是 `filter_literal`、`filter_identifier`、`filter_memberexpr`。脚本最后打印生成代码，没有期望文本，所以不是 procedure。依据保持 source-report。

<a id="decision-flow"></a>
## 父节点决定外提还是过滤

`is_literal` 接受字面量；`include_undefined` 为真时也接受名为 `undefined` 的标识符。一元表达式只递归参数，不看运算符。二元表达式要求左右都通过。`UpdateAST` 先生成代码再解析回 AST，遍历结束后调用一次。

插入点从当前节点向上找。没有父路径就返回 null。当前是赋值表达式时：父节点是表达式语句就记 `create_expr_stmt`；父节点不是逗号表达式就再记 `create_sequence_expr`；然后返回当前赋值。当前是语句、且不是 while 也不是 do-while 时，记 `create_expr_stmt` 并返回。走到 `Program` 时，对子节点记 `create_expr_stmt`。

会外提前缀的父节点是：数组、赋值、一元、表达式语句、return、二元表达式的左侧、逻辑表达式的左侧、if 或 while 的 test、for 的 init、switch 的 discriminant。找到插入点后，若标志里有 `create_sequence_expr`，先把目标包进新的逗号表达式，再把目标改到 `expressions[0]`。然后每次 shift 出第一项：过滤命中（字面量含 undefined、标识符、或成员表达式，由开关决定）就 `delete expr` 并继续；否则要么 `insertBefore` 一条表达式语句，要么按 `listKey` 插到目标前面。最后逗号表达式换成剩下的 `expressions[0]`。

另一类父节点是调用、成员表达式的 property、变量声明的 init。这里不外提，只在还没到最后一项时 splice 掉过滤命中的表达式；如果只剩一项，就把逗号表达式换成它。其它父节点直接落到注释掉的 `debugger`，函数没有别的返回。

示例把 `filter_literal` 和 `filter_memberexpr` 设为真，`filter_identifier` 设为假，然后调用这个遍历。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 二元表达式要两侧都是字面量才算字面量 | `if (types.isBinaryExpression(node)) return is_literal(node.left) && is_literal(node.right)` | s1 ./xfq-undated-08.md:47 | source-report | 一元只递归 argument |
| C2 | 没有父路径则不能插入 | `return null;` | s1 ./xfq-undated-08.md:67 | source-report | 注释说当前一般已是 Program 的 path |
| C3 | 表达式语句里的赋值要建表达式语句 | `flags.push('create_expr_stmt');` | s1 ./xfq-undated-08.md:79 | source-report | 同名标志后面还会 push；这里父节点是 ExpressionStatement |
| C4 | 赋值的父节点不是逗号表达式时要再包一层逗号表达式 | `flags.push('create_sequence_expr');` | s1 ./xfq-undated-08.md:82 | source-report | 只出现在赋值这一支 |
| C5 | while 语句不作为插入点 | `!current.isWhileStatement()` | s1 ./xfq-undated-08.md:94 | source-report | 下一行同样排除 do-while |
| C6 | 数组元素里的逗号表达式走外提 | `parent_path.isArrayExpression()` | s1 ./xfq-undated-08.md:128 | source-report | 同一条件还有赋值、一元、表达式语句和 return |
| C7 | 二元表达式只处理左侧 | `(parent_path.isBinaryExpression() && sequence_path.key === 'left')` | s1 ./xfq-undated-08.md:135 | source-report | 逻辑表达式的下一行同样只写 left |
| C8 | if 的 test 走外提 | `parent_path.isIfStatement()` | s1 ./xfq-undated-08.md:138 | source-report | while 的 test 写在后面，条件是 key === 'test' |
| C9 | for 只点名 init | `(parent_path.isForStatement() && sequence_path.key === 'init')` | s1 ./xfq-undated-08.md:141 | source-report | test 和 update 不在这个条件里 |
| C10 | switch 只处理 discriminant | `(parent_path.isSwitchStatement() && sequence_path.key === 'discriminant')` | s1 ./xfq-undated-08.md:142 | source-report | 没有 case 体内的单独规则 |
| C11 | create_sequence_expr 会把目标包进新的逗号表达式 | `target.replaceWith(types.sequenceExpression([target.node]));` | s1 ./xfq-undated-08.md:155 | source-report | 下一行把 target 改到 expressions[0] |
| C12 | 外提前可以按字面量过滤丢掉 | `(options.literal && is_literal(expr, true))` | s1 ./xfq-undated-08.md:165 | source-report | 同一 if 还有标识符和成员表达式 |
| C13 | 过滤命中时对局部变量 delete | `delete expr;` | s1 ./xfq-undated-08.md:169 | source-report | 节点已经 shift 出表达式数组 |
| C14 | create_expr_stmt 时用 insertBefore | `target.insertBefore(types.expressionStatement(expr));` | s1 ./xfq-undated-08.md:176 | source-report | else 分支按 listKey splice |
| C15 | 外提后逗号表达式换成剩下的第一项 | `sequence_path.replaceWith(expressions[0]);` | s1 ./xfq-undated-08.md:182 | source-report | 此时长度应已减到 1 |
| C16 | 调用表达式不走外提 | `parent_path.isCallExpression()` | s1 ./xfq-undated-08.md:190 | source-report | 同一支还有成员 property 和声明 init |
| C17 | 成员表达式只处理 property | `(parent_path.isMemberExpression() && sequence_path.key === 'property')` | s1 ./xfq-undated-08.md:191 | source-report | object 一侧不在条件里 |
| C18 | 这一支用 splice 删掉当前项 | `expressions.splice(i, 1);` | s1 ./xfq-undated-08.md:205 | source-report | 循环停在最后一项之前 |
| C19 | 只剩一项时才替换逗号表达式 | `expressions.length === 1 && sequence_path.replaceWith(expressions[0]);` | s1 ./xfq-undated-08.md:212 | source-report | 过滤不掉的前缀会留下 |
| C20 | 未列出的父节点没有别的处理 | `// debugger;` | s1 ./xfq-undated-08.md:217 | source-report | 这行是注释 |
| C21 | 字面量开关来自 filter_literal | `literal: Boolean(my_params.filter_literal),` | s1 ./xfq-undated-08.md:222 | source-report | 标识符和成员表达式是另两个布尔 |
| C22 | 遍历后重新生成并解析 | `UpdateAST(cfg);` | s1 ./xfq-undated-08.md:236 | source-report | 定义是 generator 后再 parse |
| C23 | 示例打开字面量过滤 | `filter_literal: true,` | s1 ./xfq-undated-08.md:246 | source-report | 下一行把标识符过滤设为 false |
| C24 | 示例打开成员表达式过滤 | `filter_memberexpr: true` | s1 ./xfq-undated-08.md:248 | source-report | 没有打印结果 |

## 验证与限制

不把示例那一行输入的嵌套数组当成已经化简后的输出。`delete expr` 发生在 `expressions.shift()` 之后，不能读成从父节点再删一次。for 的 test/update、二元和逻辑的右侧、成员的 object 都没有被点名。未命中的父节点不会抛错，只会落到注释。没有本地运行，也没有 Babel 版本。
