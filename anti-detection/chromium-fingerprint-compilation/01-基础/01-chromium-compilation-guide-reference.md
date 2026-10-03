---
schema_version: 2
id: chromium-build-gn-args-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-build]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./01-chromium-compilation-guide.md#八构建与编译"
    basis: unknown
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: unknown
    limits: 只记录本篇写明的环境开关和 gn 参数。安装步骤作者要求以官网为准。没有修订号，本次未编译。
relations:
  - type: derived_from
    target: "./01-chromium-compilation-guide.md#八构建与编译"
tags: [chromium, gn, unknown]
---

# Chromium 指纹浏览器系列的最小构建参数

这张卡只回答一个检索问题：这篇编译笔记里，哪些参数是作者自己写下、并且没有被现有卡片覆盖的。Visual Studio、SDK 和 depot_tools 的安装，作者写明要以上游文档为准，这里不再复述。

<a id="parameters"></a>
## 参数

作者先把 `DEPOT_TOOLS_WIN_TOOLCHAIN` 设为 0。最小 `gn gen out\Default` 参数是关闭组件构建、关闭 debug、关闭 nacl，并把 blink、v8 和整体的 symbol level 都设为 0。作者特别写了不要打开 debug，否则产物会非常卡；参数中的空格也不能随便删。

两组可选参数分开用。要 HTML 播放器时追加专有编解码器和 Chrome 的 ffmpeg branding。只在正式发布时追加 official build，同时关闭官方 Google API keys，并把 PGO 相位设为 0；作者的理由是体积更小但没有调试信息。编译目标写的是 `out/Default` 的 `chrome`，启动文件是 `chrome.exe`。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C2 | DEPOT_TOOLS_WIN_TOOLCHAIN 设为 0 | s1 01-chromium-compilation-guide.md:59 | unknown | chromium-build | 本机工具链开关 |
| C3 | 最小参数关闭组件构建、debug、nacl，三档 symbol_level 为 0 | s1 01-chromium-compilation-guide.md:85 | unknown | chromium-build | 未对照当前官方 args |
| C4 | 不要打开 is_debug，否则作者认为会非常卡 | s1 01-chromium-compilation-guide.md:89 | unknown | chromium-build | 不是本次编译结果 |
| C5 | 参数空格不能随意删除 | s1 01-chromium-compilation-guide.md:90 | unknown | chromium-build | 无失败日志 |
| C6 | 可选打开 proprietary_codecs | s1 01-chromium-compilation-guide.md:96 | unknown | chromium-build | 不属于最小参数 |
| C7 | 可选把 ffmpeg_branding 设为 Chrome | s1 01-chromium-compilation-guide.md:97 | unknown | chromium-build | 与 C6 同组 |
| C8 | 正式发布才追加 is_official_build | s1 01-chromium-compilation-guide.md:105 | unknown | chromium-build | 作者称无调试信息 |
| C9 | 该组把 use_official_google_api_keys 设为 false | s1 01-chromium-compilation-guide.md:106 | unknown | chromium-build | 只是布尔开关，没有密钥 |
| C10 | 该组把 chrome_pgo_phase 设为 0 | s1 01-chromium-compilation-guide.md:107 | unknown | chromium-build | 当前里程碑是否仍使用未知 |
| C12 | ninja 目标是 out/Default chrome | s1 01-chromium-compilation-guide.md:115 | unknown | chromium-build | 无编译日志 |

## 验证与限制

作者自己写编译教程要以官网为准（C1，行 23）。本篇没有 Chromium 修订号，也没有把“生成了 chrome.exe”（C13，行 118）写成一次通过记录。安装包和绿色包只是后文的产物描述，没有独立验收，也没有失败后的出口，所以这张卡不是流程。

本次没有编译。本机代理和 git 身份不记录。
