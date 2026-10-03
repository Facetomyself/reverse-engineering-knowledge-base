---
schema_version: 2
id: chromium-blink-screen-offset-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-screen]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./23-screen-size-modification.md#二如何更改源码"
    basis: unknown
  - id: s2
    ref: "./23-screen-size-modification.md#四反反检测"
    basis: unknown
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2]
    basis: unknown
    limits: 只记录 screen.cc 与 media_query_evaluator.cc 里作者点名的函数。宿主尺寸一致性已在 screen 参考卡，这里不重复，也不记录控制台读数。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: unknown
    limits: 只保留 fingerprints 开关的角色和 availHeight 的一条返回式。没有种子样例，也没有其余 Screen 函数的公式。
relations:
  - type: derived_from
    target: "./23-screen-size-modification.md#二如何更改源码"
  - type: derived_from
    target: "./23-screen-size-modification.md#四反反检测"
tags: [chromium, blink, screen, unknown]
---

# Blink screen 尺寸偏移的源码位置

这张卡只回答：这篇归档改的是哪两个 Blink 文件、哪几个函数，以及 `availHeight` 的返回式如何使用 `fingerprints`。JS 的 `screen` 字段、`matchMedia` 一致性和分辨率坑已经在 `../../../web-reverse/browser-env-objects/screen.md`，本卡不再建那一层。控制台里的屏幕读数不进入本卡。

<a id="interfaces"></a>
## 接口位置

尺寸函数在 `/third_party/blink/renderer/core/frame/screen.cc`。作者给出替换体的是 `int Screen::availHeight() const {`，并写“这里只更改了”这一个函数。媒体查询求值在 `\third_party\blink\renderer\core\css\media_query_evaluator.cc`，点名 `DeviceHeightMediaFeatureEval` 与 `DeviceWidthMediaFeatureEval`。高度函数的比较被写成 `//if (value.IsValid())`。作者称因此 `window.matchMedia(lie_js).matches` 变为 true。这是 source-report，没有补丁后的读数。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 文件含 `/third_party/blink/renderer/core/frame/screen.cc` | s1 23-screen-size-modification.md:52 | unknown | 作者点名的路径 | 无版本 |
| C2 | 函数签名含 `int Screen::availHeight() const {` | s1 :63 | unknown | 唯一给出的替换体 | 其余函数没有函数体 |
| C5 | 作者写有 `这里只更改了` | s1 :99 | unknown | availHeight | 随后的函数只是名单 |
| C6 | 文件含 `\third_party\blink\renderer\core\css\media_query_evaluator.cc` | s2 :137 | unknown | 媒体查询求值 | 无调用方 |
| C7 | 高度函数名 `DeviceHeightMediaFeatureEval` | s2 :142 | unknown | 作者找到的符号 | 未与上游核对 |
| C8 | 宽度函数名 `DeviceWidthMediaFeatureEval` | s2 :155 | unknown | 同一段 | 找到段与替换段都出现 |
| C9 | 高度比较被写成 `//if (value.IsValid())` | s2 :175 | unknown | 替换段 | 宽度在后文另有同样注释 |
| C10 | 作者点名 `window.matchMedia(lie_js).matches` | s2 :199 | unknown | 作者对返回值的说法 | 没有补丁后输出 |

<a id="parameters"></a>
## 参数角色

返回式使用 `HasSwitch("fingerprints")` 读当前进程开关；没有开关时作者改用当前时间。写出的运算是 `height() - 10 - seed%10`。没有种子样例。常用分辨率数组属于作者后文的风控备注，不作为设备指纹抄入。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C3 | 种子入口含 `HasSwitch("fingerprints")` | s1 :80 | unknown | availHeight 这一处 | 无开关样例 |
| C4 | 返回式含 `height() - 10 - seed%10` | s1 :87 | unknown | 仅 availHeight | 未验证与其他尺寸一致 |

## 验证与限制

没有补丁后的尺寸或 `matchMedia` 读数，也没有失败时的停止条件，所以不能当成流程。`screen` 目标上的 risk-control 仍以既有参考卡为准。
