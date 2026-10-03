---
schema_version: 2
id: mobile-proxy-network-reference
document_type: reference
original_date: '2026-05-20'
archived_date: '2026-10-02'
scope:
  targets: [mobile-proxy]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260520-01.md#十625万个蜂窝代理ip黑名单几乎抓不住
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留黑名单命中、/24 集中、高连接低体积和被动指纹偏 Linux 的转述。不抄目的域名，也不写集成 SDK 的做法。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留蜂窝占比和两条传输协议的来源观察。没有报文样例。
relations:
  - type: derived_from
    target: ./ruyi-20260520-01.md#十625万个蜂窝代理ip黑名单几乎抓不住
tags: [mobile-proxy, source-report]
---

# 移动代理出口的黑名单边界

这篇卡检索的是：笔记转述的 IEEE S&P 2021 测量里，蜂窝代理出口为什么不能只靠 IP 黑名单看，以及几家 SDK 用了哪类长连接。不提供购买或集成步骤。

<a id="risk-control"></a>
## 检测边界

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 只有  ** 0.44%  ** 的蜂窝代理IP被至少一个IP黑名单报告。 | s1，源文件第 311 行 | source-report | 笔记中的蜂窝代理 IPv4 | 不是现行名单 |
| C5 | 如果你的代理检测主要靠IP黑名单，移动代理基本能轻松绕过去。 | s1，源文件第 319 行 | source-report | 绑定前文 0.44% 的那次测量 | 不是通用评测 |
| C6 | Top 5%的IPv4 /24贡献了  ** 50.64%  ** 的代理IPv4地址。 | s1，源文件第 299 行 | source-report | 9 家服务的渗透样本 | 不能外推到未测服务商 |
| C7 | 这些域名连接数很高，但流量体积不大。 | s1，源文件第 256 行 | source-report | 笔记抓到的广告相关目的域名 | 不设阈值，不抄域名 |
| C8 | 它不会在转发前请求用户同意； | s1，源文件第 282 行 | source-report | 笔记所称的 SDK X | 不收录硬编码域名 |
| C9 | 被动指纹用p0f，覆盖了72.06%的蜂窝代理IP。结果显示，Linux占绝大多数。 | s1，源文件第 326 行 | source-report | p0f 覆盖到的蜂窝代理 IP | 主动响应率只有 0.85%，不能当成单机暴露 |

<a id="parameters"></a>
## 出口与传输

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 被IPinfo标记为蜂窝IP，占IPv4代理IP的  ** 8.70%  ** 。 | s1，源文件第 137 行 | source-report | 该次渗透得到的 IPv4 | IPv6 是否蜂窝未覆盖 |
| C2 | MonkeySocks使用HTTP/2； | s1，源文件第 228 行 | source-report | 笔记的动态分析观察 | 没有报文 |
| C3 | Luminati、Oxylabs等使用WebSocket； | s1，源文件第 229 行 | source-report | 点名的这几家 | 不外推未点名服务商 |

## 验证与限制

`android-app-device-fingerprint` 只讲设备画像一致性。`Mihomo/Clash proxy chain` 是本机代理平面，不是这批蜂窝出口。`residential-proxy` 没有卡片。测量步骤、佣金和域名表不进入本卡。数字保持 source-report。
