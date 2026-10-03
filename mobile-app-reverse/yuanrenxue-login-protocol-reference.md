---
schema_version: 2
id: mobile-app-reverse-yuanrenxue-login-protocol-reference
document_type: reference
scope:
  targets: [unknown]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200524-01.md#reference-extraction-101
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 来源称 `securitykey` 由参数集合拼接后摘要得到；键顺序、空值、编码和完整请求范围未闭合。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅整理静态定位与运行时类名校正边界，不构成脱壳、Hook 或登录 procedure。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 来源记载的 Hook 输出与抓包比较未提供原始日志；本轮未做 APK、设备、parity 或服务端验收。
relations:
  - type: derived_from
    target: ./yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200524-01.md#reference-extraction-101
tags:
  - android
  - parameters
  - encryption
  - ClassLoader
  - source-report
original_date: '2020-05-24'
archived_date: '2026-10-02'
---

# Android 登录参数定位边界参考

这是一张匿名目标的窄范围 source-report 参考卡，只保留字段定位、变换标签和类加载边界。来源中的手机号、设备/伪造标识、地理字段、摘要值、密码材料、截图和外部图片不复制到本卡。

<a id="parameters"></a>
## 参数机制

来源报告称，抓包对比后将登录请求中的 `securitykey` 单独列为待分析字段，并沿参数容器追到一个以分隔符拼接参数、再调用 MD5 helper 的路径。这个描述能帮助建立“字段 → 参数集合 → 摘要 helper”的定位关系，但不能生成字节级 signer：来源没有闭合 map 迭代顺序、键筛选、空值处理、转义、字符编码或所有接口是否共用同一路径。

<a id="encryption"></a>
## 密码变换边界

来源报告将 `password` 的 helper 标为 `AES/CBC/PKCS5Padding`，并称其结果与抓包字段相符。key、IV、明文编码、输出编码、调用参数和测试向量均未进入来源 archive 可复用边界，因此这里不提供公式、样值或可运行实现，也不把“相符”升级为本地 parity 或 server acceptance。

<a id="request-chain"></a>
## 定位与类加载链

来源叙述的静态到动态路径是：抓包字段定位 → dump 后的 DEX 搜索参数名 → 沿参数构造与 helper 引用追踪 → 面对加壳/MultiDex 时等待目标类经 `ClassLoader` 加载 → 用运行时方法追踪纠正反编译得到的类/方法名 → 再观察 Hook 参数和返回值。它是历史分析叙述，不是适用于当前 App 的完整 Hook 操作流程。

<a id="validation"></a>
## 证据边界

来源报告记载 Hook 参数/返回值与抓包字段的比较结果，但原始 trace、类加载器身份、DEX/SO、请求响应和测试样本没有随 archive 提供。本轮也未运行 APK、设备、Frida/Xposed、代理、Hook、parity 或当前服务；29 个外部截图引用的像素未审查，本卡不做任何截图提取。

## 来源与限制

完整来源保留于 [`yuanrenxue-app-20200524-01.md`](./yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200524-01.md)。本卡的四个模块均为 `source-report`，目标与版本未知；不要把它当成可复现登录协议、设备风控模型或生产密码实现。
