---
schema_version: 2
id: babel-core-objects-reference
document_type: reference
original_date: unknown
archived_date: "2026-10-08"
scope:
  targets: [babel]
  client: node
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./babel-core-objects.md#source-body
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只整理来源列出的对象分工和 API 名。未安装这些包，未验证当前主版本的导出。
relations:
  - type: derived_from
    target: ./babel-core-objects.md#source-body
  - type: supplements
    target: ./babel-ast-node-types-reference.md#interfaces
  - type: supplements
    target: ./benru-web-reverse-compilation/benru-web-20260316-01-procedure.md#prerequisites
tags: [babel, path, scope, binding]
---

# Babel 的 path、node、scope、binding、types

这张卡只回答：写 visitor 时这五个对象各管什么。节点类型表不在这里。常量字符串还原的四步顺序是另一张 procedure，本卡不改它的验收。

<a id="interfaces"></a>
## 五个对象

来源给出的管道是 `@babel/parser` → AST → `@babel/traverse` → `@babel/types` → `@babel/generator`。反混淆用途只是来源列举的能力，没有本轮输入输出。

| 对象 | 来源的分工 | 来源点名的入口 |
|---|---|---|
| `path` | 节点在树中的位置和操作，不是节点本体 | `node`、`parent`、`parentPath`、`scope`、`key`、`listKey`；`get`、`isXxx`、`replaceWith`、`replaceWithMultiple`、`remove`、`insertBefore`、`insertAfter`、`findParent`、`skip`、`stop` |
| `node` | 节点数据 | `type`，以及按节点而变的 `name`、`value`、`left`、`right`、`body`、`params` |
| `scope` | 变量环境 | `hasBinding`、`hasOwnBinding`、`getBinding`、`getOwnBinding`、`generateUidIdentifier`、`push`、`rename`、`crawl` |
| `binding` | 一个名字的绑定档案 | `identifier`、`path`、`scope`、`referencePaths`、`constantViolations`、`constant` |
| `types` | 创建和判断节点，来源常写成 `t` | `identifier`、`stringLiteral`、`numericLiteral`、`booleanLiteral`、`nullLiteral`、`callExpression`、`memberExpression`、`variableDeclaration`、`variableDeclarator`、`expressionStatement`、`blockStatement`；判断用 `t.isXxx` |

来源把读取放在 `path.node`，把替换、删除、插入放在 `path` 的方法上。`scope.hasBinding` 走作用域链，`hasOwnBinding` 只看当前层。`binding.constant` 表示来源所谓的常量语义是否还在，`constantViolations` 是破坏它的位置。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | parser、traverse、types、generator 被来源排成解析、遍历、改节点、再生成 | s1 开篇流程 | source-report | 来源描述的用法 | 未核对包导出 |
| C2 | path 操作位置，node 是数据，types 造节点，scope/binding 管名字 | s1 五对象各节 | source-report | 笔记中的 API 名 | 不是插件教程的运行结果 |

## 验证与限制

没有请求参数或风控模块。节点类分组见 [节点类型参考](./babel-ast-node-types-reference.md#interfaces)。已有的 [常量字符串还原](./benru-web-reverse-compilation/benru-web-20260316-01-procedure.md#prerequisites) 只覆盖它自己的四步，不由本卡扩大。
