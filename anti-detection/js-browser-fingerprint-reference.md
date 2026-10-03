---
schema_version: 2
id: js-browser-fingerprint
document_type: reference
original_date: unknown
archived_date: unknown
scope:
  targets: [browser-fingerprint]
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
    limits: 缺 locator，未复现。只记 fingerprint 相对 cookie、本地存储和 IP 的差别。采集 API、序列化格式、回传字段、算法和密钥不采用。同句里的「加密」不升成 encryption。
  - name: risk-control
    anchor: risk-control
    sources: [notes]
    basis: source-report
    limits: 缺 locator，未复现。一致性和完整性只是风险描述。只改一半会被说成触发拒绝、封禁或连续验证，不是某站复现，也不是 server-accepted。
tags: [browser-fingerprint, fingerprint, parameters, risk-control]
---

# 浏览器 JS 指纹

浏览器 JS 指纹是把硬件、软件和操作序列化后回服务器，形成可追踪标识。它和 cookie、IP 不是同一类关联手段。归 anti-detection。不并进混淆或滑块。不写成 encryption 文档。

<a id="parameters"></a>

## 参数：fingerprint

采集范围是硬件、软件和操作。序列化后回服务器。同句里出现的「加密」不能把 fingerprint 升成 encryption。算法、编码和密钥不采用。这也不是 encoding 破解，不是 token，不是 signature。

较早的关联手段是 cookie、某种本地存储和 IP。它们可以伪造，也可以走代理，所以后续转向更依赖真实设备成本的指纹。存储 API 的名字不猜。

浏览器维护方只留三类：一家是搜索公司的母公司体系，一家是基金会体系，一家是苹果体系。换皮浏览器仍走苹果内核。内核产品名和引擎接口不核对。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 硬件、软件和操作序列化后回服务器的可追踪标识叫做指纹 | notes | source-report | 定义 | 无 API、无格式、无字段；不升成 encryption |
| C2 | cookie、某种本地存储和 IP 是较早、较易伪造或可走代理的关联手段 | notes | source-report | 对照项 | 存储 API 名不采用 |
| C3 | 转向指纹是因为更依赖真实设备成本 | notes | source-report | 动机 | 不是某风控规则已接受 |
| C4 | 浏览器维护方保留母公司体系、基金会体系、苹果体系三类 | notes | source-report | 大类 | 内核产品名和引擎接口未核对 |

<a id="risk-control"></a>

## 一致性与完整性

隐私浏览器少留个人信息，尽量像普通访问。它不是指纹浏览器。无痕不留本地记录，但不隐藏于网络侧。改出口与多开不是同一件事。指纹浏览器解决多开，并要求一致性：改一项必须与其余匹配。完整性是：要改就整套改。只改一半，会被当成触发拒绝、封禁或连续验证。这是风险描述，不是某站复现。

系统、时区、字体、IP、邮箱、机型对不上，是讲解用的虚构组合，不是站点规则。检测站名不采用。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 隐私浏览器、无痕、改出口、多开是四件不同的事 | notes | source-report | 概念区分 | 不是产品清单 |
| C6 | 指纹浏览器要求一致性和完整性；只改一半会触发拒绝、封禁或连续验证 | notes | source-report | 风险描述 | 未在服务端复现 |
| C7 | 系统、时区、字体、IP、邮箱、机型对不上，是讲解用的虚构组合 | notes | source-report | 讲解例 | 不是站点规则 |

## 验证与限制

没有和混淆文、滑块文或 V2Pro 案例合并。缺 locator，未复现。不能声称一致性规则已被某风控服务端接受。
