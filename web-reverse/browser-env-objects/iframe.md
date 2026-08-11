# iframe / 子 realm 参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

iframe 是子浏览器上下文，不只是一个 DOM 元素。`contentWindow`、`contentDocument`、子 `location/navigator/screen/storage` 和主子窗口引用关系必须作为一个子 realm 建模。

## 检测面

- iframe 元素属性：`src/name/sandbox/width/height`；子 window、子 document、子 location、子 navigator/screen/visualViewport 状态；与主窗口共享或隔离的 cookie/storage 引用；load/readystatechange 事件状态。
- 派生一致性：`iframe.contentWindow.document === iframe.contentDocument`；`contentDocument.defaultView === contentWindow`；`contentWindow.top` 指向主 top；`contentWindow.parent` 指向直接父 window；`contentWindow.window/self/globalThis` 指向子 window 自己。
- 子文档独立：子 document 的 `URL/readyState/currentScript` 独立于主 document。
- src 与加载语义：写 `iframe.src` 影响子 location；`about:blank`、相对 URL、完整 URL 走 location 解析语义；插入 DOM 后是否触发 load/readystatechange 由子 document 生命周期状态决定。
- 脚本执行上下文：iframe 内脚本执行时 `currentScript/defaultView/location` 属于子 realm。
- storage/cookie：同源 iframe 可能共享 cookie/localStorage/sessionStorage，也可能按上下文隔离；`document.cookie` 按子 document URL 作用域判断可见 cookie。
- 身份关系：同一 iframe 多次读 `contentWindow/contentDocument` 稳定；主 `frames[index]/frames[name]` 与 `contentWindow` 一致；postMessage 链路的 `event.source` 指向实际发送方 window。

## 常见坑

- `contentWindow` 是普通 `{}` 或全局 Proxy 外壳，目标访问子对象全断。
- `contentDocument` 直接等于主 document，子 realm 身份错误。
- 子 window 的 top/parent/self/window 关系错误。
- iframe storage/cookie 直接复制主状态，同轮读写不一致。
- 在 iframe 元素创建、currentScript 附着或 DOM append 时提前执行目标脚本，加载顺序造假。
- `event.source` 用主 window 或空对象代替实际发送方。

## 观察优先级

- 先看浏览器证据里 iframe 入口：createElement('iframe')、frames 索引还是 postMessage 链路。
- 记录子 realm 被读取的对象清单（location/navigator/screen/storage/cookie），决定最小子 realm 内容。
- 核对子文档生命周期：目标何时读取 readyState/load，脚本在哪一刻执行。
- 核对 postMessage 的 source/ports 身份与消息顺序。
- 只补当前目标链路需要的最小子 realm 与身份关系，不搭完整 iframe 浏览器。

## 补环境要点

- 子 realm 按最小链路实现：只补目标触达的子 window / document / location / storage 面。
- 主子关系（top / parent / self / window）与 contentWindow / contentDocument 互指一致。
- 子文档 URL / readyState / currentScript 独立于主文档，不共用。
- storage / cookie 共享或隔离按子文档作用域决定，不默认复制主状态。
- postMessage 的 event.source / ports 指向实际发送方，不伪造身份。
- 不提前执行 iframe 内脚本；加载时序以当前链路证据为准。
