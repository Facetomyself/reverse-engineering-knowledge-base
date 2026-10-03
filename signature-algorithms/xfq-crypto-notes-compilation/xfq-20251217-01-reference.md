---
schema_version: 2
id: blowfish-ecb-ofb-parameter-layout
document_type: reference
original_date: '2025-12-17'
archived_date: '2026-10-02'
scope:
  targets: [Blowfish]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./xfq-20251217-01.md#42-f-函数
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留讲义写明的分组、端序、F 组合、521 次替换和 OFB 反馈。四个 S 盒的数值不在正文。
  - name: validation
    anchor: boundaries
    sources: [s1]
    basis: source-report
    limits: 两段密文和“实现步骤和标准的有区别”都是作者自述。本轮没有运行这段 Python。
relations:
  - type: derived_from
    target: ./xfq-20251217-01.md#42-f-函数
tags: [blowfish, ofb, feistel, source-report]
---

# Blowfish 的大端 Feistel 与 OFB 反馈

这份参考卡回答：讲义里的 Blowfish 怎样切 64 位块、F 怎样用四个 S 盒、密钥扩展做到哪一次替换，以及 OFB 的密钥流从哪来。它不是可运行实现，也不收录示例密钥。来源是 [Blowfish 实现讲义](./xfq-20251217-01.md#42-f-函数)。

<a id="parameters"></a>
## 参数

参数表写密钥 `32-448 位 (4-56 字节)`，分组 `64 位 (8 字节)`，`16 轮`，结构是 `Feistel 网络`。P 与 S 的 `初始值来自 π 的小数部分`。贴出的 P 阵列共 18 个字，开头是 `0x243F6A88`。S 盒被写成 `4 个,每个 256 个 32 位元素`，随后 `太多了,丢进代码里`。

密钥按 `每 4 字节构造一个 32 位整数,与 P[i] 异或`。循环下标那一行在讲义里粘在一起，原文是 `j = (j + 1) % key_lenself.P[i] ^= ret_32int`。替换从全零块开始：`P矩阵18长度,每次替换两个`，四个 S 盒同样成对写入。流程概述把这一段叫 `521次加密替换P和S`。

明文块 `Blowfish 块大小为 8 字节`。填充函数的块长是 `block_size: int = 8`。讲义的 8 字节样例在整块之后仍写 `填充值: 0x08 × 8`。拆块是 `int.from_bytes(block[0:4], "big")`，右半同样用 `"big"`。

16 轮里先 `L ^= self.P[idx]`，再 `R ^= self.___feistel(L)`，然后 `L, R = R, L`。轮后还有 `L ^= self.P[16]`、`R ^= self.P[17]`，并再交换一次。F 的文字式是 `F(x) = ((S[0][a] + S[1][b]) mod 2^32) XOR S[2][c]) + S[3][d]) mod 2^32`。代码把高字节放在 `a = (x >> 24) & 0xFF`。

OFB 三句是 `加密解密操作相同`、`无需填充,密文长度 = 明文长度`、`IV 必须唯一,不可重复使用`。实现里 `output_block = iv`，每 8 字节先 `output_block = self._encrypt_block(output_block)`，再 `zip(plain_block, output_block)`。返回说明是 `密文 (不含 IV,长度 = 明文长度)`。解密函数 `return self.encrypt_ofb(ciphertext, key_bytes, iv)`。IV `长度必须等于块大小(8字节)`，并且 `每次加密使用不同的 IV`，`IV 可以明文传输`。

<a id="boundaries"></a>
## 验证与限制

作者在开头写 `(这里我自己的实现步骤和标准的有区别,大家可以看看)`，但正文没有指出哪一步偏离标准。ECB 段给出 `完整密文(hex): b8498c7952e8a7946e70232f3c3d404a`。OFB 段给出 `# 密文(hex): 64994f4c7aa4221e`。两段都是讲义贴出的结果。四个 S 盒不在正文，示例密钥不进入本卡。本轮没有运行这段 Python。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 密钥 `32-448 位 (4-56 字节)`，分组 `64 位 (8 字节)`，`16 轮`。 | s1 第 100、104、106 行 | source-report | 讲义参数表 | 未对照 RFC 或标准实现 |
| C2 | P/S `初始值来自 π 的小数部分`，P 从 `0x243F6A88` 起；S 盒 `太多了,丢进代码里`。 | s1 第 117、141、149 行 | source-report | 初始化常数 | 四个 S 盒数值不在正文 |
| C3 | 密钥 `每 4 字节构造一个 32 位整数,与 P[i] 异或`，然后 `521次加密替换P和S`。 | s1 第 166、461 行 | source-report | 密钥扩展 | 521 次写在流程概述里 |
| C4 | 块按 `int.from_bytes(block[0:4], "big")` 拆开。整块样例仍写 `填充值: 0x08 × 8`。 | s1 第 271、332 行 | source-report | ECB 分块 | 示例密钥不入卡 |
| C5 | 轮后 `L ^= self.P[16]`、`R ^= self.P[17]`。F 为 `F(x) = ((S[0][a] + S[1][b]) mod 2^32) XOR S[2][c]) + S[3][d]) mod 2^32`。 | s1 第 377、378、430 行 | source-report | 16 轮 Feistel | 括号是讲义原文 |
| C6 | OFB `无需填充,密文长度 = 明文长度`，先 `output_block = self._encrypt_block(output_block)`，解密 `return self.encrypt_ofb`。 | s1 第 539、637、645 行 | source-report | 讲义中的 OFB | 未跑解密 |
| C7 | 作者写实现 `和标准的有区别`。ECB 密文为 `b8498c7952e8a7946e70232f3c3d404a`，OFB 密文为 `64994f4c7aa4221e`。 | s1 第 75、502、666 行 | source-report | 讲义贴出的两组结果 | 差别没有写明，本轮未运行 |
