---
schema_version: 2
id: anti-detection-ruyi-cbii-isolation-policy-reference
document_type: reference
original_date: '2026-02-26'
archived_date: '2026-07-13'
scope:
  targets: [cloud-browser-isolation-policy]
  client: browser
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260226-01.md#云端浏览器隔离的allow策略漏洞
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只整理来源对一篇西点军校报告的转述。域名占比和请求占比不是通用基线。不含端点名单、像素样本或请求格式。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只整理来源陈述的策略分支。没有配置样例、验收条件或失败出口，不能当成已执行的变更流程。
relations:
  - type: derived_from
    target: ./ruyi-20260226-01.md#云端浏览器隔离的allow策略漏洞
tags: [cbii, browser-isolation, source-report]
---

# 云端浏览器隔离四档策略：allow、isolate 与 read-only

这张卡只回答一个检索问题：来源如何区分云端浏览器隔离的四档策略，以及哪一档才被说成能剥离嵌在其他网站里的追踪代码。它不提供域名清单、策略导出或拦截步骤。

<a id="risk-control"></a>
## 风险控制信号

来源把风险定义成两类：追踪器域名的请求次数可以远高于域名个数；追踪像素嵌在用户本来要访问的其他网站里，而不是用户主动打开的追踪站点。这些数字只属于来源转述的那次测量。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源写 Top 1000 域名里 21.2% 是纯追踪器域名。来源写「这1000个域名里，21.2%是纯追踪器域名」 | s1，ruyi-20260226-01.md:46 | source-report | 来源转述的第一轮域名占比 | 一次来源测量，不是通用比例；不收录端点名单 |
| C2 | 来源写第二轮追踪器域名占连接请求量的 41.89%，高于域名占比。来源写「追踪器域名占了总请求量的41.89%」 | s1，ruyi-20260226-01.md:53 | source-report | 来源转述的第二轮请求量占比 | 来源数字，没有原始流量 |
| C3 | 来源写站点分析数据与浏览器指纹、数据经纪商聚合结合后可以跨设备识别个人。来源写「当这些数据和浏览器指纹技术结合，再被数据经纪商聚合之后，就能识别到个人并跨设备追踪。」 | s1，ruyi-20260226-01.md:76 | source-report | 来源对站点分析数据的风险边界 | 没有聚合字段或识别过程 |
| C8 | 来源写数据集中的 Top 1000 域名都被标成 allow，从而绕过 CBII。来源写「这些追踪器域名完全绕过了CBII的保护，直接和军人的浏览器通信。」 | s1，ruyi-20260226-01.md:123 | source-report | 来源对数据集策略标记的报告 | 来源对一份数据集的陈述，没有策略导出 |
| C12 | 来源写追踪像素不是用户主动访问的网站，而是嵌在其他网站里的代码。来源写「它不是一个用户主动访问的网站，而是嵌入在其他网站中的一小段代码。」 | s1，ruyi-20260226-01.md:147 | source-report | 来源对追踪像素的定义 | 没有像素样本或请求格式 |
<a id="decision-flow"></a>
## 策略分支

来源把 CBII 分成 allow、isolate、isolate, read-only、blocked。allow 不隔离；isolate 仍保留脚本执行；read-only 被写成清洗 DOM；blocked 是封禁。登录后的服务端认证会话被写成 isolate 挡不住的另一条路径。浏览器配置、DNS 拦截和 read-only 被写成必须叠加，但没有验收。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 来源把 allow 定义成直接放行、不经过隔离。来源写「allow：直接放行，不经过隔离」 | s1，ruyi-20260226-01.md:117 | source-report | 来源列出的 CBII 策略 | 没有策略配置样例 |
| C5 | 来源把 isolate 定义成云端容器渲染且保持交互。来源写「isolate：在云端容器中渲染，但保持交互性」 | s1，ruyi-20260226-01.md:118 | source-report | 来源列出的 CBII 策略 | 没有容器产品版本 |
| C6 | 来源把 isolate, read-only 定义成剥离所有可执行代码、只返回静态内容。来源写「isolate, read-only：在云端容器中渲染，剥离所有可执行代码，只返回静态内容」 | s1，ruyi-20260226-01.md:119 | source-report | 来源列出的 CBII 策略 | 没有 DOM 清洗实现 |
| C7 | 来源把 blocked 定义成完全封禁。来源写「blocked：完全封禁」 | s1，ruyi-20260226-01.md:120 | source-report | 来源列出的 CBII 策略 | 没有封禁名单 |
| C9 | 来源写把追踪器域名从 allow 改成 isolate 仍不够，登录大站后的服务端认证会话可以跨设备追踪。来源写「即使把追踪器域名从"allow"改成"isolate"，也不够。」 | s1，ruyi-20260226-01.md:125 | source-report | 来源对 isolate 的失败条件 | 没有会话协议或账号材料 |
| C10 | 来源写只有 isolate, read-only 会清洗 DOM 并剥离追踪代码。来源写「才能真正剥离追踪代码——它会清洗DOM，只返回纯静态内容。」 | s1，ruyi-20260226-01.md:126 | source-report | 来源对 read-only 的效果陈述 | 没有清洗前后的 DOM 对照 |
| C11 | 来源写 isolate 仍保留 JavaScript，追踪代码能在容器里运行；read-only 剥离可执行代码。来源写「前者保留了JavaScript执行能力，追踪代码仍然可以在云端容器中运行并将数据发回追踪服务器」 | s1，ruyi-20260226-01.md:141 | source-report | 来源对两种 isolate 的区别 | 没有脚本样本 |
| C13 | 来源写浏览器配置、DNS 拦截和 isolate, read-only 任一层都不够。来源写「任何单一层都不够——浏览器配置挡不住"allow"策略下的直连流量，DNS拦截挡不住IP直连的追踪请求，CBII挡不住桌面软件的遥测。」 | s1，ruyi-20260226-01.md:183 | source-report | 来源建议的三层覆盖及其单层缺口 | 建议没有验收条件和失败出口，不构成流程 |

## 验证与限制

实战建议有十三则，但来源没有把前提、步骤、输出、验收和失败出口五段写全，所以不升为流程。攻击方视角只有风险命名，本卡不补采集或绕过步骤，也不列出追踪端点。`../../web-reverse/browser-env-objects/fingerprint-overview.md` 不包含这四档隔离策略。
