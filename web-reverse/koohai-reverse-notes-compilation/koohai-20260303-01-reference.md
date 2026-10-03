---
schema_version: 2
id: khbox-canvas-todataurl-branch
document_type: reference
original_date: '2026-03-03'
archived_date: '2026-10-02'
scope:
  targets:
    - KhBox
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./koohai-20260303-01.md#二风控检测了什么-jsdom_canvasjs-分析"
    basis: source-report
  - id: s2
    ref: "./koohai-20260303-01.md#三框架如何对抗-envfuncsjs-实现"
    basis: source-report
  - id: s3
    ref: "./koohai-20260303-01.md#五优先级与使用方式"
    basis: source-report
  - id: s4
    ref: "./koohai-20260303-01.md#七局限性与后续方向"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1, s4]
    basis: source-report
    limits: 扣分标志来自文中粘贴的检测脚本和分析小节。未运行脚本。作者的通过表只覆盖 sRGB 与 WebP，颜色数量仍被写成失败。
  - name: parameters
    anchor: parameters
    sources: [s2, s3]
    basis: source-report
    limits: 只保留 toDataURL 分支、session 缓存和 canvasRandom 的三层来源。PNG 字节组装没有完整实现。不收录被省略的 WebP 载荷。
  - name: interfaces
    anchor: interfaces
    sources: [s2, s3, s4]
    basis: source-report
    limits: 只点名 envFuncs.js 的 Hook 名、三个被改文件和 POST /sign 这个入口。不收录请求体中的其它字段，也没有响应样本。
relations:
  - type: derived_from
    target: "./koohai-20260303-01.md#五优先级与使用方式"
tags:
  - KhBox
  - canvas
  - source-report
---

# KhBox 笔记里的 Canvas 扣分标志和 toDataURL 分支

这张卡只回答 2026-03-03 这篇 KhBox 笔记：检测脚本扣哪些标志，`toDataURL` 按什么顺序返回，`canvasRandom` 从哪一层覆盖。它不是 PNG 生成器，也不把对照表里的通过写成已复现。

通用 Canvas / WebGL 对象语义仍看浏览器环境对象里的 Canvas / WebGL 参考卡。那张卡写明只覆盖宿主对象语义，没有这里的 chunk 标志、WebP 分支、session 缓存或 `/sign` 开关。

<a id="risk-control"></a>
## 检测脚本里的扣分标志

分析小节说 `test_jsdom/jsdom_canvas.js` 有五个维度，标题只展开了四项。颜色计数留在粘贴脚本里。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | `fillText.toString()` 要包含 `[native code]`，否则扣分 | s1，检测项一 | source-report | 文中的检测脚本 | 未运行 |
| C2 | 失败标志原文是 `fillText_hooked` | s1，同一行 | source-report | 该脚本 | 不包含 safeFunc 的实现 |
| C3 | 颜色过低的标志原文是 `color_count_too_low`，其下还有 `color_count_suspicious` | s1，粘贴脚本的颜色计数 | source-report | 该脚本的 220×30 画布 | 阈值不能挪到别的尺寸 |
| C4 | getImageData 失败的标志原文是 `getImageData_error` | s1，同一颜色分支 | source-report | 该脚本 | 未构造异常 |
| C5 | 缺少 sRGB 的标志原文是 `missing_sRGB_chunk` | s1，PNG chunk 小节 | source-report | 该脚本解析出的 chunk 名 | 未解析真实 PNG |
| C6 | 出现 pHYs 的标志原文是 `has_pHYs_chunk` | s1，同一小节 | source-report | 该脚本 | Cairo 行为是作者对照 |
| C7 | 随机 PNG 被写成只有 1 个像素，颜色数量检测仍无法通过 | s4，局限性 | source-report | 文中的 1×1 随机 PNG | 不是通过项 |
| C8 | `[native code]` 外观依赖 `addon.safeFunc()`，原文写不在本次改造范围内 | s4，局限性 | source-report | 本次 Canvas 改造之外 | 本文没有该函数 |
| C20 | 作者把修掉的扣分点写成 `webp_unsupported` 与 sRGB 缺失 | s1 的对照表 | source-report | 作者自称的随机模式 | 未复跑，不能当成验收 |
| C22 | 小节原文写五个维度，标题并没有五个检测项 | s1，分析导语 | source-report | 这篇笔记的编号 | 不能据此发明第五个标题 |

<a id="parameters"></a>
## toDataURL 分支和 canvasRandom 来源

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C9 | WebP 类型按 `image/webp` 单独返回，不进入随机 PNG | s2，WebP 伪造 | source-report | 该 Hook 片段 | 不抄被省略的载荷 |
| C10 | 随机结果放在 `_sessionPng`，由 `isCanvasRandom` 决定是否生成 | s2，session 缓存 | source-report | 工厂函数作用域 | 未比较多次返回值 |
| C11 | 原文要求同一个 session 内调用返回同一个值 | s2，同一小节 | source-report | toDataURL | 稳定性未被复测 |
| C12 | 读取顺序原文是 `userVar?.canvasRandom ?? khBox.config?.canvasRandom ?? false` | s3，envFuncs 清单 | source-report | 这篇笔记的三层配置 | 未打开赋值点 |
| C13 | 最高层原文写成 `POST /sign` 的 body | s3，优先级 | source-report | 文中的本地示例 | 没有响应 |
| C14 | 最底层原文是 `KHENV_CONFIG.canvasRandom` | s3，同一行 | source-report | 不改配置时的默认 | 默认关闭只来自片段 |
| C15 | IDAT 压缩被写成 `zlib.deflateSync`，chunk 由 `_pngChunk` 组装 | s2，PNG 修复 | source-report | 随机模式的结构说明 | 没有可编译的查找表 |

分支图的另外两支是配置里的 data URL，以及 jpeg/png 兜底占位图。占位图会被前面的 sRGB 检测扣分，所以它不是随机模式的输出。

<a id="interfaces"></a>
## 被点名的 Hook 和入口

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C16 | Hook 名原文是 `HTMLCanvasElement_toDataURL` | s2，envFuncs | source-report | 该注册表 | 其它 Hook 不在本卡 |
| C17 | 全局默认值所在文件原文含 `KhEnv.js` | s3，改造清单 | source-report | 这次三个文件 | 没有整文件 |
| C18 | 请求透传所在文件原文是 `server.js` | s3，改造清单 | source-report | runSign 路径 | 不收录其它 body 字段 |
| C19 | 增加字段的函数原文是 `runSign()` | s3，改动一 | source-report | POST body | 未发送请求 |
| C21 | WebGL 入口只被写成 `customData.webgl` | s4，局限性 | source-report | 后续方向 | 没有参数表 |

## 验证与限制

对照表里的通过是作者自述。1 像素 PNG 过不了颜色计数；`fillText` 的原生外观不在这次改动里。curl 没有失败分支，不能当成流程。WebP 载荷和请求体里的会话材料都不进入本卡。
