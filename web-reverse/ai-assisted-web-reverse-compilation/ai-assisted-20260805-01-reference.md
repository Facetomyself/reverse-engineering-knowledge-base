---
schema_version: 2
id: grok-desensitized-music-zzc-sign
document_type: reference
original_date: '2026-08-05'
archived_date: '2026-10-02'
scope:
  targets: [desensitized-music-zzc]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ai-assisted-20260805-01.md#签名整体结构"
    basis: source-report
  - id: s2
    ref: "./ai-assisted-20260805-01.md#请求体加密另一台vm和签名不是一回事"
    basis: source-report
  - id: s3
    ref: "./ai-assisted-20260805-01.md#版本演化哈希原语被整体替换过"
    basis: source-report
  - id: s4
    ref: "./ai-assisted-20260805-01.md#决定性发现响应解密是21字节固定xor不是aes"
    basis: source-report
  - id: s5
    ref: "./ai-assisted-20260805-01.md#站点的反调试手段"
    basis: source-report
  - id: s6
    ref: "./ai-assisted-20260805-01.md#落地验证"
    basis: source-report
  - id: s7
    ref: "./ai-assisted-20260805-01.md#两轮分析踩在一个版本差上"
    basis: source-report
  - id: s8
    ref: "./ai-assisted-20260805-01.md#环境"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s3, s4]
    basis: source-report
    limits: 取位下标、前缀 zzc/zzb、版本字节 98/99、AES-GCM 的 12 字节 IV 和 21 字节周期是来源原句。20 字节掩码、AES 密钥和 21 字节 pad 的内容都没有写出。
  - name: request-chain
    anchor: request-chain
    sources: [s2, s4, s8]
    basis: source-report
    limits: 平台名称已脱敏。签名 VM 和请求体 VM 是两台 switch 机。响应层不是请求层的 AES 逆运算。
  - name: risk-control
    anchor: risk-control
    sources: [s5, s7]
    basis: source-report
    limits: 用后即删、寄存器复用和版本字节是分析障碍，不是可执行的绕过步骤。
  - name: validation
    anchor: validation
    sources: [s6]
    basis: source-report
    limits: 259KB 与 399 字节、两边都是 HTTP 200，是作者自述。本次没有请求。
relations:
  - type: derived_from
    target: "./ai-assisted-20260805-01.md#某音乐平台的response加密强度约等于没加"
tags: [zzc, sha1, aes-gcm, source-report]
---

# 脱敏音乐接口的 zzc 签名与不对称响应

这张卡回答来源里那一个未点名的批量点播接口：sign 怎么从 SHA1 取位，请求体和响应体为什么不是同一套算法。近邻没有同目标卡片。依据停在 `source-report`。掩码和密钥不在正文里，不能据此算出 sign。

<a id="parameters"></a>
## 参数

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | sign = ('zzc' + map1(7) + middle + map2(8)).lower() | s1，第 66 行 | source-report | 前缀 zzc 的这一版 | 掩码未公开 |
| C2 | [23,14,6,36,16,7,19] | s1，第 71 行 | source-report | map1 | 同行还有 map2 的 [16,1,32,12,19,27,8,5] |
| C3 | 逐字节异或一段20字节掩码 | s1，第 66 行 | source-report | middle | 同行还写去掉尾部的=，以及去掉所有的/和+ |
| C4 | 83分支的大switch语句直接做分派 | s1，第 68 行 | source-report | 签名解释器 | 没有 opcode 表 |
| C5 | iv(12字节随机) + AES-GCM(密钥, iv, body明文) | s2，第 81 行 | source-report | 请求体 | 密钥未给出 |
| C6 | 前缀是zzb不是zzc | s3，第 89 行 | source-report | 旧版前缀 | 第 94 行另写 zzb版本这一位是十进制98 与 zzc版本变成99 |
| C7 | 周期数出来正好21字节 | s4，第 103 行 | source-report | 响应层 | 同行写这段pad和会话、密钥都没关系；pad 内容未写出 |

<a id="request-chain"></a>
## 请求链

第50行写 POST body 先 AES 再 base64，URL 另带时间戳、一个标识请求体加密方式的常量，还有 sign。sign 前缀 zzc 之后跟 37 到 39 个字符，总长 40 到 42。第83到84行写 Content-Type写的是text/plain，同一个脚本文件里一共装了两台自定义VM。第 43 行写响应是一段固定21字节的密钥流反复异或。第99行写换了几种常见的AES变体(不同分组模式、不同IV位置)也全部失败。

<a id="risk-control"></a>
## 反分析

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 签名函数用后即删 | s5，第 120 行 | source-report | 签名函数 | 第121行写常规按函数名下断点会直接扑空 |
| C9 | 批量请求复用运算寄存器 | s5，第 123 行 | source-report | 多子请求 | 第124行写同一组寄存器依次算完每一个 |
| C10 | 核心哈希包了一层VM | s5，第 126 行 | source-report | SHA1/MD5 常量仍可见 | 未给常量数值 |
| C11 | 字节码换成了zzc,版本标志字节从98变成99 | s7，第 112 行 | source-report | zzb 到 zzc | 旧版取位表不在这一节 |

第92行写哈希函数换了、掩码长度变了、取位的字符数量也不一样。先对版本字节，再谈算法。

<a id="validation"></a>
## 验证与限制

第 45 行写故意传错sign接口照样返回200，内容缩成几百字节。第131到132行把正确 sign 写成大约259KB，错误 sign 写成响应体缩水到399字节，同一个状态码。这是作者自述。

平台名、20 字节掩码、AES 密钥和 21 字节 pad 都不在正文里。取位下标不能单独复现 sign。没有失败出口和验收阈值，不能做成流程卡。
