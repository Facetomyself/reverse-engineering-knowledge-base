---
schema_version: 2
id: yuanrenxue-web-20200413-python-obfuscation-ladder
document_type: reference
original_date: '2020-04-13'
archived_date: '2026-10-02'
scope:
  targets:
    - python
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./yuanrenxue-web-20200413-01.md#python-的控制流代码混淆"
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留正文已经写明的判别顺序。前后对照在图片里，本卡不把图片当成代码。未安装 Intensio-Obfuscator 或 ASTObfuscate，未运行 exec。
relations:
  - type: derived_from
    target: "./yuanrenxue-web-20200413-01.md#python-的控制流代码混淆"
tags:
  - python
  - intensio-obfuscator
  - source-report
---

# Python 混淆笔记里的三档判别

这张卡只回答：2020-04-13 这篇笔记如何区分 Intensio 的简单改名、它的复杂模式，以及 AST 改写；静态分析在哪一档仍然被作者认为走得通。它不提供混淆器或还原器。

JavaScript 的控制流平坦化卡片不覆盖 Intensio-Obfuscator、`ast.NodeTransformer` 或 ASTObfuscate。

<a id="decision-flow"></a>
## 作者写的判别顺序

简单模式只被描述成把名字变长。复杂模式被收成三步，并且作者认为把名字缩短后，多出来的 for 和 if 仍能静态跳过。AST 那一档才被写成要动态调试。字节码和 so 只被点为更难，没有步骤。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 简单混淆被写成字符串、常量和代码脉络仍能静态看清。quote: 字符串和常量都一目了然，代码结构，就靠静态分析，代码的脉络也看得还是清楚。 | s1，一般混淆 | source-report | 来源所称 Intensio 简单模式 | 对照图未读成代码。库版本未写 |
| C2 | 复杂模式被总结为拉长名字、加入无效代码，再把源码压成字符串用 exec 执行。quote: 先是把代码变量函数名弄得很长，然后是在代码里加入了无效代码，最后是把源代码压缩当成一个字符串，用 exec 来执行。 | s1，复杂模式收束 | source-report | 来源所称同一库的复杂模式 | 句子从上一行的库名接过来。没有脚本 |
| C3 | 多出来的 for 和 if，在缩短变量名之后仍被写成可以静态跳过。quote: 通过静态分析，还是较容易跳过去。 | s1，干扰代码段 | source-report | 来源图中标红的那些多余分支 | 「重名命」是原文用字。图本身不是文本 |
| C4 | 控制流混淆被放在上述方式之后，并写成通常靠 AST 修改程序。quote: 更复杂一点的混淆就是控制流混淆。 | s1，抽象语法树混淆开头 | source-report | 这篇笔记的分档 | 没有平坦化调度器或分发变量 |
| C5 | 字符串、常量和 import 也被改掉的例子，被写成要动态调试才知道在做什么。quote: 要通过动态调试才知道程序在干嘛。 | s1，AST 例子图后的一句 | source-report | 来源那张对照图所代表的例子 | 调试器、断点和样本都没有 |
| C6 | 作者把访问字符串和 Import 写成 NodeTransformer 的 visit_Str、visit_ImportFrom，并写明只能混淆、不能改变结果。quote: 实现visit_Str这个方法 | s1，自定义类那两行 | source-report | 来源点名的访问方法 | 方法体在图里，不在正文。visit_ImportFrom 在下一行 |
| C7 | ASTObfuscate 被写成会操作 AST，但没有逻辑流混淆；控制流要自己实现整棵解析树。quote: 不过对程序逻辑流的混淆没有 | s1，库名句 | source-report | 来源提到的这个第三方库 | 没有版本、仓库或调用示例 |
| C8 | 更难的一档被写成混淆字节码，或把关键代码做成 so；两者都被称为汇编指令。quote: 通过混淆字节码，或者把关键代码做成 so 文件 | s1，末段 | source-report | 作者的难度判断 | 没有字节码偏移或 so 符号 |

正文里唯一的 exec 示例是 `exec("1+1")`，结果写成 2。这只说明内置 exec 能跑字符串，不是一份混淆样本。

## 验证与限制

没有安装命令、输入样本、输出对照或失败出口，所以不建流程。图片里的改名和干扰语句本轮没有转写。作者说「程序要能正常运行」，本轮没有运行。
