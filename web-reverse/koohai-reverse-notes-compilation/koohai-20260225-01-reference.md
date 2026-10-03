---
schema_version: 2
id: khbox-node-binding-dispatch
document_type: reference
original_date: '2026-02-25'
archived_date: '2026-10-02'
scope:
  targets:
    - KhBox
  client: node
  version: node-internal
  observed_at: '2026-02-25'
sources:
  - id: s1
    ref: "./koohai-20260225-01.md#核心方案内部绑定而非-node-插件"
    basis: source-report
  - id: s2
    ref: "./koohai-20260225-01.md#toolsdispatchjs--引擎层"
    basis: source-report
  - id: s3
    ref: "./koohai-20260225-01.md#toolskhenvjs--框架层"
    basis: source-report
  - id: s4
    ref: "./koohai-20260225-01.md#toolsenvfuncsjs--dom-hook-实现"
    basis: source-report
  - id: s5
    ref: "./koohai-20260225-01.md#serverjs--http-签名服务"
    basis: source-report
  - id: s6
    ref: "./koohai-20260225-01.md#关键反检测特性"
    basis: source-report
  - id: s7
    ref: "./koohai-20260225-01.md#异步-token-获取-demo"
    basis: source-report
  - id: s8
    ref: "./koohai-20260225-01.md#正文"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s5, s7]
    basis: source-report
    limits: 只保留绑定入口、路由和字段名。不收录 Cookie、User-Agent 或 token 示例值。
  - name: decision-flow
    anchor: decision-flow
    sources: [s2, s3, s7, s8]
    basis: source-report
    limits: 并发覆盖和 30 秒上限是限制句，没有失败后的动作。
  - name: parameters
    anchor: parameters
    sources: [s3, s4]
    basis: source-report
    limits: 55 个钩子只看到四个键名。省略号不是实现。
  - name: risk-control
    anchor: risk-control
    sources: [s4, s6]
    basis: source-report
    limits: 表是作者对检测点的归类。未对照浏览器。
relations:
  - type: derived_from
    target: "./koohai-20260225-01.md#toolsdispatchjs--引擎层"
tags:
  - KhBox
  - Node
  - jsdom
---

# KhBox node 重构：内部绑定、jsDispatch 和两条回读

这张卡只回答 2026-02-25 重构后框架怎么挂进 Node、属性访问怎么分发、结果从哪一层读回来。不提供签名计算，也不收录示例里的 Cookie、User-Agent 或 token。

<a id="interfaces"></a>
## 内部绑定和 HTTP 字段

改动原因的原文含 使用原生vm会污染自己构造的context。绑定宏的原文是 NODE_BINDING_CONTEXT_AWARE_INTERNAL。入口原文是 addon = globalThis.khBox。

路由原文含 POST /sign/batch，同一行写明批量是顺序执行，避免状态竞争，另外有健康检查和页面列表。预置请求点名字段含 execAsync。响应计时字段原文含 executionTime。V8 回读表达式原文含 globalThis.__khResult。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C2 | 宏原文是 NODE_BINDING_CONTEXT_AWARE_INTERNAL | s1，核心方案 | source-report | 这篇描述的二进制 | 没有编译文件清单 |
| C3 | 入口原文含 addon = globalThis.khBox | s1，核心方案 | source-report | 新加载方式 | 未在进程里读取该符号 |
| C11 | 批量路由原文含 POST /sign/batch | s5，HTTP 签名服务 | source-report | 作者列出的四条路由 | 不收录请求示例值 |
| C15 | 异步字段原文含 execAsync | s5，请求体示例 | source-report | 预置页面这种形状 | 同行的 Cookie 和 User-Agent 不收录 |
| C16 | 计时字段原文含 executionTime | s5，响应示例 | source-report | 该次作者示例 | 不收录 cookie 或 token 字段的值 |
| C22 | 回读原文含 globalThis.__khResult | s7，extractResult | source-report | 写在 V8 全局上的结果 | 不表示业务签名字段 |

<a id="decision-flow"></a>
## 分发、隔离和两条结果

jsDispatch 的原文含 优先走 envFuncs Hook，否则 unwrap 到 JSDOM。每个请求的原文含 每次请求独立 JSDOM + browserContext。批量的限制原文是 并发请求会导致 Hook 互相覆盖。等待原文含 最大超时 30 秒。

异步约定原文含 window.__khResult。和 JSDOM 的差别原文是 JSDOM 没有副本。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 改动原因原文含使用原生vm会污染自己构造的context | s8，正文 | source-report | 这次重构的动机 | 未复现断点行为 |
| C4 | 优先分支原文是优先走 envFuncs Hook | s2，dispatch | source-report | browserContext 里的属性访问 | 未单步 jsDispatch |
| C6 | 等待上限原文是最大超时 30 秒 | s3，smartWait | source-report | setTimeout 计数 | 没有超时后的动作 |
| C13 | 隔离原文含每次请求独立 JSDOM + browserContext | s5，设计决策 | source-report | 该 HTTP 服务 | 未看实现是否真的新建 context |
| C14 | 并发风险原文是并发请求会导致 Hook 互相覆盖 | s5，设计决策 | source-report | 进程级 envFuncs | 不是失败处理步骤 |
| C20 | 约定名原文含 window.__khResult | s7，场景 | source-report | 作者的异步 demo | 不收录演示公式 |
| C21 | 存储差原文是 JSDOM 没有副本 | s7，读取原理 | source-report | __khResult 这一路 | cookie 平面仍走 jsDispatch |

<a id="parameters"></a>
## 模板注册和钩子键

注册原文含 addon.initialize(filteredConfig)，同一行还有 initDispatcher。启动一次的原文含 注册 842 个 DOM 模板。

钩子键原文含 Window_document_get 和 Navigator_webdriver_get。个数写在钩子表末尾，是 55。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 注册原文含 addon.initialize(filteredConfig) | s3，init | source-report | 过滤内置类之后 | 过滤名单只有 Error、Array 这种例子 |
| C12 | 次数原文含注册 842 个 DOM 模板 | s5，设计决策 | source-report | 进程启动 | 未数 json 条目 |
| C7 | 键名原文含 Window_document_get | s4，envFuncs | source-report | 这篇钩子表 | 函数体没有展开 |
| C8 | 键名原文含 Navigator_webdriver_get | s4，envFuncs | source-report | 这篇钩子表 | 不记录 userAgent |

<a id="risk-control"></a>
## 作者把检测点归到哪里

`Document_all_get` 的说明原文含 Document_all_get。堆栈钩子原文含 Error_prepareStackTrace。表里把 constructor 归到 createBrowserContext()，把 native toString 归到 addon.safeFunc(fn, name)，把 webdriver 写成 envFuncs Hook 强制返回。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C9 | 钩子名原文含 Document_all_get | s4，envFuncs | source-report | 该键的注释 | 实现是省略号 |
| C10 | 钩子名原文含 Error_prepareStackTrace | s4，envFuncs | source-report | 该键的注释 | 没有过滤规则正文 |
| C17 | 表的原文含 createBrowserContext() | s6，关键反检测特性 | source-report | window.constructor.name 这一行 | 未读 FunctionTemplate |
| C18 | 表的原文含 addon.safeFunc(fn, name) | s6，关键反检测特性 | source-report | Function.toString 这一行 | 未调用 toString |
| C19 | webdriver 原文含 envFuncs Hook 强制返回 | s6，关键反检测特性 | source-report | 表中这一行 | 返回值按该行所写，未实测 |

## 验证与限制

- 全是 source-report。没有编译自定义 Node，也没有发 `/sign`。
- 请求和日志里的 Cookie、User-Agent、token 不进入卡片。
- 30 秒和“并发会覆盖钩子”不够成失败出口，所以没有流程卡。
- V0.1 的 kYes/kNo 缺口、v1 仍在 JS 的 bootstrap 细节分别留在那两篇，不并进这张卡。
