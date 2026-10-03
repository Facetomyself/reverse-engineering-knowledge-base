---
schema_version: 2
id: paopao-20260414-unidbg-svc-dispatch-reference
document_type: reference
original_date: '2026-04-14'
archived_date: '2026-07-13'
scope:
  targets: [unidbg-svc-dispatch]
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260414-01.md#unidbg学习笔记四一条-svc-指令引发的连锁反应"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 立即数、寄存器和桩地址是来源用来说明机制的例子，不是某一 SO 的实测现场。
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 类名和分发伪代码按来源的简化写法收录。未对照当前仓库。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 五类来客和栈底读法是来源的排错解释。没有前提、验收和失败出口，因此不是 procedure。
relations:
  - type: derived_from
    target: "./paopao-20260414-01.md#unidbg学习笔记四一条-svc-指令引发的连锁反应"
tags: [unidbg, svc, source-report]
---

# Unidbg 的 SVC 分发

这张卡只保留来源对“一条 SVC 如何同时承载 JNI、系统调用、虚拟模块、Hook 和系统属性”的说法，以及报错栈底为什么总落在 SyscallHandler。它不提供 Hook 实现，也不把伪代码当成仓库原文。

<a id="parameters"></a>
## SVC 与调用号

来源把 ARM64 的 `svc #0` 写成四个字节，并给出机器码 `0x010000D4`。它写 Linux 上立即数通常无意义，系统调用号走寄存器。ARM64 一行把调用号放在 `x8`，参数放在 `x0` 到 `x5`，返回值放在 `x0`。

JNI 桩不靠不同的立即数区分函数。来源写每段桩的 PC 就是函数 ID。FindClass 示例把桩放在 `0xfffe0030`，表项偏移写成 `0x30`，这两处都标明是例子。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 机器码示例 | 0x010000D4 | s1 :46 | source-report | 只对应来源所写的 svc #0 |
| C2 | 调用号不在立即数 | 系统调用号是通过寄存器传递的 | s1 :79 | source-report | 未对真机追踪 |
| C3 | ARM64 调用号寄存器 | x8 | s1 :84 | source-report | 同一行还写参数 x0–x5、返回 x0 |
| C4 | 用 PC 而不是立即数 | SVC 指令所在的内存地址本身作为唯一标识 | s1 :160 | source-report | 地址空间是来源的设计描述 |

<a id="interfaces"></a>
## 一个入口上的查表

来源写 SO 跳到桩上的 `svc #0` 后，Unicorn 或 Dynarmic 把特权指令交给中断回调。回调用当前 PC 查 `svcMemory`；命中则走已注册的 `Svc.handle`，并把返回值写回 `x0`。未命中才读 `x8` 做 Linux 系统调用。

它点名的注册位置是 `DalvikVM64.java` 与 `DalvikVM.java` 里的 `svcMemory.registerSvc`，系统调用分发在 `ARM32SyscallHandler.java` 与 `Arm64SyscallHandler.java`。HookZz 路径被写成把函数入口改成 SVC 桩。SystemPropertyHook 被写成必须在 `loadLibrary` 之前注册，因为 PLT 在加载时就定下桩地址。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C5 | 查表键 | 用 PC 地址查 svcMemory 中注册的 handler | s1 :256 | source-report | 伪代码，不是逐行源码 |
| C6 | 地址映射类型 | Map<Address, Svc> | s1 :187 | source-report | 示例 PC 为 0xfffe0030 |
| C7 | JNI 注册文件 | DalvikVM64.java | s1 :332 | source-report | 未打开该文件 |
| C8 | 特权指令陷入 | Unicorn/Dynarmic 的指令模拟器识别出这是一条特权指令 | s1 :237 | source-report | 未单步 Backend |
| C9 | 属性 Hook 的时序 | SystemPropertyHook 必须在 | s1 :386 | source-report | 后文才写 loadLibrary；未复现漏注册 |

<a id="decision-flow"></a>
## 五类来客与栈底

来源把走这道门的路径收成五类：JNI 函数表、Linux 系统调用、虚拟模块导出、HookZz/Whale 回调、SystemPropertyHook。总结句写成 JNI、syscall、虚拟模块、Hook、SystemProperty。

排错含义是：JNI 报错和 syscall 报错都从 SVC 中断抛出，栈底常见 `ARM64SyscallHandler.hook`；要看的是紧挨 hook 的上一帧，而不是把栈底当成另一类故障。Frida 被写成够不到 SVC 指令本身。Dynarmic 不支持普通指令 Hook 和 Trace，但来源写 SVC 陷入仍是各 Backend 共有的，所以 JNI 和系统调用仍然走得通。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C10 | 五类汇合 | JNI、syscall、虚拟模块、Hook、SystemProperty | s1 :457 | source-report | 未逐类对源码 |
| C11 | 栈底位置 | ARM64SyscallHandler.hook | s1 :406 | source-report | 示例栈，不是本次异常 |
| C12 | JNI 与 syscall 同类出口 | 所有 JNI 报错的栈底，都是 SyscallHandler | s1 :406 | source-report | 句子在该行被截断，后文才写完 |
| C13 | Frida 边界 | 但它没法 Hook | s1 :415 | source-report | 下一行才写 SVC 指令本身 |
| C14 | Dynarmic 仍处理 SVC | 为什么 Dynarmic 不支持指令级 Hook，但仍然支持 SVC 中断？ | s1 :429 | source-report | 这是来源的设问，后文给了特权指令理由 |
| C15 | Trace 仍限于 Unicorn | 否 (仅 Unicorn/Unicorn2) | s1 :443 | source-report | 该行的能力名是 Trace |

## 验证与限制

中断分发和 FindClass 的 Java handler 都被来源标成简化。桩地址和表偏移是例子。本卡不覆盖真机内核的异常向量，也不把 Softard 笔记里的 JNI 实参寄存器说明并进这条 SVC 分发。
