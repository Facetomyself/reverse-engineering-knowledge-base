---
schema_version: 2
id: anti-crawler-risk-20260701-network-fingerprint-reference
document_type: reference
original_date: '2026-07-01'
archived_date: '2026-10-02'
scope:
  targets:
    - ja3
    - ja4
    - http2-fingerprint
    - ip-reputation
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./anti-crawler-risk-20260701-01.md#11-原理一句话"
    basis: source-report
  - id: s2
    ref: "./anti-crawler-risk-20260701-01.md#21-原理"
    basis: source-report
  - id: s3
    ref: "./anti-crawler-risk-20260701-01.md#31-ip-的三六九等"
    basis: source-report
  - id: s4
    ref: "./anti-crawler-risk-20260701-01.md#41-常见的露馅点"
    basis: source-report
  - id: s5
    ref: "./anti-crawler-risk-20260701-01.md#13-python-脚本的-tls-指纹为什么一眼假"
    basis: source-report
  - id: s6
    ref: "./anti-crawler-risk-20260701-01.md#22-看看你当前工具发的-http2-指纹"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2]
    basis: source-report
    limits: 只保留来源对 JA3 拼接规则和 HTTP2 SETTINGS 构成的描述。示例 JA3 明文字符串和 SETTINGS 数值未转写，未按当前浏览器版本复算。
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2, s3, s4]
    basis: source-report
    limits: 分档、泄露点和「三者对不上」都是来源陈述。未对照当前 Akamai、Cloudflare 或任何站点的拦截结果。
  - name: interfaces
    anchor: interfaces
    sources: [s5, s6]
    basis: source-report
    limits: 三档客户端和回显站点只是来源点名的对照入口。归档代码围栏粘连，不能当可运行客户端。
relations:
  - type: derived_from
    target: "./anti-crawler-risk-20260701-01.md#一tls-指纹ja3-与-ja3s"
tags:
  - ja3
  - http2-fingerprint
  - ip-reputation
  - source-report
---

# JA3、HTTP2 指纹与 IP 信誉的来源边界

这张卡只回答：来源如何描述 TLS ClientHello 的 JA3、HTTP2 SETTINGS 指纹，以及 IP 信誉和代理泄露各自看什么。不提供可运行的伪装客户端。Akamai 的 Cookie、`sensor_data` 和 challenge 链仍以产品卡为准；这里不覆盖那条链路。

来源没有可公开定位的原文 URL。成功与否只到作者自述。示例指纹明文字符串、SETTINGS 数值和代理账号形态不进入本卡。

<a id="parameters"></a>
## 参数机制

来源把 JA3 写成 ClientHello 里五类相对固定字段的拼接，再取 MD5。它点名 JA3S 看 ServerHello，JA4 拆得更细，但没有给出 JA4 的字段表。

> 把这 5 项按规则拼成字符串，取 MD5，就是  ** JA3  ** （后来演进到 JA3S 看 ServerHello，JA4 拆得更细）。

五类字段是 TLS 版本、cipher suites 顺序、extensions 种类和顺序、supported_groups 顺序、ec_point_formats。来源强调顺序属于客户端实现，不是单个套件名单。

HTTP2 指纹被写成 `h2` 上 SETTINGS 帧的键顺序加值，并称为 Akamai HTTP2 指纹。来源另把紧随的 WINDOW_UPDATE 和 PRIORITY 算进同一组对照，没有单列算法名。

`curl_cffi` 被写成按浏览器版本抄 ClientHello，对齐 cipher 顺序、extension 顺序、ALPN 和 GREASE。这是作者对库的描述，不是本轮字节对照。

<a id="risk-control"></a>
## 对照时风控看什么

来源把第一道关放在 TCP/TLS/HTTP2 握手，而不是应用层账号字段。它给出的直接判据是：UA 像 Chrome，JA3 却像 Python 客户端。

> 风控拿到你第一个 TLS 握手包，算一下 JA3，就知道你是不是"挂着 Chrome UA 但实际是 Python 脚本"。

JA3、HTTP2 SETTINGS 顺序和值、以及 WINDOW_UPDATE / PRIORITY 三者对不上，来源写成机器人嫌疑。它点名同时看这些的是 Akamai 和 Cloudflare，没有写具体策略版本。

IP 被分成住宅 ISP、移动 4G/5G、数据中心、机房裸机、VPN 出口和公开代理。来源把住宅和移动放在高信誉，把数据中心写成新号注册容易 403，把公开代理写成不要用。移动网段「批量注册反而容易触发」只是这一句，没有阈值。

代理即使出口像住宅，来源仍单列四类泄露：DNS 仍走本地 ISP、WebRTC 经 `RTCPeerConnection` 暴露内网或未走代理的公网地址、TCP 时间戳和窗口缩放能区分 OS、HTTP CONNECT / SOCKS5 / MITM CA 有协议或证书特征。TCP 项被作者自己标成比 JA3 次要。

任一单项对不上都被写成加权项，攒多了就 403。没有权重、阈值或单站点样本。

<a id="interfaces"></a>
## 来源点名的客户端和回显入口

来源把客户端分成三档，只作为选择表，不作为本卡的调用说明：

| 来源方案 | 来源对成本的说法 | 来源对效果的说法 |
|---|---|---|
| `curl_cffi` | 低 | 够用 |
| `tls-client` | 中 | 很稳 |
| Playwright / Selenium / 无头 Chrome | 高 | 最稳 |

回显入口被点名为 `https://http2.pro/api/v1` 和 `https://tls.browserleaks.com/json`。IP 类型查询被点名为 `ipapi.co` 和 `ipinfo.io`。这些是来源用来看回显的站点，不是本轮请求结果。

作者写明 scapy 的 `ssl_tls` 解析不完整，生产环境更偏向 tls-client 或 ja3 库；服务端可看的名字是 sslh、zeek、suricata。本机字段抽取被写成 tshark 过滤 `tls.handshake.type == 1`。归档里的 Python 示例粘在同一行，不能执行。

## 验证与限制

- 没有 JA3/JA4 字段表的当前版本对照，也没有 HTTP2 SETTINGS 数值。
- 没有本地计算、没有回显响应、没有站点接受或拒绝记录。
- `navigator.webdriver` 与 `disable-blink-features=AutomationControlled` 只被写成浅层检测不够，没有复测。
- 文末场景选型（轻量请求、登录后、批量注册、只测指纹）是建议表，缺前提、输出、验收和失败出口，所以不是流程卡。
- 住宅代理示例里的账号形态已省略。
