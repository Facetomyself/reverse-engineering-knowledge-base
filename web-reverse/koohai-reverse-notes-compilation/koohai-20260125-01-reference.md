---
schema_version: 2
id: koohai-20260125-addon-dispatch-reference
document_type: reference
original_date: '2026-01-25'
archived_date: '2026-10-02'
scope:
  targets:
    - khbox
    - jsdom
    - node
  client: node
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./koohai-20260125-01.md#nodejs-浏览器环境模拟从-addon-再到纯-node"
    basis: source-report
  - id: s2
    ref: "./koohai-20260125-01.md#1-双层对象架构"
    basis: source-report
  - id: s3
    ref: "./koohai-20260125-01.md#2-js-层分发逻辑"
    basis: source-report
  - id: s4
    ref: "./koohai-20260125-01.md#3-补环境能力"
    basis: source-report
  - id: s5
    ref: "./koohai-20260125-01.md#问题表现"
    basis: source-report
  - id: s6
    ref: "./koohai-20260125-01.md#v8-context-的本质"
    basis: source-report
  - id: s7
    ref: "./koohai-20260125-01.md#临时解决方案"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2]
    basis: source-report
    limits: 只保留来源对 C 层初始化、Shadow Object 和 InternalField 的描述。效果展示一节为空。未核对 addon 二进制。
  - name: decision-flow
    anchor: decision-flow
    sources: [s3, s4, s5, s6, s7]
    basis: source-report
    limits: envFuncs 优先、instanceof 失败和 new Function 绕行都是来源陈述。自定义 UA 占位原值不转写。篇末仍要求改 Node。
relations:
  - type: derived_from
    target: "./koohai-20260125-01.md#核心机制"
tags:
  - khbox
  - jsdom
  - source-report
---

# KhBox addon 的 jsDispatch 与 V8 Context 隔离

这张卡只回答：来源如何描述 addon 版一次 DOM 调用经过哪些层，`envFuncs` 和 jsdom 谁先执行，以及为什么作者说 vm Context 里 `instanceof` 会断。不提供 addon 源码。自定义 UA 占位原值不进入本卡。

「已跑通但有局限」是作者自述。效果展示没有内容。篇末写还是得改 Node。2026-01-05 的 `node_contextify` 查找键是另一套拼法，不并进本卡。

<a id="interfaces"></a>
## 双层对象

来源把以前在 JS 层做的对象初始化改到 C 层，先完成原型链和方法保护，再导入 sandbox 当全局。原文把 sandbox 写成 sanbox。使用时 jsdom 只作实际执行者，不使用它的原型链。来源认为这样用户只写缺失的 env，同时承认有局限。

示意中的一次 `document.getElementById` 依次经过 Shadow Object（C++ 拦截器）、`GenericMethod`、`CallJSDispatcher`、`jsDispatch`、unwrap 出的 JSDOM 实现、`WrapReturnValue`，最后返回 Shadow Element。Shadow Object 带 V8 拦截器。JSDOM 对象被说成放在 InternalField。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 来源把原型链和方法保护先在 C 层做完，再导入 sandbox 作为全局；原文写作 sanbox。 | 导入到sanbox作为全局 | ./koohai-20260125-01.md:39 | source-report | 框架完成度是作者自述。 |
| C2 | 使用时 jsdom 只作执行者，来源称不使用它的任何原型链。 | jsdom只作为实际执行者，不使用它的任何原型链。 | ./koohai-20260125-01.md:40 | source-report | 同句承认这个做法有局限。 |
| C3 | 一次 getElementById 被画成先进入 Shadow Object 这层 C++ 拦截器。 | Shadow Object (C++ 拦截器) | ./koohai-20260125-01.md:52 | source-report | 图是来源的调用示意，不是堆栈采样。 |
| C4 | 示意在 unwrap JSDOM 实现之前经过 jsDispatch。 | jsDispatch(JS) | ./koohai-20260125-01.md:52 | source-report | 与 C3 来自同一张示意。 |
| C5 | 来源把 JSDOM 对象说成真实 DOM 实现，并放在 InternalField。 | 存在 InternalField | ./koohai-20260125-01.md:55 | source-report | 未核对 V8 internal field 槽位。 |

<a id="decision-flow"></a>
## 补丁优先，以及 Context 断开后的临时执行

`jsDispatch` 的顺序是：先看 `global.khBox.envFuncs[dispatchName]`，有则 `apply(receiver, args)`；否则 `addon.unwrap(receiver)`，再 `impl[prop].apply(impl, args)`。返回值由 C++ 再包装。

补丁键写成 `Navigator_userAgent_get`、`Document_cookie_get`、`Document_all_call`，并注明优先级高于 JSDOM。这里只保留键名。`Document_cookie_get` 读来源自己的存储；存储内容不记录。这套大写类名前缀和 2026-01-05 的 `base_name + "_" + property + "_get"` 不是同一条已经对照过的规则。

vm Context 里，`getElementsByTagName` 的结果被作者标成 `instanceof HTMLCollection` 为 false，元素对 `HTMLSpanElement` 同样失败。来源的原因是每个 V8 Context 有自己的构造函数，同名也不是同一个对象，并写 `ctor_main != ctor_vm`。

临时取舍原句是：不用 vm 可以运行，但会多一些监测点；用 vm 会丢原型链，并在 `isinstanceof` 上报错。对应代码注释掉 `vm.Script`，改为 `addon.getConstructors()` 铺进 sandbox，再用 `new Function(...Object.keys(sandbox), scriptCode)`。作者最后仍写还是得改 Node，只是认为现有逻辑大部分可以复用。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C6 | jsDispatch 先查 global.khBox.envFuncs[dispatchName]，命中则 apply 到 receiver。 | global.khBox.envFuncs[dispatchName] | ./koohai-20260125-01.md:60 | source-report | 分发函数是粘连片段，不是完整源文件。 |
| C7 | 补丁键使用 Navigator_userAgent_get 这种类名加属性加 get 的形式，并被写成高于 JSDOM。 | Navigator_userAgent_get | ./koohai-20260125-01.md:68 | source-report | 只记录键名。函数返回的 UA 占位原值不进入卡片。 |
| C8 | 同一补丁表还有 Document_cookie_get，读取来源自己的 cookie 存储。 | Document_cookie_get | ./koohai-20260125-01.md:69 | source-report | 不记录存储内容。 |
| C9 | Document_all_call 被写成可以完全自定义，而不是交给 JSDOM 的默认实现。 | Document_all_call | ./koohai-20260125-01.md:70 | source-report | 函数体只有占位注释。 |
| C10 | 来源在 vm Context 里把 spans instanceof HTMLCollection 标成 false，并认为应当为 true。 | spans instanceof HTMLCollection | ./koohai-20260125-01.md:79 | source-report | false 是作者注释，不是本轮执行。 |
| C11 | 来源把上述 instanceof 失败归结为原型链断裂。 | 原型链断裂 | ./koohai-20260125-01.md:81 | source-report | 未单独验证 __proto__ 比较。 |
| C12 | 来源用 ctor_main 与 ctor_vm 不相等说明两个 Context 的构造函数是不同对象。 | ctor_main != ctor_vm | ./koohai-20260125-01.md:97 | source-report | 示例没有附带可编译的 V8 片段。 |
| C13 | 临时取舍是不用 vm 也能跑但监测点变多；用 vm 则丢原型链并在 isinstanceof 上报错。 | 不使用vm可以运行但是会额外增加一些监测点。使用vm会导致一些原型链丢失，isinstanceof 报错。 | ./koohai-20260125-01.md:103 | source-report | isinstanceof 是来源原拼写。两条都未复跑。 |
| C14 | 临时执行路径用 addon.getConstructors() 把构造函数铺进 sandbox。 | addon.getConstructors() | ./koohai-20260125-01.md:110 | source-report | 没有列出构造函数名单。 |
| C15 | 脚本通过 new Function 注入 sandbox 的键，而不是 vm.Script。 | new Function(...Object.keys(sandbox), scriptCode) | ./koohai-20260125-01.md:110 | source-report | 上方 vm.Script 路径在来源里被注释掉。 |
| C16 | 篇末仍然认为要改 Node，只是说当前逻辑大部分可以复用。 | 还是得改node | ./koohai-20260125-01.md:112 | source-report | 不是验收通过，也没有给出改动的文件清单。 |

## 验证与限制

未运行 addon，未核对 C++ 拦截器或 `getConstructors` 的返回值。效果展示是空标题。没有可指认的输出定义、验收条件或失败出口，所以不建流程。

`instanceof` 为 false、不用 vm 会增加监测点、以及「很快就可以出效果」，都停留在来源自述。自定义 UA 占位字符串不转写。
