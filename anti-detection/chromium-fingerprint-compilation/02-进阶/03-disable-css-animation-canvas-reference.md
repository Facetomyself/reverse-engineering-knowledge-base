---
schema_version: 2
id: chromium-disable-css-animation-canvas-reference
document_type: reference
archived_date: '2026-10-02'
scope:
  targets: [chromium-css-canvas-disable]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./03-disable-css-animation-canvas.md#一目标"
    basis: unknown
  - id: s2
    ref: "./03-disable-css-animation-canvas.md#四修改chromium源码"
    basis: unknown
  - id: s3
    ref: "./03-disable-css-animation-canvas.md#六如何禁用canvas"
    basis: unknown
  - id: s4
    ref: "./03-disable-css-animation-canvas.md#五检测"
    basis: unknown
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: unknown
    limits: 只记录两个开关名，以及作者要求先具备 Chromium 编译基础。没有版本号、switches 注册位置，也没有浏览器进程与渲染进程的实际命令行。
  - name: interfaces
    anchor: interfaces
    sources: [s2, s3]
    basis: unknown
    limits: 只对照粘贴的路径、函数签名和提前返回。未核对当前树里这些符号是否仍在，也未编译。所示渲染进程转发只追加 CSS 开关，没有追加 canvas 开关。
  - name: validation
    anchor: validation
    sources: [s4]
    basis: unknown
    limits: CPU 百分比是作者自述。图片未审。来源没有失败出口，不能把这些百分比当成验收合同。
relations:
  - type: derived_from
    target: "./03-disable-css-animation-canvas.md#四修改chromium源码"
  - type: derived_from
    target: "./03-disable-css-animation-canvas.md#六如何禁用canvas"
tags: [Chromium, Blink, CSS, Canvas, unknown]
---

# Chromium 禁用 CSS 动画与 Canvas 的源码接缝

这张卡只定位两个启动开关在来源粘贴里碰到的 Blink / content 接缝。它不是编译流程：来源没有失败出口，CPU 下降也只是作者自述。系列索引里的一行摘要不包含渲染进程转发差异。

<a id="parameters"></a>
## 开关

作者要的输入是两个进程开关，前提是读者已经能编译 Chromium。来源没有给出 `switches::` 常量、GN 目标或版本。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C1 | CSS 开关名为 `disable-css-animation`，作者用来关掉 CSS 动画 | *   实现传入参数`--disable-css-animation`，禁用css动画 | s1 03-disable-css-animation-canvas.md:24 | unknown | chromium-css-canvas-disable | 未核对开关是否已在官方 switches 中注册 |
| C2 | Canvas 开关名为 `disable-canvas`，作者用来关掉 canvas 渲染 | *   实现传入参数`--disable-canvas`，禁用canvas渲染 | s1 03-disable-css-animation-canvas.md:25 | unknown | chromium-css-canvas-disable | 未说明渲染进程是否看得到该开关 |
| C3 | 使用前需要已有 Chromium 编译基础 | > 阅读此篇博客前，请确保已具备chromium编译基础。 | s1 03-disable-css-animation-canvas.md:27 | unknown | chromium-css-canvas-disable | 没有工具链、分支或 out 目录合同 |

<a id="interfaces"></a>
## 粘贴中的接缝

CSS 路径有两处。`style_resolver.cc` 里 `StyleResolver::ApplyAnimatedStyle` 在看到 `disable-css-animation` 时直接 `return false`。`render_process_host_impl.cc` 把同一个开关从当前进程命令行 `AppendSwitch` 到渲染进程命令行。构建命令是 `ninja -C out/Default chrome`。这些是粘贴形态，不是本轮编译结果。

Canvas 路径只贴了 `html_canvas_element_module.cc` 的 `HTMLCanvasElementModule::getContext`：看到 `disable-canvas` 就 `return nullptr`。同一篇里，渲染进程转发片段只判断 `disable-css-animation`，没有对应的 `disable-canvas` 追加。因此不能从这篇粘贴推出渲染进程一定能看见 canvas 开关。

本地动画示例页在代码围栏里，这里不转写。它只被作者用来说明“有动画的页面”，不是指纹样值。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C4 | CSS 提前返回所在文件是 Blink 的 style resolver | *   打开 `\third_party\blink\renderer\core\css\resolver\style_resolver.cc` | s2 03-disable-css-animation-canvas.md:97 | unknown | 粘贴中的路径 | 未对当前树做存在性核对 |
| C5 | 命中 CSS 开关时函数直接返回 false |       return false; | s2 03-disable-css-animation-canvas.md:124 | unknown | `ApplyAnimatedStyle` 粘贴片段 | 返回值对其余样式重算的影响未知 |
| C6 | 渲染进程转发只追加 CSS 开关 |       command_line->AppendSwitch("disable-css-animation"); | s2 03-disable-css-animation-canvas.md:141 | unknown | 所示 `render_process_host_impl.cc` 片段 | 片段中没有 `disable-canvas` |
| C7 | Canvas 提前返回位于 `getContext` | V8RenderingContext* HTMLCanvasElementModule::getContext( | s3 03-disable-css-animation-canvas.md:169 | unknown | 粘贴中的函数签名 | 签名是否仍匹配未知 |
| C8 | 命中 canvas 开关时返回空指针 |       return nullptr; | s3 03-disable-css-animation-canvas.md:178 | unknown | 所示 `getContext` 片段 | 调用方对 nullptr 的处理未知 |

<a id="validation"></a>
## 作者自述与未闭合项

作者写打开本地动画页时 CPU 大约 5%，编译后再测大约 0.2%，并称另一个滑块动画页接近 5%。这些句子保持作者自述。图片链接没有做视觉审查。来源没有写“若占用不下降该检查什么”，所以缺失败出口，不能升成 procedure。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C9 | 作者称修改前本地动画页 CPU 约 5% | > 用浏览器打开这个页面，发现一个浏览器的cpu占用率就有大概5%左右。 | s4 03-disable-css-animation-canvas.md:93 | unknown | 作者的本地 html | 本轮未测量 |
| C10 | 作者称编译后同一页 CPU 约 0.2% | *   编译完成后再次检测刚刚页面的cpu占用，提示cpu占用大约只有0.2%左右了 | s4 03-disable-css-animation-canvas.md:155 | unknown | 作者的复测叙述 | 没有采样方法，图片未审 |

未知：Chromium 版本、`ApplyAnimatedStyle` 的后续语句、`getContext` 返回 nullptr 后的页面行为，以及 `disable-canvas` 能否进入渲染进程。
