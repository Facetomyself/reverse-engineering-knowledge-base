---
schema_version: 2
id: uncrackable-l2-libfoo-gate-reference
document_type: reference
original_date: '2026-05-11'
archived_date: '2026-10-02'
scope:
  targets: [owasp.mstg.uncrackable2]
  client: Android
  version: UnCrackable-Level2 arm64-v8a; build unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./softard-20260511-01.md#第一步用-jadx-找入口"
    basis: source-report
  - id: s2
    ref: "./softard-20260511-01.md#第二步使用ida64-打开-arm64-v8a的so"
    basis: source-report
  - id: s3
    ref: "./softard-20260511-01.md#第三步追开关找到反调试"
    basis: source-report
  - id: s4
    ref: "./softard-20260511-01.md#第四步patch-so绕过反调试"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2]
    basis: source-report
    limits: 只覆盖 Level 2 这个 APK 的 arm64-v8a libfoo.so。其他 ABI 和 L1 的 smali 注入不在本卡。
  - name: parameters
    anchor: parameters
    sources: [s2]
    basis: source-report
    limits: 口令来自来源伪 C。JNI 虚表偏移没有函数名。本轮未运行。
  - name: risk-control
    anchor: risk-control
    sources: [s3]
    basis: source-report
    limits: fork/ptrace 的指令级细节来源写明留到下篇。函数体图未随文保存。
  - name: decision-flow
    anchor: decision-flow
    sources: [s4]
    basis: source-report
    limits: 只记录来源报告的单点字节修改。字节不符、重打包失败和非 arm64 都没有失败出口，所以不是 procedure。
relations:
  - type: derived_from
    target: "./softard-20260511-01.md#某厂安全研发的逆向笔记9新手村实战3刚出村遇见一只拦路猫"
tags: [uncrackable, libfoo, jni, anti-debug]
---

# UnCrackable Level 2：libfoo.so 的校验入口、口令门闩和 sub_918

这张卡只回答公开练习样本 `owasp.mstg.uncrackable2` 的三件事：口令比较停在哪个 native 导出，什么门闩会让正确口令仍然失败，来源准备改 `libfoo.so` 的哪几个字节。来源是 [笔记（9）](./softard-20260511-01.md#第四步patch-so绕过反调试)。

近邻查询里，`owasp.mstg.uncrackable2`、`UnCrackable-Level2` 和 `libfoo.so` 都没有已有模块。FinClip 的多进程 ptrace 卡、笔记（10）的 ARM64 寄存器卡是别的目标：前者不分析这个 APK，后者只说上一篇的 F5 够用。依据保持 source-report。来源没有写出字节对不上时怎么办，因此不是 procedure。

<a id="interfaces"></a>
## 入口

jadx 里校验在 `CodeCheck.a()`，类里只有 native `bar(byte[] bArr)`。`System.loadLibrary("foo")` 指向 `lib/arm64-v8a/` 下的 `libfoo.so`。IDA 导出窗口没有 `jni_onload`，名字带 `Java_` 前缀；来源因此按静态注册，直接打开 `Java_sg_vantagepoint_uncrackable2_CodeCheck_bar`。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | Java 入口是 CodeCheck.a | `CodeCheck.a()` | s1 ./softard-20260511-01.md:64 | source-report | 只这条转发 |
| C2 | native 声明是 bar(byte[]) | `bar(byte[] bArr)` | s1 ./softard-20260511-01.md:67 | source-report | 类体被压成两行 |
| C3 | 库名是 foo | `System.loadLibrary("foo")` | s1 ./softard-20260511-01.md:76 | source-report | 只这个静态块 |
| C4 | 文件是 libfoo.so | `libfoo.so` | s1 ./softard-20260511-01.md:78 | source-report | 同句限定 lib/arm64-v8a/ |
| C5 | 来源称没有 jni_onload | `jni_onload` | s2 ./softard-20260511-01.md:91 | source-report | 原文就是这个小写拼写 |
| C6 | 导出符号 | `Java_sg_vantagepoint_uncrackable2_CodeCheck_bar` | s2 ./softard-20260511-01.md:93 | source-report | 包名来自符号本身 |

<a id="parameters"></a>
## 口令与门闩

伪 C 在 `byte_1300C == 1` 时把 `"Thanks for all the fish"` 拷进栈，用 `strncmp` 比较 `0x17u`，并要求 JNI 长度调用的返回值等于 23。来源把这句总结成 23 个字符。虚表偏移 `1472LL` 和 `1368LL` 只出现在伪 C 里，来源没有把它们命名成某个 JNI 函数。门闩不为 1 时函数直接返回 false。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C7 | 明文字符串 | `Thanks for all the fish` | s2 ./softard-20260511-01.md:104 | source-report | 公开练习口令，本轮未运行 |
| C8 | 比较长度是 0x17 | `0x17u` | s2 ./softard-20260511-01.md:102 | source-report | 23 的十进制写法在第 104 行 |
| C9 | 门闩必须为 1 | `byte_1300C == 1` | s2 ./softard-20260511-01.md:106 | source-report | 赋值不在 bar 里 |

<a id="risk-control"></a>
## 反调试与崩溃

`byte_1300C` 的写点在 init：先调用 `sub_918`，返回后再把字节置 1。来源说 `sub_918` 里有 `fork` 和 `ptrace`，是子进程 attach 父进程占坑，外部调试器不能再 attach。把 `sub_918` 变成空函数后，这个反调试就失效。部分机型的崩溃被解释成 fork 之后 libbinder 不能再用。调用链是 `onCreate() → loadLibrary("foo") → init() → sub_918() → byte_1300C = 1`。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C10 | fork 与 ptrace 在 sub_918 | `fork` | s3 ./softard-20260511-01.md:126 | source-report | 同句还有 ptrace；细节留到下篇 |
| C11 | 崩溃信息指向 fork 后的 binder | `libbinder ProcessState can not be` | s3 ./softard-20260511-01.md:128 | source-report | 下一行才是 used after fork；pid 不收录 |
| C12 | 置 1 发生在 sub_918 之后 | `onCreate() → loadLibrary("foo") → init() → sub_918() → byte_1300C = 1` | s3 ./softard-20260511-01.md:134 | source-report | init 的反编译名字来源未解释 |

<a id="decision-flow"></a>
## 来源报告的修改

来源为了不再 fork，让 `sub_918` 一进入就返回。文件偏移 `0x918` 的第一条指令被写成 `SUB SP, SP, #0x30`，核对字节是 `FF 83 00 D1`，改成 `RET` 的 `C0 03 5F D6`。编辑器点名 010 editor。保存后再用 IDA 打开，这个函数应被看成只有 RET。来源称替换原 so、重打包安装后应用不再崩溃，再输入那 23 个字符即可。

本轮没有打开 so，也没有打包。来源没有写：核对字节不是 `FF 83 00 D1` 时停止，重打包失败时停止，或者文件不是 arm64-v8a 时停止。缺失败出口，不能当成 procedure。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C13 | 改之前要看到的原字节 | `FF 83 00 D1` | s4 ./softard-20260511-01.md:148 | source-report | 偏移 0x918 在第 141 行 |
| C14 | 来源改成的 RET 字节 | `C0 03 5F D6` | s4 ./softard-20260511-01.md:146 | source-report | 字节不符没有退路 |
| C15 | 作者称安装后不再崩溃 | `发现app不崩溃了` | s4 ./softard-20260511-01.md:155 | source-report | 作者自述，本轮未复现 |

## 验证与限制

未回答的问题留在来源末尾：反调试具体反了什么、export 里的 start、init 如何被调用、为什么 IDA Strings 里没有这句口令。本卡不补这些答案。墓碑日志里的 pid、uid 和机型版本不收录。
