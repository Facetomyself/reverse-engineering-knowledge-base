---
schema_version: 2
id: boss-zhipin-13160-yzwg-reference
document_type: reference
original_date: '2025-09-22'
archived_date: '2026-10-02'
scope:
  targets:
    - com.hpbr.bosszhipin
  client: Android
  version: '13.160'
  observed_at: '2025-09-22'
sources:
  - id: s1
    ref: "./xfq-20250922-01.md#xxss直聘13160讲义"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留来源对 sig、sp 形状的原句。盐的字节、RC4 密钥原文、头第 20 位的运算式和证书指纹都不在本卡。作者用 13.163 的 so 看纯算，和 13.160 安装包不是同一份。
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只保留来源点名的 Java 方法和 so。unidbg 补环境步骤散在缺图的叙述里，不收成可执行加载器。
relations:
  - type: derived_from
    target: "./xfq-20250922-01.md#xxss直聘13160讲义"
tags:
  - boss-zhipin
  - md5
  - rc4
  - lz4
  - source-report
---

# BOSS直聘 13.160：sig 加盐 MD5 与 sp 的 LZ4、RC4、码表替换

这张卡只回答：`com.hpbr.bosszhipin` 13.160 的 `sig` 和请求体 `sp`，在来源正文里被定位到哪个入口、被说成什么算法。不提供可运行纯算。盐字节、RC4 密钥原文、证书指纹、本地路径和扫描器命中的路径列表都不进入本卡。作者自称 unidbg 与内存对上，只保留为 source-report。

<a id="parameters"></a>
## 参数机制

来源把全文收成两句：`sig` 是加盐 MD5，`sp` 是 LZ4、RC4，再加码表改过的 Base64。安装包文件名写的是无加固的 13.160，扫描器结论是未发现加固特征。`libdexvmp` 只被点了一句「可能存在 vmp」，没有展开。

`sig` 在 Java 层被认定是 `com.twl.signer.a.h`，不是旁边看过的 `w3.d.a`。第一个参数像未加密的请求体，第二个参数是 null。返回字节在转字符串之前已经是十六进制。`v3.0` 这一段是 so 加上的。so 名是 `libyzwg.so`，日志 TAG 是 `YZWG`，注册被描述成动态注册。纯算倒查停在 `1C38c`，来源称寄存器里带盐，并且「就是个简单的 md5」。盐本身没有写进正文。

`sp` 从 Java 进 native，来源记下的动态注册偏移是 `209a4`。纯算时来源改用 IDA 7.5 打开「最新版 13.163」的 so，否则控制流平坦化看不全。因此下面的偏移不能直接套回 13.160 的安装包。`0x21020` 由 JNI 日志对上汇编。`1ceb8` 把标准 Base64 里的 `+`、`/`、`=` 换成 `-`、`_`、`~`。往前是标准 Base64，来源用 `aAbcdefghijklmn` 这种 IDA 字符串前缀认出码表，并称断点对上了。再往前被认成标准 RC4：`2e680` 有交换、被猜成 init，密钥在第二个参数，格式被说成 UTF-8。密钥原文不收录。RC4 之前有 LZ4，压缩长度再加 24 才是后面的填充长度。头部叙述是：先放一段头，第 8 位填 0，第 12 位是压缩长度，第 16 位是原文字节长度，第 20 位是这两个长度再运算的结果。运算式只写「问了下 ai」，正文没有式子。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | sig 被写成加盐 MD5 | sig:加盐md5 | s1 :60 | source-report | 盐字节不在正文 |
| C2 | sp 被写成 LZ4、RC4 和改码表 Base64 | sp:lz4编码+rc4加密+码表魔改型b64 | s1 :62 | source-report | 未复算 |
| C3 | 签名入口被认定是 a.h | 就是a.h,也就是第四个; | s1 :643 | source-report | 调用栈图缺失 |
| C4 | 返回缓冲在转字符串前已是十六进制 | 返回的字节数组已经做了十六进制处理了 | s1 :646 | source-report | 未见输入输出对 |
| C5 | v3.0 在 so 中拼接 | 也是在so层中加上的 | s1 :649 | source-report | 拼接位置只有叙述 |
| C6 | so 名为 libyzwg.so | libyzwg.so | s1 :650 | source-report | 未对 so 做静态复核 |
| C7 | 1C38c 被说成带盐的普通 MD5 | 测试发现就是个简单的md5而已 | s1 :692 | source-report | 盐不在正文 |
| C8 | 纯算 so 来自 13.163，不是 13.160 包 | ida7.5+最新版13.163的so | s1 :712 | source-report | 偏移不能跨版本套用 |
| C9 | 1ceb8 做 Base64 字符替换 | 1ceb8基本就是做了个替换 | s1 :727 | source-report | 替换字符在同一句，本表不重抄符号 |
| C10 | 替换前被说成标准 Base64 | 这个码表对比之后是个标准b64 | s1 :737 | source-report | 码表全文不在正文 |
| C11 | RC4 被说成标准实现 | 所以这个也是标准rc4 | s1 :792 | source-report | 密钥原文不收录 |
| C12 | LZ4 长度再加 24 对齐先前的填充 | lz4_压缩的长度,然后+24 | s1 :804 | source-report | 第 20 位运算式缺失 |
| C13 | 头部第 8 位被写成 0 | 第8位填了0 | s1 :812 | source-report | 未复算 |
| C14 | 第 12 位被写成 LZ4 压缩长度 | 第12填了v10:v10就是前面lz4压缩计算得到的 | s1 :814 | source-report | 未复算 |
| C15 | 第 16 位被写成传入数据长度 | 第16填了v5,v5就是a3,也就是传入数据的长度 | s1 :816 | source-report | 第 20 位的运算式不在正文 |

<a id="interfaces"></a>
## 来源点名的入口

| 材料 | 来源点名的入口 |
|---|---|
| sig | `com.twl.signer.a.h`；so `libyzwg.so`，TAG `YZWG` |
| 被看过但作者否定的签名候选 | `w3.d.a` |
| sp | 动态注册偏移 `209a4`，汇编侧 `0x21020`、`1ceb8`、`2e680` |
| 扫描器附带 | `libdexvmp.so` 被单独点名，没有分析 |

quote：`209a4,我们直接unidbg补然后再用他的控制台去搞纯算吧`（s1 :665）。这只说明作者打算用 unidbg 控制台，不是一份补环境清单。

## 验证与限制

正文没有盐、没有 RC4 密钥可抄录的必要，也没有头第 20 位的运算。13.160 与 13.163 的 so 被作者自己拆开用。大量 ApkCheckPack 路径命中和证书主题是扫描器输出，Charles 证书指纹不进入本卡。缺图、缺验收反例、缺失败出口，所以不把这篇收成流程。
