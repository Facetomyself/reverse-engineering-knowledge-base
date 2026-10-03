---
schema_version: 2
id: anti-detection-ruyi-thresholdfp-linking-reference
document_type: reference
original_date: '2026-02-28'
archived_date: '2026-07-13'
scope:
  targets: [thresholdfp]
  client: browser
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260228-01.md#一算法拆解
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只整理来源抄录的分数公式和两个举例分数。totalChanges 的计数口径不明。分数不是指纹原值。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只整理来源描述的关联、累积和修复分支。没有数据结构、验收或失败出口。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只整理来源报告的阈值、追踪时间、精确率和属性稳定性分层。数字不是本次测量。未测主动伪造，不补做法。
relations:
  - type: derived_from
    target: ./ruyi-20260228-01.md#一算法拆解
tags: [thresholdfp, fingerprint-linking, source-report]
---

# ThresholdFP：属性不稳定性分数、累积阈值与修复

这张卡只回答一个检索问题：来源把浏览器指纹前后关联说成哪一种不靠硬编码规则的分数和阈值，以及它报告了哪些来源级结果和未测边界。它不提供可编译实现，也不提供对抗步骤。

<a id="parameters"></a>
## 参数机制

来源把每个属性的分数定义成变化越少越高。公式输入是该属性的变化次数和全部变化次数。机构数据集上的 colorDepth 与 fonts 只是举例，不能当成别的人群的参数。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C3 | 来源给出的属性分数是 100 减去该属性变化占全部变化的百分比。来源写「attributeScore[attr] = 100 - (attributeChange[attr] / totalChanges × 100)」 | s1，ruyi-20260228-01.md:72 | source-report | 来源抄录的属性分数公式 | totalChanges 的计数口径不在正文；公式两侧有不换行空格 |
| C4 | 来源写机构数据集里 colorDepth 几乎不变，分数 99.89。来源写「colorDepth  ` （颜色深度）几乎从不变化，分数高达99.89」 | s1，ruyi-20260228-01.md:74 | source-report | 来源举的机构数据集分数 | 不是可复用的指纹原值，只是来源报告的分数 |
| C5 | 来源写字体列表经常变化，分数 62.07，颜色深度不同则差异分约 99。来源写「经常变化，分数只有62.07」 | s1，ruyi-20260228-01.md:75 | source-report | 来源举的机构数据集分数 | 只是来源报告的分数 |
<a id="decision-flow"></a>
## 关联分支

来源的关联规则是：新指纹相对某条活跃指纹的差异分数，加上该链已有累积分数，小于阈值才连成后继；多个候选取差异最小的 min 变体。过时指纹再次出现则断开并回退累积分数。Panopticlick 被写成更死的单属性或 85% 字符串规则。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源写 Panopticlick 只在一个属性不同且属于允许变化集合，或字符串相似度超过 85% 时关联。来源写「只有一个属性不同，并且这个属性属于"允许变化"的集合，或者字符串相似度超过85%」 | s1，ruyi-20260228-01.md:51 | source-report | 来源转述的 Panopticlick 规则 | 允许变化集合没有逐项列出 |
| C2 | 来源写差异总分不超过阈值就视为同一浏览器实例的演化。来源写「只要新旧指纹之间的差异总分不超过阈值」 | s1，ruyi-20260228-01.md:58 | source-report | 来源对 ThresholdFP 决策的定义 | 阈值选取过程不在这一句 |
| C6 | 来源写累积分数加差异分数小于阈值就关联为后继，多个候选时选差异最小的。来源写「小于阈值，就把新指纹关联为它的后继。如果有多个候选，选差异分数最小的那个。」 | s1，ruyi-20260228-01.md:79 | source-report | 来源对关联决策的描述 | 活跃指纹的存储结构不在正文 |
| C7 | 来源写差异分数沿演化链累加，用来打断每次只变一点但方向不同的链。来源写「每次演化的差异分数会累加。」 | s1，ruyi-20260228-01.md:81 | source-report | 来源对累积分数的设计说明 | 没有衰减或重置规则 |
| C8 | 来源写过时指纹重现后断开关联，并减去来自前驱的累积分数。来源写「断开A和B之间的关联，把B的累积分数中来自A的部分减掉」 | s1，ruyi-20260228-01.md:87 | source-report | 来源对修复机制的描述 | 没有触发条件和数据结构 |
| C9 | 来源写 min、earliest、max 差异不大，min 在两个数据集上略优。来源写「min变体在两个数据集上都略优」 | s1，ruyi-20260228-01.md:99 | source-report | 来源对三个变体的比较 | 没有逐次对照表 |
<a id="risk-control"></a>
## 风险控制信号

来源报告机构数据集阈值 40、平均追踪 55.7 天，志愿者数据集阈值 32、精确率 99.5%。高稳定属性一变更像另一台设备；fonts、canvas、webgl 等高熵属性分数更低。小幅 Canvas 噪声被写成不会过阈值。数据集、代码不公开，主动伪造没有测试。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C10 | 来源写机构数据集使用的阈值是 40。来源写「在机构数据集上（阈值=40）」 | s1，ruyi-20260228-01.md:115 | source-report | 来源报告的机构数据集设定 | 阈值搜索过程不在正文 |
| C11 | 来源写机构数据集上 ThresholdFP 平均追踪 55.7 天。来源写「ThresholdFP平均追踪时间：55.7天」 | s1，ruyi-20260228-01.md:117 | source-report | 来源报告的追踪时间 | 不是本次测量 |
| C12 | 来源写相对 FP-Stalker 上界提升 24.3%，相对无算法基线提升 191.6%。来源写「提升了24.3%，比基线提升了191.6%。」 | s1，ruyi-20260228-01.md:123 | source-report | 来源报告的相对提升 | 不是本次测量 |
| C13 | 来源写志愿者数据集使用的阈值是 32。来源写「在志愿者数据集上（阈值=32）」 | s1，ruyi-20260228-01.md:125 | source-report | 来源报告的志愿者数据集设定 | 两个阈值不能互换使用 |
| C14 | 来源写志愿者数据集上精确率 99.5%。来源写「ThresholdFP在志愿者数据集上达到99.5%」 | s1，ruyi-20260228-01.md:131 | source-report | 来源报告的精确率 | 估计精确率与实际精确率的差距在后文另说，不是本次测量 |
| C15 | 来源把分数高于 95 的显示类属性写成几乎不变，一变就更像另一台设备。来源写「这些属性几乎从不变化，一旦变化就意味着很可能是不同的设备。」 | s1，ruyi-20260228-01.md:143 | source-report | 来源归纳的高稳定性属性 | 属性名单是来源观察，没有熵表 |
| C16 | 来源把 fonts、plugins、canvas、audio、webgl 写成分数低于 70 的低稳定性属性。来源写「低稳定性属性（分数<70）：fonts、plugins、canvas、audio、webgl。」 | s1，ruyi-20260228-01.md:147 | source-report | 来源归纳的低稳定性属性 | 没有各属性的原始分数表 |
| C17 | 来源写高熵属性恰恰更不稳定，容差只是缓解这个张力。来源写「属性分数和Shannon熵之间存在"松散的反比关系"」 | s1，ruyi-20260228-01.md:150 | source-report | 来源对熵和稳定性的关系 | 没有相关系数 |
| C18 | 来源写 Canvas 小幅噪声会被容差吃掉，因为该属性分数本来就低。来源写「小幅变化不会让差异分数超过阈值。」 | s1，ruyi-20260228-01.md:171 | source-report | 来源对小幅噪声的边界 | 后文的大幅度改法没有属性清单、幅度、验收或失败出口，不记成做法 |
| C19 | 来源写两个数据集和代码都不公开。来源写「两个数据集都不公开，代码也不公开。」 | s1，ruyi-20260228-01.md:187 | source-report | 来源声明的可复现性 | 因此正文数字不能独立重算 |
| C20 | 来源写论文假设变化都是自然演化，没有测试主动伪造。来源写「没有考虑攻击者主动伪造指纹的场景。」 | s1，ruyi-20260228-01.md:191 | source-report | 来源声明的未测场景 | 不补伪造步骤；这句只标明证据缺口 |

## 验证与限制

来源的集成建议和“大幅度、低频率”评论都没有把前提、步骤、输出、验收、失败出口写全，所以不升为流程，也不补属性改写做法。`../../web-reverse/browser-env-objects/fingerprint-overview.md` 不包含这套分数和阈值。后文 archive `ruyi-20260330-01.md` 仍是目标 unknown 的归档，不是已发布卡；审到那篇时应补进目标 thresholdfp，而不是另建一张。
