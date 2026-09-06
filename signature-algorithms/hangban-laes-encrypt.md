# 航班管家 laesEncryptStringWithBase64：魔改 AES-like 纯算还原

> 来源: PDF 归档 `航班管家 ai还原 全过程.pdf`
> 原始发布时间: 2026-04-17
> 归档日期: 2026-09-06
> 分类: signature-algorithms
>
> `com.hbgjbangbang.CryptoTool.laesEncryptStringWithBase64` 不是标准 AES 套壳。
> JNI 只做 UTF-8 / hex 解码 / 自定义 Base64；核心在 `libhbgjbangbang_crypto_tool.so`
> 的 `hbgjbangbang_LAES_ecb_encrypt`。key 前 4 字节是模式头，轮密钥用滚动异或派生，
> AddRoundKey 改成 nibble 查表，S-box 与 T-box 均非标准 AES。

## 分析目标

Java 入口：`HangBan.java` → `com.hbgjbangbang.CryptoTool.laesEncryptStringWithBase64(String, String, byte[])String`。

样本（只作算法回放，不是账号）：

| 字段 | 值 |
|------|------|
| 明文 | `4575259160971777252101` |
| `key_hex` | `1b2aeb17` … `a34f08`（hex 解码后 180 字节） |
| IV | `null` |
| 包名 | `com.flightmanager.view` |
| 目标 so | `libhbgjbangbang_crypto_tool.so` |

目标是脱离 unidbg/JNI/IDA 的纯算法，不是“调通模拟器”。

## 发现过程

### 1. trace 先钉输入输出

在 `trace_aes.log` 里按 JNI / 明文 / `key_hex` / so 符号检索，关键命中：

- `GetStringUTFChars` 拿到明文 `4575259160971777252101`，长度 `0x16`（22 字节）
- 第二个字符串是长 hex，即 `key_hex`
- 进入 `libhbgjbangbang_crypto_tool.so::hbgjbangbang_LAES_ecb_encrypt`
- JNI 最终 `NewStringUTF("BEQYoxZzvqCJYkySYfg4qWeTXnZZpgdXWqDPmRjkSsA=")`

结论：Java 不是调标准 AES，后续看 native。

### 2. IDA 函数关系

| 地址 | 角色 |
|------|------|
| `0x3a2c` | `Java_com_hbgjbangbang_CryptoTool_laesEncryptStringWithBase64` JNI 包装 |
| `0xd6c` | `hbgjbangbang_LAES_ecb_encrypt` |
| `0xfe4` | `sub_FE4` 调度 / 参数校验 / 伪 key schedule |
| `0x18b4` | `sub_18B4` 单分组核心轮函数 |

调用链：JNI `0x3a2c` → `hbgjbangbang_LAES_ecb_encrypt` → `sub_FE4` → `sub_18B4`。

### 3. JNI 包装层只做四件事

1. 明文：`GetStringUTFChars` / `GetStringUTFLength`，按 UTF-8 进 native。
2. `key_hex`：每两个 hex 字符 `strtoul(..., 16)`，等价 `bytes.fromhex`。
3. 调 `hbgjbangbang_LAES_ecb_encrypt(plain, plain_len, out, &out_len, key_bytes, key_len, 1)`。
4. 手写 Base64（表 `aAbcdefghijklmn…`），不是系统 `Base64`。

Base64 只是输出包装，不是核心算法。

### 4. `sub_FE4`：模式、padding、伪 key schedule

`hbgjbangbang_LAES_ecb_encrypt` 很短，真正关键在 `0xfe4`。

模式头（`key_hex` 前 4 字节 `1b 2a eb 17`）：

```text
switch (a7[3] ^ *a7)     # 0x17 ^ 0x1b = 0x0c → case 12
校验 a7[1] == 0x2A
校验 a7[2] == 0xEB
```

前 4 字节是算法头 / 路径选择，不是普通 AES key 前缀。

case 12 下：`block size = 16`，加密路径，ECB。函数名 `*_ecb_encrypt` 与此一致。

padding 是 PKCS7：`memset(&p_3[item_count_1], n16_2, n16_2)`。明文 22 字节，`22 % 16 = 6`，pad `0x0A`，变成两组 16 字节。

轮密钥不是标准 AES 扩展。`key_material` 180 字节，输出 176 字节：

```python
round_keys[i] = key_material[i + 4] ^ key_material[(i + 1) % 3]  # i = 0..175
```

前 4 字节不进正常轮密钥；用前 3 字节做滚动异或种子，后 176 字节混成轮密钥材料。直接拿前 16 字节跑标准 AES-128/ECB 对不上。

### 5. 排除“魔改 key + 标准 AES”

用派生出的前 16 字节跑普通 AES-128/ECB/PKCS7，得到：

```text
pyki1UcGr+g9Ag4jG+LBwDMcWt2exf3LmCPZgeVXWWc=
```

真实 trace：

```text
BEQYoxZzvqCJYkySYfg4qWeTXnZZpgdXWqDPmRjkSsA=
```

因此轮函数本身也改了，必须拆 `sub_18B4` 并提表。

### 6. `sub_18B4`：AES-like 表驱动

初始轮不是 `state[i] = plaintext[i] ^ round_key[i]`，而是 nibble 查表混合：

```python
def _mix(tbl, left, right):
    hi = tbl[(left & 0xF0) | (right >> 4)] & 0xF0
    lo = tbl[((left & 0x0F) << 4) | (right & 0x0F)] >> 4
    return hi | lo
```

中间轮是 4 个自定义 T-box（`dword_6660/5760/5B60/5F60`）加混合表 `byte_5360`。列映射仍像 ShiftRows/MixColumns 骨架：

```text
(0,5,10,15)
(4,9,14,3)
(8,13,2,7)
(12,1,6,11)
```

末轮用 `byte_6360`（S 盒/行移位风格）和 `byte_5660`（与轮密钥混合），都不是标准 AES 表。标准 AES S-box 开头是 `63 7c 77 7b`；该样本 `_S` 开头是 `ff 7e e2 88`。

### 7. 从表偏移固化纯算

| so 偏移 | 纯算名 | 用途 |
|--------|--------|------|
| `0x5360` | `_X` | 中间轮 nibble 混合 |
| `0x5560` | `_U` | 初始轮混合 |
| `0x5660` | `_V` | 末轮混合 |
| `0x5760` | `_T1` | T-box |
| `0x5B60` | `_T2` | T-box |
| `0x5F60` | `_T3` | T-box |
| `0x6360` | `_S` | 末轮替换 |
| `0x6660` | `_T0` | T-box |

表固化后不再依赖 unidbg / JNI / IDA / trace。

### 8. Python 回放

流程：UTF-8 → PKCS7 → 16 字节分组 → 自定义 AES-like block → 拼接 → Base64。

`hangban_algo.py` 对上述样本输出 `BEQYoxZzvqCJYkySYfg4qWeTXnZZpgdXWqDPmRjkSsA=`，与 trace 一致。这是样本输入/输出闭环，不是“看起来像”。

## 相对标准 AES 的五点魔改

1. 前 4 字节是模式头，不是普通 key。
2. 轮密钥：180 字节材料 → 滚动异或得到 176 字节，不是 AES-128/192/256 schedule。
3. AddRoundKey 换成 nibble 查表混合，不是 byte XOR。
4. S-box 不是标准 AES S-box。
5. 中间轮 T-box 表值全部自定义；只保留 T-box 外形。

保留的部分：16 字节分组、ECB、PKCS7、多轮表驱动、末轮无 MixColumns 风格的骨架。

## 完成口径

`localReproduced` = 同一明文/`key_hex` 离线脚本输出与官方 JNI 返回的 Base64 一致。`serverAccepted` 仍要独立业务 readback。标准 AES 套壳假设已被同一对输入输出证伪。
