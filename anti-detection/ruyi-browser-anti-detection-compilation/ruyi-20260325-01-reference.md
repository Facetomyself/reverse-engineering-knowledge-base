---
schema_version: 2
id: ruyi-20260325-stylisticfp-reference
document_type: reference
original_date: '2026-03-25'
archived_date: '2026-10-02'
scope:
  targets: [stylisticfp]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ruyi-20260325-01.md#怎么做到的iframe--媒体查询的精密机关"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留该文转述的尺寸回传结构：iframe 视口、分组请求数、媒体特性的幂次编码。不收录元素像素表或字体名单。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 绕过与部署对照都是来源对论文的转述。Brave 字体通道按来源已在 v1.44 修复，不能当成当前版本仍开放。
relations:
  - type: derived_from
    target: "./ruyi-20260325-01.md#怎么做到的iframe--媒体查询的精密机关"
tags: [stylisticfp, source-report]
---

# StylisticFP 的 CSS 尺寸回传

这篇卡检索的是：该文转述的 StylisticFP 如何不用 JavaScript、靠元素尺寸和媒体查询把环境差异送回服务器，以及来源对 Tor、扩展和 Brave 字体通道怎么下判断。不收录“换成常见环境”的建议。

<a id="parameters"></a>
## 回传结构

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 条件满足就发请求：这是一个纯CSS行为，不需要JavaScript。 | s1，源文件第 69 行 | source-report | 媒体查询触发背景图 URL | 没有请求路径表 |
| C2 | 尺寸探针靠子文档视口：iframe内部的CSS媒体查询会把iframe本身当作视口。 | s1，源文件第 80 行 | source-report | 该文的 iframe 测尺寸步骤 | 媒体查询不能直接量单个元素，这是来源给出的绕法 |
| C3 | 分组后的请求量：总共只需要83个网络请求 | s1，源文件第 122 行 | source-report | 339 个元素分成 25 组再加 1 个主 iframe | 未复测请求数 |
| C4 | 特性支持压成一个宽度和：每个元素的宽度是2的幂次。 | s1，源文件第 139 行 | source-report | 23 个 CSS 媒体特性的二进制编码 | 特性名单不在这句 |

<a id="risk-control"></a>
## 来源报告的防御边界

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 尺寸通道仍在：Tor没有伪造  ` min-width  ` 和  ` min-height  ` 媒体特性。 | s1，源文件第 219 行 | source-report | 该文对 Tor 的媒体查询对照 | 屏幕分辨率被写成无效，因为 Tor 强制返回固定值 |
| C6 | 只 Hook 脚本的扩展碰不到：StylisticFP不调用任何JavaScript API。 | s1，源文件第 255 行 | source-report | 该文点名的六款 Chrome 扩展 | 没有逐个扩展的复测 |
| C7 | 本地字体文件这条被标成已修：Brave因此给论文作者发了一笔漏洞赏金，并在v1.44修复了这个绕过。 | s1，源文件第 179 行 | source-report | Brave 字体随机化对 `@font-face` 本地文件的那次绕过 | 修复范围以这句为限 |
| C8 | 跨访问更稳、碰撞也更多：FingerprintJS有188台设备跨访问指纹不一致（主要因Canvas和screenFrame不稳定），StylisticFP只有41台 | s1，源文件第 297 行 | source-report | 该文九周、866 台设备的部署转述 | 同段还写 CSS 尺寸在同配置设备上更容易撞车 |
| C9 | 伪造尺寸查询会拆布局：是响应式设计的核心——如果伪造这两个值，几乎所有响应式网站的布局都会乱掉。 | s1，源文件第 335 行 | source-report | 来源对伪造 min-width / min-height 的判断 | 不是防御实现说明 |

## 验证与限制

`css` / `font` 的风险控制卡描述 computed style、FontFaceSet 和 `matchMedia` 的对象语义，不覆盖用 iframe 视口把元素尺寸送回服务器。`stylisticfp` 目标下没有已有卡片。元素渲染像素和字体名单不写入本卡。给自动化的环境建议没有验收和失败出口，不建流程。部署数字保持 source-report。
