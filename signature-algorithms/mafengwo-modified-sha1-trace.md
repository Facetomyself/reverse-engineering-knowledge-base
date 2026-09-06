# 马蜂窝魔改 SHA1：从 HashFinder 到轮函数分段

> 来源: 语雀 xiaofeng777/android_example
> 原始发布时间: 2026-04-18
> 归档日期: 2026-09-06
> 分类: signature-algorithms
>
> 马蜂窝 `libmfw.so` 对输入 `123456` 给出 40 位 hex。语雀练习稿用 HashFinder 的 `0x80` 扫描和逐轮 `a_new` 对照，把压缩函数从标准 SHA-1 的 20 轮一段改成 Ch / Parity / Maj 错位分段。更完整的四类魔改（含 feed-forward `H2/H3` 对调）以知识星球笔记为准，不要停在「40–59 改成 Ch 就跑通」。

## 收录说明

原文：[马蜂窝旅游 魔改sha1 trace还原](https://www.yuque.com/xiaofeng777/android_example/dal64628z7lf3cgm?singleDoc#)。这是作者对着已有 AI 读 trace 结果自己重做的练习稿，不是从零的完整闭合。截图 OCR、星球短链和插件广告未收录。

同一案例的闭合结论、逐轮差分表和 feed-forward 对位见 [mfw_trace_sha1_学习笔记](xfq-crypto-notes-compilation/xfq-20260417-02.md)。HashFinder 的 `0x80` 扫描见 [unidbg插件-哈希-明文扫描](xfq-crypto-notes-compilation/xfq-20260419-01.md)。

## 样本与锚点

| 项 | 内容 |
|---|---|
| Native | `libmfw.so` |
| 练习输入 | `123456` |
| 观察输出 | `2f45b7dd81d48343c79ddbc14cddb756d7353190` |
| 长度暗示 | 40 个 hex 字符 = 20 字节，优先当 SHA-1 家族 |

输出按 5 个大端 word 切开：

```text
2f45b7dd  81d48343  c79ddbc1  4cddb756  d7353190
```

SHA-1 / SHA-0 / MD4 都可能出现部分相同 IV。作者先搜 SHA-1 独有量：

```text
IV[4] = 0xC3D2E1F0
K     = 0x5A827999  0x6ED9EBA1  0x8F1BBCDC  0xCA62C1D6
```

`0xC3D2E1F0` 在本 trace 里不好直接搜到；`0x8F1BBCDC` 和 `0xCA62C1D6` 能搜到，足够把家族从「普通 MD5」里剔掉。

## 先分清 feed-forward 和真实 IV

把 5 个输出 word 当成「最终寄存器 + 旧 IV」反推时，会得到一组混着标准 IV 的加数：

```text
0x2f45b7dd = 0xee6ac08b + 0x40daf752
0x81d48343 = 0x9206d7ba + 0xefcdab89
0xc79ddbc1 = 0x2ee2fec3 + 0x98badcfe
0x4cddb756 = 0xee9397da + 0x5e4a1f7c
0xd7353190 = 0xc702dd1a + 0x10325476
```

这里的 `0xefcdab89` / `0x98badcfe` / `0x10325476` 像标准 IV，但 `H0` / `H3` / `H4` 对不上 `0x67452301` / `0x10325476` / `0xC3D2E1F0`。练习稿的关键修正：不要把 feed-forward 加数当成初始 `a`。

用明文 `0x31323334`（`1234`）和 `b` 的 `ROTL 30` 当锚，回到压缩函数入口，初始 `a` 仍是 `0x67452301`。改完后再搜 `a_new` 才能对上第 0 轮。

## HashFinder：第一个 `0x80` 不一定是业务输入

按 MD 结构扫 `0x80` 时，第一次命中发生在证书信息哈希：输入 `123456` 还没进缓冲。长度尾 `0x30`（48 bit = 6 字节）才对上练习输入。

过滤规则：

- 不要只按立即数 `0x80` 扫，日志会上千行且 PC 容易错位
- 跟到真正执行 `v6 = 0x80` 的那条 PC（文中 `0x668A8`）
- 再看该缓冲更早的写入；本样本里 `a2` 被直接交给这块缓冲

确认消息块后，padding 仍是标准 SHA 风格：`31 32 33 34 35 36 80 ... 00 00 00 30`。

## 逐轮只改一个点

标准 SHA-1 的 `a_new` 搜不到时，先不要改 W 扩展。作者用上一轮的 `a`/`b` 定位，发现：

| 轮次 | 标准期望 | 本样本 |
|---|---|---|
| 0–15 | Ch + `0x5A827999` | 与标准一致（IV 改对之后） |
| 16–19 | 仍应是 Ch | 三个 `eor`，即 Parity；K 已是 `0x6ED9EBA1` |
| 20–39 | Parity | `((b \| c) & d) ^ (b & c)`，即 Maj；K 为 `0x8F1BBCDC` |
| 40–59 | Maj | 回到 Ch / Choose |

W[16] 仍是 `ROTL1(W[i-3] ^ W[i-8] ^ W[i-14] ^ W[i-16])`，所以 16 轮首次出错应归到 `f`/`K` 分段，不是消息扩展。

语雀稿在把 40–59 改成 Ch 后写「跑通了」。同一案例的星球笔记继续对照 digest，发现 80 轮内部可以对齐，但第 3、4 个 word 仍错，直到 feed-forward 改成 `H2 += d`、`H3 += c`。归档时以笔记的四类魔改为准：

```text
H0..H4 = 0x67452301, 0xefcdab89, 0x98badcfe, 0x5e4a1f7c, 0x10325476

0..15  : Ch  + 0x5A827999
16..19 : Par + 0x6ED9EBA1
20..39 : Maj + 0x8F1BBCDC
40..59 : Ch  + 0x5A827999
60..79 : Par + 0xCA62C1D6

digest[2] = old_H2 + d
digest[3] = old_H3 + c
```

对 `123456` 的闭合输出仍是 `2f45b7dd81d48343c79ddbc14cddb756d7353190`。

## 可复用打法

1. 40 位 hex 先按 5 个 word 切开，用独有 K / `H4` 定家族，再谈魔改。
2. 输出 word 的加法拆解只能恢复 feed-forward，不能直接当 IV。
3. HashFinder 的第一次 `0x80` 可能是证书或其他预哈希；用 bit 长度和 ASCII 明文交叉确认。
4. 每次只改 IV、一段 `f/K` 或 feed-forward 中的一个点，用 first mismatch round 找分界。
5. 80 轮都对齐但 digest 仍错，优先查最后 5 个 word 的对位，而不是回头改 W。
