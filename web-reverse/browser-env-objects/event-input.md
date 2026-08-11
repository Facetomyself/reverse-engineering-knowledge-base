# 事件与输入设备参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

事件系统由 EventTarget listener 表、事件对象字段、传播路径、默认行为状态和输入设备内容组成。事件不是 `{ type: "click" }`。

## 检测面

- EventTarget：listener 列表（type、callback、capture、once、passive、signal）、`onxxx` 属性回调、当前 dispatch 状态；`addEventListener/removeEventListener/dispatchEvent` 都操作这份状态。
- 事件基础字段：`type/target/currentTarget/eventPhase/bubbles/cancelable/defaultPrevented/composed/isTrusted/timeStamp`、propagation/immediate stopped 标记。
- 行为语义：`preventDefault()` 只在 cancelable 时改变 `defaultPrevented`；`stopPropagation()`/`stopImmediatePropagation()` 影响后续 listener；listener 内 `this` 通常等于 `currentTarget`。
- 传播：`target` 整次派发保持原始目标；`currentTarget` 随当前 listener 对象变化；`composedPath()` 返回 target 到 window 的路径数组，顺序与 DOM 树一致；捕获/目标/冒泡阶段影响执行顺序。
- 输入事件：Mouse/Pointer 的 clientX/Y、pageX/Y、screenX/Y 互相可解释，button/buttons、修饰键、pointerId/pointerType/pressure 成组；Touch 的 touches/targetTouches/changedTouches 是 TouchList 语义；Keyboard 的 key/code/keyCode/which 是同一按键状态的不同表现，修饰键与 `getModifierState` 一致；Wheel delta 成组；input 事件的 data/inputType/isComposing 来自输入状态；ClipboardEvent 的 clipboardData 是 DataTransfer 语义对象；DeviceMotion/Orientation 字段是设备状态对象。
- 时间语义：`timeStamp` 与性能时间源一致；事件时间顺序不倒置；事件回调写入的状态后续读取必须可见。

## 常见坑

- `addEventListener` 空函数无 listener 表，注册后回调永不触发。
- `dispatchEvent` 不设置 target/currentTarget，listener 内读取 undefined。
- `isTrusted` 随便写 true，与真实事件链矛盾。
- `composedPath()` 返回空数组或顺序错误。
- 鼠标/触摸坐标字段互相矛盾，目标交叉校验失败。
- `preventDefault` 不影响 defaultPrevented，或对不可取消事件也生效。
- 同步直接调用 listener 冒充异步派发，microtask/timer 顺序偏移。

## 观察优先级

- 先看浏览器证据里事件入口：目标注册什么类型 listener、派发什么事件、读取哪些字段。
- 记录事件构造方式（new Event / new MouseEvent / createEvent）与 init 参数。
- 核对 target/currentTarget 身份与被监听元素的一致性。
- 记录回调内写入的状态，确认后续读取可见。
- 只补目标链路触达的事件类型与传播路径；未触达的输入设备面不补。

## 补环境要点

- listener 表是事件系统的核心，addEventListener / removeEventListener / dispatchEvent 共用。
- 派发时设置 target / currentTarget / eventPhase，listener 内 `this` 等于 currentTarget。
- preventDefault / stopPropagation / stopImmediatePropagation 按事件状态生效。
- 输入事件字段成组派生，坐标组、按钮组、按键组互不矛盾。
- timeStamp 与 performance 时间源一致，事件顺序不倒置。
- 事件回调写入的状态后续读取可见；未触达的事件类型不预建。
