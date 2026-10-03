---
schema_version: 2
id: ruyi-canvas-randomization-recovery
document_type: reference
original_date: '2025-11-20'
archived_date: '2026-10-02'
scope:
  targets: [canvas-randomization]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ruyi-20251120-01.md#1pixel-recovery-攻击扩展全部阵亡"
    basis: source-report
  - id: s2
    ref: "./ruyi-20251120-01.md#2-brave-farbling业内最强也被击穿"
    basis: source-report
  - id: s3
    ref: "./ruyi-20251120-01.md#2statistical-attack针对-brave-farbling"
    basis: source-report
  - id: s4
    ref: "./ruyi-20251120-01.md#如意解读"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s3]
    basis: source-report
    limits: 只保留笔记写出的偏移、掩码、HMAC/LFSR 名称、稀疏上界和 N=5。没有实现，也没有本地求逆结果。
  - name: risk-control
    anchor: risk-control
    sources: [s4, s2]
    basis: source-report
    limits: 攻破和 100% 复原是来源对论文的转述。不覆盖补环境对象语义。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s3, s4]
    basis: source-report
    limits: 只有防御类别到攻击分支的对应。没有失败出口，不能当成操作流程。
relations:
  - type: derived_from
    target: "./ruyi-20251120-01.md#1pixel-recovery-攻击扩展全部阵亡"
  - type: derived_from
    target: "./ruyi-20251120-01.md#2-brave-farbling业内最强也被击穿"
  - type: derived_from
    target: "./ruyi-20251120-01.md#2statistical-attack针对-brave-farbling"
tags: [canvas-randomization, brave-farbling]
---

# Canvas 随机化的求逆与统计恢复

这张卡检索一件事：笔记如何描述扩展随机化和 Brave Farbling 被恢复，以及风控侧把多次采样用来识别伪装。Canvas / WebGL 对象语义仍以 `../../web-reverse/browser-env-objects/canvas-webgl.md` 为准，指纹对象总纲仍以 `../../web-reverse/browser-env-objects/fingerprint-overview.md` 为准。这里不并入那两张卡。

来源是如意私塾对一篇路易斯安那州立大学论文的转述。依据只到 source-report。N=5、少于 1000 像素和 100% 复原都没有在本次复现。

<a id="parameters"></a>
## 参数

扩展路径在笔记里是可逆运算：固定偏移，或对像素做 XOR。还原先用已知画布求偏移，再从扰动像素减回去。Brave 路径只列出 HMAC、LFSR、逐位 XOR，以及每个 canvas 的稀疏 bit-flip；统计侧是重复渲染后取多数像素。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | pixel = real_pixel + fixed_offset或pixel ^= fixed_mask | s1 ./ruyi-20251120-01.md:161 | source-report | 见 scope | 笔记里的公式碎片，不是扩展或 Brave 的源码摘录，本次未运行求逆。 |
| C2 | 偏移量 = 扰动像素 - 原像素 | s1 ./ruyi-20251120-01.md:229 | source-report | 见 scope | 笔记里的公式碎片，不是扩展或 Brave 的源码摘录，本次未运行求逆。 |
| C3 | real_pixel = noisy_pixel - offset | s1 ./ruyi-20251120-01.md:238 | source-report | 见 scope | 笔记里的公式碎片，不是扩展或 Brave 的源码摘录，本次未运行求逆。 |
| C4 | 给每个像素加固定偏移量（+5、-7 等） | s1 ./ruyi-20251120-01.md:216 | source-report | 见 scope | 笔记里的公式碎片，不是扩展或 Brave 的源码摘录，本次未运行求逆。 |
| C5 | 给 RGB 做 XOR 操作 | s1 ./ruyi-20251120-01.md:218 | source-report | 见 scope | 笔记里的公式碎片，不是扩展或 Brave 的源码摘录，本次未运行求逆。 |
| C6 | HMAC | s1 ./ruyi-20251120-01.md:170 | source-report | 见 scope | 只出现算法名，没有密钥、输入或输出长度。 |
| C7 | LFSR | s1 ./ruyi-20251120-01.md:172 | source-report | 见 scope | 没有多项式、抽头或种子。 |
| C8 | 逐位 XOR | s1 ./ruyi-20251120-01.md:174 | source-report | 见 scope | 没有位序或掩码来源。 |
| C9 | 稀疏随机扰动（每个 canvas 仅修改少量像素） | s1 ./ruyi-20251120-01.md:176 | source-report | 见 scope | 这是对论文结果的转述，不是本次测量。 |
| C10 | 每个 Canvas 只扰动少量像素（< 1000） | s1 ./ruyi-20251120-01.md:250 | source-report | 见 scope | 这是对论文结果的转述，不是本次测量。 |
| C11 | 扰动为 bit-flip（随机翻转一位） | s1 ./ruyi-20251120-01.md:252 | source-report | 见 scope | 这是对论文结果的转述，不是本次测量。 |
| C12 | 扰动概率固定 | s1 ./ruyi-20251120-01.md:254 | source-report | 见 scope | 没有概率值。 |
| C13 | 反复渲染 N 次（论文中 N=5 就够） | s1 ./ruyi-20251120-01.md:182 | source-report | 见 scope | 这是对论文结果的转述，不是本次测量。 |
| C14 | 对每个像素检测“出现次数最多的值” | s1 ./ruyi-20251120-01.md:261 | source-report | 见 scope | 这是对论文结果的转述，不是本次测量。 |
| C15 | majority vote----多数投票 | s1 ./ruyi-20251120-01.md:187 | source-report | 见 scope | 这是对论文结果的转述，不是本次测量。 |

<a id="risk-control"></a>
## 风控含义

笔记的检测含义是：随机化输出不是终点，多次采样可以回到真实像素，于是批量伪装会被认出来。固定输出或直接禁止被写成另一类明显特征。对抗方向只写到不可逆、不可统计，或限制读取频率，没有构造。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C16 | 所有随机化防护，包括 Brave Farbling，都能被攻破。 | s1 ./ruyi-20251120-01.md:80 | source-report | 见 scope | 这是对论文结果的转述，不是本次测量。 |
| C17 | 完整恢复原始指纹（100% 精确复原） | s1 ./ruyi-20251120-01.md:152 | source-report | 见 scope | 这是对论文结果的转述，不是本次测量。 |
| C18 | 可对用户进行“多次 Canvas 采样”，统计恢复真实像素，稳稳识别伪装浏览器 | s1 ./ruyi-20251120-01.md:275 | source-report | 见 scope | 识别效果是来源判断，本次未复现。 |
| C19 | 需要构建不可逆、不可统计、非线性的大规模扰动；或限制 Canvas 的读取频率 | s1 ./ruyi-20251120-01.md:278 | source-report | 见 scope | 没有构造方法，只是方向。 |

<a id="decision-flow"></a>
## 防御类别与攻击分支

笔记先把防御分成禁止 API、固定画布、加噪声和过滤脚本。加噪声再分成两支：扩展随机化走求逆，Brave Farbling 走多次采样。固定输出和禁止不走这两支恢复，但被写成会暴露明显特征。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C20 | 对像素加噪声（扩展 + Brave） | s1 ./ruyi-20251120-01.md:105 | source-report | 见 scope | 只保留来源写出的分支，没有失败阈值。 |
| C21 | 直接禁止 Canvas API | s1 ./ruyi-20251120-01.md:101 | source-report | 见 scope | 分类名来自笔记，不是接口清单。 |
| C22 | 输出统一的固定画布 | s1 ./ruyi-20251120-01.md:103 | source-report | 见 scope | 只保留来源写出的分支，没有失败阈值。 |
| C23 | 针对“扩展随机化”→ 可以  直接求逆，把真实 Canvas 完整还原 | s1 ./ruyi-20251120-01.md:127 | source-report | 见 scope | 只保留来源写出的分支，没有失败阈值。 |
| C24 | 针对 Brave Farbling→  多次采样  抵消随机噪声，恢复真实像素 | s1 ./ruyi-20251120-01.md:131 | source-report | 见 scope | 只保留来源写出的分支，没有失败阈值。 |
| C25 | 固定输出 / 阻止 = 明显特征，被检测反识别 | s1 ./ruyi-20251120-01.md:290 | source-report | 见 scope | 没有列出特征项。 |

## 验证与限制

缺 HMAC 输入、LFSR 多项式、bit-flip 概率，以及偏移不恒定时的失败条件。因此不能写成流程。论文数字保持来源转述。
