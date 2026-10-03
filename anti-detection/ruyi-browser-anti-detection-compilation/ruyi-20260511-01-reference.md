---
schema_version: 2
id: ruyi-20260511-traffic-shadowing-reference
document_type: reference
original_date: '2026-05-11'
archived_date: '2026-10-02'
scope:
  targets: [traffic-shadowing]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260511-01.md#一这篇到底在测什么
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留影子复制的定义、DNS 与 HTTP/TLS 的位置差异，以及 10 天仍会回流的转述。不抄诱饵标识或解析器地址。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留一次性诱饵、honeypot 回流、下界归因和回流多是侦察。没有失败出口，不能当成操作流程。
relations:
  - type: derived_from
    target: ./ruyi-20260511-01.md#五最核心的结果dns最容易被影子复制
tags: [traffic-shadowing, source-report]
---

# Traffic shadowing 的测量边界

这篇卡检索的是：该文转述的 IMC 2024 实验里，什么样的后续请求被算成流量影子，以及这个结论不能归因到哪里。不提供诱饵构造模板。

<a id="risk-control"></a>
## 什么叫做被影子复制

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C1</td><td>定义原文：你的流量没有被“阻断”，但被“偷看”和“复制使用”了。</td><td>s1，源文件第 74 行</td><td>source-report</td><td>该文的 shadowing 定义</td><td>不是单条路径的现场记录</td></tr>
<tr><td>C2</td><td>和被动看见分开：看见了→ 记住了→ 之后主动发起新的请求</td><td>s1，源文件第 117 行</td><td>source-report</td><td>honeypot 上出现的后续请求</td><td>没打回测量者的不算</td></tr>
<tr><td>C3</td><td>协议差异：DNS decoy 最容易触发 traffic shadowing。</td><td>s1，源文件第 273 行</td><td>source-report</td><td>文中 Figure 3 的转述</td><td>不是所有解析器</td></tr>
<tr><td>C4</td><td>DNS 位置：99.7% 的DNS shadowing只有当包真正到达目的解析器时才触发</td><td>s1，源文件第 321 行</td><td>source-report</td><td>文中 DNS traceroute</td><td>不能指到某一台设备</td></tr>
<tr><td>C5</td><td>HTTP 位置：97.7% 的HTTP shadowing发生在链路中间，不是终点服务器</td><td>s1，源文件第 335 行</td><td>source-report</td><td>文中 HTTP 诱饵</td><td>不外推到 TLS</td></tr>
<tr><td>C6</td><td>TLS 位置：TLS shadowing发生在链路中间其余更多接近目标端</td><td>s1，源文件第 342 行</td><td>source-report</td><td>文中 TLS 诱饵</td><td>中间比例不是通用常数</td></tr>
<tr><td>C7</td><td>保留时间：40%的DNS decoy，10天后还会触发HTTP/TLS请求</td><td>s1，源文件第 370 行</td><td>source-report</td><td>该实验的 DNS decoy</td><td>不是真实查询的概率</td></tr>
<tr><td>C8</td><td>范围：某些公共递归解析器方向特别容易发生 traffic shadowing。</td><td>s1，源文件第 304 行</td><td>source-report</td><td>公共递归方向</td><td>根、权威和自建对照在第 300 行被写成几乎不出现</td></tr>
</table>

<a id="decision-flow"></a>
## 怎样判定，以及判定到哪为止

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C9</td><td>一次性和唯一性：每个诱饵只发一次每个诱饵的标识都独一无二</td><td>s1，源文件第 178 行</td><td>source-report</td><td>QNAME、Host、SNI 三类诱饵</td><td>不记录标识格式</td></tr>
<tr><td>C10</td><td>闭环：我发一次→ 中间谁偷偷记下来了→ 它以后拿去自己探→ 探测请求打回我这里→ 我就知道它动手了</td><td>s1，源文件第 237 行</td><td>source-report</td><td>wildcard 指向自有 honeypot</td><td>没有中间抓包</td></tr>
<tr><td>C11</td><td>归因上限：很难最终归因“就是某台具体设备、某家公司、某个运营商干的”</td><td>s1，源文件第 43 行</td><td>source-report</td><td>路径和 AS 层</td><td>下一行把实验写成下界测量</td></tr>
<tr><td>C12</td><td>回流内容：作者没有看到大规模的漏洞利用尝试，这一点很重要。</td><td>s1，源文件第 401 行</td><td>source-report</td><td>打回的 HTTP/HTTPS 请求</td><td>第 411 行只点出路径枚举和目录扫描</td></tr>
<tr><td>C13</td><td>同一品牌可以不一样：同一个公共解析器品牌，不同国家/地区的实例行为可能完全不同。</td><td>s1，源文件第 557 行</td><td>source-report</td><td>114DNS 案例的转述</td><td>不推广到全部公共解析器</td></tr>
</table>

## 验证与限制

`browser-fingerprint` 只描述浏览器宿主对象之间的一致性，没有这条 DNS/HTTP/TLS 诱饵测量。数字和比例都保持 source-report。第十二节建议用 ECH 隐藏 SNI、用 ODoH 或 OHTTP 拆开 DNS 内容和来源，但本篇没有测量加密之后的网站指纹，所以那些句子不是本卡的结论。没有验收条件和失败出口，不能当成流程。
