---
schema_version: 2
id: softard-20260501-art-method-entry
document_type: reference
original_date: "2026-05-01"
archived_date: "2026-10-02"
scope:
  targets: [art-runtime]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./softard-20260501-01.md#每个-java-方法背后都有一张身份证"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录来源写下的执行档位和 ArtMethod 字段角色。结构体是示意，没有字段偏移，也没有 Frida 脚本。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 启动顺序和壳的五步是来源陈述。没有 dump 命令、地址或工具参数，未在设备上核对。
relations:
  - type: derived_from
    target: "./softard-20260501-01.md#每个-java-方法背后都有一张身份证"
tags: [art, artmethod, zygote]
---

# ART 方法入口与壳介入时机

这张卡只回答一个检索问题：来源如何用执行档位、ArtMethod 的两个字段，以及 Zygote 之后的 Application 回调，说明 Java 方法在 Android 上怎么被跑起来、壳插在哪一步。范围是这篇归档的文本。不提供 hook 实现或内存转储步骤。

<a id="parameters"></a>
## 执行档位和 ArtMethod 字段

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 解释执行被写成逐条读 Dalvik 字节码，不需要提前编译。quote: Interpreter（解释执行） | s1 ./softard-20260501-01.md:49 | source-report | 来源对 ART 三档的第一档 | 未看解释器实现 |
| C2 | 即时编译被写成 Android 7 引入，热点方法的机器码先留在内存。quote: JIT（即时编译） | s1 ./softard-20260501-01.md:52 | source-report | 来源对第二档 | 未核对具体系统版本 |
| C3 | 提前编译被写成空闲充电时用 dex2oat，按 .prof 把热点方法做成 .oat。quote: AOT（提前编译） | s1 ./softard-20260501-01.md:56 | source-report | 来源对第三档 | 未看 oat 文件 |
| C4 | Android 7+ 的默认档被写成 speed-profile，安装时几乎不编译。quote: speed-profile | s1 ./softard-20260501-01.md:62 | source-report | 来源对安装后的混合模式 | 不是某个 App 的配置 |
| C5 | 每个 Java 方法对应一个叫 ArtMethod 的 C++ 对象。quote: ArtMethod | s1 ./softard-20260501-01.md:68 | source-report | 来源的内存对象模型 | 结构体未标偏移 |
| C6 | dex_code_item_offset_ 指向该方法字节码在 dex 中的位置；来源把抽取壳写成挖空这个字段。quote: dex_code_item_offset_ | s1 ./softard-20260501-01.md:76 | source-report | 来源对方法抽取壳的字段说法 | 没有样本和回填代码 |
| C7 | entry_point_ 被写成随状态变化的执行入口。quote: entry_point_ | s1 ./softard-20260501-01.md:79 | source-report | 三种执行档共用这一指针 | 未读 libart |
| C8 | 解释档指向全局的 artQuickToInterpreterBridge；JIT 指向该方法自己的机器码；AOT 指向 .oat 里的机器码。quote: artQuickToInterpreterBridge | s1 ./softard-20260501-01.md:82 | source-report | 来源给的三档落点 | 地址未测量 |
| C9 | 来源写 hook 工具改的是 entry_point_。quote: Hook 工具改的就是这里 | s1 ./softard-20260501-01.md:84 | source-report | 来源对 Java hook 落点的陈述 | 不包含替换代码 |
| C10 | 来源写 JIT 之后调用方可能内联缓存，从而绕过 entry_point_，所以 Frida 会先把方法切回解释模式。quote: 强制把方法切回解释模式 | s1 ./softard-20260501-01.md:87 | source-report | 来源对 Frida Java hook 前一步的说法 | 未复现，无脚本 |

<a id="decision-flow"></a>
## 从 Zygote 到壳的回调

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C11 | 第一个用户态进程被写成 Zygote，它预加载 ART、framework 和常用 SO。quote: Zygote | s1 ./softard-20260501-01.md:94 | source-report | 来源的开机顺序 | 未跟踪 init |
| C12 | App 进程来自 Zygote 的 fork，且只 fork、不 exec。quote: Zygote 只 fork，不 exec | s1 ./softard-20260501-01.md:97 | source-report | 来源对继承预加载内存的解释 | 未看 zygote 源码 |
| C13 | fork 之后的共享被写成 COW，只读代码页继续共享。quote: COW（写时复制） | s1 ./softard-20260501-01.md:101 | source-report | 来源对物理内存只保留一份的说法 | 未测内存 |
| C14 | 壳被放在 attachBaseContext，理由是这是 Application 最早的回调，onCreate 已经偏晚。quote: attachBaseContext() | s1 ./softard-20260501-01.md:110 | source-report | 来源给的介入点 | 不是所有壳的证明 |
| C15 | 来源把壳里的顺序写成加载壳 SO、在 SO 中解密或解压 dex、DexClassLoader、替换 ClassLoader、回填 dex_code_item_offset_。quote: 填回 dex_code_item_offset_ | s1 ./softard-20260501-01.md:117 | source-report | 这一篇列出的五步 | 没有命令和样本 |
| C16 | 来源把拿到原始 dex 的时机说成还原完成之后、执行之前。quote: 还原完成后、执行前 | s1 ./softard-20260501-01.md:119 | source-report | 来源的一句话时机 | 没有 dump 命令或地址 |

## 验证与限制

`kb_catalog.py query` 对 art-runtime、art、android 的 parameters、interfaces、decision-flow 都是 0。泡泡以安那篇 Frida 入门只是空模块归档，标题级提到 ArtMethod 入口指针，不覆盖本目标。文末三道思考题没有答案。微信链接的查询串未写入本卡。没有本地运行证据。
