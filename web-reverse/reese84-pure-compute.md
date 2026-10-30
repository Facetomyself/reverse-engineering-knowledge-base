---
schema_version: 2
id: reese84-pure-compute
document_type: archive
original_date: unknown
archived_date: "2026-10-30"
scope:
  targets: [reese84]
  client: web
  version: unknown
  observed_at: "2026-10-28"
sources:
  - id: s1
    ref: https://mp.weixin.qq.com/s/KGLV7-gLseIbzRERn7mmxw
    basis: source-report
relations:
  - type: supplements
    target: ./products/reese84.md#常见链路
source_completeness: partial
tags: [reese84, vmp, pow, encoding, source-report]
---

# Reese84 反混淆、VMP 反编译与 p 生成（来源报告）

来源讨论航空站点上的 Reese84：从当前 JS 提取字段目录、编码计划和动态常量，再在本地把指纹结构编成参数 `p`。文首写明「文章由 ai 生成内容注意甄别」。发表日期未知。`observed_at` 只用作者写下的 2026-10-28 测试批次，不是本次编辑的观测时间。

产品命中和放行口径已经在 [Reese84 参考](./products/reese84.md)。本文不重复 Cookie 名、过渡页和业务放行清单，只保留这篇来源里的指令、编码和 PoW 结构。Canadian North 那份案例是另一条 VM 执行交接，也不在这里重写。

## 清洗与完整性说明

- 文首「文章由 ai 生成内容注意甄别」保留在本节，不当成额外证据。
- 删除文末购买、联系和「教程购买」导流，以及四张 1px 占位图。图片内容无法恢复。
- 作者没有给出 `oxc.js`、`get_84.js` 的完整源码，指纹文件、cookie、token 和 `p` 的具体样值也不进入正文。
- 作者写的「0.2s～0.5s 出可用 cookie」和「50 次查询全部成功」只作为 source-report。本次未复现，不升为 `runtime-observation` 或 `server-accepted`。
- 因此完整性为 partial。

## 来源正文

### 链路

作者把流程写成：当前挑战 JS → 外层反混淆 → VMP 语义还原 → 提取常量、字段目录和编码计划 → 结合指纹结构、当轮输入和 PoW → 本地组装编码得到 `p` → 提交后收下 token → 业务请求携带状态并检查业务 JSON。

挑战脚本提供当版参数和编码规则。本地算出 `p` 后提交，服务端返回 token，业务请求再用 `x-d-token` 等字段携带。作者最终保留的四个文件名是 `oxc.js`、`reese84_fp.json`、`get_84.js`、`flght_search.py`。相同版本 JS 用提取缓存，新版本现场反编译，PoW 按当轮挑战求解。

### 外层字符串解码

外层是字符串解码、别名链和常量折叠。概念示例（作者标明不是原样本）是：别名指向解码函数，用常量参数替换解码调用，再折叠数值和字符串，从而读到属性名，并继续找 VM 的数据入口和执行器。

一份外层审计样本约 823 KB，作者记录 3174 次解码替换、1967 次表达式折叠、319 个别名移除。这些数字被用来检查转换是否异常缩水。这个阶段只处理外层 JS；时间、随机数和环境调用留到运行阶段。

### 三元指令

作者分析的一份 VM 基线用槽位和组合子构造调用图，执行模型包含柯里化调用和显式延迟求值。指令是三个小端 Uint16：

```text
[target, functionSlot, argumentSlot]
```

分发效果是：

```js
slots[target] = slots[functionSlot](slots[argumentSlot]);
```

槽位里可以是部分应用函数、延迟节点或具体值。条件、循环和异常由组合子表达。反编译把槽位对象提升为常量、成员访问、普通调用、方法调用、构造调用，以及条件、循环、短路和异常处理。

每次调用单独分配局部 frame，嵌套函数经父 frame 访问闭包。作者称早期版本共用局部数组，交错调用会覆盖父函数数据。

历史基线记录 86046 条三元指令、225 个 VM 函数，未识别 handler 和未绑定 VM 标识符均为 0。作者写明这些数字来自早期基线，闭包和调用用隔离样例对照，没有跑完整浏览器流程。

### 迁到 OXC

后续 AST 基础设施换成 `oxc-parser`、自定义遍历和适配层，并用 `astring` 生成代码。`oxc.js` 串起反混淆、`vmpReverse.js` 的 VM 恢复、目录提取和字符串折叠。作者称主要开销在 AST 遍历、Path、克隆、作用域和 GC，parser 本身占比小。

换打印器后，数字成员访问从 `123["toString"]()` 变成 `(123)["toString"]()`。原先向前读数字的提取遇到右括号就停，常量提取失败。作者称修正后重新对比了 catalog、plans、动态常量和固定输入下的完整 `p`。对比用的 `p` 原值不入库。

### catalog、plans 和动态常量

提取入口经过反混淆、VMP 还原、目录与计划提取、前导常量求值和字符串折叠。输出四类：版本相关常量（例如 `st`、`sr`）、字段目录 catalog、编码计划 plans、采集与计算配置（音频、绘图、WASM 和分支开关）。catalog 决定字段和回调的对应，plans 保存变换顺序和参数，生成器同时读两者。

作者保存的提取审计覆盖 10 组记录、5 份源码，目录规模出现 348 和 354。字段数不变不能单独当成同版本。提取入口检查必要常量、未解决语义和配置范围，失败就报错。

### 指纹文件怎样参与生成

`reese84_fp.json` 在来源里保存字段树、历史环境样本、设备数据和音频表。本文不收录该文件的任何样值。作者区分的结构字段是：`i` 对应值的位置，`cid` 是容器，`fieldId` 是字段标识，`packed` 描述子容器引用。`packed: []` 只表示没有子容器引用，不能据此判断屏幕高度是不是空。行尾中文注释是说明，不是字段值。空字符串、空对象、null 和 undefined 要保留各自的类型。

生成时按当版 catalog 和 plans 匹配指纹树，用当轮派生子覆盖历史位置，先重建子容器，再按父容器写入，最后得到 Base64 形式的 `p`。旧样本里已经编码好的子容器字节可能绑着旧随机数或旧计划，不能当成通用素材。概念式是：`p = Encode(当前编码计划, 指纹结构, 当轮动态字段, 当前随机输入)`。固定环境值来自保存的 fp；时间、随机数、CRC、PoW 按当轮输入生成。

### p 的二进制编码

编码分成序列化、密钥生成、字节变换和容器组装，最后对二进制做 Base64。

每个容器有 buffer、length、seed 和 cursor。seed 使用本轮 `cr`。buffer 起始写入四个字节 `bin0`，length 和 cursor 从 4 开始。字段顺序是：值的内容，执行该字段的变换计划，类型/长度尾标，再写小端 fieldId。

```js
function appendField(state, fieldId, value, transform) {
  serializeValue(state, value, transform);
  appendUint32(state, fieldId);
}
```

类型和长度合并为 `type | (length << 4)`：

| 值类型 | 内容和尾标 |
| --- | --- |
| null | 尾标 0 |
| undefined | 尾标 1 |
| true / false | 尾标 2 / 3 |
| number | 8 字节小端 Float64，尾标 4 |
| string | UTF-8 字节，尾标 5 |
| array | 起始标记 6，递归写各项，尾标 7 |
| object | 起始标记 8，按 `Object.keys` 顺序递归写键和值，尾标 9 |
| 已编码子容器 | 子容器原始字节，尾标 10 |

数组和普通对象的内容长度包含起始标记。递归写内部成员时不单独执行外层字段计划，写完后统一变换。变换范围是 `buffer[cursor:length]`。计划执行完才把 cursor 移到当前 length，然后追加类型尾标和 fieldId。因此下一次变换还会盖住上一字段的尾部元数据。

每个 plan 有 `firstSeed` 和 `keyLength`，第二个种子是本轮 `cr`。作者给出的 PRNG 保持 JS 有符号 32 位运算，两处右移都是 `>>`：

```js
function createPrng(firstSeed, secondSeed) {
  let first = firstSeed;
  let second = secondSeed;
  return function next() {
    let left = first;
    const right = second;
    first = right;
    left ^= left << 23;
    left ^= left >> 17;
    left ^= right;
    left ^= right >> 26;
    second = left;
    return (first + second) % 4294967296;
  };
}
```

调用 `next()` `keyLength` 次，每次取 `next() & 255`。

字段的 operations 有序。参数可以是常数、key 的某一字节、key 的切片或整个 key。作者列出的操作是：`reverse-segment`、`rotate-segment-left/right`、`swap-adjacent`、`interleave-key`（每个原字节后插入一个循环 key 字节，段长翻倍）、`rotate-left/right-bytes`（位数为 `(amount % 7) + 1`）、`add-key`（`((byte + (keyByte & 127)) % 256) ^ 128`）、`subtract-key`（`((byte + 256 - (keyByte & 127)) % 256) ^ 128`）、`feedback-xor-encode/decode`。

反馈异或编码的初始 previous 为 113：当前字节与 `key[i % key.length]`、previous 异或，然后 previous 改成编码结果。解码也从 113 开始，但 previous 更新为输入密文。操作顺序从当前 plans 读取，不是固定全局顺序。

生成器按 `cid` 分组，先编码子容器。节点用 fieldId、出现次数和目录位置找回调，再取 plan。运行时覆盖值优先于 fp 里的历史值。根容器完成后，把开头的 `bin0` 改成 `bin1`（作者写 `setUint32(0, 829319522, true)`），按源码截去末尾 8 字节，再 Base64。固定的是序列化和变换函数；随脚本变化的是目录、计划顺序、种子和配置。缓存保存这些提取结果。

### PoW

作者称生成时间的主要开销在 PoW。当前 SHA1 分支按挑战给出的输入、目标摘要和搜索范围枚举候选，命中后返回候选和耗时。结果作为当轮动态字段进入 `p`，不是固定设备指纹。具体挑战、seed、target 和 `p` 不入库。

最初逐个候选调用 Node 哈希。后来用没有宿主导入、也没有 DOM 或目标站 VMP 的四路 SIMD WebAssembly 算术模块分批计算，找到后再用 Node SHA1 独立校验一次。同一固定挑战、相同搜索顺序下，作者保存的单次对照是：10 万候选 143.25 ms 对 5.01 ms，100 万 1519.42 ms 对 45.87 ms，500 万 6417.77 ms 对 232.94 ms。500 万这一组作者写成约 27.55 倍。作者同时写明，线上两轮挑战的工作量不同，不能直接拿耗时相除。这些毫秒数是来源记录，本次没有重跑。

### 提取缓存

正式缓存按完整 JS 源码 SHA256 与提取器 SHA256 一起查找。源码或提取器变化都会失效；未命中或缓存损坏则重新提取。作者的离线回归：同一套输入冷提取 1071.71 ms，热读 5.63 ms，命中路径不启动 OXC 子进程。缓存检查还覆盖源码变化、提取器变化、损坏恢复、禁用和写入失败。每五分钟采集 JS 的后台任务只做观察和提取，不持续提交 `p`。

另一次 10 次同版 JS 查询里，作者称提取缓存全部命中、业务全部成功，但 PoW 的原始挑战、完整求解输入、seed 和 target 各有 10 个不同值。作者明确写了：没有提交过上一轮 PoW 答案，因此没有「旧答案是否被服务端接受」的结论。同挑战的本地摘要校验不能代替跨轮提交。

### 作者的 50 次查询

离线对照固定时钟、随机数和挑战，比较编码计划与完整 `p`。请求回归从空 cookie 会话开始，记录本地 `p` 与实际提交内容的摘要，再核对返回 token 和业务状态。摘要和 token 原值不在来源正文里，这里也不补。

作者称 2026-10-28 对同一航线与日期顺序做了 50 次查询，每次新进程、新会话，失败即停，批次层不额外重试。保存的表是：50/50 成功；每次 10 个行程组合；缓存命中 49 次；1 次现场提取后成功；查询主流程平均约 3.60 秒；本地 generate（含 PoW）平均约 525 ms，其中 PoW 约 483 ms，其余约 42 ms。作者自己写了这些时间有包含关系，不能简单相加；也没有覆盖同一会话长时间续期，更不能保证以后的站点版本。本次没有复现这 50 次。

### Canvas 与音频

动态绘图在作者所称 `folded.js` 约 5538 行，输出截取辅助函数约在 1951 行和 2170 行。画布 600×160，poi 保存图形指令。初始种子从 `floor(采集起始毫秒 / 1000) + sr` 的 SHA1 末三个十六进制字符转成整数、右移两位再加 1。颜色通道每次 `seed = 22661 * seed % 32749`，再 `seed % 256`。连续三次得到 RGB，配合指令里的 globalAlpha。`shape=0` 走 `fillRect`；`shape=1` 走 `beginPath`、`arc`、`fill`、`closePath`。画完读取左上角 5×5，复制到新画布，导出 PNG data URL，取 `substr(33, poil)` 后继续处理。data URL 不入库。

作者称本地 `canvas_png` 已有整数矩形、像素混合和 PNG 编码，圆形分支还没有。两组共 266 份样本里，88 份与浏览器有差异，合计 168 个 RGBA 字节不同。这是来源计数，本次没有对拍。

音频在 `folded.js` 约 1312–1467 行。`OfflineAudioContext(1, 765, 44100)`。波形取 `poa[0]`，triangle 用 1500 Hz，其余 1000 Hz。`poa[1…5]` 分别是 threshold、knee、ratio、attack、release。连接是 Oscillator → DynamicsCompressor → destination，`start(0)` 后离线渲染。第 0 声道截取 `[265, 765)` 得 500 点，再算样本标准差（分母 n−1）、绝对值之和、最小值、最大值，以及 `[300, 306)` 六个点。作者称本地仍从四张历史波形表读这 500 点，振荡器和压缩器的数值生成还没有替换查表。波形表原值不入库。

## 复用边界

三元指令、尾标、PRNG、字节变换和 PoW 分支都是这篇来源的结构描述。作者的耗时、50 次成功、缓存命中和「出 cookie」速度都没有在本次复核。缺少完整生成器源码、指纹样值和图片。不能把某一版 catalog 规模或某一组毫秒数当成当前站点仍接受的证据。
