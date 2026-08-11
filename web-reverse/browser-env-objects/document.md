# document 对象参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

`document` 是 DOM 树、生命周期、脚本执行上下文、cookie 和查询/创建工厂的组合对象，不是 `readyState` 加几个方法的普通对象。

## 检测面

- 顶层状态：`defaultView`、`documentElement/head/body`、`readyState`、`currentScript`、URL/referrer/domain/title/visibility。
- 集合来源：`scripts/forms/images/links/styleSheets` 从 DOM 树派生，带集合语义（length、索引、item/namedItem）。
- 派生一致性：`defaultView.document === document`；`document.URL`、`document.location` 与 `location.href` 同一 URL 状态；`document.cookie` 走 CookieJar getter/setter。
- 创建工厂：`createElement(tag)` 返回具体元素对象；`createElement('script')` 带 `src/async/defer/onload/onerror` 与插入后加载语义；`createElement('iframe')` 能产生子 realm；`createElement('canvas')` 命中后进入 canvas 语义。
- 查询：`querySelector/getElementById/getElementsByTagName` 返回 DOM 树中的同一身份节点；返回集合时用集合语义。
- 生命周期：`appendChild/removeChild/insertBefore` 维护 parent/children/childNodes/ownerDocument；插入 script 可能改变 `currentScript`、触发 load/error；插入 iframe 触发子 document 生命周期。
- 返回对象：`createTextNode` 返回 text node（nodeType/nodeValue/textContent 一致）；`createEvent/new Event` 进入事件语义；`implementation.createHTMLDocument` 返回新 document 而非主 document 别名。
- `readyState` 影响事件与脚本分支，不能默认永远 `complete`。

## 常见坑

- `createElement` 只返回 `{}`，script/iframe/canvas 后续语义断裂。
- `document.cookie` 是普通字符串变量，不接 CookieJar，写入覆盖和 attributes 丢失。
- `currentScript` 永远 null，目标通过 script URL 或属性定位脚本时失配。
- `appendChild` 返回节点但不更新 DOM 树和集合，后续查询失真。
- `scripts/forms/images/links` 用普通数组，缺集合外观。
- `document.documentElement` 不是真实元素节点，缺 ownerDocument。

## 观察优先级

- 先看浏览器证据里 document 入口：`readyState`/`currentScript` 分支、createElement 类型、cookie 读写还是集合遍历。
- 记录 createElement 创建的元素类型与其后续方法调用，决定需要哪一档元素语义。
- 核对 `currentScript` 在目标执行期间的实际指向与 script 属性。
- 核对 cookie 的读写顺序与 attributes，和请求边界 Cookie header 互相解释。
- 只补目标链路触达的树与工厂语义；document 全集不预搭。

## 补环境要点

- document 状态集中维护（树、URL、cookie、readyState），字段由状态派生，不逐字段写死。
- createElement 按目标触达的类型补语义，script / iframe / canvas 各自闭环。
- 集合返回统一走集合语义，不用普通数组。
- `currentScript` 仅在脚本执行期间指向当前 script，执行后恢复或变 null。
- cookie 读写与请求边界 header 同一 CookieJar，attributes 不丢失。
- DOM 树操作维护 parent / children / ownerDocument 三向一致。
- 未触达的工厂与查询路径不预建。
