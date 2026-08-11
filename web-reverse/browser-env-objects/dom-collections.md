# DOM 集合对象参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

DOM 集合是类数组对象，不是普通数组。核心内容是 length、数字索引、命名查找、迭代、枚举顺序，以及 live/static 更新策略。

## 检测面

- 集合外观：内部 items 列表、数字索引到 item 映射、`length`、可选 name/id 映射、live 或 static 属性、所属来源（document、parent node、attributes、plugin store）。
- 索引语义：`collection[0]` 与 `item(0)` 指向同一对象；越界 `item(index)` 返回 `null`；`namedItem(name)` 按 id/name 匹配。
- 迭代与枚举：`for...of`、`keys/values/entries` 按接口存在；`Object.keys`、ownKeys、数字索引与命名属性的枚举顺序来自集合模型。
- 具体集合：NodeList（索引/length/item/可迭代）；HTMLCollection（索引/length/item/namedItem）；DOMTokenList（token 顺序、`value/toString`、`contains/add/remove/toggle` 同步来源字符串）；NamedNodeMap（`getNamedItem/setNamedItem/removeNamedItem`、attr.ownerElement）；CSSStyleDeclaration（属性名索引、cssText、getPropertyValue 族）；PluginArray/MimeTypeArray（索引、name 查找、plugin 与 mimeType 互相引用）。
- live/static：HTMLCollection 与 `document.forms/images/scripts/links` 常见 live，DOM 变化后内容变化；`querySelectorAll` 的 NodeList 常见 static；是否 live 由对象来源决定，不能猜。
- 写入语义：`DOMTokenList.add` 不重复追加；`remove` 后同步 className；`toggle(token, force)` 返回 boolean；`setNamedItem` 替换同名 attr；`setProperty` 影响读取与 cssText。

## 常见坑

- 用数组冒充集合：`Array.isArray`、constructor、item/namedItem 全错，目标可识别。
- `length` 固定不变，写入删除后不更新。
- `namedItem` 缺失，目标按 id/name 查找失败。
- `classList` 修改后 `className` 不变，attribute 不同步。
- plugin/mimeType 只有 length 没有 item 内容与 enabledPlugin 引用。
- live/static 语义错位：static 集合随 DOM 变化，或 live 集合不随来源更新。

## 观察优先级

- 先看浏览器证据里集合入口：`document.scripts`、`getElementsByTagName`、`classList` 还是 `navigator.plugins`。
- 记录目标访问的索引方式（数字索引、item、namedItem、迭代）与读取顺序。
- 核对集合是否 live：目标在 DOM 变化前后是否重复读取同一集合。
- 记录 `classList`/attribute 的写入序列，确认同步关系。
- 集合 item 的 ownerDocument/ownerElement/enabledPlugin 回指来源对象；与目标链路无关的集合类型不补。

## 补环境要点

- 集合实现先定 live / static，再决定内容更新策略，来源决定不靠猜。
- 索引、item、namedItem、迭代、ownKeys 枚举顺序来自同一集合模型。
- DOMTokenList 的增删同步 className；CSSStyleDeclaration 的 setProperty 同步 cssText。
- NamedNodeMap 维护 attr.ownerElement 与同名替换语义。
- PluginArray / MimeTypeArray 维护 plugin 与 mimeType 双向引用。
- 集合 item 的 ownerDocument / ownerElement / enabledPlugin 回指来源对象。
- 未触达的集合类型不预建；补入后按接口外观与来源语义一并核对。
