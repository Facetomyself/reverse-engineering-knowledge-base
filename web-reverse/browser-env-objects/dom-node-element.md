# DOM 节点与元素参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

DOM 节点是带树关系、属性表、文本内容、样式子对象和布局读数的对象；具体元素还带各自的 HTML/SVG 专有 property。不能用普通对象替代。

## 检测面

- 节点基础：`nodeType`、`nodeName/tagName/localName`、`ownerDocument`、`parentNode/parentElement`、`childNodes/children`、attributes 表、`textContent/innerHTML/outerHTML`。
- 元素扩展：`style`（CSSStyleDeclaration 语义）、`dataset`（DOMStringMap 风格）、`classList`（DOMTokenList）、布局读数 client/offset/scroll/rect。
- 派生规则：HTML 元素 `nodeName/tagName` 大写、`localName` 小写；`id/className` 与 attributes 同步；`dataset.foo` 从 `data-foo` 派生且写入反向同步；`classList` 从 className 派生；`children` 只含元素节点、`childNodes` 含全部。
- 写入语义：`setAttribute` 修改 attribute 表并同步 property；`getAttribute` 不存在返回 `null`；`removeAttribute` 删除并同步；`appendChild` 先移除旧 parent 再挂新 parent；`insertBefore(node, null)` 等同 append；`contains/compareDocumentPosition` 由树关系决定。
- 特殊元素：HTMLScriptElement（src/type/async/defer/onload/onerror、插入后加载执行）；HTMLIFrameElement（contentWindow/contentDocument、子 realm）；HTMLCanvasElement（width/height/getContext/toDataURL）；HTMLImageElement（src/complete/naturalWidth/naturalHeight/onload/onerror）；HTMLAnchorElement（href 派生 protocol/host/pathname/search/hash）；HTMLInputElement（value/checked/type/name/defaultValue）；HTMLFormElement（elements 集合、提交目标）。
- 返回对象：`getBoundingClientRect()` 返回字段互相派生的 DOMRect；`style/attributes/classList/dataset` 各是语义对象。
- 事件对象的 `target` 回指该元素。

## 常见坑

- 元素只有 `tagName`，attributes/property 无同步，`setAttribute` 后 `getAttribute` 读不到。
- `style/classList/dataset/attributes` 是空对象，目标链式调用断裂。
- layout 字段互相矛盾（rect width 与 offsetWidth 完全不相关）。
- `appendChild` 不维护 parent/children，后续查询和集合失真。
- 同一节点多次返回不同对象身份，目标比较引用失败。
- `innerHTML` 写入后 `textContent` 不同步。

## 观察优先级

- 先看浏览器证据里节点入口：createElement 类型、querySelector 路径还是 getBoundingClientRect。
- 记录目标读取的 property 序列与 attribute 写入序列，确认同步依赖。
- 核对节点身份：同一节点在树、集合、事件 target 中是否同一对象。
- 记录 layout 字段被读的具体项，与 screen/viewport 状态交叉核对。
- 只补目标链路触达的节点种类与字段；未触达的元素类型不预建。

## 补环境要点

- attribute 表与 property（id / className / src / href / value）双向同步，写入与读取同一状态。
- dataset 与 data-* attribute、classList 与 className 保持反向同步。
- 树操作维护 parent / children / childNodes / ownerDocument 一致，append 先摘旧父。
- 布局读数（getBoundingClientRect、client / offset）来自单一 layout 状态。
- 同一节点多次返回同一对象身份，事件 target 回指元素。
- 按目标触达的元素类型补语义，未触达类型不预建。
