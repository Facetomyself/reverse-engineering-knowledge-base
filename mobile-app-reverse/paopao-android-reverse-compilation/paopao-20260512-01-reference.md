---
schema_version: 2
id: paopao-20260512-frida-native-api-reference
document_type: reference
original_date: '2026-05-12'
archived_date: '2026-07-13'
scope:
  targets: [frida]
  client: android
  version: Frida 14 instance reads; findGlobalExportByName since 16.7; AAPCS64
  observed_at: unknown
sources:
  - id: s1
    ref: ./paopao-20260512-01.md#24-类型转换
    basis: source-report
  - id: s2
    ref: ./paopao-20260512-01.md#73-什么时候用-replace
    basis: source-report
  - id: s3
    ref: ./paopao-20260512-01.md#94-module-对象
    basis: source-report
modules:
  - name: parameters
    anchor: pointer-contract
    sources: [s1]
    basis: source-report
    limits: 只整理来源对 NativePointer、NativeFunction 类型串和 GC 保活的陈述。没有在指定 Frida 版本上复跑，类型表的 LP64/LLP64 大小未对照头文件。
  - name: decision-flow
    anchor: intercept-choice
    sources: [s2]
    basis: source-report
    limits: attach 与 replace 的选择、protect 四步和 this 传递是来源的用法约束。示例里的检测函数名是占位，不证明任何检测被绕过。
  - name: interfaces
    anchor: export-lookup
    sources: [s3]
    basis: source-report
    limits: 导出查找的 null 与抛异常、以及 16.7 前后写法，只按来源记录。没有枚举真实 SO 的导出表。
relations:
  - type: derived_from
    target: ./paopao-20260512-01.md#24-类型转换
tags: [frida, nativepointer, interceptor, android, source-report]
---

# Frida Native 指针、拦截与导出查找边界

这张卡检索 Android 上 Frida Native API 里哪些写法会丢地址精度、被回收、递归进自己的替换函数，以及导出查找在 16.7 前后怎么选。来源是 [Frida Native 层 API 全解](./paopao-20260512-01.md#24-类型转换)。`target=frida` 的 parameters、decision-flow、interfaces 在目录里没有卡片。`target=unknown` 的 decision-flow 是技巧菜单和未导出函数定位，不覆盖这些合同。来源没有验收和失败出口，不建 procedure。依据保持 source-report。

<a id="pointer-contract"></a>
## 指针与调用类型

NativePointer 的 `add/sub/and/or/shr` 在对象内部做 64 位运算。来源写明不要用 `parseInt(ptr.toString(), 16)` 取大地址，比较用 `equals` 或 `compare`。只有显式 `toInt32()`、`toUInt32()` 或 `Number(...)` 才落到 JS Number。从 Frida 14 起，读写优先 `addr.readX()` / `addr.writeX()`，`Memory.read*` 静态形式已标弃用。

`NativeFunction` 的类型串按来源的表对应 C 类型。Android ARM64 默认 AAPCS64，来源说本系列实战不必另写 ABI；`stdcall` 只在跨到 Windows x86 时放进第四个参数。`NativeCallback` 和 `Memory.alloc` 的存活跟 JS 对象走。交给 Native 长期持有时，来源要求放在全局变量里，否则回收后函数指针或缓冲区失效。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 大地址不要用 parseInt 取值，比较走 equals 或 compare | `来获取地址的数值——对于大地址会丢失精度。` | s1 paopao-20260512-01.md:207 | source-report | 2^53 边界是来源陈述 |
| C2 | Frida 14 起优先实例读写，静态 Memory.read 已弃用 | `从 Frida 14 起，所有读写优先用` | s1 paopao-20260512-01.md:1294 | source-report | 未对照 14 的发行说明 |
| C3 | 长期交给 Native 的回调和 alloc 必须在 JS 侧保活 | `必须在 JS 端用全局变量保活` | s1 paopao-20260512-01.md:1295 | source-report | 没有复现回收后的崩溃 |
| C9 | Android ARM64 默认 AAPCS64 | `Android ARM64 默认使用 AAPCS64` | s1 paopao-20260512-01.md:404 | source-report | stdcall 只被点名为跨平台例外 |

<a id="intercept-choice"></a>
## 旁观、替换与改页

只看参数和返回值，或在 onEnter/onLeave 里改参数和返回值，来源推荐 `Interceptor.attach`。要跳过原函数、换成自己的实现，或 attach 因栈帧把进程打崩时，来源改推 `replace`。`replace` 之前必须先 `new NativeFunction(addr, ...)` 留下原函数；之后再构造会指到替换体，调用变成递归。

直接改代码段被写成四步，漏一步或次序错会崩或被检测：备份原始字节，页对齐后 `Memory.protect` 到可写，写入，再改回 `r-x`。长期 `rwx` 被来源标成常见反 Frida 特征。patch 不随脚本卸载还原。onEnter 和 onLeave 之间只用本次调用的 `this` 传指针和长度；多线程下全局变量会串。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C6 | 不改变行为时用 attach | `想看参数和返回值，不改变行为` | s2 paopao-20260512-01.md:786 | source-report | 表是用法建议 |
| C7 | 要跳过原函数时用 replace | `想完全跳过函数执行` | s2 paopao-20260512-01.md:788 | source-report | 未验证具体函数被跳过 |
| C4 | replace 之后再包原地址会递归到自己 | `否则 replace 后再创建会得到自己，导致无限递归。` | s2 paopao-20260512-01.md:1297 | source-report | 没有递归栈样本 |
| C10 | protect 四步漏一步或错位会崩或被检测 | `任何一步漏掉或者错位都会导致进程崩溃或被检测` | s2 paopao-20260512-01.md:614 | source-report | 检测特征未在本轮观察 |
| C5 | 改完代码段要回到 r-x，并自己留原始字节 | `长期保留  ` rwx  ` 是最常见的反 Frida 检测特征之一` | s2 paopao-20260512-01.md:1298 | source-report | 反 Frida 是来源的概括 |
| C11 | onEnter 到 onLeave 不能靠全局变量传参 | `多线程 App 用全局变量传参一定会串。` | s2 paopao-20260512-01.md:1296 | source-report | 没有双线程对照 |

<a id="export-lookup"></a>
## 导出查找

Frida 16.7 起，来源把不限定模块的查找写成 `Module.findGlobalExportByName`。限定模块仍是 `Module.findExportByName(模块, 名字)`。`find*` 找不到返回 null；`get*` 找不到抛异常。`this.context.x0` 到 `x7` 被来源说成与 `args` 对应，`retval` 对应离开时的 x0。这是寄存器别名说明，不是某份 SO 的原型。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C12 | 16.7 起全局导出用 findGlobalExportByName | `Frida ≥ 16.7 推荐写法` | s3 paopao-20260512-01.md:982 | source-report | 16.6 旧写法只被标成兼容 |
| C8 | find 系列找不到是 null，get 系列抛异常 | `findExportByName / findGlobalExportByName 找不到时返回 null` | s3 paopao-20260512-01.md:990 | source-report | 下一行才写 get 会抛异常 |

## 验证与限制

文件监控脚本和速查片段复述上述 API，没有通过条件，也没有失败时停在哪一步。`Memory.scan` 的模式串、hexdump 的 length/offset/header/ansi，以及 open 标志要用 `O_ACCMODE` 取低两位，都停在示例，不单列模块。Thumb 地址加一不在本篇展开。作者写下的成功保持 source-report。
