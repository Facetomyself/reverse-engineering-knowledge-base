# location 对象参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

`location` 是 URL 状态机，不是一个 href 字符串。`href`、`origin`、`protocol`、`host`、`hostname`、`port`、`pathname`、`search`、`hash`、`toString()` 都应从同一份内部 URL 状态派生。

## 检测面

- 内部状态：scheme/protocol、hostname、port、pathname、search、hash、原始 href 序列化规则；username/password 仅在目标读取时才补。
- 字段派生：`href` 是完整序列化 URL；`origin` 是 protocol + `//` + host；`host` 是 hostname 加可见 port；`pathname` 以 `/` 为路径语义；`search` 有 query 带 `?` 无则空串；`hash` 有 fragment 带 `#` 无则空串。
- 字符串化：`toString()`、字符串拼接、模板字符串与 `href` 一致。
- 写入语义：写 `href` 整体替换内部 URL；写 `protocol/host/hostname/port/pathname/search/hash` 只替换对应部分再重新派生；写 search/hash 时输入是否带 `?`/`#` 都要归一到浏览器可见形态。
- 方法语义：`assign(url)` 按当前 href 解析相对 URL 并更新内部 URL；`replace(url)` 同解析语义，是否保留 history 由调用点决定；`reload()` 不改变 URL，若后续读取依赖 reload 状态要记录调用标记。
- 交叉一致性：`new URL(relative, location.href)` 使用同一套解析结果；location 作为字符串参数传入走 href 序列化；`document.location` 与当前 document 的 location 状态一致；`document.URL` 是 href 的快照或派生值。
- 页面 URL、脚本 URL、接口 URL 是不同概念，不能混成同一个 href。

## 常见坑

- 只补 `location.href`，origin/search/pathname/hash 为空或互相矛盾。
- 各字段散写，写 search 后 href/origin 不重新派生，状态错乱。
- `assign/replace` 是空函数，写入后再读仍旧值。
- 相对 URL 不按当前 href 解析，`new URL` 结果与 location 不一致。
- 主窗口和 iframe 共用同一个 location 对象，子 realm 身份错误。
- `toString` 结果与 href 不同，目标字符串化时失配。

## 观察优先级

- 先看浏览器证据里 location 入口：目标读 href 还是逐字段读，是否做相对 URL 解析。
- 记录页面 URL、脚本 URL、接口 URL 三者关系，防止混用。
- 核对写入序列：目标是否先写 search/hash 再读 href 或 origin。
- 核对 `new URL` 的基地址参数与调用结果。
- 只补目标链路触达的字段与解析路径；username/password 等未读字段不预补。

## 补环境要点

- URL 状态集中维护，字段由状态派生，写任意段后整体重新派生。
- 相对 URL 解析与 `new URL(relative, base)` 用同一套规则。
- search / hash 写入时归一到浏览器可见形态（? / #）。
- toString / 模板字符串与 href 一致。
- 页面 URL、脚本 URL、接口 URL 区分维护，不混为一个 href。
- 主窗口与 iframe 各有 location 状态；未触达字段不预补。
