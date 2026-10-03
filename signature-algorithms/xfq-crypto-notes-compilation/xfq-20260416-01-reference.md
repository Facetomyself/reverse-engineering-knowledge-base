---
schema_version: 2
id: md5-core-trace-landmarks
document_type: reference
original_date: '2026-04-16'
archived_date: '2026-10-02'
scope:
  targets: [md5]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260416-01.md#md5-流程-py-实现-"
    basis: source-report
  - id: s2
    ref: "./xfq-20260416-01.md#明文填充padding-"
    basis: source-report
  - id: s7
    ref: "./xfq-20260416-01.md#初始寄存器abcd-"
    basis: source-report
  - id: s3
    ref: "./xfq-20260416-01.md#64轮压缩流程-"
    basis: source-report
  - id: s4
    ref: "./xfq-20260416-01.md#代码中的64大轮日志表格-"
    basis: source-report
  - id: s5
    ref: "./xfq-20260416-01.md#最终-digest-是怎么出来的-"
    basis: source-report
  - id: s6
    ref: "./xfq-20260416-01.md#魔改md5-"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s2, s3, s4, s5, s6, s7]
    basis: source-report
    limits: 只保留作者写下的填充、初值、轮函数、g 索引、小端输出和块尾相加。归档代码有语句粘连，本卡不把它当成可运行实现。
  - name: validation
    anchor: validation
    sources: [s1, s4]
    basis: source-report
    limits: 「123456」的期望摘要和 M[0]、M[1]、M[14] 都来自作者贴出的轮日志。本轮没有重算。
  - name: decision-flow
    anchor: decision-flow
    sources: [s6]
    basis: source-report
    limits: 魔改落点是作者的对照分支。文末通杀打法只有一句转引，没有验收和失败出口。
relations:
  - type: derived_from
    target: "./xfq-20260416-01.md#md5-流程-py-实现-"
tags: [md5, trace, source-report]
---

# 标准 MD5 轮日志地标与魔改落点

这张卡回答：怎样从一轮日志认出作者所谓的标准 MD5，以及对不上时作者把原因归到哪一层。target `md5` 的 parameters、validation、decision-flow 查询都是空的。Shein random 那张卡是另一个目标上的变体状态字；HashFinder 那张卡是 unidbg 里扫 `0x80` 填充，都不是这张轮日志。依据停在 `source-report`。

<a id="parameters"></a>
## 填充、四轮与小端摘要

作者把填充写成三步：先补 `0x80`，再补 `0x00` 直到长度模 64 等于 56，最后补 8 字节小端的比特长度。初值 A 写成 `0x67452301`。每步是布尔函数加 a、加 T、加 M[g]，左旋 S[i]，再加回 b，然后寄存器轮转。F 的原句是 `f = (b & c) | (~b & d)`。F/G/H/I 各 16 步。g 在第一大轮等于 i，第二大轮是 `(5*i+1) mod 16`。块尾是旧 ABCD 与本块 ABCD 按字相加。摘要不是把四个寄存器按寄存器显示的字节序直接拼接，而是每个 32 位字小端写出。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 1. 先补一个字节 0x80 | s2 ./xfq-20260416-01.md:261 | source-report | 作者的填充第 1 步 | 与按位补 1 的叙述作者认为是同一规则 |
| C2 | 2. 再补若干个 0x00,补到长度 % 64 == 56 | s2 ./xfq-20260416-01.md:262 | source-report | 作者的填充第 2 步 | 长度是字节长度 |
| C3 | 3. 最后补上原始消息长度(bit位长度)的 8 字节小端序 | s2 ./xfq-20260416-01.md:265 | source-report | 作者的填充第 3 步 | 未讨论超过 64 位长度 |
| C4 | self.A = 0x67452301 | s7 ./xfq-20260416-01.md:308 | source-report | 作者列出的标准初值 A | B/C/D 在相邻行，本条只引 A |
| C5 | f_value      = F/G/H/I(b, c, d) | s3 ./xfq-20260416-01.md:320 | source-report | 作者的一轮公式开头 | 完整四行在相邻代码行 |
| C6 | (~b & d) | s3 ./xfq-20260416-01.md:351 | source-report | 作者写下的 F | 原句是 b 与 c 相与，再或上这个式子；只覆盖第 0–15 步 |
| C7 | 第1轮(F): g = i | s3 ./xfq-20260416-01.md:371 | source-report | 作者的第一大轮取字 | 后三大轮索引不同 |
| C8 | a, d, c, b = d, c, b, b_new | s3 ./xfq-20260416-01.md:324 | source-report | 作者的标准寄存器轮转 | 魔改节复述了同一句；改了轮转会从下一轮开始错位 |
| C9 | b_new = b + left_rotate(f + a + T[i] + M[g], S[i]) | s6 ./xfq-20260416-01.md:760 | source-report | 作者的标准迭代 | 作者把缺 b、改加 c、把加改成异或都算魔改 |
| C10 | self.A = (self.A + a) & 0xFFFFFFFF | s4 ./xfq-20260416-01.md:566 | source-report | 作者的块尾 feed-forward | 只引 A；B/C/D 同形 |
| C11 | 原因很简单:公式确实是拼起来,但是 MD5要求了 输出时每个 32 位寄存器按小端序写入。 | s5 ./xfq-20260416-01.md:596 | source-report | 作者对摘要字节序的解释 | 未独立打包 |

<a id="validation"></a>
## 「123456」轮日志里的三个字

作者把 `123456` 的期望摘要写成 `e10adc3949ba59abbe56e057f20f883e`，并贴了 64 轮表。用来认填充块的三处是：第 0 轮 M[0] 为 `34333231`，第 1 轮 M[1] 对应 `35 36 80 00` 的小端字 `0x00803635`，第 14 轮 M[14] 为 `0x30`（48 bit）。第 16 轮函数从 F 换成 G，g 不再等于 i。这些是作者表里的地标，不是本轮重算。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C12 | correct_md5_hex = "e10adc3949ba59abbe56e057f20f883e" | s1 ./xfq-20260416-01.md:76 | source-report | 作者给「123456」的期望摘要 | 未见本轮打印结果 |
| C13 | M[g] = 34333231,正好就是填充后第一组 word | s4 ./xfq-20260416-01.md:444 | source-report | 作者第 0 轮 | 只对这条明文的小端首字 |
| C14 | 35 36 80 00  ->  0x00803635 (小端) | s4 ./xfq-20260416-01.md:467 | source-report | 作者第 1 轮的填充字 | 只对这条 6 字节明文 |
| C15 | M[14] = 0x00000030 | s4 ./xfq-20260416-01.md:481 | source-report | 作者第 14 轮的长度字 | 48 bit 只属于这条消息 |

<a id="decision-flow"></a>
## 对不上时作者归到哪一层

作者的判据是四件事：`f_value`、`M[g]`、`b_new`、块尾 ABCD。M[g] 已经不是原始明文，归到加盐或预先编码。M[g] 的值变了但访问顺序没变，先怀疑字的端序或额外异或，而不是 g 公式。T、S、M[g] 都能对上而 `f_value` 不能，归到布尔函数。`f_value` 和 T、S、M[g] 都对而 `b_new` 不对，归到迭代式。四大轮的 F/G/H/I 节奏不对，归到轮数或大轮顺序。单块时块尾 ABCD 不对、多块时下一块初值也错，归到 feed-forward。ABCD 对而十六进制摘要不对，归到输出字节序或摘要后再包一层。等价布尔式、另一种 rotate 写法、运行时现算 T 表，作者称为伪魔改，不把核心判成已改。

Shein、xhs 只被点名。Shein 的状态字在另一张卡，不在本篇重复。文末要读者去看别的文章，没有本篇自己的步骤和失败出口。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C16 | f_value 对不对 | s6 ./xfq-20260416-01.md:896 | source-report | 作者列出的四项判据之一 | 同段还有 M[g]、b_new、块尾 ABCD |

## 验证与限制

- 64 轮全表不转写，只留能对上填充块的三个字和期望摘要。
- 第一大轮 g 连续这一点，作者认为可以从 trace 里抽出明文；HashFinder 卡走的是另一条内存扫描，不并入。
- 没有原始 trace，没有本轮重算，也没有目标版本。
