---
schema_version: 2
id: grok-paopao-20260629-stalker-reference
document_type: reference
original_date: "2026-06-29"
archived_date: "2026-10-02"
scope:
  targets: [frida-stalker]
  client: android
  version: "16.x"
  observed_at: "2026-06-29"
sources:
  - id: s1
    ref: "./paopao-20260629-01.md#二核心-api-详解"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录来源写下的事件字段、队列默认值和信任阈值。示例基于来源所称 Frida 16.x，17 的模块 API 差异来源只点了一句，未逐项核对。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 选择顺序和互斥回调是来源的使用建议。未在本机跟线程。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 减速倍数和 drcov 记录布局是来源文本。不把来源自称的真机次数当成本次运行结果。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只记录来源对 Stalker 自身暴露面的描述。不收录按端口比较改寄存器的示例。
relations:
  - type: derived_from
    target: "./paopao-20260629-01.md#二核心-api-详解"
tags: [frida-stalker, android]
---

# Frida Stalker 的事件字段、追踪范围和失效条件

这张卡只回答一个检索问题：来源把 Stalker 的哪些事件、默认值和线程生命周期写成可复用参数，以及它如何在 Interceptor、事件类型和排除范围之间选择。范围是这篇归档的文本。第七章的包名、偏移和异或密钥来源自己标成占位，不进入卡片。作者称在某音乐应用上命中过调用统计，保持为来源陈述。

<a id="parameters"></a>
## 事件字段与默认配置

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | annotate 模式下 call 事件来源写成四元组：类型、location、target、depth。quote: ["call", location, target, depth] | s1 ./paopao-20260629-01.md:300 | source-report | frida-stalker | 未解析真实 GumEvent |
| C2 | 同表把 exec 事件写成只有类型和当前 PC。quote: 当前执行指令的 PC | s1 ./paopao-20260629-01.md:302 | source-report | frida-stalker | 未开 exec 采集 |
| C3 | 来源把队列容量默认值写成 16384。quote: 16384 | s1 ./paopao-20260629-01.md:314 | source-report | Stalker.queueCapacity | 只此赋值注释 |
| C4 | 来源把自动排空间隔默认值写成 250ms。quote: 默认值 250ms | s1 ./paopao-20260629-01.md:318 | source-report | queueDrainInterval | 未改间隔对照 |
| C5 | trustThreshold 默认注释是执行 1 次后信任，不再检查基本块是否被修改。quote: 基本块执行 1 次后信任 | s1 ./paopao-20260629-01.md:322 | source-report | 无自修改代码的默认档 | 未观察重编译 |
| C6 | 来源把 -1 写成永不信任，用于自修改代码或 VMP，并写明很慢。quote: -1 = 永不信任 | s1 ./paopao-20260629-01.md:323 | source-report | trustThreshold 注释 | 未对 VMP 样本开关 |
| C7 | iterator 不调用 keep 时，来源写成丢弃当前指令。quote: 不调用则丢弃该指令 | s1 ./paopao-20260629-01.md:567 | source-report | transform | 未改指令流 |

<a id="decision-flow"></a>
## 先粗后细、回调互斥和回收顺序

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 来源建议先用 Interceptor 定位函数，再用 Stalker 看内部。quote: 先用 Interceptor 定位关键函数，再用 Stalker | s1 ./paopao-20260629-01.md:105 | source-report | 已知入口之后 | 定位方法不在本篇 |
| C9 | onReceive 与 onCallSummary 来源写成只能二选一。quote: 只能二选一 | s1 ./paopao-20260629-01.md:161 | source-report | follow 选项 | 未传双回调对照 |
| C10 | 来源把 unfollow 后立刻 garbageCollect 写成 SIGSEGV，并要求约 50ms 安全窗。quote: unfollow → 立刻 garbageCollect → SIGSEGV | s1 ./paopao-20260629-01.md:220 | source-report | attach 后的回收顺序 | 未复现崩溃 |
| C11 | 覆盖率场景来源只开 compile，并称为最小数据量。quote: 只开 compile | s1 ./paopao-20260629-01.md:761 | source-report | 基本块首次编译 | 未导出覆盖率文件 |
| C12 | 总结禁止一开始打开 exec。quote: 不要一上来就开 | s1 ./paopao-20260629-01.md:1977 | source-report | 事件选择 | 与第 8 章减速表一致，仍是来源口径 |

<a id="validation"></a>
## 来源给出的减速档和 drcov 记录

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C13 | 来源把全开 exec 写成大约 80-100 倍减速，并称为不可用挡位。quote: 80-100x | s1 ./paopao-20260629-01.md:1712 | source-report | 来源性能表 | 没有本次计时 |
| C14 | 对比表还写 exec 全开约 80-100 倍、call/ret 约 10-15 倍、稳态约 3-5 倍。quote: exec 全开 ~80-100x、call/ret ~10-15x、稳态 ~3-5x | s1 ./paopao-20260629-01.md:99 | source-report | 同一来源的另一张表 | 两表倍数不完全同一行 |
| C15 | drcov 基本块记录来源写成 uint32 起始偏移、uint16 大小、uint16 模块号。quote: uint32 start_offset, uint16 size, uint16 module_id | s1 ./paopao-20260629-01.md:1801 | source-report | Lighthouse 文件布局 | 未生成文件，未加载 IDA |

<a id="risk-control"></a>
## 来源描述的暴露面

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C16 | 来源写 Stalker 不改原始代码，因此简单的代码段哈希可能抓不到，但执行路径完整性检查仍可能抓到。quote: 虽然 Stalker 不修改原始代码 | s1 ./paopao-20260629-01.md:1725 | source-report | copy-on-exec 描述 | 未做完整性对照 |
| C17 | 来源把可执行匿名映射写成可通过进程 maps 观察的内存特征。quote: 可通过读取 ` /proc/self/maps ` 来检测 | s1 ./paopao-20260629-01.md:1727 | source-report | 来源列举的检测面 | 未读 maps |
| C18 | exclusive load/store 序列中插入 putCallout，来源写成会崩溃。quote: 在 exclusive 序列中插入 putCallout 会导致崩溃 | s1 ./paopao-20260629-01.md:677 | source-report | ARM exclusive 区间 | 未触发 |

## 验证与限制

第七章和文末工作流使用来源自己声明的虚构包名、偏移和密钥，不能当作验收。第 6.4 节的条件改写示例不进入本卡。同合集更早的 Stalker 讲义不是目录里的同目标卡片；本次查询没有 frida-stalker 的 parameters、decision-flow、validation 或 risk-control。Frida 17 只在环境节被点名为导出 API 有变，本卡不把 16.x 字段外推到 17。
