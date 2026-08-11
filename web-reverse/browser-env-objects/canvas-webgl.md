# Canvas / WebGL 对象参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

Canvas 是带尺寸、绘制状态和输出方法的元素；2D context 是绘制状态机；WebGL context 是 GPU-like 状态机。base64、像素数组、TextMetrics、WebGL 参数都应由上下文状态派生，不是孤立常量。

## 检测面

- Canvas 元素：`width/height`、`getContext(type)` 返回 2D 或 WebGL context、`toDataURL/toBlob` 输出、`canvas.width/height` 改变后绘制内容重置。
- Canvas 2D：fill/stroke style、font/textAlign/textBaseline、transform、globalAlpha、lineWidth 等绘制状态；`measureText` 返回 TextMetrics 对象。
- TextMetrics：`width` 与 text、font、字体状态相关，不是数字。
- ImageData：`getImageData` 返回含 `width/height/data` 的对象，`data` 为 Uint8ClampedArray，长度应为 `width*height*4`。
- WebGL：`getParameter(enum)` 按参数表返回对应类型（number/boolean/string/typed array/对象），不能所有 enum 同一值；`getSupportedExtensions()` 与 `getExtension(name)` 内容一致。
- Shader/Program/Buffer：`createShader` 返回属于当前 context 的对象；`compileShader` 改变 compile 状态；`getUniformLocation` 返回属于 program 和 context 的 location 对象。
- `readPixels` 写入调用方传入的 TypedArray，不是返回新数组；写入内容要与 width/height/format/type 可解释。
- `ctx.canvas === canvas` 身份引用；WebGL 对象只在所属 context 下有效。

## 常见坑

- `getContext` 返回 `{}`，后续所有绘制调用直接报错或静默失败。
- `toDataURL` 补成固定字符串，但 `getImageData` 和绘制状态不存在，两条路径结果互相矛盾。
- `measureText` 返回普通数字，目标读 `width` 时得到 undefined。
- WebGL enum 全部返回 vendor 字符串，`getParameter` 类型错乱。
- `readPixels` 返回新数组而非写入传入 buffer，字节内容进入 hash 时与后续请求不一致。
- 字体状态和 canvas `measureText` 无关联（见 css-layout-font）。
- WebGL 输出进入 hash 后，TypedArray 内容与请求/Worker 字节不同源。

## 观察优先级

- 先确认浏览器证据里 canvas 的入口：`toDataURL` 结果、`getImageData` 像素、`measureText` 宽度还是 WebGL `getParameter` 进入目标参数。
- 记录绘制命令顺序与前置写入（fillText 文本、字体设置、fillStyle 等），这些决定输出内容。
- 核对 WebGL 被读的 enum 清单与对应值类型，与同一渲染 profile 的 screen/vendor 状态一致。
- 核对 `measureText` 的字体与 document.fonts / computed font 状态同源。
- 指纹值只在目标链路触达时补；目标不读的绘制面不扩张。

## 补环境要点

- 目标只读 `toDataURL` 时，输出与尺寸/绘制状态同源的固定位图即可，不实现完整 2D 绘制器。
- `getContext` 对同一 canvas 多次调用应返回同一 context 实例。
- WebGL 参数表按被读 enum 清单建表，类型（number / boolean / string / typed array）逐项核对。
- shader / program 对象保留 compile / link 状态，`getShaderParameter` 从状态派生。
- 位图内容与后续请求 / Worker 字节一致；重置尺寸后输出应变化或清空。
- `ctx.canvas` 身份引用与字体测量同源关系先对齐，再定绘制值。
- 未触达的绘制接口不补；补入接口后与其状态依赖一并补齐。
