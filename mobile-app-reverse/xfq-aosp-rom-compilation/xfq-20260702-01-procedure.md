---
schema_version: 2
id: aosp-panther-pixel-launcher-procedure
document_type: procedure
original_date: '2026-07-02'
archived_date: '2026-10-02'
scope:
  targets: [aosp-panther-pixel-launcher]
  client: Android
  version: aosp_panther-user; Android 13 as cited; factory image id tq3a.230901.001
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260702-01.md#20260702-pixel-launcher-预置与默认-homerecents-切换"
    basis: source-report
modules:
  - name: parameters
    anchor: prerequisites
    sources: [s1]
    basis: source-report
    limits: 包名、override 列表和 RRO 字符串只按来源摘录。不收录设备序列号。壁纸体系不在本卡。
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 步骤是来源从 system_ext 提取、覆盖 Launcher3，并用 product RRO 改 Recents 的顺序。本轮没有编译或刷机。
  - name: validation
    anchor: acceptance
    sources: [s1]
    basis: source-report
    limits: HOME、权限 granted 和焦点是来源写下的验收句。本轮没有设备输出。
relations:
  - type: derived_from
    target: "./xfq-20260702-01.md#20260702-pixel-launcher-预置与默认-homerecents-切换"
tags: [aosp, panther, pixel-launcher, source-report]
---

# panther 预置 Pixel Launcher 并切换 Recents

这份流程回答：怎样把原厂 Pixel Launcher 放进实验 ROM，让 HOME 指向 `NexusLauncherActivity`，并用 product RRO 把 framework 的 Recents 组件换过去，避免 `signature|recents` 权限没授予时桌面崩溃。它不包含 Pixel 壁纸、动态壁纸、主题或 At a Glance。来源是 [Pixel Launcher 预置与 HOME/Recents](./xfq-20260702-01.md#20260702-pixel-launcher-预置与默认-homerecents-切换)。

<a id="prerequisites"></a>
## 前提与输入

- 设备与构建按来源：Pixel 7 / panther，`aosp_panther-user`。必须是 user，不允许 userdebug。
- Google APK 是专有 payload，只放本机 `vendor/xf_gms/panther`，不提交 GitHub。本卡不写家目录和设备序列号。
- Pixel Launcher 不在 `product.img`，在 `system_ext.img` 的 `priv-app/NexusLauncherRelease`。原厂目录里的 oat/vdex/odex 丢掉，只保留 APK。
- `aapt2 dump packagename` 的预期是 `com.google.android.apps.nexuslauncher`。
- 预置宏的第 4 个参数写入 `LOCAL_OVERRIDES_PACKAGES`，值是 `Launcher3 Launcher3QuickStep Launcher3QuickStepGo`。模块是 PRESIGNED、privileged、system_ext。
- `gms.mk` 只在该 APK 的 wildcard 存在时，同时加入 `NexusLauncherRelease` 和 `XfPixelLauncherFrameworkOverlay`。没有 Launcher 时不要改 Recents 指向。
- RRO 的 `config_recentsComponentName` 目标值是 `com.google.android.apps.nexuslauncher/com.android.quickstep.RecentsActivity`。AOSP 默认仍是 `com.android.launcher3/com.android.quickstep.RecentsActivity`。
- 壁纸若要原厂效果，来源把它拆到 `feature/pixel-wallpaper-preload`，不是这条流程的失败。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | HOME 组件名 | com.google.android.apps.nexuslauncher/.NexusLauncherActivity | s1 :40 | source-report | 还要 RRO 才不会崩 |
| C2 | Launcher 在 system_ext | 实际在 `system_ext.img` | s1 :89 | source-report | 不在 product.img |
| C3 | 只留 APK | 只保留 APK | s1 :124 | source-report | 未比对 oat 差异 |
| C4 | override 三个 Launcher3 | LOCAL_OVERRIDES_PACKAGES := $(4) | s1 :157 | source-report | 第 4 参数见调用 |
| C5 | overlay 与 APK 同条件 | 没有 Pixel Launcher 时不应该改 framework Recents 指向 | s1 :190 | source-report | 本轮未跑 make |

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 从 image zip 取出 `system_ext.img`，转 raw 后在 priv-app 里找 NexusLauncherRelease，只复制 APK 并删 oat | 包名等于预期 | 包名不对走 F1 |
| S2 | 用带来源第 4 参数的 priv-app 宏声明 NexusLauncherRelease，覆盖三个 Launcher3 模块 | Android.mk 规则 | 没有 override 走 F2 |
| S3 | 在 gms.mk 里把 Launcher 和 `XfPixelLauncherFrameworkOverlay` 绑到同一个 APK wildcard | 两者同时出现或同时不出现 | 只有 Launcher 没有 overlay 走 F3 |
| S4 | 新增 product RRO，targetPackage 为 android，isStatic，priority 900；写入 recents 组件字符串 | `/product/overlay/XfPixelLauncherFrameworkOverlay.apk` | 去改 pantah vendor overlay 走 F4 |
| S5 | 提取脚本的 `system_ext_priv_apps` 加入 NexusLauncherRelease，使以后的提取带上 Launcher | proprietary-files 与 checksums 被脚本刷新；APK 仍被 gitignore | 清单更新了但 APK 被提交走 F1 |
| S6 | user 变体编译 product、system_ext 和 vbmeta。`PRODUCT_PACKAGES` 里仍出现 Launcher3QuickStep 先不要当失败 | installed-files 与后续 pm path | 最终文件里还有 Launcher3QuickStep.apk 走 F2 |
| S7 | system_ext 变了就 full flashall，且不加 `-w`。只改了 product RRO 时才刷 product 与对应 slot 的 vbmeta、vbmeta_system | 开机，`ro.build.type=user` | 只刷 product 但 system_ext 已变走 F5 |

来源写第一次只装 Launcher、不改 Recents 时，HOME 能 resolve，但打开会抛 `SecurityException`，`getRootTaskInfo()` 需要 `MANAGE_ACTIVITY_TASKS`。原因是 framework 仍按默认 `config_recentsComponentName` 决定谁是 Recents provider，签名类权限不会只因为 privapp XML 就授给 `com.google.android.apps.nexuslauncher`。

<a id="outputs"></a>
## 输出

- `/system_ext/priv-app/NexusLauncherRelease/NexusLauncherRelease.apk`。
- `/product/overlay/XfPixelLauncherFrameworkOverlay.apk`。
- 最终安装列表里不再有 `/system_ext/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk`。
- HOME resolve 为 `com.google.android.apps.nexuslauncher/.NexusLauncherActivity`。
- 来源列出的 Recents 相关权限为 granted=true，包括 `MANAGE_ACTIVITY_TASKS`、`MONITOR_INPUT`、`READ_FRAME_BUFFER`、`GET_TOP_ACTIVITY_INFO`、`REMOVE_TASKS`、`ACCESS_SHORTCUTS`。
- 按 HOME 后焦点落在 NexusLauncherActivity，且没有 `FATAL EXCEPTION`。

`PRODUCT_PACKAGES` 不是输出。来源写它只是产品变量。

<a id="acceptance"></a>
## 验收

来源把验收放在实机命令上，而不是编译日志。来源自己的一次编译写了约 01:24 完成；那是来源报告，本轮没有复跑。

- `sys.boot_completed=1` 且 `ro.build.type=user`。
- `pm path com.google.android.apps.nexuslauncher` 指向 system_ext 里的 NexusLauncherRelease APK。
- `pm path` overlay 包 `com.xiaofeng.frameworkres.overlay.pixellauncher` 指向 product overlay APK。
- `pm path com.android.launcher3` 无输出。
- `cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME` 给出 NexusLauncherActivity。不要用 `cmd role holders`。
- dumpsys install permissions 里上述权限没有 `granted=false`。来源记录的通过句是这些权限 `granted=true`。
- HOME 键之后 `mCurrentFocus` / `mFocusedApp` 落在 NexusLauncherActivity，logcat 不出现 `FATAL EXCEPTION`，也不出现 `getRootTaskInfo()` 要求 `MANAGE_ACTIVITY_TASKS`。
- 桌面已是 Pixel Launcher 但壁纸不是 Pixel 默认：按来源这是范围外，不算失败。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C6 | 必须 user | 不允许 userdebug | s1 :299 | source-report | 未查 lunch 输出 |
| C7 | 权限通过句 | MANAGE_ACTIVITY_TASKS: granted=true | s1 :472 | source-report | 来源预期，不是本轮 dumpsys |
| C8 | 崩溃即未通过 | FATAL EXCEPTION | s1 :500 | source-report | 与权限拒绝一起看 |
| C9 | role 子命令不可用 | Unknown command | s1 :626 | source-report | 来源限定 Android 13 这台设备 |

<a id="failure-exits"></a>
## 失败出口

F1：system_ext 里找不到 NexusLauncherRelease，或包名不是 `com.google.android.apps.nexuslauncher`。停止。不要从 product.img 里另找一个桌面来顶替。专有 APK 被提交进 Git 也停，回到本机 payload。

F2：最终 `installed-files-system_ext.txt` 或 `pm path com.android.launcher3` 仍显示 `Launcher3QuickStep.apk`。`get_build_var PRODUCT_PACKAGES` 里还能看到这个名字不一定是失败。只有安装列表和 pm path 才算数。override 没生效时回到 S2，不要只改产品变量。

F3：Launcher 已装但 `MANAGE_ACTIVITY_TASKS: granted=false`，或打开时 `getRootTaskInfo()` 被拒绝。先 `pm path` overlay 包。RRO 不存在，就是 overlay 没进 product.img，或没刷 product/vbmeta。没有 Launcher 时不应单独启用这条 RRO。

F4：改了 `device/google/pantah/panther/overlay/...` 下的 framework config。来源写当前 `vendor.img` 主要是预编译 copy，这个 overlay 不会稳定进最终镜像。改回 product RRO，路径是 `/product/overlay/XfPixelLauncherFrameworkOverlay.apk`。

F5：`system_ext.img` 变了却只刷 product。来源写必须走一致镜像集，最稳是全量 flashall，并且不加 `-w`。只改 product 里的 RRO、且 system_ext 未变时，才可以按来源刷 product 和对应 slot 的 vbmeta。

F6：用 `cmd role holders android.app.role.HOME` 验收。来源写 Android 13 上该子命令返回 `Unknown command`。验收命令换成 `cmd package resolve-activity` 的 HOME 查询。

壁纸、WallpaperPicker、PixelThemes 缺失时走范围外说明，不开新的失败编号。来源建议另开 `feature/pixel-wallpaper-preload`。
