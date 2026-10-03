---
schema_version: 2
id: signature-algorithms-mafengwo-modified-sha1-reference
document_type: reference
original_date: '2026-04-18'
archived_date: '2026-10-03'
scope:
  targets: [mafengwo]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./mafengwo-modified-sha1-trace.md#reference-extraction-202
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录 IV、f/K 分段与 feed-forward 对位的来源陈述；练习输入与 digest 留在 archive fixture，不作为 runtime 或可运行实现。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 每次只改一个点、先分清 feed-forward 与 IV、HashFinder 首次 0x80 可能是证书哈希，均为来源排查顺序，不是已验证通用脚本。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 80 轮对齐不等于 digest 正确，40 hex 不等于 serverAccepted；本轮未跑 unidbg/IDA/trace。
relations:
  - type: derived_from
    target: ./mafengwo-modified-sha1-trace.md#reference-extraction-202
  - type: supplements
    target: ../mobile-app-reverse/xfq-android-cases-compilation/mafengwo-xpreauthencode-hook.md#mafengwo-xpreauth-canonical
  - type: supplements
    target: ./xfq-crypto-notes-compilation/xfq-20260419-01.md#hashfinder-scan-window
tags: [mafengwo, SHA-1, HashFinder, Ch, Parity, Maj, feed-forward, libmfw.so, source-report]
---

# 马蜂窝魔改 SHA-1 轮函数分段参考

这张窄卡只整理来源 archive 对 **`libmfw.so` 压缩函数** 的 IV / `f`+`K` 错位分段 / feed-forward 对位。JNI 入口、canonical 串和 unidbg 观察窗口仍以 [xPreAuthencode hook](../mobile-app-reverse/xfq-android-cases-compilation/mafengwo-xpreauthencode-hook.md) 为准；通用 `0x80` 扫描见 [HashFinder](./xfq-crypto-notes-compilation/xfq-20260419-01.md)。更完整的逐轮差分表见合集笔记 [xfq-20260417-02](./xfq-crypto-notes-compilation/xfq-20260417-02.md)。练习明文与 digest 不进本卡。

<a id="parameters"></a>
## 四类魔改（来源闭合口径）

归档以星球笔记的四类魔改为准，而不是语雀练习稿在 40–59 改成 Ch 后写的“跑通了”：

| 部位 | 来源描述 | 类别 |
|---|---|---|
| IV | `H0..H4`：标准 `H0/H1/H2/H4`，`H3` 非标准 | 初始状态 |
| W 扩展 | 仍为 `ROTL1(W[i-3] ^ W[i-8] ^ W[i-14] ^ W[i-16])` | 未改 |
| 0–15 | Ch + `0x5A827999` | 与标准一致（IV 改对之后） |
| 16–19 | Parity + `0x6ED9EBA1` | 标准此处仍应是 Ch |
| 20–39 | Maj + `0x8F1BBCDC` | 标准此处是 Parity |
| 40–59 | Ch + `0x5A827999` | 标准此处是 Maj |
| 60–79 | Parity + `0xCA62C1D6` | 分段继续错位 |
| feed-forward | `digest[2] = old_H2 + d`，`digest[3] = old_H3 + c` | 对位交换 |

40 位 hex 先按 5 个大端 word 切开。SHA-1 独有 `K` / `H4` 用于定家族；本 trace 不易直接搜到 `0xC3D2E1F0`，后两档 `K` 已足够排除普通 MD5。

<a id="decision-flow"></a>
## 排查顺序

1. 用输出 word 做减法只能恢复 feed-forward 加数，不能直接当初始 `a`。若干加数看起来像标准 IV，但 `H0` / `H3` / `H4` 对不上时，先回到压缩函数入口核对初始 `a`。
2. HashFinder 第一次 `0x80` 在本样本里落在证书信息哈希，业务输入尚未进缓冲。用 bit 长度尾与 ASCII 明文交叉确认后再跟写入 PC。样本观察 PC 须按当前 `libmfw.so` 重核。
3. 标准 `a_new` 搜不到时，先不要改 W。用上一轮 `a`/`b` 定位 first mismatch round。
4. 每次只改 IV、一段 `f/K` 或 feed-forward 中的一个点。
5. 80 轮内部对齐但 digest 第 3、4 个 word 仍错，优先查最后 5 个 word 的对位。

<a id="validation"></a>
## 验收口径与限制

| 观察 | 来源允许的最小结论 | 不允许的外推 |
|---|---|---|
| 40 hex | SHA-1 家族候选 | 服务端已接受或当前版本仍用此函数 |
| 首次 `0x80` 命中 | 需要与长度尾交叉过滤 | 命中即业务明文 |
| 16 轮首次出错且 W[16] 标准 | 归到 `f`/`K` 分段 | 消息扩展已改 |
| 80 轮寄存器对齐 | 压缩循环内部可能已对 | digest 已闭合 |
| 语雀稿“40–59 改成 Ch 跑通” | 练习中途口径 | 四类魔改已完整 |

## 验证与限制

- `client` / `version` / `observed_at` 均为 unknown。Hook 面不在本卡重复。
- 练习输入与 40-hex digest 只留在来源 archive，不作为可运行 fixture 发布。
- 本轮未运行 unidbg、IDA 或 trace；常数与分段保持 `source-report`。
