---
schema_version: 2
id: paopao-20260330-frida-stalker-api
document_type: reference
original_date: '2026-03-30'
archived_date: '2026-10-02'
scope:
  targets: [frida-stalker]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260330-01.md#12-底层原理"
    basis: source-report
  - id: s2
    ref: "./paopao-20260330-01.md#21-stalkerfollowthreadid-options"
    basis: source-report
  - id: s3
    ref: "./paopao-20260330-01.md#25-stalkerexcluderange"
    basis: source-report
  - id: s4
    ref: "./paopao-20260330-01.md#四transform-回调--stalker-的核心能力"
    basis: source-report
  - id: s5
    ref: "./paopao-20260330-01.md#52-精确选择事件类型"
    basis: source-report
  - id: s6
    ref: "./paopao-20260330-01.md#81-性能开销"
    basis: source-report
  - id: s7
    ref: "./paopao-20260330-01.md#十总结"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s2, s6]
    basis: source-report
    limits: 事件开关和三个默认值按作者教程记录，没有对某个 Frida 版本核对。
  - name: interfaces
    anchor: interfaces
    sources: [s1, s3]
    basis: source-report
    limits: 只记录不改原始代码、exclude 和 call probe 的作者描述。不补具体 so。
  - name: decision-flow
    anchor: decision-flow
    sources: [s2, s4, s5, s7]
    basis: source-report
    limits: 先定位再跟踪、避开主线程和 exclusive 序列，是作者的使用边界。没有设备上的卡顿或崩溃记录。
  - name: validation
    anchor: validation
    sources: [s6]
    basis: source-report
    limits: 减速倍数表写的是大致范围。本次没有计时。
relations:
  - type: derived_from
    target: "./paopao-20260330-01.md#二核心-api-详解"
tags: [frida, stalker, source-report]
---

# Frida Stalker 的事件、队列和插桩边界

这张卡回答作者如何区分 Stalker 与函数级 Hook、事件和队列有哪些默认开关、以及什么时候不该把回调插进指令流。第七节的占位签名和检测函数里的寄存器改写不在本卡。依据停在 `source-report`。近邻查询在 `frida-stalker` 上没有已声明模块。

<a id="parameters"></a>
## 事件与默认队列

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | follow 的事件包括「捕获 CALL 指令」，以及 ret、exec、block、compile；exec 被写成数据量极大。 | s2，第 133–137 行 | source-report | 作者示例里的 events 对象 | 没有在指定版本上实际收到事件。 |
| C2 | onReceive 与 onCallSummary「只能选择其中一个」，空回调仍会生成事件。 | s2，第 152、163 行 | source-report | 作者的互斥提示 | 没有做只留一个回调的对照。 |
| C3 | queueCapacity 的注释是默认「16384」，queueDrainInterval 的注释是「默认值 250ms」，trustThreshold 默认 1；-1 被写成每次重新编译。 | s2，第 287–297 行 | source-report | 作者写出的默认值 | 未核对当前 Frida 的实际默认。 |

<a id="interfaces"></a>
## 引擎在改什么

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | copy-on-exec 被写成「它不修改原始代码」，已编译的基本块会缓存。 | s1，第 84–84 行 | source-report | 作者对 Stalker 机制的描述 | 后文同时说更激进的检测仍可能看执行路径。 |
| C5 | exclude 被写成「性能优化最重要的手段」，并点名要排除 frida-agent，避免跟踪自身。 | s3，第 211、223 行 | source-report | 作者列出的系统库和 agent | 模块名随 ABI 变化，列表不是全集。 |
| C6 | iterator.memoryAccess 为 open，被写成当前位置可以插入代码、不在 exclusive 序列中。 | s4，第 517 行 | source-report | 作者的 iterator 表 | 没有对 ARM exclusive 指令做实验。 |

<a id="decision-flow"></a>
## 先收窄再下钻

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | 「不要随意跟踪主线程」，否则作者认为可能卡死。跟踪放在目标函数的进入和离开之间。 | s2 所在章的坑点，第 447–447 行 | source-report | 作者的线程建议 | ANR 没有复现。 |
| C8 | 「在 exclusive 序列中插入 putCallout 会导致崩溃」。 | s4，第 605 行 | source-report | 作者描述的 ARM exclusive 序列 | 没有崩溃样本。 |
| C9 | compile「只在基本块首次编译时触发」，被用来做覆盖率；完整调用链用 call 加 ret。总结要求「先粗后细」，不要一开始开 exec。 | s5 与 s7，第 691、1815 行 | source-report | 作者的事件选择 | drcov 导出没有用真实模块加载过。 |

<a id="validation"></a>
## 作者给出的开销范围

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C10 | 仅 block 或 compile 被写成大约「2-5x」，call 加 ret 大约 5-10x，putCallout 大约 10-50x。follow「不会自动跟踪该线程创建的子线程」。 | s6，第 1562–1564、1593 行 | source-report | 作者的大致表 | 表头已写明是大致减速倍数，不是测量。 |

第六节里改比较结果的示例，以及第七节 `com.example` 的签名还原，都是占位叙述，不进入上表。
