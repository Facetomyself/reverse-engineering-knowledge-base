# 菠萝包轻小说 SFSecurity：mt19937 nonce 与自定义编码 MD5

> 来源: 语雀 xiaofeng777/android_example
> 原始发布时间: 2026-04-24
> 归档日期: 2026-09-06
> 分类: signature-algorithms
>
> 菠萝包轻小说（`com.sfacg`）请求头 `SFSecurity` 在 5.1.54 上可离线还原：`/dev/urandom` 种子经 mt19937 生成 UUID v4 `nonce`，再对 nonce / timestamp / deviceToken / 固定 key 做自定义编码后拼成 93 字节，标准 MD5 即 `sign`。5.2.x 把算法放进匿名内存，unidbg 需要先过自定义 linker，不能再按映射 SO 偏移当完成。

## 收录说明

原文：[菠萝包轻小说](https://www.yuque.com/xiaofeng777/android_example/nizu0lcsgh6mwgdc?singleDoc#)。公开页以 5.1.54 算法还原为主；作者写明 ArtMethod / 自定义 linker 的实战演示和附件脚本另放 B 站与知识星球，本篇只归档页内可复核的算法与方法。截图 OCR 乱码、未脱敏 deviceId、APK 转储包名和星球导流未收录。

知识星球同日摘要见 [菠萝包 轻小说 trace算法还原](xfq-crypto-notes-compilation/xfq-20260424-01.md)。mt19937 实现见 [mt19937伪随机.py](xfq-crypto-notes-compilation/xfq-undated-01.md)。HashFinder 原理见 [unidbg插件-哈希-明文扫描](xfq-crypto-notes-compilation/xfq-20260419-01.md)。

## 案例边界

| 项 | 内容 |
|---|---|
| 包名 | `com.sfacg` |
| 观察版本 | 5.1.54（算法主线）；5.2.18 / 5.2.54（自定义 linker + 匿名内存） |
| Java 入口 | `com.sf.security.AuthConfig.getSFSecurity` |
| Native | `libsfdata.so` |
| 目标字段 | 请求头 `SFSecurity`：`nonce`、`timestamp`、`devicetoken`、`sign` |
| 5.1.54 路径 | unidbg 补 maps / `clock_gettime` 后可出参 |
| 5.2.x 路径 | spawn 有 Frida 检测；`RegisterNatives` 难钩；函数不在映射 SO，而在匿名内存 |

公开页把 5.2.x 的对抗变化概括为：算法本身更新不大，但业务 SO 用自定义 linker 把核心代码释放到匿名内存。这时 `registerNatives` 拿到的地址不能当文件 RVA，unidbg 也不能只 `load` 原 SO。页内没有给出 linker 实现细节。

## 5.1.54 出参形状

固定 `clock_gettime` 后，unidbg 一次 `getSFSecurity` 的本地复现形如：

```text
nonce=<uuid-v4>
timestamp=<unix-ms>
devicetoken=<device-token>
sign=<32-hex-md5>
```

作者给出的一组本地 fixture（不是线上抓包）：

```text
nonce=FD57BB58-B88C-417B-B2AA-B2AEA8764F03
timestamp=1775747085949
devicetoken=910D166A-736E-3231-8B21-8D12DFD75F16
sign=27F506663D5191A6A483BCEBC374F9C1
```

`sign` 是标准 MD5，不是魔改压缩函数。工作量在拼出 MD5 之前的 93 字节明文。

## 用 Merkle-Damgård 特征抓明文

样本混淆重，IDA 可读性差，主线走指令 trace + HashFinder。

MD5 是 Merkle-Damgård：消息按 64 字节分块，最后一块以 `0x80` 起垫，尾部写 bit 长度。作者在 trace 里看到：

- 尾部出现 `0x80`、`0x00` 填充和长度 `0x2e8`
- `0x2e8 = 744 bit = 93 字节 = 64 + 29`
- 同一 PC 上 `str` 多次写出可见字符，符合「先写满一块再写残块」

因此 HashFinder 第一次扫到的 29 字符只是最后一块，前面还有完整 64 字节块。按 PC 正则抽出两块后拼成：

```text
QP4Q9MPQ1OPPO2097P8739O77M9CA2O4ME852Q34QO63PN763P18BBO4A9O56P0O13N86OM968895QD853Q91GRMQN2GO
```

对该串做标准 MD5，即得到 `sign`。不要把中间某次哈希日志当成最终明文：作者先拿到 `13N86OM968895QD853Q91GRMQN2GO`，CyberChef 对不上，才回头按填充长度补前一块。

## 明文四段

93 字节不是一次写成的。`memcpy` 反复打两个缓冲，地址循环出现：

| 顺序 | 缓冲 | 长度 | 抽出片段 |
|---|---|---|---|
| 1 | `0x1245e098` | 36 | `QP4Q9MPQ1OPPO2097P8739O77M9CA2O4ME85` |
| 2 | `0x12453168` | 13 | `2Q34QO63PN763` |
| 3 | `0x1245e098` | 36 | 第二轮 36 字节 |
| 4 | `0x12453168` | 8 | 收尾 8 字节 |

同一地址被写两轮，说明外层有循环，不能按「四个无关结构体」拆。

### 36 字节段：nonce 的自定义编码

单字节写入的 PC 经常落在同一处（文中 `0x332cc`）。来源先读 `0x12453090`，再做模 36 查表。

关键指令：

```text
msub w11, w13, w15, w11    ; w11 = w11 - (w13 * w15)
asr  x13, x13, #0x23       ; 算术右移 35，等价于 / 36
csel                       ; 按 cmp w11, #0xa 在 0x30 / 0x37 之间选加数
```

整理后的字母数字编码：

```text
n = input % 36
f(input) = (n < 10) ? (n + 0x30) : (n + 0x37)
out      = isalnum(input) ? input : f(input)
```

`isalnum` 为假时走 `csel` 选编码函数；为真时原字节透传。数字还走另一条 `>> 1` / ASCII 相加路径（文中 `'4' + '5'`），所以不能只用一条 PC 搜齐 36 字节。

编码输入能对回 `nonce`：`FD57BB58` 出现在左侧，后半从 UUID 靠后位置接着读。36 字节段的原料就是 `nonce`，不是独立随机串。

### 13 字节段：时间戳 + nonce 偏移

`2Q34QO63PN763` 的写入也出现 `>> 1`，并有 `memcpy`/`memmove` 从 nonce 缓冲搬数据。偏移不是常数：

```text
[libsfdata.so 0x2b024] add x15, x16, x15
; x16=0x124530c0  x15=0x20  =>  x15=0x124530e0
```

`0x20` 来自 nonce 连续 4 字节分别对 `0x24` 取余后再参与地址计算。也就是：用 nonce 当盐，决定从哪一段拼时间戳编码。

固定 key 不在这四段循环里算出来，而是 SO 内常量，RVA 约 `0xdf860`（运行时 `0x120df860`，基址 `0x12000000`）。

## nonce：mt19937 出 UUID v4

`nonce` 形如 `FD57BB58-B88C-417B-B2AA-B2AEA8764F03`，按字节写入后做 hex 查表。追到的除法：

```text
udiv  ; 0xDA3C1A71 / 0x0FFFFFFF = 0xD
```

同一 PC、不同 `x14` 索引反复从 `0xe4ffc680` 取数，状态机是 mt19937。种子来自 `random_device` / `/dev/urandom`。unidbg 里常见被钉成 `0xF0000000`，与合集里的 [mt19937 示例](xfq-crypto-notes-compilation/xfq-undated-01.md) 一致。

生成后还要套 UUID v4 的版本/变体位，不能把 16 个随机字节直接 hex 连起来。维基百科「梅森旋转算法」足以实现生成器本身。

## 完整管道

```text
seed = /dev/urandom            # unidbg 可固定，例如 0xF0000000
nonce = uuid_v4(mt19937(seed))
parts = custom_encode(nonce, timestamp, deviceToken, fixed_key)
sign  = MD5(parts[0] || parts[1] || parts[2] || parts[3])   # 93 字节
SFSecurity = "nonce=...&timestamp=...&devicetoken=...&sign=..."
```

可复用的打法：

1. 先锁出参字段，不要从混淆控制流猜算法名。
2. 用 `0x80` + 长度字确认 Merkle-Damgård，再决定是 MD5 还是 SHA。
3. 残块长度对不上时，按同一 PC 把前面的 64 字节块补齐。
4. 多字节一起看模式（模 36、`isalnum`、UUID 分段），不要逐字节盲翻。
5. 伪随机只追 seed 和缩放，不要把每次 `extract` 当新算法。

公开页没有给出可独立运行的 `custom_encode` 完整脚本；附件 `mt19937.py` / `generate_nonce.py` / `custom_algorithm.py` 未随语雀正文导出。5.2.x 匿名内存路径仍标未在本页闭合。
