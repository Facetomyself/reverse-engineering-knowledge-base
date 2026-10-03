---
schema_version: 2
id: ruyi-20260216-fp-inconsistent-reference
document_type: reference
original_date: '2026-02-16'
archived_date: '2026-10-02'
scope:
  targets: [fp-inconsistent]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260216-01.md#61-核心思路
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留自相矛盾、同一设备 platform 稳定和两家服务实测检测率的转述。不抄分辨率、时区或设备取值。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留分组、人工审核和空间优先于时间的来源步骤。没有驳回条件，不能当成可执行流程。
relations:
  - type: derived_from
    target: ./ruyi-20260216-01.md#61-核心思路
tags: [fp-inconsistent, source-report]
---

# FP-Inconsistent 的不一致检测边界

这篇卡检索的是：该文转述的蜜罐实验里，逃逸流量被说成哪一类矛盾，以及 FP-Inconsistent 在上线前要经过哪几步。不提供伪装清单。

<a id="risk-control"></a>
## 矛盾现象

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C1</td><td>逃逸样本的规律被写成：Bot在伪装指纹时，会在不同属性之间产生"自相矛盾"。</td><td>s1，源文件第 66 行</td><td>source-report</td><td>20 家购买流量的蜜罐转述</td><td>不是通用模型</td></tr>
<tr><td>C2</td><td>跨请求约束：一台真实设备的platform永远不会变！</td><td>s1，源文件第 156 行</td><td>source-report</td><td>同一第一方 Cookie 的多次请求</td><td>单次请求无法使用这条</td></tr>
<tr><td>C3</td><td>服务效果对照原文：实测检测率  |  55.44%  |  47.07%</td><td>s1，源文件第 61 行</td><td>source-report</td><td>表头顺序为 DataDome、BotD</td><td>只覆盖文中的 2023 年 9 到 11 月样本</td></tr>
</table>

<a id="decision-flow"></a>
## 规则怎么形成

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 不按单属性打分：第一步：把指纹属性分成4组 | s1，源文件第 174 行 | source-report | 屏幕、设备、浏览器、位置四组 | 组内取值表不在本卡 |
| C5 | 上线前有人审：第三步：人工审核 → 生成过滤规则 → 部署检测 | s1，源文件第 176 行 | source-report | FP-Inconsistent 的来源步骤 | 没有审核失败出口 |
| C6 | 先做单次请求能看的矛盾：空间不一致是主力，时间不一致是补充。 | s1，源文件第 209 行 | source-report | 文中两家服务的增强对照 | 时间不一致需要重复访问 |

## 验证与限制

`datadome` 已有卡片只覆盖 interstitial 请求链。`browser-fingerprint` 只说宿主对象之间不能矛盾，没有这四组步骤，也没有蜜罐检测率。Android 设备画像卡是另一个客户端。8.2 的属性修改清单不进入本卡。隐私浏览器一节只说明 Tor 被来源写成误判、拦截型扩展没有，这是限制而不是失败出口。效果数字保持 source-report。
