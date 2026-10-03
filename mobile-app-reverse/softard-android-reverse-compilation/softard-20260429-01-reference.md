---
schema_version: 2
id: grok-mobile-app-reverse-softard-20260429-01
document_type: reference
original_date: "2026-04-29"
archived_date: "2026-10-02"
scope:
  targets: [android-so-elf]
  client: android
  version: ELF64 examples; Class 01 and Machine 0x28 are also listed
  observed_at: unknown
sources:
  - id: s1
    ref: "./softard-20260429-01.md#一so-文件也是有身份证的"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录来源表里的节、头字段、符号字母和 JNI 三元组形状。未对样例 SO 跑 readelf。不收录替换 GOT 或改内存权限的做法。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: Section 被破坏仍能运行、strip 后退回 readelf，以及静态名与 JNI_OnLoad 两条入口，都是来源的定位顺序。模拟器判断来源写了但不展开。
relations:
  - type: derived_from
    target: "./softard-20260429-01.md#一so-文件也是有身份证的"
tags: [elf, android-so, jni]
---

# Android SO 的 ELF 字段和 JNI 入口分叉

这张卡只回答：来源如何用 Section 与 Segment、ELF 头偏移、以及静态名或 JNI_OnLoad 来定位一个 SO。某个具体 App 的动态注册表不在本卡。替换函数地址和改页权限的句子不收录。

<a id="parameters"></a>
## 节、头字段和符号字母

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | .text 权限 r-x，放机器码。quote: 编译后的机器码，函数实现在这里 | s1 ./softard-20260429-01.md:56 | source-report | 来源的 Section 表 | 表是教学摘要 |
| C2 | .got 与 .got.plt 为 rw-，存外部函数运行时地址。quote: 全局偏移表，存外部函数的运行时真实地址 | s1 ./softard-20260429-01.md:61 | source-report | 同上 | 重定位之后的权限见决策段，不在这格 |
| C3 | .init_array 是加载时依次调用的函数指针，来源写壳常把解密放这里。quote: 壳常在这里放解密代码 | s1 ./softard-20260429-01.md:65 | source-report | 来源对 init_array 的提示 | 没有解密步骤 |
| C4 | .bss 文件中不占空间，加载时补零。quote: 加载时补零 | s1 ./softard-20260429-01.md:59 | source-report | Section 表 | 与后面 FileSiz 不等于 MemSiz 是同一现象 |
| C5 | 64 位平台文件头固定 64 字节。quote: 64 字节 | s1 ./softard-20260429-01.md:79 | source-report | 来源说的 64 位 ELF | 32 位头长未给 |
| C6 | 偏移 0x00 的 magic 写成 7F 45 4C 46。quote: 7F 45 4C 46 | s1 ./softard-20260429-01.md:86 | source-report | 扫内存找 SO | 公开文件魔数 |
| C7 | 偏移 0x04 的 Class：02 为 64 位，01 为 32 位。quote: = 32 位，判断架构 | s1 ./softard-20260429-01.md:87 | source-report | 来源头字段表 | 这格说的是 Class，不是 Machine |
| C8 | 偏移 0x12 的 Machine：0xB7 为 ARM64，0x28 为 ARM32。quote: 0xB7 | s1 ./softard-20260429-01.md:88 | source-report | 来源头字段表 | 同句还有 0x28 |
| C9 | 偏移 0x10 的 Type 为 ET_DYN (3) 时是动态库。quote: ET_DYN (3) | s1 ./softard-20260429-01.md:89 | source-report | SO | 可执行文件的 Type 未展开 |
| C10 | e_phoff 在 0x20，是 Segment 表偏移。quote: e_phoff | s1 ./softard-20260429-01.md:90 | source-report | 64 位头布局 | 来源未给 e_phentsize |
| C11 | e_shoff 在 0x38，来源写加固时常被清零。quote: 加固时常被清零 | s1 ./softard-20260429-01.md:91 | source-report | Section 表偏移 | 未附被清零的样本 |
| C12 | 某个 LOAD 的 FileSiz 不等于 MemSiz 时，多出的部分被写成 .bss。quote: 未初始化全局变量 | s1 ./softard-20260429-01.md:115 | source-report | 来源的 readelf -l 例子 | 例子里的具体差值不单列成通用常数 |
| C13 | GNU_STACK 无 X 表示栈不可执行；来源写若是 RWE 则 NX 关闭。quote: 标记栈不可执行（NX/DEP 保护开启） | s1 ./softard-20260429-01.md:119 | source-report | 该 Program Header 标志 | 同句后半是风险判断，不是检测脚本 |
| C14 | ET_DYN 的 VirtAddr 通常从 0 起，真实地址是运行时基址加偏移。quote: 运行时基址加上这个偏移才是真正的地址 | s1 ./softard-20260429-01.md:130 | source-report | SO | 未测量 ASLR |
| C15 | GOT 存运行时地址，来源写可由 linker 写入。quote: 可以被 linker 写入 | s1 ./softard-20260429-01.md:148 | source-report | 重定位完成前的 .got | 不收录之后如何改写 |
| C16 | PLT 是读 GOT 再跳转的固定跳板。quote: 读 GOT 后跳转 | s1 ./softard-20260429-01.md:149 | source-report | .plt | 未抄桩指令 |
| C17 | nm 的 U 表示未定义导入，对应 GOT 的一格。quote: 对应 GOT 里的一格 | s1 ./softard-20260429-01.md:167 | source-report | nm -D 的字母 | T/t/D/B 同句列出，本行只钉 U |
| C18 | 动态注册表每一项是 Java 方法名、方法签名和函数指针。quote: Java方法名 | s1 ./softard-20260429-01.md:202 | source-report | 来源的 JNINativeMethod 说明 | 示例方法名不进入结论 |

<a id="decision-flow"></a>
## 还能跑、还能定位的顺序

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C19 | 运行时必须的是 Segment；破坏 Section Header 后 IDA 认不出节，程序仍能跑，因为加载器只看 Segment Header。quote: 它只看 Segment Header | s1 ./softard-20260429-01.md:72 | source-report | 来源对加固的描述 | 上一行写 IDA 解析不了 Section |
| C20 | strip 删掉符号表和 Section Header，运行不受影响。quote: 程序运行不受任何影响 | s1 ./softard-20260429-01.md:74 | source-report | strip 命令的来源解释 | 未对文件做 strip 对照 |
| C21 | 散文把 32/64 位说成看 Machine 字段。quote: 不确定是 32 位还是 64 位时，看这个字段就行 | s1 ./softard-20260429-01.md:93 | source-report | 紧挨头字段表的那句 | 与 C7 的 Class 字段不一致，本卡两句都保留，不把散文改写成表 |
| C22 | 重定位完成后 GNU_RELRO 使 .got 只读，直接写 GOT 做钩子会触发故障。quote: linker 重定位完成后 .got 变成只读 | s1 ./softard-20260429-01.md:126 | source-report | 来源的 RELRO 说明 | 下一行的改权限和改时机不进入本卡 |
| C23 | 静态注册的名字形状是 Java_包名_类名_方法名。quote: Java_包名_类名_方法名 | s1 ./softard-20260429-01.md:184 | source-report | 来源的静态注册规则 | 包名里的点换下划线在后文 |
| C24 | 静态入口是在 IDA 或 nm -D 里搜 Java_ 前缀。quote: 输出里搜 | s1 ./softard-20260429-01.md:191 | source-report | 未 strip 的导出 | 前缀在同一行 |
| C25 | 动态入口是 JNI_OnLoad，再找 RegisterNatives，第三个参数是 methods 数组，再读函数指针。quote: 跟进第三个参数 | s1 ./softard-20260429-01.md:204 | source-report | 来源写的追踪顺序 | 不包含某个 SO 的注册表地址 |
| C26 | 对照表把动态注册的定位写成先找 JNI_OnLoad 再追函数指针。quote: 再追函数指针 | s1 ./softard-20260429-01.md:210 | source-report | 该对照表 | 与 C25 同一顺序 |
| C27 | 来源写多数核心逻辑用动态注册；加固会混淆 JNI_OnLoad，使 IDA 找不到 RegisterNatives。quote: 核心逻辑都用动态注册 | s1 ./softard-20260429-01.md:214 | source-report | 来源的经验句 | 不是统计 |
| C28 | strip 之后 nm 看不到符号，来源改为 readelf -l 确认结构，再用 IDA 从序言、尾声和交叉引用重建。quote: prologue/epilogue 特征和交叉引用重建逻辑 | s1 ./softard-20260429-01.md:229 | source-report | 无符号 SO | 上一行写明靠 readelf -l；本卡不把命令扩成流程 |

## 验证与限制

查询 android-so-elf 的 parameters、decision-flow、interfaces 均无命中。ARM64 汇编阅读卡的目标是寄存器和 JNI 参数寄存器，不是 ELF 头。另一张 signKey 卡的 target 是 unknown，它的 interfaces 只覆盖那个应用的动态注册边界，查询 android-so-elf 不会命中它，本卡也不复制那个应用的方法名。Machine 字段判断模拟器只有一句，来源写不展开，保持未知。没有本地运行证据。
