---
schema_version: 2
id: xf-rom-dual-channel-instrumentation-log-reference
document_type: reference
original_date: '2026-06-18'
archived_date: '2026-10-02'
scope:
  targets:
    - xf-rom dual-channel instrumentation log
  client: AOSP panther userdebug
  version: android13_r78 feature/xf-rom-log-infra and feature/xf-log-v2
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260618-01.md#一功能目标"
    basis: source-report
  - id: s2
    ref: "./xfq-20260618-01.md#systemjava-native-声明"
    basis: source-report
  - id: s3
    ref: "./xfq-20260618-01.md#六selinux"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s2]
    basis: source-report
    limits: 只保留来源写出的 Java/JNI 签名和三条包装入口。头文件里的 mkdir 与写文件实现被省略号截断，本卡不补全。
  - name: parameters
    anchor: parameters
    sources: [s1, s3]
    basis: source-report
    limits: 路径、tag、module 名和 property 只属于这份 ROM 日志约定。crypto 与 net 在表里仍是计划中。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s3]
    basis: source-report
    limits: userdebug_or_eng 对齐和目录 0777 是来源对 enforcing 落盘失败的解释。本轮未编 sepolicy，也未在设备上制造 avc。
relations:
  - type: derived_from
    target: "./xfq-20260618-01.md#六selinux"
tags:
  - aosp
  - logcat
  - sepolicy
  - source-report
---

# xf-rom 插装日志的双通道约定

这张卡只回答：来源把 ROM 插装日志分成哪两个通道、Java/native 入口长什么样，以及 app 写 `/data/misc/rommgr` 时它如何绕开 neverallow 和目录权限。它不是 jnilog 注入流程，也不是 ROMManager 加密算法开关卡。编译节只有命令，没有通过条件，所以不建流程。

<a id="interfaces"></a>
## 入口

来源把同一套日志收成三层包装，底层是 `libcore` 的两个 native。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | `public static native void xfLog(String module, String pkg, char level, String message);` | s2，`xfq-20260618-01.md` 第 147 行 | source-report | `java.lang.System` 上的 `@hide` 声明 | 注释写 pkg 非空才双通道。 |
| C2 | `public static native void xfLogRaw(String pkg, String message);` | s2，第 150 行 | source-report | 同上 | 来源写明只写文件、不打 logcat、堆分配不截断。 |
| C3 | JNI 注册为 `xfLog (Ljava/lang/String;Ljava/lang/String;CLjava/lang/String;)V` 与 `xfLogRaw (Ljava/lang/String;Ljava/lang/String;)V`。 | 第 156–156 行 | source-report | `System.c` 的 `gMethods` | 没有方法体。 |
| C4 | C/C++ 用 `xf_logi/w/e/d(module, pkg, ...)`，大块只走 `xf_log_file_raw(pkg, json_line)`。libcore 对应 `XfLog.i` / `XfLog.iRaw`，framework 对应 `XfRomLog.i` / `XfRomLog.raw`。 | 第 81-84、106-109、117-138 行 | source-report | 来源列出的头文件和两个 Java 类 | 示例参数不是抓到的调用。 |

`pkg` 为空时，头文件在打完 logcat 后直接 return，不写文件。`XfRomLog.w(module, message)` 被写成只有 logcat。

<a id="parameters"></a>
## 路径、tag 与级别

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | logcat tag 是 `xf.{module}`，key=value；文件是 `/data/misc/rommgr/<pkg>/xf_trace.jsonl`。 | s1，第 47–47 行 | source-report | 来源的 log-v2 约定 | `<pkg>` 是路径成分，不是某个包的样本。 |
| C6 | 大 payload 的 logcat 打截断版，文件写完整版。 | 第 50 行 | source-report | 加密数据和证书一类长度 | 截断长度只在注释里出现栈 buf 3800，没有格式定义。 |
| C7 | module 已落地的名字是 `jni`、`linker`，兜底 `rom`。`crypto` 与 `net` 标明计划中。 | 第 200-206 行 | source-report | 这份约定表 | 不要把计划中的 module 当成已经插装。 |
| C8 | 级别 property 是 `persist.debug.xf.log.level`，来源列出 `V/D/I/W/E/A/OFF`，默认 `I`。 | 第 250–250 行 | source-report | 来源给出的 setprop 示例 | 没有读取该 property 的代码。 |
| C9 | 类型 `xf_rommgr_trace_file` 标在 `/data/misc/rommgr(/.*)?`。`userdebug_or_eng` 内允许 appdomain 创建目录和 append 文件，neverallow 豁免同一类型。 | 第 214-227 行 | source-report | 来源贴出的四段 policy | 不是 user 构建的允许规则。 |

<a id="decision-flow"></a>
## 为什么落盘会静默失败

来源把失败分成两层，而且两层都要同时满足才会写出 `<pkg>` 子目录。

| 条件 | 来源写的结果 | 来源给的收口 |
|---|---|---|
| `app_neverallows.te` 禁止 `untrusted_app` 对 `file_type` 目录 `create` | enforcing 下三方 App 不能 `mkdir`，文件落盘静默失败；permissive 看起来正常 | `allow` 和 `neverallow` 都包进 `userdebug_or_eng()`，user 构建不受影响 |
| `init.rc` 把 `/data/misc/rommgr` 建成 owner=system 且 other 只有 `r-x` | app UID 的 `mkdir` 被 POSIX 拒绝 | `mkdir /data/misc/rommgr 0777 system system` |

双通道本身的分支是：普通 `xf_log*` 同时打 logcat 和文件；`*Raw` 只写文件。logcat 过滤示例是 `adb logcat -s xf.jni:I` 这种 tag，不构成验收。

## 验证与限制

- 第 八 节只有 `lunch aosp_panther-userdebug` 和若干 `m` 命令，没有退出码、没有设备上的 jsonl 样本。本卡因此没有 validation 模块。
- `crypto` 插装被写成后续分支，不在本卡。
- 头文件实现以注释省略。栈上 3800 字节只出现在注释里。
- 真机行含序列号，本卡不记录该值。
- jnilog 的 per-app 注入流程、ROMManager 加密开关的 property，是另外两个目标，不把本篇补进去。
