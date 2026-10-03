---
schema_version: 2
id: grok-web-babel-ast-literal-rewrite
document_type: reference
original_date: "2026-03-15"
archived_date: "2026-07-16"
scope:
  targets: [babel-ast]
  client: node
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./benru-web-20260315-01.md#四第一个ast脚本把数字123变成456"
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只记录来源写下的 parse、traverse、generate 顺序，以及数字替换、常量折叠和改名条件的文本。未安装依赖，未运行 node。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 预期输出是来源印出的文本。没有失败时的分支，不能当成 procedure 的验收。
relations:
  - type: derived_from
    target: "./benru-web-20260315-01.md#四第一个ast脚本把数字123变成456"
tags: [babel, ast, numeric-literal]
---

# Babel 字面量改写的入门文本

这张卡只回答一个检索问题：这篇入门稿用哪四个包把 JS 解析成 AST，它怎样改数字字面量和二元常量，以及它印出的结果和改名条件在文本上是否一致。范围是这一篇。字符串混淆留在下一篇，不在这里展开。作者称运行后 123 都会变成 456，保持为来源陈述；本轮没有执行。

<a id="decision-flow"></a>
## 解析、访问与两处替换

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源把 AST 写成浏览器执行前的结构化数据，混淆只改外观。quote: 浏览器在执行之前，会先把代码解析成一种结构化的数据 | s1 ./benru-web-20260315-01.md:49 | source-report | 第一节 | 没有证明任意混淆都保持同一棵树 |
| C2 | 安装命令同时装 parser、traverse、generator 和 types。quote: npm install @babel/parser @babel/traverse @babel/generator @babel/types | s1 ./benru-web-20260315-01.md:91 | source-report | 第三节 | 没有版本号 |
| C3 | 脚本用 require 取 parser，traverse 和 generator 取 `.default`。quote: const parser = require('@babel/parser'); | s1 ./benru-web-20260315-01.md:108 | source-report | demo.js | 未对应当前包的导出形态 |
| C4 | 数字替换只在 NumericLiteral 的 value 等于 123 时把该字段写成 456。quote: path.node.value === 123 | s1 ./benru-web-20260315-01.md:127 | source-report | 第四节 visitor | 不替换字符串里的 123 |
| C5 | 常量折叠的文字规则是：BinaryExpression 左右都是数字时计算，再用数字节点替换整段表达式。quote: 如果左右两边都是数字，就计算结果，然后用数字节点替换整个表达式 | s1 ./benru-web-20260315-01.md:178 | source-report | 第五节 | 运算符只写了加减乘除 |
| C6 | 折叠的替换调用是 path.replaceWith(t.numericLiteral(result))。quote: path.replaceWith(t.numericLiteral(result)) | s1 ./benru-web-20260315-01.md:194 | source-report | 常量折叠片段 | 片段没有展示 parser.parse |
| C7 | 改名散文要求小心关键字和函数名，代码条件却是名为 a 且不是 referenced identifier。被引用的 a 按这段文本不会改名。quote: !path.isReferencedIdentifier() | s1 ./benru-web-20260315-01.md:207 | static-review | 改名片段 | 未运行，不能说运行时会怎样 |

<a id="validation"></a>
## 来源印出的结果

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 来源让读者执行 node demo.js。quote: node demo.js | s1 ./benru-web-20260315-01.md:144 | source-report | 第四节 | 没有失败命令 |
| C9 | 来源写所有 123 都变成 456，并印出 `let c = 456 + 456;`。quote: 所有123都变成了456 | s1 ./benru-web-20260315-01.md:158 | source-report | 来源贴出的输出 | 本轮未复跑 |
| C10 | 折叠一节写 `let c = 123 + 456;` 会变成 `let c = 579;`。quote: let c = 579 | s1 ./benru-web-20260315-01.md:199 | source-report | 常量折叠 | 与 C9 的未折叠输出不是同一次运行 |
| C11 | 来源把 AST Explorer 当成对照节点的在线工具，并给出 https://astexplorer.net/ 。quote: AST Explorer | s1 ./benru-web-20260315-01.md:217 | source-report | 第六节 | 不是目标接口，本轮未打开 |

## 验证与限制

本轮只读文本。C7 是代码形态和上一句散文不一致，不是运行结论。来源没有写 parse 失败、包版本不符或输出不符时停在哪里，所以不能建成 procedure。近邻查询里 `babel-ast`、`@babel/parser` 和 `ast` 的 decision-flow 都没有已有卡片。目标为 unknown 的 decision-flow 命中是 Frida 选择、原生函数定位、加固产品、补环境对象、材料台账和产品索引，都不是这次字面量改写。字符串还原在同目录下一篇，不并进本卡。
