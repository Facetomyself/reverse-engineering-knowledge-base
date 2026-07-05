# Qidian SO 逆向分析报告

> 工具: radare2 6.1.8 + IDA Pro 9.3 (idalib)

## 文件清单

| 文件 | 大小 | 架构 | 核心功能 |
|------|------|------|------|
| libfock.so | 154KB | ARM64 | QDSign 生成、JNI 动态注册 |
| libfockrt.so | 1.2MB | ARM64 | QuickJS 引擎、fockrt 密钥协商 |
| libnib.so | 138KB | ARM64 | 设备指纹 (ibex) |
| libknobs.so | 150KB | ARM64 | 服务端配置 (sora) |
| libcrypto.so | 1.6MB | ARM64 | OpenSSL (未被 fock 导入) |

## libfock.so 分析

### QDSign 结构

```
QDSign = Base64(128 字节签名) = 172 chars (无空格)
         └─ 60 chars (chunk 1) + 60 chars (chunk 2) + 52 chars (chunk 3)
         └─ 解码: 45 + 45 + 38 = 128 bytes
```

- 128 字节 = 1024 bit ← 典型 RSA-1024 签名尺寸
- 前 21 chars (~15 bytes) 为静态前缀 `R7TCs6Tou2X1UIwpRMMiP` → FockKey 标识符
- 后 113 bytes 随 URL 变化 → 实际签名字段

### 关键函数

| 函数 | 地址 | 大小 | 推测 |
|------|------|------|------|
| JNI_OnLoad | 0x9690 | 892B | RegisterNatives 注册所有 JNI |
| fock_uksf | 0xad60 | 800B | Update Key Signing Function — 主签名入口 |
| fock_lk | 0xac58 | 264B | Lock — 文本加密 |
| fock_35775553 | 0x16f60 | 160B | Hex 编码 (引用 hex 表) |

### 加密算法表 @ 0x20150

```
MD2, MD4, MD5, RIPE(MD160), SHA1, SHA224, SHA256, SHA384
```

**关键发现**: libfock.so **无任何加密库导入** (无 OpenSSL/RSA/HMAC/EVP 导入)。密码算法均为 **自实现** (静态编译进 so)。

### Hex 编码表 @ 0x20100

```
0123456789abcdef fedcba9876543210
```
被 8 个不同函数引用 — 用于 hex 编解码。

## libfockrt.so 分析

### 架构

- 内嵌 **QuickJS** JavaScript 引擎
- JNI 方法: `Java_com_yuewen_fockrt_vm_QuickJS_createContext/Runtime/Value*`
- JS 代码负责 fockrt.yuewen.com 的密钥协商协议

### fockrt 协议

```
GET https://fockrt.yuewen.com/files?t=1
Headers:
  App-Key: 60256761-e7d0-4406-8254-c6d0bde2c306 (静态)
  Uid: 7ec64622-36ad-4885-a24f-21d10908c2d1 (设备UUID)
  Bundle-ID: com.qidian.QDReader
  Sign: ae912d92aa71d98efbb1fe408bdc82cb (32 hex = MD5?)
  Timestamp: 1782549007
Response:
  {"status":0, "data": [{"d": "RgBjS8AB5ayO/..."}]}
  data.d → Base64 → 119 bytes → 加密的 bootstrap key
```

**Sign 公式**: MD5(?) — 所有候选组合已穷举测试未命中。可能包含嵌入在 JS 字节码中的密钥/盐值。

## Bootstrap 密钥链

```
1. fockrt.yuewen.com/files?t=1 → 返回加密 bootstrap key (119 bytes)
2. 解密 bootstrap key → 生成 QDSign for bookcontent/getkey
3. druidv6/argus/api/v4/bookcontent/getkey → 返回 FockKey {Key, Version}
4. FockKey → FockUtil.addRetrofitH() → 128-byte signature → Base64 → QDSign
```

## 360 Jiagu 对抗

| 方法 | 结果 |
|------|------|
| frida-server spawn | hooks 安装成功，Java VM 被秒杀 |
| frida-server attach | ptrace 被占用，无法附加 |
| frida-gadget LD_PRELOAD | 注入成功，Java 层被检测并杀死 |
| frida-gadget listen+wait | 连接成功，会话很快断开 |

## 后续突破点

1. **IDA 反编译**: 接受 IDA 许可证后，Hex-Rays 可将 `fock_uksf` (800B) 反编译为伪 C 代码
2. **QuickJS 字节码提取**: 从 libfockrt.so 的 .rodata 段提取 JS 字节码
3. **Unicorn 模拟**: 用 Unicorn 引擎模拟 ARM64 代码，输入测试数据观察输出
