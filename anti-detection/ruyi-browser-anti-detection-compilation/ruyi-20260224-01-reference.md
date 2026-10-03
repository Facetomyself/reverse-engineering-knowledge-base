---
schema_version: 2
id: anti-detection-sandia-proxy-cross-layer-reference
document_type: reference
original_date: '2026-02-24'
archived_date: '2026-07-13'
scope:
  targets: [proxy-cross-layer-discontinuity]
  client: network
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260224-01.md#分层分类体系table-3-1
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只整理来源对 SAND2025-02246 的转述。没有 pcap、Zeek 脚本或阈值。MSS 与延迟数字不是本次测量。不收录选代理或改协议栈的做法。
relations:
  - type: derived_from
    target: ./ruyi-20260224-01.md#分层分类体系table-3-1
tags: [proxy, mss, tls-hello-delay, source-report]
---

# 代理在网络各层留下的指纹错位

这张卡只回答一个检索问题：来源把 Sandia 技术报告 SAND2025-02246 转述成哪些跨层不一致信号。它不提供采集命令或绕过步骤。

<a id="risk-control"></a>
## 风险控制信号

来源把检测点定义成 cross-layer discontinuity：代理改写哪一层，那一层以下的指纹属于出口，以上属于原始客户端。L3、L4、L7 各自留下不同的错位。开篇广告句不是检测内容。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源写「Charles Smutz在2025年2月发布了这份技术报告（SAND2025-02246）」 | s1，ruyi-20260224-01.md:44 | source-report | 来源点名的技术报告 | 无报告页码 |
| C2 | 来源写「代理在不同网络层制造的"指纹错位"（cross-layer discontinuity），是它无法根治的先天缺陷。」 | s1，ruyi-20260224-01.md:47 | source-report | 来源的问题定义 | 无形式化定义 |
| C3 | 来源写「代理操作在哪一层，那一层以下的指纹就属于代理出口节点，以上的指纹属于原始客户端。」 | s1，ruyi-20260224-01.md:68 | source-report | 来源的分层比较规则 | 无判定代码 |
| C4 | 来源写「WireGuard默认1380，Windows VPN默认1360，正常以太网1460」，并写「IP TTL与TCP指纹的OS不一致」 | s1，ruyi-20260224-01.md:64 | source-report | 来源点名的包代理信号 | 不是本次抓包 |
| C5 | 来源写「TCP RTT ≠ TLS RTT；TLS Hello延迟异常；TCP指纹OS ≠ TLS指纹OS」 | s1，ruyi-20260224-01.md:65 | source-report | 来源点名的流代理信号 | 无 RTT 算法 |
| C6 | 来源写「TLS指纹=Golang而非浏览器；HTTP头被修改/排序；HTTP RTT ≠ TLS RTT」 | s1，ruyi-20260224-01.md:66 | source-report | 来源点名的应用代理信号 | 无头名单 |
| C7 | 来源写「反映的是exit node的OS，实际上几乎全是Linux或BSD」，并写「Tor浏览器无论跑在什么系统上，永远报」 | s1，ruyi-20260224-01.md:74-75 | source-report | 来源点名的 Tor 矛盾 | 无出口样本；UA 原文带反引号和空格，这里不抄整段 |
| C8 | 来源写「导致ja3值和标准Firefox完全不同——这一个特征就能锁定Tor浏览器」 | s1，ruyi-20260224-01.md:76 | source-report | 来源点名的 ja3 差异 | 无 ja3 原值 |
| C9 | 来源写「标准Firefox首次访问会开  ** 2个  ** TCP/TLS连接，Tor浏览器只开  ** 1个  **」 | s1，ruyi-20260224-01.md:77 | source-report | 来源点名的连接数 | 无复现记录 |
| C10 | 来源写「经常超过  ** 500ms  **」，并称「TLS Hello延迟」这个指标用于代理画像 | s1，ruyi-20260224-01.md:78-80 | source-report | 来源点名的 Hello 延迟 | 不是本次计时 |
| C11 | 来源写「MSS在TCP SYN包里明文广播」，以及「广播了正常的1460但实际MTU只有1380，大包会被丢弃导致连接卡死」，不一致「本身又是一个新的检测信号」 | s1，ruyi-20260224-01.md:92-94 | source-report | 来源的 MSS 约束 | 无丢包实验 |
| C12 | 来源列出「tcpi_advmss」「tcpi_pmtu」「tcpi_rcv_mss」 | s1，ruyi-20260224-01.md:98-100 | source-report | 来源点名的内核字段 | 无读取步骤 |
| C13 | 来源写「添加和删除」「把HTTP头按字母排序」「把URL查询参数也排序了」「改变HTTP头的大小写」 | s1，ruyi-20260224-01.md:108-111 | source-report | 来源点名的 L7 签名 | 无头样本 |
| C14 | 来源写「保留完整的HTTP头信息，包括顺序和大小写，不要做标准化处理」 | s1，ruyi-20260224-01.md:113 | source-report | 来源的日志保留建议 | 无日志格式 |
| C15 | 来源写「L4代理：TCP RTT（到exit node的距离）≠ TLS RTT（到真实客户端的距离）」「L7代理：TLS RTT（到MitM代理的距离）≠ HTTP RTT（到真实客户端的距离）」「L3代理：IP RTT（ping exit node）≠ TCP RTT（到真实客户端的距离）」 | s1，ruyi-20260224-01.md:155-157 | source-report | 来源的 RTT 比较类别 | 无基线差值 |
| C16 | 来源写「用NIDS被动测量RTT时，必须测量  ** 三次  **」，下一行写「传输的时间（不是两次）」 | s1，ruyi-20260224-01.md:169-170 | source-report | 来源点名的测量陷阱 | 无计时实现 |
| C17 | 来源写「一个Zeek扩展，采集IP/TCP/TLS各层的指纹和时序元数据」 | s1，ruyi-20260224-01.md:164 | source-report | 来源点名的工具 | 未核对仓库内容 |
| C18 | 来源写「每加一层代理，就多暴露一层的检测特征」，并写「复合代理的时序特征会"叠加"」 | s1，ruyi-20260224-01.md:215 | source-report | 来源对复合代理的检测结论 | 无叠加量 |

## 验证与限制

实战建议没有单独的前提、输出、验收和失败出口，性能表里的 CPU 与日志增幅也只是来源数字，所以不升为流程。第 197–218 行从自动化一侧重述同一约束，本卡不把选代理或改栈写成步骤。`browser-fingerprint` 的 risk-control 只覆盖宿主对象状态组。query 的 ja3、residential-proxy、tls-fingerprint 均为 0。`08-tls-ja3-fingerprint-randomization.md` 的 target 是 unknown，正文是自编译浏览器的 JA3 说明，不是这份跨层错位框架，因此不并入。
