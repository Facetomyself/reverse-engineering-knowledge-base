---
schema_version: 2
id: anti-detection-ruyi-wasm-cpu-timing-fingerprint-reference
document_type: reference
original_date: '2025-11-12'
archived_date: '2026-07-13'
scope:
  targets: [wasm-cpu-timing-fingerprint]
  client: browser
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20251112-01.md#五如意对风控和检测的思考anti-fraud--fingerprint-evasion
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只整理来源对一篇未具名论文的转述。不含微基准源码、计时器 API、样本、模型、阈值或对抗实现。文中数字不是本次测量。
relations:
  - type: derived_from
    target: ./ruyi-20251112-01.md#五如意对风控和检测的思考anti-fraud--fingerprint-evasion
tags: [wasm, timing-fingerprint, risk-control, source-report]
---

# Wasm 微基准时序作为硬件层指纹信号

这张卡只回答一个检索问题：来源把 WebAssembly 执行时间分布说成哪一种传统 JS API 改写盖不住的硬件层指纹，以及它点到哪些检测和对抗方向。它不提供基准程序、计时实现或分类器。

<a id="risk-control"></a>
## 风险控制信号

来源把信号定义成：不读取浏览器属性，而是测量编译为 Wasm 的微基准执行时间分布，用来反映 CPU 微架构差异。Canvas、WebGL、AudioContext、Navigator 被来源归为容易被指纹浏览器改写的一层。论文题名、作者、实验代码和浏览器版本都不在正文里。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源写「WebAssembly 能深入  CPU 微架构层（如缓存、流水线、时钟偏移）  ，难以伪造。」 | s1，ruyi-20251112-01.md:70 | source-report | 来源对 Wasm 时序相对 JS API 改写的边界 | 没有探针或对照实验 |
| C2 | 来源摘录「We designed a set of 20 microbenchmarks in C and compiled them to」，并用高精度计时器测执行时间分布 | s1，ruyi-20251112-01.md:77 | source-report | 来源转述的方法类别 | 20 个基准没有逐项列出，计时 API 未命名 |
| C3 | 来源摘录「Our evaluation shows that the Wasm-based fingerprint achieves 93.1% device」 | s1，ruyi-20251112-01.md:116 | source-report | 来源摘录的论文结果 | 不是本次测量，也没有数据集 |
| C4 | 来源摘录「2.3× more entropy (14.5 bits vs 6.3 bits).」 | s1，ruyi-20251112-01.md:121 | source-report | 来源摘录的熵比较 | 不是本次测量 |
| C5 | 来源摘录「provide limited or no protection against Wasm-based timing fingerprints.」 | s1，ruyi-20251112-01.md:154 | source-report | 来源点名的防护有限类别 | 没有浏览器版本或复测 |
| C6 | 来源写「目前许多“反指纹浏览器”通过修改 JS API 属性欺骗检测，但无法伪造底层硬件时序」 | s1，ruyi-20251112-01.md:168 | source-report | 来源对 JS API 改写的边界 | 作者判断，无测量 |
| C7 | 来源建议「在 Canvas / Audio / WebGL 基础上，可增加 Wasm 时序测试模块，用来检测 CPU 真伪、虚拟化特征、沙盒执行差异。」 | s1，ruyi-20251112-01.md:183 | source-report | 来源的检测侧设想 | 没有采集字段、窗口或判定规则 |
| C8 | 来源写非原生硬件时「其 Wasm 任务的执行分布与真实设备不同，可作为高置信度识别信号。」 | s1，ruyi-20251112-01.md:184 | source-report | 来源点名的云、虚拟机、Docker、RDP 类别 | 无分布距离或阈值 |
| C9 | 来源建议「将 Wasm 微基准测试嵌入风控 SDK，收集执行时间分布，用机器学习模型（如 SVM/Random Forest）区分正常 vs 模拟环境。」 | s1，ruyi-20251112-01.md:186 | source-report | 来源的采集设想 | 无特征、模型或样本 |
| C10 | 来源列出的对抗方向是「1）为 Wasm 引入随机噪声计时器；2）在浏览器层屏蔽高精度计时器；3）虚拟化 CPU 行为一致化。」 | s1，ruyi-20251112-01.md:187 | source-report | 来源命名的防御类别 | 没有噪声分布、计时器开关或一致化做法 |
| C11 | 来源写「如意现在没想到好办法。」 | s1，ruyi-20251112-01.md:110 | source-report | 作者自述的对抗空白 | 不补写伪造方法 |

## 验证与限制

正文没有可执行步骤、操作者输出、验收条件和失败出口，所以不升为流程。作者写现在没有想到伪造办法，本卡不补对抗实现。`../../web-reverse/browser-env-objects/fingerprint-overview.md` 的 risk-control 只覆盖宿主对象状态组，不包含上述 Wasm 微基准时序，因此不并入该卡。Wasm 解密 loader 与 JS fallback 版本卡处理的是模块加载和版本绑定，也不是这个目标。
