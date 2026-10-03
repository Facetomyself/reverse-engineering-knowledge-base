---
schema_version: 2
id: koohai-ida-md5-findhash
document_type: reference
original_date: '2024-06-23'
archived_date: '2026-09-06'
scope:
  targets: [ida-md5]
  client: native
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./koohai-20240623-01.md#md5在ida中的识别及使用方法"
    basis: source-report
  - id: s2
    ref: "./koohai-20240623-01.md#数值类型转换"
    basis: source-report
  - id: s3
    ref: "./koohai-20240623-01.md#find-hash-的使用"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2]
    basis: source-report
    limits: 只保留作者用来认 MD5 的初值和填充字节。这些是公开算法常量，不是某一份样本的摘要，也没有和已知输入对过。
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2, s3]
    basis: source-report
    limits: IDA 操作和 findhash 0.1 的 32 位限制按作者日志整理。插件输出的地址属于作者自己的 revdemo，不外推到别的 SO。
  - name: decision-flow
    anchor: decision-flow
    sources: [s2, s3]
    basis: source-report
    limits: Final 的填充分支、魔改初值仍被标出，以及“变换函数第二个参数是明文”，都是作者读反编译后的判断。后半脚本缺逗号，本卡不收录脚本正文。
relations:
  - type: derived_from
    target: "./koohai-20240623-01.md#md5在ida中的识别及使用方法"
tags: [ida-md5, findhash, source-report]
---

# IDA 里认出 MD5 以及 findhash 的 32 位边界

这张卡只回答：作者在 IDA 里用哪些立即数和数据展示认出 MD5，findhash 漏掉什么，以及日志里的偏移怎么跳回去。依据停在 source-report。target `md5`、`ida-md5`、`findhash` 都没有同模块卡片。`md5-1038` 是另一张 Web 参数卡，不覆盖这里的 IDA 识别。

<a id="parameters"></a>
## 识别用的初值和填充

作者给出的 `MD5Init` 把前两个字清零，后面四个字是十进制初值。同一个初值也可以用立即数 `0x67452301` 去搜。一轮里的 `__ROR4__` 带着负的立即数，作者用反转符号看。填充的第一个字节是 `0x80`。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 初值写成 “result[2] = 1732584193” 和 “result[3] = -271733879”。 | s1 ./koohai-20240623-01.md:48-50 | source-report | ida-md5 | 只引用了前两个状态字 |
| C2 | “搜索立即数 0x67452301; 这是上面的init中的state一个数”。 | s1 ./koohai-20240623-01.md:61 | source-report | ida-md5 | 菜单名在原文里写成了 imdate-value |
| C3 | 一轮是 “__ROR4__” 加 “- 0x28955B88”，并用 “invert  sign” 改负号。 | s1 ./koohai-20240623-01.md:66-70 | source-report | ida-md5 | 没有把 64 步常量列全 |
| C4 | `PADDING` 按 D 转成 DCB 后，第一个字节是 `0x80`。 | s2 ./koohai-20240623-01.md:134 | source-report | ida-md5 | 样本数据地址是 0x6000，不代表别的 SO |

<a id="interfaces"></a>
## IDA 展示和 findhash

按 H 把十进制看成十六进制。数据项按 D 会在 DCD 和 DCB 之间转，用来看填充。findhash 0.1 放到 IDA 的 plugins 目录后运行。作者写明这个脚本只考虑 32 位 SO 的反编译，64 位未适配。它仍把改过初值的 `MD5InitMagic` 标成疑似哈希。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 先右键转为 hex，或者按 H。 | s1 ./koohai-20240623-01.md:37 | source-report | ida-md5 | 没有 IDA 版本 |
| C6 | 跳到 padding 后按 D，DCB 即可看到 `0x80`；作者区分 thumb 与 arm 的显示宽度。 | s2 ./koohai-20240623-01.md:154 | source-report | ida-md5 | 原文把 padding 写成了 paddind |
| C7 | findhash 只考虑 32 位 SO 的反编译代码，64 位未适配。 | s3 ./koohai-20240623-01.md:178 | source-report | ida-md5 | 作者的插件日志，不是插件源码审计 |
| C8 | `MD5InitMagic` 被标成“包含初始化魔数的代码”。 | s3 ./koohai-20240623-01.md:188 | source-report | ida-md5 | 地址 `0x20634` 只属于这次 revdemo |

<a id="decision-flow"></a>
## Final、参数和回到 IDA

`MD5Final` 被读成：用 `(*a1 >> 3) & 0x3F` 算长度，大于 `0x37` 时填充长度取 `120 - v4`，否则取 `56 - v4`，再压入 padding 和 8 字节长度。作者认为 transform 的第二个参数是 64 字节明文。日志里拿到偏移后，在 IDA 按 G 跳到相对地址。trace 插件只收录指令数大于 10 的函数，thumb 模式把地址加 1。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C9 | “这是识别的final   ，计算长度，压入padding放入长度 拼接”。 | s2 ./koohai-20240623-01.md:108 | source-report | ida-md5 | 长度分支没有用已知输入核对 |
| C10 | “transfrom 第二个参数 的64个字节” 在下一行被说成 “就是明文”。 | s3 ./koohai-20240623-01.md:269-270 | source-report | ida-md5 | 原文写成 transfrom 和铭文，没有内存摘录 |
| C11 | “大于10行的函数 才记录”，并且 “如果是thumb模式，地址+1”。 | s3 ./koohai-20240623-01.md:419-421 | source-report | ida-md5 | 这是地址名单的过滤，不是 MD5 判定 |
| C12 | 从日志里的偏移，例如 `0x1eb98`，在 IDA 中按 G 跳到对应地址。 | s3 ./koohai-20240623-01.md:503 | source-report | ida-md5 | 该偏移只对应这次日志 |

## 验证与限制

插件日志里的函数地址、Java 符号和本机脚本路径都是 revdemo 这一次的输出，不能当成其他 SO 的定位。后半把地址列表塞回 hook 时缺逗号，脚本本身不闭合。没有一份已知输入和摘要的对照，64 位未适配也只是一句限制，不是失败出口。因此不建流程。
