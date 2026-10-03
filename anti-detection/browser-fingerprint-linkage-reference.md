---
schema_version: 2
id: browser-fingerprint-linkage
document_type: reference
original_date: unknown
archived_date: unknown
scope:
  targets: [browser-fingerprint-linkage]
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
  - name: risk-control
    anchor: risk-control
    sources: [notes]
    basis: source-report
    limits: 缺 locator，未复现。只处理变化后是否仍可关联、能否复制、同配置是否碰撞。不写 TLS 字段表，不写论文步骤，不写序列号读取方式。
relations:
  - type: supplements
    target: ./tls-fingerprint-reference.md#parameters
tags: [fingerprint, linkage, risk-control]
---

# 浏览器指纹的关联、复制与碰撞

指纹变了还能不能关联、能不能复制、同配置会不会碰撞，讲的是 fingerprint 在变化之后还能否被当成同一个人或同一台机器。不要把它们塞进 [TLS 指纹](./tls-fingerprint-reference.md) 的参数表，也不要写成 encryption。两边是补充，不是派生。

<a id="risk-control"></a>

## 三个问题

指纹变了能否关联：更新会造成摘要大变。多项相似度仍可以把相邻状态连起来。地点与出口一起变，仍可能被接受。操作系统或 CPU 一类大改，容易不被认可。具体型号不采用。这不是已验证的关联规则。

能否复制他人指纹：可以留下的概念句是，唯一性不等于不可伪造性。有研究用中间采集再交给另一方，那不是中间人攻击。论文题名和链接不采用。本文不记录采集或转交步骤。声称可以复制，不等于本次已验证。

两台全新同配置机器的浏览器指纹可能相同，也就是碰撞。硬件还有唯一序列号，并被当作隐私。序列号字段和读取方式不采用。本篇不把序列号收成 TLS 参数。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 指纹更新会使摘要大变，多项相似度仍可能把相邻状态关联起来 | notes | source-report | 变化后的关联 | 不是已验证规则；型号不采用 |
| C2 | 地点和出口一起变仍可能被接受；操作系统或 CPU 一类大改容易不被认可 | notes | source-report | 接受差异 | 未复现 |
| C3 | 唯一性不等于不可伪造性 | notes | source-report | 概念 | 无论文链接；不写采集步骤 |
| C4 | 两台全新同配置机器的浏览器指纹可能碰撞；硬件唯一序列号属于隐私 | notes | source-report | 碰撞 | 序列号字段不采用；不是 TLS 参数 |

## 验证与限制

没有 parameters 模块，避免和 TLS 的完整性、顺序、两代结构混成一张表。没有 signature、token 或 encryption。缺 locator，未复现。不能把「可以复制」写成运行时观察。
