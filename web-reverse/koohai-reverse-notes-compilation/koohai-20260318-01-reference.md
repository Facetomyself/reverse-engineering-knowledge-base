---
schema_version: 2
id: web-ruishu-rs-while-codegen
document_type: reference
original_date: '2026-03-18'
archived_date: '2026-10-02'
scope:
  targets:
    - ruishu
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./koohai-20260318-01.md#rs-while的构造器"
    basis: source-report
  - id: s2
    ref: "./koohai-20260318-01.md#1-局部生成测试"
    basis: source-report
  - id: s3
    ref: "./koohai-20260318-01.md#这段代码是-典型的rs-jsvmp-核心逻辑中的代码生成器code-generator或指令分发器-"
    basis: source-report
  - id: s4
    ref: "./koohai-20260318-01.md#一-核心原理解析"
    basis: source-report
  - id: s5
    ref: "./koohai-20260318-01.md#二-分析这段代码的三个用法"
    basis: source-report
  - id: s6
    ref: "./koohai-20260318-01.md#三-实战改造生成-vmp-的-while-循环代码"
    basis: source-report
  - id: s7
    ref: "./koohai-20260318-01.md#2-当前网站-vmp双层嵌套--动态组装引擎"
    basis: source-report
  - id: s8
    ref: "./koohai-20260318-01.md#3-为什么rs会有明文的-while1-字符串"
    basis: source-report
  - id: s9
    ref: "./koohai-20260318-01.md#4-这个vmp变简单了吗"
    basis: source-report
  - id: s10
    ref: "./koohai-20260318-01.md#3-eval-动态执行"
    basis: source-report
  - id: s11
    ref: "./koohai-20260318-01.md#运行结果揭秘"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s3, s4, s6]
    basis: source-report
    limits: 教学用 BYTECODE 和文末 mini interpreter 都不是 rs 内层指令集。操作码数组只保留作者写的长度和 case 22 的拼接形状，不转录整表。本次未运行 generate 或 eval。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s6, s7, s8, s9, s11]
    basis: source-report
    limits: 索引 30 到 case 22 是作者按标志位为假手算的路径。来源没有页面、代数或样本哈希。不替代已有 ruishu request-chain 与 validation。
  - name: risk-control
    anchor: risk-control
    sources: [s5, s10]
    basis: source-report
    limits: typeof document 分支是作者后加的教学升级，不是粘贴的 _$$0 case。计数器或反调试是作者对索引入口 53 的解读，本次未看到它触发。
relations:
  - type: derived_from
    target: "./koohai-20260318-01.md#rs-while的构造器"
tags:
  - ruishu
  - source-report
---

# rs while 代码生成器：组装机和静态引擎怎么分开

这张卡只回答：这篇笔记里的 rs while 是怎样被认出来的，粘贴的 `_$$0` 怎样用操作码数组拼出 `while(1)` 取指壳，以及它和写死在源码里的解释器有什么差别。它不覆盖瑞数请求链或验收口径。那两块已有 `../products/ruishu-rs6-challenge.md` 和 `../products/ruishu-rs6-hybrid.md`。本篇没有代数、域名或样本哈希，不能补进那两张卡。

`kb_catalog.py query` 里 target `ruishu` 的 parameters、decision-flow、risk-control、interfaces 均为 0。request-chain 与 validation 各有上述两张卡。target `jsvmp` 的 parameters、decision-flow 为 0，但本篇目标按正文里的「瑞数」记为 ruishu，不另建 jsvmp 目标。

作者称这是粗浅还原。文中的「完美输出: 30」和文末注释里的结果 10 都保持 source-report。本次没有运行。

<a id="parameters"></a>
## 生成器的程序计数器、输出缓冲和取指壳

来源先声明：前面的 `generate` 是在生成 while 字符串，不是 while 的 vmp，while 的 vmp 见文末。教学字节码用入口 27 只拼出一条取指，入口 0 拼出完整自执行函数。后文才贴出 `_$$0`。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 边界原文是这是生成while 循环的代码，不是while 的vmp | s1，rs-while的构造器 | source-report | 文中第一个 generate 演示 | 不能把教学 opcode 1/2/0 当成 rs 内层指令 |
| C2 | 入口 27 的注释输出原文含 op=code[pc++] | s2，局部生成测试 | source-report | 该教学生成器 | 未运行 generate |
| C3 | 定性原文含代码生成器（Code Generator），同句还有或“指令分发器”。运行句原文含 new Function，并以将其运行收束 | s3，粘贴函数后的定性 | source-report | 这篇粘贴的 _$$0 | 没有调用点的动态栈。eval 与 new Function 之间不是连续原文 |
| C4 | 操作码数组的长度原文是数组的长度是 62。 | s4，核心原理解析 | source-report | 作者给这串数字的计数 | 本卡不转录这 62 个数 |
| C5 | 程序计数器原文是充当了程序计数器（PC） | s4，核心原理解析 | source-report | _$$0 的入参 _$eO 到 _$hD | 名字和后文之间有标点，未跟踪真实调用的起点分布 |
| C6 | 输出任务原文是向数组里塞 JS 代码片段。case 22 的翻译原文是 while(1){ op = code[pc++]; | s4 与 s6 | source-report | _$eI.push 与 case 22 | 两句不在同一段。随机名的具体键没有样本 |

C6 的两句原文要分开核对：入参说明里有大量 `_$eI.push("var ", ...)`；翻译句的原文是 while(1){ op = code[pc++];

<a id="decision-flow"></a>
## 字节码 while 的三个锚点和双层组装

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | 出口锚点原文含 JUMP_IF_FALSE 和锚点① 有出口跳转 | s1，识别特征 | source-report | 作者给原字节码 while 的识别特征 | 没有配一份真实字节码地址 |
| C8 | 回跳锚点原文是无条件回跳，且目标 < 当前地址 | s1，识别特征 | source-report | 同上 | 同上 |
| C9 | 第三个锚点原文是 exit 就是 JUMP_IF_FALSE 的目标 | s1，识别特征 | source-report | 同上 | 同上 |
| C10 | 从索引 30 走到 case 22 的收束原文是 Case 22: 生成 while 循环。换入口的原文是改变了调用的索引起点，就能生成不同结构的代码 | s6，实战改造；运行结果揭秘 | source-report | 作者手算的这一条入口，以及他对入口的总说明 | 跳转依赖标志位为假。文中复述加了步数上限，本次未跑。不是一份入口表 |
| C11 | 分层原文是用来制造虚拟机的机器，以及第一层：组装机（Builder） | s7，双层嵌套 | source-report | 作者对当前这段 rs 的分层 | 第二层引擎的指令表不在这篇 |
| C12 | 作者解释搜不到引擎壳的原文是在瑞数的混淆脚本里，以及真正的执行代码根本就不在 AST 树里 | s9，变简单了吗 | source-report | 作者所说的瑞数混淆脚本 | 没有给出检索过的脚本文件 |
| C13 | 字符串拆开的原因原文含瑞数通过这种方式，让你在静态代码里搜不到 while(1) | s8，明文 while | source-report | 作者对 while 字符串来源的解释 | 示例 out.push 是说明，不是抓到的运行时字符串 |

改变调用索引就能换结构，原文是改变了调用的索引起点，就能生成不同结构的代码。这只说明入口不同，输出不同，不是一份入口表。

<a id="risk-control"></a>
## 作者追加的 document 检测和他对计数器的读法

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C14 | 教学升级里的检测原文含 typeof document !== 'undefined' | s10，eval 一节之后的升级代码 | source-report | 作者后加的 opcode 3 分支 | 不是粘贴的 _$$0。演示里的全局对象不收录 |
| C15 | 索引入口 53 的作用原文是计数器/反调试陷阱 | s5，三个用法 | source-report | 作者对 _$$0(53, ...) 的读法 | 作者写「可能会」。本次未看到触发 |
| C16 | 另外两个入口原文是 _$_4 = _$$0(0, _$al); 和 _$$0(6, _$co, _$f9); | s5，三个用法 | source-report | 作者列出的三处调用写法 | 调用点本身没有在粘贴函数外再出现上下文 |

## 验证与限制

条件跳转的形状，作者写成 `!_$_1 ? _$hD += 14 : 0;`。偏移随 case 变化，14 只是例子。

文末 mini interpreter 把 `while (i < 5)` 收成 push、比较和 `JUMP_IF_FALSE`。作者接着写 rs内层的风格也和这个不一样。因此那套 OP 表不能当成 rs 内层参数。注释里的结果 10 未运行。

已有瑞数卡的 request-chain、validation 这篇没有新的请求顺序或验收条件，所以不补充那两张卡。没有失败出口和针对真实页面的验收，不建流程。
