---
schema_version: 2
id: aosp-panther-developer-defaults-procedure
document_type: procedure
original_date: '2026-06-14'
archived_date: '2026-10-02'
scope:
  targets: [aosp-panther-developer-defaults, pixel-screen-brightness]
  client: android
  version: android13-r78-aosp-panther-userdebug
  observed_at: '2026-06-14'
sources:
  - id: s1
    ref: "./xfq-20260614-01.md#需求"
    basis: source-report
  - id: s2
    ref: "./xfq-20260614-01.md#1-panther-产品配置"
    basis: source-report
  - id: s3
    ref: "./xfq-20260614-01.md#2-settingsprovider-默认值"
    basis: source-report
  - id: s4
    ref: "./xfq-20260614-01.md#3-亮度同步保护"
    basis: source-report
  - id: s5
    ref: "./xfq-20260614-01.md#刷机与验证"
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [s2, s4, s5]
    basis: source-report
    limits: 生效点按来源写成 SettingsProvider 的 int 默认值加 BrightnessSynchronizer。overlay 的 float 尝试值不是生效点。未刷机。
  - name: parameters
    anchor: parameters
    sources: [s2, s3, s4]
    basis: source-report
    limits: 默认键和三个数值空间是来源写下的对照。stay_on 的 true 与快照 15 没有换算说明。不记录设备序列号。
  - name: validation
    anchor: acceptance
    sources: [s5]
    basis: source-report
    limits: 开机快照是作者列出的键值。build completed 与 boot_completed 不升级为依据。screen_brightness_float 在快照里是 null。
relations:
  - type: derived_from
    target: "./xfq-20260614-01.md#3-亮度同步保护"
tags: [aosp, panther, settingsprovider, brightness, source-report]
---

# Panther 开发者默认项与第一次亮度不被 float 默认值覆盖

这份流程只回答：来源怎样在 `aosp_panther-userdebug` 上写入开发者默认项，并让第一次开机的低 int 亮度不被 Pixel 的 float 默认值盖掉。它不回答 user 构建的 adb RSA 授权，也不重复 captive portal URL 改动。来源是 [Pixel 7 AOSP 开发者默认项与亮度默认值](./xfq-20260614-01.md#3-亮度同步保护)。

验证机型行写了 Pixel 7 / panther 和一台序列号。序列号不进入本卡。作者的编译成功和开机快照保持来源自述。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 来源要求 | 不足时 |
|---|---|---|
| 分支 | `分支：`feature/developer-defaults` → 合入 `dev`` | 不在这条分支上时，属性名可能还没接进 framework |
| 树与午餐 | 来源进入 `android13_r78` 后执行 `lunch aosp_panther-userdebug`，再 `m -j8` | 不是 panther userdebug 时，不要把快照键值当成合同 |
| 需求 | 默认开发者模式、Stay awake、不自动熄屏、关 OTA 自动更新、开 USB 调试、低亮度 | 只想改其中一项时，仍要单独看亮度同步，不能只改 overlay |
| 排除 | `packages_modules_NetworkStack.patch` 在已验证镜像里，但来源写 `它不是本次亮度需求新增点` | 把该 patch 当成亮度修复走 F3 |

<a id="parameters"></a>
## 参数口径

产品文件 `device/google/pantah/aosp_panther.mk` 增加的属性是：

- `persist.sys.usb.config=adb`
- `ro.adb.secure=0`
- `ro.xf.default_screen_brightness=8`

`ro.xf.default_screen_brightness` 是本 ROM 的只读属性。来源用它标记：第一次启动时若 SettingsProvider 写入的 int 就是 ROM 默认值，就保留这个 int，避免被 Pixel 的 float 默认亮度覆盖。

SettingsProvider `defaults.xml` 的键：

- `def_screen_off_timeout=2147483647`：近似永不自动息屏
- `def_screen_brightness=8`
- `def_stay_on_while_plugged_in=true`
- `def_development_settings_enabled=true`
- `def_adb_enabled=true`
- `def_ota_disable_automatic_update=true`

`DatabaseHelper.java` 在初始化 global settings 时写入 `Settings.Global.ADB_ENABLED` 和 `Settings.Global.OTA_DISABLE_AUTOMATIC_UPDATE`。

亮度有三个数值空间，不能混用：

| 空间 | 来源写法 | 来源给出的数 |
|---|---|---|
| Settings int | `settings get system screen_brightness`，传统 `0..255` | 默认写入 8 |
| float | `0.0..1.0`，Pixel 7 运行时显示默认值 | `0.17429718` |
| 快捷设置 gamma | `BrightnessUtils.convertLinearToGammaFloat(...)` | `GAMMA_SPACE_MAX=65535` |

来源写下拉亮度条不是 `screen_brightness / 255`。因此会出现 `screen_brightness=45` 且 `config_screenBrightnessSettingDefaultFloat=0.17429718`，滑条看起来仍像 80% 以上。

同步保护的三个条件是：属性 `ro.xf.default_screen_brightness` 存在；当前 int 等于 ROM 默认值；当前 float 默认值和 int 换算出来的 float 不一致。满足时 `则启动同步时优先把 int 默认值同步到 float/显示侧`。来源写这只影响本 ROM 声明过的第一次默认值，不改变用户后来手动调节的同步。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 核对分支、panther userdebug 午餐目标，以及六项需求 | 前提表 | 树或午餐目标不符则停止 |
| S2 | 在 `aosp_panther.mk` 写入三个属性，并把 ROMManager 放进 PRODUCT_PACKAGES | 属性清单 | overlay float 被当成唯一生效点走 F1 |
| S3 | 写 defaults.xml 的六个 def_ 键，并在 DatabaseHelper 写 ADB 与 OTA 两个 global | 默认值清单 | 缺 ADB_ENABLED 的代码写入时，不要只靠 xml 一句 |
| S4 | 在 BrightnessSynchronizer 加上面的三条件，让 int 默认值盖过 Pixel float | 条件三句 | 不处理时来源写会覆盖成约 45，走 F2 |
| S5 | 按来源编译 | 作者报告的成功行 | 没有成功行就不进入刷机叙述 |
| S6 | 刷机后只对照来源列出的快照键 | 验收表 | 键值不符走 F4；序列号不录入 |

来源的午餐与编译是 `lunch aosp_panther-userdebug` 和 `m -j8`。成功行是 `#### build completed successfully (06:29 (mm:ss)) ####`。刷机使用 panther 产品输出目录的 `fastboot flashall -w`，并设置 `ANDROID_PRODUCT_OUT`。命令中的设备序列号省略。刷机前、开机后各有一份备份目录，路径在来源的 `android13_r78_changes/backups/` 下。

<a id="outputs"></a>
## 输出

交付的是三份 patch 的角色说明，而不是 patch 正文：`device_google_pantah.patch`、`frameworks_base.patch`，以及被排除出本次需求的 NetworkStack patch。

再加来源开机快照里的这些键：`boot_completed=1`，`ro.xf.default_screen_brightness=8`，`persist.sys.usb.config=adb`，`ro.adb.secure=0`，`development_settings_enabled=1`，`adb_enabled=1`，`ota_disable_automatic_update=1`，`screen_off_timeout=2147483647`，`screen_brightness=8`，`screen_brightness_mode=0`。`slot=_b` 只是该次槽位。

<a id="acceptance"></a>
## 验收

来源的结论句是：这版已正常开机，开发者默认项生效，亮度默认值已降到 `screen_brightness=8`。本卡把这句话保持为作者自述。可核对的是快照是否同时出现下面三项，而不是滑条百分比。

| 观察 | 来源快照 | 不算通过 |
|---|---|---|
| 开机 | `boot_completed=1` | 只有编译成功行 |
| 低亮度 int | `screen_brightness=8` | 滑条位置，或 int 约 45 |
| float 设置键 | `screen_brightness_float=null` | 不能把散文里的 `0.17429718` 填进这个键 |
| 接电不息屏 | `stay_on_while_plugged_in=15` | 不能改写成 xml 里的字符串 true |
| adb | `adb_enabled=1` 且 `ro.adb.secure=0` | 不证明 user 构建不会再弹 RSA |

<a id="failure-exits"></a>
## 失败出口

F1：overlay 不是生效点。来源写 `config_screenBrightnessSettingDefaultFloat=0.027559055` 留在 patch 里，但运行时 lookup 仍是 `0.17429718`。看到 overlay 值仍被设备配置盖住就停止，回到 S4，不要再调这个 float 试图压低亮度。

F2：不加同步保护时，来源写 `会把我们在 SettingsProvider 中写入的低 int 亮度覆盖成约 `45``。快照若是 45 左右，本流程没有完成。

F3：NetworkStack captive portal patch 不是本次需求。亮度或开发者开关的问题不要改探测 URL。user 构建的 adb RSA 也不在本篇。

F4：xml 写 `def_stay_on_while_plugged_in=true`，快照却是 `stay_on_while_plugged_in=15`。来源没有给出 true 到 15 的换算。快照里 `screen_brightness_float=null`，与散文中的设备 float 默认值也不是同一个字段。对不上时停止，不要把两个数说成同一次测量。
