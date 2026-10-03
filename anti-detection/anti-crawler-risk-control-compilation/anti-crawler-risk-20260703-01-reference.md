---
schema_version: 2
id: anti-crawler-risk-20260703-behavior-model-reference
document_type: reference
original_date: '2026-07-03'
archived_date: '2026-10-02'
scope:
  targets:
    - behavior-model
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./anti-crawler-risk-20260703-01.md#一人类行为的核心特征"
    basis: source-report
  - id: s2
    ref: "./anti-crawler-risk-20260703-01.md#51-人类操作的时间分布"
    basis: source-report
  - id: s3
    ref: "./anti-crawler-risk-20260703-01.md#31-人类打字特征"
    basis: source-report
  - id: s4
    ref: "./anti-crawler-risk-20260703-01.md#八风控行为检测的常见陷阱与对策"
    basis: source-report
  - id: s5
    ref: "./anti-crawler-risk-20260703-01.md#九注意事项"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1, s4, s5]
    basis: source-report
    limits: 维度和陷阱表是来源对行为模型的描述。Datadome、Akamai、Cloudflare 只是举例，没有这些产品的当前检测规则。
  - name: parameters
    anchor: parameters
    sources: [s2, s3, s4]
    basis: source-report
    limits: 时间区间和点击偏移是作者给出的范围，不是测量分布。代码里的随机参数未逐项收录，也未运行。
relations:
  - type: derived_from
    target: "./anti-crawler-risk-20260703-01.md#一人类行为的核心特征"
tags:
  - behavior-model
  - source-report
---

# 行为模型关注的维度和来源给出的时间范围

这张卡只回答：来源认为网页行为模型给哪些动作打分，以及它写下的时间范围是什么。不收录鼠标轨迹、击键或滚动的实现。DOM 事件对象模型仍看事件与输入设备卡；DataDome 的 interstitial 链路仍看产品卡。

来源没有可公开定位的原文 URL。作者把目标写成让自动化在行为上看起来像真人，本卡只保留检测维度和已写出的范围。

<a id="risk-control"></a>
## 行为打分维度

来源称指纹对齐之后，行为模式仍会被打分，并举例 Datadome、Akamai Bot Manager、Cloudflare Bot Management。

> 你鼠标怎么动、键盘怎么敲、页面怎么滚、两次操作间隔多少、甚至屏幕有没有晃动，都在实时打分。  **

> 风控建模通常关注这几个维度：

维度表把人类特征和自动化常见错误对照为：

| 维度 | 来源写的人类特征 | 来源写的自动化常见错误 |
|---|---|---|
| 鼠标移动 | 曲线、加速度、微抖动、非直线 | 直线、匀速、完美贝塞尔 |
| 点击 | 有停留、有偏移、双击少 | 瞬间点击、坐标精确 |
| 滚动 | 变速、随机停顿、偶尔反向 | 匀速、一次滚到底 |
| 键盘 | 间隔不等、有错再改 | 固定间隔、无错误 |
| 页面停留 | 阅读时间分布广、有回头 | 极短或完全一致 |
| 视口 | 会改窗口、会切焦点 | 固定不变 |
| 并发 | 单线程、串行 | 并行大量请求 |

作者把原则写成下面这句，同时又写不要模拟得太完美。这两句同时成立，来源没有给出熵的度量。

> ** 核心原则：增加熵，减少规律性。  **

>   1. ** 不要过度模拟  ** ：太完美的"人类"反而可疑。保留一些不规则性，但不要刻意制造太多异常。

陷阱表重复的检测点是：移动快到像瞬移、点击总在元素中心、没有轨迹就 `element.click()`、`window.scrollTo` 一次到底、`send_keys` 等间隔、打开就填表、没有长停顿、窗口始终聚焦。来源要求行为层和 TLS/HTTP2 指纹、浏览器指纹一起看，并写明单一维度过不了强风控。

>   2. ** 结合指纹伪装  ** ：行为模拟要和 TLS/HTTP2 指纹、浏览器指纹一起工作，单一维度突破不了强风控。

<a id="parameters"></a>
## 来源写下的时间范围

这些数字都是作者给的区间，不是样本统计。原句是：

>   * ** 击键间隔不均匀  ** ：字母间 100-300ms，空格和标点更长

>   * ** 两次操作间隔  ** ：通常在 0.5~5 秒之间，呈长尾分布

>   * ** 页面加载后  ** ：有 1~3 秒的"阅读"时间

>   * ** 表单填写  ** ：每个字段之间有 0.5~2 秒停顿

> ** 点击坐标完全精确  ** |  总是元素中心  |  随机偏移 ±3~10px

| 场景 | 来源区间 |
|---|---|
| 字母击键 | 100–300 ms，空格和标点更长 |
| 两次操作间隔 | 通常 0.5–5 秒，长尾 |
| 页面加载后的阅读 | 1–3 秒 |
| 表单字段之间 | 0.5–2 秒 |
| 提交前确认 | 0.3–1 秒 |
| 点击偏离中心 | 来源在陷阱表写随机偏移 ±3–10 px |

延迟函数被描述成截断正态分布，示例默认均值 1.5 秒、标准差 0.8、下限 0.2、上限 5.0。不同动作还有另一组均值，本卡不把代码默认值提升成测量结果。

## 验证与限制

- 鼠标、键盘、滚动和轨迹录放的代码围栏是粘连示例，本卡不重建。
- 录放一节针对来源所谓高安全场景，只有采样和回放骨架，没有验收样本，因此没有抽成流程。
- `bot.sannysoft.com` 和 `fingerprintjs.com/demo` 只被点名用来看自动化是否被检测，没有通过条件和反例。
- 未运行桌面或浏览器自动化，也不能把这些区间写成某个产品的当前阈值。
