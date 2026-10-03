---
schema_version: 2
id: signature-algorithms-sha1-trace-baseline
document_type: reference
original_date: "2026-04-17"
archived_date: unknown
scope:
  targets: [sha-1]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-crypto-notes-compilation/xfq-20260417-01.md#来一份标准数据-"
    basis: source-report
  - id: s2
    ref: "./xfq-crypto-notes-compilation/xfq-20260417-01.md#先记住-sha-1-的整体结构-"
    basis: source-report
  - id: s3
    ref: "./xfq-crypto-notes-compilation/xfq-20260417-01.md#明文填充-"
    basis: source-report
  - id: s4
    ref: "./xfq-crypto-notes-compilation/xfq-20260417-01.md#w015-怎么来-"
    basis: source-report
  - id: s5
    ref: "./xfq-crypto-notes-compilation/xfq-20260417-01.md#w1679-怎么扩展-"
    basis: source-report
  - id: s6
    ref: "./xfq-crypto-notes-compilation/xfq-20260417-01.md#初始寄存器-"
    basis: source-report
  - id: s7
    ref: "./xfq-crypto-notes-compilation/xfq-20260417-01.md#80-轮到底在干什么-"
    basis: source-report
  - id: s8
    ref: "./xfq-crypto-notes-compilation/xfq-20260417-01.md#代码中的日志里的列到底怎么看-"
    basis: source-report
  - id: s9
    ref: "./xfq-crypto-notes-compilation/xfq-20260417-01.md#直接看前几轮日志-"
    basis: source-report
  - id: s10
    ref: "./xfq-crypto-notes-compilation/xfq-20260417-01.md#块尾为什么还要再加一次-"
    basis: source-report
  - id: s11
    ref: "./xfq-crypto-notes-compilation/xfq-20260417-01.md#最后摘要怎么拼-"
    basis: source-report
  - id: s12
    ref: "./xfq-crypto-notes-compilation/xfq-20260417-01.md#对着日志怎么判断是不是标准-sha-1-"
    basis: source-report
  - id: s13
    ref: "./xfq-crypto-notes-compilation/xfq-20260417-01.md#sha-1-常见魔改点-"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s3, s4, s5, s6, s7, s9, s10, s11]
    basis: source-report
    limits: 只整理这篇讲义写明的标准 SHA-1 结构、常量、填充和 123456 对照值。未运行讲义脚本，未对照标准正文。围栏错位的公式不补写。
  - name: decision-flow
    anchor: decision-flow
    sources: [s8, s12, s13]
    basis: source-report
    limits: 十条检查和七类魔改是讲义的识别清单。验收句用了“基本就是”。马蜂窝样本的错位分段不在本篇。
relations:
  - type: derived_from
    target: "./xfq-crypto-notes-compilation/xfq-20260417-01.md#对着日志怎么判断是不是标准-sha-1-"
tags: [SHA-1, trace, source-report]
---

# 标准 SHA-1 的 trace 对照与魔改位置

这张卡用来判断一份轮日志像不像讲义中的标准 SHA-1，以及作者把魔改分成哪几类。它不是站点签名卡。马蜂窝那一个样本的轮分段和 feed-forward 对调见 [马蜂窝魔改 SHA1](./mafengwo-modified-sha1-trace.md#逐轮只改一个点) 与 [mfw_trace_sha1 学习笔记](./xfq-crypto-notes-compilation/xfq-20260417-02.md#mfw_trace_sha1_学习笔记)。讲义只说魔改案例相对少、目前只碰到过一个马蜂窝，没有写出该样本的替换表。

<a id="parameters"></a>
## 标准结构里要对照的字段

讲义把 SHA-1 写成 Merkle-Damgard：先填充，再按 64 字节分块，块尾把工作状态加回初始状态，最后把内部寄存器拼成摘要。和 MD5 对照时，来源强调 SHA-1 是大端、5 个 32 位寄存器、80 轮而不是 64 轮、4 段常量而不是 64 个 T[i]。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 讲义用 message b"123456" 的期望摘要 7c4a8d09ca3762af61e59520943dc26494f8941b 作为标准对照 | s1，标准数据 | source-report | 该讲义的单块例子 | 本轮未计算 |
| C2 | 填充是大端：先 0x80，再 0x00，直到长度模 64 等于 56，最后 8 字节大端 bit 长度 | s3，明文填充 | source-report | 讲义描述的标准 padding | 123456 的 bit 长度被写成 48 = 0x30 |
| C3 | 长度字段若不是这种大端补法，来源即视为已经不是标准 SHA-1 | s3，填充末 | source-report | 单块长度字段 | 未覆盖多块消息 |
| C4 | W[0..15] 按大端拆 32 位字；123456 的 W0 被写成 0x31323334 | s4，W[0..15] | source-report | 该测试明文 | 不把小端字形态当成 SHA-1 |
| C5 | W[i] = ROTL1(W[i-3] XOR W[i-8] XOR W[i-14] XOR W[i-16])，后 64 个字由扩展而来 | s5，扩展公式 | source-report | 标准消息扩展 | 日志里看到该扩展只说明这一段像标准扩展 |
| C6 | 初始五字在日志例子中为 67452301 efcdab89 98badcfe 10325476 c3d2e1f0 | s6，初始寄存器日志 | source-report | 标准 IV | 一上来不同通常被来源解释为改了 IV |
| C7 | 每轮核心式为 temp = ROTL5(a) + f(b, c, d) + e + K + W[i]，且 a_new = temp | s7，统一公式 | source-report | 标准轮函数 | 讲义称其余寄存器是带旋转的搬运 |
| C8 | 80 轮分 4 段、每段 20 轮，每段只换布尔函数和常量 K | s7，四段函数 | source-report | 标准分段 | 段内公式在来源导出里有断行，不据此补全实现 |
| C9 | K0 到 K3 被写成 floor(2^30 * sqrt(2/3/5/10))，十六进制为 5A827999、6ED9EBA1、8F1BBCDC、CA62C1D6 | s7，为什么 K | source-report | 标准 K | 分段仍是 20/20/20/20 但 K 不同，来源视为魔改 |
| C10 | 块尾做 feed-forward，不是直接输出当前 a b c d e；123456 的拼接结果与 C1 相同 | s10 块尾；s1 期望摘要 | source-report | 单块 123456 | 未验证多块加法 |
| C11 | 摘要是 160 bit / 20 字节，五个 32 位寄存器按大端直接拼接 | s11，摘要拼接 | source-report | 标准输出 | 截断、倒序或小端输出被来源分开算 |

第 20 轮是来源用来看第一段是否切走的位置：函数从 Ch 变成 Par，K 从 0x5A827999 变成 0x6ED9EBA1。没有这次切换，来源就不把它当标准 SHA-1。

<a id="decision-flow"></a>
## 日志上先看哪里

来源给出的日志列包括进入时的 a b c d e、函数名、f 的值、K、W[i]、ROTL5(a)、ROTL30(b) 和 temp。它要求 a_new 等于 temp，下一轮 b 等于旧 a，下一轮 c 等于 ROTL30(b)，下一轮 d 等于旧 c，下一轮 e 等于旧 d。这些关系不成立，就不是标准寄存器更新。

十条需同时满足的检查从 padding、64 字节分块、大端 W[0..15]、ROTL1 扩展、标准 IV、四段轮界、Ch/Parity/Maj/Parity、四段 K、ROTL5(a) 与 ROTL30(b)，直到块尾 H += working_state。来源的收束句是“这 10 条都对，基本就是标准 SHA-1 核心了”，不是严格的唯一性证明。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C12 | 从 trace 反推时，来源要求十条同时成立才把核心叫作标准 SHA-1 | s12，十条 | source-report | 有轮日志或等价 trace 的实现 | “基本就是”保留了未列举差异 |
| C13 | 初始 ABCDE 不等于标准 IV、但轮函数和 W、K 仍在时，来源只把它叫作改了初始化 | s13，魔改点 1 | source-report | IV 类魔改 | 不自动决定业务还能否复现 |
| C14 | 四段 K 不是那四个标准值，来源称为核心魔改 | s13，魔改点 2 | source-report | K 类 | 需先确认分段仍是四段 |
| C15 | 标准轮只有一个 f(b, c, d)；再串布尔函数或 temp 按标准式对不上，就不是标准轮 | s13，魔改点 4 | source-report | 轮函数 | 讲义没有给出额外函数的通用模板 |
| C16 | W 扩展的 ROTL1、主状态 ROTL5(a)、c 更新 ROTL30(b) 被改位数，就不是标准核心 | s13，魔改点 5 | source-report | 旋转类 | 来源只举了“变成别的位数” |
| C17 | 块尾不再 H += state 而是直接覆盖，来源视为结构已被改掉 | s13，魔改点 6 | source-report | feed-forward | 不表示这种改法常见 |
| C18 | 小端、截断或改拼接顺序时，核心轮函数仍可能标准，但最终 hash 不是标准 SHA-1 | s13，魔改点 7 | source-report | 输出类 | 要先把轮函数和输出分开看 |

## 验证与限制

- 没有本地脚本运行。C1 的期望摘要只是讲义中的字符串。
- 讲义正文有围栏和标题错位。本卡不把断行公式恢复成可编译实现。
- 不覆盖 SHA-256 除“padding 同样是大端”这句以外的内容，不覆盖 HMAC、盐或业务编码。
- 未知：多块消息的跨块 feed-forward 例子、讲义提到但未附上的两份 Python、马蜂窝样本的具体替换。后者去案例文，不在本卡补全。
