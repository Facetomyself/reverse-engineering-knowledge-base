# 51job 风控检测面分析 & bypass 对抗设计

## 目标

分析 51job (we.51job.com) 对 Tampermonkey/debugger-bypass 脚本的**所有潜在检测向量**，并逐一设计对抗策略。

## 风控架构回顾

```
51job 三层联防:
  L1: 阿里 ACW WAF     → antidom.js (debugger注入) + interfaceacting.js (WebDriver检测)
  L2: 阿里飞林 FeiLin   → v1.4.2 设备指纹 + 人机识别 + 滑块验证码
  L3: 神策 SensorsData  → 用户行为埋点分析
```

## 检测向量清单 & 对抗矩阵

### V1: Function.prototype.toString 检测

| 项目 | 描述 |
|------|------|
| **检测原理** | `Function.prototype.toString.call(window.setInterval)` 检查是否返回 `function setInterval() { [native code] }` |
| **攻击面** | 如果 hook 返回自定义函数，toString 暴露自定义源码，立即可检测 |
| **v1 脚本状态** | 未处理 — `hookedSetInterval.toString()` 返回自定义函数体 |
| **v3 对策** | 预存原生 toString 字符串 → `wrapper.toString = function(){ return nativeStr; }` — 返回与原生完全一致的字符串 |
| **验证方法** | `Function.prototype.toString.call(window.setInterval) === _siStr` |

### V2: 回调执行完整性测试（关键！）

| 项目 | 描述 |
|------|------|
| **检测原理** | FeiLin 设置 `let flag=false; setInterval(function(){flag=true;debugger;},10)` → 50ms 后检查 `flag`。如果 hook 直接拦截了整个 setInterval 调用（返回0），则 `flag` 永远为 `false`，hook 暴露 |
| **攻击面** | v1/v2 脚本对含 debugger 的 callback 直接拦截整个 setInterval 调用，回调完全不执行 |
| **v3 对策** | **源码级净化** — 不拦截调用，而是用 `_sanitize()` 从 callback 源码中删除 `debugger;` 语句（替换为 `;`），重新构造函数，传给原生 setInterval。回调正常执行，flag 正常变为 true |
| **净化流程** | `fn.toString()` → `str.replace(/\bdebugger\b\s*;?/gi, ';')` → 提取参数+函数体 → `new Function(args, body)` → 传给原生 setInterval |
| **验证方法** | 在 Chrome DevTools 中运行 `let f=false;setInterval(function(){f=true;debugger;},10);setTimeout(function(){console.log('flag=',f)},50);` → 应输出 `flag=true` 且无 debugger 暂停 |

### V3: typeof / instanceof 检查

| 项目 | 描述 |
|------|------|
| **检测原理** | `typeof window.setInterval !== 'function'` 或 `!(window.setInterval instanceof Function)` |
| **攻击面** | Proxy 包装某些情况下可能改变 typeof 行为 |
| **v3 对策** | 使用普通 function wrapper（非 Proxy），`typeof` 和 `instanceof` 完全正常 |

### V4: Object.getOwnPropertyDescriptor 属性描述符检查

| 项目 | 描述 |
|------|------|
| **检测原理** | `Object.getOwnPropertyDescriptor(window, 'setInterval')` 检查 writable/configurable/enumerable 是否异常，或是否有 getter/setter |
| **攻击面** | 如果使用 accessor descriptor（getter/setter），或 configurable:false 标记，可被检测 |
| **v3 对策** | 使用 data descriptor: `{value: wrapper, writable:true, configurable:true, enumerable:true}` — 与原生完全一致 |
| **注意** | v2 中在 toString 上使用了 `writable:false, configurable:false`，这在 `Object.getOwnPropertyDescriptor(fn, 'toString')` 时可能暴露。v3 已移除 |

### V5: iframe 引用对比攻击

| 项目 | 描述 |
|------|------|
| **检测原理** | `document.createElement('iframe')` → `iframe.contentWindow.setInterval` 获取干净原生函数 → 与 `window.setInterval` 比较引用或 toString |
| **攻击面** | 原生 setInterval 的 toString 与我们的 wrapper 不同 |
| **v3 对策** | 部分缓解 — 因为 51job 自身已包装 setInterval（见下方 V10），窗口中的 setInterval 本身就不原生，iframe 对比不会触发额外告警。完整对抗需要 hook iframe.createElement |
| **风险评估** | 低 — 页面自身已覆盖原生函数 |

### V6: Tampermonkey 扩展检测

| 项目 | 描述 |
|------|------|
| **检测原理** | 检查 `navigator.userAgent` 中扩展痕迹、`document.documentElement.dataset.*`、`window.external`、`GM_*` 全局变量、`chrome.runtime` 等 |
| **攻击面** | Tampermonkey 在部分版本会在页面暴露可检测的属性 |
| **v3 对策** | 脚本使用 `@grant none`（不暴露 GM_* API）、清理 `data-tampermonkey` 等 DOM 属性 |
| **注意** | Firefox/ruyipage 中 `window.chrome` 不存在，这是天然优势。在 Chrome 中需额外注意 |

### V7: 脚本源码静态扫描

| 项目 | 描述 |
|------|------|
| **检测原理** | 遍历 `document.querySelectorAll('script:not([src])')` 扫描 textContent 中的敏感关键词（"debugger", "bypass", "hook", "hooked", "51job" 等） |
| **攻击面** | Tampermonkey 将脚本以 inline `<script>` 注入页面，FeiLin 可扫描其内容 |
| **v3 对策** | 关键字符串使用 `String.fromCharCode(100,101,98,117,103,103,101,114)` 替代 "debugger"；变量名精简为短名（`_hsi`, `_nts` 等）；移除所有注释；v3 脚本正文不含 "debugger" 字面量 |
| **验证** | 脚本 textContent 不包含字符串 `debugger` |

### V8: Error().stack 调用栈泄露

| 项目 | 描述 |
|------|------|
| **检测原理** | 在 hook 的回调中 `throw new Error()` 或检查 `Error().stack` 看是否有扩展/US 脚本路径 |
| **攻击面** | Hook 函数执行时如果抛出异常，调用栈会显示 userscript 路径 |
| **v3 对策** | Hook 函数是纯 JS 闭包，不含用户脚本引用。`@grant none` 不暴露扩展 ID。正常执行不会抛出异常 |

### V9: performance.now() 时序分析

| 项目 | 描述 |
|------|------|
| **检测原理** | 测量 `setInterval(fn, 0)` 或 `setTimeout(fn, 0)` 的执行时间，与预期值比较。Hook 增加额外处理开销 |
| **攻击面** | 源码级净化（`_sanitize`）涉及 `toString()` + `replace()` + `new Function()`，增加微秒级开销 |
| **v3 对策** | 开销极小（仅对含 debugger 的 callback 触发净化，正常 callback 直接透传）。`!hasDbg(src)` 时 `return fn` 直接返回，零额外开销 |
| **风险评估** | 低 — 正常函数零开销，debugger 函数极少被调用 |

### V10: 页面自身包装的 setInterval 冲突

| 项目 | 描述 |
|------|------|
| **检测原理** | 51job 的 Webpack bundle **本身已经包装了 setInterval/setTimeout**（用于 arguments→array polyfill）。这意味着 `window.setInterval` 在页面加载后已经不是原生函数 |
| **攻击面** | 我们的 hook 替换的是页面版本（非原生），页面可能在 init 时保存了对自己包装版本的引用，后续可检测 `window.setInterval !== savedRef` |
| **v3 对策** | 无法完全避免。但页面自己的包装也是非原生的，同样的检测机制会误伤页面的正常替换。风险评估：低 |
| **实际观察** | ruyipage 中 `setInterval.toString()` 返回 `function(){for(var e=arguments.length,n=new Array(e)...` — 证实页面已覆盖 |

### V11: eval 功能完整性检测

| 项目 | 描述 |
|------|------|
| **检测原理** | `eval('1+1')` 应返回 `2`。如果 hook 破坏了 eval 的作用域或返回值，立即可检测 |
| **攻击面** | eval 的 hook 需要小心处理作用域（直接 eval vs 间接 eval） |
| **v3 对策** | 对不含 debugger 的 code，直接透传给 `_ev.call(this, code)`（保持 this 上下文），行为与原生一致 |

### V12: CSP (Content Security Policy) 绕过检测

| 项目 | 描述 |
|------|------|
| **检测原理** | 页面设置 CSP 禁止 inline script，而 Tampermonkey 脚本是 inline 注入的，如果脚本能执行说明 CSP 被绕过 |
| **攻击面** | Tampermonkey 天然绕过 CSP，这是扩展层面的行为 |
| **v3 对策** | 无法从脚本层面解决。这是 Tampermonkey 架构的固有限制。但实际观察 51job **未设置 CSP**（meta 检查确认无 CSP 头） |

### V13: Object.defineProperty 对 Protection 的二次覆盖

| 项目 | 描述 |
|------|------|
| **检测原理** | 飞林/antidom 可能尝试用 `Object.defineProperty(window, 'setInterval', ...)` 覆盖我们的 hook |
| **攻击面** | 如果页面重置了我们 hook 的属性，debugger 恢复 |
| **v3 对策** | 在 `_si` 中保存原始引用。即使页面覆盖 window.setInterval，也只是覆盖成一个新的 wrapper。但我们的 hook 在 document-start 先执行，飞林的后执行覆盖只会把 setInterval 换成飞林的版本（然后飞林的 debugger 注入仍然被阻断，因为我们 Hook 的是飞林调用 setInterval 的路径... 等等，不完全对） |
| **实际分析** | 如果飞林用 `Object.defineProperty(window, 'setInterval', {value: origNative})` 恢复原生，那么后续的 `setInterval(function(){debugger},50)` 会正常执行。但飞林在页面加载时保存的原始引用，在 document-start 时就已经被我们替换了。飞林拿到的 "原始引用" 实际上是我们的 hook。所以飞林恢复的也是我们的 hook（或尝试恢复但失败）。除非飞林通过 iframe 获取真正的原生引用。 |

## 风险矩阵总结

| 向量 | 风险 | v3 状态 | 备注 |
|------|------|---------|------|
| V1 toString 检测 | 高 | 已解决 | toString 伪装 |
| V2 回调执行测试 | 高 | 已解决 | 源码净化 |
| V3 typeof/instanceof | 低 | 正常 | 函数包装器天然兼容 |
| V4 属性描述符 | 中 | 已解决 | 使用 data descriptor |
| V5 iframe 对比 | 中 | 部分缓解 | 页面自身已覆盖 setInterval |
| V6 TM 扩展检测 | 中 | 已缓解 | @grant none |
| V7 静态源码扫描 | 中 | 已解决 | fromCharCode 编码 |
| V8 调用栈泄露 | 低 | 安全 | 闭包不暴露路径 |
| V9 时序分析 | 低 | 极低开销 | 无 debugger 时零开销 |
| V10 页面包装冲突 | 低 | 注意 | 页面自身已包装 |
| V11 eval 完整性 | 低 | 正常 | 透传机制 |
| V12 CSP 绕过 | 低 | 无 CSP | 51job 未设 CSP |
| V13 二次覆盖 | 中 | 有限对抗 | 先到先得优势 |

## v3 脚本核心改进点

### vs v1 (原始版)
| 改进 | v1 | v3 |
|------|-----|-----|
| toString 伪装 | | 返回原生字符串 |
| 回调执行完整性 | 直接拦截 | 源码净化，回调正常执行 |
| 关键词隐藏 | 明文 "debugger" | `String.fromCharCode()` |
| 属性描述符 | 未处理 | data descriptor 匹配原生 |
| 注释暴露 | 大量中文注释 | 无注释 |
| eval 透传 | | 保持 |
| setTimeout | | 同样净化处理 |

### vs v2 (stealth 初版)
| 改进 | v2 | v3 |
|------|-----|-----|
| 回调执行方式 | 直接拦截（与 v1 同）| 源码净化（核心升级）|
| 变量名暴露 | `hasDebugger`, `hookedSetInterval` 等 | `_hasDbg`, `_hsi` 等短名 |
| 关键词隐藏 | 明文 | fromCharCode |
| 字符串编码 | 无 | 正则/关键词全编码 |
| toString 的 descriptor | writable:false 可能被检 | 不特殊标记 toString |
| 自清理 | 定时器残留 | 用完即释放闭包引用 |

## 未完全解决的残留风险

1. **iframe 引用对比** — 如果飞林通过 iframe.contentWindow 获取真正原生 setInterval 并替换 window.setInterval，我们的 hook 会被覆盖。需要额外 hook `HTMLIFrameElement` 的 contentWindow getter。

2. **Chrome DevTools Protocol 检测** — 飞林可能通过 CDP 侧信道检测调试器是否附着。这不是 JS 层面能解决的。

3. **神策行为分析** — 如果我们的访问模式（无鼠标移动、快速翻页等）被神策埋点捕获，可能触发风控降级。这不是 anti-debugger 脚本的范畴。

4. **阿里验证码** — 如果风控把用户标记为可疑，会主动弹出滑块验证码。此时需要 ruyipage 指纹对抗。
