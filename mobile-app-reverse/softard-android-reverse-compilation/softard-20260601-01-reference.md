---
schema_version: 2
id: android-so-obfuscation-countermeasure-order-reference
document_type: reference
original_date: '2026-06-01'
archived_date: '2026-10-02'
scope:
  targets: [Android SO obfuscation countermeasures]
  client: Android
  version: IDA tool-order note; plugin and script versions unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./softard-20260601-01.md#一基本块调度"
    basis: source-report
  - id: s2
    ref: "./softard-20260601-01.md#二分裂基本块"
    basis: source-report
  - id: s3
    ref: "./softard-20260601-01.md#三控制流间接化"
    basis: source-report
  - id: s4
    ref: "./softard-20260601-01.md#四各手法对抗工具汇总"
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s2, s3, s4]
    basis: source-report
    limits: 只整理来源给出的现象、工具名和顺序。没有版本，没有某个 SO 的对照，本轮未运行工具。命令里的函数地址是占位符。
relations:
  - type: derived_from
    target: "./softard-20260601-01.md#某厂安全研发的逆向笔记111更多混淆手法与对抗工具"
tags: [ollvm, d-810, deflat, ida]
---

# Android SO 混淆：三种进阶手法和工具顺序

这张卡回答：IDA 里看到基本块被打乱、切碎或间接跳转时，来源先用什么、后用什么。来源是 [笔记（11.1）](./softard-20260601-01.md#四各手法对抗工具汇总)。前篇的调度器、不透明谓词和示意 state 不在这里重复。

目标 `Android SO obfuscation countermeasures` 的 decision-flow 和 parameters 查询都没有命中。没有工具版本，没有「改完之后应看到什么」的验收，也没有把缺文件、插件失败写成独立前提，所以不是 procedure。依据保持 source-report。

<a id="decision-flow"></a>
## 先认现象，再选工具

基本块调度（Block Reordering）把块在内存里随机重排，块尾用无条件跳转接回逻辑顺序。文本视图会和执行顺序脱节；来源称切换到图形视图之后影响基本消失。对抗就是直接用图形视图，不看文本视图。

分裂是把一个块从中间切开，插入无条件跳转。块数变多，而且通常和 CFF 叠加。手工分析时遇到只有无条件跳转的块就直接跳过；自动合并留给 D-810。

控制流间接化把直接跳转换成从表里取地址再 `br x8`。IDA 静态分析看不出目标，图形视图的边会断。对抗是运行时观察 x8 的实际值，或者静态分析 target_table，手工把边补上。

工具表把前面的核心手法也排进同一顺序：CFF 用 D-810，光标放在函数里按 Ctrl+Shift+D；另一条是 `python deflat.py -f target.so --addr 0x函数地址`。BCF 同样交给 D-810，或用 angr + Z3 识别恒真、恒假谓词。字符串加密用 Frida hook 解密函数，运行时打印明文。分裂基本块用 D-810 自动合并碎片块。间接跳转用 Frida 或手工把目标记下来。

来源的实际顺序是：先跑 D-810，覆盖 CFF、BCF 和分裂；CFG 若还正常，就回到系列里的四步方法；关键字符串搜不到就 Frida；间接跳转让边断了就动态补全；以上都不奏效，就当成叠加了自定义混淆，需要针对性分析。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 调度对图形视图影响基本消失 | `切换到图形视图之后影响基本消失` | s1 ./softard-20260601-01.md:49 | source-report | 没有样例函数 |
| C2 | 调度的对抗是换视图 | `直接用图形视图，不看文本视图` | s1 ./softard-20260601-01.md:51 | source-report | 不处理间接跳转 |
| C3 | 只有无条件跳转的块可以跳过 | `只有无条件跳转的块就直接跳过` | s2 ./softard-20260601-01.md:64 | source-report | 自动合并见工具表 |
| C4 | 断边的指令形态是 br x8 | `br x8` | s3 ./softard-20260601-01.md:75 | source-report | 只是来源的例子 |
| C5 | 补边看运行时的 x8 | `运行时观察 x8 的实际值` | s3 ./softard-20260601-01.md:77 | source-report | 同句还有 target_table |
| C6 | D-810 的快捷键 | `Ctrl+Shift+D` | s4 ./softard-20260601-01.md:84 | source-report | 无插件版本 |
| C7 | deflat.py 的命令形 | `python deflat.py -f target.so --addr 0x函数地址` | s4 ./softard-20260601-01.md:85 | source-report | 地址是占位符 |
| C8 | BCF 的另一条是 angr + Z3 | `angr + Z3` | s4 ./softard-20260601-01.md:87 | source-report | 没有脚本 |
| C9 | 字符串用 Frida 打解密函数 | `hook 解密函数，运行时打印明文` | s4 ./softard-20260601-01.md:88 | source-report | 没有函数名 |
| C10 | 通用顺序走不通就停通用手法 | `以上都不奏效` | s4 ./softard-20260601-01.md:96 | source-report | 四步方法本篇没有定义 |

## 验证与限制

缺的三段是：要先装好哪些版本才算前提成立，做完后哪张 CFG 或哪段明文算输出，以及怎样算验收。第五步只说明通用表不够时要换路线，不能单独把全文升成 procedure。本轮没有运行 D-810、deflat.py、angr 或 Frida。
