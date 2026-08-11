# Audio 指纹对象参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

Web Audio 是上下文、节点图、AudioParam、时间线和渲染 buffer 的组合，指纹输出通常来自离线渲染后的 AudioBuffer 或 analyser 写入数组。音频指纹是状态机产出的数据，不是一组固定数字。

## 检测面

- `AudioContext`：目标检查 `sampleRate`、`currentTime`、`state`、`destination`、`resume/suspend/close` 方法存在性与调用返回。
- `OfflineAudioContext`：目标检查 channel count、length、sampleRate、`startRendering()` 的 Promise 形态、`oncomplete` 事件与渲染结果。
- `AudioNode`：`context` 引用、输入输出数量、channelCount/channelMode、connect/disconnect 连接关系。
- `AudioParam`：`value`、automation 事件列表（setValue/ramp 时间线）；`oscillator.frequency`、compressor 参数等是 AudioParam 对象而非数字。
- 输出方法：`getChannelData(i)` 返回 Float32Array；`AnalyserNode.getFloatFrequencyData/getByteFrequencyData` 写入调用方传入数组；`copyFromChannel/copyToChannel` 读写调用方数组。
- `typeof` / `instanceof` / constructor 外观：AudioContext、AudioBuffer、AnalyserNode、Float32Array 等须是各自接口，不能混成普通对象或普通数组。

## 常见坑

- `startRendering` 同步返回普通数组，而不是 Promise resolve AudioBuffer。
- `getChannelData` 返回普通数组，且多次读取内容漂移。
- AudioParam 直接补成数字，目标访问 `param.value` 链式调用时断裂。
- 所有 node 共用一个空对象，缺 context、输入输出和连接关系。
- analyser 方法返回数组而不是写入传入数组，`Float32Array` 内容与后续 hash 不一致。
- `currentTime` 补成固定值或完全随机，与时间源语义冲突；`state` 变化不影响方法和事件行为。
- `node.context === audioCtx`、`destination.context === audioCtx` 等身份引用缺失。

## 观察优先级

- 先看浏览器证据里音频调用链的入口：目标是 `new AudioContext()` 还是 `new OfflineAudioContext()`，还是只触碰 `navigator.mediaDevices` 间接路径。
- 核对 `startRendering` 的调用方是否 await、是否注册 `oncomplete`；这决定本地执行层必须实现 Promise 还是事件。
- 记录方法签名：目标传入的数组类型（Float32Array/Uint8Array）与长度，返回对象后续是否被读取字段。
- 核对同一 AudioBuffer 的 channel data 多次读取内容是否稳定，以及渲染结果是否进入后续 hash / 请求参数。
- 证据不足时只记录缺口，不补完整音频引擎；与目标链路无关的音频面不补。

## 补环境要点

- 音频面只在目标调用链触达时启用，不预建完整音频引擎。
- 输出为样本值时，保留生成它的调用序列说明：创建参数、节点连接、渲染参数、输出类型。
- 类型严格区分：`Float32Array`（getChannelData / analyser 浮点接口）与 `Uint8Array`（字节接口）不能互换。
- `startRendering` 的 Promise 与 `oncomplete` 事件按证据二选一实现，不双写造成时序矛盾。
- `currentTime` 使用单调递增时间源，与 performance / 事件时间戳同一来源。
- 渲染结果进入 hash 或请求参数时，与本地执行层后续字节保持同源。
- 节点与 context 的身份引用（`node.context`、`destination.context`）先于字段值核对。
