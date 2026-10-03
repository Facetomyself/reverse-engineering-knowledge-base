---
schema_version: 2
id: ruyi-20260214-crawler-fingerprint-reference
document_type: reference
original_date: '2026-02-14'
archived_date: '2026-10-02'
scope:
  targets: [crawler-fingerprint-detection]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260214-01.md#22-第二阶段找出用指纹检测的网站
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留来源对指纹检测判定、eval 长度和跨站共享的转述。未复现 Hook，不收录第六节的覆写脚本，也不抄环境值。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留两只爬虫对照后的人工标注规则。没有截图样本，不能当成当前站点的自动判定。
relations:
  - type: derived_from
    target: ./ruyi-20260214-01.md#22-第二阶段找出用指纹检测的网站
tags: [crawler-fingerprint, source-report]
---

# 爬虫指纹检测的判定与标注边界

这篇卡只回答一个检索问题：该文转述的论文怎样把站点判成“在用指纹检测”，以及拦截标注在两边都 403 时怎么分支。不提供伪装脚本，也不把拦截率数字当成可复现结果。

<a id="risk-control"></a>
## 检测判定

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 三条要同时成立才算使用指纹检测：1. 调用了canvas/WebGL/audio/WebRTC相关API（强指纹特征）2. 访问了爬虫特征属性（如navigator.webdriver、window._phantom）3. 访问了至少12个指纹属性 | s1，源文件第 98 行 | source-report | 该文转述的 291 个拦截站筛选 | 未复现注入脚本 |
| C2 | 浏览器一致性里，如果UA声称是Chrome，但这个值不是33，就是伪造的 | s1，源文件第 152 行 | source-report | eval.toString().length 这一检查点 | 长度未在当前引擎复核 |
| C3 | 覆盖深度不一致：只有1家做了完整的OS一致性验证和编解码器检测 | s1，源文件第 140 行 | source-report | 文中四家未点名脚本 | 公司名未公开，空单元格不能补成“未检测” |
| C4 | 跨站效应：同一家反爬公司部署在多个网站上时，会共享检测结果。 | s1，源文件第 298 行 | source-report | 该文实验里观察到的同一服务 | 没有站点名或请求证据 |

<a id="decision-flow"></a>
## 拦截标注

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 对照结果直接标拦截：Crawler 1看到CAPTCHA或拦截页面，Crawler 2正常 → blocked | s1，源文件第 83 行 | source-report | Headless 标记 UA 与普通 Chrome UA 的首页加内页对照 | 依赖人工看截图 |
| C6 | 两边失败不能直接下结论：两个都403 → 手动用住宅IP验证，如果正常访问则blocked | s1，源文件第 84 行 | source-report | 两次访问都是 403 的站点 | 没有住宅 IP 记录；无法判断则保持 unknown |

## 验证与限制

近邻 `browser-fingerprint` 的 risk-control 只描述通用宿主对象，不包含这三条站点判定。`datadome` 的已有卡片是 interstitial 请求链，不是这篇论文的标注流程。附录里的属性名不另建模块。第六节的启动参数和 init script 没有验收、失败出口，本卡不收录。作者给出的拦截计数保持 source-report，本次没有运行证据。
