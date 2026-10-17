---
schema_version: 2
id: babel-ast-node-types
document_type: archive
original_date: unknown
archived_date: "2026-10-08"
scope:
  targets: [javascript-ast, babel]
  client: node
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: null
    basis: source-report
    citation: "AST 节点体系基础类型"
    reason: "原始材料未提供作者名或可公开定位的链接"

source_completeness: complete
relations: []
tags: [babel, ast, node-types]
---

# AST 节点体系基础类型

来源是一份没有作者名和公开链接的 AST 节点类型笔记。归档只保留原文分类和例子，不表示本轮用某个 Babel 版本跑过 parser。

## 清洗与完整性说明

无平台导航、无图、无表。代码块和节点名按原文保留。未从别处补节点。

<a id="source-body"></a>
## 来源正文

这部分属于 **JavaScript AST 的节点类型体系**，也可以叫：

- AST 节点类型
- Babel AST 节点类型
- JavaScript AST 节点分类
- AST Node Types
- Babel Node Types

它主要解决的问题是：

> JavaScript 源码被解析成 AST 之后，每一种语法结构对应什么节点类型。

例如：

```js
const x = foo("hi");
```

这行代码在 AST 中不会只是一个节点，而是会拆成多个节点，例如：

- `VariableDeclaration`
- `VariableDeclarator`
- `Identifier`
- `CallExpression`
- `StringLiteral`

---

## 1. 基础节点

基础节点是最常见、最底层的一批节点，通常表示文件、名字、字面量等内容。

### `Program`

表示整个 JavaScript 文件的根节点。

```js
const a = 1;
console.log(a);
```

整个文件最外层就是一个 `Program` 节点。

### `Identifier`

表示标识符，也就是代码里的名字。

```js
let x = 1;
function foo() {}
```

这里的 `x`、`foo` 都是 `Identifier`。

### `StringLiteral`

表示字符串字面量。

```js
"hello"
```

### `NumericLiteral`

表示数字字面量。

```js
123
```

### `BooleanLiteral`

表示布尔值。

```js
true
false
```

### `NullLiteral`

表示 `null`。

```js
null
```

### `RegExpLiteral`

表示正则字面量。

```js
/abc/g
```

### `BigIntLiteral`

表示大整数字面量。

```js
123n
```

---

## 2. 声明类节点

声明类节点表示“声明了某个东西”，比如变量、函数、类、模块导入导出等。

### `VariableDeclaration`

表示变量声明整体。

```js
let x = 1;
const y = 2;
```

整句 `let x = 1` 或 `const y = 2` 是 `VariableDeclaration`。

### `VariableDeclarator`

表示变量声明中的某一项。

```js
let x = 1, y = 2;
```

这里有一个 `VariableDeclaration`，里面有两个 `VariableDeclarator`：

- `x = 1`
- `y = 2`

### `FunctionDeclaration`

表示函数声明。

```js
function foo(a, b) {
  return a + b;
}
```

### `ClassDeclaration`

表示类声明。

```js
class User {}
```

### `ImportDeclaration`

表示模块导入。

```js
import React from "react";
```

### `ExportNamedDeclaration`

表示具名导出。

```js
export const name = "test";
```

---

## 3. 语句类节点

语句类节点表示一条可以执行的语句。语句通常强调“做一件事”，比如返回、判断、循环、跳出等。

### `ExpressionStatement`

表示表达式语句。

```js
foo();
a + b;
```

`foo()` 本身是 `CallExpression`，但整句 `foo();` 是 `ExpressionStatement`。

### `ReturnStatement`

表示 `return` 语句。

```js
return x;
```

### `IfStatement`

表示 `if` 条件语句。

```js
if (x > 0) {
  console.log(x);
}
```

### `ForStatement`

表示 `for` 循环。

```js
for (let i = 0; i < 10; i++) {
  console.log(i);
}
```

### `WhileStatement`

表示 `while` 循环。

```js
while (x > 0) {
  x--;
}
```

### `BlockStatement`

表示代码块，也就是 `{}` 包起来的内容。

```js
{
  let x = 1;
}
```

函数体、if 代码块、循环体通常都是 `BlockStatement`。

### `BreakStatement`

表示 `break`。

```js
break;
```

### `ContinueStatement`

表示 `continue`。

```js
continue;
```

---

## 4. 表达式类节点

表达式类节点表示“会产生一个值”的语法结构。

### `CallExpression`

表示函数调用。

```js
foo("hi");
```

其中 `foo("hi")` 是 `CallExpression`。

### `MemberExpression`

表示成员访问。

```js
obj.name
obj["name"]
```

### `BinaryExpression`

表示二元运算表达式。

```js
a + b
x > 10
```

### `LogicalExpression`

表示逻辑表达式。

```js
a && b
a || b
```

### `AssignmentExpression`

表示赋值表达式。

```js
x = 1
obj.name = "Tom"
```

### `ConditionalExpression`

表示三元表达式。

```js
flag ? a : b
```

### `ArrowFunctionExpression`

表示箭头函数表达式。

```js
const fn = () => {};
```

这里 `() => {}` 是 `ArrowFunctionExpression`。

### `ObjectExpression`

表示对象字面量。

```js
const obj = { name: "Tom" };
```

这里 `{ name: "Tom" }` 是 `ObjectExpression`。

### `ArrayExpression`

表示数组字面量。

```js
const arr = [1, 2, 3];
```

这里 `[1, 2, 3]` 是 `ArrayExpression`。

### `NewExpression`

表示 `new` 调用。

```js
new User()
```

---

## 5. 结构和模式类节点

结构和模式类节点经常出现在解构、函数参数、变量声明等地方。它们不是普通表达式，而是描述“怎么匹配或接收值”。

### `ObjectPattern`

表示对象解构模式。

```js
const { name } = user;
```

这里 `{ name }` 是 `ObjectPattern`。

### `ArrayPattern`

表示数组解构模式。

```js
const [first, second] = arr;
```

这里 `[first, second]` 是 `ArrayPattern`。

### `RestElement`

表示剩余参数或剩余解构。

```js
function fn(...args) {}
const [first, ...rest] = arr;
```

这里的 `...args`、`...rest` 是 `RestElement`。

### `AssignmentPattern`

表示带默认值的模式。

```js
function fn(a = 1) {}
```

这里 `a = 1` 是 `AssignmentPattern`。

### `SpreadElement`

表示展开元素。

```js
foo(...args);
const arr2 = [...arr];
```

这里的 `...args`、`...arr` 是 `SpreadElement`。

注意：

- `RestElement` 常用于“接收剩余值”
- `SpreadElement` 常用于“展开已有值”

---

## 6. 怎么理解这些节点

可以把 AST 想成一棵语法树：

```text
Program
└─ VariableDeclaration
   └─ VariableDeclarator
      ├─ Identifier
      └─ CallExpression
         ├─ Identifier
         └─ StringLiteral
```

对应源码：

```js
const x = foo("hi");
```

大致关系是：

- `Program`：整个文件
- `VariableDeclaration`：`const x = foo("hi");`
- `VariableDeclarator`：`x = foo("hi")`
- `Identifier`：`x`
- `CallExpression`：`foo("hi")`
- `Identifier`：`foo`
- `StringLiteral`：`"hi"`

可以这样记：

- `Identifier` 是“名字”
- `Literal` 类节点是“值”
- `Expression` 类节点是“表达式，会产生值”
- `Statement` 类节点是“语句，表示执行动作”
- `Declaration` 类节点是“声明，表示定义变量、函数、类、模块关系”
- `Pattern` 类节点是“模式，表示解构或参数接收结构”

---

## 在 Babel 插件开发中的位置

这部分是 Babel 插件开发的基础层：

```text
第一层：AST 是什么
  JS 源码 -> Parser -> AST 树

第二层：AST 节点类型
  Identifier
  CallExpression
  VariableDeclaration
  FunctionDeclaration
  StringLiteral
  IfStatement
  ...

第三层：节点之间的父子关系
  Program
   └─ VariableDeclaration
       └─ VariableDeclarator
           ├─ Identifier
           └─ CallExpression

第四层：Babel 遍历机制
  visitor
  path
  enter / exit

第五层：作用域分析
  scope
  binding
  referencePaths
  constantViolations

第六层：AST 修改
  replaceWith
  remove
  insertBefore
  types 创建节点
```

一句话总结：

> 这部分是在学 JavaScript 代码被解析成 AST 后，每个语法结构对应什么节点类型。

## 复用边界

这是语法节点对照，不是混淆还原流程。常量字符串还原仍看已有 Babel procedure，不从本篇推出可运行插件。
