---
schema_version: 2
id: ruyi-20260322-browser-polygraph-reference
document_type: reference
original_date: '2026-03-22'
archived_date: '2026-10-02'
scope:
  targets: [browser-polygraph]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ruyi-20260322-01.md#核心思路不追踪用户只检测浏览器是否在说谎"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留该文转述的原型属性个数特征和 6 毫秒、1KB 约束。28 个特征的逐项名单不在正文，Table 8 未附。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 检测边界和部署数字都是来源对论文的转述。没有会话样本，不能外推到文中未点名的浏览器。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 风险因子公式按来源原文收录。没有重训数据或阈值校准，不能直接当线上规则。
relations:
  - type: derived_from
    target: "./ruyi-20260322-01.md#核心思路不追踪用户只检测浏览器是否在说谎"
tags: [browser-polygraph, source-report]
---

# Browser Polygraph 的原型属性数量与 UA 对照

这篇卡检索的是：该文转述的 Browser Polygraph 用哪些原型属性个数对照 user-agent，哪些反指纹浏览器类别在来源里被写成可检或不可检，以及风险因子怎么从聚类距离算出来。不收录自动化侧的降风险清单。

<a id="parameters"></a>
## 特征与采集约束

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 特征形状是原型自有属性个数：Object.getOwnPropertyNames(Element.prototype).length | s1，源文件第 107 行 | source-report | 该文举出的 28 个同类特征 | 正文只举例，没有 Table 8 全表 |
| C2 | 筛完后的构成：最终保留22个偏差特征 + 6个时间特征 = 28个特征。 | s1，源文件第 181 行 | source-report | FinOrg 上从 513 个候选筛到的这一组 | 筛选依赖人工，换浏览器世代要重做 |
| C3 | 采集预算写成 ** 6毫秒  ** ，同一行还有 ** 1KB  ** | s1，源文件第 81 行 | source-report | 该文对比表里的 Browser Polygraph 行 | 未复测耗时或字节数 |
| C4 | 这组特征故意很粗：只有0.3%是唯一的 | s1，源文件第 116 行 | source-report | 该文对 20.5 万指纹的隐私分析 | 不能当成用户追踪标识 |

<a id="risk-control"></a>
## 能检与不能检

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 会换引擎的一类被写成检不出：Browser Polygraph对这类浏览器无效。 | s1，源文件第 142 行 | source-report | 来源标成 Category 3 的 AdsPower 较新版本 | 没有版本边界的独立核对 |
| C6 | 来源总结可检范围：Browser Polygraph能检测Category 1和2的反指纹浏览器 | s1，源文件第 163 行 | source-report | 该文点名并分入 1、2 类的产品 | 同句写明 Category 3 和 4 无效 |
| C7 | 同聚类版本会漏：如果user-agent也设成Chrome 63-65这种同聚类的版本，就检测不出来。 | s1，源文件第 259 行 | source-report | Sphere 1.3 那次私有站实验的漏检解释 | 聚类表会随重训改变 |
| C8 | 漂移例：聚类号从1变到了10 | s1，源文件第 275 行 | source-report | Firefox 119 的 Element 原型变化 | 来源据此写大约 3.5 个月要重训 |

<a id="decision-flow"></a>
## 风险因子

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C9 | 厂商对不上取最大：风险因子 = 20（最大值） | s1，源文件第 215 行 | source-report | 声称厂商与聚类厂商不同 | 只是来源转述的打分，不是当前阈值 |
| C10 | 同厂商看版本差：风险因子 = abs(版本差) / 4 | s1，源文件第 217 行 | source-report | 厂商相同但版本差距较大 | 同段还写取所有可能匹配里的最小距离 |

## 验证与限制

`browser-fingerprint` 的风险控制卡只建模 navigator、canvas、字体和 `performance.now` 等宿主对象，不覆盖原型属性个数与 user-agent 聚类。`browser-polygraph` 目标下没有已有卡片。正文后部给风控的四步没有验收和失败出口，给自动化的降风险清单不进入本卡。聚类精度、召回和 ATO 倍数均保持 source-report。
