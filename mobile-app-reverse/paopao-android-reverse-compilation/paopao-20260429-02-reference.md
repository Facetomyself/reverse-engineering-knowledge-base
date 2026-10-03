---
schema_version: 2
id: unidbg-hook-framework-selection-reference
document_type: reference
original_date: '2026-04-29'
archived_date: '2026-10-02'
scope:
  targets:
    - unidbg hook
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260429-02.md#hook-的本质"
    basis: source-report
  - id: s2
    ref: "./paopao-20260429-02.md#框架-1-functioncalllistener---只观察不改变"
    basis: source-report
  - id: s3
    ref: "./paopao-20260429-02.md#框架-2-systempropertyhook---专治系统属性"
    basis: source-report
  - id: s4
    ref: "./paopao-20260429-02.md#框架-3-xhook-plt-hook---拦截库函数调用"
    basis: source-report
  - id: s5
    ref: "./paopao-20260429-02.md#框架-4-hookzz-inline-hook---函数入口拦截"
    basis: source-report
  - id: s6
    ref: "./paopao-20260429-02.md#框架-6-codehook--blockhook---指令级核武器"
    basis: source-report
  - id: s7
    ref: "./paopao-20260429-02.md#三个常见的坑"
    basis: source-report
  - id: s8
    ref: "./paopao-20260429-02.md#hookzz-ctx-范式算法分步-hook-的工业级写法"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2, s3, s4, s5, s6]
    basis: source-report
    limits: 六个框架的挂载点只复述来源。未打开 unidbg 仓库核对 IxHook.java 或 DynarmicBackend.java。属性示例里的设备指纹字面量不收录。
  - name: decision-flow
    anchor: decision-flow
    sources: [s4, s5, s6, s7]
    basis: source-report
    limits: 自上而下的选型、refresh 症状和 Backend 表是来源规则。走样案例没有独立验收，不升成流程。
  - name: parameters
    anchor: parameters
    sources: [s8]
    basis: source-report
    limits: ctx 栈规则是 HookZz 用法。偏移和 Thumb +1 只属于来源点名的 Aweme libEncryptor.so 样本，未对二进制重定位。
relations:
  - type: derived_from
    target: "./paopao-20260429-02.md#框架-3-xhook-plt-hook---拦截库函数调用"
tags:
  - unidbg
  - hook
  - source-report
---

# Unidbg 六种 Hook 的挂载点和选型边界

这张卡只回答：来源把哪六种 Hook 挂在哪一层、xHook 为什么要单独 `refresh`、什么时候不能用 CodeHook，以及 HookZz ctx 栈和那份 TTEncrypt 偏移怎么记。不收录各框架的完整回调，也不收录系统属性示例里的指纹字面量。指令级 Trace 的行格式不在这张卡。

来源没有 unidbg 版本，也没有可公开定位的原文 URL。

<a id="interfaces"></a>
## 六种框架挂在哪里

来源自己的计数是六个框架、五层抽象。底层三类是 GOT/PLT（xHook）、inline（HookZz / Whale）、模拟器指令（CodeHook / BlockHook）。另外两个不归这三类：`SystemPropertyHook` 走 `HookListener`，在 `dlsym` 解析时把目标转到 SVC；`FunctionCallListener` 在 Debugger 里靠 BL/BLR。

| 框架 | 来源写的挂载点 | 来源写的能力边界 |
|---|---|---|
| FunctionCallListener | `emulator.attach()` 之后的 Debugger。`traceFunctionCall(listener)` 全局，`traceFunctionCall(module, listener)` 限模块 | 只观察。不能改行为 |
| SystemPropertyHook | `new SystemPropertyHook(emulator)`，`setPropertyProvider`，再 `addHookListener` | 只包 `__system_property_get` / `__system_property_find`。未命中返回 null，走默认逻辑 |
| xHook | `XHookImpl.getInstance`，`register(pathname, symbol, callback, true)`，然后 `refresh()` | 拦的是某个 SO 对外部符号的 PLT/GOT，不是全局符号，也不是 SO 内部函数 |
| HookZz | `HookZz.getInstance`，`wrap` 或 `replace` | `wrap` 原函数仍执行；`replace` 原函数不执行 |
| Whale | `Whale.getInstance`，`inlineHookFunction` | 来源把它写成 HookZz replace 的后备，不作为默认 |
| CodeHook / BlockHook | `emulator.getBackend().hook_add_new(new CodeHook() ...)` | 唯一的指令粒度。Trace 被说来源就是 CodeHook 封装 |

xHook 第一参在来源里不叫精确文件名，而叫 `pathname_regex_str`，并指向 `IxHook.java:13`。`"libtarget.so"` 因能当正则子串才匹配；`".*"` 被写成全局。本轮没有打开那个 Java 文件。

系统属性一节的返回值示例含设备指纹字面量，本卡只保留键名 `ro.build.fingerprint` 和 `ro.build.version.release`，以及未命中返回 null。不保存示例值。

`ReplaceCallback` 被来源写成抽象类，不能用 lambda。HookZz 的 `wrap` 示例类型是 `WrapCallback<HookZzArm64RegisterContext>`。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | FunctionCallListener 不在 Emulator / SyscallHandler 上, 而在 Debugger 上 | s2，`paopao-20260429-02.md:112` | source-report | unidbg hook | 未对照 Debugger 实现 |
| C2 | SystemPropertyHook 专门拦截 `__system_property_get` / `__system_property_find` | s3，`:139` | source-report | 系统属性读取 | 不收录示例指纹值 |
| C3 | xHook 注册后必须再调用 `xHook.refresh()` 才会改 GOT | s4，`:205` | source-report | PLT hook | 症状是来源叙述，本轮未跑 |
| C4 | xHook 第一参被来源称为 `pathname_regex_str` | s4，`:212` | source-report | IxHook 注册 | 未打开 IxHook.java:13 |
| C5 | `wrap` 时原始函数仍然执行；`replace` 完全替代 | s5，`:307-308` | source-report | HookZz | 未在样本上区分两种模式 |
| C6 | CodeHook 切到 Dynarmic 后直接抛 `UnsupportedOperationException` | s6，`:386` | source-report | 指令级 hook | 未打开 DynarmicBackend.java |

<a id="decision-flow"></a>
## 自上而下选一层

来源的规则是：从高到低，用能完成任务的最高层，不要先上 CodeHook 或 inline。选型表把 libc 调用给 xHook，系统属性给 SystemPropertyHook，SO 内部观察给 HookZz `wrap`，SO 内部替换给 HookZz `replace`，HookZz 失败再换 Whale，JNI 调用时机给 FunctionCallListener，单条指令给 CodeHook。整函数轨迹明确不要用 CodeHook，改用 Trace。

时机不能合成一条。xHook 和 HookZz 要在目标函数首次被调用前注册；xHook 还要 `refresh()`。Whale 必须在 `loadLibrary` 之后，因为要 `findSymbolByName`。CodeHook、SystemPropertyHook、FunctionCallListener 被写成任意时机。来源纠正了一种说法：xHook 不是必须在 `loadLibrary` 之前，`JniDispatch64` 的测试是加载并 `callJNI_OnLoad` 之后才注册，只要 OnLoad 没调用目标就仍有效。保守做法仍是把会在 OnLoad 里碰到的 libc 函数提前登记。

同一函数不要叠两个框架。来源的模型是：xHook 改调用方 PLT/GOT，HookZz 改被调方函数头，两边对 lr 和原始指令备份的假设会错位。统计和改返回值应写在同一个回调里。

Backend 表里，前五个框架 Unicorn 系和 Dynarmic 都是 OK，只有 CodeHook / BlockHook 在 Dynarmic 列不支持。

忘记 `refresh` 的现场被写成：日志有 `Register getrusage success`，但回调里的打印一次都不出现。这是失败症状，不是验收通过条件。走样案例把全模块 CodeHook 改成 xHook、SystemPropertyHook 和 HookZz.replace 三层，来源称效果一致，但没有对照输入和通过标准，所以不建流程。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | xHook 要在目标函数首次被调用之前注册并 `refresh()` | s7，`:421` | source-report | PLT 改写时机 | `JniDispatch64` 说明「加载前」不是更准确的表述 |
| C8 | xHook 改的是 PLT/GOT，拦的是调用方那一侧 | s7，`:465` | source-report | 与 HookZz 混用的失败模型 | 未在两个版本的 unidbg 上对比覆盖顺序 |
| C9 | CodeHook / BlockHook 在 Dynarmic 上不支持 | s7，`:509` | source-report | Backend 选择 | 与 C6 同一来源判断 |

<a id="parameters"></a>
## HookZz ctx 栈和样本偏移

来源用 `AwemeTTEncrypt.java` 和 `libEncryptor.so` 说明分析阶段用 `wrap` 而不是 `replace`。`preCall` 与 `postCall` 默认不共享局部变量，指针要 `ctx.push`，返回后按相反顺序 `ctx.pop`。约束是：先 push 的最后 pop；两边次数必须一样，否则 ctx 栈泄漏。

地址上的 `+ 1` 只属于这条 ARM32 Thumb 样本。原句是 `module.base + 0x3640 + 1`，ARM64 不加。

| 来源函数名 | 偏移 | 来源给的步骤 |
|---|---|---|
| `hookSub3BB8` | `+0x3BB8` | 主入口 |
| `hookSub3640` | `+0x3640` | AES 单块 |
| `hookSub8BAC` | `+0x8BAC` | SHA512 |
| `hookSub8214` | `+0x8214` | 字节级 XOR |

`Inspector.inspect(bytes, label)` 被写成 Unidbg 自带的十六进制加 ASCII 打印。偏移没有样本版本，不能当成当前抖音 so 的地址。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C10 | ARM32 Thumb 的 wrap 地址要 `module.base + 0x3640 + 1`，ARM64 不加 +1 | s8，`:662` | source-report | 来源的 libEncryptor.so 示例 | 未对 so 重定位 |
| C11 | push 与 pop 是反序，先 push 的最后 pop | s8，`:660` | source-report | HookZz ctx 栈 | 未跑长时间泄漏 |

## 验证与限制

`Register ... success` 只被来源定义成写进内部表，不是 GOT 已改。走样案例的「效果完全一致」没有输入、输出和反例。属性 provider 的示例字符串已从本卡删除。Whale 与 HookZz 谁更稳，只有「社区实践」一句，没有失败样本。本轮没有运行 unidbg，也没有打开被点名的 Java 源文件。
