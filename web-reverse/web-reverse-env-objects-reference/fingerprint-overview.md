# 指纹内容总纲

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

指纹内容不是一组固定值，而是由浏览器身份 profile、图形/音频/字体/layout 状态、权限设备状态和调用顺序共同产生的输出。本文描述这些输出对象如何建模，供各对象文档共用。

## 检测面

- 状态来源组：浏览器身份（navigator、screen、window metrics）；图形状态（canvas 2D 绘制状态、WebGL context 状态）；音频状态（AudioContext、节点图、AudioParam、渲染 buffer）；字体与布局（computed style、FontFaceSet、DOMRect、TextMetrics）；设备与权限（media、clipboard、battery、network、orientation）；时间与调度（performance.now、requestAnimationFrame、observer callback）。
- 状态间一致性：字体状态影响 canvas `measureText`；viewport 影响 layout rect；WebGL 参数属于同一渲染 profile；这些状态互相不能矛盾。
- 输出类型正确性：像素、音频 sample、字体宽度、WebGL 参数数组保持各自类型（字符串、TypedArray、ArrayBuffer、Float32Array、DOMRect、TextMetrics），不能混用。
- 稳定性与变化：多次读取同一上下文状态稳定；重置上下文或改变尺寸后输出变化或清空。
- 关联链：Canvas 2D 与 CSS Font/Layout 关联；WebGL 与 screen/GPU profile/TypedArray 关联；Audio 与 performance/timer/Promise 关联；FontFaceSet 与 document、layout、canvas text 关联；mediaDevices 与 permissions、navigator、device profile 关联。

## 常见坑

- 只补一串固定 canvas base64，但 canvas 尺寸、绘制状态、字体状态不存在，交叉校验即败。
- WebGL vendor/renderer 单点补了，其它 limits/extensions/shader 状态互相矛盾。
- audio rendering 返回普通数组，不是 AudioBuffer/Float32Array。
- 字体列表存在，但 `measureText/getBoundingClientRect` 与字体状态无关。
- 各对象值来自不同 profile 拼接，navigator 与 screen 与 canvas 对不上。
- 输出固定为样本值但没有保留生成它的输入状态说明（调用参数、对象身份、前置写入）。

## 观察优先级

- 先看浏览器证据里目标最先触达的指纹面：navigator 字段、canvas、audio 还是 layout。
- 记录方法调用序列与参数（绘制命令、文本、字体、尺寸），输出是调用与状态的结果。
- 核对跨对象关联点：字体 ↔ measureText ↔ layout；screen ↔ viewport ↔ media query；WebGL ↔ TypedArray 输出。
- 记录重置/尺寸变化后的行为，决定本地执行层是否需状态变化。
- 目标链路未触达的指纹面不预补；已触达面先对齐关联链再定值。

## 补环境要点

- 先定目标链路触达的指纹面清单，再逐面对齐关联链，不先补值。
- 每个输出保留生成它的输入状态：调用参数、对象身份、前置写入、输出类型。
- 跨对象同源：字体与测量、viewport 与 layout、WebGL 与 screen 同一状态组。
- 输出类型严格保持（字符串 / TypedArray / ArrayBuffer / DOMRect / TextMetrics），不混用。
- 多次读取稳定，重置或尺寸变化后输出变化或清空。
- 各对象值来自同一浏览器身份 profile，禁止跨 profile 拼接。
- 与目标链路无关的指纹面不补。
