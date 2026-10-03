---
schema_version: 2
id: native-analysis-qishen-vmp-restore-52pojie
document_type: archive
original_date: '2026-09-28'
archived_date: '2026-10-02'
scope:
  targets: [qishen-android-vmp]
  client: android
  version: 40.2.0
  observed_at: unknown
sources:
  - id: s1
    ref: https://www.52pojie.cn/thread-2130745-1-1.html
    basis: source-report
source_completeness: partial
tags: [qishen, VMP, structural-ir, SM3, source-report]
---

# 七神 VMP 还原：从去虚拟化日志到结构

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>

吾爱破解 [thread-2130745](https://www.52pojie.cn/thread-2130745-1-1.html)，发帖账号 rsds0duck，文内署名「人生导师」。文内日期 2026-09-28，帖子时间 2026-10-02。上文是看雪 [thread-292925](https://bbs.kanxue.com/thread-292925.htm)。

</details>

上篇停在去虚拟化的 trace 日志。这篇要收缩的是重复执行行为，不是再列一遍指令。作者把目标写成 Structural IR：把动态序列里的重复、分叉、回边和调用边压成结构节点。本库没有他的 lifter、trace 或 33 个函数的输出。

<a id="structures"></a>
## 五种结构

作者按程序形态拆了五类：

1. 直线代码按 worklist 收成必经块。
2. 条件对应 VM 里不确定的 IP 推进。他认为当时的字节码步进是规整的，可以分别看 true 和 false 各加多少。
3. 循环靠同一段重复执行再加回边判断。文中的例子用 IP `0x11b` 回到 `0x104`，不相等时偏移 `-0x18`，相等时落到 `0x11c`，被解释成 `while (reg_a != reg_b)`。
4. 调用不是分支，按必然执行的基本块处理，跳走再回来。
5. 错误处理要看这台 VM 有没有实现。作者拿京东的 VMP 作对照：那边有一条小分支然后 `ret`，作用是防止虚拟机意外，不是给还原用的错误模型。豌豆荚这份是否同样实现，文内没有另写。

他同时认为当时的输出还像日志，不像能继续降低的 IR。想要的形状是接近伪汇编的 `opcode dst, src`，复合指令再像 P-code 一样拆开。条件跳转怎么拆，文内写明还没定。

<a id="lift-and-check"></a>
## 提升和自检

立即数如果提升器没有内存，会摊成多条 `ldr` / `sxt`。作者说顺着临时量的 def 链拼回去，运行时地址留着当回查 IDA 的锚点。

验收只用 trace 自己：每一步的实际后继要落在解出的两路目标里。他给出的数字是 129648 条转移里 129645 条对上，余 3 条分在三个函数。这是作者统计，本库没有原始转移表。

<a id="ceilings"></a>
## 作者写出的三堵墙

动态 trace 只有走过的路径。164 个跳转落点里 27 个指向本次没执行的槽位，缺的边只能换输入再跑。常量有的是每次调用解密出来的，不在字节码里，两次调用之间只差少数 `mov` 立即数。操作数槽的运行时地址在没有内存的提升器里仍解不出值。

常量指纹方面，作者用 `--consts` 把拆成高低两半的 32 位立即数拼回去。他据此把成串的 `0x79cc4519` 与 `0x7a879d8a` 认成 SM3 轮常量，并提到 func 7 一带还有 SM3 的 IV。直接搜索拼好的常数会漏掉，因为日志里高半和低半是分开的。func 11 的 `0x20220420` 和 func 26 的另外两个常数，作者写明还没认出来。

压缩结果被写成 566691 次 handler 执行收到 33 个函数、9183 行。作者把还原定义成仪器：认出 SM3 之后，下一步是查输入从哪来、摘要谁取走，以及 316 个 native 调用的归属，而不是读懂每一轮。他明确不推荐为了还原而还原，并认为这份二进制还原仍然模糊，达不到 JSVMP 那种可替换代码。

<a id="limits"></a>
## 本库没有补上的部分

没有重放 129648 条转移，没有核对 99.998% 这个比例，没有把 SM3 常量代回样本，也没有 func 11 / func 26 的未识别常数结论。分析篇收在 [七神 VMP 分析](./qishen-vmp-analysis-kanxue.md)。
