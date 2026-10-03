---
schema_version: 2
id: khbox-v01-context-and-named-property
document_type: reference
original_date: '2026-02-05'
archived_date: '2026-10-02'
scope:
  targets:
    - KhBox
  client: node
  version: V0.1
  observed_at: '2026-02-05'
sources:
  - id: s1
    ref: "./koohai-20260205-01.md#khbox-6v01-功能实现"
    basis: source-report
  - id: s2
    ref: "./koohai-20260205-01.md#-已实现功能"
    basis: source-report
  - id: s3
    ref: "./koohai-20260205-01.md#-待实现功能"
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s2]
    basis: source-report
    limits: 只记录作者对 context 和分发顺序的说法。未替换 getCurrentContext，也未看 addon。
  - name: parameters
    anchor: parameters
    sources: [s2, s3]
    basis: source-report
    limits: kYes/kNo 是未完成项。不把这段回调当成已经接上的 in/delete。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 22 和 0 是作者计数。本次没有运行。通用宿主检测面不在这张卡复述。
relations:
  - type: derived_from
    target: "./koohai-20260205-01.md#-待实现功能"
tags:
  - KhBox
  - V8
  - jsdom
---

# KhBox V0.1：context 拆开和没做完的 in/delete

这张卡只回答 2026-02-05 这篇 V0.1 进度：原型对不上被归到哪里，分发先走哪一层，以及 `in`/`delete` 卡在什么返回值。`document`、`window`、`navigator` 的通用检测面仍看既有宿主对象卡，这里不重列 typeof 或布尔化谓词。

<a id="decision-flow"></a>
## context 和分发顺序

作者把原型不一致写成 node、vm、addon 各有 context。原文是：node运行js的时候有个自己的context。接着写处理是：替换掉了getCurrentContext。

已实现清单里的分发顺序是：分发函数优先用自己的envFuncs， 没有的话降级jsdom。返回之后：分发函数返回后c层自动包装+保护。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 原型不一致的原因原文含 node运行js的时候有个自己的context | s1，正文 | source-report | 这篇 V0.1 | 没有替换前后的原型对照 |
| C2 | 处理原文是替换掉了getCurrentContext | s1，正文 | source-report | 这篇 V0.1 | 未看替换后的调用点 |
| C3 | 分发原文是分发函数优先用自己的envFuncs， 没有的话降级jsdom | s2，已实现功能 | source-report | 作者当时的分发 | 没有 envFuncs 名单 |
| C4 | 返回后的原文是分发函数返回后c层自动包装+保护 | s2，已实现功能 | source-report | 作者当时的分发 | 未看 C 层包装代码 |

<a id="parameters"></a>
## 保护位置和未完成的命名属性

get/set 要看函数挂在哪一层。原文是：get/set保护（识别到函数是在构造 ,原型,或者实例上 ）。toString 在这句里写成了 toSting，不改字。

`in` 和 `delete` 没有做成。原文是：返回的是kYes 或者kNo，不是true或者false。同段回调使用 PropertyHandlerFlags::kNonMasking。错误堆栈 filter 和运行时动态指纹只有待实现标题，没有参数。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 保护位置原文是 get/set保护（识别到函数是在构造 ,原型,或者实例上 ） | s2，已实现功能 | source-report | V0.1 已实现清单 | 原文 toString 拼写是 toSting |
| C6 | 未完成原因原文是返回的是kYes 或者kNo，不是true或者false | s3，待实现功能 | source-report | 命名属性拦截 | 作者写明暂时没有更好的思路 |
| C7 | 回调标志原文含 PropertyHandlerFlags::kNonMasking | s3，待实现功能 | source-report | 该段配置 | 不表示 in/delete 已经返回布尔值 |

<a id="validation"></a>
## 作者自己的计数

汇总行含 通过: 22 项。收束句是 目前的算是都过了。这只说明作者当时把自测计成全过，不说明宿主对象语义已经和浏览器一致。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 汇总原文含 通过: 22 项 | s1，正文 | source-report | 这次粘贴的自测 | 本次未重跑，失败数以作者所写 0 为准 |
| C9 | 收束原文是目前的算是都过了 | s1，正文 | source-report | 这篇进度 | 后文立即列出未实现项 |

## 验证与限制

- 依据保持 source-report。没有本地运行，也不把 22/0 写成已复核。
- 通用 `document.all`、window 身份和 navigator 检测面不从这篇复制到宿主对象卡，也不从那些卡回填 KhBox。
- 堆栈 filter 和动态指纹没有步骤，不能升成流程。
- 2026-02-09 的 bootstrap 和 2026-02-25 的内部绑定不在这篇范围内。
