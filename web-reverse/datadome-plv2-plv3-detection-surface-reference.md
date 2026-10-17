---
schema_version: 2
id: web-reverse-datadome-plv2-plv3-detection-surface-reference
document_type: reference
original_date: unknown
archived_date: "2026-10-13"
scope:
  targets: [datadome]
  client: web
  version: "1.33.1"
  observed_at: unknown
sources:
  - id: s1
    ref: ./datadome-plv2-plv3-source-archive.md#source-body
    basis: source-report
modules:
  - name: interfaces
    anchor: collection-surfaces
    sources: [s1]
    basis: source-report
    limits: 只整理来源笔记归纳的 API 类别与两条采集面；没有原始 bundle、反汇编或运行时证据，本卡不证明每项均在当前版本执行。
  - name: risk-control
    anchor: detection-patterns
    sources: [s1]
    basis: source-report
    limits: 检测机制与覆盖数量均为来源笔记自述；未复现当前 DataDome 行为，不含设备指纹原值、路径或可运行补环境实现。
relations:
  - type: derived_from
    target: ./datadome-plv2-plv3-source-archive.md#source-body
  - type: supplements
    target: ./datadome-env-patch-reference.md#decision-flow
tags: [datadome, plv2, plv3, browser-environment, source-report]
---

# DataDome plv2 / plv3 静态检测面参考

这张卡概括本地笔记对一个 DataDome interstitial 版本的静态提取结果。笔记中的浏览器、GPU、键盘布局等实测值及本机路径未复制；以下内容仍是来源报告，不代表本轮检查了原始脚本或目标站点。

<a id="collection-surfaces"></a>
## 两条采集面

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源笔记把 plv2 描述为普通 JS 采集，把 plv3 描述为由内层 VM 执行的另一条采集线；两者有重叠项，也有各自独有的面。 | s1，标题下的概览 | source-report | 笔记所述 DataDome 1.33.1 interstitial | 未取得对应 bundle 与 VM 输入，未独立核对版本或分支。 |
| C2 | plv2 类别包括 Navigator、Document、screen、插件 / MIME、媒体能力、Intl、WebAssembly、canvas / WebGL，以及调用栈和函数原生性检查。 | s1，plv2 各节 | source-report | 来源列出的静态调用和字段类别 | 不代表所有类别都在一次请求中执行，也不保留采样值。 |
| C3 | plv3 侧重点包括 WebGL 运算、CSS 布局读回、canvas / SVG 和时间相关宿主能力；来源还报告了对自动化运行时特征的检查。 | s1，plv3 各节 | source-report | 来源列出的 VM 常量与静态分析结论 | 没有反汇编、常量池或目标运行时供本轮复验。 |

<a id="detection-patterns"></a>
## 检测类别与阅读边界

来源笔记将检测面归为两类：

- **宿主对象与能力面**：属性存在性、插件 / MIME 结构、媒体与权限 API、语言 / 时区、WebAssembly 与 GPU 能力等。
- **实现与计算面**：调用栈 / 调用方、原生函数形态、Canvas / WebGL / CSS / SVG 计算结果，以及时间和性能接口。

来源报告强调，静态提取与一次运行轨迹的覆盖范围不同：未执行的版本门、异常分支或 fallback 可能不会出现在单次动态记录中。这个判断只按该笔记转述；它不是对所有混淆脚本或 DataDome 版本的通则。

## 验证与限制

- 笔记引用的 `3.js`、VM 常量池、反汇编与字段映射文件不在本批输入中，原笔记也未提供可公开定位的源码仓库或版本哈希。
- 来源中的设备值、环境哈希、键盘布局、脚本本机路径和逐字段样值不进入本卡。
- 本轮未运行脚本、未构造浏览器环境、未请求 DataDome，也未做本地 parity 或服务端验收。
- 无感 interstitial 的请求链、iframe / Worker 排查和验收边界见 [DataDome 补环境参考](./datadome-env-patch-reference.md)；本卡只补充来源笔记报告的静态检测类别。
