---
schema_version: 2
id: tls-fingerprint
document_type: reference
original_date: unknown
archived_date: unknown
scope:
  targets: [tls]
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
    limits: 缺 locator，未复现。只记网络层 fingerprint 的完整性、顺序，以及两代方案的结构。不写代号、套件、曲线、点格式或摘要算法名。不收 HTTP/2，不收硬件序列号。
  - name: risk-control
    anchor: risk-control
    sources: [notes]
    basis: source-report
    limits: 缺 locator，未复现。只记栈差异会暴露客户端。栈名、库名和插入值的正式名称不采用。不是已复现的拒绝实验。不写伪装步骤。
tags: [tls, fingerprint, parameters, risk-control]
---

# TLS 指纹的完整性与两代结构

网络层 TLS fingerprint 检查什么，以及前后两代方案在结构上有什么差别，都在这里。变化、复制和碰撞见 [浏览器指纹关联](./browser-fingerprint-linkage-reference.md)，不要塞进本篇参数表。不收 HTTP/2。不收硬件序列号。不和 HTTP/2 文互相派生。

指纹可以分成网络层和硬件层。本文先讲网络层。硬件和软件的细目不写入参数。

<a id="parameters"></a>

## 参数：有哪些项，顺序对不对

网络层鉴别是两件事：有哪些项，顺序是否一致。作者用完整性和一致性命名这两条。缺项不行，顺序错也会失败。字段名单不采用。这是 fingerprint，不是 encryption，不是 encoding，不是 token，也不是 signature。

流行方案有前后两代。前一代按固定顺序拼接若干字段。少一组或顺序错都不行。字段个数一度被说成五个，五个不是稳定清单。后一代用来避开前一代的局限：摘要碰撞或可按序还原，以及随机插入值会误伤正常用户。后一代格式不同，分成多段，下划线前称为 A 段。代号、公司名、套件、曲线和点格式全部不采用。摘要被攻破后转向更难碰撞的下一代，是背景，不写成某种具名套件。

查看自己的指纹有三条路：网站、抓包工具、代码库。网址、工具名和库名不采用。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 网络层 fingerprint 同时检查有哪些项，以及顺序是否一致；缺项或乱序会失败 | notes | source-report | 网络层 | 字段名单不采用；未复现 |
| C2 | 前一代是固定顺序拼接；后一代格式不同，用来避开碰撞、可还原和随机值误伤 | notes | source-report | 两代结构 | 不写代号和套件；「五个」不是清单 |
| C3 | 后一代分成多段，下划线前称为 A 段 | notes | source-report | 结构 | 不是已核对的指纹串格式 |
| C4 | 本篇不收 HTTP/2，也不收硬件序列号 | notes | source-report | 范围边界 | 序列号放在关联文，且字段不采用 |

<a id="risk-control"></a>

## 栈差异

浏览器能开、某种 Python HTTP 库出现拒绝，归因于库所依赖的开源 TLS 栈和浏览器厂商自维护分支不同。最显著的差别是后者会随机插入无意义值，用来区分客户端。栈名和插入值的正式名称不采用。这不是已复现的拒绝实验，不写状态码，不写库名，不写 URL。

常见 HTTP 库几乎不能伪装。另一种实现更能扛一部分检测。更深仍要手工逐项探测再封装。语言和库的名字不采用。每个客户端的 TLS 实现不同，完整性和一致性检查能暴露差异。本文不记录探测步骤或封装步骤。「可以」不等于本次已验证。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 拒绝被归因于开源 TLS 栈和浏览器自维护分支不同，后者会随机插入无意义值 | notes | source-report | 栈差异 | 专名不采用；不是已复现实验 |
| C6 | 常见库几乎不能伪装；逐项探测只是评论，不是本文的步骤 | notes | source-report | 方法评论 | 不提供伪造步骤 |

## 验证与限制

关联文补充本篇，但不能合成一个「加密指纹」模块。缺 locator，未复现。不能声称任何具名套件、密钥，或某个库在某个 URL 上的拒绝结果。
