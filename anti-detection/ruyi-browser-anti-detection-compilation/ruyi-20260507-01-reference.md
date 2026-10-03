---
schema_version: 2
id: ruyi-20260507-ruyijs-runtime-reference
document_type: reference
original_date: '2026-05-07'
archived_date: '2026-10-02'
scope:
  targets: [ruyijs]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260507-01.md#下一代js补环境新方案-纯浏览器js引擎和环境抽离运行
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只保留真实引擎、整份 DOM、对应网络库，以及不用 vm2、指纹走替换接口这两句。不记录单站脚本、浏览器标识或会话材料。
relations:
  - type: derived_from
    target: ./ruyi-20260507-01.md#下一代js补环境新方案-纯浏览器js引擎和环境抽离运行
tags: [ruyijs, source-report]
---

# ruyijs 运行时边界

这篇卡检索的是：来源把这套补环境运行时说成什么，以及它没有说清的接口。不提供单站采集步骤。

<a id="interfaces"></a>
## 运行时说了什么

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C1</td><td>运行时被写成：核心是把  浏览器的JS引擎+全部的DOM环境拿了下来  ，再用对应的浏览器网络库请求即可。</td><td>s1，源文件第 35 行</td><td>source-report</td><td>该文对 ruyijs 的运行时宣称</td><td>没有抽出步骤或网络库字段</td></tr>
<tr><td>C2</td><td>和沙盒分开：不再使用node的vm2之类的这种沙盒，采用真实原生的浏览器JS引擎和环境来跑代码生成参数，核心的指纹开接口进行替换。</td><td>s1，源文件第 37 行</td><td>source-report</td><td>相对 node vm2 的选择</td><td>替换接口没有字段表</td></tr>
<tr><td>C3</td><td>作者自述输入输出：使用1小时6分钟自动补完房地产的瑞数，直接把HTML和JS放进去就能出结果</td><td>s1，源文件第 39 行</td><td>source-report</td><td>文中的瑞数示例</td><td>不是验收条件</td></tr>
</table>

## 验证与限制

`ruishu` 已有卡片覆盖挑战页、两阶段会话和业务请求前刷新，不在这里重写。`iv8` 是 Python 内嵌 V8 的另一套 host bridge。`browser-fingerprint` 只列宿主对象检测面。后文单站脚本不进入本卡。成功用时保持 source-report。
