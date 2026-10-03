---
schema_version: 2
id: grok-fangdi-rs6-p-cookie-parameters
document_type: reference
original_date: '2026-07-31'
archived_date: '2026-10-02'
scope:
  targets: [fangdi]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ai-assisted-20260731-01.md#整体结构"
    basis: source-report
  - id: s2
    ref: "./ai-assisted-20260731-01.md#lcg与fisher-yates置换"
    basis: source-report
  - id: s3
    ref: "./ai-assisted-20260731-01.md#property57的codebook"
    basis: source-report
  - id: s4
    ref: "./ai-assisted-20260731-01.md#整体公式"
    basis: source-report
  - id: s5
    ref: "./ai-assisted-20260731-01.md#one选中哪个wrapper"
    basis: source-report
  - id: s6
    ref: "./ai-assisted-20260731-01.md#two定位mainfunction"
    basis: source-report
  - id: s7
    ref: "./ai-assisted-20260731-01.md#env-fixed字段"
    basis: source-report
  - id: s8
    ref: "./ai-assisted-20260731-01.md#会话相关字段"
    basis: source-report
  - id: s9
    ref: "./ai-assisted-20260731-01.md#外层两层加密"
    basis: source-report
  - id: s10
    ref: "./ai-assisted-20260731-01.md#站点的反调试手段"
    basis: source-report
  - id: s11
    ref: "./ai-assisted-20260731-01.md#识别到分析手段就换算法"
    basis: source-report
  - id: s12
    ref: "./ai-assisted-20260731-01.md#codebook差点被误判成session-derived"
    basis: source-report
  - id: s13
    ref: "./ai-assisted-20260731-01.md#落地验证"
    basis: source-report
  - id: s14
    ref: "./ai-assisted-20260731-01.md#落地验证-2"
    basis: source-report
  - id: s15
    ref: "./ai-assisted-20260731-01.md#完整链路回顾"
    basis: source-report
  - id: s16
    ref: "./ai-assisted-20260731-01.md#决定性发现雪崩混淆其实是字段序列化"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s2, s3, s4, s5, s6, s7, s8, s9]
    basis: source-report
    limits: 只记录来源写出的 LCG 常数、Huffman 权重、codeUid 取段、basearr 段前缀和两层 AES 的 key/iv 角色。derive_keys、encryptMode2、自定义 base64 字母表、完整 codebook 和洗牌表 gX 都不在正文里。
  - name: request-chain
    anchor: request-chain
    sources: [s1, s15, s16]
    basis: source-report
    limits: 链路顺序来自作者的清单。通用瑞数挑战卡没有这些常数；本卡也不把 12/12 当成已复核结果。
  - name: risk-control
    anchor: risk-control
    sources: [s10, s11, s12]
    basis: source-report
    limits: debugger、计时和 Proxy 检测是作者描述。环境指纹一层作者写明仍要真实浏览器。vmtrace 未开源，观察步骤不可照做。
  - name: validation
    anchor: validation
    sources: [s13, s14]
    basis: source-report
    limits: 字段是否被拒、12/12 和 7/7 都是作者自述。本次没有请求，也没有对照字节。
relations:
  - type: derived_from
    target: "./ai-assisted-20260731-01.md#fangdi-rs6-逆向四篇p-cookie-链路lcg-置换与-huffmancodeuid-crc32basearr-结构"
  - type: supplements
    target: ../products/ruishu-rs6-challenge.md#常见链路
tags: [fangdi, ruishu, rs6, source-report]
---

# fangdi RS6 的 P cookie 参数

这张卡回答 fangdi 这一份 rs6 在来源里把 P cookie 拆成了哪些可指名的参数。通用瑞数产品卡只写挑战页和 cookie 刷新，没有这里的 LCG、Huffman、codeUid 或 basearr。依据停在 `source-report`。

<a id="parameters"></a>
## 参数

分开置换、压缩、codeUid、basearr 和两层 AES。密钥派生函数和自定义 base64 字母表来源没有写出。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | state = (state & 0xFFFF) * 15679 + 2531011 | s2，第 152 行 | source-report | fangdi 这一份 LCG | 初始种子不在这一行 |
| C2 | 第898次调用后会reseed回初始种子 | s2，第 154 行 | source-report | 作者称跨会话固定 | 未复算调用次数 |
| C3 | i = 900 | s2，第 163 行 | source-report | Fisher-Yates 起点 | 数组初值未给出；同行还有 PRNG() % i |
| C4 | 符号0的频率权重是36,符号255的频率权重是6,其余254个符号权重都是1 | s3，第 169 行 | source-report | property57 | 完整 codebook 未列出 |
| C5 | 184 >> accbits | s3，第 181 行 | source-report | 编码收尾 | 未对照真实输出 |
| C6 | codeUid = (CRC32(one) ^ CRC32(two)) & 0xFFFF | s4，第 227 行 | source-report | basearr 的 sec3 | CRC32 变体未写明 |
| C7 | functionsNameSort[keys33].wrapper | s4，第 227 行 | source-report | one 的输入 | 排序表 opdata 未给出 |
| C8 | 段边界(累积大小) = 38, 46(38+8), 53(46+7), 56(53+3) | s5，第 243 行 | source-report | 四段 wrapper | c4 二次排序没有表 |
| C9 | mainFunction.substr(741 * keys34, 741) | s4，第 227 行 | source-report | two 的输入 | 150000 只是长度上限 |
| C10 | basearr = numarrJoin( | s7，第 319 行 | source-report | 段前缀 | 各段内部字节未逐项展开 |
| C11 | sec6[1] = encryptMode2(decrypt(keys[22]), keys[16], 1) | s8，第 337 行 | source-report | 会话段 | encryptMode2 本体未写 |
| C12 | AES-CBC(key17, iv = key2[:16]) | s9，第 350 行 | source-report | property57 之后 | key 字节不在正文 |
| C13 | 第二层AES-CBC(key16,IV是随机值) | s9，第 357 行 | source-report | frame 之外 | 自定义 base64 字母表未给出 |

<a id="request-chain"></a>
## 请求链

来源把顺序写成：412 里的 nsd/cd，派生 45 个 key，VM 生成约 293KB 的 kH，算 codeUid，拼约 150 字节 basearr，LCG 与 Fisher-Yates，property57，两层 AES-CBC，自定义 base64，再提交。第 82 行以 `curl请求412挑战` 开头。第365行复述同一顺序，并写明约 80 字节环境段可复用、约 70 字节随会话变。第 310 行把所谓雪崩改写成字段拼接。O 只作完成标记，不参与加密。

<a id="risk-control"></a>
## 反分析

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C14 | 代码里随机撒debugger语句 | s10，第 93 行 | source-report | 生成出的签名代码 | 没有补丁字节 |
| C15 | 插桩插太多,跑得慢了会被识别 | s10，第 96 行 | source-report | 全指令挂钩 | 阈值未给出 |
| C16 | 发现有人用Proxy包底层函数,直接换一套算法 | s11，第 101 行 | source-report | Proxy 包装 | 替换后的算法未写 |
| C17 | 环境指纹采集这一层,目前只能靠真实浏览器 | s11，第 104 行 | source-report | navigator/screen/canvas | 作者称未绕开 |
| C18 | 插桩本身触发了站点的某种检测 | s12，第 189 行 | source-report | codebook 那一轮 | decoy 分支没有opcode |

<a id="validation"></a>
## 验证与限制

来源第 109 行写 sec2、sec3、fixedValue20 改了会直接拒，env 模板和 sec6 的部分字节、占位段改了不影响。第 111 行写连续测试12次全部返回200，空响应 400 被作者归到某次 412 会话。第171行写 256个符号全部一致。第165行写 920次(i,j)对全部精确命中。第 263 行写 7个全部命中。这些都是作者自述。

缺了 derive_keys、encryptMode2、base64 字母表、完整 codebook 和 gX，就不能从正文单独算出 P。环境指纹按作者说法仍要真实浏览器。产品卡 `ruishu-rs6-challenge` 与 `ruishu-rs6-hybrid` 的 target 是 ruishu，没有上述常数。
