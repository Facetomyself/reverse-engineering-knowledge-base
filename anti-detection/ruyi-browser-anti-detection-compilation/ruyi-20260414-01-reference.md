---
schema_version: 2
id: ruyi-20260414-bandwidth-sharing-proxy-reference
document_type: reference
original_date: '2026-04-14'
archived_date: '2026-10-02'
scope:
  targets: [bandwidth-sharing-proxy]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260414-01.md#五从网络运营商视角的检测建议
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留来源对家庭基线与自愿带宽应用节点的流量、连接差异。不包含案例里的绕过理由或请求伪装清单。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 心跳和 DNS 是来源提出的运营商侧信号，没有阈值、误报出口或可执行规则。黑名单交叉只用于给历史明文请求贴标。
relations:
  - type: derived_from
    target: ./ruyi-20260414-01.md#五从网络运营商视角的检测建议
tags: [bandwidth-sharing-proxy, source-report]
---

# 自愿带宽应用的运营商侧差异

这篇卡检索的是：该文转述的受控节点里，家庭流量和自愿安装的带宽共享应用在哪些模式上被写成不同，以及运营商侧还能靠什么名单做对照。不提供把住宅出口用于欺诈或页面伪装的做法。

<a id="risk-control"></a>
## 和家庭基线相比差在哪

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 时间不落在作息上：24小时持续活跃  ** （代理应用在后台持续运行） | s1，源文件第 352 行 | source-report | 来源对比的家庭昼夜模式 | 真实家庭若有长期在线设备会靠近这条 |
| C2 | 方向反了：上行流量异常高  ** （代理需要把请求转发出去） | s1，源文件第 353 行 | source-report | 相对以下行为主的家庭 | 没有给出上行倍数 |
| C3 | 目的地不收敛：访问的域名极度分散  ** （代理流量来自不同的客户，目标各不相同） | s1，源文件第 354 行 | source-report | DNS 与 TLS 名称 | 85% 加密，看不见路径和正文 |
| C4 | 连接很碎：短连接比例高  ** （很多代理请求是一次性的短连接） | s1，源文件第 368 行 | source-report | 相对家庭里较固定的长连接 | 没有并发数阈值 |

<a id="decision-flow"></a>
## 运营商侧还能对什么

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 控制面先看固定目的地：心跳包的目标IP/域名是固定的 | s1，源文件第 375 行 | source-report | 文中 8 个应用的控制流量 | 名单本身没有写进本篇 |
| C6 | DNS 也可以单列：某些代理应用会使用特定的DNS服务器（可以作为检测信号） | s1，源文件第 386 行 | source-report | 与域名数量、类型分散并列 | 没有服务器名字 |
| C7 | 明文里的已知坏域名用名单贴标：论文把所有HTTP请求的目标域名和以下黑名单做了交叉比对： | s1，源文件第 194 行 | source-report | 测试床上的明文 HTTP | 随后点名的三份名单不覆盖加密流量 |

第 196 到 198 行把交叉名单写成 PhishTank、OpenPhish 和 Safe Browsing。这是事后贴标，不是一条上线规则。

## 验证与限制

`bandwidth-sharing-proxy` 的 risk-control 与 decision-flow 没有已发布卡。住宅出口重叠、TLS 分裂和移动 SDK 归因是别的文章，而且目录里还没有同一目标的模块。案例一到三里的频率、地理伪装和库存占用只说明来源看见了哪些滥用类型；其中的绕过理由和请求伪装清单不进入本卡。测试床没有家庭背景流量，第 449 行写明约 85% 为加密，内容结论不能外推。效果数字保持 source-report。
