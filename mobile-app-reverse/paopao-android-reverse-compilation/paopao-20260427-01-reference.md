---
schema_version: 2
id: unidbg-trace-three-layers-reference
document_type: reference
original_date: '2026-04-27'
archived_date: '2026-10-02'
scope:
  targets:
    - unidbg trace
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260427-01.md#第一层指令级-trace"
    basis: source-report
  - id: s2
    ref: "./paopao-20260427-01.md#第二层函数级-trace"
    basis: source-report
  - id: s4
    ref: "./paopao-20260427-01.md#第三层内存级-trace"
    basis: source-report
  - id: s5
    ref: "./paopao-20260427-01.md#2-在-trace-中搜索关键常量"
    basis: source-report
  - id: s6
    ref: "./paopao-20260427-01.md#backend-限制只有-unicorn-系列支持-trace"
    basis: source-report
  - id: s7
    ref: "./paopao-20260427-01.md#两种展示扁平-vs-树形"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2, s4, s7]
    basis: source-report
    limits: API 落点只复述来源。未对照 unidbg 仓库版本，示例里的 libxxx 与地址不是某次运行记录。
  - name: parameters
    anchor: parameters
    sources: [s1, s4, s5, s6]
    basis: source-report
    limits: 行字段和常量检索键来自来源的示例与常量表。nzcv 解码、字节序和吞吐数字都未在本地 trace 上复核。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s2, s6, s7]
    basis: source-report
    limits: 分层顺序和 Backend 取舍是来源建议。Diff 四步没有验收条件，不把脚本当流程。
relations:
  - type: derived_from
    target: "./paopao-20260427-01.md#第一层指令级-trace"
tags:
  - unidbg
  - trace
  - source-report
---

# Unidbg Trace 的三层接口和读法

这张卡只回答：来源把 Unidbg 的 Trace 分成哪三层、各挂在哪个接口、一行指令 trace 怎么读，以及为什么必须留在 Unicorn 系 Backend。不收录 listener 全文，也不把 diff 或染色脚本当成已验收流程。签名数组为空和 HashFinder 扫描不在这张卡里。

来源没有可公开定位的原文 URL，版本号也没有写。下面的 API 和示例输出都是作者写下的形态。

<a id="interfaces"></a>
## 三层接口落点

指令级在 `Emulator` 上。来源先给无参全量，再给地址窗：

> emulator.traceCode();

> emulator.traceCode().setRedirect(redirect);

函数级不在 `Emulator` 上。来源写 `traceFunctionCall` 在 `Debugger` 上，要先 `emulator.attach()`，再把 `FunctionCallListener` 的匿名子类交给它。`FunctionCallListener` 被写成 abstract class，需要覆盖 `onCall` 和 `postCall`。符号用 `findClosestSymbolByAddress`，第二个参数 `false` 表示未命中时返回 null，不抛异常。

内存级被写成和 `traceCode` 对称的 `traceRead` / `traceWrite`：无参全量、`begin/end` 地址窗、再加 listener。来源给的窗口例子是 `emulator.traceRead(0x10000L, 0x10100L).setRedirect(traceStream)`，写侧同样。

调用树不是内置能力。原句是「unidbg 没有内置 call-tree API」。缩进靠自写 listener 在 `onCall` / `postCall` 里加减 depth。来源同时写，裸 `BR`、`setjmp/longjmp` 或尾调用会让配对失真。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 指令级入口是 `emulator.traceCode()`，输出用 `setRedirect` 离开 stdout | s1，`paopao-20260427-01.md:94` 与 `:168` | source-report | unidbg trace | 未对照仓库；无参形式来源明确不推荐全量 |
| C2 | 函数级入口名是 `traceFunctionCall`，来源写它不在 Emulator 接口上，而在 Debugger 接口上 | s2，`:182` | source-report | unidbg trace | 只说明注册点，不收录 listener 实现 |
| C3 | `traceRead` 与 `traceWrite` 和 `traceCode` 对称，各有无参、地址窗和 listener | s4，`:354-360` | source-report | unidbg trace | 默认格式只保留来源描述的 PC/LR 字段名 |

<a id="parameters"></a>
## 行字段和常量检索键

来源把一行指令 trace 拆成五列：时间戳、Unicorn 绝对虚拟地址、`模块名 + 模块内偏移`、Capstone 助记符、本条指令读过或写过的寄存器。没变化的寄存器不打。模块内偏移被写成可以拿去对 IDA。

比较指令后面会出现标志寄存器。来源对示例 `nzcv=0x60000000` 的读法是：`6` 的低四位 `0110` 表示 `Z=1, C=1, N=0, V=0`，随后的 `b.ne` 因 `Z=1` 不跳。这是对那一行示例的解释，不是通用 NZCV 手册摘录。

内存 trace 的默认行被写成 `{date} Memory READ/WRITE at 0x{addr}, data size = ..., data value = ..., PC=..., LR=...`。来源认为这比指令 trace 少一层无关运算，但全量 `traceRead()` 会把栈上局部访问也打出来。

常量检索键只保留来源表里的起始形式，不把整表当算法识别证明：

| 算法 | 来源写的检索起点 |
|---|---|
| AES | S-Box 起始字节 `63 7C 77 7B F2 6B 6F C5` |
| SHA-256 | 初始值 `6A09E667 BB67AE85 3C6EF372 A54FF53A` |
| SHA-1 | 初始值 `67452301 EFCDAB89` |
| MD5 | 初始值 `67452301 EFCDAB89 98BADCFE 10325476` |
| ChaCha20 | `expand 32-byte k` |
| Blowfish | P-box 起始 `243F6A88 85A308D3` |

来源额外写了两个坑：ARM64 小端下内存序会把 `0x6a09e667` 倒成 `67 e6 09 6a`；编译器可能把同一个立即数拆成 `movz` / `movk` 半字，整常数 grep 会落空。

吞吐表被来源标成经验值：Unicorn2 空跑约 50M 指令每秒，开指令级 Trace 降到约 5M，Dynarmic 空跑约 500M 以上且不支持 Trace。数量级，不是测量记录。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 示例比较指令后的标志是 `nzcv=0x60000000`，来源把它读成相等且 `b.ne` 不跳 | s1，`:123` | source-report | 该示例行 | 未用真实 trace 复核 NZCV |
| C5 | AES 检索起点被写成 S-Box 起始字节 `63 7C 77 7B F2 6B 6F C5` | s5，`:454` | source-report | 来源列出的标准常量 | 不是某样本的命中日志 |
| C6 | 开指令级 Trace 后，来源把 Unicorn2 吞吐写成降到 ~5M，Dynarmic 列为不支持 | s6，`:567` | source-report | 来源的经验表 | 未复测 |

<a id="decision-flow"></a>
## 先选层，再决定能不能开

来源的顺序是：函数级看调用骨架，指令级缩到关键函数大约几百字节到 `0x800`，内存级再圈 S-Box 或密钥缓冲。全量 `traceCode()` 被写成会打出 5 万到 50 万行、100 MB 以上文本。输出要重定向到文件。

Backend 门槛的原句是「Trace 功能只在 Unicorn / Unicorn2 backend 上可用」。Dynarmic 被写成去掉了指令钩子，内存级同样只在 Unicorn 系可用。分析期用 Unicorn2，量产期再切回 Dynarmic 并不开 Trace。来源给的经验判据是三条同时成立才值得开指令级：输入只改 1 字节、函数体不超过 10 万条指令、Trace 范围能限到 100 字节以内；有一条不成立就先退回函数级，再用人肉单步。

树形和扁平的分界：首次看大 SO 用树；样本有 inline、跳转表或自定义栈时用扁平，因为 depth 会失真。

Diff 两次指令 trace、给 IDA block 上色、统计分支 taken，来源都写成读 trace 的办法。四步 diff 没有写出通过条件和失败时停止哪条结论，所以不升成流程。固定随机被指向系列的另一篇，本篇没有那个操作的步骤。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | Trace 只在 Unicorn / Unicorn2 backend 上可用 | s6，`:545` | source-report | unidbg trace | 未打开 DynarmicBackend 源码核对 |
| C8 | 没有内置 call-tree API，树形缩进要自写 listener | s7，`:304` | source-report | 函数级 trace | 非常规跳转会使 depth 失真 |

## 验证与限制

缺 unidbg revision、目标 SO 和一份真实 trace。示例寄存器值、`libxxx.so` 偏移和 0x10000 窗口都是课文数字。常量表、吞吐表和「白盒 AES 几乎只能靠 diff」是作者判断，保持 source-report。本轮没有运行 Unidbg，也没有把 Console Debugger 单步写成步骤。
