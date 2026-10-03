---
schema_version: 2
id: frida-java-object-location-decision-flow
document_type: reference
original_date: '2026-05-09'
archived_date: '2026-10-02'
scope:
  targets: [Frida]
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./paopao-20260509-01.md#12-语法init
    basis: source-report
  - id: s2
    ref: ./paopao-20260509-01.md#21-内部类在字节码中的命名规则
    basis: source-report
  - id: s3
    ref: ./paopao-20260509-01.md#45-javachoose-的局限性
    basis: source-report
  - id: s4
    ref: ./paopao-20260509-01.md#71-混淆不会改变的东西
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s2, s3, s4]
    basis: source-report
    limits: 只整理来源给出的定位分支。Java.choose 在本篇被写成精确 class pointer、不走 instanceof；同系列后文写成包含子类。两边都没有版本对照，本卡不把任一说写成已验证行为。未运行脚本。
relations:
  - type: derived_from
    target: ./paopao-20260509-01.md#45-javachoose-的局限性
tags: [frida, java, android, source-report]
---

# Frida 里对象和混淆方法怎么定位

这张卡检索：要看对象诞生、活实例，还是混淆后的方法时，来源让你改挂哪一个点。来源是[构造、内部类、字段与对象搜索](./paopao-20260509-01.md#45-javachoose-的局限性)。分支没有验收，不是 procedure。

<a id="decision-flow"></a>
## 定位分支

关心的是对象怎么被创建，而不是某个方法被谁调用时，来源让你挂构造函数。Frida 里构造函数叫 `$init`，因为字节码名是 `<init>`，wrapper 把以 `<` 开头的特殊方法改写成 `$xxx`。回调里必须再调用 `this.$init(...)`，否则字段停在零值。构造函数回调不写 `return`。`$init` 是拦截 App 自己的构造；`$new()` 是脚本主动 `new`。OkHttp 的 Builder 在字节码里是 `okhttp3.Request$Builder`，来源选择挂 `build()` 一次拿走 URL、方法和头，而不是挂 `java.net.URL`。

内部类在 `Java.use` 里必须用 `$`，不能用源码里的 `.`。匿名类是 `Outer$1`、`Outer$2`，编号按源码出现顺序，增删匿名类会改号。来源的找法是枚举 `Outer$` 前缀，再打印 `getInterfaces()` 和 `getDeclaredMethods()`。

要在没有调用发生时读到活对象，来源用 `Java.choose`。它把底层说成 `art::gc::Heap::VisitObjects`，并写明按 class pointer 精确比对，不走 `instanceof`，所以父类或接口名不会带出子类。`onMatch` 可以是 0 次、1 次或多次。找不到时的表是：已存在的单例继续搜堆；还没创建就挂 `$init`；短命但有必经方法就在那个方法里抓 `this`。不要在很密的循环里反复 `choose`。

`static final` 的基本类型和 `String` 可能被编译期内联。来源的例子是把 `MAX_RETRY` 改成 100 之后，已经编进去的比较仍然是字面量 `3`。对象类型的 `final` 不在这条限制里。启动后才改字段，如果 App 已经把值抄进别的字段，修改也不会被看到。`getDeclaredField` 看不到父类字段，来源用沿 `getSuperclass()` 递归的 `findFieldRecursive`；private 要 `setAccessible(true)`。

混淆会改类名、方法名、字段名。来源列出不会变的东西：字符串常量、Framework API、参数和返回类型、接口方法名、JNI 方法名，以及 Manifest 里的四大组件类名。三条路线是：从字符串引用回到混淆类；挂 `Cipher.doFinal` 一类不会被改名的框架方法，用堆栈看调用者；按未混淆的签名在 App 包前缀里搜方法。全方法追踪只针对一个类，并设每方法日志上限；不要对一个包里的每个类都挂上。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 构造 Hook 必须调用原始 $init | `this.$init(...)` | s1 paopao-20260509-01.md:100 | source-report | 未观察不调用时的崩溃 |
| C2 | Java.use 要用字节码类名里的 $ | `必须使用字节码中的实际类名` | s2 paopao-20260509-01.md:175 | source-report | 匿名类编号稳定性只是来源判断 |
| C3 | static final 基本类型改字段不一定改到调用点 | `已经编译的代码中仍然是硬编码的` | s1 paopao-20260509-01.md:399 | source-report | 只对应来源举的 int 常量例子 |
| C4 | 本篇把 choose 写成精确类型，不走 instanceof | `按对象的 class pointer 精确比对，不走` | s3 paopao-20260509-01.md:595 | source-report | 同系列后文说法相反，未对照版本 |
| C5 | choose 的堆遍历被记成 VisitObjects | `art::gc::Heap::VisitObjects` | s3 paopao-20260509-01.md:505 | source-report | 来源已声明函数名以 AOSP 主干为准，版本可能不同 |
| C6 | 混淆仍留下字符串、框架 API 和签名 | `混淆工具会改变类名、方法名、字段名，但以下内容` | s4 paopao-20260509-01.md:930 | source-report | 不变量表没有用真实混淆包核对 |

## 验证与限制

`Java.choose` 是否返回子类，本篇和后文冲突，不能从这两篇文本里选定。占位包名 `com.example` 不是某个 App 的类定位。没有“找到了就算通过”以外的验收。
