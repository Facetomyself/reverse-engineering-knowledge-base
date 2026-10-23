---
schema_version: 2
id: xtun-go-reverse-supplement-archive
document_type: archive
original_date: unknown
archived_date: '2026-10-23'
scope:
  targets: [xtun, cftun]
  client: native
  version: unknown
  observed_at: unknown
sources:
  - id: supplement-a1
    ref: null
    basis: source-report
    citation: 'A1 · 补充 — APK 完整拆解分析'
    reason: 原始补充教学仅有本地 Markdown，未提供可公开定位的原始发布链接；作者身份未知。
  - id: supplement-a2
    ref: null
    basis: source-report
    citation: 'A2 · 补充 — SO 文件与 ELF 分析'
    reason: 原始补充教学仅有本地 Markdown，未提供可公开定位的原始发布链接；作者身份未知。
  - id: supplement-a3
    ref: null
    basis: source-report
    citation: 'A3 · 补充 — 十六进制分析'
    reason: 原始补充教学仅有本地 Markdown，未提供可公开定位的原始发布链接；作者身份未知。
  - id: supplement-a4
    ref: null
    basis: source-report
    citation: 'A4 · 补充 — 内存分析'
    reason: 原始补充教学仅有本地 Markdown，未提供可公开定位的原始发布链接；作者身份未知。
  - id: supplement-a5
    ref: null
    basis: source-report
    citation: 'A5 · 补充 — Frida 动态 Hook 完整教学'
    reason: 原始补充教学仅有本地 Markdown，未提供可公开定位的原始发布链接；作者身份未知。
  - id: supplement-a6
    ref: null
    basis: source-report
    citation: 'A6 · 补充 — 加壳检测与脱壳'
    reason: 原始补充教学仅有本地 Markdown，未提供可公开定位的原始发布链接；作者身份未知。
  - id: supplement-a7
    ref: null
    basis: source-report
    citation: 'A7 · 补充 — IDA Pro 交叉验证'
    reason: 原始补充教学仅有本地 Markdown，未提供可公开定位的原始发布链接；作者身份未知。
  - id: supplement-a8
    ref: null
    basis: source-report
    citation: 'A8 · 补充 — websocket 类型节点：从 86 次失败到完全攻破'
    reason: 原始补充教学仅有本地 Markdown，未提供可公开定位的原始发布链接；作者身份未知。
source_completeness: partial
tags: [golang, native, apk, elf, pe, frida, abi, evidence-boundary, source-archive]
---

# xTun / cftun Go 逆向补充教学来源归档

本文合并保留《教学补充文档》中的 A1–A8 八篇 Markdown。作者身份与原始发布链接未知；原日期仅 A8 明写 2026-09-18，其他篇未明确，不将该日期扩展为整批观测窗口。来源谈及 Android APK/ARM64 SO、Windows AMD64 PE、Go 1.25.0 与应用版本 1.0.9，均为作者自述，未获得对应二进制和版本证据。

## 清洗与完整性说明

- 路线为有缺口的来源 archive，不是可运行教程或本次逆向报告。按原顺序保留八篇目标、章节、表格、代码、预期输出及结论，不静默修正作者原话；编辑说明与原文分开。
- 真实节点 IP、出口地址、虚拟 IP、DomainPool/服务域名、Tunnel/节点标识、实际 secret/key 及其 hex/转义副本、私有工程路径替换为 `{TYPE_PLACEHOLDER}`；同类值按稳定别名区分，相同值复用别名，反转 Host 的编号对应虚拟 IP 编号。占位符不是可用配置；脱敏后示例可能不再满足原来的字节长度、语法或算法关系，禁止把它们当测试向量。
- 公共工具链接、通用函数名、格式字段、算法、示意 PE VA/偏移、标准 Android 路径等保留；它们不是本次环境配置。来源中的相对回链按合并文章重映射，不猜造来源发布 URL。
- 随包只有 Markdown：没有 APK/PE/SO、IDA/Ghidra 项目、内存 dump、Frida 原始日志、DNS/pcap/ETL、配置密文/明文文件或其自述脚本附件；正文中的脚本是文本而不是附件交付。未补造图片、二进制、数据或缺失结果。
- ZIP/成员字节校验通过不等于技术完整；本归档 `source_completeness: partial`。原始包和逐成员原件保持不动，未执行来源代码或指令，未访问来源目标网络。本轮检查只覆盖文档结构、保留范围、脱敏和公开规范窄对照。

## 补充教学导航

- [A1 · APK、Flutter/Dart AOT 与 Go Native 分层](#source-supplement-a1)
- [A2 · ELF/SO Section/Segment、导出与地址换算](#source-supplement-a2)
- [A3 · 十六进制、端序、PE RVA/VA/文件偏移](#source-supplement-a3)
- [A4 · Go 内存、调试与运行期证据边界](#source-supplement-a4)
- [A5 · Frida Go Hook、ABI 与运行期读取限制](#source-supplement-a5)
- [A6 · 壳识别、熵启发式与未加壳 Go 的区别](#source-supplement-a6)
- [A7 · Ghidra/IDA/Capstone 交叉核查与地址边界](#source-supplement-a7)
- [A8 · 两种传输连接模式、历史假设冲突与作者成功自述](#source-supplement-a8)

## 来源正文

以下每篇的“编辑说明”属于本次清洗；其后的一级标题起为该篇来源正文。原文中的“确认”“✅”“成功”“最可靠”等仍仅是来源措辞。

<a id="source-supplement-a1"></a>

> **编辑说明（A1；source-report）**：本篇的文件大小、包名、版本、架构及“全部协议逻辑在 Go 层”“任一平台等价”等均是来源陈述或预期输出；未随包提供 APK/SO/PE，未对平台差异、桥接边界、签名或 Flutter 工具兼容性复核。源码中泛化的 APK/签名/Flutter 描述不能替代当前样本判定；保留原文措辞，不升级为本轮发现。

# A1 · 补充 — APK 完整拆解分析

---

## 目标

把 `xtun.apk` 从头到尾拆开，搞清楚每一层里装了什么，找到逆向的核心目标文件。

---

## 一、APK 是什么

APK（Android Package）本质是一个 **ZIP 压缩包**，改了扩展名。你可以直接用任何 ZIP 工具打开它。

### 1.1 APK 内部结构

```
xtun.apk (ZIP)
├── META-INF/               ← 签名信息（MANIFEST.MF, CERT.SF, CERT.RSA）
├── AndroidManifest.xml     ← 应用清单（二进制 XML，需要工具解码）
├── classes.dex             ← Dalvik 字节码（Java/Kotlin 代码编译产物）
├── classes2.dex            ← 第二个 DEX（方法数超 65535 时会分包）
├── lib/                    ← 原生 SO 库（按 CPU 架构分目录）
│   ├── arm64-v8a/          ← 64 位 ARM（主流）
│   │   ├── libapp.so       ← Flutter Dart AOT 编译产物（UI 层）
│   │   ├── libct-go.so     ← Go 编译的 VPN 核心（协议逻辑）
│   │   └── libflutter.so   ← Flutter 引擎
│   └── armeabi-v7a/        ← 32 位 ARM（兼容旧设备）
├── assets/                 ← 原始资源文件（字体、配置、Flutter 资源）
│   └── flutter_assets/     ← Flutter 资源包
├── res/                    ← 编译后的资源（布局、图片、字符串）
└── resources.arsc          ← 资源索引表
```

### 1.2 验证：直接解压

```bash
# 用 unzip 直接解压看结构
mkdir xtun_unzip
cd xtun_unzip
unzip ../xtun.apk

# 看目录树
find . -maxdepth 2 -type f | head -30
```

预期输出（节选）：

```
./META-INF/MANIFEST.MF
./META-INF/CERT.SF
./META-INF/CERT.RSA
./AndroidManifest.xml
./classes.dex
./lib/arm64-v8a/libapp.so
./lib/arm64-v8a/libct-go.so
./lib/arm64-v8a/libflutter.so
./res/drawable/...
./assets/flutter_assets/...
```

**要点**：直接 unzip 能看到文件，但 `AndroidManifest.xml` 是二进制格式，直接打开是乱码。需要 apktool 解码。

---

## 二、用 apktool 解包

apktool 能把 APK 完全解码，包括二进制 XML → 可读 XML、资源反编译、DEX → smali。

### 2.1 安装 apktool

```bash
# 下载 apktool
# https://ibotpeaches.github.io/Apktool/
# 放到你的工具目录，例如:
# apktool_2.9.3.jar

# 验证
java -jar apktool_2.9.3.jar --version
# 预期: 2.9.3
```

### 2.2 解包命令

```bash
# 解包 xtun.apk
java -jar apktool_2.9.3.jar d xtun.apk -o xtun_apktool

# 参数:
#   d          = decode（解包）
#   -o         = 输出目录
#   xtun.apk   = 输入文件
```

### 2.3 输出目录结构

```
xtun_apktool/
├── AndroidManifest.xml     ← 已解码的可读 XML！
├── apktool.yml             ← apktool 元数据（版本、压缩方式等）
├── lib/
│   ├── arm64-v8a/
│   │   ├── libapp.so       ← Flutter Dart AOT (7.6MB)
│   │   ├── libct-go.so     ← Go VPN 核心 (8.5MB) ← 逆向目标
│   │   └── libflutter.so   ← Flutter 引擎 (~10MB)
│   └── armeabi-v7a/
│       └── ...
├── assets/
│   └── flutter_assets/
│       ├── AssetManifest.json
│       ├── FontManifest.json
│       └── fonts/
├── res/                    ← 反编译后的资源
│   ├── drawable/
│   ├── layout/
│   ├── values/
│   │   └── strings.xml     ← 字符串资源（可能有 API URL）
│   └── xml/
├── smali/                  ← DEX 反编译为 smali 代码
│   └── com/
│       └── xtun/
│           └── ...
└── original/               ← 原始签名文件
    └── META-INF/
```

### 2.4 每个目录的含义

| 目录/文件 | 逆向价值 | 说明 |
|-----------|---------|------|
| `AndroidManifest.xml` | ⭐⭐⭐ | 权限、组件、VPN 配置，必看 |
| `lib/arm64-v8a/libct-go.so` | ⭐⭐⭐⭐⭐ | Go VPN 核心，协议逻辑全在这里 |
| `lib/arm64-v8a/libapp.so` | ⭐⭐ | Flutter UI，Dart AOT 编译，逆向难度高 |
| `smali/` | ⭐⭐ | Java 层代码，看 Flutter 和 Go 的桥接调用 |
| `res/values/strings.xml` | ⭐ | 可能藏有 API URL 或配置字符串 |
| `assets/flutter_assets/` | ⭐ | Flutter 资源，字体和配置 |
| `original/META-INF/` | ⭐ | 签名信息，验证是否被修改过 |

---

## 三、用 jadx 反编译 DEX

jadx 把 `classes.dex` 反编译为可读的 Java 源码（比 smali 好读得多）。

### 3.1 安装 jadx

```bash
# 下载 jadx
# https://github.com/skylot/jadx/releases
# 解压后有 bin/jadx 和 bin/jadx-gui
```

### 3.2 GUI 方式打开

```bash
# 启动 jadx GUI
jadx-gui xtun.apk
```

GUI 中：
1. 左侧树形结构显示包层级
2. 展开 `com.xtun` 看应用代码
3. `Ctrl+Shift+F` 全局搜索字符串
4. 双击类名跳转到源码

### 3.3 命令行批量反编译

```bash
# 反编译到目录
jadx -d xtun_jadx xtun.apk

# 输出:
# xtun_jadx/
#   sources/    ← Java 源码
#   resources/  ← 资源文件
```

### 3.4 搜索关键内容

```bash
# 搜索 API URL
grep -r "{API_DOMAIN_SEARCH_PREFIX}" xtun_jadx/sources/

# 搜索 cftun 相关
grep -r "cftun" xtun_jadx/sources/

# 搜索 Go 桥接调用
grep -r "libct-go" xtun_jadx/sources/
grep -r "System.loadLibrary" xtun_jadx/sources/

# 搜索 WebSocket
grep -r "websocket" xtun_jadx/sources/
```

### 3.5 xTun 的 Java 层结构

Flutter + Go 应用的 Java 层通常很薄：

```
com.xtun/
├── MainActivity.java          ← Flutter 入口 Activity
├── MainApplication.java       ← Application 初始化
├── vpn/
│   └── VpnService.java        ← Android VPN Service（系统级 TUN 接口）
└── bridge/
    └── GoBridge.java           ← JNI 桥接：Java ↔ Go（调用 libct-go.so）
```

**关键**：Flutter 应用的业务逻辑不在 Java 层，而在 `libapp.so`（Dart 代码）。Java 层只负责：
- 启动 Flutter 引擎
- 提供 VPN Service（创建 TUN 接口）
- JNI 桥接到 Go 层

---

## 四、识别 Flutter + Go 架构

### 4.1 怎么判断是 Flutter 应用

```bash
# 特征 1: libflutter.so 存在
ls xtun_apktool/lib/arm64-v8a/libflutter.so
# 存在 → Flutter

# 特征 2: libapp.so 存在
ls xtun_apktool/lib/arm64-v8a/libapp.so
# 存在 → Flutter AOT 编译

# 特征 3: flutter_assets 目录
ls xtun_apktool/assets/flutter_assets/
# 存在 → Flutter

# 特征 4: DEX 中有 FlutterActivity
grep -r "FlutterActivity" xtun_apktool/smali/
```

### 4.2 怎么判断有 Go 组件

```bash
# 特征 1: libct-go.so 存在（go 在文件名中）
ls xtun_apktool/lib/arm64-v8a/libct-go.so

# 特征 2: strings 搜索 Go 运行时标记
strings xtun_apktool/lib/arm64-v8a/libct-go.so | grep "runtime.morestack"
strings xtun_apktool/lib/arm64-v8a/libct-go.so | grep "go.buildid"

# 特征 3: Go 模块路径
strings xtun_apktool/lib/arm64-v8a/libct-go.so | grep "fmnx/cftun"
```

### 4.3 三个 SO 的职责

| SO 文件 | 大小 | 语言 | 职责 | 逆向方法 |
|---------|------|------|------|----------|
| `libflutter.so` | ~10MB | C++ | Flutter 引擎（渲染、事件循环） | 通常不需要逆向 |
| `libapp.so` | ~7.6MB | Dart AOT | UI 逻辑（登录界面、节点选择、设置） | Dart snapshot 逆向（难） |
| `libct-go.so` | ~8.5MB | Go | VPN 核心（协议、加密、隧道） | Ghidra/IDA 反编译（可行） |

**逆向目标是 `libct-go.so`**，协议逻辑全在里面。`libapp.so` 只是 UI，不涉及协议细节。

---

## 五、提取 SO 文件

### 5.1 从 APK 提取

```bash
# 方法1: 从 apktool 解包结果复制
cp xtun_apktool/lib/arm64-v8a/libct-go.so .
cp xtun_apktool/lib/arm64-v8a/libapp.so .

# 方法2: 直接从 APK 解压指定文件
unzip xtun.apk lib/arm64-v8a/libct-go.so -d .
```

### 5.2 确认架构 (ELF ARM64)

```bash
# 用 file 命令
file libct-go.so

# 预期输出:
# libct-go.so: ELF 64-bit LSB shared object, ARM aarch64, version 1 (SYSV),
# dynamically linked, Go BuildID=..., not stripped
```

关键信息：
- `ELF 64-bit` → 64 位 ELF 格式
- `ARM aarch64` → ARM64 架构
- `Go BuildID=...` → Go 编译
- `not stripped` → 符号表保留（有利于逆向）

### 5.3 用 Python 解析 ELF 头

```python
#!/usr/bin/env python3
"""parse_elf.py — 解析 SO 文件的 ELF 头"""
import struct

def parse_elf(path):
    with open(path, 'rb') as f:
        # ELF Magic
        magic = f.read(4)
        assert magic == b'\x7fELF', f"不是 ELF 文件: {magic}"

        ei_class = f.read(1)[0]   # 1=32位, 2=64位
        ei_data = f.read(1)[0]    # 1=小端, 2=大端
        ei_version = f.read(1)[0]
        ei_osabi = f.read(1)[0]
        f.read(8)                  # padding

        # ELF Header (64-bit)
        e_type = struct.unpack('<H', f.read(2))[0]
        e_machine = struct.unpack('<H', f.read(2))[0]

        print(f"文件: {path}")
        print(f"  类型: {'64位' if ei_class == 2 else '32位'}")
        print(f"  字节序: {'小端' if ei_data == 1 else '大端'}")
        print(f"  ELF类型: {['无', 'REL', 'EXEC', 'DYN', 'CORE'][e_type] if e_type < 5 else hex(e_type)}")
        print(f"  架构: {hex(e_machine)}")
        # 0xB7 = ARM64 (aarch64), 0x28 = ARM (32-bit), 0x3E = x86_64
        arch_names = {0xB7: 'ARM64 (aarch64)', 0x28: 'ARM (32-bit)', 0x3E: 'x86_64'}
        print(f"         {arch_names.get(e_machine, '未知')}")

parse_elf('libct-go.so')
parse_elf('libapp.so')
```

预期输出：

```
文件: libct-go.so
  类型: 64位
  字节序: 小端
  ELF类型: DYN
  架构: 0xb7
         ARM64 (aarch64)
文件: libapp.so
  类型: 64位
  字节序: 小端
  ELF类型: DYN
  架构: 0xb7
         ARM64 (aarch64)
```

### 5.4 SO vs EXE 对比

| 属性 | libct-go.so (Android) | xtun-windows.exe (Windows) |
|------|----------------------|---------------------------|
| 格式 | ELF 64-bit | PE64 |
| 架构 | ARM64 (aarch64) | AMD64 (x86_64) |
| 类型 | 共享库 (.so) | 可执行文件 (.exe) |
| 大小 | ~8.5MB | ~50MB |
| Go 版本 | 相同 (1.25.0) | 相同 (1.25.0) |
| Go 模块 | github.com/fmnx/cftun/backend | 同左 |
| 加密逻辑 | 相同 | 相同 |
| Ghidra 分析 | 需要选 ARM64 处理器 | 需要选 x86_64 处理器 |

**同一份 Go 代码交叉编译为不同平台。** 协议逻辑完全相同，逆向任意一个平台即可。Windows 版更大是因为它包含了 Flutter 引擎和完整的 GUI 框架。

---

## 六、AndroidManifest.xml 分析

### 6.1 打开已解码的 Manifest

```bash
# apktool 解码后可以直接看
cat xtun_apktool/AndroidManifest.xml
```

### 6.2 关键信息提取

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="..."
    package="com.xtun"
    android:versionCode="9"
    android:versionName="1.0.9">

    <!-- 权限 -->
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>

    <application android:label="xTun" ...>

        <!-- Flutter 主 Activity -->
        <activity android:name=".MainActivity"
            android:launchMode="singleTop"
            android:theme="@style/LaunchTheme">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>

        <!-- VPN Service -->
        <service android:name=".vpn.XTunVpnService"
            android:permission="android.permission.BIND_VPN_SERVICE">
            <intent-filter>
                <action android:name="android.net.VpnService"/>
            </intent-filter>
        </service>

    </application>
</manifest>
```

### 6.3 逐项分析

| 字段 | 值 | 含义 |
|------|-----|------|
| `package` | `com.xtun` | 应用包名（唯一标识） |
| `versionCode` | `9` | 内部版本号 |
| `versionName` | `1.0.9` | 显示版本号 |
| `INTERNET` | 权限 | 网络访问（VPN 必须） |
| `FOREGROUND_SERVICE` | 权限 | 前台服务（VPN 服务持续运行） |
| `BIND_VPN_SERVICE` | 权限 | 绑定 VPN 服务（Android VPN API） |
| `MainActivity` | Activity | Flutter 入口，`singleTop` 防重复创建 |
| `XTunVpnService` | Service | VPN 服务，创建 TUN 接口 |

### 6.4 VPN Service 的意义

`android.net.VpnService` 是 Android 提供的 VPN API：

1. 用户授权 → 系统创建 TUN 虚拟网卡
2. xTun 的 VpnService 读取 TUN 上的流量
3. Go 层（libct-go.so）建立 WebSocket 隧道
4. 流量通过隧道转发到 xTun 节点

**逆向时不需要关心 VPN Service 本身**，它只是操作系统的接口。核心逻辑在 Go 层。

---

## 七、smali 代码阅读入门

### 7.1 smali 是什么

smali 是 Dalvik 字节码的人类可读汇编表示。apktool 解包时自动把 `classes.dex` 转为 smali。

```
smali/com/xtun/MainActivity.smali    → Java: com.xtun.MainActivity
smali/com/xtun/vpn/XTunVpnService.smali → Java: com.xtun.vpn.XTunVpnService
```

### 7.2 基本语法

```smali
# 类定义
.class public Lcom/xtun/MainActivity;
.super Lio/flutter/embedding/android/FlutterActivity;

# 方法定义
.method protected onCreate(Landroid/os/Bundle;)V
    .locals 2            # 本地变量数量

    # 调用父类方法
    invoke-super {p0, p1}, Lio/flutter/embedding/android/FlutterActivity;->onCreate(Landroid/os/Bundle;)V

    # 加载 Go 库
    const-string v0, "ct-go"
    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

    return-void
.end method
```

### 7.3 语法速查

| smali 指令 | 含义 | 示例 |
|------------|------|------|
| `invoke-virtual` | 调用实例方法 | `invoke-virtual {v0}, Ljava/lang/String;->length()I` |
| `invoke-static` | 调用静态方法 | `invoke-static {v0}, Ljava/lang/System;->loadLibrary(...)V` |
| `invoke-super` | 调用父类方法 | `invoke-super {p0}, ...->onCreate(...)V` |
| `const-string` | 加载字符串常量 | `const-string v0, "ct-go"` |
| `move-result` | 取方法返回值 | `move-result v1` |
| `iget-object` | 读取字段 | `iget-object v0, p0, Lcom/xtun/...;->field:Ljava/lang/String;` |
| `sget-object` | 读取静态字段 | `sget-object v0, Lcom/xtun/...;->INSTANCE:L...;` |

类型标记：
| 标记 | Java 类型 |
|------|-----------|
| `V` | void |
| `I` | int |
| `Z` | boolean |
| `J` | long |
| `Ljava/lang/String;` | String |
| `[B` | byte[] |

### 7.4 找关键调用

```bash
# 搜索加载 Go 库的地方
grep -r "loadLibrary" xtun_apktool/smali/
# 预期: const-string v0, "ct-go"
#       invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

# 搜索 VPN 相关
grep -r "VpnService" xtun_apktool/smali/

# 搜索 native 方法声明（Java → Go 桥接入口）
grep -r "\.method.*native" xtun_apktool/smali/
```

---

## 八、Flutter Dart 逆向简介

### 8.1 libapp.so 是什么

Flutter 应用的 Dart 代码经过 AOT (Ahead-of-Time) 编译，生成原生机器码，打包在 `libapp.so` 中。它不是标准的 ELF 可执行代码，而是 **Dart VM snapshot** 格式。

```bash
# 验证: 搜索 Dart snapshot magic
strings libapp.so | grep "kDartVmSnapshotInstructions"
strings libapp.so | grep "_kDartIsolateSnapshotInstructions"
```

### 8.2 为什么难逆向

| 挑战 | 原因 |
|------|------|
| 没有符号表 | Dart AOT 编译后函数名被 strip |
| 自定义格式 | Snapshot 格式非标准 ELF，Ghidra/IDA 无法直接反编译 |
| 混淆 | Flutter 默认会 tree-shake 和优化 |
| 对象池 | Dart 的对象分配使用内部堆，不走标准 malloc |

### 8.3 逆向工具

| 工具 | 用途 | 链接 |
|------|------|------|
| **reFlutter** | 提取 Dart snapshot，可以做运行时 hook | https://github.com/nicolo-mn/reFlutter |
| **Doldrums** | 解析 Dart snapshot 格式，恢复类名和方法签名 | https://github.com/nicolo-mn/doldrums |
| **darter** | 解析 Dart snapshot 的另一个工具 | https://github.com/aspect-build/rules_dart |
| **blutter** | 较新的 Flutter 逆向工具，支持 AOT snapshot 分析 | https://github.com/nicolo-mn/blutter |

### 8.4 基本操作

```bash
# 用 blutter 分析（如果版本兼容）
python3 blutter.py xtun_apktool/lib/arm64-v8a/

# 输出:
#   asm/          ← 反汇编（带恢复的函数名）
#   blutter_frida.js  ← Frida hook 脚本模板
#   objs.txt      ← 对象列表
#   pp.txt        ← 对象池
```

### 8.5 xTun 中需要从 Dart 层逆向的内容

| 信息 | 重要性 | 说明 |
|------|--------|------|
| API URL | 低 | 已从 Go 层和字符串搜索获得 |
| 登录逻辑 | 低 | 已通过 API 逆向获得 |
| Go 桥接调用 | 中 | Dart 通过 MethodChannel 调用 Go 函数的参数 |
| UI 文本 | 低 | 节点名称、错误消息 |

**结论**：对 xTun 来说，Dart 层逆向不是必须的。协议逻辑全在 Go 层（libct-go.so），从 Windows 的 xtun-windows.exe 逆向更方便（x86_64 + 更好的工具支持）。

---

## 九、签名和证书检查

### 9.1 META-INF 中的文件

```bash
ls xtun_apktool/original/META-INF/
```

| 文件 | 作用 |
|------|------|
| `MANIFEST.MF` | 每个文件的 SHA 哈希 |
| `CERT.SF` | 对 MANIFEST.MF 的签名摘要 |
| `CERT.RSA` | 开发者的 X.509 证书（含公钥） |

### 9.2 查看签名信息

```bash
# 用 keytool 查看证书
keytool -printcert -jarfile xtun.apk

# 或从 RSA 文件提取
keytool -printcert -file xtun_apktool/original/META-INF/CERT.RSA
```

预期输出（节选）：

```
Owner: CN=xTun, O=xTun, L=Unknown, ST=Unknown, C=Unknown
Issuer: CN=xTun, O=xTun, ...
Serial number: ...
Valid from: ... until: ...
Certificate fingerprints:
     SHA256: XX:XX:XX:...
```

### 9.3 验证签名完整性

```bash
# 用 apksigner 验证（Android SDK 工具）
apksigner verify --verbose xtun.apk

# 或用 jarsigner
jarsigner -verify -verbose xtun.apk
```

如果输出 `jar verified`，说明 APK 没有被修改过。如果你修改了任何文件并重新打包，签名会失效，需要重新签名。

### 9.4 重新签名（修改 APK 后）

```bash
# 1. 生成签名密钥
keytool -genkey -v -keystore my-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias mykey

# 2. 用 apktool 重新打包
java -jar apktool_2.9.3.jar b xtun_apktool -o xtun_modified.apk

# 3. 签名
apksigner sign --ks my-key.jks --out xtun_signed.apk xtun_modified.apk

# 4. 安装
adb install xtun_signed.apk
```

---

## 十、关键发现总结

走完这一步你应该确认：

- ✅ APK 是 ZIP 格式，包含 DEX + SO + 资源 + 签名
- ✅ xTun 架构: Flutter (libapp.so) + Go (libct-go.so) + Flutter Engine (libflutter.so)
- ✅ 逆向核心目标是 `libct-go.so`（Go VPN 核心），不是 libapp.so
- ✅ libct-go.so 是 ELF 64-bit ARM64，Go 1.25.0 编译，符号未 strip
- ✅ Java 层很薄：MainActivity (Flutter入口) + VpnService (系统接口)
- ✅ AndroidManifest.xml: 包名 com.xtun, 版本 1.0.9, VPN 权限
- ✅ Dart 层逆向不是必须的，Windows exe 更适合做协议逆向
- ✅ smali 可以找到 Go 桥接入口 (`System.loadLibrary("ct-go")`)

---

**下一步**：[A2 · SO 文件与 ELF 分析](#source-supplement-a2)

---

<a id="source-supplement-a2"></a>

> **编辑说明（A2；source-report）**：ELF Header、Section、符号和导入步骤按来源保留。Program Header/Segment 服务加载，Section 服务链接与分析，二者不是同一地址映射；ARM64 与 AMD64 的 ABI 也不能用本篇通用寄存器示例互套。基址、load bias、RVA、文件偏移须结合实际映射复核，Windows VA 不能当 Android RVA。SO/EXE 同源同逻辑是作者自述，无二进制可比对。

# A2 · 补充 — SO 文件与 ELF 分析

---

## 目标

理解 Android 平台下 xTun 的核心 SO 文件结构，掌握 ELF 格式解析，能独立分析 `libct-go.so`（Go 后端）和 `libapp.so`（Flutter UI）。

---

## 一、SO 文件是什么

### 1.1 定义

SO（Shared Object）是 Linux/Android 上的动态链接库，等价于 Windows 的 DLL。xTun 的 APK 里包含两个关键 SO：

| 文件 | 大小 | 编译语言 | 架构 | 作用 |
|------|------|----------|------|------|
| `libct-go.so` | 8.5 MB | Go | ARM64 (AArch64) | VPN 核心：协议、加密、隧道 |
| `libapp.so` | 7.6 MB | Dart (Flutter AOT) | ARM64 | UI 层：登录界面、节点选择 |

**逆向重点在 `libct-go.so`**，因为协议逻辑和加密算法都在这里。`libapp.so` 是 Flutter 的 AOT snapshot，缺少标准符号表，分析难度大且价值低。

### 1.2 ELF vs PE 格式对比

| 特征 | ELF（Linux/Android .so） | PE（Windows .exe/.dll） |
|------|------------------------|----------------------|
| Magic | `\x7fELF`（4 字节） | `MZ`（2 字节） |
| 头长度 | 64 字节（ELF64） | DOS头 + PE头 + Optional头 |
| 节区命名 | `.text`, `.rodata`, `.data` | `.text`, `.rdata`, `.data` |
| 字符串节区 | `.rodata` | `.rdata` |
| 动态链接信息 | `.dynamic` + `.dynsym` | Import Table (IAT) |
| 符号表 | `.symtab` + `.strtab` | Export Table（通常被 strip） |
| 重定位 | `.rela.dyn`, `.rela.plt` | `.reloc` |
| 可执行标记 | ELF header `e_type`=ET_DYN | PE header Characteristics |
| 解析工具 | readelf, objdump, pyelftools | pefile (Python), CFF Explorer |

### 1.3 提取 SO 文件

```bash
# 用 apktool 解包 APK
java -jar apktool_2.9.3.jar d xtun.apk -o apktool_out

# 找到 SO 文件
ls -la apktool_out/lib/arm64-v8a/
# libapp.so    — Flutter Dart AOT (UI)
# libct-go.so  — Go VPN 核心 (协议逻辑)
# libflutter.so — Flutter 引擎

# 也可以直接用 unzip（APK 就是 zip）
unzip xtun.apk -d apk_unzipped
ls apk_unzipped/lib/arm64-v8a/
```

---

## 二、ELF 头解析

### 2.1 ELF 文件整体结构

```
┌──────────────────────┐  偏移 0x00
│    ELF Header        │  64 字节（ELF64）
├──────────────────────┤
│  Program Header Table│  告诉加载器如何加载到内存
├──────────────────────┤
│       .text          │  可执行代码
│       .rodata        │  只读数据（字符串、常量）
│       .data          │  可读写全局变量
│       .dynamic       │  动态链接信息
│       .symtab        │  符号表
│       .strtab        │  字符串表
│       ...            │
├──────────────────────┤
│  Section Header Table│  节区元数据
└──────────────────────┘
```

### 2.2 用 readelf 查看 ELF 头

```bash
readelf -h apktool_out/lib/arm64-v8a/libct-go.so
```

预期输出：

```
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00
  Class:                             ELF64
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              DYN (Shared object file)
  Machine:                           AArch64
  Version:                           0x1
  Entry point address:               0x...
  Start of program headers:          64 (bytes into file)
  Start of section headers:          ... (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Number of section headers:         ...
```

### 2.3 怎么读 Magic Bytes

```
7f 45 4c 46 02 01 01 00
│  │  │  │  │  │  │  │
│  └──┴──┘  │  │  │  └── OS/ABI (0=UNIX)
│    "ELF"  │  │  └── ELF版本 (1=current)
│           │  └── 数据编码 (1=小端)
└── 0x7f    └── 类别 (2=64位)
```

| 字节 | 值 | 含义 |
|------|-----|------|
| `0x7f` | 固定 | ELF magic 前缀 |
| `45 4c 46` | "ELF" | ELF 标识 |
| `02` | 2 | ELF64（64位）；1=ELF32 |
| `01` | 1 | 小端字节序；2=大端 |

### 2.4 用 Python 解析 ELF 头

```python
#!/usr/bin/env python3
"""parse_elf_header.py — 手动解析 ELF64 头"""
import struct

def parse_elf64_header(path):
    with open(path, 'rb') as f:
        # Magic (16 bytes)
        e_ident = f.read(16)
        magic = e_ident[:4]
        assert magic == b'\x7fELF', f"不是 ELF 文件: {magic}"

        ei_class = e_ident[4]    # 1=32bit, 2=64bit
        ei_data = e_ident[5]     # 1=LE, 2=BE
        ei_version = e_ident[6]
        ei_osabi = e_ident[7]

        endian = '<' if ei_data == 1 else '>'
        bits = 64 if ei_class == 2 else 32

        # ELF64 header fields (偏移 16 开始)
        fmt = endian + 'HHIQQQIHHHHHH'
        data = f.read(struct.calcsize(fmt))
        fields = struct.unpack(fmt, data)

        e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, \
        e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, \
        e_shnum, e_shstrndx = fields

        type_names = {0: 'NONE', 1: 'REL', 2: 'EXEC', 3: 'DYN', 4: 'CORE'}
        machine_names = {0x03: 'x86', 0x3E: 'AMD64', 0xB7: 'AArch64', 0x28: 'ARM'}

        print(f"=== ELF Header: {path} ===")
        print(f"  Class:       ELF{bits}")
        print(f"  Endian:      {'Little' if ei_data == 1 else 'Big'}")
        print(f"  Type:        {type_names.get(e_type, hex(e_type))}")
        print(f"  Machine:     {machine_names.get(e_machine, hex(e_machine))}")
        print(f"  Entry:       {hex(e_entry)}")
        print(f"  PH offset:   {e_phoff}")
        print(f"  SH offset:   {e_shoff}")
        print(f"  Sections:    {e_shnum}")
        print(f"  SH str idx:  {e_shstrndx}")

parse_elf64_header("apktool_out/lib/arm64-v8a/libct-go.so")
```

预期输出：

```
=== ELF Header: apktool_out/lib/arm64-v8a/libct-go.so ===
  Class:       ELF64
  Endian:      Little
  Type:        DYN
  Machine:     AArch64
  Entry:       0x...
  Sections:    ...
```

**关键确认：Type=DYN（共享库）、Machine=AArch64（ARM 64位）。**

---

## 三、节区分析

### 3.1 用 readelf 查看节区

```bash
readelf -S apktool_out/lib/arm64-v8a/libct-go.so
```

预期输出（简化）：

```
Section Headers:
  [Nr] Name              Type            Address          Off    Size   ES Flg
  [ 0]                   NULL            0000000000000000 000000 000000 00
  [ 1] .text             PROGBITS        ...              ...    ...    00  AX
  [ 2] .rodata           PROGBITS        ...              ...    ...    00   A
  [ 3] .data             PROGBITS        ...              ...    ...    00  WA
  [ 4] .bss              NOBITS          ...              ...    ...    00  WA
  [ 5] .dynamic          DYNAMIC         ...              ...    ...    10  WA
  [ 6] .dynsym           DYNSYM          ...              ...    ...    18   A
  [ 7] .dynstr           STRTAB          ...              ...    ...    00   A
  [ 8] .gnu.hash         GNU_HASH        ...              ...    ...    00   A
  [ 9] .rela.dyn         RELA            ...              ...    ...    18   A
  [10] .rela.plt         RELA            ...              ...    ...    18  AI
  [11] .symtab           SYMTAB          ...              ...    ...    18
  [12] .strtab           STRTAB          ...              ...    ...    00
  ...
```

### 3.2 关键节区含义

| 节区 | 类型 | 权限 | 内容 | 逆向价值 |
|------|------|------|------|----------|
| `.text` | PROGBITS | R-X | 可执行机器码 | 函数逻辑 |
| `.rodata` | PROGBITS | R-- | 只读数据（字符串、常量） | 关键字符串搜索入口 |
| `.data` | PROGBITS | RW- | 已初始化全局变量 | 全局配置值 |
| `.bss` | NOBITS | RW- | 未初始化全局变量 | 运行时状态 |
| `.dynamic` | DYNAMIC | RW- | 动态链接信息 | 依赖库列表 |
| `.dynsym` | DYNSYM | R-- | 动态符号表 | 导出/导入函数名 |
| `.dynstr` | STRTAB | R-- | 动态符号字符串 | 函数名字符串 |
| `.symtab` | SYMTAB | --- | 完整符号表（可能被 strip） | 所有函数名 |
| `.strtab` | STRTAB | --- | 完整字符串表 | 所有符号名 |
| `.gnu.hash` | GNU_HASH | R-- | 符号哈希表 | 加速符号查找 |
| `.rela.dyn` | RELA | R-- | 动态重定位表 | 交叉引用 |

### 3.3 用 Python 读取节区

```python
#!/usr/bin/env python3
"""list_elf_sections.py — 列出 ELF 所有节区"""
import struct

def list_sections(path):
    with open(path, 'rb') as f:
        f.seek(0)
        e_ident = f.read(16)
        assert e_ident[:4] == b'\x7fELF'
        assert e_ident[4] == 2  # ELF64

        # 读 ELF header
        f.seek(40); e_shoff = struct.unpack('<Q', f.read(8))[0]
        f.seek(58); e_shentsize = struct.unpack('<H', f.read(2))[0]
        f.seek(60); e_shnum = struct.unpack('<H', f.read(2))[0]
        f.seek(62); e_shstrndx = struct.unpack('<H', f.read(2))[0]

        # 读 section header string table
        shstr_off = e_shoff + e_shstrndx * e_shentsize
        f.seek(shstr_off + 24); sh_offset = struct.unpack('<Q', f.read(8))[0]
        f.seek(shstr_off + 32); sh_size = struct.unpack('<Q', f.read(8))[0]
        f.seek(sh_offset)
        shstrtab = f.read(sh_size)

        print(f"=== Sections ({e_shnum}) ===")
        for i in range(e_shnum):
            f.seek(e_shoff + i * e_shentsize)
            sh_name = struct.unpack('<I', f.read(4))[0]
            sh_type = struct.unpack('<I', f.read(4))[0]
            sh_flags = struct.unpack('<Q', f.read(8))[0]
            sh_addr = struct.unpack('<Q', f.read(8))[0]
            sh_offset_val = struct.unpack('<Q', f.read(8))[0]
            sh_size_val = struct.unpack('<Q', f.read(8))[0]

            # 从 shstrtab 读取节区名
            end = shstrtab.index(b'\x00', sh_name)
            name = shstrtab[sh_name:end].decode('utf-8', 'replace')

            flags_str = ''
            if sh_flags & 0x01: flags_str += 'W'
            if sh_flags & 0x02: flags_str += 'A'
            if sh_flags & 0x04: flags_str += 'X'

            type_names = {0:'NULL', 1:'PROGBITS', 2:'SYMTAB', 3:'STRTAB',
                          4:'RELA', 5:'HASH', 6:'DYNAMIC', 7:'NOTE',
                          8:'NOBITS', 9:'REL', 11:'DYNSYM',
                          0x6ffffff6:'GNU_HASH'}

            print(f"  [{i:2d}] {name:20s} type={type_names.get(sh_type, hex(sh_type)):12s} "
                  f"addr={hex(sh_addr):14s} size={sh_size_val:10d} flags={flags_str}")

list_sections("apktool_out/lib/arm64-v8a/libct-go.so")
```

---

## 四、Go SO 的特征识别

### 4.1 怎么判断是 Go 编译的

Go 编译的 SO 有以下特征字符串，用 `strings` 搜索：

```bash
# 搜索 Go 标识
strings libct-go.so | grep "go.buildid"
strings libct-go.so | grep "runtime\." | head -10
strings libct-go.so | grep "fmnx/cftun"
```

预期结果：

```
go.buildid=...
runtime.morestack_noctxt
runtime.gcWriteBarrier
runtime.mallocgc
github.com/fmnx/cftun/backend/...
```

### 4.2 Go 特征字符串清单

| 字符串 | 含义 | Go 独有？ |
|--------|------|-----------|
| `go.buildid` | Go 构建 ID | ✅ |
| `runtime.morestack` | Go 栈增长 | ✅ |
| `runtime.gcWriteBarrier` | Go GC 写屏障 | ✅ |
| `runtime.mallocgc` | Go 内存分配 | ✅ |
| `goroutine` | Go 协程 | ✅ |
| `golang.org/x/crypto` | Go 标准加密库 | ✅ |
| `github.com/gorilla/websocket` | gorilla WebSocket 库 | ✅ |
| `github.com/fmnx/cftun` | xTun 模块路径 | ✅ |

### 4.3 一条命令确认

```bash
strings libct-go.so | grep -cE "go\.buildid|runtime\.(morestack|gcWriteBarrier)|fmnx/cftun"
# 如果返回 >=3，就是 Go 编译的
```

### 4.4 Go 版本检测

```bash
# 搜索 Go1.x.y 版本号
strings libct-go.so | grep -oE 'Go1\.[0-9]+\.[0-9]+' | sort -u
# 预期: Go1.25.0
```

### 4.5 Go SO vs 普通 C/C++ SO

| 特征 | Go SO | C/C++ SO |
|------|-------|----------|
| 符号表 | 包含包路径（如 `github.com/...`） | 短符号名 |
| 体积 | 巨大（静态链接 runtime） | 相对小（动态链接 libc） |
| 栈管理 | 连续栈（`runtime.morestack`） | 系统栈 |
| GC | 自带 GC（`runtime.gc*`） | 手动管理 |
| 字符串 | (指针, 长度) 对，无 null 终止 | null 终止 C 字符串 |
| 入口点 | `runtime.rt0_go` → `main.main` | `_start` → `main` |

---

## 五、Flutter SO 的特征

### 5.1 libapp.so 是什么

`libapp.so` 不是普通的 C/C++ 共享库，而是 Flutter 的 **Dart AOT Snapshot**。Dart 代码被 AOT 编译成机器码，打包为 ELF 格式。

```bash
readelf -h apktool_out/lib/arm64-v8a/libapp.so
# Type: DYN
# Machine: AArch64
```

### 5.2 为什么 libapp.so 难以逆向

| 特征 | 说明 |
|------|------|
| 没有标准符号表 | Dart AOT 不保留函数名 |
| 没有调试信息 | release 模式不含 DWARF |
| 自定义 ABI | Dart 的调用约定与 C ABI 不同 |
| 对象池 (Object Pool) | 所有常量都在一个巨大的对象池里 |
| snapshot 格式 | Dart VM 自定义格式，非标准 ELF 节区布局 |

### 5.3 识别 Flutter SO

```bash
# 搜索 Dart snapshot 标记
strings libapp.so | head -20
# 可能看到 _kDartVmSnapshotInstructions 或类似标记

# 搜索 Flutter 特征
strings libapp.so | grep -i "flutter\|dart"
```

### 5.4 逆向建议

对于 xTun 的逆向，**不需要分析 libapp.so**。原因：

1. UI 逻辑（登录、节点选择）不含协议细节
2. 所有加密/协议逻辑在 `libct-go.so`
3. Dart AOT snapshot 逆向工具不成熟
4. API URL 等信息在 Go 后端中同样存在

如果确实需要分析 Dart 代码（例如提取 UI 中的硬编码值），可以用 [reFlutter](https://github.com/nicolo-ribaudo/reFlutter) 或 Doldrums 工具。

---

## 六、字符串搜索

### 6.1 基础搜索

```bash
# 提取所有可打印字符串（>=4字符）
strings -n 4 libct-go.so > libct_strings.txt
wc -l libct_strings.txt
# 预期: 几万行

# 搜索关键字
grep -i "cftun" libct_strings.txt
grep -i "websocket" libct_strings.txt
grep -i "payloadsecret\|payload_secret" libct_strings.txt
grep -i "access_point" libct_strings.txt
grep "{API_DOMAIN_SEARCH_PREFIX}" libct_strings.txt
```

### 6.2 分类搜索脚本

```python
#!/usr/bin/env python3
"""search_so_strings.py — 搜索并分类 SO 中的关键字符串"""
import re

with open("apktool_out/lib/arm64-v8a/libct-go.so", "rb") as f:
    data = f.read()

strings = re.findall(rb'[\x20-\x7e]{4,}', data)

categories = {
    'cftun协议': [s for s in strings if b'cftun' in s.lower()],
    'websocket': [s for s in strings if b'websocket' in s.lower()],
    'crypto': [s for s in strings if any(k in s.lower() for k in
               [b'aes', b'gcm', b'chacha', b'x25519', b'hkdf', b'sha256'])],
    'api': [s for s in strings if b'xtun' in s.lower() or b'api.' in s],
    'go模块': [s for s in strings if b'fmnx/cftun' in s],
    'secret': [s for s in strings if b'secret' in s.lower() or b'password' in s.lower()],
}

for cat, items in categories.items():
    print(f"\n=== {cat} ({len(items)}) ===")
    for s in items[:15]:
        try:
            print(f"  {s.decode('utf-8')[:120]}")
        except:
            print(f"  (binary: {s[:40].hex()})")
```

### 6.3 带偏移的搜索（定位在文件中的位置）

```bash
# strings -t x 显示十六进制偏移
strings -t x libct-go.so | grep "cftun"
# 输出示例:
#   3a5f20 cftun websocket v3
#   3a5f40 cftun-txt
#   3a5f50 cftun-config-response-v1

# 这些偏移可以直接在 HxD/010Editor 中跳转查看
```

---

## 七、符号表提取

### 7.1 动态符号表

```bash
# 查看动态符号（导出/导入函数）
readelf -s --dyn-syms libct-go.so | head -30

# 或用 nm
nm -D libct-go.so | head -30
```

### 7.2 完整符号表

Go 编译器默认不 strip 符号表（除非手动 `go build -ldflags="-s -w"`）。如果 `.symtab` 存在：

```bash
# 完整符号表
readelf -s libct-go.so | wc -l
# 如果有几万行 → 符号表完整

# 搜索 cftun 相关函数
readelf -s libct-go.so | grep -i "cftun\|AccessPoint\|Websocket\|PayloadSecret"
```

### 7.3 如果符号表被 strip 了

```bash
# 检查是否被 strip
readelf -S libct-go.so | grep -c "\.symtab"
# 0 = 被 strip 了
# 1 = 符号表存在

# 即使被 strip，.dynsym 仍然存在（动态链接需要）
readelf -S libct-go.so | grep "dynsym"
```

如果被 strip，Go 的函数名仍然藏在 `.rodata` 的 `gopclntab`（Go PC Line Table）中。Ghidra 12+ 能自动从 gopclntab 恢复函数名。

### 7.4 提取函数列表

```python
#!/usr/bin/env python3
"""extract_symbols.py — 用 pyelftools 提取符号"""

# pip install pyelftools
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection

with open("apktool_out/lib/arm64-v8a/libct-go.so", "rb") as f:
    elf = ELFFile(f)

    for section in elf.iter_sections():
        if isinstance(section, SymbolTableSection):
            print(f"\n=== {section.name} ({section.num_symbols()} symbols) ===")
            count = 0
            for sym in section.iter_symbols():
                name = sym.name
                if any(kw in name for kw in ['cftun', 'AccessPoint', 'Websocket',
                                              'PayloadSecret', 'Argo', 'HKDF']):
                    addr = sym['st_value']
                    size = sym['st_size']
                    print(f"  {name}  addr={hex(addr)}  size={size}")
                    count += 1
            print(f"  ... (筛选了 {count} 个关键函数)")
```

---

## 八、Ghidra 中导入 ARM64 ELF

### 8.1 导入步骤

1. 启动 Ghidra GUI → `File → Import File`
2. 选择 `libct-go.so`
3. **Language 选择**: `AARCH64:LE:64:v8A`（关键！不要选 ARM 32 位）
4. Format: `ELF`（自动识别）
5. 点击 `OK` → 开始分析

### 8.2 ARM64 vs AMD64 架构差异

| 特征 | ARM64 (AArch64) | AMD64 (x86_64) |
|------|-----------------|----------------|
| 指令集 | RISC（定长 4 字节） | CISC（变长 1-15 字节） |
| 寄存器 | X0-X30 + SP + PC | RAX, RBX, ... RSP, RIP |
| 函数调用 | X0-X7 传参，X0 返回 | RDI, RSI, RDX, RCX, ... |
| 栈对齐 | 16 字节 | 16 字节 |
| 分支 | B, BL, BR | JMP, CALL, RET |

### 8.3 Ghidra Headless 导入 SO

```bash
# Headless 导入 libct-go.so
analyzeHeadless.bat "{GHIDRA_PROJECT_DIR}" xtun_so_proj \
  -import "apktool_out/lib/arm64-v8a/libct-go.so" \
  -processor "AARCH64:LE:64:v8A" \
  -overwrite
```

### 8.4 分析注意事项

- Go 的 ARM64 二进制和 x86_64 二进制使用相同的包路径和函数命名
- 函数逻辑相同，只是指令集不同
- Ghidra 反编译 ARM64 的质量略低于 x86_64（ARM 的条件执行更复杂）
- 如果 Ghidra 反编译效果差，用 IDA Pro 对比（IDA 的 ARM64 支持更成熟）

---

## 九、SO vs EXE 对比

### 9.1 代码对应关系

xTun 的 `libct-go.so`（ARM64）和 `xtun-windows.exe`（AMD64）是**同一份 Go 源代码的不同平台编译产物**。

| 函数 | xtun-windows.exe (AMD64) | libct-go.so (ARM64) |
|------|--------------------------|---------------------|
| `decryptAccessPoint` | `0x140365f60` | 地址不同，但函数名相同 |
| `DecryptResponse` | `0x1404eaec0` | 地址不同，但逻辑相同 |
| `NewWebsocket` | `0x140348120` | 地址不同 |
| `connectWithPurpose` | `0x14034afc0` | 地址不同 |

### 9.2 怎么在 SO 中找到对应函数

```bash
# 在 SO 中搜索同名函数
readelf -s libct-go.so | grep "decryptAccessPoint"
# 输出:  xxxxx: 00000000003a1234  1024 FUNC  LOCAL  DEFAULT  1 ...decryptAccessPoint

# 或搜索字符串交叉引用
strings -t x libct-go.so | grep "cftun-txt"
# 找到 AAD 字符串的偏移 → 在 Ghidra 中找引用 → 定位 decryptAccessPoint
```

### 9.3 为什么要分析 SO

| 场景 | 用 EXE | 用 SO |
|------|--------|-------|
| 第一次逆向 | ✅ 推荐（x86_64 反编译质量更好） | |
| 验证发现 | | ✅ 交叉验证 EXE 分析结果 |
| Android 特有逻辑 | | ✅ TUN 接口、VPN Service |
| 函数地址不同 | EXE 的地址 | SO 的地址（不能直接套用） |
| 动态分析 | Windows 上运行 + 调试 | Android 上 Frida hook |

---

## 十、完整 Python ELF 解析脚本

```python
#!/usr/bin/env python3
"""analyze_elf.py — 完整的 ELF 文件分析（使用 pyelftools）"""

# pip install pyelftools
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
import sys, re

def analyze(path):
    with open(path, 'rb') as f:
        elf = ELFFile(f)

        # === ELF Header ===
        print(f"{'='*60}")
        print(f"  ELF Analysis: {path}")
        print(f"{'='*60}")
        print(f"  Class:       {elf.elfclass}-bit")
        print(f"  Endian:      {'Little' if elf.little_endian else 'Big'}")
        print(f"  Machine:     {elf.header['e_machine']}")
        print(f"  Type:        {elf.header['e_type']}")
        print(f"  Entry:       {hex(elf.header['e_entry'])}")

        # === Sections ===
        print(f"\n--- Sections ({elf.num_sections()}) ---")
        for section in elf.iter_sections():
            name = section.name
            if not name:
                continue
            sh = section.header
            flags = ''
            if sh['sh_flags'] & 0x01: flags += 'W'
            if sh['sh_flags'] & 0x02: flags += 'A'
            if sh['sh_flags'] & 0x04: flags += 'X'
            print(f"  {name:20s} size={sh['sh_size']:10d}  addr={hex(sh['sh_addr']):14s}  flags={flags}")

        # === Symbols (key functions) ===
        print(f"\n--- Key Symbols ---")
        keywords = ['cftun', 'AccessPoint', 'Websocket', 'websocket',
                    'PayloadSecret', 'HKDF', 'ChaCha', 'AESGCM',
                    'Argo', 'ConfigResponse', 'X25519', 'DecryptResponse']
        for section in elf.iter_sections():
            if not isinstance(section, SymbolTableSection):
                continue
            for sym in section.iter_symbols():
                name = sym.name
                if any(kw in name for kw in keywords):
                    print(f"  {name[:80]}  addr={hex(sym['st_value'])}  size={sym['st_size']}")

        # === Go Detection ===
        print(f"\n--- Go Detection ---")
        f.seek(0)
        data = f.read()
        go_markers = [b'go.buildid', b'runtime.morestack', b'fmnx/cftun']
        for marker in go_markers:
            idx = data.find(marker)
            if idx >= 0:
                print(f"  FOUND '{marker.decode()}'  at offset {hex(idx)}")
            else:
                print(f"  NOT FOUND '{marker.decode()}'")

        # === Go Version ===
        versions = set(re.findall(rb'Go1\.(\d+)\.(\d+)', data))
        for major, minor in sorted(versions):
            print(f"  Go version: 1.{major.decode()}.{minor.decode()}")

        # === Critical Strings ===
        print(f"\n--- Critical Strings ---")
        critical = [b'cftun websocket v3', b'cftun-txt',
                    b'cftun-config-response-v1',
                    b'{PAYLOAD_SECRET}',
                    b'{API_DOMAIN}', b'X-Cftun-Config-Key']
        for s in critical:
            idx = data.find(s)
            if idx >= 0:
                print(f"  FOUND '{s.decode()}'  at {hex(idx)}")
            else:
                print(f"  NOT FOUND '{s.decode()}'")

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else "apktool_out/lib/arm64-v8a/libct-go.so"
    analyze(path)
```

### 运行

```bash
pip install pyelftools
python analyze_elf.py apktool_out/lib/arm64-v8a/libct-go.so
```

---

## 十一、关键发现总结

走完这一步你应该确认：

- ✅ `libct-go.so` 是 ELF64, AArch64 (ARM64), Type=DYN (共享库)
- ✅ Go 1.25.0 编译，模块路径 `github.com/fmnx/cftun/backend`
- ✅ 关键字符串全部在 `.rodata` 节区中找到
- ✅ 函数名与 `xtun-windows.exe` 中的一致（地址不同）
- ✅ `libapp.so` 是 Flutter Dart AOT，逆向价值低
- ✅ 协议逻辑在 `libct-go.so` 中，不在 `libapp.so`
- ✅ Ghidra 导入时选 `AARCH64:LE:64:v8A`
- ✅ 符号表（如果存在）可用 readelf/pyelftools 提取

---

**返回**：[核心教学 README](./xtun-go-reverse-teaching-archive.md#source-core-16)

---

<a id="source-supplement-a3"></a>

> **编辑说明（A3；source-report）**：保留源文中节区表和地址演算的原貌，其中“VA”列实际混用 RVA，4.4 节有未闭合的等式；阅读时应分别确认 VA、ImageBase、RVA 和落入的文件支撑节区，再按 file_offset = RVA - section.VirtualAddress + section.PointerToRawData 换算，并检查范围。7.5 节把 0x23 的 IP 归类为 CDN，是 A8 历史假设，不应覆盖 A8 末段修正。节点地址的文字、hex 与转义字节同步脱敏。

# A3 · 补充 — 十六进制分析

---

## 目标

学会用十六进制编辑器手动查看二进制文件，定位 PE 结构、字符串、加密常量和自定义数据格式。反编译器不是万能的，有些数据结构必须直接看 hex。

---

## 一、为什么需要看十六进制

反编译器（Ghidra/IDA）擅长把代码还原成伪代码，但以下场景它帮不了你：

| 场景 | 为什么反编译器搞不定 | 十六进制能做什么 |
|------|---------------------|-----------------|
| 自定义二进制格式 | 反编译器不认识私有格式 | 手动逐字节解析 |
| 反字符串搜索 | 开发者逐字节构造字符串，避免被 strings 发现 | 搜索 hex 模式而非 ASCII |
| 加密常量 | S-Box 不是函数，是查找表 | 搜索已知常量的 hex 特征 |
| Go 字符串 | Go 的 (指针,长度) 对不以 null 结尾 | 手动定位和读取 |
| 文件格式验证 | 确认 PE/ELF 头是否完整 | 直接看 Magic Bytes |
| 补丁/Patch | 修改一个字节的跳转指令 | 精确到字节修改 |
| 加密前后对比 | 看密文结构（nonce + ciphertext + tag） | 对比两段数据 |

---

## 二、工具

| 工具 | 价格 | 特点 | 推荐场景 |
|------|------|------|----------|
| **HxD** | 免费 | Windows 原生，打开 50MB 无压力 | 日常查看、搜索、修改 |
| **010 Editor** | $49.95 | 模板系统（自动解析 PE/ELF/ZIP） | 结构化分析 |
| **ImHex** | 免费开源 | 模式匹配、自定义高亮 | 自定义格式分析 |
| **Python struct** | 免费 | 脚本化、批量处理 | 自动化解析 |

本教学以 **HxD** 为主（免费 + 够用），Python 辅助。

### 安装 HxD

```
下载: https://mh-nexus.de/en/hxd/
安装后，用 HxD 打开 xtun-windows.exe
```

---

## 三、PE 文件的 Magic Bytes

### 3.1 MZ 头 — 文件的第一关

用 HxD 打开 `xtun-windows.exe`，文件开头就是 DOS 头：

```
偏移      十六进制                                          ASCII
00000000: 4D 5A 90 00 03 00 00 00 04 00 00 00 FF FF 00 00  MZ..............
00000010: 8B 00 00 00 00 00 00 00 40 00 00 00 00 00 00 00  ........@.......
00000020: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
00000030: 00 00 00 00 00 00 00 00 00 00 00 00 80 00 00 00  ................
00000040: 0E 1F BA 0E 00 B4 09 CD 21 B8 01 4C CD 21 54 68  ........!..L.!Th
00000050: 69 73 20 70 72 6F 67 72 61 6D 20 63 61 6E 6E 6F  is program canno
00000060: 74 20 62 65 20 72 75 6E 20 69 6E 20 44 4F 53 20  t be run in DOS
00000070: 6D 6F 64 65 2E 0D 0D 0A 24 00 00 00 00 00 00 00  mode....$.......
```

| 偏移 | 值 | 含义 |
|------|-----|------|
| `0x0000` | `4D 5A` | "MZ" — DOS 可执行文件签名。所有 Windows PE 都以此开头 |
| `0x003C` | `80 00 00 00` | **e_lfanew** — PE 头的文件偏移（小端）= `0x00000080` |
| `0x0040-0x007F` | DOS stub | "This program cannot be run in DOS mode" — 在 DOS 下运行时显示的提示 |

**操作方法**: HxD → 按 `Ctrl+G`（跳转到偏移）→ 输入 `3C` → 读取 4 字节小端值 `80 00 00 00` → PE 头在偏移 `0x80`。

### 3.2 PE 签名

跳转到偏移 `0x80`：

```
00000080: 50 45 00 00 64 86 09 00 00 00 00 00 00 A8 F5 02  PE..d...........
00000090: 00 00 00 00 F0 00 22 00 0B 02 03 00 00 76 5B 00  ......"......v[.
000000A0: 00 54 11 00 00 00 00 00 20 C7 07 00 00 10 00 00  .T...... .......
000000B0: 00 00 00 40 01 00 00 00 00 10 00 00 00 02 00 00  ...@............
```

| 偏移 | 值 | 含义 |
|------|-----|------|
| `0x0080` | `50 45 00 00` | "PE\0\0" — PE 签名，确认是 PE 格式 |
| `0x0084` | `64 86` | Machine = `0x8664`（小端）= AMD64 / x86_64 |
| `0x0086` | `09 00` | NumberOfSections = `9` |
| `0x0098` | `0B 02` | Optional Header Magic = `0x020B` = PE32+（64位）|

**怎么判断 32 位还是 64 位**:
- `0x010B` = PE32（32位）
- `0x020B` = PE32+（64位）← xtun-windows.exe 是这个

### 3.3 Python 验证

```python
import struct

with open("xtun-windows.exe", "rb") as f:
    # 检查 MZ
    assert f.read(2) == b'MZ', "不是 PE 文件"

    # 读取 e_lfanew
    f.seek(0x3C)
    pe_offset = struct.unpack('<I', f.read(4))[0]
    print(f"PE头偏移: 0x{pe_offset:X}")  # 0x80

    # 检查 PE 签名
    f.seek(pe_offset)
    assert f.read(4) == b'PE\x00\x00', "PE签名错误"

    # 读取 Machine
    machine = struct.unpack('<H', f.read(2))[0]
    print(f"Machine: 0x{machine:X}")  # 0x8664 = AMD64
```

---

## 四、手动定位节区

### 4.1 从 PE 头找节区表

节区表紧跟在 Optional Header 之后。计算方法:

```
节区表偏移 = PE签名偏移(0x80) + 4(签名) + 20(COFF头) + OptionalHeaderSize(240)
            = 0x80 + 4 + 20 + 240 = 0x80 + 264 = 0x188
```

在 HxD 中 `Ctrl+G` 跳转到 `0x188`，每个节区头 40 字节。

### 4.2 xtun-windows.exe 的 9 个节区

| 节区 | VA | 文件偏移(RawPtr) | 文件大小(RawSize) | 属性 |
|------|-----|------------------|-------------------|------|
| `.text` | 0x00001000 | **0x00000600** | 0x005B7600 | 可执行代码 |
| `.rdata` | 0x005B9000 | **0x005B7C00** | 0x02841A00 | 只读数据（字符串） |
| `.data` | 0x02DFB000 | **0x02DF9600** | 0x00115400 | 可读写数据 |
| `.pdata` | 0x02F6B000 | 0x02F0EA00 | 0x00024C00 | 异常处理表 |
| `.xdata` | 0x02F90000 | 0x02F33600 | 0x00000200 | 展开信息 |
| `.idata` | 0x02F91000 | 0x02F33800 | 0x00000600 | 导入表 |
| `.reloc` | 0x02F92000 | 0x02F33E00 | 0x00026A00 | 重定位表 |
| `.symtab` | 0x02FB9000 | 0x02F5A800 | 0x00000200 | 符号表 |
| `.rsrc` | 0x02FBA000 | 0x02F5AA00 | 0x000A1E00 | 资源（图标等）|

**重点**: 逆向要搜索的字符串在 `.rdata` 节区，文件偏移从 `0x005B7C00` 开始。

### 4.3 跳转到 .rdata 看字符串

在 HxD 中 `Ctrl+G` → 输入 `5B7C00` → 你现在在 `.rdata` 的起始位置。

往下滚动，能看到大量 Go 运行时字符串、模块路径、错误消息等。

### 4.4 VA 和文件偏移的转换

Ghidra 显示的地址是 **VA (Virtual Address)**，十六进制编辑器用的是**文件偏移**。转换公式：

```
文件偏移 = VA - 节区VA + 节区RawPtr

例: Ghidra 显示某字符串在 VA=0x1405ED737
    这个 VA 在 .rdata 节区内 (VA=0x1405B9000 ~ 0x1427FA938)
    去掉 ImageBase(0x140000000): RVA = 0x5ED737
    .rdata: VA=0x5B9000, RawPtr=0x5B7C00
    文件偏移 = 0x5ED737 - 0x5B9000 + 0x5B7C00 = 0x5EC337

    不对，更简单的方法：
    文件偏移 ≈ RVA - 节区VA + 节区RawPtr
             = 0x5ED737 - 0x5B9000 + 0x5B7C00
             = 0x5EC337 + (0x5B7C00 - 0x5B9000 + 0x5B9000)
```

**更实用的方法**: 直接在 HxD 中搜索字符串（`Ctrl+F` → Text string → 输入关键词），不用手动算偏移。

---

## 五、搜索关键字符串

### 5.1 在 HxD 中搜索

`Ctrl+F` → 选择 "Text string" → 输入搜索内容。

### 5.2 xTun 关键字符串及其文件偏移

| 字符串 | 文件偏移 | 十六进制 | 上下文 |
|--------|----------|----------|--------|
| `payload_secret` | `0x007420CD` | `70 61 79 6C 6F 61 64 5F 73 65 63 72 65 74` | JSON 字段名 |
| `access_point` | `0x007401FF` | `61 63 63 65 73 73 5F 70 6F 69 6E 74` | JSON 字段名 |
| `tunnel_uuid` | `0x0073F3A6` | `74 75 6E 6E 65 6C 5F 75 75 69 64` | JSON 字段名 |
| `xtun-config-response-v1` | `0x0074D078` | `78 74 75 6E 2D 63 6F 6E 66 69 67 2D 72 65 73 70 6F 6E 73 65 2D 76 31` | 第一层解密的 AAD/info |
| `{API_DOMAIN}` | `0x007678F6` | `{DOMAIN_ASCII_HEX_BYTES}` | API 域名 |
| `DEV` | `0x0073AF23` | `44 45 56` | User-Agent 值 |
| `gorilla/websocket` | `0x005E77E4` | — | WebSocket 库 |
| `chacha20poly1305` | `0x005EDB80` | — | 加密库 |
| `golang.org/x/crypto/hkdf` | `0x005E268D` | — | HKDF 库 |
| `go1.25.0` | `0x029E6300` | `67 6F 31 2E 32 35 2E 30` | Go 编译器版本 |

### 5.3 关键发现：cftun-txt 没有作为完整字符串出现

搜索 `cftun-txt`（`63 66 74 75 6E 2D 74 78 74`）在整个二进制中**找不到**。

这是因为 Go 代码**逐字节构造 AAD**，避免被 strings 搜索发现：

```c
// Ghidra 反编译看到的
byte aad[9];
aad[0] = 0x63;  // 'c'
aad[1] = 0x66;  // 'f'
aad[2] = 0x74;  // 't'
aad[3] = 0x75;  // 'u'
aad[4] = 0x6E;  // 'n'
aad[5] = 0x2D;  // '-'
aad[6] = 0x74;  // 't'
aad[7] = 0x78;  // 'x'
aad[8] = 0x74;  // 't'
```

**怎么找**: 在 HxD 中搜索不到完整字符串时，去 Ghidra 的反编译窗口看函数体，会看到逐字节赋值的模式。把 hex 值拼起来就是完整字符串。

同理，`"cftun websocket v3"` 和 `"{PAYLOAD_SECRET}"` 也搜不到，都是运行时构造的。

### 5.4 但 xtun-config-response-v1 可以搜到

```
0074D078: 78 74 75 6E 2D 63 6F 6E 66 69 67 2D 72 65 73 70  xtun-config-resp
0074D088: 6F 6E 73 65 2D 76 31 62 61 64 20 6B 61 72 61 74  onse-v1bad karat
```

**为什么这个没有被混淆**: 这个字符串同时用于 HTTP 头 (`Accept: application/vnd.cftun.config-encrypted+json`) 的内部逻辑和 HKDF info 参数，代码中多处引用，无法完全逐字节化。

### 5.5 有趣的字符串上下文

在 `DEV` 字符串附近 (`0x0073AF23`) 可以看到：

```
0073AF13: 31 73 65 74 27 22 27 29 3A 20 69 70 34 69 70 36  1set'"'): ip4ip6
0073AF23: 44 45 56 2F 65 2F 2F 76 2F 63 66 5F 2A 2F 2A 62  DEV/e//v/cf_*/*b
0073AF33: 67 70 3B 52 52 3B 52 44 2E 25 64 74 75 6E 3A 5C  gp;RR;RD.%dtun:\
```

一行就能读出关键协议细节:
- `DEV` — User-Agent
- `/e/` — implicit_websocket 路径中的 exit_server_ip 标记
- `/v/` — 某种版本路径（未在教学中出现，可能是旧版协议）
- `cf_` — Argo 模式的 upstream 前缀
- `;RR` — Round Robin 负载均衡模式
- `;RD` — Random 负载均衡模式
- `tun:` — tunnel 相关

**这就是十六进制分析的价值**: 一眼扫过就能发现反编译器可能分散在几十个函数里的协议关键词。

---

## 六、识别加密常量

### 6.1 AES S-Box

AES 的 S-Box 是一个固定的 256 字节查找表，开头是：

```
63 7C 77 7B F2 6B 6F C5 30 01 67 2B FE D7 AB 76
```

在 HxD 中 `Ctrl+F` → Hex values → 输入 `63 7C 77 7B F2 6B` 搜索。如果找到，说明二进制内嵌了 AES 实现（而非调用系统库）。

Go 的 `crypto/aes` 确实包含内联的 S-Box，所以在 `xtun-windows.exe` 中大概率能找到。

### 6.2 ChaCha20 常量

ChaCha20 的初始常量是 `"expand 32-byte k"`:

```
65 78 70 61 6E 64 20 33 32 2D 62 79 74 65 20 6B
```

搜索这个 16 字节序列可以定位 ChaCha20 的实现位置。

### 6.3 X25519 基点

Curve25519 的基点是固定的 32 字节:

```
09 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
```

（就是数字 9 的小端 32 字节编码）

### 6.4 Python 批量搜索

```python
#!/usr/bin/env python3
"""search_crypto_constants.py — 搜索加密常量"""

with open("xtun-windows.exe", "rb") as f:
    data = f.read()

constants = {
    "AES S-Box": bytes([0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5]),
    "ChaCha20 expand": b"expand 32-byte k",
    "X25519 basepoint": b"\x09" + b"\x00" * 31,
    "SHA-256 init H0": bytes([0x6A, 0x09, 0xE6, 0x67]),
}

for name, pattern in constants.items():
    idx = data.find(pattern)
    if idx >= 0:
        print(f"[+] {name} @ 0x{idx:08X}")
    else:
        print(f"[-] {name} 未找到（可能使用 CPU 指令集）")
```

---

## 七、二进制数据结构分析 — decodeTXTBinaryPayload

### 7.1 格式定义

access_point 解密后的明文是自定义二进制格式 (`txt_cipher.go:78`)。这种格式没有任何文档，只能通过 hex dump + 反编译来逆向。

```
[1字节 mode]        低2位: 0=plain, 1=RR, 2=RD, 3=error
[uvarint count]     entry 数量（变长编码）
每个 entry:
  [1字节 type]      0x22='"' (implicit_websocket) 或 0x23='#' (websocket)
  [4字节 IPv4]      IP 地址，每字节一段
  [2字节 port]      端口，大端编码
  [1字节 term]      0x00 终止符
```

### 7.2 实际 hex dump 分析

假设解密后的明文是:

```
01 04 22 {IPV4_BYTES_06} 00 50 00 22 {IPV4_BYTES_05} 00 50 00 22 {IPV4_BYTES_04} 00 50 00 22 {IPV4_BYTES_14} 00 50 00
```

逐字节解析:

| 偏移 | 十六进制 | 解析 |
|------|----------|------|
| 0 | `01` | mode = 1 (RR = Round Robin) |
| 1 | `04` | count = 4 (uvarint, 单字节，值=4) |
| 2 | `22` | type = 0x22 ('"') = implicit_websocket |
| 3-6 | `{IPV4_BYTES_06}` | IPv4 = {IPV4_ADDRESS_06} |
| 7-8 | `00 50` | port = 0x0050 = 80 |
| 9 | `00` | 终止符 |
| 10 | `22` | type = 0x22 = implicit_websocket |
| 11-14 | `{IPV4_BYTES_05}` | IPv4 = {IPV4_ADDRESS_05} |
| 15-16 | `00 50` | port = 80 |
| 17 | `00` | 终止符 |
| ... | ... | 继续，共 4 个 entry |

结果: `{IPV4_ADDRESS_06}:80,{IPV4_ADDRESS_05}:80,{IPV4_ADDRESS_04}:80,{IPV4_ADDRESS_14}:80;RR`

### 7.3 uvarint 编码

Go 的 uvarint 是变长整数编码:
- 如果最高位 (bit 7) 为 0，则该字节就是值
- 如果最高位为 1，则低 7 位是值的一部分，继续读下一字节

```
0x04         → 4（单字节，最高位 0）
0x80 0x01    → 128（第一字节 0x80: 低7位=0, 续读; 第二字节 0x01: 值=1<<7=128）
0xAC 0x02    → 300（0x2C | (0x02 << 7) = 44 + 256 = 300）
```

### 7.4 Python 完整解析

```python
def decode_txt_binary_payload(data: bytes) -> str:
    """完整解析 decodeTXTBinaryPayload 格式"""
    # 1. mode 字节
    mode = data[0] & 0x03
    mode_str = {0: '', 1: ';RR', 2: ';RD', 3: ''}.get(mode, '')

    # 2. 读取 uvarint count
    idx = 1
    count = 0
    shift = 0
    while idx < len(data):
        b = data[idx]
        count |= (b & 0x7F) << shift
        idx += 1
        if not (b & 0x80):
            break
        shift += 7

    # 3. 解析每个 entry
    entries = []
    for _ in range(count):
        if idx + 8 > len(data):
            break
        entry_type = data[idx]; idx += 1        # 0x22 或 0x23
        ip = f"{data[idx]}.{data[idx+1]}.{data[idx+2]}.{data[idx+3]}"
        idx += 4
        port = (data[idx] << 8) | data[idx+1]   # 大端
        idx += 2
        idx += 1                                 # 0x00 终止
        entries.append(f"{ip}:{port}")

    return ','.join(entries) + mode_str
```

### 7.5 0x22 vs 0x23 的含义

| type | 字符 | 含义 | 节点类型 |
|------|------|------|----------|
| `0x22` | `"` | IP 是直连源站 | implicit_websocket |
| `0x23` | `#` | IP 是 CDN 任播 | websocket |

这个字节决定了客户端用哪种连接器:
- `0x22`: NewRouteRacer (HTTPBridgeDialer)，Host=纯IP，Path=/{upstream}/e/{exit_ip}
- `0x23`: NewWebsocket (gorilla Dialer)，Host=DomainPool，Path=/

---

## 八、Go 字符串的十六进制特征

### 8.1 Go 字符串不以 null 结尾

C 字符串: `"hello\0"` — 以 `00` 结尾
Go 字符串: `{pointer, length}` — 是一个 16 字节结构体（64位: 8字节指针 + 8字节长度）

在 hex dump 中的表现:

```
005ED72F: 74 14 6A 73 6F 6E 3A 22 70 61 79 6C 6F 61 64 53  t.json:"payloadS
005ED73F: 65 63 72 65 74 22 00 22 2A 73 74 72 75 63 74 20  ecret"."*struct
```

注意 `payloadSecret"` 后面紧跟 `00 22` — 这不是 null 终止符 + 下一个字符串的开头。`00` 可能是对齐填充，`22` 是下一个字段标注 `"*struct`。

Go 字符串在 `.rdata` 中紧密排列，没有 null 分隔。

### 8.2 怎么找 Go 字符串的引用

Go 字符串引用方式:
```
LEA RAX, [RIP + 0x1234]     ; 加载字符串地址
MOV RBX, 14                 ; 字符串长度 = 14 ("payloadSecret" = 14 字节)
```

在 hex 中看到的是:
```
48 8D 05 xx xx xx xx    ; LEA RAX, [RIP + offset]
48 C7 C3 0E 00 00 00    ; MOV RBX, 14 (0x0E)
```

**实用方法**: 在 Ghidra 中看反汇编比在 hex 中手动找更高效。Hex 分析更适合看数据区，Ghidra 更适合看代码区。

### 8.3 Go 模块路径的特征

Go 编译后，模块路径以连续字符串的形式存在于 `.rdata`:

```
005E77E4: github.com/gorilla/websocket
005E268D: golang.org/x/crypto/hkdf
```

搜索 `github.com/` 或 `golang.org/` 可以快速列出所有依赖库。

---

## 九、比较两段数据

### 9.1 HxD 的文件对比

`Analysis → File compare` → 选择两个文件 → HxD 会高亮不同的字节。

用途: 比较修改前后的二进制，或两个版本的 exe。

### 9.2 Python 对比加密前后数据

```python
#!/usr/bin/env python3
"""compare_crypto.py — 对比加密前后数据"""

def hex_compare(name_a, data_a, name_b, data_b):
    """并排对比两段数据"""
    max_len = max(len(data_a), len(data_b))
    print(f"{'偏移':6s}  {name_a:48s}  {name_b}")
    print("-" * 110)
    for offset in range(0, max_len, 16):
        a_chunk = data_a[offset:offset+16]
        b_chunk = data_b[offset:offset+16]
        a_hex = ' '.join(f'{b:02X}' for b in a_chunk).ljust(48)
        b_hex = ' '.join(f'{b:02X}' for b in b_chunk).ljust(48)
        # 标记不同的字节
        diff = " " if a_chunk == b_chunk else "≠"
        print(f"{offset:04X} {diff} {a_hex}  {b_hex}")

# 示例: 对比 open frame 明文和密文
import os, hashlib
from Crypto.Cipher import ChaCha20_Poly1305

plaintext = b'\x04\x01\x06\x04' + b'\x01\x00\x00\x00' + b'{DESTINATION_IPV4_BYTES}' + b'\x01\xbb'
# ... (省略完整构造)

key = hashlib.sha256(b"example").digest()
nonce = os.urandom(12)
cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
ciphertext, tag = cipher.encrypt_and_digest(plaintext)

hex_compare("明文", plaintext, "密文", nonce + ciphertext + tag)
```

### 9.3 加密数据的 hex 特征

| 结构 | 长度 | 特征 |
|------|------|------|
| Nonce | 12 字节 | 随机数据（open frame）或 4零+8字节seq（数据通道）|
| Ciphertext | 与明文等长 | 看起来完全随机 |
| Tag | 16 字节 | Poly1305 认证标签 |

密文的辨识方法: 如果一段数据看起来完全随机（无可见 ASCII），前 12 字节可能是 nonce，最后 16 字节可能是 tag，中间是密文。

---

## 十、修改二进制（概念）

### 10.1 常见的单字节 Patch

| 原始指令 | 十六进制 | 修改为 | 十六进制 | 效果 |
|----------|----------|--------|----------|------|
| `JNZ rel8` | `75 xx` | `JZ rel8` | `74 xx` | 反转条件跳转 |
| `JNZ rel8` | `75 xx` | `JMP rel8` | `EB xx` | 强制跳转 |
| `JNZ rel8` | `75 xx` | `NOP NOP` | `90 90` | 删除跳转 |
| `CALL rel32` | `E8 xx xx xx xx` | `NOP×5` | `90 90 90 90 90` | 跳过函数调用 |
| `TEST EAX,EAX` | `85 C0` | `XOR EAX,EAX` | `33 C0` | 强制返回 0 |

### 10.2 在 HxD 中修改

1. `Ctrl+G` 跳转到目标偏移
2. 直接在 hex 编辑区输入新值
3. `Ctrl+S` 保存
4. **注意**: 修改后的 exe 校验和(checksum) 会变，需要用工具修复

### 10.3 修改后需要注意

| 检查项 | 工具 | 说明 |
|--------|------|------|
| PE Checksum | `python-pefile` 的 `pe.generate_checksum()` | 部分 Windows 检查 |
| 代码签名 | 无法修复（除非有原始签名证书） | 修改后签名失效 |
| Go runtime integrity | 无标准检查 | Go 不检查自身完整性 |
| 文件大小 | 不要改变 | NOP 填充保持大小不变 |

### 10.4 xTun 相关的 Patch 思路

理论上可以 patch 的位置:
- `connectWithPurpose` 中设置 `UA=DEV` 的位置 → 改为自定义 UA
- `decryptAccessPoint` 的 AAD 校验 → 跳过 AAD 检查（不推荐，破坏安全性）
- `isArgo` 检查 → 强制启用/禁用 cf_ 前缀

**不推荐对 xTun 做 binary patch**: 协议逆向已经完成，用 Python 重新实现比 patch 更可靠。Binary patch 适用于没有源码且无法重新实现的场景。

---

## 十一、Go 构建信息（.data 节区特殊标记）

在 `.data` 节区起始位置（文件偏移 `0x02DF9600`）有 Go 构建信息标记:

```
02DF9600: FF 20 47 6F 20 62 75 69 6C 64 69 6E 66 3A 08 02  . Go buildinf:..
02DF9610: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
02DF9620: 08 67 6F 31 2E 32 35 2E 30 E5 0E 30 77 AF 0C 92  .go1.25.0..0w...
02DF9630: 74 08 02 41 E1 C1 07 E6 D6 18 E6 70 61 74 68 09  t..A.......path.
```

| 偏移 | 值 | 含义 |
|------|-----|------|
| `0x02DF9600` | `FF 20 47 6F 20 62 75 69 6C 64 69 6E 66 3A` | `\xFF Go buildinf:` — Go 构建信息标记 |
| `0x02DF9621` | `67 6F 31 2E 32 35 2E 30` | `go1.25.0` — 编译器版本 |
| `0x02DF9630+` | `70 61 74 68 09...` | `path\t...` — 模块路径信息开始 |

**搜索方法**: 在 HxD 中搜索 `FF 20 47 6F 20 62 75 69 6C 64` 即可找到 Go 构建信息。

---

## 十二、实战练习

### 练习 1: 找到 API URL

用 HxD 打开 `xtun-windows.exe`，`Ctrl+F` 搜索 `{API_DOMAIN_SEARCH_PREFIX}`，找到完整的 API URL。

预期答案: 在偏移 `0x007678F6` 找到 `https://{API_DOMAIN}/v1/common/network-profile`

### 练习 2: 确认 Go 版本

搜索 `Go buildinf` (hex: `47 6F 20 62 75 69 6C 64 69 6E 66`)，找到后往下读取版本号。

预期答案: `go1.25.0` 在偏移 `0x02DF9621`

### 练习 3: 找到协议关键词

搜索 `DEV`，观察周围的上下文。

预期答案: 在偏移 `0x0073AF23` 找到 `DEV/e//v/cf_*/*bgp;RR;RD`，一行包含了 User-Agent、路径模式、前缀和负载均衡模式。

### 练习 4: 计算节区偏移

`.text` 节区 RawPtr = `0x600`, `.rdata` 节区 RawPtr = `0x5B7C00`。两者之间差多少？

答案: `0x5B7C00 - 0x600 = 0x5B7600` = 5,993,984 字节 ≈ 5.7MB。这就是 `.text` 节区的大小（全部可执行代码）。

---

## 十三、关键发现总结

走完这一步你应该掌握:

- ✅ 用 HxD 打开大型二进制文件并快速导航
- ✅ 从 DOS 头找到 PE 头 (MZ → e_lfanew → PE\0\0)
- ✅ 手动读取 PE 字段（Machine, Magic, NumberOfSections）
- ✅ 定位节区并计算文件偏移
- ✅ 搜索 ASCII/Hex 字符串
- ✅ 识别反字符串搜索技术（逐字节构造 AAD）
- ✅ 识别加密常量（AES S-Box, ChaCha20 expand）
- ✅ 解析自定义二进制格式（decodeTXTBinaryPayload）
- ✅ 理解 Go 字符串在 hex 中的表现
- ✅ 知道 binary patch 的基本方法和限制

---

**回到**: [核心教学 README](./xtun-go-reverse-teaching-archive.md#source-core-16)

---

<a id="source-supplement-a4"></a>

> **编辑说明（A4；source-report）**：本篇是内存观察/Hook 教学与预期输出，不是已捕获的原始日志。“搜索到密钥即确认计算链”“SHA256/HKDF/X25519 返回值必为 RAX 指针”等不能直接采用：数组、slice、interface、多返回值须按具体 ABI 和机器码核验。内存区域、goroutine 栈与 GC 描述也不构成样本观测；只有开启 KeyLogWriter 才有相应 TLS key log 语义，设置环境变量本身不证明日志会产生。

# A4 · 补充 — 内存分析

---

## 目标

理解什么是运行时内存分析，判断 xTun 逆向中是否需要它，掌握 5 种内存分析工具的实操方法。

---

## 一、什么是内存分析

### 静态分析 vs 内存分析

| 维度 | 静态分析 | 内存分析（运行时分析） |
|------|----------|----------------------|
| 时机 | 程序没运行，直接看文件 | 程序正在运行，看进程内存 |
| 数据来源 | 磁盘上的 .exe / .so / .apk | 进程的虚拟地址空间 |
| 能看到什么 | 硬编码字符串、函数逻辑、常量 | 运行时生成的密钥、解密后的明文、动态变量 |
| 看不到什么 | 运行时才计算的值、网络返回的数据 | 已被 GC 回收或覆盖的数据 |
| 工具 | Ghidra、IDA、pefile、strings | CE、x64dbg、WinDbg、Frida、Process Hacker |

### 为什么有些数据只在内存中

1. **动态生成的密钥**：X25519 密钥对每次连接随机生成，磁盘上不存在
2. **派生密钥**：HKDF 派生的 AES/ChaCha20 密钥，只在运行时计算
3. **解密后的明文**：API 返回的加密配置解密后只在内存中
4. **网络数据**：服务器返回的响应体、WebSocket 帧内容
5. **TLS 会话密钥**：HTTPS 连接的对称密钥，握手后才存在

---

## 二、xTun 需要内存分析吗

### 结论：当前不需要，但将来可能需要

| 数据 | 是否需要内存分析 | 原因 |
|------|-----------------|------|
| payloadSecret | ❌ 不需要 | 硬编码在二进制中：`"{PAYLOAD_SECRET}"`，strings 就能提取 |
| AES 密钥 (Layer 2) | ❌ 不需要 | `SHA256(payloadSecret)` — payloadSecret 已知，可以离线计算 |
| X25519 密钥对 | ⚠️ 可选 | 每次连接随机生成，内存中能截获，但我们已经自己生成密钥对了 |
| HKDF 派生密钥 | ⚠️ 可选 | 可以自己算，不需要从内存抓 |
| 数据通道密钥 | ⚠️ 可选 | 握手时派生，我们已经完整实现了 |
| API Token (JWT) | ❌ 不需要 | 登录 API 就能拿到 |
| 节点配置 JSON | ❌ 不需要 | 两层解密已经实现 |

### 什么时候必须用内存分析

**如果将来 payloadSecret 从硬编码改为动态获取**（比如服务器下发、从 license 文件读取），那么：

1. 静态分析只能看到"从某处读取 payloadSecret"的逻辑，看不到值
2. 必须在运行时截获 payloadSecret 的实际值
3. 方法：Frida hook `SHA256()` 函数，打印输入参数

**如果 API 加了设备指纹 / 签名验证**：

1. 需要看运行时签名生成的完整参数
2. hook 签名函数，截获输入输出

---

## 三、工具介绍

| 工具 | 类型 | 免费？ | 适合场景 |
|------|------|--------|----------|
| **Cheat Engine (CE)** | 内存搜索/修改 | ✅ | 搜索已知字符串/值，内存扫描 |
| **Process Hacker** | 进程管理 + 内存查看 | ✅ | dump 进程内存，查看内存映射 |
| **x64dbg** | 动态调试器 | ✅ | 断点调试，寄存器查看，单步执行 |
| **WinDbg** | 微软官方调试器 | ✅ | 内核调试，crash dump 分析 |
| **Frida** | 动态 hook 框架 | ✅ | 运行时 hook 函数，截获参数/返回值 |

### 安装

```bash
# Cheat Engine
# 下载: https://www.cheatengine.org/downloads.php
# 安装时注意取消捆绑软件

# Process Hacker
# 下载: https://processhacker.sourceforge.io/
# 或者用 System Informer (新名)

# x64dbg
# 下载: https://x64dbg.com/
# 解压即用，无需安装

# Frida
pip install frida frida-tools
```

---

## 四、用 Cheat Engine 搜索内存

### 4.1 目标

在 xtun-windows.exe 的进程内存中搜索已知字符串 `"{PAYLOAD_SECRET}"`，确认它在运行时内存中的位置。

### 4.2 步骤

```
1. 启动 xtun-windows.exe（让它正常运行）
2. 启动 Cheat Engine
3. 点击左上角 [打开进程] 按钮（电脑图标）
4. 在进程列表中找到 xtun-windows.exe，双击选中
5. 搜索类型改为 [String]
6. 在搜索框输入: {PAYLOAD_SECRET}
7. 点击 [首次搜索 (First Scan)]
8. 等待搜索完成
```

### 4.3 预期结果

```
Found: 2-5 个地址

地址示例:
  0x00007FF6xxxxxxxx — .rdata 节区（静态字符串，和 strings 提取一样）
  0x000001E0xxxxxxxx — Go 堆内存（运行时拷贝）
```

### 4.4 怎么看搜到的地址

| 地址范围 | 含义 |
|----------|------|
| `0x140000000` 附近 | PE 镜像的 .rdata 节区（静态数据） |
| `0x000001xx` 或 `0x000002xx` 开头 | Go 堆分配（运行时动态分配） |
| 栈地址（随线程变化） | 函数局部变量或参数 |

### 4.5 搜索其他关键值

```
搜索 "cftun-txt"         → AAD 在内存中的位置
搜索 "cftun websocket v3" → 协议标识
搜索 "{API_DOMAIN}"     → API 域名
搜索 hex: {AES_KEY_HEX_PREFIX_8_BYTES} → AES 密钥的前 8 字节（SHA256 结果）
```

搜索 AES 密钥的十六进制值（`{AES_KEY_HEX_32_BYTES}`）：

```
1. CE 搜索类型改为 [Byte Array]
2. 输入: {AES_KEY_BYTES_PREFIX_8}
3. 搜索
```

如果搜到，说明程序确实在运行时计算了 `SHA256(payloadSecret)` 并在内存中持有 AES 密钥。

---

## 五、用 Process Hacker dump 进程内存

### 5.1 目标

将 xtun-windows.exe 的完整进程内存导出为文件，离线分析。

### 5.2 完整 dump

```
1. 启动 Process Hacker (以管理员权限)
2. 找到 xtun-windows.exe 进程
3. 右键 → Miscellaneous → Create dump file
4. 保存为 xtun_memdump.dmp
5. 文件大小约 200-500MB（包含所有映射的内存页）
```

### 5.3 查看内存映射

```
1. 双击 xtun-windows.exe 进程
2. 切换到 [Memory] 标签
3. 可以看到所有内存区域:
   - Image (PE 镜像)
   - Heap (堆)
   - Stack (栈，每个 goroutine 一个)
   - Mapped (内存映射文件)
   - Private (私有分配)
```

### 5.4 dump 指定区域

```
1. 在 Memory 标签中找到感兴趣的区域
2. 右键 → Save 或 Read/Write
3. 可以只 dump Go 堆区域（减小文件大小）
```

### 5.5 离线分析 dump 文件

```python
#!/usr/bin/env python3
"""analyze_dump.py — 在 dump 文件中搜索关键字符串"""

with open("xtun_memdump.dmp", "rb") as f:
    data = f.read()

targets = [
    b"{PAYLOAD_SECRET}",
    b"cftun-txt",
    b"cftun websocket v3",
    b"{AES_KEY_ESCAPED_BYTES_PREFIX_8}",  # AES key 前 8 字节
]

for t in targets:
    offsets = []
    start = 0
    while True:
        idx = data.find(t, start)
        if idx < 0: break
        offsets.append(hex(idx))
        start = idx + 1
    print(f"  '{t[:30]}...' → {len(offsets)} 处: {offsets[:5]}")
```

---

## 六、用 x64dbg 动态调试

### 6.1 目标

在 `decryptAccessPoint` 函数 (0x140365f60) 下断点，查看运行时的 AES 密钥和解密参数。

### 6.2 Attach 到进程

```
1. 启动 xtun-windows.exe
2. 启动 x64dbg (x96dbg.exe → 选择 x64)
3. File → Attach → 选择 xtun-windows.exe
4. 等待 attach 完成（程序会暂停）
5. 按 F9 让程序继续运行
```

### 6.3 下断点

```
1. 按 Ctrl+G (Go to address)
2. 输入: 0x140365f60
3. 回车跳到 decryptAccessPoint 函数入口
4. 按 F2 在当前地址设置断点（地址变红）
5. 按 F9 继续运行
6. 在 xTun 客户端里触发一个连接（会调用 decryptAccessPoint）
7. 断点命中！程序暂停在函数入口
```

### 6.4 查看寄存器和栈

Go 的调用约定（Go 1.17+ 使用寄存器传参）：

| 寄存器 | Go 用途 |
|--------|---------|
| RAX | 第 1 个参数 / 返回值 |
| RBX | 第 2 个参数 |
| RCX | 第 3 个参数 |
| RDI | 第 4 个参数 |
| RSI | 第 5 个参数 |
| R14 | goroutine 指针 (g) |
| RSP | 栈指针 |

```
断点命中时:
  RAX → access_point 字符串指针
  RBX → access_point 字符串长度
  RCX → payloadSecret 字符串指针
  RDI → payloadSecret 字符串长度

在右侧 [Dump] 窗口:
  右键 → Follow in dump → RAX
  → 可以看到 access_point 的 base64url 编码内容

  右键 → Follow in dump → RCX
  → 可以看到 "{PAYLOAD_SECRET}"
```

### 6.5 单步跟踪

```
F8 — Step Over (执行一条指令，不进入函数调用)
F7 — Step Into (执行一条指令，进入函数调用)
F9 — Run (继续运行到下一个断点)

跟踪 decryptAccessPoint 内部:
1. F7 进入函数
2. 找到 sha256 调用（CALL 指令）
3. 在 sha256 返回后查看 RAX → 应该是 32 字节 AES 密钥
4. 在 Dump 窗口 Follow RAX
5. 应该看到: {AES_KEY_BYTES_PREFIX_16}...
```

### 6.6 Go 二进制调试注意事项

| 问题 | 原因 | 解决 |
|------|------|------|
| 断点没命中 | Go 函数可能被内联 | 搜索 `sha256` 的 CALL 指令，在那里下断点 |
| 寄存器值看起来像指针 | Go 字符串是 (ptr, len) 对 | Follow ptr in dump，看 len 字节 |
| 栈上数据乱 | Go 用连续栈，和 C 不同 | 看 R14 指向的 goroutine 结构 |
| 程序卡死 | Go runtime 依赖 timer/GC | 不要暂停太久，Go GC 会超时 |

---

## 七、用 Frida 提取运行时密钥

### 7.1 目标

在 xtun-windows.exe 运行时 hook `crypto/sha256.Sum256`，截获输入（payloadSecret）和输出（AES 密钥）。

### 7.2 找到 SHA256 函数地址

```bash
# 方法1: strings 搜索
strings xtun-windows.exe | grep "crypto/sha256"

# 方法2: 在 Ghidra 中搜索
# Symbol Tree → 搜索 "sha256" → 找到 crypto/sha256.Sum256
# 记下地址，假设为 0x14XXXXXXX
```

### 7.3 Frida Hook 脚本

```javascript
// hook_sha256.js — Hook Go 的 SHA256，打印输入输出
// 用法: frida -p <pid> -l hook_sha256.js

// Go SHA256.Sum256 的地址（从 Ghidra 获取，需要替换）
var SHA256_ADDR = ptr("0x14XXXXXXX");  // 替换为实际地址

Interceptor.attach(SHA256_ADDR, {
    onEnter: function(args) {
        // Go 寄存器传参: RAX=数据指针, RBX=数据长度
        var dataPtr = this.context.rax;
        var dataLen = this.context.rbx.toInt32();

        if (dataLen > 0 && dataLen < 1024) {
            var data = Memory.readByteArray(dataPtr, dataLen);
            console.log("[SHA256] 输入 (" + dataLen + " bytes):");
            console.log("  hex: " + hexdump(data, {length: Math.min(dataLen, 64)}));

            // 尝试读为 UTF-8 字符串
            try {
                var str = Memory.readUtf8String(dataPtr, dataLen);
                console.log("  str: " + str);
            } catch(e) {}
        }
    },
    onLeave: function(retval) {
        // 返回值在 RAX (指向 32 字节 hash)
        var hashPtr = this.context.rax;
        var hash = Memory.readByteArray(hashPtr, 32);
        console.log("[SHA256] 输出 (32 bytes):");
        console.log("  " + hexdump(hash, {length: 32}));
    }
});

console.log("[*] SHA256 hook 已安装，等待调用...");
```

### 7.4 运行 Hook

```bash
# 1. 启动 xtun-windows.exe
# 2. 找到进程 PID
tasklist | findstr xtun

# 3. 运行 Frida
frida -p <PID> -l hook_sha256.js

# 4. 在 xTun 客户端中触发连接
# 5. 观察 Frida 输出
```

### 7.5 预期输出

```
[SHA256] 输入 (36 bytes):
  hex: {PAYLOAD_SECRET_HEX_DUMP_PART_1}
       {PAYLOAD_SECRET_HEX_DUMP_PART_2}
       {PAYLOAD_SECRET_HEX_DUMP_PART_3}
  str: {PAYLOAD_SECRET}
[SHA256] 输出 (32 bytes):
  {AES_KEY_BYTES_PREFIX_16}
  {AES_KEY_BYTES_SUFFIX_16}
```

这就确认了 AES 密钥 = `{AES_KEY_HEX_32_BYTES}`

### 7.6 Hook HKDF 提取数据通道密钥

```javascript
// hook_hkdf.js — Hook HKDF 派生
// HKDF 函数地址从 Ghidra 获取

var HKDF_EXPAND_ADDR = ptr("0x14XXXXXXX");  // 替换

Interceptor.attach(HKDF_EXPAND_ADDR, {
    onEnter: function(args) {
        // 打印 info 参数 (HKDF 的 info 字段包含方向字符串)
        // Go 参数通过寄存器传递，具体位置取决于函数签名
        console.log("[HKDF] 调用:");
    },
    onLeave: function(retval) {
        // 返回的 32 字节密钥
        var keyPtr = this.context.rax;
        if (keyPtr && !keyPtr.isNull()) {
            var key = Memory.readByteArray(keyPtr, 32);
            console.log("[HKDF] 派生密钥:");
            console.log("  " + hexdump(key, {length: 32}));
        }
    }
});
```

### 7.7 Hook X25519 密钥交换

```javascript
// hook_x25519.js — 截获 ECDH 共享密钥
// x25519.scalarMult 或类似函数

var X25519_ADDR = ptr("0x14XXXXXXX");  // 替换

Interceptor.attach(X25519_ADDR, {
    onLeave: function(retval) {
        // 共享密钥 = 32 字节
        var sharedPtr = this.context.rax;
        var shared = Memory.readByteArray(sharedPtr, 32);
        console.log("[X25519] 共享密钥:");
        console.log("  " + hexdump(shared, {length: 32}));
    }
});
```

---

## 八、Go 运行时内存布局

### 8.1 Go 进程的内存结构

```
低地址
  ┌─────────────────────┐
  │ .text  (代码段)     │  ← 可执行指令
  │ .rdata (只读数据)   │  ← 字符串常量、Go 类型信息
  │ .data  (可读写数据) │  ← 全局变量
  ├─────────────────────┤
  │ Go Heap             │  ← GC 管理的堆内存
  │  - mspan            │     分页管理
  │  - mcache           │     P-local 缓存
  │  - mcentral         │     全局缓存
  ├─────────────────────┤
  │ Goroutine Stacks    │  ← 每个 goroutine 独立的栈
  │  - 初始 8KB         │     按需增长（连续栈）
  │  - 最大 1GB         │
  ├─────────────────────┤
  │ OS Stacks           │  ← 系统线程栈
  │ TLS / Thread Local  │
  └─────────────────────┘
高地址
```

### 8.2 Go 字符串在内存中的样子

Go 字符串不是 C 风格的 null-terminated，而是 `(指针, 长度)` 对：

```
Go string 结构体 (16 字节):
  [8 字节] 指向字符数据的指针
  [8 字节] 字符串长度 (int)

例: "cftun-txt" 在内存中:
  指针 → 0x0000014000ABCDEF (指向 .rdata 中的 "cftun-txt")
  长度 → 0x0000000000000009 (9)

实际字符数据:
  0x14000ABCDEF: 63 66 74 75 6E 2D 74 78 74  (无 \0 终止)
```

### 8.3 Go GC 对内存分析的影响

| GC 行为 | 对内存分析的影响 |
|---------|-----------------|
| 标记-清除 | 不再引用的对象会被回收，搜索可能找不到 |
| 对象移动 | Go 1.x 不移动对象（不是压缩 GC），地址稳定 |
| 栈拷贝 | goroutine 栈增长时会拷贝到新位置，旧栈被释放 |
| 零化 | Go 不主动零化释放的内存，但新分配会覆盖 |

**实际影响**：密钥等短生命周期的 `[]byte` 在函数返回后很快会变成垃圾。需要在函数执行期间（用断点或 hook）截获，而不是事后在 dump 里搜。

### 8.4 怎么在内存中找 Go 对象

```
1. 搜索已知字符串 → 找到 .rdata 中的字符串常量
2. 搜索字符串指针 → 找到引用该字符串的 Go string 结构体
3. 查看结构体附近 → 可能是一个 Go struct 的字段
4. 从结构体推断上下文 → 确定是哪个变量/对象
```

---

## 九、TLS 密钥提取

### 9.1 为什么需要

xTun 的 API 通信走 HTTPS ({API_DOMAIN})。如果要用 Wireshark 看 API 请求/响应明文，需要 TLS 会话密钥。

### 9.2 方法 1: SSLKEYLOGFILE 环境变量

某些 Go 程序支持 `SSLKEYLOGFILE`（Go 1.8+ 的 `crypto/tls` 有 `KeyLogWriter` 字段）：

```bash
# 设置环境变量
set SSLKEYLOGFILE={LOCAL_PROJECT_DIR}/tls_keys.log

# 启动 xTun
xtun-windows.exe
```

但 xTun 可能没有设置 `KeyLogWriter`，这个方法不一定有效。

### 9.3 方法 2: Frida Hook crypto/tls

```javascript
// hook_tls.js — Hook Go 的 TLS 握手，提取主密钥

// crypto/tls.(*Conn).clientHandshake 的地址（从 Ghidra 获取）
var TLS_HANDSHAKE = ptr("0x14XXXXXXX");  // 替换

Interceptor.attach(TLS_HANDSHAKE, {
    onLeave: function(retval) {
        // TLS 连接对象在 RAX
        // masterSecret 是 tls.Conn 结构体的字段
        // 偏移量取决于 Go 版本，需要在 Ghidra 中确认
        console.log("[TLS] clientHandshake 完成");
    }
});
```

### 9.4 方法 3: mitmproxy 中间人

```bash
# 用 mitmproxy 代理 API 请求
pip install mitmproxy

# 启动代理
mitmproxy --mode regular -p 8888

# 配置 xTun 使用代理（可能需要 patch 或环境变量）
set HTTP_PROXY=http://{IPV4_ADDRESS_21}:8888
set HTTPS_PROXY=http://{IPV4_ADDRESS_21}:8888

# 安装 mitmproxy 的 CA 证书
# 但 Go 程序可能 pin 了证书，这个方法不一定有效
```

### 9.5 xTun 的情况

对于 xTun 逆向，我们**不需要** TLS 密钥提取，因为：
- API 请求格式已经通过静态分析确认
- 用 Python 直接调 API 就能看到请求和响应
- 加密配置的解密逻辑已经完全实现

TLS 密钥提取主要用于：你不确定客户端发了什么 HTTP 请求，需要 Wireshark 解密看明文。在 xTun 项目中，这是验证手段，不是必需。

---

## 十、内存分析的局限性

### 10.1 Go 特有的限制

| 限制 | 说明 |
|------|------|
| goroutine 栈拷贝 | 栈增长时整个栈拷贝到新地址，旧地址数据不可靠 |
| GC 回收 | 短生命周期对象（密钥 slice）在函数返回后很快被标记为垃圾 |
| 内存复用 | 新分配可能覆盖旧数据，搜索时序敏感 |
| 不确定的类型信息 | Go 的反射信息在 .rdata，但内存中的裸 []byte 没有类型标记 |
| defer/panic 栈展开 | 异常处理可能提前释放变量 |

### 10.2 通用限制

| 限制 | 说明 |
|------|------|
| 地址随机化 (ASLR) | Windows PE 基址每次加载可能不同，断点地址需要加偏移 |
| 反调试 | 有些程序检测 IsDebuggerPresent，xTun 目前没有 |
| 加壳/混淆 | 如果二进制加壳，内存中的代码和磁盘上不一样 |
| 多线程竞争 | Go 有大量 goroutine，内存状态在不断变化 |
| dump 太大 | 完整 dump 可能有几百 MB，搜索很慢 |

### 10.3 什么时候用什么工具

| 场景 | 推荐工具 |
|------|----------|
| 快速搜索已知字符串 | Cheat Engine |
| 完整内存快照 | Process Hacker dump |
| 函数级断点调试 | x64dbg |
| 截获函数参数/返回值 | Frida |
| 分析 TLS 流量 | Wireshark + SSLKEYLOGFILE |
| 分析 crash dump | WinDbg |

---

## 十一、实操练习

### 练习 1: 确认 AES 密钥在内存中

```
1. 启动 xtun-windows.exe，让它连接一个节点
2. 用 CE 搜索 hex: {AES_KEY_BYTES_PREFIX_8}
3. 记录找到的地址数量和位置
4. 结论: AES 密钥确实在运行时内存中
```

### 练习 2: Frida 验证 payloadSecret

```
1. 写 Frida 脚本 hook SHA256
2. attach 到 xtun-windows.exe
3. 触发节点连接
4. 观察 SHA256 的输入是不是 "{PAYLOAD_SECRET}"
5. 观察输出是不是 {AES_KEY_HEX_PREFIX_8_BYTES}...
```

### 练习 3: x64dbg 断点 decryptAccessPoint

```
1. attach x64dbg 到 xtun-windows.exe
2. 在 0x140365f60 下断点 (注意 ASLR 偏移)
3. 触发节点列表刷新
4. 断点命中后查看 RAX (access_point 指针)
5. 在 dump 窗口查看 access_point 内容
```

---

## 十二、关键发现总结

走完这一步你应该理解：

- ✅ 内存分析是运行时查看进程内存中的数据
- ✅ xTun 当前不需要内存分析（密钥已从静态分析获取）
- ✅ 如果 payloadSecret 变为动态，就必须用 Frida hook
- ✅ 5 种内存分析工具各自适用场景
- ✅ Go 运行时的内存布局和 GC 对分析的影响
- ✅ Go 字符串在内存中是 (指针, 长度) 对，不是 null-terminated

---

**回到**：[核心教学 README](./xtun-go-reverse-teaching-archive.md#source-core-16)

---

<a id="source-supplement-a5"></a>

> **编辑说明（A5；source-report）**：公开规范窄核对：Go 1.25.0 官方 ABIInternal 的 amd64 整数寄存器序列为 RAX、RBX、RCX、RDI、RSI、R8、R9、R10、R11，且明确 ABI 不稳定；这仅佐证规范，不佐证本篇函数原型、receiver、参数分解、内联、返回值或地址。见 [固定 tag 规范](https://github.com/golang/go/blob/go1.25.0/src/cmd/compile/abi-internal.md)。Hook 安装/打印“Hooked”不等于有效命中，也不等于参数读取正确；(string, error) 的 error 占 interface 字段，不能将其简化成单个 RCX。系统 connect/getaddrinfo/send 是否覆盖 Go 实际路径需独立证据，TLS 下系统 send 看到的通常不是 HTTP 明文；本篇 ClientHello 示例不提供通用完整解析器。Frida API、CLI 与 frida-tools 兼容性未测试，保留历史示例但不声称可直接运行。10.3 节仍含点分 Host 与“CDN IP”早期预期，须连同 A8 末段修正阅读。

# A5 · 补充 — Frida 动态 Hook 完整教学

---

## 目标

用 Frida 在运行时 hook xTun 的加密函数和网络连接函数，截获明文数据、密钥、连接参数。Frida 是逆向工程中验证静态分析结论、发现运行时行为的核心工具。在本项目中，websocket 类型节点最终通过静态分析 + DNS 验证攻破（见 [A8](#source-supplement-a8)），但 Frida 方法同样适用于类似的逆向场景。

---

## 一、Frida 是什么

Frida 是一个动态代码注入框架。它能在目标进程运行时注入 JavaScript 脚本，hook 任意函数，读写内存，修改行为——不需要源码，不需要重新编译。

| 特性 | 说明 |
|------|------|
| 平台 | Windows / macOS / Linux / Android / iOS |
| 注入方式 | attach（挂载到已运行进程）或 spawn（启动并注入） |
| 脚本语言 | JavaScript（V8 引擎，运行在目标进程内） |
| 驱动端 | Python / Node.js / CLI（frida 命令行） |
| 核心 API | Interceptor（hook 函数）、Memory（读写内存）、NativeFunction（调用原生函数） |

**为什么用 Frida 而不是调试器（x64dbg/WinDbg）？**

1. Go 二进制的调试器支持很差（栈结构不同、协程切换频繁）
2. Frida 脚本化，可以批量 hook 几十个函数同时记录
3. 不需要断点暂停，不会中断程序运行
4. 输出结构化数据（JSON），方便后续分析

---

## 二、安装

### 2.1 安装 Frida

```bash
pip install frida frida-tools
```

### 2.2 验证

```bash
frida --version
# 预期: 16.x.x 或更高

frida-ps
# 列出当前运行的进程，确认 Frida 可以枚举进程
```

### 2.3 常见安装问题

| 问题 | 解决 |
|------|------|
| `pip install frida` 编译失败 | 用 `pip install frida --no-build-isolation`，或升级 pip |
| `frida-ps` 报权限错误 | 以管理员身份运行 PowerShell |
| 版本不匹配 | `frida` 和 `frida-tools` 版本必须一致，`pip install frida==16.x.x frida-tools==12.x.x` |

---

## 三、基本概念

### 3.1 Agent 脚本

Frida 脚本是 JavaScript，运行在目标进程的地址空间内。你可以直接访问目标进程的内存。

```javascript
// hook.js — 最简单的 Frida 脚本
console.log("[*] Frida agent loaded, PID:", Process.id);
console.log("[*] Module base:", Process.enumerateModules()[0].base);
```

### 3.2 Attach vs Spawn

| 模式 | 命令 | 适用场景 |
|------|------|----------|
| **Attach** | `frida -p <pid> -l hook.js` | 目标已经在运行，挂载上去 |
| **Spawn** | `frida -f xtun-windows.exe -l hook.js` | 由 Frida 启动目标，注入后再恢复执行 |

**Attach** 适合 hook 运行中的函数调用（比如点击连接按钮后截获参数）。
**Spawn** 适合 hook 初始化阶段的函数（比如配置加载）。

### 3.3 Interceptor vs NativeFunction

| API | 用途 |
|-----|------|
| `Interceptor.attach(addr, { onEnter, onLeave })` | 在函数入口/出口插入回调，不改变原函数行为 |
| `Interceptor.replace(addr, impl)` | 用自定义实现替换原函数 |
| `new NativeFunction(addr, retType, argTypes)` | 把地址当函数调用（主动调用原生函数） |

本教学主要用 `Interceptor.attach`——只观察，不修改。

---

## 四、连接到 xtun-windows.exe

### 4.1 CLI 方式（推荐入门）

```bash
# 步骤 1: 启动 xTun 客户端（正常双击打开）
# 步骤 2: 找到 PID
frida-ps | grep -i xtun
# 输出类似: 12345  xtun-windows.exe

# 步骤 3: attach 并加载脚本
frida -p 12345 -l hook.js
```

或者用 Spawn 模式：

```bash
frida -f "{LOCAL_PROJECT_DIR}/xtun-windows.exe" -l hook.js --no-pause
```

`--no-pause` 表示注入后立即恢复执行（不暂停在入口）。

### 4.2 Python 驱动方式（推荐实战）

```python
#!/usr/bin/env python3
"""frida_driver.py — Python 驱动 Frida hook xTun"""
import frida, sys, json

def on_message(message, data):
    """接收 Agent 脚本发来的消息"""
    if message['type'] == 'send':
        payload = message['payload']
        if isinstance(payload, dict):
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(f"[Agent] {payload}")
    elif message['type'] == 'error':
        print(f"[ERROR] {message['stack']}")

# 方式 A: attach 到已运行的进程
pid = int(input("输入 xtun-windows.exe 的 PID: "))
session = frida.attach(pid)

# 方式 B: spawn 启动
# session = frida.spawn(["{LOCAL_PROJECT_DIR}/xtun-windows.exe"])

# 加载 Agent 脚本
with open("hook.js", "r", encoding="utf-8") as f:
    script_code = f.read()

script = session.create_script(script_code)
script.on('message', on_message)
script.load()

print("[*] Hook 已加载，按 Ctrl+C 退出")
try:
    sys.stdin.read()
except KeyboardInterrupt:
    print("\n[*] 正在卸载...")
    session.detach()
```

### 4.3 找到模块基址

Go 编译的 PE 默认基址是 `0x140000000`，但 ASLR 可能改变它。用 Frida 确认：

```javascript
// check_base.js — 确认模块基址
var mod = Process.enumerateModules()[0];
console.log("Module:", mod.name);
console.log("Base:  ", mod.base);
console.log("Size:  ", mod.size);

// Go PE64 默认基址 0x140000000
// 如果 ASLR 生效，实际基址可能不同
// Ghidra 中的地址需要做偏移修正:
//   实际地址 = Ghidra地址 - 0x140000000 + mod.base
```

---

## 五、Hook Go 函数

### 5.1 地址计算

Ghidra 中看到的函数地址是基于 ImageBase=`0x140000000` 的虚拟地址。如果 ASLR 生效，需要修正：

```javascript
// addr_helper.js — 地址修正工具
var GHIDRA_BASE = ptr("0x140000000");
var ACTUAL_BASE = Process.enumerateModules()[0].base;
var OFFSET = ACTUAL_BASE.sub(GHIDRA_BASE);

function ghidra(addr) {
    // 将 Ghidra 地址转换为运行时地址
    return ptr(addr).add(OFFSET);
}

// 示例: decryptAccessPoint 在 Ghidra 中是 0x140365f60
var decryptAP = ghidra("0x140365f60");
console.log("decryptAccessPoint @", decryptAP);
```

### 5.2 读取 Go 字符串

**Go 字符串不是 C 字符串。** Go 字符串是 `(指针, 长度)` 结构，没有 null 终止符。

```javascript
// go_string.js — 读取 Go 字符串的辅助函数

function readGoString(ptrAddr, lenAddr) {
    /**
     * Go 字符串在寄存器/栈上的传递方式:
     *   参数1 = 字符串指针 (8 字节)
     *   参数2 = 字符串长度 (8 字节)
     * 或者作为结构体:
     *   [0:8]  = 指针
     *   [8:16] = 长度
     */
    var strPtr = ptr(ptrAddr);
    var strLen = parseInt(lenAddr);
    if (strLen <= 0 || strLen > 65536) return "<invalid>";
    try {
        return strPtr.readUtf8String(strLen);
    } catch (e) {
        return "<read error: " + e + ">";
    }
}

function readGoStringFromStack(sp, offset) {
    /**
     * 从栈上读取 Go 字符串
     * Go 的调用约定（Go 1.17+ register ABI on amd64）:
     *   前几个参数通过寄存器传递: RAX, RBX, RCX, RDI, RSI, R8, R9, R10, R11
     *   溢出参数通过栈传递
     */
    var strPtr = sp.add(offset).readPointer();
    var strLen = sp.add(offset + 8).readU64();
    return readGoString(strPtr, strLen);
}

function readGoStringStruct(addr) {
    /**
     * 从内存中读取 Go string 结构体
     * struct { ptr uintptr; len int }
     */
    var strPtr = addr.readPointer();
    var strLen = addr.add(8).readU64();
    return readGoString(strPtr, strLen);
}
```

### 5.3 Go 调用约定（关键）

Go 1.17+ 在 amd64 上使用寄存器传参（register-based ABI）：

| 寄存器 | 用途 |
|--------|------|
| RAX | 第 1 个参数 / 第 1 个返回值 |
| RBX | 第 2 个参数 / 第 2 个返回值 |
| RCX | 第 3 个参数 |
| RDI | 第 4 个参数 |
| RSI | 第 5 个参数 |
| R8-R11 | 第 6-9 个参数 |
| RSP+8, RSP+16... | 溢出参数（栈传递） |

**Go 字符串作为参数传递时占两个参数位（指针+长度）：**

```
func decryptAccessPoint(accessPoint string, payloadSecret string)
→ RAX = accessPoint.ptr
  RBX = accessPoint.len
  RCX = payloadSecret.ptr
  RDI = payloadSecret.len
```

### 5.4 Hook decryptAccessPoint

```javascript
// hook_decrypt_ap.js — Hook access_point 解密函数
// decryptAccessPoint @ 0x140365f60 (txt_cipher.go:39)
// func decryptAccessPoint(accessPoint string, payloadSecret string) (string, error)

var GHIDRA_BASE = ptr("0x140000000");
var ACTUAL_BASE = Process.enumerateModules()[0].base;
var OFFSET = ACTUAL_BASE.sub(GHIDRA_BASE);

function ghidra(addr) { return ptr(addr).add(OFFSET); }

Interceptor.attach(ghidra("0x140365f60"), {
    onEnter: function(args) {
        // Go 1.17+ register ABI:
        //   RAX = accessPoint.ptr
        //   RBX = accessPoint.len
        //   RCX = payloadSecret.ptr
        //   RDI = payloadSecret.len
        var apPtr = this.context.rax;
        var apLen = this.context.rbx.toInt32();
        var psPtr = this.context.rcx;
        var psLen = this.context.rdi.toInt32();

        var accessPoint = "<too long>";
        if (apLen > 0 && apLen < 4096) {
            try { accessPoint = ptr(apPtr).readUtf8String(apLen); } catch(e) {}
        }
        var payloadSecret = "<error>";
        if (psLen > 0 && psLen < 256) {
            try { payloadSecret = ptr(psPtr).readUtf8String(psLen); } catch(e) {}
        }

        this.apStr = accessPoint;
        send({
            type: "decryptAccessPoint_enter",
            access_point: accessPoint.substring(0, 80) + (accessPoint.length > 80 ? "..." : ""),
            access_point_len: apLen,
            payload_secret: payloadSecret,
            payload_secret_len: psLen
        });
    },
    onLeave: function(retval) {
        // 返回值: (string, error) → RAX=result.ptr, RBX=result.len
        var resultPtr = this.context.rax;
        var resultLen = this.context.rbx.toInt32();
        var result = "<error>";
        if (resultLen > 0 && resultLen < 4096) {
            try { result = ptr(resultPtr).readUtf8String(resultLen); } catch(e) {}
        }
        send({
            type: "decryptAccessPoint_leave",
            result: result,
            result_len: resultLen
        });
    }
});

console.log("[+] Hooked decryptAccessPoint @ " + ghidra("0x140365f60"));
```

### 5.5 Hook PayloadSecret 读取

```javascript
// hook_payload_secret.js
// (*Websocket).PayloadSecret @ 0x140349220 (dialer.go:707)
// func (w *Websocket) PayloadSecret() string

Interceptor.attach(ghidra("0x140349220"), {
    onEnter: function(args) {
        // Go 方法: RAX = receiver (w *Websocket)
        this.receiver = this.context.rax;
    },
    onLeave: function(retval) {
        // 返回 string: RAX=ptr, RBX=len
        var ptr_ = this.context.rax;
        var len_ = this.context.rbx.toInt32();
        var secret = "<error>";
        if (len_ > 0 && len_ < 256) {
            try { secret = ptr(ptr_).readUtf8String(len_); } catch(e) {}
        }
        send({
            type: "PayloadSecret",
            value: secret,
            length: len_,
            receiver: this.receiver.toString()
        });
    }
});

console.log("[+] Hooked PayloadSecret @ " + ghidra("0x140349220"));
```

### 5.6 Hook AES-GCM 解密

```javascript
// hook_aes_gcm.js — Hook Go crypto/cipher AEAD.Open
// 需要找到 crypto/cipher.gcmAble.Open 的实际地址
// 在 Ghidra 中搜索 "gcm" 相关函数

// 方法: Hook crypto/aes 的 NewCipher 来截获 AES key
// 然后 Hook gcm.Open 来截获 nonce/ciphertext/plaintext

// 简化方法: 直接 Hook DecryptResponse (Layer 1 解密入口)
// DecryptResponse @ 0x1404eaec0 (config_response_crypto.go:89)

Interceptor.attach(ghidra("0x1404eaec0"), {
    onEnter: function(args) {
        send({type: "DecryptResponse_enter", note: "Layer 1 配置响应解密开始"});
        // 参数是 ConfigResponseEnvelope 结构体
        // 具体布局需要看 Ghidra 反编译
    },
    onLeave: function(retval) {
        // 返回解密后的 JSON 配置
        var resultPtr = this.context.rax;
        var resultLen = this.context.rbx.toInt32();
        if (resultLen > 0 && resultLen < 1048576) {
            try {
                var result = ptr(resultPtr).readUtf8String(Math.min(resultLen, 2000));
                send({
                    type: "DecryptResponse_leave",
                    plaintext_preview: result,
                    total_len: resultLen
                });
            } catch(e) {
                send({type: "DecryptResponse_leave", error: e.toString()});
            }
        }
    }
});

console.log("[+] Hooked DecryptResponse @ " + ghidra("0x1404eaec0"));
```

---

## 六、Hook WebSocket 连接

**这是攻破 websocket 类型节点的关键。** 我们需要截获真实客户端连接 websocket 类型节点时的完整 HTTP 请求。

### 6.1 Hook connectWithPurpose

```javascript
// hook_connect.js — Hook WebSocket 连接建立
// connectWithPurpose @ 0x14034afc0 (dialer.go:1019)

Interceptor.attach(ghidra("0x14034afc0"), {
    onEnter: function(args) {
        send({type: "connectWithPurpose_enter", note: "WebSocket 连接开始"});
        // 需要读取函数内部使用的 URL, Headers
        // 这个函数内部会调用 gorilla dialer
    },
    onLeave: function(retval) {
        send({type: "connectWithPurpose_leave"});
    }
});
```

### 6.2 Hook gorilla/websocket Dialer

gorilla/websocket 的 `Dialer.DialContext` 是实际发起 WebSocket 升级的函数。在 Ghidra 中搜索 `gorilla/websocket` 相关函数找到地址。

```javascript
// hook_gorilla_dial.js — Hook gorilla WebSocket Dialer
// 需要先在 Ghidra 中找到 gorilla/websocket.(*Dialer).DialContext 的地址
// 搜索字符串 "gorilla/websocket" 的交叉引用

// 假设地址为 GORILLA_DIAL_ADDR（需要从 Ghidra 确认）
// var GORILLA_DIAL_ADDR = "0x14XXXXXXX";

// 替代方案: Hook net/http.(*Transport).RoundTrip
// 这是所有 HTTP 请求的最终出口，包括 WebSocket 升级请求

// 在 Ghidra 中搜索 "net/http.(*Transport).RoundTrip"
// 或搜索字符串 "Upgrade" 的交叉引用

// 更可靠的方法: Hook net.(*Dialer).DialContext — TCP 连接层
// 这样可以看到实际连接的 IP:port

// 搜索 Ghidra 中的 net.(*Dialer).DialContext 或 net.Dial
```

### 6.3 Hook TCP 连接（net.Dial）

```javascript
// hook_net_dial.js — Hook TCP 连接
// 在 Ghidra 中搜索 "net.(*Dialer).DialContext" 或 "net.Dial"
// Go 标准库函数也在二进制中（静态链接）

// 方法: 搜索 Ghidra 函数列表中包含 "net.Dial" 的函数
// 通常地址可以通过以下方式找到:
//   1. Ghidra Symbol Tree → 搜索 "Dial"
//   2. strings xtun-windows.exe | grep "net.Dial"

// 假设找到 net.(*Dialer).DialContext 的地址:
// Interceptor.attach(ghidra("0x14XXXXXXX"), { ... });

// 备用: Hook Windows API connect()
var connect = Module.getExportByName("ws2_32.dll", "connect");
Interceptor.attach(connect, {
    onEnter: function(args) {
        var sockfd = args[0].toInt32();
        var addrPtr = args[1];
        var addrLen = args[2].toInt32();

        // 解析 sockaddr_in
        var family = addrPtr.readU16();
        if (family === 2) { // AF_INET
            var port = (addrPtr.add(2).readU8() << 8) | addrPtr.add(3).readU8();
            var ip = addrPtr.add(4).readU8() + "." +
                     addrPtr.add(5).readU8() + "." +
                     addrPtr.add(6).readU8() + "." +
                     addrPtr.add(7).readU8();
            send({
                type: "tcp_connect",
                ip: ip,
                port: port,
                socket: sockfd
            });
        }
    }
});

console.log("[+] Hooked ws2_32!connect");
```

### 6.4 Hook DNS 解析

```javascript
// hook_dns.js — Hook DNS 解析
// 截获 xTun 解析 {POOL_DOMAIN_A} 等域名时的结果

var getaddrinfo = Module.getExportByName("ws2_32.dll", "getaddrinfo");
Interceptor.attach(getaddrinfo, {
    onEnter: function(args) {
        this.hostname = args[0].readAnsiString();
        this.service = args[1].isNull() ? null : args[1].readAnsiString();
        if (this.hostname) {
            send({
                type: "dns_query",
                hostname: this.hostname,
                service: this.service
            });
        }
    },
    onLeave: function(retval) {
        if (retval.toInt32() === 0 && this.hostname) {
            // 成功，解析结果在 *result 参数中
            send({
                type: "dns_result",
                hostname: this.hostname,
                status: "success"
            });
        } else if (this.hostname) {
            send({
                type: "dns_result",
                hostname: this.hostname,
                status: "failed",
                error_code: retval.toInt32()
            });
        }
    }
});

console.log("[+] Hooked ws2_32!getaddrinfo");
```

### 6.5 Hook TLS 握手

```javascript
// hook_tls.js — Hook TLS SNI
// Go 的 TLS 实现在二进制内部（静态链接）
// 但底层仍调用 Windows Schannel 或 Go 自己的 TLS

// 方法 1: Hook Go crypto/tls 内部
// 在 Ghidra 中搜索 "crypto/tls.(*Conn).Handshake"

// 方法 2: Hook 发送的 ClientHello 数据
// TLS ClientHello 的 SNI 在固定偏移处

// 方法 3: Hook Windows API (如果 Go 使用 Schannel)
// 通常 Go 不使用 Schannel，使用自己的 TLS 实现

// 最可靠: Hook send() 捕获 ClientHello
var send_func = Module.getExportByName("ws2_32.dll", "send");
Interceptor.attach(send_func, {
    onEnter: function(args) {
        var buf = args[1];
        var len = args[2].toInt32();

        if (len > 5) {
            var contentType = buf.readU8();
            // TLS ClientHello: content_type=0x16, version=0x0301/0x0303
            if (contentType === 0x16) {
                var version = buf.add(1).readU16();
                var msgType = buf.add(5).readU8();
                if (msgType === 0x01) { // ClientHello
                    // 解析 SNI (在 extensions 中)
                    var data = buf.readByteArray(Math.min(len, 512));
                    send({
                        type: "tls_client_hello",
                        length: len,
                        hex_preview: Array.from(new Uint8Array(data)).map(
                            b => b.toString(16).padStart(2, '0')).join(' ').substring(0, 200)
                    });
                }
            }
        }
    }
});

console.log("[+] Hooked ws2_32!send (TLS ClientHello detection)");
```

### 6.6 Hook HTTP 请求发送（捕获完整 WebSocket 升级请求）

```javascript
// hook_http_send.js — 截获发送的 HTTP 请求
// 这是最直接的方法: 看 xTun 实际发送了什么 HTTP 头

var send_func = Module.getExportByName("ws2_32.dll", "send");
Interceptor.attach(send_func, {
    onEnter: function(args) {
        var buf = args[1];
        var len = args[2].toInt32();

        if (len > 4 && len < 8192) {
            try {
                var data = buf.readUtf8String(Math.min(len, 2000));
                // 检测 HTTP 请求
                if (data && (data.startsWith("GET ") || data.startsWith("POST ") ||
                             data.startsWith("CONNECT "))) {
                    send({
                        type: "http_request",
                        length: len,
                        data: data
                    });
                }
                // 检测 WebSocket 升级
                if (data && data.indexOf("Upgrade: websocket") !== -1) {
                    send({
                        type: "websocket_upgrade",
                        length: len,
                        request: data
                    });
                }
            } catch(e) {
                // 不是 UTF-8 文本（可能是二进制/TLS 数据）
            }
        }
    }
});

console.log("[+] Hooked ws2_32!send (HTTP request capture)");
```

---

## 七、读取 Go 字符串（深入）

### 7.1 Go 字符串内存布局

```
Go string 在内存中:
  [8 bytes] 指向字符数据的指针
  [8 bytes] 长度（不含 null）

Go slice 在内存中:
  [8 bytes] 指向数据的指针
  [8 bytes] 长度
  [8 bytes] 容量
```

### 7.2 从结构体中读取

```javascript
function readGoStringFromMemory(addr) {
    var strPtr = addr.readPointer();
    var strLen = addr.add(8).readS64();
    if (strLen <= 0 || strLen > 1048576) return null;
    return strPtr.readUtf8String(Number(strLen));
}

function readGoSlice(addr) {
    var dataPtr = addr.readPointer();
    var length = addr.add(8).readS64();
    var capacity = addr.add(16).readS64();
    return { ptr: dataPtr, len: Number(length), cap: Number(capacity) };
}

function readGoBytes(addr, maxLen) {
    var slice = readGoSlice(addr);
    if (slice.len <= 0 || slice.len > (maxLen || 65536)) return null;
    return slice.ptr.readByteArray(slice.len);
}
```

### 7.3 Go map 和 struct 的读取

Go 的 map 和 struct 布局比较复杂，通常不直接读取。更好的方法是 hook 访问这些结构的函数，从函数参数/返回值中获取数据。

---

## 八、Hook 返回值

### 8.1 onLeave 回调

```javascript
Interceptor.attach(targetAddr, {
    onEnter: function(args) {
        // 保存输入参数供 onLeave 使用
        this.inputParam = this.context.rax;
    },
    onLeave: function(retval) {
        // Go 1.17+ register ABI:
        // 返回值通过寄存器: RAX (第1个), RBX (第2个), RCX (第3个)
        var result1 = this.context.rax;  // 第一个返回值
        var result2 = this.context.rbx;  // 第二个返回值

        // 对于返回 (string, error) 的函数:
        // RAX = string.ptr
        // RBX = string.len
        // RCX = error (interface, 16 bytes: type ptr + data ptr)
    }
});
```

### 8.2 注意: retval 参数

在 Go 函数中，`retval` 参数（Frida 传给 onLeave 的）通常不可靠，因为 Go 不遵循 C 调用约定。直接读 `this.context.rax/rbx/rcx` 更准确。

---

## 九、Python 驱动脚本

### 9.1 完整驱动脚本

```python
#!/usr/bin/env python3
"""frida_xtun_capture.py — 用 Frida 截获 xTun 的连接参数和加密数据"""
import frida, sys, json, time, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Agent 脚本 ──
AGENT_CODE = """
'use strict';

var GHIDRA_BASE = ptr("0x140000000");
var ACTUAL_BASE = Process.enumerateModules()[0].base;
var OFFSET = ACTUAL_BASE.sub(GHIDRA_BASE);
function ghidra(addr) { return ptr(addr).add(OFFSET); }

console.log("[*] xTun Agent loaded");
console.log("[*] Module base: " + ACTUAL_BASE);
console.log("[*] ASLR offset: " + OFFSET);

// ── 1. Hook TCP connect ──
var ws2_connect = Module.getExportByName("ws2_32.dll", "connect");
Interceptor.attach(ws2_connect, {
    onEnter: function(args) {
        var addrPtr = args[1];
        var family = addrPtr.readU16();
        if (family === 2) {
            var port = (addrPtr.add(2).readU8() << 8) | addrPtr.add(3).readU8();
            var ip = addrPtr.add(4).readU8() + "." +
                     addrPtr.add(5).readU8() + "." +
                     addrPtr.add(6).readU8() + "." +
                     addrPtr.add(7).readU8();
            if (port === 80 || port === 443) {
                send({type: "tcp_connect", ip: ip, port: port});
            }
        }
    }
});

// ── 2. Hook DNS ──
var getaddrinfo = Module.getExportByName("ws2_32.dll", "getaddrinfo");
Interceptor.attach(getaddrinfo, {
    onEnter: function(args) {
        this.host = args[0].isNull() ? null : args[0].readAnsiString();
    },
    onLeave: function(retval) {
        if (this.host && this.host.length > 0) {
            send({type: "dns", hostname: this.host, result: retval.toInt32()});
        }
    }
});

// ── 3. Hook HTTP send ──
var ws2_send = Module.getExportByName("ws2_32.dll", "send");
Interceptor.attach(ws2_send, {
    onEnter: function(args) {
        var len = args[2].toInt32();
        if (len > 10 && len < 8192) {
            try {
                var data = args[1].readUtf8String(Math.min(len, 4000));
                if (data && data.indexOf("Upgrade: websocket") !== -1) {
                    send({type: "ws_upgrade", request: data});
                } else if (data && (data.startsWith("GET ") || data.startsWith("POST "))) {
                    send({type: "http", request: data.substring(0, 500)});
                }
            } catch(e) {}
        }
    }
});

// ── 4. Hook decryptAccessPoint ──
try {
    Interceptor.attach(ghidra("0x140365f60"), {
        onEnter: function(args) {
            var apLen = this.context.rbx.toInt32();
            var psLen = this.context.rdi.toInt32();
            var ap = "", ps = "";
            try { if (apLen > 0 && apLen < 4096) ap = ptr(this.context.rax).readUtf8String(apLen); } catch(e) {}
            try { if (psLen > 0 && psLen < 256) ps = ptr(this.context.rcx).readUtf8String(psLen); } catch(e) {}
            send({type: "decrypt_ap", access_point: ap.substring(0, 80), payload_secret: ps});
        }
    });
    console.log("[+] Hooked decryptAccessPoint");
} catch(e) {
    console.log("[-] Failed to hook decryptAccessPoint: " + e);
}

// ── 5. Hook PayloadSecret ──
try {
    Interceptor.attach(ghidra("0x140349220"), {
        onLeave: function(retval) {
            var len = this.context.rbx.toInt32();
            if (len > 0 && len < 256) {
                try {
                    var s = ptr(this.context.rax).readUtf8String(len);
                    send({type: "payload_secret", value: s});
                } catch(e) {}
            }
        }
    });
    console.log("[+] Hooked PayloadSecret");
} catch(e) {
    console.log("[-] Failed to hook PayloadSecret: " + e);
}

console.log("[+] All hooks installed. Waiting for activity...");
"""

class XTunCapture:
    def __init__(self):
        self.events = []
        self.ws_upgrades = []

    def on_message(self, message, data):
        if message['type'] == 'send':
            payload = message['payload']
            self.events.append(payload)
            evt_type = payload.get('type', '?')

            if evt_type == 'tcp_connect':
                print(f"  [TCP] {payload['ip']}:{payload['port']}")
            elif evt_type == 'dns':
                status = "OK" if payload['result'] == 0 else f"FAIL({payload['result']})"
                print(f"  [DNS] {payload['hostname']} → {status}")
            elif evt_type == 'ws_upgrade':
                print(f"  [WS]  WebSocket Upgrade Request:")
                for line in payload['request'].split('\\r\\n')[:10]:
                    print(f"        {line}")
                self.ws_upgrades.append(payload['request'])
            elif evt_type == 'http':
                print(f"  [HTTP] {payload['request'][:100]}")
            elif evt_type == 'decrypt_ap':
                print(f"  [DECRYPT] AP={payload['access_point'][:40]}... PS={payload['payload_secret']}")
            elif evt_type == 'payload_secret':
                print(f"  [SECRET] PayloadSecret = {payload['value']}")
            else:
                print(f"  [{evt_type}] {json.dumps(payload, ensure_ascii=False)[:120]}")

        elif message['type'] == 'error':
            print(f"  [ERROR] {message.get('stack', message)}")

    def run(self):
        print("=" * 60)
        print("  xTun Frida Capture")
        print("=" * 60)
        print()

        # 查找进程
        try:
            device = frida.get_local_device()
            procs = [p for p in device.enumerate_processes() if 'xtun' in p.name.lower()]
        except Exception as e:
            print(f"[-] Frida 错误: {e}")
            return

        if procs:
            print(f"[+] 找到 xTun 进程: PID={procs[0].pid} ({procs[0].name})")
            session = frida.attach(procs[0].pid)
        else:
            print("[-] 未找到 xTun 进程")
            choice = input("是否启动 xTun? (y/n): ").strip().lower()
            if choice == 'y':
                exe = input("xTun 路径 [{LOCAL_PROJECT_DIR}/xtun-windows.exe]: ").strip()
                if not exe:
                    exe = "{LOCAL_PROJECT_DIR}/xtun-windows.exe"
                pid = frida.spawn([exe])
                session = frida.attach(pid)
                frida.resume(pid)
            else:
                return

        script = session.create_script(AGENT_CODE)
        script.on('message', self.on_message)
        script.load()

        print()
        print("[+] Hook 已安装，现在去 xTun 客户端连接一个节点...")
        print("[+] 特别是: 连接一个 websocket 类型节点（东京/新加坡/法兰克福等）")
        print("[+] 按 Ctrl+C 停止")
        print()

        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print(f"\\n[+] 捕获完成，共 {len(self.events)} 个事件")
            print(f"[+] 其中 WebSocket 升级请求: {len(self.ws_upgrades)} 个")

            # 保存结果
            out_path = os.path.join(SCRIPT_DIR, "frida_capture_result.json")
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "capture_time": time.strftime('%Y-%m-%dT%H:%M:%S'),
                    "events": self.events,
                    "ws_upgrades": self.ws_upgrades
                }, f, ensure_ascii=False, indent=2)
            print(f"[+] 结果已保存: {out_path}")

            session.detach()

if __name__ == "__main__":
    XTunCapture().run()
```

### 9.2 运行方法

```bash
# 1. 先启动 xTun 客户端
# 2. 运行 Frida 捕获脚本（管理员权限）
python frida_xtun_capture.py

# 3. 在 xTun 客户端中:
#    - 连接一个 websocket 类型节点（如{NODE_LABEL_01}）
#    - 等待连接完成
#    - 观察控制台输出

# 4. Ctrl+C 停止，查看 frida_capture_result.json
```

---

## 十、实战: 验证 websocket 类型节点连接参数

**背景**: websocket 类型节点最终通过 Ghidra 静态分析 + DNS 验证攻破（DomainPool Host 格式 + Cloudflare 边缘路由，见 [A8](#source-supplement-a8)）。以下展示如何用 Frida 动态验证这些发现——当静态分析结论不确定时，Frida hook 是最可靠的验证手段。

### 10.1 需要截获的信息

| 信息 | 为什么需要 | 怎么截获 |
|------|-----------|----------|
| 实际 TCP 连接目标 | CDN IP 还是其他 IP? | Hook ws2_32!connect |
| DNS 解析 | {POOL_DOMAIN_A} 解析到什么 IP? | Hook ws2_32!getaddrinfo |
| Host 头 | 域名格式还是 IP? | Hook ws2_32!send 看 HTTP 请求 |
| Path | / 还是其他路径? | Hook ws2_32!send |
| TLS/SNI | 是否用 WSS? SNI 是什么? | Hook ClientHello |
| 子协议 | 有没有 Sec-WebSocket-Protocol? | Hook ws2_32!send |

### 10.2 步骤

1. 启动 xTun 客户端
2. 运行 `frida_xtun_capture.py`
3. 在 xTun 中选择一个 websocket 类型节点（{NODE_LABEL_01} 等）
4. 点击连接
5. 观察 Frida 输出:
   - `[DNS]` 行 — 看是否解析了 {POOL_DOMAIN_A}
   - `[TCP]` 行 — 看连接了哪个 IP:port
   - `[WS]` 行 — 看完整的 WebSocket 升级请求

6. 用截获的参数更新 `cftun_proxy.py`

### 10.3 预期发现

根据 Ghidra 反编译，websocket 类型节点应该:

1. **DNS**: 解析 `{REVERSED_VIRTUAL_IP_DOTTED_16}.{POOL_DOMAIN_A}`（DomainPool 格式）
   - 可能通过 Cloudflare DNS ({IPV4_ADDRESS_22})
   - 可能得到 Cloudflare 边缘 IP
   - 也可能解析失败（.example 保留域名）

2. **TCP**: 连接到 access_point 解密的 CDN IP ({IPV4_ADDRESS_01} 等)
   - 端口 80（config.tls=false）
   - 或端口 443（如果有 TLS）

3. **HTTP**: WebSocket 升级请求
   - Host: `{REVERSED_VIRTUAL_IP_DOTTED_16}.{POOL_DOMAIN_A}`（DomainPool）
   - Path: `/`（config.Url 为空）
   - UA: `DEV`

如果 Frida 截获到的参数与以上不同，那就是突破口。

---

## 十一、Android Frida

### 11.1 准备

```bash
# 1. 下载 frida-server（与 frida 版本一致）
# https://github.com/frida/frida/releases
# 选择 frida-server-16.x.x-android-arm64.xz

# 2. 解压
xz -d frida-server-16.x.x-android-arm64.xz

# 3. Push 到手机
adb push frida-server-16.x.x-android-arm64 /data/local/tmp/frida-server
adb shell chmod 755 /data/local/tmp/frida-server

# 4. 在手机上启动（需要 root）
adb shell su -c /data/local/tmp/frida-server &
```

### 11.2 连接 Android 上的 xTun

```bash
# 列出手机上的进程
frida-ps -U | grep xtun

# Spawn 启动 xTun
frida -U -f com.xtun -l hook_android.js --no-pause

# 或 attach 到已运行的
frida -U com.xtun -l hook_android.js
```

### 11.3 Hook libct-go.so

Android 上 Go 后端在 `libct-go.so` 中，不是 exe。

```javascript
// hook_android.js — Android xTun hook
// libct-go.so 是 Go 编译的 ARM64 shared library

Java.perform(function() {
    console.log("[*] Android xTun hook loaded");

    // 找到 libct-go.so 基址
    var mod = Process.findModuleByName("libct-go.so");
    if (!mod) {
        console.log("[-] libct-go.so not found, waiting...");
        // SO 可能还没加载，等待
        var dlopen = Module.getExportByName(null, "dlopen");
        Interceptor.attach(dlopen, {
            onLeave: function(retval) {
                var mod = Process.findModuleByName("libct-go.so");
                if (mod) {
                    console.log("[+] libct-go.so loaded at " + mod.base);
                    // 在这里安装 hook
                    installGoHooks(mod.base);
                }
            }
        });
        return;
    }

    console.log("[+] libct-go.so @ " + mod.base + " size=" + mod.size);
    installGoHooks(mod.base);
});

function installGoHooks(base) {
    // ARM64 上的 Go 函数地址需要从 Ghidra 分析 libct-go.so 获取
    // 注意: ARM64 地址与 x86_64 不同，需要单独分析

    // Hook libc connect（看 TCP 连接目标）
    var connect = Module.getExportByName("libc.so", "connect");
    Interceptor.attach(connect, {
        onEnter: function(args) {
            var addrPtr = args[1];
            var family = addrPtr.readU16();
            if (family === 2) { // AF_INET
                var portBytes = addrPtr.add(2).readByteArray(2);
                var port = new Uint8Array(portBytes);
                var portNum = (port[0] << 8) | port[1];
                var ip = addrPtr.add(4).readU8() + "." +
                         addrPtr.add(5).readU8() + "." +
                         addrPtr.add(6).readU8() + "." +
                         addrPtr.add(7).readU8();
                if (portNum === 80 || portNum === 443) {
                    send({type: "connect", ip: ip, port: portNum});
                }
            }
        }
    });
    console.log("[+] Hooked libc!connect");

    // Hook DNS
    var getaddrinfo = Module.getExportByName("libc.so", "getaddrinfo");
    Interceptor.attach(getaddrinfo, {
        onEnter: function(args) {
            this.host = args[0].isNull() ? null : args[0].readCString();
        },
        onLeave: function(retval) {
            if (this.host) {
                send({type: "dns", host: this.host, result: retval.toInt32()});
            }
        }
    });
    console.log("[+] Hooked libc!getaddrinfo");
}
```

### 11.4 Android 特有注意事项

| 问题 | 解决 |
|------|------|
| 需要 root | Frida server 需要 root 权限 |
| SELinux | `setenforce 0` 或用 Magisk |
| libct-go.so 延迟加载 | Hook dlopen 等待加载 |
| ARM64 地址 | 需要单独用 Ghidra 分析 libct-go.so |
| 多线程 | Go 协程多，Frida hook 必须线程安全 |

---

## 十二、常见问题

### Q1: Hook 导致 xTun 崩溃

**原因**: Go 的栈布局和调用约定与 C 不同。Interceptor.attach 如果修改了不该改的寄存器，Go 运行时会 panic。

**解决**:
1. onEnter/onLeave 中只读取 `this.context` 的寄存器，不要写入
2. 不要用 `Interceptor.replace`（会破坏 Go 栈管理）
3. 如果崩溃，减少 hook 数量，逐个排查

### Q2: 地址偏移不对（hook 到错误位置）

**原因**: Go 编译器可能内联（inline）了函数，或者 ASLR 偏移计算错误。

**解决**:
1. 确认 ASLR 偏移: `ACTUAL_BASE - 0x140000000`
2. 在 Ghidra 中确认函数没有被内联（检查是否有独立的函数入口）
3. 用 `Module.findExportByName` 查找已知导出（Go 二进制通常没有导出表，但可以搜索符号）

### Q3: 读取 Go 字符串乱码

**原因**: Go 字符串指针/长度读取不正确。

**解决**:
1. 确认参数传递方式（寄存器 vs 栈）
2. 确认 Go 版本的 ABI（1.17+ 用寄存器 ABI，1.16- 用栈 ABI）
3. 打印原始字节确认: `ptr(rax).readByteArray(Math.min(rbx, 100))`

### Q4: Hook Windows API 看不到 Go 的网络调用

**原因**: Go 可能使用自己的 DNS 解析器（`net.cgoLookupHost` vs `net.goLookupHost`）。

**解决**:
1. Go 在 Windows 上默认使用 cgo（调用系统 API），所以 Hook ws2_32 通常有效
2. 如果无效，Hook Go 内部的 `net.(*Resolver).lookupHost`
3. 或者用 pktmon 抓 DNS 包作为备份

### Q5: Frida 无法 attach（权限问题）

**解决**:
1. 以管理员身份运行 Python/PowerShell
2. 确认 xTun 没有反调试保护
3. 用 `frida -f` spawn 模式替代 attach

### Q6: Go 编译器内联导致函数不存在

**原因**: Go 编译器可能把小函数内联到调用者中，Ghidra 中显示的独立函数地址在运行时实际上没有对应的函数入口。

**解决**:
1. 在 Ghidra 中检查函数是否被其他函数引用
2. 如果函数被内联，改为 hook 调用者函数
3. 或者 hook 更底层的函数（如 AES.NewCipher 而不是 decryptAccessPoint）

---

## 关键发现总结

走完这一步你应该有：

- ✅ Frida 安装完成，能 attach 到 xTun
- ✅ 能 hook Go 函数（decryptAccessPoint, PayloadSecret）
- ✅ 能截获 TCP 连接目标、DNS 查询、HTTP 请求
- ✅ 能截获 WebSocket 升级请求的完整内容
- ✅ `frida_xtun_capture.py` 一键捕获脚本
- ✅ Android Frida hook 基础

**最重要的**: 运行 `frida_xtun_capture.py`，在 xTun 中连接一个 websocket 类型节点，截获的 WebSocket 升级请求就是攻破这 13 个节点的关键。

---

**回到**: [核心教学 README](./xtun-go-reverse-teaching-archive.md#source-core-16)

---

<a id="source-supplement-a6"></a>

> **编辑说明（A6；source-report）**：节名、入口位置、工具签名与 Shannon 熵都只是启发式线索；“Nothing found”只表示未识别到签名，不能证明未加壳。高熵可能来自资源/压缩/数据，并不自动等于壳；“熵 = 8 即强加密”、Go 必不加壳/必无反调试等原文绝对化判断也不能作为验证结论。Go runtime 复杂度与真正壳的运行时解包机制需分开。本轮无 PE，也未运行来源检测/脱壳脚本。

# A6 · 补充 — 加壳检测与脱壳

---

## 目标

判断 `xtun-windows.exe` 是否加壳，掌握通用的加壳检测方法，了解 Go 二进制的特殊性。

---

## 一、什么是加壳

加壳（packing）是把原始可执行文件压缩或加密，运行时由壳代码先解压/解密再跳到真正入口。

### 常见壳

| 壳 | 类型 | 特征 | 脱壳难度 |
|---|------|------|----------|
| **UPX** | 压缩壳 | 节区名 UPX0/UPX1，入口在 UPX1 | 低 — `upx -d` 一键 |
| **VMProtect** | 虚拟化壳 | .vmp0/.vmp1 节区，代码虚拟化 | 极高 — 需要逆 VM 指令集 |
| **Themida** | 保护壳 | 反调试+代码变形+IAT 加密 | 高 — dump+修复 |
| **ASPack** | 压缩壳 | .aspack 节区 | 低 — 通用工具可脱 |
| **自研壳** | 自定义 | 非标准节区名、异常入口点 | 看实现 |

### 壳做了什么

```
原始 EXE:
  .text  — 可执行代码（明文）
  .rdata — 只读数据（明文）
  .data  — 可读写数据

加壳后 EXE:
  .UPX0  — 解压目标区域（空，运行时填充）
  .UPX1  — 压缩的原始代码+数据
  .rsrc  — 资源（可能保留）
  入口点 → UPX1 的解压 stub → 解压到 UPX0 → 跳转到 OEP
```

OEP = Original Entry Point，壳解压后跳转到的真实入口。

---

## 二、怎么检测加壳

### 方法 1：Detect It Easy (DIE)

DIE 是免费的 PE 分析工具，自动检测壳和编译器。

```bash
# 下载: https://github.com/horsicq/Detect-It-Easy/releases
# 运行:
die "{LOCAL_PROJECT_DIR}/xtun-windows.exe"
```

DIE 输出示例（xTun）：
```
PE64
    Compiler: Go(1.25.0)
    Linker: Go linker
    Packer: Nothing found
```

**Packer: Nothing found** → 未加壳。

### 方法 2：PEiD

PEiD 是经典 PE 检测工具（老了但仍可用）：
```
PEiD → Load → 选择 xtun-windows.exe
结果: "Nothing found *" 或 "Go lang compiled"
```

### 方法 3：Exeinfo PE

```bash
# 下载: https://github.com/ExeinfoASL/ASL
# 拖入 exe 文件
# 输出:  Compiler: Go / Packer: Not packed
```

### 方法 4：手动判断（最可靠）

不需要工具，用 Python 就能判断。

#### 4.1 看节区名

```python
import pefile

pe = pefile.PE("xtun-windows.exe")
for s in pe.sections:
    name = s.Name.rstrip(b'\x00').decode('utf-8', 'replace')
    print(f"  {name}")
```

**正常 Go PE 节区:**
```
.text    ← 正常
.rdata   ← 正常
.data    ← 正常
.pdata   ← 正常
.rsrc    ← 正常
.reloc   ← 正常
```

**UPX 加壳的节区:**
```
UPX0     ← 明显加壳
UPX1     ← 明显加壳
.rsrc    ← 保留
```

**VMProtect 加壳的节区:**
```
.vmp0    ← 明显加壳
.vmp1    ← 明显加壳
.text    ← 可能保留但已虚拟化
```

xTun 的节区全部正常 → 未加壳。

#### 4.2 看入口点位置

```python
ep = pe.OPTIONAL_HEADER.AddressOfEntryPoint
text = [s for s in pe.sections if s.Name.startswith(b'.text')][0]
text_start = text.VirtualAddress
text_end = text_start + text.Misc_VirtualSize

if text_start <= ep < text_end:
    print(f"入口点在 .text 中: 正常")
else:
    print(f"入口点不在 .text 中: 可能加壳！")
    # 加壳后入口点通常在壳的节区（如 UPX1, .vmp0）
```

xTun 入口点在 `.text` → 正常。

#### 4.3 看节区熵值（最强判断）

```python
import math

def entropy(data):
    """计算 Shannon 熵，范围 0-8"""
    if not data: return 0.0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    ent = 0.0
    length = len(data)
    for f in freq:
        if f > 0:
            p = f / length
            ent -= p * math.log2(p)
    return ent

pe = pefile.PE("xtun-windows.exe")
for s in pe.sections:
    name = s.Name.rstrip(b'\x00').decode('utf-8', 'replace')
    data = s.get_data()
    ent = entropy(data)
    verdict = ""
    if ent > 7.5:
        verdict = " ← 高熵！可能加密/压缩"
    elif ent > 6.5:
        verdict = " ← 正常编译代码"
    elif ent < 1.0:
        verdict = " ← 几乎为空"
    print(f"  {name:8s} size={len(data):10d}  entropy={ent:.4f}{verdict}")
```

### 熵值判断标准

| 熵值范围 | 含义 |
|----------|------|
| 0.0 - 1.0 | 几乎空白（全零或重复数据） |
| 1.0 - 5.0 | 结构化数据（字符串表等） |
| 5.5 - 6.8 | 正常编译代码 |
| 6.8 - 7.2 | Go 编译代码（Go 比 C/C++ 熵值稍高） |
| 7.5 - 8.0 | 加密或压缩数据 |
| = 8.0 | 完美随机（强加密） |

**xTun 的熵值预期:**
```
.text   entropy=6.2~6.5   ← Go 代码，正常
.rdata  entropy=5.5~6.0   ← 只读数据，正常
.data   entropy=3.0~4.5   ← 全局变量，正常
```

所有节区熵值在正常范围 → 未加壳。

---

## 三、Go 二进制的特殊性

### 3.1 Go 不需要加壳

Go 编译器产生的二进制天生具有类似"壳"的特征：

| 特征 | Go 二进制 | C/C++ 二进制 |
|------|----------|-------------|
| 体积 | 巨大（50MB+） | 小（几百 KB） |
| 链接 | 静态链接所有依赖 | 动态链接 DLL |
| 符号表 | 部分保留（默认不 strip） | 通常 strip |
| 控制流 | 极复杂（goroutine/defer/GC） | 相对简单 |
| 字符串 | (指针, 长度) 对，无 null 终止 | null 终止 |
| 导出表 | 无标准 PE 导出表 | 有 |

Go 的巨大体积和复杂控制流本身就是逆向的障碍。给 Go 二进制加壳反而可能适得其反：
- UPX 压缩后体积变小 → 更容易分析
- VMProtect 虚拟化会与 Go runtime 冲突

### 3.2 xTun 的结论

```
加壳: 否
编译器: Go 1.25.0
特征: 标准 Go PE64, 未 strip, 50MB 静态链接
混淆: 无额外混淆（Go 模块路径完全可见）
反调试: 无（标准 Go 二进制不含反调试）
```

xTun 完全依赖协议加密（两层 AES-GCM + ChaCha20）而非二进制保护。

---

## 四、如果碰到加壳的目标怎么办

### 4.1 UPX 脱壳（最简单）

```bash
# 检测
upx -t target.exe
# 输出: "target.exe [OK]" 表示是 UPX

# 脱壳
upx -d target.exe -o target_unpacked.exe

# 验证
upx -t target_unpacked.exe
# 输出: "not packed" 表示脱壳成功
```

### 4.2 通用脱壳（dump + 修复）

对于非 UPX 的壳，通用方法是运行时 dump：

```
1. 用调试器（x64dbg/OllyDbg）加载加壳的 exe
2. 让壳代码运行完解压
3. 找到 OEP（壳跳转到的真实入口）
4. 在 OEP 处断下
5. 用 Scylla 插件 dump 内存
6. 用 Scylla 修复 IAT（Import Address Table）
7. 保存为脱壳后的 exe
```

#### x64dbg + Scylla 操作

```
1. x64dbg → File → Open → target.exe
2. 运行到入口点（壳的入口）
3. 设置 "Run to user code" 或手动跟踪到 OEP
4. Plugins → Scylla → IAT Autosearch → Get Imports
5. Dump → Dump PE
6. Fix Dump → 选择 dump 文件 → 修复 IAT
7. 输出: target_dumped_SCY.exe (脱壳+IAT修复后的文件)
```

### 4.3 VMProtect 特殊处理

VMProtect 虚拟化了部分代码，dump 后虚拟化的函数仍然是 VM 字节码。需要：
- 逆向 VM 处理器的指令集
- 或用 VMProtect 专用工具（如 vtil/NoVmp）
- 或绕过虚拟化的部分，只分析未虚拟化的函数

---

## 五、完整检测脚本

```python
#!/usr/bin/env python3
"""packer_detect.py — 检测 PE 文件是否加壳"""
import pefile, math, sys

def entropy(data):
    if not data: return 0.0
    freq = [0] * 256
    for b in data: freq[b] += 1
    ent = 0.0
    ln = len(data)
    for f in freq:
        if f > 0:
            p = f / ln
            ent -= p * math.log2(p)
    return ent

def detect_packer(path):
    pe = pefile.PE(path)

    print(f"=== 加壳检测: {path} ===\n")

    # 1. 节区名检查
    suspicious_names = {
        b'UPX0': 'UPX', b'UPX1': 'UPX', b'UPX2': 'UPX',
        b'.vmp0': 'VMProtect', b'.vmp1': 'VMProtect',
        b'.themid': 'Themida', b'.aspack': 'ASPack',
        b'.adata': '可能加壳', b'.packed': '自研壳',
    }

    packer_found = None
    print("节区分析:")
    for s in pe.sections:
        raw_name = s.Name.rstrip(b'\x00')
        name = raw_name.decode('utf-8', 'replace')
        data = s.get_data()
        ent = entropy(data)
        flags = []
        if raw_name in suspicious_names:
            flags.append(f"壳特征: {suspicious_names[raw_name]}")
            packer_found = suspicious_names[raw_name]
        if ent > 7.5:
            flags.append("高熵(加密/压缩?)")
        if s.SizeOfRawData == 0 and s.Misc_VirtualSize > 0:
            flags.append("空节区(运行时展开?)")
        flag_str = f" ← {', '.join(flags)}" if flags else ""
        print(f"  {name:8s} RawSize={s.SizeOfRawData:10d} "
              f"VirtSize={s.Misc_VirtualSize:10d} entropy={ent:.4f}{flag_str}")

    # 2. 入口点检查
    ep = pe.OPTIONAL_HEADER.AddressOfEntryPoint
    ep_section = None
    for s in pe.sections:
        if s.VirtualAddress <= ep < s.VirtualAddress + s.Misc_VirtualSize:
            ep_section = s.Name.rstrip(b'\x00').decode('utf-8', 'replace')
            break
    print(f"\n入口点: RVA=0x{ep:x}, 所在节区={ep_section or '未知'}")
    if ep_section and ep_section not in ('.text', '.code'):
        print(f"  ← 入口点不在 .text，可能加壳！")

    # 3. Go 特征检查
    with open(path, 'rb') as f:
        raw = f.read(min(os.path.getsize(path), 5*1024*1024))
    is_go = b'go.buildid' in raw or b'runtime.morestack' in raw
    if is_go:
        print(f"\n编译器: Go (检测到 go.buildid/runtime.morestack)")
        print(f"  Go 二进制通常不加壳")

    # 4. 结论
    print(f"\n{'='*40}")
    if packer_found:
        print(f"  结论: 检测到 {packer_found} 壳")
    elif any(entropy(s.get_data()) > 7.5 for s in pe.sections if s.SizeOfRawData > 1024):
        print(f"  结论: 可能加壳（存在高熵节区）")
    else:
        print(f"  结论: 未检测到壳")

    pe.close()

import os
detect_packer("xtun-windows.exe")
```

### 预期输出

```
=== 加壳检测: xtun-windows.exe ===

节区分析:
  .text    RawSize=  xxxxxxx VirtSize=  xxxxxxx entropy=6.3500
  .rdata   RawSize=  xxxxxxx VirtSize=  xxxxxxx entropy=5.7200
  .data    RawSize=  xxxxxxx VirtSize=  xxxxxxx entropy=4.1000
  .pdata   RawSize=  xxxxxxx VirtSize=  xxxxxxx entropy=5.9800
  .rsrc    RawSize=  xxxxxxx VirtSize=  xxxxxxx entropy=3.2000
  .reloc   RawSize=  xxxxxxx VirtSize=  xxxxxxx entropy=5.4100

入口点: RVA=0x..., 所在节区=.text

编译器: Go (检测到 go.buildid/runtime.morestack)
  Go 二进制通常不加壳

========================================
  结论: 未检测到壳
```

---

## 六、关键发现总结

走完这一步你应该理解：

- ✅ 加壳的概念和常见壳类型
- ✅ 四种检测方法（DIE/PEiD/手动节区/熵值）
- ✅ xTun 未加壳
- ✅ Go 二进制的"自然壳"特性
- ✅ 遇到加壳时的脱壳方法（UPX 一键 / 通用 dump+修复）
- ✅ 熵值分析判断标准（>7.5 = 加密/压缩）

---

**回到**：[核心教学 README](./xtun-go-reverse-teaching-archive.md#source-core-16)

---

<a id="source-supplement-a7"></a>

> **编辑说明（A7；source-report）**：三种工具对同一机器码的表示可互补，不是三个独立 runtime 证据。本篇明确含“示意”“预期输出”，未随包提供 IDA/Ghidra 项目或原始 Capstone 字节；保留地址、伪代码和工具优劣自述，但不把它们认定为已复核的实际反汇编。5.1 节预期 file_offset 与 A3 节区表并未闭合，不能照抄偏移；固定字节窗口也不证明完整函数边界。

# A7 · 补充 — IDA Pro 交叉验证

---

## 目标

用 IDA Pro 打开同一个 `xtun-windows.exe`，定位同样的函数，对比 Ghidra 的反编译结果。如果没有 IDA，用 Python Capstone 替代。

---

## 一、为什么需要交叉验证

Ghidra 和 IDA 的反编译器（分别是 Ghidra Decompiler 和 Hex-Rays）使用不同的算法，对同一段机器码的 C 伪代码可能不同：

| 维度 | Ghidra | IDA Pro + Hex-Rays |
|------|--------|-------------------|
| 价格 | 免费 | 商业授权（昂贵） |
| Go 支持 | 12+ 原生支持 Go 符号 | 需要 GoLoader 插件辅助 |
| 类型恢复 | 自动推断，有时不准 | Hex-Rays 通常更精准 |
| 控制流 | 偶尔误判循环/条件 | 通常更准确 |
| 字符串识别 | Go 字符串对需手动标注 | 同样需要插件辅助 |

交叉验证的目的不是"哪个更好"，而是**补漏**。一个工具漏掉的细节另一个可能捕获。

---

## 二、IDA Pro 导入 Go 二进制

### 2.1 打开文件

```
File → Open → xtun-windows.exe
```

IDA 弹出加载选项：
- Processor type: `MetaPC` (x86/x64 自动识别)
- ✅ Load resources
- ✅ Analysis → Autoanalysis
- Kernel options → ✅ Create function tails

点击 OK。50MB 的 Go PE 分析需要 **20-40 分钟**。

### 2.2 安装 GoLoader 插件（推荐）

GoLoader 帮助 IDA 识别 Go 的函数名、类型、接口。

```
1. 下载: https://github.com/padorka/iDAGolangHelper
   或: https://github.com/SentineLabs/AlphaGolang
2. 复制到 IDA 插件目录:
   C:\Program Files\IDA Pro 8.3\plugins\
3. 重启 IDA
4. Edit → Plugins → Golang Helper → Rename functions
```

GoLoader 做的事：
- 恢复被 IDA 识别为 `sub_140365f60` 的函数名为 `github.com/fmnx/cftun/backend/dialer.decryptAccessPoint`
- 解析 Go 的 pclntab（程序计数器行号表）恢复源文件名和行号
- 标注 Go 字符串

### 2.3 分析完成后的界面

```
左侧面板:
  Functions → 搜索 "decryptAccessPoint"
  Strings → 搜索 "cftun"

中央面板:
  IDA View-A → 反汇编视图
  Pseudocode-A → Hex-Rays 反编译（按 F5）

右侧面板:
  Cross-references (Xrefs)
```

---

## 三、定位同一个函数

### 3.1 用地址跳转

Ghidra 中 `decryptAccessPoint` 的地址是 `0x140365f60`。

在 IDA 中：

```
G 键 → 输入 0x140365f60 → Enter
```

IDA 跳转到该地址。如果 GoLoader 已运行，函数名显示为：
```
github_com_fmnx_cftun_backend_dialer__decryptAccessPoint
```

### 3.2 用字符串搜索

```
Shift+F12 → 打开 Strings 窗口
Ctrl+F → 搜索 "cftun-txt"
双击结果 → 跳到字符串
X 键 → 查看交叉引用 → 双击引用 → 跳到函数
```

### 3.3 用函数名搜索

```
Ctrl+F → 在 Functions 窗口搜索 "decrypt"
```

---

## 四、比较反编译结果

### 4.1 IDA Hex-Rays 反编译

在 `decryptAccessPoint` 函数处按 **F5** 打开 Hex-Rays：

```c
// IDA Hex-Rays 伪代码（示意）
__int64 __fastcall decryptAccessPoint(
    runtime_string accessPoint,
    runtime_string payloadSecret)
{
    // 1. base64url 解码
    v12 = runtime_base64_RawURLEncoding_DecodeString(accessPoint);

    // 2. 分割 nonce 和 ciphertext
    nonce = v12.ptr;           // 前 12 字节
    ct_with_tag = v12.ptr + 12; // 12 之后
    ct_len = v12.len - 12;

    // 3. SHA256(payloadSecret)
    crypto_sha256_Sum256(payloadSecret.ptr, payloadSecret.len, &key);

    // 4. 构造 AAD
    aad[0] = 0x63; // 'c'
    aad[1] = 0x66; // 'f'
    aad[2] = 0x74; // 't'
    aad[3] = 0x75; // 'u'
    aad[4] = 0x6E; // 'n'
    aad[5] = 0x2D; // '-'
    aad[6] = 0x74; // 't'
    aad[7] = 0x78; // 'x'
    aad[8] = 0x74; // 't'

    // 5. AES-256-GCM
    cipher = crypto_aes_NewCipher(&key, 32);
    gcm = crypto_cipher_NewGCM(cipher);
    plaintext = gcm_Open(gcm, nil, nonce, ct_with_tag, aad);

    // 6. 解析二进制格式
    return decodeTXTBinaryPayload(plaintext);
}
```

### 4.2 对比 Ghidra 反编译

| 区别点 | Ghidra | IDA Hex-Rays |
|--------|--------|-------------|
| 参数类型 | `string` (笼统) | `runtime_string` (Go 特定) |
| 变量名 | param_1, param_2 | accessPoint, payloadSecret |
| AAD 构造 | 可能合并为一个赋值 | 逐字节展示 |
| GCM 调用 | 可能识别为未知函数 | 识别为 crypto 包函数 |
| 字符串长度 | 可能丢失长度信息 | 保留 (ptr, len) 对 |

### 4.3 两个工具互补的地方

**Ghidra 更好的地方:**
- 免费，可以 Headless 批量脚本化
- 对 Go 12+ 原生支持比 IDA 更好（不需要插件）
- 可以导出 JSON 函数列表

**IDA 更好的地方:**
- Hex-Rays 的类型推断通常更准确
- 交叉引用图更清晰
- 调试器集成（可以直接附加进程调试）
- Go 字符串处理在 GoLoader 辅助下更完整

---

## 五、替代方案: Python Capstone 反汇编

如果没有 IDA Pro，用 Capstone 可以得到原始反汇编（不是伪代码，是汇编指令）。

### 5.1 提取函数字节

```python
#!/usr/bin/env python3
"""capstone_disasm.py — 用 Capstone 反汇编 decryptAccessPoint"""
import pefile
from capstone import *

pe = pefile.PE("xtun-windows.exe")
image_base = pe.OPTIONAL_HEADER.ImageBase  # 0x140000000

# decryptAccessPoint 的地址
FUNC_VA = 0x140365f60
FUNC_SIZE = 0x400  # 反汇编前 1024 字节（函数可能更大）

# VA → 文件偏移
rva = FUNC_VA - image_base
for s in pe.sections:
    if s.VirtualAddress <= rva < s.VirtualAddress + s.Misc_VirtualSize:
        file_offset = s.PointerToRawData + (rva - s.VirtualAddress)
        break

# 读取字节
with open("xtun-windows.exe", "rb") as f:
    f.seek(file_offset)
    code = f.read(FUNC_SIZE)

# 反汇编
md = Cs(CS_ARCH_X86, CS_MODE_64)
md.detail = True

print(f"=== decryptAccessPoint @ 0x{FUNC_VA:x} ===")
print(f"文件偏移: 0x{file_offset:x}")
print()

for i in md.disasm(code, FUNC_VA):
    print(f"  0x{i.address:x}:  {i.mnemonic:8s} {i.op_str}")
    # 遇到 ret 就停（函数可能有多个 ret）
    if i.mnemonic == 'ret':
        # Go 函数通常以 ret 结尾，但可能有 epilogue
        # 简单起见，打印第一个 ret 后再多打 10 条
        pass

pe.close()
```

### 预期输出

```
=== decryptAccessPoint @ 0x140365f60 ===
文件偏移: 0x1d65f60

  0x140365f60:  mov      qword ptr [rsp + 8], rcx
  0x140365f65:  mov      qword ptr [rsp + 0x10], rdx
  0x140365f6a:  sub      rsp, 0x98
  0x140365f71:  mov      rbp, qword ptr [rsp + 0x90]
  0x140365f79:  lea      rax, [rip + 0x...]
  0x140365f80:  call     runtime_base64_RawURLEncoding_DecodeString
  ...
  0x140365fa0:  call     crypto_sha256_Sum256
  ...
  0x140365fd0:  call     crypto_aes_NewCipher
  ...
  0x140365ff0:  call     crypto_cipher_NewGCM
  ...
```

### 5.2 从汇编中识别关键操作

| 汇编模式 | 含义 |
|----------|------|
| `call runtime_base64_*` | base64 解码 |
| `call crypto_sha256_*` | SHA256 哈希 |
| `call crypto_aes_NewCipher` | 创建 AES 加密器 |
| `call crypto_cipher_NewGCM` | GCM 模式 |
| `mov byte ptr [rsp+0x..], 0x63` | AAD 逐字节构造（0x63='c'） |
| `lea rax, [rip + 0x...]` | 加载字符串地址 |

### 5.3 搜索交叉引用

```python
#!/usr/bin/env python3
"""capstone_xref.py — 搜索对 decryptAccessPoint 的调用"""
import pefile, struct
from capstone import *

pe = pefile.PE("xtun-windows.exe")
image_base = pe.OPTIONAL_HEADER.ImageBase
target_va = 0x140365f60

# 读取 .text 节区
for s in pe.sections:
    if s.Name.startswith(b'.text'):
        text_data = s.get_data()
        text_va = image_base + s.VirtualAddress
        break

md = Cs(CS_ARCH_X86, CS_MODE_64)
md.detail = True

print(f"搜索调用 0x{target_va:x} (decryptAccessPoint) 的位置:")
for i in md.disasm(text_data, text_va):
    if i.mnemonic == 'call' and i.op_str.startswith('0x'):
        call_target = int(i.op_str, 16)
        if call_target == target_va:
            print(f"  0x{i.address:x}: call 0x{call_target:x}")
```

---

## 六、实际对比示例: AAD 构造

### Ghidra 看到的

```c
local_9[0] = 0x63;
local_9[1] = 0x66;
local_9[2] = 0x74;
local_9[3] = 0x75;
local_9[4] = 0x6e;
local_9[5] = 0x2d;
local_9[6] = 0x74;
local_9[7] = 0x78;
local_9[8] = 0x74;
```

### IDA Hex-Rays 看到的

```c
aad[0] = 'c';
aad[1] = 'f';
aad[2] = 't';
aad[3] = 'u';
aad[4] = 'n';
aad[5] = '-';
aad[6] = 't';
aad[7] = 'x';
aad[8] = 't';
```

### Capstone 看到的

```asm
0x140365fc0:  mov    byte ptr [rsp + 0x40], 0x63
0x140365fc5:  mov    byte ptr [rsp + 0x41], 0x66
0x140365fca:  mov    byte ptr [rsp + 0x42], 0x74
0x140365fcf:  mov    byte ptr [rsp + 0x43], 0x75
0x140365fd4:  mov    byte ptr [rsp + 0x44], 0x6e
0x140365fd9:  mov    byte ptr [rsp + 0x45], 0x2d
0x140365fde:  mov    byte ptr [rsp + 0x46], 0x74
0x140365fe3:  mov    byte ptr [rsp + 0x47], 0x78
0x140365fe8:  mov    byte ptr [rsp + 0x48], 0x74
```

三个工具看到的本质是一样的：逐字节写入 `"cftun-txt"`。

- Ghidra 显示 hex 值
- IDA 自动转为字符
- Capstone 显示原始 mov 指令

交叉验证确认了 AAD 的精确值。

---

## 七、关键发现总结

走完这一步你应该理解：

- ✅ IDA Pro 和 Ghidra 各有优劣，交叉验证能补漏
- ✅ 用地址 0x140365f60 在 IDA 中直接跳转到函数
- ✅ Hex-Rays 伪代码通常比 Ghidra 更接近源代码
- ✅ 没有 IDA 时用 Capstone 反汇编得到原始指令
- ✅ 三种工具对 AAD 构造的分析结果一致

---

**回到**：[核心教学 README](./xtun-go-reverse-teaching-archive.md#source-core-16)

---

<a id="source-supplement-a8"></a>

> **编辑说明（A8；source-report）**：阅读顺序按原件保留：先是作者在文首回填的“最终结果”，随后第一至八节保留早期失败、CDN/点分 Host/DNS 不存在的假设，最后第九至十节才是作者后续修正。早期与修正不是同时成立的教程。2026-09-18、86 次失败、13→21 个 websocket 节点、26/27 DATA_OK、CF 530 的归因及“完全攻破”均为作者自述；没有随包日志、DNS 原始响应、脚本或端到端向量，本轮未查询 DNS、连接节点或复现。101 仅表示升级层，不能独自证明协议握手、AEAD 数据互通或代理端到端成功。

# A8 · 补充 — websocket 类型节点：从 86 次失败到完全攻破

---

## 目标

记录 xTun 逆向中 websocket 类型节点从 86 次测试全部失败到最终 20/21 端到端成功的完整过程。**真实逆向不会一步到位——记录失败分析和最终突破的过程，比只记录成功更有教学价值。**

---

> **编辑时序标记：作者回填的最终摘要，非本次观测。后文仍保留历史阶段。**

## 〇、最终结果（2026-09-18 攻破）

| 类型 | 节点数 | 连接状态 | 代理可用？ |
|------|--------|----------|------------|
| implicit_websocket | 6 | ✅ 6/6 DATA_OK | ✅ 端到端可用 |
| websocket | 21 | ✅ 20/21 DATA_OK | ✅ 端到端可用（1个源站离线） |
| **总计** | **27** | **26/27** | **✅ 96% 可用** |

**关键突破**: websocket 类型需要 DNS 解析 DomainPool Host 得到 Cloudflare 边缘 IP，而不是直连 access_point 中的源站 IP。

---

> **编辑时序标记：以下第一至八节为历史记录/假设。CDN 地址归类、点分 Host、DNS 不存在及候选行动未被本次核验，且与第九节修正有冲突。**

## 一、最初的问题（86 次失败阶段）

早期测试时 websocket 类型节点全部失败：

| 类型 | 节点数 | 连接状态 | 代理可用？ |
|------|--------|----------|------------|
| implicit_websocket | 6 | ✅ 101 成功 | ✅ 端到端可用 |
| websocket | 13 | ❌ 86次全部失败 | ❌ 无法使用 |

当时以为逆向完成度只有 65%。

---

## 二、两种类型的差异

### 2.1 核心差异对比

| 特征 | implicit_websocket (✅) | websocket (❌) |
|------|------------------------|---------------|
| Go 连接器 | NewRouteRacer (HTTPBridgeDialer) | NewWebsocket (gorilla Dialer) |
| Ghidra 地址 | 0x1403594a0 | 0x140348120 |
| access_point flag | 0x22 (") | 0x23 (#) |
| endpoint IP 数量 | 20-21 个 | 4 个 |
| endpoint IP 范围 | {IPV4_PREFIX_01} (阿里云直连) | {IPV4_PREFIX_02}/{IPV4_PREFIX_03}/{IPV4_PREFIX_04}/{IPV4_PREFIX_05} (CDN 任播) |
| upstream 字段 | 有 ({UPSTREAM_ID_01}, {UPSTREAM_ID_02}, {UPSTREAM_ID_03}, {UPSTREAM_ID_04}) | 空字符串 |
| exit_server_ip | 有 ({IPV4_ADDRESS_19} 等) | 空字符串 |
| Host 头 | 纯 IP 地址 | DomainPool 域名 |
| Path | /{upstream}/e/{exit_ip} | / (空路径) |
| 连接方式 | 直连源站服务器 | 经 Cloudflare CDN |

### 2.2 具体节点分布

**implicit_websocket (6个, ✅已攻破):**
```
ID  {NODE_ID_01}  {NODE_LABEL_02}   upstream={UPSTREAM_ID_01}  exit={IPV4_ADDRESS_08}   20个{IPV4_PREFIX_01} IP
ID  {NODE_ID_02}  {NODE_LABEL_03}   upstream={UPSTREAM_ID_01}  exit={IPV4_ADDRESS_19}     20个{IPV4_PREFIX_01} IP
ID {NODE_ID_03}  {NODE_LABEL_04}   upstream={UPSTREAM_ID_03}  exit={IPV4_ADDRESS_15}    20个{IPV4_PREFIX_01} IP
ID {NODE_ID_04}  {NODE_LABEL_05}   upstream={UPSTREAM_ID_03}  exit={IPV4_ADDRESS_20}      21个{IPV4_PREFIX_01} IP
ID {NODE_ID_05}  {NODE_LABEL_06}   upstream={UPSTREAM_ID_04}  exit={IPV4_ADDRESS_11}    20个{IPV4_PREFIX_01} IP
ID {NODE_ID_06}  {NODE_LABEL_07}   upstream={UPSTREAM_ID_02}  exit={IPV4_ADDRESS_02}  21个{IPV4_PREFIX_06} IP
```

**websocket (13个, ❌未攻破):**
```
ID  {NODE_ID_07}  {NODE_LABEL_01}   upstream=空  exit=空  4个CDN IP ({IPV4_PREFIX_09}/{IPV4_PREFIX_10}/{IPV4_PREFIX_11})
ID  {NODE_ID_08}  {NODE_LABEL_08} upstream=空  exit=空  4个CDN IP ({IPV4_PREFIX_12}/{IPV4_PREFIX_13}/{IPV4_PREFIX_14})
ID  {NODE_ID_09}  {NODE_LABEL_09}              同东京CDN IP
ID {NODE_ID_10}  {NODE_LABEL_10}                  同东京CDN IP
ID {NODE_ID_11}  {NODE_LABEL_11}                同法兰克福CDN IP
ID {NODE_ID_12}  {NODE_LABEL_12}               4个CDN IP
ID {NODE_ID_13}  {NODE_LABEL_13}                  同东京CDN IP
ID {NODE_ID_14}  {NODE_LABEL_14}               同新加坡CDN IP
ID {NODE_ID_15}  {NODE_LABEL_15}               同新加坡CDN IP
ID {NODE_ID_16}  {NODE_LABEL_16}               同新加坡CDN IP
ID {NODE_ID_17}  {NODE_LABEL_17}               同新加坡CDN IP
ID {NODE_ID_18}  {NODE_LABEL_18}                 同东京CDN IP
ID {NODE_ID_19}  {NODE_LABEL_19}                 同东京CDN IP
```

注意：多个 websocket 节点共享同一组 CDN IP，说明这些 IP 是 Cloudflare 边缘任播地址，通过 Host 头路由到不同后端。

---

## 三、Ghidra 反编译发现

### 3.1 NewWebsocket 连接流程 (0x140348120)

```
1. Config.Prepare() → 解密 access_point 获取 CDN IP 列表
2. splitHostAndPath(config.Url) → 分割 URL
   → config.Url 为空 → host="", path=""
3. 如果 config.Domains 非空且 config.Direct==false:
   → NewDomainPool(config.VirtualIP, config.Domains)
   → 由 DomainPool 提供 Host 头
4. 创建 gorilla/websocket.Dialer
5. 拼接 URL: "ws://{host}{path}" → "ws://{REVERSED_VIRTUAL_IP_DOTTED_16}.{POOL_DOMAIN_A}/"
6. 连接 CDN IP:80, Host={DomainPool host}, Path=/
```

### 3.2 DomainPool Host 格式

```
NewDomainPool(virtualIP, domains):
  reversedIP = reverseVirtualIPv4(virtualIP)
  // "{IPV4_ADDRESS_16}" → "{IPV4_ADDRESS_09}"

  for each domain in domains:
    host = reversedIP + "." + domain
    // "{REVERSED_VIRTUAL_IP_DOTTED_16}.{POOL_DOMAIN_A}"
    // "{REVERSED_VIRTUAL_IP_DOTTED_16}.{POOL_DOMAIN_B}"

  轮询选择: Hosts[atomicIndex++ % len(Hosts)]
```

**每个节点的 DomainPool Host 不同**（因为 virtualIP 不同）：

| 节点 | virtual_ip | Host |
|------|-----------|------|
| {NODE_LABEL_01} | {IPV4_ADDRESS_16} | {REVERSED_VIRTUAL_IP_DOTTED_16}.{POOL_DOMAIN_A} |
| {NODE_LABEL_08} | {IPV4_ADDRESS_10} | {REVERSED_VIRTUAL_IP_DOTTED_10}.{POOL_DOMAIN_A} |
| {NODE_LABEL_09} | {IPV4_ADDRESS_18} | {REVERSED_VIRTUAL_IP_DOTTED_18}.{POOL_DOMAIN_A} |

### 3.3 connectWithPurpose (0x14034afc0)

```
1. 从 AddrPool 选择 CDN IP
2. 设置 HTTP 头: Host=DomainPool host, User-Agent=DEV
3. 检查 transport 类型:
   - "implicit_websocket" → HTTPBridgeDialer
   - 否则 → gorilla Dialer (标准 WS 升级)
4. gorilla 发起: GET / HTTP/1.1, Host={REVERSED_VIRTUAL_IP_DOTTED_16}.{POOL_DOMAIN_A}
5. 最多重试 3 次
```

### 3.4 关键差异: Subprotocols

| 类型 | Sec-WebSocket-Protocol |
|------|----------------------|
| implicit_websocket | `cftun websocket v3` (HTTPBridgeDialer 设置) |
| websocket | **nil** (gorilla Dialer 不设置 Subprotocols) |

这意味着 websocket 类型的升级请求**不带 Sec-WebSocket-Protocol 头**。

---

## 四、86次测试详细结果

### 4.1 测试过的 IP

| IP | 位置 | TCP:80 | TCP:443 | HTTP 响应 |
|----|------|--------|---------|-----------|
| {IPV4_ADDRESS_01} | 东京 CDN | ✅ | ✅ | Cloudflare 400/403 |
| {IPV4_ADDRESS_13} | 新加坡 | ✅ | ✅ | 无响应（静默） |
| {IPV4_ADDRESS_07} | 东京备用 | ✅ | ✅ | 无响应 |
| {IPV4_ADDRESS_12} | 新加坡备用 | ✅ | ✅ | 无响应 |

### 4.2 测试过的组合（部分）

| # | Host | Path | UA | TLS | {IPV4_PREFIX_09} 结果 | {IPV4_PREFIX_12} 结果 |
|---|------|------|----|-----|------------|------------|
| 1 | IP | / | DEV | 否 | 超时 | 超时 |
| 2 | {POOL_DOMAIN_A} | / | DEV | 否 | CF 400 | 超时 |
| 3 | {POOL_DOMAIN_B} | / | DEV | 否 | CF 400 | 超时 |
| 4 | {REVERSED_VIRTUAL_IP_DOTTED_16}.{POOL_DOMAIN_A} | / | DEV | 否 | CF 400 | 超时 |
| 5 | IP | / | DEV | 是 | SSL失败 | 超时 |
| 6 | {POOL_DOMAIN_A} | / | DEV | 是 | CF 403 | 超时 |
| 7 | IP | /{UPSTREAM_ID_05}/e/{IPV4_PREFIX_09}... | DEV | 否 | CF 400 | 超时 |
| 8 | IP | / | Mozilla | 否 | 超时 | 超时 |
| 9 | IP | /?v=3 | DEV | 否 | 超时 | 超时 |
| 10 | {EXAMPLE_EDGE_DOMAIN} | / | DEV | 是 | SSL失败 | 超时 |
| ... | ... | ... | ... | ... | ... | ... |

**总计 86 种组合，无一返回 101。**

### 4.3 对照实验

对 implicit_websocket 的 IP 做同样的 path=/ 测试：

```
{IPV4_ADDRESS_06} + path=/           → nginx 444 (静默断开)
{IPV4_ADDRESS_06} + path=/{UPSTREAM_ID_01}/e/...  → ✅ 101 Switching Protocols
```

**即使在已知工作的服务器上，path=/ 也失败。** 这说明 path=/ 不是有效的 WS 升级路径。

---

## 五、CDN 路由机制分析

### 5.1 Cloudflare 是怎么路由的

{IPV4_ADDRESS_01} 是 Cloudflare 的 CDN 任播地址。Cloudflare 根据 **Host 头** 决定把请求转发到哪个后端（Origin）：

```
客户端 → Cloudflare 边缘 ({IPV4_ADDRESS_01})
  → 看 Host 头
  → 查找对应的 Origin 配置
  → 转发到 Origin 服务器
```

但 {POOL_DOMAIN_A} 和 {POOL_DOMAIN_B} 在公共 DNS 中不存在。这意味着：

1. **Cloudflare Tunnel**: 域名可能通过 Cloudflare Tunnel 注册，不需要公共 DNS 记录
2. **Cloudflare for Teams / Zero Trust**: 内部域名，只在 Cloudflare 网络内部路由
3. **Cloudflare Argo**: 智能路由，通过 Cloudflare 骨干网到达 Origin

### 5.2 为什么 {IPV4_PREFIX_09} 返回 400

{IPV4_ADDRESS_01} 是真正的 Cloudflare 边缘节点（响应带 CF 头）。Cloudflare 收到请求后：
- Host=IP → 不知道转发到哪 → 超时或丢弃
- Host={POOL_DOMAIN_A} → 查找域名配置 → 找不到（或配置不匹配）→ 400

这暗示 {POOL_DOMAIN_A} 需要以**特定方式**注册在 Cloudflare 中，可能需要：
- 特定的 Cloudflare 账号下的 Tunnel
- 特定的 SNI 配置
- 或者根本不走 HTTP，而走 Cloudflare Spectrum（TCP 代理）

### 5.3 为什么 {IPV4_PREFIX_12} 等完全静默

{IPV4_ADDRESS_13} 等 IP 接受 TCP 连接但不发送任何数据。可能是：
1. **Cloudflare Spectrum**: TCP 级别代理，不解析 HTTP。期望原始 TCP 数据（cftun 可能直接发二进制帧）
2. **服务器已下线**: TCP 负载均衡器仍接受连接，但后端已不可用
3. **防火墙**: 入站连接被接受但出站响应被丢弃

---

## 六、可能的突破方向

### 6.1 方向一: Frida 动态 Hook（最可靠）

在真实 xTun 客户端连接 websocket 节点时，hook 关键函数：

```javascript
// frida_ws_type_hook.js
// Hook gorilla/websocket Dialer.DialContext

// 1. Hook net.Dial — 看实际 TCP 目标
Interceptor.attach(Module.findExportByName(null, "net.Dial"), {
    onEnter: function(args) {
        console.log("[net.Dial] network=" + args[0].readUtf8String() +
                    " addr=" + args[1].readUtf8String());
    }
});

// 2. Hook HTTP 请求 — 看完整请求头
// 需要找到 gorilla/websocket 的 Dial 函数偏移
// 用 Ghidra 确认偏移后设置断点

// 3. Hook TLS — 看 SNI
// crypto/tls.(*Conn).Handshake
```

在 Windows 上对 xtun-windows.exe 使用 Frida：
```bash
# 1. 启动 xTun 客户端
# 2. 找到进程 PID
tasklist | findstr xtun

# 3. 附加 Frida
frida -p <PID> -l frida_ws_type_hook.js

# 4. 在 xTun 客户端选择一个 websocket 类型节点（如{NODE_LABEL_01}）连接
# 5. 观察 Frida 输出
```

**预期能看到**: 真实的 TCP 连接目标、Host 头、Path、是否用 TLS、SNI 值。

### 6.2 方向二: DNS 抓包

客户端连接前可能先做 DNS 查询：

```python
#!/usr/bin/env python3
"""dns_capture.py — 抓 DNS 查询"""
import subprocess

# 启动 pktmon 抓 DNS (UDP 53)
subprocess.run(["pktmon", "filter", "add", "-p", "53", "-t", "UDP"])
subprocess.run(["pktmon", "start", "--capture",
                "--etl", "dns_capture.etl", "--pkt-size", "0", "-m"])

input("在 xTun 客户端连接 websocket 节点后按 Enter...")

subprocess.run(["pktmon", "stop"])
subprocess.run(["pktmon", "etl2pcap", "dns_capture.etl", "-o", "dns_capture.pcapng"])
print("抓包完成，用 Wireshark 打开 dns_capture.pcapng 查看 DNS 查询")
```

**观察**: 客户端是否查询 {POOL_DOMAIN_A}、{POOL_DOMAIN_B}，以及解析结果。

### 6.3 方向三: TLS + 多种 SNI

```python
#!/usr/bin/env python3
"""tls_sni_test.py — 测试不同 SNI"""
import ssl, socket

IP = "{IPV4_ADDRESS_01}"
PORT = 443

SNIS = [
    "{POOL_DOMAIN_A}",
    "{POOL_DOMAIN_B}",
    "{REVERSED_VIRTUAL_IP_DOTTED_16}.{POOL_DOMAIN_A}",
    "{SERVICE_DOMAIN}",
    "{SERVICE_DOMAIN}",
    "{TUNNEL_DOMAIN}",
    # Cloudflare Tunnel 格式
    "{TUNNEL_UUID}.{TUNNEL_PROVIDER_DOMAIN}",
]

for sni in SNIS:
    try:
        sock = socket.create_connection((IP, PORT), timeout=5)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ss = ctx.wrap_socket(sock, server_hostname=sni)
        cert = ss.getpeercert(binary_form=True)
        print(f"✅ SNI={sni}: TLS握手成功, cert={len(cert)}B")
        # 尝试 WS 升级
        req = (f"GET / HTTP/1.1\r\nHost: {sni}\r\n"
               f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
               f"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
               f"Sec-WebSocket-Version: 13\r\nUser-Agent: DEV\r\n\r\n")
        ss.sendall(req.encode())
        resp = ss.recv(4096)
        status = resp.split(b'\r\n')[0].decode('utf-8', 'replace')
        print(f"   HTTP响应: {status}")
        ss.close()
    except ssl.SSLError as e:
        print(f"❌ SNI={sni}: SSL错误 {e}")
    except Exception as e:
        print(f"❌ SNI={sni}: {e}")
```

### 6.4 方向四: 原始 TCP（非 HTTP）

如果 {IPV4_PREFIX_12} 等 IP 用的是 Cloudflare Spectrum (TCP 代理)，可能不走 HTTP/WebSocket：

```python
#!/usr/bin/env python3
"""raw_tcp_test.py — 测试原始 TCP 连接"""
import socket, os, struct
from Crypto.Cipher import ChaCha20_Poly1305
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

IP = "{IPV4_ADDRESS_13}"
PORT = 80

PAYLOAD_SECRET = b"{PAYLOAD_SECRET}"
TUNNEL_UUID = "{TUNNEL_UUID}"

# 直接发送 cftun open frame（不做 WS 升级）
client_key = os.urandom(32)
pt = bytearray([4, 1, 6, 4])
pt.extend(struct.pack('<I', 1))
pt.extend(bytes([{DESTINATION_IPV4_OCTETS}]))  # dst IP: {IPV4_ADDRESS_22}
pt.extend(struct.pack('>H', 80))
pt.append(36)
pt.extend(TUNNEL_UUID.encode())
pt.extend(client_key)

open_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
                info=b"cftun websocket v3 open key").derive(PAYLOAD_SECRET)
nonce = os.urandom(12)
cipher = ChaCha20_Poly1305.new(key=open_key, nonce=nonce)
cipher.update(b"cftun websocket v3 open")
ct, tag = cipher.encrypt_and_digest(bytes(pt))
frame = nonce + ct + tag

# 直接 TCP 发送（不做 HTTP/WS 升级）
sock = socket.create_connection((IP, PORT), timeout=10)
sock.sendall(frame)
sock.settimeout(5)
try:
    resp = sock.recv(4096)
    print(f"收到 {len(resp)} 字节: {resp[:64].hex()}")
except socket.timeout:
    print("超时，无响应")
sock.close()
```

### 6.5 方向五: 完整抓包对比

在 xTun 客户端连接 websocket 节点时，用 Wireshark 抓完整 TCP 流量：

```bash
# 1. 安装 Wireshark + Npcap
# 2. 开始抓包，过滤: tcp.port == 80 && ip.addr == {IPV4_ADDRESS_01}
# 3. 在 xTun 中选择{NODE_LABEL_01} 连接
# 4. 停止抓包
# 5. 分析 TCP 流量:
#    - Follow TCP Stream
#    - 看第一个数据包是 HTTP 还是原始二进制
#    - 看 Host 头、Path、TLS 握手
```

---

## 七、对教学的意义

### 7.1 真实逆向不是线性的

教科书式的逆向教学通常是：分析 → 理解 → 实现 → 成功。

现实是：**分析 → 假设 → 测试 → 失败 → 重新分析 → 新假设 → 再测试 → 部分成功 → 继续挖掘。**

xTun 逆向的 implicit_websocket 部分走通了这个完整流程。websocket 类型节点卡在"假设 → 测试 → 失败"的循环中，需要更多的信息（Frida hook 或抓包）来打破。

### 7.2 记录失败的价值

86次失败测试不是浪费。每次失败排除了一种可能性：

- ~~path=/ 是有效路径~~ → 排除（即使 implicit_ws 也不接受 path=/）
- ~~{POOL_DOMAIN_A} 是公共域名~~ → 排除（DNS 不存在）
- ~~纯 IP Host 可以连接~~ → 排除（{IPV4_PREFIX_09} 返回超时）
- ~~TLS:443 可以连接~~ → 排除（SSL 错误或 403）

排除法是逆向的基本方法。知道什么不行和知道什么行一样重要。

### 7.3 什么时候放弃 vs 继续

| 信号 | 动作 |
|------|------|
| 有明确的下一步（如 Frida hook） | 继续 |
| 所有已知方向都试过了 | 寻找新信息源（抓包、论坛、源码泄露） |
| 已有的成果足够用（6个节点可用） | 先用着，后台继续研究 |
| 目标更新了（服务端改了协议） | 重新开始分析 |

目前状态：有明确的下一步（Frida hook），值得继续。

---

## 八、行动计划

### 阶段一：信息收集（优先）

```
□ Frida hook gorilla dialer — 在真实客户端连接 websocket 节点时
  截获 TCP 目标、HTTP 请求头、TLS SNI
□ DNS 抓包 — 看客户端是否查询 {POOL_DOMAIN_A}
□ Wireshark 全流量抓包 — 看第一个包是 HTTP 还是原始二进制
```

### 阶段二：验证假设

```
□ 如果 Frida 显示用了 TLS → 测试正确的 SNI
□ 如果 Frida 显示用了特殊 Host → 用该 Host 重试
□ 如果是原始 TCP（非 HTTP）→ 直接发 cftun frame
□ 如果 DNS 解析到不同 IP → 用那个 IP 连接
```

### 阶段三：实现

```
□ 修改 cftun_proxy.py 支持 websocket 类型连接
□ 测试所有 13 个节点
□ 更新教学文档
```

---

> **编辑时序标记：从此处开始是作者后续修正——改称 access_point 为源站地址，Host 用横杠连接反转 IP，并经 DNS 选择边缘 IP。仅保留作者叙述，不表示本次验证。**

## 九、突破！完整解决方案（2026-09-18）

### 9.1 根因

86 次测试全部失败的原因只有一个：**连错了 IP。**

- access_point 解密出的 IP（{IPV4_PREFIX_07}, {IPV4_PREFIX_08} 等）是**源站 IP**（住宅/P2P 机器），很多已离线
- websocket 类型节点应该通过 **Cloudflare CDN** 路由，不是直连源站
- 正确做法：DNS 解析 DomainPool Host → 得到 Cloudflare 边缘 IP → 连接边缘 IP

### 9.2 正确连接流程

```
1. 构造 DomainPool Host:
   virtual_ip = "{IPV4_ADDRESS_16}"
   domain = "{POOL_DOMAIN_A}"
   → 反转 IP 用横杠: "{REVERSED_VIRTUAL_IP_HYPHENATED_16}"
   → Host = "{REVERSED_VIRTUAL_IP_HYPHENATED_16}.{POOL_DOMAIN_A}"

2. DNS 解析:
   nslookup {REVERSED_VIRTUAL_IP_HYPHENATED_16}.{POOL_DOMAIN_A}
   → {IPV4_ADDRESS_17} (Cloudflare)
   → {IPV4_ADDRESS_03} (Cloudflare)

3. 连接 Cloudflare 边缘 IP:
   TCP connect to {IPV4_ADDRESS_17}:80

4. WebSocket 升级:
   GET / HTTP/1.1
   Host: {REVERSED_VIRTUAL_IP_HYPHENATED_16}.{POOL_DOMAIN_A}
   User-Agent: DEV
   Upgrade: websocket
   Connection: Upgrade
   Sec-WebSocket-Key: {random}
   Sec-WebSocket-Version: 13
   (注意: 不发送 Sec-WebSocket-Protocol 和 Origin)

5. → 101 Switching Protocols
6. → open frame + 数据通道正常工作
```

### 9.3 与 implicit_websocket 的关键区别

| 步骤 | implicit_websocket | websocket |
|------|-------------------|-----------|
| 连接目标 | access_point IP（直连源站） | DNS 解析 DomainPool Host（Cloudflare 边缘） |
| Host 头 | 纯 IP | `{反转IP横杠}.{domain}` |
| Path | `/{upstream}/e/{exit_ip}` | `/` |
| Sec-WebSocket-Protocol | 发送 | 不发送 |
| Origin | 发送 | 不发送 |
| Content-Length: 0 | 发送 | 不发送 |

### 9.4 最终测试结果

```
websocket:          20/21 DATA_OK
implicit_websocket:  6/6  DATA_OK
Total:              26/27 DATA_OK (96%)
```

唯一失败的 Node {NODE_ID_08}（{NODE_LABEL_08}）返回 Cloudflare 530（Origin DNS Error），表示该节点的 Cloudflare Tunnel 源站不可达。这不是逆向问题，是基础设施问题。

### 9.5 教训

1. **不要假设 access_point 中的 IP 就是连接目标。** websocket 类型通过 CDN 路由，access_point IP 是源站地址，不是你应该连接的地址。
2. **DNS 解析是关键。** DomainPool Host 在公共 DNS 可解析，给出 Cloudflare 边缘 IP。
3. **头部差异很重要。** 多发一个 Sec-WebSocket-Protocol 或 Origin 可能不会导致 Cloudflare 拒绝，但少了正确的 Host 头格式一定会失败。
4. **86 次失败不是浪费。** 每次失败排除了一种可能性，最终缩小到正确答案。

---

## 十、关键发现总结

- ✅ **全部 27 个节点的连接方式已完全逆向**
- ✅ 26/27 端到端验证通过
- ✅ websocket 通过 Cloudflare CDN（DomainPool Host + DNS 解析）
- ✅ implicit_websocket 通过直连源站（纯 IP Host + path 路由）
- ✅ 代码已修复：cftun_proxy.py 支持两种类型
- ✅ 唯一失败的 Node {NODE_ID_08} 是源站离线（CF 530），非逆向问题

---

**回到**：[核心教学 README](./xtun-go-reverse-teaching-archive.md#source-core-16)

---

<a id="reuse-limits"></a>

## 复用边界

1. A1/A2 提供 APK 分层和 ELF 观察的来源案例，不能据文件名断言每个 APK 的协议都在 Go SO，不能把 Windows VA 直接复制到 ARM64 Hook。
2. A3/A7 的字符串、xref、反汇编/反编译可用于互补阅读，不能把“预期输出”当真实字节；地址换算必须回到实际 PE 节区或 ELF Segment 和运行期映射。
3. A4/A5 的 ABI、函数入口、返回值、内联和 Frida 兼容性仍需样本核验。安装、有效命中、参数读取正确、密码链因果、离线 parity 和服务端验收是不同事实，本批没有后四类结果。
4. A6 的熵和节名只是线索，不是壳/无壳结论；本归档不触发脱壳、VMP 或反调试流程。
5. A8 的最初假设与后续修正按原时间顺序共存；86 次失败、13/21 个 websocket 节点、26/27 DATA_OK 不与其他教学/源报告的节点数和 101 结果合并。后续修正仍是 `source-report`，没有本轮 runtime/parity/server-accepted 证据。

本归档保留原件中的疑点，以便后续按来源定位，而非将其吸收成新的 operative skill、目标网络脚本或 dispatcher 规则。
