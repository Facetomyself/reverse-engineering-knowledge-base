# CSS / Layout / Font 对象参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

CSS、layout 和 font 内容由元素样式状态、computed style、字体加载状态、viewport、DOM 树和测量方法共同产生，不只是若干宽高数字。

## 检测面

- CSSStyleDeclaration：property map、priority map、property 顺序、`cssText`、`getPropertyValue/setProperty/removeProperty`、索引项与 length、枚举顺序；inline style 与 computed style 不是同一对象。
- getComputedStyle：结果来自 inline style、默认样式、stylesheet、viewport/media query、pseudo 元素参数与 document/font 状态；返回只读或近似只读的 CSSStyleDeclaration 语义对象。
- DOMRect：`x/y/width/height/top/right/bottom/left` 互相派生（left=x、top=y、right=x+width、bottom=y+height）。
- 布局读数：`client/offset/scroll` 尺寸、`getBoundingClientRect`、ResizeObserver entry 的 contentRect 来自同一 layout 状态。
- FontFace/FontFaceSet：FontFace 维护 family/source/status/load Promise；FontFaceSet 维护集合、`ready` Promise、`load/check/add/delete/has`；字体加载状态影响 `measureText`、computed font 和布局宽高。
- `CSS.supports` 返回值来自当前 CSS 能力表；`matchMedia` 结果来自 viewport/screen/orientation 状态；`document.fonts.ready` 是 Promise。
- IntersectionObserver entry 的 rect 与 ratio 来自元素位置、viewport 与 root 状态。

## 常见坑

- `getComputedStyle` 返回元素 `style` 的同一个对象，写改相互污染。
- DOMRect 字段互相矛盾（如 right 与 x+width 不符）。
- `document.fonts.ready` 不是 Promise，`await` 断裂。
- 字体状态和 canvas `measureText` 无关，字体列表存在但测量结果不对。
- CSSStyleDeclaration 没有 length、索引和 `getPropertyValue`，目标按接口方法调用失败。
- `CSS.supports` 永远 true，或 `matchMedia` 返回 boolean 而不是 MediaQueryList。
- 样式/字体变化后布局读数不反映变化。

## 观察优先级

- 先看浏览器证据里布局入口：`getBoundingClientRect`、computed style 字段、`measureText` 还是 observer entry。
- 记录被读的具体 property 名与值，以及对应元素的可见性/尺寸状态。
- 核对字体相关事实：目标是否遍历 `document.fonts`、是否 await `ready`、measureText 使用哪个 font 串。
- 核对 DOMRect 派生关系与 client/offset 尺寸的同一状态来源。
- 字体与布局状态跨对象一致（canvas、observer、matchMedia）后再补值；与目标链路无关的样式面不扩张。

## 补环境要点

- 布局值来自单一 layout 状态：DOMRect、client / offset / scroll、observer entry 同一来源。
- computed style 与 inline style 分离，`getComputedStyle` 返回只读语义对象。
- 字体状态（document.fonts、FontFace status）先于测量结果对齐，`measureText` 同源。
- `document.fonts.ready` 保持 Promise 形态，加载状态变化影响测量。
- `matchMedia` / `CSS.supports` 来自当前 viewport 与能力表，不写死 true。
- 样式或字体变化后，目标读取的布局读数应反映变化。
- 未触达的样式面不预建；补入字段后与其依赖的字体/layout 状态一并核对。
