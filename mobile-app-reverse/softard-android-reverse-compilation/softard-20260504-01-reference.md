---
schema_version: 2
id: softard-20260504-dalvik-smali-registers
document_type: reference
original_date: "2026-05-04"
archived_date: "2026-10-02"
scope:
  targets: [dalvik-smali]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./softard-20260504-01.md#类型描述符"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录来源写下的寄存器编号和类型描述符。不包含把检测结果改成恒定值的改写。
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 四种 invoke、紧跟的 move-result，以及字段读写前缀，都是来源的读法。未用 apktool 回包。
relations:
  - type: derived_from
    target: "./softard-20260504-01.md#类型描述符"
tags: [smali, dalvik, dex]
---

# Dalvik Smali 的寄存器和调用形式

这张卡只回答一个检索问题：来源如何用寄存器、类型描述符和四种 invoke 把 Smali 读回 Java 方法。范围是这篇归档里的语法说明。检测结果改写、条件反转和提前返回不进入本卡。

<a id="parameters"></a>
## 寄存器和类型描述符

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | Smali 被写成 DEX 字节码的文本形式，和机器码与汇编的关系一样，可以互相转换。quote: Smali 就是 DEX | s1 ./softard-20260504-01.md:59 | source-report | 来源对 Smali 是什么的定义 | 未做字节码往返 |
| C2 | 局部寄存器写成 v，参数寄存器写成 p。quote: 局部变量寄存器 | s1 ./softard-20260504-01.md:79 | source-report | 来源的命名 | 同一组物理寄存器见 C5 |
| C3 | 实例方法的 p0 是 this；静态方法没有 this，p0 是第一个参数。quote: 实例方法的 p0 是 this | s1 ./softard-20260504-01.md:81 | source-report | 来源对 p0 的区分 | 未对具体方法计数 |
| C4 | .registers 声明的是局部和参数加在一起的总数。quote: 局部 + 参数加在一起算 | s1 ./softard-20260504-01.md:87 | source-report | 来源对这条指令的口径 | 示例数字不是固定值 |
| C5 | 来源写新增局部变量却不增大 .registers 时，apktool 回包后运行会报错。quote: apktool 回包后运行时会报错 | s1 ./softard-20260504-01.md:89 | source-report | 来源指出的常见失误 | 本次未回包 |
| C6 | p 和 v 被写成同一组寄存器的两种编号，p0 对应 registers 数减去参数数。quote: 本质上是同一组寄存器 | s1 ./softard-20260504-01.md:92 | source-report | 来源的编号换算 | 换算公式在下一行续完，未逐条验证 |
| C7 | (Ljava/lang/String;I)Z 被翻译成 boolean fun(String, int)。quote: (Ljava/lang/String;I)Z | s1 ./softard-20260504-01.md:103 | source-report | 来源给的一条方法描述符 | 只是例子 |
| C8 | 基本类型被写成单字母大写，引用类型用 L...; 。quote: 基本类型全是单字母大写 | s1 ./softard-20260504-01.md:106 | source-report | 来源的描述符规律 | 数组前缀在相邻代码行 |
| C9 | boolean 的描述符被写成 Z，并明确 B 是 byte。quote: B 是 byte | s1 ./softard-20260504-01.md:107 | source-report | 来源点名的易混项 | 未查其他类型 |
| C10 | long 和 double 各占两个寄存器槽。quote: 占两个槽位 | s1 ./softard-20260504-01.md:109 | source-report | 来源对宽类型的说法 | 未看实际寄存器分配 |

<a id="interfaces"></a>
## 调用和字段读写

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C11 | 静态方法用 invoke-static，构造或 private 用 invoke-direct，接口方法用 invoke-interface。quote: 构造或 private → direct | s1 ./softard-20260504-01.md:123 | source-report | 来源的选用口诀 | 接口一词续到下一行 |
| C12 | 其余实例方法用 invoke-virtual。quote: 其余实例方法 → virtual | s1 ./softard-20260504-01.md:124 | source-report | 来源口诀的最后一档 | 口诀，不是字节码规范摘录 |
| C13 | 写了 move-result 就必须紧跟 invoke，中间不能有别的指令；不需要返回值可以不写。quote: 就必须紧跟在 invoke 后面 | s1 ./softard-20260504-01.md:131 | source-report | 来源对回包约束的说法 | 未回包验证 |
| C14 | i 开头是实例字段，s 开头是静态字段，get 读、put 写。quote: 实例字段读 | s1 ./softard-20260504-01.md:137 | source-report | 来源对 iget/iput/sget/sput 的拼法 | 示例类名是虚构的 |
| C15 | 示例里 .registers 3 被拆成 this、一个 String 参数和唯一的局部寄存器 v0。quote: v0 是唯一的局部寄存器 | s1 ./softard-20260504-01.md:172 | source-report | 这一段示例的计数 | 不记录示例里的字符串字面量 |

## 验证与限制

`kb_catalog.py query` 对 dalvik-smali 和 smali 的 parameters、interfaces 都是 0。把检测结果改成恒 false、把 if-eqz 改成 if-nez，以及在方法开头直接返回的句子都在原文里，但不进入本卡。练习题没有答案。没有 apktool 回包证据。
