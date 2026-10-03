---
schema_version: 2
id: mobile-app-reverse-paopao-native-function-location
document_type: reference
original_date: '2026-06-18'
archived_date: '2026-10-01'
scope:
  targets: [unknown]
  client: Android/Frida Native instrumentation
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./paopao-android-reverse-compilation/paopao-20260618-01.md#九封装多策略逐级兜底框架
    basis: source-report
  - id: s2
    ref: ./paopao-android-reverse-compilation/paopao-20260618-01.md#五字符串交叉引用定位
    basis: source-report
  - id: s3
    ref: ./paopao-android-reverse-compilation/paopao-20260618-01.md#六调用点交叉引用按它调用了谁定位
    basis: source-report
  - id: s4
    ref: ./paopao-android-reverse-compilation/paopao-20260618-01.md#八arm32--thumb-的差异
    basis: source-report
  - id: s5
    ref: ./paopao-android-reverse-compilation/paopao-20260618-01.md#十真机实测在真机-libcso-上跑通整条链路
    basis: source-report
modules:
  - name: decision-flow
    anchor: locator-method-selection
    sources: [s1, s2, s3, s4]
    basis: source-report
    limits: 只整理来源文章提出的 Android/Frida Native 函数定位线索与边界；未运行代码或针对目标 SO 复验，不能据此保证跨版本定位成功。
  - name: validation
    anchor: reported-validation-boundary
    sources: [s5]
    basis: source-report
    limits: 仅记录来源作者报告的 libc 样例及其自述边界；本轮未执行验证，设备型号记录有冲突，缺原始日志和二进制。
relations:
  - type: supplements
    target: kb:mobile-app-reverse-anti-crawler-frida-hook-selection#frida-hook-technique-selection
tags: [frida, native, function-location, arm64, arm32]
---

# Android Native 未导出函数定位参考

本卡整理来源文章提出的 Native 函数定位线索，重点是无导出名时如何避免只依赖固定位置。它补充一般 Frida Hook 技巧选择卡中“导出函数或基址加偏移”的概述，聚焦符号、交叉引用与架构边界；不覆盖 Java 对象操作，也不构成可直接运行的通用脚本或流程。文中结论均为 `source-report`。

<a id="locator-method-selection"></a>
## 定位线索与适用边界

| 线索 | 来源文章描述 | 适用边界 |
|---|---|---|
| 导出符号与局部符号表 | 已知导出名时可先查导出；SO 未 strip 且保留 `.symtab` 时，来源称 `Module.enumerateSymbols()` 也可能列出局部函数名。 | strip 后局部符号可能不可用；来源没有提供当前目标 SO 的符号检查结果。 |
| 字符串交叉引用 | 从独特字符串定位引用指令，再判断所属函数。来源的 ARM64 示例覆盖 `ADRP + ADD` 直接地址与 `ADRP + LDR` 指针槽两种形式。 | 通用字符串可能有多处引用；明文可能不在映像中。函数入口回溯属于启发式，优先用可用的符号范围核对；无法确认时保留引用点人工复核。 |
| 导入调用交叉引用 | 运行时 hook 被调用的导入函数，从调用返回地址识别目标模块内的调用方；静态路线则解码调用点。 | 运行时路线须触发相关调用。静态路线需区分本模块 PLT stub 与导入函数真实实现地址，并按来源所述从 GOT 槽关系解析 stub；来源指出 `-fno-plt` 可能没有独立 stub。 |
| 字节特征码 | 来源建议对带相对或绝对位置编码的指令放宽匹配，再以剩余字节定位。 | 编译器、寄存器分配、内联、PGO/LTO 等变化可能重写函数体；需逐目标检查命中唯一性，不能视作稳定标识。 |
| 相对锚点与固定偏移 | 来源把已知导出锚点加相对距离、硬编码偏移列为后置线索。 | 函数间插入或删除代码会改变距离；固定偏移只反映某次构建位置，来源将其视为脆弱兜底。 |

来源文章给出的框架是按可用线索逐层尝试，并在输出中标明命中途径。其顺序和“抗变化”评价属于作者建议，不是跨版本基准数据。本卡不保留来源图像 alt 文本中缺少方法依据的百分比。

### 架构边界

来源示例以 ARM64 解码为主。其回溯讨论 `BTI`、`PACIASP` / `PACIBSP` 与 `STP` 等序言形态，同时提醒叶子函数可能没有典型序言、最近匹配项可能属于相邻函数，且读到未映射地址时应停止并回到引用点核对。

ARM32 / Thumb 不能直接套用 ARM64 的 `ADRP` 与固定 4 字节指令遍历。来源分别提到 `MOVW/MOVT` 或字面量池取址、不同的函数序言、Thumb 地址最低位处理以及 16/32 位混合指令宽度；其内容是差异说明，不是完整 ARM32 解码实现。

<a id="reported-validation-boundary"></a>
## 结论与证据边界

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源建议以多种内容线索分层定位，并把硬编码偏移放在后置兜底。 | s1，物理行 490–557、594–619 | source-report | 来源文章的 Android/Frida 示例 | 排序是作者建议；没有跨版本成功率数据。 |
| C2 | ARM64 字符串 xref 示例区分 `ADRP + ADD` 直接引用和 `ADRP + LDR` 指针槽引用，再从引用位置尝试回溯函数入口。 | s2，物理行 183–353 | source-report | 来源文章列出的 ARM64 指令形式 | `ADR`、字面量池等变体未覆盖；回溯是启发式。 |
| C3 | 导入调用定位分运行时返回地址观察与静态调用点分析；静态分析应匹配调用方实际跳转的本地 PLT stub，而非直接拿导入实现地址比较。 | s3，物理行 361–460 | source-report | 来源文章的 ARM64 PLT/GOT 示例 | 示例未在本轮针对任何目标 SO 执行；`-fno-plt` 路径被来源列为不适用情形。 |
| C4 | ARM32 / Thumb 的取址、序言和指令宽度与 ARM64 不同，不能复用同一套解码假设。 | s4，物理行 476–488 | source-report | 来源文章的架构差异说明 | 没有完整实现或运行验证。 |
| C5 | 来源报告其 libc 字符串 xref 入口与符号表名称匹配；作者将验证范围限制在无 PAC/BTI 的普通 `STP` 序言。 | s5，物理行 560–581 | source-report | 单个来源报告的 libc 样例 | 设备型号在来源中分别写为 Pixel 6 Pro 与 Pixel 6；无原始日志/二进制，本轮未复验，不能推广到 PAC/BTI 或其他 App。 |

### 来源完整性与未决项

- 来源文章的 5 处图像只保留了未闭合的 alt 文本，没有可读取的图片目标；其中部分说明不完整。本卡不把图中可能的信息当作证据，也没有重建图示。
- 来源只提供作者和公众号归属，未提供可公开定位的原文 URL；本卡通过同目录归档文章和具体章节锚点追溯，依据上限为 `source-report`。
- 本轮没有执行文中代码，也没有检查目标 SO、设备或运行日志。函数回溯、静态 BL 解析和跨版本稳定性均未由本轮验证。
- 来源记载的 Pixel 6 Pro / Pixel 6 型号不一致；本卡不选择其中一个作为真值，不据此设定目标或版本范围。
- 示例中的真实偏移、运行时地址、设备标识及凭据类值不在本卡复述范围内。
