---
schema_version: 2
id: ruyi-20260610-zhipin-nodebug-reference
document_type: reference
original_date: '2026-06-10'
archived_date: '2026-10-02'
scope:
  targets: [zhipin]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260610-01.md#最终判断
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留快捷键层、轮询、来源点名的命中类型、未启用项和端口分界。不写绕过，不抄上报话题字段。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留 no-debug 上报之后的页面写入，以及端口探测不是这条跳转的主链。空着的验证摘要不能当验收。
relations:
  - type: derived_from
    target: ./ruyi-20260610-01.md#最终判断
tags: [zhipin, source-report]
---

# zhipin 页面 DevTools 处理与端口探测的分界

这篇卡检索的是：来源如何把快捷键拦截、no-debug 轮询和 about:home 分成一条链，以及本地端口探测为什么被写成另一条线。不提供绕过步骤。

<a id="risk-control"></a>
## 页面在检查什么

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | F12 被禁用是事实，但它只是快捷键阻断层。 | s1，源文件第 311 行 | source-report | 该页 keydown | 不是后续跳转本身 |
| C2 | 命中的快捷键会 e.preventDefault() | s1，源文件第 65 行 | source-report | 捕获阶段监听 | 验证结果小节是空的 |
| C3 | 字符串还原的末步是 atob + TextDecoder("utf-8") | s1，源文件第 77 行 | source-report | encryptPwd 里的本地解码 | 复算结果是空的，种子不进入本卡 |
| C4 | 活动 detector 每约 500ms 被调用一次。 | s1，源文件第 133 行 | source-report | Hm 轮询 | 隐藏和弹窗时会暂停 |
| C5 | 来源写这次命中的就是这个类型，指 console.table 耗时检测。 | s1，源文件第 189 行 | source-report | 来源的这次打开 DevTools | 没有给出计时数值 |
| C6 | 正则项本次入口初始化列表没有启用。 | s1，源文件第 201 行 | source-report | ig 中的未启用项 | 不能当成这次跳转原因 |
| C7 | id getter 的解释落在引文 id getter 时，getter 会打开检测。 | s1，源文件第 165 行 | source-report | 该 detector 的来源解释 | 不是这次被点名的命中类型 |
| C11 | 端口探测代码包含 probeLocalPort(18789 | s1，源文件第 260 行 | source-report | security 脚本中的本地探测 | 同一行还有第二个端口；作者称这次超时 |

<a id="decision-flow"></a>
## 跳转主链和另一条遥测

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 命中后的动作名是 no-debug-event | s1，源文件第 125 行 | source-report | detector 基类触发器 | 上报体中的话题字段不抄 |
| C9 | about:home 的直接原因是 Bm 对 body 和 location.href 的写入。 | s1，源文件第 314 行 | source-report | 原生完整性检查通过的路径 | 引文“的直接原因是”位于该句 |
| C10 | 原生完整性检查失败时走另一条路径。 | s1，源文件第 250 行 | source-report | Bm 的失败分支 | 来源只定性为另一条路径 |
| C12 | 端口探测属于独立遥测，不是本次跳转主链路。 | s1，源文件第 315 行 | source-report | 来源的最终判断 | 当前环境未命中保持 source-report |

## 验证与限制

zhipin、boss、devtools、cdp 在现有目录里没有同模块卡片。字符串复算、初始化含义和命令结果摘要是空的。开关请求的正文没有留下，标识不进本卡。这里只区分主链和端口遥测，不构成可执行流程。
