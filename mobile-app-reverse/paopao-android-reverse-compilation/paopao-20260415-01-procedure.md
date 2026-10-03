---
schema_version: 2
id: paopao-20260415-unidbg-first-call-procedure
document_type: procedure
original_date: '2026-04-15'
archived_date: '2026-07-13'
scope:
  targets: [unidbg-first-call-triage]
  client: Android
  version: unidbg-android 0.9.8 as cited
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260415-01.md#unidbg学习笔记五第一次让-so-跑起来"
    basis: source-report
modules:
  - name: parameters
    anchor: prerequisites
    sources: [s1]
    basis: source-report
    limits: JDK、依赖版本和 JNI 类型字符只按来源摘录。示例类名和入参不进入本卡。
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 步骤是来源的排错顺序。syscall 与文件访问只保留分类，不把后文预告写成已给出的修法。
  - name: validation
    anchor: acceptance
    sources: [s1]
    basis: source-report
    limits: 通过条件是与来源要求的真机同入参结果相等。本轮没有执行对照。
relations:
  - type: derived_from
    target: "./paopao-20260415-01.md#unidbg学习笔记五第一次让-so-跑起来"
tags: [unidbg, jni, source-report]
---

# 第一次 Unidbg 调用的排错闭环

这张流程只覆盖来源自己划定的问题：第一次调用几乎必然失败时，如何把报错分成类、一次补一个 JNI 洞，并用同一组入参对照。它不收录示例工程，也不把“不报错”写成通过。

<a id="prerequisites"></a>
## 前提与输入

来源要求在写第一行 Java 之前先有侦察结果，而不是打开 IDE 再猜。缺任何一项就停在 F1，不进入骨架。

必需输入：

- native 声明带来的 SO 名、方法名、参数类型、返回类型、是否静态。
- 调用方实际怎样组参数。来源写只看签名不够。
- 若声明里有 Context 一类对象，预期 SO 会经 JNI 反查包名、版本或设备信息。具体值不进入本卡。
- 真机上用 Frida 对目标函数记下的入参和返回值。来源写没有对照的跑通是假的跑通。
- 从 APK 解出的目标架构 SO，以及完整 APK。来源写不能只放 SO，因为 `createDalvikVM` 会读签名、包名和资源。

环境按来源：JDK 8 或 JDK 11，它认为不想处理反射参数时用 JDK 11 最稳。Maven 依赖 `unidbg-android`，版本写成 `0.9.8`，仓库是 jitpack。进程名要设成目标包名，因为 SO 可能用它做完整性校验。这些版本和包名都未在本轮安装或核对。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 先侦察再写代码 | 在写第一行 Java | s1 :62 | source-report | 句子在下一行才写完 |
| C2 | 必须有真机对照 | 你必须先用 Frida 在真机上跑一遍目标函数 | s1 :126 | source-report | 未抓取任何入参 |
| C3 | JDK 范围 | JDK 8 或 JDK 11 | s1 :189 | source-report | 未安装 |
| C4 | 依赖版本 | 0.9.8 | s1 :230 | source-report | 不把该版本写成当前最新 |
| C5 | APK 不能只留 SO | APK 一定要放完整的，不能只放 SO | s1 :243 | source-report | 未做缺 APK 对照 |
| C6 | 进程名用途 | setProcessName 很重要 | s1 :274 | source-report | 未看到具体校验 |

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 收齐前提里的声明、真实传参、Frida 入参与返回值、SO 和完整 APK | 一份侦察包 | 缺任何一项走 F1；齐了走 S2 |
| S2 | 按来源搭 64 位模拟器、用完整 APK 建 Dalvik VM、注册 JNI、打开 verbose，再加载 SO | 能执行到调用行；初始化是否抛错 | 加载即失败仍按 S4 的异常类型分类，不先改 Backend |
| S3 | 调用签名从 JADX 的 smali 复制。记住 Z 是 boolean、B 才是 byte，类名用斜杠且对象类型以分号结尾 | 一条 JNI 方法签名 | 签名来源对不上声明则走 F1，不猜 |
| S4 | 运行后只读三段：异常类型、栈顶方法名、签名里的类名。栈底的 Unicorn 中断按来源忽略 | 问题大类：JNI、链接/签名、syscall、文件、内存 | JNI 走 S5；syscall 或 resolve failed 走 F4；材料不够走 F1 |
| S5 | 只 override 栈顶对应的那一个方法，用签名字符串分发；未匹配的交给 super，让下一次仍报未实现 | 这一处不再以同一签名抛出 | 出现新签名回到 S4，禁止顺手再补；看不懂的方法走 F2 |
| S6 | 用侦察阶段的同一组入参再调用，并与 Frida 记录比较 | 两份结果是否相等 | 相等走验收；不相等走 F3 |

来源把骨架目标写成先到达调用那一行，先不管会不会成功。`callStaticJniMethodObject` 被写成会补上 `JNIEnv*` 和 `jclass`。加载 SO 的第二个参数为 true 时，来源写会跑 `.init_array` 和 `JNI_OnLoad`。这些是来源的结构说明，本卡不附完整类。

JNI 类问题再按类名分流，仍是来源的表：`android/content` 多半要补框架对象，`android/telephony` 被写成设备信息，`java/util` 优先绑 JDK 真实类，App 自己的类回到 JADX。本卡只保留分流，不记录任何设备字段。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C7 | 骨架先不计成败 | 先不管会不会成功 | s1 :249 | source-report | 不是通过条件 |
| C8 | boolean 字符 | 是 boolean，不是 byte | s1 :383 | source-report | 未编译一条签名 |
| C9 | 示例签名形状 | sign([BZ)Ljava/lang/String; | s1 :309 | source-report | 示例方法，不是某个已定位 SO |
| C10 | 未实现异常 | java.lang.UnsupportedOperationException: | s1 :412 | source-report | 示例栈 |
| C11 | 栈顶决定 override | callObjectMethodV | s1 :462 | source-report | 该行是实例方法返回对象 |
| C12 | 栈底无增量信息 | 完全忽略 | s1 :480 | source-report | 来源指的是接近 unicorn.Unicorn 的几行 |
| C13 | 异常类型分流 | JNI 类问题 | s1 :497 | source-report | 同一段还列了链接、syscall、文件、内存 |

<a id="outputs"></a>
## 输出

交付两样东西，并且都能指回来源要求的记录：

- 本次调用的返回值。
- 与阶段 0 同一组入参下、Frida 记录之间的相等与否。

来源写返回值离开 Unidbg 时，对象或数组还要从 `DvmObject` 解包。解包本身不是通过。不报错也不是输出完成。

<a id="acceptance"></a>
## 验收

通过只有一条：同一组入参下，Unidbg 结果与 Frida 结果的相等判断为 true。来源原句是 Match 为 true 才是真正的跑通。没有这份对照时，即使调用返回了，也按它的另一句处理：没有对照的跑通是假的跑通。

反例：异常消失、但相等判断为 false。来源把它归到某个补过的值不对，经常是某个返回 null 的方法其实需要真实值。这不构成通过。

编辑本卡或能编译示例类，都不代替这条对照。本轮没有执行。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C14 | 通过条件 | Match 为 true 才是真正的"跑通" | s1 :734 | source-report | 未做对照 |
| C15 | 无对照即不通过 | 没有对照的"跑通"是假的跑通 | s1 :130 | source-report | 未采集真机结果 |

<a id="failure-exits"></a>
## 失败出口

F1：声明、真实传参、Frida 记录、SO 或完整 APK 缺失，或 JNI 签名不是从声明复制来的。停止调用结论，先补侦察。

F2：一次只修一个洞。来源写每次只 override 一个方法，跑一次，确认这个洞补上了再补下一个。看不懂的方法名可以先 return null，让流程继续；若随后崩溃，说明返回值重要，再回头。null 只是占位，不能拿去验收。

F3：相等判断为 false。停止“已经跑通”的结论，回到补过的返回值，而不是再改 Backend。

F4：异常落在 syscall 未实现，或 `resolve failed` 加文件路径。来源只点了类：NR 未实现要另查 syscall 表或以后在 libc 包装上处理；`/proc/self/maps` 一类路径要以后做 IOResolver。这两支不在本流程里补完。停在分类。

F5：只看到栈底 `Unicorn.onInterrupt` 或 `ARM64SyscallHandler.hook`。来源把这叫做中断分发的固定起点。回到栈顶；不要把它当成 Backend 坏了。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C16 | 一次一个洞 | 每次只 override 一个方法，跑一次 | s1 :691 | source-report | 未按此循环执行 |
| C17 | 未知方法的占位 | 先 return null | s1 :702 | source-report | 占位不是验收 |
| C18 | syscall 未实现只点到类 | syscall NR=387 not implemented | s1 :521 | source-report | 来源写以后再讲包装函数 |
| C19 | 文件类停在路径 | resolve failed: /proc/self/maps | s1 :531 | source-report | IOResolver 被推迟到后文 |
