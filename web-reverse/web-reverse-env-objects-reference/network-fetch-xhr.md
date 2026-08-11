# 网络与请求对象参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

fetch、XHR、Request、Response、Headers、URLSearchParams、FormData、Blob/File、WebSocket 都是请求边界对象。核心是 URL、Header、body、状态机、异步回调和字节编码。

## 检测面

- Headers：name 到 value 的映射、原始插入或规范化顺序、重复 header 合并策略；name 大小写规范化比较但输出顺序和字符串可能影响签名；`append` 与 `set` 不同；`get/has/delete/forEach/entries` 来自同一映射。
- URLSearchParams/FormData：有序 key/value 列表、允许重复 key；`append` 追加、`set` 替换；`get` 返回第一个、`getAll` 返回全部；`toString()` 保留顺序与编码语义；FormData value 可为字符串、Blob 或 File。
- Request/Response：Request 维护 url/method/headers/body/credentials/mode/cache/redirect/referrer 与 body used 状态；Response 维护 status/statusText/ok/url/headers/body 与 body used 状态；`text/json/arrayBuffer/blob/formData` 返回 Promise；body 只能消费一次，`clone()` 返回共享内容的新对象且 body used 独立。
- fetch：返回 Promise；input 可为字符串、URL 或 Request；init 的 headers/body/method 合并或覆盖 Request 状态；resolve Response 或 reject 错误对象，不能同步返回。
- XMLHttpRequest 状态机：`readyState/status/statusText/response/responseText/responseURL`；`open` 进入 OPENED；`setRequestHeader` 在 OPENED 后、send 前有效；`send` 记录 body 并触发 readyState/onreadystatechange/onload/onerror 变化；XHR 事件 target/currentTarget 指向 XHR 实例。
- Blob/File/FileReader：Blob 维护字节数组与 `size/type`；File 额外 `name/lastModified`；`arrayBuffer/text` 返回 Promise；FileReader 是事件式异步对象，`result/error/readyState` 随读取变化。
- WebSocket/EventSource：WebSocket 维护 `url/readyState/protocol/extensions/bufferedAmount`；`send(data)` 接受字符串、Blob、ArrayBuffer、TypedArray；message 事件 data 类型与帧内容一致；EventSource 维护 url/readyState/withCredentials 与 message/error/open 事件。

## 常见坑

- Headers 用普通对象，大小写、顺序、append/set 语义全错，签名边界变化。
- `Response.json()` 同步返回对象，await 后断裂。
- XHR `send` 空函数，没有 readyState 和事件变化，回调链断。
- URLSearchParams 重排 query，顺序与编码错导致签名不一致。
- WebSocket 只有 `send`，没有 readyState 和 message 事件内容。
- body 重复消费不报错，或 clone 后状态共享混乱。

## 观察优先级

- 先看浏览器证据里请求对象入口：fetch、XHR 还是 WebSocket，以及请求参数如何组装。
- 记录 header 的写入顺序与大小写形态，和最终 wire 请求的 header 顺序核对。
- 记录 body 编码路径（字符串/FormData/Blob/TypedArray）与字节一致性。
- 核对 XHR readyState 变化序列与事件回调顺序。
- 只补目标链路触达的请求边界；未触达的传输方式不预建。

## 补环境要点

- 请求边界对象保持异步语义，text / json / arrayBuffer 等返回 Promise。
- header 顺序与大小写形态与 wire 请求一致，影响签名边界。
- body 编码路径（字符串 / FormData / Blob / TypedArray）与字节一致性核对。
- XHR readyState 变化序列与事件回调顺序按证据实现。
- URLSearchParams / FormData 保留顺序与重复 key，toString 不重排。
- body used 与 clone 状态独立维护，重复消费按证据处理。
