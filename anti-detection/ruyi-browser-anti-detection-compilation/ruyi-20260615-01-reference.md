---
schema_version: 2
id: ruyi-20260615-browserscan-webrtc-candidate
document_type: reference
original_date: "2026-06-15"
archived_date: "2026-10-02"
scope:
  targets: [browserscan]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260615-01.md#浏览器-api-选择
    basis: source-report
  - id: s2
    ref: ./ruyi-20260615-01.md#ice-server-配置
    basis: source-report
  - id: s3
    ref: ./ruyi-20260615-01.md#候选采集函数
    basis: source-report
  - id: s4
    ref: ./ruyi-20260615-01.md#candidate-解析逻辑
    basis: source-report
  - id: s5
    ref: ./ruyi-20260615-01.md#stunturn-结果选择
    basis: source-report
  - id: s6
    ref: ./ruyi-20260615-01.md#webrtc-ip-地理位置查询
    basis: source-report
  - id: s7
    ref: ./ruyi-20260615-01.md#fpfile-改写后的站点可见结果
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2, s3, s4, s5, s6, s7]
    basis: source-report
    limits: 只保留构造器缺失、srflx/relay 分工、5 秒兜底、IP 过滤、mDNS 排除、每类取第一个、出口 IP 对比，以及 candidate 字符串与地址字段一致。不记录地址样值、trace 路径或 TURN 账号字面量。
relations:
  - type: derived_from
    target: ./ruyi-20260615-01.md#stunturn-结果选择
tags: [browserscan, webrtc, source-report]
---

# BrowserScan 页面如何选定 WebRTC 结果

这篇卡检索的是：该文还原的页面脚本把哪一类 candidate 当成 STUN 或 TURN，以及缺字段时写成什么。不提供地址样值，也不写浏览器源码补丁。

<a id="risk-control"></a>
## 结果选择

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 没有构造器就结束：没有可用构造器时，页面直接认为 WebRTC STUN/TURN 不可用。 | s1，源文件第 82 行 | source-report | 标准名和 moz、webkit 别名都没有时 | 不是网络失败 |
| C2 | 第一组的用途：作为页面显示的 WebRTC STUN IP。 | s2，源文件第 93 行 | source-report | 第一组取 srflx | 第二组取 relay；账号字面量不在本卡 |
| C3 | 超时兜底：最长等待 5 秒，超时后用已收集到的 candidate 或 SDP 兜底。 | s3，源文件第 114 行 | source-report | 采集函数 | 这是页面行为，不是操作失败出口 |
| C4 | 只收 IP：是 IPv4 或 IPv6 的 candidate 放入结果分组。 | s4，源文件第 134 行 | source-report | candidate 字符串按空格切开之后 | 不抄样例地址 |
| C5 | mDNS 不进最终值：candidate 不会进入 | s4，源文件第 135 行 | source-report | 上一行点名的 .local host | 本行接 stun/turn 最终值 |
| C6 | 每类只取第一个，键名是 stunResult.srflx[0] | s5，源文件第 148 行 | source-report | STUN 结果 | 下一行对 relay 同样取第一个，否则 disabled |
| C7 | 地理查询的用途：并与页面出口 IP 进行对比。 | s6，源文件第 192 行 | source-report | 已经选出 WebRTC IP 之后 | 查询 URL 和当次 IP 不在本卡 |
| C8 | 字段要一致：必须至少保证 candidate 字符串与 candidate 地址字段一致 | s7，源文件第 258 行 | source-report | 该页可见的 candidate | 下一行才提到 toJSON、SDP、getStats；地址样值不在本卡 |

## 验证与限制

`../../web-reverse/browser-env-objects/fingerprint-overview.md` 的目标是 browser-fingerprint，只列通用宿主对象，没有这套 srflx/relay 选择。本篇第 209 到 211 行写明 address、toJSON 和 getStats 不是这次选出 stun/turn 的必要字段，但可能被扩展读取。trace 行号没有随仓库提供，不能复核。效果描述保持 source-report。
