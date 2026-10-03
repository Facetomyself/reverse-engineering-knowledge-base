---
schema_version: 2
id: anti-detection-ruyi-fingerprint-pro-server-vid-reference
document_type: reference
original_date: '2026-02-25'
archived_date: '2026-07-13'
scope:
  targets: [fingerprint-pro-server-vid]
  client: browser
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260225-01.md#三核心发现
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只整理来源对一篇未具名论文的转述。不含 VID 原值、Cookie 名或值、请求路径、权重表和工具版本。文中比例不是本次测量。
relations:
  - type: derived_from
    target: ./ruyi-20260225-01.md#三核心发现
tags: [fingerprint-pro, risk-control, source-report]
---

# Fingerprint Pro 服务端 VID：属性权重、Cookie 覆盖与统一化

这张卡只回答一个检索问题：来源把商业服务端访客标识说成怎样一种不靠单项高熵属性精确哈希的识别，以及它点名哪些锚点和失效的随机化。它不提供接口、请求序列或改写步骤。

<a id="risk-control"></a>
## 风险控制信号

来源把服务端信号定义成：原始浏览器属性上传后由服务器计算 VID，并用模糊匹配容忍一部分属性变化。Cookie 被写成覆盖单项属性修改的锚点，IP 的 /24 变化被写成另一锚点。Canvas、WebGL、Audio 的宿主对象卡不包含这个 VID 规则。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源把 Cookie 与 IP 写成核心锚点，浏览器属性写成辅助。来源写「Cookie + IP 地址是核心锚点，浏览器属性反而是辅助」 | s1，ruyi-20260225-01.md:62 | source-report | 来源对这篇未具名论文的结论摘要 | 论文题名和实验日志都不在正文 |
| C2 | 来源写服务端指纹是把原始浏览器属性传到服务器再计算 VID。来源写「服务端指纹的特点：把原始浏览器属性传到服务器，服务器用算法计算 VID。」 | s1，ruyi-20260225-01.md:100 | source-report | 来源对服务端指纹的定义 | 没有请求路径、字段表或算法 |
| C3 | 来源摘录 Fingerprint Pro 对高熵浏览器属性权重更低。来源写「Fingerprint Pro appears to place less weight on」 | s1，ruyi-20260225-01.md:140 | source-report | 来源摘录的 Fingerprint Pro 权重判断 | 英文摘录被换行切开，权重表不在正文 |
| C4 | 来源摘录 Cookie 覆盖对浏览器属性的任何单项修改。来源写「Cookies override any and all individual modifications to」 | s1，ruyi-20260225-01.md:142 | source-report | 来源摘录的覆盖关系 | 没有 Cookie 值，也不写产品 Cookie 名 |
| C5 | 来源写服务端 Fingerprint Pro 在合成指纹上只有部分唯一。来源写「只有 66.7%（Mac）和 76.2%（Windows）是唯一的」 | s1，ruyi-20260225-01.md:154 | source-report | 来源转述的合成指纹唯一率 | 不是本次测量，样本构造不在正文 |
| C6 | 来源写 Canvas 单改后服务端仍能模糊匹配。来源写「Canvas 改了也没用，服务端能模糊匹配」 | s1，ruyi-20260225-01.md:175 | source-report | 来源对单属性测试的解读 | 没有匹配距离或阈值 |
| C7 | 来源写 AudioContext、Plugins、屏幕分辨率单改都没用。来源写「AudioContext、Plugins、屏幕分辨率——改了都没用」 | s1，ruyi-20260225-01.md:176 | source-report | 来源对低权重属性的归纳 | 对应表格没有原始 VID |
| C8 | 来源把 colorDepth 和 hardwareConcurrency 写成真正有用的硬件属性。来源写「colorDepth、hardwareConcurrency 这些硬件属性」 | s1，ruyi-20260225-01.md:177 | source-report | 来源点名的高权重硬件属性 | 没有各属性的分数 |
| C9 | 来源写浏览器、操作系统和 IP 都换了，只要那两个 Cookie 还在，VID 就不变。来源写「哪怕你把浏览器、操作系统、IP 全换了，只要这两个 Cookie 还在，VID 就不变。」 | s1，ruyi-20260225-01.md:184 | source-report | 来源对 Cookie 仍在时的 VID 稳定性 | 不记录 Cookie 名或值；有效期叙述未单列验证 |
| C10 | 来源写同一个 /24 内换 IP 没有影响。来源写「同一个 /24 网段内换 IP：没影响」 | s1，ruyi-20260225-01.md:190 | source-report | 来源对同网段换 IP 的报告 | 没有网段样本 |
| C11 | 来源写跨网段换 IP 后，Canvas、Fonts、WebGL Shader 的修改才会被当成新用户。来源写「跨网段换 IP：Canvas、Fonts、WebGL Shader 这些属性改了才会被识别成新用户」 | s1，ruyi-20260225-01.md:191 | source-report | 来源对跨网段换 IP 的报告 | 没有跨网段的判定规则 |
| C12 | 来源摘录只有 Firefox RFP 和 Tor 能阻止再次识别。来源写「are the only tools that successfully prevent re-identification.」 | s1，ruyi-20260225-01.md:207 | source-report | 来源摘录的工具结论 | 工具版本不在正文 |
| C13 | 来源写 Brave 的 Farbling 在客户端有效，服务端直接无视。来源写「在客户端检测面前很有效，但服务端直接无视。」 | s1，ruyi-20260225-01.md:232 | source-report | 来源对 Brave Farbling 的边界 | 没有 Farbling 实现或复测 |
| C14 | 来源把有效路线归纳为统一化而不是随机化。来源写「不是"随机化"，而是"统一化"——让所有用户看起来一样。」 | s1，ruyi-20260225-01.md:247 | source-report | 来源对有效工具共同点的归纳 | 没有统一化的 API 清单 |
| C15 | 来源把重要性排成 Cookie、IP、硬件属性、软件属性。来源写「Cookie > IP > 硬件属性（colorDepth、hardwareConcurrency）> 软件属性（Canvas、Fonts）」 | s1，ruyi-20260225-01.md:263 | source-report | 来源给出的属性排序 | 排序是作者摘要，不是测量表 |
| C16 | 来源写 IP 要换到不同 /24 才有意义。来源写「IP 地址要换到不同 /24 网段才有意义」 | s1，ruyi-20260225-01.md:271 | source-report | 来源给指纹浏览器的建议 | 建议没有验收条件，不构成流程 |

## 验证与限制

正文的实验步骤停在“改一个属性再看 VID”，没有操作者输出、通过条件和失败出口，所以不升为流程。`../../web-reverse/browser-env-objects/fingerprint-overview.md` 以及 canvas、webgl、navigator、storage 卡只覆盖宿主对象状态，不包含 Fingerprint Pro 的服务端 VID 权重，因此不并入。产品 Cookie 名和任何 Cookie 值都不进入本卡。
