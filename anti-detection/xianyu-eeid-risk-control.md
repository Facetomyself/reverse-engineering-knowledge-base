---
schema_version: 2
id: anti-detection-xianyu-eeid-risk-control
document_type: archive
scope:
  targets:
  - xianyu
  client: unknown
  version: unknown
  observed_at: unknown
sources:
- id: s1
  ref: null
  basis: source-report
  citation: 闲鱼 7.28.30（`com.taobao.idlefish`，versionCode 520）/ SecurityGuard 6.7.260202 独立分析（Redmi K20 Pro，Android 11）
  reason: 原归档明确记载出处，但未提供可定位的公开来源链接；本轮只保留来源自述。
source_completeness: unknown
tags:
- EEID
- SecurityGuard
- Mini 探针
- ET 探针
- SGEXT
- UTDID
- SG 文件
- ACS-MUM
- x-eeid
- 闲鱼
original_date: '2026-09-24'
archived_date: '2026-09-26'
---

# 闲鱼 EEID 风控体系完全揭秘

## 本轮提炼评估

本篇继续保留为脱敏来源 archive，不新增 `reference`、`case` 或 `procedure`：原始输入、私有对照材料和运行环境不可核验，服务端评分/阈值为来源推测，签名输入待验证。设备与遥测样值、私有路径、密钥线索及细粒度规避细节已脱敏或抽象；不把来源结果推广为当前客户端/服务端事实。

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: 闲鱼 7.28.30（`com.taobao.idlefish`，versionCode 520）/ SecurityGuard 6.7.260202 独立分析（Redmi K20 Pro，Android 11）
> 分析日期: 2026-09-24
> 归档日期: 2026-09-26
> 分类: 反检测/风控对抗 — 阿里 SecurityGuard EEID 设备风控
</details>
>
> 闲鱼 EEID（Extended Equipment ID）是 SecurityGuard 在客户端采集 Mini 探针（7 字节布尔段 + 11 字节半字节段）、ET 探针（本包实采 55 个）、SGEXT 45 字段、PL 测量、BI/CS 上报后，由 ACS-MUM 服务端签发的设备扩展标识。本文按原文结构归档探针位定义、SG 文件（`.s/` 目录、`.sg` mtime → SGEXT `fields[4]`）、UTDID 持久化、EEID 注册/验证协议与签名参数关系；服务端评分与 EEID 生成算法为原文推测。

## 收录说明

原文列出的项目文件、报告和工具均属于未公开本地材料，不随本文收录。

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
  "utdid": "[REDACTED: sample value]",  // ⭐⭐⭐⭐⭐ 最重要
  "device_id": "[REDACTED: sample value]",                        // 可选
  "ttid": "[REDACTED: sample value]",
  "x_umt": "[REDACTED: sample value]",  // 与 utdid 相同
  "wua": "[REDACTED: sample value]"            // 设备指纹摘要
}
```

**UTDID 详解**：
- **存储位置**：`未公开本地材料`
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
布尔段（7 字节）：[REDACTED: sample value]
半字节段（11 字节）：[REDACTED: sample value]
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

> 来源报告涉及设备完整性、运行环境、传感器与网络状态等防御性检测类别。具体位映射、条件阈值、风险分值及处理逻辑不入 Public。

#### 2.2.3 ET 探针（435 个深度检测）⭐⭐⭐⭐⭐

ET (Environment Telemetry) 探针是**最详细**的环境检测系统，每个探针都有具体的检测目标。

---

##### ET 探针完整列表（实际采集的 55 个核心探针）

**说明**：闲鱼 7.28.30 版本实际采集了 55 个核心 ET 探针，以下是完整的探针列表及其风控作用。

---

###### 【设备身份类】- 10 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 1 | 0299 | [REDACTED: sample value] | 系统类型 | ⭐⭐⭐⭐⭐ 验证是否真实 Android 设备（模拟器可能返回其他值） |
| 3 | 023c | [REDACTED: sample value] | UUID 设备标识符 | ⭐⭐⭐⭐⭐ 设备指纹追踪，跨应用识别 |
| 12 | bd30 | [REDACTED: sample value] | UUID 设备标识符 | ⭐⭐⭐⭐ 另一个设备唯一标识 |
| 16 | 45b7 | [REDACTED: sample value] | UUID 设备标识符 | ⭐⭐⭐⭐ 与 bd30 交叉验证 |
| 21 | d79b | [REDACTED: sample value] | UTDID（阿里设备ID） | ⭐⭐⭐⭐⭐ **最核心**的设备标识，跨阿里系 App |
| 27 | 8f57 | [REDACTED: sample value] | Android ID | ⭐⭐⭐⭐ 系统级设备标识 |
| 34 | e345 | [REDACTED: sample value] | UUID 设备标识符 | ⭐⭐⭐ 额外的设备追踪标识 |
| 41 | 0174 | [REDACTED: sample value] | 设备指纹 Hash | ⭐⭐⭐⭐ 综合设备特征哈希 |
| 48 | 85ba | [REDACTED: sample value] | 设备特征码 | ⭐⭐⭐ 额外的设备指纹 |
| 17 | b7ab | [REDACTED: sample value] | 设备序列号 | ⭐⭐⭐⭐ 硬件序列号（可能是 IMEI） |

**风控重点**：
- UTDID (tag d79b) 是最核心的标识，服务端用它关联所有历史行为
- 多个 UUID 交叉验证，防止单一标识被伪造
- 设备序列号验证硬件真实性

---

###### 【系统版本类】- 9 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 5 | f471 | [REDACTED: sample value] | Android 版本号 | ⭐⭐⭐⭐ 系统版本校验，与 ro.build.version 交叉验证 |
| 6 | 403e | [REDACTED: sample value] | 设备代号 | ⭐⭐⭐⭐⭐ Redmi K20 Pro 内部代号，验证设备型号 |
| 7 | 8fdc | [REDACTED: sample value] | 完整编译指纹 | ⭐⭐⭐⭐⭐ 包含设备、版本、编译信息 |
| 15 | 2b09 | [REDACTED: sample value] | Build Tags | ⭐⭐⭐⭐⭐ **test-keys=高风险**（自编译/开发版） |
| 18 | 3b0a | [REDACTED: sample value] | MIUI 版本号 | ⭐⭐⭐ 验证系统版本真实性 |
| 20 | b8c8 | [REDACTED: sample value] | 编译类型 | ⭐⭐⭐⭐⭐ **release-keys=正常**，test-keys=风险 |
| 22 | fd52 | [REDACTED: sample value] | 完整系统指纹 | ⭐⭐⭐⭐⭐ 系统完整性验证 |
| 29 | 1cdb | [REDACTED: sample value] | OTA 服务器 | ⭐⭐⭐ 验证系统更新来源是否官方 |
| 44 | f31c | [REDACTED: sample value] | SDK 版本 | ⭐⭐⭐⭐ Android 11 = SDK 30 |

**风控重点**：
- **test-keys 检测**（tag 2b09）：自编译系统 = 高风险
- **release-keys 验证**（tag b8c8）：官方正式版 = 正常
- 多维度交叉验证系统版本真实性

---

###### 【硬件信息类】- 8 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 4 | a2c2 | [REDACTED: sample value] | 屏幕分辨率 | ⭐⭐⭐⭐ 验证设备型号（Redmi K20 Pro 特征） |
| 8 | c342 | [REDACTED: sample value] | CPU 核心数 | ⭐⭐⭐⭐ 验证硬件配置（K20 Pro = 8核） |
| 25 | aaca | [REDACTED: sample value] | 设备型号 | ⭐⭐⭐⭐⭐ 官方型号名称 |
| 40 | 2b23 | [REDACTED: sample value] | 设备厂商 | ⭐⭐⭐⭐ 厂商验证 |
| 45 | b07c | [REDACTED: sample value] | 设备代号 | ⭐⭐⭐⭐ 与 tag 403e 交叉验证 |
| 36 | aaa0 | [REDACTED: sample value] | 可用屏幕分辨率 | ⭐⭐⭐ 减去状态栏/导航栏后的分辨率 |
| 37 | efe7 | [REDACTED: sample value] | 设备序列号 | ⭐⭐⭐⭐ 与 tag b7ab 交叉验证 |
| 43 | a5a4 | [REDACTED: sample value] | 内存配置 | ⭐⭐⭐ 物理内存大小（KB） |

**风控重点**：
- 屏幕分辨率 + 设备型号 + CPU 核心数 组合验证
- 检测是否为该型号的真机
- 模拟器通常硬件参数不匹配或缺失

---

###### 【网络硬件类】- 6 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 9 | 0864 | [REDACTED: sample value] | WiFi MAC 地址 | ⭐⭐⭐⭐⭐ 网络硬件唯一标识 |
| 10 | 9ff5 | [REDACTED: sample value] | 蓝牙 MAC 地址 | ⭐⭐⭐⭐ 蓝牙硬件标识 |
| 32 | 0864 | [REDACTED: sample value] | 另一个 MAC 地址 | ⭐⭐⭐⭐ 可能是移动网络 MAC |
| 46 | 0864 | [REDACTED: sample value] | 网络接口 MAC | ⭐⭐⭐ 移动数据网络接口 |
| 49 | 0864 | [REDACTED: sample value] | 虚拟网络接口 MAC | ⭐⭐⭐ 检测 VPN/代理 |
| 50 | 8676 | [REDACTED: sample value] | 网卡 MAC 地址 | ⭐⭐⭐⭐ 物理网络硬件标识 |

**风控重点**：
- 多个 MAC 地址交叉验证
- 检测 MAC 地址是否为随机生成（模拟器特征）
- 检测虚拟网络接口（VPN、代理、抓包工具）

---

###### 【运营商/SIM 卡类】- 4 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 24 | 095a | [REDACTED: sample value] | 运营商名称 | ⭐⭐⭐⭐ SIM 卡信息，验证地理位置 |
| 38 | f02e | [REDACTED: sample value] | 运营商名称（重复） | ⭐⭐⭐ 与 tag 095a 交叉验证 |
| 33 | a506 | [REDACTED: sample value] | 时间戳 | ⭐⭐⭐ SIM 卡相关时间戳 |
| 39 | b616 | [REDACTED: sample value] | SIM 卡状态 | ⭐⭐⭐ -1 可能表示无 SIM 或飞行模式 |

**风控重点**：
- 验证是否有真实 SIM 卡（模拟器通常无 SIM）
- 运营商信息与 IP 地址对比
- 检测虚拟 SIM 卡

---

###### 【应用信息类】- 4 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 11 | 3ed1 | [REDACTED: sample value] | 应用包名 | ⭐⭐⭐⭐⭐ 验证应用身份（防二次打包） |
| 13 | 1c2b | [REDACTED: sample value] | 应用签名 SHA1 | ⭐⭐⭐⭐⭐ 验证应用签名（防篡改） |
| 14 | 6980 | [REDACTED: sample value] | 另一个签名 Hash | ⭐⭐⭐⭐ 交叉验证签名 |
| 26 | db95 | [REDACTED: sample value] | 应用版本号 | ⭐⭐⭐⭐ 验证版本真实性 |

**风控重点**：
- **应用签名校验**（tag 1c2b, 6980）：检测二次打包
- 包名 + 签名 + 版本号 三重验证
- 防止破解版、注入版

---

###### 【时间戳类】- 3 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 2 | d38e | [REDACTED: sample value] | 系统构建时间戳 | ⭐⭐⭐⭐ 验证系统编译时间 |
| 23 | f75f | [REDACTED: sample value] | 当前时间 | ⭐⭐⭐⭐⭐ 时间一致性验证（防时间穿越） |
| 54 | 920a | [REDACTED: sample value] | Unix 时间戳 | ⭐⭐⭐ 系统启动时间或构建时间 |

**风控重点**：
- 检测系统时间是否被篡改
- 验证时间戳合理性（过早或过晚都可疑）
- 防止时间穿越攻击

---

###### 【SecurityGuard 版本】- 2 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 30 | e1dc | [REDACTED: sample value] | SG 版本号 | ⭐⭐⭐⭐⭐ SecurityGuard SDK 版本 |
| 55 | f410 | [REDACTED: sample value] | SG 配置版本 | ⭐⭐⭐ SG 内部配置版本 |

**风控重点**：
- 验证 SecurityGuard 版本与 App 版本匹配
- 检测是否使用了旧版或修改版 SG

---

###### 【传感器数据类】- 3 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 19 | bced | [REDACTED: sample value] | 传感器数据序列 | ⭐⭐⭐⭐⭐ 传感器原始数据（加速度、陀螺仪等） |
| 35 | 9785 | [REDACTED: sample value] | 传感器状态 JSON | ⭐⭐⭐⭐ 传感器可用性和状态 |
| 53 | e7b4 | [REDACTED: sample value] | 内核版本 | ⭐⭐⭐⭐ 系统内核信息 |

**风控重点**：
- 检测设备是否有真实传感器（模拟器通常无传感器）
- 传感器数据合理性验证
- 内核版本与系统版本匹配性

---

###### 【加密/特殊数据类】- 6 个探针

| # | Tag | 值示例 | 含义 | 风控作用 |
|---|-----|-------|------|---------|
| 28 | e0a1 | [REDACTED: sample value] | 加密的系统指纹 | ⭐⭐⭐⭐⭐ Base64 编码的系统特征 |
| 31 | 0eef | [REDACTED: sample value] | 小米设备特征 JSON | ⭐⭐⭐⭐ 小米设备专属特征 |
| 42 | 284e | [REDACTED: sample value] | 分隔的数值数据 | ⭐⭐⭐ 某种编码的特征数据 |
| 47 | ba2e | [REDACTED: sample value] | 数值型标志 | ⭐⭐⭐ 某种状态标志 |
| 51 | 71f3 | [REDACTED: sample value] | 数值型配置 | ⭐⭐⭐ 配置参数 |
| 52 | a506 | [REDACTED: sample value] | 文件系统信息 | ⭐⭐⭐⭐ 存储分区特征 |

**风控重点**：
- 加密数据防止直接读取和篡改
- 特殊厂商数据（小米）增强识别准确性
- 文件系统特征验证设备真实性

---

##### ET 探针风控逻辑总结

> 来源报告将探针用于环境、设备、应用完整性和状态一致性检查。具体评分公式、阈值、覆盖率及效果未公开；本文不将其视为服务端实现。

#### 2.2.4 SGEXT 扩展字段（45 个状态字段）

SGEXT 是 **SecurityGuard Extended** 的缩写，包含 45 个字段：

```python
# SGEXT 字段映射
fields = {
    0: "[REDACTED: sample value]",           # context 序列号（LCG 生成）
    1: "[REDACTED: sample value]",           # mini 序列号（LCG 生成）
    2: "[REDACTED: sample value]",               # flags 类型
    3: "[REDACTED: sample value]",                # 保留
    4: "[REDACTED: sample value]",      # SG 文件修改时间（秒）⭐⭐⭐⭐⭐
    5: "[REDACTED: sample value]",# 特征码
    6: "[REDACTED: sample value]",               # SG 主版本
    7: "[REDACTED: sample value]",               # 子版本
    8: "[REDACTED: sample value]",              # 标志位
    9: "[REDACTED: sample value]",            # 保留
    10: "[REDACTED: sample value]",              # 计数器
    11-17: "[REDACTED: sample value]",           # 功能启用标志
    18: "[REDACTED: sample value]",              # ACTION_DOWN 计数（触摸统计）⭐⭐⭐⭐
    19: "[REDACTED: sample value]",              # 触摸源 CRC 计数 ⭐⭐⭐⭐
    20-24: "[REDACTED: sample value]",           # 事件统计
    25-27: "[REDACTED: sample value]",  # 分支状态 ⭐⭐⭐
    28-34: "[REDACTED: sample value]",           # 各种统计
    35: "[REDACTED: sample value]",              # sgcookie 状态 ⭐⭐⭐⭐
    36: "[REDACTED: sample value]",               # extraBuffer ⭐⭐⭐
    37: "[REDACTED: sample value]",              # UMT 状态 ⭐⭐⭐⭐
    38: "[REDACTED: sample value]",              # 保留
    39: "[REDACTED: sample value]",              # 固定值
    40-43: "[REDACTED: sample value]",           # 其他状态
    44: "[REDACTED: sample value]",    # 遥测段（复杂编码）⭐⭐⭐⭐⭐
}
```

**重点字段详解**：

**重点字段详解**：

1. **fields[4] - SG 文件修改时间**
   - 来源：未公开本地材料
   - 风控作用：用于文件状态和时间连续性检查；具体判定值不公开。

2. **fields[18-19] - 触摸统计**
   - 用于记录触摸事件相关状态；具体样值与阈值不公开。

3. **fields[35] - sgcookie 状态**
   - 用于本地与内存状态一致性检查；具体编码值不公开。

4. **fields[37] - UMT 状态**
   - 用于组件状态检查；具体编码值不公开。

5. **fields[44] - 遥测段**
   - 遥测字段及载荷样值：未公开本地材料。

#### 2.2.5 PL 性能与日志（158 个参数）

PL (Performance & Logging) 测量系统性能和日志：

```python
PL_PARAMS = {
    # 时间测量（毫秒）
    "t1": "[REDACTED: sample value]",      # Mini 采集耗时
    "t2": "[REDACTED: sample value]",     # ET 采集耗时
    "t3": "[REDACTED: sample value]",      # 签名计算耗时
    "t4": "[REDACTED: sample value]",       # SGEXT 生成耗时

    # 内存测量（KB）
    "m1": "[REDACTED: sample value]",    # Java 堆内存
    "m2": "[REDACTED: sample value]",     # Native 内存
    "m3": "[REDACTED: sample value]",     # 缓存大小

    # 计数器
    "c1": "[REDACTED: sample value]",     # API 调用次数
    "c2": "[REDACTED: sample value]",      # 异常次数
    "c3": "[REDACTED: sample value]",       # 重试次数

    # 状态码
    "s1": "[REDACTED: sample value]",     # HTTP 状态
    "s2": "[REDACTED: sample value]",       # 错误码

    # 校验和
    "ck": "[REDACTED: sample value]",  # CRC64-ECMA 校验 ⭐⭐⭐⭐⭐
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
    "utdid": "[REDACTED: sample value]",
    "sid": "[REDACTED: sample value]",
    "pageName": "[REDACTED: sample value]",
    "action": "[REDACTED: sample value]",
    "timestamp": "[REDACTED: sample value]",
    "duration": "[REDACTED: sample value]",        // 页面停留时长（毫秒）
    "touchCount": "[REDACTED: sample value]",        // 触摸次数
    "scrollDistance": "[REDACTED: sample value]",  // 滚动距离（像素）
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
    "dexHash": "[REDACTED: sample value]",     // DEX 文件哈希
    "soHash": "[REDACTED: sample value]",      // SO 库哈希
    "signatureHash": "[REDACTED: sample value]", // 应用签名哈希
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
   输出：[REDACTED: sample value]
   ↓
持久化存储
   路径：未公开本地材料
   节点：<string name="UTDID2">[REDACTED: sample value]</string>
```

#### 3.1.2 SG 文件系统创建

**目录结构初始化**：
```
未公开本地材料
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
    f"2={appkey}",                   # [REDACTED: sample value]
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
# 1. 密钥素材：未公开本地材料
secret = "[REDACTED: credential material]"

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
  "req_biz_code": "[REDACTED: sample value]",
  "context": "[REDACTED: sample telemetry]",
  "mini": "[REDACTED: sample telemetry]",
  "sgext": "[REDACTED: sample telemetry]",
  "et": "[REDACTED: sample telemetry]",
  "pl": "[REDACTED: sample telemetry]"
}
```

#### 3.2.4 服务端验证流程

> 来源报告将服务端验证概括为签名、探针与状态一致性、完整性及风险决策等类别。具体处理次序、阈值、评分权重和 EEID 生成细节属于未公开的服务端模型；原文明确标注相关内容为推测，不作为已验证事实。

#### 3.2.5 响应协议

**成功响应** (HTTP 200)：
```json
{
  "ret": ["SUCCESS::调用成功"],
  "data": {
    "eeid": "[REDACTED: sample value]",
    "device_score": "[REDACTED: sample value]",
    "risk_level": "LOW",
    "expire_time": "[REDACTED: sample value]",
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
    "block_duration": "[REDACTED: sample value]"
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
        ├─ value: "[REDACTED: sample value]"
       └─ expire: 1727276885
        └─ expire: [REDACTED: sample value]

### 3.3 EEID 验证协议

#### 3.3.1 后续请求携带 EEID

**协议变化**：
```diff
  Headers:
    x-sign: {重新计算的签名}
    +   x-eeid: [REDACTED: sample value]
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

> 来源报告概括了标识绑定、探针变化、状态连续性与行为模式等检查类别。具体字段、规则、评分及模型细节未公开，且未由本次 runtime 证据验证。

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
- appkey_secret：受保护存储，具体方式不公开。

#### 3.5.2 探针防重放

**时间窗口验证**：
```python
if request_timestamp falls outside the server-defined freshness window:
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
- 客户端采集时延：来源报告提及采集耗时；具体值未公开。
- 服务端处理时延：来源报告提及处理耗时；具体值未公开。
- 总 RTT（含网络传输）：来源报告提及端到端耗时；具体值未公开。

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
未公开本地材料
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
├─ Flags: [REDACTED: sample value] (105)
├─ Timestamp: [REDACTED: sample value]
└─ CRC32: 0x12345678

[Body: Variable length]
├─ UTDID: [REDACTED: sample value]
├─ Device Profile
│   ├─ Manufacturer: Xiaomi
│   ├─ Model: Redmi K20 Pro
│   ├─ Android Version: 11
│   └─ SDK Version: 30
│
├─ Mini Snapshot
│   ├─ 布尔段: [REDACTED: sample value] (hex)
│   └─ 半字节段: [REDACTED: sample value] (hex)
│
├─ ET Snapshot (压缩存储)
│   └─ 435 个探针的最近一次值
│
└─ [Footer: 16 bytes]
    └─ Signature: HMAC-SHA1
```

**修改时间的重要性** ⭐⭐⭐⭐⭐：
- **fields[4] = [REDACTED: sample value]**（SG 文件的 mtime）
- **风控作用**：
  - 验证文件是否被篡改
  - 检测时间穿越（mtime 在未来）
  - 关联设备历史（mtime 过早=可疑）
  - 检测文件重放（mtime 与 UTDID 不匹配）

**如何验证 SG 文件**：
```bash
# 查看 SG 文件修改时间
adb shell "su -c ls -l 未公开本地材料"
# 样本输出：未公开本地材料

# 修改时间戳转换
date -d @[REDACTED: sample value]
# 转换结果：未公开本地材料
```

#### 4.2.2 .s 状态文件 ⭐⭐⭐⭐

**内容**：
```json
{
  "byte49_initial": "[REDACTED: sample value]",      // 初始状态字节
  "byte50_initial": "[REDACTED: sample value]",      // 初始状态字节
  "byte30_initial": "[REDACTED: sample value]",      // Mini 初始状态
  "sgcookie_status": "[REDACTED: sample value]",       // sgcookie 状态（一致）
  "umt_status": "[REDACTED: sample value]",            // UMT 状态（已安装）
  "last_update": "[REDACTED: sample value]",  // 最后更新时间
  "request_count": "[REDACTED: sample value]",      // 请求计数
  "error_count": "[REDACTED: sample value]"            // 错误计数
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
    "x-utdid": "[REDACTED: sample value]",            # ⭐⭐⭐⭐⭐
    "x-umt": "[REDACTED: sample value]",              # ⭐⭐⭐⭐
    "x-ttid": "[REDACTED: sample value]",

    # 设备信息
    "x-devid": "Axxxxxxxxxxxxx==",                    # ⭐⭐⭐⭐
    "x-features": "27",

    # App 信息
    "x-appkey": "[REDACTED: sample value]",        # App 标识
    "x-app-ver": "7.28.30",

    # 其他
    "x-t": "[REDACTED: sample value]",          # 时间戳
    "x-sid": "session_id",        # 会话 ID
    "x-uid": "user_id",           # 用户 ID（登录后）
    "x-location": "[REDACTED: sample value]",          # 位置
    "x-bx-version": "6.7.260202", # SecurityGuard 版本
}
```

### 5.2 INPUT 参数组成（22 个字段）

**INPUT** 是签名的输入，包含 22 个字段按特定顺序拼接：

```python
INPUT_FIELDS = [
    "UTDID",          # 0. [REDACTED: sample value]
    "ttid",           # 1. [REDACTED: sample value]
    "appkey",         # 2. [REDACTED: sample value]
    "timestamp",      # 3. [REDACTED: sample value]
    "api",            # 4. API method
    "version",        # 5. API version
    "data",           # 6. [REDACTED: sample value]
    "sid",            # 7. Session ID (optional)
    "uid",            # 8. User ID (optional)
    "deviceId",       # 9. Device ID (optional)
    "lat",            # 10. [REDACTED: sample value]
    "lng",            # 11. [REDACTED: sample value]
    "features",       # 12. [REDACTED: sample value]
    "bx-version",     # 13. SecurityGuard version
    "mini_base64",    # 14. Mini encoded probe data
    "sgext_base64",   # 15. SGEXT encoded data
    "context",        # 16. Context data
    "extdata",        # 17. [REDACTED: sample value]
    "x-umt",          # 18. [REDACTED: sample value]
    "pv",             # 19. Protocol version
    "utdid2",         # 20. [REDACTED: sample value]
    "req-counter",    # 21. Request counter
]

# INPUT 拼接示例（样值已脱敏）
INPUT = "&".join([
    "UTDID=[REDACTED: sample value]",
    "ttid=[REDACTED: sample value]",
    "appkey=[REDACTED: sample value]",
    "timestamp=[REDACTED: sample value]",
    "data=[REDACTED: sample value]",
    "mini_base64=[REDACTED: sample value]",
    "sgext_base64=[REDACTED: sample value]",
])
```
```

### 5.3 签名计算流程

```python
def calculate_signature(input_str: str, appkey: str) -> str:
    """
    计算 x-sign 签名
    """
# 1. 密钥素材：未公开本地材料
    secret = "[REDACTED: credential material]"

    # 2. 使用 HMAC-SHA1 计算签名
    signature = hmac.new(
        key=secret.encode('utf-8'),
        msg=input_str.encode('utf-8'),
        digestmod=hashlib.sha1
    ).hexdigest()

    # 3. 返回签名（40 个十六进制字符）
    return "[REDACTED: sample value]"
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

#### 6.1.1 设备标识一致性
> 防御性检测类别：标识格式、绑定关系与历史一致性。具体字段和判定值不公开。

#### 6.1.2 探针与运行时完整性
> 防御性检测类别：探针交叉一致性、运行时完整性及环境状态。具体检测步骤、位映射和阈值不公开。

#### 6.1.3 本地状态连续性
> 防御性检测类别：本地状态完整性与跨请求连续性。具体文件值、篡改步骤和判定阈值不公开。

#### 6.1.4 签名与代码完整性
> 防御性检测类别：请求完整性、应用代码完整性与运行环境校验。密钥获取和签名伪造细节不公开。

#### 6.1.5 行为一致性
> 防御性检测类别：行为序列、操作节奏与触摸统计。具体样值、策略和规避方式不公开。

#### 6.1.6 虚拟环境识别
> 防御性检测类别：设备能力、系统环境及多信号一致性。具体检测值和规避步骤不公开。

### 6.2 风控强度评估

| 层级 | 来源提及的检测类别 | 证据边界 |
|------|--------------------|----------|
| L1 | 签名完整性 | 规则与效果未验证 |
| L2 | 设备标识 | 规则与效果未验证 |
| L3 | 快速环境检测 | 规则与效果未验证 |
| L4 | 深度环境检测 | 规则与效果未验证 |
| L5 | 本地状态连续性 | 规则与效果未验证 |
| L6 | 行为分析 | 规则与效果未验证 |
| L7 | 代码完整性 | 规则与效果未验证 |
| L8 | 设备信誉 | 服务端模型未公开 |

**总体评估**：原文的强度判断没有附可复核测量依据，不作为实际部署结论。

### 6.3 理论上的完全绕过方案（仅供研究）

> 本节具体绕过步骤、设备配置、签名材料与同步方法不入 Public。可复用内容仅限前述防御性检测类别；该来源没有提供足以验证绕过效果的当前 runtime 证据。

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

1. 未公开本地材料
2. 未公开本地材料
3. 未公开本地材料
4. 未公开本地材料
5. 未公开本地材料
6. 未公开本地材料

### 8.2 技术文档

- SecurityGuard SDK 官方文档
- MTOP 协议规范
- HMAC-SHA1 算法标准
- CRC64-ECMA 算法规范
- TEA/XTEA 加密算法

### 8.3 工具

- 未公开本地材料
- 未公开本地材料
- 未公开本地材料

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
