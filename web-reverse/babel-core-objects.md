---
schema_version: 2
id: babel-core-objects
document_type: archive
original_date: unknown
archived_date: "2026-10-08"
scope:
  targets: [babel]
  client: node
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: null
    basis: source-report
    citation: "Babel 中的 path / node / binding / types / scope"
    reason: "原始材料未提供作者名或可公开定位的链接"

source_completeness: complete
relations: []
tags: [babel, path, scope, binding]
---

# Babel 中的 path / node / binding / types / scope

来源是一份没有作者名和公开链接的 Babel 对象笔记。它描述 path、node、scope、binding、types 的分工，不报告某次反混淆已经跑通。

## 清洗与完整性说明

无平台导航、无图、无表。API 示例按原文保留，未补版本号。

<a id="source-body"></a>
## 来源正文

## Babel 是什么

Babel 是一个 JavaScript 代码转换工具。

在 AST 反混淆中，可以使用 Babel 把 JavaScript 源码解析成 AST，遍历并修改 AST，最后重新生成新的 JavaScript 源码。

Babel 的基本处理流程：

```text
JavaScript 源码
    ↓
@babel/parser
    ↓
AST 抽象语法树
    ↓
@babel/traverse
    ↓
遍历 AST 节点
    ↓
@babel/types
    ↓
判断节点 / 创建新节点 / 替换节点
    ↓
@babel/generator
    ↓
重新生成 JavaScript 源码
```

### Babel 常用模块

- `@babel/parser`：把 JavaScript 源码解析成 AST
- `@babel/traverse`：遍历 AST，找到需要处理的节点
- `@babel/types`：判断节点类型，创建新的 AST 节点
- `@babel/generator`：把修改后的 AST 重新生成 JavaScript 源码

### Babel 在 AST 反混淆中的用途

Babel 可以用来实现：

- 字符解码
- 常量计算
- 对象合并
- 数组简化
- 成员表达式还原
- 删除无用代码
- 删除 `if` 假分支
- 花指令处理
- 控制流平坦化还原
- return 函数简化

可以把整个反混淆过程理解成：

```text
解析源码
    ↓
得到 AST
    ↓
找到混淆节点
    ↓
修改或替换节点
    ↓
重新生成可读源码
```

---

## Babel 的五个核心对象

这五个东西是写 Babel 插件时最常碰到的核心对象。

可以先记住一句话：

- `path`：当前节点的“路径对象”，负责操作 AST
- `node`：当前节点本体，AST 数据
- `scope`：当前作用域，负责变量环境
- `binding`：某个标识符在作用域里的绑定信息
- `types`：`@babel/types`，负责创建和判断节点

---

## 1. `path`

`path` 是最重要的入口。它不是节点本身，而是“节点在树中的位置 + 一组操作方法”。

### 作用

- 读取当前节点
- 获取子节点、父节点、兄弟节点
- 替换、删除、插入节点
- 查找父级节点
- 结合 `scope` 做变量分析

### 常见属性

- `path.node`：当前节点本体
- `path.parent`：父节点本体
- `path.parentPath`：父节点对应的 path
- `path.scope`：当前作用域
- `path.key`：当前节点在父节点中的键名或下标
- `path.listKey`：如果在数组里，表示数组字段名

### 常见 API

#### `path.get(key)`
获取子路径。

```js
const callee = path.get("callee");
const firstArg = path.get("arguments.0");
```

#### `path.isXxx()`
判断当前 path 对应的节点类型。

```js
path.isIdentifier();
path.isCallExpression();
path.isStringLiteral();
```

也可以带属性判断：

```js
path.isIdentifier({ name: "foo" });
path.isStringLiteral({ value: "hello" });
```

#### `path.replaceWith(node)`
用新节点替换当前节点。

```js
path.replaceWith(t.identifier("bar"));
```

#### `path.replaceWithMultiple(nodes)`
把当前位置替换成多个节点。

适合语句位置。

#### `path.remove()`
删除当前节点。

#### `path.insertBefore(node)` / `path.insertAfter(node)`
在当前节点前后插入节点。

#### `path.findParent(fn)`
向上查找父节点。

```js
const funcPath = path.findParent(p => p.isFunctionDeclaration());
```

#### `path.skip()`
跳过当前节点的子树遍历。

#### `path.stop()`
停止整个遍历。

---

## 2. `node`

`node` 是 AST 节点数据本身，也就是一个普通对象。

### 作用

- 直接读取节点字段
- 查看节点类型
- 配合 `types` 生成或修改节点

### 常见字段

不同节点字段不同，但最常见的是：

- `node.type`
- `node.name`
- `node.value`
- `node.left`
- `node.right`
- `node.body`
- `node.params`

### 例子

```js
Identifier(path) {
  console.log(path.node.type); // Identifier
  console.log(path.node.name); // 变量名
}
```

### 常见理解

- `node` 是内容
- `path` 是入口和操作器

一般：

- 读数据用 `path.node`
- 做结构操作用 `path` 的方法

---

## 3. `scope`

`scope` 是当前节点所在的作用域环境。

它负责处理：

- 这个名字能不能找到
- 这个变量在哪声明
- 有没有被重新赋值
- 会不会重名
- 是否需要生成新变量名

### 作用

- 查变量绑定
- 判断局部变量 / 外部变量
- 生成不冲突的标识符
- 安全重命名变量
- 向当前作用域添加变量

### 常见 API

#### `scope.hasBinding(name)`
查当前作用域链中是否有这个绑定。

```js
scope.hasBinding("x");
```

#### `scope.hasOwnBinding(name)`
只查当前作用域本身，不往外找。

```js
scope.hasOwnBinding("x");
```

#### `scope.getBinding(name)`
获取某个名字的 binding 对象。

```js
const binding = scope.getBinding("x");
```

#### `scope.getOwnBinding(name)`
只拿当前作用域里的 binding。

#### `scope.generateUidIdentifier(baseName)`
生成一个不容易冲突的标识符。

```js
const uid = path.scope.generateUidIdentifier("temp");
```

#### `scope.push({ id, init })`
把变量推入当前作用域。

```js
scope.push({
  id: t.identifier("temp"),
  init: t.numericLiteral(1)
});
```

#### `scope.rename(oldName, newName)`
重命名变量和它的引用。

```js
scope.rename("oldName", "newName");
```

#### `scope.crawl()`
重新扫描并收集作用域信息。

在动态修改作用域后有时会用到。

---

## 4. `binding`

`binding` 是某个标识符在作用域中的绑定信息对象。

你可以把它理解成：

> 这个名字在当前作用域里的“档案”。

### 作用

- 找到声明位置
- 找到所有引用位置
- 看是否被修改过
- 判断是否是常量语义

### 常见属性

#### `binding.identifier`
声明处的那个标识符节点。

#### `binding.path`
声明位置对应的 path。

#### `binding.scope`
这个绑定所在的作用域。

#### `binding.referencePaths`
所有引用这个变量的位置。

#### `binding.constantViolations`
所有破坏常量语义的修改位置。

#### `binding.constant`
是否仍然保持常量语义。

### 例子

```js
const binding = path.scope.getBinding("x");
if (binding) {
  console.log(binding.identifier.name);
  console.log(binding.referencePaths.length);
  console.log(binding.constant);
}
```

### 常见用途

- 判断变量是否被引用
- 判断变量是否被改写
- 做变量重命名
- 做代码分析和压缩

---

## 5. `types`

`types` 一般指 `@babel/types`，常写成 `t`。

它是用来：

- 创建节点
- 判断节点类型
- 构造 AST 结构

### 作用

- `path` 负责“操作已有节点”
- `types` 负责“造新节点”

### 常见 API

#### 创建节点

```js
t.identifier("foo")
t.stringLiteral("hello")
t.numericLiteral(1)
t.callExpression(t.identifier("foo"), [])
```

#### 判断节点类型

```js
t.isIdentifier(node)
t.isCallExpression(node)
t.isStringLiteral(node)
```

#### 常见构造函数

- `t.identifier(name)`
- `t.stringLiteral(value)`
- `t.numericLiteral(value)`
- `t.booleanLiteral(value)`
- `t.nullLiteral()`
- `t.callExpression(callee, args)`
- `t.memberExpression(object, property)`
- `t.variableDeclaration(kind, declarations)`
- `t.variableDeclarator(id, init)`
- `t.expressionStatement(expr)`
- `t.blockStatement(body)`

### 例子

```js
CallExpression(path) {
  const newNode = t.callExpression(
    t.identifier("bar"),
    path.node.arguments
  );
  path.replaceWith(newNode);
}
```

---

## 6. 它们之间的关系

可以这样理解：

```text
path
 ├─ node     当前节点数据
 ├─ scope    当前作用域
 │    └─ binding   某个名字的绑定信息
 └─ 方法     替换、删除、插入、查找

types
 └─ 创建 / 判断节点
```

再简化一点：

- `path`：操作入口
- `node`：节点内容
- `scope`：变量环境
- `binding`：变量档案
- `types`：节点工厂

---

## 7. 典型使用场景

### 改函数名

```js
CallExpression(path) {
  const callee = path.get("callee");
  if (callee.isIdentifier({ name: "foo" })) {
    callee.replaceWith(t.identifier("bar"));
  }
}
```

### 查变量是否局部声明

```js
Identifier(path) {
  const binding = path.scope.getBinding(path.node.name);
  if (binding) {
    console.log("local or reachable binding found");
  }
}
```

### 生成临时变量

```js
const uid = path.scope.generateUidIdentifier("temp");
```

### 判断变量是否被修改

```js
const binding = path.scope.getBinding("config");
if (binding && binding.constant) {
  console.log("not reassigned");
}
```

---

## 8. 一句话总结

Babel 插件里最核心的思路是：

- 用 `path` 找位置、做操作
- 用 `node` 看节点长什么样
- 用 `scope` 找变量环境
- 用 `binding` 看某个变量的完整信息
- 用 `types` 生成和判断 AST 节点

---

## 9. 学习顺序建议

如果你在整理 Babel 笔记，可以按这个顺序学：

1. AST 节点类型
2. `path` 和 `node`
3. `scope` 和 `binding`
4. `types`
5. 常见修改方法：`replaceWith`、`remove`、`insertBefore`、`insertAfter`

这样会比直接背 API 更稳。

## 复用边界

反混淆用途清单是来源的能力列举，不是本轮验收。节点类型对照在相邻归档，不在这里重复。
