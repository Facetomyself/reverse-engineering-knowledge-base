# AI 复杂 VM 算法还原

> 来源: 微信公众号转载稿（原文链接见源稿）
> 原始发布时间: unknown
> 归档日期: 2026-07-13
> 分类: native-analysis
>
> pc模拟执行指令，jni libc svc转发到真实设备实现急速trace，以前在手机上跑要几个小时，现在只需要几分钟，使用llvm做指令解析，收集足够的信息，存入自定义的数据库格式，即使几十G的文件，也只需要几秒就可以查完，中间不断优化skill 跟 mcp 工具，主要突破是给了更高维度的信息，让ai不再是追踪字节计算，想办法绕过复杂计算过程，快速的进行算。

pc模拟执行指令，jni libc svc转发到真实设备实现急速trace，以前在手机上跑要几个小时，现在只需要几分钟，使用llvm做指令解析，收集足够的信息，存入自定义的数据库格式，即使几十G的文件，也只需要几秒就可以查完，中间不断优化skill 跟 mcp 工具，主要突破是给了更高维度的信息，让ai不再是追踪字节计算，想办法绕过复杂计算过程，快速的进行算法识别。


我本身自己有trace数据adj8的还原只用了一点时间，因为我是一直跟过来的，但是ai是没有任何提示的情况下独立完成的，强行从vm里面还原了所有计算。

AI + 自定义 MCP：一次 nSign 算法还原的完整复盘
===============================

这篇文章不是一篇“我猜中了某个算法”的爽文。真正值得讲的是另一件事：当目标函数被 VMP、扁平化控制流、白化常量、反调试和海量 trace 淹没时，我没有让 AI 坐在反编译伪代码前面瞎猜，而是把执行轨迹做成一套可查询的数据库，再用自定义 MCP 把这些查询能力交给 AI。


结果是，AI 不再只是聊天窗口里的“逆向经验包”，而变成一个能反复查证据、写查询计划、维护错误路线、生成验证脚本的协作者。它做的不是玄学命名，而是把每个猜测压成一组问题：

```
这个字节第一次在哪里被写出来？这个寄存器的真实 producer 是哪条指令？这个 PC 跑了多少次，是否构成 round/template？这个 immediate 是常量，还是某个动态 state 碰巧等于它？这个输出能否用标准库从输入、key、IV 前向复现？
```


最终，Adjust SDK `nSign` 的 176 字节输出被还原成：

```
output = A[16] || B[128] || C[32]A = nonce16B = AES-256-CBC(P, K, IV=A)C = HMAC-SHA256(B, fixed_native_key)P = 01 00 08 || salt16 || 02 || rnd4 || 03 || SHA1(update_arg)    || 04 || rnd32 || 05 || SHA256("") || 06 || 01P = PKCS7_pad(P, 16)
```


这里最有意思的地方，不是最终出现了 AES 和 HMAC，而是中间我们曾经认真走过很多错路：`KEY16`、repeating-key XOR、`"Saw"` 明文、HKDF、五段 SHA 输出、自定义 byte-mixing VM、非标准 AES。它们都不是胡说八道，它们都来自当时 trace 里的真实局部现象。问题在于，局部现象不是算法结论。


我的框架解决的正是这个问题：把“看起来像”变成“证据链闭合”。

战场：反编译已经不够用了
------------

目标是 `Java_com_adjust_sdk_sig_NativeLibHelper_nSign`，返回 176 字节。静态上看，核心逻辑被压进巨大的扁平化函数和大量内联 step gadget 里。里面有 dispatcher、slot、linked-list 节点、字节表、白化常量和重复的位运算模板。反编译器能给出一些结构，但无法告诉你哪条数据流才是签名算法本体。


更麻烦的是 trace 本身也不好拿。早期真机 trace 跑了 9 小时，产生 1.13B 条指令和约 196GB 文本，结果卡在反调试逻辑里。根因后来被确认：目标会枚举 `/proc/self/fd`，而 trace 工具自身在采集期间不断制造 fd，导致真实 Linux procfs 下 `readdir` 永远读不完。unidbg 对照 trace 则显示同一段逻辑只需要很少的 `readdir` 就能返回。


这件事给了一个很重要的教训：逆向不是只有“算法难”，采集环境也会改变程序行为。如果没有 PC 统计、调用统计和 trace 对照，我们很容易把反调试死循环当成算法复杂度。


于是工具链变成了这样：

```
ARM64 execution trace  -> 自定义 tracedb  -> mmap fixed-width row + addr/value/reg 索引  -> user-trace-mcp  -> AI 在 Cursor 内发起结构化查询  -> Python assertion 固化证据
```


数据库层的意义很直接：几十 GB 到几百 GB 的 trace 不能靠打开文本、grep 和肉眼滚动来分析。它必须支持按 `trace_id` 顺序取窗口、按地址找读写、按值找出现、按寄存器找 producer、按 PC 统计执行次数、按调用层解析 libc/JNI/syscall。MCP 的意义是把这些动作变成 AI 可以调用的工具，而不是让我在聊天窗口里复制粘贴命令和结果。

方法论：从输出往回走
----------

这套流程的核心原则只有一句话：从输出开始，不从算法名开始。


我不会因为看到 32 字节就叫它 SHA-256，也不会因为看到 `0x55`、`0x36`、S-box 或 GF 运算就直接宣布 AES。所有结论都要从具体执行证据落地：

```
output slice  -> first real producer  -> producer operands  -> operand producers  -> PC/template/count  -> arithmetic proof  -> Python reimplementation  -> cross-run validation
```


在这个过程中，MCP 工具承担的是证据放大器：

*   `find_value_occurrences`

     用来找某个值第一次在哪里出现，但不能把“同值”当“同源”。

*   `get_producers`

     和 `walk_dataflow` 用来跳过 transport，直接看真实计算 producer。

*   `get_pc_stats`

    、`get_pc_executions`、`analyze_pc_sequence` 用来数 round、找重复模板、定位首尾边界。

*   `taint_trace_origin`

     用来做字节级反向污点，尤其适合从某个输出 byte 回溯真实计算链。

*   `get_call_at`

    、`list_calls`、`find_callers` 用来识别 `rand`、`read`、JNI 等外部来源，避免硬把外部返回值追成内部算法。

*   Python 脚本负责把每条证据变成断言：不是“像”，而是 `assert computed == observed`。


AI 的价值在这里开始显现。它适合维护上下文，适合把一堆 trace 片段整理成表，适合看到矛盾后提醒“这可能是跨 run 样本混用了”，也适合把手动推导翻译成可执行自检。它不适合做最终裁判。最终裁判只能是 trace 证据和前向复现。

错误路线地图
------

这次分析里最值得保留的不是“我一开始就对了”，而是每条错路怎么出现、怎么被淘汰。因为这正好说明自定义 MCP 框架为什么有必要。

### KEY16 和 repeating-key XOR

早期出现过一个非常诱人的 16 字节值：

```
KEY16 = 4a7fb887817354b8ff88204f1d268582
```


当时很多局部公式可以被写成：

```
B[i] = PRE[j] ^ KEY16[i % 16]B[i] = STAGE_C[i] ^ KEY16[i % 16]
```


这条路线为什么合理？因为 trace 中确实大量出现 `0x55`、`0x36`、`0xff` 这样的白化/掩码常量，也确实有很多字节值能和某个 16 字节周期发生匹配。早期 `PRE/OP/DSP/HEAP` 的来源统计里，也能看到“唯一 KEY16 命中”的槽位。


但后来它被推翻了。关键原因有三个：

```
1. 同输入双 run 中 B 的 128 字节全部随 nonce 改变，不是固定 repeating-key XOR 输出。2. 4a7f... 后来被解释为 AES 末轮密钥 RK14 ^ 0x55 的白化形态，不是主密钥。3. 真正主密钥是 32 字节固定 AES-256 key：   ffb5e5f9c862b637d13351c292633e39965a3c2d037ed64dfff5388e11d80db3
```


这就是值碰撞的典型陷阱。一个值出现在 trace 里，不等于它的语义就是“密钥”。它可能是白化后的 round key，可能是中间 state，也可能只是某个动态值碰巧等于你正在找的常量。

### `"Saw"` 明文误判

另一条很有戏剧性的错路是 `"Saw"`。旧分析里曾经看到：

```
PRE[710] = 0x53 = 'S'DSP[50]  = 0x61 = 'a'DSP[52]  = 0x77 = 'w'
```


于是很容易得出结论：明文直接进入了 B 段，甚至能在某些输出字节里被 XOR 还原出来。


这同样不是完全凭空来的。早期 trace 里确实有这些字节，局部 XOR 公式也能复现某些输出。但后来更完整的 producer 追踪和明文层恢复表明，当前 native 可见的输入主窗口是：

```
SHA1(update_arg) -> P[25:45]
```

`   `

`"Saw"` 路线的问题是把单 trace 中间 operand 当成了语义明文。对 VMP 来说，一个中间槽的值可能来自 nibble 重组、白化、S-box、旧状态覆盖，不能因为它等于 ASCII 就给它命名。


这也是 AI 容易犯错的地方：它特别擅长给人类可读的字节赋予故事。但 MCP 查询让这个故事必须回答 producer 问题：这个 `0x53` 是从输入 copy 来的，还是从 `0xb8 >> 4`、ORR、EOR、mask 一路算出来的？

### HKDF / HMAC-PRF 候选

176 字节输出天然会让人想到扩展输出：HKDF、HMAC-PRF、若干段 SHA/HMAC 拼接。早期也确实找到过 SHA-256 IV、K 常量、HMAC ipad/opad，以及多个 SHA final-add 形态。


这条路线的合理性在于：C 段最终确实是 HMAC-SHA256，`rnd32` 的一部分也确实落到了 SHA-256 compression 的 final-add 层。问题是，这些证据只能说明“局部存在 SHA/HMAC”，不能说明“整个 176B 是 HKDF 输出”。


最终边界是：

```
C = output[144:176] = HMAC-SHA256(B, fixed_native_key)
```


而不是：

```
output[0:176] = HKDF(...)
```


这条错路被淘汰的方式很典型：先确认标准算法的 I/O 边界，再用标准库验证。标准库跑不通，就不要继续给 HKDF 猜变体；回到 trace 找真实 producer。

### 五段 SHA 输出

早期 case-study 里，一度把 `output[16:176]` 解释成多段 SHA-256 digest 拼接：

```
output[16:47]   = SHA #1 final digestoutput[48:79]   = SHA #2 final digestoutput[80:111]  = SHA #3 final digestoutput[112:143] = SHA #4 final digestoutput[144:175] = SHA #5 final digest
```


这条路线来自真实的 SHA 常量命中和 `add w2,w0,w21` finalization 证据。它的价值不是最终结论，而是证明了工具链能快速识别标准 SHA-256 结构：IV、K、`H[i] += working[i]`、message schedule。


后续更完整的 B 段端到端验证推翻了“B 是 SHA digest 拼接”。现在的结论是：

```
B[0:128] = AES-256-CBC ciphertextC[0:32] = HMAC-SHA256(B, key)
```

`   `

`rnd32` 分支里仍然有 SHA-256 compression 证据，但它属于明文 P 内的随机派生字段，不是 B 段整体结构。

### 自定义 byte-mixing VM

最难处理的一条路线是“B 段是自定义 byte-mixing VM”。它不是简单错误，因为早期看到的现象都是真的：

```
OUTSLOT 写历史white_sbox = AES_SBOX ^ 0x55gf_xtime / gf_mul3x ^= (x << 1/2/4) & 0xff0x55 / 0x36 / 0x63 白化常量slot 覆盖链和 VM tape
```


如果只看局部，这就是一个复杂的自定义 VM。甚至用 trace replay 可以复现很多中间状态。但“能 replay”不等于“还原了算法”。trace replay 只是录音机，算法还原要求我们把每个 term 追到 primitive input、常量或外部来源。


最终 B 段被反转为标准 AES-256-CBC，靠的是更强的证据：

```
1. pc=0x104eec 的 AddRoundKey 循环计数：   8 blocks * 15 groups * 16 bytes = 19202. Nr=14，符合 AES-256。3. 末轮满足：   B[i] = SubBytes(state)[i] ^ RK14[i]4. 中间轮满足：   MixColumns(ShiftRows(SubBytes(state))) == 下一轮输入5. key schedule 从 RK0||RK1 展开出的 RK2/RK14 与 trace 实测一致。6. 端到端：   AES256(P0 ^ A, K) == B0   AES256(P1 ^ B0, K) == B1
```


这时原先的 VM 现象才被重新解释：VM 是承载层，AES 是它承载的计算。`white_sbox` 是带白化的 SubBytes，GF 链是 S-box 生成和 MixColumns 的 GF 运算，`KEY16` 是末轮密钥白化快照，不是外部 repeating key。


这次反转很适合拿出去讲。它说明 AI + MCP 的目标不是坚持某个漂亮假设，而是让假设随证据升级甚至死亡。

最终还原：A 段
--------

输出前 16 字节是 nonce。trace 的 call layer 证明它来自 `srand(time())` 和 8 次 `rand()`，按 4 个 word 输出：

```
A_word[k] = rand[2k] ^ rand[2k+1]A = concat_be32(A_word[0..3])
```


这里有一个方法论要点：随机数返回值往往不是模块内 ALU 算出来的。纯 value-walk 或 taint 可能会在某个寄存器上断掉，甚至错误落到一个常量 `mov`。这时要切换到 call 层查询，用 `get_call_at` 或 `find_callers` 确认 `rand@libc.so` 的返回值。


这就是 MCP function/call layer 的价值。它让“追不到”变成一个明确结论：这是外部来源，不是内部算法。

最终还原：B 段
--------

B 段是 128 字节，也是整个分析中反转最多的地方。最终公式是：

```
B0 = AES_256_encrypt(P0 ^ A, K)Bi = AES_256_encrypt(Pi ^ B(i-1), K)   i = 1..7K = ffb5e5f9c862b637d13351c292633e39    965a3c2d037ed64dfff5388e11d80db3IV = A[0..15]
```


证明过程分几层。


第一层是计数。`pc=0x10ec6c` 的 ORR 序列化出现 32 次，对应 32 个 32-bit word，也就是 128 字节 B。`pc=0x104eec` 出现 1920 次，刚好是：

```
8 blocks * 15 round-key groups * 16 bytes
```


这给出了 AES-256 的轮数轮廓。


第二层是末轮。末轮没有 MixColumns，trace 中能看到：

```
B[i] = SubBytes(state)[i] ^ RK14[i]
```


旧的 `KEY16 = 4a7f...` 在这里被重新定位：

```
RK14        = 1f2aedd2d42601edaadd751a4873d0d7RK14 ^ 0x55 = 4a7fb887817354b8ff88204f1d268582
```


也就是说，早期所谓 `KEY16` 是末轮密钥被 `0x55` 白化后的形态。


第三层是中间轮。把 block0 的 round1 到 round2 拿出来，用标准 AES 的：

```
SubBytes -> ShiftRows -> MixColumns -> AddRoundKey
```


逐字节计算，结果与下一轮输入匹配。再用 `RK0||RK1` 展开 AES-256 key schedule，得到的 `RK2` 和 `RK14` 都与 trace 实测一致。


第四层是端到端。只要 `K` 和 CBC 输入块成立，标准库风格实现就必须能从明文块得到密文块：

```
AES256(P0 ^ A,  K) == B0AES256(P1 ^ B0, K) == B1
```


实际脚本已经把全 8 块 B 前向加密到逐字节相等。到这一步，B 段不再是“像 AES”，而是标准 AES-256-CBC。

最终还原：P 明文层
----------

知道 B 是 AES-256-CBC 之后，下一步就不是继续追 VM slot，而是直接解 CBC。`recover_b_plaintext.py` 用固定主钥 `K` 和 `IV=A` 解出 128 字节 P，再做双 run 对拍。


得到的结构是一个 113 字节数据加 15 字节 PKCS#7 padding 的 TLV-like 信封：

```
off 0   :01 00 08off 3   :salt16       16B  nonce 派生off 19  :02off 20  :rnd4         4B   /dev/urandom 首 4Boff 24  :03off 25  :SHA1(update_arg) 20B 输入摘要off 45  :04off 46  :rnd32        32B  nonce 派生 / SHA-256 层off 78  :05off 79  :SHA256("")   32B  固定常量off 111 :06off 112 :01off 113 :0f * 15      PKCS#7
```


三个断言非常关键：

```
P[25:45]  == SHA1(update_arg)P[79:111] == SHA256("")P[113:]   == b"\x0f" * 15
```


同输入、不同 nonce 的两条 run 对拍后，可以看到 `SHA1(update_arg)`、`SHA256("")`、固定 tag、padding 保持不变，而 `salt16`、`rnd4`、`rnd32` 随 nonce 变化。


这一步把“输入相关字段”和“随机字段”分开了。它也解释了为什么很多早期路线会混乱：如果你只在密文 B 上看差异，nonce 会把全部 128 字节都搅动；只有先识别 CBC，才能看到明文 P 的真实结构。

salt16：自定义分支也能被还原
-----------------

虽然最终签名生成可以把 `salt16` 当 nonce 随机生成，但分析上我们还是把它下钻闭合了。`salt16` 来自 `/dev/urandom` 首 4 字节，也就是 `rnd4`，经过一条确定性 VM 扩展链：

```
rnd4  -> Park-Miller 31-bit LCG  -> inside-out Fisher-Yates perm[0..15]  -> 16 个扫描掩码 M  -> bitset 表 T[0..15]  -> 8 个固定 XOR 子集 HALF_COMBOS  -> 4 个 source word  -> bswap16_each  -> salt16
```


这条链的价值在于，它展示了“自定义算法不是死路”。标准 AES/HMAC 可以用标准库证明；自定义 VM 分支则用 producer、PC、operand 和跨 run 模板证明。


例如 `T` 表写入不是抽象拟合，而是 trace 中真实的：

```
pc=0x135250: T[index] |= (1 << bit)pc=0x135254: strh 写回 T[index]
```

`   `

`HALF_COMBOS` 也不是从输出凑出来的常量表，而是同一条 `eor @0x135428` 在两条 run 中稳定执行出的固定 XOR 子集。run1/run2 都能从各自 `rnd4` 生成对应 `salt16`：

```
run1: rnd4=d020b6de -> salt16=486b703d4547d0bc4ad57fafe5c6c578run2: rnd4=cf664a41 -> salt16=cb70bd7314d348faa3d70a77e15a886a
```


这就是“不是 replay”的标准：per-run 值只作为 test vector，程序常量和操作模板必须来自 producer 证据。

rnd32：从 VM bit-mix 回到 SHA-256 compression
-----------------------------------------

`rnd32` 是 P 中的 32 字节可变字段。它的输出层被推进到了 SHA-256 compression final-add：

```
pc=0x1015fc:H[i] = (H[i] + working[i]) mod 2^32
```


第一组 8 次 final-add 从标准 SHA-256 IV 得到 `SHA256("")`。最后一组 8 次输出正好等于 `P[46:78]` 的 `rnd32`。这说明它不是随手写的 VM add/bit-mix，而是在 SHA-256 state 上做标准压缩。


run1 首 word 的证据是：

```
0x92058f99 + 0x12fb69fa = 0xa500f993 (mod 2^32)
```


更进一步，最后一个 compression block 的 `W[0..15]` 也从 `K[t]+W[t]` 注入点恢复，并用标准 SHA-256 compression 复算通过。这里我们仍然保持边界清晰：`rnd32` 的 SHA 层已证，前序消息块来源仍可继续下钻，但对最终可生成签名来说，它属于 nonce 派生字段，不承载输入信息。

最终还原：C 段
--------

C 段最终最干净：

```
C = HMAC-SHA256(B, fixed_native_key)
```


早期 HKDF/HMAC-PRF 猜测之所以会出现，是因为 trace 里确实有 HMAC 结构、ipad/opad 和 SHA-256 常量。但最终边界只有最后 32 字节。C 段覆盖的是 B，不覆盖整个 176 字节，也不是用来扩展出 B 的 PRF。


这再次说明：标准密码学证据必须先找 I/O 边界，再跑标准库验证。看到 HMAC 常量不等于整段都是 HMAC 派生。

最终可执行规范
-------

最终的前向实现被收束到 `nsign_full_algorithm.py`。它不需要 VM tape，不需要旧的 `KEY16`，不需要猜测中间 slot。


核心就是：

```
def build_plaintext(sha1_update_arg, salt16, rnd4, rnd32):    p = (b"\x01\x00\x08"         + salt16         + b"\x02" + rnd4         + b"\x03" + sha1_update_arg         + b"\x04" + rnd32         + b"\x05" + hashlib.sha256(b"").digest()         + b"\x06" + b"\x01")    return pkcs7_pad(p, 16)def nsign(master_key, hmac_key, sha1_update_arg, A, salt16, rnd4, rnd32):    P = build_plaintext(sha1_update_arg, salt16, rnd4, rnd32)    B = aes256_cbc_encrypt(P, master_key, A)    C = hmac.new(hmac_key, B, hashlib.sha256).digest()    return A + B + C
```


run1 自检做了几件事：

```
1. 组装 P，确认各字段 offset。2. AES-256-CBC(P,K,IV=A) 得到的 B 逐字节等于 trace 输出。3. salt16 的外层 bswap16_each 双 run 断言通过。4. 最终输出结构与 A/B/C 分段一致。
```


这就是我认为“算法还原完成”的标准：不是写出一堆看起来像逆向成果的中间常量，而是从 primitive inputs 和随机字段出发，前向生成目标输出。

为什么这套框架有效
---------

这套 AI + MCP 框架真正解决了四类问题。


第一，解决规模问题。几十 GB 到几百 GB trace 不能靠人眼看。自定义 tracedb 用 mmap、fixed-width row 和索引把它变成可交互数据源。AI 可以在这个数据源上发起很多小查询，而不是一次性吞掉整份 trace。


第二，解决定位问题。VMP 里 transport、dispatch、slot 覆盖远多于真实计算。`get_producers skip_transport`、`walk_dataflow data_only`、`taint_trace_origin auto_pivot` 能把注意力从搬运层拉回计算层。


第三，解决误判问题。旧路线里的很多错误都来自“值像”。`0x55` 像 HMAC 常量，`0x36` 像 ipad，`4a7f...` 像 KEY16，ASCII 像明文，GF/S-box 像 AES，又不像完整 AES。MCP 查询强迫每个值回答来源、producer、PC、operand、跨 run 稳定性。


第四，解决协作问题。AI 很适合写阶段计划、整理历史、生成验证脚本、维护“过期结论”隔离区。人负责判断哪些问题值得问，工具负责返回证据，脚本负责最终验算。三者缺一不可。


整个闭环可以概括成：

```
假设-> 查询 trace-> 找 producer / count / boundary-> 写 Python assertion-> 跨 run 对拍-> 更新结论或归档为过期路线
```


这比“AI 帮我看伪代码”强太多。因为它不是让 AI 更自信，而是让 AI 更容易被证据纠正。

经验总结
----

这次 nSign 还原给我的最大经验是：复杂逆向里最危险的不是不知道，而是局部知道一点就开始命名。


看到 SHA 常量，不等于整个输出是 SHA 链。看到 HMAC ipad/opad，不等于是 HKDF。看到 S-box 和 GF，不等于已经证明 AES，也不等于不是 AES。看到某个 16 字节周期值，不等于它就是 key。看到 ASCII，不等于它就是明文。


自定义 MCP 和 trace DB 的意义，是把这些“看起来像”的东西全部拉回同一个证据平面：

```
谁写的？什么时候写的？读了谁？算了什么？跑了几次？跨 run 是否稳定？能否前向复现？
```


AI 在这个体系里不是神谕，而是放大器。它能把查询速度、文档整理、脚本生成、假设管理全部提速。但最后能拿出去吹的，不是“AI 猜到了 AES”，而是“我让 AI 通过自定义 MCP 操作自己的 trace 数据库，用证据驱动的方式把一堆错误路线淘汰，最终把算法收束成可执行规范”。


这才是这套框架最有价值的地方。

可复核资料
-----

这篇复盘对应的主要证据文件如下：

*   `current_clean_recovery/README.md`

    当前干净总览，记录 A/B/C 三段最终结论、过期路线和全算法状态。

*   `current_clean_recovery/B段_OUTSLOT_AES_GF_SBOX.md`

    B 段从 OUTSLOT/GF/S-box 到标准 AES-256-CBC 的反转证据。

*   `current_clean_recovery/nsign_full_algorithm.py`

    最终前向参考实现，run1 自检把 P 组装、AES-256-CBC、B 段输出逐字节闭合。

*   `current_clean_recovery/recover_b_plaintext.py`

    CBC 解密恢复 P，给出 TLV 布局和双 run 对拍。

*   `current_clean_recovery/recover_salt16_algorithm.py`

    `rnd4 -> Park-Miller -> perm/mask -> T -> salt16` 的完整自定义分支。

*   `current_clean_recovery/recover_rnd32_sha_layer.py`

    `rnd32` 的 SHA-256 final-add/final-block 验证。

*   `current_clean_recovery/过期结论.md`

    `FINAL_ANALYSIS_v3.md`、`ALGORITHM_REVEAL_v6.md`：错误路线和阶段性假设的来源，用来证明这些反转不是事后编故事。


---


看雪ID：zhuzhu\_biu

https://bbs.kanxue.com/user-home-878476.htm

\*本文为看雪论坛精华文章，由 zhuzhu\_biu 原创，转载请注明来自看雪社区

[![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)](https://mp.weixin.qq.com/s?__biz=MjM5NTc2MDYxMw==&mid=2458616439&idx=1&sn=ed63972eed0764f9dc562e899e512e05&scene=21#wechat_redirect)

第十届安全开发者峰会【议题征集】-欢迎投稿

\# 往期推荐

[ret2dlresolve分析](https://mp.weixin.qq.com/s?__biz=MjM5NTc2MDYxMw==&mid=2458616819&idx=1&sn=6754cf279a5824193e7817edc480ca63&scene=21#wechat_redirect)

[ELF GOT Hook 实战](https://mp.weixin.qq.com/s?__biz=MjM5NTc2MDYxMw==&mid=2458616803&idx=1&sn=169a63cd320c405cc6f793cb0611de1d&scene=21#wechat_redirect)

[面向复现的逆向工程实践：Hermes 在设备刷写、提权与 Frida 魔改中的自动化能力验证](https://mp.weixin.qq.com/s?__biz=MjM5NTc2MDYxMw==&mid=2458616783&idx=1&sn=219d3d357722602c80071a048c05a2b7&scene=21#wechat_redirect)

[把 .o 变成 .ko：GKI 安全特性的铁幕](https://mp.weixin.qq.com/s?__biz=MjM5NTc2MDYxMw==&mid=2458616782&idx=2&sn=bef4d5e72317a35c94b6d9a35359930f&scene=21#wechat_redirect)

[实战APP全流程分析(检测绕过/登录分析/视频解锁/native加密/广告绕过)](https://mp.weixin.qq.com/s?__biz=MjM5NTc2MDYxMw==&mid=2458616656&idx=1&sn=f9a9b53085541a0e47c3d9e43e08d2f5&scene=21#wechat_redirect)


**球分享**


**球点赞**
