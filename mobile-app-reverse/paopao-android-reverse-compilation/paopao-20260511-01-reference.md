---
schema_version: 2
id: frida-java-bridge-call-surface
document_type: reference
original_date: '2026-05-11'
archived_date: '2026-10-02'
scope:
  targets: [Frida]
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./paopao-20260511-01.md#23-调用实例方法先找到对象
    basis: source-report
  - id: s2
    ref: ./paopao-20260511-01.md#33-切换-classloaderjavaclassfactory
    basis: source-report
  - id: s3
    ref: ./paopao-20260511-01.md#44-cast-在加密分析中的经典应用
    basis: source-report
  - id: s4
    ref: ./paopao-20260511-01.md#111-art-的-jit-编译与-hook-冲突
    basis: source-report
  - id: s5
    ref: ./paopao-20260511-01.md#61-什么时候需要创建新类
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2, s3, s4, s5]
    basis: source-report
    limits: 只整理来源描述的 Java 桥可调用面。Java.choose 在本篇写成包含子类，同系列前一篇写成精确 class pointer。deoptimize 的减速在文内有 5-10 倍和 3-5 倍两种说法。未运行，不复制示例密钥或口令。
relations:
  - type: derived_from
    target: ./paopao-20260511-01.md#33-切换-classloaderjavaclassfactory
tags: [frida, java, android, source-report]
---

# Frida Java 桥的主动调用面

这张卡检索第 03、04 篇声明不再重复的那些调用：主动调方法、换 ClassLoader、cast、建数组、注册类，以及 Hook 不触发时的 deoptimize。来源是[Java 层 API 全解](./paopao-20260511-01.md#33-切换-classloaderjavaclassfactory)。没有统一验收，不是 procedure。

<a id="interfaces"></a>
## 可调用面

静态方法直接挂在类 wrapper 上调用。有重载时来源用 `.call(EncryptUtils, ...)`，并写明第一个参数是类 wrapper 本身，即使静态方法用不到实例。实例方法要先有对象：`Java.choose`、在 Hook 里留下 `this`，或 `$new()`。把 `this` 存到回调外面时必须 `Java.retain`。来源把 retain 写成 JNI `NewGlobalRef`，否则回调结束后局部引用失效，之后用会遇到 stale reference；不用时对 wrapper 调 `$dispose()`。`$new()` 被写成 `NewObject`：分配、调用构造、返回引用。`$init` Hook 替换的是其中的构造函数本身。必须在主线程做的事用 `Java.scheduleOnMainThread`。`Java.perform` 的直接回调在 JS 引擎线程，不在主线程；Hook 回调则跟在调用被 Hook 方法的那条线程上。`Java.isMainThread()` 用来区分。

类在兄弟 DexClassLoader 上时，来源认为双亲委派只向上找，默认 PathClassLoader 会 `ClassNotFoundException`。找到 loader 后可以赋 `Java.classFactory.loader`，这会影响之后所有 `Java.use`；要同时操作两个 loader，用 `Java.ClassFactory.get(loader)` 得到独立工厂，再 `factory.use`。枚举回调返回 `'stop'` 可以停下。通用模板是先试默认 loader，失败再枚举。

声明类型是父类或接口时，wrapper 只能调声明类型上的方法。`Java.cast` 把它换成目标类型的 wrapper。`$className` 是运行时类名。来源在 `Cipher.init(int, Key, AlgorithmParameterSpec)` 上把 Key 收成 `SecretKeySpec` 再 `getEncoded()`，把参数收成 `IvParameterSpec` 再 `getIV()`。

JS 数组不能直接充当 Java 数组，要用 `Java.array(类型名, 值)`。来源写 Java `byte` 是有符号的 -128 到 127；读出来可能是负数，转无符号用 `& 0xff`。`long` 超过 2^53 时，来源说传到 JS number 会丢精度，需要精确时先 `toString()`。

接口方法本身不能靠 `Java.use` 去 Hook 实现。来源的办法是 `Java.registerClass` 做一个实现该接口的代理，再在调用点把回调参数换成代理实例，并 `Java.retain` 原来的回调，否则异步回来时局部引用已经失效。

本篇把 `Java.choose` 写成会匹配指定类型及其子类，堆遍历对每个对象做 `instanceof`，开销跟堆上对象总数成正比。`onMatch` 返回 `'stop'` 是早停。来源不建议在高频 Hook 里每次都 `choose`，而是初始化时 retain 一份引用。这和前一篇“精确 class pointer、不返回子类”互相矛盾，本卡只记录本篇原文。

Hook 设上了却不进回调时，来源归因于 ART JIT：`ArtMethod` 同时有解释器入口和 `entry_point_from_quick_compiled_code`。早期 Frida 只改前者，JIT 后走后者。来源称 Frida 16.x 已同时覆盖两个入口，框架类或加固自定义编译仍可能踩中。`Java.deoptimizeEverything()` 把方法打回解释执行；`Java.deoptimizeBootImage()` 只处理 boot image 里的框架方法。来源建议先不加 deoptimize，不触发再加。减速在正文写成通常 5 到 10 倍，在文末速查写成 3 到 5 倍，两处都没有测量。

反射 `getName()` 对数组返回 JNI 形式。来源的 `jvmSigToFridaName` 把 `[B` 收成 `byte[]` 这类写法，并说 overload 两种都能收，二维数组上 JNI 形式更稳。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 跨回调保存 Java 对象要 NewGlobalRef | `NewGlobalRef` | s1 paopao-20260511-01.md:226 | source-report | 未复现 stale reference |
| C2 | 替换默认 loader 用 classFactory.loader | `Java.classFactory.loader` | s2 paopao-20260511-01.md:453 | source-report | 未在加固样本上切换 |
| C3 | cast 把 wrapper 改到目标类型 | `转换为指定类型的 Wrapper` | s3 paopao-20260511-01.md:581 | source-report | Cipher 示例没有真实密钥材料 |
| C4 | 接口方法不能靠 use 接口去 Hook | `没法 Hook 接口方法本身` | s5 paopao-20260511-01.md:803 | source-report | 代理类是否被 App 接受未验证 |
| C5 | 本篇称 choose 匹配子类 | `会匹配指定类型及其所有子类的实例` | s1 paopao-20260511-01.md:1359 | source-report | 与前一篇精确匹配说冲突 |
| C6 | onMatch 返回 stop 会停止遍历 | `'stop'` | s1 paopao-20260511-01.md:1310 | source-report | “官方支持”没有引到 Frida 文档位置 |
| C7 | 早期 Frida 只改解释器入口 | `Frida 早期版本只改前者` | s4 paopao-20260511-01.md:1482 | source-report | 16.x 的覆盖范围未核对发行说明 |
| C8 | 读 Java byte 可能是负数 | `是有符号的（-128 到 127）` | s3 paopao-20260511-01.md:776 | source-report | 未用真实 byte 数组核对符号扩展 |

## 验证与限制

文内工具函数是来源草稿，不是本轮跑过的脚本。示例里的密钥字节、口令和 token 字段名都不进入本卡。choose 的子类行为和 deoptimize 的倍数都以来源原句并列，不选边。
