# screen / visualViewport 参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

screen、window metrics、visualViewport 和 orientation 是一组尺寸/显示状态，不是孤立数字。目标读取其中任意字段时，都可能与其它尺寸字段互相校验。

## 检测面

- 显示状态组：physical screen `width/height/availWidth/availHeight`；color `colorDepth/pixelDepth`；window metrics `innerWidth/innerHeight/outerWidth/outerHeight`；`devicePixelRatio`；viewport `visualViewport.width/height/scale/offsetLeft/offsetTop/pageLeft/pageTop`；orientation `type/angle`；resize/orientation listener 表。
- 派生规则：`screen.width/height` 与 orientation 横竖屏状态合理；`availWidth/availHeight` 不应大于 `width/height`；`innerWidth/innerHeight` 与 `visualViewport.width/height/scale` 可解释；`outerWidth/outerHeight` 通常不小于 inner；`devicePixelRatio` 影响 CSS px 与物理 px 关系；`screen.orientation.type` 与 `angle` 成对变化。
- 方法与事件：`matchMedia` 的 width/height/resolution/orientation 查询基于同一显示状态；`screen.orientation.addEventListener('change')` 与 `visualViewport.addEventListener('resize'/'scroll')` 使用 EventTarget 语义；尺寸变化后再读字段必须反映新状态。
- 身份：`window.screen === screen` 由所属 window 统一持有；多次读 `screen.orientation` 是否同一对象与状态模型一致；iframe 子 window 可有独立 viewport 或复用主 screen，不默认全部同一对象。
- 交叉一致：layout、canvas、font 测量用到的尺寸与这里同源。

## 常见坑

- 随便写一组常见分辨率，与 viewport/layout 不一致，交叉校验失败。
- `screen.orientation` 是普通字符串，目标读 type/angle 断裂。
- `matchMedia` 返回 boolean 而非 MediaQueryList。
- resize 后只改 `innerWidth`，不改 visualViewport 或 media query 结果。
- avail 大于 physical、outer 小于 inner 等不可能组合。
- orientation 变化后 angle 与 type 不配套。

## 观察优先级

- 先看浏览器证据里尺寸入口：screen 字段、inner/outer、visualViewport 还是 orientation。
- 记录被读字段清单，确认同一显示状态组的成员关系。
- 核对 devicePixelRatio 与 canvas/layout 测量的换算关系。
- 记录 resize/orientation 变化序列与变化后读取的字段。
- 只补目标链路触达的尺寸面；未触达的显示字段不预补。

## 补环境要点

- 显示状态组单一维护，physical / avail / inner / outer / viewport / orientation 同源。
- devicePixelRatio 与 canvas / layout 测量的换算一致。
- orientation.type 与 angle 成对变化，resize 后全部相关字段更新。
- window.screen 与全局 screen 同一对象，iframe 按作用域独立或共享。
- matchMedia 的尺寸查询与当前显示状态一致。
- 未触达的显示字段不预补。
