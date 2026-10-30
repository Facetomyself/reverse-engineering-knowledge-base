---
schema_version: 2
id: jsvmp-from-toy-vm-to-devirt
document_type: archive
original_date: unknown
archived_date: 2026-10-23
scope:
  targets: [JSVMP, public practice target yuanrenxue match/26 and match/30]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: null
    basis: source-report
    citation: "JSVMP 从入门到入土（序）至（终）"
    reason: 原始 Markdown 未提供可公开定位的稳定文章链接集合；原件已移出 Public article 留证，身份见吸收回执的 sha256。
  - id: s2
    ref: null
    basis: source-report
    citation: "JSVMP 进阶：分派器、反调试、动态 eval、环境、常量、自修改字节码、VM 套娃、devirt"
    reason: 原始 Markdown 为本地转载稿，链接和图片未作为本次公共归档定位源。
source_completeness: partial
tags: [JSVMP, JavaScript, virtual-machine, opcode, dispatcher, anti-debugging, devirtualization, source-report]
---

# JSVMP：从玩具 VM 到执行流、动态字节码与 devirtualization

## 归档说明

本文合并归档 13 篇连续教程，保留其教学顺序和主要代码/判断口径，去除重复的“下一篇预告”、平台导流语句和转载尾注。内容以作者自写玩具 VM 与公开练习靶站为例；本次只做文字清洗与结构整理，没有运行原文代码、复核靶站版本或验证任何商业站点行为。因此文中的“实测”“成功”等均按 `source-report` 理解，不是本库的 runtime 或 server-accepted 结论。原件已移出 Public article 留证，身份见吸收回执的 sha256。

## 一、先建立最小 VM 心智模型

JSVMP 把原本直线执行的算法拆成字节码、程序计数器 `pc`、操作数栈和 dispatcher。玩具示例用 `PUSH`、`LOADX`、`ADD`、`XOR`、`ROTL`、`RET` 表示输入、常量、算术和返回。逆向时先回答四个问题：字节码在哪，谁推进 `pc`，栈如何变化，以及哪个循环按 opcode 选择 handler。

这个模型的价值在于把“看不懂的混淆 JS”转成可观察状态机。算法是否仍在这层 VM、是否被转发到另一层 VM/WASM，必须后续用执行流和调用边界确认，不能看到大数组就直接认定是签名核心。

## 二、反汇编与对齐

有 opcode 菜单时，反汇编器只需按 `pc` 读取 opcode，再读取该 opcode 声明的操作数数量。例如 `PUSH` 和 `ROTL` 各多占一个数字，下一条指令地址因此不连续。长度判断错一次，后续整条流都会错位；真实 VM 中，先确认每个 opcode 的取数行为，往往比给它命名更重要。

没有菜单时，给解释器加执行前日志，记录 `pc`、opcode 和栈快照。相邻两条日志之间的栈差异可揭示入栈、出栈、二元运算以及额外操作数；同一 opcode 需要多次样本确认，避免把一次偶然的值变化误认为语义。得到的菜单再回喂反汇编器，检查指令边界是否与执行日志一致。

## 三、从请求定位 dispatcher

真实分析从请求开始：先在 Sources 全局搜索接口路径或参数名，或设置 XHR/fetch 断点，从调用栈回溯到拼装签名的位置。脚本文件名可能变化，接口字符串等内容锚更稳定。

随后只认形态，不急着逐行读混淆代码。常见 dispatcher 包括：

* `switch`/`if` 型：循环读取 opcode 后直接分支；
* table 型：`handlers[op](...)`，handler 数组和栈操作较清晰；
* threaded 型：通过函数/闭包续接下一条指令，未必有一个显眼的大循环；
* 变体：递归、状态对象或多层 wrapper，但仍需存在“取 opcode → 选择动作 → 推进状态”的边界。

Performance 火焰图只能作为定位线索：被频繁调用的函数可能是 dispatcher，但必须再用 opcode 读取点、栈变化和请求触发次数交叉确认。抓到执行流后，先判断算法是否在当前层：若 handler 主要做取数、拼字符串或调用宿主 `MD5/SM3/SubtleCrypto`，优先沿宿主原语边界恢复；若只看到转发到 WASM/另一台 VM，则应转向里层。

## 四、算法指纹与“不要逐 op”的分流

当 VM 层只暴露标准算法的运算骨架时，循环左移位数、乘法常量、字长和轮数等数据流指纹，通常足以区分 MD5、SM3、murmur 等候选。先用小样本或 handler 级日志确认指纹，再决定是否需要完整 ISA。逐 opcode 适用于算法确实编在当前字节码、且宿主原语或里层边界无法闭合的情况；否则会把大量时间耗在与请求无关的壳上。

## 五、观察本身会改变结果

反调试常见形态包括大量 `debugger`、暂停耗时检测、`Function.prototype.toString` 反 hook、DevTools 开启探测和 console getter。日志断点应尽量不暂停；插桩前后要比较请求输出，不能只看本地是否得到了一个稳定字符串。补环境同样是条件：`navigator.webdriver`、`window.chrome`、WebGL、时钟等缺口可能使签名器选择伪常量而不抛异常。

常量也可能来自环境分支、密文解码、碎片拼装或外部对象。不要把字节码字面量直接当作算法常量；在算术 handler 的运算点记录操作数，才能看到当前观测环境下真正参与运算的值。最终裁判仍是与真实抓包逐字节对比；对不上时先查观测环境和请求材料，而不是立即改算法。

## 六、动态生成与自修改字节码

静态脚本断点一次不命中，可能是 `eval` 或 `new Function` 运行时生成了真正的 VM。可以在生成入口捕获源码，或给临时脚本建立稳定名字后再分析；拿到生成后的 VM，后续仍按普通 dispatcher 处理。

自修改字节码的特征是对 code 数组写入。对数组加 `Proxy` 的 `set` 监视器可记录改写位置和值，帮助定位解密点。若每个槽位只执行一次，运行后 dump 数组可能得到明文；分支未覆盖的槽位仍是密文，循环中重复 XOR 还可能把槽位改回密文。更稳的办法是在解密点按执行顺序记录还原后的字节，得到实际路径；同时保留运行后数组以观察布局。

看到 `c[pos] ^= key` 不等于一定要脱壳：先检查首遍 key。若初值为 0，第一次变换是恒等，静态数组本身可能已经是明文。滚动 key、整块解密和 opcode 自改写则要分别记录轮次、覆盖范围和写入者。

## 七、VM 套娃、WASM 与 devirtualization

外层 VM 的 opcode 分布和调用边界可帮助区分“真身”和“壳”：如果大量 handler 只是搬运参数、调用另一个解释器或 WASM 导出，算法不在当前层。进入里层前记录输入输出边界和版本身份，避免把外层的成功运行误当作算法恢复。

当算法确实编进 opcode 且逐 op 不可避免，可以把解释器的“计算值”改成“表达式”：`PUSH 7` 产生常量节点，`LOADX` 产生符号 `x`，`ADD/XOR/ROTL` 组合 AST，`RET` 输出表达式，再对纯常量子树做折叠。这类 devirt 对直线型路径最有效；输入相关分支和循环只覆盖当前路径，需要路径分裂或专业符号执行工具才能扩大覆盖。它是逐 op 之后的自动化手段，不是跳过边界确认的第一步。

## 复用边界

本归档适合用作 JSVMP 分诊、执行流观测、动态字节码捕获和“宿主原语/里层/逐 op”决策的教学材料。它不提供任何站点可直接发送的 token，不证明猿人学之外目标的 opcode、版本、环境要求或服务端验收，也不替代针对具体样本的 trace、parity 与请求回放证据。
