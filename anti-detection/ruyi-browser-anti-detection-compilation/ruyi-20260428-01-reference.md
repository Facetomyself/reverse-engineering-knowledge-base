---
schema_version: 2
id: ruyi-20260428-gpu-eu-timing-reference
document_type: reference
original_date: '2026-04-28'
archived_date: '2026-10-02'
scope:
  targets: [gpu-eu-timing]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260428-01.md#三实验结果
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留该文转述的同型号区分、跨浏览器相关和追踪时长。没有原始测量向量，不外推到其他 GPU 或当前浏览器计时精度。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留来源对像素噪声、相对速度和禁用 WebGL 的判断。没有本地对照，不能当成当前浏览器的缓解清单。
relations:
  - type: derived_from
    target: ./ruyi-20260428-01.md#三实验结果
tags: [gpu-eu-timing, source-report]
---

# GPU 执行单元时序的来源边界

这篇卡检索的是：该文转述的 DrawnApart 在同型号设备和追踪时长上写了什么，以及它把哪些防御写成无效。不收录着色器正文，也不收录自动化绕过建议。

<a id="risk-control"></a>
## 来源报告的区分与追踪

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 同型号结论：传统指纹对同型号设备完全失效，DrawnApart可以区分。 | s1，源文件第 181 行 | source-report | 文中受控同型号组 | 准确率表未复核 |
| C2 | 跨浏览器：不同浏览器上采集的指纹高度一致 | s1，源文件第 187 行 | source-report | 同一台设备上的 Chrome、Firefox、Edge、Brave | 没有原始向量 |
| C3 | 相关系数：跨浏览器的指纹相关系数：0.93-0.97（1.0=完全一致） | s1，源文件第 189 行 | source-report | 该文的跨浏览器对照 | 不是标识原值 |
| C4 | 追踪时长：中位追踪时间从17.5天提升到29.3天——延长了67%。 | s1，源文件第 219 行 | source-report | FP-Stalker 加上长向量的那一档 | 众包转述，未复现 |
| C5 | 一次比对：在FPR=1%的标准下（每100次比对有1次误判），67%的设备可以被正确识别。 | s1，源文件第 254 行 | source-report | 文中 2504 台设备的孪生网络测试 | 不外推到其他阈值 |

<a id="decision-flow"></a>
## 来源写下的防御边界

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 噪声加在像素上：DrawnApart测量的不是渲染  ** 结果  ** （像素值），而是渲染  ** 时间  ** ——噪声加在像素上不影响执行时间的测量 | s1，源文件第 319 行 | source-report | 该文对渲染结果加噪的讨论 | 未测当前浏览器 |
| C7 | Farbling：Farbling是给Canvas和WebGL的渲染输出加随机噪声，但DrawnApart测量的是渲染时间而不是渲染结果。 | s1，源文件第 403 行 | source-report | 该文对 Brave Farbling 的判断 | 不是 Farbling 实现分析 |
| C8 | 温度：论文使用  ** 相对速度  ** （每个EU的时间 / 所有EU的平均时间）而不是绝对速度。 | s1，源文件第 282 行 | source-report | 该文的温度噪声处理 | 没有温度曲线 |
| C9 | 彻底防御的来源原话：唯一彻底的防御是：  ** 禁用WebGL  ** 。 | s1，源文件第 340 行 | source-report | 该文的结论句 | 不评估禁用后的站点兼容性 |

## 验证与限制

`webgl` 与 `canvas` 的已有 risk-control 是宿主对象语义，`browser-fingerprint` 是通用指纹总纲，`drawnapart` 与 `gpu-eu-timing` 下没有同模块卡片。它们都不覆盖这组同型号追踪数字和“像素噪声不影响执行时间”的来源判断。第二节的着色器与 stall 参数、第六节给自动化的窗口和设备轮换，都不进入本卡。所有数字保持 source-report。
