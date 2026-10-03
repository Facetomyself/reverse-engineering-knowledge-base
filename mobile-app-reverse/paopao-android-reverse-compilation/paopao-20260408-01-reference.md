---
schema_version: 2
id: paopao-20260408-android-rsa-markers-reference
document_type: reference
original_date: '2026-04-08'
archived_date: '2026-10-02'
scope:
  targets:
    - android-rsa
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260408-01.md#12-rsa-的核心特性"
    basis: source-report
  - id: s2
    ref: "./paopao-20260408-01.md#31-密钥生成流程"
    basis: source-report
  - id: s3
    ref: "./paopao-20260408-01.md#41-填充模式padding-schemes"
    basis: source-report
  - id: s4
    ref: "./paopao-20260408-01.md#42-pkcs-1-v15-填充结构"
    basis: source-report
  - id: s5
    ref: "./paopao-20260408-01.md#44-javaandroid-中的-rsa-实现"
    basis: source-report
  - id: s6
    ref: "./paopao-20260408-01.md#62-java-层特征字符串"
    basis: source-report
  - id: s7
    ref: "./paopao-20260408-01.md#63-nativeso层特征"
    basis: source-report
  - id: s8
    ref: "./paopao-20260408-01.md#64-数据特征识别"
    basis: source-report
relations:
  - type: derived_from
    target: "./paopao-20260408-01.md#62-java-层特征字符串"
tags:
  - android-rsa
  - source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s3, s4, s5, s6, s7, s8]
    basis: source-report
    limits: 字符串和长度是来源列出的识别标记，不是某个 App 的测量。不包含提取、挂钩或还原脚本。
---

# 安卓逆向笔记里用来认出 RSA 的标记

这张卡只回答：这篇笔记用哪些算法串、填充字节、公钥头和密文长度来认出 RSA，以及它如何写下 AndroidKeyStore 私钥的导出边界。数学推导、工具命令，以及后文的挂钩和还原脚本都不在卡里。

来源没有可公开定位的原文 URL。标记是作者的归纳。

<a id="parameters"></a>
## 识别标记

抓包时的长度启发式：

> 固定长度（如 256 字节）的密文

来源接着说，长度随明文变而且远大于 256 字节时，通常更像 AES。这只是该段的对照，不是判定器。

| 标记 | 来源原句里的含义 |
|---|---|
| 0x10001 或 65537 | 见到即可高度怀疑是 RSA。Native 特征重复同一常量 0x10001 |
| RSA/ECB/PKCS1Padding | 被标成最常见加密模式 |
| PKCS1Padding | 见到该字符串即可确认 PKCS#1 v1.5 |
| OAEPWithSHA-256AndMGF1Padding | OAEP 加密模式名 |
| SHA256withRSA | 被标成签名算法 |
| 00 02 / 00 01 | 加密填充与签名填充的前两字节 |
| 245 字节 | 2048 位、PKCS#1 v1.5 下明文上限 |
| MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A | 被写成 2048 位 X.509 公钥的 Base64 头 |
| 2048 位密文 | 256 字节，Base64 ~344 字符，来源标成最常见 |

AndroidKeyStore 的边界是单独一句，不是导出方法：

> 无法直接导出私钥

来源后文建议改去看使用密钥的业务调用。那一句没有展开成步骤，本卡也不补。

## 验证与限制

课堂用的小素数、JCA 示例代码、场景总表和 openssl 命令清单都没有新的识别字段。填充方案上的已知风险只在来源表里出现名字，这里不描述。长度「约 344 字符」没有误差范围。没有本地样本，也没有对当前 Android 默认变换做复核。
