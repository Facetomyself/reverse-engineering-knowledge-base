---
schema_version: 2
id: thresholdfp-link-reference
document_type: reference
original_date: '2026-03-30'
archived_date: '2026-10-02'
scope:
  targets: [thresholdfp]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260330-01.md#thresholdfp的方案
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 分数公式和例子只属于来源转述的机构数据集。原文要求换人群后重算，不能把 9.6 或 94.63 当成通用权重。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 关联比较的是同一用户的活跃指纹。分数不区分属性值语义。没有失败出口，不能当部署流程。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 机构集只有估计精确率。志愿者集的真实精确率不能外推。未与混合算法对比，也没有对抗样本。
relations:
  - type: derived_from
    target: ./ruyi-20260330-01.md#thresholdfp的方案
tags: [thresholdfp, source-report]
---

# ThresholdFP 的阈值关联边界

这篇卡检索的是：来源如何用属性变化分、累积分和阈值决定两条浏览器指纹是否连成一条链，以及哪些数据集数字不能当成真值。不收录如何把差异分抬过阈值。

<a id="parameters"></a>
## 属性分数

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C1</td><td>分数 = 100 - 变化百分比</td><td>s1，源文件第 91 行</td><td>source-report</td><td>来源对 Algorithm 2 的转述</td><td>变化次数要按自己的指纹对重算</td></tr>
<tr><td>C2</td><td>` userAgent  ` ：分数9.6</td><td>s1，源文件第 96 行</td><td>source-report</td><td>机构数据集例子</td><td>不是通用权重，也不是指纹原值</td></tr>
<tr><td>C3</td><td>` timezone  ` ：分数94.63</td><td>s1，源文件第 98 行</td><td>source-report</td><td>机构数据集例子</td><td>同段还有 canvas 20.08 与 indexedDB 99.99</td></tr>
<tr><td>C4</td><td>属性分数需要用你自己的数据校准</td><td>s1，源文件第 269 行</td><td>source-report</td><td>来源的部署建议</td><td>建议本身没有校准结果</td></tr>
</table>

<a id="decision-flow"></a>
## 关联与修复

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C5</td><td>所有变化属性的分数之和如果没超过阈值，就把它们关联起来。</td><td>s1，源文件第 81 行</td><td>source-report</td><td>来源对方案的概括</td><td>正式差异分还要加累积分</td></tr>
<tr><td>C6</td><td>差异分数 =  ` fp_active  ` 的累积分数 + 所有变化属性分数之和</td><td>s1，源文件第 109 行</td><td>source-report</td><td>同一用户的活跃指纹</td><td>不是全库最近邻</td></tr>
<tr><td>C7</td><td>如果差异分数 < 阈值，  ` fp_active  ` 成为候选关联目标</td><td>s1，源文件第 110 行</td><td>source-report</td><td>候选筛选</td><td>阈值没有唯一值</td></tr>
<tr><td>C8</td><td>在所有候选中选择差异分数最小的（min变体）</td><td>s1，源文件第 111 行</td><td>source-report</td><td>来源后续采用的变体</td><td>max 与 earliest 未被写成失效</td></tr>
<tr><td>C9</td><td>如果阈值是40，这次关联就会被拒绝</td><td>s1，源文件第 115 行</td><td>source-report</td><td>累积分防漂移的例子</td><td>30 加 20 不是测量值</td></tr>
<tr><td>C10</td><td>断开错误的父子链接</td><td>s1，源文件第 122 行</td><td>source-report</td><td>过时指纹重新出现时</td><td>还要扣回累积分并回到活跃集合</td></tr>
<tr><td>C11</td><td>没有考虑属性值的语义信息</td><td>s1，源文件第 223 行</td><td>source-report</td><td>来源承认的算法限制</td><td>小版本和跨浏览器会得到同一属性分</td></tr>
</table>

<a id="validation"></a>
## 来源报告的结果

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C12</td><td>40  |  ** 55.7  ** |  ** >98%  **</td><td>s1，源文件第 171 行</td><td>source-report</td><td>机构数据集、估计精确率</td><td>没有浏览器级真值</td></tr>
<tr><td>C13</td><td>32  |  ** 50.1  ** |  ** 99.5%  ** |  ~80%</td><td>s1，源文件第 182 行</td><td>source-report</td><td>志愿者数据集这一行</td><td>未与混合算法对比</td></tr>
<tr><td>C14</td><td>真实精确率从不低于99%，但估计精确率在高阈值下跌到70%。</td><td>s1，源文件第 185 行</td><td>source-report</td><td>志愿者数据集</td><td>不能用来改写机构集的估计精确率</td></tr>
</table>

## 验证与限制

`browser-fingerprint` 的 parameters、decision-flow、validation 没有卡片；其 risk-control 是宿主对象总纲。`fp-stalker` 与 `fingerprint-linking` 也没有 decision-flow 卡片。移动端被排除，隐私浏览器未测。越过阈值的做法不在本卡。所有数字保持 source-report。
