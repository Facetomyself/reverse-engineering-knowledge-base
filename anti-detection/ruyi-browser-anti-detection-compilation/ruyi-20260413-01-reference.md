---
schema_version: 2
id: ruyi-20260413-free-http-proxy-reference
document_type: reference
original_date: '2026-04-13'
archived_date: '2026-10-02'
scope:
  targets: [free-http-proxy]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260413-01.md#每日测试流程
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留来源转述的三步日检：5 秒连通、固定页面比对、三类头。不包含注入样本，也不把漏洞编号写成利用步骤。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 比例只对应文中 2021-01 至 2023-06、64 万余条免费代理转述。HTTPS 降级没有计数。
relations:
  - type: derived_from
    target: ./ruyi-20260413-01.md#每日测试流程
tags: [free-http-proxy, source-report]
---

# 免费 HTTP 代理的日检与存活边界

这篇卡检索的是：该文转述的纵向测量里，一条免费代理怎样被标成活跃、篡改或暴露真实地址，以及存活和篡改比例被写成多少。不提供注入样本，也不提供漏洞利用。

<a id="decision-flow"></a>
## 每天怎么标一条代理

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 连通只看自己的测试机：如果代理在5秒内转发了请求，标记为"活跃"。 | s1，源文件第 102 行 | source-report | 每日 HTTP GET | 超时即非活跃，没有重试口径 |
| C2 | 篡改基线是固定页：测试服务器返回一个固定的HTML页面（包含特定的标记字符串）。 | s1，源文件第 106 行 | source-report | 与直连响应比对 | 只覆盖该测试页 |
| C3 | 正文改动即篡改：如果响应内容被修改（注入了额外的HTML/JavaScript/广告），标记为"内容篡改" | s1，源文件第 108 行 | source-report | 响应体 | 不区分广告与脚本的利用方式 |
| C4 | 头改动也算：如果响应头被修改（添加/删除了某些HTTP头），也标记为"内容篡改" | s1，源文件第 109 行 | source-report | 响应头 | 没有列出哪些头算正常跳变 |
| C5 | 露出真实地址的一类：透明代理（Transparent）  ** ：暴露了用户真实IP | s1，源文件第 121 行 | source-report | 来源写的三类之一 | 高匿类仍能看见明文 HTTP |

判类所用的头，来源写在第 115 到 117 行：`X-Forwarded-For` 对应透明，`Via` 与 `Proxy-Connection` 对应暴露代理存在。三类定义在第 121 到 123 行。这里不展开后文的页面改写样本。

<a id="risk-control"></a>
## 来源给出的比例

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 大多数名单条目没有活过：640,600个代理中，只有221,007个（34.5%）在30个月的测试期间至少有一次成功响应。 | s1，源文件第 140 行 | source-report | 11 个名单、30 个月 | 不是当前名单的可用率 |
| C7 | 活跃集合里的篡改面：16,923个代理（占活跃代理的7.7%）在修改通过它们的HTTP响应内容。 | s1，源文件第 225 行 | source-report | 至少成功响应过的子集 | 一个代理可兼多种改写，类型比例不能相加 |
| C8 | 匿名度的最大桶原文是透明代理（暴露真实IP），同一行记 ~52%。 | s1，源文件第 296 行 | source-report | 活跃代理 | 同行另有匿名与高匿两桶，本格只钉透明桶 |

## 验证与限制

`free-http-proxy` 的 decision-flow 与 risk-control 在已发布卡里没有命中。`browser-fingerprint` 只讲宿主对象，不覆盖这次代理日检。MikroTik 与 CVE 编号只说明来源把大量节点记在该设备上，不进入本卡的步骤。广告、挖矿和图片外带三段是攻击样本，不进入本卡。第五节的使用建议没有验收和失败出口，所以不是流程。比例保持 source-report。
