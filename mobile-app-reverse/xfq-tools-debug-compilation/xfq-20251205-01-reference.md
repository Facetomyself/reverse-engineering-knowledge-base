---
schema_version: 2
id: libcxx-std-string-object-layout-reference
document_type: reference
original_date: '2025-12-05'
archived_date: '2026-09-04'
scope:
  targets:
    - libcxx-std-string
  client: unidbg
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20251205-01.md#211-sso-small-string-optimization"
    basis: source-report
  - id: s2
    ref: "./xfq-20251205-01.md#32-如何读取字符串内容"
    basis: source-report
  - id: s3
    ref: "./xfq-20251205-01.md#41-为什么有时候读取失败"
    basis: source-report
  - id: s4
    ref: "./xfq-20251205-01.md#212-内存布局示例"
    basis: source-report
  - id: s5
    ref: "./xfq-20251205-01.md#51-关键点"
    basis: source-report
  - id: s6
    ref: "./xfq-20251205-01.md#42-如何判断是哪种实现"
    basis: source-report
  - id: s7
    ref: "./xfq-20251205-01.md#16-基本概念"
    basis: source-report
  - id: s8
    ref: "./xfq-20251205-01.md#31-从unidbg输出分析"
    basis: source-report
  - id: s9
    ref: "./xfq-20251205-01.md#33-封装好的printstdstring方法"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s4, s5, s7]
    basis: source-report
    limits: 长字符串字段表与总结句可以并列引用。短字符串的字段表、Hello 转储和读取代码互相冲突，不合成一条 ABI。未对照 libc++ 源码。
  - name: interfaces
    anchor: interfaces
    sources: [s2]
    basis: source-report
    limits: 只记录来源代码怎样从 24 字节对象头取出 size 和指针。围栏粘连，不能当可编译片段。
  - name: validation
    anchor: validation
    sources: [s3, s6, s8, s9]
    basis: source-report
    limits: 边界和失败原因都是来源陈述。例题里的 size 大于它自己写下的容量。没有可观察的通过样本。
relations:
  - type: derived_from
    target: "./xfq-20251205-01.md#211-sso-small-string-optimization"
tags:
  - libcxx
  - std-string
  - unidbg
  - source-report
---

# unidbg 里 libc++ std::string 的对象边界

这张卡只回答：来源如何描述 64 位 libc++ `std::string` 对象，以及 unidbg 片段怎样从对象头取出长字符串。短字符串没有唯一布局，本卡不把它收成一条可执行规则。

来源没有可公开定位的原文 URL。布局是否与某一版 libc++ 一致，只到作者自述，本轮没有对照上游源码。

<a id="parameters"></a>
## 参数机制

来源把 64 位对象收成三句：固定 24 字节，用最低位分长短，短字符串内联而长字符串存指针。

> 1. std::string大小固定为24字节(64位系统)
> 2. 通过最低位判断长短字符串
> 3. 短字符串内联存储,长字符串存指针

长字符串表与这三句一致。容量在对象起始 8 字节且最低位为 1，长度在 +8，堆指针在 +16。

> 0x00    8     __cap (容量,最低位=1表示长字符串)
> 0x08    8     __size (字符串长度)
> 0x10    8     __data (指向堆内存的指针)

短字符串表是另一套：最低位仍在首字节，但长度独占 0x01，数据从 0x02 起，共 22 字节。

> 0x00    1     __is_long (最低位=0表示短字符串)
> 0x01    1     __size (字符串长度)
> 0x02    22    __data (内联存储的字符串内容)

Hello 转储又是一套。它把长度编码进首字节，并注明 `0x05<<1`，字符放在 0x08，不是 0x01 或 0x02。

> 0x00: 0a 00 00 00 00 00 00 00  // size=5 (0x05<<1 | 0 = 0x0a)

平台说法也不收成一句。1.6 写 LLVM/libc++ 为 macOS/iOS 常用；同文后又写 Android NDK 通常使用 libc++ 或 libstdc++。

> 2. LLVM/libc++ (macOS/iOS常用)

> Android NDK通常使用 libc++ 或 libstdc++。

新版 libstdc++ 只留了一句阈值，没有字段表，不能并进上面的 24 字节规则。

> 新版libstdc++也使用SSO,但阈值不同(通常是15字节)。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 64 位对象被写成 24 字节，靠最低位分长短 | `std::string大小固定为24字节(64位系统)` | source-report | 来源所称 64 位 libc++ | 未对照上游 |
| C2 | 长字符串是容量、size、指针三槽 | `__cap (容量,最低位=1表示长字符串)` | source-report | 来源的长字符串表 | 未核对真实对象 |
| C1 | 短字符串表把 size 放在 0x01、数据放在 0x02 | `__size (字符串长度)` 与 `__data (内联存储的字符串内容)` | source-report | 来源的短字符串表 | 与 Hello 转储和代码冲突 |
| C3 | Hello 转储把长度编码进首字节 | `size=5 (0x05<<1 | 0 = 0x0a)` | source-report | 该转储示例 | 数据起点在 0x08 |
| C17 | 新版 libstdc++ 只给出约 15 字节阈值 | `阈值不同(通常是15字节)` | source-report | 来源所称新版 libstdc++ | 无偏移表 |

<a id="interfaces"></a>
## 读取入口

直接把寄存器里的地址当成字符缓冲区，读到的是对象头。

> 你读取的不是字符串内容,而是std::string对象的内部结构!

来源代码先读 24 字节，再用首字节最低位判别。长字符串的 size 取自偏移 8，数据指针取自偏移 16，然后再 `mem_read`。

> boolean isLong = (header[0] & 1) == 1;if (isLong) {

> long size = ByteBuffer.wrap(header, 8, 8)

> long dataPtr = ByteBuffer.wrap(header, 16, 8)

短字符串分支不采用字段表，也不采用 Hello 转储。它把首字节右移 1 当长度，并从 offset 1 拷贝。

> int size = (header[0] & 0xFF) >> 1;
> String str = new String(header, 1, size, StandardCharsets.UTF_8);

这段代码粘连，只说明作者写下的读法。不能把它和 C1、C3 合并成一个函数。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 对象地址不是字符指针 | `你读取的不是字符串内容,而是std::string对象的内部结构!` | source-report | unidbg 直接 mem_read | 未复现乱码样本 |
| C6 | 长短由首字节最低位决定 | `(header[0] & 1) == 1` | source-report | 来源的读取片段 | 围栏不可编译 |
| C7 | 长字符串 size 在头的 +8 | `ByteBuffer.wrap(header, 8, 8)` | source-report | 该片段的长字符串分支 | 未跑通 |
| C8 | 长字符串指针在头的 +16 | `ByteBuffer.wrap(header, 16, 8)` | source-report | 该片段的长字符串分支 | 未跑通 |
| C9 | 短字符串代码从 offset 1 读，长度为首字节右移 1 | `(header[0] & 0xFF) >> 1` | source-report | 该片段的短字符串分支 | 与字段表冲突 |

<a id="validation"></a>
## 验证与限制

来源自己的长字符串例题对不上。容量按右移写成 144，长度却写成 286。

> capacity = 0x121 >> 1 = 144

> size = 0x11e = 286

封装函数另加了门槛：长字符串 size 必须大于 0 且小于 100000，数据指针要大于 0x1000；短字符串 size 要在 1 到 22。异常只打印失败，不恢复。

> if (size > 0 && size < 100000 && dataPtr > 0x1000) {

> if (size > 0 && size <= 22) {

读失败被写成三类：地址不是对象、短字符串被误判为长字符串、字符串已被释放。实现选择只写了看 SO 依赖里的 `libc++.so` 或 `libstdc++.so`。IDA 里的类型签名则被说成可以被混淆抹掉。最后要求在 hook 里看结果是否合理，但没有定义合理的反例。

> 1. 地址不是std::string对象

> 2. 短字符串被误判为长字符串

> 3. 字符串已被释放

> // 如果看到libc++.so → libc++实现

> 4. 在hook中验证读取结果的合理性

因此不能把这篇收成流程：短字符串没有唯一布局，例题的 size 大于它写下的容量，通过条件没有反例。绕过 `std::string`、改看 cstring 或 byte 的那条路，来源也写明不是每个应用都成立，本卡不把它当成替代步骤。
