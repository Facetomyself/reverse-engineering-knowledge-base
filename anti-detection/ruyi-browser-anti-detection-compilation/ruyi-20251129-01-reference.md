---
schema_version: 2
id: ruyi-advanced-web-bot-log-mouse
document_type: reference
original_date: '2025-11-29'
archived_date: '2026-10-02'
scope:
  targets: [advanced-web-bot]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ruyi-20251129-01.md#1web-logs把用户的浏览习惯量化"
    basis: source-report
  - id: s2
    ref: "./ruyi-20251129-01.md#2mouse-behaviour把鼠标轨迹当作生物特征"
    basis: source-report
  - id: s3
    ref: "./ruyi-20251129-01.md#3logs--mouse-的决策级融合"
    basis: source-report
  - id: s4
    ref: "./ruyi-20251129-01.md#3组合使用logs--mouse"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2]
    basis: source-report
    limits: 只保留笔记点名的日志特征和鼠标特征。没有公式、窗口、CNN 结构或阈值。
  - name: risk-control
    anchor: risk-control
    sources: [s4, s1]
    basis: source-report
    limits: 识别率和“指纹贡献最低”是来源对论文的转述。不覆盖浏览器对象指纹语义。
  - name: decision-flow
    anchor: decision-flow
    sources: [s3]
    basis: source-report
    limits: 只有决策级融合的三段输出。没有权重、冲突规则，也没有无交互时的失败出口。
relations:
  - type: derived_from
    target: "./ruyi-20251129-01.md#1web-logs把用户的浏览习惯量化"
  - type: derived_from
    target: "./ruyi-20251129-01.md#2mouse-behaviour把鼠标轨迹当作生物特征"
  - type: derived_from
    target: "./ruyi-20251129-01.md#3logs--mouse-的决策级融合"
tags: [advanced-web-bot, mouse-behaviour]
---

# 高级 Web Bot 的日志与鼠标决策级融合

这张卡检索笔记里的检测信号：哪些 Web 日志特征和鼠标特征被点名，以及 log 模型与 mouse 模型怎样在决策级合并。浏览器指纹对象语义仍以 `../../web-reverse/browser-env-objects/fingerprint-overview.md` 为准，不把行为融合并进那张卡。

来源是如意私塾对一篇 ACM 论文的转述。依据只到 source-report。文中的识别率不是本次结果。

<a id="parameters"></a>
## 参数

日志侧是会话和请求习惯，不是浏览器对象字段。鼠标侧把 (x, y, t) 转成矩阵交给 CNN，笔记只点名微抖、加速度惯性和曲线是否过滑。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 请求间隔时间的分布（inter-arrival time） | s1 ./ruyi-20251129-01.md:89 | source-report | 见 scope | 只有特征名，没有公式、窗口或阈值。 |
| C2 | 会话持续时间 | s1 ./ruyi-20251129-01.md:91 | source-report | 见 scope | 只有特征名，没有公式、窗口或阈值。 |
| C3 | 页面深度（path traversal） | s1 ./ruyi-20251129-01.md:93 | source-report | 见 scope | 只有特征名，没有公式、窗口或阈值。 |
| C4 | 静态资源与动态资源的比例 | s1 ./ruyi-20251129-01.md:95 | source-report | 见 scope | 只有特征名，没有公式、窗口或阈值。 |
| C5 | 错误码（404/500）出现频率 | s1 ./ruyi-20251129-01.md:97 | source-report | 见 scope | 只有特征名，没有公式、窗口或阈值。 |
| C6 | 鼠标轨迹 (x, y, t)  转换成矩阵，然后交给卷积神经网络（CNN）识别。 | s1 ./ruyi-20251129-01.md:125 | source-report | 见 scope | 没有网络结构、输入尺寸或训练数据。 |
| C7 | 鼠标是否含有微抖（hand tremor） | s1 ./ruyi-20251129-01.md:129 | source-report | 见 scope | 只有特征名，没有公式、窗口或阈值。 |
| C8 | 加速度变化是否有“人类惯性” | s1 ./ruyi-20251129-01.md:131 | source-report | 见 scope | 只有特征名，没有公式、窗口或阈值。 |
| C9 | 曲线是否自然（Bot 曲线过于平滑） | s1 ./ruyi-20251129-01.md:133 | source-report | 见 scope | 只有特征名，没有公式、窗口或阈值。 |

<a id="risk-control"></a>
## 风控含义

笔记的检测目标是像不像人，而不是浏览器有没有被改。单一日志、行为或指纹被写成不够；组合被写成更强，且指纹贡献最低。百分比只作为来源转述保留。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C10 | 单一维度（指纹、行为、日志）已经不足以识别高级 Bot | s1 ./ruyi-20251129-01.md:59 | source-report | 见 scope | 这是笔记转述的论文假设，不是实测结论。 |
| C11 | 单一信号都不够，组合后才能碾压Bot。 | s1 ./ruyi-20251129-01.md:77 | source-report | 见 scope | 识别率是来源对论文的转述，本次未复现，不能当验收。 |
| C12 | 不是检测浏览器有没有被改，而是检测用户是否  像“人” | s1 ./ruyi-20251129-01.md:81 | source-report | 见 scope | 没有判定阈值。 |
| C13 | 识别率大约在 70%–90% | s1 ./ruyi-20251129-01.md:169 | source-report | 见 scope | 识别率是来源对论文的转述，本次未复现，不能当验收。 |
| C14 | 某些数据集接近 99% 准确率 | s1 ./ruyi-20251129-01.md:174 | source-report | 见 scope | 识别率是来源对论文的转述，本次未复现，不能当验收。 |
| C15 | 准确率逼近 97%–100%，远超单独模块。 | s1 ./ruyi-20251129-01.md:179 | source-report | 见 scope | 识别率是来源对论文的转述，本次未复现，不能当验收。 |
| C16 | 多模态组合是识别高级 Bot 的最有效实践方法 | s1 ./ruyi-20251129-01.md:183 | source-report | 见 scope | 识别率是来源对论文的转述，本次未复现，不能当验收。 |
| C17 | 指纹（fingerprinting vectors）在本研究中  贡献度最低 | s1 ./ruyi-20251129-01.md:187 | source-report | 见 scope | 没有贡献度数值或消融表。 |
| C18 | 浏览器指纹不再是风控的核心武器。行为才是 | s1 ./ruyi-20251129-01.md:190 | source-report | 见 scope | 这是笔记结论，不是跨站点测量。 |

<a id="decision-flow"></a>
## 决策级融合

笔记不用特征拼接。log 模型与 mouse 模型各自给出是否为 Bot，再交给融合模块。鼠标这一支依赖用户交互，笔记没有写没有交互时改走哪一支。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C19 | 决策级融合  ** （decision-level fusion），而不是简单拼特征。 | s1 ./ruyi-20251129-01.md:150 | source-report | 见 scope | 没有融合权重或投票规则。 |
| C20 | log 模型输出是否为 Bot | s1 ./ruyi-20251129-01.md:154 | source-report | 见 scope | 没有模型输出字段。 |
| C21 | mouse 模型再输出是否为 Bot | s1 ./ruyi-20251129-01.md:156 | source-report | 见 scope | 没有模型输出字段。 |
| C22 | 最终再由一个融合模块综合判断 | s1 ./ruyi-20251129-01.md:158 | source-report | 见 scope | 没有冲突时的优先规则。 |
| C23 | 必须有用户交互。 | s1 ./ruyi-20251129-01.md:175 | source-report | 见 scope | 没有交互缺失时的替代分支。 |

## 验证与限制

缺特征公式、CNN 结构、融合权重和失败出口，不能写成流程。70%–90%、接近 99%、97%–100% 都留在来源转述，不升格。
