---
schema_version: 2
id: ai-android-algorithm-workflow
document_type: archive
original_date: unknown
archived_date: "2026-10-30"
scope:
  targets: [android-algorithm]
  client: app
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: https://mp.weixin.qq.com/s/W3xDragHQ4LDsZjiWvqyFQ
    basis: source-report
source_completeness: partial
tags: [android, jadx, gumtrace, trace, source-report]
---

# 一套基于 AI 的安卓算法分析流程（来源报告）

来源把 App 算法分析收成四段：参数定位、人工日志、trace、再把 trace 交给模型。作者写明只想加快「看懂算法逻辑」，并要把模型和人工的边界分开。没有作者署名，发表日期未知。

四段都没有验收标准和失败出口，图片又补不齐，所以做成 archive，不做成 procedure。

## 清洗与完整性说明

- 删除文末「转自 / 如有侵权请联系删除」。文章定位用 sources 的公开链接。
- 网盘地址和提取码不入库。
- 来源有两张微信图床链接，其余多张是 1px SVG 占位。提示词截图缺失。本文不嵌图片，也不根据缺图编提示词。正文里能读到的那一句不完整提示词按原文保留。
- 作者称四神算法约七分钟且「算法无误」。这是 source-report。本次没有 trace，也没有跑模型。
- 完整性为 partial。

## 来源正文

### （一）参数定位

作者仍从抓包开始，找出要看的参数和接口。下一步不再只靠人工 hook HashMap、拦截器和字符串拼接，而是用 jadx mcp 找生成位置；apktool、jeb 被写成可以一试的替代。作者还希望模型在分析时说明有没有 native 层加密，以及加密入口。两张说明这个步骤的图没有下载到本地，不能把图里的界面当成已核对的点击路径。

这一步的输出，按作者的说法，是算法生成位置和入参，供下一段使用。

### （二）人工日志

作者不让模型在这个阶段直接去 hook。理由是模型写的 hook 可能触发平台侧的滥用判定，并特别点了 Claude。人工介入的方式是：采用模型给出的代码，但加上 `-o`，用来打日志。为什么必须人工，作者说后面会解释；后文没有再给出独立的失败案例，只有第（三）段把这份日志交给 trace。

这里没有命令行全文，不补。

### （三）trace

工具是作者二开的 GumTrace，公开地址 `https://github.com/lidongyooo/GumTrace`。作者称思路参考 xfqtrace：可以主动调用 trace，并用入参的 hex 过滤是不是目标数据。作者把分块传输、断点恢复和流式合并归到「q 佬」的改动。用法是把第（二）段的人工日志交给模型，让模型按文档写主动调用 trace 脚本。

三张 trace 界面图都是 1px 占位，看不到参数。作者写的结果物是一个压缩包，里面有 trace 日志、入参，以及对应返回值的 json。样值不入库。

### （四）分析提示词

提示词图缺失。正文里能读到的句子在「不执着于固定的」处截断，原文是：

> 这是trace日志和返回值信息，分析算法生成逻辑，使用最简python代码复现，要求每一个算法一个py文件，都使用最简洁的算法逻辑，能够使用动态参数调用，不执着于固定的

不补后半句，也不把「一个算法一个 py 文件」写成已验收的输出格式。

作者称在没有降智的 GPT 上，四神算法大约七分钟出来，并且算法无误。结果图同样是占位，没有算法正文。作者还说后续工具会开源，当时仍在测试。

## 复用边界

四段顺序、GumTrace 的公开仓库、`-o` 日志和那句残缺提示词，都只是这篇 source-report。没有前提清单、没有失败出口，不能当成 procedure。缺图的界面和提示词没有被猜写。七分钟和无误不是本次结果。
