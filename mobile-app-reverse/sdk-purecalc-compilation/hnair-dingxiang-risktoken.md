---
schema_version: 2
id: mobile-app-reverse-sdk-purecalc-compilation-hnair-dingxiang-risktoken
document_type: reference
scope:
  targets:
  - DXRisk riskToken issuance
  client: Android app
  version: source report; exact SDK/app build unknown
  observed_at: unknown
sources:
- id: s1
  ref: null
  basis: source-report
  citation: 本地项目分析材料（定位不公开）
  reason: 出处来自原归档来源字段；本地路径已省略，原始材料未随本文公开，本轮未重跑来源实验。
source_completeness: unknown
modules:
- name: request-chain
  anchor: dxrisk-m1-chain
  sources: [s1]
  basis: source-report
  limits: 请求链来自来源报告；appKey、XXTEA key、画像 schema 和本轮网络验收均不公开。
- name: parameters
  anchor: dxrisk-m1-wire-format
  sources: [s1]
  basis: source-report
  limits: 只保留字段形状和 ZIP 字节约束，不提供敏感常量或完整画像。
- name: validation
  anchor: dxrisk-acceptance-boundary
  sources: [s1]
  basis: source-report
  limits: 正文明确区分本地 protobuf 对齐与 serverAccepted；本轮未执行任一验收。
tags: [dxrisk, risktoken, protobuf, xxtea]
original_date: 2026-08-14 源码
archived_date: '2026-09-06'
---

# 顶象 DXRisk：riskToken 是签发请求不是本地拼串

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: workspace/hnair-dingxiang-risktoken
> 原始发布时间: 2026-08-14 源码
> 归档日期: 2026-09-06
> 分类: mobile-app-reverse
</details>
>
> 海南航空 Android 接入顶象 DXRisk。客户端构造 `/udid/m1` 签发请求，token 在响应里。不收录 appKey、XXTEA key 和 189 项真实画像。

<a id="dxrisk-m1-chain"></a>
## 结论

`riskToken` 由顶象服务端签发。不存在「本地拼 8 位时间十六进制 + 32 位随机串」的真实算法。

```text
RiskSdk.getToken()
  -> JNI
  -> metadata + N 项 profile
  -> protobuf
  -> sign = MD5(appKey || protobuf || appKey)
  -> ZIP(entry=data, raw DEFLATE)
  -> XXTEA(include_length=true)
  -> POST /udid/m1
  -> 响应 XXTEA -> ZIP -> protobuf -> riskToken
```

HTTP 是 `application/octet-stream`。query 带 `sign` / `appKey` / 包名 / SDK 版本。

<a id="dxrisk-m1-wire-format"></a>
## ZIP 约束

Native 固定向量要求手工拼 ZIP 头：DOS 时间、extra、注释均为 0。用 `zipfile` 默认时间戳会对不齐逐字节对照。

## 画像

profile 必须成组，来自同一台设备的一次 Native 捕获。Windows 主机不能实时读 Android API。只刷新已证明有时间关系的少数键，禁止逐项随机或 SoC/GPU hybrid。

<a id="dxrisk-acceptance-boundary"></a>
## 边界

- protobuf 逐字节对齐 ≠ `serverAccepted`
- 接入常量和 XXTEA 材料按 App/SDK 版本绑定，不能跨包混用
- 完整字段字典和实现留 `workspace/hnair-dingxiang-risktoken/source/`

## 提炼说明（454）
retain 既有 DXRisk riskToken 签发链 reference。
protobuf 对齐不等于 serverAccepted。
本轮不另建卡。
