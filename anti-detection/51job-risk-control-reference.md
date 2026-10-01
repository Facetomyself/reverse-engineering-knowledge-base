---
schema_version: 2
id: site-51job-risk-control-reference
document_type: reference
scope:
  targets: [51job]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: architecture-report
    ref: ./51job-anti-detection-analysis.md#风控架构回顾
    basis: source-report
  - id: vector-report
    ref: ./51job-anti-detection-analysis.md#检测向量清单--对抗矩阵
    basis: source-report
  - id: residual-report
    ref: ./51job-anti-detection-analysis.md#未完全解决的残留风险
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [architecture-report, vector-report, residual-report]
    basis: source-report
    limits: 来源中的潜在检测面与历史观察，未重新采集站点运行时证据；不继承已解决、低风险或稳定绕过等结论，不代表当前部署。
relations:
  - type: derived_from
    target: ./51job-anti-detection-analysis.md#检测向量清单--对抗矩阵
tags: [51job, anti-debugging, browser-instrumentation, risk-control, evidence-boundary]
---

# 51job Web 风控参考卡：检测面与证据边界

用于快速回答“调试改动可能影响哪些检测面，还缺什么验证”，不是当前可用的绕过配方。来源稿署名日期为 2026-07-05；该日期不等于每条结论的实际观测时间。原站点版本、脚本 hash 和当前部署未在本次整理中确认，因此 scope 的版本与观测时间均为 `unknown`。

本卡保留 [来源分析](./51job-anti-detection-analysis.md)，只提炼有材料支撑的风控模块；没有整理出接口、加密参数或请求链路，不为模块齐全补写内容。以下 `source-report` 表示来源作者的描述，包含作者提出的假设，不是本次独立运行时事实。

<a id="risk-control"></a>
## 风控检测面

| claim_id | 来源提供的材料 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源把 ACW WAF、FeiLin 和 SensorsData 列为三层相关组件，并分别讨论反调试、指纹/人机识别、行为埋点 | [architecture-report：风控架构回顾](./51job-anti-detection-analysis.md#风控架构回顾) | source-report | 来源所述 51job Web 页面 | 只是历史组件归因；埋点存在不自动证明其参与某次服务端拦截 |
| C2 | 来源把函数字符串、类型/引用、属性描述符、iframe 对照、调用栈与时序列为插装可见面 | [vector-report：V1、V3–V5、V8–V10](./51job-anti-detection-analysis.md#检测向量清单--对抗矩阵) | source-report | 对 timer 等浏览器 API 的页面侧改动 | 是候选检查面，不代表当前页面实际逐项执行这些检查 |
| C3 | 来源用“timer 回调是否仍执行”说明只阻断整个回调会混淆反调试与正常业务行为，并单列 eval 完整性问题 | [vector-report：V2、V11](./51job-anti-detection-analysis.md#检测向量清单--对抗矩阵) | source-report | 回调执行与动态求值的行为一致性 | 本次未运行来源的源码净化或 eval 包装；不能从“未暂停”推出语义等价 |
| C4 | 来源讨论扩展痕迹、内联脚本扫描、CSP 与后续覆盖 hook 的可能性 | [vector-report：V6、V7、V12、V13](./51job-anti-detection-analysis.md#检测向量清单--对抗矩阵) | source-report | 注入方式、页面安全策略与初始化时机 | 未验证目标的当前检测脚本或响应头；来源中的未设置 CSP 结论不作为当前事实 |
| C5 | 来源明确保留 iframe 原生引用、调试侧信道、行为分析和挑战弹窗等未解决项 | [residual-report：残留风险](./51job-anti-detection-analysis.md#未完全解决的残留风险) | source-report | 来源脚本的能力边界 | 不代表这些机制都已在目标上命中，也不证明更换浏览器即可解决 |

### 查阅时怎样使用

- **调试暂停消失但业务异常**：先查 C3，对比未修改基线中的回调副作用、返回值和异常，不先把业务异常归为新的服务端检测。
- **页面初始化前后表现不同**：查 C2、C4，记录 wrapper 的安装时机和后续覆盖；来源报告的页面自行包装 timer 不足以证明额外包装不会被发现。
- **页面能运行但仍出现挑战**：查 C1、C5。反调试、身份/指纹、行为和挑战处置不是同一个完成条件；当前命中的原因仍须采证。

## 验证与限制

以下是复用前需要补齐的验收问题，不是已经完成的实验：

| 对照项 | 要区分什么 | 当前状态 |
|---|---|---|
| 浏览器与页面版本 | 哪个 bundle、哪个浏览器版本、何时采集 | 未记录当前样本，不能跨版本继承 |
| 函数字符串检查 | `fn.toString()` 与 `Function.prototype.toString.call(fn)` 是否分别对照 | 未复现；不能直接继承来源的“已解决”标签 |
| timer / eval 行为 | 是否保留必要的副作用、作用域、返回值与异常 | 没有本次等价性 fixture；来源方案只作为待审查材料 |
| CSP | 响应头与页面声明分别提供什么约束 | 没有当前响应头；仅检查 meta 不作为当前完整结论 |
| 可见改动与服务端结果 | 哪一项改动对应哪一种可重复现象 | 未做单变量对照，不给出因果或稳定绕过结论 |

不收录来源中的 v3 实现为通用修复代码，不复制其风险高低评级。需要当前站点事实时，应新建有明确版本与采样边界的分析记录，再按结论更新本卡；不要覆盖或改写原来源稿。
