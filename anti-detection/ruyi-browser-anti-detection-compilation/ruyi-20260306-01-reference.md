---
schema_version: 2
id: ruyi-20260306-v8-bytecode-fingerprint-reference
document_type: reference
original_date: '2026-03-06'
archived_date: '2026-07-13'
scope:
  targets: [v8-bytecode-fingerprint]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260306-01.md#第三步打标签用启发式规则判断指纹行为
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留来源的四条函数级规则、混淆样本依赖和混合脚本结论。不收录拆分采集函数的建议。指标不是本次测量。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留元数据输出、三元组对齐和哈希查表。没有 V8 补丁、哈希算法或权重，不能当成可跑流水线。
relations:
  - type: derived_from
    target: ./ruyi-20260306-01.md#第三步打标签用启发式规则判断指纹行为
tags: [v8, bytecode, fingerprint, source-report]
---

# V8 字节码函数级指纹判定的标签与查表边界

这张卡只回答一个检索问题：来源转述的检测把什么函数标成指纹函数，字节码怎样和执行轨迹对齐，部署时查的是什么，以及匿名函数、没见过的混淆和四条规则之外为什么不算覆盖。不提供模型或引擎补丁。

<a id="risk-control"></a>
## 函数级标签

来源不看源码，而在 V8 编译之后、执行之前看字节码模式。正例来自四条规则：Canvas 先写文本再读图，字体测量次数和 font 取值都要过阈值，Audio 最后读 getChannelData，WebRTC 走 SDP。任一命中即标为指纹函数。没把混淆样本放进训练时，字节码模型仍会失效。来源还写所有指纹脚本都混有正常函数，所以不能按脚本整段拦截。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 在JavaScript被V8引擎编译成字节码之后、实际执行之前，去分析字节码的模式。 | s1，ruyi-20260306-01.md:49 | source-report | 来源选择的检测层 | 没有改过的 V8 |
| C2 | 写入的文本至少10个字符，还没有调用save/restore/addEventListener。 | s1，ruyi-20260306-01.md:96 | source-report | 来源的 Canvas 规则后半 | 前一行才写 fillText 与 toDataURL |
| C3 | 属性被设置了20种以上不同的值。 | s1，ruyi-20260306-01.md:99 | source-report | 来源的字体规则 | 前一行才写 measureText 超过 20 次 |
| C4 | 这些音频API，最后又调了  ` getChannelData  ` | s1，ruyi-20260306-01.md:102 | source-report | 来源的 Audio 规则 | 振荡器与压缩器在上一行 |
| C5 | 这是在通过WebRTC的SDP交换过程获取本地IP地址。 | s1，ruyi-20260306-01.md:106 | source-report | 来源对 WebRTC 规则的解释 | 不记录地址 |
| C6 | 符合上述任一规则的函数标记为"指纹函数"，其余标记为"非指纹函数"。 | s1，ruyi-20260306-01.md:108 | source-report | 四条规则的或关系 | 规则外没有标签 |
| C7 | 如果模型完全没见过混淆后的字节码模式，依然会失效。 | s1，ruyi-20260306-01.md:175 | source-report | 来源的抗混淆表第一行 | 百分比未复测 |
| C8 | 100%的指纹脚本都是"混合脚本" | s1，ruyi-20260306-01.md:182 | source-report | 来源的脚本构成统计 | 不是本次统计 |
| C9 | 如果按脚本维度一刀切地拦截，必然会破坏那些和指纹函数同属一个脚本的正常功能。 | s1，ruyi-20260306-01.md:185 | source-report | 来源对脚本级拦截的反对 | 没有功能回归记录 |
| C10 | 如果有人发明了一种全新的指纹方法，这些规则覆盖不到，模型也就学不到。 | s1，ruyi-20260306-01.md:195 | source-report | 标签来源的天花板 | 没有新指纹对照 |

<a id="decision-flow"></a>
## 对齐与查表

来源改 DoFinalizeJobImpl，使字节码带上脚本 URL、脚本 ID 和函数名，并只保留指令名。轨迹和字节码靠这三项对齐，匿名函数因此被丢掉。部署时不跑在线推理：编译一个函数就算一次字节码哈希，命中列表才拦截。范围只写了 V8。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C11 | 让它在生成字节码时同时输出三个信息：  ** 脚本URL、脚本ID、函数名  ** 。 | s1，ruyi-20260306-01.md:63 | source-report | 来源对 DoFinalizeJobImpl 的改动 | 没有补丁或版本 |
| C12 | 只保留指令序列，混淆对它的影响就大大减小了。 | s1，ruyi-20260306-01.md:79 | source-report | 来源去掉操作数的理由 | 没见过混淆样本时仍会失效 |
| C13 | 对应的方式是三元组匹配——  ** 脚本URL + 脚本ID + 函数名  ** 。 | s1，ruyi-20260306-01.md:112 | source-report | 轨迹与字节码的对齐键 | 匿名函数没有函数名 |
| C14 | 匿名函数没有函数名，没法做匹配，所以全部被排除了。 | s1，ruyi-20260306-01.md:114 | source-report | 来源的训练集对齐 | 约 38% 未复核 |
| C15 | 运行时，V8每编译一个函数，就算一次字节码哈希，在列表里查一下 | s1，ruyi-20260306-01.md:139 | source-report | 来源的部署路径 | 哈希算法不在正文 |
| C16 | 匹配上了就拦截，匹配不上就放行 | s1，ruyi-20260306-01.md:140 | source-report | 来源的查表结果 | 没有拦截后的页面定义 |
| C17 | 只适用于V8引擎 | s1，ruyi-20260306-01.md:197 | source-report | Chrome、Edge、Brave 等 Chromium | 其他引擎要各自训练 |

## 验证与限制

`canvas` 与 `browser-fingerprint` 不包含字节码哈希或这四条函数级规则。unknown 上的 decision-flow 也不是这个目标，所以不并入。训练超参和结果表没有验收、失败出口，不升为流程。文末把采集拆开以躲开函数级检测的说法不进入本卡。
