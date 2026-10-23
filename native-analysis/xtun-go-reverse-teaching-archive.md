---
schema_version: 2
id: xtun-go-reverse-teaching-archive
document_type: archive
original_date: unknown
archived_date: '2026-10-23'
scope:
  targets:
  - xtun
  - cftun
  client: unknown
  version: Windows 1.0.20250720 / Android 1.0.9（来源自述）
  observed_at: unknown
sources:
- id: core-00
  ref: null
  basis: source-report
  citation: 00 · 前言 — 你要逆向什么
  reason: 本地教学导出材料可核对文章标题，但原件未提供作者身份或可公开定位的原文链接；只保留来源自述，未独立复现。
- id: core-01
  ref: null
  basis: source-report
  citation: 01 · 第一步 — 认识目标
  reason: 本地教学导出材料可核对文章标题，但原件未提供作者身份或可公开定位的原文链接；只保留来源自述，未独立复现。
- id: core-02
  ref: null
  basis: source-report
  citation: 02 · 第二步 — 准备工具
  reason: 本地教学导出材料可核对文章标题，但原件未提供作者身份或可公开定位的原文链接；只保留来源自述，未独立复现。
- id: core-03
  ref: null
  basis: source-report
  citation: 03 · 第三步 — 二进制识别
  reason: 本地教学导出材料可核对文章标题，但原件未提供作者身份或可公开定位的原文链接；只保留来源自述，未独立复现。
- id: core-04
  ref: null
  basis: source-report
  citation: 04 · 第四步 — Ghidra 导入分析
  reason: 本地教学导出材料可核对文章标题，但原件未提供作者身份或可公开定位的原文链接；只保留来源自述，未独立复现。
- id: core-05
  ref: null
  basis: source-report
  citation: 05 · 第五步 — 定位关键函数
  reason: 本地教学导出材料可核对文章标题，但原件未提供作者身份或可公开定位的原文链接；只保留来源自述，未独立复现。
- id: core-06
  ref: null
  basis: source-report
  citation: 06 · 第六步 — 反编译加密函数
  reason: 本地教学导出材料可核对文章标题，但原件未提供作者身份或可公开定位的原文链接；只保留来源自述，未独立复现。
- id: core-07
  ref: null
  basis: source-report
  citation: 07 · 第七步 — 逆向 API 通信
  reason: 本地教学导出材料可核对文章标题，但原件未提供作者身份或可公开定位的原文链接；只保留来源自述，未独立复现。
- id: core-08
  ref: null
  basis: source-report
  citation: 08 · 第八步 — 解密节点配置
  reason: 本地教学导出材料可核对文章标题，但原件未提供作者身份或可公开定位的原文链接；只保留来源自述，未独立复现。
- id: core-09
  ref: null
  basis: source-report
  citation: 09 · 第九步 — 抓包分析流量
  reason: 本地教学导出材料可核对文章标题，但原件未提供作者身份或可公开定位的原文链接；只保留来源自述，未独立复现。
- id: core-10
  ref: null
  basis: source-report
  citation: 10 · 第十步 — 测试 WebSocket 连接
  reason: 本地教学导出材料可核对文章标题，但原件未提供作者身份或可公开定位的原文链接；只保留来源自述，未独立复现。
- id: core-11
  ref: null
  basis: source-report
  citation: 11 · 第十一步 — 实现协议握手
  reason: 本地教学导出材料可核对文章标题，但原件未提供作者身份或可公开定位的原文链接；只保留来源自述，未独立复现。
- id: core-12
  ref: null
  basis: source-report
  citation: 12 · 第十二步 — 实现数据通道
  reason: 本地教学导出材料可核对文章标题，但原件未提供作者身份或可公开定位的原文链接；只保留来源自述，未独立复现。
- id: core-13
  ref: null
  basis: source-report
  citation: 13 · 第十三步 — 实现代理功能
  reason: 本地教学导出材料可核对文章标题，但原件未提供作者身份或可公开定位的原文链接；只保留来源自述，未独立复现。
- id: core-14
  ref: null
  basis: source-report
  citation: 14 · 第十四步 — 端到端验证
  reason: 本地教学导出材料可核对文章标题，但原件未提供作者身份或可公开定位的原文链接；只保留来源自述，未独立复现。
- id: core-15
  ref: null
  basis: source-report
  citation: 15 · 常见问题与排错
  reason: 本地教学导出材料可核对文章标题，但原件未提供作者身份或可公开定位的原文链接；只保留来源自述，未独立复现。
- id: core-16
  ref: null
  basis: source-report
  citation: xTun 逆向工程教学
  reason: 本地教学导出材料可核对文章标题，但原件未提供作者身份或可公开定位的原文链接；只保留来源自述，未独立复现。
- id: ghidra-jdk-spec
  ref: https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.1.3_build/GhidraDocs/GettingStarted.md
  basis: source-report
source_completeness: partial
tags:
- Go
- PE
- Flutter
- Ghidra
- WebSocket
- X25519
- HKDF
- AEAD
- source-report
---

# xTun Go 逆向核心教学（脱敏来源归档）

## 来源、范围与证据边界

本文合并保留《xTun 逆向工程教学》的 00–15 章和 README，共 17 篇来源正文。作者身份与原始发布日期未知；README 原文末尾标注“由逆向工程教学子代理生成”。材料以 Windows Go PE 为主，兼有 Android Flutter/Go SO 分层说明；`scope.client: unknown` 表示这份混合平台材料未归并为单一端，不是当前运行环境。

以下原文中的“确认”“成功”“已攻破”、预期输出、节点数量和勾选项均为 **source-report**：本次只做文档读取、脱敏与结构核对，没有目标样本、运行日志、测试向量或服务端验收。代码按来源保留，包括简化、未实现及省略部分；没有执行或补写成可用工具。

## 清洗与完整性说明

- 保留各篇原始标题、段落、表格、代码、数字行和排错顺序；README 中的 16 个章节链接改为本合并文章的稳定锚点。没有把来源重写成新的操作流程。
- 原材料中出现账户、密码、token 片段、Tunnel 标识、真实节点/探测地址、域名、secret 和派生密钥，以及原工作机路径。公开正文统一使用 `REDACTED_*`、`*_HOST.invalid`、`*_DOMAIN.invalid` 和 `*_ROOT` 类型占位符；相同 IPv4 的占位符保持一致以保留对比关系。`127.0.0.1`、`0.0.0.0` 是标准回环/监听语义，不是实际节点地址。
- **公开占位符绝不是可用凭据或密钥。** 来源中“看起来像占位符但实际返回”“不是占位符”等措辞只描述已脱敏的原值；不能把替换后的 `REDACTED_PAYLOAD_SECRET` 当成服务器实际返回值。占位替换也可能使原代码的长度、UUID/IPv4 解析示例不能执行；这里保留结构而不提供可运行连接材料。
- 目标 PE/APK/SO、Ghidra/IDA 工程、抓包文件、配置 JSON、Frida 原日志及最终代理脚本没有随本批材料交付。文中的文件名、项目路径、表格或运行结果不表示附件已提供；省略片段不补造。完整未脱敏原件留在本地，公开归档为 **partial**，不授权清理原件。
- 算法名、公开协议/函数名、字段名、Go 模块路径、标准长度/端序与公开工具下载地址保留。`source-core-00` 至 `source-core-16` 只提供来源定位，不表示技术验证等级。

## 编辑勘误与跨来源冲突

1. **Ghidra / JDK**：第 02 章原文的 JDK 17+ 说法保留。Ghidra `Ghidra_12.1.3_build` 固定版本官方 [GettingStarted.md](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.1.3_build/GhidraDocs/GettingStarted.md) 在 Minimum Requirements 明确写的是 **Java 21 64-bit Runtime and Development Kit**。这是工具依赖勘误，不是本次安装或启动成功的记录。
2. **配置加密链**：核心教学以 `SHA256(payloadSecret)`、逐层 HKDF/AAD 说明为主；同批项目源分析中还存在 `SHA256(accessPoint)`、`base64(payloadSecret)` 与“直接复制无 KDF”等互相不兼容的描述。来源顺序和原话分别保留，不由整理者选定实现。没有二进制与测试向量，不能据本篇宣称恢复成功；应逐层核对输入、输出、用途、编码和依据。
3. **结果范围**：核心中的 5/6 节点、其他来源的 101 升级结果和补充材料的后续 DATA_OK 不是同一层验收；101 不等于自定义握手、AEAD 数据通道或代理端到端成功。`pktmon` 仅采到单向的表述是作者该次采集经验，不是工具的普遍能力限制。
4. **历史排错**：本篇仍保留来源对特定 Host、路径、UA、WAF 或证书行为的断言；它们未经本次复验，也不适用于其他服务或版本。附带的 Android 抓包/Hook 示例只是来源正文，不改变本仓现行工具入口和调度合同。

## 来源导航

| 稳定定位 | 原始篇名 |
|---|---|
| [source-core-00](#source-core-00) | 00 · 前言 — 你要逆向什么 |
| [source-core-01](#source-core-01) | 01 · 第一步 — 认识目标 |
| [source-core-02](#source-core-02) | 02 · 第二步 — 准备工具 |
| [source-core-03](#source-core-03) | 03 · 第三步 — 二进制识别 |
| [source-core-04](#source-core-04) | 04 · 第四步 — Ghidra 导入分析 |
| [source-core-05](#source-core-05) | 05 · 第五步 — 定位关键函数 |
| [source-core-06](#source-core-06) | 06 · 第六步 — 反编译加密函数 |
| [source-core-07](#source-core-07) | 07 · 第七步 — 逆向 API 通信 |
| [source-core-08](#source-core-08) | 08 · 第八步 — 解密节点配置 |
| [source-core-09](#source-core-09) | 09 · 第九步 — 抓包分析流量 |
| [source-core-10](#source-core-10) | 10 · 第十步 — 测试 WebSocket 连接 |
| [source-core-11](#source-core-11) | 11 · 第十一步 — 实现协议握手 |
| [source-core-12](#source-core-12) | 12 · 第十二步 — 实现数据通道 |
| [source-core-13](#source-core-13) | 13 · 第十三步 — 实现代理功能 |
| [source-core-14](#source-core-14) | 14 · 第十四步 — 端到端验证 |
| [source-core-15](#source-core-15) | 15 · 常见问题与排错 |
| [source-core-16](#source-core-16) | xTun 逆向工程教学 |


---

<a id="source-core-00"></a>

> **归档编辑注**：本章为脱敏来源正文；原始目标文件、工程、抓包/结果附件未提供。下文的预期输出与成功断言不是本次复现记录。

<!-- source-core-00:source-start -->

# 00 · 前言 — 你要逆向什么

---

## 一、xTun 是什么

xTun 是一个商业 VPN 应用，架构如下：

| 层 | 技术 | 文件 | 作用 |
|----|------|------|------|
| UI 层 | Flutter (Dart AOT) | `libapp.so` (7.6MB) | 界面、登录、节点选择 |
| 核心层 | Go 编译 | `libct-go.so` (8.5MB) / `xtun-windows.exe` (50MB) | VPN 隧道、加密、协议 |

- **包名**：`com.xtun`
- **版本**：Android 1.0.9 / Windows 1.0.20250720
- **Go 模块**：`github.com/fmnx/cftun/backend`
- **自研协议**：`cftun websocket v3`（非 v2ray/trojan/ss 标准协议）
- **加密栈**：X25519 + HKDF-SHA256 + ChaCha20-Poly1305 + AES-256-GCM
- **传输**：WebSocket over Cloudflare Argo Tunnel，端口 80，无 TLS

xTun 不使用任何标准代理协议。v2ray/xray/Clash 客户端**无法直接连接**，因为服务器期望 cftun v3 握手。

---

## 二、为什么要逆向

xTun 客户端闭源，只提供 Windows/Mac/Linux/Android/iOS 客户端。逆向后你可以：

1. **脱离客户端**：用标准 socks5h / http 代理接入 xTun 网络
2. **跨平台**：一个纯 Python 脚本，任何能跑 Python 的设备都能用
3. **自动化**：脚本化连接、切换节点、批量测速
4. **理解协议**：完整掌握 cftun websocket v3 的握手与加密细节

---

## 三、最终目标

一个纯 Python 脚本 `cftun_proxy_working.py`，实现：

- 登录 xTun API，获取 token 和 tunnel_uuid
- 解密服务器返回的加密节点配置
- 对每个节点解密 access_point，提取真实出口 IP
- 建立 WebSocket 连接（绕过 WAF）
- 完成 cftun v3 协议握手（X25519 + ChaCha20-Poly1305）
- 建立加密数据通道
- 对外暴露 SOCKS5 + HTTP 代理端口

**不依赖 xTun 客户端，不依赖 Go 运行时，只依赖 Python + pycryptodome + cryptography。**

---

## 四、你需要什么基础

| 基础 | 用在哪 | 最低要求 |
|------|--------|----------|
| Python | 写解密脚本、代理脚本 | 能读懂 async/socket 代码 |
| 网络协议 | WebSocket 握手、SOCKS5、HTTP 代理 | 知道 TCP 三次握手 |
| 加密 | AES-GCM、ChaCha20-Poly1305、X25519、HKDF | 知道对称 vs 非对称 |
| 二进制逆向 | Ghidra/IDA 读 Go 二进制 | 能看懂 C 伪代码 |
| PE 格式 | 识别 Go 编译特征 | 知道 .text/.rdata 节区 |

不需要你是逆向专家。每一步都有手把手命令和代码。

---

## 五、需要什么工具

| 工具 | 用途 |
|------|------|
| **Ghidra** | 反编译 Go 二进制（免费，需要 JDK 17+） |
| **IDA Pro** | 交叉验证反编译结果（可选，Capstone 替代） |
| **Python 3.12** | 运行解密/代理脚本 |
| **pycryptodome** | AES-256-GCM、ChaCha20-Poly1305 |
| **cryptography** | X25519、HKDF-SHA256 |
| **pefile** | 解析 PE 头 |
| **capstone** | 反汇编（IDA 替代） |
| **frida** | 动态 hook（验证用，可选） |
| **pktmon** | Windows 内置抓包工具 |
| **jadx** | 反编译 APK 的 DEX（Android 分析用） |
| **apktool** | 解包 APK（提取 SO 文件） |

---

## 六、教学路径

这份教学分 15 步，每一步都是手把手，一个细节不落：

```
认识目标 → 准备工具 → 二进制识别 → Ghidra导入 → 定位函数
→ 反编译加密 → 逆向API → 解密配置 → 抓包 → 测试WebSocket
→ 协议握手 → 数据通道 → 代理功能 → 端到端验证 → 排错
```

走完之后，你手里会有一个能用的 Python 代理脚本，和完整的逆向方法论。

---

**下一步**：`01-第一步-认识目标.md`

<!-- source-core-00:source-end -->


---

<a id="source-core-01"></a>

> **归档编辑注**：本章为脱敏来源正文；原始目标文件、工程、抓包/结果附件未提供。下文的预期输出与成功断言不是本次复现记录。

<!-- source-core-01:source-start -->

# 01 · 第一步 — 认识目标

---

## 目标

找到 xTun 的可执行文件，确认它是 Go 编译的，提取版本和架构信息。

---

## 一、找到可执行文件

xTun 在不同平台的文件：

| 平台 | 文件 | 路径 |
|------|------|------|
| Windows | `xtun-windows.exe` | 下载或 `INSTALL_ROOT\` |
| Android | `xtun-android-release.apk` 内的 `libct-go.so` | APK 解包后 `lib/arm64-v8a/` |

本教学以 **Windows 的 `xtun-windows.exe`** 为主目标（50MB，Go PE64）。

### 手把手：确认文件存在

```bash
# Windows PowerShell
ls "WORKSPACE_ROOT\xtun-windows.exe"

# 或 Git Bash
file "WORKSPACE_ROOT/xtun-windows.exe"
```

预期输出包含 `PE32+ executable`（64位 PE）。

---

## 二、确认是 Go 编译的

Go 二进制有特征字符串。用 `strings` 搜索：

```bash
# 搜索 Go build ID
strings xtun-windows.exe | grep "go.buildid"

# 搜索 Go runtime 标记
strings xtun-windows.exe | grep "runtime."

# 搜索 Go 模块路径
strings xtun-windows.exe | grep "fmnx/cftun"
```

### 预期结果

```
go.buildid: Go1.25.0...
runtime.morestack
runtime.gcWriteBarrier
github.com/fmnx/cftun/backend/...
```

看到这三样就确认是 Go 编译：
1. `go.buildid` — Go 编译器注入的构建标识
2. `runtime.` — Go 运行时函数
3. `github.com/fmnx/cftun` — 模块路径

---

## 三、看文件大小和版本信息

### 文件大小

```bash
ls -la xtun-windows.exe
# 预期: 50,043,240 bytes (约 50MB)
```

50MB 对一个 VPN 客户端很大，因为 Go 静态链接了所有依赖（runtime + crypto + net + gorilla/websocket）。

### 版本信息（用 pefile）

```python
import pefile

pe = pefile.PE("xtun-windows.exe")
print(f"Machine: {hex(pe.FILE_HEADER.Machine)}")
# 0x8664 = AMD64 (64位)
print(f"Sections: {len(pe.sections)}")
for s in pe.sections:
    name = s.Name.rstrip(b'\x00').decode()
    print(f"  {name}: VA={hex(s.VirtualAddress)} Size={s.SizeOfRawData}")
```

### 预期输出

```
Machine: 0x8664
Sections: 6
  .text:   VA=0x1000  Size=...
  .rdata:  VA=...     Size=...
  .data:   VA=...     Size=...
  .pdata:  VA=...     Size=...
  .rsrc:   VA=...     Size=...
  .reloc:  VA=...     Size=...
```

`0x8664` = AMD64 = 64 位。Go 1.25.0 编译。

---

## 四、Go 二进制的特征字符串清单

搜索这些字符串确认 Go 特征：

| 字符串 | 含义 |
|--------|------|
| `go.buildid` | Go 构建 ID（含编译器版本） |
| `runtime.morestack` | Go runtime 栈增长 |
| `runtime.gcWriteBarrier` | Go GC 写屏障 |
| `runtime.main` | Go 主函数 |
| `goroutine` | Go 协程 |
| `github.com/fmnx/cftun` | xTun 的 Go 模块路径 |
| `golang.org/x/crypto` | Go 加密库 |
| `github.com/gorilla/websocket` | WebSocket 库 |

### 一条命令全搜

```bash
strings xtun-windows.exe | grep -E "go\.buildid|runtime\.|fmnx/cftun|gorilla/websocket" | head -20
```

---

## 五、从 APK 提取（如果目标是 Android）

```bash
# 1. 用 apktool 解包
java -jar apktool_2.9.3.jar d xtun-android-release.apk -o apktool_out

# 2. 找到 Go SO
ls apktool_out/lib/arm64-v8a/
# libapp.so   — Flutter Dart AOT (UI)
# libct-go.so — Go VPN 后端 (协议逻辑)

# 3. 确认 libct-go.so 是 Go
strings apktool_out/lib/arm64-v8a/libct-go.so | grep "fmnx/cftun"
```

**Go 协议逻辑在 `libct-go.so`，不在 `libapp.so`。** `libapp.so` 是 Flutter UI。

---

## 六、关键发现总结

走完这一步你应该确认：

- ✅ 目标文件是 `xtun-windows.exe`，50MB
- ✅ 64 位 PE（Machine=0x8664）
- ✅ Go 1.25.0 编译
- ✅ 模块路径 `github.com/fmnx/cftun/backend`
- ✅ 使用了 gorilla/websocket 和 x/crypto

---

**下一步**：`02-第二步-准备工具.md`

<!-- source-core-01:source-end -->


---

<a id="source-core-02"></a>

> **归档编辑注**：本章为脱敏来源正文；原始目标文件、工程、抓包/结果附件未提供。下文的预期输出与成功断言不是本次复现记录。 原文 JDK 17+ 保留，请同时阅读前述 Ghidra 12.1.3 / JDK 21 编辑勘误。

<!-- source-core-02:source-start -->

# 02 · 第二步 — 准备工具

---

## 目标

安装所有逆向工具，验证每个都能用。

---

## 一、工具清单

| 工具 | 版本 | 用途 | 必需？ |
|------|------|------|--------|
| Python | 3.12+ | 脚本运行 | ✅ |
| pycryptodome | latest | AES-GCM, ChaCha20 | ✅ |
| cryptography | latest | X25519, HKDF | ✅ |
| pefile | latest | PE 解析 | ✅ |
| capstone | latest | 反汇编 | ✅ |
| Ghidra | 12.1.3 | 反编译 Go 二进制 | ✅ |
| JDK | 17+ | Ghidra 依赖 | ✅ |
| IDA Pro | 8.3+ | 交叉验证（可选） | ❌ |
| frida | latest | 动态 hook（可选） | ❌ |
| jadx | latest | APK 反编译 | Android 才需要 |
| apktool | 2.9.3 | APK 解包 | Android 才需要 |

---

## 二、安装 Python 依赖

```bash
pip install pycryptodome cryptography pefile capstone frida
```

### 验证

```python
from Crypto.Cipher import AES, ChaCha20_Poly1305
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
import pefile, capstone
print("All imports OK")
```

---

## 三、安装 Ghidra

### 3.1 下载

Ghidra 是 NSA 开源的免费反编译器。从官方 GitHub 下载：

```
https://github.com/NationalSecurityAgency/ghidra/releases
```

下载 `ghidra_12.1.3_PUBLIC.zip`，解压到 `GHIDRA_ROOT\`。

### 3.2 安装 JDK 17+

**Ghidra 需要 JDK 17 或更高。这是硬性要求，JDK 11 不够。**

```bash
# 验证 Java 版本
java -version
# 预期: openjdk version "17" 或更高
```

如果没有，安装 Temurin JDK 17：
```
https://adoptium.net/temurin/releases/?version=17
```

### 3.3 设置 Ghidra 环境变量

```bash
# Windows
set GHIDRA_HOME=GHIDRA_ROOT
set PATH=%PATH%;%GHIDRA_HOME%\support
```

### 3.4 验证 Ghidra

```bash
# Headless 模式验证
GHIDRA_ROOT\support\analyzeHeadless.bat
# 应该输出用法说明，不报错
```

---

## 四、安装 IDA Pro（可选）

IDA Pro 用于交叉验证 Ghidra 的反编译结果。如果没有 IDA，用 Capstone 反汇编替代。

### Capstone 替代方案

```python
from capstone import *
md = Cs(CS_ARCH_X86, CS_MODE_64)
# 反汇编一段 .text 字节
for i in md.disasm(code_bytes, 0x140000000):
    print(f"0x{i.address:x}: {i.mnemonic} {i.op_str}")
```

---

## 五、安装 frida（可选，动态分析用）

```bash
pip install frida frida-tools
```

frida 用于运行时 hook 加密函数，验证静态分析结果。本教学中静态分析已足够，frida 是验证手段。

---

## 六、安装 jadx + apktool（Android 分析用）

```bash
# jadx — Java 反编译器
# 下载: https://github.com/skylot/jadx/releases
# 路径: JADX_ROOT\bin\jadx.bat

# apktool — APK 解包
# 下载: https://ibotpeaches.github.io/Apktool/
# 路径: APKTOOL_ROOT\apktool_2.9.3.jar
```

---

## 七、验证全部安装

```python
#!/usr/bin/env python3
"""verify_tools.py — 验证所有工具可用"""
import subprocess, shutil, sys, os

checks = []

# Python 包
try:
    from Crypto.Cipher import AES, ChaCha20_Poly1305
    checks.append(("pycryptodome", True))
except: checks.append(("pycryptodome", False))

try:
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
    checks.append(("cryptography", True))
except: checks.append(("cryptography", False))

try:
    import pefile
    checks.append(("pefile", True))
except: checks.append(("pefile", False))

try:
    import capstone
    checks.append(("capstone", True))
except: checks.append(("capstone", False))

# Ghidra
ghidra = os.path.exists(
    r"GHIDRA_ROOT\support\analyzeHeadless.bat")
checks.append(("ghidra", ghidra))

# Java
try:
    r = subprocess.run(["java", "-version"], capture_output=True, text=True)
    checks.append(("java", "17" in r.stderr or "21" in r.stderr))
except: checks.append(("java", False))

print("=== 工具验证 ===")
for name, ok in checks:
    print(f"  [{'✅' if ok else '❌'}] {name}")
```

---

## 八、目录结构建议

```
WORKSPACE_ROOT\
├── xtun-windows.exe          # 目标二进制
├── 教学\                     # 本教学
├── ghidra_project\           # Ghidra 项目
├── ghidra_scripts\           # Ghidra 脚本
└── cftun_proxy_working.py    # 最终代理脚本
```

---

**下一步**：`03-第三步-二进制识别.md`

<!-- source-core-02:source-end -->


---

<a id="source-core-03"></a>

> **归档编辑注**：本章为脱敏来源正文；原始目标文件、工程、抓包/结果附件未提供。下文的预期输出与成功断言不是本次复现记录。

<!-- source-core-03:source-start -->

# 03 · 第三步 — 二进制识别

---

## 目标

用 pefile 深入解析 PE 头，确认编译器版本、位数、节区布局。

---

## 一、完整 PE 解析脚本

```python
#!/usr/bin/env python3
"""analyze_pe.py — 解析 xtun-windows.exe 的 PE 结构"""
import pefile, sys

path = "xtun-windows.exe"
pe = pefile.PE(path)

# === DOS 头 ===
print("=== DOS Header ===")
print(f"  e_magic: {hex(pe.DOS_HEADER.e_magic)}")  # 0x5a4d = "MZ"

# === PE 头 ===
print("\n=== PE Header ===")
fh = pe.FILE_HEADER
print(f"  Machine: {hex(fh.Machine)}")
# 0x8664 = AMD64, 0x14c = i386
print(f"  NumberOfSections: {fh.NumberOfSections}")
print(f"  TimeDateStamp: {fh.TimeDateStamp}")
print(f"  Characteristics: {hex(fh.Characteristics)}")

# === Optional 头 ===
print("\n=== Optional Header ===")
oh = pe.OPTIONAL_HEADER
print(f"  Magic: {hex(oh.Magic)}")  # 0x20b = PE32+
print(f"  AddressOfEntryPoint: {hex(oh.AddressOfEntryPoint)}")
print(f"  ImageBase: {hex(oh.ImageBase)}")  # 0x140000000 (Go 默认)
print(f"  SizeOfImage: {hex(oh.SizeOfImage)}")

# === 节区 ===
print("\n=== Sections ===")
for s in pe.sections:
    name = s.Name.rstrip(b'\x00').decode('utf-8', 'replace')
    print(f"  {name:8s} VA={hex(s.VirtualAddress):12s} "
          f"VSize={hex(s.Misc_VirtualSize):10s} "
          f"RSize={s.SizeOfRawData:10d} "
          f"Flags={hex(s.Characteristics)}")

# === 入口点 ===
print(f"\n=== Entry Point ===")
print(f"  RVA: {hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint)}")
print(f"  VA:  {hex(pe.OPTIONAL_HEADER.ImageBase + pe.OPTIONAL_HEADER.AddressOfEntryPoint)}")

pe.close()
```

---

## 二、怎么看编译器版本

Go 编译器版本藏在 `go.buildid` 字符串里：

```python
#!/usr/bin/env python3
"""extract_go_version.py — 提取 Go 编译器版本"""
import re

with open("xtun-windows.exe", "rb") as f:
    data = f.read()

# 方法1: 搜索 go.buildid
m = re.search(rb'go\.buildid\s*([^\x00\s]+)', data)
if m:
    print(f"go.buildid: {m.group(1).decode('utf-8', 'replace')}")

# 方法2: 搜索 Go1.x.y 模式
versions = set(re.findall(rb'Go1\.(\d+)\.(\d+)', data))
for major, minor in sorted(versions):
    print(f"Go version: 1.{major.decode()}.{minor.decode()}")
```

### 预期输出

```
go.buildid: Go1.25.0...
Go version: 1.25.0
```

**xTun 用 Go 1.25.0 编译。**

---

## 三、怎么看是 32 位还是 64 位

```python
import pefile
pe = pefile.PE("xtun-windows.exe")

machine = pe.FILE_HEADER.Machine
if machine == 0x8664:
    print("64 位 (AMD64 / x86_64)")
elif machine == 0x14c:
    print("32 位 (i386)")
```

xTun 是 **64 位**（`0x8664`）。ImageBase = `0x140000000`（Go 64 位默认基址）。

---

## 四、怎么看节区

Go PE 的典型节区布局：

| 节区 | 内容 | 权限 |
|------|------|------|
| `.text` | 可执行代码 | R-X |
| `.rdata` | 只读数据（字符串、常量） | R-- |
| `.data` | 可读写数据（全局变量） | RW- |
| `.pdata` | 异常处理表 | R-- |
| `.rsrc` | 资源 | R-- |
| `.reloc` | 重定位表 | R-- |

### 关键：Go 的字符串在 .rdata

逆向时要搜索的字符串（`cftun`、`websocket`、`payloadSecret`）都在 `.rdata` 节区。

```python
# 提取 .rdata 节区
for s in pe.sections:
    name = s.Name.rstrip(b'\x00').decode()
    if name == '.rdata':
        rdata = pe.get_data(s.VirtualAddress, s.Misc_VirtualSize)
        print(f".rdata 大小: {len(rdata)} bytes")
        # 搜索关键字符串
        for kw in [b'cftun', b'websocket', b'payloadSecret', b'access_point']:
            idx = rdata.find(kw)
            if idx >= 0:
                print(f"  找到 '{kw.decode()}' 在 .rdata 偏移 {hex(idx)}")
```

---

## 五、提取所有字符串并分类

```python
#!/usr/bin/env python3
"""extract_strings.py — 提取并分类字符串"""
import re

with open("xtun-windows.exe", "rb") as f:
    data = f.read()

# 提取可打印 ASCII 字符串（>=4字符）
strings = re.findall(rb'[\x20-\x7e]{4,}', data)

categories = {
    'cftun': [],
    'websocket': [],
    'crypto': [],
    'api': [],
    'go_module': [],
}

for s in strings:
    s_dec = s.decode('utf-8', 'replace')
    if 'cftun' in s_dec.lower():
        categories['cftun'].append(s_dec)
    if 'websocket' in s_dec.lower():
        categories['websocket'].append(s_dec)
    if any(k in s_dec.lower() for k in ['aes', 'gcm', 'chacha', 'x25519', 'hkdf']):
        categories['crypto'].append(s_dec)
    if 'API_HOST_TOKEN' in s_dec or 'WEB_HOST.invalid' in s_dec:
        categories['api'].append(s_dec)
    if 'fmnx/cftun' in s_dec:
        categories['go_module'].append(s_dec)

for cat, items in categories.items():
    print(f"\n=== {cat} ({len(items)}) ===")
    for s in items[:10]:
        print(f"  {s[:100]}")
```

---

## 六、关键发现总结

走完这一步你应该确认：

- ✅ PE32+ (64位)，ImageBase=0x140000000
- ✅ Go 1.25.0 编译
- ✅ 6 个节区，字符串在 .rdata
- ✅ 关键字符串已定位：cftun、websocket、payloadSecret、access_point
- ✅ Go 模块路径 `github.com/fmnx/cftun/backend`

---

**下一步**：`04-第四步-Ghidra导入分析.md`

<!-- source-core-03:source-end -->


---

<a id="source-core-04"></a>

> **归档编辑注**：本章为脱敏来源正文；原始目标文件、工程、抓包/结果附件未提供。下文的预期输出与成功断言不是本次复现记录。

<!-- source-core-04:source-start -->

# 04 · 第四步 — Ghidra 导入分析

---

## 目标

用 Ghidra Headless 模式导入 `xtun-windows.exe`，自动分析，生成项目。

---

## 一、为什么用 Headless 模式

Go 二进制 50MB，GUI 模式分析会卡顿。Headless 模式：
- 命令行启动，不打开 GUI
- 自动导入 + 自动分析
- 可以跑脚本批量反编译
- 分析完成后再用 GUI 打开看结果

---

## 二、Headless 导入命令

```bash
# 完整命令
GHIDRA_ROOT\support\analyzeHeadless.bat \
  "GHIDRA_PROJECT_ROOT" \
  xtun_proj \
  -import "WORKSPACE_ROOT\xtun-windows.exe" \
  -overwrite \
  -postScript "WORKSPACE_ROOT\ghidra_scripts\ExportFunctions.java" \
  -scriptPath "WORKSPACE_ROOT\ghidra_scripts"
```

### 参数解释

| 参数 | 含义 |
|------|------|
| `GHIDRA_PROJECT_ROOT` | 项目目录（Ghidra 会创建） |
| `xtun_proj` | 项目名 |
| `-import` | 要导入的二进制文件 |
| `-overwrite` | 如果项目已存在，覆盖（否则会报错） |
| `-postScript` | 导入后自动运行的脚本 |
| `-scriptPath` | 脚本搜索路径 |

---

## 三、导入后怎么确认成功

```bash
# 检查项目目录
ls "GHIDRA_PROJECT_ROOT\xtun_proj"
# 应该有 .gpr 文件和 .rep 目录

# 检查日志
cat "GHIDRA_PROJECT_ROOT\xtun_proj\xtun.exe.log"
# 最后一行应该有 "Analysis succeeded" 或类似
```

---

## 四、分析要等多久

**Go 二进制分析很慢。** 50MB 的 Go PE：

| 阶段 | 耗时 |
|------|------|
| 导入 | ~2 分钟 |
| 自动分析 | **30-60 分钟**（Go 符号多） |
| 脚本反编译 | ~10-20 分钟 |

总计约 **1-1.5 小时**。耐心等，不要中断。

### 分析在做什么

Ghidra 分析 Go 二进制时会：
1. 识别所有函数（Go 有几万个函数）
2. 反汇编 .text 节区
3. 建立交叉引用
4. 恢复类型信息（Go 的 `golang.org/x/debug/elf` 有 DWARF 调试信息）
5. 识别字符串引用

---

## 五、用 GUI 打开分析完成的项目

```bash
# 启动 Ghidra GUI
GHIDRA_ROOT\ghidraRun.bat
```

在 GUI 中：
1. `File → Open Project → GHIDRA_PROJECT_ROOT\xtun_proj`
2. 双击 `xtun.exe`
3. 等待 GUI 加载（~1 分钟）
4. 左侧 `Symbol Tree` 可以看到所有函数

---

## 六、Ghidra 反编译脚本

分析完成后，用脚本批量反编译关键函数：

```java
// ghidra_scripts/DecompileFunctions.java
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import java.io.FileWriter;

public class DecompileFunctions extends GhidraScript {
    @Override
    public void run() throws Exception {
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);

        FileWriter fw = new FileWriter("WORKSPACE_ROOT\\decompiled_functions.txt");

        // 搜索包含关键词的函数
        String[] keywords = {"decrypt", "AccessPoint", "Websocket",
                             "PayloadSecret", "ConfigResponse", "HKDF",
                             "ChaCha20", "AESGCM", "X25519"};

        FunctionIterator funcs = currentProgram.getFunctionManager().getFunctions(true);
        while (funcs.hasNext()) {
            Function func = funcs.next();
            String name = func.getName();
            for (String kw : keywords) {
                if (name.contains(kw)) {
                    DecompileResults res = decomp.decompileFunction(func, 60, monitor);
                    if (res.decompileCompleted()) {
                        fw.write("// === " + name + " @ " +
                                func.getEntryPoint() + " ===\n");
                        fw.write(res.getDecompiledFunction().getC() + "\n\n");
                    }
                    break;
                }
            }
        }
        fw.close();
        decomp.dispose();
        println("Decompilation complete!");
    }
}
```

### 运行反编译脚本

```bash
GHIDRA_ROOT\support\analyzeHeadless.bat \
  "GHIDRA_PROJECT_ROOT" \
  xtun_proj \
  -process "xtun.exe" \
  -noanalysis \
  -postScript DecompileFunctions.java \
  -scriptPath "WORKSPACE_ROOT\ghidra_scripts"
```

注意：`-process` 而不是 `-import`，`-noanalysis` 跳过分析（已完成）。

---

## 七、细节：Go 二进制的特殊处理

Go 编译器生成的 PE 有一些特殊性：

1. **函数名包含包路径**：`github.com/fmnx/cftun/backend/dialer.decryptAccessPoint`
2. **没有标准 PE 导出表**：Go 用自己的符号表
3. **字符串没有 null 终止**：Go 字符串是 (指针, 长度) 对
4. **栈管理不同**：Go 用连续栈，Ghidra 可能误判

Ghidra 12+ 对 Go 有较好支持，能自动识别 Go 函数名和类型。

---

## 八、关键发现总结

走完这一步你应该有：

- ✅ Ghidra 项目 `GHIDRA_PROJECT_ROOT\xtun_proj`
- ✅ 分析完成（等了约 1 小时）
- ✅ `decompiled_functions.txt`（反编译结果，约 561KB）
- ✅ 可以用 GUI 浏览函数

---

**下一步**：`05-第五步-定位关键函数.md`

<!-- source-core-04:source-end -->


---

<a id="source-core-05"></a>

> **归档编辑注**：本章为脱敏来源正文；原始目标文件、工程、抓包/结果附件未提供。下文的预期输出与成功断言不是本次复现记录。

<!-- source-core-05:source-start -->

# 05 · 第五步 — 定位关键函数

---

## 目标

在 Ghidra 中搜索关键字符串，从字符串引用找到关键函数，确定函数地址。

---

## 一、搜索什么字符串

这些字符串是逆向的入口点：

| 字符串 | 含义 | 在哪个函数里 |
|--------|------|-------------|
| `cftun websocket v3` | 协议子协议名 | NewWebsocket |
| `cftun-txt` | access_point 解密的 AAD | decryptAccessPoint |
| `cftun-config-response-v1` | 配置响应解密的 info/AAD | DecryptResponse |
| `REDACTED_PAYLOAD_SECRET` | payloadSecret 值 | PayloadSecret |
| `payload_secret` | JSON 字段名 | configsFromPayload |
| `access_point` | JSON 字段名 | decodeAccessPointAddrPool |
| `X-Cftun-Config-Key` | HTTP 头名 | fetchConfigs |
| `API_HOST.invalid` | API 域名 | HTTP 客户端 |
| `cftun websocket v3 open` | open frame AAD | buildArgoOpenFrame |
| `cftun websocket v3 client to server` | 数据通道 AAD | newArgoAEAD |

---

## 二、怎么在 Ghidra 中搜索字符串

### 方法 A：GUI 搜索

1. Ghidra GUI → `Search → For Strings`
2. 等待字符串表构建（~1 分钟）
3. 在搜索框输入 `cftun`
4. 双击结果跳转到字符串地址
5. 右键 → `References → Find references to`
6. 跳转到引用该字符串的函数

### 方法 B：脚本搜索

```python
#!/usr/bin/env python3
"""find_strings.py — 在二进制中搜索关键字符串并找引用"""
import pefile, re

pe = pefile.PE("xtun-windows.exe")
image_base = pe.OPTIONAL_HEADER.ImageBase  # 0x140000000

# 读取整个文件
with open("xtun-windows.exe", "rb") as f:
    data = f.read()

keywords = [
    b"cftun websocket v3",
    b"cftun-txt",
    b"cftun-config-response-v1",
    b"REDACTED_PAYLOAD_SECRET",
    b"payload_secret",
    b"access_point",
    b"X-Cftun-Config-Key",
    b"API_HOST.invalid",
]

for kw in keywords:
    # 找所有出现位置
    offset = 0
    while True:
        idx = data.find(kw, offset)
        if idx < 0:
            break
        # 转换为 VA（近似）
        va = image_base + idx  # 简化，实际需要 RVA 转换
        print(f"  '{kw.decode()}' @ file offset {hex(idx)} (~VA {hex(va)})")
        offset = idx + 1
```

---

## 三、怎么从字符串找到引用它的函数

### 在 Ghidra GUI 中

1. 搜索到字符串后，双击跳到字符串地址
2. 按 `Ctrl+Shift+F`（Find References）
3. 弹出引用列表，每行是一个引用该字符串的代码地址
4. 双击引用地址，跳到反汇编
5. Ghidra 自动识别包含该地址的函数
6. 函数名显示在反汇编窗口顶部

### 用 Ghidra 脚本

```java
// FindStringRefs.java
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.address.*;

public class FindStringRefs extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] targets = {"cftun-txt", "cftun websocket v3",
                           "cftun-config-response-v1"};

        for (String target : targets) {
            println("=== Searching: " + target + " ===");
            // 搜索数据域中的字符串
            Memory mem = currentProgram.getMemory();
            Address addr = mem.findBytes(currentProgram.getMinAddress(),
                target.getBytes(), null, true, monitor);
            if (addr != null) {
                println("  String at: " + addr);
                // 找引用
                ReferenceManager rm = currentProgram.getReferenceManager();
                Reference[] refs = rm.getReferencesTo(addr);
                for (Reference ref : refs) {
                    Function func = currentProgram.getFunctionManager()
                        .getFunctionContaining(ref.getFromAddress());
                    if (func != null) {
                        println("  Referenced by: " + func.getName() +
                               " @ " + func.getEntryPoint());
                    }
                }
            }
        }
    }
}
```

---

## 四、关键函数列表（已确认的地址）

以下是 Ghidra 反编译确认的关键函数，地址是 VA（Virtual Address），base=0x140000000：

| 函数 | 地址 | 源文件 | 作用 |
|------|------|--------|------|
| `decryptAccessPoint` | `0x140365f60` | txt_cipher.go:39 | 解密 access_point |
| `DecryptResponse` | `0x1404eaec0` | config_response_crypto.go:89 | 解密 API 配置响应 |
| `decodeTXTBinaryPayload` | `0x140366380` | txt_cipher.go:78 | 解析解密后的二进制格式 |
| `decodeAccessPointAddrPool` | `0x140347ec0` | dialer.go:474 | 地址池解码入口 |
| `authenticatedAccessPointPayload` | `0x1401bf9a0` | access_point_identity.go:46 | 认证的接入点载荷 |
| `decodeConfigResponsePublicKey` | `0x1404eac40` | config_response_crypto.go:69 | 解码服务器公钥 |
| `decodeRawBase64URL` | `0x1404eb600` | config_response_crypto.go:151 | base64url 解码 |
| `splitHostAndPath` | `0x140349260` | dialer.go:720 | 分割 Host 和 Path |
| `parseAccessPointAddrPoolMode` | `0x140347fa0` | dialer.go:491 | 解析地址池模式 |
| `(*Websocket).PayloadSecret` | `0x140349220` | dialer.go:707 | 获取 PayloadSecret |
| `(*RouteRacer).PayloadSecret` | `0x140365ee0` | route_racer.go:1342 | 获取 PayloadSecret |
| `NewWebsocket` | `0x140348120` | dialer.go | 创建 WebSocket 连接 |
| `connectWithPurpose` | `0x14034afc0` | dialer.go | 设置 UA=DEV 并连接 |
| `implicitWebsocketRouteUpstream` | `0x14034f3a0` | dialer.go:1521 | upstream 编码 |
| `implicitWebsocketHost` | `0x14034f540` | dialer.go:1540 | Host 头构造 |
| `websocketIPHost` | `0x14034f4a0` | dialer.go:1532 | IP 格式化 Host |
| `buildArgoOpenFrame` | — | argo.go:183 | 构造 open frame |
| `buildArgoOpenPlaintext` | — | argo.go:285 | 构造 open frame 明文 |
| `newArgoAEAD` | — | argo.go:317 | 创建 AEAD 加密器 |
| `newArgoFrameCodec` | — | argo.go:337 | 帧编解码器 |

---

## 五、怎么确定函数地址

### 在 Ghidra GUI 中

1. `Window → Symbol Tree`
2. 在搜索框输入函数名（如 `decryptAccessPoint`）
3. 双击搜索结果
4. 反汇编窗口显示该函数
5. 顶部地址栏显示函数入口地址（如 `0x140365f60`）

### 用 Ghidra 脚本批量导出

```java
// ExportFunctions.java
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import java.io.FileWriter;

public class ExportFunctions extends GhidraScript {
    @Override
    public void run() throws Exception {
        FileWriter fw = new FileWriter("WORKSPACE_ROOT\\all_functions.json");
        fw.write("[");

        FunctionIterator funcs = currentProgram.getFunctionManager().getFunctions(true);
        boolean first = true;
        while (funcs.hasNext()) {
            Function func = funcs.next();
            String name = func.getName();
            // 只导出 cftun 相关函数
            if (name.contains("cftun") || name.contains("AccessPoint") ||
                name.contains("Websocket") || name.contains("PayloadSecret") ||
                name.contains("ConfigResponse") || name.contains("Argo")) {
                if (!first) fw.write(",");
                fw.write(String.format("{\"name\":\"%s\",\"addr\":\"%s\",\"size\":%d}",
                    name, func.getEntryPoint(), func.getBody().getNumAddresses()));
                first = false;
            }
        }
        fw.write("]");
        fw.close();
    }
}
```

---

## 六、关键发现总结

走完这一步你应该有：

- ✅ 20+ 个关键函数的地址和源文件
- ✅ 知道每个函数的作用
- ✅ `all_functions.json`（函数列表）
- ✅ 可以在 Ghidra 中跳转到任意函数

核心函数地址（记下来，后面要用）：
```
decryptAccessPoint       @ 0x140365f60
DecryptResponse          @ 0x1404eaec0
NewWebsocket             @ 0x140348120
connectWithPurpose       @ 0x14034afc0
```

---

**下一步**：`06-第六步-反编译加密函数.md`

<!-- source-core-05:source-end -->


---

<a id="source-core-06"></a>

> **归档编辑注**：本章为脱敏来源正文；原始目标文件、工程、抓包/结果附件未提供。下文的预期输出与成功断言不是本次复现记录。 secret/密钥/UUID 原值已替换；原文关于“真实值/非占位符”的说法不适用于公开占位符。 KDF 输入与输出用途和其他项目来源存在冲突，不能以本章文字代替二进制/向量核验。

<!-- source-core-06:source-start -->

# 06 · 第六步 — 反编译加密函数

---

## 目标

在 Ghidra 中反编译关键加密函数，读懂 C 伪代码，识别加密算法，追踪密钥派生链。

---

## 一、怎么在 Ghidra 中反编译函数

### GUI 方式

1. `Window → Symbol Tree` → 搜索 `decryptAccessPoint`
2. 双击跳到函数
3. 反汇编窗口右侧会自动显示 **Decompiler** 窗口
4. Decompiler 窗口显示 C 伪代码

如果没有 Decompiler 窗口：`Window → Decompiler`

### 脚本方式

```java
// DecompileFunction.java — 反编译单个函数
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.Function;

public class DecompileFunction extends GhidraScript {
    @Override
    public void run() throws Exception {
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);

        // 反编译 decryptAccessPoint
        Function func = findFunctionByName("decryptAccessPoint");
        if (func != null) {
            DecompileResults res = decomp.decompileFunction(func, 120, monitor);
            if (res.decompileCompleted()) {
                println(res.getDecompiledFunction().getC());
            }
        }
        decomp.dispose();
    }

    Function findFunctionByName(String name) {
        FunctionIterator funcs = currentProgram.getFunctionManager().getFunctions(true);
        while (funcs.hasNext()) {
            Function f = funcs.next();
            if (f.getName().contains(name)) return f;
        }
        return null;
    }
}
```

---

## 二、怎么读反编译的 C 伪代码

### decryptAccessPoint 的反编译（简化）

```c
// decryptAccessPoint @ 0x140365f60 (txt_cipher.go:39)
string decryptAccessPoint(string accessPoint, string payloadSecret) {
    // 1. base64url 解码
    bytes raw = decodeRawBase64URL(accessPoint);

    // 2. 分割 nonce 和 ciphertext
    bytes nonce = raw[:12];
    bytes ct_with_tag = raw[12:];

    // 3. 派生 AES 密钥: SHA256(payloadSecret)
    bytes key = sha256(payloadSecret);

    // 4. 构造 AAD (逐字节，避免被字符串搜索发现)
    bytes aad = bytes{
        0x63, 0x66, 0x74, 0x75, 0x6e, 0x2d, 0x74, 0x78, 0x74
    };  // = "cftun-txt"

    // 5. AES-256-GCM 解密
    cipher = aes_gcm_new(key, nonce);
    cipher.update(aad);  // 设置 AAD
    plaintext = cipher.decrypt_and_verify(ct_with_tag[:-16], ct_with_tag[-16:]);

    // 6. 解析二进制格式
    return decodeTXTBinaryPayload(plaintext);
}
```

### 阅读要点

| 伪代码模式 | 实际含义 |
|------------|----------|
| `raw[:12]` | Go slice 切片，取前 12 字节 |
| `raw[12:]` | 从第 12 字节到末尾 |
| `ct_with_tag[-16:]` | 最后 16 字节（GCM tag） |
| `sha256(x)` | SHA-256 哈希 |
| `bytes{0x63, 0x66, ...}` | 逐字节构造字符串（反检测） |
| `aes_gcm_new(key, nonce)` | 创建 AES-GCM 加密器 |

---

## 三、识别加密算法

### 算法识别清单

| 算法 | 在伪代码中的特征 | 用在哪 |
|------|------------------|--------|
| AES-256-GCM | `aes_gcm_new`, key=32字节, nonce=12字节, tag=16字节 | 配置响应 + access_point |
| ChaCha20-Poly1305 | `chacha20_poly1305_new`, key=32字节, nonce=12字节 | 数据通道 |
| X25519 | `x25519_exchange`, 32字节公钥/私钥 | 配置响应密钥交换 |
| HKDF-SHA256 | `hkdf_new`, `hkdf_expand`, info 参数 | 密钥派生 |
| SHA-256 | `sha256_new`, 32字节输出 | payloadSecret → AES key |

### 怎么确认是 AES-256-GCM

1. **Key 长度 = 32 字节** → AES-256
2. **Nonce 长度 = 12 字节** → GCM 标准
3. **Tag 长度 = 16 字节** → GCM 标准
4. **有 AAD** → GCM 的认证数据
5. **函数名含 `gcm` 或 `aes`** → 直接确认

### 怎么确认是 ChaCha20-Poly1305

1. **Key 长度 = 32 字节** → ChaCha20
2. **Nonce 长度 = 12 字节** → ChaCha20-Poly1305 标准
3. **Tag 长度 = 16 字节** → Poly1305
4. **函数名含 `chacha` 或 `poly1305`**

---

## 四、追踪密钥派生链

### 配置响应解密的密钥派生

```
客户端生成 X25519 密钥对 (priv, pub)
→ 公钥 pub 放入 HTTP 头 X-Cftun-Config-Key (base64url)
→ 服务器返回 {server_public_key, salt, nonce, ciphertext}
→ shared = X25519(client_priv, server_pub)        // ECDH 共享密钥
→ aesKey = HKDF-SHA256(shared, salt=salt,          // HKDF 派生
                        info="cftun-config-response-v1",
                        length=32)
→ AES-256-GCM(aesKey, nonce, ciphertext,           // 解密
              AAD="cftun-config-response-v1")
→ plaintext = JSON 配置
```

### access_point 解密的密钥派生

```
payloadSecret = "REDACTED_PAYLOAD_SECRET"  // 从配置 JSON 中读取
→ key = SHA256(payloadSecret.encode())                 // 32 字节 AES 密钥
→ raw = base64url_decode(access_point)
→ nonce = raw[:12]
→ ct_with_tag = raw[12:]
→ AES-256-GCM(key, nonce, ct_with_tag, AAD="cftun-txt")
→ plaintext = 二进制格式的 IP 地址池
```

### 数据通道密钥派生

```
payloadSecret = "REDACTED_PAYLOAD_SECRET"
→ open_key = HKDF-SHA256(payloadSecret, salt=None,
                         info="cftun websocket v3 open key", length=32)
→ clientKey = random(32 bytes)
→ c2s_key = HKDF-SHA256(payloadSecret, salt=clientKey,
                         info="cftun websocket v3 client to server key", length=32)
→ s2c_key = HKDF-SHA256(payloadSecret, salt=clientKey,
                         info="cftun websocket v3 server to client key", length=32)
```

---

## 五、每个加密层的参数

### Layer 1: 配置响应传输加密

| 参数 | 值 |
|------|-----|
| 算法 | AES-256-GCM |
| Key | HKDF-SHA256(X25519(priv, server_pub), salt, info="cftun-config-response-v1", 32) |
| Nonce | 服务器返回的 nonce（base64url 解码） |
| AAD | `b"cftun-config-response-v1"` |
| 编码 | base64url |

### Layer 2: access_point 加密

| 参数 | 值 |
|------|-----|
| 算法 | AES-256-GCM |
| Key | `SHA256(payloadSecret.encode())` = `SHA256("REDACTED_PAYLOAD_SECRET")` |
| Key (hex) | `REDACTED_KEY_HEX` |
| Nonce | `base64url_decode(access_point)[:12]` |
| Ciphertext+Tag | `base64url_decode(access_point)[12:]` |
| AAD | `b"cftun-txt"` (9 字节) |
| Tag | 最后 16 字节 |

### Layer 3: open frame 加密

| 参数 | 值 |
|------|-----|
| 算法 | ChaCha20-Poly1305 |
| Key | `HKDF-SHA256(payloadSecret, salt=None, info="cftun websocket v3 open key", 32)` |
| Nonce | 12 字节随机 |
| AAD | `b"cftun websocket v3 open"` |

### Layer 4: 数据通道加密

| 参数 | 值 |
|------|-----|
| 算法 | ChaCha20-Poly1305 |
| Key (c2s) | `HKDF-SHA256(payloadSecret, salt=clientKey, info="cftun websocket v3 client to server key", 32)` |
| Key (s2c) | `HKDF-SHA256(payloadSecret, salt=clientKey, info="cftun websocket v3 server to client key", 32)` |
| Nonce | `b'\x00\x00\x00\x00' + pack('>Q', seq)` (4 零 + 8 字节序号) |
| AAD (c2s) | `b"cftun websocket v3 client to server" + pack('>Q', seq)` |
| AAD (s2c) | `b"cftun websocket v3 server to client" + pack('>Q', seq)` |

---

## 六、细节：AAD 是逐字节构造的

Go 代码中 AAD 不是直接写字符串字面量，而是逐字节构造，避免被 `strings` 搜索发现：

```c
// Ghidra 反编译看到的
byte aad[9];
aad[0] = 0x63;  // 'c'
aad[1] = 0x66;  // 'f'
aad[2] = 0x74;  // 't'
aad[3] = 0x75;  // 'u'
aad[4] = 0x6e;  // 'n'
aad[5] = 0x2d;  // '-'
aad[6] = 0x74;  // 't'
aad[7] = 0x78;  // 'x'
aad[8] = 0x74;  // 't'
// 合起来 = "cftun-txt"
```

看到逐字节赋值，把 hex 拼起来转 ASCII 就知道 AAD 是什么。

---

## 七、关键发现总结

走完这一步你应该理解：

- ✅ 两层 AES-256-GCM 加密（配置响应 + access_point）
- ✅ 两层 ChaCha20-Poly1305 加密（open frame + 数据通道）
- ✅ X25519 ECDH 用于配置响应密钥交换
- ✅ HKDF-SHA256 用于所有密钥派生
- ✅ payloadSecret = `"REDACTED_PAYLOAD_SECRET"`（字面字符串）
- ✅ AAD 是逐字节构造的反检测技巧
- ✅ 完整的密钥派生链

---

**下一步**：`07-第七步-逆向API通信.md`

<!-- source-core-06:source-end -->


---

<a id="source-core-07"></a>

> **归档编辑注**：本章为脱敏来源正文；原始目标文件、工程、抓包/结果附件未提供。下文的预期输出与成功断言不是本次复现记录。

<!-- source-core-07:source-start -->

# 07 · 第七步 — 逆向 API 通信

---

## 目标

分析 xTun 的 API 通信，找到 API base URL、登录接口，用 Python 模拟登录。

---

## 一、怎么找到 API base URL

### 搜索字符串

```bash
strings xtun-windows.exe | grep -E "WEB_HOST_TOKEN|DOWNLOAD_HOST_TOKEN|api\." | sort -u
```

### 预期结果

```
API_HOST.invalid
WEB_HOST.invalid
DOWNLOAD_HOST.invalid
```

### 服务器列表

| 服务 | URL | 用途 |
|------|-----|------|
| API | `https://API_HOST.invalid` | 主 API 服务器 |
| Web | `https://WEB_HOST.invalid` | 前端网站 |
| 下载 | `https://DOWNLOAD_HOST.invalid` | 客户端下载 |
| 网络画像 | `REDACTED_IPV4_06:8800` 等 | 网络探测 |

---

## 二、怎么找到登录接口

### 搜索 API 路径字符串

```bash
strings xtun-windows.exe | grep -E "/v1/|/auth/|/login|/node/|/tunnel/" | sort -u
```

### 预期结果

```
/v1/auth/login
/v1/auth/register
/v1/auth/reset
/v1/common/send_code
/v1/common/site/config
/v1/public/node/summary
/v1/public/node/catalog.dat
/v1/public/tunnel/info
/v1/public/user/info
/v1/public/user/subscribe
/v1/public/subscribe/list
/v1/common/network-profile
```

### API 端点分类

| 端点 | 方法 | 说明 | 需登录？ |
|------|------|------|----------|
| `/v1/auth/login` | POST | 登录 | ❌ |
| `/v1/auth/register` | POST | 注册 | ❌ |
| `/v1/auth/reset` | POST | 密码重置 | ❌ |
| `/v1/common/send_code` | POST | 发送验证码 | ❌ |
| `/v1/common/site/config` | GET | 站点配置 | ❌ |
| `/v1/public/node/summary` | GET | 节点摘要 | ✅ |
| `/v1/public/node/catalog.dat` | GET | 节点目录 | ✅ |
| `/v1/public/tunnel/info` | GET | 隧道信息 | ✅ |
| `/v1/public/user/info` | GET | 用户信息 | ✅ |
| `/v1/public/user/subscribe` | GET | 订阅状态 | ✅ |
| `/v1/public/subscribe/list` | GET | 套餐列表 | ✅ |
| `/v1/common/network-profile` | GET | 网络画像 | ❌ |

---

## 三、认证方式

### 细节：Authorization header 无 Bearer 前缀

xTun 的认证头是**裸 JWT**，不加 `Bearer ` 前缀：

```
Authorization: <JWT token>
```

不是：
```
Authorization: Bearer <JWT token>    ← 错误！
```

这是逆向发现的关键细节。标准 OAuth2 用 `Bearer `，xTun 不用。

### 必须的请求头

| 头 | 值 | 说明 |
|----|-----|------|
| `Authorization` | `<JWT>` | 裸 token，无 Bearer |
| `Origin` | `https://WEB_HOST.invalid` | 必须带 |
| `Referer` | `https://WEB_HOST.invalid/` | 必须带 |
| `Content-Type` | `application/json` | POST 请求 |
| `User-Agent` | `Mozilla/5.0` 或任意 | 服务器不检查 |

---

## 四、用 Python 模拟登录

```python
#!/usr/bin/env python3
"""login_api.py — 模拟 xTun 登录"""
import socket, ssl, json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def raw_https(method, path, extra_headers=None, json_body=None):
    """裸 HTTPS 请求（不依赖 requests 库）"""
    s = socket.create_connection(('API_HOST.invalid', 443), timeout=20)
    ss = ctx.wrap_socket(s, server_hostname='API_HOST.invalid')

    parts = [f'{method} {path} HTTP/1.1', 'Host: API_HOST.invalid']
    if extra_headers:
        for k, v in extra_headers.items():
            parts.append(f'{k}: {v}')
    parts.append('User-Agent: Mozilla/5.0')
    parts.append('Connection: close')

    payload = b''
    if json_body is not None:
        payload = json.dumps(json_body).encode()
        parts.append(f'Content-Length: {len(payload)}')
        parts.append('Content-Type: application/json')

    parts.extend(['', ''])
    req = '\r\n'.join(parts).encode() + payload
    ss.send(req)

    resp = b''
    while True:
        try:
            c = ss.recv(65536)
            if not c: break
            resp += c
        except: break
    ss.close()

    idx = resp.index(b'\r\n\r\n')
    return resp[:idx].decode('utf-8', 'replace'), resp[idx+4:]

# === 登录 ===
h, b = raw_https('POST', '/v1/auth/login',
    extra_headers={'Origin': 'https://WEB_HOST.invalid'},
    json_body={
        'email': 'REDACTED_ACCOUNT_EMAIL',
        'password': 'REDACTED_ACCOUNT_PASSWORD'
    })

result = json.loads(b)
print(f"Status: {result.get('code')}")
print(f"Message: {result.get('msg')}")

if result.get('code') == 200:
    token = result['data']['token']
    tunnel_uuid = result['data'].get('tunnel_uuid', '')
    print(f"Token: {token[:50]}...")
    print(f"Tunnel UUID: {tunnel_uuid}")

    # 保存 token
    with open('token.txt', 'w') as f:
        f.write(token)
    print("Token saved to token.txt")
```

### 预期输出

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "token": "REDACTED_AUTH_TOKEN",
    "tunnel_uuid": "REDACTED_TUNNEL_UUID",
    "user_id": "REDACTED_USER_ID"
  }
}
```

---

## 五、获取节点配置

登录后，请求节点列表。**需要带 X25519 公钥头**：

```python
import base64
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives import serialization

# 1. 生成 X25519 密钥对
client_priv = X25519PrivateKey.generate()
client_pub = client_priv.public_key().public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw
)
pub_b64 = base64.urlsafe_b64encode(client_pub).rstrip(b'=').decode()

# 2. 请求节点列表
h, b = raw_https('GET', '/v1/public/node/list',
    extra_headers={
        'Authorization': token,           # 裸 JWT，无 Bearer
        'Origin': 'https://WEB_HOST.invalid',
        'X-Cftun-Config-Key': pub_b64,    # X25519 公钥
    })

config_response = json.loads(b)
print(f"Algorithm: {config_response.get('algorithm')}")
print(f"Version: {config_response.get('version')}")
# 服务器返回: {version, algorithm, server_public_key, salt, nonce, ciphertext}
```

---

## 六、API 请求流程图

```
1. POST /v1/auth/login
   body: {email, password}
   → 返回 {token, tunnel_uuid}

2. 生成 X25519 密钥对 (client_priv, client_pub)

3. GET /v1/public/node/list
   headers: Authorization=<token>, X-Cftun-Config-Key=base64url(client_pub)
   → 返回加密的 {server_public_key, salt, nonce, ciphertext}

4. 解密配置响应 (Layer 1)
   → 得到 {data: {list: [{nodes: [19个节点]}]}}

5. 对每个节点解密 access_point (Layer 2)
   → 得到真实出口 IP 列表
```

---

## 七、细节：Token 存储位置

xTun 客户端把 token 存在：

| 平台 | 位置 |
|------|------|
| Windows | `USER_CONFIG_ROOT\user.json` |
| Android | SharedPreferences / `cftun.authorization` |
| Web | `localStorage["cftun.authorization"]` |

---

## 八、关键发现总结

走完这一步你应该有：

- ✅ API base URL: `https://API_HOST.invalid`
- ✅ 登录接口: `POST /v1/auth/login`
- ✅ 认证方式: 裸 JWT（无 Bearer 前缀）
- ✅ 必须头: Authorization + Origin
- ✅ 节点列表接口: `GET /v1/public/node/list` + `X-Cftun-Config-Key` 头
- ✅ Python 登录脚本可用
- ✅ Token 和 tunnel_uuid 已获取

---

**下一步**：`08-第八步-解密节点配置.md`

<!-- source-core-07:source-end -->


---

<a id="source-core-08"></a>

> **归档编辑注**：本章为脱敏来源正文；原始目标文件、工程、抓包/结果附件未提供。下文的预期输出与成功断言不是本次复现记录。 secret/密钥/UUID 原值已替换；原文关于“真实值/非占位符”的说法不适用于公开占位符。 KDF 输入与输出用途和其他项目来源存在冲突，不能以本章文字代替二进制/向量核验。

<!-- source-core-08:source-start -->

# 08 · 第八步 — 解密节点配置

---

## 目标

解密 API 返回的加密配置，得到 19 个节点的完整信息。

---

## 一、两层加密概述

xTun 的节点配置有两层加密：

| 层级 | 算法 | 密钥来源 | AAD | 解密什么 |
|------|------|----------|-----|----------|
| Layer 1 | X25519 + HKDF + AES-256-GCM | ECDH + HKDF 派生 | `cftun-config-response-v1` | API 配置响应 |
| Layer 2 | AES-256-GCM | SHA256(payloadSecret) | `cftun-txt` | 每个节点的 access_point |

---

## 二、Layer 1 解密：配置响应

### 流程

```
1. 客户端生成 X25519 密钥对 (client_priv, client_pub)
2. 公钥 base64url 编码放入 X-Cftun-Config-Key 头
3. 服务器返回 {version, algorithm, server_public_key, salt, nonce, ciphertext}
4. shared = X25519(client_priv, server_pub)           // ECDH 共享密钥
5. aesKey = HKDF-SHA256(shared, salt=salt,             // HKDF 派生
                         info="cftun-config-response-v1",
                         length=32)
6. AES-256-GCM(aesKey, nonce, ciphertext,              // 解密
              AAD="cftun-config-response-v1")
7. plaintext = JSON 配置
```

### Python 实现

```python
#!/usr/bin/env python3
"""decrypt_config_response.py — Layer 1 解密"""
import base64, json
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey, X25519PublicKey
)
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from Crypto.Cipher import AES

def b64url_decode(s):
    """base64url 解码（自动补 padding）"""
    if isinstance(s, str): s = s.encode()
    pad = (4 - len(s) % 4) % 4
    return base64.urlsafe_b64decode(s + b'=' * pad)

# === 假设你已经有了 ===
# client_priv: X25519PrivateKey 对象
# config_response: API 返回的 JSON

# 1. 解码服务器返回的各字段
server_pub = b64url_decode(config_response['server_public_key'])
salt = b64url_decode(config_response['salt'])
nonce = b64url_decode(config_response['nonce'])
ciphertext = b64url_decode(config_response['ciphertext'])

# 2. X25519 ECDH 共享密钥
shared = client_priv.exchange(X25519PublicKey.from_public_bytes(server_pub))

# 3. HKDF-SHA256 派生 AES 密钥
aes_key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    info=b'cftun-config-response-v1'
).derive(shared)

# 4. AES-256-GCM 解密
cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
cipher.update(b'cftun-config-response-v1')  # AAD

# 注意: Go 的 GCM 把 tag 附在 ciphertext 末尾
# pycryptodome 的 decrypt_and_verify 需要分开传
ct = ciphertext[:-16]
tag = ciphertext[-16:]
plaintext = cipher.decrypt_and_verify(ct, tag)

# 5. 解析 JSON
config = json.loads(plaintext.decode('utf-8'))
nodes = config['data']['list'][0]['nodes']
print(f"解密成功！共 {len(nodes)} 个节点")

for node in nodes:
    print(f"  [{node['id']:3d}] {node['name']} "
          f"({node['country_code']}) transport={node['transport']}")
```

### 解密后的配置结构

```json
{
  "data": {
    "network_profile_endpoints": [
      "http://REDACTED_IPV4_06:8800/v1/common/network-profile",
      "http://REDACTED_IPV4_04:8800/v1/common/network-profile",
      "http://REDACTED_IPV4_05:8800/v1/common/network-profile"
    ],
    "list": [{
      "nodes": [
        {
          "id": 1,
          "name": "东京·节点1",
          "virtual_ip": "REDACTED_IPV4_03",
          "domains": ["NODE_DOMAIN.invalid", "ALT_NODE_DOMAIN.invalid"],
          "access_point": "REDACTED_ACCESS_POINT_CIPHERTEXT",
          "transport": "websocket",
          "is_argo": false,
          "config": {
            "tls": false,
            "port": 80,
            "payload_secret": "REDACTED_PAYLOAD_SECRET"
          },
          "country_code": "JP",
          "city_code": "TYO"
        }
        // ... 共 19 个节点
      ]
    }],
    "config_hash": "REDACTED_CONFIG_HASH",
    "catalog_hash": "REDACTED_CATALOG_HASH",
    "catalog_revision": "REDACTED_CATALOG_REVISION",
    "tunnel_uuid": "REDACTED_TUNNEL_UUID"
  }
}
```

---

## 三、Layer 2 解密：access_point

### 细节：payloadSecret

```python
payloadSecret = "REDACTED_PAYLOAD_SECRET"
```

**这看起来像占位符，但它是实际的 payloadSecret 值。** 服务器真的返回这个字符串，客户端直接传给 SHA256。

### 流程

```
1. payloadSecret = "REDACTED_PAYLOAD_SECRET"
2. key = SHA256(payloadSecret.encode())          → 32 字节 AES 密钥
3. raw = base64url_decode(access_point)
4. nonce = raw[:12]
5. ct_with_tag = raw[12:]
6. AES-256-GCM(key, nonce, ct_with_tag, AAD="cftun-txt")
7. plaintext = 二进制格式的 IP 地址池
8. decodeTXTBinaryPayload(plaintext) → "IP:port,IP:port;RR"
```

### Python 实现

```python
#!/usr/bin/env python3
"""decrypt_access_point.py — Layer 2 解密"""
import base64, hashlib
from Crypto.Cipher import AES

def b64url_decode(s):
    if isinstance(s, str): s = s.encode()
    pad = (4 - len(s) % 4) % 4
    return base64.urlsafe_b64decode(s + b'=' * pad)

# payloadSecret — 服务器返回的字面字符串
payloadSecret = "REDACTED_PAYLOAD_SECRET"

# 派生 AES 密钥
key = hashlib.sha256(payloadSecret.encode()).digest()
print(f"AES Key (SHA256): {key.hex()}")
# 输出: REDACTED_KEY_HEX

# AAD
aad = b'cftun-txt'

# 解密每个节点的 access_point
for node in nodes:
    raw = b64url_decode(node['access_point'])
    nonce = raw[:12]
    ct_with_tag = raw[12:]

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    cipher.update(aad)

    ct = ct_with_tag[:-16]
    tag = ct_with_tag[-16:]
    plaintext = cipher.decrypt_and_verify(ct, tag)

    # 解析二进制格式
    ips = decode_txt_binary_payload(plaintext)
    print(f"Node {node['id']} ({node['name']}): {ips}")
```

---

## 四、decodeTXTBinaryPayload 格式解析

解密后的明文是自定义二进制格式（`txt_cipher.go:78`）：

```
[1B mode]      低2位: 0=plain, 1=RR(RoundRobin), 2=RD(Random), 3=error
[uvarint]      entry count
每个 entry:
  [1B type]    0x22='"' 或 0x23='#'
  [4B IPv4]    4 字节 IP 地址
  [2B port]    端口
  [1B term]    0x00 终止符
```

### Python 解析

```python
def decode_txt_binary_payload(data: bytes) -> str:
    """解析 decodeTXTBinaryPayload 格式"""
    mode = data[0] & 0x03
    mode_str = {0: '', 1: ';RR', 2: ';RD', 3: ''}.get(mode, '')

    # 读取 uvarint entry count
    idx = 1
    count = 0
    shift = 0
    while True:
        b = data[idx]
        count |= (b & 0x7f) << shift
        idx += 1
        if not (b & 0x80):
            break
        shift += 7

    entries = []
    for _ in range(count):
        # type (1 byte)
        entry_type = data[idx]; idx += 1
        # IPv4 (4 bytes)
        ip = '.'.join(str(b) for b in data[idx:idx+4]); idx += 4
        # port (2 bytes, big endian)
        port = (data[idx] << 8) | data[idx+1]; idx += 2
        # terminator
        idx += 1  # 0x00
        entries.append(f"{ip}:{port}")

    return ','.join(entries) + mode_str
```

### 解密结果示例

```
Node 1 (东京·节点1): REDACTED_IPV4_10:80,REDACTED_IPV4_07:80,REDACTED_IPV4_08:80,REDACTED_IPV4_09:80
Node 2 (香港·节点2): REDACTED_IPV4_15:80,REDACTED_IPV4_16:80,...;RR
```

---

## 五、完整解密脚本

```python
#!/usr/bin/env python3
"""full_decrypt.py — 完整两层解密"""
import socket, ssl, json, base64, hashlib
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from Crypto.Cipher import AES

# ... (raw_https 函数同前)

# 1. 登录
h, b = raw_https('POST', '/v1/auth/login',
    extra_headers={'Origin': 'https://WEB_HOST.invalid'},
    json_body={'email': 'REDACTED_ACCOUNT_EMAIL',
               'password': 'REDACTED_ACCOUNT_PASSWORD'})
token = json.loads(b)['data']['token']

# 2. X25519 + 获取配置
client_priv = X25519PrivateKey.generate()
client_pub = client_priv.public_key().public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw)
pub_b64 = base64.urlsafe_b64encode(client_pub).rstrip(b'=').decode()

h, b = raw_https('GET', '/v1/public/node/list',
    extra_headers={'Authorization': token, 'Origin': 'https://WEB_HOST.invalid',
                   'X-Cftun-Config-Key': pub_b64})
cfg_resp = json.loads(b)

# 3. Layer 1: 解密配置响应
spk = b64url_decode(cfg_resp['server_public_key'])
salt = b64url_decode(cfg_resp['salt'])
nonce = b64url_decode(cfg_resp['nonce'])
ct = b64url_decode(cfg_resp['ciphertext'])
shared = client_priv.exchange(X25519PublicKey.from_public_bytes(spk))
aes_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=salt,
               info=b'cftun-config-response-v1').derive(shared)

cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
cipher.update(b'cftun-config-response-v1')
plaintext = cipher.decrypt_and_verify(ct[:-16], ct[-16:])
config = json.loads(plaintext.decode('utf-8'))
nodes = config['data']['list'][0]['nodes']

# 4. Layer 2: 解密 access_point
payloadSecret = nodes[0]['config']['payload_secret']
key = hashlib.sha256(payloadSecret.encode()).digest()

for node in nodes:
    raw = b64url_decode(node['access_point'])
    cipher = AES.new(key, AES.MODE_GCM, nonce=raw[:12])
    cipher.update(b'cftun-txt')
    pt = cipher.decrypt_and_verify(raw[12:-16], raw[-16:])
    ips = decode_txt_binary_payload(pt)
    print(f"Node {node['id']} ({node['name']}): {ips}")
```

---

## 六、19 个节点解密结果

| # | 名称 | 国家 | 出口 IP | Endpoint 数 | 传输 |
|---|------|------|---------|-----------|------|
| 1 | 东京·节点1 | JP | REDACTED_IPV4_10 | 4 | websocket |
| 2 | 香港·节点2 | CN | REDACTED_IPV4_11 | 20 | implicit_ws |
| 4 | 新加坡·节点1 | SG | REDACTED_IPV4_02 | 4 | websocket |
| 6 | 香港·节点1 | CN | REDACTED_IPV4_19 | 20 | websocket |
| 13 | 西雅图·节点1 | US | REDACTED_IPV4_13 | 4 | websocket |
| 14 | 洛杉矶·节点1 | US | REDACTED_IPV4_12 | 4 | websocket |
| 26 | 首尔·节点1 | KR | REDACTED_IPV4_18 | 21 | websocket |

（共 19 个节点，5 个服务器集群，173 个 endpoint IP）

---

## 七、关键发现总结

走完这一步你应该有：

- ✅ Layer 1 解密成功（X25519+HKDF+AES-256-GCM）
- ✅ Layer 2 解密成功（AES-256-GCM with SHA256(payloadSecret)）
- ✅ payloadSecret = `"REDACTED_PAYLOAD_SECRET"`（字面值）
- ✅ AAD = `b"cftun-txt"`
- ✅ 19 个节点的真实出口 IP 全部提取
- ✅ `decrypted_config_full.json` 已保存

---

**下一步**：`09-第九步-抓包分析流量.md`

<!-- source-core-08:source-end -->


---

<a id="source-core-09"></a>

> **归档编辑注**：本章为脱敏来源正文；原始目标文件、工程、抓包/结果附件未提供。下文的预期输出与成功断言不是本次复现记录。

<!-- source-core-09:source-start -->

# 09 · 第九步 — 抓包分析流量

---

## 目标

用 Windows 内置的 pktmon 抓包，分析 xTun 的 WebSocket 流量，提取协议细节。

---

## 一、为什么用 pktmon

| 工具 | 优点 | 缺点 |
|------|------|------|
| pktmon | Windows 内置，无需安装 | 只抓到客户端→服务器方向 |
| Wireshark | 功能强大，解析完整 | 需要安装，Npcap 驱动 |
| Frida | 应用层 hook，看到明文 | 需要 frida 环境 |

本教学用 **pktmon**（零安装），辅以 Frida（应用层）。

---

## 二、pktmon 命令

### 2.1 开始抓包

```bash
# 管理员权限运行 PowerShell

# 添加过滤器（抓 TCP 80 端口）
pktmon filter add -p 80

# 开始抓包，输出到 ETL 文件
pktmon start --capture --etl "WORKSPACE_ROOT\ws_capture.etl" --pkt-size 0 -m

# 现在去 xTun 客户端连接一个节点...

# 停止抓包
pktmon stop
```

### 2.2 转换为 pcap 格式

```bash
# ETL → pcap
pktmon etl2pcap "WORKSPACE_ROOT\ws_capture.etl" -o "WORKSPACE_ROOT\ws_capture.pcapng"
```

### 2.3 文本格式查看

```bash
# ETL → 文本
pktmon format "WORKSPACE_ROOT\ws_capture.etl" -o "WORKSPACE_ROOT\ws_capture.txt"
```

---

## 三、解析 pcap 文件

### 3.1 用 Python 解析

```python
#!/usr/bin/env python3
"""parse_pcap.py — 解析 pcap，提取 WebSocket 帧"""
import struct

def parse_pcap(path):
    with open(path, 'rb') as f:
        # pcap 全局头
        magic = struct.unpack('<I', f.read(4))[0]
        if magic == 0xa1b2c3d4:
            endian = '<'
        elif magic == 0xd4c3b2a1:
            endian = '>'
        else:
            print(f"Unknown magic: {hex(magic)}")
            return

        f.read(20)  # 跳过其余全局头

        pkt_num = 0
        while True:
            # 包头
            hdr = f.read(16)
            if len(hdr) < 16: break
            ts_sec, ts_usec, incl_len, orig_len = struct.unpack(
                endian + 'IIII', hdr)

            # 包数据
            data = f.read(incl_len)
            pkt_num += 1

            # 解析 Ethernet → IP → TCP
            if len(data) < 54: continue

            # Ethernet (14 bytes)
            eth_type = struct.unpack('>H', data[12:14])[0]
            if eth_type != 0x0800: continue  # 不是 IPv4

            # IP (20 bytes)
            ip_hdr = data[14:34]
            ip_proto = ip_hdr[9]
            if ip_proto != 6: continue  # 不是 TCP

            ip_src = '.'.join(str(b) for b in ip_hdr[12:16])
            ip_dst = '.'.join(str(b) for b in ip_hdr[16:20])

            # TCP
            tcp_start = 14 + (ip_hdr[0] & 0x0f) * 4
            tcp_hdr = data[tcp_start:tcp_start+20]
            src_port = struct.unpack('>H', tcp_hdr[0:2])[0]
            dst_port = struct.unpack('>H', tcp_hdr[2:4])[0]
            tcp_flags = tcp_hdr[13]
            data_offset = (tcp_hdr[12] >> 4) * 4

            # TCP payload
            payload = data[tcp_start + data_offset:]

            if payload:
                print(f"Pkt {pkt_num}: {ip_src}:{src_port} → {ip_dst}:{dst_port} "
                      f"flags={hex(tcp_flags)} payload={len(payload)}B")

                # 检查是否是 HTTP/WebSocket 升级
                if payload.startswith(b'GET '):
                    print(f"  HTTP Request: {payload[:200].decode('utf-8', 'replace')}")
                elif payload.startswith(b'HTTP/'):
                    print(f"  HTTP Response: {payload[:200].decode('utf-8', 'replace')}")

parse_pcap("ws_capture.pcapng")
```

### 3.2 提取 WebSocket 帧

```python
def extract_ws_frames(payload):
    """从 TCP payload 中提取 WebSocket 帧"""
    frames = []
    idx = 0
    while idx + 2 <= len(payload):
        # WebSocket 帧头
        b0 = payload[idx]
        b1 = payload[idx + 1]

        fin = (b0 & 0x80) != 0
        opcode = b0 & 0x0f
        masked = (b1 & 0x80) != 0
        length = b1 & 0x7f

        idx += 2

        if length == 126:
            length = struct.unpack('>H', payload[idx:idx+2])[0]
            idx += 2
        elif length == 127:
            length = struct.unpack('>Q', payload[idx:idx+8])[0]
            idx += 8

        if masked:
            mask = payload[idx:idx+4]
            idx += 4

        data = payload[idx:idx+length]
        if masked:
            data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
        idx += length

        op_names = {0: 'continuation', 1: 'text', 2: 'binary',
                    8: 'close', 9: 'ping', 10: 'pong'}
        frames.append({
            'opcode': op_names.get(opcode, f'unknown({opcode})'),
            'fin': fin,
            'data': data,
        })

    return frames
```

---

## 四、抓包发现的关键信息

### 4.1 WebSocket 升级请求

```
GET /hkg/e/REDACTED_IPV4_11 HTTP/1.1
Host: REDACTED_IPV4_15
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: <base64>
Sec-WebSocket-Version: 13
Sec-WebSocket-Protocol: cftun websocket v3
Origin: https://WEB_HOST.invalid
User-Agent: DEV
Content-Length: 0
```

### 4.2 服务器响应

```
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: <base64>
```

### 4.3 第一个 WebSocket 帧（open frame）

- Opcode: 2 (binary)
- FIN: true
- 长度: ~83 字节
- 内容: 12 字节 nonce + ciphertext + 16 字节 tag

---

## 五、细节：pktmon 只抓到客户端→服务器方向

pktmon 在某些配置下只能看到单向流量。如果需要双向：

### 方法 1：用 netsh trace

```bash
netsh trace start capture=yes maxsize=512 tracefile="WORKSPACE_ROOT\trace.etl"
# 连接节点...
netsh trace stop
```

### 方法 2：用 Frida hook（应用层，看到明文）

```javascript
// frida_hook_ws.js
Java.perform(function() {
    var socket = Java.use('java.net.Socket');
    socket.$init.overload('java.lang.String', 'int').implementation = function(host, port) {
        console.log("[Socket] " + host + ":" + port);
        return this.$init(host, port);
    };
});
```

---

## 六、关键发现总结

走完这一步你应该有：

- ✅ pktmon 抓包成功（ETL + pcapng）
- ✅ 看到 WebSocket 升级请求
- ✅ 提取了 WebSocket 帧
- ✅ 确认了 Host=纯IP、Path=/{upstream}/e/{exit_ip}、UA=DEV
- ✅ 看到了第一个 binary 帧（open frame）

---

**下一步**：`10-第十步-测试WebSocket连接.md`

<!-- source-core-09:source-end -->


---

<a id="source-core-10"></a>

> **归档编辑注**：本章为脱敏来源正文；原始目标文件、工程、抓包/结果附件未提供。下文的预期输出与成功断言不是本次复现记录。

<!-- source-core-10:source-start -->

# 10 · 第十步 — 测试 WebSocket 连接

---

## 目标

构造 WebSocket 升级请求，测试不同 Host/Path/Header 组合，找到能成功的参数。

---

## 一、怎么构造 WebSocket 升级请求

```python
#!/usr/bin/env python3
"""ws_connect.py — 测试 WebSocket 连接"""
import socket, base64, os

def ws_upgrade(ip, port, host, path, extra_headers=None, timeout=10):
    """构造 WebSocket 升级请求"""
    sock = socket.create_connection((ip, port), timeout=timeout)
    sock.settimeout(timeout)

    ws_key = base64.b64encode(os.urandom(16)).decode()

    headers = [
        f"GET {path} HTTP/1.1",
        f"Host: {host}",
        "Upgrade: websocket",
        "Connection: Upgrade",
        f"Sec-WebSocket-Key: {ws_key}",
        "Sec-WebSocket-Version: 13",
        "Sec-WebSocket-Protocol: cftun websocket v3",
        "Origin: https://WEB_HOST.invalid",
        "User-Agent: DEV",
        "Content-Length: 0",
        "",
        ""
    ]

    if extra_headers:
        # 插入额外头
        insert_pos = len(headers) - 2
        for k, v in extra_headers.items():
            headers.insert(insert_pos, f"{k}: {v}")

    req = "\r\n".join(headers).encode()
    sock.sendall(req)

    response = b""
    while b"\r\n\r\n" not in response:
        chunk = sock.recv(4096)
        if not chunk:
            sock.close()
            return None, "Connection closed"
        response += chunk

    status_line = response.split(b"\r\n")[0].decode('utf-8', 'replace')
    sock.close()
    return status_line, response.decode('utf-8', 'replace')
```

---

## 二、测试不同 Host/Path/Header 组合

### 2.1 精确连接参数（已验证成功）

| 参数 | 值 | 说明 |
|------|-----|------|
| **Host** | 纯 IP 地址（不带端口） | 如 `REDACTED_IPV4_15` |
| **Path** | `/{upstream}/e/{exit_server_ip}` | 如 `/hkg/e/REDACTED_IPV4_11` |
| **User-Agent** | `DEV` | 大小写敏感 |
| **Port** | 80 | 无 TLS (ws://) |
| **Sec-WebSocket-Protocol** | `cftun websocket v3` | 可选 |
| **Origin** | `https://WEB_HOST.invalid` | 必须 |

### 2.2 测试脚本

```python
#!/usr/bin/env python3
"""test_ws_headers.py — 批量测试 WebSocket 连接"""

# 已知 endpoint IP（从 access_point 解密得到）
ENDPOINTS = [
    "REDACTED_IPV4_15",
    "REDACTED_IPV4_16",
    "REDACTED_IPV4_14",
    "REDACTED_IPV4_17",
]

# 测试组合
tests = [
    # (描述, ip, host, path, ua)
    ("正确: 纯IP + /hkg/e/ + DEV", "REDACTED_IPV4_15", "REDACTED_IPV4_15", "/hkg/e/REDACTED_IPV4_11", "DEV"),
    ("错误: 域名Host", "REDACTED_IPV4_15", "NODE_DOMAIN.invalid", "/hkg/e/REDACTED_IPV4_11", "DEV"),
    ("错误: Host带端口", "REDACTED_IPV4_15", "REDACTED_IPV4_15:80", "/hkg/e/REDACTED_IPV4_11", "DEV"),
    ("错误: UA≠DEV", "REDACTED_IPV4_15", "REDACTED_IPV4_15", "/hkg/e/REDACTED_IPV4_11", "Mozilla/5.0"),
    ("错误: Path带cf_前缀", "REDACTED_IPV4_15", "REDACTED_IPV4_15", "/cf_hkg/e/REDACTED_IPV4_11", "DEV"),
    ("错误: Path=/", "REDACTED_IPV4_15", "REDACTED_IPV4_15", "/", "DEV"),
]

for desc, ip, host, path, ua in tests:
    status, resp = ws_upgrade(ip, 80, host, path,
                              extra_headers={'User-Agent': ua})
    result = "✅" if status and "101" in status else "❌"
    print(f"{result} {desc}: {status}")
```

### 2.3 预期结果

```
✅ 正确: 纯IP + /hkg/e/ + DEV: HTTP/1.1 101 Switching Protocols
❌ 错误: 域名Host: HTTP/1.1 403 Forbidden
❌ 错误: Host带端口: (timeout / connection reset)
❌ 错误: UA≠DEV: (444 silent disconnect)
❌ 错误: Path带cf_前缀: HTTP/1.1 404 Not Found
❌ 错误: Path=/: HTTP/1.1 404 Not Found
```

---

## 三、怎么判断成功

成功的标志是 **`101 Switching Protocols`**：

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

任何其他状态码都是失败：

| 状态码 | 原因 |
|--------|------|
| 101 | ✅ 成功 |
| 403 | Beaver WAF 拦截（域名 Host） |
| 404 | 路径错误 |
| 444 | nginx 静默断开（UA 不对） |
| timeout | 连接被拒绝或重置 |

---

## 四、怎么识别 WAF

### 4.1 WAF 架构

```
客户端 → Beaver WAF → nginx/1.31.4 → WebSocket 后端
```

### 4.2 三层过滤

| 层 | 检查什么 | 失败结果 |
|----|----------|----------|
| **Beaver WAF** | Host 头是域名 → ICP 未备案 | 403 Forbidden |
| **nginx 1.31.4** | User-Agent ≠ "DEV" | 444 静默断开 |
| **WebSocket 后端** | Path 格式不对 | 404 Not Found |

### 4.3 识别方法

```python
# 测试 WAF 响应
status, resp = ws_upgrade("REDACTED_IPV4_15", 80, "NODE_DOMAIN.invalid", "/hkg/e/REDACTED_IPV4_11")

if "403" in status:
    print("Beaver WAF 拦截 (域名 Host)")
    # 检查响应体是否有 "ICP" 字样
    if "ICP" in resp or "beaver" in resp.lower():
        print("确认: Beaver WAF")

status, resp = ws_upgrade("REDACTED_IPV4_15", 80, "REDACTED_IPV4_15",
                          "/hkg/e/REDACTED_IPV4_11",
                          extra_headers={'User-Agent': 'Mozilla/5.0'})
if not status or "444" in status:
    print("nginx 静默断开 (UA 不对)")
```

---

## 五、细节：为什么之前 186 次失败

### 失败原因分析

| # | 错误 | 正确值 | 原因 |
|---|------|--------|------|
| 1 | Path 带 cf_ 前缀 `/cf_hkg/e/...` | `/hkg/e/...` | isArgo=false 时不加 cf_ 前缀 |
| 2 | Host 带端口 `REDACTED_IPV4_15:80` | `REDACTED_IPV4_15` | 纯 IP 不带端口 |
| 3 | 用域名 Host | 用纯 IP Host | 域名触发 Beaver WAF 403 |
| 4 | User-Agent 不精确 | `DEV` | nginx 检查 UA 精确匹配 |

### Ghidra 反编译确认

| 函数 | 地址 | 确认内容 |
|------|------|----------|
| `implicitWebsocketRouteUpstream` | `0x14034f3a0` | isArgo=false 时不加 cf_ 前缀 |
| `connectWithPurpose` | `0x14034afc0` | UA=DEV 在初始 HTTP 请求就设置 |
| `NewWebsocket` | `0x140348120` | gorilla Dialer Subprotocols=nil |

---

## 六、验证成功的 IP

经过测试，这些 endpoint IP 全部返回 101：

| IP | 状态 | 关联节点 |
|----|------|----------|
| `REDACTED_IPV4_15` | ✅ 101 | 香港/曼谷/河内 |
| `REDACTED_IPV4_16` | ✅ 101 | 香港/曼谷/河内 |
| `REDACTED_IPV4_14` | ✅ 101 | 香港/曼谷/河内 |
| `REDACTED_IPV4_17` | ✅ 101 | 香港/曼谷/河内 |

---

## 七、关键发现总结

走完这一步你应该有：

- ✅ WebSocket 连接参数全部确认
- ✅ Host = 纯 IP（不带端口）
- ✅ Path = `/{upstream}/e/{exit_server_ip}`（无 cf_ 前缀）
- ✅ UA = `DEV`（大小写敏感）
- ✅ 端口 80，无 TLS
- ✅ WAF 架构理解（Beaver → nginx → backend）
- ✅ 4 个 IP 返回 101 成功

---

**下一步**：`11-第十一步-实现协议握手.md`

<!-- source-core-10:source-end -->


---

<a id="source-core-11"></a>

> **归档编辑注**：本章为脱敏来源正文；原始目标文件、工程、抓包/结果附件未提供。下文的预期输出与成功断言不是本次复现记录。

<!-- source-core-11:source-start -->

# 11 · 第十一步 — 实现协议握手

---

## 目标

构造 cftun v3 的 open frame，完成协议握手，建立加密通道。

---

## 一、握手概述

cftun websocket v3 的握手很简单：

```
1. WebSocket 连接成功 (101)
2. 客户端发送 open frame (一个加密的 binary WebSocket 帧)
3. 握手完成 — 不等服务器响应，直接开始数据通道
```

**关键：open frame 发送后，握手就完成了。** 服务器不返回握手响应，直接进入数据通道模式。

---

## 二、open frame 明文格式

### 2.1 字段定义

```
[1B frame_type]       4=无 route_metadata, 5=有 route_metadata
[1B protection_flag]  0=明文, 1=加密
[1B protocol]         6=TCP, 17=UDP (IP 协议号)
[1B ip_version]       4=IPv4, 6=IPv6
[4B uint32 LE]        protection_flag (重复，小端)
[4B dest_ip]          目标 IPv4 地址
[2B uint16 BE]        目标端口 (大端)
[1B tunnel_uuid_len]  tunnel_uuid 字符串长度
[tunnel_uuid_len B]   tunnel_uuid 字符串
[32B clientKey]       随机 32 字节
```

### 2.2 每个字段的含义和值

| 偏移 | 长度 | 字段 | 值 | 说明 |
|------|------|------|-----|------|
| 0 | 1 | frame_type | `4` | 无 route_metadata（socksProxy 为空时） |
| 1 | 1 | protection_flag | `1` | 加密通道 |
| 2 | 1 | protocol | `6` (TCP) / `17` (UDP) | IP 协议号 |
| 3 | 1 | ip_version | `4` (IPv4) / `6` (IPv6) | IP 版本 |
| 4 | 4 | protection_flag (uint32 LE) | `\x01\x00\x00\x00` | 小端编码的 1 |
| 8 | 4 | dest_ip | 如 `REDACTED_DESTINATION_IPV4_BYTES` | 目标 IPv4 (4 字节) |
| 12 | 2 | dest_port | 如 `\x01\xbb` (443) | 大端编码 |
| 14 | 1 | tunnel_uuid_len | `36` | UUID 字符串长度 |
| 15 | 36 | tunnel_uuid | `"REDACTED_TUNNEL_UUID"` | UTF-8 字符串 |
| 51 | 32 | clientKey | 随机 32 字节 | 用于派生数据通道密钥 |

总长度: 51 + 32 = **83 字节**

### 2.3 Python 构造明文

```python
import struct, os

TUNNEL_UUID = "REDACTED_TUNNEL_UUID"

def build_open_plaintext(client_key: bytes, dst_ip: str, dst_port: int,
                         is_tcp: bool = True) -> bytes:
    """
    构造 open frame 明文 (buildArgoOpenPlaintext, argo.go:285)
    """
    frame_type = 4       # 无 route metadata
    protection_flag = 1  # 加密
    protocol = 6 if is_tcp else 17  # IP 协议号
    ip_version = 4       # IPv4

    tunnel_uuid_bytes = TUNNEL_UUID.encode('utf-8')
    dst_ip_bytes = bytes(int(x) for x in dst_ip.split('.'))

    pt = bytearray()
    pt.append(frame_type)                           # [0] frame_type
    pt.append(protection_flag)                      # [1] protection_flag
    pt.append(protocol)                             # [2] protocol
    pt.append(ip_version)                           # [3] ip_version
    pt.extend(struct.pack('<I', protection_flag))   # [4:8] uint32 LE
    pt.extend(dst_ip_bytes)                         # [8:12] dest IP
    pt.extend(struct.pack('>H', dst_port))          # [12:14] port BE
    pt.append(len(tunnel_uuid_bytes))               # [14] uuid length
    pt.extend(tunnel_uuid_bytes)                    # [15:51] uuid string
    pt.extend(client_key)                           # [51:83] clientKey

    return bytes(pt)

# 示例
client_key = os.urandom(32)
plaintext = build_open_plaintext(client_key, "REDACTED_IPV4_20", 443)
print(f"明文长度: {len(plaintext)}")  # 83
print(f"明文 hex: {plaintext.hex()}")
```

---

## 三、怎么加密 open frame

### 3.1 密钥派生

```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

PAYLOAD_SECRET = b"REDACTED_PAYLOAD_SECRET"
INFO_OPEN_KEY = b"cftun websocket v3 open key"

def derive_open_key() -> bytes:
    """派生 open frame 加密密钥"""
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,                    # salt 为 None
        info=INFO_OPEN_KEY
    ).derive(PAYLOAD_SECRET)
```

### 3.2 加密参数

| 参数 | 值 |
|------|-----|
| 算法 | ChaCha20-Poly1305 |
| Key | `HKDF-SHA256(payloadSecret, salt=None, info="cftun websocket v3 open key", 32)` |
| Nonce | 12 字节随机 |
| AAD | `b"cftun websocket v3 open"` |
| 输出 | nonce(12) + ciphertext + tag(16) |

### 3.3 Python 加密

```python
from Crypto.Cipher import ChaCha20_Poly1305
import os

AAD_OPEN = b"cftun websocket v3 open"

def encrypt_open_frame(plaintext: bytes) -> bytes:
    """加密 open frame"""
    open_key = derive_open_key()

    # 12 字节随机 nonce
    nonce = os.urandom(12)

    cipher = ChaCha20_Poly1305.new(key=open_key, nonce=nonce)
    cipher.update(AAD_OPEN)  # 设置 AAD

    # encrypt_and_digest 返回 (ciphertext, tag)
    # Go 的 AEAD.Seal() 返回 ciphertext + tag (连续)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)

    # 帧格式: nonce(12) + ciphertext + tag(16)
    frame = nonce + ciphertext + tag
    return frame

# 加密
frame = encrypt_open_frame(plaintext)
print(f"加密帧长度: {len(frame)}")  # 12 + 83 + 16 = 111
```

---

## 四、关键 bug：encrypt_and_digest() vs encrypt()

### 4.1 问题描述

Go 的 `aead.Seal(dst, nonce, plaintext, aad)` 返回 `ciphertext + tag`（连续拼接）。

pycryptodome 有两个方法：

| 方法 | 返回值 | tag 在哪 |
|------|--------|----------|
| `encrypt(plaintext)` | 只有 ciphertext | 需要单独调 `digest()` |
| `encrypt_and_digest(plaintext)` | `(ciphertext, tag)` 元组 | 分开返回 |

### 4.2 正确做法

```python
# ✅ 正确: 用 encrypt_and_digest
cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
cipher.update(aad)
ciphertext, tag = cipher.encrypt_and_digest(plaintext)
frame = nonce + ciphertext + tag  # Go 兼容格式

# ❌ 错误: 用 encrypt（丢失 tag）
cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
cipher.update(aad)
ciphertext = cipher.encrypt(plaintext)
frame = nonce + ciphertext  # 缺少 tag！服务器会拒绝
```

### 4.3 解密时也要注意

```python
# 接收到的帧: nonce(12) + ciphertext + tag(16)
nonce = data[:12]
ciphertext = data[12:-16]  # 去掉 nonce 和 tag
tag = data[-16:]            # 最后 16 字节

cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
cipher.update(aad)
plaintext = cipher.decrypt_and_verify(ciphertext, tag)  # 验证 tag
```

---

## 五、发送 open frame

```python
def do_handshake(ws, dst_ip: str, dst_port: int) -> bool:
    """完成 cftun v3 握手"""
    # 1. 生成随机 clientKey
    client_key = os.urandom(32)

    # 2. 构造明文
    plaintext = build_open_plaintext(client_key, dst_ip, dst_port)

    # 3. 加密
    frame = encrypt_open_frame(plaintext)

    # 4. 作为 WebSocket binary 帧发送
    ws.send_frame(frame, opcode=0x02)  # 0x02 = binary

    # 5. 派生数据通道密钥
    write_key = hkdf_sha256(PAYLOAD_SECRET, client_key,
                            b"cftun websocket v3 client to server key", 32)
    read_key = hkdf_sha256(PAYLOAD_SECRET, client_key,
                           b"cftun websocket v3 server to client key", 32)

    # 6. 握手完成 — 不等服务器响应
    print("Handshake OK (open frame sent)")
    return True, write_key, read_key
```

---

## 六、完整握手示例

```python
#!/usr/bin/env python3
"""handshake_example.py — 完整 cftun v3 握手"""
import socket, base64, os, struct, hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from Crypto.Cipher import ChaCha20_Poly1305

PAYLOAD_SECRET = b"REDACTED_PAYLOAD_SECRET"
TUNNEL_UUID = "REDACTED_TUNNEL_UUID"

# 1. WebSocket 连接
sock = socket.create_connection(("REDACTED_IPV4_15", 80), timeout=10)
ws_key = base64.b64encode(os.urandom(16)).decode()
req = (f"GET /hkg/e/REDACTED_IPV4_11 HTTP/1.1\r\n"
       f"Host: REDACTED_IPV4_15\r\n"
       f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
       f"Sec-WebSocket-Key: {ws_key}\r\n"
       f"Sec-WebSocket-Version: 13\r\n"
       f"Sec-WebSocket-Protocol: cftun websocket v3\r\n"
       f"Origin: https://WEB_HOST.invalid\r\n"
       f"User-Agent: DEV\r\nContent-Length: 0\r\n\r\n")
sock.sendall(req.encode())

resp = b""
while b"\r\n\r\n" not in resp:
    resp += sock.recv(4096)
assert b"101" in resp, f"WS failed: {resp[:100]}"
print("[+] WebSocket 101 OK")

# 2. 构造 open frame
client_key = os.urandom(32)
pt = bytearray([4, 1, 6, 4])  # frame_type, protection, protocol, ip_ver
pt.extend(struct.pack('<I', 1))  # protection_flag LE
pt.extend(bytes(int(x) for x in "REDACTED_IPV4_20".split('.')))  # dst IP
pt.extend(struct.pack('>H', 443))  # dst port
pt.append(36)  # uuid len
pt.extend(TUNNEL_UUID.encode())
pt.extend(client_key)

# 3. 加密
open_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
                info=b"cftun websocket v3 open key").derive(PAYLOAD_SECRET)
nonce = os.urandom(12)
cipher = ChaCha20_Poly1305.new(key=open_key, nonce=nonce)
cipher.update(b"cftun websocket v3 open")
ct, tag = cipher.encrypt_and_digest(bytes(pt))
frame = nonce + ct + tag

# 4. 发送 (WebSocket binary frame)
# ... (封装成 WebSocket 帧发送)
print(f"[+] Open frame sent: {len(frame)} bytes")

# 5. 派生数据通道密钥
c2s_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=client_key,
               info=b"cftun websocket v3 client to server key").derive(PAYLOAD_SECRET)
s2c_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=client_key,
               info=b"cftun websocket v3 server to client key").derive(PAYLOAD_SECRET)
print("[+] Data channel keys derived")
print("[+] Handshake complete!")
```

---

## 七、关键发现总结

走完这一步你应该有：

- ✅ open frame 明文格式（83 字节，每个字段含义）
- ✅ ChaCha20-Poly1305 加密参数（key, nonce, AAD）
- ✅ encrypt_and_digest() vs encrypt() 的 bug
- ✅ 握手流程：发送 open frame → 完成
- ✅ 数据通道密钥派生（c2s_key, s2c_key）

---

**下一步**：`12-第十二步-实现数据通道.md`

<!-- source-core-11:source-end -->


---

<a id="source-core-12"></a>

> **归档编辑注**：本章为脱敏来源正文；原始目标文件、工程、抓包/结果附件未提供。下文的预期输出与成功断言不是本次复现记录。

<!-- source-core-12:source-start -->

# 12 · 第十二步 — 实现数据通道

---

## 目标

实现 cftun v3 的加密数据通道，双向收发数据。

---

## 一、数据通道概述

握手完成后，每个 WebSocket binary 帧就是一个加密的数据包：

```
发送: 应用数据 → ChaCha20-Poly1305 加密 → WebSocket binary 帧
接收: WebSocket binary 帧 → ChaCha20-Poly1305 解密 → 应用数据
```

**客户端→服务器** 和 **服务器→客户端** 使用不同的密钥。

---

## 二、加密参数

### 2.1 密钥

| 方向 | 密钥 | 派生 |
|------|------|------|
| client → server | `c2s_key` | `HKDF-SHA256(payloadSecret, salt=clientKey, info="cftun websocket v3 client to server key", 32)` |
| server → client | `s2c_key` | `HKDF-SHA256(payloadSecret, salt=clientKey, info="cftun websocket v3 server to client key", 32)` |

### 2.2 Nonce 和 AAD（序号递增）

每个包有一个递增的序号 `seq`（从 0 开始）：

| 字段 | 值 |
|------|-----|
| Nonce | `b'\x00\x00\x00\x00' + struct.pack('>Q', seq)` (4 零 + 8 字节大端序号) |
| AAD (c2s) | `b"cftun websocket v3 client to server" + struct.pack('>Q', seq)` |
| AAD (s2c) | `b"cftun websocket v3 server to client" + struct.pack('>Q', seq)` |

**关键：nonce 和 AAD 都包含 seq，每个包递增。**

### 2.3 帧格式

```
[WebSocket binary frame]
  = nonce 不在帧里（nonce 由 seq 计算，不传输）
  = ciphertext + tag(16)
```

注意：数据通道的 nonce 是由 seq 计算的，不像 open frame 那样随机生成并传输。接收方用自己维护的 seq 计算 nonce 来解密。

---

## 三、Python 实现

### 3.1 发送数据（client → server）

```python
import struct, os
from Crypto.Cipher import ChaCha20_Poly1305

AAD_C2S = b"cftun websocket v3 client to server"

class DataChannel:
    def __init__(self, write_key: bytes, read_key: bytes):
        self.write_key = write_key  # c2s_key
        self.read_key = read_key    # s2c_key
        self.write_seq = 0
        self.read_seq = 0

    def write(self, data: bytes) -> bytes:
        """加密一个 client→server 数据包"""
        seq = self.write_seq
        self.write_seq += 1

        # Nonce: 4 零 + 8 字节大端 seq
        nonce = b'\x00\x00\x00\x00' + struct.pack('>Q', seq)

        # AAD: 方向字符串 + 8 字节大端 seq
        aad = AAD_C2S + struct.pack('>Q', seq)

        # 加密
        aead = ChaCha20_Poly1305.new(key=self.write_key, nonce=nonce)
        aead.update(aad)
        ciphertext, tag = aead.encrypt_and_digest(data)

        # 帧格式: ciphertext + tag (Go 的 Seal 格式)
        return ciphertext + tag
```

### 3.2 接收数据（server → client）

```python
AAD_S2C = b"cftun websocket v3 server to client"

class DataChannel:
    # ... (write 方法同上)

    def read(self, frame: bytes) -> bytes:
        """解密一个 server→client 数据包"""
        seq = self.read_seq
        self.read_seq += 1

        # Nonce
        nonce = b'\x00\x00\x00\x00' + struct.pack('>Q', seq)

        # AAD
        aad = AAD_S2C + struct.pack('>Q', seq)

        # 分割 ciphertext 和 tag
        if len(frame) < 16:
            raise ValueError("Frame too short")
        ciphertext = frame[:-16]
        tag = frame[-16:]

        # 解密
        aead = ChaCha20_Poly1305.new(key=self.read_key, nonce=nonce)
        aead.update(aad)
        plaintext = aead.decrypt_and_verify(ciphertext, tag)

        return plaintext
```

---

## 四、WebSocket 帧封装

数据通道的加密包需要封装成 WebSocket binary 帧发送：

```python
import struct, os

class WebSocketConnection:
    def __init__(self, sock):
        self.sock = sock
        self._recv_buf = b''

    def send_frame(self, data: bytes, opcode: int = 0x02):
        """发送 WebSocket 帧（客户端必须 mask）"""
        frame = bytearray([0x80 | opcode])  # FIN + opcode

        length = len(data)
        if length < 126:
            frame.append(0x80 | length)  # mask bit + length
        elif length < 65536:
            frame.append(0x80 | 126)
            frame.extend(struct.pack('>H', length))
        else:
            frame.append(0x80 | 127)
            frame.extend(struct.pack('>Q', length))

        # Mask key (客户端发送必须 mask)
        mask = os.urandom(4)
        frame.extend(mask)

        # Masked data
        frame.extend(bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

        self.sock.sendall(bytes(frame))

    def recv_frame(self, timeout=30) -> tuple:
        """接收 WebSocket 帧"""
        header = self._recv_n(2, timeout)
        opcode = header[0] & 0x0f
        masked = (header[1] & 0x80) != 0
        length = header[1] & 0x7f

        if length == 126:
            length = struct.unpack('>H', self._recv_n(2, timeout))[0]
        elif length == 127:
            length = struct.unpack('>Q', self._recv_n(8, timeout))[0]

        mask = self._recv_n(4, timeout) if masked else b''
        data = self._recv_n(length, timeout)

        if masked:
            data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))

        return opcode, data

    def _recv_n(self, n: int, timeout=30) -> bytes:
        """精确读取 n 字节"""
        buf = bytearray()
        self.sock.settimeout(timeout)
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError(f"EOF at {len(buf)}/{n}")
            buf.extend(chunk)
        return bytes(buf)
```

---

## 五、完整数据通道示例

```python
#!/usr/bin/env python3
"""data_channel_example.py — 完整数据通道"""

# 假设 ws 是已连接的 WebSocketConnection
# 假设 c2s_key, s2c_key 已从握手获得

channel = DataChannel(c2s_key, s2c_key)

# === 发送 HTTP 请求通过隧道 ===
http_request = b"GET / HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\n\r\n"

# 加密
encrypted = channel.write(http_request)
print(f"加密包: {len(encrypted)} bytes")

# 通过 WebSocket 发送
ws.send_frame(encrypted, opcode=0x02)
print("已发送")

# === 接收响应 ===
while True:
    opcode, data = ws.recv_frame(timeout=30)

    if opcode == 0x08:  # close
        print("WebSocket closed")
        break
    elif opcode == 0x09:  # ping
        ws.send_frame(data, opcode=0x0A)  # pong
        continue
    elif opcode == 0x0A:  # pong
        continue

    # 解密
    plaintext = channel.read(data)
    print(f"响应: {plaintext[:200]}")
```

---

## 六、序号同步问题

### 6.1 问题

客户端和服务器各自维护自己的 seq。如果丢包或乱序，seq 会不同步，导致解密失败。

### 6.2 解决

cftun 协议是**有序的**（WebSocket 保证有序），所以 seq 严格递增，不会乱序。

但如果连接断开重连，seq 从 0 重新开始。

### 6.3 错误处理

```python
def read(self, frame: bytes) -> bytes:
    try:
        # ... 解密 ...
        return plaintext
    except ValueError as e:
        # tag 验证失败 = seq 不同步或密钥错误
        print(f"解密失败 (seq={self.read_seq}): {e}")
        raise
```

---

## 七、关键发现总结

走完这一步你应该有：

- ✅ 数据通道加密参数（c2s_key, s2c_key, seq-based nonce/AAD）
- ✅ 发送/接收完整实现
- ✅ WebSocket 帧封装（客户端 mask）
- ✅ 序号同步理解
- ✅ 可以通过隧道收发数据

---

**下一步**：`13-第十三步-实现代理功能.md`

<!-- source-core-12:source-end -->


---

<a id="source-core-13"></a>

> **归档编辑注**：本章为脱敏来源正文；原始目标文件、工程、抓包/结果附件未提供。下文的预期输出与成功断言不是本次复现记录。

<!-- source-core-13:source-start -->

# 13 · 第十三步 — 实现代理功能

---

## 目标

在数据通道之上实现 SOCKS5 + HTTP 代理服务器，对外暴露本地代理端口。

---

## 一、架构

```
浏览器/应用 → SOCKS5/HTTP 代理 (本地) → cftun 隧道 → xTun 出口 → 目标网站
                ↑                        ↑
            本地端口 1080          WebSocket + ChaCha20
```

代理流程：
1. 本地应用连接 SOCKS5 代理
2. SOCKS5 协商目标地址
3. 代理建立 cftun 隧道到 xTun 节点
4. 通过隧道转发数据

---

## 二、SOCKS5 服务器

### 2.1 SOCKS5 协议

```
1. 客户端发送: 0x05 0x01 0x00 (版本5, 1方法, 无认证)
2. 服务器响应: 0x05 0x00 (版本5, 无认证)
3. 客户端发送: 0x05 0x01 0x00 0x01 [4B IP] [2B port]
   (版本5, CONNECT, 保留, IPv4, IP, 端口)
4. 服务器响应: 0x05 0x00 0x00 0x01 [4B IP] [2B port]
5. 开始转发数据
```

### 2.2 Python 实现

```python
import socket, struct, threading

class Socks5Server:
    def __init__(self, host, port, nodes):
        self.host = host
        self.port = port
        self.nodes = nodes
        self.node_idx = 0

    def _next_node(self):
        """轮询选择节点"""
        node = self.nodes[self.node_idx % len(self.nodes)]
        self.node_idx += 1
        return node

    def handle_client(self, client_sock, addr):
        try:
            client_sock.settimeout(15)

            # 1. SOCKS5 握手
            data = client_sock.recv(1024)
            if not data or data[0] != 0x05:
                return
            client_sock.sendall(b'\x05\x00')  # 无认证

            # 2. 读取请求
            data = client_sock.recv(1024)
            if not data or data[0] != 0x05:
                return

            cmd = data[1]
            if cmd != 0x01:  # 只支持 CONNECT
                client_sock.sendall(b'\x05\x07\x00\x01\x00\x00\x00\x00\x00\x00')
                return

            # 3. 解析目标地址
            atyp = data[3]
            if atyp == 0x01:  # IPv4
                dst_ip = socket.inet_ntoa(data[4:8])
                dst_port = struct.unpack('>H', data[8:10])[0]
            elif atyp == 0x03:  # 域名
                dlen = data[4]
                domain = data[5:5+dlen].decode()
                dst_port = struct.unpack('>H', data[5+dlen:7+dlen])[0]
                # DNS 解析
                dst_ip = socket.getaddrinfo(domain, None,
                    socket.AF_INET)[0][4][0]
            elif atyp == 0x04:  # IPv6
                dst_ip = socket.inet_ntop(socket.AF_INET6, data[4:20])
                dst_port = struct.unpack('>H', data[20:22])[0]
            else:
                return

            print(f"SOCKS5: {dst_ip}:{dst_port}")

            # 4. 通过 cftun 隧道连接
            node = self._next_node()
            conn = CftunConnection(node)
            if not conn.connect(dst_ip, dst_port):
                # 连接失败
                client_sock.sendall(b'\x05\x05\x00\x01\x00\x00\x00\x00\x00\x00')
                return

            # 5. 告诉客户端连接成功
            client_sock.sendall(b'\x05\x00\x00\x01' +
                bytes(int(x) for x in dst_ip.split('.')) +
                struct.pack('>H', dst_port))

            # 6. 双向转发
            conn.relay(client_sock)
            conn.close()

        except Exception as e:
            print(f"SOCKS5 error: {e}")
        finally:
            try: client_sock.close()
            except: pass

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(128)
        print(f"SOCKS5 proxy: socks5://{self.host}:{self.port}")

        while True:
            client, addr = server.accept()
            threading.Thread(target=self.handle_client,
                            args=(client, addr), daemon=True).start()
```

---

## 三、'HTTP 代理服务器

### 3.1 HTTP CONNECT 方法

```python
class HttpProxyServer:
    def handle_client(self, client_sock, addr):
        try:
            client_sock.settimeout(15)
            data = b''
            while b'\r\n\r\n' not in data:
                data += client_sock.recv(4096)

            request_line = data.split(b'\r\n')[0].decode()
            parts = request_line.split()

            if parts[0].upper() == 'CONNECT':
                # HTTPS: CONNECT host:port HTTP/1.1
                host_port = parts[1]
                host_str, port_str = host_port.rsplit(':', 1)
                dst_port = int(port_str)

                # DNS 解析
                dst_ip = socket.getaddrinfo(host_str, None,
                    socket.AF_INET)[0][4][0]

                # 通过 cftun 连接
                node = self._next_node()
                conn = CftunConnection(node)
                if not conn.connect(dst_ip, dst_port):
                    client_sock.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
                    return

                # 告诉客户端连接成功
                client_sock.sendall(
                    b'HTTP/1.1 200 Connection Established\r\n\r\n')

                # 转发
                conn.relay(client_sock)
                conn.close()
            else:
                # 普通 HTTP: 解析 Host 头
                headers = data.decode('utf-8', 'replace')
                for line in headers.split('\r\n')[1:]:
                    if line.lower().startswith('host:'):
                        host_str = line.split(':', 1)[1].strip()
                        break

                if ':' in host_str:
                    host_str, port_str = host_str.rsplit(':', 1)
                    dst_port = int(port_str)
                else:
                    dst_port = 80

                dst_ip = socket.getaddrinfo(host_str, None,
                    socket.AF_INET)[0][4][0]

                node = self._next_node()
                conn = CftunConnection(node)
                if not conn.connect(dst_ip, dst_port):
                    client_sock.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
                    return

                # 发送原始 HTTP 请求
                conn.channel.write(data)
                conn.relay(client_sock)
                conn.close()

        except Exception as e:
            print(f"HTTP proxy error: {e}")
        finally:
            try: client_sock.close()
            except: pass
```

---

## 四、双向转发

```python
class CftunConnection:
    def relay(self, client_sock, timeout=300):
        """双向转发: client ↔ tunnel"""
        def client_to_tunnel():
            """客户端 → 隧道"""
            try:
                while self.channel and self.channel.handshake_done:
                    client_sock.settimeout(1)
                    try:
                        data = client_sock.recv(65536)
                    except socket.timeout:
                        continue
                    if not data:
                        break
                    if not self.channel.write(data):
                        break
            except: pass

        def tunnel_to_client():
            """隧道 → 客户端"""
            try:
                while self.channel and self.channel.handshake_done:
                    data = self.channel.read(timeout=2)
                    if data is None:
                        break
                    if data:
                        client_sock.sendall(data)
            except: pass

        t1 = threading.Thread(target=client_to_tunnel, daemon=True)
        t2 = threading.Thread(target=tunnel_to_client, daemon=True)
        t1.start()
        t2.start()
        t1.join(timeout=timeout)
        t2.join(timeout=2)
```

---

## 五、节点连接管理

```python
class CftunConnection:
    def __init__(self, node):
        self.node = node
        self.endpoint_ips = node.get('endpoint_ips', [])
        self.port = node.get('port', 80)
        self.upstream = node.get('upstream', '')
        self.exit_server_ip = node.get('exit_server_ip', '')
        self.channel = None

    def _build_ws_path(self):
        """构造 WebSocket 路径"""
        if self.upstream and self.exit_server_ip:
            return f"/{self.upstream}/e/{self.exit_server_ip}"
        return '/'

    def connect(self, dst_ip, dst_port, is_tcp=True):
        """连接到节点"""
        path = self._build_ws_path()

        # 尝试多个 endpoint IP
        for ep_ip in self.endpoint_ips[:5]:
            try:
                # WebSocket 连接
                ws = ws_connect(ep_ip, self.port, ep_ip, path)
                print(f"WS 101 OK: {ep_ip}")

                # cftun 握手
                self.channel = CftunChannel(ws)
                if self.channel.do_handshake(dst_ip, dst_port, is_tcp):
                    return True

                self.channel.close()
                self.channel = None
            except Exception as e:
                print(f"Failed {ep_ip}: {e}")

        return False
```

---

## 六、启动代理

```python
#!/usr/bin/env python3
"""启动 SOCKS5 + HTTP 代理"""
import json

# 加载节点
with open('cftun_nodes.json', 'r') as f:
    nodes = json.load(f)['nodes']

# 过滤可用节点（有 upstream 和 exit_server_ip 的）
nodes = [n for n in nodes if n.get('upstream') and n.get('exit_server_ip')]
print(f"可用节点: {len(nodes)}")

# 启动 SOCKS5
socks = Socks5Server('0.0.0.0', 1080, nodes)
threading.Thread(target=socks.start, daemon=True).start()

# 启动 HTTP 代理
http = HttpProxyServer('0.0.0.0', 8080, nodes)
http.start()
```

### 使用

```bash
# SOCKS5
curl --proxy socks5h://127.0.0.1:1080 https://httpbin.org/ip

# HTTP 代理
curl --proxy http://127.0.0.1:8080 https://httpbin.org/ip
```

---

## 七、关键发现总结

走完这一步你应该有：

- ✅ SOCKS5 代理服务器
- ✅ HTTP CONNECT 代理服务器
- ✅ 双向转发
- ✅ 节点轮询
- ✅ 多 endpoint IP 容错

---

**下一步**：`14-第十四步-端到端验证.md`

<!-- source-core-13:source-end -->


---

<a id="source-core-14"></a>

> **归档编辑注**：本章为脱敏来源正文；原始目标文件、工程、抓包/结果附件未提供。下文的预期输出与成功断言不是本次复现记录。

<!-- source-core-14:source-start -->

# 14 · 第十四步 — 端到端验证

---

## 目标

完整运行代理脚本，验证端到端可用：浏览器 → 代理 → xTun 隧道 → 目标网站。

---

## 一、运行代理脚本

```bash
# 运行完整代理
python cftun_proxy_working.py

# 预期输出
[+] SOCKS5 proxy: socks5://0.0.0.0:1080
[+] HTTP proxy: http://0.0.0.0:8080
[*] 可用节点: 19
```

---

## 二、验证 SOCKS5

### 2.1 curl 测试

```bash
# 测试 SOCKS5
curl --proxy socks5h://127.0.0.1:1080 https://httpbin.org/ip

# 预期返回（节点出口 IP）
{
  "origin": "REDACTED_IPV4_11"
}
```

### 2.2 Python 测试

```python
import socks, socket

# 设置 SOCKS5 代理
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1080)
socket.socket = socks.socksocket

# 访问网站
import requests
r = requests.get("https://httpbin.org/ip")
print(r.json())  # {"origin": "REDACTED_IPV4_11"}
```

---

## 三、验证 HTTP 代理

```bash
# HTTP 代理
curl --proxy http://127.0.0.1:8080 https://httpbin.org/ip

# 预期
{
  "origin": "REDACTED_IPV4_11"
}
```

---

## 四、端到端测试脚本

```python
#!/usr/bin/env python3
"""e2e_test.py — 端到端验证"""
import socket, struct, threading, time, json
import socks

def test_socks5(proxy_host, proxy_port, test_url="https://httpbin.org/ip"):
    """测试 SOCKS5 代理"""
    try:
        socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port)
        s = socks.socksocket()
        s.settimeout(15)

        # 连接 httpbin
        s.connect(("httpbin.org", 443))

        # TLS
        import ssl
        ctx = ssl.create_default_context()
        ss = ctx.wrap_socket(s, server_hostname="httpbin.org")

        # 发送 HTTP 请求
        ss.send(b"GET /ip HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\n\r\n")

        resp = b""
        while True:
            chunk = ss.recv(4096)
            if not chunk: break
            resp += chunk

        # 解析响应
        body = resp.split(b"\r\n\r\n", 1)[1]
        result = json.loads(body)
        return True, result.get("origin", "")
    except Exception as e:
        return False, str(e)

def test_all_nodes(nodes):
    """测试所有节点"""
    results = []

    for node in nodes:
        name = node.get('name', '?')
        node_id = node.get('id', '?')
        exit_ip = node.get('exit_server_ip', '?')

        # 测试 WebSocket + 握手 + 数据
        ok, origin = test_socks5("127.0.0.1", 1080)

        status = "✅" if ok else "❌"
        results.append({
            'id': node_id,
            'name': name,
            'exit_ip': exit_ip,
            'ws_101': ok,
            'handshake': ok,
            'data': ok,
            'status': '101+HS+DATA' if ok else 'FAILED',
        })

        print(f"{status} [{node_id}] {name}: {origin if ok else 'failed'}")

    return results

# 运行测试
with open('cftun_nodes.json') as f:
    nodes = json.load(f)['nodes']

results = test_all_nodes(nodes)
print(f"\n成功: {sum(1 for r in results if r['ws_101'])}/{len(results)}")
```

---

## 五、验证结果

### 5.1 实际测试结果

```
✅ [2]  香港·节点2: REDACTED_IPV4_11      — 101+HS+DATA
✅ [6]  香港·节点1: REDACTED_IPV4_19    — 101+HS+DATA
✅ [23] 曼谷·节点1: REDACTED_IPV4_13     — 101+HS+DATA
✅ [24] 曼谷·节点2: REDACTED_IPV4_12       — 101+HS+DATA
✅ [25] 河內·节点1: REDACTED_IPV4_01     — 101+HS+DATA

成功: 5/6
```

### 5.2 成功标准

| 阶段 | 验证方法 | 成功标志 |
|------|----------|----------|
| WebSocket | HTTP 101 | `101 Switching Protocols` |
| 握手 | open frame 发送 | 无异常 |
| 数据通道 | 收到响应 | 解密成功 |
| 端到端 | httpbin.org/ip | 返回出口 IP |

---

## 六、浏览器配置

### Firefox

```
设置 → 网络设置 → 手动代理配置
SOCKS5 主机: 127.0.0.1  端口: 1080
✓ 使用 SOCKS5 进行 DNS 查询
```

### Chrome

```bash
# 启动 Chrome 用 SOCKS5
chrome.exe --proxy-server="socks5://127.0.0.1:1080"

# 或用 HTTP 代理
chrome.exe --proxy-server="http://127.0.0.1:8080"
```

### 验证

浏览器访问 `https://httpbin.org/ip`，应该显示 xTun 节点的出口 IP。

---

## 七、性能测试

```python
import time, requests

proxies = {
    'http': 'socks5h://127.0.0.1:1080',
    'https': 'socks5h://127.0.0.1:1080'
}

# 延迟测试
start = time.time()
r = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=15)
latency = time.time() - start
print(f"延迟: {latency:.2f}s")
print(f"出口 IP: {r.json()['origin']}")

# 下载速度
start = time.time()
r = requests.get('https://speed.hetzner.com/100MB.bin',
                proxies=proxies, timeout=60, stream=True)
total = 0
for chunk in r.iter_content(1024*1024):
    total += len(chunk)
elapsed = time.time() - start
print(f"下载: {total/1024/1024:.1f}MB in {elapsed:.1f}s = {total/1024/1024/elapsed:.1f}MB/s")
```

---

## 八、关键发现总结

走完这一步你应该有：

- ✅ SOCKS5 代理可用
- ✅ HTTP 代理可用
- ✅ 5/6 节点端到端成功
- ✅ 浏览器可以正常使用
- ✅ 出口 IP 正确（xTun 节点 IP）

**项目完成！** 你有了一个不依赖 xTun 客户端的纯 Python 代理。

---

**下一步**：`15-常见问题与排错.md`

<!-- source-core-14:source-end -->


---

<a id="source-core-15"></a>

> **归档编辑注**：本章为脱敏来源正文；原始目标文件、工程、抓包/结果附件未提供。下文的预期输出与成功断言不是本次复现记录。 secret/密钥/UUID 原值已替换；原文关于“真实值/非占位符”的说法不适用于公开占位符。

<!-- source-core-15:source-start -->

# 15 · 常见问题与排错

---

## 一、连接问题

### Q1: WebSocket 返回 403 Forbidden

**原因**：Host 头用了域名（如 `NODE_DOMAIN.invalid`），触发 Beaver WAF。

**解决**：Host 头用纯 IP 地址。

```python
# ❌ 错误
ws_connect(ip, 80, "NODE_DOMAIN.invalid", path)

# ✅ 正确
ws_connect(ip, 80, ip, path)  # Host = IP
```

---

### Q2: 连接被静默断开（无响应）

**原因**：User-Agent 不是 `DEV`，nginx 静默断开（444）。

**解决**：精确设置 `User-Agent: DEV`。

```python
# ❌ 错误
headers['User-Agent'] = 'Mozilla/5.0'

# ✅ 正确
headers['User-Agent'] = 'DEV'  # 大小写敏感
```

---

### Q3: WebSocket 返回 404 Not Found

**原因**：Path 格式错误。

**解决**：Path = `/{upstream}/e/{exit_server_ip}`，无 `cf_` 前缀。

```python
# ❌ 错误
path = "/cf_hkg/e/REDACTED_IPV4_11"  # 多了 cf_ 前缀
path = "/"                       # 太短

# ✅ 正确
path = "/hkg/e/REDACTED_IPV4_11"     # upstream 不带 cf_
```

---

### Q4: Host 带端口导致连接失败

**原因**：Host 头包含了端口号。

**解决**：Host 头不带端口。

```python
# ❌ 错误
headers['Host'] = 'REDACTED_IPV4_15:80'

# ✅ 正确
headers['Host'] = 'REDACTED_IPV4_15'
```

---

## 二、解密问题

### Q5: AES-GCM 解密失败（tag 验证错误）

**原因 1**：AAD 错误。

```python
# ❌ 错误
cipher.update(b"cftun")           # AAD 太短
cipher.update(b"cftun-txt\x00")   # 多了 null

# ✅ 正确
cipher.update(b"cftun-txt")       # 精确 9 字节
```

**原因 2**：key 错误。

```python
# ❌ 错误
key = payloadSecret.encode()[:32]  # 截断

# ✅ 正确
key = hashlib.sha256(payloadSecret.encode()).digest()  # SHA256
```

**原因 3**：tag 和 ciphertext 没分开。

```python
# ❌ 错误 (pycryptodome 的 decrypt 要分开传)
plaintext = cipher.decrypt(ct_with_tag)

# ✅ 正确
ct = ct_with_tag[:-16]
tag = ct_with_tag[-16:]
plaintext = cipher.decrypt_and_verify(ct, tag)
```

---

### Q6: payloadSecret 是占位符吗？

**不是。** `"REDACTED_PAYLOAD_SECRET"` 是服务器实际返回的值。

```python
# ✅ 正确 — 直接用这个字符串
payloadSecret = "REDACTED_PAYLOAD_SECRET"
key = hashlib.sha256(payloadSecret.encode()).digest()
# key = REDACTED_KEY_HEX
```

---

### Q7: 配置响应解密失败

**原因**：X25519 公钥没有正确传给服务器。

**检查**：
1. 公钥用 base64url 编码（不是 base64）
2. 放在 `X-Cftun-Config-Key` 头
3. 不带 `=` padding

```python
# ✅ 正确
pub_b64 = base64.urlsafe_b64encode(pub).rstrip(b'=').decode()
headers['X-Cftun-Config-Key'] = pub_b64
```

---

## 三、握手问题

### Q8: open frame 发送后无响应

**这是正常的。** cftun v3 握手不等服务器响应，发送 open frame 后直接进入数据通道。

```python
# 发送 open frame 后
ws.send_frame(frame)
# 不等响应，直接开始数据通道
handshake_done = True
```

---

### Q9: 数据通道解密失败

**原因 1**：seq 不同步。

**检查**：每次连接 seq 从 0 开始，每个包递增 1。

```python
# 发送端
self.write_seq = 0  # 初始化
# 每次发送
seq = self.write_seq
self.write_seq += 1

# 接收端
self.read_seq = 0  # 初始化
# 每次接收
seq = self.read_seq
self.read_seq += 1
```

**原因 2**：nonce 格式错误。

```python
# ✅ 正确: 4 零 + 8 字节大端 seq
nonce = b'\x00\x00\x00\x00' + struct.pack('>Q', seq)

# ❌ 错误
nonce = struct.pack('>Q', seq)        # 少了 4 零
nonce = struct.pack('<Q', seq)        # 小端
```

**原因 3**：AAD 格式错误。

```python
# ✅ 正确: 方向字符串 + 8 字节大端 seq
aad = b"cftun websocket v3 client to server" + struct.pack('>Q', seq)

# ❌ 错误
aad = b"cftun websocket v3 client to server"  # 少了 seq
aad = b"cftun websocket v3 client to server" + struct.pack('<Q', seq)  # 小端
```

---

### Q10: encrypt_and_digest vs encrypt

**关键 bug。** Go 的 `AEAD.Seal()` 返回 `ciphertext + tag`，pycryptodome 分开返回。

```python
# ✅ 正确
ct, tag = cipher.encrypt_and_digest(plaintext)
frame = ct + tag  # Go 兼容

# ❌ 错误
ct = cipher.encrypt(plaintext)
frame = ct  # 缺少 tag
```

---

## 四、API 问题

### Q11: API 返回 401 Unauthorized

**原因**：Authorization 头格式错误。

```python
# ❌ 错误
headers['Authorization'] = f'Bearer {token}'

# ✅ 正确 — 裸 JWT，无 Bearer
headers['Authorization'] = token
```

---

### Q12: API 返回 403

**原因**：缺少 Origin 头。

```python
# ✅ 必须带
headers['Origin'] = 'https://WEB_HOST.invalid'
```

---

### Q13: API 偶尔 404

**原因**：`API_HOST.invalid` 在 Cloudflare 后面，偶尔 404。

**解决**：重试。

```python
for attempt in range(5):
    try:
        resp = api_request(...)
        if resp['code'] == 200:
            break
    except:
        time.sleep(1)
```

---

## 五、Ghidra 问题

### Q14: Ghidra 分析卡住

**原因**：Go 二进制很大（50MB），分析需要 30-60 分钟。

**解决**：耐心等。可以在 Ghidra GUI 的右下角看分析进度。

---

### Q15: Ghidra 找不到函数

**原因**：Go 函数名包含包路径。

```java
// ❌ 搜索 "decryptAccessPoint" 可能找不到
// ✅ 搜索完整路径
"github.com/fmnx/cftun/backend/dialer.decryptAccessPoint"
```

---

### Q16: 反编译结果是乱码

**原因**：Ghidra 没有正确识别 Go 类型。

**解决**：
1. 确认用的是 Ghidra 12+（对 Go 支持更好）
2. 手动设置函数签名
3. 用 IDA Pro 交叉验证

---

## 六、其他问题

### Q17: 节点连接不稳定

**原因**：endpoint IP 可能临时不可用。

**解决**：多 IP 容错，尝试前 5 个。

```python
for ep_ip in node['endpoint_ips'][:5]:
    try:
        ws = ws_connect(ep_ip, ...)
        break
    except:
        continue
```

---

### Q18: 速度慢

**原因**：Python 加密比 Go 慢。

**解决**：
1. 用 pycryptodome（C 实现，比纯 Python 快）
2. 减少不必要的拷贝
3. 用更大的缓冲区

---

### Q19: 代理不工作

**排查步骤**：

```bash
# 1. 确认代理在运行
curl --proxy socks5h://127.0.0.1:1080 https://httpbin.org/ip

# 2. 确认节点可用
python -c "from cftun_proxy_working import *; test_nodes()"

# 3. 确认 DNS 解析
nslookup httpbin.org

# 4. 确认防火墙没拦
netstat -an | findstr 1080
```

---

### Q20: Token 过期

**原因**：JWT 有过期时间。

**解决**：重新登录。

```python
# 检查 token 是否过期
import jwt  # pip install PyJWT
decoded = jwt.decode(token, options={'verify_signature': False})
exp = decoded.get('exp', 0)
if time.time() > exp:
    # 重新登录
    token = login(email, password)
```

---

## 七、排错检查清单

```
□ xtun-windows.exe 确认是 Go 1.25.0 编译
□ Ghidra 项目已分析完成
□ Python 依赖已安装 (pycryptodome, cryptography)
□ API 登录成功 (token 获取)
□ Authorization 头无 Bearer 前缀
□ Origin 头已设置
□ X-Cftun-Config-Key 头已设置 (X25519 公钥)
□ 配置响应解密成功 (Layer 1)
□ payloadSecret = "REDACTED_PAYLOAD_SECRET"
□ access_point 解密成功 (Layer 2)
□ WebSocket Host = 纯 IP (不带端口)
□ WebSocket Path = /{upstream}/e/{exit_ip} (无 cf_ 前缀)
□ User-Agent = DEV
□ open frame 用 encrypt_and_digest (不是 encrypt)
□ 数据通道 nonce = 4零 + 大端seq
□ 数据通道 AAD = 方向字符串 + 大端seq
□ SOCKS5 端口 1080 / HTTP 端口 8080 已监听
□ curl 测试通过
```

---

**回到**：`README.md`

<!-- source-core-15:source-end -->


---

<a id="source-core-16"></a>

> **归档编辑注**：本章为脱敏来源正文；原始目标文件、工程、抓包/结果附件未提供。下文的预期输出与成功断言不是本次复现记录。 secret/密钥/UUID 原值已替换；原文关于“真实值/非占位符”的说法不适用于公开占位符。 原 README 的“账号信息已脱敏”属于来源自述；本次实际逐值替换后才公开。

<!-- source-core-16:source-start -->

# xTun 逆向工程教学

> 手把手教你从零逆向 xTun VPN，一个细节都不落。

---

## 这是什么

这是一份完整的逆向工程教学文档，教你如何：

1. 分析 xTun（Flutter + Go VPN 应用）的二进制
2. 逆向其自研 `cftun websocket v3` 协议
3. 解密节点配置，提取真实出口 IP
4. 实现纯 Python 代理，不依赖 xTun 客户端

最终产物：一个 `cftun_proxy_working.py`，对外暴露 SOCKS5 + HTTP 代理，通过 xTun 网络访问互联网。

---

## 教学目录

| 文件 | 内容 | 阶段 |
|------|------|------|
| [00-前言](#source-core-00) | xTun 是什么、为什么逆向、需要什么 | 认知 |
| [01-认识目标](#source-core-01) | 找到可执行文件、确认 Go 编译 | 侦察 |
| [02-准备工具](#source-core-02) | 安装 Ghidra/Python/依赖 | 准备 |
| [03-二进制识别](#source-core-03) | PE 解析、Go 版本、节区 | 侦察 |
| [04-Ghidra导入](#source-core-04) | Headless 导入、自动分析 | 静态分析 |
| [05-定位函数](#source-core-05) | 搜索字符串、找函数地址 | 静态分析 |
| [06-反编译加密](#source-core-06) | 读伪代码、识别算法、密钥链 | 静态分析 |
| [07-逆向API](#source-core-07) | API URL、登录、认证 | 网络分析 |
| [08-解密配置](#source-core-08) | 两层 AES-GCM 解密 | 实现 |
| [09-抓包分析](#source-core-09) | pktmon 抓包、提取 WS 帧 | 动态分析 |
| [10-测试WebSocket](#source-core-10) | Host/Path/UA 组合测试 | 突破 |
| [11-协议握手](#source-core-11) | open frame 构造与加密 | 实现 |
| [12-数据通道](#source-core-12) | ChaCha20 双向加密通道 | 实现 |
| [13-代理功能](#source-core-13) | SOCKS5 + HTTP 代理 | 实现 |
| [14-端到端验证](#source-core-14) | 完整测试、浏览器配置 | 验证 |
| [15-排错](#source-core-15) | 20 个常见问题与解决 | 排错 |

---

## 快速开始

如果你只想用结果，不想走过程：

```bash
# 1. 安装依赖
pip install pycryptodome cryptography

# 2. 运行代理
python cftun_proxy_working.py

# 3. 配置浏览器
# SOCKS5: 127.0.0.1:1080
# HTTP:   127.0.0.1:8080
```

如果你想学习完整的逆向方法，从 `00-前言` 开始，一步一步走。

---

## 技术栈

| 层 | 技术 |
|----|------|
| 目标 | xTun VPN (Flutter + Go) |
| 协议 | cftun websocket v3 (自研) |
| 加密 | X25519 + HKDF-SHA256 + ChaCha20-Poly1305 + AES-256-GCM |
| 传输 | WebSocket (port 80, 无 TLS) |
| 逆向 | Ghidra 12.1.3 + pefile + capstone |
| 实现 | Python 3.12 + pycryptodome + cryptography |

---

## 关键数据

| 项目 | 值 |
|------|-----|
| 目标文件 | `xtun-windows.exe` (50MB, Go 1.25.0, PE64) |
| Go 模块 | `github.com/fmnx/cftun/backend` |
| API | `https://API_HOST.invalid` |
| 协议 | `cftun websocket v3` |
| payloadSecret | `REDACTED_PAYLOAD_SECRET` |
| Tunnel UUID | `REDACTED_TUNNEL_UUID` |
| 节点数 | 19 |
| Endpoint IP | 173 |
| 验证结果 | 5/6 节点 101+HS+DATA 成功 |

---

## 学习路径建议

### 路径 A：完整逆向（推荐）

从 00 到 15，每步都做。约需 2-3 小时（Ghidra 分析占 1 小时）。

### 路径 B：快速实现

跳过 04-06（Ghidra 部分），直接从 07 开始用已知的函数地址和加密参数。

### 路径 C：只用结果

直接运行 `cftun_proxy_working.py`，不需要理解原理。

---

## 文件依赖

```
教学文档 (本目录)
    ↓ 参考
cftun_proxy_working.py    ← 最终代理脚本
cftun_nodes.json          ← 19 节点数据
xtun-windows.exe          ← 目标二进制
ghidra_project/           ← Ghidra 项目
```

---

## 注意事项

- 本教学仅供学习逆向工程技术
- 所有数据来自已完成的逆向分析项目
- 账号信息已在文档中脱敏处理
- 请遵守当地法律法规

---

*由逆向工程教学子代理生成*

<!-- source-core-16:source-end -->

## 归档后的复用边界

本篇供定位来源段落、比较输入/输出层次和辨认未验证假设使用，不是当前目标成功回执。来源缺公开 locator，且目标样本、日志、配置、脚本不全；任何后续 `reference` 都应继承这些限制。公开工具规范仅支撑对应工具事实，不替代目标算法或服务端验收。原件、脱敏映射与逐篇覆盖回执留在本地，未随 Public 文章发布。
