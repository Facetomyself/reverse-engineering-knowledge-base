---
schema_version: 2
id: anti-detection-zhihu-libdu-fingerprint-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [zhihu]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./shuzilm-libdu-fingerprint.md#extraction-reference
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 仅转述来源所述 d2api report 路径及字段去向；未请求当前服务或验证服务端接受。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 仅概括字段到采集来源的映射类型；全表包含注册之外的采集点，分组存在来源自述的不确定项。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 只描述报告中的采集、签发与后续携带关系；不推断风控评分、激活状态或 server-accepted。
relations:
  - type: derived_from
    target: ./shuzilm-libdu-fingerprint.md#extraction-reference
tags: [libdu.so, d2api, cdd, x-ms-id, field-provenance, source-report]
---

# 知乎 Android 数盟 libdu 字段来源与签发链

这张卡用于查找来源文章报告的字段来源映射，以及 `d2api` 报告到业务标识的关系。范围限定为知乎 Android 的单份历史分析材料；字段/API 名称用于定位，不能当成当前版本清单。

<a id="interfaces"></a>
## 接口边界

来源报告记载 native 收集数据后请求 `/a/d2api/report`，响应中的 `cdd` 随后被业务请求作为 `x-ms-id` 携带。传输封装描述为 XOR 与 zlib 组合；具体字面量和样值不在本参考中。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 报告接口响应 `cdd` 与后续业务 `x-ms-id` 被来源描述为同一签发链上的前后字段。 | s1，签发与请求链章节 | source-report | 来源所述知乎 Android 样本 | 未验证当前接口、字段语义或服务端接受 |

<a id="parameters"></a>
## 字段来源

来源归档按字段记录含义、指纹数据类别、采集方式和出现位置。可复用的是映射方法与公开 API/字段名：例如 Android `Build` 字段、系统属性与服务 API、时间/配置来源、以及 native 采集入口。查询单个字段时应回到来源表核对其行，不要把整张表视为注册包字段表。

来源明确区分较窄的注册载荷与更广的字段清单；部分分组及若干字段归属未完全确定。静态列出字段不证明它在某次请求中实际发送。

| 字段示例 | 来源报告中的映射 | 复用边界 |
|---|---|---|
| `rG1` / `rG11` | `android.os.Build.BOARD` / `android.os.Build.BRAND` | 只保留 API 来源，不包含设备属性值 |
| `pEC` / `mEC` / `0q1` | 配置 JSON 中的 `pEventCode` / `mEventCode` / `dna` | 只记录字段名映射，不包含配置内容 |
| `6yY` | `MediaDrm.getPropertyByteArray("deviceUniqueId")` | 只记录 getter 来源，不包含返回值 |

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C2 | 来源表将字段名映射到 API/采集入口，但其范围大于注册请求，且有未闭合分组。 | s1，字段清单与未决项章节 | source-report | 来源归档中保留的 366 个字段/API 名称 | 字段样例已脱敏；来源包不可用，不能独立复核映射 |

<a id="request-chain"></a>
## 请求链路

```text
native 采集
  -> POST /a/d2api/report
     来源报告：XOR + zlib 请求封装，具体常量不公开
  -> 响应字段 cdd
  -> 后续业务请求头 x-ms-id
```

这表示来源报告中的标识签发/传递关系，不表示客户端已激活、业务请求已成功或服务器接受了某个样本。不要把封装描述称为完整签名算法。

## 样例与验证边界

字段/API 名称保留在来源归档；设备、网络、App 环境、hash/digest 样值及静态 XOR 字面量不复制到本卡。来源样例做过脱敏，样例来源性质未知，原始来源包不可用；来源归档的 `source_completeness` 为 `partial`。

本卡与[设备画像一致性参考](./android-device-fingerprint-consistency-reference.md)仅在设备字段语境上相邻；额外内容是 libdu 字段来源与 `cdd` 签发关系，不推断风险评分或服务端判定规则。本文没有 runtime、parity 或 server 验收。
