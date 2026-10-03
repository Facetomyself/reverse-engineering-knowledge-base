---
schema_version: 2
id: ruyi-20260408-bidi-challenge-entry
document_type: reference
original_date: '2026-04-08'
archived_date: '2026-10-02'
scope:
  targets: [ruyipage]
  client: web
  version: '151'
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260408-01.md#下一代web自动化框架乱杀5s盾cloudfare
    basis: source-report
  - id: s2
    ref: ./ruyi-20260408-01.md#过copilot定制5s盾需要ip纯净否则弹窗都失败
    basis: source-report
  - id: s3
    ref: ./ruyi-20260408-01.md#过copilot定制5s盾需要ip纯净否则弹窗都失败
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2]
    basis: source-report
    limits: 只保留 BiDi 与内核抹除 webdriver 的对应句、非 JS 的 isTrusted，以及 IP 不纯则弹窗失败。作者的“没被拦住”不是本轮结果。无指纹取值。
  - name: interfaces
    anchor: interfaces
    sources: [s3]
    basis: source-report
    limits: 只保留挑战函数的调用参数和真假两句打印。函数体不在来源。不转录 cookie 打印。
relations:
  - type: derived_from
    target: ./ruyi-20260408-01.md#过copilot定制5s盾需要ip纯净否则弹窗都失败
tags: [ruyipage, bidi, source-report]
---

# ruyiPage 的 BiDi 前提与挑战入口

这篇卡检索的是：2026-04-08 这篇把“没有 CDP 检测点”限定在什么浏览器上，以及 Copilot 定制 5s 在源码里只露出哪个调用。不提供挑战内部步骤。

<a id="risk-control"></a>
## 检测主张的边界

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 无检测点被写成协议选择的结果：不存在CDP检测点 | s1，源文件第 40 行 | source-report | 该文声称的 BiDi 火狐框架 | 作者断言，本轮未打开浏览器 |
| C2 | 浏览器前提是：必须使用内核层抹除了webdriver的火狐浏览器 | s1，源文件第 40 行 | source-report | 同一句后的 151 只是作者点名的版本 | 没有抹除位置 |
| C3 | 输入被写成：如意原生isTrusted行为（非JS） | s1，源文件第 37 行 | source-report | 该文的行为自动化说法 | 没有事件构造 |
| C4 | 作者成功句是：没见到被任何网站拦住的 | s1，源文件第 37 行 | source-report | 引言里的站点列举 | 无请求、无时间、无失败样本 |
| C5 | Copilot 一节的失败前提：需要IP纯净，否则弹窗都失败 | s2，源文件第 61 行 | source-report | 该节标题所指的定制 5s | 没有纯净判定，也没有换路 |

<a id="interfaces"></a>
## 挑战调用

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 源码只调用一次：passed = page.handle_cloudflare_challenge(timeout=120, check_interval=2) | s3，源文件第 87 行 | source-report | 该粘连示例里的 FirefoxPage | 函数体不在本文 |
| C7 | 假分支的原文是：超时未通过 | s3，源文件第 88 行 | source-report | passed 的假分支 | 真分支的 cookie 打印不转录；通过与否没有独立页面条件 |

## 验证与限制

`ruyipage` 的 risk-control 和 interfaces 都没有已有卡。`ruyipage Firefox browser collector stability` 的 risk-control 是单出口 IP 的软挑战时间窗、断言崩溃和 OOM，不是这个调用。`cloudflare` 的 request-chain 是另一条挑战链路，没有 `handle_cloudflare_challenge`。第 62-86 行的选择器、提问句、发送失败和找不到输入框都不进入本卡。第 89-90 行无论结果都再等 500 秒后 quit，所以不能把返回值升成流程。
