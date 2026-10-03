---
schema_version: 2
id: firefox-webgpu-fpfile-consistency
document_type: reference
original_date: '2026-06-01'
archived_date: '2026-10-02'
scope:
  targets: [firefox-webgpu]
  client: firefox
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260601-01.md#配置入口
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留 --fpfile、两套开关名，以及未写明的 limit 仍走原值。不记录示例画像。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留 pref 放行、两边 limits、feature 过滤、空 adapter、canvas context 和 NOOP 优先。没有失败出口，不能当流程。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留不要孤立配置，以及常见 JS 面和 NOOP 的来源边界。
relations:
  - type: derived_from
    target: ./ruyi-20260601-01.md#配置入口
  - type: derived_from
    target: ./ruyi-20260601-01.md#文件改动
  - type: derived_from
    target: ./ruyi-20260601-01.md#一致性原则
  - type: derived_from
    target: ./ruyi-20260601-01.md#已知边界
tags: [firefox, webgpu, fpfile, source-report]
---

# Firefox WebGPU 指纹开关与交叉一致性

这篇卡检索自定义 Firefox 怎样用一份 fp.txt 决定 WebGPU 是否暴露，以及 adapter、device、canvas 和 NOOP 哪些必须一起改。不记录示例 GPU 画像，也不把作者的探针清单当成验收。

<a id="parameters"></a>
## 开关与覆盖范围

入口和缺省规则都来自同一篇对 fp.txt 的描述。

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C1</td><td>运行 Firefox 时需要带  ` --fpfile  ` ，例如当前方案使用：</td><td>s1，源文件第 72 行</td><td>source-report</td><td>作者当前 Firefox 方案</td><td>没有 fpfile 时的原生 WebGPU 不在本条</td></tr>
<tr><td>C2</td><td>    * ` WebGPUFpEnabled()  ` 支持显式开关：  ` webgpu.enabled  ` /  ` webgpu_enabled  ` 。</td><td>s1，源文件第 136 行</td><td>source-report</td><td>显式开关</td><td>不记录取值</td></tr>
<tr><td>C3</td><td>    * 没有显式开关时，只要存在  ` webgpu.  ` 或  ` webgpu_  ` 前缀字段，也认为 WebGPU 指纹模式启用。</td><td>s1，源文件第 138 行</td><td>source-report</td><td>没有显式开关时</td><td>不是 prefs 默认值</td></tr>
<tr><td>C4</td><td>    * 用 override 数组可以只覆盖  ` fp.txt  ` 配置过的字段，没有配置的字段仍保留原来的默认/真实值。</td><td>s1，源文件第 244 行</td><td>source-report</td><td>已配置的 limit</td><td>未配置字段保持原值</td></tr>
</table>

<a id="decision-flow"></a>
## 暴露面必须一起改

下面每条都是来源给出的分支，不是本地补上的步骤。

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C5</td><td>    * ` Instance::PrefEnabled()  ` ：当  ` WebGPUFpEnabled()  ` 为真时，即使  ` dom.webgpu.enabled  ` pref 没开，也暴露  ` navigator.gpu  ` 。</td><td>s1，源文件第 152 行</td><td>source-report</td><td>Instance::PrefEnabled</td><td>只钉 pref 例外</td></tr>
<tr><td>C6</td><td>    * BrowserScan 会同时读取  ` adapter  ` 和  ` device  ` 两边。如果只改  ` adapter.limits  ` ，但  ` device.limits  ` 仍是真实值，会出现交叉不一致。</td><td>s1，源文件第 218 行</td><td>source-report</td><td>同时读取 adapter 与 device</td><td>单边修改会被写成不一致</td></tr>
<tr><td>C7</td><td>    * features 必须过滤 Firefox 当前真正实现的 feature，避免配置了未实现 feature 后  ` requestDevice()  ` 失败。</td><td>s1，源文件第 222 行</td><td>source-report</td><td>requestDevice 前的 feature</td><td>未实现枚举要滤掉</td></tr>
<tr><td>C8</td><td>    * 现在如果  ` WebGPUFpEnabled()  ` 为真，会创建  ` Adapter::CreateFallback()  ` 。</td><td>s1，源文件第 268 行</td><td>source-report</td><td>底层 adapter 为空</td><td>不展开 forceFallbackAdapter</td></tr>
<tr><td>C9</td><td>    * 只暴露  ` navigator.gpu  ` 不够，canvas 的  ` webgpu  ` context 也必须可识别。</td><td>s1，源文件第 296 行</td><td>source-report</td><td>canvas webgpu context</td><td>不只暴露 navigator.gpu</td></tr>
<tr><td>C10</td><td>    * 如果  ` allow_noop_fallback  ` 为真，优先尝试  ` Backends::NOOP  ` 。</td><td>s1，源文件第 315 行</td><td>source-report</td><td>allow_noop_fallback 为真</td><td>其后仍有原有后端</td></tr>
</table>

<a id="risk-control"></a>
## 不能当成真实 GPU

一致性原则和已知边界只保留来源自己划的范围。

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C11</td><td>WebGPU 指纹不要孤立配置。建议和 WebGL 保持同一个 GPU 画像：</td><td>s1，源文件第 445 行</td><td>source-report</td><td>与 WebGL 一起配置</td><td>不抄画像</td></tr>
<tr><td>C12</td><td>    * ` webgpu.vendor  ` 与  ` webgl.unmasked_vendor  ` 不要冲突。</td><td>s1，源文件第 447 行</td><td>source-report</td><td>vendor 对齐</td><td>device 句不在本格</td></tr>
<tr><td>C13</td><td>当前方案主要覆盖 BrowserScan 常见的 WebGPU JS 暴露面，不等于完整模拟真实 GPU。</td><td>s1，源文件第 457 行</td><td>source-report</td><td>常见 JS 暴露面</td><td>不等于真实 GPU</td></tr>
<tr><td>C14</td><td>    * NOOP fallback 可以支撑基础 API，但不能等价于真实 DX12/AMD 后端。</td><td>s1，源文件第 469 行</td><td>source-report</td><td>NOOP fallback</td><td>不能当成真实后端</td></tr>
</table>

## 验证与限制

browser-fingerprint 的 risk-control 只写宿主对象不能矛盾，没有 --fpfile、CreateFallback 或 NOOP。chromium-webgpu 与 webgpu 的目录查询都是 0；即便包内另有 Blink limit 种子草稿，客户端和函数也不是这篇 Gecko 路径。第 85-103 行的画像和第 369-442 行的 limit 名单不进入本卡。第 324-368 行的探针没有通过条件和失败出口。效果描述保持 source-report。
