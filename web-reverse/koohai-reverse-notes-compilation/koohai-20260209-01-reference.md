---
schema_version: 2
id: khbox-v1-vm-bootstrap-and-invocation
document_type: reference
original_date: '2026-02-09'
archived_date: '2026-10-02'
scope:
  targets:
    - KhBox
  client: node
  version: v1
  observed_at: '2026-02-09'
sources:
  - id: s1
    ref: "./koohai-20260209-01.md#khbox-7v1完善"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留作者新增点名的非法调用、堆栈路径和 webdriver 条件。不收录指纹原值。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: bootstrap 仍在 JS。作者写明要重构。不覆盖后来的内部绑定。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录别名键和 toStringTag 的写法。不把 __config 当成公开配置格式。
relations:
  - type: derived_from
    target: "./koohai-20260209-01.md#khbox-7v1完善"
tags:
  - KhBox
  - V8
  - Illegal invocation
---

# KhBox v1：VM 内 bootstrap 和新增的调用、堆栈检查

这张卡只回答 2026-02-09 这一版比前一篇多写清的两件事：检测上新加了什么，以及初始化为什么仍放在 VM 里的 JS。`document.all` 的 typeof 和布尔化不在这里重复。

<a id="risk-control"></a>
## 非法调用、堆栈和 webdriver

作者对新增点的原句是：新加的几个监测点比如非法调用，stack堆栈等。toString 除了 alert 的格式，还要求 无法通过 call 绕过 toString 保护。

webdriver 的条件原文是 navigator.webdriver === false 或 undefined。脱离上下文的检查名是 getElementById 脱离上下文抛出 Illegal invocation。堆栈原文要求 Error.stack 不暴露 khbox_internal，同一行还要求不暴露 node_modules。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 新增点原文是新加的几个监测点比如非法调用，stack堆栈等 | s1，正文 | source-report | 作者说的这一版 input | 同时写了可能还有遗漏 |
| C2 | call 绕过检查的原文含无法通过 call 绕过 toString 保护 | s1，正文 | source-report | alert 这一条 | 未拿真实函数串对照 |
| C3 | webdriver 条件原文是 navigator.webdriver === false 或 undefined | s1，正文 | source-report | 这条检查 | 不记录实际属性值 |
| C4 | 脱离上下文的检查名是 getElementById 脱离上下文抛出 Illegal invocation | s1，正文 | source-report | getElementById 这一条 | setAttribute 是下一条同类检查 |
| C5 | 堆栈原文含 Error.stack 不暴露 khbox_internal | s1，正文 | source-report | 这条字符串检查 | 未看到堆栈样本 |

<a id="decision-flow"></a>
## 仍在 JS 里的 VM bootstrap

初始化原句含 addon.initializeInContext(__config)。shadow 的创建原句含 addon.createInstance(globalThis,"Window")。原型接上的原句是 Object.setPrototypeOf(globalThis, shadowWindow)。

作者把边界写在最后：部分还是放在了js层来做保护，需要重构。因此这张卡停在 v1 的 JS bootstrap，不把 2026-02-25 的内部绑定算进来。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 初始化原文含 addon.initializeInContext(__config) | s1，正文 | source-report | 这段 bootstrap | __config 的字段不在正文 |
| C7 | Window shadow 原文含 addon.createInstance(globalThis,"Window") | s1，正文 | source-report | 同一次 VM 初始化 | 其余类名同一行列出，未逐个验证 |
| C9 | 原型原文是 Object.setPrototypeOf(globalThis, shadowWindow) | s1，正文 | source-report | 这段 bootstrap | 未看 C++ 是否又改原型 |
| C11 | 边界原文是部分还是放在了js层来做保护，需要重构 | s1，文末 | source-report | v1 | 重构发生在别的日期的笔记 |

<a id="parameters"></a>
## 别名和 toStringTag

四个别名的键原文是 ['window','self','top','parent']，getter 返回 globalThis。toStringTag 的原文含 Symbol.toStringTag，值写成 Window。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 别名键原文是 ['window','self','top','parent'] | s1，bootstrap | source-report | 这段 JS | 不证明 iframe 里 top 仍等于 window |
| C10 | 标签原文含 Symbol.toStringTag | s1，bootstrap | source-report | globalThis 这一处 | 未调用 Object.prototype.toString |

## 验证与限制

- 作者说这一版过了，同时说可能还有遗漏。计数不是本次结果。
- 不把 userAgent、语言或屏幕数字写进来。正文只检查类型或 undefined。
- bootstrap 缺 addon 和 __config 的定义，不能当初始化说明书。
- 没有失败出口，不建流程。
