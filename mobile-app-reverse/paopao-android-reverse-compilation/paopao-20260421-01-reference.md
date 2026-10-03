---
schema_version: 2
id: unidbg-arm64-syscall-gap-reference
document_type: reference
original_date: '2026-04-21'
archived_date: '2026-07-13'
scope:
  targets:
    - unidbg
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260421-01.md#心态切换你不是在补环境你是在帮-unidbg-打补丁"
    basis: source-report
  - id: s2
    ref: "./paopao-20260421-01.md#第三步查-syscall-表"
    basis: source-report
  - id: s3
    ref: "./paopao-20260421-01.md#类型二部分实现--参数空间没覆盖全"
    basis: source-report
  - id: s4
    ref: "./paopao-20260421-01.md#一个特殊提醒vdso-和-vsyscall"
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s4]
    basis: source-report
    limits: 介入顺序和 99% 都是作者经验。没有 Unidbg 版本，也没有本次运行。
  - name: parameters
    anchor: parameters
    sources: [s2, s3]
    basis: source-report
    limits: 编号、寄存器和结构大小只核对该篇正文，未对照内核头文件或真机。
relations:
  - type: derived_from
    target: "./paopao-20260421-01.md#心态切换你不是在补环境你是在帮-unidbg-打补丁"
tags:
  - unidbg
  - syscall
  - source-report
---

# Unidbg 系统调用缺口：何时介入，以及两套编号

这张卡只回答两件事：Unidbg 里什么时候该碰系统调用，以及该篇写下的 ARM32/ARM64 编号和几个返回语义。不收录 getrusage 或 clock_gettime 的实现，也不把作者“报错消失”当成验收。

<a id="decision-flow"></a>
## 何时介入

来源把系统调用层和 JNI、文件层分开：后两者不补就会失败，系统调用是 Unidbg 自己有 handler 但覆盖不全。三条介入规则是：

> 如果 Unidbg 默认行为已经够用，碰都不要碰系统调用层

> syscall NR=xxx not implemented

> 99% 的情况下选库函数层 hook

正文把 `intno == 2` 当成 SVC。其它 intno 不是这条线。走 vDSO 的 `clock_gettime` 被写成：

> 根本不会触发 SVC 中断

因此来源说补这个时钟不要指望 SyscallHandler 的 case。作者把 getrusage 示例的结果写成下面这句，同时否定“不崩即正确”：

> 报错消失，结果出来了。  ** 但别急着庆祝  ** —— 用 Frida 在真机上跑同样的输入，看签名是否一致。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 默认够用就不改系统调用层 | s1，该篇心态段 | source-report | unidbg | 无版本 |
| C2 | 未实现报错才是工单 | s1，该篇心态段 | source-report | unidbg | 不是所有缺口都打印这句 |
| C3 | 优先库函数层，除非改上游 | s1，类型一对照 | source-report | unidbg | 99% 未测量 |
| C4 | intno==2 才是 syscall | s1，定位第一步 | source-report | 该篇描述的 handler | 未对后端复现 |
| C13 | vDSO 路径不进 SVC | s4，vDSO 段 | source-report | 该篇点名的时钟调用 | 未验证映射 |
| C14 | 不崩之后仍要对照真机签名 | s1，getrusage 结尾 | source-report | 作者的 getrusage 例子 | 无本次运行 |

<a id="parameters"></a>
## 编号与返回语义

ARM64 传参被写成：

> ARM64  |  ` x8  ` |  ` x0  ` ~  ` x5  ` |  ` x0  `

NR 在 x8，参数在 x0 到 x5，返回值在 x0。ARM32 的 NR 在 r7。来源禁止混用两套表：

> 绝对不能复用 ARM32 的查表结果

该篇表格里的两行是：

> getrusage  |  77  |  165

> clock_gettime  |  263  |  113

getrusage 的结构大小写成：

> ARM64 上 144 字节（注意 ARM32 上是 72 字节，因为 long 不同）

clock_gettime 的覆盖写成：

> Unidbg 通常实现了  ` 0  ` 和  ` 1  `

语义偏差的例子是 stat 的 inode、固定的 getcpu，以及 uname 的占位 release。来源对前两个的原句是：

> 最终签名和真机不一样，因为 inode 输入不对

> 通常硬编码返回  ` cpu=0, node=0  `

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | ARM32 与 ARM64 编号不能混用 | s2，查表段 | source-report | 该篇列出的 syscall | 未对照 unistd.h |
| C6 | getrusage：ARM32 77，ARM64 165 | s2，编号表 | source-report | 该篇表格 | 未对照头文件 |
| C7 | clock_gettime：ARM32 263，ARM64 113 | s2，编号表 | source-report | 该篇表格 | 未对照头文件 |
| C8 | ARM64 的 NR 在 x8，参数在 x0-x5 | s2，寄存器表 | source-report | 该篇寄存器表 | 未单步 |
| C9 | rusage：ARM64 144 字节，ARM32 72 字节 | s2，getrusage 步骤 | source-report | 该篇给出的大小 | 未核对布局 |
| C10 | clock id 通常只实现 0 和 1 | s3，类型二 | source-report | 作者说的“通常” | 无版本 |
| C11 | stat 成功但 inode 不同会改变签名 | s3，类型三 | source-report | 来源假设 SO 使用 inode | 无具体 SO |
| C12 | getcpu 通常返回 cpu=0、node=0 | s3，类型三 | source-report | 作者说的“通常” | 无版本 |

## 验证与限制

没有 Unidbg 版本，也没有本地运行。作者的成功句保持 source-report。类型三只能靠对照发现，本卡不把 Frida 草稿当成已执行的校验。第六到第十篇的通道表只是导航，不在这里展开。
