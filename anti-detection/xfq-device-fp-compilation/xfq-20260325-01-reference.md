---
schema_version: 2
id: xfq-20260325-nekobox-chain-reference
document_type: reference
original_date: '2026-03-25'
archived_date: '2026-10-02'
scope:
  targets: [nekobox]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260325-01.md#正文"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只保留来源点名的 NekoBox 发布页、剪切板导入和手动住宅节点。http 是作者那一次的选择。没有版本、主机、端口或账号。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 只保留链式代理的勾选顺序和随后开启 VPN。没有顺序颠倒时的现象，也没有分应用规则。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 检查只到「打开 ipinfo.io/json」。没有字段、国家或 App 内通过条件，本轮未打开该 URL。
relations:
  - type: derived_from
    target: "./xfq-20260325-01.md#正文"
tags: [nekobox, source-report]
---

# NekoBox 链式代理的节点顺序

这张卡只回答：来源如何在 Android 的 NekoBox 里把机场节点和住宅节点串起来，以及它把什么当成出口检查。不提供节点、账号或可导入配置。Mihomo 内核链是另一张卡的目标，不能把这里的菜单顺序当成 `dialer-proxy`。

<a id="interfaces"></a>
## 客户端与节点入口

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 作者点名的客户端是 NekoBox，并写明 v2rayNG 没有测成功。 | s1 第 39 行：1. 下载NekoBox（v2rayNG也行，但是我没测试成功） | source-report | 这篇自述的 Android 路径 | 没有版本，也没有 v2rayNG 的失败步骤 |
| C2 | 下载位置写成 NekoBoxForAndroid 的 Releases。 | s1 第 40 行：[Releases · MatsuriDayo/NekoBoxForAndroid · GitHub](https://github.com/MatsuriDayo/NekoBoxForAndroid/releases) | source-report | 来源给出的发布页 | 没有 tag |
| C3 | 机场订阅从剪切板导入。 | s1 第 42 行：去机场网站复制一波订阅链接，然后NekoBox右上角 添加服务器配置=》从剪切板导入 | source-report | NekoBox 的订阅入口 | 没有订阅地址 |
| C4 | 住宅节点手动输入；http 只是作者这一次选的协议。 | s1 第 44 行：侧边栏 配置=》然后右上角添加服务器配置 =》手动输入=》选一个你用的（我这里是http） ，然后正常配置 | source-report | 来源这一次的手动节点 | 「选一个你用的」没有把协议限定为 http |

<a id="request-chain"></a>
## 链式代理顺序

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 先勾选机场节点，再勾选住宅节点，来源要求注意顺序。 | s1 第 46 行：右上角添加服务器配置=》手动输入=》最下面的链式代理，勾选一个机场节点，然后再勾选你的住宅节点（注意顺序） | source-report | NekoBox 手动输入里最下面的链式代理 | 没有顺序颠倒后的现象 |
| C6 | 然后选中这条链式代理并开启 VPN。 | s1 第 47 行：然后选择链式代理，开启vpn即可； | source-report | 来源写出的启用动作 | 没有分应用或权限失败分支 |

<a id="validation"></a>
## 出口检查

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | 来源的检查只是浏览器打开 ipinfo.io/json。 | s1 第 48 行：最后浏览器打开ipinfo.io/json测试就行了 | source-report | 浏览器里看出口 | 没有字段级通过条件 |

## 验证与限制

第 38 行把先前的 Windows 路径写成一句话：之前我们的文章说了win上的链式代理，我测试是clash搞机场开tun，然后v2rayN配住宅ip，然后proxifier让指定进程走v2rayN； 然后今天是android端， 主要是为了正常使用海外社交媒体/电商类app，不用应该也行，但是容易风控； 这句没有端口、规则或失败出口，不收成模块。`Mihomo/Clash proxy chain` 已有 interfaces、request-chain、validation，描述的是内核 `dialer-proxy` 平面，不是 NekoBox 菜单。前提、字段级验收和失败出口都不在本篇，不建流程。作者的「我测试」「没测试成功」保持 source-report。
