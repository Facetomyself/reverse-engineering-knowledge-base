---
schema_version: 2
id: aosp-panther-apatch-integration-procedure
document_type: procedure
original_date: '2026-06-26'
archived_date: '2026-10-02'
scope:
  targets: [aosp-panther-apatch]
  client: Android
  version: aosp_panther-user; source pins APatch versionCode 11215 and versionName 2c00671
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260626-02.md#apatch--kernelpatch-集成总览唯一入口"
    basis: source-report
modules:
  - name: parameters
    anchor: prerequisites
    sources: [s1]
    basis: source-report
    limits: 镜像选择、工具名和构建参数只按来源摘录。默认 superkey 原值、设备序列号和预装 APK 的 sha256 不进入本卡。
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 步骤是来源为自己的 panther user 构建写的集成顺序。本轮没有编译、打包或刷机。
  - name: validation
    anchor: acceptance
    sources: [s1]
    basis: source-report
    limits: 验收句是来源写下的实机结果。本轮没有设备输出。
relations:
  - type: derived_from
    target: "./xfq-20260626-02.md#apatch--kernelpatch-集成总览唯一入口"
tags: [aosp, panther, apatch, kernelpatch, source-report]
---

# panther user 构建把 APatch 收进 ROM

这份流程回答：在来源描述的 Pixel 7 / panther、`aosp_panther-user` 上，怎样把 APatch 做成刷机前的 ROM 组件，而不是刷完再手工安装。它不覆盖 Magisk ramdisk 文章里的 init_boot 做法，也不覆盖账号、Play Integrity 或别的机型。来源是 [APatch / KernelPatch 集成总览](./xfq-20260626-02.md#apatch--kernelpatch-集成总览唯一入口)。

<a id="prerequisites"></a>
## 前提与输入

缺任何一条就停在 F1，不要先刷。

- 目标是把 Manager 预装进 `/product/app`，在刷机前给带 kernel 的 boot 注入 payload，并用构建参数注入默认 superkey。来源把实验 ROM 的 Manager 放在普通 product app，不放 priv-app。
- 不要按“Pixel 7 就 patch init_boot”处理。判据是 `kptools unpack` 之后是否产生 kernel，以及 `kptools -i kernel -f` 是否包含 `CONFIG_KALLSYMS=y`。来源写当前 panther out 里 `boot.img` 有 kernel，`init_boot.img` 的 kernel size 为 0。patch 目标因此是 `out/target/product/panther/boot.img`。
- host tool 用 `kptools-linux`，payload 用 `kpimg-android`。不要用 `kpimg-linux`。
- 实验 ROM 用来源所说的 debug APK。没有 APatch 官方签名的 release APK 会在上游签名校验处退出。
- Gradle 参数是 `DEFAULT_SUPERKEY`、`AUTO_INSTALL_APATCH`、`AUTO_INSTALL_MODULES`。认证顺序是 stored key，然后 `BuildConfig.DEFAULT_SUPERKEY`，然后 `"su"`。本卡不收录来源写下的 key 原值。
- 来源的 fork 提交说明是 `2c00671 feat: auto initialize APatch for ROM builds`。本机家目录、force-push 和 APK sha256 都不进入本卡。
- 预装包名是 `me.bmax.apatch`，manifest profiles 为 `apatch` 与 `full`。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | Manager 预装到 product app | 预装到 `/product/app` | s1 :41 | source-report | 不是 priv-app |
| C2 | 默认入口只留 su | 默认 su 入口只使用 `/system/bin/su` | s1 :46 | source-report | 不探测 xu/xfu/kp |
| C3 | 不以机型名决定 init_boot | 不要固定按“Pixel 7 就 patch init_boot” | s1 :88 | source-report | 判据是 kernel |
| C4 | init_boot 当前不可 patch | Kernel size: 0，不可 patch | s1 :101 | source-report | 只对来源当时的 out |
| C5 | payload 不是 linux 版 | kpimg-android | s1 :114 | source-report | 误用见 F2 |
| C6 | release 签名不满足就退出 | 会触发上游签名校验退出 | s1 :157 | source-report | 本轮未打包 |

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 对候选镜像做来源的两条判据：unpack 后有没有 kernel，kernel 配置里有没有 CONFIG_KALLSYMS=y | 可 patch 的镜像路径 | 没有 kernel 走 F1；当前来源结论是 boot.img，然后走 S2 |
| S2 | 用 debug 变体和三个 Gradle 参数构建 Manager。key 只从构建参数进入，不写进本卡 | debug APK | 要改用无官方签名的 release 走 F3；否则走 S3 |
| S3 | 把 APK 放进 preloads 的 apatch 条目，profiles 含 apatch 与 full，再跑 `generate_xf_preloads.py --profile full --clean` | `/product/app` 预装模块，APK 字节保持不变，并抽出 arm64 JNI so | 生成器改写了 APK 字节则停，不继续；否则走 S4 |
| S4 | 跑 `patch_apatch_boot.py --replace`，把 patched boot 覆盖回 product out | out 里的 boot.img 已是 patched | 刷机前没做 replace，走 F4 |
| S5 | `lunch aosp_panther-user` 后编译。改了 adbd、system、boot 或 root 链就 full flash；只改 APK 或预装内容才可以 product-only | 刷入的镜像集 | 用 product-only 带上 boot 或 adbd 改动走 F5 |
| S6 | 首次打开 Manager。superkey 按 stored、DEFAULT_SUPERKEY、`su` 的顺序。`AUTO_INSTALL_APATCH=true` 且状态是 NOT_INSTALLED 或 NEED_UPDATE 时调用 `APApplication.installApatch()` | `/data/adb/apd` 与 `/data/adb/ap/su_path` | su_path 不是 `/system/bin/su` 则不要改回 kp，走 F6 |
| S7 | adbd 的 shell fork 只走 `/system/bin/su`，失败再 `/system/bin/sh`。user 构建上 `adb root` 不可用是来源写明的预期 | shell 身份 | 仍在探测 kp、xu、xfu 则回到 S6 的入口策略 |

来源写 root shell 的 fallback 是 `/system/bin/su`，然后 PATH 里的 su，然后 sh。`kp`、`xu`、`xfu` 不再作为 App 或 adbd 的候选。不要在每次 AOSP 编译时自动查 GitHub；需要时才显式跑 `patch_apatch_boot.py --check-updates`。

<a id="outputs"></a>
## 输出

来源把交付定义成这些可检查项，而不是“刷完即成功”：

- product app 路径上的 APatch Manager，以及 app-local 的 arm64 JNI 库，避免 `System.loadLibrary()` 找不到 so。
- product out 里已经 `--replace` 过的 `boot.img`。
- `/data/adb/ap/su_path` 等于 `/system/bin/su`。
- `/data/adb/apd` 的版本与 Manager 一致。来源记录过不 wipe 时 userdata 里的旧 apd 要等 App 首次启动才从 11214 升到 11215。
- user 构建上的 root shell 来自 su，而不是 `adb root`。来源报告的 SELinux context 是 `u:r:magisk:s0`。

<a id="acceptance"></a>
## 验收

下列句子都是来源写下的通过条件。本轮没有刷机，不能把它们写成这次审阅的设备结果。

- `sys.boot_completed = 1`。
- Manager 位于 `/product/app/xf_preload_apk_apatch_manager/`，versionCode `11215`，versionName `2c00671`。
- `/data/adb/apd -V` 与 Manager 同版本；若刷机后立刻看到旧版本，打开 App 后再看一次。
- `/data/adb/ap/su_path` 为 `/system/bin/su`，`/system/bin/su -c id` 为 root。
- `/system/bin/kp`、`/system/bin/xu`、`/system/bin/xfu` 均为 missing。
- `adb shell id` 为 root，且 context 为来源所写的 `u:r:magisk:s0`。`adb root` 在 user 构建上失败不算本功能失败。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C7 | 不 wipe 时 apd 留在 userdata | `/data/adb/apd` 属于 userdata | s1 :374 | source-report | 不直接覆盖 data |
| C8 | 打开 App 后版本对齐 | 启动 APatch 后: /data/adb/apd = 11215 | s1 :380 | source-report | 来源的一次窗口 |
| C9 | shell context 按来源记录 | context=u:r:magisk:s0 | s1 :365 | source-report | 本轮无设备输出 |

<a id="failure-exits"></a>
## 失败出口

F1：候选镜像 unpack 后没有 kernel，或没有 `CONFIG_KALLSYMS=y`。停在该镜像上，不要改去 patch `init_boot.img`。来源写它当前不是 APatch/KP 目标。

F2：用了 `kpimg-linux`。来源写 supercall 能部分工作，但 Android 侧 `kp/sumgr/supercmd` 不完整。换 `kpimg-android` 后重做 S4。

F3：release APK 没有 APatch 官方签名，上游签名校验退出。实验 ROM 回到 debug APK，不要把签名失败当成 boot patch 失败。

F4：full `flashall` 会覆盖 boot。刷前没有 `patch_apatch_boot.py --replace`，或者刷后没有单独刷 patched boot。停止把未 patch 的 boot 当成已集成。

F5：product-only 只能更新 APK 和预装内容。adbd、system、boot 或 root 链的改动改走 full flash。

F6：userdata 被清掉，且 APatch 还没把 runtime su path 设成 `/system/bin/su`。首次 adb shell 可能先落回普通 sh。打开 Manager 做自动初始化后再验收，不要把入口改回 `/system/bin/kp`。

F7：想改 kpimg 编译期的 `SU_PATH` 时，不要对 `kpimg-android` 做二进制字符串替换。从来源所说的 KernelPatch 源码重新编译。

F8：把上游 fetch 放进普通 AOSP 编译。来源要求构建可离线；网络失败不能让普通 build 失败。检查上游只走显式的 `--check-updates`。
