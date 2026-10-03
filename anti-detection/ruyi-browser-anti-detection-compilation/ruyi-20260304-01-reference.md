---
schema_version: 2
id: ruyi-20260304-wechat-miniprogram-fingerprint-reference
document_type: reference
original_date: '2026-03-04'
archived_date: '2026-07-13'
scope:
  targets: [wechat-miniprogram-fingerprint]
  client: wechat-miniprogram
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260304-01.md#二检测方法拆解muffin
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留来源对 Cat. III、无权限 API、模板集成和反向索引失效的转述。不收录测试字符串、反向词表或 URL。未对照当前基础库。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留 MUFFIn 的边类型和作者写明的漏检。批量阈值是作者猜测。没有 JAW 样例，不能当成可跑的判定器。
relations:
  - type: derived_from
    target: ./ruyi-20260304-01.md#二检测方法拆解muffin
tags: [wechat-miniprogram, fingerprint, source-report]
---

# 微信小程序无权限指纹面与 MUFFIn 判定边界

这张卡只回答一个检索问题：来源转述的论文把哪些无需权限的小程序 API 当成指纹面，MUFFIn 怎样从依赖图边判断批量访问，以及它明确漏掉什么。不提供检测器实现，也不把家族占比当成可复现结果。

<a id="risk-control"></a>
## 无权限指纹面

来源把信号放在 Cat. III：单独不敏感、组合后可识别设备。12 个无需权限的 API 分设备信息与 Canvas 导出。京东 Kepler 和有赞 vendor.js 被写成模板自带，而不是商家现写。反向索引让 AST 看不到 canvas 这个名字。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | Cat. III的数据虽然单独看不敏感，但组合起来可以做设备指纹识别。 | s1，ruyi-20260304-01.md:67 | source-report | 来源对微信小程序权限分层的转述 | 没有本地小程序样本 |
| C2 | 识别出20个可以用于指纹追踪的API，其中12个不需要任何权限： | s1，ruyi-20260304-01.md:96 | source-report | 来源列出的设备信息与渲染 API | 未对照当前基础库 |
| C3 | 16/30（53.3%）的高频案例来自京东小程序开放平台（JD Miniprogram Open Platform）。 | s1，ruyi-20260304-01.md:195 | source-report | 来源的 50 个 case study | 未复核样本 |
| C4 | 指纹逻辑打包在  ` vendor.js  ` 中 | s1，ruyi-20260304-01.md:202 | source-report | 来源点名的有赞模板 | 没有文件版本 |
| C5 | 指纹追踪不是个体开发者实现的，而是通过第三方库/模板集成的。 | s1，ruyi-20260304-01.md:208 | source-report | 来源对高频家族的判断 | 不是全量小程序结论 |
| C6 | 不同设备的Canvas渲染会有微小差异（字体渲染、抗锯齿算法、颜色空间），导致哈希值不同，从而可以识别设备。 | s1，ruyi-20260304-01.md:232 | source-report | 来源对绘制后导出再哈希的解释 | 未复现。不收录测试字符串 |
| C7 | AST分析看到的是  ` s(24)  ` ，无法知道这是"canvas" | s1，ruyi-20260304-01.md:267 | source-report | 来源描述的反向索引案例 | 不抄反向词表 |

<a id="decision-flow"></a>
## MUFFIn 判定

来源的流程是：先用 fingerprint 关键词收候选，再用 JAW 的 invocation、parameter、element 边回溯 API 和参数，element 边要展平嵌套数组。批量阈值正文没有给出。动态代码、混淆和 WebView 被写成漏检。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 搜索包含"fingerprint"关键词的脚本，得到1,367个候选。 | s1，ruyi-20260304-01.md:126 | source-report | 来源的语义过滤 | 召回率未给出 |
| C9 | 如果边类型是invocation，记录API名称 + 上下文AST节点类型 | s1，ruyi-20260304-01.md:141 | source-report | JAW 依赖图上的调用边 | 没有输出样例 |
| C10 | 如果边类型是element，说明参数是在数组中批量声明的（如Figure 1），需要展平嵌套数组 | s1，ruyi-20260304-01.md:143 | source-report | 来源 Figure 1 那种数组声明 | 只有深度优先这一句 |
| C11 | 论文没有明确阈值，但从结果看应该是≥3个 | s1，ruyi-20260304-01.md:152 | source-report | 作者对批量计数的猜测 | 不能当成论文规则 |
| C12 | 只能检测静态声明的API调用，无法检测动态生成的代码（如  ` eval  ` 、  ` Function  ` ） | s1，ruyi-20260304-01.md:337 | source-report | MUFFIn 的静态范围 | 未用动态样本验证 |
| C13 | 无法检测混淆（TalkingData案例就是漏网之鱼） | s1，ruyi-20260304-01.md:338 | source-report | 来源点名的混淆案例 | 检测器本身并未命中该案例 |
| C14 | 无法检测通过WebView加载的外部网页 | s1，ruyi-20260304-01.md:339 | source-report | 小程序内嵌 H5 | 没有 WebView 样本 |

## 验证与限制

`canvas` 与 `browser-fingerprint` 的 risk-control 只写通用 Web 宿主对象，不包含上述小程序 API 和边类型，因此不并入。第四节的平台建议没有验收和失败出口，不升为流程。1310、285 和 53.3% 保持来源数字。
