# Cloudflare 5s v2：/fo 与 form.submit 补环境

> 来源: Firefox 151 ruyitrace 整理（早期两次 `/fo` 基线 + 近期四份成功样本）
> 原始日期: 2026-07
> 归档日期: 2026-09-26
> 分类: web-reverse
>
> Cloudflare managed challenge（`cFPWv=g`，`cType=managed`）的补环境边界：Python 是唯一真实 HTTP 层，Node 执行本轮 fresh orchestrate，自然生成 `/fo` body，并在主站 accepted 响应回灌后自己创建 form 与 3 个 hidden。`cf_clearance` 和 `location.reload()` 都不是完成。样本业务页是 `cn.airbusan.com` 的航班查询 POST；字段值、三元组和 onload 名每轮变化，下文只保留形态。

## 完成门

完整成功只有一条：

```text
业务 GET
-> 403 challenge HTML（_cf_chl_opt）
-> 本轮 orchestrate JS
-> Node 自然发出每一次 /fo
-> Python 真实发送，并把完整 response envelope 回灌给 XHR
-> 主站 accepted：text/html，约 3440 字节，Set-Cookie: cf_clearance
-> orchestrate 自己 createElement(form/input) 并 HTMLFormElement.submit()
-> Python 用同一会话 POST 原业务 URL
-> 业务 200，响应不再是 challenge
```

`cf_clearance` 之后若只看到 `location.reload()`，或带着 cookie 再 GET 仍回到 403，记失败，不继续刷。业务通过后的 JSD（`scripts/jsd/main.js`、`/h/g/jsd/oneshot`，body 约 14.5KB，可能再刷新 `cf_clearance`）是后续检测，不并入 5s 主状态机。

课程材料里的 `flow/ov1` 是另一条版本路径，命中特征见 [cloudflare-5s-challenge.md](./products/cloudflare-5s-challenge.md)。本文只覆盖 `/h/<g|b>/fo/` 这一批 trace。

## Python 与 Node

Python 负责：初始 GET、解析 `_cf_chl_opt`、按 `cFPWv` 选 `/h/g/` 或 `/h/b/`、拉取 fresh orchestrate、会话/TLS/头序/Cookie、接收 Node 的请求记录、真实发送主站与 Turnstile 子请求、分类响应、回灌 XHR、发送最终业务 POST、打状态机日志。

Python 不构造 `/fo` body，不猜 proof 字段，不硬拼 `cf_clearance` 或 3 个 hidden，不用旧 trace body 顶 live body，也不在没有 `form.submit` 时冒充最终 POST。

Node 负责：DOM/BOM 补环境、执行本轮 orchestrate、自然创建 script/iframe/Worker/Blob/XHR/timer/event、自然生成每次 `/fo` body、消费回灌响应并走完 `readystatechange` 2/3/4、`load`、`loadend`，最后输出 `form.submit` 的 urlencoded body 和 telemetry。

Node 不直连目标站，不发最终 POST，不手写业务参数，不屏蔽 debugger Worker，不改 VM 槽、opcode、handler，不用固定 sleep 掩盖 task 顺序。旧补丁库只能按模块迁，迁入前要有 trace 证据、最小 smoke 和指定 trace 回放；整包搬会把请求层和补环境层缠在一起。

## 状态机

```text
S00_INIT
S01_INITIAL_GET
S02_CHALLENGE_403
S03_ORCHESTRATE_LOADED
S04_NODE_STARTED
S05_WAIT_FO_REQUEST
S06_SEND_FO
S07_CLASSIFY_FO_RESPONSE
S08_FEED_FO_RESPONSE_TO_NODE
S09_WAIT_RUNTIME_FINAL_ACTION
S10_FORM_POST_READY
S11_SEND_BUSINESS_POST
S12_BUSINESS_200
```

失败分类：

| 代码 | 含义 |
|---|---|
| `E_INITIAL_NOT_403` | 初始响应不是 challenge HTML |
| `E_ORCHESTRATE_MISSING` | 没有本轮 orchestrate |
| `E_NODE_NO_FO` | orchestrate 没自然打开 `/fo` |
| `E_FO_EB_MANAGED` | 落到 `/eb/managed` 或明显降级短分支 |
| `E_FO_SHORT_RELOAD` | accepted 形态不对，随后只 reload |
| `E_FO_LOOP_403` | 业务 GET 403 → `/fo` → reload → 再 403 |
| `E_RUNTIME_RELOAD_ONLY` | 只有 `location.reload()` |
| `E_RUNTIME_NO_FORM_POST` | 有 cookie，没有 form submit |
| `E_BUSINESS_POST_403` | runtime body 已发出，业务仍是 challenge |
| `E_TIMEOUT` | 超时 |

`cFPWv=g/b` 只决定路径族，不区分无感和点击。`/fo` 也不能按全局第几次判断。分类键是 host、path 三元组、`cRay`、`cH`、Content-Type、是否 `cf_clearance`、Node 是否产出 `form.submit`。

| 响应 | 分类 | 动作 |
|---|---|---|
| `text/plain`，无 `cf_clearance`，大材料 | `FO_CONTINUE` | 回灌，等下一次 `/fo` |
| 主站 `text/html` 约 3440，有 `cf_clearance` 和 `cf-chl-out-s` | `FO_ACCEPTED` | 保存 cookie，回灌，等 form.submit |
| Turnstile 子站 `text/html` 约 6696，无主站 cookie | 子链材料 | 按子 host 回灌，不当主站通过 |
| `/eb/managed` 或明显降级 | `FO_REJECT_OR_DEGRADE` | 停止，不伪造后续 |
| 有 cookie 但 Node 只 reload | `FO_RELOAD_ACCEPTED_BUT_NOT_BUSINESS` | 继续等 form，超时失败 |
| 业务 GET 403 循环 | `LOOP_403` | 停止 |

本批里主站第一次 `/fo` 的 `text/plain` 响应可以是约 113KB（类型 A）或约 774KB（类型 B），都是 `FO_CONTINUE`。失败样本里也出现过约 113KB 的首包，所以不能用 113KB 单独判失败。失败样本的后段是约 3112 字节的 HTML、cookie、`location.reload()`，然后业务 GET 又 403。3440 与 3112 要分开。

请求记录至少带 `source=XMLHttpRequest`、method、url、`cf-chl`、`cf-chl-ra`、`Content-Type: text/plain;charset=UTF-8` 和 body。回灌至少带 status、Content-Type、`cf-chl-out` / `cf-chl-out-s`、Set-Cookie、body、responseURL。大响应要分阶段把 `responseText` 长度推近 trace，不能跳过回调。

主站与 Turnstile 子 `/fo` 会交错。request id 按 host + 三元组 + `cRay` + `cH` + 序号，不要用一个全局 `fo_index`。`GET /h/g/pat/` 返回 401、`brunhild.challenges.cloudflare.com` 的 `/h/g/i/` status 0，是子链探测，不据此判主站失败。

第一阶段只验收闭环：403 → orchestrate → Node 发出 fo1 → Python 发送并回灌 → XHR `loadend` → 进入下一异步动作。这一步过了再迁 Worker、iframe、timer、媒体和 form。

## 两条成功形态

四份近期 trace 的 403 HTML 都是 `cFPWv=g`、`cType=managed`。orchestrate 响应约 226–231KB，每轮变，不能缓存旧脚本。Turnstile `api.js` 这一版响应稳定约 82469 字节。页面上的 Transcend `airgap.js` 不进 `/fo` 状态机。

| 类型 | 样本 | `/fo` 怎么数 | clearance | 最终动作 |
|---|---|---|---|---|
| A | 三份无感成功 | 主站 2 次 + `challenges.cloudflare.com` 子站 2 次，共 4 次 | 主站第 2 次 | 有 `form_submit` 四阶段；未直接命中 `HTMLFormElement.submit()` call |
| B | 一份点击/交互成功 | 只有主站 3 次，没有子 `/fo` | 主站第 3 次 | 直接命中 `HTMLFormElement.submit()` |

类型 A 主站量级：第一次 body 2295，响应约 113.6KB `text/plain`、无 cookie；第二次 body 约 8684–8695，响应 3440 `text/html` + `cf_clearance`。子站第一次 body 约 4.4KB，响应约 822KB `text/plain`；第二次 body 约 84KB，响应 6696 `text/html`、无主站 cookie。

类型 B 主站三次：2295 → 773676 `text/plain`；76364 → 106268 `text/plain`；77772 → 3440 `text/html` + `cf_clearance`。中间还有一次业务 GET 403，说明 runtime reload 没有结束流程。

早期两次 `/fo` 基线（另一批成功 trace）是：fo1 body 约 2284、响应约 416KB `text/plain`；fo2 body 约 77KB、响应约 3440 `text/html` + cookie；业务 POST body 约 2371。它证明 fo1/fo2 是不同阶段，fo2 body 吃的是第一阶段响应加第二阶段采集。它不能当成“第二次一定通过、第三次一定是假值”。

## Turnstile api.js

四份近期 trace 都加载了 `challenges.cloudflare.com/turnstile/v0/g/<rev>/api.js?onload=<cb>&render=explicit`。`api.js` 只说明 Turnstile runtime 在；出现 subdocument 和子 `/fo` 才说明本轮进了 widget 子 challenge。类型 B 只有 `api.js`，没有子 iframe、子 `/fo`、`/pat`、brunhild，不能因此删掉 Turnstile 支持，也不能强行补子链。

orchestrate 动态创建 script，设置 nonce/src/async/defer/onerror/crossorigin 再 append。`api.js` 读 `document.currentScript.src`，用 `URLSearchParams` 解析 onload 与 `render=explicit`，注册 `window` 的 `message`，安装 `window.turnstile`，`setTimeout(0)` 调用 onload 回调。`render=explicit` 表示不靠扫描 `.cf-turnstile` 自动渲染。

`window.turnstile` 上能看到 `ready`、`render`、`execute`、`reset`、`remove`、`getResponse`、`isExpired`。脚本会检查 `"turnstile" in window` 以及 upgrade / already loaded。预置一个假对象会走进 duplicate/upgrade，表现常常是 onload 不进 render、iframe 不创建、accepted 后没有 form.submit，而不是立刻抛异常。

子 iframe 的 `message` 语义包括 `init`、`requestExtraParams`、`complete`、`fail`、`reloadRequest`、`interactiveBegin` / `interactiveEnd`。`requestExtraParams` 会读父页 form、location、resource timing、viewport，再 `postMessage` 回 iframe。`complete` / `fail` 带回 token 与 `cfChlOut` 一类状态。要补的是 script/currentScript/onload 时序、message、iframe `contentWindow` 和 resource timing，不是固定 token，也不是跳过 onload 去调混淆函数。子站 accepted 不等于主站 `cf_clearance`。

## HTML 字段

Python 每轮解析后传给 Node，不拿它们拼 `/fo` body，也不跨轮复用：

| 字段 | 用途 |
|---|---|
| `cFPWv` | `/h/g/` 或 `/h/b/` |
| `cRay` | orchestrate query、`/fo` URL、Worker probe URL |
| `cH` | `/fo` URL、Worker probe URL |
| `cUPMDTk` | 恢复路径，带 `__cf_chl_tk` |
| `cITimeS` | 本轮时间片 |
| `md` | 本批最终 POST 第一个 hidden value，长度 1258 |
| `mdrd` | 本批第二个 hidden value，长度 639；早期另一批是 661 量级 |
| `__cf_chl_tk` | Referer / challenge URL |

`md`、`mdrd`、`cH`、`__cf_chl_tk` 都是 per-run。

## 补环境阶段

没有 trace 对照不补。只有本地报错、没有浏览器同阶段读取，不补。

| 阶段 | 退出条件 |
|---|---|
| 0 输入与状态机 | 403 HTML、`_cf_chl_opt`、orchestrate 进状态机；不预判无感/点击 |
| 1 Window/Document/Location/Navigator | orchestrate 能起跑。Firefox trace 里 `navigator.deviceMemory` 是 missing，不要补成 Chrome 数字；不要硬补 `navigator.userAgentData` |
| 2 script / currentScript | 自然打开第一个主站 XHR `/fo`。不从文档硬拼三元组，不复用旧 `/fo` 前缀 |
| 3 XHR bridge | fo1 `loadend` 后继续跑 |
| 4 Worker/Blob | 类型 B 成功顺序是 trace 内部 id `193 -> 529 -> 142 -> 61 -> 537`。多出的 `80/59` 是 `eval(debugger)` 与过早 `setTimeout`，禁止屏蔽或把返回值钉成 trace |
| 5 iframe/srcdoc | `about:srcdoc` load 后不因 window identity 掉进 `80/59` |
| 6 Event | 合成 `mousedown` 的 `isTrusted=false`；真实 `pointermove` 的 `isTrusted=true` |
| 7 Timer/Promise | task 不被 Node 压成同一条宿主序列。禁止全局把 Promise 改同步或改成 `setTimeout(0)`，禁止用固定 sleep 换通过 |
| 8 Storage/FileSystem/Performance | `navigator.storage.getDirectory` → per-run 文件名 → `createSyncAccessHandle` → write/flush/close，再 `postMessage` 一个计时数。FileSystem 的 promise 不要抢到 Worker `61` 前面 |
| 9 Canvas/OffscreenCanvas/WebGL/WebGPU | `getImageData` 次数和关键尺寸接近 trace；有 WebGPU mapped readback。不要按 `/fo` 字节 diff 反推常量 |
| 10 Media/Font/Audio/RTC | 本批曾见 MediaCapabilities 15 vs trace 18。`FontFace.load` 分批。RTC `close` 前 `iceGatheringState` 仍可能是 `gathering`。不要为了凑调用数去猜 codec 表 |
| 11 Form | `form.submit` 一次，hidden 3 个，name 长度 64 |
| 12 live | 只看状态机分类，不临时 patch |

类型 B 的 Worker 验收不能出现 `193 -> 529 -> 142 -> 80/59 -> 61 -> 537`。`61` 之后 trace 里 FontFace、load、timer、Worker 是分批的，本地容易被压进同一任务序列。

## Worker 与 iframe

Blob 不是网络资源。链路是：orchestrate 拼 wrapper 字符串 → `new Blob` → `createObjectURL` → `blob:https://<page-origin>/<uuid>` → `new Worker` → 主线程 `postMessage` 一段待执行 JS → Worker 里 direct eval → `self.postMessage(result)` → 主线程 listener 写入采集队列 → 下一次 `/fo` body 变大。UUID 每轮变。`createObjectURL` 在四份近期 trace 里都是 4 次。

主线程下发的字符串任务类型稳定，key 名不稳定：navigator/platform、`performance.now` 微计时、`setTimeout` 后再 `postMessage`、以及直接的字符串任务。早期基线里还有 fetch probe，失败对象 `TypeError: NetworkError when attempting to fetch resource.` 本身就是有效采集，不能当成异常分支丢掉。

Worker 侧 `MessageEvent` 不能用 `{ data: codeString }` 代替。要有 `isTrusted`、空字符串 origin、非 WindowProxy 的 `source`、`ports`，以及 Trusted Types 的 `createPolicy().createScript`。`terminate` 之后不再投递已取消任务。Worker realm 的 UA、`languages` 与请求 `Accept-Language` 对齐。

iframe 与 Worker 交错，不是两条无关旁路。要补 `contentWindow`（WindowProxy）、`contentDocument.defaultView` 指回该 window、`frameElement` 指回 iframe、`top/parent/self/frames`、srcdoc 的副作用和 `about:srcdoc` load、`removeChild` 之后仍被持有的引用。srcdoc 不是 Python 要去请求的 URL。

计数只作趋势：类型 B 大约 7 次 create iframe、contentWindow/contentDocument 有读取、srcdoc 与 remove 都出现；类型 A 因为还有 Turnstile 子文档，create iframe 大约 11 次。iframe 外观错时通常不是抛 `iframe error`，而是多一个 debugger Worker、第二阶段 body 量级不对、或只 reload。

## 行为事件

类型 B 要拆成三件事，不能写成“点了按钮所以生成 3 hidden”。

1. orchestrate 初始化就在 document 上挂 `pointermove` / `mousemove`。轨迹不是提交前临时采集。
2. 合成检测：创建 div，对自定义事件名 `x` 做 capture/bubble `addEventListener` 再 `removeEventListener`，`dispatchEvent(new Event("x"))` 返回 true，`isTrusted=false`。随后有 `input[type=range]` 的合成 `mousedown`，`buttons=1`，`isTrusted=false`。不要把这次 `isTrusted` 改成 true。
3. 浏览器派发的真实 `pointermove`：`isTrusted=true`，`phase=3`，冒泡到 Document，listener 在 Document。本批 event 分区对高频事件按 rate=32 采样，落盘只有一个坐标样本，不代表轨迹只有一个点。`pageX` / `clientX` 等 getter 没有落出。回调多次读 `Event.type` 区分 `pointermove` 与 `mousemove`，但内部队列的字段名和编码前明文没有暴露。

challenge 上能看到 `value="Verify you are human"` 的按钮和 `onclick`。主文档事件分区没有这条按钮的 `click` listener_call。可写的是：按钮 UI 存在；可复现的证据是行为事件进了回调，以及 accepted `/fo` 之后的 form submit。不能把单个采样坐标写成通用轨迹，也不能断言第三个 hidden 就是鼠标轨迹。

若 live 点击分支确实需要行为输入，把它做成显式输入，不要藏进 `/fo` body 拼接。

## form.submit 与 3 hidden

accepted 响应被 XHR 读完后，orchestrate 几乎立刻进入 DOM 提交，不是 Python 后处理，也不是浏览器自动重试 GET。类型 B 的窗口是：读 `content-type`、`status`、`responseText`，对 3440 字节和其中一段做两次 `atob`，然后创建 form。

创建顺序：

```text
createElement("form")
set action 为带 __cf_chl_f_tk 的相对业务路径
set method=POST
set enctype=application/x-www-form-urlencoded
三个 hidden：type、64 长度 name、value，append 到 form
把 action 收成业务路径
history.replaceState 保留 __cf_chl_tk
action 规范化为绝对 URL
body.appendChild(form)
form_submit: submit -> constructEntryList -> buildSubmission -> submitSubmission
HTMLFormElement.submit()
```

类型 A 没有直接命中 `HTMLFormElement.submit()` call，但有同样的四阶段 `form_submit`，`field_count=3`。无感链同样有 3 hidden，只是记录形态不同。

本批四份最终 POST 一致：

```text
POST 原业务 URL
Content-Type: application/x-www-form-urlencoded
Cookie 带本轮 cf_clearance
Referer 带本轮 __cf_chl_tk
body 2349 = 三个 64 长度 name，value 长度 1258 / 639 / 255
```

对照关系：

```text
hidden[0].value === 本轮 _cf_chl_opt.md
hidden[1].value === 本轮 _cf_chl_opt.mdrd
hidden[2].value 不是 md，也不是 mdrd
hidden[2] 的时间片晚于初始 HTML 的 cITimeS
三个 name 都不是 sha256(value)
```

所以前两个 value 的来源可以指到 HTML，字段名和第三个 value 必须由 accepted 分支自然生成。Node 捕获 submit 时要从 form controls 构造 entry list，再生成 urlencoded body，不能只记“submit 被调用了”。Firefox 还会走 `form.elements` 和 `HTMLInputElement.mozIsTextField(true) === false`；不必复刻全部内部 actor，但 hidden 不能进文本字段集合。

早期基线的 POST body 约 2371，说明 2349 只是本批对照，不是跨版本常数。

## document.all

两批汇总里，Firefox 全局 ownKeys 有 `HTMLAllCollection` 构造器，目标链路的 domtrace/jscall 没有 `document.all` 读取窗口。它是高危候选，不是已确认进入 `/fo` proof 的采集项。没有命中不补。

浏览器语义是 `typeof document.all === "undefined"`，`document.all == null` 为 true，`Boolean(document.all)` 为 false，同时它又有 HTMLAllCollection / legacy caller 外观。Node 纯 JS 补不出完整 `IsHTMLDDA`。命中后再按表达式最小补：

| 表达式 | 补法 |
|---|---|
| `typeof document.all` | 只满足 typeof，不补成普通对象 |
| `== null` / `Boolean(document.all)` | 做 falsy 与宽松相等；普通对象会错 |
| `"all" in document`、descriptor、ownKeys | 补存在性与枚举外观 |
| `.length` / `item` / `namedItem` / call | 再补最小集合行为 |

不要写成 `{}` 或 `[]`，不要为了消掉 undefined 报错就补普通对象，也不要把它当成和 `document.body` 一样的基础必补项。

## 证据优先级

```text
P0  当前 live 的 fresh 403 HTML、fresh orchestrate、fresh /fo 响应
P1  最近成功 ruyitrace（类型 A/B）
P2  早期两次 /fo 基线，只用于 Worker/Blob/iframe 和“两次也可以通过”
P3  旧补丁实现，只作候选
失败循环样本只用于分类，不能当成功基线
```

模块准入记录要写：模块名、它推进哪两个状态、trace 文件与窗口、旧实现来源、v2 文件、smoke、trace 回放、是否需要 live、状态（`pending` / `pass` / `fail` / `reverted` / `blocked`）。方向证伪就 reverted，不留在完成列表里。

## 禁止

```text
不补 Boolean.prototype.charCodeAt
不补 VM slot，不追混淆变量名
不硬拼 /fo body、cf_clearance、3 hidden、Turnstile token
不把 reload、cookie、或“第 N 次 /fo”当通过
不用 trace 静态业务 body 替代 live body
不在 Node 里发真实网络请求
不把 document.all 补成普通对象
不把子站 /fo accepted 当成主站通过
```
