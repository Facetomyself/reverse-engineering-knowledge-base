---
schema_version: 2
id: ruyi-20260514-residential-ip-proxy-reference
document_type: reference
original_date: '2026-05-14'
archived_date: '2026-10-02'
scope:
  targets: [residential-ip-proxy]
  client: server
  version: unknown
  observed_at: 2022-01-12/2022-05-01
sources:
  - id: s1
    ref: ./ruyi-20260514-01.md#一住宅代理不是一个ip而是一套调度系统
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 只保留来源对 backconnect 的转述。不提供接入地址、账号或调度实现。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 重合、TTL 和失败重试都是 2022 年四家服务商采样的来源报告。TTL 不是操作系统鉴定。间隔秒数表不进入本卡。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: /24 只作为加权和挑战触发。来源写明没有部署误报率，不能当成封禁流程。
relations:
  - type: derived_from
    target: ./ruyi-20260514-01.md#一住宅代理不是一个ip而是一套调度系统
tags: [residential-ip-proxy, source-report]
---

# 住宅代理出口复用与 /24 加权边界

这篇卡检索的是：来源转述的 2023 年 workshop 测量里，住宅出口如何复用，以及 /24 和失败重试被说成什么信号。不提供代理接入或资源消耗步骤。

<a id="request-chain"></a>
## 连接被谁终止

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 出口不是客户端直连家庭设备：真实的住宅代理通常是 backconnect 模式。你不是直接连某个家庭设备，而是先连服务商的 | s1，源文件第 76 行 | source-report | 来源描述的 backconnect | 下一行才写到 superproxy 和 gateway；本卡不补接入参数 |

<a id="risk-control"></a>
## 复用、重合和失败时的换出口

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C2 | 单路径看起来更随机：服务商不是不复用IP，而是把复用藏到不同路径之间。 | s1，源文件第 170 行 | source-report | 同一 client-server 路径对比全局唯一 IP | 单站日志看不到跨路径复用 |
| C3 | 两家池子不是各算各的：从Oxylabs视角看，它有  ** 63%  ** 的IP也出现在Smartproxy池里 | s1，源文件第 238 行 | source-report | 该次 110 天采样 | 反向比例在下一行；来源不断言两家是同一实体 |
| C4 | 设备大类可以分开，但不能当成系统名：Oxylabs和Smartproxy几乎一样，都是97%以上TTL=64。ProxyRack则完全反过来，92.79%是TTL=128。 | s1，源文件第 285 行 | source-report | 初始 TTL 的来源汇总 | 第 468 行写明这不是 Linux 或 Windows 鉴定 |
| C5 | 失败时的换出口不同于内核重传：如果服务器故意延迟SYN-ACK，不立即回复，普通客户端只会重传原SYN；但这些住宅代理服务商可能会从多个不同gateway、多个端口继续尝试。 | s1，源文件第 395 行 | source-report | 来源的 UNACKEDDS 转述 | 没有部署误报率；各家间隔秒数不抄入本卡 |
| C6 | 宣传规模不是同时在线池：宣传数字不能直接当成可用、独立、同时在线的出口池规模。 | s1，源文件第 336 行 | source-report | Oxylabs、Smartproxy、ProxyRack 的来源估计对比 | 估计曲线本身未复算 |

<a id="decision-flow"></a>
## /24 怎么用

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | 网段不能直接封：不要直接把/24黑掉。住宅网段里正常用户太多，误伤会很严重。 | s1，源文件第 429 行 | source-report | 来源建议的风险特征 | 第 472 行写明没有误报率、召回率和业务影响 |
| C8 | 延迟不能面向全部用户：你不能对所有正常用户都延迟SYN-ACK，否则用户体验会炸。比较合理的方式是只对可疑/24、可疑ASN、可疑行为触发这个挑战。 | s1，源文件第 404 行 | source-report | 来源给出的触发范围 | 没有“可疑”的判定式，也没有挑战失败后的出口 |

## 验证与限制

效果与比例保持 source-report。Mihomo 代理平面卡只描述本机链式出口身份，不覆盖住宅 gateway。Bright Data 在来源里只跑了约 13 天。第 402 行关于消耗代理资源的说法不进入本卡。这不是流程：没有验收阈值，也没有证据不闭合时的停止条件。
