# navigator 对象参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

`navigator` 是浏览器身份、能力、权限、设备和上报接口的入口。顶层字段多是只读环境状态；部分字段返回复杂子对象或 Promise API。

## 检测面

- 身份 profile：UA 族 `userAgent/appVersion/platform/vendor`、语言 `language/languages`、自动化与能力 `webdriver/cookieEnabled/onLine`、硬件 `hardwareConcurrency/deviceMemory/maxTouchPoints`。
- 子对象入口：`userAgentData/connection/permissions/plugins/mimeTypes/mediaDevices/geolocation/storage/credentials/clipboard/serviceWorker`、`getBattery()`，读取后转对应子对象语义。
- 派生规则：`language` 与 `languages[0]` 一致；platform/vendor/userAgent/appVersion 属于同一浏览器身份组合；`webdriver` 的缺失、false、undefined 是不同可观察语义；`plugins.length`、`mimeTypes.length` 与集合内容来自同一 plugin store；`cookieEnabled` 与 cookie/storage 可用状态不冲突。
- 方法语义：`sendBeacon(url, body)` 返回 boolean，并记录一次上报意图或进入请求边界；`javaEnabled()` 存在时返回 boolean 且 native 外观与 Navigator 方法一致；顶层方法不应只返回 undefined。
- 外观：navigator 实例 `instanceof Navigator`、原型链、方法 name/length 与真实外观一致。

## 常见坑

- 只补 `userAgent/platform/language`，plugins/mimeTypes 等子对象读取即断。
- `languages` 是字符串而不是数组，目标遍历失败。
- 顶层字段与子对象从不同 profile 拼接，互相矛盾。
- `plugins/mimeTypes` 用普通数组，缺 item/namedItem/enabledPlugin。
- `sendBeacon` 空函数返回 undefined，目标 boolean 判断失败。
- `webdriver` 直接补 false，但缺失语义不同，目标用 `'webdriver' in navigator` 探测。
- iframe 子 window 直接复用主 window 身份对象而非共享 profile。

## 观察优先级

- 先看浏览器证据里 navigator 入口：顶层字段读取、子对象读取还是方法调用。
- 记录被读字段清单与顺序，确认哪些属于同一身份组合。
- 核对 `language/languages`、`plugins/mimeTypes`、`cookieEnabled` 的交叉一致性。
- 记录 `sendBeacon`/`javaEnabled` 的调用参数与返回消费方式。
- 子对象一旦被读，转对应子对象文档；未触达的子对象不预补。

## 补环境要点

- navigator profile 整体维护，顶层字段与子对象同源，不跨 profile 拼接。
- language / languages、plugins / mimeTypes、cookieEnabled 交叉一致。
- webdriver 的缺失 / false / undefined 语义按浏览器证据对齐。
- sendBeacon / javaEnabled 等方法有返回与 native 外观，不返回 undefined。
- 子对象被读后转对应子对象语义并保持稳定身份。
- iframe 子 window 共享 profile 但不复用主 window 身份对象。
