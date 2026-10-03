---
schema_version: 2
id: xfq-rabbit-endian-split-reference
document_type: reference
original_date: '2026-02-24'
archived_date: '2026-10-02'
scope:
  targets: [rabbit]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260224-02.md#1-密钥初始化"
    basis: source-report
  - id: s2
    ref: "./xfq-20260224-02.md#2-iv-初始化可选"
    basis: source-report
  - id: s3
    ref: "./xfq-20260224-02.md#3-状态更新与密钥流生成"
    basis: source-report
  - id: s4
    ref: "./xfq-20260224-02.md#测试数据"
    basis: source-report
  - id: s5
    ref: "./xfq-20260224-02.md#4-异或加密"
    basis: source-report
  - id: s6
    ref: "./xfq-20260224-02.md#6-常见变种与非标准实现"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s3]
    basis: source-report
    limits: 只保留讲义里仍成行的状态规模、小端装入、G 函数、常数 A 的开头和输出字的第一项。密钥调度和 IV 混合的函数体粘连，不恢复成实现。
  - name: decision-flow
    anchor: decision-flow
    sources: [s3, s6]
    basis: source-report
    limits: RFC 与 CryptoJS、CyberChef 的分叉是作者陈述。提取函数粘连，且后文又把整段密钥流倒序称为唯一重组，这与前面的前 8 字节异或例子冲突。本卡不把倒序或 CyberChef 尾部抽取收成可执行规则。
  - name: validation
    anchor: validation
    sources: [s4, s5, s6]
    basis: source-report
    limits: 两套密文和附录块都是讲义写下的十六进制。未对照 RFC 4503 正文，也没有跑 CryptoJS。全 0 附录句和示例密文句是两个不同输入。
relations:
  - type: derived_from
    target: "./xfq-20260224-02.md#6-常见变种与非标准实现"
tags:
  - rabbit
  - cryptojs
  - source-report
---

# Rabbit 的平方非线性与 RFC / CryptoJS 分叉

这张卡用来记住讲义中的 Rabbit：8 个状态字加 8 个计数器，非线性来自平方后的高低 32 位异或，以及同一输入在作者称为 RFC 4503 和 CryptoJS 旧实现时会得到两串不同密文。它不把 CyberChef 或粘连的提取函数当成基准实现。

<a id="parameters"></a>
## 参数

讲义把内部状态写成 8 个状态字、8 个计数器和 1 位进位。密钥按小端装入 32 位字。G 函数对状态加计数器的和做平方，再把高 32 位和低 32 位异或。计数器递增使用以 0x4D34D34D 开头的常数。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 状态是 8 个 32 位状态、8 个 32 位计数器和 1 位进位 | Rabbit 的状态由 8 个 32 位状态变量 + 8 个 32 位计数器 + 1 位进位 组成。 | s1，xfq-20260224-02.md:138 | source-report | 未核对迭代后的具体字 |
| C2 | 密钥按小端每 4 字节收成一个字 | k = [int.from_bytes(key[i:i+4], 'little') for i in range(0, 16, 4)] | s1，xfq-20260224-02.md:143 | source-report | 交叉填入 state 和 counter 的循环粘连 |
| C3 | IV 混合被作者标成按 RFC 4503 去异或计数器，第一项是 counter[0] 异或 v0 | # 按照 RFC 4503 的方式用 IV 修改计数器counter[0] ^= v0 | s2，xfq-20260224-02.md:179 | source-report | 注释和语句粘在同一行，其余 counter 项未分开引用 |
| C4 | 计数器常数的前四项以 0x4D34D34D、0xD34D34D3、0x34D34D34、0x4D34D34D 开头 | A = [0x4D34D34D, 0xD34D34D3, 0x34D34D34, 0x4D34D34D, | s3，xfq-20260224-02.md:214 | source-report | 数组在行末截断，后四项在下一行 |
| C5 | G 的结果是平方值的高 32 位与低 32 位异或 | g[i] = ((sq >> 32) ^ sq) & 0xFFFFFFFF  # 将平方的高32位与低32位做异或 | s3，xfq-20260224-02.md:233 | source-report | 与后文“加上 constant 再平方”的写法不一致，见限制 |
| C6 | 输出过滤的第一项是 state[0] 的低 16 位异或 state[5] 的高 16 位 | s[0] = (state[0] & 0xFFFF) ^ (state[5] >> 16)  # 取state0低16位 异或 state5高16位 | s3，xfq-20260224-02.md:274 | source-report | 其余输出字被省略号代替 |

<a id="decision-flow"></a>
## 识别

先搜常数 0x4D34D34D。状态混合若被写成异或而不是加法，讲义认为丢掉了进位。G 函数、常数 A 和旋转量被列出三种魔改。实现对不齐时，讲义要求分开 RFC 提取、CryptoJS 的端序，以及它归到 CyberChef 的尾部抽取，不要用后者当基准。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C7 | 状态混合被写成异或时，讲义认为失去模加法进位 | 注意:网上部分教程和代码在这一步写成了异或(以为是 g[0] ^ ...),这样失去了模加法带来的进位 | s3，xfq-20260224-02.md:261 | source-report | 正确的加法式跨行粘连，不补 |
| C8 | 后文又把标准 G 写成先加 constant 再平方后异或 | 1. G 函数修改 (平方运算) 标准 G 函数:((x + constant)^2) ^ ((x + constant)^2 >> 32)。 魔改:修 | s6，xfq-20260224-02.md:350 | source-report | 与 C5 的 (state+counter) 平方不是同一句，不合并 |
| C9 | 识别常数被写成搜索 0x4D34D34D | 识别:搜索 0x4D34D34D。 | s6，xfq-20260224-02.md:358 | source-report | 只覆盖计数器常数 |
| C10 | 状态更新的旋转量被写成 16、16、8、8 这一组，改掉就算魔改 | 3. 旋转常数修改 状态更新时的循环移位量(16, 16, 8, 8...)。 魔改:修改这些移位参数。 | s6，xfq-20260224-02.md:361 | source-report | 省略号后的具体序列未展开 |
| C11 | 讲义把非 16 字节整块的异或写成从 S 的尾部取值 | result[offset+j] = plaintext[offset+j] ^ S[16 - length + j]; | s6，xfq-20260224-02.md:398 | source-report | 周围函数粘连，不能当成已核对的源码 |
| C12 | 讲义把 RFC 与当时 crypto-js 的差异写成小端对大端 | eSTREAM/RFC 标准要求密钥(Key)、IV 和输出(Output)都按**小端序(Little-Endian)**处理,而当时的crypto-js 却错误地使用了大端序。 | s6，xfq-20260224-02.md:484 | source-report | 转述 Issue，未打开该 issue |
| C13 | 不兼容的版本被写成保留为 CryptoJS.RabbitLegacy | 为了保证向后兼容,crypto-js 最终将那个“不标准”的版本保留为 CryptoJS.RabbitLegacy,并推出了修复后 | s6，xfq-20260224-02.md:489 | source-report | 句子在行末截断 |
| C14 | 讲义要求对照 RFC 4503 附录或所附代码，不要用 CyberChef 当基准 | 避坑警告:如果试图用代码还原或者学习 Rabbit 算法,请**对照 RFC 4503 的官方测试附录(TestVectors B.1 / B.2)**或者我的星球文章附带的代码,不要把 CyberChef 或者网上一些魔改版流密码模块作为基准对照点。 | s6，xfq-20260224-02.md:456 | source-report | 所附 py 不在本篇正文 |
| C15 | 后文又把小端追加之后的整段倒序称为唯一重组 | # 为了方便对照后续字节位置,将其倒序后输出,这是唯一的重组形式 | s6，xfq-20260224-02.md:425 | source-report | 与 C18 使用密钥流前 8 字节冲突，不采用 |

<a id="validation"></a>
## 对照值

同一组示例输入被写成两串密文。附录那一块全 0 向量是另一句话，不要和示例密文当成同一次输入。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C16 | 示例明文被写成 xiaofeng，8 字节 | 明文: xiaofeng (8 字节) | s4，xfq-20260224-02.md:125 | source-report | 密钥在下一行，本格不引用 |
| C17 | 讲义把 c9004494abcdf896 标成 RFC 4503 | 密文(hex): c9004494abcdf896  (RFC 4503 标准) | s4，xfq-20260224-02.md:130 | source-report | 未对照 RFC |
| C18 | 异或小节用密钥流前 8 字节得到同一串密文 | 密文(hex):          c9004494abcdf896 | s5，xfq-20260224-02.md:309 | source-report | 只说明讲义内部这两处一致 |
| C19 | 讲义把 de68add3ec9b7b3f 标成 CryptoJS 变体 | 密文(hex): de68add3ec9b7b3f  (CryptoJS 变体) | s4，xfq-20260224-02.md:131 | source-report | 未跑 CryptoJS |
| C20 | 后文把同一串 de68add3ec9b7b3f 标成 CryptoJS Legacy | CryptoJS Legacy 模式(03-rabbit_js.py )生成:de68add3ec9b7b3f | s6，xfq-20260224-02.md:498 | source-report | 脚本不在正文 |
| C21 | 全 0 输入的附录第一块被写成 3D2DF3C83EF627A1E97FC38487E2519C | 3D2DF3C83EF627A1E97FC38487E2519C。我们的 01-rabbit_standard.py 完全吻合并通过了该附录官 | s6，xfq-20260224-02.md:473 | source-report | 引导句在第 470 行，密钥和明文的具体全 0 字节未在本行写全；未对照附录 |
| C22 | 16 字节密钥流被写成 b16925fbcda896f140cfa657c0899682 | 完整密钥流(16字节): b16925fbcda896f140cfa657c0899682 | s3，xfq-20260224-02.md:283 | source-report | 未重算 |

## 验证与限制

- 没有本地计算，也没有打开 RFC 4503 或 crypto-js 仓库。成功与否停留在作者自述。
- C5 把 G 写成 (state+counter) 的平方；C8 写成先加 constant 再平方。两句同时保留，不选一个当标准式。
- C15 的整段倒序和 C18 的前 8 字节异或不一起成立。本卡不把 `keystream[::-1]` 收进参数。
- 第 6 节的提取函数和字交换代码断行粘连。C11 只保留那一条仍完整的赋值。
- 未知：IV 简化成直接异或到密钥的非标准做法没有例子；CyberChef 被写成类似 38a6c7 的输出没有完整十六进制；附件脚本不在本篇。
