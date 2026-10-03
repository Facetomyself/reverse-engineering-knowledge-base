---
schema_version: 2
id: anti-detection-ruyi-chromium-switch-bom-fingerprint-reference
document_type: reference
original_date: '2026-03-10'
archived_date: '2026-07-13'
scope:
  targets: [chromium-switch-bom-fingerprint]
  client: browser
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260310-01.md#几个关键参数的具体影响
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只整理来源对一篇 WWW 2025 论文的转述。不含 Similarity 公式、Table 3 逐项属性、采集脚本或补丁。文中准确率不是本次测量。
relations:
  - type: derived_from
    target: ./ruyi-20260310-01.md#几个关键参数的具体影响
tags: [chromium, bom, command-line-switch, source-report]
---

# Chromium 启动参数在 BOM 上留下的可检测差异

这张卡只回答一个检索问题：来源把哪些 Chromium 命令行参数说成会改变 JavaScript 可见的 BOM，以及它把反向识别限定在受影响属性子集上。它不提供指纹 JSON、匹配公式或注入补丁。

<a id="risk-control"></a>
## 风险控制信号

来源把信号定义成：单独打开一个启动参数后再从 `window` 递归遍历 BOM，和默认配置比新增、删除或改值。超过 97% 的参数没有可检测影响；有影响的是自动化里常见的那几十个。匹配时只看该参数的影响子集，不比较整份指纹。Chrome 113 到 130 是来源给出的采集范围，不是本卡验证过的版本。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源写「你打开Chromium时带的那些启动参数，很多时候会在浏览器的JavaScript接口上留下可被检测的痕迹。」 | s1，ruyi-20260310-01.md:45 | source-report | 来源对启动参数相对默认 BOM 的边界 | 没有探针或对照实验 |
| C2 | 来源写「在headful模式下，每个版本有40到56个参数会改变BOM。在headless模式下稍少，32到41个。」 | s1，ruyi-20260310-01.md:124 | source-report | 来源转述的 18 个 Chromium 版本 | 不是本次测量，属性清单未逐项列出 |
| C3 | 来源写 headless「在所有18个版本中都能被检测到，影响BOM的8个属性。」 | s1，ruyi-20260310-01.md:132 | source-report | 来源点名的 `--headless` | 8 个属性没有名字；128 之后差异变小但仍存在 |
| C4 | 来源写「` --disable-3d-apis  ` 和  ` --disable-webgl  `」 | s1，ruyi-20260310-01.md:137 | source-report | 来源点名的一对开关 | 同名关系在下一句，不是本行 |
| C5 | 来源写「这两个参数的影响完全一致——论文查了Chromium源码确认它们就是同一个功能的两个名字。开了之后，BOM中WebGL相关的属性全部消失，影响2200多个属性，是所有参数里影响面最大的。」 | s1，ruyi-20260310-01.md:139 | source-report | 紧挨上一行那对开关 | 没有源码位置或属性名单 |
| C6 | 来源写「它会影响BOM的4个属性，在11个版本中可被检测。」 | s1，ruyi-20260310-01.md:143 | source-report | 上一行点名的 `--disable-web-security` | 4 个属性未命名，不是全部 18 个版本 |
| C7 | 来源写「它影响70多到100多个属性（随版本变化），在所有版本中都能被检测。」 | s1，ruyi-20260310-01.md:147 | source-report | 上一行点名的 `--enable-blink-test-features` | 没有具体启动命令 |
| C8 | 来源写「影响60到80个属性，全版本可检测。」 | s1，ruyi-20260310-01.md:151 | source-report | 上一行点名的 `--enable-gpu-benchmarking` | 新增接口未命名 |
| C9 | 来源写「影响26个属性，全版本可检测。」 | s1，ruyi-20260310-01.md:155 | source-report | 上一行点名的 `--dom-automation` | 26 个属性未列出 |
| C10 | 来源写「所以它被22个不同的参数影响。虽然它变化很频繁，但没法用它来判断具体是哪个参数在起作用。」 | s1，ruyi-20260310-01.md:162 | source-report | 上一行点名的 `window._length` | 不能单独当参数分类器 |
| C11 | 来源写「只提取该参数会影响的那几个属性（而不是比较整个指纹）」 | s1，ruyi-20260310-01.md:115 | source-report | 来源的子集匹配范围 | Similarity 公式未给出 |
| C12 | 来源写「对数据集中已知的指纹进行识别，平均成功率84.36%。」 | s1，ruyi-20260310-01.md:170 | source-report | 来源的单参数识别 | 不是本次测量；行末开始解释等价参数 |
| C13 | 来源写多参数随机组合「平均成功率78.15%。」 | s1，ruyi-20260310-01.md:177 | source-report | 来源的多参数采样 | 不是本次测量 |
| C14 | 来源写换到笔记本「平均成功率77.54%，和服务器上的78.15%差距很小。」 | s1，ruyi-20260310-01.md:181 | source-report | 来源的跨设备数字 | 不是本次测量，也没有操作系统对照 |
| C15 | 来源写「有影响的参数数量突然从40多个跳到了53-56个——增加了约30%。同时识别准确率反而下降了（从88%降到64-67%）。」 | s1，ruyi-20260310-01.md:185 | source-report | 来源观察到的 128 版本断点 | 不能把更早版本的清单套到 128 之后 |
| C16 | 来源写「` window._length  ` 的值——虽然它本身不够稳定，但如果和默认值偏差较大，说明浏览器配置被改过。」 | s1，ruyi-20260310-01.md:225 | source-report | 来源的一个高价值属性 | 没有默认值或阈值 |
| C17 | 来源写「WebGL相关属性是否存在——缺失说明3D API被禁用了，这是自动化工具常见的配置。」 | s1，ruyi-20260310-01.md:226 | source-report | 来源的一个高价值属性 | 没有属性名单 |
| C18 | 来源写「` window.openDatabase  ` 是否存在——缺失说明数据库功能被禁用了。」 | s1，ruyi-20260310-01.md:227 | source-report | 来源的一个高价值属性 | 没有版本条件 |
| C19 | 来源写「` window.speechSynthesis  ` 相关属性是否存在——缺失说明语音合成API被禁了。」 | s1，ruyi-20260310-01.md:228 | source-report | 来源的一个高价值属性 | 没有属性名单 |

## 验证与限制

正文没有操作者前提、可执行步骤、验收条件和失败出口，所以不升为流程。准确率、属性个数和版本断点都是来源转述。等价参数（3D API 与 WebGL）和包含关系（语音相关开关）会使「猜中开了哪个参数」低于 100%。只覆盖命令行，不含 `chrome://flags`、扩展和组策略。Docker 与真实硬件、Firefox 和 Safari 都不在来源数据集里。`../../web-reverse/browser-env-objects/fingerprint-overview.md` 的 risk-control 只写宿主对象状态组，不包含启动参数到 BOM diff 的对照，因此不并入。已有的无头绕过和 Chromedriver 归档目标是 `unknown`，写的是源码改写，不是这张参数影响面。
