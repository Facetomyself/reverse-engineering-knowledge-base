---
schema_version: 2
id: aes-gcm-j0-ghash-layout
document_type: reference
original_date: '2026-03-18'
archived_date: '2026-10-02'
scope:
  targets: [aes-gcm]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260318-02.md#2-gcm-的完整流程-"
    basis: source-report
  - id: s2
    ref: "./xfq-20260318-02.md#3-ghashgcm-的认证核心-"
    basis: source-report
  - id: s3
    ref: "./xfq-20260318-02.md#4-代码测试数据分步解析-"
    basis: source-report
  - id: s4
    ref: "./xfq-20260318-02.md#5-解密流程先验证再解密-"
    basis: source-report
  - id: s5
    ref: "./xfq-20260318-02.md#7-逆向实战加密找什么解密找什么-"
    basis: source-report
  - id: s6
    ref: "./xfq-20260318-02.md#8-gcm-的魔改方向-"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s5]
    basis: source-report
    limits: 只整理作者写出的 12 字节 IV、J0、GHASH 拼接和 IV|密文|Tag 切分。不是某个客户端的抓包，也没有本轮重算。
  - name: validation
    anchor: validation
    sources: [s3]
    basis: source-report
    limits: H、密文、S 和 Tag 都是作者分步日志。作者称 NIST 用例通过，本轮没有重跑。
  - name: decision-flow
    anchor: decision-flow
    sources: [s4, s6]
    basis: source-report
    limits: 先验证再解密，以及九类魔改的观察点，都是作者的分支。没有失败后的停机步骤，不能当成流程卡。
relations:
  - type: derived_from
    target: "./xfq-20260318-02.md#aes-gcm-认证加密模式实现-"
tags: [aes-gcm, ghash, source-report]
---

# AES-GCM 的 J0、GHASH 与报文切分

这张卡回答作者如何摆 AES-GCM 的计数器、认证输入和线上三段报文，以及 Tag 对不上时作者往哪几类魔改看。target `aes-gcm` 的 parameters、validation、decision-flow 查询均为空。`xtime` 卡的目标是 GF(2^8)，不覆盖这里的 GF(2^128)。依据停在 `source-report`。

<a id="parameters"></a>
## J0、GHASH 与三段报文

作者把 12 字节 IV 定为规范建议长度。五步写成：H 是密钥加密全零块；J0 的原句是 `2 构造初始计数器 J0 = IV || 0x00000001`；明文从 J0 加 1 起做 CTR，并且只加最后 4 字节；GHASH 吃 AAD、密文和两边的比特长度；Tag 是 GHASH 结果再异或 AES(J0)。J0 本身不加密明文，作者的理由是那块 AES 输出已经用在 Tag 上。

GHASH 的域参数被写成 x^128 + x^7 + x^2 + x + 1，常数 R = 0xE1 左移 120。归档里的乘法函数语句粘连，本卡不把它当成可运行实现。

作者把常见报文写成前 12 字节 IV、中间密文、末尾 16 字节 Tag。同一行的原句是 `| IV (12 字节) | 密文 (N 字节) | Tag (16 字节) |`。加密侧作者点名的输入是 Key、12 字节 IV、AAD 和明文；解密侧再加密文和 Tag。这是讲义里的参数表，不是某次抓包。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 初始向量(GCM 规范强烈建议使用 12 字节) | s1 ./xfq-20260318-02.md:237 | source-report | 作者参数表里的 IV | 非 12 字节 IV 的 GHASH 派生作者只在魔改节提到 |
| C2 | 1 生成哈希子密钥 H = AES_K(0^128) | s1 ./xfq-20260318-02.md:247 | source-report | 作者五步的第 1 步 | 未独立加密全零块 |
| C3 | 2 构造初始计数器 J0 = IV | s1 ./xfq-20260318-02.md:249 | source-report | 12 字节 IV 的 J0 | 原句在 IV 后用两个竖线接上 0x00000001；作者把改成 0x00000002 或小端当成魔改 |
| C4 | 注意:J0 本身不用于加密明文!从 J0+1 开始递增计数器,只递增最后 4 字节。 | s1 ./xfq-20260318-02.md:252 | source-report | 作者的标准计数器 | 与上一篇整块 128 位加一不同 |
| C5 | 5 计算最终认证标签 Tag = S ⊕ AES_K(J0) | s1 ./xfq-20260318-02.md:258 | source-report | 作者的 Tag 合成 | S 的算法细节在 GHASH 节 |
| C6 | 不可约多项式为:x128 + x7 + x2 + x + 1(对应常数 R = 0xE1 << 120) | s2 ./xfq-20260318-02.md:324 | source-report | 作者写下的 GF(2^128) 常数 | 乘法示例语句粘连 |
| C7 | IV (12 字节) | s5 ./xfq-20260318-02.md:544 | source-report | 作者说的常见拼法 | 同一行还有密文和 Tag (16 字节)；不是某个 App 的报文 |

<a id="validation"></a>
## 作者的分步数字

作者用一条 8 字节明文和一段 AAD 打了分步日志：H、密文、GHASH 的 S，以及 S 异或 AES(J0) 得到的 Tag。同一节写解密成功为 True，并把密文首字节翻 1 bit 之后的结果写成认证失败、拒收。NIST SP 800-38D 的 Test Case 3 与 4 只被说成「验证通过」，没有贴出向量本身。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 1. 生成哈希子密钥 H: e021cf297de1a05a478260c923ad4795 | s3 ./xfq-20260318-02.md:370 | source-report | 作者这组样例的 H | 未重算 |
| C9 | 生成密文 (CT): 3dcc8198fea2674f | s3 ./xfq-20260318-02.md:382 | source-report | 作者这组样例的密文 | 未重算 |
| C10 | 4. GHASH 运算结果 S: 8b265774d5e816a0d2c610758df5a685 | s3 ./xfq-20260318-02.md:404 | source-report | 作者这组样例的 S | 未重算 |
| C11 | 6. S ⊕ AES_K(J0) = 最终认证标签 MAC: c549a32bac84320e941f298ca20e2783 | s3 ./xfq-20260318-02.md:412 | source-report | 作者这组样例的 Tag | 未重算 |

<a id="decision-flow"></a>
## 验 Tag 与魔改落点

标准顺序被写成：先按同样方式算出 Tag，不一致就丢弃、不解密，一致才做 CTR。作者另写了一句阅读捷径：只想看数据时可以不验 Tag，直接做 CTR 异或。这是作者的说法，本卡不把它扩成操作步骤。

魔改节把对不上的现象分成几支：CTR 能出明文但 Tag 错、又看不到成片的 0xE1 移位，作者判 GHASH 被换掉；0xE1 常数被换成别的不可约多项式，就要改还原脚本里的常数；J0 可能从 `0x00000001` 改成 `0x00000002`、改小端，或对 12 字节 IV 也走 GHASH。其余几支（H 不是加密全零、砍掉长度域、查表白盒、位序反过来、密钥流再异或一层、明文尾部多垫废数据）都只有特征描述，没有验收。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C12 | GCM 的解密顺序非常重要:必须先验证 Tag,再解密。 | s4 ./xfq-20260318-02.md:437 | source-report | 作者的标准解密顺序 | 没有失败出口步骤 |
| C13 | 可以跳过 Tag 验证,直接用 CTR 解密 | s5 ./xfq-20260318-02.md:539 | source-report | 作者说的只读捷径 | 未验证；不提供做法 |
| C14 | 若 CTR 能解出明文但 Tag 报错,检查生成 Tag 的收尾函数。若无大量的 0xE1 异或与移位操 | s6 ./xfq-20260318-02.md:569 | source-report | 作者对 GHASH 被替换的判据 | 原句在归档里被代码围栏截断 |
| C15 | 特征:将标准的 0xE100...00 替换为其他 128 位合法的不可约多项式(如 0x87)。 | s6 ./xfq-20260318-02.md:576 | source-report | 作者对约简常数的魔改 | 未看到具体二进制 |

## 验证与限制

- 模式对照表（ECB 到 GCM，以及 XTS、GCM-SIV、OCB、PCBC）只说明作者把 GCM 放在哪一类，不单独建模块。
- 测试字符串和「抓到的完整报文」这类占位不转写。
- 九类魔改没有前提、验收和失败出口，所以保持 reference，不建 procedure。
- 没有目标客户端，也没有本轮运行记录。
