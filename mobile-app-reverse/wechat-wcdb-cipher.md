---
schema_version: 2
id: wechat-wcdb-cipher
document_type: archive
original_date: unknown
archived_date: "2026-10-08"
scope:
  targets: [wechat-windows]
  client: windows
  version: "4.1.13.65"
  observed_at: unknown
sources:
  - id: s1
    ref: null
    basis: source-report
    citation: "微信 4.x 本地数据库解密原理"
    reason: "原始材料未提供作者名或可公开定位的链接"

source_completeness: complete
relations: []
tags: [wechat, wcdb, sqlcipher, aes]
---

# 微信 4.x 本地数据库解密原理

来源描述微信 4.x 本地库的 SQLCipher/WCDB 参数，以及 4.1 相对 4.0 不再把派生密钥以明文留在进程内存。数据目录用 `<wxid>` 占位，原文就是这样写的。

## 清洗与完整性说明

无图。参数表、HMAC 公式、页布局和来源给出的 32 字节循环掩码按原文保留。该掩码是来源所称的固定混淆常数，不是某个库的密钥，也不是凭据。

<a id="source-body"></a>
## 来源正文

本机实测环境：Windows · 微信 4.1.13.65 · 数据目录 `Documents\xwechat_files\<wxid>\db_storage`

---

## 一、加密机制

微信 4.x 用 **WCDB**（腾讯基于 SQLCipher 4 的封装）加密全部本地数据库。

| 参数 | 值 |
|---|---|
| 算法 | AES-256-CBC |
| 页面大小 | 4096 字节 |
| 每页 reserve | 80 字节（IV 16 + HMAC-SHA512 64） |
| 密钥派生 | PBKDF2-HMAC-SHA512 |
| KDF 迭代 | 256000 |

每个数据库有**独立的 16 字节随机盐**，存放在 page 1 的前 16 字节。

---

## 二、4.0 与 4.1 的关键差异

| 版本 | 密钥存放方式 | 后果 |
|---|---|---|
| 4.0 | 把派生后的 raw key 以 `x'<64位hex密钥><32位hex盐>'` **明文**缓存在进程内存 | 直接扫内存即可，PyWxDump 等工具可用 |
| 4.1+ | **不再缓存明文密钥** | 所有基于内存特征扫描的老工具失效 |

这是本项目存在的根本原因。

---

## 三、4.1+ 的密钥位置：`Config.Cipher` 对象图

密钥存放在 WCDB 运行时的 `com.Tencent.WCDB.Config.Cipher` 对象中，
且 blob 内容经过一层 **32 字节循环 XOR 混淆**——这正是为什么对内存做
AES 暴力扫描也一无所获（密钥在内存里从不以明文形态出现）。

### 遍历步骤

```
1. 在进程内存中搜索类名字符串 "com.Tencent.WCDB.Config.Cipher"
   得到若干 needle 地址

2. 构造匹配模式 (needle地址, 长度29) 的小端 16 字节：
       struct.pack("<Q", addr) + struct.pack("<Q", 29)
   这是 C++ std::string 对象的内存布局（数据指针 + 长度）

3. 命中后回退 0x10 字节读 0x50 字节得到节点：
       node[0x10] == needle地址
       node[0x18] == 29
   校验通过后取：
       config_ptr = node[0x28]

4. 读 config_ptr + 0x88 处 0x28 字节：
       data_ptr = obj[0x08]
       data_len = obj[0x10]
   合理性检查：0 < data_len <= 1024 且 data_ptr 落在用户地址空间

5. 读出 blob，与 32 字节循环掩码 XOR：
       掩码 d2c7442458020000004889442450488b
            450048844c2448488944254048584c24

6. 得到 x'<64位hex密钥><32位hex盐>'，解析出密钥
```

实测每个库的 blob 长度为 **99 字节**（64+32 hex 字符 + 框架字符）。

实现见 `wxdump/keys.py`。

---

## 四、HMAC 校验：判断密钥真伪的唯一标准

不需要尝试解密来判断密钥对不对——SQLCipher 的 page 1 自带 HMAC，
可以直接验算。这是**精确**的：随机 32 字节通过的概率可忽略不计。

```
mac_salt = page1[0:16] XOR 0x3a
mac_key  = PBKDF2-HMAC-SHA512(enc_key, mac_salt, iterations=2, dklen=32)
expected = HMAC-SHA512(mac_key, page1[16:4032] || LE32(1))
stored   = page1[4032:4096]          # 页面末尾 64 字节
assert expected == stored
```

注意迭代次数是 **2**（不是 256000）——这是 SQLCipher 用于生成 MAC 密钥的
固定值，与数据库主密钥的 KDF 迭代无关。

---

## 五、几个容易踩的坑

### 1. page 1 的 IV 不在页内

SQLCipher 用 16 字节盐覆盖了 SQLite 文件头的前 16 字节，所以：

- 偏移 16 处的第一个密文块解出来是文件头的 **16–31 字节**
  （`10 00 01 01 50 40 20 20`），**不是** `SQLite format 3`
- page 1 的 IV 由密钥派生，**不存放在页内**；page 2 及以后的 IV 才在页尾 reserve 区

这一点在写暴力扫描预言机时至关重要（见 `research/test_iv*.py` 的推导过程）。

### 2. reserve 字节的位置

在 16 字节的大端块里，reserve 大小位于**第 4 字节**（偏移 88 bit），不是第 15 字节。
早期版本这里算错，导致预言机自检失败（真实密钥被拒绝）。

### 3. `WCDB_CT_<列名>` 压缩标记

消息表的 `message_content` / `source` 两列都可能被 zstd 压缩：

| 值 | 含义 |
|---|---|
| `0` | 明文 |
| `4` | zstd 压缩，必须先解压 |

实测某会话 25,149 条消息中，`message_content` 有 7,685 条压缩、
`source` 有 24,872 条压缩——**两列都必须先看标记再解码**，
否则会读到乱码。很多工具只处理其中一列，导致部分消息丢失。

### 4. 空数据库是正常的

`solitaire.db`、`weclaw.db` 等本身就是只有一个页面的空库（page_count=1，无表）。
用「能否查到行」判断密钥对错会误判，正确做法是看读取**是否抛异常**。

---

## 六、备用路径

`wxdump/memory_scan.py` 保留了两条独立路径，用于未来微信再次更换密钥存放方式时兜底：

1. **明文密钥扫描** —— 4.0 的老办法，4.1+ 通常返回 0 命中
2. **AES 暴力扫描** —— 利用 page 1 头部的已知明文做预言机
   （7 个固定字节 = 56 bit 已知明文）

第二条路径的预言机可用 `python -m wxdump selftest` 验证：
它会现场生成一个已知密钥的数据库，确认真实密钥被接受、且 20 万个随机密钥零假阳性。

实测在 4.1+ 上暴力扫描 9 分钟返回 0 命中——因为密钥被 XOR 掩码保护，
内存中从不存在明文形态。保留它只是为了应对未来的变化。

---

## 七、相关脚本

| 脚本 | 作用 |
|---|---|
| `wxdump/keys.py` | 生产实现：对象图遍历 + HMAC 校验 |
| `wxdump/memory_scan.py` | 备用路径与预言机 |
| `research/test_iv*.py` | IV 约定的发现过程（4 个迭代版本） |
| `research/diag.py` | 确认 4.1+ 无明文密钥字面量 |
| `research/probe.py` / `dump_ctx.py` | 对象图探测 |
| `research/legacy/config_cipher_scan.py` | 初版密钥提取脚本 |

## 复用边界

这是 encryption 与页完整性校验，不是 signature 或 encoding。偏移、掩码和“实测 99 字节”都是来源对 4.1.13.65 的自述。本轮没有打开微信进程。`WCDB_CT_*` 是列压缩标记，不是密钥。
