# mmtls 协议深度分析

> 基于 `yyb_go` 源码逆向还原。目标：腾讯应用宝 (YYB) / 微信小程序 WMPF 登录与 API 调用链。
> 分析日期：2026-07-05

---

## 目录

1. [架构总览](#1-架构总览)
2. [Record 层 — 帧格式](#2-record-层--帧格式)
3. [握手协议 — 完整 ECDHE](#3-握手协议--完整-ecdhe)
4. [PSK 0-RTT — 快速重连](#4-psk-0-rtt--快速重连)
5. [密码学细节](#5-密码学细节)
6. [ShortLink — 应用数据层](#6-shortlink--应用数据层)
7. [iLink 协议 — 业务层](#7-ilink-协议--业务层)
8. [NewDNS — 服务发现](#8-newdns--服务发现)
9. [完整通信流程](#9-完整通信流程)
10. [安全分析](#10-安全分析)

---

## 1. 架构总览

```
┌──────────────────────────────────────────────────────┐
│                    HTTP API (Gin)                     │
│   /qr → /accounts → /wxapp/getCode|getPhone|operate  │
├──────────────────────────────────────────────────────┤
│                   iLink 业务层                         │
│   ManualAuth (登录)  │  JSAPI Transfer (WX API调用)    │
│   hybridECDHEncrypt  │  wpkg head + AES-GCM + LZ4     │
├──────────────────────────────────────────────────────┤
│                ShortLink 应用帧层                       │
│   magic=0x1110  │  cmd/seq  │  ver=0x076d             │
├──────────────────────────────────────────────────────┤
│                  mmtls 安全层                          │
│   ┌─────────────┐  ┌──────────────────┐              │
│   │ ECDHE 握手   │  │ PSK 0-RTT 快速恢复│              │
│   │ (P-256)     │  │ (access/refresh) │              │
│   └─────────────┘  └──────────────────┘              │
│   Record: ct|version(0xf103)|length|payload           │
├──────────────────────────────────────────────────────┤
│               TCP + 代理 (SOCKS5/HTTP-CONNECT)         │
├──────────────────────────────────────────────────────┤
│              NewDNS (aedns.weixin.qq.com)             │
└──────────────────────────────────────────────────────┘
```

**协议栈层次：**

| 层 | 协议 | 端口 | 方向 |
|---|------|------|------|
| L7 业务 | iLink (ManualAuth / JSAPI Transfer) | — | YYB ↔ 微信后台 |
| L6 应用帧 | ShortLink (magic 0x1110) | — | 封装在 mmtls AppData |
| L5 安全 | **mmtls** (类 TLS 1.3) | 8080/80/443 | YYB ↔ longcloud.weixin.com |
| L4 传输 | TCP + SOCKS5/HTTP-CONNECT | — | 可过代理 |
| L3 服务发现 | NewDNS (HTTP DNS) | 80 | aedns.weixin.qq.com |

---

## 2. Record 层 — 帧格式

mmtls Record 是协议的最小传输单元，结构类似 TLS 1.3 的 TLSPlaintext / TLSCiphertext，但字段语义不同。

### 2.1 Record 结构

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| ContentType   |           0xf103 (Record Version)              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Payload Length        |                                |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                                |
|                     Payload (变长)                              |
|                 (TLSPlaintext 或 TLSCiphertext)                 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

| 字段 | 偏移 | 大小 | 说明 |
|------|------|------|------|
| ContentType | 0 | 1 | 记录类型 |
| Version | 1 | 2 | 固定 `0xf103`（不是 TLS 的 0x0303） |
| Length | 3 | 2 | Payload 长度（big-endian，最大 65535） |
| Payload | 5 | N | 明文或密文，取决于 ContentType 和握手阶段 |

### 2.2 ContentType 枚举

| 值 | 常量 | TLS 等价 | 说明 |
|----|------|---------|------|
| `0x15` | `ctAlert` | Alert | 告警（0-RTT 中用于 early alert） |
| `0x16` | `ctHandshake` | Handshake | 握手消息 |
| `0x17` | `ctAppData` | Application Data | 应用数据 |
| `0x19` | `ctPSKHandshake` | (TLS 1.3 无此值) | **mmtls 特有** — PSK 握手阶段消息 |
| `0x14` | (未命名) | ChangeCipherSpec | 仅在 `knownContentType()` 中判定为已知 |

### 2.3 Record 编解码

**编码 (`buildRecord`):**
```
output = [ContentType:1] [0xf103:2] [len(payload):2] [payload:N]
```

**解码 (`parseRecords`):** 从字节流中循环解析，校验 version == 0xf103 且 ContentType 已知，直到数据不足时停止。返回已解析的 record 列表和消费的字节数。

**关键差异 vs TLS 1.3：**
1. **Version 固定 `0xf103`**，对应 TLS 1.3 的 `0x0303` + 0xee00 偏移（疑似腾讯私有协议族标记）
2. **引入 `ctPSKHandshake (0x19)`** 作为独立的 PSK 握手阶段 ContentType，TLS 1.3 中 PSK 消息复用 `ctHandshake`
3. **无 ChangeCipherSpec (0x14) 语义** — 虽然 `knownContentType()` 接受 0x14，但实际流程中未使用

---

## 3. 握手协议 — 完整 ECDHE

### 3.1 握手概览

```
Client                                          Server (longcloud.weixin.com)
  │                                                    │
  │ ──── ClientHello (ctHandshake, 0x16) ──────────▶   │
  │                                                    │
  │   ◀──── ServerHello + {CertVerify} +               │
  │         {NewSessionTicket} + ServerFinished ────    │
  │         (ctHandshake, 加密在 hsSKey/hsSIV 下)        │
  │                                                    │
  │ ──── ClientFinished (ctHandshake, 加密) ───────▶   │
  │                                                    │
  │   ◀═══════════ AppData 双向加密 ═══════════▶       │
```

mmtls 握手为 **1-RTT ECDHE**，共 3 个 flight：
- **Flight 1**: Client → Server: ClientHello（明文）
- **Flight 2**: Server → Client: ServerHello + CertVerify + NewSessionTicket + ServerFinished（ServerHello 明文，其余 hsSKey 加密）
- **Flight 3**: Client → Server: ClientFinished（hsCKey 加密）

### 3.2 ClientHello 结构

```
ClientHello (以 buildHandshake(hsClientHello=0x01, body) 封装)

Handshake 封装 (对所有握手消息通用):
  [total_len:4][msg_type:1][body:N]
  total_len = 1 + len(body)  (包含 msg_type)

ClientHello body:
  [0x03, 0xf1]          — TLS legacy_version (映射为 mmtls 0xf103)
  [1]                    — 未知标记（可能是 cipher_suites 数量）
  [cipher:2]             — 0xc02b (TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256)
  [client_random:32]     — crypto/rand 随机
  [timestamp:4]          — Unix 时间戳
  [ext_total_len:4]      — 扩展区总长度
    [ext_type:1]         — 0x01 (extKeyShare)
    [ext_len:4]
      [0x00, 0x10]       — 未知前缀（可能是 key_share 条目数标记）
      [2]                — 两个 key_share 条目
      KeyShare #1 (groupSecP256R1):
        [entry_len:4]
        [group:4]        — 0x01 (secp256r1 / P-256)
        [key_len:2]      — 65 (0x41, 未压缩公钥)
        [public_key:65]  — G1 公钥 (04 || x || y)
      KeyShare #2 (group2):
        [entry_len:4]
        [group:4]        — 0x02 (第二条曲线)
        [key_len:2]      — 65
        [public_key:65]  — G2 公钥
      [0,0,0,1]          — 未知尾部
```

**关键观察：**

1. **双曲线 KeyShare** — Client 发送两条 P-256 公钥 (G1, G2)，Server 仅选择 G1 (groupSecP256R1=0x01) 响应。G2 的用途未知（可能在特定场景下启用备选曲线），在逆向实现中 G2 的私钥被丢弃不用。

2. **Cipher 固定 `0xc02b`** — 这是 TLS 1.2 的 `TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256`。但 mmtls 实际不使用 ECDSA 证书，而是通过 CertVerify 消息实现服务端认证。

3. **No SNI, No ALPN** — ClientHello 中无 SNI/ALPN 扩展，说明目标服务是固定的。

### 3.3 ServerHello 解析

```
ServerHello body:
  [0x03, 0xf1]          — legacy_version
  [cipher:2]             — 0xc02b
  [server_random:32]     — 服务端随机数
  [ext_len:4]
    [ext_type:1]         — 0x01 (extKeyShare)
    [ext_len:4]
      [0x00, 0x10]       — 前缀（ClientHello 中也有）
      [2]                — 条目数
      KeyShare #1:
        [entry_len:4]
        [group:4]        — 0x01 (P-256)
        [key_len:2]      — 65
        [public_key:65]  — 服务端 P-256 公钥
      KeyShare #2:       — 可能包含额外公钥
```

**从 ServerHello 中提取：**
- `ServerRandom` → 参与后续密钥派生
- `ServerPubKey` → 与 Client G1 私钥做 ECDH 得到 shared secret
- `ServerGroup` → 必须为 0x01 (P-256)，否则握手失败

### 3.4 CertVerify — 服务端认证

在 ServerHello 之后、Finished 之前，Server 发送 CertVerify 消息（`hsCertVerify=0x0f`）。

mmtls 中的 CertVerify 不承载 X.509 证书链，而是通过以下方式实现认证：
- **隐式认证**：Server 必须持有与 Client 已知的公钥对应的私钥，才能正确派生共享密钥
- **Transcript Hash**：CertVerify 时刻的 transcript hash `hCertV` 被保存，后续用于 PSK 派生

### 3.5 NewSessionTicket — PSK 票据

```
NewSessionTicket body:
  [ticket_count:1]       — 票据数量
  每个票据:
    [entry_len:4]        — 票据条目长度
    [psk_type:1]         — PSK 类型 (1=access, 2=refresh)
    [lifetime:4]         — 有效期（秒，big-endian）
    [...剩余字节...]      — ticket_entry（原始字节）
```

**票据类型：**
| PSKType | 标签 | 用途 |
|---------|------|------|
| 1 | Access PSK | 用于 ShortLink 0-RTT 业务请求 |
| 2 | Refresh PSK | 用于票据续期 |

### 3.6 Finished — 握手完成验证

```
Finished:
  [verify_data_len:2]    — 固定 32
  [verify_data:32]       — HMAC-SHA256(key, transcript_hash)
```

**双向验证**：
- ServerFinished: `finishedVerifyData(handshake_secret, isClient=false, H_final)`
- ClientFinished: `finishedVerifyData(handshake_secret, isClient=true, H_final)`

其中 `H_final` = `SHA256(transcript)`，transcript 包含截止 Finished 之前的所有握手消息。

Client 收到 ServerFinished 后**立即验证** verify_data，不匹配则握手失败。

---

## 4. PSK 0-RTT — 快速重连

### 4.1 触发条件

首次完整 ECDHE 握手后，Server 下发 `psk_type=1` (access PSK) 的 NewSessionTicket。后续请求使用该 PSK 发起 0-RTT，跳过 ECDHE 握手。

### 4.2 PSK ClientHello

```
PSK ClientHello body:
  [0x03, 0xf1]          — legacy_version
  [1]                    — 标记
  [cipher:2]             — 0x00a8 (TLS_PSK_WITH_AES_128_GCM_SHA256)
  [client_random:32]     — 随机数
  [timestamp:4]          — Unix 时间戳
  [ext_total_len:4]
    [ext_type:1]         — 0x01 (extKeyShare，复用字段但含义不同)
    [ext_len:4]
      [0x00, 0x0f]       — 前缀（与 ECDHE 的 0x00,0x10 差 1）
      [1]                — 条目数
      [ticket_entry_len:4]
      [ticket_entry:N]   — 完整的 ticket_entry（含 PSK type + lifetime + 数据）
```

**关键观察：**
1. PSK ClientHello 的 cipher 是 `0x00a8` (TLS_PSK_WITH_AES_128_GCM_SHA256)，复用 extKeyShare 扩展但内容变为 ticket_entry
2. `ticket_entry` 是从 NewSessionTicket 中获取的**完整原始条目**（含 type + lifetime + PSK 数据）

### 4.3 0-RTT 请求构建 (`build0RTTRequest`)

```
0-RTT 请求 = 4 条 Record 串联:

Record 0: ctPSKHandshake (0x19) — 明文
  └── PSK ClientHello

Record 1: ctPSKHandshake (0x19) — 加密 (early_keys, seq=1)
  └── Type8 消息:
      [0x00, 0x00, 0x00, 0x10, 0x08, 0x00, 0x00, 0x00,
       0x0b, 0x01, 0x00, 0x00, 0x00, 0x06, 0x00, 0x12]
      [timestamp:4]

Record 2: ctAppData (0x17) — 加密 (early_keys, seq=2)
  └── ShortLink 封装的业务请求 (envelope)

Record 3: ctAlert (0x15) — 加密 (early_keys, seq=3)
  └── [0x00, 0x00, 0x00, 0x03, 0x00, 0x01, 0x01]  (Early Alert)
```

**注意：** PSK 0-RTT 使用独立的加密密钥 `early_keys`（`derivePSKOneWayKeys(psk, labelEarlyKeys, hs_hash)`），与握手密钥和应用数据密钥完全不同。

### 4.4 0-RTT 响应解析

0-RTT 响应通过 ShortLink HTTP 隧道返回（POST `/mmtls/{timestamp}` 到 `shortcloud.weixin.com`）。

解析过程 (`parse0RTTResponse`)：
1. 从 HTTP body 提取 mmtls records
2. 找到 ServerHello (明文) + AppData (密文)
3. **多候选 Transcript**：尝试 3 种 transcript 组合计算 handshake keys：
   - `pskCH || ServerHello`
   - `pskCH || type8 || ServerHello`
   - `pskCH || ServerHello || type8`
4. 对每种组合，尝试 seq=1,2,3 解密 AppData
5. 用 recvKey (iLink session 的 RecvKey) 进一步解密 ShortLink body
6. 提取 `code` 字段返回

### 4.5 0-RTT 服务器端处理过程（推断）

从 Client 端逆向可推断 Server 端流程：

```
Server 收到 0-RTT 请求:
  1. 解析 Record 0 → 提取 PSK ClientHello 中的 ticket_entry
  2. 用 ticket_entry 查 PSK 数据库，获取 pre_shared_key
  3. 派生 early_keys = derivePSKOneWayKeys(psk, "early data key expansion", SHA256(pskCH))
  4. seq=1 解密 Record 1 → 校验 type8 + timestamp
  5. seq=2 解密 Record 2 → 提取 ShortLink envelope → 执行业务逻辑
  6. seq=3 解密 Record 3 → 确认 early alert
  7. 构建响应:
     - ServerHello (明文)
     - AppData (加密) — ShortLink 封装的业务响应
```

---

## 5. 密码学细节

### 5.1 密钥层次

```
                     G1 私钥 + Server公钥
                           │
                    ECDH(P-256)
                           │
                    SHA256(shared)
                           │
                    ┌──────┴──────┐
                    │   Handshake  │
                    │   Secret     │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        handshake_keys  H_final    CertVerify
         (hsCKey/hsSKey)   │          hash
              │            │       (hCertV)
              │       deriveMaster   │
              │            │         │
              │       Master Secret  │
              │            │         │
              │       app_keys       │
              │    (appCKey/appSKey)  │
              │                       │
              └───────────────────────┤
                                      │
                              derivePSK(secret, hCertV, pskType)
                                      │
                               ┌──────┴──────┐
                          PSK_ACCESS     PSK_REFRESH
                          (type=1)       (type=2)
                              │
                      derivePSKOneWayKeys
                              │
                         early_keys
                     (0-RTT 加密用)
```

### 5.2 HKDF 实现

mmtls 使用标准 HKDF，但 TLS 1.3 的 `Derive-Secret` 用 `HkdfExpandLabel`。

**HKDF-Extract:**
```
HKDF-Extract(salt, IKM) = HMAC-SHA256(salt, IKM)
```

**HKDF-Expand:**
```
HKDF-Expand(PRK, info, L) = T(1) || T(2) || ... (截断到 L 字节)
其中 T(i) = HMAC-SHA256(PRK, T(i-1) || info || counter_byte)
```

**Expand-Label (类 TLS 1.3):**
```
Derive-Secret(Secret, Label, Messages) = HKDF-Expand(Secret, Label || Messages, length)
```

### 5.3 密钥派生公式

**Handshake Secret → Handshake Keys:**
```
hs_hash_input = transcript of ClientHello...CertVerify
hk = Derive-Secret(handshake_secret, "handshake key expansion", hs_hash, 56 bytes)
hsCKey = hk[0:16]   (Client 加密 key)
hsSKey = hk[16:32]  (Server 加密 key)
hsCIV  = hk[32:44]  (Client IV)
hsSIV  = hk[44:56]  (Server IV)
```

**Master Secret → App Keys:**
```
H_final = SHA256(transcript including ServerFinished)
master_secret = Derive-Secret(handshake_secret, "expanded secret", H_final, 32 bytes)
ak = Derive-Secret(master_secret, "application data key expansion", H_final, 56 bytes)
appCKey = ak[0:16]
appSKey = ak[16:32]
appCIV  = ak[32:44]
appSIV  = ak[44:56]
```

**PSK 派生 (从 handshake secret):**
```
PSK_ACCESS  = Derive-Secret(handshake_secret, "PSK_ACCESS",  hCertV, 32)  // pskType=1
PSK_REFRESH = Derive-Secret(handshake_secret, "PSK_REFRESH", hCertV, 32)  // pskType=2
```

**PSK → 0-RTT Early Keys:**
```
H_early = SHA256(pskClientHello)
ek = Derive-Secret(psk, "early data key expansion", H_early, 28 bytes)
earlyKey = ek[0:16]
earlyIV  = ek[16:28]
```

**PSK → 0-RTT Response Handshake Keys:**
```
H_response = SHA256(pskCH || ServerHello)  // 或其他 candidate
hk = Derive-Secret(psk, "handshake key expansion", H_response, 56 bytes)
→ 同 splitBiKeys 分拆
```

**Finished Verify Data:**
```
finished_key = Derive-Secret(handshake_secret, "client finished"/"server finished", nil, 32)
verify_data = HMAC-SHA256(finished_key, transcript_hash)
```

### 5.4 AES-128-GCM Record 加密

```
加密:
  nonce = xorBytes(IV, seq_to_8bytes_be)  // 12-byte IV XOR 8-byte seq
  AAD = [seq:8][content_type:1][version:2 0xf103][ciphertext_len:2]
         共 13 字节
  ciphertext = AES-128-GCM-Seal(key, nonce, plaintext, AAD)

解密:
  nonce = xorBytes(IV, seq_to_8bytes_be)
  AAD = [seq:8][content_type:1][version:2 0xf103][ciphertext_len:2]
  plaintext = AES-128-GCM-Open(key, nonce, ciphertext, AAD)
```

**关键设计：**
1. **Seq-based nonce** — 使用递增的 64-bit 序列号而非随机 nonce，通过 XOR 嵌入到 IV 中，保证每条 record 的 nonce 唯一
2. **Record header 包含在 AAD** — 防止 record 层的类型/版本/长度被篡改
3. **GCM tag 16 字节** — 标准 TLS 1.3 tag 长度

### 5.5 iLink 层 AES-GCM Layout

iLink 层使用不同的加密布局（`aesGCMEncryptLayout` / `aesGCMDecryptLayout`）：

```
Wire Format:
  [ciphertext_body: N-28]  — 去除 tag 的密文体
  [iv: 12]                 — 随机 IV
  [tag: 16]                — GCM 认证标签

Tag 放在末尾的标准 GCM 布局，但 IV 被嵌入到密文中部而非前置。
```

### 5.6 iLink HKDF (ilinkHKDFSalt)

```
ilinkHKDFSalt = "security hdkf expand"  (原文拼写错误 "hdkf" 保留)

用于 ManualAuth 中的混合 ECDH 密钥派生:
  prk = HKDF-Extract(ilinkHKDFSalt, CEK)
  okm = HKDF-Expand(prk, hash, 56 bytes)
```

### 5.7 LZ4 压缩

所有 iLink 层的 plaintext 在加密前经过 **LZ4 全字面量压缩** (`lz4AllLiteral`)：

```go
func lz4AllLiteral(data []byte) []byte {
    // 将所有数据编码为 LZ4 字面量块 (literal-only block)
    // 不做任何匹配/回引压缩，仅添加 LZ4 帧头
    // token = 0xf0 (15 literal length + 0 match length)
    // 后跟 literal length 的 varint 编码
}
```

**实际上这是"假压缩"** — 只做 LZ4 格式封包而不做真正的字典压缩。可能的原因是：
1. 协议规范要求 LZ4 格式但内容已足够紧凑
2. 方便在需要时开启真正的 LZ4 压缩
3. 作为一种数据混淆手段

---

## 6. ShortLink — 应用数据层

ShortLink 是 mmtls AppData 中承载的应用层协议。

### 6.1 帧格式

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Total Length          |           0x1110 (Magic)       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Version (0x076d)      |           Cmd                 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                             Seq                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
|                     Body (变长)                                |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

| 字段 | 偏移 | 大小 | 说明 |
|------|------|------|------|
| Total Length | 0 | 4 | 整包长度 (含 header) |
| Magic | 4 | 2 | **0x1110** — ShortLink 协议魔数 |
| Version | 6 | 2 | 默认 **0x076d** |
| Cmd | 8 | 4 | 命令 ID |
| Seq | 12 | 4 | 序列号 (递增) |
| Body | 16 | N | 业务负载 |

### 6.2 已知命令

| Cmd | 名称 | 方向 | 说明 |
|-----|------|------|------|
| `0x0d7d` | `cmdManualAuth` | C→S | iLink 登录认证 |
| `0x0b41` | `transferCmd` | C→S | iLink JSAPI Transfer (WX API) |

### 6.3 ShortLink 在 mmtls 中的封装

```
mmtls AppData (解密后)
  └── ShortLink 帧
        └── iLink 业务层 (见第 7 章)
```

**发送路径 (sendApp):**
```
iLink plaintext → LZ4 → AES-GCM(wpkg head) → ShortLink(transferCmd)
  → mmtls sendEncrypted(ctAppData, appCKey, appCIV)
```

---

## 7. iLink 协议 — 业务层

iLink 是 YYB 与微信后台通信的业务协议，分两个子协议：
1. **ManualAuth** — 首次登录/会话建立
2. **JSAPI Transfer** — 微信小程序 API 调用

### 7.1 ManualAuth — 登录流程

```
Client                                              Server
  │                                                    │
  │ ① parseLoginBuffer(login_buffer_b64)               │
  │   → ticket, device_id, host_appid                  │
  │                                                    │
  │ ② buildManualAuthRequest:                          │
  │   pb{1: pb{1: appDeviceID, 2: 1901},              │
  │       3: pb{1: ticket},                            │
  │       4: 4, 6: nil, 7: 0, 8: 6}                   │
  │                                                    │
  │ ③ hybridECDHEncrypt(plaintext, serverPub, temp):   │
  │   - 生成临时 ECDH 密钥对                             │
  │   - shared = ECDH(eph_priv, serverPub)              │
  │   - secret = SHA256(shared)                        │
  │   - CEK = random 32 bytes                          │
  │   - encCEK = AES-GCM(secret[:24], CEK)             │
  │   - okm = HKDF(ilinkHKDFSalt, CEK)                 │
  │   - comp = LZ4(plaintext)                          │
  │   - encBody = AES-GCM(okm[:24], comp)              │
  │   → 输出: pb{1:1, 2:pb{1:415, 2:ephPub},          │
  │             3:encCEK, 4:nil, 5:encBody}            │
  │                                                    │
  │ ④ manualAuthHead(deviceID):                        │
  │   wpkg head (25 int fields + 3 bytes fields)       │
  │                                                    │
  │ ⑤ 合并 head + hybrid_body → ShortLink(cmdManualAuth)│
  │                                                    │
  │ ──── mmtls sendApp(cmdManualAuth, body) ───────▶   │
  │                                                    │
  │   ◀──── mmtls recvApp() ◀─────────────────────     │
  │                                                    │
  │ ⑥ parseLoginResponse:                              │
  │   从 wpkg head 后提取 hybrid response               │
  │   hybridECDHDecrypt(response, temp):                │
  │     - 提取 serverRespPub                            │
  │     - shared = ECDH(eph_priv, serverRespPub)        │
  │     - secret = SHA256(shared)                       │
  │     - AAD = SHA256(okm[24:56] || compBody ||       │
  │                    "415" || serverRespPub || credType)│
  │     - comp = AES-GCM-Decrypt(secret[:24], AAD, ct)  │
  │     - plaintext = LZ4-Decompress(comp)              │
  │                                                    │
  │ ⑦ extractSession(plaintext):                       │
  │   → SendKey, RecvKey, F9, UIN, Ticket, DeviceID    │
  │                                                    │
  │ ⑧ mmtls.extractPSKs() → Access PSK (type=1)       │
  │   → 用于后续 ShortLink 0-RTT                        │
```

### 7.2 ManualAuth 密码学详解

**混合 ECDH 加密 (`hybridECDHEncrypt`):**

```
输入: plaintext, serverPub (硬编码在代码中的服务端公钥)

1. 生成临时 ECDH 密钥对:
   eph_priv, eph_pub = ECDH-P256.Generate()

2. 与硬编码的 serverPub 做 ECDH:
   shared = eph_priv.ECDH(serverPub)
   secret = SHA256(shared)   // 32 bytes

3. 加密 CEK (Content Encryption Key):
   hash1 = SHA256("1" || "415" || eph_pub)
   CEK = crypto/rand 32 bytes
   encCEK = aesGCMEncryptLayout(secret[:24], hash1, CEK)

4. 加密 Body:
   prk = HKDF-Extract("security hdkf expand", CEK)
   okm = HKDF-Expand(prk, hash1, 56 bytes)
   hash2 = SHA256("1" || "415" || eph_pub || encCEK)
   comp = LZ4(plaintext)
   encBody = aesGCMEncryptLayout(okm[:24], hash2, comp)

输出: protobuf 封装的 hybrid body
```

**服务端硬编码公钥：**
```
serverPub = 0x04
  ef87876d6478b15f1796eab12068610541173b7176b67f1dcc86683e901acd44
  d18b4ac36938251d0812dd0cf842aa2d6cbb8115712d1c0087dcefc14a44cd58
```
这是标准的 P-256 未压缩公钥 (65 bytes, 0x04 || x || y)，硬编码在应用中。

**安全含义：**
- 服务端公钥硬编码 = 证书固定 (Certificate Pinning) 的等价实现
- 临时 ECDH 密钥对保证前向安全性
- CEK 双层加密：外层用 ECDH secret 加密 CEK，内层用 CEK 派生的 okm 加密 body
- "415" 可能是一个协议版本或魔数

### 7.3 JSAPI Transfer — WX API 调用

登录成功后，通过 iLink Transfer 调用微信小程序 API。

**请求构建 (`buildTransferPacket`):**

```
1. 构建 JSAPI 内层 plaintext (buildJSAPIPlaintext):
   sessionInfo = pb{
     1: "sessionkey",          // session key 字面量
     2: uin32,                 // 用户 UIN
     3: sessDevice,            // 随机 session device ID (MAC 格式)
     4: 1661404927,            // session client version
     5: "UnifiedPCWindows",    // 窗口标识
     6: 0
   }
   
   loginReq = pb{
     1: sessionInfo,
     2: appID,
     4: 1, 5: nil, 6: nil, 7: 1
   }
   
   最外层 = pb{
     1: sessionInfo (windowsName="Windows"),
     2: transferURL (/cgi-bin/mmbiz-bin/js-login 等),
     3: hostAppID (默认 "wxd44977328b36e647"),
     4: 5,                     // 未知
     5: loginReq,              // 内层请求
     6: appID,
     7: transCmdID (1029/1020/1133),
     8: 1610627409,            // 固定时间戳
     9: "WindowsxWebPlugin",   // 插件标识
     10: 573651281             // 未知
   }

2. 加密: aesGCMEncryptLayout(SendKey, nil, LZ4(plaintext))

3. wpkg head 封包: sessionWpkgHead(uin, f9, deviceID)
   - 26 个 int 字段 (client version, flags 等)
   - 4 个 bytes 字段 (deviceID, f9 等)

4. ShortLink 帧:
   inner = ShortLink(transferCmd=0x0b41, seq=0, wpkg + enc)
   
5. Envelope (最外层封装):
   [transferURL_len:2][transferURL:N]
   [transferHost_len:2][transferHost:N]  // "shortcloud.weixin.com"
   [inner_len:4][inner:N]
   前加 [total_len:4]
```

**三个 WX API 端点：**

| API | URL | CmdID | 用途 |
|-----|-----|-------|------|
| js-login | `/cgi-bin/mmbiz-bin/js-login` | 1029 | 获取 wx.login code |
| js-getuserwxphone | `/cgi-bin/mmbiz-bin/js-getuserwxphone` | 1020 | 获取手机号 |
| js-operatewxdata | `/cgi-bin/mmbiz-bin/js-operatewxdata` | 1133 | 操作微信数据 (通用 API) |

### 7.4 WPKG Head 结构

WPKG (微信包) head 是 iLink 层的通用包头格式：

```
wpkg head:
  [varint:1]                   — 标记字节 (固定 1)
  [int_fields...]              — 变长 int 键值对, key 为 varint, value 为 varint
  [varint:0]                   — int 字段终止符
  [bytes_fields...]            — 变长 bytes 键值对, key 为 varint, len 为 varint, 后跟数据
  [varint:0]                   — bytes 字段终止符
  [varint:total_len]           — head 总长度 (用于定位 body 起始)
```

**ManualAuth head 关键字段：**
| Key | Value | 含义 |
|-----|-------|------|
| 1 | 1 | 协议版本? |
| 5 | 524545 | clientVersion |
| 6 | 11 | 未知 |
| 20 | 1504 | 未知 |
| 24 | deviceID | 设备 ID |
| 25 | 17 | 未知 |
| 28 | 1 | 未知 |
| 29 | 1 | 未知 |

**Session (Transfer) head 关键字段：**
| Key | Value | 含义 |
|-----|-------|------|
| 2 | UIN | 用户 UIN |
| 5 | 524545 | clientVersion |
| 22 | UIN | 重复 UIN |
| 25 | 16 | (比登录的 17 少 1) |
| 27 | F9 | 从 ManualAuth 响应提取的 F9 字段 |

### 7.5 Protobuf 编码

iLink 使用自定义的轻量 protobuf 编解码（非标准 protobuf 库）：

**wire type 支持：**
| Wire Type | 值 | 编码 |
|-----------|-----|------|
| Varint | 0 | `tag = (field<<3)|0`, value = varint |
| Length-delimited | 2 | `tag = (field<<3)|2`, length = varint, data = bytes |

**不支持 wire type 1 (64-bit) 和 5 (32-bit)**，遇到则终止解析。

**Varint 编码：** 标准 protobuf varint，每字节低 7 位为数据，最高位表示是否继续。

**智能解析 (`protobufToMap`):** 对 Length-delimited 字段做启发式判断：
- UTF-8 有效 & 可打印 → 转为 string
- JSON 开头 `{` → 视为 JSON string
- 递归解析为嵌套 protobuf → 转为 map
- 否则 → `{"__bytes__": hex}`

---

## 8. NewDNS — 服务发现

mmtls 不依赖系统 DNS，使用微信自有的 HTTP DNS 服务。

### 8.1 查询接口

```
GET http://aedns.weixin.qq.com/cgi-bin/default/getdns
    ?clientversion=0
    &devicetype=Windows
    &uin=0
    &format=json

Host: aedns.weixin.qq.com
User-Agent: MicroMessenger Client
```

备用 IP: `180.153.202.85`（当域名解析失败时直连）

### 8.2 响应结构

```json
{
  "dns": {
    "retcode": 0,
    "domainlist": [
      {
        "name": "longcloud.weixin.com",
        "timeout": 5000,
        "iplist": [{"ip": "x.x.x.x"}, ...],
        "protocollist": [
          {"name": "mmtlsovertcp", "portlist": [8080, 80, 443, 5000]}
        ]
      },
      {
        "name": "shortcloud.weixin.com",
        "iplist": [...],
        "protocollist": [
          {"name": "http", "portlist": [80]}
        ]
      }
    ]
  }
}
```

### 8.3 服务器选择策略

**LongLink (mmtls 握手):**
- 协议: `mmtlsovertcp`
- 端口优先级: 8080 > 80 > 443 > 5000
- 最多尝试 6 个候选
- 去重后按 IP 排序

**ShortLink (PSK 0-RTT):**
- 协议: `http`
- 端口: 80
- IP 去重
- 默认 fallback: `120.241.131.173:80`

### 8.4 DNS 缓存

- 缓存 Key: `"0|Windows"` (clientVersion|deviceType)
- TTL: 30 分钟（可配置）
- 线程安全 (sync.Mutex)

### 8.5 业务域名

| 域名 | 用途 | 协议 |
|------|------|------|
| `longcloud.weixin.com` | mmtls 完整握手 + ManualAuth | mmtlsovertcp |
| `shortcloud.weixin.com` | PSK 0-RTT ShortLink | HTTP (POST /mmtls/{ts}) |
| `aedns.weixin.qq.com` | HTTP DNS 服务发现 | HTTP |
| `open.weixin.qq.com` | 微信 OAuth QR 码 | HTTPS |
| `yybadaccess.3g.qq.com` | YYB OAuth 回调 + Token API | HTTPS |

---

## 9. 完整通信流程

### 9.1 首次登录 (完整 ECDHE)

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Browser │     │ YYB Go   │     │ longcloud│     │  short   │
│  (前端)   │     │ (本服务)  │     │ .weixin  │     │ .weixin  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                 │               │                  │
     │ ① GET /qr       │               │                  │
     │────────────────▶│               │                  │
     │                 │               │                  │
     │                 │ ② WeChat OAuth                 │
     │                 │   open.weixin.qq.com            │
     │                 │   → QR uuid                     │
     │                 │               │                  │
     │ ③ QR Image      │               │                  │
     │◀────────────────│               │                  │
     │                 │               │                  │
     │ ④ 微信扫码确认   │               │                  │
     │                 │               │                  │
     │ ⑤ GET /qr/{id}/poll (长轮询)    │                  │
     │────────────────▶│               │                  │
     │                 │ ⑥ 获取 OAuth code + cookies      │
     │                 │   yybadaccess.3g.qq.com          │
     │                 │               │                  │
     │ ⑦ POST /qr/{id}/confirm         │                  │
     │────────────────▶│               │                  │
     │                 │               │                  │
     │                 │ ⑧ Fetch login_buffer             │
     │                 │   yybadaccess.3g.qq.com          │
     │                 │   → login_buffer (base64)         │
     │                 │               │                  │
     │                 │ ⑨ NewDNS 查询                    │
     │                 │   aedns.weixin.qq.com            │
     │                 │   → longcloud IPs:ports          │
     │                 │               │                  │
     │                 │ ⑩ TCP 连接 + mmtls ECDHE 握手    │
     │                 │   (8080/80/443/5000)             │
     │                 │──────────────▶│                  │
     │                 │   ClientHello ◀───────────       │
     │                 │   ServerHello + Finished         │
     │                 │   ClientFinished                 │
     │                 │──────────────▶│                  │
     │                 │               │                  │
     │                 │ ⑪ ManualAuth (ShortLink appData) │
     │                 │   hybridECDHEncrypt              │
     │                 │──────────────▶│                  │
     │                 │◀──────────────│                  │
     │                 │  → SendKey/RecvKey/UIN/F9/PSK    │
     │                 │               │                  │
     │                 │ ⑫ extractPSKs → Access PSK      │
     │                 │               │                  │
     │ ⑬ 返回账号信息    │               │                  │
     │◀────────────────│               │                  │
```

### 9.2 后续 API 调用 (PSK 0-RTT)

```
┌──────────┐     ┌──────────┐          ┌──────────┐
│  Client  │     │ YYB Go   │          │ short    │
│          │     │ (本服务)  │          │ .weixin  │
└────┬─────┘     └────┬─────┘          └────┬─────┘
     │                 │                     │
     │ POST /wxapp/getCode                  │
     │ {ref, app_id}   │                     │
     │────────────────▶│                     │
     │                 │                     │
     │                 │ ① 查 DB: session 缓存│
     │                 │   有? → 直接用        │
     │                 │   无? → 重建(需 PSK)  │
     │                 │                     │
     │                 │ ② buildJSAPIPlaintext│
     │                 │   + buildTransferPacket │
     │                 │   + build0RTTRequest │
     │                 │                     │
     │                 │ ③ POST /mmtls/{ts}  │
     │                 │   HTTP/1.0          │
     │                 │   Host: shortcloud.weixin.com │
     │                 │────────────────────▶│
     │                 │                     │
     │                 │ ④ 解析 0-RTT 响应    │
     │                 │   parse0RTTResponse │
     │                 │   → code/resp       │
     │                 │◀────────────────────│
     │                 │                     │
     │ ⑤ 返回结果       │                     │
     │◀────────────────│                     │
```

### 9.3 Session 缓存与过期

```
Session 生命周期:
  1. ManualAuth 成功后:
     → 存储 WmpfSession 到 SQLite
       key = accountID + tcpProxy
       blob = {session_keys, psk_entry, shortlink_targets}
       过期 = min(PSK.lifetime, SessionTTL)

  2. API 调用时:
     → 查 SQLite session 缓存
     → 有效 → 直接 0-RTT
     → 过期/不存在 → 重建:
       - 从 account 取 login_buffer
       - 重新执行 mmtls ECDHE 握手 + ManualAuth
       - 更新 PSK 和 session

  3. 调用失败:
     → InvalidateSession → 删除缓存
     → 下次调用触发重建

  4. refreshLiveness:
     → RefreshLoginBuffer (HTTP API)
     → 更新 access_token
     → 标记 "alive" 或 "expired"
```

---

## 10. 安全分析

### 10.1 协议安全性评估

| 方面 | 评估 | 说明 |
|------|------|------|
| 密钥交换 | 安全 | ECDH P-256，临时密钥对 |
| 前向安全性 | 具备 | 每次握手生成新 ECDH 密钥对 |
| 加密算法 | 安全 | AES-128-GCM，业界标准 |
| 完整性保护 | 具备 | GCM 认证标签 + Record AAD |
| 重放保护 | 具备 | Seq-based nonce，每次递增 |
| 服务端认证 | 隐式 | 无证书链，依赖硬编码公钥 + ECDH 隐式认证 |
| PSK 管理 | 基础 | PSK 派生自 handshake secret，票据无加密 |
| 0-RTT 重放 | 有限 | 依赖 timestamp 校验，无单次令牌 |

### 10.2 与 TLS 1.3 的差异

| TLS 1.3 | mmtls |
|---------|-------|
| Record version: 0x0301 (伪装) / 0x0303 (实际) | 0xf103 (固定) |
| 5 种 ContentType | + 0x19 (PSKHandshake) |
| Cipher 0x1301 (TLS_AES_128_GCM_SHA256) | 0xc02b (TLS 1.2 命名) |
| 证书链 (Certificate/CertificateVerify) | 无证书，隐式 ECDH 认证 |
| KeyShare 单曲线 | KeyShare 双曲线 (G1+G2) |
| EncryptedExtensions | 无（扩展在 ServerHello 内） |
| 标准 TLS 库兼容 | **不兼容** — 需专用实现 |

### 10.3 攻击面

1. **硬编码公钥泄露** — serverPub 硬编码在客户端，若服务端私钥泄露则所有会话可解密
2. **0-RTT 重放窗口** — PSK 0-RTT 无显式 anti-replay 机制（TLS 1.3 建议 server 侧维护 ClientHello 哈希白名单）
3. **PSK 存储安全** — PSK hex 编码后存储在 SQLite，无额外加密
4. **login_buffer 敏感** — 包含 ticket 和 device_id，base64 编码存储在数据库，泄露后可冒充登录
5. **DNS 劫持** — NewDNS 走 HTTP 明文，可被中间人篡改返回恶意 IP

### 10.4 逆向方法总结

| 技术 | 应用 |
|------|------|
| 字符串搜索 | serverPub hex, ilinkHKDFSalt, UA string, domain names |
| 常量推断 | 0xf103 (version), 0x1110 (magic), 0xc02b (cipher) |
| 流量对比 | 抓包 → 逐字节匹配 → 确定字段边界 |
| 密码学还原 | GCM tag 位置 → 确定 IV/Key 长度; HKDF labels → 确定密钥层次 |
| 协议状态机 | doHandshake() 的 send/recv 序列 → 还原消息流 |
| fallback 分析 | "all candidates failed" → 发现重试策略; default IP `120.241.131.173` → 硬编码后备 |

---

## 附录 A: 常量速查

| 常量 | 值 | 位置 |
|------|-----|------|
| `recordVersion` | `0xf103` | mmtls_protocol.go |
| `shortlinkMagic` | `0x1110` | mmtls_protocol.go |
| `defaultVer` | `0x076d` | mmtls_protocol.go |
| `cipherECDHE` | `0xc02b` | mmtls_protocol.go |
| `cipherPSK` | `0x00a8` | mmtls_protocol.go |
| `groupSecP256R1` | `0x01` | mmtls_protocol.go |
| `group2` | `0x02` | mmtls_protocol.go |
| `keyLen` | `65` | mmtls_protocol.go |
| `aesKeyLen` | `16` | mmtls_crypto.go |
| `aesIVLen` | `12` | mmtls_crypto.go |
| `gcmTagLen` | `16` | mmtls_crypto.go |
| `clientVersion` | `524545` | ilink.go |
| `appVersion` | `1901` | ilink.go |
| `transferCmd` | `0x0b41` | ilink.go |
| `cmdManualAuth` | `0x0d7d` | mmtls_protocol.go |
| `jsLoginCmdID` | `1029` | ilink.go |
| `phoneCmdID` | `1020` | ilink.go |
| `operateCmdID` | `1133` | ilink.go |
| `sessClientVer` | `1661404927` | ilink.go |
| `hostAppIDDefault` | `wxd44977328b36e647` | ilink.go |
| `ilinkDevice` | `ilinkapp_060000b7b93f6c` | ilink.go |
| `loginBusinessID` | `pc_yyb_auth` | loginbuffer.go |
| `loginAccessKey` | `wgrdg373hy26ww2` | loginbuffer.go |
| `newdnsHost` | `aedns.weixin.qq.com` | newdns.go |
| `newdnsBackupIP` | `180.153.202.85` | newdns.go |
| `longlinkDomain` | `longcloud.weixin.com` | newdns.go |
| `shortlinkDomain` | `shortcloud.weixin.com` | newdns.go |

## 附录 B: HKDF Label 速查

| Label | 用途 | 输出长度 |
|-------|------|---------|
| `"expanded secret"` | Handshake Secret → Master Secret | 32 |
| `"handshake key expansion"` | Secret → Handshake Keys | 56 |
| `"application data key expansion"` | Master → App Keys | 56 |
| `"early data key expansion"` | PSK → Early Keys | 28 |
| `"client finished"` | → Client Finished Key | 32 |
| `"server finished"` | → Server Finished Key | 32 |
| `"PSK_ACCESS"` | Secret → Access PSK | 32 |
| `"PSK_REFRESH"` | Secret → Refresh PSK | 32 |
| `"security hdkf expand"` | iLink HKDF Salt (固定) | — |

## 附录 C: 文件对照

| 文件 | 行数 | 职责 |
|------|------|------|
| `mmtls_protocol.go` | 321 | Record/Handshake 编解码 + ShortLink 帧 |
| `mmtls_crypto.go` | 231 | ECDH + HKDF + AES-GCM + GCM Layout |
| `mmtls_client.go` | 335 | mmtls 客户端状态机 (握手/加解密/PSK) |
| `shortlink.go` | 166 | PSK 0-RTT 请求构建与响应解析 |
| `ilink.go` | 539 | iLink ManualAuth + JSAPI Transfer + wpkg |
| `bytes.go` | 243 | varint/protobuf/LZ4 编解码 |
| `transport.go` | 166 | TCP + SOCKS5 + HTTP-CONNECT |
| `newdns.go` | 264 | HTTP DNS 服务发现 |
| `pool.go` | 461 | 连接池 + 会话管理 + 并发控制 |
| `loginbuffer.go` | 347 | login_buffer 获取/刷新 + 签名 |
