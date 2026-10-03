---
schema_version: 2
id: unidbg-dynarmic-breakpoint-loop
document_type: reference
original_date: '2025-12-18'
archived_date: '2026-10-02'
scope:
  targets:
    - unidbg
    - DynarmicFactory
  client: unidbg
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./xfq-20251218-01.md#无限debugger原因一
    basis: source-report
modules:
  - name: interfaces
    anchor: call-chain
    sources: [s1]
    basis: source-report
    limits: 符号和调用顺序来自作者整理的链。本轮没有打开 unidbg 源码核对。
  - name: parameters
    anchor: svc-number
    sources: [s1]
    basis: source-report
    limits: exception=8 与 svcNumber=0 是作者写在链上的值。unidbg 版本没有写。
  - name: decision-flow
    anchor: loop
    sources: [s1]
    basis: source-report
    limits: 「按 c 继续」是作者对调试器行为的描述。没有给出换后端的类名。
  - name: validation
    anchor: boundaries
    sources: [s1]
    basis: source-report
    limits: 「测试均无这问题」没有列出后端名单，也没有第二次样本。本轮未运行。
relations:
  - type: derived_from
    target: ./xfq-20251218-01.md#无限debugger原因一
tags:
  - unidbg
  - dynarmic
  - source-report
---

# DynarmicFactory 断点回调缺失时的无限调试器

这张卡回答：unidbg 用 `DynarmicFactory` 且 `emulator.attach().addBreakPoint` 时，为什么会停在调试器里出不来，以及作者把它和 Unicorn2 差在哪。它不提供换后端的补丁。来源是 [无限debugger原因一](./xfq-20251218-01.md#无限debugger原因一)。

<a id="call-chain"></a>
## 断点进来之后走到哪

复现写法是 `emulator.attach().addBreakPoint`。作者给出的链是：Dynarmic 引擎触发 `EXCEPTION_BREAKPOINT`，进入 `DynarmicBackend.handleExceptionRaised(pc, exception=8)`，再 `interruptHookNotifier.notifyCallSVC(this, EXCP_BKPT, 0)`，然后 `AbstractARMDebugger.brk(pc, svcNumber=0)`。找不到 `BreakPointCallback` 时直接 `debug()`，进入调试器循环。段首有一处拼写 `dunarmic`，后面的类名仍写 Dynarmic。

<a id="svc-number"></a>
## svcNumber 为什么对不上

链上写 `svcNumber=0 (被写死的)`。核心句是 `DynarmicBackend.handleExceptionRaised()` 传递的 `svcNumber` 永远是 0，而不是 `bkpt` 指令里的立即数。作者把 Dynarmic 的断点实现称为半成品：只能触发断点进调试器，不支持断点回调。

<a id="loop"></a>
## 为什么按继续还会再停

Dynarmic 这条路径是：断点触发，找不到回调，进入调试器；按 `c` 继续时 PC 没变，于是再次触发断点。作者的处理是改用其他后端。其他后端的工厂类名没有写出来。

Unicorn2 被写成对照：触发时解析 `bkpt` 编号，交给回调；回调返回 true 就跳过调试器。

<a id="boundaries"></a>
## 验证与限制

样本只写了酷安 v9.6.3 的 `x-app-token`。作者写「其他样本目前没有这个问题」，以及换其他后端后「测试均无这问题」。这两句都是 source-report，没有后端名单，也没有第二份日志。unidbg 版本未知。泡泡以安笔记里的 Dynarmic 速度比较没有这个回调链，不能当成同一结论。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 问题出在 `DynarmicFactory`，hook 方式是 `emulator.attach().addBreakPoint`。 | s1 第 37–37 行 | source-report | 作者点名的这次复现 | 其他样本被说成没有 |
| C2 | 样本是 `酷安v9.6.3的x-app-token`。 | s1 第 38 行 | source-report | 这一条 token 路径 | 没有 apk 或 unidbg 版本 |
| C3 | 异常进入 `DynarmicBackend.handleExceptionRaised(pc, exception=8)`，随后 `notifyCallSVC(this, EXCP_BKPT, 0)`。 | s1 第 45、47 行 | source-report | 作者画出的调用链 | 未对源码 |
| C4 | `brk` 收到的 `svcNumber=0`，找不到 `BreakPointCallback` 就 `debug()`。 | s1 第 49–49 行 | source-report | 该链的落点 | 回调匹配规则没有展开 |
| C5 | `svcNumber` 永远是 0，不是 `bkpt` 指令中的立即数。 | s1 第 53 行 | source-report | DynarmicBackend 这条路径 | 立即数的编码没有举例 |
| C6 | 按 `c` 继续时 `PC 没变`，所以再次触发断点。 | s1 第 56 行 | source-report | 作者描述的 Dynarmic 循环 | 没有寄存器日志 |
| C7 | Unicorn2 会解析 `bkpt` 编号；回调返回 true 则跳过调试器。 | s1 第 55、57 行 | source-report | 作者写的对照 | 未运行 Unicorn2 |
| C8 | 解决办法是 `使用其他后端，测试均无这问题`。 | s1 第 39 行 | source-report | 作者说测过的其他后端 | 后端名字不在正文 |
