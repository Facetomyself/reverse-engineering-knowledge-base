---
schema_version: 2
id: xiaoheihe-13368-hkey-reference
document_type: reference
original_date: '2025-10-23'
archived_date: '2026-10-02'
scope:
  targets:
    - com.max.xiaoheihe
  client: Android
  version: '1.3.368'
  observed_at: '2025-10-23'
sources:
  - id: s1
    ref: "./xfq-20251023-01.md#小黑盒_13368讲义"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留 hkey 的分层叙述和正文里写得出的常量。码表索引的后半、MixColumns 的逐条位运算、RSA 公钥、nonce 和 h_src 都不在正文。调试日志里的第三段字符串和内存转储不收录。
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只保留 JNI 注册名和 phone_num 的 Java 入口。不收录加载日志里的本机路径。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 只记录作者自己写下的对照：把 sub_35F8 的输入改成 abc 后对上公开 SHA1 测试向量，以及一次求和余数与 unidbg 一致。本次没有重跑。
relations:
  - type: derived_from
    target: "./xfq-20251023-01.md#小黑盒_13368讲义"
tags:
  - xiaoheihe
  - hmac-sha1
  - source-report
---

# 小黑盒 1.3.368：hkey 的路径 Base64、HMAC-SHA1 与 MixColumns 校验位

这张卡只回答：`com.max.xiaoheihe` 1.3.368 的 `hkey` 在来源正文里被拆成哪些标准件，以及哪些参数作者没有做完。不提供可运行实现。调试日志中的路径以外的第三段字符串、内存转储、证书主题里的邮箱编码和号码密文都不进入本卡。

<a id="parameters"></a>
## 参数机制

包名 `com.max.xiaoheihe`，版本名 `1.3.368`，版本号 `1012`。扫描结论是未发现加固特征。来源把重点写成：`hkey` 纯算是 Base64、HMAC-SHA1、AES MixColumns、Base32 形态和自定义码表。作者事先把 HMAC 说成「两轮 SHA1」，做完才承认 HMAC 本身就是两轮；正文没有改掉前半的措辞。

每个请求附加一个与时间有关的 `hkey`。入口是 native `encode`。JNI 符号被认成 `_o00_y2y1`。`__strlen_chk` 的长度参数是 8，C 字符串到 `\x00` 为止，来源从抓包看出实际是 7 个字符。前几位用码表 `2345JKMNPQRT6789BCDFGHVWXY`。后两位被说成校验位。

路径先走标准 Base64。来源从 `byte_E9C` 看到 `0x2F`，换成十进制后认成 `ABCD...abcd...012/=`。HMAC 的密钥被说成这条路径的标准 Base64，不是路径原文。密钥短于 65 字节就直接复制，否则先哈希。opad 是 `0x5C` 重复，ipad 是 `0x36` 重复。内层哈希喂 `(key ⊕ ipad) || message`，外层调用长度写成 84，也就是 64 字节 opad 加 20 字节内层摘要，对上 SHA1 的长度。来源后来把内层函数 `sub_35F8` 认成标准 SHA1。

从 HMAC 结果往码表走，正文只写清这三步：取 `BYTE3(v50)` 的低 4 位，再 `bswap32`，再与 `0x7FFFFFFF`。后面的索引算术来源说「照着伪 C 写」，式子不在正文。校验位来自 AES 的 MixColumns，不是完整 AES。四个 32 位整数用 `vaddvq_s32` 相加，再对 100 取余，按十进制宽度决定是否补 0。MixColumns 内部的位运算来源称后来让模型改对了，步骤不在正文。

`phone_num` 被说成 Java RSA，输入是区号加号码，公钥不在正文。来源称换号码后结果不变，于是不再跟 native。`nonce` 只写「有点特别的随机」，指向别的文章。`h_src` 跟到一半停下。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 来源对 hkey 的总括 | hkey纯算还原:b64+hmacsha1+AESMixColumns+b32+自定义码表 | s1 :59 | source-report | 前半仍留着「两轮 sha1」的口误 |
| C2 | 包名 | 包名: com.max.xiaoheihe | s1 :129 | source-report | 版本名 `版本名: 1.3.368` 在 :130，版本号在 :131 |
| C3 | 无加固特征 | 未发现加固特征 | s1 :136 | source-report | 只是扫描器字符串结论 |
| C4 | hkey 被说成与时间有关 | hkey是个时间相关的token | s1 :545 | source-report | 时间如何进入明文没有单列公式 |
| C5 | 走 encode | 最后发现这个hkey走的encode函数 | s1 :546 | source-report | 类名在后面的注册日志里 |
| C6 | 符号名 | _o00_y2y1 | s1 :549 | source-report | 未做静态复核 |
| C7 | 可见长度是 7 | 所以实际长度是7 | s1 :557 | source-report | 依据是作者的抓包观察 |
| C8 | 自定义码表 | 2345JKMNPQRT6789BCDFGHVWXY | s1 :572 | source-report | 索引后半不在正文 |
| C9 | 末两位是校验位 | 发现后两位主要是校验位 | s1 :598 | source-report | 未复算 |
| C10 | 路径编码被认成标准 Base64 | 012/=的码表 | s1 :618 | source-report | 码表地址是 byte_E9C，见 :611 |
| C11 | HMAC 密钥是路径的标准 Base64 | 密钥是前面路径的标准b64 | s1 :767 | source-report | 该行后部的 Base64 文本不收录 |
| C12 | 长密钥先哈希 | 如果密钥长度小于65字节,直接复制;否则先哈希 | s1 :687 | source-report | 伪 C 与汇编粘在同一行 |
| C13 | opad / ipad 是 0x5C / 0x36 | opad: 0x5C重复16次 | s1 :691 | source-report | ipad 在 :694 |
| C14 | 外层长度按 SHA1 的 20 字节计算 | 84 = 64(opad) + 20(inner_hash长度) | s1 :754 | source-report | 未复算 |
| C15 | 索引提取的前三步 | BYTE3(v50) & 0xF | s1 :2071 | source-report | bswap32 与 0x7FFFFFFF 在 :2072、:2073 |
| C16 | 校验位只用 MixColumns | 没有用到aes但是把aes的部分算法给扣下来,用作生成校验位 | s1 :2102 | source-report | 列混合内部步骤不在正文 |
| C17 | 校验位对 100 取余 | 对100求余数 | s1 :2112 | source-report | 该句里的一次余数不收录；相加见 :2108 |
| C18 | 不足两位则补 0 | 如果小于就是一位数需要补0 | s1 :2128 | source-report | 格式化被说成 sprintf 式的十进制 |
| C19 | phone_num 是 Java RSA | java层的rsa而已 | s1 :516 | source-report | 公钥不在正文 |

<a id="interfaces"></a>
## 来源点名的入口

`libnative-lib.so` 在 `JNI_OnLoad` 里为 `com.max.xiaoheihe.utils.NDKTools` 注册三个方法：`checkSignature`、`encode`、`getrsakey`。hkey 走 `encode`。`phone_num` 的 Java 入口被说成 `com.max.xiaoheihe.utils.z.a`，参数是区号字段加号码字段。

quote：`NDKTools, encode`（s1 :817）；`libnative-lib.so`（s1 :819）。

<a id="validation"></a>
## 作者写下的对照

来源先假定 `sub_35F8` 是标准 SHA1，用真实缓冲对不上。原因被写成自己在内嵌的 `00` 处把后面的字节丢了，实际长度是 72。改成输入 `abc` 之后，来源称输出对上了公开测试向量。另一次校验位路径里，四个 32 位整数相加再对 100 取余，来源称和 unidbg 的那一次结果一样。unidbg 调用 `encode` 时来源写「不用补额外代码就出值了」。这些都是作者自述，本次没有重跑。MixColumns 函数体没有留下可对照的逐步结果。

quote：`abc标准的sha1`（s1 :2030）；`他塞了一点00来混淆试听`（s1 :2033）；`将4个32位整数相加`（s1 :2108）。

## 验证与限制

nonce、h_src、RSA 公钥、码表索引后半和 MixColumns 内部都不在正文。抓包一节只点出号码体、cookie 字段名 `x_xhh_tokenid`、验证码 code、一个像腾讯点选的 WebView，以及阅读接口上的 `h_src`，没有可复用的请求序列。数美 id 作者写明没研究。缺完整步骤、验收反例和失败出口，不收成流程。
