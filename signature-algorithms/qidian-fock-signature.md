# Qidian (起点读书) — 签名算法分析报告

> 时间: 2026-06-27 ｜ 基于: jadx 反编译 + 28MB 流量分析

## 总体架构

起点读书 APP 使用**阅文自研 Fock SDK** 进行请求签名，核心逻辑全部在 **Native层 (.so)** 实现。Java 层只做桥接和调度。

```
请求发起 → OkHttp Interceptor Chain
  ├─ [1] C4984e (QDRequestInterceptor)
  │     └─ FockUtil.addRetrofitH(request) → NATIVE → 注入 QDSign/borgus/cecelia/gorgon/ibex
  ├─ [2] QDRequestAddKnobsInterceptor
  │     └─ native intercept() → 注入 sora
  └─ [3..7] 登录/错误处理拦截器
```

## 7 大签名头详解

### 1. QDSign — 核心请求签名

| 属性 | 值 |
|------|-----|
| 生成位置 | `libfock.so` / `libfockrt.so` 的 `addRetrofitH()` |
| 格式 | Base64 (174~187 chars) |
| 固定前缀 | `R7TCs6Tou2X1UIwpRMMiP` (21 chars) |
| 类型 | 疑似 RSA 签名或 HMAC-SHA256 |

**证据**:
- 所有请求的 QDSign 共享相同 21-char 前缀 → 这是 Fock Key 的固定标识符
- 前缀可能对应 Base64 编码的 RSA 公钥指纹或 HMAC key ID
- 长度因 URL/body 长度而变化 (174 vs 187 chars)
- 每个请求值都不同

```
样本 1 (GET):  R7TCs6Tou2X1UIwpRMMiP65kdT7LAB0gLJWI1G8d9vO...  (174 chars)
样本 2 (POST): R7TCs6Tou2X1UIwpRMMiPzrlHgzK0jWrjmZaxxzUkWL... (174 chars)
样本 3 (POST): R7TCs6Tou2X1UIwpRMMiP/wa5vBQMFvO/25MLcduvqF...  (187 chars)
```

### 2. borgus — 请求哈希

| 属性 | 值 |
|------|-----|
| 格式 | 32-char hex (MD5) |
| 样本 | `57f4e90d64453960b2a5475d16db35cb` |
| 推测 | URL + body + tstamp 的 MD5 |

### 3. cecelia — 版本化签名

| 属性 | 值 |
|------|-----|
| 格式 | `2_` + 68-char hex |
| 样本 | `2_e5317e67a68b059cca9a9ddda492b1f69b7d8ad18a05e90bcb8c853821c4f6ccc7cf` |
| 推测 | Version=2, 68 hex chars = SHA-256? |

### 4. tstamp — 时间戳

| 属性 | 值 |
|------|-----|
| 格式 | Unix 毫秒时间戳 |
| 样本 | `1782546156804` (= 2026-06-27 15:42:36) |
| 用途 | 防重放攻击的时效性参数 |

### 5. gorgon — 设备令牌 (静态!)

| 属性 | 值 |
|------|-----|
| 格式 | 超长 Base64 (~1100 chars) |
| 特殊性 | **所有请求完全相同！** |
| 推测 | 设备注册时生成，长期不变 |

**关键发现**: gorgon 是静态的！这意味着它可以在一次提取后被复用。

### 6. sora — 服务端配置 (Knobs)

| 属性 | 值 |
|------|-----|
| 生成位置 | `QDRequestAddKnobsInterceptor` → `checkKnobsUrl()` |
| 格式 | 超长 Base64 (~1100 chars) |
| 对应 SO | `libknobs.so` |
| 推测 | 服务端下发的环境配置/策略信息 |

### 7. ibex — 设备指纹 (Nib SDK)

| 属性 | 值 |
|------|-----|
| 生成位置 | `com.yuewen.nib.search.cihai(Context)` |
| 对应 SO | `libnib.so` |
| 格式 | 超长 Base64 (~800+ chars) |
| 内容 | 设备环境 + 风控检测结果 |

**采集的指纹维度** (反编译 `com.yuewen.nib.search.judian()`):
- 硬件信息: `ro.boot.hardware`, `ro.setupwizard.mode`, `ro.secureboot.lockstate`
- 设备属性: `ro.product.model`, `ro.product.brand`, `ro.product.board`, `ro.product.manufacturer`
- CPU: `ro.product.cpu.abi`, `ro.product.cpu.abi2`
- 安全检测: Xposed, Frida (端口/文件描述符/task), Root (PATH/pkg/Magisk/ATTR)
- 模拟器检测: CPU info, 文件特征, eth0 MAC, Multi-box, VMOS
- 辅助功能: Accessibility, Auto.js, UIAutomator
- SCRCPY 检测, ADB 检测, LSPosed 检测
- GUID, QIMEI, 签名 MD5, 包名

## Native 库清单

| 文件 | 大小 | 职责 |
|------|------|------|
| `libfock.so` | 154K | Fock 核心 — 签名生成 |
| `libfockrt.so` | 1.2M | Fock Runtime — 密钥管理/加密 |
| `libnib.so` | 138K | Nib SDK — 设备指纹 |
| `libknobs.so` | 150K | Knobs — 服务端配置策略 |
| `libcrypto.so` | 1.6M | OpenSSL — 基础密码运算 |
| `libjiagu_vip.so` | — | 360加固 — 反调试/完整性 |

## 密钥管理流程

```
1. APP 启动 → FockUtil.run()
     ├─ checkAssets() → 校验 assets 完整性
     ├─ checkMeta() → 校验 META-INF 签名
     └─ checkSign() → 校验 APK 签名

2. requestKey(context) → 向服务器请求 FockKey
     GET/POST druidv6.if.qidian.com/argus/api/v1/client/getFockKey (?)
     返回: { key: "...", version: "..." }
     → 存入 SharedPreferences + 内存

3. 每次 HTTP 请求:
     FockUtil.addRetrofitH(request)
     ├─ 读取缓存的 FockKey
     ├─ tstamp = System.currentTimeMillis()
     ├─ borgus = MD5(url + body + tstamp)
     ├─ cecelia = "2_" + SHA256(...)
     ├─ QDSign = RSA_sign(FockKey, url + body + tstamp + ...)
     ├─ gorgon = 设备注册令牌 (静态)
     ├─ ibex = Nib SDK 设备指纹
     └─ sora = Knobs 服务端配置
```

## 攻击面分析

### 已确认可绕过

| 机制 | 状态 | 说明 |
|------|------|------|
| 排行榜认证 | 可绕过 | API 不校验登录态 |
| gorgon | 可复用 | 静态令牌，一个值无限复用 |

### 需要逆向的

| 机制 | 难度 | 路径 |
|------|------|------|
| QDSign | 高 | Native `libfock.so` `addRetrofitH()` |
| borgus/cecelia | 中 | 同一 Native 函数内 |
| ibex | 中 | `libnib.so` 或 Frida Hook `com.yuewen.nib.search.cihai()` |
| sora | 低 | `libknobs.so` 或 Frida Hook `checkKnobsUrl()` |

### 建议攻击路径

| 优先级 | 方法 | 说明 |
|--------|------|------|
| 1️⃣ | **Frida Hook** `FockUtil.addRetrofitH()` | 直接拦截签名前/后的 headers，观察输入→输出 |
| 2️⃣ | **Frida Hook** `getH()` | 返回 Map<String,String>，直接导出签名参数 |
| 3️⃣ | IDA 静态分析 `libfock.so` | 深度逆向签名算法，但 360 加固增加难度 |
| 4️⃣ | 重放攻击 | gorgon 静态 + tstamp 可控 → 尝试修改时间窗口 |

## Frida Hook 模板

```javascript
// Hook FockUtil.addRetrofitH — 签名入口
Java.perform(function() {
    var FockUtil = Java.use("com.qidian.QDReader.component.util.FockUtil");
    FockUtil.addRetrofitH.implementation = function(request) {
        console.log("[FockUtil.addRetrofitH]");
        console.log("  URL: " + request.url().toString());
        console.log("  Method: " + request.method());
        console.log("  Headers BEFORE: " + request.headers().toString());
        
        var result = this.addRetrofitH(request);
        
        console.log("  Headers AFTER: " + result.headers().toString());
        return result;
    };
    
    // Hook FockUtil.getH — 签名参数 Map
    FockUtil.getH.implementation = function(url, str, requestBody) {
        console.log("[FockUtil.getH] url=" + url);
        var result = this.getH(url, str, requestBody);
        console.log("  Result: " + JSON.stringify(result));
        return result;
    };
    
    // Hook Nib — 设备指纹
    var NibSearch = Java.use("com.yuewen.nib.search");
    NibSearch.cihai.implementation = function(context) {
        console.log("[Nib.cihai] generating device fingerprint...");
        var result = this.cihai(context);
        console.log("  ibex = " + result.substring(0, 100) + "...");
        return result;
    };
});
```

## 关联文件

| 文件 | 位置 |
|------|------|
| 流量分析 | `analysis/report.md` |
| 结构化发现 | `analysis/findings.json` |
| 项目 triage | `triage.md` |
| SO 文件 | `native/arm64-v8a/` (libfock.so, libnib.so, libknobs.so, libfockrt.so) |
| 反编译 Java | `decompiled/java/` |
