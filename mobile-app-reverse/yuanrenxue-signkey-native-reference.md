---
schema_version: 2
id: mobile-app-reverse-yuanrenxue-signkey-native-reference
document_type: reference
original_date: '2020-02-20'
archived_date: '2026-10-02'
scope:
  targets: [unknown]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200220-01.md#reference-extraction-106
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 字段角色和排序拼接来自来源报告；编码、null/empty、转义、重复键、完整输入和 key 派生均未闭合。
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 仅整理 Java 到 Native 的动态 JNI 注册边界；没有 APK/SO、ABI、注册表地址或当前函数原型的独立证据。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅整理来源作者报告的观察链；Hook、摘要比较和服务端说法均未在本轮重跑，不提供可运行 signer。
relations:
  - type: derived_from
    target: ./yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200220-01.md#reference-extraction-106
tags: [signKey, signKeyV1, MD5, HMAC-SHA256, JNI, RegisterNatives, Frida, source-report]
---

# 猿人学 signKey / Native 参考

这是一张安全文本 reference，只整理匿名 Android App 来源报告中的字段角色、参数规范化和 Java/Native 边界。原文中的手机号、设备/地理/请求样值、摘要输出、Native 指针/偏移、salt/key 和截图均不进入本卡；它不构成当前目标协议或可运行签名器。

<a id="parameters"></a>
## 字段与规范化边界

来源报告将 `signKey` 与 `signKeyV1` 视为两条不同签名输出，并将 `t`、设备相关 trace 关系、分页和游标字段与固定请求字段区分开。报告称较新的签名输入来自 `formatQueryParaMap` 的返回值，但没有闭合完整请求合同。

`formatQueryParaMap` 的来源描述是：按 key 排序，排除 `functionId`，再把剩余 value 用 `&` 拼接。这里仅保留结构，不补写 key、value、编码、null/empty、转义、重复键或盐值派生规则；排序发生在签名输入侧，也不自动等于线上请求顺序。

| 结论 | 来源与边界 | basis |
|---|---|---|
| 两个签名字段由不同 Java 方法进入 Native | s1，Java 参数组装段 | source-report |
| `formatQueryParaMap` 产生较新签名的上游输入 | s1，参数组装与规范化段 | source-report |
| 排序/排除字段/拼接的具体实现如上 | s1，`formatQueryParaMap` 段 | source-report |

<a id="interfaces"></a>
## Java 到 Native 的动态 JNI 链

来源报告将 Java 方法 `k` / `k2` 与 Native 方法 `gk` / `gk2` 关联，并描述了从 `JNI_OnLoad` 进入 `RegisterNatives` 表的定位方式：表中包含 Java 方法名、JNI 字段描述符、Native 函数名和方法数量。该链解释了为什么导出区找不到 Java 风格静态 JNI 名称时，仍可沿动态注册表找函数；不包含目标 SO 的地址、偏移或 ABI 结论。

Native 调用边界需区分 JNI 框架参数和 Java 层方法参数。来源报告提醒 `JNIEnv` 与 class/object 位于 Java 参数之前，但 IDA 的类型推断可能不完整；这只是审阅和 Hook 时的结构提醒，不是当前二进制函数原型。

<a id="request-chain"></a>
## 观察链与算法边界

来源报告的观察链可压缩为：抓取两次请求并比较字段变化 → 在 Java 层定位参数组装 → 观察 `formatQueryParaMap` 输入/输出 → 沿动态 JNI 注册找到 Native 函数 → 在 MD5 的数据处理边界和 HMAC-SHA256 的输入/长度/密钥长度边界观察签名材料。这个顺序用于定位生产者，不等于可复现流程。

报告将第一条输出描述为 MD5 路径，将第二条输出描述为 HMAC-SHA256 路径，并提到后者存在 Java 基础 key、字符变换、尾部取 key 等未闭合步骤。没有完整编码、key 派生、测试向量或独立摘要回执，因此不提供公式、Hook 偏移或 Python signer。

## 验证与限制

本卡全部模块为 `source-report`，scope 与 source completeness 保持 `unknown`。本轮没有 APK/DEX/SO、设备、IDA、Frida、网络请求、local parity 或服务端验收；原文 14 张外部截图未做像素审查，视觉隐私限制仍归属于来源 archive。原文关于某字段未被服务端校验的说法没有 response receipt，只能作为未证实的来源断言，不能升级为 `server-accepted`、风控规则或通用绕过结论。
