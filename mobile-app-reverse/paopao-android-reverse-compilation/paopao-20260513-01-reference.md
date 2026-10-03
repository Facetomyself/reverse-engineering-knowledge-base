---
schema_version: 2
id: paopao-20260513-frida-hook-triage-reference
document_type: reference
original_date: '2026-05-13'
archived_date: '2026-07-13'
scope:
  targets: [frida]
  client: android
  version: frida-trace -j and -i; Java overload descriptors
  observed_at: unknown
sources:
  - id: s1
    ref: ./paopao-20260513-01.md#四hook-排错系统化流程
    basis: source-report
  - id: s2
    ref: ./paopao-20260513-01.md#65-unable-to-find-method方法找不到
    basis: source-report
  - id: s3
    ref: ./paopao-20260513-01.md#三frida-trace快速侦察的利器
    basis: source-report
modules:
  - name: decision-flow
    anchor: triage-order
    sources: [s1]
    basis: source-report
    limits: 五步缩小范围、子进程 child gating、重载和 JIT 都是来源的诊断顺序。没有对某个包跑通，空脚本崩溃只被解释成检测，不是检测已定位。
  - name: parameters
    anchor: overload-and-backtrace
    sources: [s2]
    basis: source-report
    limits: JVM 数组描述符和两种 Backtracer 的速度精度对照只按来源表抄录。信号编号没有附崩溃日志。
  - name: interfaces
    anchor: trace-and-log
    sources: [s3]
    basis: source-report
    limits: console.log、send 和 frida-trace 的模式串是通道说明。没有 Python on_message 的实测报文。
relations:
  - type: derived_from
    target: ./paopao-20260513-01.md#四hook-排错系统化流程
tags: [frida, hook-triage, frida-trace, android, source-report]
---

# Frida Hook 不触发时的诊断顺序

这张卡检索 Hook 没有输出时先查连接、加载、设置、触发还是进程，以及 overload 类型串和 frida-trace 模式怎么写。来源是 [调用栈、日志与 Hook 排错](./paopao-20260513-01.md#四hook-排错系统化流程)。`target=frida` 下没有同模块卡片。`unknown` 的 decision-flow 不包含这条诊断链。第 8 节是检查清单，没有单独的验收和失败出口，所以不是 procedure。依据保持 source-report。

<a id="triage-order"></a>
## 诊断顺序

来源把范围收成：Frida 连接，脚本加载，Hook 设置，方法触发，然后才看输出。不要跳步。连接以注入后能打出固定短句为准，否则回到环境篇。只看到脚本开头的日志、看不到 `Java.perform` 内的日志，问题在进入 Java 之前。设置阶段用 try 把 `Java.use` 失败和运行时不触发分开。

`frida -U -f` 只进入主进程。子进程里的方法不会命中；已运行的子进程用 `-n` 附加。来源写加固壳若在子进程里早解密，需要父 session `enable_child_gating()`，在 `child-added` 里再挂脚本然后 resume。Hook 已装上却不触发时，表内还有：操作路径不对、混淆名、重载挂错、`Java.deoptimizeEverything()` 关 JIT、以及只在启动跑一次所以要 spawn。同一个 Java 方法同时只能有一个 `implementation`，后写的覆盖先写的。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 诊断按连接、加载、设置、触发、输出，不跳步 | `Frida 连接 → 脚本加载 → Hook 设置 → 方法触发 →` | s1 paopao-20260513-01.md:1230 | source-report | 下一行才写到输出正常 |
| C2 | spawn 注入只覆盖主进程 | `Frida 只注入主进程` | s1 paopao-20260513-01.md:497 | source-report | 包名是示例 |
| C12 | 不触发时要考虑挂错了重载 | `方法有多个重载，Hook 了错误的版本` | s1 paopao-20260513-01.md:819 | source-report | 表内还有混淆、时机和死代码 |
| C3 | JIT 绕过时来源给出 deoptimizeEverything | `Java.deoptimizeEverything()` | s1 paopao-20260513-01.md:820 | source-report | 没有 JIT 前后对照 |
| C4 | 后设置的 implementation 覆盖先设置的 | `后设置的 Hook 会覆盖先设置的。` | s1 paopao-20260513-01.md:1121 | source-report | 未讨论 Native attach 叠加 |

<a id="overload-and-backtrace"></a>
## 类型串与调用栈

`Unable to find method` 时先枚举 `overloads` 的 `argumentTypes.className`。对象用全限定名；`byte[]` 写成 `"[B"`，`String[]` 写成 `"[Ljava.lang.String;"`。一维数组前缀是 `[`，二维 `int[][]` 是 `"[[I"`。对象数组末尾有分号。

Java 栈来源优先 `Log.getStackTraceString(Throwable.$new())`，要过滤帧再用 `Thread.currentThread().getStackTrace()`。Native 栈默认 `Backtracer.ACCURATE`，慢、依赖展开元数据；取不到帧再用 `FUZZY`。JNI 边界之下要另打 Java 栈。崩溃日志里 SIGSEGV、SIGABRT、SIGTRAP 被分别解释成非法访问、主动退出和可能的反调试断点，这是读日志的对照，不是已捕获的 tombstone。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C9 | 数组 overload 使用 JVM 描述符 | `数组类型的 JVM 编码规则` | s2 paopao-20260513-01.md:1027 | source-report | 基本类型字母拆在后续行 |
| C7 | ACCURATE 慢但依赖栈展开元数据，作为默认 | `依赖栈展开元数据` | s2 paopao-20260513-01.md:624 | source-report | 表内精度未复测 |
| C8 | FUZZY 在 ACCURATE 取不到帧时再用 | `ACCURATE 取不到栈帧时退而求其次` | s2 paopao-20260513-01.md:625 | source-report | 启发式扫描的误帧未知 |
| C10 | SIGTRAP 被来源标成可能的反调试断点 | `signal 5 (SIGTRAP)` | s2 paopao-20260513-01.md:945 | source-report | 同句还有 SIGSEGV 与 SIGABRT，无日志 |

<a id="trace-and-log"></a>
## 日志与 frida-trace

`console.log` 走异步 IPC，脚本不等待终端画出该行。高频 Hook 会堵通道。结构化或带二进制附件用 `send`。`-j` 的格式是 `类名模式!方法名模式`，`*` 为通配。`-i`/`-x` 按函数名包含或排除，`-I`/`-X` 按模块名；`-I` 是包含整个模块，不是排除。来源把 trace 放在写脚本之前，用来确认方法是否被调用。需要改返回值、复杂过滤或 RPC 时，表内写明不适合 trace。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C5 | console.log 的显示是异步的 | `这个过程是  ** 异步的  **` | s3 paopao-20260513-01.md:67 | source-report | 未测量 IPC 延迟 |
| C6 | -j 用类名感叹号方法名 | `` ` -j  ` 参数的格式是  ` 类名模式!方法名模式  ` `` | s3 paopao-20260513-01.md:314 | source-report | -i 的包含排除在后文 |
| C11 | 先 trace 再写针对性脚本 | `先用  ` frida-trace  ` 快速扫描` | s3 paopao-20260513-01.md:380 | source-report | 10 秒对比是来源的说法 |

## 验证与限制

速查清单把 Thumb 函数地址加一列在 32 位 SO 一行里，本卡不把它做成模块；未导出函数和 Thumb 的展开在后来的定位卡。文件日志路径、采样和限速是日志策略，没有验收口径。作者的「Frida OK」只是连接探针的预期字符串。依据保持 source-report。
