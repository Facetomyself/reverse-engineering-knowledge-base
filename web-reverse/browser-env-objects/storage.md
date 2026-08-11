# storage / cookie 参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

`localStorage`、`sessionStorage`、`document.cookie` 都是同轮状态容器，不是静态字段。Storage 关注 key/value Map、顺序、字符串化和属性访问；cookie 关注 CookieJar、可见性、覆盖和 Header 输出。

## 检测面

- Storage 状态：内部字符串 key 到字符串 value 的 Map；key 顺序用于 `length`、`key(index)`、枚举和索引行为；属性镜像（直接读 `localStorage.foo` 与 Map 同步）；所属作用域（主 window、iframe、session 或跨轮持久状态）。`localStorage` 与 `sessionStorage` 不共用同一 Map。
- Storage 方法：`length` 从 key 数量派生；`getItem(key)` 不存在返回 `null` 不是 `undefined`；`setItem` 按字符串保存、新 key 追加末尾；`removeItem` 删除 Map 项与属性镜像；`clear()` 清空全部；`key(index)` 越界返回 `null`；直接属性写入要同步到 Map。
- CookieJar：name/value、domain/path 可见性、expires/max-age、secure/httpOnly/sameSite 可见影响、写入/输出顺序、当前 document URL 作用域。
- Cookie 派生：`document.cookie` getter 只输出当前 document 可见且非 httpOnly 的 cookie；`document.cookie = raw` 只解析第一段 name/value 为内容，后续段是 attributes；同名同 domain/path 覆盖旧值；过期或 max-age 失效不再出现；getter 输出形态 `name=value; name2=value2`，顺序来自 CookieJar；服务端 Set-Cookie 后同轮后续 getter 与请求 header 反映变化。
- HTTP `Cookie` header 是请求边界输出，不等同于 `document.cookie` 的原始字符串变量。
- IndexedDB/CacheStorage：`indexedDB.open()` 返回 request 对象（onsuccess/onerror/onupgradeneeded、result/error/transaction 互相关联）；`caches.open()` 返回 Promise resolve Cache；`cache.match()` 返回 Promise resolve Response 或 `undefined`；仅被检测存在时保持接口外观即可。
- 身份：`window.localStorage === localStorage` 与全局一致；iframe storage 共享或隔离由 iframe 作用域决定；Map、属性镜像、length、key(index)、枚举顺序来自同一份状态；CookieJar、document.cookie、请求 Header、Set-Cookie 写入互相解释。

## 常见坑

- `getItem` 返回 `undefined` 而非 `null`，目标判断失败。
- `setItem` 不字符串化，数字/对象直接存，后续 hash 结果不同。
- `length` 固定数字，不随写入删除变化。
- cookie 只是普通字符串变量，多次写入覆盖和 attributes 全丢。
- 参数生成成功后同轮 cookie/header/storage 状态未带到后续请求，重放失败。
- `indexedDB.open` 同步返回数据库对象，`caches.match` 同步返回普通对象。

## 观察优先级

- 先看浏览器证据里 storage 入口：localStorage/sessionStorage 读写、document.cookie 还是 indexedDB/caches。
- 记录 key 写入顺序与字符串化形态，和后续读取/hash 一致。
- 记录 cookie 写入段（attributes）与请求边界 header 的对应关系。
- 核对 iframe 场景下 storage 的共享或隔离语义。
- 只补目标链路触达的存储面；未触达的 IDB/Cache 不预建。

## 补环境要点

- Storage Map、属性镜像、length、key(index)、枚举顺序同一状态来源。
- setItem 按字符串化保存，getItem 缺失返回 null。
- localStorage 与 sessionStorage 分 Map 维护，作用域隔离。
- CookieJar 与 document.cookie、请求 header、Set-Cookie 互相解释。
- 参数生成后的同轮 cookie / header / storage 状态带到后续请求。
- indexedDB / caches 被读时按异步对象实现，仅检测存在时保持外观。
