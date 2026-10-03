---
schema_version: 2
id: twofish-ecb-round-layout
document_type: reference
original_date: '2026-02-13'
archived_date: '2026-10-02'
scope:
  targets: [Twofish]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./xfq-20260213-01.md#4-16-轮-feistel-网络
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留讲义写明的端序、两套约化常数、白化和一轮不对称移位。Q 表与 RS 矩阵数值不在正文。
  - name: validation
    anchor: boundaries
    sources: [s1]
    basis: source-report
    limits: 密文和解密成功是作者自述。本轮没有运行这段 Python，也不把结尾的“很多大厂”当成已定位产品。
relations:
  - type: derived_from
    target: ./xfq-20260213-01.md#4-16-轮-feistel-网络
tags: [twofish, mds, feistel, source-report]
---

# Twofish 的小端四路 Feistel

这份参考卡回答：讲义里的 Twofish 怎样把密钥拆成 Me/Mo，RS 与 MDS 各用哪个约化常数，白化吃哪一组子密钥，以及一轮里两路移位为什么不对称。它不是可运行实现。已有的 xtime 卡只覆盖 AES 乘 2 与 0x1B，不覆盖这里的 0x4D 与 0x69。来源是 [Twofish 实现讲义](./xfq-20260213-01.md#4-16-轮-feistel-网络)。

<a id="parameters"></a>
## 参数

参数表写密钥 `128/192/256 位`，分组 `128 位 (16 字节)`，`16 轮`，结构 `Feistel 网络 + MDS + PHT`。密钥扩展要得到 `40 个子密钥 + 4 个密钥依赖的 S-box`。

密钥 `将密钥按 小端序 转成 32 位字`，代码是 `int.from_bytes(key[i:i+4], 'little')`，再分成偶数组 Me 和奇数组 Mo。RS 与 MDS 分开约化：`约化常数 0x4D`，`约化常数 0x69`。S 盒密钥顺序被写成 `S[k-1]...S[0]`。贴出的 h 函数注释只标了 `128-bit key` 的两层 q 置换。子密钥用 `rho = 0x01010101`，合并式是 `K[2i] = A + B` 与 `K[2i+1] = ROL(A + 2B, 9)`。四个 S 盒 `内容取决于密钥`。

填充块长是 `block_size: int = 16`。块拆成 `int.from_bytes(block[i:i+4], 'little')`。白化是 `明文 ⊕ K[0..3](输入白化)` 和 `结果 ⊕ K[4..7](输出白化)`。16 轮之后有一行 `撤销最后一次交换`。

讲义把结构称为 `4 路 Feistel(R[0]~R[3])`。文字式写 `R[2] = ROR(R[2] ⊕ T0, 1)` 且 `先异或,再右移1位`，`R[3] = ROL(R[3], 1) ⊕ T1` 且 `先左移1位,再异或`。F 里 `R1 先左移8位`，子密钥下标是 `self.K[8 + 2*r]` 与 `self.K[9 + 2*r]`。g 函数是 `self.S[i][b[i]]` 再做 MDS。贴出的 MDS 首行是 `[0x01, 0xEF, 0x5B, 0x5B]`。域乘法溢出时 `a ^= 0x69`。

<a id="boundaries"></a>
## 验证与限制

讲义给出 `密文(hex): afb68c0269659fc7230cffbc24ed150c`，并写 `解密成功: True`。这是作者贴出的结果。Q0/Q1 表和 RS 矩阵的数值不在正文，h 函数没有把 192/256 位的层数展开成与 128 位同等的代码。结尾只说很多实现会使用或参考 Twofish，没有点名产品。本轮没有运行这段 Python。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 密钥 `128/192/256 位`，分组 `128 位 (16 字节)`，结构 `Feistel 网络 + MDS + PHT`。 | s1 第 67、69、73 行 | source-report | 讲义参数表 | 未对照论文逐项 |
| C2 | 密钥按 `小端序` 拆字，代码为 `int.from_bytes(key[i:i+4], 'little')`。 | s1 第 79、85 行 | source-report | Me/Mo | 示例密钥不入卡 |
| C3 | RS `约化常数 0x4D`，MDS `约化常数 0x69`。S 盒密钥顺序是 `S[k-1]...S[0]`。 | s1 第 136、137、154 行 | source-report | 两套约化 | 不是 AES 的 0x1B；RS 矩阵数值不在正文 |
| C4 | 子密钥 `rho = 0x01010101`，`K[2i] = A + B`，`K[2i+1] = ROL(A + 2B, 9)`。 | s1 第 200、211、212 行 | source-report | 40 个子密钥的合并式 | h 的注释只写了 `128-bit key` |
| C5 | 输入白化是 `明文 ⊕ K[0..3]`，输出白化是 `结果 ⊕ K[4..7]`，轮后 `撤销最后一次交换`。 | s1 第 285、286、302 行 | source-report | 单块加密 | 未重算白化 |
| C6 | `先异或,再右移1位` 对 R[2]，`先左移1位,再异或` 对 R[3]。`R1 先左移8位`。 | s1 第 327、328、339 行 | source-report | 一轮 F | 未单步核对 |
| C7 | MDS 首行 `[0x01, 0xEF, 0x5B, 0x5B]`，溢出 `a ^= 0x69`。 | s1 第 384、408 行 | source-report | g 函数的 MDS | Q 表不在正文 |
| C8 | 讲义密文是 `afb68c0269659fc7230cffbc24ed150c`，并写 `解密成功: True`。 | s1 第 460、461 行 | source-report | 作者贴出的一组 ECB 结果 | 本轮未运行 |
