---
schema_version: 2
id: anti-detection-chromium-ua-gpu-minor-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-ua-gpu-minor]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./17-ua-gpu-version-modification.md#目标依旧保持不变"
    basis: unknown
  - id: s2
    ref: "./17-ua-gpu-version-modification.md#注意的点"
    basis: unknown
  - id: s3
    ref: "./17-ua-gpu-version-modification.md#一更改显卡gpu信息"
    basis: unknown
  - id: s4
    ref: "./17-ua-gpu-version-modification.md#二更改useragent"
    basis: unknown
  - id: s5
    ref: "./17-ua-gpu-version-modification.md#三更改内核小版本"
    basis: unknown
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s3, s5]
    basis: unknown
    limits: 只记录 switch 的有无、int 上限，以及来源用取模或时间回退驱动返回值。示例种子、显卡返回串和版本文本不写入本卡。
  - name: interfaces
    anchor: interfaces
    sources: [s3, s4, s5]
    basis: unknown
    limits: 只定位三个来源点名的文件和函数。没有源码 checkout，没有编译，没有把作者的随机结果当成已核对的运行事实。
relations:
  - type: derived_from
    target: "./17-ua-gpu-version-modification.md#一更改显卡gpu信息"
tags: [Chromium, fingerprints, WebGL, userAgent, unknown]
---

# Chromium `--fingerprints` 与 GPU、reduced UA、小版本

这张卡检索来源如何用同一个启动 switch 分支改 WebGL unmasked renderer、reduced userAgent 和 `uaFullVersion`。依据只到 `source-report`。来源没有验收条件和失败出口，不升为 procedure。具体显卡串、追加标记和版本文本不转入本卡。

<a id="parameters"></a>
## 启动 switch

不传 `--fingerprints` 时，来源称每个访问请求的指纹全部随机生成。传入时来源称指纹固定，换一个正整数就换一套。来源把参数收成 int，并写最大值为 2,147,483,647。示例种子不记录。

GPU 与小版本两处都先看 `HasSwitch("fingerprints")`。有 switch 时解析该值；GPU 段在没有 switch 时改用当前时间，小版本段在没有 switch 时改用 `rand`。GPU 段再用 `tmp % 9` 参与返回串。返回串正文不转入本卡。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 不传 switch 时来源称逐请求随机 | s1 `17-ua-gpu-version-modification.md:25` 原文：不传参数`--fingerprints`，则每个访问请求的指纹全部随机生成。 | unknown | chromium-ua-gpu-minor | 未运行 |
| C2 | 来源把 switch 限制为 int，并给出上限 | s2 `17-ua-gpu-version-modification.md:29` 原文：`--fingerprints`只能传整数，且最大值为2,147,483,647 | unknown | chromium-ua-gpu-minor | 未核对 CommandLine 解析 |
| C3 | GPU 分支读取 fingerprints switch | s3 `17-ua-gpu-version-modification.md:65` 原文：if (base_command_line->HasSwitch("fingerprints")) { | unknown | chromium-ua-gpu-minor | 不复制返回串 |
| C4 | GPU 返回串使用 tmp % 9 | s3 `17-ua-gpu-version-modification.md:72` 原文：std::string rstr_1 = std::to_string(tmp % 9); | unknown | chromium-ua-gpu-minor | 只此取模 |
| C5 | 小版本分支同样读取该 switch | s5 `17-ua-gpu-version-modification.md:155` 原文：if (base_command_line->HasSwitch("fingerprints")) { | unknown | chromium-ua-gpu-minor | 不复制版本文本 |

<a id="interfaces"></a>
## 三个源码位置

GPU 段打开 `third_party\blink\renderer\modules\webgl\webgl_rendering_context_base.cc`，落在 `WebGLDebugRendererInfo::kUnmaskedRendererWebgl`。原 `GetString(GL_RENDERER)` 返回被换掉。

reduced UA 段打开 `components/version_info/version_info_with_user_agent.cc` 的 `GetProductNameAndVersionForReducedUserAgent`。来源的原理句是在 userAgent 里加上一串字符。追加的标记原文不转入本卡。

小版本段先写 `navigator.userAgentData` 的高熵值，再打开 `third_party\blink\renderer\core\frame\navigator_ua.cc`，替换 `ua_data->SetUAFullVersion(...)`。来源称这样拿到的小版本是随机的。这是作者结论，不是本轮核对。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | renderer 改动位于 webgl_rendering_context_base.cc | s3 `17-ua-gpu-version-modification.md:34` 原文：webgl_rendering_context_base.cc | unknown | chromium-ua-gpu-minor | 未对照修订 |
| C7 | 来源点名 kUnmaskedRendererWebgl | s3 `17-ua-gpu-version-modification.md:45` 原文：case WebGLDebugRendererInfo::kUnmaskedRendererWebgl: | unknown | chromium-ua-gpu-minor | 只此 case |
| C8 | reduced UA 位于 version_info_with_user_agent.cc | s4 `17-ua-gpu-version-modification.md:85` 原文：version_info_with_user_agent.cc | unknown | chromium-ua-gpu-minor | 不复制追加标记 |
| C9 | 来源替换 GetProductNameAndVersionForReducedUserAgent | s4 `17-ua-gpu-version-modification.md:98` 原文：std::string GetProductNameAndVersionForReducedUserAgent( | unknown | chromium-ua-gpu-minor | 未核对调用方 |
| C10 | 来源把改动概括为往 userAgent 加一串字符 | s4 `17-ua-gpu-version-modification.md:123` 原文：原理是在userAgent里加上了一串随机字符 | unknown | chromium-ua-gpu-minor | 作者概括 |
| C11 | 小版本文件是 navigator_ua.cc | s5 `17-ua-gpu-version-modification.md:142` 原文：navigator_ua.cc | unknown | chromium-ua-gpu-minor | 未对照修订 |
| C12 | 原语句是 SetUAFullVersion(metadata.full_version) | s5 `17-ua-gpu-version-modification.md:145` 原文：ua_data->SetUAFullVersion(String::FromUTF8(metadata.full_version)); | unknown | chromium-ua-gpu-minor | 替换字面量不转入 |
| C13 | 来源称小版本因此随机 | s5 `17-ua-gpu-version-modification.md:166` 原文：这样获取的版本里，小版本就随机了 | unknown | chromium-ua-gpu-minor | 作者结论 |

## 验证与限制

结果图没有做视觉审查。文末只说动机是绕过 Akamai 指纹风控，并称最初目标已经实现。这句话没有检测点，不建 risk-control。公开来源 URL 未知。本轮没有编译，也没有读取 `navigator.userAgentData`。
