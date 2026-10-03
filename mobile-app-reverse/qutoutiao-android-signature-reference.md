---
schema_version: 2
id: qutoutiao-android-signature-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [qutoutiao]
  client: android
  version: 3.10.98.000.0611.1144
  observed_at: unknown
sources:
  - id: s1
    ref: ./xfq-android-cases-compilation/xfq-20260311-01.md#正文
    basis: source-report
modules:
  - name: interfaces
    anchor: signer-interface
    sources: [s1]
    basis: source-report
    limits: 仅整理作者对该 APK 的 JNI/native 分析入口描述；未独立核实 JNI 注册、控制流或当前样本，也不构成 HTTP API、稳定 ABI 或可调用 SDK 合同。
  - name: parameters
    anchor: signer-components
    sources: [s1]
    basis: source-report
    limits: 仅记录来源作者对输出组件的概括，不给出字段映射、公式或测试向量；MD5 长度单位、a3/bArr 参数身份和伪代码均有歧义或损坏，不能据此实现算法或重放请求。
relations:
  - type: derived_from
    target: ./xfq-android-cases-compilation/xfq-20260311-01.md#正文
tags: [qutoutiao, android, JNI, native-signer, source-report]
---

# 趣头条 Android signer 组件边界（来源报告）

本卡只提供按 APK 版本检索的 JNI/native signer 入口和输出组件线索。来源文章中的账号、设备、随机输出、密钥派生中间值、密文及 byte-array 样例均未复制；下述内容不代表当前运行时验证或服务端接受。

<a id="signer-interface"></a>
## JNI / native 入口

来源作者描述以 unidbg 调用 Java 静态 JNI `secure` 入口，并沿 JNI 注册、native wrapper 与 `InnoSecure` 库追踪输出。这里仅记录作者报告的分析边界，不把 JNI 方法签名、寄存器/地址或控制流视为本轮独立核查结果。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 作者报告从该 APK 的 Java 静态 JNI `secure` 调用进入 native signer，并沿注册与 wrapper 路径追踪输出。 | s1，[正文](./xfq-android-cases-compilation/xfq-20260311-01.md#正文)、[JNI 调用与静态分析](./xfq-android-cases-compilation/xfq-20260311-01.md#1-unidbg主动调用) | source-report | 趣头条 Android `3.10.98.000.0611.1144` | 未核查二进制、JNI 注册或当前 APK；不构成 HTTP 接口或稳定 ABI。 |

<a id="signer-components"></a>
## 输出组件

作者将 native 输出描述为由分隔符拆分的多个部分，并分别关联到 UUID 相关的 MD5 十六进制文本、Base64 编码的键值段、随机输入参与的短混淆段，以及 JSON 密文段。末段的 AES-256-CBC 归因也是来源报告；本卡不复述构造公式、实际字段值或样例。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C2 | 来源作者报告 signer 输出包含上述几类组件，并将较长的 JSON 密文段归因为 AES-256-CBC。 | s1，[静态分析与输出划分](./xfq-android-cases-compilation/xfq-20260311-01.md#2-初步静态分析)、[组件分析](./xfq-android-cases-compilation/xfq-20260311-01.md#3-第一部分-32字节)、[密文分析](./xfq-android-cases-compilation/xfq-20260311-01.md#5-第三部分) | source-report | 趣头条 Android `3.10.98.000.0611.1144` | 来源对 MD5 长度的单位表述不一致，且 `a3` / `bArr` 参数身份未闭合；代码片段存在粘连。本卡不声明精确字节长度、组件到参数的映射、可运行公式、HTTP 请求归属或服务端验收。 |

## 未覆盖范围

没有 HTTP endpoint、请求/响应顺序、query/header/body 位置、风控决策链或可重放协议材料。算法实现、端到端 parity、运行时行为和 server acceptance 均未验证；仅来源 archive 中的高层结构适合检索。
