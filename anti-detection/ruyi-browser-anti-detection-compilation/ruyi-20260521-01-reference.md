---
schema_version: 2
id: android-proxy-sdk-attribution-reference
document_type: reference
original_date: '2026-05-21'
archived_date: '2026-10-02'
scope:
  targets: [android-proxy-sdk-attribution]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260521-01.md#四最关键的是防止背题dex-grouped交叉验证
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留图结构指标、capa 变差、控制流占比和 APKPure 留存的转述。没有特征名、样本哈希或模型文件。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留 DEX 分组约束和自动 YARA 低于图模型的对照。没有训练脚本，也没有规则正文。
relations:
  - type: derived_from
    target: ./ruyi-20260521-01.md#四最关键的是防止背题dex-grouped交叉验证
tags: [android-proxy-sdk, source-report]
---

# Android 住宅代理 SDK 的静态归因边界

这篇卡检索的是：笔记转述的图核论文如何避免 DEX 泄漏，以及只用代码结构时四家族归因报到什么水平。不提供训练或规则生成步骤。

<a id="decision-flow"></a>
## 怎么切分、规则落到哪

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 只要两个APK共享任意DEX文件，它们就被归到同一个group。交叉验证时，同一个group只能出现在训练集或测试集的一边，不能同时出现。 | s1，源文件第 197 行 | source-report | 这篇笔记的 DEX-grouped 5 折 | 没有实现 |
| C8 | 总体F1：  ** 0.644  ** | s1，源文件第 284 行 | source-report | 过滤跨家族字符串之前的自动 YARA | 不是图模型分数 |
| C9 | 总体F1：  ** 0.7704  ** | s1，源文件第 294 行 | source-report | 过滤之后的自动 YARA | 仍低于图模型，且没有规则正文 |

<a id="risk-control"></a>
## 结构特征能分开什么

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C2 | 闭集四分类 macro-F1：  ** 0.985 ± 0.022  ** | s1，源文件第 222 行 | source-report | 3365 个样本、只用图结构的 SGD | DEX-grouped 转述 |
| C3 | open-world五分类 macro-F1：  ** 0.977 ± 0.011  ** | s1，源文件第 223 行 | source-report | 另加 1000 个普通 App | 不是全量开放世界 |
| C4 | 闭集 macro-F1：  ** 0.932  ** | s1，源文件第 232 行 | source-report | 笔记所称 WL 加 capa 的扩展集闭集 | 不能与第 222 行互换 |
| C5 | 最重要的特征大多来自控制流图，而不是函数调用图。 | s1，源文件第 248 行 | source-report | SHAP/LIME 解释 | 没有特征名 |
| C6 | SHAP的Top 10特征里，7个来自控制流图，3个来自函数调用图。 | s1，源文件第 250 行 | source-report | SHAP Top 10 | 只这一组 |
| C7 | 51.4% 仍然被分类为原来的代理家族。 | s1，源文件第 315 行 | source-report | APKPure 上仍可分析的 576 个包 | 不是 Play 全量 |

## 验证与限制

`android-app-device-fingerprint` 没有 DEX 分组或图核指标。`mobile-proxy` 还没有卡片，出口侧黑名单边界不在本卡。动态加载和混淆只作为笔记自己的扣分，没有失败出口，所以不建流程。数字保持 source-report。
