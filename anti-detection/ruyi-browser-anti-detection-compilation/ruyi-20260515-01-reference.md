---
schema_version: 2
id: ruyi-20260515-badpass-rtt-reference
document_type: reference
original_date: '2026-05-15'
archived_date: '2026-10-02'
scope:
  targets: [badpass]
  client: server
  version: unknown
  observed_at: 2022-01-12/2022-05-01
sources:
  - id: s1
    ref: ./ruyi-20260515-01.md#二关键直觉住宅代理拆了tcp但没拆tls
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 只保留来源对“TCP 在 gateway 终止、TLS 仍端到端”的转述。不描述如何改隧道。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 50ms 和两项准确率都是来源自建平台上的报告。不是生产阈值，也未在本轮复测。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只覆盖会拆开 TCP、但不拆 TLS 的结构。NAT、IPsec VPN 和不拆 TCP 的隧道不在范围内。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 测点必须在公网入口一侧。来源没有给出 CDN、连接复用或 HTTP/3 下的停止条件，因此不能当成流程。
relations:
  - type: derived_from
    target: ./ruyi-20260515-01.md#二关键直觉住宅代理拆了tcp但没拆tls
tags: [badpass, source-report]
---

# BADPASS 的 TCP 与 TLS RTT 差边界

这篇卡检索的是：来源转述的 BADPASS 用哪一段路径差把直连和这类住宅代理分开，以及 50ms 规则被报告成什么。不提供绕过做法。

<a id="request-chain"></a>
## 两段 RTT 各量到谁

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | TCP 往返停在出口：TCP RTT测到的是 gateway 到服务器的距离； | s1，源文件第 111 行 | source-report | 来源描述的 backconnect HTTPS | 直连时这一段与 TLS 是同一条路径 |
| C2 | TLS 往返仍走完整代理链：TLS RTT测到的是 客户端经过superproxy、gateway再到服务器的端到端距离。 | s1，源文件第 112 行 | source-report | 不解密 TLS 的转发 | 来源未把具体握手记录名写成必选实现 |

<a id="parameters"></a>
## 50ms 规则和来源报告的数字

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C3 | 直连差值集中在很小的区间：97%的直连连接，RTT difference小于等于20ms。 | s1，源文件第 200 行 | source-report | 来源 Figure 3 的直连转述 | 负差值被写成抖动，不是另一类代理 |
| C4 | 判定式只有一个比较：如果TLS RTT - TCP RTT大于50ms，判定为代理； | s1，源文件第 232 行 | source-report | 来源选定的经验阈值 | 下一行写明否则判直连；没有按服务商分阈值 |
| C5 | 同一阈值的误报被写成：False Positive：  ** 0.04%  ** | s1，源文件第 56 行 | source-report | 开篇对 50ms 的来源汇总 | 与后文结果段重复，仍是 source-report |
| C6 | 同一阈值的漏报被写成：False Negative：  ** 1.93%  ** | s1，源文件第 57 行 | source-report | 同上 | 不利假设下的漏报是另一行，不混用 |
| C7 | 同一阈值的准确率被写成：Accuracy：  ** 99.01%  ** | s1，源文件第 58 行 | source-report | 来源 9271 万条完整连接的转述 | 第 379 行写明不是生产站流量 |
| C8 | 不利假设下的准确率被写成：Accuracy：  ** 92.78%  ** | s1，源文件第 260 行 | source-report | 第 256 行定义的 worst-case | 不能把它说成现场验收线 |

<a id="risk-control"></a>
## 不覆盖哪些隧道

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C9 | 检测对象是特定结构：这篇方法检测的不是“所有代理”，而是检测一种特定结构：  ** 会断开TCP端到端连接，但保持TLS端到端的代理。  ** | s1，源文件第 287 行 | source-report | backconnect 住宅代理；来源也提到 SSH forwarding 可能符合 | NAT 和 IPsec VPN 被明确排除 |

<a id="decision-flow"></a>
## 测点放在哪

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C10 | 测点在 WAF 后面会量错路径：但如果检测点在WAF后面，看到的TCP和TLS都是WAF到后端这一段，两者可能仍然接近。所以这种连接不一定会被判成住宅代理。 | s1，源文件第 309 行 | source-report | 企业 WAF 终止 TLS 的来源讨论 | 这是布置限制，不是已测量的误报率 |
| C11 | 来源要求靠近公网入口：实际部署时，最好在最靠近公网入口的地方测，比如边缘负载均衡、TLS终止点、前置网关。 | s1，源文件第 315 行 | source-report | 来源建议的测点 | 没有 CDN 或 HTTP/3 下的失败出口 |

## 验证与限制

99.01% 和 92.78% 保持 source-report。catalog 里还没有 `badpass` 或 `residential-ip-proxy` 卡片；同目录 20260514 讲的是出口复用和 /24，没有这条 RTT 规则。绕过一节只说明中间人 TLS、拉高 TCP 延迟或改成不拆 TCP 的隧道会离开该信号，本卡不写做法。缺可执行的失败出口，不能建成流程。
