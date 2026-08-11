# Crypto / 编码 / 二进制对象参考

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse

二进制对象的核心是字节内容、buffer 共享关系、offset/length、编码边界和异步 Promise。TypedArray、ArrayBuffer、DataView、Blob、subtle 结果不能混成普通数组或字符串。

## 检测面

- ArrayBuffer/TypedArray：`byteLength`、TypedArray 的 `byteOffset/byteLength/length`、元素类型与字节宽度；Uint8/Uint16/Uint32 等元素宽度不同；BigInt typed array 元素是 BigInt 不是 Number。
- 共享语义：`subarray` 共享底层 buffer，`slice` 复制内容；写 TypedArray 元素改变底层 buffer；多次读 `.buffer` 回到同一 ArrayBuffer。
- DataView：绑定 ArrayBuffer/byteOffset/byteLength；`getUint16/getUint32` 等按 offset 与 littleEndian 读取；`set...` 写回底层 buffer；越界抛对应异常。
- TextEncoder/TextDecoder：`encode(str)` 返回 Uint8Array；`encodeInto(str, dest)` 写入调用方数组并返回 `{read, written}`；`decode(input, options)` 的 fatal/stream 选项影响错误与状态。
- atob/btoa/hex/URL 编码：输入输出是字符串但内容边界是字节；Unicode 直接 btoa 应报错；hex、base64、ArrayBuffer 互转明确字节顺序。
- crypto：`getRandomValues(typedArray)` 原地填充并返回同一对象，只接受整数 TypedArray；`randomUUID()` 返回 UUID 字符串；`crypto.subtle.*` 全部返回 Promise（digest resolve ArrayBuffer、importKey resolve CryptoKey、encrypt/decrypt/sign/verify 按算法返回 ArrayBuffer 或 boolean）。
- Blob/File：字节内容可转 ArrayBuffer/text；structured clone 复制数据或转移所有权，不是引用赋值。

## 常见坑

- `getRandomValues` 返回新数组或固定字符串，且接受普通数组不报错。
- `TextEncoder.encode` 返回普通数组，后续 `.buffer`/`.byteLength` 访问断裂。
- subtle 方法同步返回，`await` 后得到 undefined 或直接抛错。
- ArrayBuffer 长度与 TypedArray length/byteLength 不一致。
- DataView 忽略 littleEndian，字节序错导致签名/参数错误。
- 用 Node Buffer 外观暴露给目标 JS，`Array.isArray`/constructor 可被识别。
- 同一二进制 payload 进入 hash、请求 body、Worker message 时字节不同源。

## 观察优先级

- 先看浏览器证据里二进制数据的流向：getRandomValues 填充后进入哪里、subtle.digest 结果如何被消费。
- 记录目标传入的数组类型与长度、调用是否 await、返回对象后续读取哪些字段。
- 核对同一 payload 在多个边界（hash、请求体、消息）的字节一致性。
- 记录 encodeInto/decode 的调用参数（fatal/stream），决定本地执行层异常外观。
- 只补目标链路触达的编码与算法面；未触达的 subtle 算法不预补。

## 补环境要点

- 二进制面优先保证字节同源：同一 payload 在 hash、请求体、消息边界内内容一致。
- `getRandomValues` 用同一随机源原地填充，多次调用不返回相同字节。
- subtle 结果保持 Promise 形态，resolve 对象（ArrayBuffer / CryptoKey / boolean）按算法表对齐。
- 编码转换（hex / base64 / UTF-8）明确字节序与填充规则，与浏览器结果逐字节核对。
- DataView 读写实现 littleEndian 参数，越界抛对应异常外观。
- TypedArray 的 byteOffset / byteLength / length 与底层 ArrayBuffer 一致。
- 未触达的算法与编码不预补；补入后与其输入输出类型一并核对。
