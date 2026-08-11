# navigator 子对象参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

navigator 子对象通常是独立接口：集合、权限状态、设备管理器、Promise 返回对象或事件目标。不能把它们补成普通 `{}`。

## 检测面

- userAgentData：`brands`（有序对象数组）、`mobile`、`platform`、high entropy 字段表；`getHighEntropyValues(keys)` 返回 Promise，resolve 对象只包含请求的字段和必要基础字段；mobile/platform 与顶层 navigator profile 一致。
- permissions：`query(desc)` 返回 Promise，resolve 值为 PermissionStatus（`name/state/onchange`）；state 影响 geolocation/media/clipboard 等 API 的成功或失败；reject 是合理错误对象，不是同步 throw 字符串。
- plugins/mimeTypes：PluginArray/MimeTypeArray 集合语义；`mimeType.enabledPlugin` 回指 plugin；`plugins[name]`、`item()`、`namedItem()` 与索引项一致。
- connection：`effectiveType/rtt/downlink/saveData` 属于同一网络状态；`addEventListener('change')` 走 EventTarget；多次读取保持同一 NetworkInformation 状态来源。
- mediaDevices：`enumerateDevices()` 返回 Promise resolve 设备数组（kind/label/deviceId/groupId 成组）；`getUserMedia()` 返回 Promise，resolve/reject 受权限和安全上下文影响。
- geolocation：`getCurrentPosition(success, error, options)` 是回调 API；成功参数是含 coords/timestamp 的 position 对象；失败参数是 GeolocationPositionError 语义对象；`watchPosition` 返回 watch id、`clearWatch` 取消。
- 其余：`navigator.storage.estimate()` Promise resolve `{usage, quota}`；`credentials.get/create/store` Promise 返回 credential 或 null；`clipboard.readText/writeText` Promise；`serviceWorker.ready` Promise、`controller` 可为 null 或对象；`getBattery()` Promise resolve BatteryManager。
- 身份：子对象状态与 navigator 顶层 profile、permissions、页面 URL、安全上下文一致；Promise resolve 的对象后续被读时保持对象身份和字段；PermissionStatus、NetworkInformation、BatteryManager 可作为 EventTarget。

## 常见坑

- `permissions.query` 同步返回 `{state: "granted"}`，Promise 语义断裂。
- `userAgentData.getHighEntropyValues` 返回固定全字段对象，忽略 keys 参数。
- `mediaDevices.enumerateDevices` 同步返回数组。
- `serviceWorker.ready` 是普通对象，缺 Promise 语义。
- plugin/mimeType 没有双向引用，enabledPlugin 断裂。
- connection 字段随机组合，rtt 与 effectiveType 矛盾。
- geolocation 错误回调不是 Error 语义对象，目标读字段失败。

## 观察优先级

- 先看浏览器证据里子对象入口：目标 query 什么 permission、读哪些 device、调用哪些 Promise API。
- 记录 keys 参数与 resolve 字段，确认本地执行层返回范围。
- 核对子对象状态与顶层 profile、权限、URL 安全上下文的一致性。
- 记录 Promise resolve 对象的后续读取，保持对象身份稳定。
- 未触达的子对象不预补；触达后按最小接口面实现。

## 补环境要点

- Promise 类接口（query / getHighEntropyValues / enumerateDevices / getBattery 等）保持异步形态。
- resolve 对象按证据实现字段范围，getHighEntropyValues 只返回请求 keys 与基础字段。
- PermissionStatus 状态与 media / geolocation / clipboard 行为配对一致。
- plugin / mimeType 双向引用与集合语义一起补。
- connection / battery 字段组合与状态来源一致，change 先更新后回调。
- 子对象状态与顶层 profile、权限、URL 安全上下文对齐后再定值。
