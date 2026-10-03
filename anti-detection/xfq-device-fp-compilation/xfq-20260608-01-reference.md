---
schema_version: 2
id: xfq-20260608-behavior-timing-reference
document_type: reference
original_date: '2026-06-08'
archived_date: '2026-10-02'
scope:
  targets: [app-behavior-timing]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260608-01.md#真实人类的高随机性"
    basis: source-report
  - id: s2
    ref: "./xfq-20260608-01.md#具体表现"
    basis: source-report
  - id: s3
    ref: "./xfq-20260608-01.md#补量难点"
    basis: source-report
  - id: s4
    ref: "./xfq-20260608-01.md#伪随机数"
    basis: source-report
  - id: s5
    ref: "./xfq-20260608-01.md#攻击方视角状态恢复攻击"
    basis: source-report
  - id: s6
    ref: "./xfq-20260608-01.md#种子可预测性时间戳种子的风险"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s4]
    basis: source-report
    limits: 只保留来源列出的事件参数、三套分布数字，以及 random、secrets、numpy 默认生成器的名字。没有数据集，不复述 MT19937 的 twist。
  - name: risk-control
    anchor: risk-control
    sources: [s2, s3, s4, s5, s6]
    basis: source-report
    limits: 均匀分布对照、联合分布、624 个输出和时间戳窗口都是来源陈述。未运行预测或枚举，不收录示例 token 和断开的代码。
  - name: decision-flow
    anchor: decision-flow
    sources: [s2]
    basis: source-report
    limits: c 的分档来自粘连的第 79 行和随后三行一组的文本。不是已拟合阈值。
relations:
  - type: derived_from
    target: "./xfq-20260608-01.md#具体表现"
tags: [app-behavior-timing, source-report]
---

# App 行为时间分布与弱伪随机的来源边界

这张卡只回答：这篇讲义把哪些事件和哪三套时间分布写成风控对照，以及它如何把「看起来均匀」和「可复现的弱伪随机」分开。不提供采样器、预测器或枚举脚本。MT19937 的状态转换实现在 `../../signature-algorithms/xfq-crypto-notes-compilation/xfq-undated-01.md`，这里不复述 twist。

<a id="parameters"></a>
## 事件与分布参数

来源把事件拆成逐行，而不是一张画好的表。retention 写成天级，其余事件的参数行都紧挨着毫秒级那一行。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C2 | launch 的参数是启动方式，含冷启动和热启动。 | s1 第 45 行：启动方式(冷启动/热启动) | source-report | 来源列出的 launch | 没有采集 API |
| C3 | session_start 的参数是会话 ID 和前序会话间隔。 | s1 第 48 行：会话ID、前序会话间隔 | source-report | 来源列出的 session_start | 事件名在上一非空参数行之前 |
| C4 | session_end 的参数是会话时长和页面浏览数。 | s1 第 51 行：会话时长、页面浏览数 | source-report | 来源列出的 session_end | 没有时长单位以外的字段 |
| C5 | purchase 的参数是商品 ID、金额和货币类型。 | s1 第 54 行：商品ID、金额、货币类型 | source-report | 来源列出的 purchase | 没有金额单位 |
| C7 | retention 的参数是 D1/D7/D30，时间精度单独写成天级。 | s1 第 56–56 行：天级 / D1/D7/D30留存标记 | source-report | 来源列出的 retention | 没有留存判定口径 |
| C8 | re-engagement 的参数是推送 ID 和唤回渠道。 | s1 第 60 行：推送ID、唤回渠道 | source-report | 来源列出的 re-engagement | 事件名带连字符 |
| C9 | deeplink 的参数是链接参数和来源 App。 | s1 第 63 行：链接参数、来源App | source-report | 来源列出的 deeplink | 没有链接模板 |
| C10 | 会话时长被写成对数正态。 | s2 第 68 行：符合对数正态分布(Log-Normal Distribution) | source-report | 来源的 session 时长 | 没有 μ、σ |
| C11 | 中位数写成 45-90 秒，均值写成 120-180 秒。 | s2 第 69–69 行：中位数: 45-90秒 / 均值: 120-180秒(被长尾拉高) | source-report | 来源给出的两个区间 | 没有样本 |
| C13 | 极短小于 10 秒，极长大于 30 分钟。 | s2 第 71 行：存在极短session(<10秒,误触)和极长session(>30分钟,深度使用) | source-report | 来源对尾部的描述 | 误触和深度使用是解释 |
| C14 | 打开间隔被写成威布尔，c 是形状参数。 | s2 第 76 行：符合威布尔分布(Weibull Distribution) | source-report | 两次打开之间的间隔 | 同节还有错字，没有估计方法 |
| C15 | 日活被写成泊松，λ 为 2-15 次/天，工作日和周末有差异。 | s2 第 87–87 行：符合泊松分布(Poisson Distribution) / λ参数因人而异(2-15次/天) / 工作日与周末有显著差异 | source-report | 来源的每日活跃次数 | 没有差异量 |
| C18 | random 被写成 MT19937，周期 2^19937-1。 | s4 第 103 行：基于 Mersenne Twister (MT19937) 算法,周期长达 2^19937-1,是最常用的选择。 | source-report | 来源对 Python random 的描述 | 不复述 twist |
| C19 | secrets 被写成系统随机源。 | s4 第 112 行：Python 3.6+ 引入,底层使用系统的 /dev/urandom 或 CryptGenRandom: | source-report | 来源对 secrets 的描述 | 围栏断开，没有可运行调用 |
| C20 | numpy 新 API 的默认生成器被写成 PCG64，并称优于 MT19937。 | s4 第 142 行：PCG64 — 默认,质量优于 MT19937 | source-report | 来源点名的 BitGenerator | 没有测试向量 |

<a id="risk-control"></a>
## 来源报告的识别边界

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C21 | 用 uniform(30, 300) 生成会话时长，被写成和对数正态的尾部差异极大。 | s2 第 72 行：风控含义:机器流量假如用 uniform(30, 300) 直接生成 session 时长,——均匀分布和对数正态分布的尾部形状差异极大。 | source-report | 来源举的这一种均匀采样 | 不是本轮直方图 |
| C25 | 最难仿造的是会话时长、打开间隔和活跃次数的联合分布。 | s3 第 97 行：最难仿造的是跨维度联合分布:session 时长、打开间隔、活跃次数三者在真实用户中存在相关性 | source-report | 来源点名的三个量 | 还要求真实数据拟合，并且参数再加噪声 |
| C26 | 「超过基准即异常」只是作者对泊松的简单说法。 | s2 第 90 行：泊松分布简单来说:基于某段时间的基准,如果今天超过基准,即视为异常 | source-report | 这句原文 | 没有检验量 |
| C28 | 弱伪随机数的三列被堆成 Yes、No、No，对应随机性、不可预测性、不可重现性。 | s4 第 155–158 行：弱伪随机数 / Yes / No / No | source-report | 紧挨表头的弱伪随机数 | 不把堆叠行重排成新表 |
| C32 | 来源的收束是伪随机不等于随机分布，只靠伪随机绕不过风控。 | s4 第 217–217 行：我们只需要了解伪随机!=随机分布 / 所以如果只是简单的想通过伪随机数来绕过风控的检测,是不可能的 | source-report | 这节的结论句 | 没有检测器 |
| C34 | 来源写 624 个 32-bit 输出可以还原 MT19937 状态并预测后续输出。 | s5 第 223 行：MT19937 的内部状态由 624 个 32-bit 整数组成(共 19968 bits)。只要攻击者能连续观察到 624个输出值,就可以完全还原内部状态,从而预测后续所有输出。 | source-report | 来源对连续原始输出的陈述 | 未运行，不收录预测循环 |
| C37 | 时间戳种子的窗口被写成 HTTP Date 所能对上的大约 ±1 小时，搜索空间 3,600,000，并称小于 1 秒。 | s6 第 272–272 行：攻击者知道请求的大致时间(HTTP 响应头 Date 字段) / 毫秒级时间戳搜索空间约 3600 × 1000 = 3,600,000(±1小时) / 暴力枚举全部种子,在普通笔记本上 < 1秒 完成 | source-report | 来源假设种子是毫秒时间戳 | 计时是作者自述；示例 token 未收录 |

<a id="decision-flow"></a>
## 威布尔形状参数的来源分档

第 79 行先写 c 越大越像机器人，然后同一行粘上了相反方向，以及 `<1` 和约等于 1 两档。`1.0-2.5` 和 `>3` 才各占后续独立行。下面只引用能逐行对上的片段，不把粘连行补成一张完整矩阵。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C39 | c 越大，来源写成间隔越集中、越规律、越像机器人。 | s2 第 79 行：c 越大 → 间隔越集中 → 行为越规律 → 越像机器人c 越小 → 间隔越分散 → 行为越随机 → 越像真人C含义来源<1早期高频,后期稀疏新用户探索期≈1指数分布(无记忆性随机活跃用户 | source-report | 这一行的前半 | 行尾粘连了更小的 c |
| C40 | 1.0-2.5 的后续两行是正常磨损曲线和成熟用户。 | s2 第 80–82 行：1.0-2.5 / 正常磨损曲线 / 成熟用户 | source-report | 这三行的顺序 | 讲义没有列标题 |
| C41 | >3 的后续两行是高度规律、间隔集中，然后是机器人流量。 | s2 第 83–85 行：>3 / 高度规律,间隔集中 / 机器人流量 | source-report | 这三行的顺序 | 没有估计出的 c |

## 验证与限制

`android-app-device-fingerprint` 的 risk-control 只保留硬件、ROM 和 APK 的一致性，并且不复述分布数字，所以不把本篇补进那张卡。`MT19937 pseudorandom generator implementation` 的 parameters 是 624 项状态和 twist，本篇的 624 是输出个数陈述，不把 twist 抄过去。菠萝包的 parameters 是另一条 nonce 与 MD5 链。

第 95 行要求参数从真实数据拟合再加噪声，第 167 行说密码学随机数是前两种，但没有再定义「前两种」。代码围栏跨句断开。前提、可执行步骤、输出、验收和失败出口不能同时定位，不建流程。成功与计时保持 source-report。
