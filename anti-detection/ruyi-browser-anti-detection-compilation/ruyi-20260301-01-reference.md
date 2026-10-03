---
schema_version: 2
id: ruyi-20260301-canvas-fingerprinter-reference
document_type: reference
original_date: '2026-03-01'
archived_date: '2026-07-13'
scope:
  targets: [canvas-fingerprinter]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260301-01.md#4-反canvas随机化检测
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留测试画布锚点、两次渲染检查、会话内持久噪声、随机化被检出本身成信号、每站唯一画布，以及 URL 拦截失效的转述。不抄测试画布文本或输出。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留两台硬件交叉验证和三条过滤。没有驳回条件，不能当成可执行流程。
relations:
  - type: derived_from
    target: ./ruyi-20260301-01.md#4-反canvas随机化检测
tags: [canvas, fingerprinter, source-report]
---

# 用测试画布反向识别 Canvas 指纹服务商

这张卡只回答：来源如何只靠 Canvas API 输出归因服务商，以及非持久随机噪声为什么过不了两次渲染检查。它不提供画布样本、哈希或拦截规则。

<a id="risk-control"></a>
## 识别边界

来源把同一服务商的测试画布写成跨站、跨时间都不能改的锚点。识别不走解混淆。约 45% 的指纹站点用两次渲染是否一致来发现噪声；会话内对相同调用序列返回相同加噪结果才能通过。Imperva 被写成每站一块不同画布，因此不能跨站比对。URL 拦截在来源的对照里只挡住约 5%。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源写「测试画布是指纹系统的"锚点"，改不了。」 | s1，ruyi-20260301-01.md:184 | source-report | 来源转述的跨时间比对约束 | 未核对任何服务商的当前画布 |
| C2 | 来源写「不需要分析混淆后的JavaScript代码  ，不需要逆向工程指纹脚本，只需要  记录Canvas API」 | s1，ruyi-20260301-01.md:54 | source-report | 来源的归因入口 | 没有输出库或哈希 |
| C3 | 来源写「45%的做Canvas指纹的网站会执行"一致性检查"：渲染同一个测试画布两次，比较结果是否一致。」 | s1，ruyi-20260301-01.md:167 | source-report | 来源报告的首页爬取 | 不是本次测量 |
| C4 | 来源写「在同一个会话内，对相同的Canvas API调用序列返回相同的（但经过噪声处理的）结果。」 | s1，ruyi-20260301-01.md:208 | source-report | 来源点名能通过检查的噪声 | 无噪声分布或浏览器版本 |
| C5 | 来源写「被检测到"使用了Canvas随机化"本身就是一个指纹信号。」 | s1，ruyi-20260301-01.md:174 | source-report | 来源对非持久随机化的额外信号 | 无熵或占比 |
| C6 | 来源写「它为每个客户网站生成不同的测试画布。这意味着Imperva从架构上就不具备跨站追踪的能力」 | s1，ruyi-20260301-01.md:130 | source-report | 来源点名的 Imperva | 不推广到其他产品 |
| C11 | 来源写「广告拦截器只挡住了5%的Canvas指纹活动。49%的指纹脚本以第一方身份加载」 | s1，ruyi-20260301-01.md:206 | source-report | 来源对 URL 拦截的对照结论 | 不是本次复测 |

<a id="decision-flow"></a>
## 过滤与交叉验证

归因前先丢掉三类画布，再用两台不同硬件确认“哪些站相同”来自脚本而不是 GPU。这三步没有失败出口。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | 来源写「它证明了测试画布的"相同性"来自脚本逻辑，而不是硬件巧合。」 | s1，ruyi-20260301-01.md:72 | source-report | 来源的两机交叉验证 | 只点名两台机器 |
| C8 | 来源写「排除有损压缩格式（JPEG、WebP）——压缩会丢失像素级差异，不适合做指纹」 | s1，ruyi-20260301-01.md:78 | source-report | 第一条过滤 | 无误删比例 |
| C9 | 来源写「排除  小于16×16像素的画布——复杂度不够，无法有效区分设备」 | s1，ruyi-20260301-01.md:79 | source-report | 第二条过滤 | 只有这一处阈值 |
| C10 | 来源写「排除包含动画方法（save/restore等）的脚本生成的画布——这些通常是正常的图形应用」 | s1，ruyi-20260301-01.md:80 | source-report | 第三条过滤 | 方法只举了 save/restore |

## 验证与限制

正文的十条建议没有验收条件和失败出口，所以不升为流程。`../../web-reverse/browser-env-objects/canvas-webgl.md` 的 risk-control 只覆盖 Canvas 宿主对象语义，`fingerprint-overview.md` 只覆盖状态组，都不包含上述归因和两次渲染边界。论文题名和画布样本不在正文里。只爬首页、爬虫可能被反 Bot 改写、相同画布归因是上界，都保持为来源自己的限制。
