# Web 补环境浏览器对象参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 浏览器宿主对象（DOM/BOM/Web API）在本地执行层补环境时的对象级参考：每个对象的检测面、常见坑与观察优先级。配合证据链（浏览器事实 + 本地事实 + first divergence）使用。

## 用途

当本地执行层（Node 等）运行目标 JS 出现环境缺口、属性未定义、行为不一致时，先按对象检索本文档与子文档，再回到当前目标的浏览器证据核实真实值、descriptor、异常外观与调用顺序。文档只描述对象的通用知识面，不提供具体站点的补环境配方。

## 补环境纪律

- **证据驱动**：每个补入的值、字段、getter/setter、descriptor、prototype、异常外观与方法返回对象，都必须来自当前目标的浏览器事实；观察日志只用于发现本地缺口，不是真值来源。
- **五维度语义**：目标链路内禁止壳子式补环境。凡目标 JS 会继续读取、枚举、调用、比较或依赖的对象，都按证据补齐可观察语义——外观（`typeof` / `instanceof` / constructor / descriptor / 枚举结果 / `Symbol.toStringTag` / native-like `toString`）、内容（字段值 / 数组长度 / URL / cookie 与 storage 状态）、行为（方法入参 / 返回对象 / 副作用 / 异常类型与 message）、身份关系（同一对象多次读取是否稳定、owner / target / currentTarget / source / ports 引用）、时序状态（写入后读取、listener 顺序、microtask / timer / Worker 消息顺序）。
- **只补目标链路**：与目标参数生成、校验、注入、请求组装或最终验证无关的对象与指纹面，不因 trace 中存在或本地缺口提示就顺手补入。
- **批次推进**：先补目标链路触达的基础对象，再补方法入参与返回对象，最后才按证据补 canvas / webgl 等指纹面；目标已能出值时优先验证目标值，不继续扩张环境面。
- **禁止猜测式异步**：MessagePort / Worker / iframe `postMessage` 的消息顺序、`MessageEvent.source/ports`、transferable 与异步派发必须以目标链路证据为准；证据不足时记录缺口并暂停该项，不手写猜测式队列或同步假回调。
- **加载时机**：`currentScript`、script append/load、iframe 文档加载与 runtime 初始化不得过早触发；WebAssembly 命中时先归类加载方式、胶水层、imports/exports、memory/table 与业务入口，只补 JS 胶水层需要的宿主能力。

## 对象一览

| 对象 | 关键检测面 | 子文档 |
|------|-----------|--------|
| window | 全局属性/方法、self/top/parent/frames、构造器身份、`window.window === window` | [window.md](web-reverse-env-objects-reference/window.md) |
| document | `document.all`、`document.readyState`、节点工厂、`currentScript`、`referrer` | [document.md](web-reverse-env-objects-reference/document.md) |
| location | `href` / `host` / `origin` / `search` / `hash` 一致性、赋值副作用、`history` 联动 | [location.md](web-reverse-env-objects-reference/location.md) |
| navigator | `userAgent` / `platform` / `language` / `webdriver`、`mimeTypes` / `plugins`、vendor | [navigator.md](web-reverse-env-objects-reference/navigator.md) |
| navigator 子对象 | `geolocation` / `permissions` / `mediaDevices` / `connection` / `storage` 子面 | [navigator-subobjects.md](web-reverse-env-objects-reference/navigator-subobjects.md) |
| screen | `width` / `height` / `avail*` / `colorDepth` / `pixelDepth`、orientation | [screen.md](web-reverse-env-objects-reference/screen.md) |
| storage | `localStorage` / `sessionStorage` 同名/隔离、`getItem/setItem/removeItem/key` 行为、异常（SecurityError） | [storage.md](web-reverse-env-objects-reference/storage.md) |
| performance / timing | `performance.now`、`navigationStart`、`resourceTiming`、`getEntriesByType`、高精度时序检测 | [performance-timing.md](web-reverse-env-objects-reference/performance-timing.md) |
| DOM 节点 / 元素 | `nodeType` / `tagName` / `ownerDocument`、`parentNode` / `children` 身份、`attributes` | [dom-node-element.md](web-reverse-env-objects-reference/dom-node-element.md) |
| DOM 集合 | `HTMLCollection` / `NodeList` 类数组外观、`item` / `namedItem`、live 性 | [dom-collections.md](web-reverse-env-objects-reference/dom-collections.md) |
| 事件 / 输入 | `addEventListener` 顺序、`event.type` / `target` / `isTrusted`、键盘/鼠标坐标 | [event-input.md](web-reverse-env-objects-reference/event-input.md) |
| iframe | `contentWindow` / `contentDocument` 身份、跨域隔离、`postMessage` 目标、frame 遍历 | [iframe.md](web-reverse-env-objects-reference/iframe.md) |
| Worker / 消息 | `Worker` / `MessageChannel` / `MessagePort` / `postMessage` / transferable / `onmessage` 派发 | [worker-message.md](web-reverse-env-objects-reference/worker-message.md) |
| 网络（fetch / XHR） | `fetch` / `XMLHttpRequest` 原型面、请求边界捕获、`credentials` / 头一致性 | [network-fetch-xhr.md](web-reverse-env-objects-reference/network-fetch-xhr.md) |
| Canvas / WebGL | `getContext` 返回面、canvas 指纹方法集、WebGL 参数/扩展枚举、`toDataURL` | [canvas-webgl.md](web-reverse-env-objects-reference/canvas-webgl.md) |
| Audio 指纹 | `AudioContext` / `createOscillator` / `createAnalyser`、频率数组、`currentTime` | [audio-fingerprint.md](web-reverse-env-objects-reference/audio-fingerprint.md) |
| 密码学 | `crypto.subtle` / `getRandomValues`、`TextEncoder`、二进制编解码、native 外观 | [crypto-binary.md](web-reverse-env-objects-reference/crypto-binary.md) |
| CSS / 布局 / 字体 | `getComputedStyle`、`offset*` / `client*` 几何、字体枚举（`document.fonts`） | [css-layout-font.md](web-reverse-env-objects-reference/css-layout-font.md) |
| 权限 / 设备 | `navigator.permissions` / `geolocation` 模拟、`mediaDevices`、`deviceMemory` / `hardwareConcurrency` | [permissions-device.md](web-reverse-env-objects-reference/permissions-device.md) |
| 指纹面总览 | 22 维指纹（UA / Canvas / WebGL / Audio / 字体 / 硬件并发 / 屏幕 / WebRTC / 时区语言） | [fingerprint-overview.md](web-reverse-env-objects-reference/fingerprint-overview.md) |

## 使用边界

- 子文档只描述对象的通用检测面与常见坑；具体站点的真值必须来自当前目标证据，禁止套用其他站点的值。
- `document.all`、iframe/window 身份关系、Worker 通信是关键检测点，命中时必须优先按对应子文档核对。
- 本参考与 [web-reverse-products-index](./web-reverse-products-index.md) 配合使用：产品文档给出链路的优先观察点，对象文档给出对应宿主面的补齐纪律。
