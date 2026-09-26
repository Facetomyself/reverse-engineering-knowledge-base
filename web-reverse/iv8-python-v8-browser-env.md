# iv8 使用手册：Python 内嵌 V8 的浏览器补环境运行时

> 来源: 微信公众号：爬虫逆向技术栈（[原文](https://mp.weixin.qq.com/s/eBF8z9yEzEzaSTXO2Uhvzw)）
> 作者: 爬虫逆向技术栈
> 原始发布时间: 2026-09-24
> 归档日期: 2026-09-26
> 分类: web-reverse
>
> iv8 是 Python 原生扩展，内嵌 Chromium 同款 V8，在 C++ 层预置 BOM/DOM/CSSOM，单进程跑依赖浏览器环境的 JS。`page.load` 用 `html` + `baseURL` + `resources` 代替真实导航；默认 logical 虚拟时间，`eventLoop.advance` / `sleep` / `tick` 瞬间推进，`drain()` 可能让定时器先于微任务；`mode="debug"` 开 DevTools inspector，`vdebugger` / `vconsole` 替代被禁用的原生调试，`watch_apis` 和缺失 API 日志辅助补环境；`wrapNative` 伪装 `[native code]`，`input.dispatch*` 出 `isTrusted=true`；网络走 `expose` / `add_resource` 离线资源表与 `netLog`；`environment` 是指纹画像、`config` 是行为；多线程按 Isolate 隔离并注意 GIL；WASM 同步 `Module` 可用，`instantiateStreaming` 不可用。

## 收录说明

原文标题「iv8库使用手册-完整版」，2026-09-24 09:30（UTC+8）发布，公众号标注原创。归档时用公开文章 URL 纯 HTTP 拉取（桌面 Chrome UA，无需登录、未遇验证页），`#js_content` 转 Markdown，标题、代码块、表格、列表按原结构保留。正文无插图，只有一张 mdnice 标题装饰背景图，未收录。原文代码块未标语言，按原样保留为无语言围栏。

原文给出的项目地址：`https://github.com/HanZzzzz000/iv8.git`。文中 API、默认值和「能 / 不能」清单以作者当时版本为准，版本升级后先对照项目文档复核。

相关地图：

| 主题 | 文档 |
|------|------|
| 补环境浏览器对象面（DOM/BOM/WebAPI） | [browser-env-objects.md](./browser-env-objects.md) |
| DataDome jsdom + vm 补环境与 VM 分叉 | [datadome-env-patch.md](./datadome-env-patch.md) |
| 隔离 Node 运行器合同 | [isolated-node-runner-contract.md](./isolated-node-runner-contract.md) |
| 纯算 vs 预言机成本账 | [purecalc-vs-oracle-cost.md](./purecalc-vs-oracle-cost.md) |
| KhBox 补环境 / Illegal invocation | [koohai-reverse-notes-compilation.md](./koohai-reverse-notes-compilation.md) |

## 1. iv8 是什么、有什么作用

iv8 是基于 V8 引擎的高性能 Python 原生扩展，在 C++ 层实现浏览器 API，提供高可控、高保真的 BOM/DOM/CSSOM 模拟，内置 API 调用链监控与 Chrome DevTools 远程调试，可在 Python 中直接运行依赖 Web 环境的 JavaScript，无需启动浏览器。 适用于浏览器环境模拟、自动化脚本执行、安全研究、JS 引擎测试等场景。

### 1.1 与传统方案的本质区别

|  | jsdom / Node.js | Headless Chrome CDP | iv8 |
|---|---|---|---|
| 引擎 | Node.js V8 | 完整 Chromium | 内嵌 V8（Chromium 同款） |
| 浏览器 API | 手动补，补一个漏十个 | 真实浏览器，全量 | C++ 层预置，常用 API 已实现 |
| 进程 | Python + Node 双进程 | Python + Chrome 双进程 | 纯 Python 单进程 |
| 资源占用 | 轻 | 极重 | 轻 |
| 速度（逻辑时间） | 取决于真实定时器 | 取决于真实页面加载 | `eventLoop.advance(5000)` 瞬间完成 |
| 检测面 | 环境指纹可能不一致 | 接近真实，但 CDP 可被检测 | 可控，按需注入 |
| 反检测 | 需手动补环境 | 需 stealth 插件 | 按需构造 `environment` dict |

一句话：iv8 相当于把 Chromium 的 V8 引擎单独拆出来，用 Python 直接控制，同时保留了关键浏览器 API 的模拟层。

### 1.2 核心 API（先记这几个）

- `iv8.JSContext(environment=..., time_mode="logical")`：创建隔离上下文，注入浏览器环境
- `ctx.expose(data, name)`：挂到 `__iv8__.data.<name>`
- `__iv8__.page.load(...)`：灌 HTML + 资源，跑脚本，触发生命周期
- `__iv8__.eventLoop.advance(ms)`：推进逻辑时间（瞬间完成）
- `__iv8__.input.dispatchMouseEvent` / `dispatchPointerEvent`：派发 `isTrusted=true` 事件
- `__iv8__.wrapNative(fn, name)`：函数伪装成 `[native code]`
- `__iv8__.netLog.entries`：捕获 XHR/fetch 记录

**github地址**

```
https://github.com/HanZzzzz000/iv8.git
```

## 2. iv8 DOM 操作与页面加载

### 2.1 真浏览器怎么加载页面

1. 打开完整 URL（如 `https://baidu.com/`）→ 这就是文档地址
2. 按该地址请求，拿到 HTML **字节流**
3. 解析器**边收边建 DOM**（流式），不是等整页下完再一次性生成
4. 遇到 `<script>` / `<link>` / 图片等，用文档 URL（或 `<base href>`）拼绝对路径再拉
5. 同时建 CSSOM、跑脚本，再布局、绘制

| 概念 | 含义 |
|---|---|
| 普通下载 | 收齐再处理 |
| 流式加载 | 边收字节边解析、边建 DOM |

### 2.2 iv8 怎么做：`page.load`

iv8 **跳过真实导航请求**：你把「导航结果」直接塞进去——`html` + 假装来自哪的 `baseURL`。

```
window.__iv8__.page.load({
    baseURL: 'https://example.com/page',
    html: `<!DOCTYPE html>
        <html>
        <head><title>Hello iv8</title></head>
        <body>
            <div id="app">Initial Content</div>
        </body>
        </html>`
});
// 之后：document.title / document.URL / location.href 已对齐 baseURL
```

会做的事（对齐浏览器导航关键阶段）：

- 按 chunk **流式解析** HTML
- 遇到 `<script>` 暂停并执行（外联从 `resources` / bundle 取）
- 处理样式、派发 `DOMContentLoaded` / `load`
- 同步 `document.URL`、`location.href`

### 2.3 `page.load` 参数

| 字段 | 必填 | 说明 |
|---|---|---|
| `baseURL` | 是 | 页面 URL → `document.URL` / `location` |
| `html` | 是 | HTML 源码 |
| `resources` | 否 | 外联资源表：URL → body（脚本/样式等，**不走真网**） |
| `headers` | 否 | 主文档响应头（CSP、`Set-Cookie`、`content-type` 等） |

`resources` 示例：相对路径会先用 `baseURL` 拼绝对地址再查表。

```
window.__iv8__.page.load({
    baseURL: 'https://mysite.com',
    html: `<html><head>
        <script src="/lib.js"></script>
        <script src="/app.js"></script>
    </head><body></body></html>`,
    resources: {
        'https://mysite.com/lib.js': { body: 'window.LIB_VERSION = "1.0";' },
        'https://mysite.com/app.js': {
            body: 'window.APP_INIT = true; window.APP_LIB = window.LIB_VERSION;'
        }
    }
});
```

### 2.4 `page.load` vs `innerHTML`

| 方式 | 脚本执行 | 生命周期事件 | 同步 URL | 适用 |
|---|---|---|---|---|
| `page.load(snapshot)` | 会 | 会（DOMContentLoaded / load） | 会 | 跑页面脚本、模拟真实加载 |
| `document.documentElement.innerHTML = ...` | 否 | 否 | 否 | 只要 DOM 结构、轻量解析 |

### 2.5 加载后的 DOM 操作

`page.load` 之后就是普通 DOM API，和浏览器一样用：

```
document.getElementById('root')
document.querySelectorAll('.item')
document.createElement('h1')
parent.appendChild(node)
el.setAttribute('data-loaded', 'true')
el.style.cssText = '...'
```

### 2.6 生命周期顺序（有内联脚本时）

```
script-executed → DOMContentLoaded → load
```

`DOMContentLoaded`：DOM 建好；`load`：依赖资源也处理完。前者先触发。

口诀：**真浏览器 = 请求流 + 解析；iv8 = 直接灌 html + baseURL，外联靠 resources。**

## 3. 事件循环和定时器控制

默认 `time_mode="logical"`：**虚拟时间**，`advance` / `sleep` 不睡真实墙钟，瞬间推进。\
需要跟墙钟对齐时用 `time_mode="system"`（见 3.6）。

| API | 作用 |
|---|---|
| `eventLoop.advance(total, step?)` | 按帧推进虚拟时间（默认步长约 16.67ms，贴 rAF） |
| `eventLoop.sleep(ms)` | 沿时间线推进 ms，到期任务按序跑完 |
| `eventLoop.tick(ms?)` | **单轮**事件循环，适合逐步调试 |
| `eventLoop.drain()` | 排空**当前已到期**任务，**不推进时间**（见下方坑） |
| `eventLoop.drainMicrotasks()` | 只排微任务 |
| `eventLoop.drainTimers()` | 只跑已到期定时器（同样不拨表；刚注册时常见是 timeout=0） |

### 3.1 案例：宏任务 vs 微任务

```
with iv8.JSContext() as ctx:
    ctx.eval("""
        var log = [];
        setTimeout(() => log.push('timeout-0'), 0);
        Promise.resolve().then(() => log.push('promise-1'));
        queueMicrotask(() => log.push('microtask-1'));
        log.push('sync');
    """)
    print("执行同步代码后:", ctx.eval("log", to_py=True))
    ctx.eval("window.__iv8__.eventLoop.drainMicrotasks()")
    print("drainMicrotasks后:", ctx.eval("log", to_py=True))
    ctx.eval("window.__iv8__.eventLoop.drain()")
    print("drain后:", ctx.eval("log", to_py=True))
```

```
执行同步代码后: ['sync']
drainMicrotasks后: ['sync', 'promise-1', 'microtask-1']
drain后: ['sync', 'promise-1', 'microtask-1', 'timeout-0']
```

顺序：`sync` → 微任务（promise / queueMicrotask）→ 宏任务（setTimeout）。

### 3.2 案例：`advance` 按帧推进虚拟时间

```
with iv8.JSContext() as ctx:
    ctx.eval("""
        var log = [];
        setTimeout(() => log.push('100ms'), 100);
        setTimeout(() => log.push('200ms'), 200);
        setTimeout(() => log.push('500ms'), 500);
        Promise.resolve().then(() => log.push('micro'));
    """)
    ctx.eval("window.__iv8__.eventLoop.advance(300)")
    print("advance(300)后:", ctx.eval("log", to_py=True))
    ctx.eval("window.__iv8__.eventLoop.advance(300)")
    print("再 advance(300)后:", ctx.eval("log", to_py=True))
```

```
advance(300)后: ['micro', '100ms', '200ms']
再 advance(300)后: ['micro', '100ms', '200ms', '500ms']
```

先到 300ms：微任务 + 100/200 定时器；500 还没到期。再推 300（累计 600）才触发 500ms。

### 3.3 案例：`sleep` 按时间线推进

```
with iv8.JSContext() as ctx:
    ctx.eval("""
        var log = [];
        setTimeout(() => log.push('50ms'), 50);
        setTimeout(() => log.push('150ms'), 150);
    """)
    ctx.eval("window.__iv8__.eventLoop.sleep(100)")
    print("sleep(100)后:", ctx.eval("log", to_py=True))
    ctx.eval("window.__iv8__.eventLoop.sleep(100)")
    print("再 sleep(100)后:", ctx.eval("log", to_py=True))
```

```
sleep(100)后: ['50ms']
再 sleep(100)后: ['50ms', '150ms']
```

`sleep(100)` 把时钟推 100ms 并处理这段里到期的任务；再 `sleep(100)` 累计到 200，150ms 定时器才跑。

### 3.4 案例：`tick` 单轮调试

```
with iv8.JSContext() as ctx:
    ctx.eval("""
        var log = [];
        setTimeout(() => log.push('A'), 0);
        setTimeout(() => {
            log.push('B');
            Promise.resolve().then(() => log.push('B-micro'));
        }, 0);
        setTimeout(() => log.push('C'), 0);
    """)
    ctx.eval("window.__iv8__.eventLoop.tick()")
    print("tick 1:", ctx.eval("log", to_py=True))
    ctx.eval("window.__iv8__.eventLoop.tick()")
    print("tick 2:", ctx.eval("log", to_py=True))
    ctx.eval("window.__iv8__.eventLoop.tick()")
    print("tick 3:", ctx.eval("log", to_py=True))
```

```
tick 1: ['A']
tick 2: ['A', 'B', 'B-micro']
tick 3: ['A', 'B', 'B-micro', 'C']
```

每次 `tick` 只走一轮：跑一个到期宏任务，并清掉它产生的微任务。适合逐步看定时器嵌套。

### 3.5 坑：`drain()` 可能让定时器先于微任务

浏览器 / HTML 规范习惯顺序是：同步 → **微任务** → **宏任务（定时器）**。\
但直接调一次 `eventLoop.drain()` 时，实测会出现**到期定时器先跑、微任务后跑**：

```
with iv8.JSContext() as ctx:
    ctx.eval("""
        var log = [];
        setTimeout(() => log.push('t0'), 0);
        Promise.resolve().then(() => log.push('micro'));
        log.push('sync');
    """)
    ctx.eval("window.__iv8__.eventLoop.drain()")
    print(ctx.eval("log", to_py=True))
    # 实测: ['sync', 't0', 'micro']  ← 定时器在微任务前面（和规范直觉相反）
```

要对齐「先微后宏」，**先**清微任务，**再** drain / drainTimers（案例 1 的写法）：

```
ctx.eval("window.__iv8__.eventLoop.drainMicrotasks()")
ctx.eval("window.__iv8__.eventLoop.drain()")
# → ['sync', 'promise-…', 'microtask-…', 'timeout-0']
```

`drainTimers()` 同理：只处理**当前已到期**的定时器，不是「永远只有 timeout=0」；时钟没推时 timeout=0 刚好到期，timeout=100 不会跑。跑定时器时若产生微任务，也可能被顺带消化，别默认顺序和浏览器完全一致。

选型：`drain`* 不推进时间只清队；要「过一会儿」用 `advance` / `sleep`；要一步一步用 `tick`；**要规范顺序就先 `drainMicrotasks` 再 `drain`。**

### 3.6 `time_mode`：`logical` vs `system`

创建 Context 时可选时间模式（也可用 `config={"time": {"mode": "..."}}`）：

| 模式 | `Date.now()` / 定时器时间线 | 适用 |
|---|---|---|
| `logical`（默认） | 虚拟时钟：`sleep(5000)`**瞬间完成**，`Date.now()` 也跳 5s | 自动化、补环境、快速跑定时器 |
| `system` | 锚定墙钟：JS 跑多久，`Date.now()` 就涨多少 | PoW、时间差校验、要和真实耗时对齐的场景 |

```
import time
import iv8

# logical：虚拟推进，墙钟几乎不耗
t_wall0 = time.perf_counter()
with iv8.JSContext(time_mode="logical") as ctx:
    ctx.eval("var t0 = Date.now();")
    ctx.eval("window.__iv8__.eventLoop.sleep(5000)")
    js_elapsed = ctx.eval("Date.now() - t0")
print(f"logical: JS 增量={js_elapsed}ms, 墙钟≈{(time.perf_counter()-t_wall0)*1000:.1f}ms")
# 典型：JS 增量=5000，墙钟只有几毫秒

# system：Date.now() 跟真实耗时走
with iv8.JSContext(time_mode="system") as ctx:
    ctx.eval("var t0 = Date.now();")
    # 这里不 sleep 虚拟表；跑一点真实工作再读差
    elapsed = ctx.eval("Date.now() - t0")
print(f"system: Date.now() 增量反映真实耗时 ≈ {elapsed}ms")
```

口诀：**默认用 logical 把时间「快进」；只有业务盯墙钟时才开 system。**

## 4. debugger 调试 / inspect

### 4.1 是什么

iv8 在 C++ 运行时里嵌了 **V8 Inspector**，对外开一个 **CDP（Chrome DevTools Protocol）Server**。用法接近 `node --inspect`：Chrome DevTools（或任意 CDP Client）连上 WebSocket 后，走 `Debugger` / `Runtime` 等域下指令，即可断点、单步、看变量。

```
Chrome DevTools / 你的 CDP Client
        │  WebSocket + CDP JSON
        ▼
iv8 CDP Server（默认端口 9229）
        │  dispatchProtocolMessage()
        ▼
V8InspectorSession
        ▼
当前 JSContext 对应的 V8 Isolate
```

要点：

- 必须 `JSContext(mode="debug")`，再链式 `.with_devtools(...)`，调试面才打开。
- 每个 `JSContext` 独占一个 Isolate；多 Context 并行时各自一套调试会话。
- 还有 **API 访问断点**（`watch_apis`）：读指定属性时自动停，不用在业务 JS 里手写断点。

### 4.2 怎么用（操作步骤）

1. 跑带 `with_devtools` 的脚本；终端会打印 DevTools URL，进程**阻塞等待前端连接**。
2. 把 URL 粘到 Chrome 地址栏（形如 `devtools://devtools/bundled/inspector.html?ws=127.0.0.1:9229/...`）。
3. 连上后脚本继续跑；遇到 `vdebugger;` 或命中 `watch_apis` 时，Sources 面板暂停。
4. 在 DevTools 里单步 / 看 Scope / 改变量，点 **Resume（▶）** 进入下一处断点。

### 4.3 关键 API

- `JSContext(mode="debug")`：打开 debug 面（监控 + 可挂 Inspector）
- `.with_devtools(port=9229, watch_apis=None, enable_console=True)`：起 CDP；可挂 API 访问断点
- `ctx.eval(..., name="", line=-1, col=-1, to_py=False, devtools=True)`：`name`/`line`/`col` 决定 Sources 显示
- JS：`vdebugger;` → **显式断点**（替代原生 `debugger;`）
- JS：`vconsole.log(...)` → 仅 DevTools 可见（配合 `enable_console=False`）

`with_devtools` 参数：

| 参数 | 默认 | 说明 |
|---|---|---|
| `port` | `9229` | CDP 监听端口 |
| `watch_apis` | `None` | 如 `"navigator.userAgent"`；访问即断 |
| `enable_console` | `True` | `True`：标准 console；`False`：改用 `vconsole`（防探针） |

#### `eval` 的 `name`：给脚本一个「假 URL」

从本地文件 `eval` 大段业务 JS 时，**传不传 `name`，堆栈 / Sources 长得不一样**：

|  | 不传 `name` | 传了 `name="https://.../xxx.js"` |
|---|---|---|
| `Error.stack` / 调用栈 | `at foo (<anonymous>:3:36)` | `at foo (https://.../xxx.js:3:36)` |
| DevTools Sources | 无名脚本，常显示 `(anonymous)` / 难对上真站 | 按你给的 URL 当资源名列出 |
| 用途 | 随手试一行 | 本地灌包、线上对行号 / 断点 |

实测堆栈对比：

```
# 不传 name
Error: no-name
    at foo (<anonymous>:3:36)
    at <anonymous>:3:60

# 传了 name
Error: with-name
    at bar (https://storage.360buyimg.com/webcontainer/main/js_security_v3_main.js:3:36)
    at https://storage.360buyimg.com/webcontainer/main/js_security_v3_main.js:3:62
```

写法：

```
with open("js_security_v3_main.js", "r", encoding="utf-8") as f:
    js_code = f.read()

ctx.eval(
    js_code,
    name="https://storage.360buyimg.com/webcontainer/main/js_security_v3_main.js",
)
```

| 参数 | 含义 |
|---|---|
| `name` | 脚本在 Inspector / `Error.stack` 里的资源名；习惯填真实 CDN URL |
| `line` / `col` | 起始行号、列号（默认 `-1`）；和 `name` 一起对齐堆栈 |
| `to_py` | 把返回值转成 Python dict/list 等 |
| `devtools` | `False`：本段不进调试器、不等待前端连接 |

口诀：**不传是 `<anonymous>`；要线上路径感就传 `name="https://...真实.js"`。**

### 4.4 反调试：`debugger` → `vdebugger`，`console` → `vconsole`

目标脚本常见手法：死循环 `debugger;`、或探测 `console.groupEnd.toString()` 等差异。

| 原生 | iv8 行为 | 你该用 |
|---|---|---|
| `debugger;` | **已禁用**，不会暂停（防无限 debugger） | `vdebugger;`（行为等同标准 debugger） |
| `console.`* | `enable_console=False` 时可关掉 DevTools 上报通道 | `vconsole.log` / `warn` / …（只进 DevTools，对页面脚本不可见） |

```
=== DevTools 调试器已就绪（端口 9229，监听 127.0.0.1）===

  本机调试：
    devtools://devtools/bundled/inspector.html?ws=127.0.0.1:9229
```

> 运行程序之后，直接浏览粘贴访问调试路径即可

### 4.5 完整示例

```
import iv8

with iv8.JSContext(mode="debug").with_devtools(
    port=9229,
    # 访问这些 API 时自动断点；Call Stack 可回溯到触发行
    watch_apis=[
        "navigator.userAgent",
        "navigator.webdriver",
        "document.cookie",
        "screen.width",
    ],
    # enable_console=False,  # 需要隐蔽调试时再开
) as ctx:

    # 初始化：不等待 DevTools、不触发断点
    ctx.eval("""
        window.__iv8__.page.load({
            baseURL: 'https://www.baidu.com',
            html: '<html><body></body></html>'
        });
    """, devtools=False)

    # 断点 1：显式 vdebugger（第一次走调试器的 eval 会先等前端连上）
    ctx.eval("""
        var x = 10, y = 20;
        debugger;     // 不会停
        vdebugger;    // 会停：Sources 看 x/y，再 Resume
        var z = x + y;
    """)

    # 断点 2～5：watch_apis 各停一次（共 Resume 四次）
    # Sources 里可能看到动态插入的 "vdebugger; // navigator.userAgent"；
    # 到 Call Stack 往上翻才能定位到你的业务行。
    ctx.eval("""
        var ua     = navigator.userAgent;
        var wd     = navigator.webdriver;
        var cookie = document.cookie;
        var sw     = screen.width;
    """)

    z  = ctx.eval("z",  devtools=False)
    ua = ctx.eval("ua", devtools=False)
    print(f"z  = {z}")
    print(f"ua = {ua}")
```

隐蔽通道禁用打印函数示例：

```
with iv8.JSContext(mode="debug").with_devtools(
    port=9229,
    watch_apis=["navigator.userAgent", "document.cookie", "canvas.toDataURL"],
    enable_console=False,
) as ctx:
    ctx.eval("let ua = navigator.userAgent;")       # 触发 API 断点
    ctx.eval("vconsole.log('调试信息', ua);")       # 仅 DevTools 可见
```

### 4.6 DevTools 里能做什么

| 能力 | 说明 |
|---|---|
| `vdebugger;` 断点 | Sources 暂停、单步、改局部变量 |
| `watch_apis` | 属性读即断，定位「谁在摸指纹」 |
| 事件监听器断点 | 按事件类型断（与 Chrome 同类） |
| XHR / Fetch URL 断点 | 按请求 URL 断 |
| Elements | 看 DOM 结构 |
| Application | Cookie / Storage 查看与编辑 |
| Console | 标准 console 或 `vconsole` |

### 4.7 常见坑

1. **忘了 `mode="debug"`** → `with_devtools` 无效或起不来调试面；也看不到 API 监控日志。
2. **写了 `debugger;` 却不停** → 正常；改成 `vdebugger;`。
3. **脚本卡在启动** → 在等你打开 DevTools URL；或把启动段 `eval(..., devtools=False)`。
4. **`watch_apis` 停在「假源码」** → 看 **Call Stack** 上一帧才是业务代码。
5. **端口占用** → 换 `port=`，或关掉占用 9229 的旧进程。

### 4.8 补环境时用 debug 打缺失 API

实际补环境不一定要开 DevTools。只要：

```
with iv8.JSContext(mode="debug") as ctx:
    ctx.eval(""" /* 目标脚本 / page.load 后的业务 */ """)
```

终端（stderr）会刷 API 访问链。脚本读到**未实现、落到 `undefined`** 的属性时，重点搜：

```
[INFO]    实例访问 - navigator.xxx -> getter -> undefined
[INFO]    原型访问 - Navigator.prototype.xxx -> getter -> undefined
[WARNING] 疑似缺失API - Navigator.prototype.xxx    ← 按这条去补
```

工作流：

```
mode="debug" 跑目标 JS
        ↓
终端搜「疑似缺失API」
        ↓
按路径补（定义属性 / environment 覆盖 / wrapNative / expose …）
        ↓
再跑 → 警告消失或换下一批缺失项
```

| 模式 | 监控日志 |
|---|---|
| `prod`（默认） | 不记，适合量产 |
| `debug` | 记属性读/写、方法调用、构造；缺失会打 `疑似缺失API` |

降噪：高频内置（Math / JSON / Array 等）默认已静音；还吵就传 `ignore_apis=[...]` 排除指定路径。

和 DevTools 的关系：`mode="debug"` 单独就能看缺失日志；需要断点 / Call Stack 再链式 `.with_devtools(...)`。定位「谁摸了指纹」也可用 `watch_apis`（见 4.3）。

口诀：**补环境先开 debug 看「疑似缺失API」；要对着源码停再用 with_devtools。**

## 5. 函数的伪装

公开 API 是 **`__iv8__.wrapNative(fn, name)`**：把自定义函数伪装成原生——`toString` 变成 `function name() { [native code] }`，并按原生习惯处理 `prototype`（例如伪装成 `alert` 这类无 prototype 的函数）。

当前没有单独的 `hookNative`；要「hook 内置再伪装」，就是：**先改实现，再 `wrapNative` 盖回去**。

### 5.1 最小例子：自定义函数变 native

```
with iv8.JSContext() as ctx:
    checks = ctx.eval("""
        (function () {
            var results = [];

            results.push('webdriver: ' + navigator.webdriver);
            results.push('eval is native: ' + (eval.toString().indexOf('[native code]') !== -1));

            var fake = window.__iv8__.wrapNative(function () {}, 'alert');
            results.push('wrapped alert is native: ' + (fake.toString().indexOf('[native code]') !== -1));
            results.push('typeof __iv8__: ' + typeof window.__iv8__);
            // 伪装成 alert 这类系统函数时，prototype 也会被拿掉
            results.push('fake has no prototype: ' + (fake.prototype === undefined));

            return results;
        })()
    """, to_py=True)
    for line in checks:
        print(line)
```

**结果**

```
webdriver: false
eval is native: true
wrapped alert is native: true
typeof __iv8__: undefined
fake has no prototype: true
```

### 5.2 Hook 内置再 wrapNative（推荐写法）

替换 `JSON.stringify` / `fetch` 等时，先包一层业务逻辑，再用 `wrapNative` 把 `toString` 伪装回去：

```
with iv8.JSContext() as ctx:
    ctx.eval("""
        var origStringify = JSON.stringify;
        var callCount = 0;
        JSON.stringify = window.__iv8__.wrapNative(function () {
            callCount++;
            return origStringify.apply(JSON, arguments);
        }, 'stringify');
    """)
    print(ctx.eval("JSON.stringify.toString()"))
    # function stringify() { [native code] }
    print(ctx.eval("JSON.stringify({a: 1})"))  # {"a":1}
    print(ctx.eval("callCount"))               # 1
```

口诀：**改行为用 hook；过检测用 wrapNative；两者叠在一起用。**

## 6. 事件模拟

### 6.1 先搞清 `isTrusted`

对，浏览器里就是这样：

1. **用户真实操作**（鼠标点、触屏、键盘）→ 引擎自己造的事件 → `e.isTrusted === true`
2. **页面脚本自己造**（`new Event` / `new MouseEvent` / `el.dispatchEvent(...)`）→ **永远**`e.isTrusted === false`
3. **`isTrusted` 是只读的**：构造参数里写不进、赋值改不了；`Object.defineProperty(e, 'isTrusted', …)` 在真机上也改不动（规范要求由 UA 独占）

```
const e = new MouseEvent('click', { bubbles: true });
e.isTrusted;          // false
e.isTrusted = true;   // 无效，仍是 false（严格模式赋值可能静默失败）
btn.dispatchEvent(e); // 监听器里拿到的还是 isTrusted === false
```

风控 / 滑块常读 `e.isTrusted` 区分「真人」和「脚本假点」。\
所以 iv8 提供 `__iv8__.input.*`：在模拟层直接派发 **`isTrusted=true`** 的事件，语义对齐 Chrome 的可信输入。

### 6.2 输入事件模拟

派发可信鼠标 / 指针事件；捕获 → 目标 → 冒泡链与真机一致。

| API | 作用 |
|---|---|
| `__iv8__.input.dispatchMouseEvent(init)` | 可信鼠标事件（click / mousedown / mouseup / mousemove …） |
| `__iv8__.input.dispatchPointerEvent(init)` | 可信指针事件（pointerdown / move / up …） |

常用 `init` 字段：`type`、`target`、`clientX` / `clientY`、`button` / `buttons`；指针还可带 `pointerId`、`pointerType`、`pressure`（0～1，触控笔/压感常用；鼠标默认多为 `0.5`）。

### 6.3 最小 click

```
with iv8.JSContext() as ctx:
    ctx.eval("""
        window.__iv8__.page.load({
            baseURL: 'https://example.com',
            html: '<html><body><button id="btn">Click</button></body></html>'
        });

        var clicked = false;
        document.getElementById('btn').addEventListener('click', function (e) {
            clicked = e.isTrusted;  // true
        });
        // 派发点击事件
        window.__iv8__.input.dispatchMouseEvent({
            type: 'click',
            target: document.getElementById('btn'),
            clientX: 50, clientY: 25,
            button: 0, buttons: 0
        });
    """)
    print(ctx.eval("clicked"))  # True
```

### 6.4 完整按下 / 抬起 / 点击（鼠标）

```
var btn = document.getElementById('btn');
window.__iv8__.input.dispatchMouseEvent({
    type: 'mousedown', target: btn, clientX: 50, clientY: 25, button: 0, buttons: 1
});
window.__iv8__.input.dispatchMouseEvent({
    type: 'mouseup', target: btn, clientX: 50, clientY: 25, button: 0, buttons: 0
});
window.__iv8__.input.dispatchMouseEvent({
    type: 'click', target: btn, clientX: 50, clientY: 25, button: 0, buttons: 0
});
```

### 6.5 PointerEvent 案例（down → move → up）

```
with iv8.JSContext() as ctx:
    ctx.eval("""
        window.__iv8__.page.load({
            baseURL: 'https://example.com',
            html: '<html><body><div id="area" style="width:200px;height:200px;"></div></body></html>'
        });

        var pointerEvents = [];
        var area = document.getElementById('area');
        ['pointerdown', 'pointermove', 'pointerup'].forEach(function (type) {
            area.addEventListener(type, function (e) {
                pointerEvents.push({
                    type: e.type,
                    isTrusted: e.isTrusted,
                    clientX: e.clientX,
                    clientY: e.clientY,
                    pointerId: e.pointerId,
                    pointerType: e.pointerType,
                    pressure: e.pressure
                });
            });
        });

        var target = document.getElementById('area');
        window.__iv8__.input.dispatchPointerEvent({
            type: 'pointerdown', target: target,
            clientX: 10, clientY: 10, button: 0, buttons: 1,
            pointerId: 1, pointerType: 'mouse', pressure: 0.5
        });
        window.__iv8__.input.dispatchPointerEvent({
            type: 'pointermove', target: target,
            clientX: 50, clientY: 50, button: 0, buttons: 1,
            pointerId: 1, pointerType: 'mouse', pressure: 0.5
        });
        window.__iv8__.input.dispatchPointerEvent({
            type: 'pointerup', target: target,
            clientX: 50, clientY: 50, button: 0, buttons: 0,
            pointerId: 1, pointerType: 'mouse', pressure: 0
        });
    """)
    print(ctx.eval("pointerEvents", to_py=True))
    # 每条 isTrusted 均为 true；pressure / pointerId / pointerType 按传入回显
```

触控笔可把 `pointerType` 改成 `'pen'`，并调 `pressure`（0～1）。滑块轨迹一般是循环 `pointermove`（可再配 `dispatchMouseEvent` 的 mousemove）。

### 6.6 isTrusted 对照

| 派发方式 | `e.isTrusted` | 说明 |
|---|---|---|
| 用户真实点击 / 触控 / 按键 | `true` | 浏览器 UA 生成 |
| `__iv8__.input.dispatchMouseEvent` / `dispatchPointerEvent` | `true` | iv8 可信输入，对齐真人 |
| `new MouseEvent(...)` + `element.dispatchEvent(...)` | `false` | 脚本自造；只读，改不成 `true` |

口诀：**脚本 new 出来的事件永远不可信且改不了；要过检测用 `__iv8__.input.*`。**

## 7. Python ↔ JS 互调

### 7.1 是什么

`ctx.expose(...)` 把 **Python 对象**挂到 JS 的 `__iv8__.data` 下，**不污染 `window`**。\
JS 里用 `__iv8__.data.xxx`（或 `window.__iv8__.data.xxx`）读写 / 调用；Python 侧用 `ctx.eval` 读回结果。

```
Python                         JS（同一 JSContext）
──────                         ──────────────────
ctx.expose(fn, "httpGet")  →   __iv8__.data.httpGet(...)
ctx.expose({"a":1}, "cfg") →   __iv8__.data.cfg.a
ctx.eval("...")            ←   执行结果自动转 Python（可选 to_py=True）
```

### 7.2 三种暴露方式

```
import requests
import iv8

with iv8.JSContext() as ctx:
    # 方式一：命名暴露
    ctx.expose(requests.get, "httpGet")
    # JS: __iv8__.data.httpGet("https://...")

    # 方式二：自动命名（用函数的 __name__）
    def fetch_data(url):
        return requests.get(url).text
    ctx.expose(fetch_data)
    # JS: __iv8__.data.fetch_data("https://...")

    # 方式三：关键字参数批量暴露
    ctx.expose(get=requests.get, post=requests.post)
    # JS: __iv8__.data.get(...), __iv8__.data.post(...)

    # 非函数：字典 / 列表等也能挂
    ctx.expose({"token": "abc123", "debug": True}, "config")
    print(ctx.eval("__iv8__.data.config.token"))  # "abc123"
```

| 写法 | JS 侧名字 |
|---|---|
| `expose(obj, "name")` | `__iv8__.data.name` |
| `expose(fn)`（函数） | `__iv8__.data.<fn.__name__>` |
| `expose(a=..., b=...)` | `__iv8__.data.a` / `__iv8__.data.b` |

### 7.3 返回值与类型

- JS 调 Python 函数：参数从 V8 转进 Python，返回值再转回 JS（常见：`str` / `int` / `float` / `bool` / `dict` / `list` / `None`）。
- 复杂 HTTP 响应建议在 Python 里用 **`json.dumps` 成字符串**，JS 再 `JSON.parse`，边界更干净。
- Python 读 JS：`ctx.eval(expr)`；要原生 dict/list 时加 `to_py=True`。

### 7.4 GIL 与性能（必读）

JS 调用已 expose 的 Python 函数时：

1. **当前 V8 执行暂停**（Isolate 单线程）
2. **自动拿 GIL**，整个 Python 调用期间持有
3. **其它 Python 线程**在这次调用返回前会被挡住

因此：桥接函数要尽量轻；长耗时 HTTP 是**同步阻塞**的。高并发优先：`add_resource` 预灌、Python 侧先拉再注入，或按业务拆多 Context / 多线程（每 Context 一 Isolate）。

### 7.5 典型用途

- **页面快照**：`expose({html, baseURL, resources}, "snapshot")` → `page.load(__iv8__.data.snapshot)`
- **配置 / token**：`expose({"token": "..."}, "config")`
- **JS 要真上网**：expose `requests` 包装函数 → 见第 8 章
- **Hook XHR 再走 Python**：expose `realFetch`，在 `send` 里调 → 见 8.2

快照示例：

```
with iv8.JSContext() as ctx:
    ctx.expose({
        "baseURL": "https://example.com",
        "html": "<!DOCTYPE html><html><body></body></html>",
    }, "snapshot")
    ctx.eval("__iv8__.page.load(__iv8__.data.snapshot);")
```

### 7.6 和「网络拦截」怎么选

- JS 主动调 Python（真 HTTP / 读文件 / 算签名）→ **`expose`**
- 假装 XHR/fetch 已成功（离线表）→ **`add_resource` / `page.load.resources`**
- 两者结合 → Hook `send` → `expose` 的 `realFetch` 拉真网 → `add_resource` 灌回再走原生 `send`

口诀：**挂东西用 expose → `__iv8__.data`；假响应用 add_resource；真上网 = expose + 轻量包装。**

## 8. 网络桥接：将 Python requests 传入 V8

iv8 **默认不发真 HTTP**。要让页面脚本「像浏览器一样请求外网」，把 Python 的 `requests`（或 `curl_cffi`）经上一章的 `expose` 挂进 `__iv8__.data`，由 JS 同步调用。

### 8.1 最小 GET

```
import json
import requests
import iv8

with iv8.JSContext() as ctx:
    def py_get(url):
        resp = requests.get(str(url), timeout=10)
        return json.dumps({
            "status": resp.status_code,
            "statusText": resp.reason,
            "headers": dict(resp.headers),
            "body": resp.text[:2000],
        })

    ctx.expose(py_get, "pyGet")

    result = ctx.eval("""
        (function () {
            var resp = JSON.parse(__iv8__.data.pyGet('https://httpbin.org/get?foo=bar'));
            return { ok: resp.status === 200, status: resp.status };
        })()
    """, to_py=True)
    print(result)  # {'ok': True, 'status': 200}
```

### 8.2 和 XHR 对齐的两种套路

1. **JS 直接调桥**（简单）：业务改成 `__iv8__.data.pyGet(url)`，不经过 XHR（见 8.1）。
2. **Hook 再灌表**（页面仍写 XHR）：`send` 里调 `__iv8__.data.realFetch` → Python `requests` → `ctx.add_resource` → 再走原生 `send` 读假表。

最小可跑（同步 XHR）：

```
import json
import requests
import iv8

with iv8.JSContext() as ctx:
    def real_fetch(method, url, body, headers_json):
        method = str(method).upper()
        url = str(url)
        req_headers = json.loads(str(headers_json)) if headers_json else {}
        req_body = str(body) if body and str(body) != "null" else None
        resp = requests.request(
            method, url, data=req_body, headers=req_headers, timeout=30
        )
        # 灌回离线表，让后面的原生 send 以为「已经请求成功」
        ctx.add_resource(
            url=url,
            body=resp.text,
            status=resp.status_code,
            headers=dict(resp.headers),
        )

    ctx.expose(real_fetch, "realFetch")

    ctx.eval("""
        window.__iv8__.page.load({
            html: '<html><body></body></html>',
            baseURL: 'https://example.com'
        });

        (function () {
            var _open = XMLHttpRequest.prototype.open;
            var _send = XMLHttpRequest.prototype.send;
            var _setHeader = XMLHttpRequest.prototype.setRequestHeader;

            XMLHttpRequest.prototype.open = function (method, url) {
                this.__method = method;
                this.__url = url;
                this.__headers = {};
                return _open.apply(this, arguments);
            };
            XMLHttpRequest.prototype.setRequestHeader = function (name, value) {
                this.__headers[name] = value;
                return _setHeader.apply(this, arguments);
            };
            XMLHttpRequest.prototype.send = function (body) {
                __iv8__.data.realFetch(
                    this.__method,
                    this.__url,
                    body,
                    JSON.stringify(this.__headers || {})
                );
                return _send.apply(this, arguments);
            };
        })();
    """)

    # 页面照常写 XHR；实际发包在 Python
    result = ctx.eval("""
        (function () {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', 'https://httpbin.org/get?demo=iv8', false);
            xhr.send(null);
            return { status: xhr.status, len: xhr.responseText.length };
        })()
    """, to_py=True)
    print(result)  # {'status': 200, 'len': ...}
```

流程：

```
JS xhr.send
    → expose 的 realFetch（Python requests 真上网）
    → add_resource 把响应塞进离线表
    → 原生 send 读表，填 status / responseText
```

异步 XHR 还要在 `send` 后 `eventLoop.drain()`，让 readyState / load 按序跑完。

注意：桥接期间持 GIL，整次请求阻塞 V8 与其它 Python 线程；批量并发别全挤在一个 Context 的同步 expose 上。

## 9. iv8 网络请求拦截与监控

iv8 **不会真的发 HTTP**。JS 里的 `XMLHttpRequest` / `fetch` / 外联脚本，默认从一份**离线资源表（resource bundle）**里按 URL 取响应。

注入方式有两种（进的是同一张表）：

| 方式 | 何时用 |
|---|---|
| `ctx.add_resource(url, body, status=200, headers=...)` | Python 侧随时注入（运行中补） |
| `page.load({ resources: { url: body } })` | 加载页面时预置外联 `<script>` / `<link>` |

### 9.1 示例：`add_resource` + XHR

```
with iv8.JSContext() as ctx:
    # 1) 先有一个文档环境（location / document 等）
    ctx.eval("""
        window.__iv8__.page.load({
            html: '<html><body></body></html>',
            baseURL: 'https://example.com'
        });
    """)

    # 2) 往离线表里塞一条「假装服务端返回」
    ctx.add_resource(
        url="https://api.example.com/config",
        body=json.dumps({"version": "2.0", "features": ["a", "b"]}),
        status=200,
        headers={"content-type": "application/json"},
    )

    # 3) JS 里照常 XHR；匹配到上面的 url 就返回注入的 body
    ctx.eval("""
        var xhr = new XMLHttpRequest();
        xhr.open('GET', 'https://api.example.com/config', false);  // false = 同步
        xhr.send();
    """)

    print(ctx.eval("xhr.status"))        # 200
    print(ctx.eval("xhr.responseText"))  # {"version":"2.0",...}
```

流程：

```
page.load 建好假页面
        ↓
add_resource 登记 URL → 响应正文
        ↓
xhr.open/send 请求该 URL
        ↓
iv8 查 bundle，命中则填 status / responseText
        ↓
（没有命中则拿不到真实网络响应；不会替你上网）
```

要点：

1. **不是拦截真网卡**，是「预置假响应，让页面 API 以为请求成功了」。
2. URL 要**对得上**（含协议和路径）；对不上就命中失败。
3. `open(..., false)` 是同步 XHR，方便立刻读 `responseText`；异步还要配合事件循环 `advance`/`drain`。
4. 真要上网：Python 用 `requests`/`curl_cffi` 拉完，再 `add_resource` 灌回去（见第 8 章网络桥接），或 hook `send` 调 `__iv8__.data.realFetch`（见 8.2）。

和 `page.load.resources` 的关系：外联脚本用 `resources`；运行期 API 请求用 `add_resource` 更灵活，表是同一份。

### 9.2 网络请求拦截：`netLog` 监控

XHR / fetch / 导航发生时，iv8 **自动**往 `__iv8__.netLog.entries` 里追加记录（不需要自己 hook）。注意大小写是 **`netLog`**，不是 `netlog`。

```
import iv8

with iv8.JSContext() as ctx:
    ctx.eval("""
        window.__iv8__.page.load({
            html: '<html><body></body></html>',
            baseURL: 'https://example.com'
        });
    """)

    print("初始条数:", ctx.eval("window.__iv8__.netLog.entries.length"))

    ctx.eval("""
        var xhr = new XMLHttpRequest();
        xhr.open('GET', 'https://example.com/api/data', false);
        xhr.setRequestHeader('X-Token', 'abc');
        xhr.send('payload');
    """)

    entries = ctx.eval("window.__iv8__.netLog.entries", to_py=True)
    for i, entry in enumerate(entries):
        print(f"[{i}] {entry.get('method')} {entry.get('url')} type={entry.get('type')}")
        print(f"    headers={entry.get('headers')} body={entry.get('body')!r}")
```

每条记录字段（`netLog.help()`）：

| 字段 | 含义 |
|---|---|
| `method` | HTTP 方法 |
| `url` | 请求 URL |
| `headers` | 请求头（多为 `[[name, value], ...]`） |
| `body` | 请求体字符串 |
| `cookie` | 相关 cookie（有则带） |
| `type` | 如 `navigation`；普通 XHR/fetch 可能无此字段 |
| `timestamp` | 时间戳（有则带） |

和 `add_resource` 的分工：

|  | `add_resource` | `netLog.entries` |
|---|---|---|
| 干什么 | **灌假响应**，让 XHR/fetch 读到 body | **记账**，看脚本发了哪些请求 |
| 何时用 | 要把接口跑通 | 要摸请求链 / 对齐真机抓包 |

JS 侧随时读：

```
window.__iv8__.netLog.entries          // 数组
window.__iv8__.netLog.entries.length
window.__iv8__.netLog.help()           // 控制台打印字段说明
```

## 10. iv8 浏览器环境配置与指纹伪装

iv8 内置一套基于 Chrome 桌面 / Windows 基线的默认指纹（200+ 字段），不传 `environment` 即开箱可用。 通过 `environment` 字典可选择性覆盖指纹字段，未覆盖的保持默认值。 对外暴露的浏览器版本号由 `navigator.userAgent` / `navigator.userAgentData` 等字段决定，由用户随时覆盖 —— 内置默认值仅作开箱即用兜底，**不构成对"项目锚定哪个 Chrome 版本"的承诺**。

- **environment**：浏览器/设备画像（「浏览器长什么样」）→ 直接映射到 JS 可观测属性
- **config**：框架行为（「引擎怎么跑」）→ 时间模式、权限、Canvas/WebGL 行为等；只支持标量，数组型（如 `navigator.languages`）必须走 `environment`

**可定制类指纹名单**

> 数据来源：`iv8.JSContext.get_defaults()`。下面 **10.2 把常用 environment 写全（含默认值）**；数组型见 10.4。冷门字段再用 `get_defaults()` 自查。

当前环境指纹路径约 **297** 项（不含 `config.*`）。`environment={"a":{"b":x}}` → JS 可读路径 `a.b`。

### 10.1 分类一览

| 分类 | 项数 | 映射到 JS 侧 |
|---|---|---|
| `audioContext` | 2 | AudioContext |
| `batteryManager` | 4 | BatteryManager |
| `canvas` | 5 | Canvas 指纹输出 |
| `chrome` | 6 | chrome.loadTimes |
| `clipboard` | 1 | Clipboard |
| `credentials` | 2 | Credentials |
| `document` | 9 | Document |
| `geolocation` | 3 | Geolocation |
| `history` | 2 | History |
| `html` | 4 | HTMLImageElement 默认 |
| `location` | 8 | Location |
| `managed` | 7 | Managed Device |
| `media` | 17 | Media Queries（matchMedia） |
| `navigator` | 33 | Navigator / UA / 网络 / Client Hints |
| `performance` | 5 | Performance |
| `screen` | 11 | Screen |
| `storage` | 7 | Storage（estimate） |
| `video` | 4 | Video |
| `visualViewport` | 5 | VisualViewport |
| `webgl` | 71 | WebGL |
| `webgl2` | 24 | WebGL2 |
| `webgpu` | 43 | WebGPU |
| `webrtc` | 2 | WebRTC ICE |
| `window` | 21 | Window 视口与窗口 |
| `xhr` | 1 | XHR |

### 10.2 常用 `environment`（含默认值）

日常对齐指纹，优先改这些。未列出的路径保持引擎默认，可用：

```
import iv8
for k, v in sorted(iv8.JSContext.get_defaults().items()):
    if not k.startswith("config."):
        print(k, "=", repr(v))
```

#### `navigator`（UA / 硬件 / Client Hints）

| 路径 | 默认值 | 说明 |
|---|---|---|
| `navigator.userAgent` | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ... Chrome/...` | UA；决定对外浏览器版本观感 |
| `navigator.appVersion` | 与 UA 配套的截断串 | 历史字段，常和 UA 一起改 |
| `navigator.platform` | `Win32` | 如 `Win32` / `MacIntel` / `Linux x86_64` |
| `navigator.vendor` | `Google Inc.` | Chrome 常见值 |
| `navigator.vendorSub` | `""` | 桌面 Chrome 多为空 |
| `navigator.language` | `zh-CN` | 首选语言 |
| `navigator.languages` | 见 10.4 | **数组型**，只能走 environment |
| `navigator.hardwareConcurrency` | `8` | 逻辑 CPU 核数 |
| `navigator.deviceMemory` | `8.0` | 设备内存 GB（近似） |
| `navigator.maxTouchPoints` | `0` | 触控点数；桌面多为 0 |
| `navigator.webdriver` | `false` | 自动化标记，保持 `false` |
| `navigator.cookieEnabled` | `true` | 是否启用 cookie |
| `navigator.onLine` | `true` | 是否在线 |
| `navigator.pdfViewerEnabled` | `true` | PDF 查看器 |
| `navigator.connection.downlink` | `10.0` | 下行带宽估计 Mbps |
| `navigator.connection.effectiveType` | `4g` | 有效网速档 |
| `navigator.connection.rtt` | `50.0` | 往返时延 ms |
| `navigator.connection.type` | `wifi` | 网络类型 |
| `navigator.userAgentData.architecture` | `x86` | UA-CH 架构 |
| `navigator.userAgentData.bitness` | `64` | UA-CH 位数 |
| `navigator.userAgentData.mobile` | `false` | 是否移动端 |
| `navigator.userAgentData.platform` | `Windows` | UA-CH 平台名 |
| `navigator.userAgentData.platformVersion` | `10.0.0` | UA-CH 平台版本 |

#### `screen` / `window`（几何）

| 路径 | 默认值 | 说明 |
|---|---|---|
| `screen.width` | `1920` | 屏幕宽 |
| `screen.height` | `1080` | 屏幕高 |
| `screen.availWidth` | `1920` | 可用宽 |
| `screen.availHeight` | `1040` | 可用高 |
| `screen.colorDepth` | `24` | 色深 |
| `screen.pixelDepth` | `24` | 像素深度 |
| `screen.orientation.type` | `landscape-primary` | 方向类型 |
| `window.innerWidth` | `1920` | 视口内宽 |
| `window.innerHeight` | `969` | 视口内高 |
| `window.outerWidth` | `1920` | 窗外宽 |
| `window.outerHeight` | `1040` | 窗外高 |
| `window.devicePixelRatio` | `1.0` | 设备像素比 |
| `window.isSecureContext` | `true` | 安全上下文 |

#### `location`

| 路径 | 默认值 | 说明 |
|---|---|---|
| `location.href` | `about:blank` | 完整 URL |
| `location.origin` | `""` | 源 |
| `location.protocol` | `https:` | 协议 |
| `location.hostname` | `localhost` | 主机名 |
| `location.pathname` | `/` | 路径 |
| `location.port` | `""` | 端口 |
| `location.search` | `""` | 查询串 |
| `location.hash` | `""` | hash |

#### `webgl` / `canvas` / `chrome`（指纹向）

| 路径 | 默认值 | 说明 |
|---|---|---|
| `webgl.UNMASKED_VENDOR_WEBGL` | `Google Inc. (NVIDIA)` | GPU 厂商串 |
| `webgl.UNMASKED_RENDERER_WEBGL` | `ANGLE (NVIDIA, NVIDIA GeForce GTX 1650 ...)` | GPU 渲染器串 |
| `canvas.fingerprint.toDataURL.png` | `""` | 固定 png 指纹；空=走引擎 |
| `canvas.fingerprint.toDataURL.jpeg` | `""` | 固定 jpeg 指纹 |
| `canvas.toDataURL` | `""` | 环境级覆盖（也可用 `config.canvas.toDataURL`） |
| `chrome.loadTimes.connectionInfo` | `h2` | chrome.loadTimes 连接信息 |
| `chrome.loadTimes.npnNegotiatedProtocol` | `h2` | NPN/协议协商 |
| `chrome.loadTimes.wasFetchedViaSpdy` | `true` | 是否 SPDY/h2 |
| `chrome.loadTimes.wasNpnNegotiated` | `true` | 是否协商成功 |

分类项数见 10.1（`webgl` / `webgpu` 字段最多，冷门项用上面的 `get_defaults()` 拉）。

### 10.3 常用 `config`（行为，不是画像）

`config` 只支持标量；数组型指纹只能放 `environment`。

| 路径 | 默认 | 说明 |
|---|---|---|
| `time.mode` | `logical` | `logical` 虚拟时钟 / `system` 墙钟 |
| `canvas.toDataURL` | `""` | 非空则覆盖 canvas 输出 |
| `canvas.context.2d.enabled` | `true` | 是否允许 2d |
| `canvas.context.webgl.enabled` | `true` | 是否允许 webgl |
| `canvas.context.webgl2.enabled` | `true` | 是否允许 webgl2 |
| `webgl.fingerprint.mode` | `clear` | `clear` / `seeded` |
| `webgl.fingerprint.seed` | `""` | seeded 时的种子 |
| `permissions.geolocation` | `prompt` | `granted` / `denied` / `prompt` |
| `wasm.streaming.strictMime` | `true` | streaming 路径 MIME（日常可忽略） |

其余 `features` / `security` / `cookies` / `streams` / `iframe` 等同样用 `get_defaults()` 查 `config.*`。

### 10.4 补充（数组型等）

| 指纹路径 | 默认值 | 说明 |
|---|---|---|
| `navigator.languages` | `["en-US","en"]`（运行时语言基线可能为 zh-CN 系） | 数组型；只能走 `environment`，不能塞进仅标量的 `config` |

### 10.5 用法示例

```
import iv8

with iv8.JSContext(
    environment={
        "navigator": {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "platform": "Win32",
            "hardwareConcurrency": 8,
            "webdriver": False,
        },
        "screen": {"width": 1920, "height": 1080},
        "webgl": {
            "UNMASKED_VENDOR_WEBGL": "Google Inc. (NVIDIA)",
            "UNMASKED_RENDERER_WEBGL": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1650 ...)",
        },
    },
    config={
        "time": {"mode": "logical"},
        "permissions": {"geolocation": "granted"},
        "webgl": {"fingerprint": {"mode": "clear"}},
    },
) as ctx:
    print(ctx.eval("navigator.userAgent"))
    print(ctx.eval("screen.width"))
```

拉取全量路径与当前默认值：

```
for path, value in sorted(iv8.JSContext.get_defaults().items()):
    print(f"{path} = {value!r}")
```

## 11. iv8 多线程与 Isolate 隔离

### 11.1 结构

```
Python 进程
├── 线程 A
│     └── JSContext₁ ──► Isolate₁ ──► window / document / navigator …
├── 线程 B
│     └── JSContext₂ ──► Isolate₂ ──► 另一套全局（互不看见₁的 var）
└── 同线程也可再开
      └── JSContext₃ ──► Isolate₃
```

规则：

- **一 Context = 一 Isolate**（独立堆、独立全局）
- Context 之间 `var` / DOM / 指纹 **不串**
- 多线程跑 JS **不用**再给 V8 加锁
- `eval` 跑 JS 时 **放 GIL**；`expose` 回调 Python 时 **拿回 GIL**

```
ctx.eval(js)
  → 放 GIL → V8 执行
      →（JS 调 __iv8__.data.fn）拿 GIL → Python → 放 GIL
  → 返回 → 拿回 GIL
```

### 11.2 最小源码：多线程

```
import threading
import iv8

def run(i):
    with iv8.JSContext(environment={
        "navigator": {"userAgent": f"Bot/{i}"}
    }) as ctx:
        print(i, ctx.eval("navigator.userAgent"), ctx.eval(f"{i}*{i}"))

ts = [threading.Thread(target=run, args=(i,)) for i in range(4)]
for t in ts: t.start()
for t in ts: t.join()
```

### 11.3 最小源码：同线程多 Context

```
import iv8

c1 = iv8.JSContext(environment={"navigator": {"userAgent": "UA-1"}})
c2 = iv8.JSContext(environment={"navigator": {"userAgent": "UA-2"}})
c1.eval("var secret = 'a'")
c2.eval("var secret = 'b'")
print(c1.eval("navigator.userAgent"), c1.eval("secret"))  # UA-1 a
print(c2.eval("navigator.userAgent"), c2.eval("secret"))  # UA-2 b
c2.close(); c1.close()
```

### 11.3.1 啥时候开多线程、啥时候收着

**适合多线程（纯 JS 算）：** 每个线程一个 `JSContext`，里面只跑加密 / 循环 / 签名，**不调**`__iv8__.data` 去 Python。V8 执行时会放掉 GIL，几条线程可以一起算。

```
import threading
import iv8

def run_sign(i):
    with iv8.JSContext() as ctx:
        # 全程在 V8 里算，不进 Python 桥
        h5st = ctx.eval("""
            (function () {
                var s = '';
                for (var k = 0; k < 200000; k++) s += Math.sin(k);
                return s.slice(0, 16);
            })()
        """)
        print(i, h5st)

ts = [threading.Thread(target=run_sign, args=(i,)) for i in range(8)]
for t in ts: t.start()
for t in ts: t.join()
# 8 路并行算，比单线程快一截（官方算密测约 4.7x）
```

**要控并发（HTTP 桥）：** JS 一旦 `__iv8__.data.pyGet(url)`，就进 Python，拿着 GIL 同步 `requests.get`。此时：

- 其它线程就算有自己的 Context，也要等这把 GIL
- 10 个线程同时桥接，往往变成「排队发 HTTP」，还容易打满代理连接数

```
# ❌ 别这样：8 线程 × 每线程狂刷 expose HTTP
def bad(i):
    with iv8.JSContext() as ctx:
        def py_get(url):
            return requests.get(str(url), timeout=10).text  # 持 GIL 整段阻塞
        ctx.expose(py_get, "pyGet")
        ctx.eval("""
            for (var k = 0; k < 50; k++)
                __iv8__.data.pyGet('https://httpbin.org/get?i=' + k);
        """)

# ✅ 这样：Python 先拉（自己控并发池），灌进 add_resource，JS 只读假表、不撞 GIL
def good(urls):
    with iv8.JSContext() as ctx:
        ctx.eval("""
            window.__iv8__.page.load({
                html: '<html><body></body></html>',
                baseURL: 'https://example.com'
            });
        """)
        for url in urls:
            body = requests.get(url, timeout=10).text  # 在 Python 侧拉，可用线程池限 4 路
            ctx.add_resource(url, body, 200, {"content-type": "application/json"})
        ctx.eval("""
            var xhr = new XMLHttpRequest();
            xhr.open('GET', 'https://api.example.com/a', false);
            xhr.send();
        """)
```

若业务必须 JS 里调桥：线程数开小（例如 2～4），或桥函数里自己做限流；不要「一站点一线程、线程里再循环 100 次 pyGet」。

口诀：**纯算多开线程；上网 Python 先拉再灌表，少让 JS 进 expose。**

### 11.4 性能开销

| 维度 | 指标 | 约数 |
|---|---|---|
| 速度 | `JSContext` 创建 + eval + 销毁 | ~2.4 ms / 次（约 400+ ctx/s，机型相关） |
|  | 简单 `eval("1+1")` | ~95 万 ops/s |
|  | 浏览器 API（navigator / DOM / crypto） | 34～57 万 ops/s |
|  | 大页 DOM 解析（~440 KB） | ~7 ms / 页 |
| 内存 | `import iv8` + 首个 Context | +约 15 MB |
|  | 批量循环峰值增量 | ~9 MB |
| 多线程 | 2 / 4 / 8 线程加速比（算密 JS） | ~1.86x / 3.26x / 4.71x |

```
import time, iv8
N = 100
t0 = time.perf_counter()
for _ in range(N):
    with iv8.JSContext() as ctx:
        ctx.eval("1+1")
print(f"平均 {(time.perf_counter()-t0)/N*1000:.1f} ms/次")
```

本机实测创建100个isolate v8上下文（iv8 0.1.4 / macOS）：

```
N=100
总耗时: 0.237s
平均 2.4 ms/次
约 422 ctx/s
```

（官方 README 另一台机器约 ~3.3 ms/次，硬件不同会漂。）

实践：Context 轻、可勤换；多站点并行优先多线程；只要 DOM 用 `innerHTML` 往往比 `page.load` 便宜；量产用 `prod`。

口诀：**一 Context 一 Isolate；跑 JS 放 GIL；创建便宜可勤换；重活多线程，重桥少并发。**

## 12. 跑 WebAssembly

iv8 内嵌的是 Chromium 同款 V8，**`window.WebAssembly` 是原生能力**（不是自己补的假对象）。签名 / 风控脚本里的 `.wasm`，优先 **黑盒直接跑**，对齐 JS import 与导出即可。

### 12.1 能 / 不能

**能**

- `WebAssembly` / `Module` / `Instance` / `Memory` / `Table`（`toString` 为 `[native code]`）
- 同步：`new Module(bytes)` + `new Instance(mod, imports?)`
- 异步：`instantiate` / `compile`（配合 `eventLoop.drain*`）
- `expose` 字节列表，或 `add_resource` 灌 `.wasm`
- `fetch(...).arrayBuffer()` 再 `instantiate`；同步 XHR `arraybuffer` 再 `Module`

**不能（或不可靠）**

- `instantiateStreaming` / `compileStreaming`（`Response.body` 为空会报错）
- `structuredClone(Module)` / 把 Module 传给 Worker

回退口诀：**站点写了 streaming，就改成 `arrayBuffer` + `instantiate`（或同步 Module）。**

相关配置（一般不用动）：`config.wasm.streaming.strictMime`（默认 `true`，streaming 路径才看 MIME）。

### 12.2 最小可跑：同步 Module（推荐上手）

下面是一个导出 `add(i32,i32)->i32` 的最小模块（无需外部 `.wasm` 文件）：

```
import iv8

# (module (func (export "add") (param i32 i32) (result i32)
#   local.get 0 local.get 1 i32.add))
WASM_ADD = bytes([
    0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00,
    0x01, 0x07, 0x01, 0x60, 0x02, 0x7f, 0x7f, 0x01, 0x7f,
    0x03, 0x02, 0x01, 0x00,
    0x07, 0x07, 0x01, 0x03, 0x61, 0x64, 0x64, 0x00, 0x00,
    0x0a, 0x09, 0x01, 0x07, 0x00, 0x20, 0x00, 0x20, 0x01, 0x6a, 0x0b,
])

with iv8.JSContext() as ctx:
    ctx.expose(list(WASM_ADD), "wasmBytes")
    result = ctx.eval("""
        (function () {
            var bytes = new Uint8Array(__iv8__.data.wasmBytes);
            if (!WebAssembly.validate(bytes)) return { ok: false };
            var mod = new WebAssembly.Module(bytes);
            var inst = new WebAssembly.Instance(mod);
            return {
                ok: true,
                brand: Object.prototype.toString.call(mod),  // [object WebAssembly.Module]
                add: inst.exports.add(2, 3),                 // 5
            };
        })()
    """, to_py=True)
    print(result)
```

有真实文件时，把 `WASM_ADD` 换成：

```
WASM_ADD = open("add.wasm", "rb").read()
```

### 12.3 带 JS import（WASM 回调 Python/JS）

很多站点是「WASM 调 JS 取时间 / 打日志 / 读写内存」。import 名字和签名必须对齐：

```
import iv8

# import env.hello; export run → call hello
WASM_HELLO = bytes([
    0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00,
    0x01, 0x04, 0x01, 0x60, 0x00, 0x00,
    0x02, 0x0d, 0x01, 0x03, 0x65, 0x6e, 0x76,
          0x05, 0x68, 0x65, 0x6c, 0x6c, 0x6f, 0x00, 0x00,
    0x03, 0x02, 0x01, 0x00,
    0x07, 0x07, 0x01, 0x03, 0x72, 0x75, 0x6e, 0x00, 0x01,
    0x0a, 0x06, 0x01, 0x04, 0x00, 0x10, 0x00, 0x0b,
])

with iv8.JSContext() as ctx:
    ctx.expose(list(WASM_HELLO), "wasmBytes")
    logs = ctx.eval("""
        (function () {
            var logs = [];
            var bytes = new Uint8Array(__iv8__.data.wasmBytes);
            var inst = new WebAssembly.Instance(new WebAssembly.Module(bytes), {
                env: { hello: function () { logs.push('hello world'); } }
            });
            inst.exports.run();
            return logs;
        })()
    """, to_py=True)
    print(logs)  # ['hello world']
```

要对齐真站导出 / 导入边界，可在编译后查：

```
WebAssembly.Module.exports(mod)
WebAssembly.Module.imports(mod)
```

### 12.4 从「假 URL」加载 `.wasm`（页面常见写法）

站点经常是 `fetch('/x.wasm')` 或 XHR。iv8 不上真网，用 **离线资源表** 灌二进制：

```
import iv8

WASM_ADD = open("add.wasm", "rb").read()  # 或前面的最小字节

with iv8.JSContext() as ctx:
    ctx.eval("""
        window.__iv8__.page.load({
            html: '<html><body></body></html>',
            baseURL: 'https://example.com'
        });
    """)
    ctx.add_resource(
        url="https://example.com/add.wasm",
        body=WASM_ADD,
        status=200,
        headers={"content-type": "application/wasm"},
    )

    # 写法 A：同步 XHR（最省事）
    print(ctx.eval("""
        (function () {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', 'https://example.com/add.wasm', false);
            xhr.responseType = 'arraybuffer';
            xhr.send();
            var inst = new WebAssembly.Instance(new WebAssembly.Module(xhr.response));
            return inst.exports.add(9, 1);
        })()
    """))  # 10

    # 写法 B：fetch + arrayBuffer（异步，要 drain）
    ctx.eval("""
        (async function () {
            var buf = await (await fetch('https://example.com/add.wasm')).arrayBuffer();
            var r = await WebAssembly.instantiate(buf);
            globalThis.__add = r.instance.exports.add(1, 2);
        })();
    """)
    ctx.eval("window.__iv8__.eventLoop.drainMicrotasks()")
    ctx.eval("window.__iv8__.eventLoop.drain()")
    print(ctx.eval("globalThis.__add"))  # 3
```

**不要**依赖：

```
await WebAssembly.instantiateStreaming(fetch(url))  // iv8 里 Response.body 为空会炸
```

改成上面的 `arrayBuffer` + `instantiate` 即可。

### 12.5 实战注意

1. **优先黑盒**：把抓到的 `.wasm` 原样灌进 Context，用 JS 壳 + import 对齐；默认别反汇编 opcode。
2. **字节从 Python 进**：`open(..., "rb").read()` → `expose(list(bytes), ...)` 或 `add_resource(..., body=bytes)`。
3. **异步路径**记得 `drainMicrotasks` / `drain`（或 `advance`），否则 `await` 结果还没落。
4. wasm-bindgen 一类常要 `TextEncoder` / `TextDecoder`；缺了就在 `mode="debug"` 里看「疑似缺失API」。
5. `config.wasm.streaming.strictMime` 只影响 streaming；既然 streaming 暂不可靠，日常可忽略。

口诀：**expose/add_resource 灌字节 → Module/instantiate 黑盒跑；streaming 不行就 arrayBuffer。**

## 13. 应用场景

iv8 已经能覆盖多数日常场景：补环境、跑混淆 / 签名脚本、指纹对齐、调试探针。

**Canvas 指纹**\
**能**：2D / `toDataURL` / `toBlob`；可用 `environment` / `config.canvas` 固定输出。\
注意：`toDataURL` 为空表示未灌固定内容，填 png/jpeg 即可。

**WebAssembly**\
**能**：`Module` / `Instance` / `instantiate`；本地字节或 `add_resource` + XHR / `fetch.arrayBuffer`。\
**不能**：`instantiateStreaming`（`Response.body` 为空）；`Module` 不能 `structuredClone`。

**Worker**\
**能**：`data:text/javascript,...`；或 `https://.../w.js`（先 `page.load` 再 `add_resource`）。\
**不能**：`blob:`（缺 `URL.createObjectURL`）。

**SharedWorker**\
**能**：构造存在；`data:` / `https:`（同样要灌资源），有 `sw.port`。\
**不能**：`blob:`（同上）。

**window.chrome**\
**能**：有对象；`loadTimes` / `csi` / `app`。可用 `environment.chrome.loadTimes.*` 配。

**RuntimeContext**\
每个 `JSContext` 一套运行时上下文；创建时传 `environment` / `config`。

**Service Worker**\
有构造与 `navigator.serviceWorker.register`；接口面可用，别当完整后台拦截栈。

**其它用法**：

1. AST 辅助还原（找字符串表、读解码器再替换）。
2. 在可控 V8 + 浏览器壳里调试脚本摸了哪些环境（`mode="debug"` / DevTools / `watch_apis`，先看 `疑似缺失API` 再按需断点watch_apis）。
3. 借鉴 Isolate / RuntimeContext / 离线网络 / 可信输入等分层，完善自有补环境框架或写 V8 插件，我参考其思路写了几个v8插件。

网络侧：**不能**直接发真 HTTP；XHR / fetch 走离线资源表。真上网用 `expose` 挂 `requests` / `curl_cffi`，或 Python 拉完再 `add_resource`。

## 14. 总结

以前要跑一段依赖浏览器的 JS，往往得开 Chrome，或者自己在 Node 里一点点补环境。\
iv8 换了条路：**在 Python 里嵌一个带浏览器壳的 V8**——有 `window` / `document`，能点能拖，能调定时器，也能挂指纹, 相较于传统的补环境方案，iv8的思路还是很值得研究的。传统方案基本都是双进程，Python + Node（jsdom / 自己补环境 / execjs 之类）， 现在是全部都在一个进程里面，性能开销也会缩减。

你会的几件事基本都在里面：

- 把页面 HTML 灌进去跑脚本
- 调试、看缺了哪个 API
- 用 Python 帮忙发真实请求，再塞回 JS
- 多开几个环境并行算签名
- 黑盒跑 `.wasm`（`Module` / `instantiate`；streaming 先回避）

它**不是**完整 Chrome（比如默认不上真网、复杂排版有限），但对「跑混淆、出参数、对探针」这类活，已经够当一台**小型浏览器**用了。
