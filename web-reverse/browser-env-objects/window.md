# window / WindowProxy 参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

`window` 是全局对象、宿主 API 容器和窗口关系入口。`WindowProxy` 不是普通对象；它要维持 `self/window/globalThis/top/parent/frames` 的身份关系，并承载 document、location、navigator、screen、history、storage、performance 等对象引用。

## 检测面

- 内部状态：自身全局对象引用、所属 document、location、navigator、screen/visualViewport、history、storage 引用、事件 listener 表、窗口尺寸和坐标状态、父子窗口关系 `top/parent/frames/opener`、全局构造器和宿主方法表。
- 主窗口派生：`window === self === globalThis`；`window.document.defaultView === window`；`window.location` 与 `document.location` 同一 URL 状态；`window.length` 由子 frame 数量派生；inner/outer/devicePixelRatio 与 screen/visualViewport 互相解释；`frames[i]`、`frames.length`、`iframe.contentWindow` 由子窗口集合派生。
- 方法与事件：`addEventListener/removeEventListener/dispatchEvent` 共享 EventTarget 语义；`requestAnimationFrame` 回调时间与 performance 时间源一致；`setTimeout/setInterval/queueMicrotask` 调度结果不与 Promise/消息时序冲突；`matchMedia(query)` 返回 MediaQueryList；`getComputedStyle(element)` 返回 CSSStyleDeclaration 语义对象。
- 全局属性外观：全局构造器是否存在、在哪一层、是否可枚举，属于 window 外观内容；宿主方法、构造器和实例对象要有合理的 name、prototype、可构造/不可构造语义。
- 子窗口关系：`child.window === child.self === child.globalThis`；`child.top` 指向主窗口，`child.parent` 指向直接父窗口；`iframe.contentWindow.document === iframe.contentDocument`；`document.defaultView` 回指所属 window。
- 主窗口与 iframe 子窗口是不同 window 状态，不能共用一份对象。

## 常见坑

- `window = global` 直接暴露 Node 私有全局（process/Buffer/require/module），目标特征探测即中。
- `top/parent/frames` 全部指向同一个空对象，窗口关系断裂。
- 只补 `innerWidth`，screen/visualViewport/outerWidth 不一致。
- 构造器只是名字表，没有 prototype、instanceof 和属性归属语义。
- 多次读取同一核心对象返回不同身份。
- globalThis 与 window 不互指，目标用 `globalThis === window` 探测失败。

## 观察优先级

- 先看浏览器证据里 window 入口：全局构造器使用、top/parent/frames 关系、定时器/RAF 还是 matchMedia。
- 记录目标使用的全局构造器清单与其调用方式（new/静态方法/属性）。
- 核对窗口关系：iframe 场景下 top/parent/self 的指向与 frames 索引。
- 记录 RAF/timer 回调与参数生成的时间关系。
- 只补目标链路触达的全局面与构造器；未触达的宿主 API 不预建。

## 补环境要点

- 全局身份关系（window / self / globalThis / top / parent / frames）优先于字段值对齐。
- 不把本地执行层私有全局暴露到 window 面。
- 全局构造器按目标触达清单补，带 prototype / instanceof / 可构造语义。
- 定时器、RAF、microtask 与消息时序来自同一调度模型。
- 主窗口与子窗口状态分离，iframe 子 realm 独立。
- 未触达的宿主 API 不预建。
