---
schema_version: 2
id: web-reverse-datadome-plv2-plv3-source-archive
document_type: archive
original_date: unknown
archived_date: "2026-10-13"
scope:
  targets: [datadome]
  client: web
  version: "1.33.1"
  observed_at: unknown
sources:
  - id: s1
    ref: null
    basis: source-report
    citation: 本地分析笔记《DataDome 环境检测清单（plv2 + plv3）》
    reason: 原材料为本地分析笔记，未提供可公开定位的链接。
source_completeness: partial
tags: [datadome, plv2, plv3, environment-detection, source-report]
---

# DataDome 环境检测清单（plv2 + plv3）

## 清洗与完整性说明

本地笔记的原始目录路径、浏览器 / GPU / 屏幕 / 字体 / 布局样值、环境哈希与本机栈路径均已脱敏；静态检测字段名、分析步骤、来源对各类接口的解释和不确定性保留。原笔记头部标注的 2026-10-13 是更新日期，不当作观察日期或原始发布日期。没有独立图片或附件。原笔记引用的 `3.js`、VM 常量池、反汇编与字段映射不在本批，故仅为 `partial`，不代表静态提取结论已由本轮复核。

<a id="source-body"></a>
## 来源正文

> 配套：[[DataDome plv2(payload)]]（容器算法）、[[DataDome plv3(内层VM)]]（VM 算法）。
>
> **两条独立的采集线**：
> - **plv2 线**：webpack 模块 516，**明文 JS**，采集结果以 `A("字段名", 值)` 塞进 plv2，共 **228 个字段**
> - **plv3 线**：webpack 模块 872 的**内层字节码 VM**，自己读宿主、自己算，结果进 plv3
>
> 两条线的检测项**大部分不重叠**。plv2 偏"广"（228 个字段铺开全部 API 面），plv3 偏"深"（WebGL/CSS/canvas 三套计算型指纹）。
>
> **本文全部是静态提取的**，所以包含**这一次没执行到的分支**（版本门、UA 门、try/catch 退路）。
> 补环境时要照静态清单补，不能照运行时记录补 —— 曾用 Node 沙箱跑出运行时清单，只有 13 条，
> 因为沙箱走了 fallback 路径，严重不全。

## 一、plv2 线（明文 JS，静态全量）

根对象按条目数：`ddResObj 76 / navigator 62 / document 36 / Object 23 / RegExp 13 / screen 10 / Math 9 / WebAssembly 7 / Array 7 / performance 5 / Intl 5 / speechSynthesis 5 / ddm 4` …（113 个）

### 1.1 navigator（62 条，全量）

**常规指纹**

| 属性 | 次数 | 实测值 |
|---|---|---|
| `navigator.userAgent` | 5 | [来源样值已脱敏] |
| `navigator.platform` | 1 | [来源样值已脱敏] |
| `navigator.vendor` | 1 | [来源样值已脱敏] |
| `navigator.language` | 2 | [来源样值已脱敏] |
| `navigator.hardwareConcurrency` | 7 | [来源样值已脱敏] |
| `navigator.maxTouchPoints` | 9 | [来源样值已脱敏] |
| `navigator.deviceMemory` | 2 | [来源样值已脱敏] |
| `navigator.onLine` | 1 | [来源样值已脱敏] |
| `navigator.pdfViewerEnabled` | 1 | [来源样值已脱敏] |

**浏览器身份 / 自动化检测**（这些属性在正常 Chrome 上**不存在**，存在即可疑）

| 属性 | 检测什么 |
|---|---|
| `navigator.brave` | Brave 浏览器 |
| `navigator.genspark` | **Genspark AI 浏览器** |
| `navigator.buildID` | Firefox 特有 |
| `navigator.oscpu` ×5 + `navigator.oscpu.indexOf("Linux")` | Firefox 特有，并单独判 Linux |
| `navigator.browserLanguage` / `navigator.systemLanguage` / `navigator.userLanguage` | IE 时代属性的存在性 |
| `navigator.cpuPerformance` | 非标准属性 |
| `navigator.ContactsManager` / `navigator.contacts` | 非标准 |
| `navigator.__proto__` ×3 | 原型链是否被动过 |

**插件 / MIME（假对象最容易露馅的地方）**

```text
navigator.plugins                      x3
navigator.plugins.length               x4     实测值已脱敏
navigator.plugins[0]                   x3
navigator.plugins[0].name              x2
navigator.plugins[0].length            x1
navigator.plugins[0][0].enabledPlugin.name   x1    ← 深层结构，补环境常漏
navigator.plugins.item(859523698994125)      x1    ← 荒谬大索引，真浏览器返回 null
navigator.mimeTypes / .length / [0] / [?].type
```

实测：`Lcx34k = "PDF Viewer,Chrome PDF Viewer,Chromium PDF Viewer,Microsoft Edge PDF Viewer,WebKit built-in PDF"`、`23xCxY = "application/pdf,text/pdf"`

> `plugins.item(859523698994125)` 是个明显的陷阱：真实 `PluginArray.item()` 对越界索引返回 `null`，
> 用 Proxy 或数组伪造的 plugins 很容易返回非 null 或抛错。

**高熵 / 新 API**

| 调用 | 实测值 |
|---|---|
| `navigator.userAgentData.getHighEntropyValues([6项])` | [来源样值已脱敏] |
| `navigator.gpu.getPreferredCanvasFormat()` | [来源样值已脱敏] |
| `navigator.gpu.requestAdapter()` | [来源样值已脱敏] |
| `navigator.gpu.wgslLanguageFeatures` | [来源样值已脱敏] |
| （GPU features） | [来源样值已脱敏] |
| （GPU limits） | [来源样值已脱敏] |
| `navigator.keyboard.getLayoutMap()` | [来源样值已脱敏] |
| `navigator.mediaDevices.enumerateDevices()` | [来源样值已脱敏] |
| `navigator.connection.{effectiveType,rtt,downlink,saveData}` | [来源样值已脱敏] |
| `navigator.storage.estimate()` | [来源样值已脱敏] |
| `navigator.permissions.query(<var>)` | [来源样值已脱敏] |
| `navigator.getBattery()` | [来源样值已脱敏] |
| `navigator.getGamepads` | [来源样值已脱敏] |

### 1.2 screen（10 条，全量）

```text
screen.width / height               实测 [样值已脱敏]
screen.availWidth / availHeight     实测 [样值已脱敏]
screen.availLeft / availTop
screen.colorDepth / pixelDepth      实测 [样值已脱敏]
screen.orientation.type             实测 [样值已脱敏]
screen.msOrientation                ← IE 特有，存在性检测
```

相关字段实测样值已脱敏；字段含义须回到源码表达式反查，不能按数值猜测。

> 教训：字段含义必须回 `3.js` 反查表达式，**不能按值猜**。`qzJ7rH` 的值 1536 看着就是 `screen.width`，实际不是。

### 1.3 document（36 条，全量）

**创建的标签（7 种）**

```text
document.createElement("div")      x7      ← CSS 布局指纹的载体
document.createElement("span")     x3
document.createElement("canvas")   x1      ← canvas 指纹
document.createElement("video")    x1      ← canPlayType 探测
document.createElement("audio")    x1      ← canPlayType 探测
document.createElement("iframe")   x1      ← 取干净的原生函数 / 环境对比
document.createElement("style")    x1      ← 注入 CSS 变量
document.createEvent("CustomEvent")
```

**查询 / 结构**

```text
document.querySelector("browserflow-container")   ← BrowserFlow 自动化工具检测
document.getElementsByClassName("dd-2edEfe")      ← 自己的元素
document.getElementsByClassName("".concat(l))
document.getElementById / getElementsByTagName / querySelectorAll
document.documentElement.clientWidth / clientHeight
document.body.appendChild x5 / removeChild x4
document.head.appendChild x2 / removeChild x2
document.documentElement.appendChild
document.evaluate            ← XPath 能力
document.fonts               ← 字体 API
document.hasFocus()
document.[?].cache_ x2       ← 计算属性，疑似探测注入痕迹
document.[?].window
```

**其他**

```text
document.cookie x2
document.cookie.indexOf("dd_testcookie")   ← cookie 可写性测试
document.addEventListener / removeEventListener
```

### 1.4 自动化 / devtools 专项

| 检测 | 机制 |
|---|---|
| `Firebug.chrome.isInitialized` | Firebug devtools |
| `external.toString()` | IE/自动化框架痕迹 |
| `document.querySelector("browserflow-container")` | BrowserFlow |
| `navigator.webdriver` | 标准 webdriver 标志（也进 plv3） |
| `window.chrome` → `WFb4Rb = ",loadTimes,csi,app"` | Chrome 对象的属性组成 |
| `PermissionStatus.prototype.hasOwnProperty("name")` | 原型完整性 |
| `HTMLVideoElement.prototype.getVideoPlaybackQuality` | 存在性 |
| `Reflect.construct(Boolean, [], <fn>)` | Proxy / 代理对象探测技巧 |
| `Error.stack` → `snqI85` / `FrYHVI`（切成两段）+ `O0XhI5`（base64） | **调用栈**，实测含脚本 URL 与行列号 |

### 1.5 栈帧与调用方检测（反自动化核心）

这是 plv2 侧最关键的一块，而且**不是独立跑的** —— 它被包装进 6 个 DOM 查询方法，
每次有人查 DOM 就抓一次调用栈，看**是谁在调**。

**取栈（`Xg`，3.js 第 83 行）**

```js
function Xg() {
  var A;
  if (37 === X.Function.toString().length) {          // ← 门
    var g = X.Error.stackTraceLimit,
        B = X.Error.prepareStackTrace;
    X.Error.stackTraceLimit = 1 / 0;                   // 要全部栈帧，不止默认 10 层
    X.Error.prepareStackTrace = function (C, Q) {
      X.Error.stackTraceLimit = g;                     // 进来立刻恢复
      X.Error.prepareStackTrace = B;
      A = Q;                                           // ← 留下 CallSite 对象数组
      for (var D = C.toString(), c = 0; c < Q.length; ++c) D += "\n", D += "at " + Q[c].toString();
      return D;
    };
  } else 11, 12;                                       // 门不过就什么都不做
  var Q = new X.Error().stack;
  var o = {}; return o.s = Q, o.A = A, o;               // s = 栈字符串, A = CallSite 数组
}
```

`"function Function() { [native code] }"` 正好 **37** 个字符。**`Function.toString` 一旦被改，
长度就不是 37，整段栈检测直接跳过** —— 这是用原生函数的字符串长度当自检开关。

另一处还检查 `prepareStackTrace` 是不是**自有属性**，并在用完后精确还原：

```js
o = X.Object.prototype.hasOwnProperty.call(c, "prepareStackTrace"),
w = c.prepareStackTrace,
...
!o || <不透明谓词> ? delete c.prepareStackTrace : c.prepareStackTrace = w;
```

原本没有就 `delete`，原本有就写回原值 —— **不留痕迹**。

> **这正是 verify.js 栽过的坑**：当时为了让沙箱栈可复现，把 `Error.prepareStackTrace` 设成
> `writable:false, configurable:false`。但 DataDome 要**临时替换再还原**它，设成不可写会让替换失败；
> 而 `hasOwnProperty(Error, "prepareStackTrace")` 这一项还会直接发现这个属性是注入的
> （正常的 `Error` 没有自有的 `prepareStackTrace`）。

**栈帧正则匹配（3.js 第 2164-2168 行定义，2201-2216 行使用）**

```js
var B = true,                                              // 总开关
    Q = 50,                                                // 配额：最多检测 50 次
    D = new X.RegExp("pptr:|ElementHandle|evaluateHandle"), // ← Puppeteer
    c = new X.RegExp("eval\sat\sevaluate"),               // ← Puppeteer / Playwright 的 evaluate
    o = new X.RegExp("eval\sat\sexecuteScript");          // ← Selenium 的 executeScript
```

逐行扫栈，命中就塞字段**并派发检测事件**：

```js
for (var X = w.split("\n"), M = 0; M < X.length; M++) {
  if (D.test(X[M])) { g("6n2xuo", true); Kg("datadome-det-a"); break; }   // Puppeteer
  if (c.test(X[M])) { g("4yIRue", true); Kg("datadome-det-a"); break; }   // evaluate
  if (o.test(X[M])) { g("FnV3Th", true); Kg("datadome-det-a"); break; }   // executeScript
}
```

`Kg(A, g)` = `X.dispatchEvent(new X.CustomEvent(A, { detail: g }))` —— 内部检测信号总线。
全脚本共 `datadome-det-a` ×8、`datadome-det-d` ×1 个派发点。

**调用方源码检测（比栈匹配更狠）**

```js
var I = arguments.callee.caller.toString();        // ← 直接拿调用者的源码
// 白名单：这几类调用方不算可疑
0 != I.indexOf("function (){var _0x") && 0 != I.indexOf("function(){var _0x") || (C = true);  // OB 混淆代码
I.indexOf("var contactSupportComment") > -1 && I.indexOf("var humanCommentEl") > -1 && (C = true);
(I.indexOf("showForm(formWrapperId)") > -1 || I.indexOf("submitContactForm(contactFormId") > -1) && (C = true);
(I.indexOf("#iadvize-container") > -1 || I.indexOf("useForcedLinkTracking") > -1 || I.indexOf("dot-optimeeze") > -1) && (C = true);   // iAdvize 客服等
I.indexOf('"iframe_api"') > -1 && I.indexOf('"player_api"') > -1 && (C = true);   // YouTube 嵌入
I.indexOf("ga-disable-") > -1 && (C = true);                                      // Google Analytics
C || g("nsLSwZ", ZA(I.substring(0, 150)));         // ← 不在白名单 → 上报调用者源码前 150 字符(base64)
I.indexOf("on(selector, wit") > -1 && g("ekHdhg", true);
```

实测 `nsLSwZ` base64 解出来是：

```text
function(A,g,B,D){var o=X[I(0)](E(2096)),w=X[I(0)](E(Q(1866,231))),O=X[E(1)][I(1)](E(2098)),…
```

—— DataDome 自己的模块代码（`X[I(0)]` 这种混淆风格）。自己调自己也会被记一笔。

> `arguments.callee.caller` 在严格模式下会抛 `TypeError`，所以这段代码**不能在严格模式下运行**。
> 反混淆时若给产物加上 `"use strict"`，这段会走进 catch 并把 `C` 置 true（当成白名单放过），
> 检测结果就变了。

**挂载点与双层原生性校验**

```js
function w(A) {
  return "function" == typeof A
      && <不透明谓词>
      && A.toString().match(/\{\s*\[native code\]\s*\}$/m)            // 原函数要原生
      && A.toString.toString().match(/\{\s*\[native code\]\s*\}$/m)   // 连 toString 本身也要原生
    ? function () { if (Q <= 0 || !B) return A.apply(this, arguments); Q--; /* 检测 */ }
    : A;                                                              // 非原生就不包装
}

X.document.getElementById       = w(X.document.getElementById);
X.document.getElementsByTagName = w(X.document.getElementsByTagName);
X.document.querySelector        = w(X.document.querySelector);
X.document.querySelectorAll     = w(X.document.querySelectorAll);
X.document.evaluate             = w(X.document.evaluate);
X.XMLSerializer.prototype.serializeToString = w(X.XMLSerializer.prototype.serializeToString);
X.setTimeout(function () { B = false; }, 30000);                      // 30 秒后停止检测
```

**所以这 6 个方法在页面上本来就是非原生的 —— 那是 DataDome 自己包的，不是环境被污染。**
我曾把 `getElementById` / `querySelector` / `serializeToString` 的非原生当成 Cloak 浏览器留下的痕迹，
查到这里才确认是误判。**要判断某个方法是否被第三方动过，必须在目标脚本加载之前取基准。**

**CallSite.getScriptHash（遗留检测）**

```js
function Pg(A) {
  if (A) {
    for (var g = [], B = 0; B < A.length; B++) {
      var C = A[B].getScriptHash();                     // ← V8 CallSite 的非标准方法
      0 != B && g[g.length - 1] == C || g.push(C);      // 相邻去重
    }
    var Q = "";
    return g.length > 0 && (Q = g.join()).length > 500 && (Q = Q.slice(0, 500) + "..."), Q;
  }
}
```

`getScriptHash()` 返回**脚本内容的哈希**，用来发现脚本被替换或改写 —— 对 Reqable 替换、
`replace_script` 这类手段是直接威胁。但它在现代 V8 上已经移除：实测 228 个字段里
**没有** `7WDJKi` 和 `Wk25D2`（两处 `Pg` 结果的去向），说明 `getScriptHash` 调用抛错被 catch 吃掉了。
**本版本上这是个失效的遗留检测**，但换浏览器/换版本要重新确认。

**栈相关字段去向**

| 字段 | 内容 | 实测 |
|---|---|---|
| `GMhVWT` | `zg(栈字符串)`，djb2 变体哈希（`+2147483647+1` 转无符号） | [来源样值已脱敏] |
| `C6GQ31` | 另一处的栈哈希 | [来源样值已脱敏] |
| `snqI85` | 栈字符串**头 150** 字符（`B.slice(0,150)`，原文不编码） | [来源样值已脱敏] |
| `FrYHVI` | 栈字符串**尾 150** 字符（`B.slice(-150)`） | [来源样值已脱敏] |
| `O0XhI5` | 栈尾 150 字符的 base64（`ZA(w.substring(w.length-150))`） | [来源样值已脱敏] |
| `nsLSwZ` | **调用者源码**前 150 字符的 base64 | [来源样值已脱敏] |
| `6n2xuo` | 栈里命中 `pptr: | [来源样值已脱敏] | evaluateHandle` | 未命中（不在字段里） |
| `4yIRue` | 栈里命中 `eval at evaluate` | [来源样值已脱敏] |
| `FnV3Th` | 栈里命中 `eval at executeScript` | [来源样值已脱敏] |
| `ekHdhg` | 调用者源码含 `on(selector, wit` | [来源样值已脱敏] |
| `7WDJKi` / `Wk25D2` | `getScriptHash` 列表 | [来源样值已脱敏] |

**栈里会暴露脚本 URL 和行列号**：实测 `[本机 file:// 栈路径已脱敏]`。
真机上这里是 `https://ct.captcha-delivery.com/interstitial.1.33.1.202610091.js`，
**用本地文件重放时这一项必然和真机不同**（而且 `GMhVWT`/`C6GQ31` 的哈希也随之不同），
做真机对拍时要把这几个字段排除或单独处理。

### 1.6 原生性检测（函数有没有被改过）

**检测正则**：

```js
new RegExp("\\{\\s*\\[native code\\]\\s*\\}$", "m")
```

**被检测的函数**（`BtMCwr` 这一项）：

```js
[[Math, "random"], [console, "debug"], [String.prototype, "toString"],
 [Object, "defineProperty"], [String.prototype, "indexOf"], [String.prototype, "split"]]
```

本次实测 **`BtMCwr = "random"`** —— 它在报告「`Math.random` 被改过」。这正是本地重放页为了可复现而钉死的那一项，**反过来证明这个检测是有效的**。真机补环境时这一项必须是干净的 `[native code]`。

其他原生性相关：

```text
Function.prototype.toString / Function.toString()
XMLSerializer.prototype.serializeToString   x3
XMLDocument.toString()
Object.getOwnPropertyDescriptor(window, …)
```

> `XMLSerializer.prototype.serializeToString` 这一项我曾误判成 Cloak 浏览器留下的痕迹，
> 实际是 **DataDome 自己的检测代码**。判断某个方法"看起来非原生"之前，先确认它不是被检测方自己包过的。

### 1.7 媒体能力（canPlayType 矩阵）

`video` / `audio` 元素各跑一轮 `canPlayType`，实测结果铺开成大量 `"probably"` / `"maybe"` / `""` 字段：

```text
[来源中的 canPlayType 样值矩阵已脱敏]
```

### 1.8 其他 Web API

```text
AudioContext              → hlxJ26 / rYAYkN = [AudioContext 样值已脱敏]
speechSynthesis.getVoices() + addEventListener("voiceschanged") + onvoiceschanged
Intl.DateTimeFormat().resolvedOptions()     → VxMTuL = "[timezone 样值已脱敏]"
Intl.DisplayNames                           存在性
matchMedia("(display-mode: fullscreen)")
  → ILXrYI = "[media-query 样值已脱敏]"（any-pointer / any-hover）
  → ZWoIon = "[media-query 样值已脱敏]"（color-gamut / dynamic-range / display-mode）
CSS.supports(<expr>, <expr>)
getComputedStyle(<var>) x6 + getComputedStyle(<expr>)
  → n7fMWH = "[system-font 样值已脱敏]"   ← 系统字体
performance.getEntriesByType("navigation") / ("visibility-state")  → sTZzFo = "navigation"
performance.memory  → 6TiXFU / cGx97L / rYMkhS = [performance.memory 样值已脱敏]（本次为钉死值）
new Worker(<var>, {name}) + new Blob([1项],{endings}) + URL.createObjectURL/revokeObjectURL
new TextDecoder("utf-8", {ignoreBOM, fatal})
new Uint32Array([4项]) / new DataView(<var>, g>>>0, B>>>0)
setTimeout(<fn>, 200/500/30000/60000)
```

### 1.9 WebAssembly 能力门（重要）

```js
new WebAssembly.Module(X.Uint8Array.of(0, 97, 115, 109, 1, 0, 0, 0))   // wasm 魔数 "\0asm\1\0\0\0"
WebAssembly.instantiate(<var>, <var>)
new WebAssembly.Instance(<var>, <var>)
new WebAssembly.Module(<var>)
```

**这就是让 Node 沙箱走 fallback 的那道门**。配合 UA 版本门：

```js
K = UA.match(/Chrome\/(\d+)\./) || UA.match(/Chromium\/(\d+)\./);
if (K && K.length > 1) { if (parseInt(K[1], 10) < 115) R = false; }
if (R || 不透明谓词) { 同步 new WebAssembly.Module(y) … } else { WebAssembly.instantiate(y, l).then(…) }
```

探测不过就把字段写成错误码（`iVbNWw` / `2hoNGj` 会是 `-2`/`-3`/`-4`/`-5`），**不报错不中断**，所以很容易以为"没有 wasm"。

wasm 两个导出的输出就在 plv2 里：

```text
iVbNWw = [样值已脱敏]    ← wasm NnFVnu(externref) → i32（环境哈希交叉校验）
2hoNGj = [样值已脱敏]             ← wasm AiEzPp() → i32（CPU 浮点指纹：sign_bit(Infinity - Infinity)，x86=1 / ARM=0）
N3IfnA = [样值已脱敏]             ← wasm 耗时 performance.now() - P
```

### 1.10 计算型指纹（plv2 侧）

| 字段 | 实测值 | 机制 |
|---|---|---|
| `qcPlAt` | [来源样值已脱敏] | canvas `getImageData` 像素 |
| `LipKc6` | [来源样值已脱敏] | 16 个浮点，矩阵/三角运算指纹 |
| `9VBA3h` | [来源样值已脱敏] | 同一测量重复 9 次（稳定性探测） |
| `FWQAn1` | [来源样值已脱敏] | CSS 布局测量 |
| `CX1B58`/`QJvkNC`/`X1A1Qx`/`7R8AbM` | [来源样值已脱敏] | 浮点精度指纹 |
| `Qtx2X9` | [来源样值已脱敏] | 浮点运算（`1-1/e` 量级） |
| `j0h3mb` / `YV2x0R` | [来源样值已脱敏] | WebGL UNMASKED_VENDOR/RENDERER |
| `t9O4Pm` | [来源样值已脱敏] | 聚合指纹哈希 |
| `r36Xgy` | [来源样值已脱敏] | `ddm.userEnv` 拼 `_160_28_16` |

### 1.11 自己的参数与自校验

```text
ddm.userEnv x13 / ddm.hash / ddm.hash.slice(-4) / ddm.seed
CGQy0z = "1.33.1"            脚本版本
JFG8bU = "invisible"         this.fastMode ? "invisible" : "display"
dVHv1I = [VM instruction count sample redacted]              ← 内层 VM 执行的指令数（plv3 的旁证）
miJaLM                        ← VM 的 MEM[-1]
VzpBS3 = "[self-check output redacted]"        ← 函数源码自校验 hc(O.toString()+C.toString()+D.toString()+I.toString())
oEnISB = 1                   ← 自增序号
CZgBws = "[environment value redacted]"      ← window._hsv 有值时追加（默认 33）
nsLSwZ                        ← 某函数 toString 的 base64（前 512 字符）
Q25c1e                        ← g.toString().slice(0, 512)（wasm 失败分支里上报）
```

> `VzpBS3` 对反混淆是硬约束：它把四个函数的源码拼起来做哈希。
> 格式化会改 `toString()` 的结果，所以反混淆产物**必须真机验证**服务端是否接受。

## 二、plv3 线（内层 VM，258 条常量池）

VM 的字符串常量是加密存储、**就地解密**的（不走统一索引），解密公式：

```text
常量[i] = 密文[i] ^ ((S[i mod 8] ^ KEY) ^ (i+1))
S   = [32, 42, 69, 126, 66, 244, 64, 136]     ← 周期 8 的固定表
KEY = 每个字符串自己的密钥（存在字节码里）
```

258 条常量池就是 VM 侧的**完整**检测面（天然覆盖所有分支）。

### 2.1 读取的宿主对象与属性

```text
全局:    window, document, navigator, performance, crypto, location, Math, Date,
         Uint8Array, Float32Array, Array, Object, Number, String, RegExp, Proxy, console, Buffer
navigator: hardwareConcurrency, maxTouchPoints, webdriver
窗口:    outerWidth, outerHeight, devicePixelRatio
时间/性能: now, memory, usedJSHeapSize, timing, loadEventEnd, navigationStart,
          timeline, currentTime, lastModified, getTimezoneOffset
crypto:  getRandomValues, randomUUID
location: pathname
其他:    isSecureContext, atob, btoa, replace, fromCharCode, charCodeAt, indexOf,
         imul, join, push, splice, prototype, length, ownKeys, setPrototypeOf, toString
自己:    ddm, userEnv
类型判定: object, bigint, string, number, boolean, Infinity, true, false
```

### 2.2 WebGL 指纹（GPU 浮点运算）

完整的 fragment shader（常量池索引 199）：

```glsl
precision highp float;
uniform float i6, sj, qx, ck, h8;
void main(){
  float s6 = sj;
  float dq = min(sj, ck);
  mat2 en = mat2(1., 0., 1., 0.);
  vec2 jx = en * vec2(ck, s6);
  float dc = jx.x;
  mat2 l8 = mat2(1., 0., 1., 0.);
  vec2 lt = l8 * vec2(sj, dc);
  float v0 = lt.x;
  float r = v0;
  gl_FragColor = vec4(mod(r, 256.)/255.,
                      mod(floor(r/256.), 256.)/255.,
                      mod(floor(r/65536.), 256.)/255.,
                      floor(r/16777216.)/255.);
}
```

vertex shader：

```glsl
attribute vec2 p; void main(){ gl_Position = vec4(p, 0, 1); }
```

**机制**：把 5 个 uniform（`i6`/`sj`/`qx`/`ck`/`h8`）喂进去，在 GPU 上做 `mat2` 乘法和 `min`，
把 32 位结果**编码进 RGBA 四个通道**，再用 `readPixels` 读回来 —— 得到的是**这块 GPU 的浮点运算结果**，
驱动/架构不同结果就不同，而且无法用 JS 伪造。

用到的 WebGL API（全部来自常量池）：

```text
webgl, createShader, VERTEX_SHADER, FRAGMENT_SHADER, shaderSource, compileShader,
createProgram, attachShader, linkProgram, useProgram,
createBuffer, ARRAY_BUFFER, bindBuffer, bufferData, STATIC_DRAW, Float32Array,
getAttribLocation, enableVertexAttribArray, vertexAttribPointer, FLOAT,
getUniformLocation, uniform1f, drawArrays, TRIANGLES,
readPixels, RGBA, UNSIGNED_BYTE
```

### 2.3 CSS 布局引擎指纹（最独特的一项）

**机制**：注入一段带 CSS 自定义属性的 style，用 `calc()` / `max()` / `clamp()` 嵌套做运算，
再用 `offsetWidth` / `clientWidth` / `getBBox` **读回浏览器算出来的值**。
这是在用 CSS 布局引擎当计算器 —— 不同引擎/版本的舍入与单位处理有差异。

注入的 CSS（常量池拼接而成）：

```html
<style>#c5>div>div>div>div>div{--b7:calc(var(--mn) * 3)}.kw{--mn:calc(var(--fy) + 105px)}</style>
<div style="--q1:<N>px;--op:23px;--dv:152px">
  <div class="kw">
    <div>
      <div id="pu" style="display:inline-block;width:var(--b7)"></div>
    </div>
  </div>
</div>
```

涉及的自定义属性与函数：

```text
--b7  --mn  --fy  --q1  --kp  --j3  --uu  --ej  --ni  --bo  --zg  --op  --dv
calc(   max(var(--q1), 39px)   clamp(var(--j3), var(--kp), var(--j3))
position:absolute;left:-9999px;--ni:90px;--bo:172px;--zg:79px
position:absolute;left:-9999px;--j3:<N>px
#dm>div>div>div:first-of-type{display:inline-block;padding:var(--ej)}
<div style="display:inline-block;padding:6px">
<div style="display:inline-block;max-width:var(--ej)">
<div style="width:var(--uu)"></div>
```

读回用的属性：`offsetWidth`、`clientWidth`、`paddingLeft`、`boxSizing`（`content-box`）、
`visibility`、`position`（`absolute`）、`left`（`-9999px`）、`17px`、`29px`、`style`、`cssText`、`innerHTML`

实测过程中捕获到的真实中间值：`'position:absolute;left:-9999px;--j3:[layout sample redacted]'`（CSS 算出 143）、`'[object SVGPoint][layout sample redacted]'`、`'[object HTMLCanvasElement][layout sample redacted]'`

### 2.4 canvas 2D / SVG 指纹

```text
canvas, createElement, getContext, "2d", willReadFrequently,
fillStyle, fillRect, rect, beginPath, arc, fill, lineWidth,
globalCompositeOperation, "difference", getImageData, data, round,
"rgb(", "rgb(0,", "rgb(0,0,", "rgb(0,0,0)"

createElementNS, "http://www.w3.org/2000/svg", "svg",
isPointInFill, createSVGPoint, getBBox, setAttribute, width
```

实测中间值：`'[canvas color sample redacted]'`、`'[canvas color sample redacted]'`、`'[canvas color sample redacted]'`、`'[canvas color sample redacted]'`

**`isPointInFill` + `createSVGPoint`** 是在用 SVG 的几何命中测试做指纹 —— 判断某个点是否落在填充区内，结果取决于路径光栅化的实现细节。

### 2.5 自动化 / 环境伪造检测（VM 侧）

| 常量 | 检测什么 |
|---|---|
| `webdriver` | 标准 webdriver 标志 |
| `_userAgent`、`_resourceLoader`、`_virtualConsole` | **jsdom 的内部属性**（三个一起出现，几乎是 jsdom 的签名） |
| `Proxy`、`setPrototypeOf`、`ownKeys` | Proxy 包装 / 原型篡改 |
| `Buffer` | Node 环境 |
| `[native code]` + `toString` | 函数原生性 |
| `console` + `groupEnd` | devtools |
| `isSecureContext` | 上下文安全性 |
| `hidden` | 页面可见性 |
| `_virtualConsole` | jsdom 控制台 |

### 2.6 VM 对时间的使用（可复现性的关键）

```text
Date, now, lastModified, timeline.currentTime,
performance.now, performance.memory.usedJSHeapSize,
performance.timing.{navigationStart, loadEventEnd},
getTimezoneOffset, crypto.getRandomValues, crypto.randomUUID, Math.random
```

要让 plv3 可复现，这些**必须返回常量**，不能是递增或累积序列：

- `performance.now` 递增 → 耗时字段算的是两次调用之差，调用次数一变差值就变
- `Math.random` 用定种 LCG → 种子随调用次数累积，**同一页面连续触发两次就不同**

## 三、两条线的交叉与差异

| 检测项 | plv2 | plv3 | 说明 |
|---|---|---|---|
| `navigator.hardwareConcurrency` | ✅ `701v6m=[样值已脱敏]` | ✅ | 两条线都采 |
| `navigator.maxTouchPoints` | ✅ | ✅ | 两条线都采 |
| `navigator.deviceMemory` | ✅ `1fJBob=[样值已脱敏]` | ❌ | **只进 plv2**（差分验证：改它 plv3 零差异） |
| `navigator.webdriver` | ✅ | ✅ | — |
| `outerWidth` / `outerHeight` | ✅ | ✅ | — |
| `devicePixelRatio` | ✅ `ztc3Tb=[样值已脱敏]` | ✅ | — |
| `ddm.userEnv` | ✅ ×13 | ✅ | — |
| WebGL shader 运算 | ❌ | ✅ | plv3 独有 |
| CSS 布局引擎运算 | ❌（只有 getComputedStyle 取字体） | ✅ | plv3 独有 |
| SVG `isPointInFill` | ❌ | ✅ | plv3 独有 |
| wasm 两个导出 | ✅（`iVbNWw`/`2hoNGj`） | ❌ | **只进 plv2** |
| `navigator.plugins` / `mimeTypes` | ✅ | ❌ | plv2 独有 |
| `userAgentData.getHighEntropyValues` | ✅ | ❌ | plv2 独有 |
| `canPlayType` 矩阵 | ✅ | ❌ | plv2 独有 |
| `speechSynthesis` / `AudioContext` | ✅ | ❌ | plv2 独有 |
| jsdom 内部属性 | ❌ | ✅ | plv3 独有 |
| `Firebug` / `external` / `browserflow-container` | ✅ | ❌ | plv2 独有 |
| **栈帧 / 调用方检测** | ✅ | ❌ | **plv2 独有**。VM 的 258 条常量池里没有 `stack` / `prepareStackTrace` / `stackTraceLimit`，plv3 不做栈检测 |

## 四、补环境优先级

**必须真实（伪造即被识别）**

1. `BtMCwr` 那 6 个函数的原生性：`Math.random`、`console.debug`、`String.prototype.{toString,indexOf,split}`、`Object.defineProperty` —— 本次实测该字段值就是 `"random"`，直接点名
2. wasm 能跑：`new WebAssembly.Module(Uint8Array.of(0,97,115,109,1,0,0,0))` 必须成功，否则 `iVbNWw`/`2hoNGj` 变错误码
3. WebGL 真实渲染（shader 结果 readPixels）
4. CSS 布局引擎真实计算（`calc`/`max`/`clamp` 嵌套 + `offsetWidth` 读回）
5. `navigator.plugins` 的深层结构，特别是 `plugins.item(超大索引)` 返回 `null`
6. **栈帧相关（见 §1.5，最容易翻车的一块）**：
   - `Function.toString().length` 必须是 **37**（否则整段栈检测被跳过，行为与真机不一致）
   - `Error.prepareStackTrace` 必须**可写可配置**，且不能是 `Error` 的自有属性
     （DataDome 要临时替换再精确还原；设成 `writable:false` 会让它替换失败，
     而 `hasOwnProperty(Error,"prepareStackTrace")` 会直接发现注入）
   - `Error.stackTraceLimit` 必须可写（会被设成 `Infinity` 再还原）
   - 栈里不能出现 `pptr:` / `ElementHandle` / `evaluateHandle` / `eval at evaluate` / `eval at executeScript`
   - 代码**不能在严格模式**下跑：检测用 `arguments.callee.caller`，严格模式抛错会让结果变成"白名单放过"
   - `Error.stack` 的格式与脚本 URL：本地 `file://` 重放时 `snqI85`/`FrYHVI`/`O0XhI5`/`GMhVWT`/`C6GQ31`
     必然与真机不同，真机对拍要排除这 5 个字段

**不能存在**

```text
navigator.webdriver(true) / navigator.brave / navigator.genspark / navigator.oscpu / navigator.buildID
window.Buffer / Firebug / external 异常 / document.querySelector("browserflow-container") 命中
jsdom 的 _userAgent / _resourceLoader / _virtualConsole
```

**UA 一致性**：`navigator.userAgent` 里的 Chrome 版本要 ≥115（否则走 wasm fallback），
并且必须与 `userAgentData.getHighEntropyValues` 的 `uaFullVersion`、`platformVersion` 对得上。
> 这正是 Cloak 浏览器被识破的原因：`--fingerprint` 参数会**丢掉 `navigator.userAgentData` 和 `navigator.deviceMemory`**，
> 而 UA 自称 Chrome 142 —— 声称是 Chrome 90+ 却没有 90+ 的强制 API，一测就穿。去掉该参数后 [来源目标站点已脱敏] 正常通过。

## 五、取材方式（为什么是静态的）

```text
plv2 侧:  tools/i1_js_env.js      AST 扫 3.js，提取 X(=window) 打头的最长成员链 + 调用实参
                                   → out/plv2_env_static.json（266 链 + 152 调用 / 113 根对象）
          tools/h8_plv2dec.py     解密 plv2 → 228 个字段的真实取值
                                   → plv2_fields.json
          tools/h9_fieldmap.py    228 个字段名逐个对回 3.js 里的采集表达式（228/228 命中）
                                   → out/plv2_fieldmap.md
plv3 侧:  VM 常量池 258 条（就地解密，解密公式见 §2）
          out/01.disasm.mine.txt  57227 条反汇编，每行带 handler 语义注释
```

**静态提取才能覆盖未执行分支**。对照一下：同一份脚本，用 Node 沙箱跑出来的运行时清单只有
13 条属性 + 26 条成员（`out/env_touch.json` / `env_members.json`）—— 因为沙箱没过 wasm 探测，
走了 fallback，整条 wasm 线和大半检测都没碰到。**沙箱跑不完时，沙箱的结论一律不可信。**

## 复用边界

来源笔记报告其针对 DataDome interstitial 1.33.1 做了两条静态提取；未提供原始脚本、输入 hash 或底层分析产物。本轮没有运行脚本、访问目标、做 runtime parity 或服务端验收。所有作者结论均保持 `source-report`；脱敏值不应用来复现原环境。
