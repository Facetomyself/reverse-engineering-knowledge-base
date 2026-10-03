---
schema_version: 2
id: xfq-chacha20-layout-nonce-reference
document_type: reference
original_date: '2026-02-24'
archived_date: '2026-10-02'
scope:
  targets: [chacha20]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260224-01.md#算法背景"
    basis: source-report
  - id: s2
    ref: "./xfq-20260224-01.md#1-状态矩阵初始化"
    basis: source-report
  - id: s3
    ref: "./xfq-20260224-01.md#2-quarter-round-详解"
    basis: source-report
  - id: s4
    ref: "./xfq-20260224-01.md#3-列轮--对角轮"
    basis: source-report
  - id: s5
    ref: "./xfq-20260224-01.md#4-feedforward"
    basis: source-report
  - id: s6
    ref: "./xfq-20260224-01.md#测试数据"
    basis: source-report
  - id: s7
    ref: "./xfq-20260224-01.md#5-异或加密"
    basis: source-report
  - id: s8
    ref: "./xfq-20260224-01.md#71-常见配置差异非标准配置"
    basis: source-report
  - id: s9
    ref: "./xfq-20260224-01.md#72-算法核心修改真正的魔改"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s3, s4, s5]
    basis: source-report
    limits: 只保留讲义里仍成行的布局、移位量和轮索引。Quarter Round 函数体被拆成断行，不恢复成可执行轮函数。未重算 20 轮状态。
  - name: decision-flow
    anchor: decision-flow
    sources: [s8, s9]
    basis: source-report
    limits: IETF、Bernstein 和 XChaCha20 的 nonce 宽度，以及计数器起点、常数字符串、轮数和移位量，是讲义的分叉清单。没有对应到 TLS 实现。
  - name: validation
    anchor: validation
    sources: [s6, s7]
    basis: source-report
    limits: 测试向量使用 8 字节 nonce 和计数器 0，按讲义自己的分类属于 Bernstein 布局，不是 12 字节 nonce。期望密文未重算。
relations:
  - type: derived_from
    target: "./xfq-20260224-01.md#2-quarter-round-详解"
tags:
  - chacha20
  - salsa20
  - source-report
---

# ChaCha20 相对 Salsa20 的轮结构与 nonce 宽度

这张卡用来区分讲义中的 ChaCha20 和 Salsa20：常量放在哪一行、四分轮先加还是先转、列轮之后走对角还是走行，以及 8、12、24 字节 nonce 各填哪一种矩阵。它不覆盖某个产品里的 ChaCha20 调用。

<a id="parameters"></a>
## 参数

讲义把差异收成两处：四分轮的操作顺序，以及列轮之后的对角轮。矩阵把常量放在第一行，计数器和 nonce 放在第四行。20 轮之后做和 Salsa20 相同的加回初始状态。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | ChaCha20 的四分轮被写成先加、再异或、再旋转，并立即反馈 | ChaCha20: a += b; d ^= a; d = rotl(d, 16)  → 先加再异或后转 | s1，xfq-20260224-01.md:57 | source-report | 只展示了第一步的形状 |
| C2 | Salsa20 的对应步被写成先加后转再异或 | Salsa20:  b ^= rotl(a + d, 7)     → 先加后转再异或 | s1，xfq-20260224-01.md:56 | source-report | 不是完整四分轮 |
| C3 | 移位量被写成 ChaCha20 的 16、12、8、7，对照 Salsa20 的 7、9、13、18 | 移位量也不同:ChaCha20 用 16, 12, 8, 7,Salsa20 用 7, 9, 13, 18。 | s3，xfq-20260224-01.md:163 | source-report | 函数体断行，不据此补轮函数 |
| C4 | 双轮的后半被写成对角轮，而不是 Salsa20 的行轮 | ChaCha20: 列轮 + 对角轮 | s1，xfq-20260224-01.md:65 | source-report | 列轮索引在后文 |
| C5 | 主对角线四分轮的下标是 0、5、10、15 | self._quarter_round(state, 0, 5, 10, 15)  # 主对角线 | s4，xfq-20260224-01.md:178 | source-report | 其余三条对角索引未逐条引用 |
| C6 | 第一行常量被写成字符串 expand 32-byte k | state[0:4] = SIGMA  # "expand 32-byte k" | s2，xfq-20260224-01.md:121 | source-report | 四个常量字的十六进制表未逐字复核 |
| C7 | 低 32 位计数器放在 state[12] | state[12] = counter & 0xFFFFFFFF | s2，xfq-20260224-01.md:125 | source-report | 高半字和 nonce 的赋值在相邻粘连行 |
| C8 | 20 轮之后把结果加回初始状态 | 和 Salsa20 完全一样:20 轮结果加上初始状态。 | s5，xfq-20260224-01.md:210 | source-report | 未重算 feedforward 表 |

<a id="decision-flow"></a>
## 识别

同一套四分轮会因为 nonce 宽度和计数器起点对不上。讲义把这叫做最大的坑：先看第 12 到 15 字是 8 字节 nonce 加 8 字节计数器，还是 12 字节 nonce 加 4 字节计数器，再看轮数和移位量有没有被换掉。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C9 | Bernstein 原版被写成 8 字节 nonce 加 8 字节计数器 | Bernstein 原版:8 字节 Nonce + 8 字节 Counter。 | s8，xfq-20260224-01.md:296 | source-report | 未对照原论文 |
| C10 | IETF RFC 7539 被写成 12 字节 nonce 加 4 字节计数器 | IETF RFC 7539:12 字节 Nonce + 4 字节 Counter(最常见,用于 TLS/WireGuard)。 | s8，xfq-20260224-01.md:297 | source-report | 未对照 RFC 正文 |
| C11 | XChaCha20 被写成 24 字节 nonce | XChaCha20:24 字节 Nonce(用于随机 Nonce 场景)。 | s8，xfq-20260224-01.md:298 | source-report | 没有 HChaCha20 的派生步骤 |
| C12 | 计数器标准从 0 开始，讲义称有的实现从 1 开始 | 有些实现(如 TLS)可能从 1 开始。 | s8，xfq-20260224-01.md:302 | source-report | 没有具体 TLS 版本 |
| C13 | 改掉 expand 32-byte k 被当成魔改 | 同 Salsa20,标准是 "expand 32-byte k"。 魔改:修改这个字符串。 | s9，xfq-20260224-01.md:307 | source-report | 未给出替换字符串 |
| C14 | 8 轮被单独点名为 ChaCha8 | ChaCha8 (8轮):极速,某些轻量级加密使用。 | s9，xfq-20260224-01.md:309 | source-report | ChaCha12 只在下一行点名，未写入本表 |
| C15 | 改掉 16、12、8、7 这组移位量被当成魔改 | 标准移位量是 16, 12, 8, 7。 魔改:修改这组移位量。 | s9，xfq-20260224-01.md:314 | source-report | 没有替代移位表 |

<a id="validation"></a>
## 对照值

这组测试数据的 nonce 是 8 字节，计数器是 0。它只能当作讲义自己的 Bernstein 布局例子，不能拿去对 RFC 7539 的 12 字节 nonce。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C16 | nonce 被写成 12345678，8 字节 | Nonce: 12345678 (8 字节) | s6，xfq-20260224-01.md:99 | source-report | 不是 12 字节 nonce |
| C17 | 计数器被写成 0 | Counter: 0 | s6，xfq-20260224-01.md:100 | source-report | 未验证从 1 开始的分支 |
| C18 | 期望密文被写成 74e44b355401d6e39431fc383e322a94 | 密文(hex): 74e44b355401d6e39431fc383e322a94 | s6，xfq-20260224-01.md:101 | source-report | 未重算 |
| C19 | 密钥流前 16 字节被写成 0c8d2a5a3264b884f254925f465b4bfb | 密钥流前16字节: 0c8d2a5a3264b884f254925f465b4bfb | s7，xfq-20260224-01.md:232 | source-report | 64 字节块的其余部分没有列出 |
| C20 | 初始矩阵第四行被标成 counter=0 与 nonce | counter=0, nonce | s2，xfq-20260224-01.md:137 | source-report | 整行含表格竖线，只引用这一段；未重算小端字 |

## 验证与限制

- 没有本地计算。C16 到 C20 只是讲义中的字符串。
- Quarter Round、列轮循环和初始状态的代码围栏断行粘连。本卡不把它们恢复成脚本。
- 为什么选 ChaCha20 的硬件对照，以及 RC4/Salsa20/ChaCha20 对照表，不新增参数。
- 未知：RFC 7539 的 12 字节填法没有单独的测试向量；第 2 轮和第 20 轮的中间矩阵未复核；ChaCha12 只被点名。
