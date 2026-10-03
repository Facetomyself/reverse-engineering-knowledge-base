---
schema_version: 2
id: anti-detection-ruyi-webgpu-atomic-scheduling-fingerprint-reference
document_type: reference
original_date: '2026-03-19'
archived_date: '2026-07-13'
scope:
  targets: [webgpu-atomic-scheduling-fingerprint]
  client: browser
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260319-01.md#论文怎么做的atomicincrement算法
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只整理来源对 WiSec 2025 论文的转述。不含着色器、嵌入模型、阈值或对抗实现。准确率和耗时不是本次测量。
relations:
  - type: derived_from
    target: ./ruyi-20260319-01.md#论文怎么做的atomicincrement算法
tags: [webgpu, atomic-increment, timing-independent, source-report]
---

# WebGPU 原子自增顺序作为不看计时器的硬件指纹

这张卡只回答一个检索问题：来源把 AtomicIncrement 说成哪一种不读取计时器、只记录 GPU 线程调度顺序的设备信号，以及它为什么认为降低 `performance.now` 精度挡不住。它不提供着色器、采集循环或识别模型。

<a id="risk-control"></a>
## 风险控制信号

来源把信号定义成：16384 个计算线程争用同一个原子计数器，数组里留下的排队号就是指纹。它和 DrawnApart 的差别是不依赖每个执行单元的耗时。来源称 Chrome 113 起默认开 WebGPU，Edge 已跟进，Firefox 和 Safari 仍在测试。识别数字来自移动真机转述，桌面端没有直接验证。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源写 AtomicIncrement「只需要5毫秒就能给设备生成一个硬件指纹，在500多台设备中重新识别准确率达到73%。」 | s1，ruyi-20260319-01.md:52 | source-report | 来源对算法类别和报告规模的概括 | 不是本次测量；5 毫秒与后文 4.7 毫秒、1.21 秒不是同一采集量 |
| C2 | 来源写「Chrome从113版开始默认启用WebGPU，Edge也已跟进，Firefox和Safari处于测试阶段。」 | s1，ruyi-20260319-01.md:91 | source-report | 来源点名的浏览器可用面 | 没有具体小版本或开关名 |
| C3 | 来源写每个线程「对原子计数器做自增，然后把自增前的值写入自己对应的数组位置」 | s1，ruyi-20260319-01.md:111 | source-report | 来源描述的三步类别 | 没有着色器或工作组绑定代码 |
| C4 | 来源写「使用128个工作组，每组128个线程，总共16384个线程。生成一条指纹（trace）只需要约4.7毫秒。」 | s1，ruyi-20260319-01.md:117 | source-report | 来源给出的规模 | 不是本次测量，也没有缓冲区布局 |
| C5 | 来源写 AtomicIncrement「完全不关心时间，只看线程的执行顺序，天然免疫」降低计时器精度这类防御 | s1，ruyi-20260319-01.md:136 | source-report | 来源对比 DrawnApart 的边界 | 没有计时器分辨率的复测 |
| C6 | 来源写「而采集这256条指纹只需要1.21秒。用户打开一个网页，不到2秒，网站就有73%的概率准确识别你的设备。Top-10准确率更是达到88.76%」 | s1，ruyi-20260319-01.md:190 | source-report | 来源报告的投票准确率 | 不是本次测量；Top-1 与设备型号差异很大 |
| C7 | 来源写「98.20%的情况下还是能正确识别出GPU型号。也就是说，AtomicIncrement生成的指纹高度GPU特异性，大部分错误发生在"同型号GPU的不同设备"之间，而不是跨GPU型号。」 | s1，ruyi-20260319-01.md:209 | source-report | 来源的错分范围 | 没有型号名单或距离阈值 |
| C8 | 来源写限制计算着色器「不允许线程级别的ID操作，这样AtomicIncrement就拿不到每个线程的执行顺序。」 | s1，ruyi-20260319-01.md:263 | source-report | 来源命名的能力裁剪方向 | 没有 API 限制点或兼容后果的实现 |
| C9 | 来源写「移除计时器（timer）对AtomicIncrement无效——因为它根本不用计时器。」 | s1，ruyi-20260319-01.md:267 | source-report | 来源对既有时序防御的反例 | 不据此补写噪声调度 |
| C10 | 来源写「不同GPU型号之间的可区分度差异很大。实际使用时，硬件指纹应该和其他指纹维度组合使用，而不是单独依赖。」 | s1，ruyi-20260319-01.md:283 | source-report | 来源的使用边界 | 无特征融合规则 |

## 验证与限制

正文没有可执行步骤、操作者输出、验收条件和失败出口，所以不升为流程。来源点名的防御只有四类名称：隐私模式禁用 WebGPU、使用前授权、限制线程级 ID、在调度里加随机性，都没有做法。鲁棒性只转述 7 台手机、3 周，充电和前台占用会加大波动。数据集是移动 GPU，桌面没有直接验证。`../../web-reverse/browser-env-objects/fingerprint-overview.md` 不包含这条调度顺序信号。Chromium WebGPU 归档写的是适配器信息改写，目录目标是 `unknown`，不是原子自增顺序，因此不并入。本卡不写着色器，也不把来源的跨站叙述改成采集流程。
