---
schema_version: 2
id: web-translate-google-cn-tk-20190513
document_type: reference
original_date: '2019-05-13'
archived_date: '2026-10-02'
scope:
  targets:
    - translate.google.cn
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./yuanrenxue-web-20190513-01.md#爬虫技巧逆向破解js代码加密代码混淆不是难事"
    basis: source-report
  - id: s2
    ref: "./yuanrenxue-web-20190513-01.md#第一步观察网页加载了哪些js文件猜猜哪个文件可能包含tk生成的代码"
    basis: source-report
  - id: s3
    ref: "./yuanrenxue-web-20190513-01.md#第三步调试javascript探寻关键代码"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 路径来自 2019-05-13 的 Networks 记录。URL 在正文里折行。未重放。
  - name: parameters
    anchor: parameters
    sources: [s1, s3]
    basis: source-report
    limits: 只保留参数每次变化和作者对返回形态的描述。样例值不收录。函数体在截图里，不在正文。
  - name: decision-flow
    anchor: decision-flow
    sources: [s2, s3]
    basis: source-report
    limits: 文件名是作者按名字猜测。行号、压缩函数名和暂停点都是当时截图，来源写明可能不同。没有失败后的下一条路径。
relations:
  - type: derived_from
    target: "./yuanrenxue-web-20190513-01.md#第三步调试javascript探寻关键代码"
tags:
  - translate.google.cn
  - source-report
---

# 2019 年 translate.google.cn 上 translate_a/single 的 tk 被说到哪一步

这张卡只回答：2019-05-13 那篇记录把翻译 ajax 写在哪条路径，tk 被说成什么，以及作者用哪一种断点去找生成函数。它不提供公式，也不收录样例值。

<a id="interfaces"></a>
## 当时的翻译路径

Networks 里看到的路径以这一行为准。后面两行是折行，查询样例不抄。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 路径原文以 https://translate.google.cn/translate_a/single?client=webapp&sl=auto&tl=zh- 开头 | s1，开篇 | source-report | 该次 Networks 记录 | 未重放。样例值不收录 |

<a id="parameters"></a>
## tk 被说成什么

参数名在同一段写成 tk。这里不抄等号后面的样例。作者没有写出输入、常量和运算。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C2 | 原文是这个参数的值每次请求既然还不一样 | s1，开篇 | source-report | 该次页面 | 没有输入依赖 |
| C3 | 作者对生成结果的原文是形如“a.b”的一串数字 | s3，调试一节 | source-report | 作者当时跳到的那个函数 | 函数体只在截图中 |

扩展节把 `String.fromCharCode()` 和 eval 写成难读写法。那不是 tk 的公式，不收进参数表。

<a id="decision-flow"></a>
## 作者怎么找到那段函数

面板布局本身不单列。下面只保留和这次寻找直接相关的三句，以及作者自己的不稳定声明。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 文件名原文是我猜是“translate_m_zh-CN.js” | s2，第一步 | source-report | 作者当时的猜测 | 来源写明凭名字感觉 |
| C5 | 断点原文是问号后面的参数就不用填了 | s3，调试一节 | source-report | XHR/fetch Breakpoints | 没有失败出口 |
| C6 | 暂停点原文含 this.xa.send(a) | s3，调试一节 | source-report | 作者当时的调用栈 | 不是稳定符号 |
| C7 | 作者声明行数和变量名称有可能和你看到的不一样 | s3，调试一节 | source-report | 该次截图 | 行号和压缩名不进入稳定参数 |

## 验证与限制

- 记录是作者的 source-report。本卡没有打开那个页面，也没有执行断点。
- 正文没有 Python 实现。不把「会 Python 就能实现」写成已有公式。
- Charles 和 Selenium 各有一句，没有步骤、产物或验收，不建流程。
- 文末课程推广和外链没有技术结论。
