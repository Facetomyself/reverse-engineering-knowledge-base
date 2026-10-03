---
schema_version: 2
id: http2-fingerprint
document_type: reference
original_date: unknown
archived_date: unknown
scope:
  targets: [http2]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: notes
    ref: null
    basis: source-report
    citation: 本地教学笔记（定位不公开）
    reason: 正式入库不保留讲次与公开定位；原始材料未随本文公开。
modules:
  - name: parameters
    anchor: parameters
    sources: [notes]
    basis: source-report
    limits: 缺 locator，未复现。只记 fingerprint 的结构。标准名、六个参数的名字和字节布局不采用。不收 TLS，不回填套件。
  - name: risk-control
    anchor: risk-control
    sources: [notes]
    basis: source-report
    limits: 缺 locator，未复现。0 标记和低优先级帧触发风控只是风险描述。标记名和帧名不采用。没有 server-accepted。
tags: [http2, fingerprint, parameters, risk-control]
---

# HTTP/2 指纹的结构

HTTP/2 指纹在传输层之上，和 TLS 指纹分开。不要和 [TLS 指纹](./tls-fingerprint-reference.md) 并成一篇，也不要互相派生。

协议代际只保留大意：早期一问一断；后来用多路复用缓解连接数；再后一代面向低延迟。代际编号不采用。再往后的传输只保留这些能力：用户数据报、不必保证不丢包、零等待握手、抗丢包。不把这些描述回填成具名协议或套件。

<a id="parameters"></a>

## 参数：fingerprint

这里的对象是 fingerprint。它不是 encryption，不是 encoding，不是 token，也不是 signature。正式名字大多不稳定，只保留结构。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 与设定相关的一项约有六个标准参数；顺序和是否齐全会被识别 | notes | source-report | HTTP/2 指纹结构之一 | 参数名不采用；六个不是已核对清单 |
| C2 | 不同浏览器取值不同 | notes | source-report | 浏览器差异 | 没有取值表 |
| C3 | 四个固定头部的顺序是特征；浏览器之间有差 | notes | source-report | 头部顺序 | 头部名不采用 |
| C4 | 本篇不收录 TLS 字段 | notes | source-report | 范围边界 | 套件一类片段不回填 |

<a id="risk-control"></a>

## 风控触发

下面两句是风险描述，不是复现出来的规则。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 不用浏览器、程序直连时某标记为 0；0 可能被当成漏项并触发风控 | notes | source-report | 风险描述 | 标记名不采用；0 属于哪个帧未知 |
| C6 | 自称扩展浏览器却发出低优先级帧，识别后会触发风控 | notes | source-report | 风险描述 | 帧名不采用；没有服务端接受证据 |

## 验证与限制

没有 request-chain。没有指纹串、请求 URL 或计算代码。缺 locator，未复现。依据停在 source-report。
