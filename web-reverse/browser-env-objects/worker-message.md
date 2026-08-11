# Worker / Message 参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

Worker 和 MessagePort 是异步消息通道。核心内容是独立全局上下文、消息队列、MessageEvent 内容、structured clone、transferable 和 source/ports 身份关系。

## 检测面

- Worker 状态：worker 脚本 URL 或固定脚本身份、内部 global scope、双向消息队列、listener/onmessage/onerror、关闭/终止状态；Worker 内部 `self` 是 WorkerGlobalScope，不是主 window，通常没有 document。
- Worker 内部全局：`self/location/navigator/crypto/performance`、timer/Promise/microtask、`postMessage/importScripts`；与主 window 可能共享 profile 但不是同一对象身份。
- MessageEvent：`data/origin/lastEventId/source/ports`；data 可为字符串、对象、ArrayBuffer、TypedArray、Blob；对象内容不能只 mock 顶层字段，目标继续读取的子对象也要保留。
- structured clone/transferable：普通对象按 structured clone 复制可克隆内容；函数、DOM 节点等不可克隆内容报错或被拒绝；ArrayBuffer 作 transferable 传递后发送方 buffer 可能 detached；MessagePort transfer 后端口所有权和可用状态改变。
- MessageChannel/MessagePort：port1/port2、两端消息队列、onmessage、listener 表、started/closed 状态；`port1.postMessage(data)` 异步投递到 port2，反之亦然；`close()` 后不再派发。
- BroadcastChannel：按 channel name 分组广播；SharedWorker 的 port 是 MessagePort 语义；ServiceWorker 的 `controller/ready/register` 组合是状态和 Promise。
- 一致性：`event.source` 指向消息来源对象；`event.ports` 是实际可通信端口；Worker 返回的对象进入目标参数后后续读取保持同一内容结构；消息时序与 Promise/microtask/timer 队列一致。

## 常见坑

- Worker 构造器存在但 `postMessage` 不投递任何消息，回调链断。
- `postMessage` 同步直接调用另一端回调，Promise/microtask/timer 顺序偏移。
- `MessageEvent.data` 是空对象，缺目标实际字段。
- `MessageEvent.source`、`origin`、`ports` 与真实消息来源不一致。
- Worker 内 `self` 直接指向主 window。
- ArrayBuffer transfer 后发送方状态不变，detach 语义缺失。
- MessagePort 没有 start/close 与双端关系。
- 手写猜测式全局消息队列冒充真实消息路径。

## 观察优先级

- 先看浏览器证据里消息入口：new Worker、MessageChannel、postMessage 还是 BroadcastChannel。
- 记录 data 的完整结构与字段，确认目标后续读取范围。
- 记录 transferable 清单与发送方 buffer 的后续使用。
- 核对消息时序与 microtask/timer 队列的相对顺序。
- 证据不足时只记录缺口和当前阻塞点，不把猜测式消息模型写入交付；只实现证据证明参与目标产出的消息路径。

## 补环境要点

- 消息路径只在证据证明参与目标产出时实现，不建猜测式全局队列。
- postMessage 异步投递，不同步调用另一端回调，时序与 microtask / timer 一致。
- MessageEvent 的 data 按目标读取范围实现，source / ports 指向真实来源。
- transferable 实现 detach 语义，发送方 buffer 状态改变。
- MessagePort 维护 started / closed 与双端关系。
- 证据不足时记录缺口与阻塞点，不写猜测式消息模型。
