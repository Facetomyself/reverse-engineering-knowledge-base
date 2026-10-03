---
schema_version: 2
id: jsvmp-opcode-or-deobfuscate-procedure
document_type: procedure
original_date: '2026-08-10'
archived_date: '2026-10-02'
scope:
  targets:
    - jsvmp
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ai-assisted-20260810-01.md#一判据算法编进-opcode-了吗"
    basis: source-report
  - id: s2
    ref: "./ai-assisted-20260810-01.md#四六个陷阱"
    basis: source-report
  - id: s3
    ref: "./ai-assisted-20260810-01.md#六魔改点每个常量挂一个环境探测"
    basis: source-report
  - id: s4
    ref: "./ai-assisted-20260810-01.md#八验证正负对照都要做"
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [s1, s2]
    basis: source-report
    limits: 判据表是这一篇的分流，不是所有 JSVMP 的 opcode 表。案例里的执行流体积、函数范围和 debugger 次数都是作者自述。
  - name: parameters
    anchor: parameters
    sources: [s3]
    basis: source-report
    limits: 只记录常量挂在环境探测上、以及错了仍出值。不收录 IV、Tj、掩码字面量、样本输入或样本摘要。
  - name: validation
    anchor: acceptance
    sources: [s1, s4]
    basis: source-report
    limits: 结构是否可读是本流程的验收。作者写下的样本命中和 HTTP 对照不是本轮运行结果。
relations:
  - type: derived_from
    target: "./ai-assisted-20260810-01.md#一判据算法编进-opcode-了吗"
tags:
  - jsvmp
  - source-report
---

# 先判断算法有没有编进 opcode，再决定要不要逐条逆

这篇流程只解决一个分流：面对 JSVMP，什么时候反混淆就停，什么时候才逐 opcode。猿人学 match/26 只作为来源里的案例，用来说明分流和“常量挂在环境探测上会静默出错”。不收录复现脚本、常量字面量、样本摘要或请求样值。

<a id="prerequisites"></a>
## 前提与输入

先能把“源码被搅乱”和“算法被编译成字节码”分开。来源写 obfuscator.io 一类混淆器仍是源码级算法，只有 VM 保护才把算法编进 opcode。

手里至少要有可静态阅读的脚本。opcode 执行统计可选，但不能把统计范围当成全程序。标准密码常量用 AST 扫一遍，作为“先反混淆还是直接逐 opcode”的输入，不作为算法族的终判。

来源在案例里先试 webcrack，因 native 依赖没装上，再换无 native 依赖的 deobfuscator。工具名是作者当时的选择，不是本流程的唯一实现。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 先看热点算子出现在哪 | add/mul 结果是 NaN，或脚本一开始就是大量位运算、成片 debugger | 分别当成诱饵、字符串解码器、反调试。不换算法族假设，去 S2。若把它们当成哈希核，走 F1 |
| S2 | 看静态断点和标准常量 | 断点没有命中但签名仍在跑；AST 扫不到标准 crypto 常量 | 断点作废只说明执行体可能是 eval 出来的。扫不到常量有两种可能，先反混淆再判断，去 S3。直接认定常量在字节码里，走 F3 |
| S3 | 反混淆后读结构 | 源码结构直接可读，或仍然只剩 dispatcher 和常量池 | 可读则输出“不要逐 opcode”并去验收。只剩分派器和常量池，才进入逐 opcode |
| S4 | 若常量挂在环境探测上 | 每个常量单独做类型或原生 toString 判断，补错环境仍然出值 | 不把“没报错”当成环境正确。用真浏览器的输入输出样本核对常量集合，对不上走 F5 |

流程图沿用 S1 到 S4。失败不回到“再抓一份更大的执行流”来回答结构问题。

<a id="parameters"></a>
## 案例里的常量角色

来源案例把魔改放在常量上，消息扩展和轮函数结构仍按标准 SM3 描述。八个 IV 寄存器各挂一个不同的原生构造器，判断是两层：类型对不对，以及 toString 是否像原生代码。其中一个寄存器探测的是 `require`，方向和其他寄存器相反，用来区分浏览器和 node。

另有两档 Tj、一处 compress 掩码、一处字节掩码。来源把这四类合成十二个独立开关，任一翻转都会得到完全不同的输出。明文拼接被写成路径、服务端时间和页码的零分隔符连接；服务端时间不是本地时钟。这些数字和样本不进入本卡。

<a id="outputs"></a>
## 输出

交付的是分流结论，不是签名值。

- 反混淆后源码结构可读：停止逐 opcode，留下可读结构的位置。
- 反混淆后仍只有 dispatcher 和常量池：这时才把逐 opcode 或 devirt 列为下一步，并写明还缺哪一段字节码证据。
- 执行流若已经抓了，只降级成输入输出样本。来源写 141MB 执行流最后的价值是提供对照样本，不能用来回答“常量在不在被解释的程序里”。

<a id="acceptance"></a>
## 验收

通过条件是结构，不是“跑出了一个值”。

- 反混淆后能直接读到算法结构。来源案例写成 reset、write、compress、fill、sum 都在源码里，并称判据表倒数第二行成立。满足则接受“算法没编进 opcode”。
- 反混淆后仍然只剩 dispatcher 和常量池。满足才接受“算法编进了 opcode”。
- 来源另外写了离线样本逐字节一致，以及垃圾输入与正常输入的 HTTP 对照不是一回事：垃圾输入的失败也可能是频控或会话，而不一定是算法。这是作者自述。本轮没有运行反混淆器，也没有发请求，不把这些状态当成已验收。

<a id="failure-exits"></a>
## 失败出口

F1：热点全是 NaN、脚本开头的纯位运算、或成片 debugger，被当成哈希核。停在算法族结论，改采集范围或直接忽略该层。

F2：执行统计的函数范围没有盖住真正的核，于是出现“全场没有移位、没有异或”。先查采集范围，再怀疑算法族。来源案例写默认范围停在 fn 0 到 60，核在这个范围之外。

F3：静态脚本上的断点零命中，仍继续在该脚本里等。来源写真正执行的 VM 是 eval 出来的，运行时 script id 会漂。静态断点作废，不把它当成“签名没跑”。

F4：某个字面量和标准常量只差几位，就去改标准算法里邻近的那个常量。来源后来写方向是 SM3，但改的是 IV 不是 T。邻近命中本身不是改点。

F5：环境探测补错时仍然给出值，没有异常。停止把该值当通过。回到真浏览器样本核对是哪一个开关翻了；没有样本就保持未知，不继续堆环境补丁。
