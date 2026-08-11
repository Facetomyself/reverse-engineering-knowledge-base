# Performance / Timing / Observer 参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

performance 和 observer 是时间源、entry 列表、异步 record 队列和回调调度系统。它们的内容要能解释时间差、资源条目、observer 回调和事件时间戳。

## 检测面

- 时间状态：`timeOrigin`、当前 monotonic time、`performance.now()` 调用序列、event `timeStamp` 来源、timer id 与队列、microtask 队列；`now()` 不应永远固定，多次调用差值被读时要保持递增或符合当前样本。
- PerformanceEntry：`name/entryType/startTime/duration`；Navigation/Resource/Paint 子类再带对应字段；`getEntries()`、`getEntriesByType(type)`、`getEntriesByName(name)` 从同一 entry store 派生。
- PerformanceObserver：callback、observed entryTypes、pending records、connected/disconnected 状态；`observe()` 注册类型，entry 产生后异步进入 records；`takeRecords()` 返回并清空 pending；`disconnect()` 停止接收。
- MutationObserver record：`type/target/addedNodes/removedNodes/attributeName/oldValue`。
- ResizeObserver entry：`target/contentRect/borderBoxSize/contentBoxSize/devicePixelContentBoxSize`。
- IntersectionObserver entry：`target/boundingClientRect/intersectionRect/rootBounds/intersectionRatio/isIntersecting/time`。
- 任务队列语义：Promise.then 与 queueMicrotask 属 microtask；setTimeout/setInterval 属 timer 队列；observer callback、消息事件、事件 dispatch 的顺序来自同一调度模型；timer id 可清理，clear 后不再触发。
- 一致性：event `timeStamp` 与 performance 时间源不冲突；resource timing 的 URL 与资源/request 对象一致；observer entry 的 target/rect/time 与 DOM/layout 状态一致。

## 常见坑

- `performance.now()` 每次固定返回 0，目标用时间差判断失败。
- `getEntriesByType` 永远空数组，目标读取资源 timing 时拿不到条目。
- observer `observe` 空函数，callback 永不触发。
- `takeRecords()` 不消费 records，重复返回同一批。
- timer 和 microtask 顺序颠倒，Promise 链与定时器时序错位。
- observer entry 的 target 不是真实 DOM 节点身份。
- clearTimeout 后回调仍触发。

## 观察优先级

- 先看浏览器证据里时间入口：`performance.now()` 差值、getEntriesByType、observer 注册还是事件 timeStamp。
- 记录目标读取的 entryType 与字段（resource timing 的 name/initiatorType/duration）。
- 核对 observer 注册的 entryTypes 与回调消费方式（takeRecords 或回调参数）。
- 记录事件 timeStamp 与 now() 的相对关系，确认本地执行层时间源一致。
- 只补目标链路触达的 entry 类型与调度路径；未触达的 observer 类型不预建。

## 补环境要点

- 时间源统一：now()、事件 timeStamp、RAF 回调同一单调递增来源。
- entry store 集中维护，getEntries 族从同一 store 派生。
- observer 的 observe / takeRecords / disconnect 按状态机实现，回调异步触发。
- timer 与 microtask 队列顺序不颠倒，clear 后不再触发。
- observer entry 的 target 是真实节点身份，rect / time 与 layout 同源。
- 未触达的 entry 类型不预建。
