---
schema_version: 2
id: anti-detection-chromium-cdp-detection-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-cdp-detection]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./14-cdp-detection-bypass.md#一cpd检测是什么"
    basis: unknown
  - id: s2
    ref: "./14-cdp-detection-bypass.md#二cdp-检测原理"
    basis: unknown
  - id: s3
    ref: "./14-cdp-detection-bypass.md#三代码实现cdp检测"
    basis: unknown
  - id: s4
    ref: "./14-cdp-detection-bypass.md#四修改源码绕过cdp检测"
    basis: unknown
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2, s3]
    basis: unknown
    limits: 只保留来源对检测场景和计数差形状的描述。页面全文不转入本卡。未编译、未打开控制台、未用自动化工具复测。
  - name: interfaces
    anchor: interfaces
    sources: [s4]
    basis: unknown
    limits: 只定位来源点名的 V8Console::Debug 与 reportCall 注释。没有对照 Chromium 修订，没有编译产物，也没有站点通过条件。
relations:
  - type: derived_from
    target: "./14-cdp-detection-bypass.md#四修改源码绕过cdp检测"
tags: [Chromium, CDP, V8Console, unknown]
---

# Chromium CDP 检测与 V8Console::Debug 接缝

这张卡检索来源如何描述 CDP 检测，以及它把绕过落在哪个 V8 inspector 函数上。依据只到 `source-report`。末节两个站点 URL 没有观察项，不单建 validation。来源没有失败出口，不升为 procedure。

<a id="risk-control"></a>
## 检测形状

来源把 CDP 检测写成机器人检测，并把打开 F12，或用 selenium、puppeteer 打开页面，说成会被识别。原理段称 `console.debug()` 在打开控制台时才真正被调用，一旦触发就认定打开了 F12。原文把 console 写成 consle，这里不改正。

实现段的检测页在 `Error` 对象上定义 `stack` getter，getter 里累加计数，然后调用 `console.debug(errObj)` 再读 `stack`。来源用调用前后计数是否仍等于 `rng1 + rng2` 决定结果。这是来源写出的检测形状，不是本轮复现。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源把 CDP 检测写成常见机器人检测 | s1 `14-cdp-detection-bypass.md:25` 原文：cdp检测(`Chrome DevTools Protocol Detection`)，是许多网站常用的机器人检测手段之一。 | unknown | chromium-cdp-detection | 未复现 |
| C2 | 来源把 F12、selenium、puppeteer 写成会触发识别 | s1 `14-cdp-detection-bypass.md:26` 原文：当每次打开F12控制台，或者使用selenium，puppeteer之类的自动化工具打开网页，都会被识别成机器人。 | unknown | chromium-cdp-detection | 作者场景，不是本轮观察 |
| C3 | 来源称 console.debug 打开控制台才真正调用 | s2 `14-cdp-detection-bypass.md:30` 原文：cdp检测的原理一般是利用`console.debug()`函数来实现，当你打开consle控制台时，`console.debug()`才会真正的被调用。 | unknown | chromium-cdp-detection | 保留原文拼写 |
| C4 | 检测页给 Error.stack 挂 getter | s3 `14-cdp-detection-bypass.md:63` 原文：Object.defineProperty(errObj, "stack", propertyDesc); | unknown | chromium-cdp-detection | 不复制整页 |
| C5 | 来源用计数差作为检测结果 | s3 `14-cdp-detection-bypass.md:66` 原文：if (rng1 + rng2 != acc) { | unknown | chromium-cdp-detection | 未运行该页 |

<a id="interfaces"></a>
## V8Console::Debug

来源假设 Chromium 已经能编译，然后指向 `\v8\src\inspector\v8-console.cc` 的 `V8Console::Debug`。原函数把调用交给 `ConsoleHelper::reportCall(ConsoleAPIType::kDebug)`。替换段把这行 `reportCall` 注释掉。作者给出的重新编译命令是 `ninja -C out/Default chrome`。来源没有写注释后调试日志、异常或控制台其它 API 会怎样，也没有定义文末两个站点怎样算通过。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 来源把改动定位到 v8-console.cc | s4 `14-cdp-detection-bypass.md:104` 原文：找到源码：`\v8\src\inspector\v8-console.cc` | unknown | chromium-cdp-detection | 未对照修订 |
| C7 | 原函数把 Debug 交给 reportCall | s4 `14-cdp-detection-bypass.md:113` 原文：.reportCall(ConsoleAPIType::kDebug); | unknown | chromium-cdp-detection | 只此调用 |
| C8 | 来源的替换是注释掉该 reportCall | s4 `14-cdp-detection-bypass.md:124` 原文：//    .reportCall(ConsoleAPIType::kDebug); | unknown | chromium-cdp-detection | 不表示检测已消失 |
| C9 | 来源把重新编译写成 ninja chrome | s4 `14-cdp-detection-bypass.md:131` 原文：ninja  -C  out/Default chrome | unknown | chromium-cdp-detection | 未执行 |

## 验证与限制

文末只列出 fingerprint.com 的 bot-detection 产品页和 browserscan 的 bot-detection 页，没有通过、失败或对照项，所以不建 validation。公开来源 URL 在归档 front matter 里是未知。本轮没有 Chromium 树、没有编译、没有打开控制台。
