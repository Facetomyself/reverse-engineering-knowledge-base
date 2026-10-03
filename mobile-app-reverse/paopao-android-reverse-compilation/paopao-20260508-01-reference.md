---
schema_version: 2
id: frida-java-perform-overload-parameters
document_type: reference
original_date: '2026-05-08'
archived_date: '2026-10-02'
scope:
  targets: [Frida]
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./paopao-20260508-01.md#22-为什么所有-java-操作都必须在-javaperform-内部
    basis: source-report
  - id: s2
    ref: ./paopao-20260508-01.md#32-classnotfoundexception-的常见原因
    basis: source-report
  - id: s3
    ref: ./paopao-20260508-01.md#41-基本语法和语义
    basis: source-report
  - id: s4
    ref: ./paopao-20260508-01.md#53-参数类型的表示方式
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s3, s4]
    basis: source-report
    limits: 只整理来源对 Java.perform、类工厂大小写、implementation 和 overload 类型串的说法。未运行 Frida，不验证 ArtMethod 入口在具体版本上是否仍只改 quick compiled code。示例类名是占位符。
relations:
  - type: derived_from
    target: ./paopao-20260508-01.md#53-参数类型的表示方式
tags: [frida, java, android, source-report]
---

# Frida Java.perform 与 overload 类型串

这张卡检索 Frida Java 桥的附加约定、类工厂两个名字，以及方法替换和重载类型串怎么写。来源是[第一个 Hook](./paopao-20260508-01.md#53-参数类型的表示方式)。它没有独立的验收和失败出口，不是 procedure。

<a id="parameters"></a>
## 附加、替换与类型串

`Java.use` 在 `Java.perform` 之外会失败，来源给出的错误是 `not allowed outside Java.perform`。来源把原因写成：`Java.use` 要走 JNI `FindClass`，而 `JNIEnv` 要等 `JavaVM->AttachCurrentThread()` 之后才有。`setTimeout` / `setInterval` 的回调里如果还要碰 Java，必须再包一层 `Java.perform`。来源又说线程一旦附加就不会 detach，再次调用的开销几乎为零，它会发现已经附加并直接执行 callback；显式再写是为了防内部 detach。

`Java.perform` 的 callback 是同步的。VM 还没就绪时它会等；`Java.performNow` 在同样情况下立刻抛异常。来源把后者限定在“能确定 VM 已就绪且代码会被高频调用”时，用来跳过等待判断。

`Java.classFactory` 和 `Java.ClassFactory` 被写成两个并存对象，不是版本差异：小写是当前默认工厂实例，`Java.use` 用它；大写是类，`Java.ClassFactory.get(loader)` 绑定到指定 ClassLoader。来源写两者从 Frida 14.x 起一直并存，`Java.classFactory.use(...)` 与 `Java.use(...)` 等价。

设置 `implementation` 时，来源说 Frida 改的是 `ArtMethod` 的 `entry_point_from_quick_compiled_code_`，让调用先进入跳板再进 JS callback。实例方法里 `this` 是那个 Java 实例；静态方法里 `this` 指向类。字段名拿到的是描述符，读写要走 `.value`。返回值类型必须和原方法一致，来源认为类型不对会 `ClassCastException` 或进程退出。分析阶段来源要求仍调用原方法，因为跳过会丢掉副作用。

有多个重载时直接设 `implementation` 会报 `has more than one overload`。类型串：基本类型用 Java 名；对象用全限定名；数组用 JNI 前缀。来源点名 `byte[]` 为 `"[B"`，`long[]` 为 `"[J"`（J 不是 L），`String[]` 为 `"[Ljava.lang.String;"`。不确定有哪些重载时遍历 `overloads`，看 `argumentTypes` 和 `returnType.name`。一次挂上所有重载时用 `overload.apply(this, arguments)` 转发未知参数个数。

不抛异常的 Java 调用栈：`Exception.$new()` 会走 `Throwable.fillInStackTrace()`，再用 `android.util.Log.getStackTraceString` 格式化。来源认为这比 `Thread.currentThread().getStackTrace()` 更适合直接打印；要逐帧处理时才用后者。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | perform 之外不能 Java.use | `Error: not allowed outside Java.perform` | s1 paopao-20260508-01.md:82 | source-report | 未在本机复现该报错 |
| C2 | VM 未就绪时 performNow 抛异常而不是等 | `立刻抛出异常` | s1 paopao-20260508-01.md:129 | source-report | 未对照 Frida 源码 |
| C3 | 两个 ClassFactory 名字不是版本差异 | `不是版本差异` | s2 paopao-20260508-01.md:260 | source-report | 未核对 Frida 发行说明 |
| C3b | 来源把并存写到 Frida 14.x | `两者在 Frida 14.x` | s2 paopao-20260508-01.md:270 | source-report | 句子在下一行才说“起一直并存” |
| C4 | implementation 改的是 quick compiled 入口 | `entry_point_from_quick_compiled_code_` | s3 paopao-20260508-01.md:340 | source-report | 后文称 16.x 会同时改两个入口，本卡不合并 |
| C5 | 字段名是描述符，值在 .value | `字段名指向一个描述符对象` | s3 paopao-20260508-01.md:376 | source-report | 未验证名字冲突时的解析 |
| C6 | 多重载不能直接设 implementation | `has more than one overload` | s4 paopao-20260508-01.md:458 | source-report | 报错原文按来源注释，不是本次运行日志 |
| C7 | long[] 的 JNI 字母是 J 不是 L | `J 表示 long，不是 L` | s4 paopao-20260508-01.md:527 | source-report | 只覆盖来源点名的几条数组签名 |

## 验证与限制

来源没有 Frida 版本矩阵，也没有把“Hook 成功”定义成可观察的通过条件。`entry_point_from_quick_compiled_code_` 只是本篇对入口字段的说法。占位类名不能当成某个 App 的定位。
