---
schema_version: 2
id: anti-detection-ruyi-20250429-webgl-debug-renderer-reference
document_type: reference
original_date: '2025-04-29'
archived_date: '2026-07-13'
scope:
  targets: [blink-webgl-debug-renderer]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ruyi-20250429-01.md#chromium指纹浏览器开发教程之webgl指纹定制"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只记录来源点名的文件和两个 unmasked case。未对照本地 Chromium 树，版本未知。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留字段角色和 JSON 键名。不记录显卡字符串、命令行样值或哈希。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 扩展门闩和 kRuyi 分支来自来源片段。开关缺失、JSON 无效、缺键以及 renderer 定制返回都没有代码。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留“用于识别”和“交给服务端判别”这两句来源主张。没有站点、规则或结果。
relations:
  - type: derived_from
    target: "./ruyi-20250429-01.md#chromium指纹浏览器开发教程之webgl指纹定制"
tags: [Chromium, Blink, WebGL, source-report]
---

# Blink WebGL debug renderer 返回边界

这张卡只回答：来源把 unmasked vendor/renderer 的读取和返回放在哪里，以及它自己写出了哪一段替换。它不提供可编译补丁，也不把“指纹会变”当成验收。JS 宿主对象的 `getParameter` 类型语义在 canvas/webgl 卡，不在这里。

<a id="interfaces"></a>
## 返回位置

来源把基础渲染信息放在 `webgl_rendering_context_base.cc`。厂商分支的 case 是 `kUnmaskedVendorWebgl`，显卡分支的 case 是 `kUnmaskedRendererWebgl`。两段都先看 `WEBGL_debug_renderer_info` 是否启用。采集脚本对应地调用 `getParameter`，读取 `UNMASKED_VENDOR_WEBGL` 和 `UNMASKED_RENDERER_WEBGL`。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C5 | 文件名只在来源正文中出现 | webgl_rendering_context_base.cc | s1 :135 | source-report | 未对照源码树 |
| C6 | 厂商 case 名 | kUnmaskedVendorWebgl | s1 :139 | source-report | 不证明当前分支仍用该枚举 |
| C11 | 显卡 case 名 | kUnmaskedRendererWebgl | s1 :209 | source-report | 该段是原始返回 |

<a id="parameters"></a>
## 字段角色

脚本在扩展存在时读取上述两个 unmasked 值，并继续读取 `VENDOR`、`RENDERER`、`VERSION`、纹理和渲染缓冲上限、视口维度以及扩展列表。来源没有给出这些值的样例。

厂商替换只出现在命令行带 `kRuyi` 时：片段解析该开关的 JSON，取键 `webgl_vendor` 的字符串并返回。这里只登记键名，不登记键值。显卡分支没有对应的键。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C3 | 脚本读取 unmasked vendor | UNMASKED_VENDOR_WEBGL | s1 :125 | source-report | 未执行脚本 |
| C4 | 脚本读取 unmasked renderer | UNMASKED_RENDERER_WEBGL | s1 :127 | source-report | 未执行脚本 |
| C9 | 替换值来自 JSON 键名 | webgl_vendor | s1 :199 | source-report | 无缺键策略 |

<a id="decision-flow"></a>
## 分支边界

来源片段里，扩展未启用就报错并返回空。扩展启用后，原文返回 GL 字符串；作者插入的厂商片段改为：进程命令行有 `kRuyi` 时返回 `webgl_vendor`。开关不在、JSON 读失败或键不存在时，这段插入没有写出下一步。

显卡 case 仍返回原始 `GL_RENDERER`。作者只说结构类似、可以同样改返回值，替换代码不在文中。作者另称通常改这两个值指纹就会变，那是 source-report，不是本卡的通过条件。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C7 | 先看扩展是否启用 | ExtensionEnabled(kWebGLDebugRendererInfoName) | s1 :141 | source-report | 未启用时的空返回在后文 |
| C8 | 厂商替换还要求 kRuyi | kRuyi | s1 :187 | source-report | 没有 else |
| C10 | “通常会变”是作者判断 | 相关指纹信息就会发生改变。 | s1 :132 | source-report | 无对照结果 |
| C12 | renderer 定制没有代码 | 显卡信息返回值进行定制修改 | s1 :239 | source-report | 不能补写返回 |

<a id="risk-control"></a>
## 判别主张

来源把这类指纹描述为识别和跟踪浏览器的技术，并称编码后的值可以交给网站服务端判别。没有站点、请求或判定结果。browserleaks 的图只说明作者当时在看上下文和显卡信息，不能当成验证记录。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 来源的识别用途 | 用于识别和跟踪用户的浏览器的技术 | s1 :47 | source-report | 不是复现结论 |
| C2 | 来源称会交给服务端 | 传递给网站服务端进行判别。 | s1 :117 | source-report | 无接口和结果 |

## 验证与限制

未对照 Chromium 版本，未编译，未在页面上比较返回值。缺键和 renderer 定制仍是缺口。作者的成功句保持 source-report。
