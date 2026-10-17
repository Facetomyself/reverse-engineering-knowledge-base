---
schema_version: 2
id: third-party-browser-fetcher-boundaries
document_type: reference
original_date: "2026-10-09"
archived_date: "2026-10-09"
scope:
  targets: [Scrapling]
  client: python
  version: "0.4.15"
  observed_at: unknown
sources:
  - id: s-chrome
    ref: https://github.com/D4Vinci/Scrapling/blob/aa814a77d942678f1a44f68198a0c88550382d28/scrapling/fetchers/chrome.py
    basis: static-review
  - id: s-stealth
    ref: https://github.com/D4Vinci/Scrapling/blob/aa814a77d942678f1a44f68198a0c88550382d28/scrapling/engines/_browsers/_stealth.py
    basis: static-review
  - id: s-pages
    ref: https://github.com/D4Vinci/Scrapling/blob/aa814a77d942678f1a44f68198a0c88550382d28/scrapling/engines/_browsers/_validators.py
    basis: static-review
  - id: s-docs
    ref: https://github.com/D4Vinci/Scrapling/blob/aa814a77d942678f1a44f68198a0c88550382d28/docs/fetching/stealthy.md
    basis: source-report
  - id: s-readout
    ref: ../collection-engineering/scrapling-0.4.15-readout.md#fetchers
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s-chrome, s-stealth, s-pages]
    basis: static-review
    limits: 只说明 0.4.15 源码里的启动方式和标签页池上限。没有启动浏览器，没有连接 CDP，没有核对驱动版本是否仍能安装。
  - name: risk-control
    anchor: risk-control
    sources: [s-docs, s-readout]
    basis: source-report
    limits: 过检测、Cloudflare、canvas 和 WebRTC 只保留作者文档自述。本卡不把它写成绕过已成立，也不提供操作步骤。
relations:
  - type: derived_from
    target: ../collection-engineering/scrapling-0.4.15-readout.md#fetchers
tags: [Scrapling, Playwright, Patchright, CDP, source-report, static-review]
---

# 第三方浏览器 fetcher 的边界

这张卡回答一个检索问题：Scrapling 0.4.15 的动态浏览器和隐身浏览器能不能进入本仓库的采集运行时。不能。

<a id="interfaces"></a>
## 接口平面

| 平面 | 0.4.15 源码里能确认的事 | 本仓库对应面 |
|---|---|---|
| DynamicFetcher | 文档写明走 Chromium 系浏览器，可选 `real_chrome`，也可用 `cdp_url` 连接已有浏览器 | 不接入 |
| StealthyFetcher | 隐身引擎文件用 Patchright 启动，类型仍引用 Playwright Page | 不接入 |
| 标签页池 | `PagesCount` 为 1 到 50，是同时打开的标签上限 | 不是 `maxPages` |
| Camoufox | 当前 `fetchers` extra 无此依赖；文档仍保留自行安装后塞启动参数的说明 | 不是 ruyipage |

本仓库允许的浏览器平面只有三档，互不替代：RuyiTrace 3.3 提供浏览器事实；RuyiDOM 做本地执行；自动化只使用 ruyipage Firefox 151、BitBrowser 或 CloakBrowser。Python 采集器不自带浏览器。

<a id="risk-control"></a>
## 风控自述与拒绝项

作者文档把隐身 fetcher 写成能通过大量在线检测，并提供 Cloudflare challenge 开关、canvas 噪声、WebRTC 设置、browserforge 请求头、随机 impersonate、默认 Google referer、丢弃静态资源和广告域名拦截。这些句子停留在 `source-report`。本次阅读没有执行它们，不能写成“已绕过”。

采集落地不吸收上述开关，也不吸收为了使用它们而引入的 Playwright、Patchright、CDP 或 Camoufox。`scrapling-mcp` 会拉起浏览器并批量抓取，不注册。
