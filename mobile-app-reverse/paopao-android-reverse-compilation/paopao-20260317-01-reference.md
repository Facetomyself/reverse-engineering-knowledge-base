---
schema_version: 2
id: android-aes-identification-reference
document_type: reference
original_date: '2026-03-17'
archived_date: '2026-07-13'
scope:
  targets: [android-aes-identification]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260317-01.md#12-填充方式"
    basis: source-report
  - id: s2
    ref: "./paopao-20260317-01.md#七安卓逆向中识别-aes-算法"
    basis: source-report
  - id: s3
    ref: "./paopao-20260317-01.md#52-倒数两个列混淆之间发生故障对密文的影响"
    basis: source-report
  - id: s4
    ref: "./paopao-20260317-01.md#94-魔改-aescustom-s-box-aes"
    basis: source-report
  - id: s5
    ref: "./paopao-20260317-01.md#95-sm4类-aes-国密算法"
    basis: source-report
  - id: s6
    ref: "./paopao-20260317-01.md#91-按密钥长度aes-128--aes-192--aes-256"
    basis: source-report
  - id: s7
    ref: "./paopao-20260317-01.md#92-按工作模式ecb--cbc--cfb--ofb--ctr--gcm"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s5, s6, s7]
    basis: source-report
    limits: 填充、轮数、模式字符串和公开常量来自讲义。xtime 的乘 2 定义已有独立卡，这里只保留 0x1B 作为识别常数。不收录讲义里的示例密钥。
  - name: decision-flow
    anchor: decision-flow
    sources: [s2, s3, s6]
    basis: source-report
    limits: 识别顺序和 DFA 字节图是来源的教学路径。故障注入次数和候选个数没有在本轮复算，也没有验收或失败出口。
  - name: validation
    anchor: validation
    sources: [s4]
    basis: source-report
    limits: 全排列只说明 256 字节表像不像 S 盒，不能单独证明整段是 AES。
relations:
  - type: derived_from
    target: "./paopao-20260317-01.md#七安卓逆向中识别-aes-算法"
tags: [aes, sm4, dfa, source-report]
---

# 安卓逆向里如何识别 AES、模式和近邻算法

这张卡用于把一段 Android 加密实现归到 AES-128/192/256、某种工作模式、白盒或魔改 S 盒，或者把它和 SM4 分开。来源是 [AES 讲义的安卓识别章](./paopao-20260317-01.md#七安卓逆向中识别-aes-算法)。`xtime in GF(2^8) / AES-style finite-field arithmetic` 只覆盖乘 2 和 0x1B 约简，不覆盖识别面、模式字符串、DFA 字节图和 SM4。

来源有识别步骤和 DFA 的五步叙述，但没有写成可观察的验收，也没有失败出口，所以不是 procedure。依据保持 source-report。

<a id="parameters"></a>
## 长度、填充、模式和常量

讲义以 AES-128 为主：16 字节密钥、10 轮。AES-192 是 12 轮，AES-256 是 14 轮。来源写 AES-128 任意一轮轮密钥可逆推主密钥，AES-192 要一轮半，AES-256 要两轮。

块长正好是 16 的整数倍时，除 NoPadding 外都会再补一整块。PKCS5 与 PKCS7 在 16 字节块上被写成相同：填充字节的值等于填充长度。

模式字符串是检索键。ECB 无 IV。CBC 的常见串是 `AES/CBC/PKCS5Padding`，并有 16 字节 IV。CTR 的常见串是 `AES/CTR/NoPadding`。GCM 的常见串是 `AES/GCM/NoPadding`，参数类型是 `GCMParameterSpec`，密文后有 16 字节 Tag。

Native 识别常量：S 盒首行 `63 7C 77 7B F2 6B 6F C5 30 01 67 2B FE D7 AB 76`，逆 S 盒起始 `52 09 6A D5`，Rcon 在速查表里从 `01` 起，正文另一处 Rcon 列表以 `00` 起。列混淆约简常数是 `0x1B`。乘 2 的定义不在本卡展开。

SM4 块也是 16 字节，但只有 128 位密钥、32 轮，S 盒起始是 `D6 90 E9 FE CC`，没有 AES 的 Rcon。Java 字符串可以是 `SM4` 或 `SM4/CBC/PKCS5Padding`。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 整块明文除 NoPadding 外会再补 16 字节 | `除了 NoPadding 之外，其他填充方法都会在数据尾部额外添加一个 16 字节块` | s1 ./paopao-20260317-01.md:78 | source-report | 只谈块对齐的这一句 |
| C2 | PKCS5/PKCS7 的填充字节等于填充长度 | `每个补充字节的值等于补充的字节数` | s1 ./paopao-20260317-01.md:86 | source-report | 同节写两者在 16 字节块上一致 |
| C3 | 标准 S 盒首行 | `63 7C 77 7B F2 6B 6F C5 30 01 67 2B FE D7 AB 76` | s2 ./paopao-20260317-01.md:587 | source-report | 公开常量，不是某个 App 的密钥 |
| C4 | 速查表里的 Rcon 从 01 开始 | `01 02 04 08 10 20 40 80 1B 36` | s2 ./paopao-20260317-01.md:722 | source-report | 前文列表多一个前导 00，两处不一致 |
| C5 | 用轮数区分三种 AES | `10 轮为 AES-128，12 轮为 AES-192，14 轮为 AES-256` | s6 ./paopao-20260317-01.md:901 | source-report | 魔改轮数会破坏这条 |
| C6 | ECB 的模式串没有 IV | `"AES/ECB/..."` | s7 ./paopao-20260317-01.md:921 | source-report | 省略号是来源的写法 |
| C7 | GCM 使用 GCMParameterSpec | `GCMParameterSpec` | s7 ./paopao-20260317-01.md:967 | source-report | 同句还写了 AES/GCM/NoPadding |
| C8 | SM4 的 S 盒起始不同于 AES | `D6 90 E9 FE CC` | s5 ./paopao-20260317-01.md:1081 | source-report | 完整首行在后一代码块 |

<a id="decision-flow"></a>
## 识别顺序和故障窗口

Java 层先搜 `Cipher.getInstance("AES")`、`SecretKeySpec` 和 `IvParameterSpec`。字符串被拼接或反射时，来源改走 Hook `Cipher.getInstance`、`Cipher.init` 和 `doFinal`。Native 层接着搜 S 盒、Rcon、`0x1B`，以及 `AES_set_encrypt_key`、`AES_encrypt`、`EVP_EncryptInit_ex`。白盒被写成密钥已经并进查找表，标准 S 盒可能不出现。

轮密钥逆推：AES-128 一轮即可，192 要 1.5 轮，256 要 2 轮。DFA 要求故障落在倒数两次 MixColumns 之间，否则 16 字节全变或只变 1 字节。四列故障对应的密文字节是固定的四组。来源称 4 列各 2 次、共 8 次注入可以在最优情况下还原末轮密钥。这不是本轮做出的结果。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C9 | Java 识别从 Cipher.getInstance 的算法串开始 | `Cipher.getInstance("AES")` | s2 ./paopao-20260317-01.md:528 | source-report | 下一行才是 CBC/PKCS5 串 |
| C10 | AES-128 一轮轮密钥即可逆推主密钥 | `AES-128：任意 1 轮轮密钥即可逆推主密钥` | s6 ./paopao-20260317-01.md:905 | source-report | 192/256 的句在随后两行 |
| C11 | 第 1 列故障影响密文字节 1、8、11、14 | `字节 1、8、11、14` | s3 ./paopao-20260317-01.md:417 | source-report | 其余三列在 418–420 行 |
| C12 | 白盒把密钥融进表，不能直接拆出 | `密钥已融入表中，无法分离` | s2 ./paopao-20260317-01.md:1004 | source-report | 没有具体 App 的表 |

<a id="validation"></a>
## 魔改 S 盒的全排列检查

标准 S 盒搜不到时，来源改为找 256 字节表，并检查 `0` 到 `255` 是否各出现一次。通过只说明它像一张替换表。SM4 的 S 盒也被写成满足同一性质，所以全排列不能把 SM4 判成魔改 AES，还要看 32 轮和起始字节。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C13 | 疑似 S 盒要检查 0–255 各出现一次 | `每个 0-255 恰好出现一次` | s4 ./paopao-20260317-01.md:1051 | source-report | 随后的函数只比较排序结果，本轮未跑 |

## 验证与限制

不替代 xtime 卡，也不把讲义示例密钥当成某个产品的提取结果。Rcon 是否含前导 `00` 在正文两处不一致。DFA 的候选集合个数只是作者演算。白盒「GB 级别查找表」没有样本。没有运行记录。
