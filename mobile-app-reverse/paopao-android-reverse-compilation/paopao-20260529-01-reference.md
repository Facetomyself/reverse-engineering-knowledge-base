---
schema_version: 2
id: android-local-root-detection-reference
document_type: reference
original_date: '2026-05-29'
archived_date: '2026-10-02'
scope:
  targets:
    - android-local-root-detection
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260529-01.md#一检测强度分级"
    basis: source-report
  - id: s2
    ref: "./paopao-20260529-01.md#二root-检测的四个维度"
    basis: source-report
  - id: s3
    ref: "./paopao-20260529-01.md#21-文件存在性检测"
    basis: source-report
  - id: s4
    ref: "./paopao-20260529-01.md#三native-层文件检测"
    basis: source-report
  - id: s5
    ref: "./paopao-20260529-01.md#41-反直觉装了-shamiko第-23-章-大部分-hook-反而冗余"
    basis: source-report
  - id: s6
    ref: "./paopao-20260529-01.md#42-多线程检测的时序问题"
    basis: source-report
  - id: s7
    ref: "./paopao-20260529-01.md#52-两层防御--art-aot-inline"
    basis: source-report
  - id: s8
    ref: "./paopao-20260529-01.md#61-cmbshield-自研防护层"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2, s5]
    basis: source-report
    limits: 四类痕迹和 Play Integrity 边界是来源对 2026-05 前后客户端检测的描述。不是某一银行或音乐 App 的当前规则，也未复测。
  - name: interfaces
    anchor: interfaces
    sources: [s2, s3, s4]
    basis: source-report
    limits: 只记录来源点名的 API 和通配范围。不收录改返回值脚本。
  - name: decision-flow
    anchor: decision-flow
    sources: [s6, s7, s8]
    basis: source-report
    limits: 时序、inline 和延迟信号是来源对两个样本的解释。弹窗消失是作者自述，本卡不把它当成验收。
relations:
  - type: derived_from
    target: "./paopao-20260529-01.md#一检测强度分级"
tags:
  - root-detection
  - source-report
---

# 本地 Root 痕迹检测面，以及来源说 Hook 到不了的边界

这张卡只回答：来源把设备本地的 Root 痕迹分成哪几类、每一类点了哪些 API，以及哪些判定它明确说不能靠改 App 进程里的返回值结束。不收录各节的 hook 正文，也不把酷狗或招商银行的作者自述当成可复用步骤。root 管理器的 shell 命令在另一张卡。

<a id="risk-control"></a>
## 本地痕迹和本地改不到的判定

来源把范围限定在进程内的本地检测，并把它和 2025-01 之后的 Play Integrity、硬件密钥证明分开。

> > **边界** ：本文范围是 **设备本地检测** ——App 进程内的判定逻辑都可以靠 Hook 改返回值。但 2025 年 1 月 SafetyNet

Play Integrity 的 verdict 是服务端签名的 JWT，业务后端再验。来源写本地 hook 无效，因为签名密钥不在 App 里。

> **Hook App 本地无效** ——签名密钥不在

硬件证明走 `KeyStore.attestKey()` 的证书链。来源的边界是软件路径基本走不通，STRONG 它写明拿不到。

> **几乎无法软件绕过** ，业内目前只能靠 ` PlayIntegrityFix ` Magisk 模块伪造 BASIC/DEVICE

本地四类是：`su` 一类文件、`which su` 一类命令、`ro.build.tags=test-keys` 一类属性、Magisk Manager 一类包名。

> Root 痕迹分四类—— ` su ` 等特征文件、 ` which su ` 类 Shell 命令、 ` ro.build.tags=test-keys

强度只是来源的三分法：普通商业 App 多在 Java 文件和包名；游戏同时看模拟器；金融 App 常再加第三方 SDK 和后台复检。这不是产品名单。

装了 Shamiko 或 Zygisk Assistant 时，来源说 `/data/adb`、`/sbin/magisk` 一类路径会在 mount namespace 里被空目录盖住，`File.exists()` 返回 false 是真的 false。包名视图也会被藏。系统属性不在这层里面。

> Shamiko 不改 build 属性

<a id="interfaces"></a>
## 来源点名的 API

文件：Java 的 `File.exists`、`canRead`、`canExecute` 都要看。来源举的业务写法是 `exists() && canExecute()`，只改 `exists` 会漏。通配只锁路径以 `/su` 结尾或包含 `magisk`。扩到 `sys`、`root`、`security` 会碰到正常路径。

> 命中 ` /su ` 结尾或 ` magisk ` 子串就一律

> 扩到 ` sys ` 会命中 ` /system/... ` 、 ` /sys/... `

Native 还要看 `*at` 系列。只挂 `access`/`stat` 会漏。`fopen` 返回的是指针，和返回整数的 `stat` 不是同一类失败值。来源把 `fopen` 单独算进去，是因为有的检测用它而不是 `access`。

> access/stat ` 会漏。

直接 `svc #0` 的 SO 不经过这些 libc 导出。来源说这不是新手法；它点名同盾、网易易盾的部分版本会大量这样走，并说要用指令级跟踪，本篇没有给出该跟踪的验收。

命令：`Runtime.exec` 的多个重载，以及数组形式里不是第 0 项才出现 `su` 的写法。来源提醒返回 null 会让调用方读输出流时崩溃，因为返回类型是 `Process`。

> 替换成 ` echo ` 而非返 ` null ` ： ` Runtime.exec ` 返回 ` Process ` ，调用方一般会读它的输出流， `

属性：`SystemProperties.get` 的两个重载，以及 `android.os.Build.TAGS` 这种静态字段。只挂前者挡不住直接读字段的 SDK。

> 单 Hook ` SystemProperties.get ` 拦不住。

Android 11 起 `Field.modifiers` 在 hidden API 黑名单里，反射改 `final` 字段可能失败，JIT/AOT 还可能把字段收成常量。来源的判别是写完立刻读回，不相等就失败。它记录的成功环境是 Pixel 6 Pro / Android 13 / Magisk + Zygisk，不是未 root 或严格 hidden API 的设备。

包名：点查 `getPackageInfo` 的旧重载和 API 33 的 flags 重载，加上已安装包和已安装应用的枚举重载。来源数了六处入口。具体包名清单不收入本卡。

<a id="decision-flow"></a>
## 来源用来避免看错层的三条观察

Java 层已经弹 Toast：先看上面的四类 API。只有栈很干净、或出现信号文件、进程异常时，才下到 libc。分不清就 spawn，两层都挂上再删没有命中的。

Native 检测可以在 `JNI_OnLoad` 里跑完。attach 晚于这个时点。来源因此把 spawn 写成默认。

> 唯一稳妥的办法是默认上 spawn（详见 第 4.2

按线程名关键字阻止 `Thread.start` 会误伤业务线程。来源要求先只打日志。招行样本的检测它写在 `JNI_OnLoad`，不是这条 Java 线程名单能单独覆盖的。

小的 `private static` 方法可能被 ART 收进调用方的 AOT 机器码。来源在酷狗样本里的观察是：业务方法上的 hook 可以一次都不触发，而 `File.exists` 仍会触发。它把 no-op 挂到持有该方法的 `Activity.onCreate` 上，用来让 ART 丢掉这段 AOT。这是作者对那一个样本的解释。

> > **为什么 B 默认不工作 → ART AOT inline** ： ` O6/P6/Q6 ` 都是 ` private static `

第一个搜到的 `isDeviceRooted` 可以是在跑、但并不是弹窗原因。来源用这个说明不能把第一个布尔方法当成出口。

另一类样本不在调用栈里留 native 帧：native 侧只写信号文件，Java 的 `onCreate` 再去看这个文件才弹窗。

> **Toast 调用栈完全干净** ——栈里只有 ` hanDeRe → dRbf → File.exists → Toast ` ，看不到任何 native 检测痕迹。第 5 章酷狗案例的 Toast 反查工作流在这里失效

来源同时写：Toast 没了不等于判定没有被记下，同一份状态还会被服务器读到。本卡不收录切断上报的写法。

> **Toast 没了不等于绕过——同一份内部状态会被服务器读到**

第三套动态加载的检查只读一个本地文件并返回 0/1。来源说写这个文件的调用没有出现在它挂过的 libc 写入口上，并推测是直接系统调用，留成未解。这不是已定位的写点。

## 验证与限制

- 弹窗消失、`isRooted()` 为 false、触发次数，都是作者对两个样本的自述。本轮未运行。
- 直接系统调用和 STRONG 完整性没有在本篇给出可复用的闭合做法。
- 招商银行的后文在系列第 18 篇，本篇不是该样本的完整记录。
- 不把来源脚本里的返回值改写收进本卡。
