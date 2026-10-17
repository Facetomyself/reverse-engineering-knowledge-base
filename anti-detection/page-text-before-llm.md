---
schema_version: 2
id: page-text-before-llm
document_type: procedure
original_date: "2026-10-09"
archived_date: "2026-10-09"
scope:
  targets: [page text before model]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s-shell
    ref: https://github.com/D4Vinci/Scrapling/blob/aa814a77d942678f1a44f68198a0c88550382d28/scrapling/core/shell.py
    basis: static-review
  - id: s-ruyi
    ref: ./ruyi-browser-anti-detection-compilation/ruyi-20260430-01.md#四前提3间接提示注入agent为什么会执行网页里的指令
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [s-shell, s-ruyi]
    basis: source-report
    limits: 只补充送模型前的文本缺口。清洗通过不是内容可信，也不是绕过。未对活页做 runtime。不复制上游 XPath。
relations:
  - type: derived_from
    target: ../collection-engineering/scrapling-0.4.15-readout.md#sanitize
  - type: supplements
    target: ./ruyi-browser-anti-detection-compilation/ruyi-20260430-01.md#四前提3间接提示注入agent为什么会执行网页里的指令
tags: [prompt-injection, page-text, decision-flow, source-report]
---

# 页面文本送进模型之前

这份流程处理“准备把页面文字交给模型”这一步。它补充已有合集里关于间接提示注入的讨论，不替换那篇文章，也不把清洗器当成信任门。

<a id="prerequisites"></a>
## 前提与输入

输入是将要送进模型的 HTML 或已抽出的文本，以及它的来源页面。没有页面来源、只拿到一段来历不明的字符串，走 F1。不要在这一步执行页面脚本，不要为了清洗去启动浏览器。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 标出即将进入模型的那一段，分开脚本、样式、注释和正文 | 一段带来源的文本，或发现来源缺失 | 来源在，走 S2；否则 F1 |
| S2 | 去掉最小集合：内联样式里的隐藏（display none、visibility hidden、opacity 0、font-size 0、零宽高）、`aria-hidden`、`template`、零宽字符、控制字符，以及合集文章已经点名的 `display:none`、script/style 和注释 | 清洗后的文本，并记下删过哪几类 | 记下缺口后走 S3 |
| S3 | 把 class 隐藏和低对比度可见文字标成仍可能漏过 | 一份“未证明可信”的文本 | 可以交给模型做候选阅读；不能走 S4 那种信任结论 |
| S4 | 禁止步骤 | 无 | 谁把清洗通过写成“页面可信”，走 F2 |

上游清洗函数只覆盖 S2 里的内联样式、`aria-hidden`、`template`、零宽字符和控制字符，而且挂在“只要正文”的提取路径上。class 隐藏和低对比度可见文字不在其中。所以 S2 做完仍要做 S3。

<a id="outputs"></a>
## 输出

输出清洗后的文本、删过的类别，以及一句限制：这次通过不是内容信任。不要输出“已去除提示注入”或“可以执行页面中的指令”。

<a id="acceptance"></a>
## 验收

记录里能看到来源页面、S2 的类别，以及 S3 的漏过声明。只看到“函数返回了字符串”不算通过。本篇没有把这套清洗接到采集器或模型调用上。

<a id="failure-exits"></a>
## 失败出口

F1：文本没有页面来源。停止，不把这段文字当页面事实。

F2：清洗通过被写成内容可信、服务端接受，或可以执行网页里的指令。收回该结论。class 隐藏和低对比度文字仍然能把指令留在可见树里。
