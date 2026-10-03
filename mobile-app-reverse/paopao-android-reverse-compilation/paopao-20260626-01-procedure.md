---
schema_version: 2
id: android-so-dump-elf-repair-procedure
document_type: procedure
original_date: '2026-06-26'
archived_date: '2026-10-02'
scope:
  targets:
    - android-so-dump
  client: Android/Frida
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./paopao-20260626-01.md#12-dump-的时机选择
    basis: source-report
  - id: s2
    ref: ./paopao-20260626-01.md#22-完整的-so-dump-脚本
    basis: source-report
  - id: s3
    ref: ./paopao-20260626-01.md#32-使用-sofixer-修复
    basis: source-report
  - id: s4
    ref: ./paopao-20260626-01.md#33-兜底30-行的极简修复版
    basis: source-report
  - id: s5
    ref: ./paopao-20260626-01.md#51-hook-jni_onload-onleave
    basis: source-report
  - id: s6
    ref: ./paopao-20260626-01.md#63-别跳过这一步ida-二次验证
    basis: source-report
modules:
  - name: parameters
    anchor: prerequisites
    sources: [s1, s3, s4]
    basis: source-report
    limits: 窗口、ELF 头字段和 prot 位都是来源的结构说明。未对照当前 linker 或 SoFixer 版本。
  - name: decision-flow
    anchor: steps
    sources: [s1, s2, s5]
    basis: source-report
    limits: 步骤是来源给出的分支，不是本轮操作记录。示例密钥和 S-Box 字节不录入。
  - name: validation
    anchor: acceptance
    sources: [s6]
    basis: source-report
    limits: IDA 七步和 frida-trace 是作者写下的通过标准。抖音样本的基址和成功与否保持 source-report。
relations:
  - type: derived_from
    target: ./paopao-20260626-01.md#63-别跳过这一步ida-二次验证
tags:
  - android-so-dump
  - sofixer
  - frida
  - source-report
---

# 内存 SO dump 的时机、ELF 修复和 IDA 验收

这份流程只整理来源已经写出的四段：何时读内存里的 SO、怎样把 dump 修到 IDA 能打开、怎样判断修完仍不可用、以及哪条假设会读错。它不新增脱壳步骤。抖音 `libmetasec_ml.so` 只是来源里的一个样本，不并入抖音网页请求卡。

`android-so-dump` 的 parameters、decision-flow、validation 查询都是 0。`douyin` 的命中是网页参数和验证口径。示例密钥十六进制不进入本卡。

适用前提是目标 SO 会在某个时刻以可执行明文出现在进程映射里。静态文件已经能被 IDA 正常反汇编时，不需要这条流程。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 来源写下的要求 | 不足时 |
|---|---|---|
| 明文窗口 | 没加固可以在加载后任意时刻读。加固要等还原完成。来源把 JNI_OnLoad 返回写成多数场景的窗口，把自毁前写成最后窗口 | F1 |
| 读权限 | 读之前把模块标成 rwx。来源写 `.text` 若只剩可执行，直接读会触发 SIGSEGV | F2 |
| 模块身份 | 用 SO 名找模块。Android 10+ 上 dlopen 的返回值不是基址 | F3 |
| 修复器 | SoFixer 需要源 dump、输出路径、dump 时的基址和 dump 模式。基址来自脚本打印，不是 IDA 的加载地址 | F4 |
| 段头兜底 | 只在 Section Header 偏移落到文件外或节数为 0 时清掉 `e_shoff`、`e_shnum`、`e_shstrndx` | F4 |
| 样本分支 | 来源称 `libmetasec_ml.so` 不在 APK 里，要等运行时解密并 dlopen 之后再读 | 还是静态空文件就走 F1 |

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 模块已在映射里：整段 `readByteArray`，或按可读映射逐段 `Memory.copy` 到一块零填充缓冲 | 带基址和长度的 dump 字节 | 模块不存在走 S2；复制抛错记下该段并继续，整模块都不可读走 F2 |
| S2 | 动态加载：在 `dlopen` 与 `android_dlopen_ext` 的返回里按路径匹配 SO 名，再挂 `JNI_OnLoad` 的 onLeave 后读取 | onLeave 时刻的 dump | 返回值不要拿去 `findModuleByAddress`，否则 F3；还没返回就读，可能仍是部分密文，走 F5 |
| S3 | 用打印出的基址交给 SoFixer。SoFixer 报错时，仅按上面的越界条件清 Section Header | 修复后的 ELF | 魔数不是 ELF，或 class 不是 32/64，走 F4 |
| S4 | IDA Manual load，Loading address 填 0，而不是运行时基址。32 位 SO 选 ARM Little-endian 32-bit | 段、字符串、导出和 `JNI_OnLoad` 伪代码 | 对照验收。字符串全乱或 F5 没有可读字符串引用，回到 S2 |
| S5 | 不是集中在 JNI_OnLoad 解密时，来源改为把 `.text` 设成不可读，再用异常处理器看谁的 PC 访问了这段 | 解密例程的 PC | `ex.memory.address` 必须落在该 `.text` 内，否则走 F6。多段可执行不能只取第一段 |
| S6 | 自毁：监视 `mprotect`，地址落在目标 SO 且即将失去可读位时立刻读 | 擦除前的 dump | 来源用可读位而不是可执行位做判断。判错会在仍可读时误读，走 F7 |

已知值的全进程扫描只是配套分支：按可执行、`/data/` 下的 SO、或没有模块的堆栈归类。来源里的示例常量不录入，也不构成验收。

<a id="outputs"></a>
## 输出

交付三样东西，并且都能指回来源：

- dump 字节、SO 名、运行时基址和长度。整段读的代价是段间空隙被零填充，所以后面还要修复。
- SoFixer 或清掉无效节头之后的 ELF。来源写 IDA 可以靠 Program Header 反汇编，但函数名和字符串引用可能不如原始文件。
- 验收表的结果：至少 LOAD、`.text`、`.dynamic`，导出里能看到 `JNI_OnLoad`，F5 含可读字符串引用。作者样本里的具体基址不抄进本卡。

<a id="acceptance"></a>
## 验收

下列通过标准全部是来源写下的，不是本轮打开 IDA 或附加进程的结果。

| 项 | 来源的通过标准 | 不算通过 |
|---|---|---|
| 加载 | Manual load 后能选 ARM Little-endian，64 位样本选 ARM64 | 只看到 SoFixer 打印 success |
| 加载地址 | Loading address 为 0，初始化无报错 | 把 dump 基址填进 IDA |
| 段和字符串 | 能看到 LOAD、`.text`、`.dynamic`，以及正常字符串 | 字符串全是乱码 |
| 导出和伪代码 | 导出中有 `JNI_OnLoad`；F5 含可读字符串引用，而不是对绝对地址的字符解引用 | 伪代码全是 `byte_xxx`，或交叉引用跳不走 |
| 可选回读 | 用来源所说的固定 SO 偏移回到仍在运行的进程做 frida-trace，参数能打印 | 没有触发不能当成 dump 失败以外的新结论 |

<a id="failure-exits"></a>
## 失败出口

F1：模块还没加载，或二次解密还没完成。停止把当前字节当成明文，回到 S2 的 onLeave。静态 APK 里的空 SO 不能代替 dump。

F2：没有先改保护就读只可执行的段。停止这条读取，不把崩溃当成算法结论。

F3：把 Android 10+ 的 dlopen 返回值当成模块基址。改用路径里的 SO 名。

F4：文件头不是 ELF，class 不明，或节头偏移指向文件外。后者只清三个节头字段；前者停止修复。

F5：IDA 第 ⑥ 步失败。来源归因于 `-m` 基址写错，或 dump 时 `JNI_OnLoad` 还没返回。回到 S2，不换一套未写出的修复。

F6：异常处理器没有按 `.text` 范围过滤，或只取了第一段 `r-x`。多段可执行时这条 PC 不能当成解密入口。

F7：用可执行位是否消失来判断自毁。来源写这会在仍可读的权限上误报。条件不成立就不要读。
