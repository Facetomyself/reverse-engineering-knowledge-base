---
schema_version: 2
id: paopao-20260519-android-system-hook-reference
document_type: reference
original_date: '2026-05-19'
archived_date: '2026-07-13'
scope:
  targets: [android]
  client: frida
  version: AOSP field notes through Android 14; API 17 JavascriptInterface; API 26 query Bundle; targetSdk 30 package visibility
  observed_at: unknown
sources:
  - id: s1
    ref: ./paopao-20260519-01.md#32-hook-startactivity-和-sendbroadcast
    basis: source-report
  - id: s2
    ref: ./paopao-20260519-01.md#42-全面监控-sharedpreferences-读写
    basis: source-report
  - id: s3
    ref: ./paopao-20260519-01.md#23-获取当前前台-activity
    basis: source-report
modules:
  - name: decision-flow
    anchor: funnel-points
    sources: [s1]
    basis: source-report
    limits: 漏斗点是来源选择的 Framework 汇聚位置。字段在定制 ROM 上可能改名。示例输出里的标识不抄入本卡，也不证明某个 App 的存储布局。
  - name: interfaces
    anchor: storage-and-bridge
    sources: [s2]
    basis: source-report
    limits: SP 实现分裂、JSBridge 注解和 query 重载只描述来源点名的类。MMKV 与 DataStore 没有方法表。加密 SP 只说明装饰器外侧仍是明文参数。
  - name: parameters
    anchor: version-fields
    sources: [s3]
    basis: source-report
    limits: mActivities、mCurIntent、mReceiver 和 hidden API 警告按来源的版本范围记录。没有在 Android 14 设备上读字段。
relations:
  - type: derived_from
    target: ./paopao-20260519-01.md#32-hook-startactivity-和-sendbroadcast
tags: [android, frida, activity, sharedpreferences, webview, source-report]
---

# Android 系统 API 的 Frida 汇聚点

这张卡检索陌生 App 上该把 Frida 挂在哪一个 Framework 汇聚点，才能看到页面、Intent、广播、默认 SharedPreferences 和 WebView，以及哪些实现根本不会命中。来源是 [Android 系统级 Hook](./paopao-20260519-01.md#32-hook-startactivity-和-sendbroadcast)。`target=android` 的 decision-flow、interfaces、parameters 没有已发布卡片。综合脚本只有示例输出，没有验收，不建 procedure。依据保持 source-report。样例里的标识原值不写入本卡。

<a id="funnel-points"></a>
## 汇聚点而不是业务类

页面流转用来源的三个判断：`onResume` 标当前页，`onCreate` 拿跳转参数，`onPause` 与 `onResume` 配对画切换。前台 Activity 可读 `ActivityThread` 里 `ActivityClientRecord.paused` 为假的那条。Android 9 起这些字段进入 non-SDK 名单，14 再收紧；来源说 Frida 仍能读，logcat 可能出现 hidden field 警告，不影响取值。

所有 `startActivity` 来源不挂在 `Activity.startActivity`，而挂 `Instrumentation.execStartActivity` 的全部 overload，并说明这也盖住 AndroidX `ActivityResultLauncher`。广播接收侧不枚举 `BroadcastReceiver` 子类，而挂 `android.app.LoadedApk$ReceiverDispatcher$Args.run()`。Toast 文本在 `makeText` 创建期取，不在 `show` 里反查内部 TextView；Android 11 起自定义 view 被禁。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 当前页、跳转参数和页面流分别看 onResume、onCreate、onPause 配对 | `onResume 标记当前页 / onCreate 拿跳转参数` | s1 paopao-20260519-01.md:86 | source-report | 时序图本身没有文字坐标 |
| C2 | startActivity 的汇聚点是 execStartActivity | `所有入口在底层都汇聚到 ` Instrumentation.execStartActivity `` | s1 paopao-20260519-01.md:245 | source-report | overload 遍历是后续代码 |
| C3 | 广播接收侧汇聚在 LoadedApk 的 Args.run | `android.app.LoadedApk$ReceiverDispatcher$Args.run()` | s1 paopao-20260519-01.md:369 | source-report | 静态注册和动态注册都按这句概括 |
| C7 | Toast 文本在 makeText 取，不在 show 反查 view | `最可靠的做法是 hook makeText 在创建期拿 text。` | s1 paopao-20260519-01.md:925 | source-report | resId 重载另有 try |

<a id="storage-and-bridge"></a>
## 存储、WebView 与查询

默认 SP 挂 `android.app.SharedPreferencesImpl` 和 `EditorImpl`。`putXxx` 不算落盘，要再看 `commit` 或 `apply`。这套 hook 打不中平行实现：MMKV 的 `encode`/`decode`，以及 DataStore。`EncryptedSharedPreferences` 仍走 SP 接口，但 Impl 上看到的是密文；明文在公开的 Editor 方法参数上。

`addJavascriptInterface` 之后，API 17 起只有 `@JavascriptInterface` 方法暴露给 JS。`ContentResolver.query` 要遍历 overload；四参形式把 `Bundle queryArgs` 放在第三个参数，来源标成 Room/Jetpack 路径。targetSdk 30 起，`getInstalledPackages` / `getPackageInfo` 默认只返回 `<queries>` 里声明过的包。来源接着说有的环境检查因此不走这两个方法，监控面要加宽。本卡不列那些旁路的具体调用。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C4 | put 之后还要看 commit 或 apply 才算落盘 | `仅 putXxx 不会真正落盘；要在 commit/apply 之后才生效。` | s2 paopao-20260519-01.md:544 | source-report | 未区分 apply 异步失败 |
| C5 | MMKV 和 DataStore 不走这套 SP Impl hook | `后两种 MMKV / DataStore 是「平行替代系」` | s2 paopao-20260519-01.md:576 | source-report | 前三种仍落到 Impl 的句子在上一行 |
| C9 | API 17 起只有带注解的方法暴露给 JS | `@JavascriptInterface 标注的方法才暴露` | s2 paopao-20260519-01.md:742 | source-report | API 17 之前的暴露范围在同一行后半 |
| C11 | 四参 query 的第三个参数是 Bundle，Room 走这里 | `Room/Jetpack 走这条` | s2 paopao-20260519-01.md:832 | source-report | 5/6 参的 selection 位置在上一行注释 |
| C8 | targetSdk 30 起包查询默认被 queries 裁剪 | `默认只返回 ` <queries> `` | s2 paopao-20260519-01.md:1004 | source-report | 未声明时返回空或 NameNotFound 在下一行 |

<a id="version-fields"></a>
## 字段与版本范围

`mCurIntent` 在来源的 API 21–34 AOSP 注释里字段名稳定；`mCurIntent` 与 `mReceiver` 在 Android 5–14 的 AOSP 中同名。定制 ROM 改名时会 `NoSuchFieldError`，来源的退路是改枚举已加载的 Receiver。`ActivityThread.mActivities` 的 hidden API 警告见上节，不重复当成新合同。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C10 | mCurIntent 在来源所称 API 21–34 的 AOSP 上名字稳定 | `mCurIntent 在 API 21-34 的 AOSP 实现里字段名稳定` | s3 paopao-20260519-01.md:381 | source-report | ROM 改名只写了 fallback |
| C6 | Android 14 收紧后，来源仍认为能读到该隐藏字段 | `不影响读值。` | s3 paopao-20260519-01.md:227 | source-report | 警告文本未附 logcat |

## 验证与限制

收束处的三个盲区是：SP hook 只有默认实现；Android 11+ 的已安装包列表默认被裁剪；加固或混淆可能改 Toast 和自定义 SP 类名，来源让回到 `Java.deoptimizeEverything()` 和 `Java.enumerateLoadedClasses`。这是限制，不是跑完综合脚本的通过条件。剪贴板、Dialog 和主动遍历 `shared_prefs` 是同一观察面的旁支，没有单独的字段合同。依据保持 source-report。
