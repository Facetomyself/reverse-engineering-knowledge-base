---
schema_version: 2
id: a-bogus-redacted-vm-family-reference
document_type: reference
original_date: '2026-08-07'
archived_date: '2026-10-02'
scope:
  targets:
    - a_bogus
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ai-assisted-20260807-01.md#加密流程"
    basis: source-report
  - id: s2
    ref: "./ai-assisted-20260807-01.md#那段指纹字节其实是查表算出来的常量"
    basis: source-report
  - id: s3
    ref: "./ai-assisted-20260807-01.md#vm调试的三个通用坑"
    basis: source-report
  - id: s4
    ref: "./ai-assisted-20260807-01.md#小结"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留来源已写出的算法族、壳和字段角色。盐、掩码、RC4 密钥、自定义码表和浏览器偏移表都没有具体值，本卡不补，也不构成可运行实现。
  - name: risk-control
    anchor: risk-control
    sources: [s2, s4]
    basis: source-report
    limits: 指纹段和异步评分都是这一篇对单一脱敏目标的自述。另一枚 MD5 参数的规范化细则不在本卡，避免和更细的 webSign 归档抢同一结论。
  - name: decision-flow
    anchor: decision-flow
    sources: [s3]
    basis: source-report
    limits: 标题写三个坑，正文只落了两个，且没有验收样本。只当作栈式 VM 的观测约束。
relations:
  - type: derived_from
    target: "./ai-assisted-20260807-01.md#加密流程"
tags:
  - a_bogus
  - source-report
---

# a_bogus 的脱敏算法族、非硬件字节和栈观测约束

这张卡只回答三件事：来源把 `a_bogus` 写成哪几层标准算法、那段像指纹的字节从哪来、以及栈式 VM 有哪两个观测坑。不收录盐、掩码、密钥、码表、偏移表或签名样值，也不重写请求。

抖音 Web 的 host 绑定、补参链和验收口径仍看请求面矩阵与 `a_bogus` 产品卡。`x-secsdk-web-signature` 的明文规范化仍看 webSign 归档。本卡不重复这些模块。来源没有公开 URL，平台名保持脱敏。

<a id="parameters"></a>
## 参数机制

来源把 `a_bogus` 放在自定义栈式字节码 VM 里，并写成 SM3 双哈希、改过初始化的 RC4、再加一层可逆位混淆。它强调每一层都是标准算法换了常量，不是自研密码。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 字节码不在明文 JS 里，而是伪装成 zip 头的 base64；剥壳用 `raw[4:8]` 的和作异或密钥，再 raw deflate。来源称三层壳可以只靠静态分析剥完。 | s1，三层外壳 | source-report | 这篇所述 VM 壳 | 校验和与异或式按来源原文理解，未重放字节码 |
| C2 | 常量池来源写为 1001 项明文字符串，函数表 796 个，指令 77 种。双重 SM3 的十六进制串取下标 9 和 18 两个字符。随请求重算的是三处哈希和时间戳；环境串可复用；掩码、密钥、码表不变。 | s1，指令与核心算法 | source-report | 同一篇的字段角色 | 盐和取值常量未给出，不能据此对拍 |
| C3 | 位混淆是 3 个真实字节加 1 个随机字节变成 4 个输出字节，来源称为可逆编码而不是加密。RC4 的 KSA 把 `S` 倒序初始化，并在 `j` 的更新里多一次乘法；PRGA 按来源说法未改。密钥是写死的一个字节，具体值不展开。8 字节前缀要和位混淆主体一起当编码输入。 | s1，位混淆与 RC4 | source-report | 同一篇的编码层 | 掩码分配和密钥字节不在来源正文里 |

<a id="risk-control"></a>
## 风险控制边界

来源先把 payload 里一段每次都变的字节当成 canvas 或 WebGL 指纹，随后写明生成式是 `floor(random() * N)` 加浏览器偏移查表，和真实硬件测量无关。偏移表不展开。

同一篇还写：离线 `a_bogus` 与抓包逐字节一致之后，请求仍不总是被接受，规律不在 `a_bogus` 对不对。来源称这一层内容不参与服务端的独立校验；当场 200 也不等于没被记录。它把异步风险评分和当场拒绝分成两套判断，并举例浏览器码或指纹段异常仍可能返回 200，事后再做设备、账号或 IP 标记。这些都是作者对单一目标的自述。服务端下发的会话材料来源说不能自己算，本卡不记录任何材料值。

<a id="decision-flow"></a>
## 栈观测的两个约束

来源标题写三个通用坑，正文只写了两个，并说换一台栈式 VM 仍可能遇到。

1. 栈指针和数组长度不是一回事。弹栈只把独立指针退一格，不删数组末尾。读数组最后一个元素会读到残留，栈顶要按指针取。
2. 字节码走原生字符串构造时，单步指令轨迹会看到一长串空值。来源改成在关键节点对解释器内部的栈和作用域做快照。

作者写的逐字节一致、第三方实现对拍、以及“签名无效”错误，都保持 source-report。本轮没有字节码、没有抓包，也没有重放。来源自己也写这套观察目前只在这一个目标上验证过。
