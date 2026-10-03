---
schema_version: 2
id: aosp-art-bionic-jni-observe-reference
document_type: reference
original_date: '2026-06-17'
archived_date: '2026-10-02'
scope:
  targets: ["AOSP ART bionic JNI instrumentation"]
  client: Android AOSP ART/bionic
  version: feature/xf-art-instrumentation
  observed_at: unknown
sources:
  - id: s1
    ref: ./xfq-20260617-01.md#31-bionic-dlopen--bioniclinkerlinkercpp
    basis: source-report
  - id: s2
    ref: ./xfq-20260617-01.md#32-art-registernatives--artruntimejnijni_internalcc
    basis: source-report
  - id: s3
    ref: ./xfq-20260617-01.md#33-art-implicitnative--artruntimejnijava_vm_extcc
    basis: source-report
  - id: s4
    ref: ./xfq-20260617-01.md#34-query_native-即时查询--artruntimejnijava_vm_extcc
    basis: source-report
  - id: s5
    ref: ./xfq-20260617-01.md#四sepolicy4-轮踩坑后定型
    basis: source-report
  - id: s6
    ref: ./xfq-20260617-01.md#五uid--10000-守卫关键-bug-fix
    basis: source-report
  - id: s7
    ref: ./xfq-20260617-01.md#验证命令
    basis: source-report
  - id: s8
    ref: ./xfq-20260617-01.md#一功能目标
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2, s3]
    basis: source-report
    limits: 只记录来源点名的四个插装函数和偏移算法。未对照 AOSP 树，也不把后一天的日志格式迁移算进本卡。
  - name: parameters
    anchor: parameters
    sources: [s3, s4, s8]
    basis: source-report
    limits: 属性名和查询文法来自本篇。设备标识和第三方包的命中条数不写入。
  - name: decision-flow
    anchor: decision-flow
    sources: [s4, s5, s6]
    basis: source-report
    limits: sepolicy 选型是来源的四轮对照，不是本轮策略编译。持久注入 jnilog 是另一张流程卡。
  - name: validation
    anchor: validation
    sources: [s6, s7]
    basis: source-report
    limits: neverallow 与 AVC 为空是作者期望。本轮没有编译 sepolicy，也没有刷机。
relations:
  - type: derived_from
    target: ./xfq-20260617-01.md#31-bionic-dlopen--bioniclinkerlinkercpp
  - type: derived_from
    target: ./xfq-20260617-01.md#34-query_native-即时查询--artruntimejnijava_vm_extcc
  - type: derived_from
    target: ./xfq-20260617-01.md#四sepolicy4-轮踩坑后定型
  - type: derived_from
    target: ./xfq-20260617-01.md#五uid--10000-守卫关键-bug-fix
tags: [aosp, art, jni, sepolicy]
---

# AOSP 内 ART/bionic 的 JNI 可观测插装点

这张卡回答在不借助 Frida 的 ROM 里，dlopen、动态注册、隐式 JNI 和按类名即时查询分别插在哪个函数，属性与 sepolicy 怎样才能让 app 读到开关。它不是 zygote 注入 jnilog 的流程。来源里的真机条数保持作者自述。

<a id="interfaces"></a>
## 四个插装函数

bionic 只在 `do_dlopen()` 成功返回前记录。ART 在 `RegisterNativeMethods()` 里逐条记动态注册，在 `FindNativeMethodInternal()` 的 `dlsym` 非空分支记隐式绑定。so 与偏移都走 `dladdr`：文件名取 `dli_fname`，偏移是函数指针减去 `dli_fbase`。linker 处于 bootstrap，不能包含 `android/log.h`，来源改为直接调用已在 linker64 符号表里的日志函数。host 构建用 `ART_TARGET_ANDROID` 跳过这些改动。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C1 | dlopen 记在成功返回前 | 插装位置：`do_dlopen()` 函数成功返回前（`handle != nullptr` 分支）。 | s1，第 84 行 | source-report | bionic linker | 未给出完整函数上下文 |
| C2 | linker 不能包含 log 头 | `linker.cpp` 处于 bionic bootstrap 阶段，不能 `#include <android/log.h>`。 | s1，第 98 行 | source-report | bionic bootstrap | 只说明弱符号可用，未核对 Android.bp |
| C3 | 动态注册逐条遍历 | 插装位置：`RegisterNativeMethods()` 函数体，遍历每个 `JNINativeMethod` 条目。 | s2，第 103 行 | source-report | ART jni_internal | 类名格式在后文 |
| C4 | 偏移是指针减装载基址 | `fnPtr - di.dli_fbase` | s2，第 110 行 | source-report | RegisterNatives 与隐式绑定 | 依赖 dladdr 成功 |
| C5 | 隐式绑定记在 dlsym 之后 | 插装位置：`FindNativeMethodInternal()` 找到符号后（`dlsym` 返回非 null 分支）。 | s3，第 116 行 | source-report | ART java_vm_ext | 与动态注册共用一个开关 |
| C6 | host 测试不走这段改动 | host 构建跳过，不影响 ART host tests。 | s2，第 112 行 | source-report | ART_TARGET_ANDROID | 未核对宏是否包住全部改动 |

<a id="parameters"></a>
## 开关、查询文法和事件名

三个持久属性分别打开 dlopen 日志、注册记录和即时查询。隐式绑定不单独设开关。查询串是 `类名#方法名[#签名]`。即时查询由 `JavaVMExt::Create()` 里的轮询线程读属性，命中后打 `QueryNativeResult` 并清空属性。ROMManager 页改去匹配这个事件，超时从 10 秒改到 5 秒。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C7 | dlopen 用独立属性 | `persist.rommgr.dlopen_log` | s8，第 49 行 | source-report | so 加载 | 触发条件是 app 加载 so |
| C8 | 两种注册共用一个属性 | `persist.rommgr.register_natives` | s8，第 50 行 | source-report | 动态注册 | 隐式绑定写的是“同上” |
| C9 | 即时查询单独一个属性 | `persist.rommgr.query_native` | s8，第 52 行 | source-report | ROMManager 输入 | 文法在查询节 |
| C10 | 隐式绑定不另设开关 | 与 RegisterNatives 共用同一开关 `persist.rommgr.register_natives`。 | s3，第 124 行 | source-report | ImplicitNative | 未说明签名是否可省略 |
| C11 | 查询文法带可选签名 | `类名#方法名[#签名]` | s4，第 130 行 | source-report | poll 线程 | 示例类名不收录 |
| C12 | 页面按结果事件等 5 秒 | 轮询 `logcat -s xf-rom:I` 匹配 `QueryNativeResult`，超时 5 s | s4，第 140 行 | source-report | NativeQueryPage | 小于 300 ms 是作者估计 |

<a id="decision-flow"></a>
## 不要等下一次注册，也不要用 internal 属性

等下一次 `RegisterNatives` 会漏掉启动时已经绑定完的方法。来源改成启动时起轮询线程，约 300 ms 读一次属性，用 `ClassLinker::VisitClasses` 找已加载类，再取 `GetEntryPointFromJni()`。属性类型用 `system_restricted_prop`：ROMManager 可写，`appdomain` 只读。`system_internal_prop` 会让非 coredomain 的 app 读失败。`prebuilts/api/33.0/` 必须同步，否则冻结测试失败。读属性前先丢掉 uid 小于 10000 的进程，避免系统进程打出 AVC。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C13 | 等下一次注册会饿死查询 | query 就永远等不到结果。 | s4，第 128 行 | source-report | 启动时已绑定完的方法 | 早期方案已被本篇替换 |
| C14 | 轮询放在 JavaVMExt 创建时 | `JavaVMExt::Create()` | s4，第 130 行 | source-report | query_native | 300 ms 是来源间隔 |
| C15 | app 要能读、系统进程不写 | 三方 app（`appdomain`）可读；system/vendor 进程不受干扰。 | s5，第 146 行 | source-report | persist.rommgr.* | 未展开 neverallow 豁免全文 |
| C16 | internal 属性让 app 读失败 | app 进程读 prop 被 SELinux 拒绝，插装永远拿到 false | s5，第 179 行 | source-report | 第四轮选型 | 只解释了 untrusted_app |
| C17 | restricted 只限制写 | restricted 只限制 set，不限制 file read | s5，第 180 行 | source-report | 定型宏 | “全部测试通过”是作者自述 |
| C18 | 冻结快照必须一起改 | 否则 `sepolicy_freeze_test` 必挂。 | s5，第 170 行 | source-report | prebuilts/api/33.0 | API 级别只写了 33.0 |
| C19 | 读属性前先看 uid | 三处插装（bionic linker、jni_internal、java_vm_ext）均在读 prop 之前加 | s6，第 196 行 | source-report | 三个插装点 | 阈值在下一行 |
| C20 | 低于 10000 的 uid 直接返回 | if (getuid() < 10000) return; | s6，第 199 行 | source-report | app 进程 | 未核对 getuid 在 linker 里的可见性 |

<a id="validation"></a>
## 作者用来判通过的两条命令

来源把 sepolicy 三套测试的期望写成 neverallow 为 0、treble 28 到 32 通过、freeze 通过。uid 守卫之后，用 dmesg 里的 avc 与 rommgr 过滤，期望没有输出。这些是作者写下的通过条件，不是本轮执行结果。第三方包的条数和偏移不作为本卡验收。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C21 | 策略测试要三项都过 | neverallows 0，treble 28~32 全 PASS，freeze PASS | s7，第 187 行 | source-report | sepolicy 编译 | 未在本轮编译 |
| C22 | AVC 过滤应为空 | 输出为空，零 AVC。 | s6，第 202 行 | source-report | uid 守卫之后 | “零 AVC”是作者自述 |

## 验证与限制

本卡不覆盖注入 so 再打 JNI 日志的那条流程。日志行在本篇是 `xf-rom` 上的 JSON；后一篇日志基建笔记把通道改成按模块拆 tag，那次迁移没有模块卡，本卡也不把 `xf-rom` 写成后续构建仍使用的格式。没有“类还没加载就停止”的失败出口，所以不建流程。
