---
schema_version: 2
id: anti-detection-ruyi-browser-attribute-demographic-leak-reference
document_type: reference
original_date: '2026-03-21'
archived_date: '2026-07-13'
scope:
  targets: [browser-attribute-demographic-leak]
  client: browser
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260321-01.md#发现二浏览器属性可以推断用户的人口特征
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只整理来源对 PoPETs 2025 论文的转述。不复制属性的众数值，不含模型、特征编码或投放做法。AUROC 与唯一率不是本次测量。
relations:
  - type: derived_from
    target: ./ruyi-20260321-01.md#发现二浏览器属性可以推断用户的人口特征
tags: [browser-fingerprint, demographic-leak, device-memory, source-report]
---

# 浏览器属性降熵之后仍可能按人群分层

这张卡只回答一个检索问题：来源把哪 13 类浏览器属性说成既能衡量追踪唯一性、又能推断人口统计特征，以及为什么只降低熵不够。它不提供属性原值、模型或采集脚本。

<a id="risk-control"></a>
## 风险控制信号

来源的数据集是知情同意下的美国成年人样本。分析只用 13 个属性，不用已经硬化或来源认为不稳定的其余项。风险分成两层：一层是不同人群的匿名集不一样；另一层是指纹即使不唯一，属性仍和性别、年龄、种族、收入有互信息。来源强调模型故意简单，报告的 AUROC 是下界，而且只覆盖美国、一个 2023 年 12 月的截面。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源写第三项风险是「仅凭浏览器属性就能推断出用户的人口统计学特征」 | s1，ruyi-20260321-01.md:41 | source-report | 来源对追踪之外的第二类风险 | 没有推断实现 |
| C2 | 来源写「但分析中只使用了其中13个（加上它们的组合哈希构成的总体"Fingerprint"）。为什么？因为其余属性要么已经被浏览器厂商做了隐私保护（比如Plugins现在返回的是硬编码列表），要么不够稳定，不适合做指纹分析。」 | s1，ruyi-20260321-01.md:102 | source-report | 来源的属性范围 | 13 个名字在表里，众数值不抄入本卡 |
| C3 | 来源写总指纹唯一用户占比「60.2%」 | s1，ruyi-20260321-01.md:121 | source-report | 来源样本上的唯一性 | 同一行还有熵 12.10 bits；不是本次测量，也不是全网基数。该行含表格分隔符，不把整行抄进结论 |
| C4 | 来源写「低收入用户的平均匿名集大小为3.5（意味着平均只有3.5个人和你的指纹一样），高收入用户的平均匿名集大小为6.8——几乎是低收入的两倍。」 | s1，ruyi-20260321-01.md:142 | source-report | 来源样本里的收入分层 | 不是本次测量；高收入与 65 岁以上代表性不足 |
| C5 | 来源写「设备内存和收入有直接的正相关  。Device Memory=2的用户中，低收入家庭占比超过60%。这个属性虽然被W3C的API设计特意做了精度限制（取最近的2的幂），但它依然能有效地把用户按收入分层。」 | s1，ruyi-20260321-01.md:152 | source-report | 来源对这个 API 分桶的反例 | 没有分桶阈值表 |
| C6 | 来源写 User Agent「服务器从HTTP请求头里就能直接读到，不需要执行任何JavaScript，浏览器完全无法检测和阻止。」 | s1，ruyi-20260321-01.md:186 | source-report | 来源定义的被动指纹 | 没有请求样例 |
| C7 | 来源写 Screen Resolution 和 WebGL「需要JavaScript主动采集（active fingerprinting），浏览器至少有机会干预。」 | s1，ruyi-20260321-01.md:187 | source-report | 来源定义的主动指纹 | 没有干预点 |
| C8 | 来源写「都比随机猜好。最高的是推断用户是否为亚裔（0.698），其次是推断是否为女性（0.679）和是否为黑人（0.677）。」 | s1，ruyi-20260321-01.md:232 | source-report | 来源的三层 MLP、13 属性、美国样本 | AUROC 是下界，不是部署效果 |
| C9 | 来源写「这些模型故意做得很简单，只用了13个属性。」 | s1，ruyi-20260321-01.md:234 | source-report | 来源声明的实验目的 | 不能当成优化后的上界 |
| C10 | 来源写「** Device Memory  ** 对Income的互信息特别高（相对其他属性而言）——设备内存直接反映购买力」 | s1，ruyi-20260321-01.md:247 | source-report | 来源的互信息对照 | 没有归一化互信息数值 |
| C11 | 来源写「** Languages  ** 对Hispanic的互信息特别高——Language列表里有没有"es-US"几乎就是Hispanic的标签」 | s1，ruyi-20260321-01.md:248 | source-report | 来源的互信息对照 | 语言标签是来源举例，不是采集到的指纹原值 |
| C12 | 来源写「一个属性可能在指纹唯一性上贡献很小（大家的Platform就那么几种，区分度低），但在人口推断上贡献很大。」 | s1，ruyi-20260321-01.md:251 | source-report | 来源对 Platform 一类低熵属性的判断 | 不把降熵当成人口风险已消除 |
| C13 | 来源写「浏览器指纹的区分度取决于你面对的用户群体。」 | s1，ruyi-20260321-01.md:320 | source-report | 来源对唯一率不可跨人群搬用的提醒 | 美国样本不能直接推广 |
| C14 | 来源写「这7个值恰好把用户按收入水平分了层——Device Memory=2的用户中60%以上是低收入家庭。降了熵，但造成了人口画像风险。」 | s1，ruyi-20260321-01.md:342 | source-report | 来源给浏览器 API 的设计反例 | 没有新的返回值方案 |

## 验证与限制

正文没有操作者前提、步骤、验收条件和失败出口，所以不升为流程。60.2%、匿名集和 AUROC 都是来源摘录。样本偏年轻，65 岁以上和高收入段不足；没有交叉人口维度，也没有同一人的时间变化。`../../web-reverse/browser-env-objects/fingerprint-overview.md` 的 risk-control 只写宿主对象状态组和类型一致性，不包含人口互信息或「降熵仍分层」，因此不并入。来源提到的各属性众数值属于指纹原值，本卡不抄。
