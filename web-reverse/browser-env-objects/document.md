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

## document.all 补环境要点

`document.all` 是文档中历史遗留的 undetectable 对象,目标常以它作为环境检测点。

- **V8 undetectable 底座思路**:`document.all` 是 HTML 规范的 undetectable 对象——存在但 typeof 与布尔化表现特殊。补环境底座优先用 V8 原生 undetectable 能力:`--allow-natives-syntax` 下用 `%GetUndetectable()` 生成真 undetectable 对象,避免用普通对象加代理伪造外观。
- **检测点**:目标可能从三个方向检测 document.all:
  - `typeof document.all` 为 `"undefined"`(即使对象本身存在);
  - 布尔化:`if (document.all)` / `Boolean(document.all)` 为 false、`!document.all` 为 true;
  - 属性访问:`length`、`[i]` 索引、`tags`、`item`、`namedItem` 等集合语义仍可用。
- **集合语义**:document.all 是 DOM 全集索引,包含 documentElement、head、body 及所有后代元素;`length` 与 `[i]` 顺序应与其他集合(scripts/forms/images/links)同源一致。
- **与 document 整体语义衔接**:document.all 属于集合来源,随 DOM 树操作(appendChild/removeChild/insertBefore)维护,不独立写死一份副本。
- **常见坑**:普通对象加 typeof 覆写或 getter 无法同时满足「typeof 为 undefined 且对象可访问」;`%GetUndetectable()` 是同时满足两者的底座,属性和方法仍需按目标触达补齐。
- **优先按证据还原**:先查浏览器证据中目标链路实际使用的检测方式(是 typeof 判断、布尔判断、属性访问还是组合),按证据补对应语义,不默认全量实现集合。
- **验证要点**:补后对照浏览器证据核对三项——typeof 结果、布尔化结果、集合访问结果(长度、索引、tags)与目标链路一致;任一不一致即回查证据。
- **证据不足记录缺口**:证据无法确认 document.all 的检测方式或行为细节时,记录缺口与当前假设,不凭猜测补;进入补环境前该缺口须有证据或明确标注。
