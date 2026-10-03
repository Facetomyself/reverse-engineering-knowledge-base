---
schema_version: 2
id: ruyi-20260618-fingerprint-pro-vm-signal
document_type: reference
original_date: "2026-06-18"
archived_date: "2026-10-02"
scope:
  targets: [fingerprint-pro]
  client: web
  version: unknown
  observed_at: "2026-06-18"
sources:
  - id: s1
    ref: ./ruyi-20260618-01.md#请求链复盘
    basis: source-report
  - id: s2
    ref: ./ruyi-20260618-01.md#一句话结论
    basis: source-report
  - id: s3
    ref: ./ruyi-20260618-01.md#参数敏感性实验
    basis: source-report
  - id: s4
    ref: ./ruyi-20260618-01.md#2-软件渲染与-gpu-回退
    basis: source-report
  - id: s5
    ref: ./ruyi-20260618-01.md#4-服务端-ml规则融合
    basis: source-report
  - id: s6
    ref: ./ruyi-20260618-01.md#本地纯算实现
    basis: source-report
  - id: s7
    ref: ./ruyi-20260618-01.md#前端只负责展示判定来自服务端事件
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s1, s5, s7]
    basis: source-report
    limits: 只保留“布尔值不在页面本地计算、Playground 用 event_id 再查、影响结果的是 identify POST”。不写请求体，不写事件标识。
  - name: risk-control
    anchor: risk-control
    sources: [s2, s3, s4]
    basis: source-report
    limits: 只保留软件渲染不是唯一证据、VMware/SVGA 在该次对照里单独触发、另外几类没有触发、tampering 与布尔值分离、ML 分数不是阈值。不转写设备原值。
  - name: decision-flow
    anchor: decision-flow
    sources: [s5, s6]
    basis: source-report
    limits: 本地 0.6 阈值只属于来源自己的可解释规则。服务端权重未知。
relations:
  - type: derived_from
    target: ./ruyi-20260618-01.md#参数敏感性实验
tags: [fingerprint-pro, source-report]
---

# Fingerprint Playground 的虚拟机结论在服务端

这篇卡检索的是：该文把 virtual_machine 放在哪一次请求里，以及哪一类 WebGL 字符串在来源的对照里会单独改变布尔值。不收录设备原值，也不把本地规则写成官方模型。

<a id="request-chain"></a>
## 结论放在哪一跳

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 页面不算这个字段：不是页面本地计算的字段。 | s7，源文件第 110 行 | source-report | Playground 的展示 chunk | 展示的是服务端事件 JSON |
| C2 | 会改变结果的提交：真正影响结果的是 Fingerprint agent 的 identify POST | s3，源文件第 431 行 | source-report | 已经能拿到 event_id 之后 | 事件查询接口只读已算好的结果 |
| C3 | Playground 自身：event_id 二次查询 + 展示 | s5，源文件第 423 行 | source-report | 页面第二次请求 | 没有模型权重 |

<a id="risk-control"></a>
## 哪些信号被写成会改变布尔值

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 软件渲染不够单独定性：WebGL 是强信号之一，但不是唯一证据。 | s2，源文件第 66 行 | source-report | 文中那次样本解释 | renderer 原文不在本卡 |
| C5 | 回退渲染的地位：所以它通常是“加分项”，不是“一票否决”。 | s4，源文件第 387 行 | source-report | 软件或回退渲染 | 只是该文的解释 |
| C6 | 最敏感的特征写成 VMware/SVGA 特征。 | s3，源文件第 502 行 | source-report | 该次 vendor/renderer 对照 | 没有重跑 |
| C7 | vendor 单独改写：单独足以触发 virtual_machine=true。 | s3，源文件第 503 行 | source-report | 来源写的 VMware vendor | 同段还写了 SVGA3D 和 ANGLE 形式也会触发 |
| C8 | 另一组没有触发：在本次实验里都没有触发 virtual_machine=true。 | s3，源文件第 506 行 | source-report | VirtualBox、SwiftShader、低 CPU、存储不可用、空插件 | 不能外推成永远不计分 |
| C9 | 两套信号：是两套不同信号，不能混为一谈。 | s3，源文件第 507 行 | source-report | tampering 与 virtual_machine | 仍是该次实验 |
| C10 | 分数不是开关：不是最终布尔值的简单阈值。 | s3，源文件第 510 行 | source-report | virtual_machine_ml_score | 对照分数不转写 |

<a id="decision-flow"></a>
## 不要把本地规则当成服务端

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C11 | 单个 WebGL 函数不够：不能把前端 JS 中某个 WebGL 函数直接等同为完整 VM 检测算法。 | s5，源文件第 426 行 | source-report | 前端 agent | 权重不在页面里 |
| C12 | 本地实现的边界：它不复刻 Fingerprint 私有模型，只做可解释规则： | s6，源文件第 520 行 | source-report | 文末 vm_risk 规则 | 同段的 0.6 阈值不是服务端阈值 |

## 验证与限制

`../../web-reverse/browser-env-objects/fingerprint-overview.md` 的目标是 browser-fingerprint，不覆盖 Fingerprint Pro 的服务端布尔值。正文第 513 到 514 行把 VMware/SVGA 更像规则命中、软件渲染和低 CPU 更像模型分，这是来源推测。实验脚本和本地纯算文件不在本篇，所以没有流程卡。样本标识、哈希、音频和分辨率不进入本卡。依据保持 source-report。
