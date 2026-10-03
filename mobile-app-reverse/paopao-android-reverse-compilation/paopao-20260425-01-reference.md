---
schema_version: 2
id: unidbg-jni-init-boundary-reference
document_type: reference
original_date: '2026-04-25'
archived_date: '2026-07-13'
scope:
  targets:
    - unidbg
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260425-01.md#别和-jni_onload-混为一谈"
    basis: source-report
  - id: s2
    ref: "./paopao-20260425-01.md#loadlibrary-第二个参数到底控制什么"
    basis: source-report
  - id: s3
    ref: "./paopao-20260425-01.md#四步定位法"
    basis: source-report
  - id: s4
    ref: "./paopao-20260425-01.md#找到-init-之后它在做什么"
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s3, s4]
    basis: source-report
    limits: 四步法和三类症状是作者流程。代码名被作者标成占位，本轮没有 Frida 或 Unidbg 运行。
  - name: parameters
    anchor: parameters
    sources: [s1, s2]
    basis: source-report
    limits: 只保留 callJNI_OnLoad、forceCallInit 和 newObject(null) 的正文边界。BaseVM.java:314 未打开核对。
relations:
  - type: derived_from
    target: "./paopao-20260425-01.md#loadlibrary-第二个参数到底控制什么"
tags:
  - unidbg
  - jni-init
  - source-report
---

# Unidbg 初始化边界：JNI_OnLoad 和 Java 主动 init

这张卡只回答：无报错但返回空时，Unidbg 有哪几件不会自动发生，以及来源如何用症状区分 init。不收录四步法的占位脚本，也不把“应该和 Frida 一致”写成验收。类继承链的完整步骤不在本篇。

<a id="decision-flow"></a>
## 什么算初始化问题

表面症状是：

> 函数能调出来，没报错，但返回值是  ` null  `

原因被写成 Unidbg 不跑 Java：

> Unidbg 不执行 DEX，所以  ** 这一串由 Java 主动调的 native 函数永远不会自动发生  **

JNI_OnLoad 也不能按真机习惯理解：

> JNI_OnLoad  ** 不会自动执行  **

它跑完也只是装载通知，不是业务 init。来源要求判断对错之前先有标准答案：

> 永远先在 Frida 里验证，再在 Unidbg 里复现

第二步的分叉是：

> 如果这次返回结果和第一步一致

一致就回去查 JNI、文件和系统调用；不一致才逐个试导出函数。作者把 init 分成三类。安全门卫型是：

> 后续函数静默返回 null 或假数据

数据准备型是：

> 业务结果"对而不对"

名字不能当线索：

> 初始化函数  ** 不叫 init  **

构造器或 JNI_OnLoad 若拉起常驻线程：

> Unidbg 单线程模型直接卡死

四步法仍无结果时，来源让人看栈顶有没有：

> NoClassDefFoundError

那是类表还没摆好的岔路。本篇只点了这个信号，并说 libmetasec_ml.so 的三层 resolveClass 在另一篇。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 无报错且返回 null 是入口症状 | s3，篇首症状 | source-report | 该篇定义 | 不是具体 SO |
| C2 | Java 主动 native 不会自动发生 | s1，原因段 | source-report | Unidbg 不执行 DEX | 未对源码版本 |
| C3 | JNI_OnLoad 不自动执行 | s1，与 OnLoad 的区分 | source-report | Unidbg | 未运行 |
| C7 | 立刻调用若与完整环境一致，就不是 init 依赖 | s3，第二步 | source-report | 有 Frida 标准答案时 | 本轮没有标准答案 |
| C9 | 安全门卫型会静默返回 null 或假数据 | s4，分类表 | source-report | 作者的三类 | 无样本计数 |
| C10 | 数据准备型表现为结果像对但不对 | s4，分类说明 | source-report | 作者的三类 | 无输出样本 |
| C11 | 函数名不一定是 init | s4，命名陷阱 | source-report | 作者见过的名字 | 不是封闭集合 |
| C12 | 常驻线程会卡死单线程模型 | s2，何时关构造器 | source-report | .init_array 或 OnLoad | 未复现挂起点 |
| C13 | 先有 Frida 结果再复现 | s3，经验 | source-report | 该篇流程 | 未执行 |
| C14 | 四步法失败后可看 NoClassDefFoundError | s3，类表变体 | source-report | 该篇点名的岔路 | 类链步骤不在本篇 |

<a id="parameters"></a>
## 三个不会自动发生的 API

显式入口的拼写是：

> 方法名  ** 带下划线  **

`loadLibrary` 的第二个布尔值不是这个入口。正文写：

> 它控制的不是 JNI_OnLoad，是 ELF 的

作者把行号写成 BaseVM.java:314，控制 `.init_array` / `DT_INIT`。并且：

> 无论  ` forceCallInit  ` 传什么，这一行都是必要的

业务对象也不能靠构造器偷跑初始化。调用写成：

> newObject(null)

同行注释说这只造空壳，不走构造器。Frida 的 `$new` 会跑静态块和构造器里的 native。有 `GetObjectClass` 或 `CallObjectMethod` 时，空壳不够。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 方法名是 callJNI_OnLoad，带下划线 | s1，OnLoad 段 | source-report | 该篇点名的 API | 未调用 |
| C5 | forceCallInit 控制 ELF init，不控制 JNI_OnLoad | s2，第二个参数 | source-report | 作者给出的 BaseVM.java:314 | 行号未核对 |
| C6 | 无论该布尔值如何，都要显式 callJNI_OnLoad | s2，两件事分清 | source-report | Unidbg | 未运行 |
| C8 | newObject(null) 不走构造器 | s3，第四步注释 | source-report | Dalvik 类壳 | 未运行 |

## 验证与限制

四步法开头就写 callViaJava、callTarget、decodeArgs 是占位，所以不能当成流程。录制回放还依赖真机能挂上 hook、参数能序列化、初始化没有网络或真机文件副作用；这三句只是边界，没有输入输出合同。个人故事里的 `com.xxx.Sec` 不是可定位样本。
