---
schema_version: 2
id: paopao-20260327-des-identification
document_type: reference
original_date: '2026-03-27'
archived_date: '2026-10-02'
scope:
  targets: [des]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260327-01.md#12-核心参数"
    basis: source-report
  - id: s2
    ref: "./paopao-20260327-01.md#21-feistel-网络结构"
    basis: source-report
  - id: s3
    ref: "./paopao-20260327-01.md#22-初始置换-ipinitial-permutation"
    basis: source-report
  - id: s4
    ref: "./paopao-20260327-01.md#5-des-的工作模式"
    basis: source-report
  - id: s5
    ref: "./paopao-20260327-01.md#6-安卓平台中-des-的实现方式"
    basis: source-report
  - id: s6
    ref: "./paopao-20260327-01.md#7-安卓逆向中如何识别-des"
    basis: source-report
  - id: s7
    ref: "./paopao-20260327-01.md#83-常见还原陷阱"
    basis: source-report
  - id: s8
    ref: "./paopao-20260327-01.md#9-des-变种算法"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s3, s6]
    basis: source-report
    limits: 分组、有效密钥、轮数和常量前缀按作者的标准 DES 描述记录。前缀相同不能说明整张表没有被改。
  - name: interfaces
    anchor: interfaces
    sources: [s4, s5]
    basis: source-report
    limits: 只记录 Java transformation 字符串和 OpenSSL 导出名。不补某个 APK 的调用点。
  - name: decision-flow
    anchor: decision-flow
    sources: [s2, s6, s7, s8]
    basis: source-report
    limits: 逆序子密钥、字符串到常量再到动态观察，以及对不上时的分叉，都是作者的判断。没有用样本排除其他原因。
  - name: validation
    anchor: validation
    sources: [s7, s8]
    basis: source-report
    limits: 已知输入输出被写成金标准，但文中的十六进制标明要替换。本次没有对照。
relations:
  - type: derived_from
    target: "./paopao-20260327-01.md#7-安卓逆向中如何识别-des"
tags: [des, 3des, android, source-report]
---

# Android 上识别 DES 与 3DES 的常量与字符串

这张卡回答标准 DES 在作者叙述里有哪些固定参数和常量前缀、Java 与 OpenSSL 用什么字符串、以及结果对不上时作者先怀疑哪一类错误。示例密钥和密文不是样本。依据停在 `source-report`。近邻查询在 `des` 上没有已声明模块。

<a id="parameters"></a>
## 参数与常量前缀

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 明文分组是「64 bit（8 字节）」，密钥 64 bit 里有效 56 bit，外加 8 bit 奇偶校验，共 16 轮。 | s1，第 71–74 行 | source-report | 作者描述的标准 DES | 没有对某个库的实现逐字段核对。 |
| C2 | IP 表以「58, 50, 42, 34」开头；E 扩展表以「32, 1, 2, 3, 4, 5」开头。 | s3 与常量节，第 174、209 行 | source-report | 作者所称的标准表 | 只比对前缀会漏掉后半张魔改表。 |
| C3 | 密钥调度的左移位数序列写作「1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1」。 | s6，第 336 行 | source-report | 作者所称的标准调度 | 序列一旦被改，这条特征就不成立。 |
| C4 | 「DESKeySpec」被写成「只取前 8」字节，更长的输入会被忽略。 | s5，第 475–475 行 | source-report | 作者点名的 DESKeySpec | 不自动适用于 SecretKeySpec。 |

<a id="interfaces"></a>
## Java 与 OpenSSL 入口

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | ECB 的 Java 标识写作「DES/ECB/PKCS5Padding」，CBC 写作「DES/CBC/PKCS5Padding」。 | s4，第 373、384 行 | source-report | 作者给出的 javax.crypto 字符串 | 不是某个应用的引用位置。 |
| C6 | 不写模式和填充时，作者写默认是「DES/ECB/PKCS5Padding」。 | s5，第 462–463 行 | source-report | 作者对 Android Cipher 的说法 | 本次没有调用 getInstance。 |
| C7 | OpenSSL 路径被写成可以搜索导出函数名「DES_ecb_encrypt」。 | s5，第 504 行 | source-report | 作者描述的动态链接 OpenSSL | 静态链接并去掉符号后，这个名字不存在。 |

<a id="decision-flow"></a>
## 方向、模式和变种怎么分

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 子密钥「被逆序访问」，以及类似从 15 递减到 0 的循环，被写成解密线索。 | s2，第 132–134 行 | source-report | 作者描述的子密钥数组 | 其他解密写法不在这句里。 |
| C9 | 识别顺序被收成搜「DES」字符串、找 S 盒常量，再做动态观察。 | s6，第 753 行 | source-report | 作者的三步说明 | 动态观察的脚本没有运行。 |
| C10 | 「解密结果全是乱码」先看密钥或 IV；「工作模式搞错了」从第二个块起显现；「可能是 3DES」时看密钥是不是 16 或 24 字节；「IV 拼在密文前面」则结果偏移 8 字节。 | s7，第 853–860 行 | source-report | 作者的排查表 | 没有用反例证明这些是唯一原因。 |
| C11 | 算法字符串「DESede」且密钥 16 或 24 字节，被写成 3DES。S 盒结构仍是 4x16、值却不同，被写成魔改。 | s8，第 914、251 行 | source-report | 作者对 DESede 和魔改 S 盒的区分 | 2-Key 如何扩展成 24 字节只是作者对 Java 的说法。 |

<a id="validation"></a>
## 作者写的对照与本次限制

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C12 | 「用已知的输入输出对来验证还原结果」被写成确认还原的金标准。 | s7，第 864 行 | source-report | 作者提出的对照方法 | 同节十六进制标明要替换，本次没有对照。 |

附录里的整张 S 盒、弱密钥和 openssl 命令没有逐项复核。Hook 草稿只说明作者准备看算法名、mode、密钥和 IV，不作为已取得的材料。
