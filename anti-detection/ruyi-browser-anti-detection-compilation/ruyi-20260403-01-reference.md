---
schema_version: 2
id: ruyi-20260403-captcha-user-study-reference
document_type: reference
original_date: '2026-04-03'
archived_date: '2026-10-02'
scope:
  targets: [captcha-user-study]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260403-01.md#核心发现
    basis: source-report
  - id: s2
    ref: ./ruyi-20260403-01.md#做反爬风控的
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留放弃定义、认知负荷、放弃率量级，以及滑块安全性被归到行为分析。不收攻击步骤，也不把未测的 v3 或 Turnstile 算进结果。
  - name: decision-flow
    anchor: decision-flow
    sources: [s2]
    basis: source-report
    limits: 只保留来源的设计顺序。没有评分阈值、切换条件和失败出口，不能当成流程。
relations:
  - type: derived_from
    target: ./ruyi-20260403-01.md#核心发现
tags: [captcha-user-study, source-report]
---

# 九类真实验证码的可用性边界

这篇卡检索的是：该文转述的用户研究里，放弃怎么定义、烦躁跟什么有关、显式挑战应按什么顺序取舍。不提供解题或轨迹做法。

<a id="risk-control"></a>
## 研究里能用的边界

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 放弃不是解错：如果用户填完注册表单后看到验证码就直接关了页面（不做验证码），算作一次"放弃"。 | s1，源文件第 89 行 | source-report | Study 2 的自然任务 | 不是全站转化统计 |
| C2 | 烦躁口径：用户对验证码的"烦不烦"感知更多取决于"认知负荷"而非"绝对时间"。 | s1，源文件第 149 行 | source-report | 文中九类验证码的问卷转述 | 未复核原始量表 |
| C3 | 量级：总体放弃率约5-10%——也就是每10-20个用户中就有1个看到验证码后直接放弃了注册。 | s1，源文件第 167 行 | source-report | Study 2 | 不能外推到任意站点 |
| C4 | 滑块边界：Geetest的安全性主要不靠"人能做机器不能做"的认知差异，而是靠行为分析（滑动轨迹的自然度） | s1，源文件第 196 行 | source-report | 文中的极验滑块转述 | 同一行的定位和滑动做法不在本卡 |
| C5 | 测量空洞：但没有测reCAPTCHA v3（纯行为评分）和Cloudflare | s1，源文件第 268 行 | source-report | 这篇研究的负面范围 | 下一行才点名 Turnstile；效果不能用解题表代替 |

<a id="decision-flow"></a>
## 设计顺序

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 先看负荷：不要只优化解题时间，更要优化认知负荷。 | s1，源文件第 157 行 | source-report | 来源给设计者的建议 | 没有上线验收 |
| C7 | 轮数上限：最多2轮，超过2轮直接换一种验证方式（比如短信验证码）。 | s1，源文件第 214 行 | source-report | 多轮显式挑战 | 没有切换失败出口 |
| C8 | 显式挑战靠后：只有当评分很低时才回退到显式挑战。 | s2，源文件第 304 行 | source-report | 来源推荐的隐形优先 | v3 与 Turnstile 不在实测内，没有阈值 |

## 验证与限制

`google-recaptcha` 已有卡是 v3 的请求链、参数和风控面，不包含这九类对照。`hcaptcha` 近邻没有 risk-control 模块。实验全在桌面端。Bot 成功率按来源自己的说法是未使用视觉大模型时的转述。做爬虫一节不进入本卡。效果数字保持 source-report。
