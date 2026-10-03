---
schema_version: 2
id: chromium-blink-offline-audio-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-blink-offline-audio]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./06-audio-fingerprint-randomization.md#一什么是audio指纹"
    basis: unknown
  - id: s2
    ref: "./06-audio-fingerprint-randomization.md#二如何获取audio指纹"
    basis: unknown
  - id: s3
    ref: "./06-audio-fingerprint-randomization.md#替换为"
    basis: unknown
  - id: s4
    ref: "./06-audio-fingerprint-randomization.md#3编译"
    basis: unknown
  - id: s5
    ref: "./06-audio-fingerprint-randomization.md#四在线指纹验证网站"
    basis: unknown
  - id: s6
    ref: "./06-audio-fingerprint-randomization.md#二如何获取audio指纹"
    basis: unknown
  - id: s7
    ref: "./06-audio-fingerprint-randomization.md#三编译随机audio指纹"
    basis: unknown
modules:
  - name: parameters
    anchor: parameters
    sources: [s3, s7]
    basis: unknown
    limits: 只读到构造函数替换文本。扰动加在 Create 的 sample_rate 实参上。未编译，未听渲染结果。
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2, s6]
    basis: unknown
    limits: 独特性判断是作者陈述。探测脚本的摘要原值不转写。归档里的 webkit 前缀是截断文本。
  - name: validation
    anchor: validation
    sources: [s4, s5]
    basis: unknown
    limits: “每次刷新都随机”和声音副作用都是作者自述。文末两个网址没有配套观察。
relations:
  - type: derived_from
    target: "./06-audio-fingerprint-randomization.md#替换为"
tags: [chromium, blink, audio]
---

# Chromium Blink OfflineAudioContext 采样率扰动

这张卡只定位离线音频上下文构造时，`sample_rate` 被加上一个 0 到 99 的整数。近邻 [Audio 指纹对象参考](../../../web-reverse/browser-env-objects/audio-fingerprint.md) 的目标是 web-audio，模块是宿主对象检测面，不包含 `offline_audio_context.cc`。

作者把编译前提推到另一篇。文末没有把两个验证网址写成通过或失败，所以不能收成流程卡。

<a id="parameters"></a>
## 参数机制

文件是 `third_party/blink/renderer/modules/webaudio/offline_audio_context.cc`。替换文本在 `OfflineAudioDestinationNode::Create` 的调用里把采样率写成 `sample_rate+getRandomIntForFoo6Modern()`。辅助函数使用 `std::uniform_int_distribution<int> distribution(0, 99);`，并 `return distribution(generator);`。读到的改动停在这个实参，没有改 `oncomplete` 或声道数据本身。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 打开的文件是 third_party/blink/renderer/modules/webaudio/offline_audio_context.cc | s7，打开源码那一行 | unknown | 本篇路径 | 无版本号 |
| C2 | Create 的采样率实参写成 sample_rate+getRandomIntForFoo6Modern() | s3，替换后的构造函数 | unknown | 该调用表达式 | 未编译 |
| C3 | 加数来自 distribution(0, 99) 并且 return distribution(generator) | s3，getRandomIntForFoo6Modern | unknown | 该辅助函数文本 | 未跑分布 |

<a id="risk-control"></a>
## 检测面

作者写 audio 指纹都是独特性不高，并且一般要和其他指纹配合才有较高准确性。探测脚本把 `OfflineAudioContext` 赋给名为 `AudioContext` 的变量；归档里的 webkit 前缀停在 `webkitOfflineAudioContex`，末尾字母缺失。构造调用是 `let context = new AudioContext(1, 5000, 44100)`。随后用振荡器和压缩器做离线渲染再摘要。摘要原值不转写。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 作者写 audio指纹都是独特性不高 | s1 | unknown | 作者对这类指纹的范围判断 | 没有样本量 |
| C5 | 作者又写 audio指纹唯一性不是特别高，一般都是和其他指纹配合使用才能做到较高的准确性 | s2 段末 | unknown | 同上 | 未定义“较高” |
| C6 | 归档脚本把前缀写成 webkitOfflineAudioContex，构造行是 let context = new AudioContext(1, 5000, 44100) | s6，获取脚本 | unknown | 本篇粘贴的脚本文本 | 截断后的脚本不能当可运行副本 |

<a id="validation"></a>
## 验证与限制

作者称编译后每次刷新时 audio 指纹都是随机的了，并提醒这里可能会对浏览器的声音产生未知影响。在线验证只列出了 creepjs 和 ip77.net，没有写出这两页看到了什么。配图不转写。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | 编译后每次刷新时audio指纹都是随机的了。 | s4 | unknown | 作者的结果句 | 本轮未编译 |
| C8 | 这里可能会对浏览器的声音产生未知影响 | s4 | unknown | 作者的副作用提醒 | 不是失败出口 |
| C9 | 文末只列出 https://abrahamjuliot.github.io/creepjs/ 和 https://ip77.net/ | s5 | unknown | 作者点名的网址 | 没有观察结果 |
