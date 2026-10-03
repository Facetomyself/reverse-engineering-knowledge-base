---
schema_version: 2
id: xfq-rc4-ksa-prga-reference
document_type: reference
original_date: '2026-02-16'
archived_date: '2026-10-02'
scope:
  targets: [rc4]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260216-02.md#22-密钥调度算法-ksa--洗牌"
    basis: source-report
  - id: s2
    ref: "./xfq-20260216-02.md#23-伪随机生成--加密-prga--边发牌边加密"
    basis: source-report
  - id: s3
    ref: "./xfq-20260216-02.md#24-为什么加密--解密"
    basis: source-report
  - id: s4
    ref: "./xfq-20260216-02.md#21-测试数据"
    basis: source-report
  - id: s5
    ref: "./xfq-20260216-02.md#18-关键安全原则"
    basis: source-report
  - id: s6
    ref: "./xfq-20260216-02.md#25-rc4-的安全问题"
    basis: source-report
  - id: s7
    ref: "./xfq-20260216-02.md#31-常见配置差异非标准配置"
    basis: source-report
  - id: s8
    ref: "./xfq-20260216-02.md#32-算法核心修改真正的魔改"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s3]
    basis: source-report
    limits: 只保留讲义写在同一行里的 KSA、PRGA 和异或式。函数体被断行粘连，不补成可编译实现。未重算 S 盒或密钥流。
  - name: decision-flow
    anchor: decision-flow
    sources: [s5, s6, s7, s8]
    basis: source-report
    limits: 空转轮数、S 盒初值和 j 的运算替换是讲义的识别清单，没有对应到某个二进制。N=128 和 5 字节密钥只在正文里出现，本表不单列未整行引用的句子。
  - name: validation
    anchor: validation
    sources: [s2, s4]
    basis: source-report
    limits: 明文、密钥、密钥流和密文都是讲义给出的字符串。本轮没有计算。
relations:
  - type: derived_from
    target: "./xfq-20260216-02.md#22-密钥调度算法-ksa--洗牌"
tags:
  - rc4
  - stream-cipher
  - source-report
---

# RC4 的 KSA/PRGA 与常见改动识别

这张卡用来对照讲义里的标准 RC4：密钥只进入 KSA，PRGA 只吐一个字节再异或，以及作者把哪些改动当成能看出来的非标准实现。它不是某个站点的签名卡。分组密码和 CTR/GCM 的前半篇是概念复述，不进入模块。

<a id="parameters"></a>
## 参数

讲义把 RC4 分成洗牌和吐字节。密钥在洗牌之后不再使用。加密和解密是同一条密钥流再异或一次。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | KSA 的交换下标是上一轮 j、S[i] 与循环密钥字节之和再模 256 | 核心公式就一行:j = (j + S[i] + key[i % key_length]) % 256 | s1，xfq-20260216-02.md:341 | source-report | 只此一行；周围函数体粘连 |
| C2 | 洗牌结束后 PRGA 不再读取密钥 | 密钥只在这里用到!之后的 PRGA 阶段完全不再碰密钥。 | s1，xfq-20260216-02.md:353 | source-report | 未描述 drop 预跑是否算 PRGA |
| C3 | 密钥流字节取交换后的 S[i]+S[j] 再模 256 作为下标 | K = S[(S[i] + S[j]) % 256] | s2，xfq-20260216-02.md:390 | source-report | i、j 的更新式在粘连行里，不补写 |
| C4 | 加解密都被写成同一密钥流的异或，因为异或两次还原 | RC4 加密就是异或,而异或的核心特性:A ⊕ B ⊕ B = A | s3，xfq-20260216-02.md:424 | source-report | 未用密文回代 |

<a id="decision-flow"></a>
## 识别

先看有没有 nonce。讲义把没有 nonce 的密钥重用写成 WEP 失败原因。再看加密循环前有没有空转，以及 S 盒初值、表长和 j 的运算有没有离开标准式。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C5 | 讲义把 RC4 没有 nonce 时的密钥重用写成 WEP 被破解的原因 | 这就是 WEP 被破解的根本原因——RC4 没有 nonce,密钥重用。 | s5，xfq-20260216-02.md:294 | source-report | 没有 WEP IV 结构 |
| C6 | 缓解被写成丢掉前 256 到 1024 字节密钥流，并建议改用 ChaCha20 | 实践中的缓解措施:丢弃前 256~1024 字节的密钥流(RC4-drop),但现在更推荐直接用 ChaCha20 替代。 | s6，xfq-20260216-02.md:451 | source-report | 不是某库的默认参数 |
| C7 | Drop 的做法是 KSA 之后先空跑 PRGA，常见 256、768 或 1024 轮 | 做法:在 KSA 后,PRGA 预跑 N 轮(通常是 256, 768 或 1024 轮),丢弃这些输出,然后再开始加密明文。 | s7，xfq-20260216-02.md:464 | source-report | “通常”不是完整名单 |
| C8 | 加密循环前的空转循环被当成 RC4-Drop 的识别点 | 识别:如果你看代码里在加密循环之前,有一个空转的循环(比如循环 1024 次),那就是 RC4-Drop。 | s7，xfq-20260216-02.md:465 | source-report | 空转也可能是别的初始化 |
| C9 | 标准初值是 S[i]=i；逆序或乘 3 再模 256 被写成魔改 | 标准 RC4 初始化是 S[i] = i。 魔改:S[i] = 255 - i(逆序)或 S[i] = i * 3 % 256 等奇怪的填充方 | s8，xfq-20260216-02.md:474 | source-report | 句子在行末截断，下一种填法未补 |
| C10 | 表长改到 512 时，模数也改成 512 | N=512:数组开到 512,模数变成 512。 | s8，xfq-20260216-02.md:480 | source-report | 未核对 N=128 那一行的断行 |
| C11 | j 的标准加法被改成异或或乘法时，讲义视为核心魔改 | 在标准公式 j = (j + S[i] + key[i]) % 256 中加入异或、乘法等。 例如:j = (j + S[i] ^ key[i]) % | s8，xfq-20260216-02.md:489 | source-report | 模数 256 掉到下一行，不把断行拼回代码 |

<a id="validation"></a>
## 对照值

讲义用同一组明文和密钥给出期望密文，并在 PRGA 小节写出密钥流。两处密文相同，只说明讲义内部一致，不是独立计算。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C12 | 明文被写成 xiaofengfengxiao，16 字节 | 明文: xiaofengfengxiao (16 字节) | s4，xfq-20260216-02.md:318 | source-report | 示例字符串，不是业务样本 |
| C13 | 期望密文被写成 ef00736b210a60edaf87fc2cc89eba3a | 预期密文(hex): ef00736b210a60edaf87fc2cc89eba3a | s4，xfq-20260216-02.md:320 | source-report | 未重算 |
| C14 | 同一例子的密钥流被写成 97691204476f0e8ac9e2924bb0f7db55 | 密钥流(hex): 97691204476f0e8ac9e2924bb0f7db55 | s2，xfq-20260216-02.md:418 | source-report | 中间 8 个字节的逐字节过程被省略 |

## 验证与限制

- 没有本地计算。C12 到 C14 只是讲义里的字符串。
- 代码围栏多处断行粘连。本卡不恢复 KSA 或 PRGA 的完整函数。
- 前半篇对分组密码、OTP、同步流密码和 CTR/GCM 的复述不单列模块。
- 未知：boss直聘的 sp 只被点名，没有密钥、入口或字节；S 盒洗完后的前后 16 字节跨行粘连，未引用；N=128 与 40 位密钥的句子未整行进入结论表。
