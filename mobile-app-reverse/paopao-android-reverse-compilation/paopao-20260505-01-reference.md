---
schema_version: 2
id: frida-agent-injection-architecture-reference
document_type: reference
original_date: '2026-05-05'
archived_date: '2026-10-02'
scope:
  targets: [frida-agent-injection-architecture]
  client: Android
  version: source discusses 12.x pause default and 16.x engine default; exact install pin unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./paopao-20260505-01.md#frida学习笔记一frida-入门--原理与架构-1
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 字段名、补丁宽度、引擎默认值和版本口径都来自这篇教程，未对照 Frida 源码或真机。
  - name: decision-flow
    anchor: spawn-attach
    sources: [s1]
    basis: source-report
    limits: Spawn 与 Attach 的先后只按来源的生命周期名单。没有对具体 App 验证注入点。
  - name: risk-control
    anchor: detection-traces
    sources: [s1]
    basis: source-report
    limits: TracerPid 与 maps 痕迹是来源对检测面的描述，不是绕过步骤，也没有样本扫描结果。
  - name: validation
    anchor: boundaries
    sources: [s1]
    basis: source-report
    limits: 方法级粒度、调用频率和旧版暂停旗标都是来源界限。本轮未测量卡顿或握手失败。
relations:
  - type: derived_from
    target: ./paopao-20260505-01.md#frida学习笔记一frida-入门--原理与架构-1
tags: [frida, artmethod, inline-hook, spawn, source-report]
---

# Frida 注入架构：ArtMethod、补丁宽度与 Spawn 时点

这份参考卡回答：来源把 Frida 的 Java Hook、Native Inline Hook、版本对齐和 Spawn/Attach 时点分别落在什么机制上。它不提供某款 App 的绕过脚本，也不替代按困境选择 API 的那张技巧卡，更不是环境安装流程。来源是 [Frida 原理归档](./paopao-20260505-01.md#frida学习笔记一frida-入门--原理与架构-1)。

<a id="parameters"></a>
## 机制参数

Java 层来源点名 ART 的 `ArtMethod` 字段 `entry_point_from_quick_compiled_code_`。赋值 `implementation` 时，来源写 Gum 会保存原指针，`把它替换为 Frida trampoline 的地址`。因此 `Java Hook 是  ** 方法级别  ** 的`。

Native 层来源区分补丁宽度：ARM32 路径是 `整个 patch 共 8 字节`，ARM64 路径是 `整个 patch 共 16 字节`，序列写成 `LDR X16, [PC,  #8  ]; BR X16`。Thumb 函数地址的最低位被写成 `最低位只是 Thumb 标记`。

引擎方面，来源写 `近年（16.x 起）默认引擎换成了` QuickJS，并用 `Script.runtime` 在 QuickJS、Duktape、V8 之间切换。版本方面，协议 `最低要求是 major.minor 版本对齐`，同时 `工程稳妥做法是完全对齐`。

<a id="spawn-attach"></a>
## Spawn 与 Attach

来源建议 `默认使用 Spawn 模式`，因为注入发生在进程创建之后、App 的 Java 代码之前，从而盖住 `attachBaseContext`、`ContentProvider.onCreate`、静态初始化块和 `JNI_OnLoad`。Attach 被留在三种情况：目标不在初始化阶段、Spawn 会先撞上检测、以及主进程之外的子进程。`Child.gating` 只被点名，没有在本篇展开。

旧版行为单独记住：`旧版 Frida (≤ 12.x)` 的 `-f` `需要加  ` --no-pause  ``；来源写 16.x 起默认不再暂停。这是版本文档界限，不是本轮命令实验结果。

<a id="detection-traces"></a>
## 检测面

ptrace 期间 `/proc/self/status` 的 `TracerPid` 会短暂变成 frida-server 的 PID，detach 后归零。来源同时写：`frida-agent.so` 的 `内存段是无法消除的痕迹`，扫描 maps 的检测抓的是这个。大量 Native Inline Hook 时，Gum 会用 `SIGSTOP` / `SIGCONT` 停住其他线程，来源认为短时间钩几百个函数可能把停顿累加到可感知。这里只记录痕迹和代价，不记录如何抹掉它们。

<a id="boundaries"></a>
## 验证与限制

来源给出的感知界限是 `Hook 调用频率低于每秒 100 次的方法通常没有明显感知`。它同时写明 `不能 Hook 方法内部的某一行`，并把那种需求指到 smali 或 dex 修改；Native 函数可以 `Interceptor.attach` 到函数内部地址。没有 root 时来源只点名 Gadget 这条替代，安装步骤不在本篇。VMP 被写成标准 Java Hook 可能失效，因为方法体不再是原来的字节码。

`Java.use` 被要求在脚本顶部做一次并复用。示例里的登录参数打印不进入本卡。技巧菜单（构造捕获、`$new`、Stalker 范围）已有单独参考卡，目标是 `unknown`，不在这里重写。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | Java Hook 改的是 `entry_point_from_quick_compiled_code_`，并 `把它替换为 Frida trampoline 的地址`。 | s1 第 183、233 行 | source-report | 来源描述的 ART Quick 入口 | 未对照 ART 版本里的字段布局 |
| C2 | `Java Hook 是  ** 方法级别  ** 的`。调用频率界限是 `Hook 调用频率低于每秒 100 次的方法通常没有明显感知`。 | s1 第 239、244 行 | source-report | 来源的经验法则 | 没有帧率或耗时样本 |
| C3 | ARM32 `整个 patch 共 8 字节`，ARM64 `整个 patch 共 16 字节`。奇数地址 `最低位只是 Thumb 标记`。 | s1 第 317、318、325 行 | source-report | 来源描述的 Gum 补丁 | 未在 IDA 里核对被钩函数 |
| C4 | 协议 `最低要求是 major.minor 版本对齐`，同时 `工程稳妥做法是完全对齐`。16.x 起默认引擎换成 QuickJS，用 `Script.runtime` 切换。 | s1 第 136、137、151、169 行 | source-report | 来源给出的 Frida 版本口径 | 未做握手实验 |
| C5 | `默认使用 Spawn 模式`。12.x 的 `-f` `需要加  ` --no-pause  ``。 | s1 第 359、389 行 | source-report | 来源的模式选择 | 未对具体包名验证早期回调 |
| C6 | agent 映射是 `内存段是无法消除的痕迹`。 | s1 第 128 行 | source-report | 来源描述的 maps 检测面 | 没有地图样本，也不提供清除步骤 |
