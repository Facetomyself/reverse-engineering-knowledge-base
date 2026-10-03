---
schema_version: 2
id: native-analysis-qishen-vmp-trace-ir-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [qishen-android-vmp]
  client: android
  version: 40.2.0
  observed_at: unknown
sources:
  - id: s1
    ref: ./qishen-vmp-analysis-kanxue.md#register-anchors
    basis: source-report
  - id: s2
    ref: ./qishen-vmp-restore-52pojie.md#structures
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 寄存器、指令宽度和上下文偏移只对应作者描述的 Android 40.2.0 那一版。本库没有 so，不能把这张表当成其他构建的布局。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s2]
    basis: source-report
    limits: 这是作者的阅读和折叠顺序。看雪篇停在 VM 结构，吾爱篇的结构 IR 仍被作者称为模糊日志，不是可替换的程序。
  - name: validation
    anchor: validation
    sources: [s2]
    basis: source-report
    limits: 后继匹配比例、压缩倍数和 SM3 轮常量都是作者统计。本库未重放 trace，也未对当前样本做本地对照。
relations:
  - type: derived_from
    target: ./qishen-vmp-analysis-kanxue.md#register-anchors
  - type: supplements
    target: ./qishen-vmp-restore-52pojie.md#lift-and-check
tags: [qishen, VMP, ARM64, structural-ir, source-report]
---

# 七神 Android VMP：trace 锚定与结构折叠

这张卡只保留两篇来源里能定位的框架，不收录一键脱壳、过检测或算法实现。Windows VMProtect 的证据边界在 [windows-vmp-local-recovery-evidence.md](../packing-bypass/windows-vmp-local-recovery-evidence.md)。另一套从输出反查 producer 的 ARM64 trace 流程在 [vmp-trace-evidence-recovery-procedure.md](./vmp-trace-evidence-recovery-procedure.md)，目标不是这一版七神 so。

<a id="parameters"></a>
## 参数机制

作者把样本写成豌豆荚上的 Android `40.2.0`。分析篇给出的入口是 `liba.so` `0x370B64` 和 `libb.so` `0x2e01b8`。VM 指令被写成 48 字节。整数寄存器文件在 ctx+`0x6070`，32 个 8 字节槽；另外两块在 ctx+`0x6170` 和 ctx+`0x61F0`。上下文开头的魔数、IP 位于 `+0xC`，这些都只作为该帖中的字段角色。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | x23、x20、x19、x25、x24、x26、x27、x8 在 `vmOneHandler` 入口被作者固定成 IP、字节码、上下文、handler 表和三类寄存器文件。 | s1 分析篇寄存器表 | source-report | 作者描述的 40.2.0 | 未在本库的 so 上复核 |

<a id="decision-flow"></a>
## 决策流程

分析篇的顺序是：外壳调用链，初始化上下文，三个健壮检测包装三选一，进入单个 handler，再用 trace 把返回地址和 LR 对上，最后按 pass 处理专属调用和栈折叠。还原篇不再展开 handler，而是把去虚拟化日志收成直线块、条件 IP、循环回边、调用块和 VM 自身的错误返回。作者想要的下一步是 `opcode dst, src`，复合指令再拆成单步。条件跳转的拆法在还原篇里仍未定。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C2 | 还原篇收缩的是重复执行、分叉、回边和调用边，不是再反汇编一遍字节码。 | s2 五种结构 | source-report | 已有去虚拟化日志之后 | 作者写明当时产物仍像日志 |

<a id="validation"></a>
## 验证与限制

还原篇用 trace 的实际后继检查两路落点，作者计数是 129648 条里 129645 条相符。压缩计数是 566691 次 handler 执行收到 33 个函数、9183 行。SM3 的识别依赖把拆开的 32 位立即数拼回 `0x79cc4519` 和 `0x7a879d8a`，不是直接在日志里搜到完整常数。作者同时写下三条做不到的事：未执行边要换输入、调用时解密的常数不在字节码里、没有内存的提升器留着运行时地址。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C3 | 作者把后继自检和常数拼接当作这份还原能不能用的证据，并明确动态 trace 覆盖不了整台程序。 | s2 提升和自检、三堵墙 | source-report | 作者那次 trace | 本库未重放，比例和 SM3 归属都未复测 |
