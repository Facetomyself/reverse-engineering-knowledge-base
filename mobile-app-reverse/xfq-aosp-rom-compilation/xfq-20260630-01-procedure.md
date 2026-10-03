---
schema_version: 2
id: aosp-panther-gms-preload-procedure
document_type: procedure
original_date: '2026-06-30'
archived_date: '2026-10-02'
scope:
  targets: [aosp-panther-gms-preload]
  client: Android
  version: aosp_panther-user; source pins factory image directory panther_tq3a_230901_001
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260630-01.md#20260630-gms-preload-suite"
    basis: source-report
modules:
  - name: parameters
    anchor: prerequisites
    sources: [s1]
    basis: source-report
    limits: 分区、排除项和 makefile 条件只按来源摘录。不收录设备序列号，也不把原厂包路径里的家目录写进本卡。
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 步骤来自来源 2026-07-02 补上的复现顺序。本轮没有提取镜像或编译。
  - name: validation
    anchor: acceptance
    sources: [s1]
    basis: source-report
    limits: 包路径和特权标志是来源写下的实机结果。本轮没有设备输出。不覆盖登录或 Play Integrity。
relations:
  - type: derived_from
    target: "./xfq-20260630-01.md#20260630-gms-preload-suite"
tags: [aosp, panther, gms, source-report]
---

# panther 原厂 GMS 预置：提取、user 构建与路径验收

这份流程只回答来源自己划定的问题：怎样把 Pixel 7 原厂 GMS 以“本机可复现、仓库不带专有 payload”的方式放进当前 AOSP。它不保证账号登录、SafetyNet 或 Play Integrity，也不包含 Pixel Launcher。来源是 [20260630 GMS preload suite](./xfq-20260630-01.md#20260630-gms-preload-suite)。

<a id="prerequisites"></a>
## 前提与输入

缺工厂镜像、产品 makefile 条件或 user 变体时停在 F1。

- 专有 APK 只留在本机 AOSP 构建树的 `vendor/xf_gms/panther/{product,system_ext}`。GitHub 只保存提取脚本、构建规则、文件清单和校验信息。
- 来源采用的方案是从原厂 image 提取，并用 `inherit-product-if-exists`，payload 不存在就不启用。直接提交 APK、手工拷进 out、或写死 `PRODUCT_COPY_FILES` 都不采用。
- 分支名是 `feature/gms-preload-suite`。原厂包目录名包含 `panther_tq3a_230901_001`。本卡不写家目录，也不写压缩包文件名里的短校验片段。
- 提取必须去掉 `oat/odex/vdex/art/dm`。必须排除 `system_ext/etc/permissions/com.google.android.iwlan.xml`，否则和 AOSP 已有目标重复。
- `device/google/pantah/aosp_panther.mk` 里要有 `inherit-product-if-exists` 指向 `vendor/xf_gms/panther/gms.mk`。
- 三个核心包的目标路径：`PrebuiltGmsCoreSc.apk` 到 `/product/priv-app/PrebuiltGmsCore/`，`Phonesky.apk` 到 `/product/priv-app/Phonesky/`，`GoogleServicesFramework.apk` 到 `/system_ext/priv-app/GoogleServicesFramework/`。
- 构建变体必须是 `user`，不能是 `userdebug`。
- Pixel Launcher、壁纸和主题不属于这张卡。来源明确写不要混进 GMS 基础套件结论。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | payload 不进补丁仓库 | 不进入 GitHub 补丁仓库 | s1 :39 | source-report | 只约束来源这套树 |
| C2 | 预优化文件不复用 | oat/odex/vdex/art/dm | s1 :62 | source-report | 未做 ABI 对照实验 |
| C3 | 缺失 payload 不让公开树失败 | inherit-product-if-exists | s1 :72 | source-report | 本轮未跑 make |
| C4 | 不承诺完整性认证 | 不保证账号登录、SafetyNet/Play Integrity | s1 :84 | source-report | 边界不是失败 |
| C5 | Launcher 不在本卡 | 不应该混进 GMS 基础套件结论里 | s1 :86 | source-report | 见另一篇 |

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 对工厂包跑 `vendor/xf_gms/panther/extract_panther_gms.sh --factory-zip` | product 与 system_ext 下三个核心 APK；这两棵目录不提交 | 三个 APK 缺任何一个走 F1；否则走 S2 |
| S2 | 检查 `aosp_panther.mk` 的 `inherit-product-if-exists`，以及 Android.mk / gms.mk 里的三个模块名 | makefile 条件成立 | 没有条件包含走 F2 |
| S3 | `lunch aosp_panther-user`。确认 `TARGET_BUILD_VARIANT` 是 user，`PRODUCT_PACKAGES` 打印 PrebuiltGmsCore、Phonesky、GoogleServicesFramework | user 产品变量 | 变体是 userdebug 走 F2；重复目标走 F3 |
| S4 | full `fastboot flashall`，不 wipe。先确认 product 是 panther | `sys.boot_completed` 为 1 | 不是 panther 走 F1；开机后走 S5 |
| S5 | 用 pm path 和 dumpsys 的 pkgFlags / privateFlags / codePath 核对三个包 | 路径和特权标志 | 路径不对走 F3；Play Store 打不开走 F5 |
| S6 | 查 logcat 里有没有 fatal privapp allowlist 拒绝 | 无该类拒绝，或定位到缺的 permission | 有拒绝走 F4；只有旧 userdata 噪声则记录，不默认 wipe |

来源的编译示例是 `NINJA_ARGS="-l8" m -j8`。刷机命令里的设备序列号不进入本卡，只保留 full flashall 且不 wipe。

<a id="outputs"></a>
## 输出

- 本机 payload。来源计数 `proprietary-files.txt` 为 47 个文件，并写 product 约 238M、system_ext 约 8.0M。这些大小是来源报告，不是本轮测量。
- 三个安装路径：`com.google.android.gms` 指向 `/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCoreSc.apk`；`com.android.vending` 指向 Phonesky；`com.google.android.gsf` 指向 system_ext 里的 GoogleServicesFramework。
- 特权标志：gms 与 vending 为 `PRIVILEGED PRODUCT`，gsf 为 `PRIVILEGED SYSTEM_EXT`。
- Play Store 前台活动名 `com.android.vending/.AssetBrowserActivity`。这只说明来源当时能打开界面。

<a id="acceptance"></a>
## 验收

通过必须同时看到包存在、路径落在上表、特权标志匹配，以及没有 fatal privapp allowlist 拒绝。只看到编译成功不够。

- `pm list packages` 含 `com.google.android.gsf`、`com.android.vending`、`com.google.android.gms`。
- `pm path` 与来源列出的三条 priv-app 路径一致。
- `sys.boot_completed` 为 `1`，`fastboot getvar product` 为 panther。
- 不 wipe 时允许出现 `was user id 0 but is now` 这类包状态噪声。设备仍能开机且 GMS / Play Store 能启动时，不把噪声当成镜像失败。
- 本功能不把账号登录或认证设备状态算进通过。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C6 | gms 路径 | /product/priv-app/PrebuiltGmsCore/PrebuiltGmsCoreSc.apk | s1 :139 | source-report | 来源实机记录 |
| C7 | gsf 在 system_ext | /system_ext/priv-app/GoogleServicesFramework/GoogleServicesFramework.apk | s1 :141 | source-report | 来源实机记录 |
| C8 | gms 特权标志 | PRIVILEGED PRODUCT | s1 :149 | source-report | 同一段还有另外两包 |
| C9 | 未见 fatal allowlist 拒绝 | 未看到 GMS 相关的 fatal privapp allowlist 拒绝 | s1 :155 | source-report | 本轮未读 logcat |

<a id="failure-exits"></a>
## 失败出口

F1：工厂包不可读，或提取后三个核心 APK 不齐。停止编译结论。补的是同版本 factory image，不是把 APK 提交进 Git。

F2：`aosp_panther.mk` 没有 `inherit-product-if-exists`，或 `TARGET_BUILD_VARIANT` 不是 user。不要改去 userdebug 再把结果当成这张卡的通过。

F3：编译报重复目标。先看 `com.google.android.iwlan.xml` 是否被提取进来。来源刻意排除了它。排除后重跑 S1，不要另外复制一份权限文件硬凑。

F4：开机出现 fatal privapp allowlist。用来源给出的 logcat 过滤定位缺哪条 permission，再补 allowlist。过滤词包括 Privileged permission、privapp 和三个模块名。补完之前不把“扫到包名”写成特权安装成功。

F5：Play Store 打不开。先区分是不是不 wipe 留下的旧 `packages.xml`。来源允许只 `pm clear` `com.android.vending` 和 `com.google.android.gms`。不要默认 wipe 全机；干净首刷必须先得到明确同意。
