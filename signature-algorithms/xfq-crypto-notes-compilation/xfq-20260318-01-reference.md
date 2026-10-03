---
schema_version: 2
id: aes-ctr-counter-block-layout
document_type: reference
original_date: '2026-03-18'
archived_date: '2026-10-02'
scope:
  targets: [aes-ctr]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260318-01.md#2-ctr-模式的核心结构彻底搞懂-noncecounter-与-iv-"
    basis: source-report
  - id: s2
    ref: "./xfq-20260318-01.md#3-代码测试数据-"
    basis: source-report
  - id: s3
    ref: "./xfq-20260318-01.md#4-国际标杆校验nist-sp-800-38a-官方测试向量-"
    basis: source-report
  - id: s4
    ref: "./xfq-20260318-01.md#5-ctr-模式的致命弱点-"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2]
    basis: source-report
    limits: 只保留作者对 16 字节计数器块、Nonce/Counter 切分和整块大端自增的写法。没有目标样本，也没有本轮重算。
  - name: validation
    anchor: validation
    sources: [s2, s3, s4]
    basis: source-report
    limits: 密钥流、密文和 NIST 前 16 字节都是作者日志里的数字。本轮没有重跑，不能把作者写下的通过当成独立核对。
relations:
  - type: derived_from
    target: "./xfq-20260318-01.md#aes-的-ctr计数器模式实现-"
tags: [aes-ctr, counter-block, source-report]
---

# AES-CTR 计数器块切分与整块自增

这张卡回答：CTR 送进 AES 的那一块有多长、Nonce 和 Counter 怎么切、作者这篇讲义又把整块当成什么来加一。近邻查询里 target `aes-ctr` 的 parameters 与 validation 都没有已有卡片。`xtime` 那张卡是 GF(2^8) 乘 2，不覆盖这里。依据停在 `source-report`。

<a id="parameters"></a>
## 计数器块与 IV 叫法

作者把送进 AES 的输入固定成 16 字节，并叫做 Counter Block。主流协议多把这 16 字节切成 12 字节 Nonce 加 4 字节 Counter。这篇讲义自己的代码不这么切：外部传入完整 16 字节，当成一个 128 位大端整数，每块加 1。作者说这和 crypto-js 默认的 16 字节初始块同一路，并认为仍落在 NIST SP 800-38A 允许实现者自定切分的范围内。

同一句话里的 IV 粒度会变：作者把 OpenSSL / Java 的 IV 记成完整 16 字节初始块，把 PyCryptodome 的 IV 记成仅 Nonce（默认 8 字节），把 RFC 3686 的 IV 记成中间 8 字节。密文仍是密钥流异或明文，所以作者把 CTR 收成「用 ECB 加密计数器，再异或明文」。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | AES 是一个分组密码,无论什么模式,它每次只吃 16 字节(128 bit) 的输入。在 CTR 模式中,这个 16 字节的输入叫做 Counter Block(计数器块)。 | s1 ./xfq-20260318-01.md:89 | source-report | 作者对 CTR 输入宽度的表述 | 未对照某一版 NIST 正文 |
| C2 | 当今主流标准几乎都选择了 12 + 4 的切法(12 字节 Nonce + 4 字节 Counter) | s1 ./xfq-20260318-01.md:136 | source-report | 作者列出的 GCM、IPsec、SRTP 切分 | 表是讲义转述，不是协议摘录 |
| C3 | 我们采用的是传入16字节的形式,和前端加密库是一样的(cyberchef背后用的库crypto-js 默认就是16字节) | s1 ./xfq-20260318-01.md:160 | source-report | 这篇讲义点名的 crypto-js 默认 | 未打开该库源码 |
| C4 | 每加密完一块,就让这个 128 位整数 +1,转回 16 字节后再喂给 AES。 | s1 ./xfq-20260318-01.md:164 | source-report | 作者这套整块自增 | 不代表 12+4 实现 |
| C5 | 一句话总结 CTR 的本质:用 ECB 模式加密"计数器"得到伪随机密钥流,再拿密钥流异或明文得到密文。 | s2 ./xfq-20260318-01.md:237 | source-report | 作者对 CTR 与 ECB 关系的口诀 | 只在计数器不重复时作者才称其安全 |

<a id="validation"></a>
## 作者给出的对照数字

作者用 8 字节明文走第 0 块，日志里的密钥流和截断后的密文如下。同一节声称用 ECB 加密同一计数器块会得到同一条密钥流。NIST 一节只贴了 F.5.1 前 16 字节的预期和实际，并写「验证通过」。这些都是作者日志，不是本轮重算。

文末把比特翻转写成 CTR 的边界：密文是异或，改密文比特会改出明文，解密端看不出来。作者因此把纯 CTR 收束到下一篇的认证模式，这里没有验收步骤。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 生成的密钥流(hex): fe648896b6724c415b539958a237d8fd | s2 ./xfq-20260318-01.md:203 | source-report | 作者第 0 块日志 | 未重算 AES |
| C7 | 密文块(hex): 860de9f9d0172226 | s2 ./xfq-20260318-01.md:224 | source-report | 作者截取的前 8 字节 | 未重算异或 |
| C8 | 预期输出(前16): 874d6191b620e3261bef6864990db6ce | s3 ./xfq-20260318-01.md:262 | source-report | 作者贴出的 F.5.1 前 16 字节 | 只看到作者写的预期与实际相同 |
| C9 | 比特翻转攻击(Bit-flipping attack) | s4 ./xfq-20260318-01.md:269 | source-report | 作者对无认证 CTR 的限制 | 没有具体报文样本 |

## 验证与限制

- 讲义点名 `03-aes_ctr.py`，正文没有可单独运行的完整脚本。
- 测试口令字符串不转写；只保留作者日志中的密钥流、密文和 NIST 前 16 字节。
- 12+4 与整块加一是两套计数器。看到 16 字节 IV 不能直接套 GCM 的 12 字节切法。
- 没有目标、版本或本轮运行记录。作者写下的「验证通过」保持 `source-report`。
