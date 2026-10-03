---
schema_version: 2
id: ruyi-20260303-wasm-fingerprint-detector-reference
document_type: reference
original_date: '2026-03-03'
archived_date: '2026-07-13'
scope:
  targets: [wasm-fingerprint-detector]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260303-01.md#三对学术检测器的冲击
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留代码特征检测器的 recall 变化、API 层拦截不变、CDP 监控不变，以及纯 WASM 时序例外的粗粒度。不收录转换规则。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留不平衡重训会崩、平衡增强后两组指标相同、单条规则不改变指标。没有可执行步骤或失败出口。
relations:
  - type: derived_from
    target: ./ruyi-20260303-01.md#三对学术检测器的冲击
tags: [wasm, fingerprint-detector, source-report]
---

# JS 指纹脚本转 WASM 后检测器还剩哪一层

这张卡只回答：来源报告里，代码特征检测器和 API 层工具在 WASM 转换前后各变成什么样，以及不调用被监控 API 的时序为什么落在边界外。它不提供转换规则。

<a id="risk-control"></a>
## 检测边界

来源报告 DeepFPD 在自有集上 recall 从 77.78% 降到 44.44%，在新采集集上只从 86.40% 降到 81.28%。FP-Inspector 因依赖不支持 WASM 的 Firefox 52 ESR 而无法处理转换后的脚本。点名的 API 层工具和自写的 CDP 高熵 API 监控不因转换而改变结果。不调用 Canvas、WebGL、Audio 的纯 WASM 时序是例外，且来源写它只能区分 Chromium 与非 Chromium。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源写「DeepFPD的recall从77.78%掉到44.44%（在自己的测试集上），FP-Inspector直接因为依赖Firefox 52 ESR（不支持WASM）而完全失效。」 | s1，ruyi-20260303-01.md:62 | source-report | 来源转述的自有测试集和 FP-Inspector 复现 | 开头把 77.78% 写成 78%；自有集只有 18 个指纹脚本 |
| C2 | 来源写「WASM版本：Accuracy 88.54%, Precision 99.70%,  ** Recall 81.28%  **」 | s1，ruyi-20260303-01.md:161-162 | source-report | 来源的新采集数据集 | 86.40% 在该范围的 JS 版本行 |
| C3 | 来源写「完全不受影响。因为它们在API层拦截（spoofing或blocking），不管底层代码是JS还是WASM。」 | s1，ruyi-20260303-01.md:63 | source-report | 来源点名的 API 层工具 | 不覆盖 C5 的时序例外 |
| C4 | 来源写「WASM转换完全没有影响检测效果。」 | s1，ruyi-20260303-01.md:233 | source-report | 来源自写的 CDP API 监控 | 同段检测率约 28%，只对应已命中的脚本 |
| C5 | 来源写「所有API层防御都失效了。」 | s1，ruyi-20260303-01.md:278 | source-report | 来源点名的纯 WASM 时序 | 不是所有 WASM 程序 |
| C6 | 来源写「它只能区分Chromium和非Chromium浏览器，无法做细粒度的设备识别。」 | s1，ruyi-20260303-01.md:283 | source-report | 同一时序技术的区分度 | 无设备数或熵 |

<a id="decision-flow"></a>
## 重训与消融

直接把 WASM 脚本加进训练集会被来源写成模型崩溃。平衡增强后，JS 与 WASM 测试集指标相同。单独使用任何一条规则都不改变 DeepFPD 指标；指标变化被归因于多条规则一起出现。这里不列出那些规则。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | 来源写「直接把WASM脚本加到训练集会让模型崩溃（accuracy和precision都掉到5-6%，recall保持100%——模型把所有东西都标记为指纹）。」 | s1，ruyi-20260303-01.md:195 | source-report | 来源的不平衡重训 | 只对应这次转述 |
| C8 | 来源写「WASM测试集：Accuracy 98.12%, Precision 87.50%, Recall 77.78%」 | s1，ruyi-20260303-01.md:200-201 | source-report | 来源的平衡增强之后 | 相同三元组在该范围的 JS 测试集行 |
| C9 | 来源写「任何单条规则都无法显著影响检测效果。」 | s1，ruyi-20260303-01.md:289 | source-report | DeepFPD 上的单规则消融 | 不提供规则正文 |
| C10 | 来源写「检测逃避不是某一条规则的功劳，而是多条规则组合的结果。」 | s1，ruyi-20260303-01.md:293 | source-report | 同一消融的归因 | 不提供组合方式 |

## 验证与限制

第二节的转换规则和第六节给追踪方的建议已读过，但不进入这张卡。全文没有前提、输出、验收和失败出口，不升为流程。`fingerprint-overview.md` 与 `canvas-webgl.md` 的 risk-control 只覆盖宿主对象。目标为 wasm 或 webassembly 的 risk-control、以及 wasm 的 interfaces，查询都是 0 条，现有 WASM 解密卡不是这个检测边界。开头的“API 层是唯一有效手段”被 C5 限制，不当成无例外结论。
