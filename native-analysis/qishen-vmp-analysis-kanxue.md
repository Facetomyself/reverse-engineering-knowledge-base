---
schema_version: 2
id: native-analysis-qishen-vmp-analysis-kanxue
document_type: archive
original_date: '2026-08-31'
archived_date: '2026-10-02'
scope:
  targets: [qishen-android-vmp]
  client: android
  version: 40.2.0
  observed_at: unknown
sources:
  - id: s1
    ref: https://bbs.kanxue.com/thread-292925.htm
    basis: source-report
source_completeness: partial
tags: [qishen, VMP, ARM64, trace, handler, source-report]
---

# 七神 VMP 分析：寄存器锚定与 IR 提升

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>

看雪 [thread-292925](https://bbs.kanxue.com/thread-292925.htm)，发帖账号「一只鸭子」，文内署名「人生导师」。文内日期 2026-08-31，帖子时间 2026-09-11。本篇是框架锚点摘要。汇编、IR 片段和踩坑草稿以原帖为准。

</details>

作者声明只研究 VMP 虚拟机框架，不对其中算法做还原，也不提供一键脱壳或过检测代码。样本是作者所称豌豆荚上的 Android `40.2.0`。本库没有样本、trace 或 IDA 库，下面的地址和计数都是来源自述。

<a id="entry-chain"></a>
## 进入 VM 的外壳

作者给出的定位是 `liba.so` 的 `0x370B64` 与 `libb.so` 的 `0x2e01b8`。他用 `blr x23` 附近的函数指针形态找到跨 so 调用，并说明这个特征很脆，更稳的办法是搜字符串。

`libb.so` 上他写下的进入顺序是：`0x2e01b8` 的 OLLVM 外壳，到 `0x2E2B34` 间接调用外壳，`0x2E2BE8` 壳调用点，`0x2d3780` 初始化字节码并调用 VM，`0x2E5C2C` 按 `off_3E1E30[*(ByteCode+88)]` 在三个健壮检测包装里选一个，再进入 `0x2E7FE8` 的 `vmOneHandler`。三个包装被写成栈和指针边界检查，越界后走 trap，然后 `bl` 到 handler。

<a id="register-anchors"></a>
## 作者锚定的寄存器

`vmOneHandler` 开头被作者解释成一套固定锚点，而不是逐条猜 handler：

| 寄存器 | 作者给出的角色 |
|---|---|
| x23 | IP 字段地址，也是寄存器文件偏移的基准（ctx+0xC） |
| x20 | 字节码来源，`[x20]` 才是实际字节码指针 |
| x19 | VM 上下文基址 |
| x25 | handler 表 |
| x24 | 整数虚拟寄存器文件，ctx+0x6070，32 个 8 字节槽 |
| x26 | 32 位浮点或字寄存器文件，ctx+0x6170 |
| x27 | 64 位浮点寄存器文件，ctx+0x61F0 |
| x8 | 当前 VM 指令指针 |

作者把指令宽度写成 48 字节（`0x30`）。操作数从 `[x8+8]`、`[x8+9]`、`[x8+0xA]`、`[x8+0x10]` 读取，handler 尾部把 x8 推进到下一条。上下文布局里，`+0x0` 是魔数 `0x020007060C0C0803`，`+0xC` 是入口清零的 IP，`+0x6030` 被预置进寄存器槽 1。

他用来支撑 x24 的三条自述是：初始化函数 `sub_2E5C68` 对 `ctx+0x6070` 做 memset；trace 里约 34.3 万次 `[x24, idx, lsl/uxtw #3]`，索引落在 0 到 31；各 handler 用同一模板访问 `*(x24 + 8*idx)`。这些是作者的 IDA 加 trace 对拍，不是本库复测。

<a id="handler-passes"></a>
## handler 与多趟折叠

基础 handler 表被写成从 `0x3E1E58` 到 `0x3E3708`，共 1580 项，这次 trace 调到 335 个，日志量约 340 万。作者把 CMP/BEQ、SHL、OR、LDRB、STR，以及进出 x26/x27 的访存，列成统一语义，并修正过 `0x2E87E8`：源寄存器是字节码 `[8]`，目标是 `[9]`，再加上 `[0xA]` 的有符号偏移。

VMP 专属调用、栈操作和寄存器归一化被要求单独做 pass，而不是塞进第一条语义。返回点用 trace 里的 `ret` 对上 `bl` 写下的 LR。文中的一对地址是入口 `0x2e6774` 与返回 `0x2ebc54`。作者提醒 `ldr x8` 取 64 位而 `str w8` 只留低 32 位，返回值会被截断。

看雪正文停在能看出 VM 结构、准备往伪 C 走的位置。作者写明再往下发会碰到权利边界，所以这篇不包含完整还原结果。

<a id="limits"></a>
## 本库没有补上的部分

没有 `40.2.0` 样本，没有 code.log，没有核对 handler 表范围、34.3 万次索引或返回地址配对。魔数、偏移和 so 内地址只属于作者描述的那一版。帖子后半还有 SLEIGH 提升、字节道折叠，以及作者给出的全量计数：749 万行 trace、232281 段、266 个 entry。那些 IR 片段没有收进本篇。续篇在吾爱破解 [thread-2130745](https://www.52pojie.cn/thread-2130745-1-1.html)，收在 [七神 VMP 还原篇](./qishen-vmp-restore-52pojie.md)。
