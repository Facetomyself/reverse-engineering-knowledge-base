---
schema_version: 2
id: packed-state-flattening-reference
document_type: reference
original_date: '2025-10-17'
archived_date: '2026-10-02'
scope:
  targets:
    - packed-state-flattening
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./anti-crawler-web-20251017-01.md#第二篇ast-语法树硬刚某宝第二弹babel修复格式一"
    basis: source-report
  - id: s2
    ref: "./anti-crawler-web-20251017-01.md#第三篇ast-语法树硬刚某宝第二弹babel修复格式二"
    basis: source-report
  - id: s3
    ref: "./anti-crawler-web-20251017-01.md#第四篇ast-语法树硬刚某宝第三弹babel修复格式三"
    basis: source-report
  - id: s4
    ref: "./anti-crawler-web-20251017-01.md#第五篇ast-语法树硬刚某宝第四弹多层三元表达式拆解"
    basis: source-report
  - id: s5
    ref: "./anti-crawler-web-20251017-01.md#第六篇ast-语法树硬刚某宝提取控制器"
    basis: source-report
  - id: s6
    ref: "./anti-crawler-web-20251017-01.md#第七篇ast-语法树硬刚某宝无用分支破解思路"
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s2, s3, s4, s5, s6]
    basis: source-report
    limits: 语句修复、24 位状态字和无用分支都只来自粘贴文本。控制器提取停在 getparam。无用分支靠变量名筛选，不是不变式求解。225、231、223 是作者标签。不收录模仿样本里的探测串。
relations:
  - type: derived_from
    target: "./anti-crawler-web-20251017-01.md#第六篇ast-语法树硬刚某宝提取控制器"
tags:
  - control-flow-flattening
  - babel
  - source-report
---
# 语句规范化、打包状态字和无用分支

这张卡只保留三件来源写清楚的事：反混淆前怎样把语句补成块并拆开逗号表达式，for 循环里的状态字怎样拆成三个字节，以及不剪无用分支时控制器为什么会空转。ESTree 十类节点是通识，不收成模块。MTOP 的 sign 和 cookie 前提在另一张卡，这里不补。

<a id="decision-flow"></a>
## 先规范化，再看状态机

来源把格式修复放在反混淆前面。if 的非块分支改成块，但 else if 不再包一层。for 的空循环体改成空块。return 后面的逗号表达式拆成若干语句，只返回最后一项。多变量声明和逗号赋值也拆开。作者贴出的一个结果把 for 初始化里的声明挪到循环外面。

> 在真正进行ast语法树解混淆之前，我们都会先对其进行格式修复

> !types.isBlockStatement(node.consequent)

> 将 return a, b, c 拆分为 a; b; return c

> for (; i < j;

嵌套三元按层改成 if。分支里的逗号表达式再拆成语句。赋值右侧那种三元，粘贴代码写了省略；变量声明和 return 上的处理函数只出现在遍历表里。

> 此处省略具体逻辑

> 如果当前节点还是三元表达式，继续拆解

### 打包状态字

第六篇的样本被写成模仿，不是原脚本。控制转移看一个整数：低 8 位、再移 8 位后的低 8 位、再移一次后的低 8 位，分别送进分支。提取时先确认 for 体是变量声明后接 switch，再把这段运算包成 getparam。执行顺序明确留到后面，本篇没有。

> var d = 255 & l

> for后var + switch的代码形式

> 后续我们接着讲解，获取控制器后如何进行代码执行逻辑的破解

### 无用分支

来源把一类赋值写成结果与初值无关，所以总是给状态字同一个常数。不先剪掉，用控制器模拟执行顺序时会空转。筛选办法是按那批变量名找 if。来源又写，较早时这些分支总走同一侧，后来 if 和 else 都可能走到。没有给出证明不变式的步骤。

> 这段代码的结果同样固定，和所有变量初始值无关

> 会陷入死循环中

> 现在分支可能走if 也可能走else

### 结论

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | `在真正进行ast语法树解混淆之前，我们都会先对其进行格式修复`。来源要求先做格式修复，再进入反混淆。 | ./anti-crawler-web-20251017-01.md:505 | source-report | decision-flow | 没有定义修复失败就停止的出口。 |
| C2 | `!types.isBlockStatement(node.consequent)`。if 的 consequent 不是块时，来源用块包起来。 | ./anti-crawler-web-20251017-01.md:519 | source-report | decision-flow | 只读到粘贴的 visitor。 |
| C3 | `!types.isIfStatement(node.alternate)`。else if 不再包一层块，其他非块 alternate 才包裹。 | ./anti-crawler-web-20251017-01.md:519 | source-report | decision-flow | 空 else 被注释掉，没有启用。 |
| C4 | `loopBody === null`。for 的空循环体被写成空块。 | ./anti-crawler-web-20251017-01.md:572 | source-report | decision-flow | 内层 if 是否补括号不在这个 visitor 里。 |
| C5 | `将 return a, b, c 拆分为 a; b; return c`。return 后的逗号表达式被拆成前面的语句加上最后一个返回值。 | ./anti-crawler-web-20251017-01.md:614 | source-report | decision-flow | 父节点不是块、Program 或 switch case 时只写了警告。 |
| C6 | `对多变量声明`。多个声明符的变量语句要拆成多次单变量声明。 | ./anti-crawler-web-20251017-01.md:680 | source-report | decision-flow | for 初始化的搬移只见于作者贴出的结果。 |
| C7 | `对逗号表达式赋值`。逗号表达式赋值要拆成多条语句。 | ./anti-crawler-web-20251017-01.md:681 | source-report | decision-flow | 未运行。 |
| C8 | `for (; i < j;`。来源贴出的结果把 for 初始化里的多变量声明移到循环外。 | ./anti-crawler-web-20251017-01.md:745 | source-report | decision-flow | 只是作者给出的打印文本。 |
| C9 | `此处省略具体逻辑`。赋值右侧的三元分支在粘贴代码里写明省略。 | ./anti-crawler-web-20251017-01.md:812 | source-report | decision-flow | 因此这不是完整变换。 |
| C10 | `如果当前节点还是三元表达式，继续拆解`。嵌套三元按层改写成 if。 | ./anti-crawler-web-20251017-01.md:822 | source-report | decision-flow | 变量声明和 return 的处理函数只被点名。 |
| C11 | `types.isSequenceExpression(node)`。三元分支里的逗号表达式被拆成独立语句。 | ./anti-crawler-web-20251017-01.md:822 | source-report | decision-flow | 与前面的 return 逗号修复不是同一个 visitor。 |
| C12 | `var d = 255 & l`。状态字的低 8 位被写成 d = 255 & l。 | ./anti-crawler-web-20251017-01.md:869 | source-report | decision-flow | 样本被作者声明为模仿，不是原脚本摘录。 |
| C13 | `var L = 255 & c`。再右移两次后的低 8 位被写成 L。 | ./anti-crawler-web-20251017-01.md:869 | source-report | decision-flow | 中间字节 x 在同一行，本卡不展开模仿样本。 |
| C14 | `for后var + switch的代码形式`。控制器提取先判断 for 体是若干变量声明后接 switch。 | ./anti-crawler-web-20251017-01.md:878 | source-report | decision-flow | 判断式在粘贴代码里没有闭合展示。 |
| C15 | `后续我们接着讲解，获取控制器后如何进行代码执行逻辑的破解`。这篇停在抽出 getparam，执行顺序留到后文。 | ./anti-crawler-web-20251017-01.md:900 | source-report | decision-flow | 后文的无用分支也没有把顺序还原补完。 |
| C16 | `这段代码的结果同样固定，和所有变量初始值无关`。无用分支被写成结果与变量初值无关。 | ./anti-crawler-web-20251017-01.md:922 | source-report | decision-flow | 只给了例子，没有不变式算法。 |
| C17 | `会陷入死循环中`。不剪掉无用分支时，来源称控制器模拟会空转。 | ./anti-crawler-web-20251017-01.md:923 | source-report | decision-flow | 没有复现该循环。 |
| C18 | `只要依照变量名称筛选出所有有关这些变量的if语句就可以找到所有无用分支了`。来源用变量名筛选相关 if，当作无用分支。 | ./anti-crawler-web-20251017-01.md:924 | source-report | decision-flow | 这是作者的猜测加全局查看，不是判定程序。 |
| C19 | `现在分支可能走if 也可能走else`。来源称较早版本无用分支总走同一侧，后来 if 或 else 都可能。 | ./anti-crawler-web-20251017-01.md:926 | source-report | decision-flow | 223 与后来都是作者的版本标签。 |

## 验证与限制

前提、步骤、输出、验收、失败出口不能从这一篇同时定位：控制器的走查没有写出，赋值三元被省略，未知父节点只是一句警告。因此不建流程。

taobao 的 parameters 命中是 MTOP cookie 前提，不是这个状态机。不把本篇补进那张卡。没有运行 Babel。
