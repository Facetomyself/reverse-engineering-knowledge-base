---
schema_version: 2
id: mobile-app-reverse-environment-setup-procedure
document_type: procedure
scope:
  targets: [Android reverse-engineering environment setup]
  client: Android app reverse engineering
  version: unknown
  observed_at: unknown
sources:
  - id: environment-choice
    ref: ./app-reverse-environment-setup.md#environment-device-choice
    basis: source-report
  - id: certificate-proxy
    ref: ./app-reverse-environment-setup.md#certificate-proxy-validation
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [environment-choice, certificate-proxy]
    basis: source-report
    limits: 这是从来源教程整理的环境准备顺序，不表示当前设备、目标 App 或特定工具版本已通过。
  - name: validation
    anchor: acceptance
    sources: [certificate-proxy]
    basis: source-report
    limits: 浏览器 HTTPS 可读只覆盖基础代理/证书线索，不替代目标 App 的 pinning、mTLS、Frida 或业务 readback 验收。
relations:
  - type: derived_from
    target: ./app-reverse-environment-setup.md#environment-device-choice
tags: [android, app-reverse, emulator, root, certificate, proxy, frida]
---

# Android App 逆向环境准备流程

本文把 [App 逆向环境搭建](./app-reverse-environment-setup.md) 中的设备选择、Root/证书、代理和工具安装整理成可复用的准备流程。它只表达来源教程的方法边界；没有目标 App、当前设备、抓包或服务端验收证据时，流程只能停在相应的未知或失败出口。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 最低内容 | 不足时 |
|---|---|---|
| 目标范围 | App 包名、版本、要观察的操作和允许的分析边界；未知项明确写 `unknown` | F1；不以工具安装完成代替目标定义 |
| 设备 | 可回滚的模拟器或备用真机；真机需确认 Bootloader、ROM、ABI 和数据备份 | F1；不在唯一日常设备上直接解锁或刷写 |
| 连接材料 | ADB、电脑网络、代理监听地址/端口和设备代理能力 | F2；缺连接基线不进入目标抓包 |
| 信任方案 | 用户/系统证书路径或目标 App 的其他 TLS 观察方案；明确是否可能有 pinning/mTLS | F2；证书安装不等于目标 App 信任 |
| 工具链 | jadx/APKTool、Frida/Objection、抓包工具及版本记录 | F1；版本未知保留为限制 |

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 按检测敏感度选择模拟器或真机，建立可回滚备份并记录 Android/ABI/Root 状态。 | 设备选择理由、版本和备份记录。 | 设备可恢复且范围明确走 S2；否则 F1。 |
| S2 | 配置 Root 路线：模拟器记录 Root/Magisk/LSPosed；真机记录 OEM 解锁、fastboot、boot 镜像和 Magisk 变更。 | 变更清单、命令、重启结果和数据风险记录。 | Bootloader/分区/版本不确定走 F1；否则 S3。 |
| S3 | 安装证书方案并配置设备代理与 Charles/mitmproxy 的 TLS 观察面，分别记录证书和 SSL Proxying 状态。 | 证书位置、代理配置、监听端口和时间线。 | 任一配置缺失走 F2；否则 S4。 |
| S4 | 安装 jadx/APKTool、Frida/Objection、adb 等工具，固定版本并确认设备连接。 | 工具版本表、ADB 连接和 Frida 连接记录。 | 版本不匹配或连接失败走 F3；否则 S5。 |
| S5 | 用设备浏览器访问 HTTPS 基线，检查代理中是否出现可读内容；不要把浏览器读回当作目标 App 成功。 | 基础抓包截图/日志、证书错误或仅 CONNECT 的分类。 | 可读走 S6；乱码、证书错误或无流量回 F2。 |
| S6 | 对目标 App 单独检查 pinning、mTLS、模拟器/Root 检测和 Frida attach；一次只改变一个因素并保存失败证据。 | 目标 App 观察记录、失败原因和后续补采项。 | 当前问题有证据闭合才结束；否则 F2/F3/F4。 |

<a id="outputs"></a>
## 输出

1. 设备选择、版本、ABI、Root/Bootloader 状态和回滚记录。
2. 证书、代理、SSL Proxying 和基础 HTTPS 读回记录。
3. jadx/APKTool、Frida/Objection、adb 与抓包工具的版本清单。
4. 目标 App 的 pinning、mTLS、环境检测和 Frida 连接结果；未知项必须显式保留。
5. 失败出口及下一步补采条件，不用“工具已安装”替代技术验收。

<a id="acceptance"></a>
## 验收

| 门 | 通过条件 | 不能代替它的东西 |
|---|---|---|
| A1 设备可回滚 | 目标设备、数据风险和 Root/Bootloader 变更均有记录，测试后可恢复 | 设备能启动、Root 开关存在 |
| A2 基础代理链 | 设备代理、证书和 SSL Proxying 均已配置，浏览器 HTTPS 内容可读 | 只看到 CONNECT、证书文件存在 |
| A3 工具可连接 | 工具版本已记录，ADB/Frida 连接结果可定位 | 命令安装成功、端口开放 |
| A4 目标 App 边界 | pinning/mTLS、环境检测和目标 App 流量分别有观测或明确 unknown | 浏览器读回、HTTP 200 或静态工具界面 |

本轮产物只整理来源方法，A1–A4 没有新增当前设备证据；不能报告 runtime、parity 或 server acceptance。

<a id="failure-exits"></a>
## 失败出口

- **F1：设备前提不成立。** 停止刷写或解锁，先补目标范围、备份、ROM/ABI 和回滚路径；不在唯一设备上继续尝试。
- **F2：证书或代理链不闭合。** 分开检查设备代理、监听端口、证书信任和 SSL Proxying；仅 CONNECT、乱码或无 HTTPS 流量时不进入目标 App 结论。
- **F3：工具连接不闭合。** 核对 `frida-server` 与 `frida-tools` 版本、ADB 状态和设备架构；失败证据保留，不把静态猜测写成动态结果。
- **F4：目标 App 有额外保护。** 将 pinning、mTLS、模拟器/Root 检测和业务 readback 分开记录；没有新的可检验假设就停止，不以换设备或换出口盲试代替证据。

来源：[App 逆向环境搭建](./app-reverse-environment-setup.md)。本文所有模块均为 `source-report`，未复测来源工具兼容性，也未产生目标 App 的运行时或服务端验收结果。
