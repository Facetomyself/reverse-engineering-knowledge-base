---
schema_version: 2
id: anti-detection-chromium-headless-signals-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-headless]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./09-headless-detection-bypass.md#简介
    basis: unknown
  - id: s2
    ref: ./09-headless-detection-bypass.md#一修改webdriver
    basis: unknown
  - id: s3
    ref: ./09-headless-detection-bypass.md#二修改rtt
    basis: unknown
  - id: s4
    ref: ./09-headless-detection-bypass.md#三修改notificationpermission
    basis: unknown
  - id: s5
    ref: ./09-headless-detection-bypass.md#四修改user-agent
    basis: unknown
  - id: s6
    ref: ./09-headless-detection-bypass.md#五针对无头的plugin检测
    basis: unknown
  - id: s7
    ref: ./09-headless-detection-bypass.md#一无头检测简介
    basis: unknown
  - id: s8
    ref: ./09-headless-detection-bypass.md#二webgl-render
    basis: unknown
  - id: s9
    ref: ./09-headless-detection-bypass.md#三windowchrome
    basis: unknown
  - id: s10
    ref: ./09-headless-detection-bypass.md#四plugins插件
    basis: unknown
  - id: s11
    ref: ./09-headless-detection-bypass.md#五无头useragent
    basis: unknown
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1, s7, s8, s9]
    basis: unknown
    limits: 只记录作者点名的无头信号。bot.sannysoft.com 只是他使用的页面，原文没有检测结果。
  - name: parameters
    anchor: parameters
    sources: [s3, s5, s8, s11]
    basis: unknown
    limits: 常量来自作者粘贴的返回文本。未对照某一版 Chromium，也未观察这些返回值是否仍被检测脚本读取。
  - name: interfaces
    anchor: interfaces
    sources: [s2, s3, s6, s8, s9, s10, s11]
    basis: unknown
    limits: 只保留文件和函数名。不重组完整替换函数。
  - name: decision-flow
    anchor: decision-flow
    sources: [s6, s9, s10, s11]
    basis: unknown
    limits: 第二篇明确作废第一篇的 plugin 改法。除此之外没有失败出口，Linux 结语只是作者停做，不能当成流程验收。
relations:
  - type: derived_from
    target: ./09-headless-detection-bypass.md#一无头检测简介
  - type: derived_from
    target: ./09-headless-detection-bypass.md#四plugins插件
tags: [chromium, headless, blink, unknown]
---

# Chromium 无头信号与作者点名的源码位置

这张卡索引作者合并的两篇笔记里点名的无头信号、返回值和文件。它不是编译流程：原文没有记录 bot.sannysoft.com 的通过结果，也没有“改完仍被标出就停止”的出口。`navigator` 参考卡讨论的是脚本侧 `webdriver` 语义，不包含这些 Blink 位置。

<a id="risk-control"></a>
## 检测面

作者把无头浏览器写成没有界面、用作爬虫时会被站点认出。第二篇把无头检测定义成“只要检测到就是爬虫”，并用 bot.sannysoft.com 作为常用页面。他点名的信号包括：不用 GPU 时 WebGL renderer 出现 SwiftShader、有头浏览器有 `window.chrome` 而无头为 `undefined`、有头有默认插件而无头插件数为 0、以及无头 UA 与有头 UA 是两套逻辑。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C1 | 无头特征被写成爬虫识别面 | 无头浏览器就是没有界面的浏览器，但用作爬虫时会出现一些特征，会被网站识别为爬虫。 | s1，第 32 行 | unknown | 第一篇简介 | 未给出具体站点 |
| C2 | 作者把检出无头等同于爬虫 | 无头检测(`Headless Detection`)就是检测用户是否在无头浏览器。只要检测到，那百分百是爬虫。 | s7，第 161 行 | unknown | 第二篇定义 | 是作者判断，不是检测规则正文 |
| C3 | 常用页面是 bot.sannysoft.com | https://bot.sannysoft.com/ | s7，第 162 行 | unknown | 作者点名的页面 | 没有结果记录 |
| C4 | SwiftShader 被写成无头 GPU 关键字 | 检测webGL render是否有关键字"`SwiftShader`"，如果有那就是无头。 | s8，第 167 行 | unknown | 作者描述的 WebGL 检测 | 未核对检测脚本 |
| C5 | window.chrome 缺失被写成无头特征 | 正常有头的chromium内核浏览器打开F12都是有`window.chrome`的，但无头浏览器会返回`undefined`。 | s9，第 222 行 | unknown | 作者的 F12 观察自述 | 未在本轮打开浏览器 |

<a id="parameters"></a>
## 作者写下的返回值

这些是粘贴文本里的常量，不是测量到的环境样例。RTT 函数直接返回 150。产品名常量从注释中的 HeadlessChrome 改成 Chrome。WebGL 分支在存在 `fingerprints` 开关时用其整数值做种子，否则用当前时间；随后把渲染器字符串里的 SwiftShader 换成 NVDIA。无头产品版本函数不走上面的产品名常量，而是返回 Chrome、写死的 124 和 BigTom 加开关整数。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C6 | rtt 被写成常数 150 | return 150; | s3，第 76 行 | unknown | NetworkInformation::rtt 的替换文本 | 未核对调用方是否仍读该值 |
| C7 | 产品名常量改成 Chrome | const char kHeadlessProductName[] = "Chrome"; | s5，第 112 行 | unknown | headless_browser_impl.cc 这一处 | 第二篇说它盖不住另一套 UA |
| C8 | WebGL 种子读取 fingerprints 开关 | base_command_line->HasSwitch("fingerprints") | s8，第 188 行 | unknown | 这段 WebGL 追加文本 | 缺开关时改用时间，稳定性未知 |
| C9 | 替换词是 NVDIA | std::string replaceString = "NVDIA"; | s8，第 201 行 | unknown | 这段 WebGL 追加文本 | 拼写按原文保留 |
| C10 | 无头版本串带 BigTom 和写死主版本 | return "Chrome/" + std::to_string(fooversion) + ".0.0.0 BigTom/" | s11，第 317 行 | unknown | GetProductNameAndVersion 的替换文本 | fooversion 在上一行写成 124 |

<a id="interfaces"></a>
## 文件与函数

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C11 | webdriver 改在 Navigator::webdriver | bool Navigator::webdriver() const { | s2，第 49 行 | unknown | navigator.cc | 原文路径转义了下划线，以函数名为准 |
| C12 | webdriver 替换文本返回 false | return false; | s2，第 50 行 | unknown | 该函数的替换体 | 不讨论脚本侧缺失语义 |
| C13 | 通知拒绝被改成 default | return "default"; | s4，第 92 行 | unknown | DENIED 分支的替换行 | 同文件 ASK 分支原本就返回 default |
| C14 | 插件数改动落在 DOMPluginArray | bool DOMPluginArray::IsPdfViewerAvailable() { | s10，第 260 行 | unknown | dom_plugin_array.cc | 第一篇另改过 NavigatorPlugins::plugins，第二篇作废 |
| C15 | window.chrome 改动调用 WebUIExtension::Install | WebUIExtension::Install(frame_); | s9，第 247 行 | unknown | RenderFrameImpl::DidClearWindowObject | 只保留调用行 |

<a id="decision-flow"></a>
## 两篇之间的取舍

第一篇在 `UpdatePluginData` 的固定插件分支里仍推入一份 PDF 插件名。第二篇写明那一版改乱了，会被 Cloudflare 检测到，所以上一篇的这一处作废。替代文本是 `DOMPluginArray::IsPdfViewerAvailable()` 直接返回 true。`window.chrome` 的改法是注释掉 `BINDINGS_POLICY_WEB_UI` 条件后仍调用 `WebUIExtension::Install`。无头 UA 必须改 `HeadlessBrowser::GetProductNameAndVersion`，因为作者发现只改产品名常量后字符串不变。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C16 | 第一篇插件改法被作者作废 | 会被cloudflare检测到，所以上篇这里作废，我们重改。 | s10，第 255 行 | unknown | 第一篇 plugin 段 | 没有写出 Cloudflare 的具体命中项 |
| C17 | 替代是 PDF 查看器函数恒为 true | return true; | s10，第 285 行 | unknown | IsPdfViewerAvailable 的替换体 | 未验证插件列表因此变成哪几项 |
| C18 | chrome 对象改动是去掉 if | 这里就是把if条件注释掉。 | s9，第 250 行 | unknown | DidClearWindowObject | 未验证 WebUI 绑定的副作用 |
| C19 | 无头 UA 与有头 UA 分开 | 无头的UA和有头的UA是两套逻辑。 | s11，第 294 行 | unknown | 作者对前一篇的更正 | 没有两套函数的对照实验 |

## 验证与限制

结语只说无头模式是为以后的 Linux 版准备，而且作者当时不打算做。这不是验收，也不是失败后的补采条件。通知权限、RTT、产品名、WebGL 替换和 UA 模板都只有粘贴文本，没有和 bot.sannysoft.com 对照的结果。版本未知，函数若已改名，这些位置就不能直接沿用。
