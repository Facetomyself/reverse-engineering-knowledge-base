---
schema_version: 2
id: jni-register-natives-frida-reference
document_type: reference
original_date: '2026-06-25'
archived_date: '2026-10-02'
scope:
  targets:
    - jni-register-natives
  client: Android/Frida
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./paopao-20260625-01.md#21-定位-registernatives-函数
    basis: source-report
  - id: s2
    ref: ./paopao-20260625-01.md#22-完整的-registernatives-监控脚本
    basis: source-report
  - id: s3
    ref: ./paopao-20260625-01.md#四native-回调-java反向追踪
    basis: source-report
  - id: s4
    ref: ./paopao-20260625-01.md#五jni-类型转换实战
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2]
    basis: source-report
    limits: 只整理来源对 libart 符号和 JNIEnv vtable 第 215 槽的描述。未在当前 ART 上核对索引，也未运行脚本。
  - name: parameters
    anchor: parameters
    sources: [s2, s4]
    basis: source-report
    limits: JNINativeMethod 被写成三个指针。签名档距和 Get/Release 配对只来自正文，没有样例输入输出。
  - name: decision-flow
    anchor: decision-flow
    sources: [s2, s3]
    basis: source-report
    limits: spawn、strip 回退、反向调用顺序和 UnregisterNatives 都是来源建议。QQ 音乐次数是作者自述。
relations:
  - type: derived_from
    target: ./paopao-20260625-01.md#21-定位-registernatives-函数
  - type: supplements
    target: kb:mobile-app-reverse-paopao-native-function-location#locator-method-selection
tags:
  - jni
  - register-natives
  - frida
  - source-report
---

# JNI RegisterNatives 的定位与反向调用边界

这张卡只回答：导出表里没有 `Java_` 时，来源怎样定位 `RegisterNatives`、怎样读 `JNINativeMethod`，以及 Native 回调 Java 时先看哪三个 JNI 入口。它不提供可运行脚本，也不把某一款 App 的注册次数当成当前结果。

`kb_catalog.py query` 的审计门被无关文件挡住，命中来自同一实现 `query_records`。`jni-register-natives` 的 interfaces、parameters、decision-flow 都是 0。`unknown` 的 interfaces 命中猿人学 signKey 和两张 wasm 卡，都不写 vtable 槽位。未导出函数定位卡只补充符号、交叉引用和 Thumb 最低位，不覆盖这张注册表。

<a id="interfaces"></a>
## 定位 RegisterNatives

来源先在 `libart.so` 的符号里找名字含 `RegisterNatives`、且不含 `CheckJNI` 的地址。符号被 strip 时，改读 `Java.vm.getEnv().handle` 指向的函数表，取索引 215 再乘 `Process.pointerSize`。来源写索引 215 由 JNI 规范固定，并称各 Android 版本一致；本卡不把这句话升级成当前 ART 的测量。

Hook 的四个参数按来源脚本是 `env`、`jclass`、`JNINativeMethod*`、`count`。类名用 `Java.cast` 到 `java.lang.Class` 再 `getName()`。每条方法是三个连续指针：名字、签名、函数指针。函数指针再用 `Process.findModuleByAddress` 换成模块名加偏移；模块为空时教科书脚本打出问号，短脚本会直接读 `mod.name`。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 符号找不到时，来源把 RegisterNatives 固定在 JNIEnv 函数表第 215 槽 | s1，符号兜底段 | source-report | 来源引用的 JNINativeInterface 顺序 | 未对照当前 jni.h |
| C2 | 符号搜索要丢掉 CheckJNI 包装 | s1，enumerateSymbols 条件 | source-report | 来源脚本 | 不保证第一个非 CheckJNI 符号就是实现 |
| C3 | JNINativeMethod 被写成 name、signature、fnPtr 三个指针 | s2，解析循环 | source-report | 来源的 64 位步长写法 | 没有结构体定义的独立对照 |

<a id="parameters"></a>
## 签名、索引档距和 JNI 字符串

Call 系列在来源的表里按返回类型排成 base、V、A 三连槽。来源让实战只钩 base，并把下一类型的索引用「上一类型 base + 3」估算，同时要求数错时对照 `jni.h`，不要靠记忆。

`GetStringUTFChars` 必须配 `ReleaseStringUTFChars`，`GetByteArrayElements` 必须配 `ReleaseByteArrayElements`。来源把这叫做 JNI 的对账规则。线程还没 attach 时，`Java.vm.getEnv()` 可能失败；来源的替身是 `tryGetEnv` 或 `attachCurrentThread`，细节指向另一篇，本卡不补。

Java 层 `implementation` 能自动转换 `native` 方法的参数。来源写明：要看的是 JNI 入口内部的子函数时，Java 层钩子不够，只能按地址钩 Native。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | base/V/A 三连槽，来源要求只钩 base，并用上一类型 base 加 3 估算 | s2 之前的函数表说明 | source-report | 来源列出的 Call* 索引 | 公式未逐项复算 |
| C5 | Get 出来的 JNI 缓冲区要配对应的 Release | s4，类型转换总则 | source-report | 来源点名的字符串和 byte 数组 | 不覆盖其他 Get/Release 对 |

<a id="decision-flow"></a>
## 时机、短脚本和反向调用

来源把主脚本限定在 `frida -f` 的 spawn：应用第一条指令前挂上，才能截到 `JNI_OnLoad` 里的注册。attach 只能看到之后延迟加载的库。它另外记下 frida 16.7.19 加 Android 14 spawn 会在 `libframework-connectivity-jni.so` 的 dlopen 处闪退，并称与本篇脚本无关；修法指向配套脚本，正文没有给出补丁，本卡不补。

短脚本没有 vtable 回退，也没有模块为空的判断。来源把这两条写成加固或 strip 后的失败点，并建议个人分析用短脚本，交给别人或加固目标用带兜底的长脚本。

反向调用按代价递增：先 FindClass（索引 6）看类，再 GetMethodID / GetStaticMethodID（33 / 113）看方法，最后只对关心的 methodID 钩 Call*Method。来源写 Call*Method 不按 `.text` 或调用栈过滤会被输出淹没。`jnitrace -l libnative.so` 被写成这一组钩子的现成替代，手写脚本的价值是能裁剪。

如果 RegisterNatives 只触发一次之后 Java 调用没反应，来源怀疑 `UnregisterNatives`（索引 216）解绑后再注册到新地址。这是来源的反检测提示，不是本轮观察到的行为。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 要截全 JNI_OnLoad 里的注册，来源要求 spawn，而不是事后 attach | s2，时机说明 | source-report | 来源的主脚本路径 | 没有本轮注入记录 |
| C7 | strip 后的 libart 上，没有 vtable[215] 的短脚本找不到地址 | s2，两种写法对照 | source-report | 来源点名的简洁写法 | 未在 strip 过的 libart 上试 |
| C8 | 反向调用先类、再方法、最后才钩 Call，并且必须过滤 | s3，推荐顺序和表格 | source-report | 来源列出的索引 | 过滤条件没有量化阈值 |
| C9 | 只触发一次后失去映射时，来源要同时看索引 216 | s2，读懂输出后的提示 | source-report | 来源称为反检测的重注册 | 不是证明某应用正在这样做 |

## 验证与限制

作者称同一脚本在 Pixel 5、Android 14、frida 16.7.19 上 spawn QQ 音乐 30 秒，截到 7 次 RegisterNatives、共 94 个方法。这只保留为 source-report。本轮没有设备、APK 或脚本运行。示意日志里的样例字符串不进入本卡。地址漂移的多策略兜底仍以未导出函数定位卡为准。
