---
schema_version: 2
id: chromium-webgpu-limit-seed-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-webgpu]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./24-webgpu-fingerprint.md#二什么是webgpu指纹"
    basis: unknown
  - id: s2
    ref: "./24-webgpu-fingerprint.md#三获取浏览器的webgpu指纹"
    basis: unknown
  - id: s3
    ref: "./24-webgpu-fingerprint.md#四编译随机webgpu指纹"
    basis: unknown
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: unknown
    limits: 只保留作者对组成和唯一性的两句。不记录样例哈希，也不把风控等级写成已测量结论。
  - name: interfaces
    anchor: interfaces
    sources: [s2, s3]
    basis: unknown
    limits: 只保留 adapter、device 和 GPUSupportedLimits 的一个属性名。宏里的其余 limit 不列表。
  - name: parameters
    anchor: parameters
    sources: [s3]
    basis: unknown
    limits: 只保留 fingerprints 开关角色和 seed 对 128 取余。没有种子样例，也没有第二个属性的公式。
relations:
  - type: derived_from
    target: "./24-webgpu-fingerprint.md#二什么是webgpu指纹"
  - type: derived_from
    target: "./24-webgpu-fingerprint.md#三获取浏览器的webgpu指纹"
  - type: derived_from
    target: "./24-webgpu-fingerprint.md#四编译随机webgpu指纹"
tags: [chromium, webgpu, blink, unknown]
---

# Chromium WebGPU limit 的种子返回值

这张卡只回答：这篇归档把 WebGPU 指纹说成什么，采集入口叫什么，以及 `GPUSupportedLimits::maxComputeWorkgroupsPerDimension` 被改成哪种种子返回。通用宿主指纹总纲不定位这个函数。控制台打出的哈希不进入本卡。

<a id="risk-control"></a>
## 风险陈述

作者写“通过收集如GPU型号、驱动版本、支持的图形特性等信息，hash而成的指纹信息。”下一句写“WebGPU指纹唯一性并不太高，还有很多浏览器是不支持webGPU”，并据此称风控等级较低。两句都是 source-report，没有对照样本。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 原句含 `通过收集如GPU型号、驱动版本、支持的图形特性等信息，hash而成的指纹信息。` | s1 24-webgpu-fingerprint.md:31 | unknown | 作者的组成描述 | 没有封闭字段表 |
| C2 | 原句含 `WebGPU指纹唯一性并不太高，还有很多浏览器是不支持webGPU` | s1 :32 | unknown | 作者的唯一性判断 | 风控等级没有测量 |

<a id="interfaces"></a>
## 接口位置

采集侧调用 `navigator.gpu.requestAdapter()`，再调用 `adapter.requestDevice()`。源码路径是 `/third_party/blink/renderer/modules/webgpu/gpu_supported_limits.cc`。作者从宏中拿掉并重写的名字是 `maxComputeWorkgroupsPerDimension`，函数写成 `GPUSupportedLimits::maxComputeWorkgroupsPerDimension`。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C3 | 调用含 `navigator.gpu.requestAdapter()` | s2 :47 | unknown | 作者的采集脚本 | 不记录脚本输出 |
| C4 | 调用含 `adapter.requestDevice()` | s2 :53 | unknown | 同一脚本 | 不展开序列化 |
| C5 | 路径含 `/third_party/blink/renderer/modules/webgpu/gpu_supported_limits.cc` | s3 :98 | unknown | 作者点名的文件 | 无版本 |
| C6 | 属性名 `maxComputeWorkgroupsPerDimension` | s3 :145 | unknown | 被注释并重定义的那一项 | 其余宏项不列表 |
| C7 | 符号 `GPUSupportedLimits::maxComputeWorkgroupsPerDimension` | s3 :150 | unknown | 作者追加的函数 | 无调用点 |

<a id="parameters"></a>
## 参数角色

函数用 `HasSwitch("fingerprints")` 取种子，否则用当前时间。返回式是 `return seed % 128`。作者写“属性设置成了返回随机数”，并说其他属性按需照搬，但没有第二份公式。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 入口含 `HasSwitch("fingerprints")` | s3 :153 | unknown | 这一个属性 | 无开关样例 |
| C9 | 返回式含 `return seed % 128` | s3 :160 | unknown | 仅该函数 | 没有第二个属性 |
| C10 | 作者写有 `属性设置成了返回随机数` | s3 :164 | unknown | 作者对原理的说法 | 种子来源仍是开关或时间 |

## 验证与限制

文末只给出两个在线站点的名字，没有通过或失败条件。作者问改动后是否每次都变随机，但没有第二次输出。没有失败出口，不能当成流程。
