---
schema_version: 2
id: ruyi-20260609-browserscan-canvas-hash-reference
document_type: reference
original_date: '2026-06-09'
archived_date: '2026-10-02'
scope:
  targets: [browserscan]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260609-01.md#纯算边界
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留 hash 输入、文字图不入 hash、几何图尺寸和 winding 排除。不收录任何样本 hash。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留不支持、不稳定和稳定三条支路，以及渲染器与纯算的分界。作者的同页一致保持 source-report。
relations:
  - type: derived_from
    target: ./ruyi-20260609-01.md#纯算边界
tags: [browserscan, source-report]
---

# BrowserScan /canvas 的 hash 输入边界

这篇卡检索的是：该页稳定时 hash 吃哪一段画布输出，以及 dataURL 为什么不能只靠摘要函数生成。不收录样本 hash，也不提供替换画布输出的做法。

<a id="parameters"></a>
## hash 吃什么

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 稳定时的公式点名 SHA1(geometryDataURL) | s1，源文件第 60 行 | source-report | /canvas 的稳定分支 | 不稳定时不是这个输入 |
| C2 | 文字图只用于稳定性判断，不直接进入最终 hash。 | s1，源文件第 90 行 | source-report | 文字图 | 它仍决定两次输出是否相同 |
| C3 | 几何图把画布改成 122 x 110 | s1，源文件第 106 行 | source-report | 文字图已经稳定之后 | 不复制像素 |
| C4 | winding 不是最终 hash 输入，只是附带结果。 | s1，源文件第 116 行 | source-report | evenodd 点测 | 不改变主公式 |
| C9 | 来源要求验证公式，而不是固定某一个 hash 常量。 | s1，源文件第 161 行 | source-report | 来源自己的两次打开 | 打印出的 hash 不进入本卡 |

<a id="decision-flow"></a>
## 三条返回和纯算分界

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 不支持 PNG dataURL 时返回 "unsupported" | s1，源文件第 86 行 | source-report | supportCanvasPngDataUrl 失败 | 与 unstable 不是同一支路 |
| C6 | 纯算先比较 textDataURL1 === textDataURL2 | s1，源文件第 196 行 | source-report | 已有三次 dataURL 时 | dataURL 不由该式生成 |
| C7 | 纯算脚本负责稳定性判断、SHA1 和辅助解析。 | s1，源文件第 210 行 | source-report | 来源划分的工程边界 | 上一行要求渲染器产生 dataURL |
| C8 | 截断记录不能当作完整 PNG dataURL 或最终 hash 样本。 | s1，源文件第 141 行 | source-report | 长字符串被截断的 trace | 截断长度不在本卡复述 |
| C10 | 作者称同页还原结果完全一致。 | s1，源文件第 181 行 | source-report | 来源的一次同页注入 | 本轮未复跑，样本 hash 不抄 |

## 验证与限制

`canvas` / `webgl` 的既有卡只说明 toDataURL 应与绘制状态同源，没有 BrowserScan 这条“文字图只测稳定、几何图才进 SHA1”的合同。`browser-fingerprint` 是总纲，同样不覆盖该公式。脚本实现不在本文。作者的同页一致和 CRC 通过保持 source-report，正文没有把自检失败写成停止条件。
