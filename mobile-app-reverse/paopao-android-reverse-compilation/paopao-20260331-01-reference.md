---
schema_version: 2
id: paopao-20260331-ssl-pinning-recognition
document_type: reference
original_date: '2026-03-31'
archived_date: '2026-10-02'
scope:
  targets: [ssl-pinning]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260331-01.md#前言"
    basis: source-report
  - id: s2
    ref: "./paopao-20260331-01.md#11-标准-tls-握手-vs-ssl-pinning"
    basis: source-report
  - id: s3
    ref: "./paopao-20260331-01.md#12-pin-的对象"
    basis: source-report
  - id: s4
    ref: "./paopao-20260331-01.md#二抓包环境准备"
    basis: source-report
  - id: s5
    ref: "./paopao-20260331-01.md#41-network-security-configuration"
    basis: source-report
  - id: s6
    ref: "./paopao-20260331-01.md#42-okhttp-certificatepinner"
    basis: source-report
  - id: s7
    ref: "./paopao-20260331-01.md#四针对各种-ssl-pinning-实现的绕过方案"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2]
    basis: source-report
    limits: 症状和「证书链之外还要匹配预期 pin」是作者的定义。同一条握手异常也可以有别的原因。
  - name: parameters
    anchor: parameters
    sources: [s3, s4]
    basis: source-report
    limits: 三种 pin 对象和 Android 7 的用户 CA 边界按作者叙述记录。没有 pin 原值，也不记录安装系统证书或转走流量的做法。
  - name: interfaces
    anchor: interfaces
    sources: [s5, s6, s7]
    basis: source-report
    limits: 只记录配置文件、OkHttp 类名和嵌入证书的常见位置。不记录替换校验、导出客户端证书或隐藏插桩进程。
relations:
  - type: derived_from
    target: "./paopao-20260331-01.md#一ssl-pinning-原理回顾"
tags: [ssl-pinning, android, source-report]
---

# Android SSL Pinning 的症状、pin 对象和声明位置

这张卡只回答作者如何描述证书锁定的现象、pin 锁的是什么，以及 Network Security Config、OkHttp 和嵌入证书各自写在哪里。后文的替换校验、代理重定向、客户端证书导出和隐藏插桩进程不进入本卡。依据停在 `source-report`。近邻查询在 `ssl-pinning` 上没有已声明模块。

<a id="risk-control"></a>
## 现象和比证书链多出来的校验

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 作者把 Logcat 里的「Certificate pinning failure」，以及网络错误、CONNECT 不能解密和闪退，写成证书锁定的症状。 | s1，第 49–54 行 | source-report | 作者列举的抓包现象 | 没有对应某一次握手日志。 |
| C2 | 「标准 TLS 只关心"证书链是否可信"」，pinning 还要求证书或公钥是预期的那个。 | s2，第 79–79 行 | source-report | 作者对两种校验的对照 | 没有证书样本。 |

<a id="parameters"></a>
## pin 对象和平台信任边界

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C3 | 整张证书比对 DER；公钥比对「SubjectPublicKeyInfo (SPKI)」；哈希是「比对公钥的 SHA-256 哈希值」。作者写现代实现多用公钥哈希。 | s3，第 88–92 行 | source-report | 作者的三行对照 | 没有从 APK 取出任何 pin。 |
| C4 | 「应用默认不信任用户安装的 CA 证书」从 Android 7.0（API 24）写起。 | s4，第 148 行 | source-report | 作者对平台默认值的说法 | 只保留信任边界，不保留安装系统证书的做法。 |

<a id="interfaces"></a>
## 声明位置

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | Network Security Config 被写成 `res/xml/network_security_config.xml` 中的 pin-set，manifest 声明 networkSecurityConfig。 | s5，第 309–310 行 | source-report | 作者给出的常规资源名 | 应用可以改资源名。示例域名不是目标。 |
| C6 | OkHttp 特征是「okhttp3.CertificatePinner」；pin 文本的「sha256/ 前缀是 OkHttp 特有的」。 | s6，第 402、411 行 | source-report | 作者描述的 OkHttp 3 类名和 pin 文本 | 混淆后类名会变。不记录如何跳过 check。 |
| C7 | 嵌入证书被写成出现在 assets 或 res/raw，扩展名包括 cer、pem、bks（「BouncyCastle KeyStore」）和 p12。 | s7，第 642 行 | source-report | 作者列出的文件位置 | 扩展名不说明文件里是否有私钥。 |

Native 库名、WebView 和第三方库只在后文作为替换目标出现，本卡不把那些替换写成接口。排错表也没有一次闭合的抓包验收，所以不建流程。
