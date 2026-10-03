---
schema_version: 2
id: grok-anti-detection-benru-anti-20260205-01
document_type: reference
original_date: "2026-02-05"
archived_date: "2026-10-02"
scope:
  targets: [http-request-headers]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./benru-anti-20260205-01.md#二爬虫经常检测的地方"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只记录来源列出的请求头可疑点。未对任何站点复现，不把这些点当成当前服务端规则。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录来源写下的时间窗口和基础头字段。不收录 User-Agent 字面量。归档代码在关键字和名字之间缺空格，不能当可执行实现。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 概率、重试状态码和延迟分档都是来源注释里的策略，不是实测分布。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 只描述单次 GET 前如何补头。没有目标站点，也没有多跳接口。
relations:
  - type: derived_from
    target: "./benru-anti-20260205-01.md#二爬虫经常检测的地方"
tags: [http-request-headers, user-agent, referer]
---

# HTTP 请求头一致性的来源策略

这张卡只回答一个检索问题：这篇归档把哪些请求头现象写成爬虫信号，以及它为 UA 类别、Referer、缓存头和重试写下了什么规则。范围是来源文本，不是某个已命名站点。User-Agent 字面量不进入卡片。作者称换上同样的请求头就有效，保持为来源陈述；本轮没有发请求。

<a id="risk-control"></a>
## 来源列出的请求头信号

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源把 User-Agent 里的爬虫关键词写成直接判定。quote: User-Agent里有爬虫关键词 | s1 ./benru-anti-20260205-01.md:73 | source-report | http-request-headers | 未复现 |
| C2 | 来源把过少、过简单的请求头写成可疑。quote: 请求头太少太简单 | s1 ./benru-anti-20260205-01.md:74 | source-report | http-request-headers | 未给出条数阈值 |
| C3 | 来源把缺少 Accept-Language 写成不像真人。quote: 没有Accept-Language | s1 ./benru-anti-20260205-01.md:76 | source-report | http-request-headers | 未复现 |
| C4 | 来源把不合理 Referer 写成假跳转路径。quote: Referer不合理 | s1 ./benru-anti-20260205-01.md:78 | source-report | http-request-headers | 未定义何种 Referer 算合理 |
| C5 | 来源写明只换请求头并不能覆盖所有网站。quote: 你以为换了请求头就万事大吉了吗？ | s1 ./benru-anti-20260205-01.md:476 | source-report | http-request-headers | 下一篇才转到 TLS，本篇没有 TLS 参数 |

<a id="parameters"></a>
## 时间窗口与基础头

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 工作时间 9:00-18:00 来源主要选 Chrome 和 Edge 类别；同一注释写非工作时间主要选 Firefox 和 Safari。quote: 工作时间（9:00-18:00）：主要返回Chrome和Edge浏览器UA | s1 ./benru-anti-20260205-01.md:93 | source-report | 来源 UA 管理器注释 | 不记录 UA 字面量 |
| C7 | 来源初始化的语言头取值为 zh-CN,zh;q=0.9,en;q=0.8。quote: 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8' | s1 ./benru-anti-20260205-01.md:381 | source-report | SmartSession 基础头 | 只此文本，不是内容协商结果 |

<a id="decision-flow"></a>
## 分支、重试与抄头

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 首次访问某域名时，来源写 70% 概率使用搜索引擎 Referer。quote: 首次访问域名：70%概率来自搜索引擎 | s1 ./benru-anti-20260205-01.md:253 | source-report | Referer 注释 | 与后文 0.7 判断同属来源策略，未抽样 |
| C9 | 直接访问分支写 30% 几率不带 Referer。quote: 30%几率没有Referer（直接输入网址） | s1 ./benru-anti-20260205-01.md:289 | source-report | get_direct_referer | 未复现 |
| C10 | 重试注释写 429、500、502、503、504，并写 backoff_factor=0.5。quote: 自动重试策略（429、500、502、503、504状态码） | s1 ./benru-anti-20260205-01.md:327 | source-report | SmartSession 注释 | 未看重试是否真正发出 |
| C11 | 来源建议对照浏览器 Network 面板抄请求头，并写今天有效的方法明天可能失效。quote: 打开浏览器的开发者工具（F12），切换到Network标签 | s1 ./benru-anti-20260205-01.md:470 | source-report | 总结 | 没有附带任何真实头样本 |

<a id="request-chain"></a>
## 单次 GET 前的补头顺序

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C12 | 来源头里没有 User-Agent 时才补；该 URL 第一次出现时走搜索引擎 Referer。quote: 如果是首次访问该URL，生成搜索引擎Referer | s1 ./benru-anti-20260205-01.md:416 | source-report | SmartSession.get | 访问历史只存在于该对象的文本描述 |
| C13 | 来源写 80% 的请求带缓存相关头。quote: 80%使用缓存 | s1 ./benru-anti-20260205-01.md:426 | source-report | SmartSession.get | 只看到 max-age=0 与 no-cache 两个候选 |

## 验证与限制

本轮只读文本。归档代码在 `class` / `def` 与标识符之间缺空格，例如小时判断写成粘连形式，因此不能把代码块当成可运行实现。没有目标主机，没有响应样本。C5 说明请求头策略在来源自己的叙述里就不是充分条件。近邻查询里，`http-request-headers` 与 `User-Agent` 的同名模块都没有已有卡片；百家号参考卡的目标不同，不在这里合并。
