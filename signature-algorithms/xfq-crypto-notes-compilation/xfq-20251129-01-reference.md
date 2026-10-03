---
schema_version: 2
id: des-ecb-modification-checkpoints
document_type: reference
original_date: '2025-11-29'
archived_date: '2026-10-02'
scope:
  targets:
    - des
    - 3des
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./xfq-20251129-01.md#51-魔改点
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留来源点名的块长、索引、合并顺序、填充和魔改位置。置换表与 S 盒全表不转写。粘连代码不能当实现。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 期望 hex 和标准库对照句都是作者自述。本轮没有运行。另一组样例的密钥和长输入不进入本卡。
relations:
  - type: derived_from
    target: ./xfq-20251129-01.md#51-魔改点
tags:
  - des
  - 3des
  - source-report
---

# DES / 3DES 对照时先看的点

这张卡只回答：来源在手写 DES 时把哪些点和标准表对不上，以及 3DES 密钥字节数怎么拆。它不是可运行实现，也不是某个 App 的签名卡。起点的目标是复现，不去解释为什么这样设计。

近邻没有 `des` 或 `3des` 的 parameters / validation。起点的 3DES 管线是另一目标，不覆盖这些对照点。

<a id="parameters"></a>
## 对照参数

密钥编排把 64 位收到 56 位。quote: 密钥从 64 位缩减到 56 位(去掉了8个校验位)。子密钥生成是 16 轮。quote: 2. 进行16轮循环生成16个子密钥。来源提醒置换表有时是 1-based，代码里要减 1。quote: 某些情况下会使用1-based,代码中需要全部减1(注意兼容性,特别是与标准表对照时)。

填充按 8 字节倍数，差 n 就填 n 个值为 n 的字节。quote: 如果差几位就填充 对应数字的字节。长度已经是 8 的倍数时仍填满 8 字节。quote: 即使长度是8的倍数也要填充完整的8字节。

16 轮之后合并成 `R16 + L16`，不是 `L16 + R16`。quote: 16轮后是 R16 + L16(不是 L16 + R16)。S 盒行取第一位和最后一位，列取中间 4 位。quote: 1)行索引:第一位和最后一位 组成一个二进制数,转10进制。全表不转写。

CBC 在来源里只提供保密性。quote: CBC只提供保密性,不提供完整性。IV 长度必须等于块大小，来源写成 8 字节。quote: 1. 长度必须等于块大小(8字节)。完整性来源写成结合 HMAC 或 AEAD。quote: 建议结合HMAC或使用AEAD模式(如AES-GCM)。填充是否合法被单独命名为风险，本卡不收利用步骤。CBC 代码只点了文件名。

魔改清单是位置，不是一个已定位样本。来源写置换表被改时，表内数字顺序会不同。quote: 原理: 修改各种置换表,改变比特位的重排规则。同节还点名 S 盒、左移表、C/D 与 L/R 顺序、填充、F 函数顺序、字节序、轮数、子密钥顺序、额外异或、密钥扩展和 ECB/CBC 混用。识别句是和标准表比较。quote: if PC_1 != STANDARD_PC_1:print("PC-1表被魔改了")。案例名没有参数，不能当成已定位样本。

3DES 来源按密钥字节数拆：24 字节拆成 3 个，或直接是 3 个 8 字节。quote: 逆向过程中会受到24字节的密钥,然后按规则拆分成3个;或者收到3个8字节的密钥。16 字节拆成 2 个，或直接是 2 个 8 字节。quote: 逆向过程中会受到16字节的密钥,然后按规则拆分成2个;或者收到2个8字节的密钥。加密公式在归档里被拆碎，本卡不补公式。代码只有文件名。

<a id="validation"></a>
## 作者自述的对照

来源用一组固定明文和密钥，把期望密文写成 `85e813540f0ab405fdf2e174492922f8`。quote: correct_cipher_hex = "85e813540f0ab405fdf2e174492922f8"。后文用标准库 ECB 再写同一句输出。quote: 应该输出: 85e813540f0ab405fdf2e174492922f8。两句都是作者自述。

中间日志点来源点了 PC-1、K1、IP、E 扩展、异或、S 盒和 P 盒。对不上时先看索引、字节序、填充和 R/L 顺序。bytes 版只说另有文件，没有代码，不能当验收。

完整类列表被行号和断行粘在一起，不能执行。另一组调用的密钥和长输入不转写。
