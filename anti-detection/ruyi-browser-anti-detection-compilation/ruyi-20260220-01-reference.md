---
schema_version: 2
id: anti-detection-ndss2023-adversarial-fingerprint-reference
document_type: reference
original_date: '2026-02-20'
archived_date: '2026-07-13'
scope:
  targets: [adversarial-browser-fingerprint]
  client: browser
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260220-01.md#发现一恶意指纹和良性指纹差异巨大
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只整理来源对 NDSS 2023 论文的转述。没有特征字段路径、窗口、阈值或分类器。文中百分比不是本次测量。不收录自动化一侧的伪装清单。
relations:
  - type: derived_from
    target: ./ruyi-20260220-01.md#发现一恶意指纹和良性指纹差异巨大
tags: [browser-fingerprint, null-rate, credential-stuffing, source-report]
---

# 商业站点上对抗指纹与良性指纹为何几乎不重叠

这张卡只回答一个检索问题：来源把 NDSS 2023「Him of Many Faces」转述成哪些可分开的风险信号。它不提供探针、指纹库或判定代码。

<a id="risk-control"></a>
## 风险控制信号

来源把论文定位为 Johns Hopkins 与 F5 在 14 个商业网站、约 360 亿次 HTTP(s) 请求上比较对抗指纹和良性指纹。可复用的是来源点名的几类差距：JS 特征空值、唯一率、分布差异、时间演化、工具与策略、攻击类型，以及撞库的探测后绑定。数字都是来源转述。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源写论文题为「Him of Many Faces: Characterizing Billion-scale Adversarial and Benign Browser Fingerprints on Commercial Websites NDSS 2023」 | s1，ruyi-20260220-01.md:33 | source-report | 来源点名的论文 | 无 PDF 页码或公开链接 |
| C2 | 来源写「98.4%的指纹可以明确归类为"攻击者"或"正常用户"」 | s1，ruyi-20260220-01.md:105 | source-report | 来源转述的唯一指纹重叠 | 不是本次测量；正文另写纯良性 90.3%、纯恶意 8.1%、重叠 1.6% |
| C3 | 来源写「GPU渲染器的恶意空值率86.2% vs 良性1.4%，devicePixelRatio恶意82.4% vs 良性0.0%。脚本工具根本不执行JS，所以这些字段全是空的。」 | s1，ruyi-20260220-01.md:116 | source-report | 来源点名的空值信号 | 无字段路径或采样定义 |
| C4 | 来源写「屏幕分辨率的良性唯一率92.3% vs 恶意19.7%」，并写 devicePixelRatio「良性93.6% vs 恶意1.7%」 | s1，ruyi-20260220-01.md:118 | source-report | 来源点名的唯一率差距 | 不是本次测量 |
| C5 | 来源写「GPU渲染器和屏幕分辨率的KL散度都超过5.0，而良性内部的KL散度不到1.0。」 | s1，ruyi-20260220-01.md:120 | source-report | 来源点名的分布差距 | 无散度计算过程 |
| C6 | 来源写「良性用户的指纹会自然演化（浏览器升级、换设备），而攻击者的指纹要么不变（绑定账户），要么一次性使用后丢弃。」 | s1，ruyi-20260220-01.md:133 | source-report | 来源的时间维信号 | 无窗口或距离 |
| C7 | 来源写「脚本工具 80%+」，并写「贡献了60.3%的唯一指纹」 | s1，ruyi-20260220-01.md:148-149 | source-report | 来源的工具与策略占比 | 不是本次计数 |
| C8 | 来源写「93.4%用脚本工具，KL散度最高（4.1）」；礼品卡为「KL散度仅0.03（几乎和良性一样！），但唯一率96.3%」；撞库为「84.2%用脚本工具，但唯一率82.7%」 | s1，ruyi-20260220-01.md:168-171 | source-report | 来源按攻击类型分开的信号 | 无站点名单或规则参数 |
| C9 | 来源写「攻击者先用少量探测请求摸清防线，然后精确地在阈值以下发起大规模攻击。」 | s1，ruyi-20260220-01.md:181 | source-report | 来源转述的撞库两阶段 | 无失败次数阈值 |
| C10 | 来源写「Finance C的被盗账户平均被14.9个不同指纹登录过」 | s1，ruyi-20260220-01.md:192 | source-report | 来源点名的被盗账户指纹数 | 不是本次统计，无账户字段 |
| C11 | 来源写「只模仿了82个官方指纹中的6个」 | s1，ruyi-20260220-01.md:201 | source-report | 来源点名的官方 Bot 白名单差距 | 无指纹样本 |
| C12 | 来源写「几乎没人敢留空UA，会被直接拒绝」，并写 devicePixelRatio「大部分攻击者直接忽略这个字段」 | s1，ruyi-20260220-01.md:218 | source-report | 来源的分特征策略占比 | 无请求样本 |
| C13 | 来源写「Canvas和字体这种需要真实采集的特征几乎没人Mimic。」 | s1，ruyi-20260220-01.md:222 | source-report | 来源对 Mimic 稀少的解释 | 无指纹库规模 |
| C14 | 来源写「如果GPU渲染器为空且devicePixelRatio为空，标记为高风险」 | s1，ruyi-20260220-01.md:247 | source-report | 来源的空值规则设想 | 无误伤测量 |
| C15 | 来源写「如果一个指纹在你的用户群里完全没有近邻，它大概率不是真人。」 | s1，ruyi-20260220-01.md:254 | source-report | 来源的分布近邻设想 | 无相似度定义 |
| C16 | 来源写「Canvas和字体列表同时为空，而插件列表又是一个从未在真实Chrome中出现过的随机组合」 | s1，ruyi-20260220-01.md:270 | source-report | 来源的策略形态 | 无插件名单 |
| C17 | 来源写「同一指纹连续登录失败→该指纹被封→新指纹出现→重复上述模式」 | s1，ruyi-20260220-01.md:276 | source-report | 来源的撞库预警设想 | 无计数或封禁实现 |

## 验证与限制

正文没有前提、步骤、输出、验收和失败出口五段，所以不升为流程。第 279–302 行是对自动化一侧的转述，本卡不把它们写成步骤。`../../web-reverse/browser-env-objects/fingerprint-overview.md` 的 risk-control 只覆盖宿主对象状态组；`canvas-webgl.md` 只覆盖 Canvas/WebGL 对象语义。两者都没有上述生产流量上的空值率、唯一率、策略占比或撞库两阶段，因此不并入。
