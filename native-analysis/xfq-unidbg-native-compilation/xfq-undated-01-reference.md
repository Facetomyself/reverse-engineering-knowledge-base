---
schema_version: 2
id: libkwsgmain-docommandnative-parameter-hook
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [libkwsgmain.so]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-undated-01.md#正文"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只记录来源脚本写出的加载钩子和 Java 方法名。JNI_OnLoad 地址只被打印。本轮没有执行脚本。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录签名、so 名和 byte[] 的打印方式。没有样本入参，也没有返回值对照。
relations:
  - type: derived_from
    target: "./xfq-undated-01.md#正文"
tags: [libkwsgmain, doCommandNative, frida]
---

# libkwsgmain.so：doCommandNative 的加载钩子与参数打印

这张卡只回答：这份 Frida 草稿在哪个 so 的加载返回点改哪个 Java 方法，以及参数怎么被打印。它不是 unidbg 调用，也不是快手 Web 的 `__NS_sig3` / `__NS_hxfalcon` 链路。Web 那张卡的 target 是 `kuaishou`，模块是 request-chain 和 validation。阿里 `libsgmainso` 的 `doCommandNative` / `70102` 是另一个 target，不覆盖这里。

来源是 [04-追doCommandNative参数](./xfq-undated-01.md#正文)。适用面只有脚本点名的 `libkwsgmain.so` 和 `JNICLibrary.doCommandNative`。没有验收语句，不能当成已跑通的调用流程。

<a id="interfaces"></a>
## 加载钩子与方法入口

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 同时挂 `dlopen` 和 `android_dlopen_ext` | s1 `Interceptor.attach(Module.findExportByName(null, "dlopen"), {`；s1 `Interceptor.attach(Module.findExportByName(null, "android_dlopen_ext"), {` | source-report | 这份草稿 | 未执行 |
| C2 | 文件名命中后取 `JNI_OnLoad` 地址，然后调用 `hook_mointor_doCommandNative()` | s1 `let address_JNI_OnLoad = Module.getExportByName(this.fileName, 'JNI_OnLoad');` | source-report | 命中的 so | 地址只出现在日志里，没有再被挂钩 |
| C3 | Java 入口是 `Java.use("com.kuaishou.android.security.internal.dispatch.JNICLibrary")` 的 `doCommandNative` | s1 同一调用 | source-report | 该类 | 没有版本号 |

`findCorrectClassLoader` 在 `Java.use` 之前被调用，返回值没有使用。`function setClassloader(loader)` 会写 `Java.classFactory.loader = loader`，全文没有调用它。因此脚本文本本身没有把找到的 ClassLoader 接到这次 `Java.use` 上。

<a id="parameters"></a>
## 参数与打印

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 注释给出的签名是 `doCommandNative(I[Ljava/lang/Object;)Ljava/lang/Object;` | s1 该注释行 | source-report | 这份草稿 | 不是 smali 原文摘录的校对记录 |
| C5 | 启动调用是 `hook_dlopen("libkwsgmain.so");` | s1 该调用 | source-report | 这个 so 名 | 空 target 时匹配条件会放宽，启动参数不是空 |
| C6 | 元素类名是 `"[B"` 时，用 `java.lang.String` 构造器把 byte[] 打成字符串 | s1 `item.getClass().getName() === "[B"` | source-report | 对象数组里的 byte[] | 非 byte[] 走 `toString`；编码没有说明 |

## 验证与限制

脚本没有写出通过条件、失败时停止的条件，或与真实参数的对照。ClassLoader 查找和 setter 没有接上。快手 Web 签名卡不记录这个 JNI 方法。本轮没有运行 Frida。
