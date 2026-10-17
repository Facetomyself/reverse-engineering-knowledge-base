---
schema_version: 2
id: babel-ast-node-types-reference
document_type: reference
original_date: unknown
archived_date: "2026-10-08"
scope:
  targets: [javascript-ast, babel]
  client: node
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./babel-ast-node-types.md#source-body
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只登记来源点名的节点类和分组。未对照 @babel/types 当前导出，未解析示例源码。
relations:
  - type: derived_from
    target: ./babel-ast-node-types.md#source-body
  - type: supplements
    target: ./babel-core-objects-reference.md#interfaces
tags: [babel, ast, node-types]
---

# Babel AST 节点类怎么分组

这张卡只回答：来源把 JavaScript AST 节点分成哪几类，以及 `const x = foo("hi")` 被拆成哪些节点。完整例子在 [来源归档](./babel-ast-node-types.md#source-body)。path、scope 和 types 工厂不在本卡。

<a id="interfaces"></a>
## 节点类

来源的分组是检索入口，不是规范全文。

| 组 | 来源点名的类型 | 来源怎么区分 |
|---|---|---|
| 基础 | `Program`、`Identifier`、字面量（`StringLiteral`、`NumericLiteral`、`BooleanLiteral`、`NullLiteral`、`RegExpLiteral`、`BigIntLiteral`） | 文件根、名字、值 |
| 声明 | `VariableDeclaration`、`VariableDeclarator`、`FunctionDeclaration`、`ClassDeclaration`、`ImportDeclaration`、`ExportNamedDeclaration` | 定义变量、函数、类或模块关系 |
| 语句 | `ExpressionStatement`、`ReturnStatement`、`IfStatement`、`ForStatement`、`WhileStatement`、`BlockStatement`、`BreakStatement`、`ContinueStatement` | 执行动作；`foo();` 整句是语句，`foo()` 本身不是 |
| 表达式 | `CallExpression`、`MemberExpression`、`BinaryExpression`、`LogicalExpression`、`AssignmentExpression`、`ConditionalExpression`、`ArrowFunctionExpression`、`ObjectExpression`、`ArrayExpression`、`NewExpression` | 会产生值 |
| 模式 | `ObjectPattern`、`ArrayPattern`、`RestElement`、`AssignmentPattern`、`SpreadElement` | 解构或参数接收；`RestElement` 收剩余值，`SpreadElement` 展开已有值 |

`const x = foo("hi")` 在来源里的父子关系是：`Program` → `VariableDeclaration` → `VariableDeclarator` → `Identifier` `x` 与 `CallExpression`（`Identifier` `foo` + `StringLiteral` `"hi"`）。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源按基础、声明、语句、表达式、模式五组列节点，并给了上表这些类型名 | s1 | source-report | 笔记中的示例语法 | 未核对 Babel 主版本是否仍用这些名字 |
| C2 | 一条语句会拆成多类节点；表达式语句包住调用表达式 | s1 的 `foo();` 与 `const x = foo("hi")` | source-report | 这两则例子 | 不是完整语法覆盖 |

## 验证与限制

没有 parameters、request-chain、risk-control 或 validation。这里没有 signature、encryption、encoding、token 或 fingerprint。对象 API 见 [五对象参考](./babel-core-objects-reference.md#interfaces)。本轮没有安装 Babel。
