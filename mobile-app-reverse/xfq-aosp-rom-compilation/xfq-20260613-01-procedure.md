---
schema_version: 2
id: aosp-captive-portal-domestic-url-procedure
document_type: procedure
original_date: '2026-06-13'
archived_date: '2026-10-02'
scope:
  targets: [aosp-captive-portal-domestic-url]
  client: android
  version: master-0.0.2
  observed_at: '2026-06-13'
sources:
  - id: s1
    ref: "./xfq-20260613-01.md#方案尝试过程"
    basis: source-report
  - id: s2
    ref: "./xfq-20260613-01.md#最终采用方案③-直接修改源码"
    basis: source-report
  - id: s3
    ref: "./xfq-20260613-01.md#验证方法"
    basis: source-report
  - id: s4
    ref: "./xfq-20260613-01.md#已解决的问题"
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [s1, s2]
    basis: source-report
    limits: 只整理来源对 overlay、运行时 settings 和改源码三条路的取舍。作者写的刷机完成不在本流程里升级依据。
  - name: parameters
    anchor: parameters
    sources: [s2]
    basis: source-report
    limits: URL 和优先级是来源写下的字符串。fallback 仍是国际地址。没有测这些 URL 当前是否返回 204。
  - name: validation
    anchor: acceptance
    sources: [s3, s4]
    basis: source-report
    limits: dumpsys 与 logcat 只是来源给出的查看命令。国内网络已验证是作者自述，本卡没有新的命令输出。
relations:
  - type: derived_from
    target: "./xfq-20260613-01.md#最终采用方案③-直接修改源码"
tags: [aosp, networkstack, captive-portal, source-report]
---

# AOSP Captive Portal 默认探测改到国内可达地址

这份流程只回答：在来源描述的不插 SIM 的 Pixel 7 研究机上，怎样让 NetworkStack 的默认门户探测不再指向当时不可达的 Google 地址。它不覆盖系统 CA、WebView 或开发者选项。来源是 [Wi-Fi 网络验证优化](./xfq-20260613-01.md#最终采用方案③-直接修改源码)。

作者把状态写成 `状态：✅ 已完成，已刷机验证`。那是来源自述。本卡没有刷机，也没有 `dumpsys` 输出。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 来源要求 | 不足时 |
|---|---|---|
| 基线 | `基于：`master (0.0.2)``，分支 `fix/wifi-network-optimization` | 不是这条基线时，不要把文件行号当成仍适用 |
| 机型约束 | Pixel 7 研究机不插 SIM | 有中国 SIM 时，MCC 460 资源是否已经生效不在本流程的验收里 |
| 症状 | 能上网仍长期 Checking / Limited connection，或已保存网络被标成 disabled | 症状不同就停止，不改探测 URL |
| 不做的事 | 不把 `settings put global` 当成出厂默认；不只刷 product | 见 F1、F2 |

<a id="parameters"></a>
## 参数口径

来源写默认探测是：

`default_captive_portal_http_url  → http://connectivitycheck.gstatic.com/generate_204`

`default_captive_portal_https_url → https://www.google.com/generate_204`

并写 `这些地址在国内不可达。` 失败后 NetworkMonitor 把网络标成 `PARTIAL` / `CAPTIVE_PORTAL`。

MCC 460 备用文件是 `packages/modules/NetworkStack/res/values-mcc460/config.xml`，指向 `connectivitycheck.gstatic.cn`。来源写它 `仅在插入中国 SIM 卡时自动加载`，并写 `Pixel 7 研究机不插 SIM 卡，所以此配置从未生效。`

采用后的默认字符串，config.xml 与硬编码常量都改成：

`http://connectivitycheck.gstatic.cn/generate_204`

https 对应 `https://connectivitycheck.gstatic.cn/generate_204`。两处文件是：

- `packages/modules/NetworkStack/res/values/config.xml`
- `packages/modules/NetworkStack/src/android/net/util/NetworkStackUtils.java`

来源写下的探测优先级是：

1. `优先级 1: Settings.Global (ADB 运行时修改)        → 无（已清除）`
2. `优先级 2: config_captive_portal_* (RRO overlay)   → 无（空值）`
3. `优先级 3: default_captive_portal_* (config.xml)    → http://connectivitycheck.gstatic.cn/generate_204`
4. `优先级 4: DEFAULT_CAPTIVE_PORTAL_* (硬编码)        → http://connectivitycheck.gstatic.cn/generate_204`

主探测失败后的 fallback 仍是国际地址，其中一条是：

`http://play.googleapis.com/generate_204              ← 国际备选`

另外两条是 `connectivitycheck.gstatic.com` 和 `www.google.com/gen_204`。来源没有把 fallback 改成国内地址。`settings put global` 的具体键名没有写出。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 确认基线、无 SIM，以及误报或 disabled SSID 症状在材料里 | 前提表 | 缺基线或症状不符走 F4 |
| S2 | 丢掉 product overlay 和“只靠 settings”这两条作为出厂方案 | 尝试表的三行结论 | overlay 仍被当成生效点走 F1 |
| S3 | 同时改 config.xml 默认 URL 和 NetworkStackUtils 硬编码常量 | 两处都变成 gstatic.cn | 只改一处走 F1，因为优先级 3 和 4 会不一致 |
| S4 | 按来源的四段优先级核对：运行时 settings 与 RRO 为空，默认落在第 3、4 段 | 优先级清单 | 任一高优先级仍指向国际地址则不要刷机 |
| S5 | 同时编 system 与 product 镜像 | 来源命令见下方 | 只编 product 走 F2 |
| S6 | system 与 product 都刷 | fastboot 两条 flash | 只刷 product 走 F2 |
| S7 | 用 dumpsys 与 NetworkMonitor 日志看验证状态 | 命令见验收 | 仍是历史 disabled SSID 走 F3 |

来源的编译行是：

`m NetworkStack ROMManager privapp-permissions-com.xiaofeng.rommanager.xml systemimage productimage -j16`

并写需要同时编译 systemimage（NetworkStack 在 system 分区）和 productimage。刷写是 `fastboot flash system system.img` 与 `fastboot flash product product.img`。

<a id="outputs"></a>
## 输出

交付的是两份源文件里的默认 URL、四段优先级，以及仍为国际地址的 fallback 列表。来源还列出同步到 changes repo 的路径：

`sources/packages/modules/NetworkStack/res/values/config.xml`

`sources/packages/modules/NetworkStack/src/android/net/util/NetworkStackUtils.java`

提交说明里，保留的是 `885b458 fix: change captive portal default URLs to domestic-reachable endpoints`。overlay 那条提交被写成已废弃。

<a id="acceptance"></a>
## 验收

来源给出的查看命令是：

`adb shell dumpsys connectivity | grep -E "VALIDATED|CAPTIVE|PARTIAL"`

以及 `adb logcat -b main -s NetworkMonitor`。

| 观察 | 来源口径 | 不算通过 |
|---|---|---|
| 门户误报 | 作者表写国内网络已验证 | 没有这份命令的输出就不能复述该句 |
| 开机自动连 | 作者写随 captive portal 修复而解决 | 不单独证明 Wi-Fi 框架其他失败原因 |
| disabled 历史网络 | 需手动在 UI 重新连接一次 | 未做这一下仍不连接，不能算本改动失败或成功 |

作者的完成句 `状态：✅ 已完成，已刷机验证` 只说明来源自称做过，不是本卡的验收记录。

<a id="failure-exits"></a>
## 失败出口

F1：product overlay 无效。来源写 `product overlay 的 RRO 未被加载`，因为 NetworkStack 是 mainline 模块。`settings put global` 被写成 `重启后仍有效，但不是默认行为`。两条都不能代替 S3。MCC 460 资源在无 SIM 时从未生效，不能当成已经改过的默认值。

F2：只刷 product 不够。原文是 `只刷 `product.img` 不够，因为 NetworkStack 在 system 分区。` 只编 productimage 同样停。

F3：已被标成 disabled 的旧网络。来源写 `需手动在 UI 重新连接一次`。没有给出清除 disabled SSID 的命令；没有这一下就停止，不要再改 URL。

F4：材料不是 `master (0.0.2)`、机型仍插着会加载 MCC 460 的 SIM，或症状不是门户误报。停止。fallback 仍指向国际地址，主探测失败后的行为来源没有再验证。
