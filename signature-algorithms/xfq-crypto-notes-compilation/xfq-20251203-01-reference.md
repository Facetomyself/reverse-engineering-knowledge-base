---
schema_version: 2
id: aes-block-modification-checkpoints
document_type: reference
original_date: '2025-12-03'
archived_date: '2026-10-02'
scope:
  targets:
    - aes
    - aes-128
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./xfq-20251203-01.md#4-魔改方向
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留轮数、列优先、密钥长度分界和魔改约束。S 盒全表和矩阵对不转写。演示口令不进入本卡。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 「加密成功」和期望密文都是作者自述。本轮没有运行。
relations:
  - type: derived_from
    target: ./xfq-20251203-01.md#4-魔改方向
tags:
  - aes
  - aes-128
  - source-report
---

# AES 分组对照时先看的点

这张卡只回答：来源如何数 AES-128 的轮密钥，状态矩阵按什么方向排，以及改 S 盒或 MixColumns 时来源要求同时改什么。它不是可运行实现。起点写明目标是按代码复现，不去解释设计原因。

近邻没有 `aes` 或 `aes-128` 的 parameters / validation。

<a id="parameters"></a>
## 轮结构与魔改约束

AES-128 来源写成 11 个轮密钥：1 个初始密钥加 10 轮，16 字节扩成 44 个 word。quote: AES加密需要11个轮密钥(1个初始密钥 + 10轮),我们需要把16字节密钥扩展成11 * 16,如果按照word来,就是44个字(每个字4字节)。扩展到整除 4 的 word 时，来源写 RotWord、SubWord，再把首字节异或 Rcon。quote: temp = RotWord(W[4n-1])。

16 字节排成 4×4，列优先。quote: AES 将 16 字节数据排列成 4×4 矩阵,使用列优先排列。明文须是 16 的倍数，缺几字节就填几个该值。quote: AES要求明文必须是16字节的倍数,不够就要填充。

轮次：第 0 轮只有轮密钥加。quote: AddRoundKey (第0轮:只有轮密钥加)。中间标准轮是 SubBytes、ShiftRows、MixColumns、AddRoundKey。quote: 标准轮(SubBytes → ShiftRows → MixColumns → AddRoundKey)。第 10 轮没有 MixColumns。quote: 第10轮 (最后一轮,除标准无MixColumns)。

三种密钥长度来源写成 128、192、256 位。quote: AES 支持 128位、192位、256位 三种密钥长度,分别对应 AES-128、AES-192、AES-256。AES-256 在 `i % 8 == 4` 时再做一次 SubWord。quote: elif i % 8 == 4:  # AES-256特有:第4个字也需要SubWord。相关密钥的一句话比较不单列成模块。

CBC 的 IV 必须是 16 字节。quote: 1. 长度: 必须等于块大小(16字节)。来源允许调用时传入；不传则声称生成随机 IV。quote: 1. IV 作为参数传入(如果不传则生成随机 IV)。固定 IV 被写成错误。quote: # ❌ 错误:使用固定 IV。填充验证失败时不要返回细节，这只是来源的防御句，本卡不写利用。

魔改约束有三条硬边界：

- S 盒不能只改加密表。quote: 改了S盒必须同时生成对应的逆S盒,否则解密会失败。
- Rcon 和 ShiftRows 的移位数来源认为可以换。具体新表没有定位到样本。
- MixColumns 必须在来源所说的域上可逆。quote: MixColumns矩阵不能随便改!必须在GF(2^8)域上可逆,否则解密会失败。来源建议直接用已核对过的矩阵对，不在本卡重贴。quote: 建议直接使用已验证的矩阵对。

<a id="validation"></a>
## 作者自述的对照

来源给出一条期望密文 `e5ca8fc48003012aa539cf0a41f7dc7f`。quote: e5ca8fc48003012aa539cf0a41f7dc7f。收尾写加密成功且与预期一致。quote: 加密成功!最终密文与预期一致。演示口令不转写。逐轮十进制矩阵是作者过程记录，本轮没有重算。

代码围栏粘连，不能执行。密钥长度不是 16、24、32 字节时，来源的统一接口直接拒绝，没有别的验收。
