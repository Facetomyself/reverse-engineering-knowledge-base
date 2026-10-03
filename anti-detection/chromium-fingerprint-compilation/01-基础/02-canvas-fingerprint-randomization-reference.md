---
schema_version: 2
id: chromium-canvas-blink-perturbation-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-canvas]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./02-canvas-fingerprint-randomization.md#三编译随机canvas指纹"
    basis: unknown
  - id: s2
    ref: "./02-canvas-fingerprint-randomization.md#四还不够随机"
    basis: unknown
  - id: s3
    ref: "./02-canvas-fingerprint-randomization.md#四修改源码"
    basis: unknown
  - id: s4
    ref: "./02-canvas-fingerprint-randomization.md#五绕过creepjs的反修改指纹检测"
    basis: unknown
  - id: s5
    ref: "./02-canvas-fingerprint-randomization.md#二为啥有的canvas指纹-二期"
    basis: unknown
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s3, s4]
    basis: unknown
    limits: 只记录作者点名的文件和函数。没有源码树可核对签名是否仍在。
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s3]
    basis: unknown
    limits: 只记录作者写出的偏移、空格和颜色扰动范围。不整段复制替换函数。
  - name: risk-control
    anchor: risk-control
    sources: [s3, s4, s5]
    basis: unknown
    limits: creepjs 与 browserscan 的检测方式是作者的解释。通过句不升格。
relations:
  - type: derived_from
    target: "./02-canvas-fingerprint-randomization.md#三编译随机canvas指纹"
  - type: derived_from
    target: "./02-canvas-fingerprint-randomization.md#五绕过creepjs的反修改指纹检测"
  - type: derived_from
    target: "./02-canvas-fingerprint-randomization.md#二为啥有的canvas指纹-二期"
  - type: derived_from
    target: "./02-canvas-fingerprint-randomization.md#四还不够随机"
  - type: derived_from
    target: "./02-canvas-fingerprint-randomization.md#四修改源码"
tags: [chromium, canvas, blink, unknown]
---

# Chromium Canvas 源码扰动落在哪些函数

检索问题：这篇合并稿把 Canvas 扰动写进哪个 Blink 文件、改了什么量，以及作者如何解释 creepjs 和 browserscan。JS 宿主对象那张卡只要求绘制状态和读回一致，不包含这些源码位置。

<a id="interfaces"></a>
## 接口位置

两篇都改 `base_rendering_context_2d.cc`。第一篇替换两个 `fillText` 重载，并再改 `measureText`。第二篇改 `setFillStyle`；作者写最新源码可能和粘贴略有差异，但自己认为改颜色就能改指纹。creepjs 那一节再改 `getImageDataInternal`。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | fillText 路径在 base_rendering_context_2d.cc | s1 02-canvas-fingerprint-randomization.md:99 | unknown | chromium-canvas | 无修订号 |
| C6 | 颜色路径仍是这个文件 | s3 02-canvas-fingerprint-randomization.md:270 | unknown | chromium-canvas | 同一文件的后一节 |

<a id="parameters"></a>
## 扰动参数

`fillText` 在进入原来的绘制前，把 x 和 y 各加上 `getRandomIntForFoo4Modern()`。作者写这个数取 0 到 2，并且每次调用都加；偏移太大作者认为会把图形弄乱。`measureText` 则按作者的概括，随机给文字追加一个空格，用来改变测量尺寸。

颜色一节不是改填充字符串本身的常量。作者在 `setFillStyle` 里追加两行，并写这是给 creepjs 用的。字符串颜色分支里，解析后的颜色分量被加上 `rand() % 5` 这一类小模数。这里只保留这个范围，不把整段函数再贴一遍。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C2 | fillText 的 x 加上该随机函数 | s1 02-canvas-fingerprint-randomization.md:135 | unknown | chromium-canvas | 不复制整个替换函数 |
| C3 | 随机数取 0 到 2 | s1 02-canvas-fingerprint-randomization.md:151 | unknown | chromium-canvas | 未核对种子是否跨进程稳定 |
| C4 | 每次 fillText 都偏移，过大则作者认为图形混乱 | s1 02-canvas-fingerprint-randomization.md:152 | unknown | chromium-canvas | 无单独的上限实验 |
| C5 | measureText 随机追加一个空格 | s2 02-canvas-fingerprint-randomization.md:203 | unknown | chromium-canvas | 作者概括；粘贴代码还有 tmp 条件 |
| C7 | 作者用改变颜色来改变指纹。原文：通过改变canvas颜色来改变指纹。 | s3 02-canvas-fingerprint-randomization.md:332 | unknown | chromium-canvas | 作者承认源码可能略有差异 |
| C8 | setFillStyle 追加的两行被作者写成过 creepjs | s3 02-canvas-fingerprint-randomization.md:351 | unknown | chromium-canvas | 作者自述，本次未打开该站 |
| C9 | 字符串颜色分量加上 rand 模 5 这一档 | s3 02-canvas-fingerprint-randomization.md:384 | unknown | chromium-canvas | 只引用这个范围 |

<a id="risk-control"></a>
## 作者解释的检测

作者写 creepjs 和 browserscan 对随机改指纹比较严，改完仍可能被当成篡改。对 browserscan，作者的解释是同一时间点会生成两次 canvas 指纹做对比，所以纯随机对不上；后面的 `rand()` 被作者用来让同一时间点得到相同的数。对 creepjs，作者写成生成两张一样的图再逐帧对比，不同就视为篡改。对应的源码句是 `getImageDataInternal` 在 `sh==1` 时返回空。作者称这样就能绕过，原文把函数写成了 getImageDate。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C10 | 作者点名这两站会识别随机改动。原文：creepjs和browserscan这2个网站对指纹的检测比较严格，随机修改了指纹后，很容易无法通过网站的反指纹修改检测 | s5 02-canvas-fingerprint-randomization.md:223 | unknown | chromium-canvas | 无响应记录 |
| C11 | browserscan 被写成同一时间点取两次再对比 | s3 02-canvas-fingerprint-randomization.md:396 | unknown | chromium-canvas | 同时刻 rand 相同只是作者的解释 |
| C12 | creepjs 被写成两图逐帧对比 | s4 02-canvas-fingerprint-randomization.md:409 | unknown | chromium-canvas | 未核对 creepjs 源码 |
| C13 | sh==1 时返回 nullptr | s4 02-canvas-fingerprint-randomization.md:437 | unknown | chromium-canvas | 合法 1 像素读取的后果来源没写 |
| C14 | 作者把该返回值写成绕过 creepjs | s4 02-canvas-fingerprint-randomization.md:440 | unknown | chromium-canvas | 成功句只算来源自述 |

## 验证与限制

本篇列出了检测站点，也写了“再看看是不是每次都随机”。这些都不是结果记录。示例散列不收入这张卡。没有修订号，本次没有编译，作者的通过叙述保持来源自述。`sh==1` 返回空会不会打断正常读像素，来源没有讨论。
