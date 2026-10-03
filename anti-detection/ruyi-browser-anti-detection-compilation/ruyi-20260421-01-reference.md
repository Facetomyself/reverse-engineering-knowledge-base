---
schema_version: 2
id: ruyi-20260421-ruishu6-domtrace-reference
document_type: reference
original_date: '2026-04-21'
archived_date: '2026-10-02'
scope:
  targets: [ruishu]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ruyi-20260421-01.md#前言"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留四个动态字段、Caesar +2 和按 nsd 洗牌后索引不稳定。不抄字段示例、cookie 值或解码对照表。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留检测类别、自定义事件名、Node 检测和 cookie 写后读回。不收录指纹取值，也不收录绕过代码。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留「先记录 DOM API，不逆虚拟机」。作者的后三步没有驳回条件，不能当成流程。
relations:
  - type: derived_from
    target: "./ruyi-20260421-01.md#前言"
tags: [ruishu, dom-trace, source-report]
---

# 瑞数 6 代：索引会洗牌，检测看 DOM 调用

这篇卡检索的是：这份来源里，为什么不能靠静态字节码索引找字符串，以及 DOM Trace 被说成记录了哪几类检测。412 到业务响应的链路和验收已经在两张瑞数产品卡里，这里不重复，也不提供补环境脚本。

<a id="parameters"></a>
## 会变的输入

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 动态输入被写成四个关键动态参数（每次请求都变化） | s1，源文件第 136 行 | source-report | 来源解析的那次 412 页面 | 不抄表中的示例值 |
| C2 | 字符串第一层是 Caesar +2 偏移编码 | s1，源文件第 167 行 | source-report | 来源给出的关键字符串 | 解码对照表不在本卡 |
| C3 | 第二层是 Fisher-Yates 随机洗牌，洗牌种子与 $_ts.nsd 相关 | s1，源文件第 182 行 | source-report | 加载后的字符串表 | 不包含洗牌实现 |
| C4 | 因此同一个字节码索引在不同请求中指向不同的字符串 | s1，源文件第 183 行 | source-report | 这套字符串表 | 不是所有虚拟机的通例 |

<a id="risk-control"></a>
## 记录到的检测

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 检测面包括 30+种自动化工具检测、Canvas/WebGL双重指纹采集、双Cookie联动验证 | s1，源文件第 40 行 | source-report | 来源所称的第 6 代 | 30+ 是作者计数；不抄指纹值 |
| C6 | 事件名里有 addEventListener("driver-evaluate"，同一行还有 webdriver-evaluate 和 selenium-evaluate | s1，源文件第 229 行 | source-report | 来源 trace 的事件注册 | 没有处理函数本体 |
| C7 | Node 被单独写成：瑞数专门检测你是不是在Node.js里跑的 | s1，源文件第 235 行 | source-report | 来源 trace 的环境探测 | 不收录绕过写法 |
| C8 | cookie 探针的失败条件是：如果读不回来，直接判定环境异常！ | s1，源文件第 316 行 | source-report | 来源描述的写后读回 | 测试 cookie 不在本卡；这不是流程失败出口 |

<a id="decision-flow"></a>
## 先记调用，不逆虚拟机

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C9 | 方法句是：不去逆虚拟机内部，而是在更底层——DOM API层面——记录瑞数JS执行时所有的API调用。 | s1，源文件第 80 行 | source-report | 来源的 DOM Trace | 日志行数没有随文给出可复核文件 |
| C10 | 第一步写成 DOMtrace记录所有API调用（what） | s1，源文件第 92 行 | source-report | 来源列出的四步 | 后三步没有驳回条件 |

## 验证与限制

`ruishu` 的 request-chain 和 validation 已在 `../../web-reverse/products/ruishu-rs6-challenge.md` 与 `../../web-reverse/products/ruishu-rs6-hybrid.md`。本卡不建这两块。risk-control、decision-flow、parameters 的查询是 0。第 8 节的原型链、沙箱、定时器和固定画布返回值不进入本卡。第 9 节的通过表保持作者自述。站点、cookie 值和指纹取值不在这里。
