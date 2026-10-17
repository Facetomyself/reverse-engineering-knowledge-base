---
schema_version: 2
id: wechat-wcdb-cipher-reference
document_type: reference
original_date: unknown
archived_date: "2026-10-08"
scope:
  targets: [wechat-windows]
  client: windows
  version: "4.1.13.65"
  observed_at: unknown
sources:
  - id: s1
    ref: ./wechat-wcdb-cipher.md#source-body
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录来源写的 SQLCipher/WCDB 页参数和密钥形态差异。未打开数据库，未核对 4.1 之后的构建。掩码字节留在来源归档，不在本卡重复。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: HMAC 公式按来源摘录。迭代 2 次只用于 MAC 密钥，不是主密钥的 256000 次。未做自检。
relations:
  - type: derived_from
    target: ./wechat-wcdb-cipher.md#source-body
  - type: supplements
    target: ./wechat-wcdb-schema-reference.md#interfaces
tags: [wechat, wcdb, sqlcipher, aes]
---

# 微信 4.1 本地库的页加密和 HMAC

这张卡只回答两件事：来源给 WCDB 页写了哪些 encryption 参数，以及它用什么判断密钥对不对。表分工在库结构参考里。这不是请求 signature。

<a id="parameters"></a>
## 页加密参数

来源把 4.x 本地库写成 WCDB 封装的 SQLCipher 4。

| 项 | 来源的值 |
|---|---|
| 算法 | AES-256-CBC |
| 页大小 | 4096 |
| reserve | 80（IV 16 + HMAC-SHA512 64） |
| 主密钥派生 | PBKDF2-HMAC-SHA512，256000 次 |
| 盐 | 每库独立 16 字节，在 page 1 前 16 字节 |

来源对 4.0 的陈述是：派生后的 raw key 以 `x'<64 hex><32 hex salt>'` 明文留在进程内存。对 4.1+ 的陈述是：不再缓存这份明文；密钥在 `com.Tencent.WCDB.Config.Cipher` 对象图里，blob 再被 32 字节循环 XOR 掩码挡住。掩码和对象内偏移只在 [来源归档](./wechat-wcdb-cipher.md#source-body)，本卡不复制。来源称每库 blob 实测 99 字节。

page 1 的 IV 不在页内，由密钥派生；page 2 及以后的 IV 才在页尾 reserve。因此 page 1 第一块明文不是 `SQLite format 3` 的开头。来源还提醒 reserve 大小在 16 字节大端块的第 4 字节。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 页加密是 AES-256-CBC，4096 字节页，reserve 80，主 KDF 为 PBKDF2-HMAC-SHA512 × 256000 | s1 加密机制 | source-report | 来源的 4.x 口径 | 未打开文件 |
| C2 | 4.1+ 不再把 raw key 明文放进进程；对象图里的 blob 有固定 XOR 掩码 | s1 的 4.0/4.1 对照 | source-report | 来源点名的 4.1.13.65 | 掩码与偏移未复现；掩码不是用户密钥 |
| C3 | page 1 的 IV 不在页内 | s1 踩坑节 | source-report | SQLCipher 这一约定的来源陈述 | 未做预言机 |

<a id="validation"></a>
## 用页 HMAC 判断密钥

来源不用“能不能查出一行”当标准。page 1 的 HMAC 被它写成：

```text
mac_salt = page1[0:16] XOR 0x3a
mac_key  = PBKDF2-HMAC-SHA512(enc_key, mac_salt, iterations=2, dklen=32)
expected = HMAC-SHA512(mac_key, page1[16:4032] || LE32(1))
stored   = page1[4032:4096]
```

MAC 的 KDF 迭代是 2，和主密钥的 256000 次不是同一个数。空库（`page_count=1` 且无表）在来源里是正常文件，不能用行数判断密钥。

`message_content` / `source` 旁的 `WCDB_CT_*` 是压缩标记：来源写 `0` 为明文、`4` 为 zstd。这是列编码，不是 encryption 参数。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 密钥真伪用来源给出的 page 1 HMAC 公式，MAC KDF 只迭代 2 次 | s1 HMAC 节 | source-report | 该公式的来源陈述 | 未计算样本 |
| C5 | 空库不能用“有没有行”判断密钥 | s1 踩坑节 | source-report | 来源点名的空库文件名 | 未打开那些文件 |

## 验证与限制

没有 signature、token 或 fingerprint 模块。4.0 内存明文扫描和 AES 暴力扫描被来源保留为备用，并写明在 4.1+ 上没有命中。本轮没有进程，也没有数据库文件。
