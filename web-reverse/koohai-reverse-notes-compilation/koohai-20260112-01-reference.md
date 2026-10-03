---
schema_version: 2
id: koohai-20260112-proto-illegal-invocation-reference
document_type: reference
original_date: '2026-01-12'
archived_date: '2026-10-02'
scope:
  targets:
    - khbox
    - jsdom
  client: node
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./koohai-20260112-01.md#1-原型链继承"
    basis: source-report
  - id: s2
    ref: "./koohai-20260112-01.md#2-native-code-伪装"
    basis: source-report
  - id: s3
    ref: "./koohai-20260112-01.md#3-illegal-invocation-保护"
    basis: source-report
  - id: s4
    ref: "./koohai-20260112-01.md#实现方式"
    basis: source-report
  - id: s5
    ref: "./koohai-20260112-01.md#技术原理"
    basis: source-report
  - id: s6
    ref: "./koohai-20260112-01.md#第一层固定到-prototype-上"
    basis: source-report
  - id: s7
    ref: "./koohai-20260112-01.md#第二层classname-来源"
    basis: source-report
  - id: s8
    ref: "./koohai-20260112-01.md#运行结果"
    basis: source-report
  - id: s9
    ref: "./koohai-20260112-01.md#3-illegal-invocation-保护-1"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2, s3, s8]
    basis: source-report
    limits: 检测式和非法调用日志都是来源摘录。未在浏览器或本机复跑。测试输出里的 UA 原值不转写。
  - name: interfaces
    anchor: interfaces
    sources: [s4, s5]
    basis: source-report
    limits: sandbox 构造函数和 Private Symbol 只按本篇描述记录。未核对 jsdom 版本，也未核对 V8 的 toString 实现。
  - name: decision-flow
    anchor: decision-flow
    sources: [s6, s7, s9]
    basis: source-report
    limits: 来源称为三层，架构正文只展开两层。运行时 this 检查只有总结句和一条日志，没有检查函数。
relations:
  - type: derived_from
    target: "./koohai-20260112-01.md#illegal-invocation-保护机制"
tags:
  - khbox
  - jsdom
  - source-report
---

# KhBox 的原型链、native toString 与 Illegal invocation

这张卡只回答：来源把原型链、`Function.prototype.toString` 的 native code 外观，以及 getter 的 Illegal invocation，分别说成怎样检测、怎样放进 sandbox。不提供可运行补环境。作者测试日志里的 UA 原值不进入本卡。

作者把原型保护、toString 和 illegal 保护打了勾，并写「ps:可能有bug」。勾是来源自述。异步、业务日志保存和去掉 Node 特征仍在待做。2026-01-05 的 `lookup_key` 和 2026-01-25 的 Context 隔离不是这一篇的模块。

<a id="risk-control"></a>
## 来源写下的检测式

原型链检测要求 `Object.getPrototypeOf(Document.prototype).constructor.name` 为 `Node`，并且 `'addEventListener' in EventTarget.prototype` 为真。来源给出的继承关系是 Document 到 Node 到 EventTarget，Navigator 到 Object，Window 到 EventTarget。

`toString` 检测被写成：浏览器原生方法返回带 `[native code]` 的字符串，普通函数会把函数体露出来。Illegal invocation 被写成：从 `Navigator.prototype` 取出 `userAgent` 的 getter 后对 `window` 调用，浏览器抛 `TypeError: Illegal invocation`；普通 JS getter 仍能执行，来源认为这不一致。

作者粘贴的非法调用日志写有 `Expected: 'Navigator', Actual: 'Window'`。这不是本轮运行结果。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 来源把 Document.prototype 的上一层构造函数名必须是 Node 写成网站检测式。 | Object.getPrototypeOf(Document.prototype).constructor.name | ./koohai-20260112-01.md:67 | source-report | 检测式是来源摘录，未在浏览器里复跑。 |
| C2 | 同一检测块还要求 addEventListener 出现在 EventTarget.prototype 上。 | 'addEventListener' in EventTarget.prototype | ./koohai-20260112-01.md:67 | source-report | 与 C1 同属来源摘录。 |
| C3 | 来源把 this 类型不符时的浏览器行为写成 TypeError: Illegal invocation。 | TypeError: Illegal invocation | ./koohai-20260112-01.md:132 | source-report | 未在当前浏览器复现该异常。 |
| C4 | 作者贴出的非法调用日志把期望类名写成 Navigator、实际写成 Window。 | Expected: 'Navigator', Actual: 'Window' | ./koohai-20260112-01.md:193 | source-report | 这是来源粘贴的输出，不是本轮运行结果。UA 原值不摘录。 |

<a id="interfaces"></a>
## sandbox 与 Private Symbol

来源的 sandbox 同时放两套东西：经过 KhBox Proxy 的 `document`、`navigator`、`window` 实例，以及直接引用的 JSDOM 构造函数 `Document`、`Navigator`、`Window`、`Node`、`EventTarget`。总结把这说成在 sandbox 中暴露 JSDOM 的构造函数，并保持 prototype 链。

`CreateNativeWrapper` 按方法是 get 还是普通方法，生成带 `[native code]` 的字符串，再用 `GetNativeStringSymbol` 做 Private Symbol 存到函数上。来源列出三个后果：`Object.keys` 不可枚举、JavaScript 层不能读写、`Function.prototype.toString` 会优先读这个 Symbol。第三句是作者对 V8 的说法。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C5 | 原型链部分的做法是在 sandbox 里暴露 JSDOM 构造函数，而不是只放实例。 | 在 sandbox 中暴露 JSDOM 的构造函数 | ./koohai-20260112-01.md:202 | source-report | 构造函数清单以本篇 demo 片段为准，未核对 jsdom 版本。 |
| C6 | native toString 用 Private Symbol 保存自定义字符串，符号来自 GetNativeStringSymbol。 | GetNativeStringSymbol | ./koohai-20260112-01.md:112 | source-report | 未核对 V8 是否真的让 Function.prototype.toString 优先读该私有符号。 |
| C7 | 来源称这个 Private Symbol 不可枚举，Object.keys 拿不到。 | 不可枚举 | ./koohai-20260112-01.md:117 | source-report | 同时声称 JavaScript 层不能读写；本轮只读到该句。 |
| C8 | 来源称 Function.prototype.toString 会优先读取该 Symbol。 | Function.prototype.toString | ./koohai-20260112-01.md:119 | source-report | 这是作者对 V8 行为的说法，不是本轮引擎对照。 |

<a id="decision-flow"></a>
## getter 焊在何处，类名从哪来

来源把 Illegal invocation 保护称为三层检查，但「实现架构」只写了两层。第一层通过 `window[protoOwner].prototype` 把实现焊到 `Constructor.prototype`，而不是实例。来源的反例是焊在实例上时，`navigator.userAgent` 能访问，`Navigator.prototype.userAgent` 拿不到 wrapper。

第二层不用 JSDOM 的 `constructor.name` 当权威类名，因为来源认为 jsdom 可能不全，要优先用自己脱下来的环境。`addon.watch(navigator, 'Navigator')` 把类名传进 C++，再放进 Proxy 的 InternalField。JS 侧降级是：JSON 来的 `classNameFromC`，然后 `Symbol.toStringTag`，然后 `target.constructor?.name`，最后 `"Unknown"`。

总结里的第三点才是运行时严格检查 `this`。类型不匹配就抛 `TypeError: Illegal invocation`。检查函数本体没有出现，只有测试日志里的期望类名和实际类名。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C9 | 来源把 Illegal invocation 保护称作三层检查。 | 三层检查机制 | ./koohai-20260112-01.md:140 | source-report | 架构小节只展开了前两层，第三层没有独立实现片段。 |
| C10 | 第一层把实现焊到 Constructor.prototype，而不是实例。 | 焊死到 Constructor.prototype 而不是实例上 | ./koohai-20260112-01.md:146 | source-report | 未验证描述符最终落在哪个对象上。 |
| C11 | 来源认为焊在实例上时，Navigator.prototype.userAgent 拿不到这层 wrapper。 | 拿不到我们的 wrapper | ./koohai-20260112-01.md:152 | source-report | 对比句是作者注释，不是本轮实验。 |
| C12 | 第二层类名优先用 JSON 配置，而不是 JSDOM 的 constructor.name。 | 使用 JSON 配置中的类名而不是 JSDOM 的 | ./koohai-20260112-01.md:157 | source-report | 来源解释是 jsdom 的类名可能不全。 |
| C13 | 调用点把类名显式传给 addon.watch，例如 Navigator 和 Window。 | addon.watch(navigator, 'Navigator') | ./koohai-20260112-01.md:164 | source-report | 只说明本篇示例，不代表所有对象都这样包。 |
| C14 | 类名降级顺序在 JSON 配置和 Symbol.toStringTag 之后才用 constructor.name，最后是 Unknown。 | target.constructor?.name | ./koohai-20260112-01.md:169 | source-report | 降级链来自来源片段，未跑缺省分支。 |
| C15 | 总结把第三点写成运行时严格检查 this 的类型，不匹配就抛 Illegal invocation。 | 运行时严格检查 | ./koohai-20260112-01.md:216 | source-report | 总结没有给出检查函数本体。 |

## 验证与限制

测试脚本路径写的是 `khbox_vm/pages/demo_proto/input.js`。本轮没有这个目录，也没有运行。作者打勾的原型链、toString 和非法调用都不能升成更高依据。

架构小节缺少第三层实现。待做清单说明异步和去 Node 特征还没做。空标题没有额外机制。因此本篇不是流程：没有完整的前提、验收和失败出口。
