---
schema_version: 2
id: ruyi-20260305-tor-session-wf-reference
document_type: reference
original_date: '2026-03-05'
archived_date: '2026-07-13'
scope:
  targets: [tor-session-website-fingerprinting]
  client: tor
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260305-01.md#三步攻击流程
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留来源对分组前提、p_switch 和 top-5 驱动关系的转述。不收录如何插入无关页面。百分比不是本次测量。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留三步的判定顺序和间隙配置。没有特征、模型或一次会话的输入输出，不能当成可跑流程。
relations:
  - type: derived_from
    target: ./ruyi-20260305-01.md#三步攻击流程
tags: [website-fingerprinting, tor, source-report]
---

# 会话级网站指纹改写单页 top-1 的边界

这张卡只回答一个检索问题：来源转述的论文在什么前提下用 top-5 里的组连续性改写单页 WF 的 top-1，以及什么时候这个改写会失效。不提供流量采集或攻击实现。

<a id="risk-control"></a>
## 会话信号

来源把可利用的信号定义成连续访问更可能属于同一组。p_switch 是离开当前组的概率，攻击者不必知道具体值，但分组必须大致正确。好分组不是内容相似，而是用户可能连着访问、同时单页 WF 还能分开。top-5 够高时改写有增益；top-1 已经很高时可能改错。p_switch 接近 1 时退回传统 WF。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 连续访问的网页更可能属于同一个"组"。 | s1，ruyi-20260305-01.md:109 | source-report | 来源的用户行为假设 | 分组不是真实话题 |
| C2 | 用户从当前组切换到另一个组的概率 | s1，ruyi-20260305-01.md:113 | source-report | 来源命名的 p_switch | 没有真实浏览日志 |
| C3 | 攻击者不需要知道p_switch的具体值 | s1，ruyi-20260305-01.md:120 | source-report | 来源的攻击者知识假设 | 仍假设 p_switch 不太大 |
| C4 | 好的分组不是把"内容相似"的网页放在一起，而是把"用户可能连续访问、但WF能区分"的网页放在一起。 | s1，ruyi-20260305-01.md:207 | source-report | 来源对四种分组读图后的判断 | 未复算 |
| C5 | 不管top-1准确率有多低，只要top-5准确率足够高，攻击就能显著提高准确率。 | s1，ruyi-20260305-01.md:255 | source-report | 来源的模拟器发现 | 不是本次测量 |
| C6 | 如果WF的top-1已经很准了，上下文分析可能把一些原本正确的top-1猜测"纠正"成错误的 | s1，ruyi-20260305-01.md:265 | source-report | 来源 Figure 8 的高 top-1 区域 | 没有原始矩阵 |
| C7 | 如果分组不准确，攻击效果会大打折扣。 | s1，ruyi-20260305-01.md:51 | source-report | 来源承认的核心前提 | 准确行为模型被写成未来工作 |
| C8 | 没有开放世界（open-world）的实验；没有考虑任何防御措施 | s1，ruyi-20260305-01.md:52 | source-report | 来源的评估范围 | 防御类型在下一行 |
| C9 | 当p_switch接近1.0（用户频繁切换话题）时，攻击效果退化到和传统WF一样。 | s1，ruyi-20260305-01.md:280 | source-report | 来源报告的退化条件 | 不收录插入无关页面的做法 |
| C10 | 正确答案在前5个猜测中，但不是第1个。这19个百分点就是论文要"捡回来"的空间。 | s1，ruyi-20260305-01.md:86 | source-report | 来源摘录的 TF top-1 与 top-5 差距 | 58% 与 77% 不是本次测量 |

<a id="decision-flow"></a>
## 三步改写

第一步仍是现有 WF 对每次访问给出网页概率分布。第二步在整个会话中找 top-5 里出现最多且最连续的组。第三步在该组里取概率最高的网页，因此结果可以不是原来的 top-1。正确组缺席时允许配置连续间隙。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C11 | 用现有WF攻击（如TF）输出一个概率分布——每个候选网页被选中的概率。 | s1，ruyi-20260305-01.md:128 | source-report | 来源的第一步 | 没有特征或模型 |
| C12 | 出现在top-5中次数最多且最连续的组 | s1，ruyi-20260305-01.md:134 | source-report | 来源的第二步 | 没有可复算的 top-5 |
| C13 | 最终选择的网页不一定是WF攻击的top-1猜测。 | s1，ruyi-20260305-01.md:155 | source-report | 来源的第三步 | 没有完整会话样例 |
| C14 | 论文允许配置最多N个连续间隙（实验中测试了0、1、2、3），发现允许1-2个间隙可以略微提高准确率。 | s1，ruyi-20260305-01.md:160 | source-report | 来源的可选间隙 | 没有分 N 的准确率表 |

## 验证与限制

unknown 上已有的 decision-flow 是 Frida、加固和补环境索引。`browser-fingerprint` 只覆盖宿主对象。两者都不是这个目标，所以不并入。数据集收集和第五节建议没有验收与失败出口，不升为流程。
