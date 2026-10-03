---
schema_version: 2
id: grok-mobile-app-reverse-softard-20251231-01
document_type: reference
original_date: "2025-12-31"
archived_date: "2026-10-02"
scope:
  targets: [dex-string-id-fault]
  client: android
  version: dex 035 header in the tombstone; parser build unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./softard-20251231-01.md#359b0"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录这次崩溃里寄存器和 string_ids_off 的对应关系。未打开崩溃进程，不收录整段寄存器和头校验字节。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 四条排查方向和最终归到 string_ids_off 的结论都是来源陈述。偏移为何变成该值，来源明确留空。
relations:
  - type: derived_from
    target: "./softard-20251231-01.md#359b0"
tags: [dex, string-ids, tombstone]
---

# DEX string id 崩溃的寄存器对齐

这张卡只回答：来源如何把 359b0 的加载指令对齐到 `string_ids[id].string_data_off`，以及它如何用墓碑里的四个寄存器方向把崩溃收束到异常的 `string_ids_off`。通用 ARM64 寄存器宽度不在本卡，已有汇编阅读卡覆盖。不提供构造异常 DEX 的做法。

<a id="parameters"></a>
## 指令、头字段和这次的偏移

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 崩溃点被标在 359b0。quote: 这里崩，359b0 | s1 ./softard-20251231-01.md:50 | source-report | 来源注释的这一条加载 | 未在 IDA 里核对地址 |
| C2 | 该加载被写成读取 string_ids[id] 的 string_data_off。quote: string_ids[id].string_data_off | s1 ./softard-20251231-01.md:50 | source-report | 来源给出的 C 对照 | 伪代码是来源手写的对应，不是反编译器原文 |
| C3 | X8 对 string_ids 基址。quote: X8->string_ids | s1 ./softard-20251231-01.md:54 | source-report | 这次崩溃的寄存器注记 | 不是通用调用约定 |
| C4 | X21 对字符串 id。quote: X21->id | s1 ./softard-20251231-01.md:55 | source-report | 同上 | 只此函数 |
| C5 | 左移 2 被解释成 DexStringId 为 4 字节。quote: DexStringId结构体是4字节 | s1 ./softard-20251231-01.md:56 | source-report | 来源对 LSL #2 的读法 | 未单列结构体定义 |
| C6 | 索引项再取出 string_data_off。quote: string_data_off | s1 ./softard-20251231-01.md:58 | source-report | LDR W8 的目标字段 | 与 C2 同一对应 |
| C7 | 头里 string_ids_off 的注释是字符串索引偏移。quote: 字符串索引偏移 | s1 ./softard-20251231-01.md:87 | source-report | 来源粘贴的 DexHeader | 整份结构体是公开布局的复述，本卡只钉这个字段 |
| C8 | 墓碑按字打印的顺序被来源称为是反的，直接按打印序解析会错。quote: 日志打印的内存信息顺序是反的 | s1 ./softard-20251231-01.md:89 | source-report | 这份日志的显示方式 | 未附原始 tombstone 文件 |
| C9 | 手工解析把 string_ids_off 读成 0x40000070，并称为异常大。quote: 0x40000070 | s1 ./softard-20251231-01.md:95 | source-report | 这次 dex 035 头 | 不收录同段里的签名字节 |
| C10 | 来源用等式把 X8 收成 X20 加上该偏移。quote: 0000007b84ac5870 = 0000007b44ac5800 + 40000070 | s1 ./softard-20251231-01.md:97 | source-report | 这次寄存器值 | 算术是来源自己的对齐，本轮未重算内存 |

<a id="decision-flow"></a>
## 四条方向里哪一条成立

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C11 | id 是否越界看 X21。quote: 数组越界，就看X21 | s1 ./softard-20251231-01.md:62 | source-report | 来源列出的第一支 | 方向，不是脚本 |
| C12 | string_ids 基址看 X8。quote: string_ids基址不对看X8 | s1 ./softard-20251231-01.md:63 | source-report | 第二支 | 同上 |
| C13 | string_data_off 看 W8。quote: string_data_off不对，看W8 | s1 ./softard-20251231-01.md:64 | source-report | 第三支 | 同上 |
| C14 | dex 基址看 X20。quote: dex_base不对，看X20 | s1 ./softard-20251231-01.md:65 | source-report | 第四支 | 同上 |
| C15 | 这次 X21 为 0，来源判定 id 合法。quote: 说明id是合法的 | s1 ./softard-20251231-01.md:74 | source-report | 这份日志 | 0 只说明不是负数或垃圾大数，边界上限来源未算 |
| C16 | X8 附近内存为空，来源把 SEGV_ACCERR 归到这块不可访问。quote: 这是引起SEGV_ACCERR的原因 | s1 ./softard-20251231-01.md:75 | source-report | 这次 fault | 未看页表 |
| C17 | X20 处有 dex035，来源把它当作 dex 基址。quote: 就是dex的基址 | s1 ./softard-20251231-01.md:76 | source-report | 这份 memory near x20 | magic 只支持“像 dex 头” |
| C18 | 来源的收束是 string_ids_off 异常导致崩溃。quote: string_ids_off异常引起的crash | s1 ./softard-20251231-01.md:98 | source-report | 这次样本 | 下一句写明异常从何而来并未解释 |

## 验证与限制

查询 dex-string-id-fault 的 parameters 和 decision-flow 没有命中。ARM64 汇编阅读卡的目标是寄存器宽度和 JNI 参数寄存器，不包含 DexHeader 的 string_ids_off，因此不并入那张卡。X/W 宽度和 AAPCS64 在来源开头有一段复述，本卡不重复。偏移为何是 0x40000070，来源交给架构侧，本卡保持未知。没有本地运行证据。
