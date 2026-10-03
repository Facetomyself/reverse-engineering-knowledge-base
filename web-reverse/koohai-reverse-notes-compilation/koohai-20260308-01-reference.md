---
schema_version: 2
id: khbox-browserleaks-js-score
document_type: reference
original_date: '2026-03-08'
archived_date: '2026-10-02'
scope:
  targets:
    - KhBox
    - browserleaks
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./koohai-20260308-01.md#下面贴一下js代码"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留文中计分脚本的条件、分值和评级。不替换 navigator、screen 或 device 的通用对象语义，也不收录脚本外的样例原值。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留三个 getter 在缺失或不可用时的返回形态。setImpl 里的回退字面量不抄入本卡。
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 页面只作为脚本所写的检测页。browserCheckResult 没有提取端。三个函数没有验收。
relations:
  - type: derived_from
    target: "./koohai-20260308-01.md#下面贴一下js代码"
tags:
  - KhBox
  - browserleaks
  - source-report
---

# BrowserLeaks JavaScript 计分脚本和三处 KhBox getter

这张卡只回答两件事：这篇笔记里的计分脚本如何加分和归零，以及 KhBox 追加的三个 getter 在没有数据时返回什么。第 1 到 6 节对屏幕、webdriver、插件、电池和时区的散文，已有的 navigator、screen、browser-fingerprint 与 device-apis 参考卡已经覆盖对象语义；那些卡写明不是站点原值。本卡不把样例分辨率、品牌版本、时区、语言或电量抄进去，也不把散文再补进那些卡。

<a id="risk-control"></a>
## 计分脚本的条件

脚本把结果放进 `window.browserCheckResult`。作者称正常浏览器能到 90 到 100，这里只记录分支，不记录为已跑通。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C2 | 屏幕条件看 `colorDepth`，以及宽高是否大于 0 | s1，屏幕分 | source-report | 该脚本 | 不收录某次分辨率 |
| C3 | 失败文案原文是 `Invalid Resolution` | s1，同一分支 | source-report | checks.screen | 抛错时写成 ERROR |
| C4 | webdriver 为真的文案原文是 `Detected: true` | s1，webdriver 分支 | source-report | 该脚本 | 注释写封顶 50，代码不是 50 |
| C5 | 压分调用原文从 `Math.min(score,` 开始 | s1，同一行 | source-report | 该脚本 | 未运行 |
| C6 | 空插件分支还看 `pdfViewerEnabled` | s1，插件长度 | source-report | UA 含 Chrome 的分支 | 未构造 plugins |
| C7 | 缺少 userAgentData 的文案原文是 `Missing in Chrome` | s1，UA Data 分支 | source-report | 该脚本 | 不收录 brands 样例 |
| C8 | 电池 API 抛错的文案原文是 `FAIL (Error)` | s1，getBattery | source-report | 该 try/catch | 未调用 API |
| C9 | 网络项看 `n.connection` 是否存在 | s1，connection | source-report | 该脚本 | 不收录某次网络类型 |
| C10 | 时区来自 `resolvedOptions` | s1，Intl | source-report | 成功时加 20 | 不收录时区或语言样例 |
| C11 | 命中 `__webdriver_evaluate` 等名单则归零 | s1，bot 扫描 | source-report | 脚本里的五个名字 | 散文里的 cdc_ 前缀不在数组中 |
| C12 | 低于 60 的等级原文是 `Bot Detected` | s1，评级 | source-report | 该脚本的 grade | 未复跑 |

<a id="parameters"></a>
## 三个 getter 的空值形态

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C14 | 函数名原文是 `Navigator_userAgentData_get` | s1，KhBox 片段 | source-report | 这篇笔记追加的函数 | navData 来源不明 |
| C15 | 没有数据时原文是 `userAgentData || undefined` | s1，同一函数 | source-report | 该 getter | 未比较 in 运算符 |
| C16 | 连接开关原文是 `connectionData.available` | s1，connection getter | source-report | available 为假的分支 | 赋值点不在本文 |
| C17 | 可用时创建的类型原文是 `NetworkInformation` | s1，同一函数 | source-report | setImpl 之前 | 不抄回退数值 |
| C19 | 电池接口返回 `Promise.resolve` | s1，getBattery getter | source-report | 成功路径 | 没有 reject |

<a id="interfaces"></a>
## 检测页、结果槽和函数名

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 源页面原文是 `https://browserleaks.com/javascript` | s1 之前点名的页面，脚本按该页的指标编写 | source-report | 这篇笔记 | 本次未打开 |
| C13 | 结果槽原文是 `window.browserCheckResult` | s1，结算 | source-report | 该脚本 | 没有 Node 提取端 |
| C18 | 电池对象类型原文是 `BatteryManager` | s1，getBattery | source-report | createInstance | 没有验收 |
| C20 | 原文把追加实现写成加了几个函数即可 | s1，脚本之后 | source-report | 这三处 | 没有失败出口 |

## 验证与限制

散文里的一次通过结果、品牌版本和时区语言都不进入结论。getter 没有说明 navData、connectionData、batteryData 从哪个文件来。脚本注释和 `Math.min` 的上限不一致时，以代码里的调用为准。这些材料没有验收步骤，不能做成流程。
