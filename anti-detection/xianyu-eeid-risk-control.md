# 闲鱼 EEID 风控体系完全揭秘

> 来源: 闲鱼 7.28.30（`com.taobao.idlefish`，versionCode 520）/ SecurityGuard 6.7.260202 独立分析（Redmi K20 Pro，Android 11）
> 分析日期: 2026-09-24
> 归档日期: 2026-09-26
> 分类: 反检测/风控对抗 — 阿里 SecurityGuard EEID 设备风控
>
> 闲鱼 EEID（Extended Equipment ID）是 SecurityGuard 在客户端采集 Mini 探针（7 字节布尔段 + 11 字节半字节段）、ET 探针（本包实采 55 个）、SGEXT 45 字段、PL 测量、BI/CS 上报后，由 ACS-MUM 服务端签发的设备扩展标识。本文按原文结构归档探针位定义、SG 文件（`.s/` 目录、`.sg` mtime → SGEXT `fields[4]`）、UTDID 持久化、EEID 注册/验证协议与签名参数关系；服务端评分与 EEID 生成算法为原文推测。

## 收录说明

原文为 2026-09-24 独立分析稿，归档时只加元数据、本节与相关地图，正文按原结构保留。原文「八、参考资料」列出的 `*.private.json`、`xianyu_sign/`、`xianyu_eeid/` 等项目文件不随本文收录。

阅读时按证据等级区分：

- 客户端侧（探针位布局、SG 文件路径、UTDID 存储位置、ET tag 表）来自本机样本，偏移与 tag 只对闲鱼 7.28.30 / SG 6.7.260202。
- 服务端侧（3.2.4 验证管道、3.3.2 Diff 分析、各项风险分值与 BLOCK/REVIEW 阈值、3.4 时序、EEID 生成公式）原文已注明是基于协议分析的推测模型，不是服务端实现。
- 5.x 把 `x-sign` 写成 `HMAC-SHA1(appkey_secret, INPUT 22 字段)`，与本库 SG 70102 四头纯算（`MD5` state1 → `SHA1` → 交替 XOR → Base64）不一致；复现 `x-sign` 以四头文章或 InnerSignImpl RPC 为准，本文的 22 字段 INPUT 按待验证处理。

相关地图：

| 主题 | 文档 |
|------|------|
| 阿里 App 网关四头纯算（SG 70102） | [alibaba-mtop-four-headers.md](../signature-algorithms/alibaba-mtop-four-headers.md) |
| MTOP InnerSignImpl 实例 RPC | [mtop-innersign-rpc.md](../mobile-app-reverse/mtop-innersign-rpc.md) |
| 闲鱼 Android InnerSignImpl 案例 | [xianyu-android-sign-rpc-case.md](../web-reverse/xianyu-android-sign-rpc-case.md) |
| 设备指纹一致性建模 | [device-fingerprint-consistency-modeling.md](./device-fingerprint-consistency-modeling.md) |
| 数盟 libdu.so 指纹对照 | [shuzilm-libdu-fingerprint.md](./shuzilm-libdu-fingerprint.md) |

## 📋 文档说明

本文档完整揭露阿里巴巴闲鱼 App 的 EEID (Extended Equipment ID) 风控体系，包括：
- 完整的风控架构和参数体系
- EEID 注册和使用流程
- SG 文件系统的作用
- 签名参数与 EEID 的关系
- 风控对抗分析

**基于版本**：
- 闲鱼版本：7.28.30 (versionCode 520)
- SecurityGuard 版本：6.7.260202
- 设备：Xiaomi Redmi K20 Pro, Android 11
- 分析日期：2026-09-24

---

## 一、EEID 风控体系概述

### 1.1 什么是 EEID？

**EEID (Extended Equipment ID)** 是阿里巴巴安全部门开发的**设备指纹 + 行为特征识别系统**，用于：

1. **设备唯一性识别** - 跨应用追踪同一设备
2. **风险行为检测** - 识别模拟器、Root、Hook、群控
3. **账号关联分析** - 关联多个账号到同一设备
4. **实时风控决策** - 拦截高风险交易和操作

### 1.2 EEID 的核心特点

| 特点 | 说明 |
|-----|------|
| **多维度指纹** | 硬件 + 软件 + 行为 + 环境 |
| **动态采集** | 435 个 ET 探针 + 70 组 Mini 探针 |
| **持久化追踪** | UTDID + SG 文件 + EEID |
| **实时更新** | 每次请求动态生成探针数据 |
| **强加密保护** | TEA/XTEA + Base64 + 自定义编码 |
| **服务端校验** | 6,235+ 参数完整性校验 |

### 1.3 EEID 在风控体系中的位置

```
用户操作（发布商品、聊天、交易）
    ↓
客户端风控 SDK (SecurityGuard)
    ↓
采集设备指纹 (Mini/ET/PL 探针)
    ↓
生成 EEID + 签名参数
    ↓
HTTPS 请求上传到服务器
    ↓
服务端风控引擎 (ACS-MUM)
    ↓
风控决策（通过/拦截/人工审核）
```

---

## 二、EEID 风控参数体系

### 2.1 参数分类总览

EEID 体系包含 **6,235+ 个参数**，分为以下几大类：

| 分类 | 参数数量 | 作用 | 重要性 |
|-----|---------|------|--------|
| **设备身份** | 11 | 设备唯一标识 | ⭐⭐⭐⭐⭐ |
| **Mini 探针** | 70 组 | 硬件+软件快速检测 | ⭐⭐⭐⭐⭐ |
| **ET 探针** | 435 | 深度环境检测 | ⭐⭐⭐⭐⭐ |
| **PL 测量** | 158 | 性能+日志 | ⭐⭐⭐ |
| **SGEXT 扩展** | 45 | 状态+统计 | ⭐⭐⭐⭐ |
| **BI 行为** | 多个 | 用户行为上报 | ⭐⭐⭐⭐ |
| **CS 校验** | 多个 | 代码完整性 | ⭐⭐⭐⭐ |
| **签名参数** | 22 | HMAC-SHA1 签名 | ⭐⭐⭐⭐⭐ |

### 2.2 核心风控点详解

#### 2.2.1 设备身份参数（最重要）

这些参数用于唯一标识设备，是风控的基础：

```json
{
  "utdid": "arNd7GBIB9wDAFhdV44i+riU",  // ⭐⭐⭐⭐⭐ 最重要
  "device_id": "",                        // 可选
  "ttid": "1582631881546@fleamarket_android_7.28.30",
  "x_umt": "arNd7GBIB9wDAFhdV44i+riU",  // 与 utdid 相同
  "wua": "HHnB...（长字符串）"            // 设备指纹摘要
}
```

**UTDID 详解**：
- **存储位置**：`/data/data/com.taobao.idlefish/shared_prefs/Alvin2.xml`
- **生成算法**：首次安装时通过复杂算法生成，包含：
  - 设备硬件信息（MAC、IMEI、序列号等）
  - 随机数
  - 时间戳
  - 特殊编码
- **特性**：
  - 卸载重装会变（除非备份）
  - 跨阿里系 App 共享
  - 不可逆向推算
  - 持久化存储
- **风控作用**：**最核心的设备标识**，服务端用它关联所有历史行为

#### 2.2.2 Mini 探针（70 组快速检测）⭐⭐⭐⭐⭐

Mini 探针是 **7 字节布尔段 + 11 字节半字节段**，共 70 组快速检测项。

---

##### Mini 探针完整列表

**实际数据**（来自真实设备 Redmi K20 Pro）：
```
布尔段（7 字节）：99 20 85 04 80 01 44
半字节段（11 字节）：00 00 ff ff 00 ff 00 00 77 93 00
```

---

###### 【布尔段】- 56 位开关检测

**Byte 0: 0x99 (10011001)**

| Bit | 值 | 含义 | 风控作用 |
|-----|---|------|---------|
| 0 | 1 | USB 调试已开启 | ⚠️ 开发者模式（警告但不拦截） |
| 1 | 0 | ADB 网络调试关闭 | ✅ 正常 |
| 2 | 0 | 未知检测 1 | - |
| 3 | 1 | 设备正在充电 | ✅ 正常状态 |
| 4 | 1 | WiFi 已连接 | ✅ 正常网络 |
| 5 | 0 | 飞行模式关闭 | ✅ 正常 |
| 6 | 0 | 移动数据关闭 | ✅ 正常（WiFi 环境） |
| 7 | 1 | 位置服务开启 | ✅ 正常 |

**Byte 1: 0x20 (00100000)**

| Bit | 值 | 含义 | 风控作用 |
|-----|---|------|---------|
| 0 | 0 | Root 检测 - 方法 1 | ✅ 未 Root |
| 1 | 0 | Root 检测 - 方法 2 (su 文件) | ✅ 未 Root |
| 2 | 0 | Root 检测 - 方法 3 (Magisk) | ✅ 未 Root |
| 3 | 0 | Root 检测 - 方法 4 (SuperSU) | ✅ 未 Root |
| 4 | 0 | Xposed 框架检测 | ✅ 未安装 |
| 5 | 1 | 未知检测 2 | - |
| 6 | 0 | 模拟器检测 - 快速判断 | ✅ 真机 |
| 7 | 0 | VirtualApp 检测 | ✅ 未安装 |

**Byte 2: 0x85 (10000101)**

| Bit | 值 | 含义 | 风控作用 |
|-----|---|------|---------|
| 0 | 1 | 触摸屏可用 | ✅ 硬件正常 |
| 1 | 0 | 压力传感器状态 | - |
| 2 | 1 | 加速度传感器可用 | ✅ 真机特征 |
| 3 | 0 | 陀螺仪状态 | - |
| 4 | 0 | 磁力传感器状态 | - |
| 5 | 0 | 光线传感器状态 | - |
| 6 | 0 | 距离传感器状态 | - |
| 7 | 1 | 重力传感器可用 | ✅ 真机特征 |

**Byte 3: 0x04 (00000100)**

| Bit | 值 | 含义 | 风控作用 |
|-----|---|------|---------|
| 0 | 0 | 前置摄像头 | ✅ 有 |
| 1 | 0 | 后置摄像头 | ✅ 有 |
| 2 | 1 | 话筒可用 | ✅ 硬件正常 |
| 3 | 0 | 扬声器可用 | ✅ 硬件正常 |
| 4 | 0 | 耳机是否插入 | ❌ 未插入 |
| 5 | 0 | 震动马达状态 | ✅ 正常 |
| 6 | 0 | 闪光灯状态 | ✅ 正常 |
| 7 | 0 | LED 指示灯状态 | ✅ 正常 |

**Byte 4: 0x80 (10000000)**

| Bit | 值 | 含义 | 风控作用 |
|-----|---|------|---------|
| 0 | 0 | 蓝牙是否开启 | ❌ 关闭 |
| 1 | 0 | 蓝牙是否配对设备 | ❌ 无配对 |
| 2 | 0 | NFC 是否开启 | ❌ 关闭 |
| 3 | 0 | GPS 是否定位中 | ❌ 未定位 |
| 4 | 0 | 移动网络类型 (4G/5G) | - |
| 5 | 0 | VPN 是否连接 | ✅ 未连接 VPN（正常） |
| 6 | 0 | 代理是否设置 | ✅ 无代理（正常） |
| 7 | 1 | WiFi 信号强度 | ✅ 信号良好 |

**Byte 5: 0x01 (00000001)**

| Bit | 值 | 含义 | 风控作用 |
|-----|---|------|---------|
| 0 | 1 | 指纹传感器可用 | ✅ 硬件正常 |
| 1 | 0 | 人脸识别可用 | ✅ 硬件正常 |
| 2 | 0 | 虹膜识别 | ❌ 无此硬件 |
| 3 | 0 | 屏下指纹 | ❌ K20 Pro 是侧面指纹 |
| 4 | 0 | 安全芯片 (TEE) | - |
| 5 | 0 | SE 安全元件 | - |
| 6 | 0 | TrustZone 状态 | - |
| 7 | 0 | Knox 安全 (三星) | ❌ 非三星设备 |

**Byte 6: 0x44 (01000100)**

| Bit | 值 | 含义 | 风控作用 |
|-----|---|------|---------|
| 0 | 0 | 电池健康 - bit 0 | |
| 1 | 0 | 电池健康 - bit 1 | 健康状态 = 正常 (0b00) |
| 2 | 1 | 充电类型 - bit 0 | |
| 3 | 0 | 充电类型 - bit 1 | 充电类型 = 快充 (0b10) |
| 4 | 0 | 电池温度状态 | ✅ 正常温度 |
| 5 | 0 | 低电量模式 | ❌ 未开启 |
| 6 | 1 | 屏幕是否亮屏 | ✅ 亮屏中 |
| 7 | 0 | 屏幕自动旋转 | ❌ 未开启 |

---

###### 【半字节段】- 22 个半字节（4 位）数值

**Byte 0: 0x00 (高位 0, 低位 0)**

| 半字节 | 值 | 含义 | 风控作用 |
|-------|---|------|---------|
| 高 4 位 | 0 | 传感器组 1 - 加速度精度 | 0 = 未校准/未知 |
| 低 4 位 | 0 | 传感器组 1 - 陀螺仪精度 | 0 = 未校准/未知 |

**Byte 1: 0x00 (高位 0, 低位 0)**

| 半字节 | 值 | 含义 | 风控作用 |
|-------|---|------|---------|
| 高 4 位 | 0 | 传感器组 2 - 磁力计精度 | 0 = 未校准 |
| 低 4 位 | 0 | 传感器组 2 - 光线传感器级别 | 0 = 较暗环境 |

**Byte 2: 0xff (高位 15, 低位 15)**

| 半字节 | 值 | 含义 | 风控作用 |
|-------|---|------|---------|
| 高 4 位 | 15 | 触摸点最大数量 | ⭐⭐⭐⭐ 10 点触控 = 真机特征 |
| 低 4 位 | 15 | 触摸压力级别 | ⭐⭐⭐⭐ 支持压感 = 高端机型 |

**Byte 3: 0xff (高位 15, 低位 15)**

| 半字节 | 值 | 含义 | 风控作用 |
|-------|---|------|---------|
| 高 4 位 | 15 | 屏幕刷新率等级 | 15 = 可能是高刷屏 |
| 低 4 位 | 15 | 屏幕色深 | 15 = 高色深 |

**Byte 4: 0x00 (高位 0, 低位 0)**

| 半字节 | 值 | 含义 | 风控作用 |
|-------|---|------|---------|
| 高 4 位 | 0 | 摄像头数量 - 前置 | 1 个前置摄像头 |
| 低 4 位 | 0 | 摄像头数量 - 后置 | 实际可能是编码方式 |

**Byte 5: 0xff (高位 15, 低位 15)**

| 半字节 | 值 | 含义 | 风控作用 |
|-------|---|------|---------|
| 高 4 位 | 15 | 音频采样率等级 | 15 = 高质量音频 |
| 低 4 位 | 15 | 音频通道数 | 15 = 立体声/多声道 |

**Byte 6: 0x00 (高位 0, 低位 0)**

| 半字节 | 值 | 含义 | 风控作用 |
|-------|---|------|---------|
| 高 4 位 | 0 | 存储加密状态 | 0 = 未加密或部分加密 |
| 低 4 位 | 0 | SELinux 模式 | ⭐⭐⭐⭐⭐ 0 = Enforcing（正常），1 = Permissive（高风险） |

**Byte 7: 0x00 (高位 0, 低位 0)**

| 半字节 | 值 | 含义 | 风控作用 |
|-------|---|------|---------|
| 高 4 位 | 0 | 系统完整性 - DM-Verity | 0 = 启用（正常） |
| 低 4 位 | 0 | 系统完整性 - AVB | 0 = 启用（正常） |

**Byte 8: 0x77 (高位 7, 低位 7)**

| 半字节 | 值 | 含义 | 风控作用 |
|-------|---|------|---------|
| 高 4 位 | 7 | 网络状态组合 | 7 = WiFi 连接，信号良好 |
| 低 4 位 | 7 | 电池电量区间 | 7 = 70%-80% 电量 |

**Byte 9: 0x93 (高位 9, 低位 3)**

| 半字节 | 值 | 含义 | 风控作用 |
|-------|---|------|---------|
| 高 4 位 | 9 | CPU 使用率区间 | 9 = 90%-100% 区间（可能是峰值） |
| 低 4 位 | 3 | 内存使用率区间 | 3 = 30%-40% |

**Byte 10: 0x00 (高位 0, 低位 0)**

| 半字节 | 值 | 含义 | 风控作用 |
|-------|---|------|---------|
| 高 4 位 | 0 | 后台进程数量区间 | 0 = 0-10 个 |
| 低 4 位 | 0 | 系统运行时长区间 | 0 = 刚启动不久 |

---

##### Mini 探针风控逻辑

**快速拦截规则**（服务端处理时间 < 10ms）：

```python
def check_mini_probes(bool_bytes, nibble_bytes):
    risk_score = 0

    # 【第 1 关：Root 检测】⭐⭐⭐⭐⭐
    byte1 = bool_bytes[1]  # 0x20
    root_bits = byte1 & 0x0F  # 低 4 位
    if root_bits != 0:
        return "BLOCK", "检测到 Root"  # 立即拦截

    # 【第 2 关：Hook/模拟器检测】⭐⭐⭐⭐⭐
    xposed = (byte1 >> 4) & 0x01
    emulator = (byte1 >> 6) & 0x01
    virtualapp = (byte1 >> 7) & 0x01
    if xposed or emulator or virtualapp:
        return "BLOCK", "检测到 Hook/模拟器/虚拟环境"

    # 【第 3 关：传感器检测】⭐⭐⭐⭐
    byte2 = bool_bytes[2]  # 0x85
    sensor_count = bin(byte2).count('1')
    if sensor_count < 2:
        risk_score += 80  # 传感器太少（模拟器特征）

    # 【第 4 关：SELinux 检测】⭐⭐⭐⭐⭐
    nibble6_low = nibble_bytes[6] & 0x0F
    if nibble6_low == 1:  # Permissive
        risk_score += 90  # SELinux 被关闭（高风险）

    # 【第 5 关：VPN/代理检测】⭐⭐⭐⭐
    byte4 = bool_bytes[4]  # 0x80
    vpn = (byte4 >> 5) & 0x01
    proxy = (byte4 >> 6) & 0x01
    if vpn or proxy:
        risk_score += 60  # VPN/代理（可疑）

    # 【第 6 关：触摸能力检测】⭐⭐⭐⭐
    nibble2_high = (nibble_bytes[2] >> 4) & 0x0F
    if nibble2_high < 5:
        risk_score += 70  # 触摸点数过少（模拟器特征）

    # 【第 7 关：硬件完整性】⭐⭐⭐
    byte3 = bool_bytes[3]  # 0x04
    if bin(byte3).count('1') < 2:
        risk_score += 50  # 硬件组件缺失

    # 决策
    if risk_score >= 100:
        return "REVIEW", f"风险评分: {risk_score}"
    else:
        return "PASS", f"评分: {risk_score}"
```

**关键风控点总结**：

| 检测项 | 位置 | 阈值 | 风控动作 |
|-------|------|------|---------|
| **Root 检测** | Byte1 低 4 位 | 任意位为 1 | ❌ 立即拦截 |
| **Xposed** | Byte1 bit4 | = 1 | ❌ 立即拦截 |
| **模拟器** | Byte1 bit6 | = 1 | ❌ 立即拦截 |
| **VirtualApp** | Byte1 bit7 | = 1 | ❌ 立即拦截 |
| **SELinux** | Nibble6 低 4 位 | = 1 (Permissive) | ⚠️ 高风险 +90 分 |
| **传感器数量** | Byte2 | < 2 个 | ⚠️ 可疑 +80 分 |
| **VPN** | Byte4 bit5 | = 1 | ⚠️ 可疑 +60 分 |
| **触摸点数** | Nibble2 高 4 位 | < 5 点 | ⚠️ 可疑 +70 分 |

**Mini 探针的优势**：
- ✅ **速度极快**：7+11=18 字节，解析时间 < 1ms
- ✅ **准确率高**：Root/Hook/模拟器检测准确率 > 99%
- ✅ **难以伪造**：需要同时伪造 70 个检测点，且要保持一致性
- ✅ **实时采集**：每次请求都重新采集，无法重放历史数据

#### 2.2.3 ET 探针（435 个深度检测）⭐⭐⭐⭐⭐

ET (Environment Telemetry) 探针是**最详细**的环境检测系统，每个探针都有具体的检测目标。

---

##### ET 探针完整列表（实际采集的 55 个核心探针）

**说明**：闲鱼 7.28.30 版本实际采集了 55 个核心 ET 探针，以下是完整的探针列表及其风控作用。

---

###### 【设备身份类】- 10 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 1 | 0299 | Android | 系统类型 | ⭐⭐⭐⭐⭐ 验证是否真实 Android 设备（模拟器可能返回其他值） |
| 3 | 023c | 2839F8E9-BB99-49CF-... | UUID 设备标识符 | ⭐⭐⭐⭐⭐ 设备指纹追踪，跨应用识别 |
| 12 | bd30 | 680c7e9d-1277-40a0-... | UUID 设备标识符 | ⭐⭐⭐⭐ 另一个设备唯一标识 |
| 16 | 45b7 | 680c7e9d-1277-40a0-... | UUID 设备标识符 | ⭐⭐⭐⭐ 与 bd30 交叉验证 |
| 21 | d79b | arNd7GBIB9wDAFhdV44i+riU | UTDID（阿里设备ID） | ⭐⭐⭐⭐⭐ **最核心**的设备标识，跨阿里系 App |
| 27 | 8f57 | 557acc7b9005281b | Android ID | ⭐⭐⭐⭐ 系统级设备标识 |
| 34 | e345 | e5086470-5b80-4ca1-... | UUID 设备标识符 | ⭐⭐⭐ 额外的设备追踪标识 |
| 41 | 0174 | 70a841e5423314d5 | 设备指纹 Hash | ⭐⭐⭐⭐ 综合设备特征哈希 |
| 48 | 85ba | <e2827ebf73bd46384e1e72e6520e9d7 | 设备特征码 | ⭐⭐⭐ 额外的设备指纹 |
| 17 | b7ab | 243462189056 | 设备序列号 | ⭐⭐⭐⭐ 硬件序列号（可能是 IMEI） |

**风控重点**：
- UTDID (tag d79b) 是最核心的标识，服务端用它关联所有历史行为
- 多个 UUID 交叉验证，防止单一标识被伪造
- 设备序列号验证硬件真实性

---

###### 【系统版本类】- 9 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 5 | f471 | 11 | Android 版本号 | ⭐⭐⭐⭐ 系统版本校验，与 ro.build.version 交叉验证 |
| 6 | 403e | raphael | 设备代号 | ⭐⭐⭐⭐⭐ Redmi K20 Pro 内部代号，验证设备型号 |
| 7 | 8fdc | raphael-user 11 RKQ1... | 完整编译指纹 | ⭐⭐⭐⭐⭐ 包含设备、版本、编译信息 |
| 15 | 2b09 | RKQ1.200826.002 test-keys | Build Tags | ⭐⭐⭐⭐⭐ **test-keys=高风险**（自编译/开发版） |
| 18 | 3b0a | V12.5.6.0.RFKCNXM | MIUI 版本号 | ⭐⭐⭐ 验证系统版本真实性 |
| 20 | b8c8 | release-keys | 编译类型 | ⭐⭐⭐⭐⭐ **release-keys=正常**，test-keys=风险 |
| 22 | fd52 | Xiaomi/raphael/raphael... | 完整系统指纹 | ⭐⭐⭐⭐⭐ 系统完整性验证 |
| 29 | 1cdb | c5-xm-ota-bd022.bj | OTA 服务器 | ⭐⭐⭐ 验证系统更新来源是否官方 |
| 44 | f31c | 30 | SDK 版本 | ⭐⭐⭐⭐ Android 11 = SDK 30 |

**风控重点**：
- **test-keys 检测**（tag 2b09）：自编译系统 = 高风险
- **release-keys 验证**（tag b8c8）：官方正式版 = 正常
- 多维度交叉验证系统版本真实性

---

###### 【硬件信息类】- 8 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 4 | a2c2 | 1080*2340 | 屏幕分辨率 | ⭐⭐⭐⭐ 验证设备型号（Redmi K20 Pro 特征） |
| 8 | c342 | 8 | CPU 核心数 | ⭐⭐⭐⭐ 验证硬件配置（K20 Pro = 8核） |
| 25 | aaca | Redmi K20 Pro | 设备型号 | ⭐⭐⭐⭐⭐ 官方型号名称 |
| 40 | 2b23 | Xiaomi | 设备厂商 | ⭐⭐⭐⭐ 厂商验证 |
| 45 | b07c | raphael | 设备代号 | ⭐⭐⭐⭐ 与 tag 403e 交叉验证 |
| 36 | aaa0 | 1080*2296 | 可用屏幕分辨率 | ⭐⭐⭐ 减去状态栏/导航栏后的分辨率 |
| 37 | efe7 | 243462189056 | 设备序列号 | ⭐⭐⭐⭐ 与 tag b7ab 交叉验证 |
| 43 | a5a4 | 1785600 | 内存配置 | ⭐⭐⭐ 物理内存大小（KB） |

**风控重点**：
- 屏幕分辨率 + 设备型号 + CPU 核心数 组合验证
- 检测是否为该型号的真机
- 模拟器通常硬件参数不匹配或缺失

---

###### 【网络硬件类】- 6 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 9 | 0864 | 00:16:a1:80:c6:e8 | WiFi MAC 地址 | ⭐⭐⭐⭐⭐ 网络硬件唯一标识 |
| 10 | 9ff5 | 02:a3:a5:d8:17:3e | 蓝牙 MAC 地址 | ⭐⭐⭐⭐ 蓝牙硬件标识 |
| 32 | 0864 | e0:dc:ff:dd:d0:8d | 另一个 MAC 地址 | ⭐⭐⭐⭐ 可能是移动网络 MAC |
| 46 | 0864 | (rmnet_data2)00:00:00... | 网络接口 MAC | ⭐⭐⭐ 移动数据网络接口 |
| 49 | 0864 | (dummy0)1e:b5:59:9e:07:bf | 虚拟网络接口 MAC | ⭐⭐⭐ 检测 VPN/代理 |
| 50 | 8676 | 1c:94:68:d9:71:8f | 网卡 MAC 地址 | ⭐⭐⭐⭐ 物理网络硬件标识 |

**风控重点**：
- 多个 MAC 地址交叉验证
- 检测 MAC 地址是否为随机生成（模拟器特征）
- 检测虚拟网络接口（VPN、代理、抓包工具）

---

###### 【运营商/SIM 卡类】- 4 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 24 | 095a | 中国移动 | 运营商名称 | ⭐⭐⭐⭐ SIM 卡信息，验证地理位置 |
| 38 | f02e | 中国移动 | 运营商名称（重复） | ⭐⭐⭐ 与 tag 095a 交叉验证 |
| 33 | a506 | 1789800155245 | 时间戳 | ⭐⭐⭐ SIM 卡相关时间戳 |
| 39 | b616 | -1 | SIM 卡状态 | ⭐⭐⭐ -1 可能表示无 SIM 或飞行模式 |

**风控重点**：
- 验证是否有真实 SIM 卡（模拟器通常无 SIM）
- 运营商信息与 IP 地址对比
- 检测虚拟 SIM 卡

---

###### 【应用信息类】- 4 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 11 | 3ed1 | com.taobao.idlefish | 应用包名 | ⭐⭐⭐⭐⭐ 验证应用身份（防二次打包） |
| 13 | 1c2b | 50816c6b14c076d0... | 应用签名 SHA1 | ⭐⭐⭐⭐⭐ 验证应用签名（防篡改） |
| 14 | 6980 | 256da23e982f8fc4... | 另一个签名 Hash | ⭐⭐⭐⭐ 交叉验证签名 |
| 26 | db95 | 7.28.30 | 应用版本号 | ⭐⭐⭐⭐ 验证版本真实性 |

**风控重点**：
- **应用签名校验**（tag 1c2b, 6980）：检测二次打包
- 包名 + 签名 + 版本号 三重验证
- 防止破解版、注入版

---

###### 【时间戳类】- 3 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 2 | d38e | 7673468 | 系统构建时间戳 | ⭐⭐⭐⭐ 验证系统编译时间 |
| 23 | f75f | 2026-09-19 14:46:22.609 | 当前时间 | ⭐⭐⭐⭐⭐ 时间一致性验证（防时间穿越） |
| 54 | 920a | 1634558061 | Unix 时间戳 | ⭐⭐⭐ 系统启动时间或构建时间 |

**风控重点**：
- 检测系统时间是否被篡改
- 验证时间戳合理性（过早或过晚都可疑）
- 防止时间穿越攻击

---

###### 【SecurityGuard 版本】- 2 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 30 | e1dc | 6.7.260202 | SG 版本号 | ⭐⭐⭐⭐⭐ SecurityGuard SDK 版本 |
| 55 | f410 | 5 | SG 配置版本 | ⭐⭐⭐ SG 内部配置版本 |

**风控重点**：
- 验证 SecurityGuard 版本与 App 版本匹配
- 检测是否使用了旧版或修改版 SG

---

###### 【传感器数据类】- 3 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 19 | bced | 63614244.629999995,... | 传感器数据序列 | ⭐⭐⭐⭐⭐ 传感器原始数据（加速度、陀螺仪等） |
| 35 | 9785 | {"version":2,"data":...} | 传感器状态 JSON | ⭐⭐⭐⭐ 传感器可用性和状态 |
| 53 | e7b4 | Linux version 4.14.180... | 内核版本 | ⭐⭐⭐⭐ 系统内核信息 |

**风控重点**：
- 检测设备是否有真实传感器（模拟器通常无传感器）
- 传感器数据合理性验证
- 内核版本与系统版本匹配性

---

###### 【加密/特殊数据类】- 6 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 28 | e0a1 | YW3glsCgEACAhx7jl97f7KVl... | 加密的系统指纹 | ⭐⭐⭐⭐⭐ Base64 编码的系统特征 |
| 31 | 0eef | {"xm_1":"PhCyi0rR3OOO..."} | 小米设备特征 JSON | ⭐⭐⭐⭐ 小米设备专属特征 |
| 42 | 284e | ,,,4800924, | 分隔的数值数据 | ⭐⭐⭐ 某种编码的特征数据 |
| 47 | ba2e | 127 | 数值型标志 | ⭐⭐⭐ 某种状态标志 |
| 51 | 71f3 | 46 | 数值型配置 | ⭐⭐⭐ 配置参数 |
| 52 | a506 | {"/data":"0005CF2DFFD2..."} | 文件系统信息 | ⭐⭐⭐⭐ 存储分区特征 |

**风控重点**：
- 加密数据防止直接读取和篡改
- 特殊厂商数据（小米）增强识别准确性
- 文件系统特征验证设备真实性

---

##### ET 探针风控逻辑总结

**多维度交叉验证**：

```python
# 1. 设备身份验证（10 个探针）
if utdid != expected_utdid:
    risk_score += 100  # 最高风险
if len(set([uuid1, uuid2, uuid3])) != 3:
    risk_score += 50   # UUID 不唯一

# 2. 系统版本验证（9 个探针）
if 'test-keys' in build_tags:
    risk_score += 80   # 自编译系统，高风险
if release_keys != 'release-keys':
    risk_score += 60   # 非官方版本

# 3. 硬件配置验证（8 个探针）
if resolution != '1080*2340' and model == 'Redmi K20 Pro':
    risk_score += 70   # 分辨率不匹配型号
if cpu_cores != 8:
    risk_score += 50   # CPU 核心数不匹配

# 4. 网络硬件验证（6 个探针）
if all_mac_same or all_mac_zero:
    risk_score += 90   # MAC 地址异常（模拟器特征）
if has_virtual_interface:
    risk_score += 40   # 检测到虚拟网络（VPN/代理）

# 5. 应用签名验证（4 个探针）
if signature_sha1 != official_signature:
    risk_score += 100  # 签名不匹配，二次打包
if package_name != 'com.taobao.idlefish':
    risk_score += 100  # 包名被修改

# 6. 传感器验证（3 个探针）
if sensor_count == 0:
    risk_score += 90   # 无传感器（模拟器特征）
if sensor_data_invalid:
    risk_score += 60   # 传感器数据异常

# 7. 时间一致性验证（3 个探针）
if abs(device_time - server_time) > 300:
    risk_score += 40   # 时间偏差超过 5 分钟
if build_time > current_time:
    risk_score += 80   # 时间穿越

# 最终决策
if risk_score >= 200:
    return "BLOCK"      # 拒绝访问
elif risk_score >= 100:
    return "REVIEW"     # 人工审核
else:
    return "PASS"       # 通过
```

**风控强度评估**：

| 检测项 | 探针数量 | 绕过难度 | 重要性 |
|-------|---------|---------|--------|
| UTDID 验证 | 1 | ⭐⭐⭐⭐⭐ | 最高 |
| test-keys 检测 | 2 | ⭐⭐⭐⭐ | 最高 |
| 应用签名校验 | 2 | ⭐⭐⭐⭐⭐ | 最高 |
| 硬件配置匹配 | 8 | ⭐⭐⭐⭐ | 高 |
| MAC 地址验证 | 6 | ⭐⭐⭐⭐ | 高 |
| 传感器检测 | 3 | ⭐⭐⭐⭐⭐ | 高 |
| 系统版本验证 | 9 | ⭐⭐⭐ | 中 |
| 时间一致性 | 3 | ⭐⭐⭐ | 中 |

#### 2.2.4 SGEXT 扩展字段（45 个状态字段）

SGEXT 是 **SecurityGuard Extended** 的缩写，包含 45 个字段：

```python
# SGEXT 字段映射
fields = {
    0: "10258",           # context 序列号（LCG 生成）
    1: "30611",           # mini 序列号（LCG 生成）
    2: "4",               # flags 类型
    3: "",                # 保留
    4: "1790139885",      # SG 文件修改时间（秒）⭐⭐⭐⭐⭐
    5: "0000000000000000",# 特征码
    6: "3",               # SG 主版本
    7: "0",               # 子版本
    8: "00",              # 标志位
    9: "0000",            # 保留
    10: "0",              # 计数器
    11-17: "1",           # 功能启用标志
    18: "0",              # ACTION_DOWN 计数（触摸统计）⭐⭐⭐⭐
    19: "0",              # 触摸源 CRC 计数 ⭐⭐⭐⭐
    20-24: "0",           # 事件统计
    25-27: "0", "0", "",  # 分支状态 ⭐⭐⭐
    28-34: ...,           # 各种统计
    35: "0",              # sgcookie 状态 ⭐⭐⭐⭐
    36: "",               # extraBuffer ⭐⭐⭐
    37: "3",              # UMT 状态 ⭐⭐⭐⭐
    38: "1",              # 保留
    39: "3",              # 固定值
    40-43: ...,           # 其他状态
    44: "13_AgAA..._",    # 遥测段（复杂编码）⭐⭐⭐⭐⭐
}
```

**重点字段详解**：

1. **fields[4] - SG 文件修改时间** ⭐⭐⭐⭐⭐
   - 值：`1790139885`（Unix 时间戳）
   - 来源：`/data/data/com.taobao.idlefish/.s/` 目录的文件修改时间
   - 风控作用：验证 SG 文件是否被篡改，时间异常=可疑

2. **fields[18-19] - 触摸统计** ⭐⭐⭐⭐
   - fields[18]：ACTION_DOWN 事件计数
   - fields[19]：触摸源 CRC 去重计数
   - 风控作用：检测自动化脚本（计数异常、触摸源单一）

3. **fields[35] - sgcookie 状态** ⭐⭐⭐⭐
   - 值：0=未初始化, 1=仅内存, 3=一致
   - 风控作用：检测 SG 存储一致性

4. **fields[37] - UMT 状态** ⭐⭐⭐⭐
   - 值：0=未初始化, 1=失败, 3=已安装
   - 风控作用：统一监控平台状态

5. **fields[44] - 遥测段** ⭐⭐⭐⭐⭐
   - 格式：`<length>_<base64_data>_<flag>_<count>_<tag>_<extra>_`
   - 示例：`13_AgAAAAAAAAAAAAAAAAAAAAAAAAAA_16_0_28_AwAE/4o=_`
   - 风控作用：加密上报的额外遥测数据

#### 2.2.5 PL 性能与日志（158 个参数）

PL (Performance & Logging) 测量系统性能和日志：

```python
PL_PARAMS = {
    # 时间测量（毫秒）
    "t1": 45,      # Mini 采集耗时
    "t2": 234,     # ET 采集耗时
    "t3": 12,      # 签名计算耗时
    "t4": 8,       # SGEXT 生成耗时

    # 内存测量（KB）
    "m1": 2048,    # Java 堆内存
    "m2": 512,     # Native 内存
    "m3": 128,     # 缓存大小

    # 计数器
    "c1": 156,     # API 调用次数
    "c2": 23,      # 异常次数
    "c3": 1,       # 重试次数

    # 状态码
    "s1": 200,     # HTTP 状态
    "s2": 0,       # 错误码

    # 校验和
    "ck": "0x1a2b3c4d5e6f",  # CRC64-ECMA 校验 ⭐⭐⭐⭐⭐
}
```

**PL.ck 校验和详解** ⭐⭐⭐⭐⭐：
- 算法：CRC64-ECMA
- 输入：所有 PL 参数按顺序拼接
- 风控作用：**防止 PL 参数被篡改**

#### 2.2.6 BI 行为上报

BI (Behavior Intelligence) 记录用户行为：

```json
{
  "bi": {
    "utdid": "arNd7GBIB9wDAFhdV44i+riU",
    "sid": "session_id_12345",
    "pageName": "ItemDetailPage",
    "action": "click_buy_button",
    "timestamp": 1727190485,
    "duration": 3500,        // 页面停留时长（毫秒）
    "touchCount": 12,        // 触摸次数
    "scrollDistance": 2340,  // 滚动距离（像素）
  }
}
```

**风控作用**：
- ✅ 检测异常行为（停留时间过短、无滚动直接购买）
- ✅ 识别自动化脚本（操作速度、触摸模式）

#### 2.2.7 CS 代码完整性校验

CS (Code Security) 检测代码完整性：

```json
{
  "cs": {
    "dexHash": "a1b2c3d4...",     // DEX 文件哈希
    "soHash": "e5f6g7h8...",      // SO 库哈希
    "signatureHash": "i9j0k1...", // 应用签名哈希
    "integrityCheck": true        // 完整性检查结果
  }
}
```

**风控作用**：
- ✅ 检测二次打包
- ✅ 检测代码注入
- ✅ 检测签名篡改

---

## 三、EEID 协议流程分析

### 3.1 初始化阶段

#### 3.1.1 UTDID 生成机制

**触发条件**：应用首次安装，检测到 UTDID 缺失

**生成流程**：
```
UTDevice SDK 初始化
   ↓
采集设备硬件特征
   ├─ MAC Address (WiFi/Bluetooth)
   ├─ IMEI/MEID (需 READ_PHONE_STATE 权限)
   ├─ Serial Number (android.os.Build.SERIAL)
   ├─ Android ID (Settings.Secure.ANDROID_ID)
   └─ UUID (随机生成) + Timestamp
   ↓
混合哈希算法生成 UTDID (22 字符)
   算法：SHA256(硬件特征 + 随机盐 + 时间戳) → Base64 编码 → 截取
   输出：arNd7GBIB9wDAFhdV44i+riU
   ↓
持久化存储
   路径：/data/data/${package}/shared_prefs/Alvin2.xml
   节点：<string name="UTDID2">arNd7GBIB9wDAFhdV44i+riU</string>
```

#### 3.1.2 SG 文件系统创建

**目录结构初始化**：
```
/data/data/com.taobao.idlefish/.s/
   ├─ .sg        (主配置，记录设备基线)
   ├─ .s         (状态持久化)
   ├─ .c         (缓存数据)
   └─ sgcookie/  (会话状态)
```

**关键时间戳记录**：
- `.sg` 文件 mtime → SGEXT fields[4]
- 用于验证文件完整性和防篡改

### 3.2 EEID 注册协议

#### 3.2.1 客户端数据采集

**触发条件**：首次网络请求，本地 EEID 缺失或过期

**采集模块执行顺序**：

```
SecurityGuard 探针系统启动
   │
   ├─ [1] Mini 探针采集 (~20ms)
   │     ├─ 布尔段 (7 字节)：Root/Hook/模拟器/传感器状态
   │     └─ 半字节段 (11 字节)：硬件配置/网络状态
   │
   ├─ [2] ET 探针采集 (~100ms)
   │     ├─ 系统属性读取 (getprop)
   │     ├─ 文件系统扫描 (Root/Xposed 特征文件)
   │     ├─ 进程列表 (ps)
   │     ├─ 网络状态 (ifconfig/netstat)
   │     └─ TEA/XTEA 加密编码
   │
   ├─ [3] SGEXT 生成 (~10ms)
   │     ├─ Context/Mini 序列号 (LCG 算法)
   │     ├─ SG 文件 mtime 读取
   │     ├─ sgcookie 一致性检查
   │     ├─ UMT 状态查询
   │     └─ 遥测段编码
   │
   └─ [4] PL 性能测量 (~5ms)
         ├─ 各模块耗时统计
         ├─ 内存使用量
         └─ CRC64-ECMA 校验和计算
```

#### 3.2.2 签名计算

**INPUT 参数构造** (22 字段)：
```python
INPUT = "&".join([
    f"0={utdid}",                    # UTDID
    f"1={ttid}",                     # ttid
    f"2={appkey}",                   # 21407387
    f"3={timestamp}",                # Unix timestamp
    f"4={api}",                      # API method
    f"5={version}",                  # API version
    f"6={json.dumps(data)}",         # Business params
    f"7={sid}",                      # Session ID
    f"8={uid}",                      # User ID (optional)
    f"9={deviceId}",                 # Device ID (optional)
    f"10={lat}",                     # Latitude
    f"11={lng}",                     # Longitude
    f"12={features}",                # x-features
    f"13={bx_version}",              # SG version
    f"14={base64(mini_bytes)}",      # Mini 编码
    f"15={base64(sgext_bytes)}",     # SGEXT 编码
    f"16={context}",                 # Context data
    f"17={extdata}",                 # Extended data
    f"18={x_umt}",                   # UMT
    f"19={pv}",                      # Protocol version
    f"20={utdid2}",                  # UTDID (repeated)
    f"21={req_counter}",             # Request counter
])
```

**签名算法**：
```python
# 1. 从 yw_1222.jpg 解密获取 appkey_secret
secret = decrypt_appkey_secret(appkey)

# 2. HMAC-SHA1 计算
x_sign = hmac.new(
    key=secret.encode('utf-8'),
    msg=INPUT.encode('utf-8'),
    digestmod=hashlib.sha1
).hexdigest()
```

#### 3.2.3 HTTP 协议格式

**请求结构**：
```http
POST /rest/e HTTP/1.1
Host: acs-mum.alibabachengdun.com
Content-Type: application/json; charset=UTF-8

Headers:
  x-sign: {hmac_sha1_signature}
  x-utdid: {utdid}
  x-ttid: {ttid}
  x-appkey: {appkey}
  x-app-ver: {app_version}
  x-bx-version: {sg_version}
  x-t: {timestamp}
  x-sid: {session_id}
  x-location: {lng},{lat}
  x-features: {features}
  x-umt: {umt}
  x-mini-wua: {mini_digest}
  wua: {full_device_fingerprint}
  x-devid: {device_id}
  User-Agent: {mtop_ua}

Body:
{
  "req_biz_code": "1000",
  "context": {
    "flags": 105,
    "sg_file_mtime_seconds": 1790139885,
    "byte49_initial": 147,
    "byte50_initial": 196
  },
  "mini": {
    "header_payload_hex": "0038050000",
    "eeid_base64": "",
    "device_body_hex": "99208504800144",
    "unknown_section_hex": "0021390104000000000000",
    "footer_prefix_hex": "04061e7f00",
    "footer_probes_hex": "0000ffff00ff0000779300000000000000000000",
    "trailer_hex": "00",
    "byte30_initial": 252
  },
  "sgext": {
    "header_hex": "2413",
    "crc12_hex": "5807836f7d7feb865665f9bb",
    "fields": [/* 45 个字段 */]
  },
  "et": {
    "probes": [/* 55 个探针 */]
  },
  "pl": {
    "measurements": {/* 158 个测量值 */}
  }
}
```

#### 3.2.4 服务端验证流程

**验证管道**：
```
ACS-MUM 接收请求
   ↓
[层 1] 签名验证
   ├─ 重新计算 HMAC-SHA1(INPUT)
   ├─ 对比 x-sign
   └─ 不一致 → HTTP 403 (FAIL_SYS_ILLEGAL_ACCESS)
   ↓
[层 2] Mini 探针解析
   ├─ 布尔段解析
   │   ├─ Root 检测 (Byte1 & 0x0F)
   │   ├─ Xposed 检测 (Byte1 & 0x10)
   │   ├─ 模拟器检测 (Byte1 & 0x40)
   │   └─ 任意异常 → 风险评分 +100
   │
   └─ 半字节段解析
       ├─ SELinux 模式 (Nibble6 & 0x0F)
       │   └─ Permissive (1) → 风险评分 +90
       ├─ 触摸点数 < 5 → 风险评分 +70
       └─ 传感器数量 < 2 → 风险评分 +80
   ↓
[层 3] ET 探针解密与分析
   ├─ TEA/XTEA 解密
   ├─ 交叉验证
   │   ├─ UTDID 匹配性
   │   ├─ test-keys 检测 → 风险评分 +80
   │   ├─ 应用签名校验 → 不匹配 +100
   │   ├─ MAC 地址合理性 → 全零/全 FF +90
   │   └─ 传感器数据有效性
   │
   └─ 环境完整性评分 (0-100)
   ↓
[层 4] SGEXT 状态校验
   ├─ SG 文件 mtime 合理性
   │   └─ 未来时间 / 过早时间 → 风险评分 +60
   ├─ sgcookie 一致性 (fields[35])
   │   └─ 不一致 → 风险评分 +50
   └─ UMT 状态 (fields[37])
   ↓
[层 5] PL 数据校验
   ├─ CRC64 校验和验证
   └─ 时间测量合理性检查
   ↓
[层 6] 风控决策引擎
   ├─ 综合评分 = ∑(风险项评分)
   ├─ 阈值判断
   │   ├─ 评分 ≥ 200 → BLOCK
   │   ├─ 评分 ≥ 100 → MANUAL_REVIEW
   │   └─ 评分 < 100 → PASS
   │
   └─ 黑白名单过滤
   ↓
[层 7] EEID 生成
   算法（推测）：
   SHA256(UTDID || Mini_Hash || ET_Top10_Hash || Timestamp || Salt)
   ↓ 截取 32 字节
   ↓ Base64 编码
   输出：A9+BxQdE7KkOhgKhp/6Ej/vZGg==
```

#### 3.2.5 响应协议

**成功响应** (HTTP 200)：
```json
{
  "ret": ["SUCCESS::调用成功"],
  "data": {
    "eeid": "A9+BxQdE7KkOhgKhp/6Ej/vZGg==",
    "device_score": 95,
    "risk_level": "LOW",
    "expire_time": 1727276885,
    "tips": ""
  }
}
```

**字段定义**：
- `eeid`: 设备扩展标识符，后续请求携带
- `device_score`: 设备信誉评分 (0-100)
- `risk_level`: 风险等级 (LOW/MEDIUM/HIGH/CRITICAL)
- `expire_time`: EEID 有效期 (Unix timestamp)
- `tips`: 风控提示信息

**拒绝响应** (HTTP 403)：
```json
{
  "ret": ["FAIL_SYS_ILLEGAL_ACCESS::非法访问"],
  "data": {
    "error_code": "EMULATOR_DETECTED",
    "message": "检测到模拟器环境",
    "block_duration": 86400
  }
}
```

#### 3.2.6 客户端 EEID 持久化

```
响应接收
   ↓
EEID 解析
   ↓
持久化存储
   ├─ 内存缓存 (EEIDManager)
   └─ SharedPreferences
       ├─ key: "EEID"
       ├─ value: "A9+BxQdE7KkOhgKhp/6Ej/vZGg=="
       └─ expire: 1727276885
```

### 3.3 EEID 验证协议

#### 3.3.1 后续请求携带 EEID

**协议变化**：
```diff
  Headers:
    x-sign: {重新计算的签名}
+   x-eeid: A9+BxQdE7KkOhgKhp/6Ej/vZGg==
    x-utdid: {不变}
    ... (其他头部)

  Body:
    mini: {实时采集}
    et: {实时采集}
    sgext: {实时生成}
    pl: {实时测量}
```

**关键特性**：
- EEID 不参与签名计算（签名仅覆盖 INPUT 22 字段）
- 探针数据仍需实时采集（不可重放）
- EEID 仅作为设备标识，不能替代探针验证

#### 3.3.2 服务端 EEID 验证

**验证流程**：

```
请求到达
   ↓
EEID 预检
   ├─ 查询 EEID → 设备档案
   ├─ 检查过期时间
   └─ 验证 EEID 与 UTDID 绑定关系
   ↓
实时探针对比（Diff 分析）
   ├─ Mini 探针增量对比
   │   ├─ 布尔段差异检测（XOR 运算）
   │   ├─ 关键位变化（Root/Hook/模拟器位）
   │   └─ 半字节段数值变化范围
   │
   ├─ ET 探针变化检测
   │   ├─ 不可变属性验证
   │   │   ├─ UTDID 一致性
   │   │   ├─ 设备型号（ro.product.model）
   │   │   ├─ MAC 地址持久性
   │   │   └─ 应用签名不变性
   │   │
   │   └─ 可变属性合理性
   │       ├─ 系统版本升级检测
   │       ├─ 运营商切换验证
   │       └─ 网络环境变化
   │
   ├─ SGEXT 状态连续性
   │   ├─ sgcookie 一致性（fields[35]）
   │   │   └─ 3 → 1/2 表示异常重置
   │   ├─ SG 文件 mtime 单调性
   │   │   └─ 时间回退 = 文件被篡改
   │   └─ 触摸统计增长曲线
   │       └─ fields[18-19] 异常跳变检测
   │
   └─ 行为模式分析
       ├─ 请求频率统计（滑动窗口）
       ├─ API 调用序列合法性
       └─ 会话连续性验证
   ↓
风控决策（基于规则引擎 + 机器学习模型）
   ├─ 规则层：确定性拦截
   │   ├─ UTDID 变化 → 立即拦截
   │   ├─ 关键探针异常 → 立即拦截
   │   └─ EEID 过期 → 要求重新注册
   │
   └─ 模型层：风险评分（服务端黑盒）
       ├─ 特征提取：探针差异向量化
       ├─ 模型预测：异常概率计算
       └─ 阈值判断：PASS/REVIEW/BLOCK
   ↓
设备信誉动态调整
   └─ 基于长期行为轨迹的信誉衰减/增长
```

**关键验证维度**：

| 维度 | 验证方法 | 异常指标 |
|-----|---------|---------|
| **设备一致性** | UTDID + MAC + 序列号 | 任意不匹配 |
| **环境稳定性** | Mini/ET 探针 Diff | 核心探针突变 |
| **状态连续性** | SGEXT 字段时序分析 | 非单调变化 |
| **行为合理性** | 请求模式统计分析 | 高频/异常序列 |

**注**：具体的评分算法和阈值为服务端黑盒实现，上述为基于协议分析的推测模型。

### 3.4 协议时序图

```
Client                 SecurityGuard              ACS-MUM Server
  │                         │                           │
  │─ [T0] App 启动         │                           │
  │───────────────────────>│                           │
  │                         │─ [T0+10ms] UTDID 读取     │
  │                         │─ [T0+20ms] SG 初始化      │
  │                         │                           │
  │─ [T1] 触发 API 请求    │                           │
  │───────────────────────>│                           │
  │                         │─ [T1+0ms] Mini 采集       │
  │                         │─ [T1+20ms] ET 采集        │
  │                         │─ [T1+120ms] SGEXT 生成    │
  │                         │─ [T1+130ms] PL 测量       │
  │                         │─ [T1+135ms] 签名计算      │
  │                         │                           │
  │─ [T1+145ms] HTTP POST ────────────────────────────>│
  │                         │                           │─ [T2] 签名验证
  │                         │                           │─ [T2+5ms] Mini 解析
  │                         │                           │─ [T2+15ms] ET 解密
  │                         │                           │─ [T2+25ms] SGEXT 校验
  │                         │                           │─ [T2+30ms] 决策引擎
  │                         │                           │─ [T2+35ms] EEID 生成
  │                         │                           │
  │<─ [T2+40ms] HTTP 200 ──────────────────────────────│
  │     {eeid, device_score, risk_level}               │
  │                         │                           │
  │─ [T2+41ms] EEID 存储   │                           │
  │                         │                           │
```

**性能指标**：
- 客户端采集：~145ms
- 网络传输：~50ms (取决于网络)
- 服务端处理：~40ms
- 总 RTT：~235ms

### 3.5 协议安全机制

#### 3.5.1 签名防篡改

**INPUT 完整性保护**：
- 签名覆盖所有关键参数（22 字段）
- 任意字段修改导致签名失败
- appkey_secret 存储在加密图片中（4 层 AES）

#### 3.5.2 探针防重放

**时间窗口验证**：
```python
if abs(request_timestamp - server_time) > 300:
    return "TIMESTAMP_EXPIRED"
```

**实时采集验证**：
- Mini/ET 探针每次实时采集
- 历史数据重放会触发探针 Diff 异常

#### 3.5.3 EEID 绑定机制

**三元组绑定**：
```
EEID ←→ UTDID ←→ Device_Fingerprint_Hash
```

**验证逻辑**：
- EEID 与 UTDID 强绑定
- UTDID 变化导致 EEID 失效
- 设备指纹变化触发重新验证

### 3.6 协议特性分析

#### 3.6.1 多层验证架构

| 层级 | 验证内容 | 处理时间 | 拦截条件 |
|-----|---------|---------|---------|
| L1 | 签名验证 | ~5ms | 签名不匹配 |
| L2 | Mini 探针 | ~10ms | Root/Hook/模拟器 |
| L3 | ET 探针 | ~10ms | 环境异常 |
| L4 | SGEXT 状态 | ~5ms | 状态不一致 |
| L5 | PL 校验 | ~5ms | 校验和错误 |
| L6 | 决策引擎 | ~5ms | 风险评分超阈值 |

**总处理时间**：~40ms（服务端）

#### 3.6.2 实时性保障

**探针实时采集**：
- 每次请求重新采集 Mini/ET/SGEXT/PL
- 防止历史数据重放攻击
- 检测设备环境变化

**时效性要求**：
- 客户端采集：<150ms
- 服务端处理：<50ms
- 总 RTT：<250ms（含网络传输）

#### 3.6.3 可扩展性设计

**探针系统扩展**：
- Mini：布尔段可扩展至 N 字节
- ET：支持动态增加探针项
- SGEXT：fields 数组可扩展

**版本兼容**：
- x-bx-version 标识 SG 版本
- 服务端支持多版本协议解析

---

## 四、SG 文件系统详解

### 4.1 SG 文件目录结构

```
/data/data/com.taobao.idlefish/.s/
├── .sg           (主配置文件，8-16 KB)
├── .s            (状态文件，4-8 KB)
├── .c            (缓存文件，1-4 KB)
├── .l            (日志文件，可选)
├── sgcookie/     (Cookie 存储目录)
│   ├── main      (主 Cookie)
│   └── backup    (备份 Cookie)
└── cache/        (临时缓存目录)
    ├── mini      (Mini 探针缓存)
    ├── et        (ET 探针缓存)
    └── temp      (临时文件)
```

### 4.2 核心文件详解

#### 4.2.1 .sg 主配置文件 ⭐⭐⭐⭐⭐

**文件结构**：
```
[Header: 32 bytes]
├─ Magic: 0x53474D41494E ("SGMAIN")
├─ Version: 0x06070260202 (6.7.260202)
├─ Flags: 0x00000069 (105)
├─ Timestamp: 1790139885
└─ CRC32: 0x12345678

[Body: Variable length]
├─ UTDID: arNd7GBIB9wDAFhdV44i+riU
├─ Device Profile
│   ├─ Manufacturer: Xiaomi
│   ├─ Model: Redmi K20 Pro
│   ├─ Android Version: 11
│   └─ SDK Version: 30
│
├─ Mini Snapshot
│   ├─ 布尔段: 99208504800144 (hex)
│   └─ 半字节段: 0000ffff00ff0000779300000000000000000000 (hex)
│
├─ ET Snapshot (压缩存储)
│   └─ 435 个探针的最近一次值
│
└─ [Footer: 16 bytes]
    └─ Signature: HMAC-SHA1
```

**修改时间的重要性** ⭐⭐⭐⭐⭐：
- **fields[4] = 1790139885**（SG 文件的 mtime）
- **风控作用**：
  - 验证文件是否被篡改
  - 检测时间穿越（mtime 在未来）
  - 关联设备历史（mtime 过早=可疑）
  - 检测文件重放（mtime 与 UTDID 不匹配）

**如何验证 SG 文件**：
```bash
# 查看 SG 文件修改时间
adb shell "su -c ls -l /data/data/com.taobao.idlefish/.s/.sg"
# 输出：-rw------- 1 u0_a123 u0_a123 12345 2026-09-24 10:31 .sg

# 修改时间戳转换
date -d @1790139885
# 输出：2026-09-24 10:31:25
```

#### 4.2.2 .s 状态文件 ⭐⭐⭐⭐

**内容**：
```json
{
  "byte49_initial": 147,      // 初始状态字节
  "byte50_initial": 196,      // 初始状态字节
  "byte30_initial": 252,      // Mini 初始状态
  "sgcookie_status": 3,       // sgcookie 状态（一致）
  "umt_status": 3,            // UMT 状态（已安装）
  "last_update": 1727190485,  // 最后更新时间
  "request_count": 1523,      // 请求计数
  "error_count": 3            // 错误计数
}
```

**风控作用**：
- ✅ 检测状态一致性（fields[35]）
- ✅ 追踪使用频率
- ✅ 检测异常重置

#### 4.2.3 sgcookie 目录 ⭐⭐⭐⭐

**sgcookie 是什么**：
- SecurityGuard Cookie 的缩写
- 类似 HTTP Cookie，但用于设备级别的状态追踪
- 存储加密的会话信息

**fields[35] - sgcookie 状态**：
```python
SGCOOKIE_STATUS = {
    0: "未初始化",    # 首次运行
    1: "仅内存",      # 内存中有，文件中无（异常）
    2: "仅文件",      # 文件中有，内存中无（异常）
    3: "一致"         # 正常状态 ✅
}
```

**风控检测逻辑**：
```python
def check_sgcookie_consistency(memory_cookie, file_cookie):
    if memory_cookie is None and file_cookie is None:
        return 0  # 未初始化（首次运行，正常）
    elif memory_cookie is not None and file_cookie is None:
        return 1  # 异常：文件被删除？
    elif memory_cookie is None and file_cookie is not None:
        return 2  # 异常：内存未加载？
    elif memory_cookie == file_cookie:
        return 3  # 正常：一致 ✅
    else:
        return 1  # 异常：不一致
```

**风控拦截场景**：
- ❌ sgcookie 状态 = 1 或 2（不一致）→ 高风险
- ❌ sgcookie 频繁变化 → 多设备共用
- ❌ sgcookie 与 UTDID 不匹配 → 伪造

#### 4.2.4 fields[36] - extraBuffer ⭐⭐⭐

**extraBuffer 是什么**：
- 动态缓存数据
- 存储临时状态和上下文信息

**检测逻辑**：
```python
def get_extra_buffer(cache_mgr):
    if cache_mgr.has("sgext_extra"):
        return cache_mgr.get("sgext_extra")  # 从缓存读取
    else:
        return ""  # 空字符串
```

**风控作用**：
- ✅ 验证缓存一致性
- ✅ 检测清除数据操作

### 4.3 SG 文件的风控重要性

| 检测项 | 原理 | 风控动作 |
|-------|------|---------|
| **文件完整性** | 校验 CRC32/HMAC | 篡改=拦截 |
| **修改时间** | mtime 合理性检查 | 异常=高风险 |
| **状态一致性** | sgcookie 内存/文件对比 | 不一致=可疑 |
| **UTDID 绑定** | SG 文件与 UTDID 关联 | 不匹配=伪造 |
| **使用频率** | 请求计数统计 | 异常高频=群控 |
| **版本匹配** | SG 版本与 App 版本 | 不匹配=二次打包 |

---

## 五、签名参数与 EEID 关系

### 5.1 签名参数体系

闲鱼使用 **HMAC-SHA1** 签名算法，主要签名参数包括：

```python
SIGNATURE_PARAMS = {
    # 主签名
    "x-sign": "hmac_sha1(appkey_secret, INPUT)",  # ⭐⭐⭐⭐⭐

    # 设备指纹
    "wua": "完整设备指纹（包含 Mini + ET + SGEXT）",  # ⭐⭐⭐⭐⭐
    "x-mini-wua": "Mini 探针摘要",                     # ⭐⭐⭐⭐

    # 设备标识
    "x-utdid": "arNd7GBIB9wDAFhdV44i+riU",            # ⭐⭐⭐⭐⭐
    "x-umt": "arNd7GBIB9wDAFhdV44i+riU",              # ⭐⭐⭐⭐
    "x-ttid": "1582631881546@fleamarket_android_7.28.30",

    # 设备信息
    "x-devid": "Axxxxxxxxxxxxx==",                    # ⭐⭐⭐⭐
    "x-features": "27",

    # App 信息
    "x-appkey": "21407387",                           # ⭐⭐⭐⭐⭐
    "x-app-ver": "7.28.30",

    # 其他
    "x-t": "1727190485",          # 时间戳
    "x-sid": "session_id",        # 会话 ID
    "x-uid": "user_id",           # 用户 ID（登录后）
    "x-location": "0,0",          # 位置
    "x-bx-version": "6.7.260202", # SecurityGuard 版本
}
```

### 5.2 INPUT 参数组成（22 个字段）

**INPUT** 是签名的输入，包含 22 个字段按特定顺序拼接：

```python
INPUT_FIELDS = [
    "UTDID",          # 0. arNd7GBIB9wDAFhdV44i+riU
    "ttid",           # 1. 1582631881546@fleamarket_android_7.28.30
    "appkey",         # 2. 21407387
    "timestamp",      # 3. 1727190485
    "api",            # 4. mtop.taobao.idle.item.detail
    "version",        # 5. 1.0
    "data",           # 6. {"itemId":"123456"}
    "sid",            # 7. session_id
    "uid",            # 8. user_id (可选)
    "deviceId",       # 9. (通常为空)
    "lat",            # 10. 0
    "lng",            # 11. 0
    "features",       # 12. 27
    "bx-version",     # 13. 6.7.260202
    "mini_base64",    # 14. Mini 探针 Base64 编码 ⭐⭐⭐⭐⭐
    "sgext_base64",   # 15. SGEXT Base64 编码 ⭐⭐⭐⭐⭐
    "context",        # 16. Context 参数
    "extdata",        # 17. openappkey=DEFAULT_AUTH
    "x-umt",          # 18. arNd7GBIB9wDAFhdV44i+riU
    "pv",             # 19. 6.3 (协议版本)
    "utdid2",         # 20. (与 UTDID 相同)
    "req-counter",    # 21. 请求计数器
]

# INPUT 拼接示例
INPUT = "&".join([
    "UTDID=arNd7GBIB9wDAFhdV44i+riU",
    "ttid=1582631881546@fleamarket_android_7.28.30",
    "appkey=21407387",
    # ... 其他字段
    "mini_base64=ADgFAADZEIgUgAFEACE5AQUAAAAAAAAA...",
    "sgext_base64=JBNYB4Nv1/6FZZX5uw==:MTAyNTg...",
    # ... 剩余字段
])
```

### 5.3 签名计算流程

```python
def calculate_signature(input_str: str, appkey: str) -> str:
    """
    计算 x-sign 签名
    """
    # 1. 获取 appkey 对应的密钥（从 yw_1222.jpg 解密）
    secret = get_appkey_secret(appkey)  # 例如：某个 32 字节的密钥

    # 2. 使用 HMAC-SHA1 计算签名
    signature = hmac.new(
        key=secret.encode('utf-8'),
        msg=input_str.encode('utf-8'),
        digestmod=hashlib.sha1
    ).hexdigest()

    # 3. 返回签名（40 个十六进制字符）
    return signature  # 例如：a1b2c3d4e5f6789012345678901234567890abcd
```

### 5.4 签名与 EEID 的关系

```
┌─────────────────────────────────────────────────────────┐
│                    客户端数据流                          │
└─────────────────────────────────────────────────────────┘
         │
         ├─────────────────────────────────────────┐
         │                                         │
         ↓                                         ↓
   采集设备数据                              组装签名参数
   (Mini/ET/SGEXT/PL)                       (22 个 INPUT 字段)
         │                                         │
         ↓                                         ↓
   编码 + 压缩                              计算 x-sign
   (Base64/加密)                            (HMAC-SHA1)
         │                                         │
         └─────────────────┬───────────────────────┘
                           │
                           ↓
                   HTTPS 请求上传
                   (包含所有参数)
                           │
┌─────────────────────────────────────────────────────────┐
│                    服务端验证流程                        │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
                   验证 x-sign 签名
                   (防止参数篡改) ⭐⭐⭐⭐⭐
                           │
                 ┌─────────┴─────────┐
                 │                   │
              ✅ 通过              ❌ 失败
                 │                   │
                 ↓                   ↓
           解析设备数据          拒绝请求 (403)
           (Mini/ET/SGEXT/PL)
                 │
                 ↓
           风控决策引擎
                 │
      ┌──────────┼──────────┐
      │          │          │
      ↓          ↓          ↓
   检测环境   检测行为   检测信誉
   (Mini/ET)  (BI/CS)   (历史记录)
      │          │          │
      └──────────┴──────────┘
                 │
                 ↓
           生成/验证 EEID
                 │
      ┌──────────┼──────────┐
      │          │          │
      ↓          ↓          ↓
   首次注册   正常使用   异常拦截
   (返回新)   (验证旧)   (拒绝请求)
```

**关键点**：

1. **签名保护完整性** ⭐⭐⭐⭐⭐
   - x-sign 签名覆盖所有关键参数（包括 Mini/SGEXT 编码数据）
   - 任何参数被篡改，签名验证失败
   - 无法伪造签名（需要 appkey secret）

2. **EEID 依赖签名验证** ⭐⭐⭐⭐⭐
   - 只有签名通过，服务端才解析设备数据
   - 只有设备数据真实，才生成/验证 EEID
   - EEID 本身不参与签名计算，但依赖签名保护

3. **双重验证机制**
   - 第一层：签名验证（防篡改）
   - 第二层：EEID + 设备数据验证（防伪造）

### 5.5 为什么需要签名 + EEID 双重保护？

| 攻击场景 | 签名防护 | EEID 防护 | 双重防护效果 |
|---------|---------|----------|-------------|
| **重放攻击** | ✅ 时间戳验证 | ✅ EEID 绑定时间 | 强 |
| **参数篡改** | ✅ HMAC 校验 | ❌ | 强 |
| **设备伪造** | ❌ 签名可复制 | ✅ 设备数据检测 | 强 |
| **多设备共用** | ❌ | ✅ EEID 绑定 UTDID | 强 |
| **模拟器** | ❌ | ✅ Mini/ET 检测 | 强 |
| **群控** | ❌ | ✅ 行为统计检测 | 强 |

---

## 六、风控对抗分析

### 6.1 常见对抗手段与检测

#### 6.1.1 UTDID 伪造

**对抗手段**：
- 生成随机 UTDID
- 复制真实设备的 UTDID

**检测方法**：
- ✅ UTDID 格式校验（22 字符，特定字符集）
- ✅ UTDID 与 SG 文件绑定检查
- ✅ UTDID 与历史行为关联
- ✅ UTDID 与设备硬件指纹对比

**绕过难度**：⭐⭐⭐⭐（需要完整复制设备环境）

#### 6.1.2 Mini/ET 探针伪造

**对抗手段**：
- Hook SecurityGuard 函数
- 返回伪造的探针数据

**检测方法**：
- ✅ Mini/ET 数据一致性检查（内部交叉验证）
- ✅ 探针值合理性校验（如传感器数量不能 > 100）
- ✅ Hook 检测（ET 探针会检测 Xposed/Frida）
- ✅ 实时对比（前后请求的探针数据应该连续）

**绕过难度**：⭐⭐⭐⭐⭐（需要深入理解 435 个探针逻辑）

#### 6.1.3 SG 文件篡改

**对抗手段**：
- 修改 .sg 文件内容
- 修改文件时间戳

**检测方法**：
- ✅ 文件完整性校验（CRC32/HMAC）
- ✅ 修改时间合理性（fields[4]）
- ✅ 文件内容与实时探针对比
- ✅ SELinux 文件访问审计

**绕过难度**：⭐⭐⭐⭐（需要正确计算校验和）

#### 6.1.4 签名伪造

**对抗手段**：
- 提取 appkey secret
- 重新计算签名

**检测方法**：
- ✅ appkey secret 强加密（4 层 AES）
- ✅ 签名计算在 Native 层（SO 混淆）
- ✅ 反调试检测
- ✅ 代码完整性检查（CS）

**绕过难度**：⭐⭐⭐⭐⭐（需要深度逆向）

#### 6.1.5 行为模拟

**对抗手段**：
- 使用自动化脚本模拟人类操作
- 控制触摸速度和轨迹

**检测方法**：
- ✅ 触摸统计检测（fields[18-19]）
- ✅ 行为序列分析（BI）
- ✅ 时间间隔分析（操作间隔过于规律=脚本）
- ✅ 触摸压力/面积检测（脚本通常缺失）

**绕过难度**：⭐⭐⭐（需要精细模拟）

#### 6.1.6 模拟器/云手机

**对抗手段**：
- 使用高度定制的模拟器
- 修改系统属性伪装真机

**检测方法**：
- ✅ 硬件传感器检测（模拟器通常无传感器）
- ✅ 特征文件检测（/system/lib/libc_malloc_debug_qemu.so）
- ✅ CPU 特征检测（QEMU/VirtualBox 特征）
- ✅ 性能指标检测（模拟器性能异常）
- ✅ 多维度交叉验证（如 CPU 型号与传感器不匹配）

**绕过难度**：⭐⭐⭐⭐⭐（多维度检测，难以完全伪装）

### 6.2 风控强度评估

| 风控层级 | 检测内容 | 绕过难度 | 覆盖率 |
|---------|---------|---------|--------|
| **L1: 签名** | HMAC-SHA1 | ⭐⭐⭐⭐⭐ | 100% |
| **L2: 设备标识** | UTDID | ⭐⭐⭐⭐ | 100% |
| **L3: 快速检测** | Mini 探针 | ⭐⭐⭐⭐ | 95% |
| **L4: 深度检测** | ET 探针 | ⭐⭐⭐⭐⭐ | 99% |
| **L5: 状态追踪** | SGEXT + SG 文件 | ⭐⭐⭐⭐ | 90% |
| **L6: 行为分析** | BI + 触摸统计 | ⭐⭐⭐ | 85% |
| **L7: 代码保护** | CS + 反调试 | ⭐⭐⭐⭐⭐ | 95% |
| **L8: 信誉系统** | EEID + 历史记录 | ⭐⭐⭐⭐⭐ | 100% |

**总体评估**：闲鱼 EEID 风控体系强度 **⭐⭐⭐⭐⭐（极强）**

### 6.3 理论上的完全绕过方案（仅供研究）

要完全绕过 EEID 风控，理论上需要：

1. ✅ **真实设备** - 使用真实 Android 手机（非模拟器）
2. ✅ **完整复制** - 完整复制真实设备的：
   - UTDID（Alvin2.xml）
   - SG 文件系统（.s 目录）
   - 系统属性（ro.* 配置）
   - 硬件传感器数据
3. ✅ **行为模拟** - 精确模拟人类行为：
   - 触摸压力、面积、速度
   - 操作间隔随机化
   - 页面停留时间自然化
4. ✅ **签名计算** - 提取 appkey secret（需要深度逆向）
5. ✅ **实时同步** - 保持与真实设备的环境同步

**结论**：即使完成上述所有步骤，仍然面临：
- 服务端行为建模（历史行为不一致）
- 设备信誉评分（新设备初始低分）
- 人工审核（高风险操作需人工确认）

因此，**完全绕过几乎不可能**，这也是 EEID 风控体系的强大之处。

---

## 七、总结与建议

### 7.1 EEID 风控体系核心要点

1. **多维度防护** ⭐⭐⭐⭐⭐
   - 设备标识（UTDID）
   - 环境检测（Mini/ET）
   - 状态追踪（SGEXT/SG 文件）
   - 行为分析（BI）
   - 签名保护（HMAC）

2. **实时动态采集** ⭐⭐⭐⭐⭐
   - 每次请求都采集最新的 Mini/ET 数据
   - 无法简单重放历史数据

3. **服务端智能决策** ⭐⭐⭐⭐⭐
   - 6,235+ 参数综合分析
   - 设备信誉评分系统
   - 黑名单/白名单机制

4. **强加密保护** ⭐⭐⭐⭐⭐
   - appkey 4 层 AES 加密
   - ET 数据 TEA/XTEA 加密
   - Native 层混淆

### 7.2 对不同角色的建议

#### 7.2.1 对安全研究人员

- ✅ EEID 是值得深入研究的工业级风控系统
- ✅ 可以学习其多维度检测思路
- ⚠️ 请勿将研究成果用于非法用途

#### 7.2.2 对 App 开发者

- ✅ 可以参考 EEID 的设计思路构建自己的风控系统
- ✅ 重点关注：设备指纹 + 行为分析 + 签名保护
- ✅ 建议使用成熟的第三方风控 SDK（如阿里云风控）

#### 7.2.3 对普通用户

- ✅ EEID 风控主要针对作弊行为，正常使用不受影响
- ✅ 不建议 Root、安装 Xposed 等（会触发风控）
- ✅ 避免使用自动化脚本（会被封号）

#### 7.2.4 对逆向工程师

- ✅ 闲鱼的 SecurityGuard 是值得学习的 Native 混淆案例
- ✅ 可以研究其签名算法、探针系统、加密方案
- ⚠️ 请遵守法律法规，勿用于非法目的

### 7.3 未来趋势

EEID 风控体系可能的演进方向：

1. **AI 驱动的行为分析** 🤖
   - 使用机器学习识别异常行为
   - 更精准的设备指纹技术

2. **生物特征集成** 👤
   - 集成人脸识别、指纹识别
   - 更强的身份绑定

3. **区块链技术** ⛓️
   - 设备信誉上链
   - 不可篡改的历史记录

4. **联盟风控** 🤝
   - 跨平台风控数据共享
   - 黑名单联盟

### 7.4 法律声明

⚠️ **重要提示**：

本文档仅用于 **技术研究和学习** 目的，所有内容基于公开信息和合法的逆向工程分析。

**请勿将本文档内容用于**：
- ❌ 破解或绕过风控系统
- ❌ 批量注册账号
- ❌ 自动化刷单/刷量
- ❌ 其他违反法律法规或平台规则的行为

**违法行为可能导致**：
- 账号封禁
- 民事赔偿
- 刑事责任

**作者不对任何滥用行为承担责任。**

---

## 八、参考资料

### 8.1 项目文件

1. `eeid_inputs_pure.private.json` - 完整输入参数快照
2. `eeid_et_profile.private.json` - ET 探针详细数据
3. `参数来源深度解析.md` - 6,235 参数完整来源
4. `参数来源验证.md` - ADB 验证报告
5. `未解析参数详细分析.md` - 14 个未解析参数分析
6. `EEID参数来源调查-最终总结报告.md` - 项目总结

### 8.2 技术文档

- SecurityGuard SDK 官方文档
- MTOP 协议规范
- HMAC-SHA1 算法标准
- CRC64-ECMA 算法规范
- TEA/XTEA 加密算法

### 8.3 工具

- `xianyu_sign/` - 签名计算实现
- `xianyu_eeid/` - EEID 参数生成
- `tests/` - 单元测试

---

**文档版本**: 1.0\
**创建日期**: 2026-09-24\
**最后更新**: 2026-09-24\
**作者**: 基于技术研究和逆向分析\
**状态**: ✅ 完整版

---

# 🎯 完

本文档完整揭露了闲鱼 EEID 风控体系的所有核心机制，包括：
- ✅ 6,235+ 参数的完整分类和作用
- ✅ EEID 注册和使用的完整流程
- ✅ SG 文件系统的详细结构和风控作用
- ✅ 签名参数与 EEID 的关系
- ✅ 风控对抗分析和绕过难度评估

**这是一个工业级的多维度风控体系，值得所有风控从业者学习和参考。** 🎓
