---
schema_version: 2
id: spiderdemo-t30-websocket-jsvmp
document_type: archive
original_date: unknown
archived_date: "2026-10-30"
scope:
  targets: [spiderdemo]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: https://mp.weixin.qq.com/s/fa4VsV72tYs6mUQG5ZV5FA
    basis: source-report
source_completeness: partial
tags: [spiderdemo, websocket, jsvmp, msgpack, base62, source-report]
---

# spiderdemo T30：WebSocket 与 jsvmp 题解（来源报告）

来源是一篇公众号转载的练习题题解，题目站写为 `https://www.spiderdemo.cn/`，题号为 T30 WebSocket+jsvmp。作者声明内容仅供学习、不提供完整代码，并称抓包、敏感网址和数据接口已脱敏。发表日期未知。本文只清洗留存，没有运行原文代码，也没有访问题目站复核。

通用 JSVMP 教学见 [jsvmp-from-toy-vm-to-devirt](./jsvmp-from-toy-vm-to-devirt.md)。本文不重复那一套 opcode 教程，只保留这一题的协议与补环境叙述。

## 清洗与完整性说明

- 删除文末「转自 / 如有侵权请联系删除」。文章定位用 sources 的公开链接。
- 作者声明不提供完整代码，因此 `source_completeness` 为 partial。
- 来源第三节的凭证和第七节的密钥只保留机制：seed、`token_seed` 样值、加密密钥原值不入库。
- 不保留指纹 JSON 样值、canvas data URL，以及可对照会话的帧样值。
- 来源把「方向 / 内容」表拆成逐单元格，本文按阅读顺序还原，没有新增单元格。
- 部分代码被平台压成单行。下面按可见 token 恢复换行和缩进，不补原文没有的语句。
- 作者写的「日志实证」「字节级一致」「答案正确」都是 source-report。本次未复现。

## 来源正文

### 前言

作者要采集 100 页并求这些页上数字的和。形态是 WebSocket 加 VMP：页面加载 `jsvmp2.js`，业务走 `wss://www.spiderdemo.cn/ws/`。帧是自定义 base62，解开后是 msgpack。

作者的路线是：不逐条读 VMP 字节码，把 `sdk.min.js` 放进 Node vm，用最小环境把它暴露出来的密码学原语直接调用；协议则靠补环境日志记录真实输入输出再反推。

### 抓包看到的帧序

| 方向 | 内容 |
| --- | --- |
| C→S | 108 字节二进制帧（token） |
| S→C | 24 字符 base62（challenge） |
| C→S | 89 字符 base62（应答） |
| C→S | 33 字符 base62（翻页请求） |
| S→C | 609 字符 base62（页数据） |
| S→C | PING，要回 PONG |

token 帧是明文 msgpack。作者给出的结构是 fixmap，字段为 `cmd` = 100 和 `token` 字符串。其后的帧是密文。

base62 不是「大写在前」的常见字母表，而是小写在前：

```text
0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
```

### 凭证机制

WebSocket 握手要带 cookie，其中 `ads-baidu` 是动态的。作者描述的形态是：seed 的前 8 个字符，加一个点，再加一串 base62。seed 来自初始化接口：

```text
GET /authentication/api/jsvmp2_challenge/init/?challenge_type=jsvmp2_challenge
```

响应里有 `token_seed`。后面的 base62 由 `sdk.min.js` 的 `spiderEncrypt` 计算。作者写的拼接是：

```text
input = seed + "|" + timestamp + "|jsvmp2_challenge"
b62 = spiderEncrypt(input, 固定密钥)
ads = seed 的前 8 位 + "." + b62
```

固定密钥的原值不入库。作者称与浏览器样本字节级一致。这是来源陈述，不是本次验收。

### 传输层

作者称同一个 ads token 下，Python `ssl` 手动握手得到 101，Node `ws` 得到 403，并把差异归到 ClientHello。采用的分工是 Python 发包、Node 算参数。

服务端帧使用 permessage-deflate。作者写 Python 侧要用 raw inflate，并补 flush 尾：

```python
_inflator = zlib.decompressobj(-15)
TAIL = bytes([0, 0, 255, 255])

def inflate(payload):
    return _inflator.decompress(payload + TAIL)
```

### 补环境

worker 逻辑在 `sdk.min.js`，负责持有 WebSocket 和加解密。作者在 Node vm 里替换 `WebSocket`：`send()` 把文本或二进制放进 outbox，服务端帧再经 `ws_recv` 注入。跨 realm 时二进制要 `Array.from` 后再做 base64。

作者原来用 `setInterval(50ms)` 轮询，等 WebSocket 创建后再触发 open。Python 在 `worker_init` 返回后同步来取帧，outbox 仍空，泵送直接结束。日志表现为文本帧数量为 0，并出现 `WS_ERROR` / `WebSocket not ready`，之后才有 `WS_CONNECTED`。改成构造函数里 `setTimeout(0)`，等同步挂好 `onopen` 后再触发，作者称才发出帧。

随后的错误是服务端返回 `[99, "must be str, not int"]`。作者据此认为 worker 自己造的应答不被接受。

### 日志里的消息类型

作者给 `MessagePort.postMessage`、`TextEncoder.encode`、`document.createElement` 加日志。主线程发给 worker 的类型只有 `FINGERPRINT`、`PAGE`、`INIT`。作者的结论是：

1. 这条消息里的 fp 很短，指纹本体不走该消息通道。
2. `page` 是整数，不是字符串。
3. 协议消息就这三种。

canvas 采集顺序作者记为：画布高 16，`getContext("2d")`，`fillStyle` 先后为 `#f60`、`#069`、`rgba(102,204,0,0.7)`，`fillRect` / `fillText("SpiderDemo", ...)`，最后 `toDataURL()`。data URL 原值不入库。WebGL 走 `WEBGL_debug_renderer_info` 和参数 `37446`，另外有 `canPlayType("audio/mpeg;")` 与 `getVoices()`。

调用归属：`WebSocket.send` 在 `sdk.min.js`，canvas / WebGL / voices / `FINGERPRINT` / `PAGE` 在 `jsvmp2.js`。二者经 `MessageChannel` 通信，作者称并没有真正的 Worker。收到 `FINGERPRINT` 到发出应答之间，作者没有观察到环境属性访问，因此认为更长的 fp 不是这一秒现采的。

### 密钥机制

作者称给 S 盒挂 Proxy 得到 0 次命中，因为 VMP 加载时已经把函数抓进闭包；改 `Function.prototype.toString` 会因原生性校验而断流。于是不解码 VMP，直接调用沙箱里已经暴露的原语。作者列出的名字是：`S` / `S_INV`、`expandKey`、`spiderEncrypt`、`spiderEncryptBytes`、`spiderDecryptBytes`、`msgpackEncode` / `msgpackDecode`、`toBase62` / `fromBase62`。

challenge 明文被描述为固定长度的 msgpack（作者写 18 字节）。候选包括 seed、token、ads、固定串以及它们的拼接。作者称命中的是 seed 字符串本身：没有派生、没有 IV、没有 nonce。因此换 seed 就换密钥流，旧会话的 challenge 不能拿到新会话里解。具体 seed、密钥和明密文样值不入库。

### 加密契约

作者自造应答时，服务端返回 `[99, "unpack(b) received extra data."]`。作者把它读成：服务端是先解密，再 `msgpack.unpackb`，再做字段校验。长度对照是：把 base62 字符串或十六进制字符串当明文加密，结果比浏览器应答长；把明文字节（`Uint8Array`）交给 `spiderEncryptBytes`，长度才与浏览器应答相同（作者写 89 字符）。根因是字符串被当成明文又编了一层。

作者称 challenge、应答、翻页请求三帧都做了解密后再加密的回环，并与浏览器帧一致。帧样值不入库。该一致是来源陈述。

### 应答从哪来

worker 自造的应答走了回退：`cmd` 为 99，fp 回显调用方给出的短数组。浏览器路径同样是 `cmd` 99，但 fp 更长（作者计数为 38），含屏幕尺寸一类环境数。具体数组不入库。作者称 stub 环境补不齐这些值，扩展失败才回退；服务端那句 `must be str, not int` 来自这条回退。

作者没有去补全 worker 环境，而是按日志里的结构自己组 38 个值。作者称两轮不同 seed 都通过，并据此认为服务端对 fp 具体值只存储不校验。这仍是 source-report。合法应答时服务端不回复，继续翻页才有数据；非法应答才回 `[99, ...]`。

### 翻页与数字

翻页请求被解成：

```text
{"cmd": 4, "page": <int>, "ts": <毫秒时间戳>}
```

页数据是虚拟 DOM。作者称数字在长度为 3、首元素为 16、第三元素为数字字符串的节点里。提取函数按这个形状递归，字典则继续走值。服务端会发 WebSocket PING（opcode 9）；不回 PONG（opcode 10，载荷原样）会等到超时。

### 提交

作者称 100 页、每页 10 个数，共 1000 个数，求和后：

```text
POST /authentication/api/jsvmp2_challenge/submit/
```

正文含 `answer` 和 `challenge_type=jsvmp2_challenge`。作者写出的响应是 `success` 与 `is_correct` 均为真。具体答案数字不作为本次结果；本次没有提交。

### 作者总结的经验

1. 服务端错误文本会暴露 msgpack 解包和字段类型检查。
2. VMP 可以当黑盒：沙箱全局里已经有加密和 msgpack 原语。
3. 已知明文和密文对撞密钥，比逆密钥调度便宜；明文来自 worker 回显，密文来自帧。
4. 给 `postMessage`、`TextEncoder.encode`、`createElement` 打日志，用来看 VMP 内部看不到的输入输出。
5. Node vm 跨 realm 时，`Uint8Array`、类和钩子可能失效，钩子要 `runInContext` 进目标 realm。
6. 「协议没跑起来」可能是 `setInterval` 与同步泵的时序，不是服务端拒绝。

## 复用边界

以上帧长、错误字符串、函数名和拼接顺序都来自该篇 source-report。本次没有复现握手、加密、翻页或提交，不能把作者的「答案正确」当成 `runtime-observation` 或 `server-accepted`。

不提供完整客户端。凭证和密钥只有机制，没有可直接使用的原值。题目站版本、`sdk.min.js` 与 `jsvmp2.js` 的具体版本都未知。
