---
schema_version: 2
id: chromium-webgl-blink-perturbation-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-webgl]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./03-webgl-fingerprint-randomization.md#三编译随机webgl指纹"
    basis: unknown
  - id: s2
    ref: "./03-webgl-fingerprint-randomization.md#二为啥有的webgl指纹-二期"
    basis: unknown
  - id: s3
    ref: "./03-webgl-fingerprint-randomization.md#四修改源码的readpixels函数"
    basis: unknown
  - id: s4
    ref: "./03-webgl-fingerprint-randomization.md#五修改源码的todataurl函数"
    basis: unknown
  - id: s5
    ref: "./03-webgl-fingerprint-randomization.md#三获取浏览器的webgl指纹通过生成图像"
    basis: unknown
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s3, s4, s5]
    basis: unknown
    limits: 只记录作者点名的两个源文件和三个函数。toDataURL 不在 WebGL 上下文文件里。
  - name: parameters
    anchor: parameters
    sources: [s1, s3, s4]
    basis: unknown
    limits: 只记录打乱顺序、0 到 9 的裁剪，以及返回值后追加空格。不整段复制函数。
  - name: risk-control
    anchor: risk-control
    sources: [s2]
    basis: unknown
    limits: browserscan 未通过是作者对上一期的自述，没有该站响应。
relations:
  - type: derived_from
    target: "./03-webgl-fingerprint-randomization.md#三编译随机webgl指纹"
  - type: derived_from
    target: "./03-webgl-fingerprint-randomization.md#四修改源码的readpixels函数"
  - type: derived_from
    target: "./03-webgl-fingerprint-randomization.md#三获取浏览器的webgl指纹通过生成图像"
  - type: derived_from
    target: "./03-webgl-fingerprint-randomization.md#五修改源码的todataurl函数"
  - type: derived_from
    target: "./03-webgl-fingerprint-randomization.md#二为啥有的webgl指纹-二期"
tags: [chromium, webgl, blink, unknown]
---

# Chromium WebGL 源码扰动落在哪些函数

检索问题：这篇合并稿如何改 WebGL 指纹的三条读回路径。JS 宿主对象卡要求扩展列表和 `getExtension` 一致、`readPixels` 写入调用方缓冲；它不包含这里的源码扰动。

<a id="interfaces"></a>
## 接口位置

扩展名列表在 `webgl_rendering_context_base.cc` 的 `getSupportedExtensions`。图像这一路，作者点名 `readPixels` 和 `toDataURL`；前者的修改仍在这个 WebGL 文件的 `ReadPixelsHelper`，后者改到 `html_canvas_element.cc`。所以空格追加不限于 WebGL 画布。示例脚本里 `readPixels` 被注释掉，实际返回的是 `toDataURL`。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 扩展列表位于 webgl_rendering_context_base.cc | s1 03-webgl-fingerprint-randomization.md:111 | unknown | chromium-webgl | 无修订号 |
| C5 | 作者把图像路径收成 readPixels 与 toDataURL。原文：关键函数是`readPixels()`和`toDataURL()`。 | s5 03-webgl-fingerprint-randomization.md:279 | unknown | chromium-webgl | 示例里 readPixels 被注释 |
| C6 | ReadPixelsHelper 仍在 WebGL 上下文文件 | s3 03-webgl-fingerprint-randomization.md:283 | unknown | chromium-webgl | 只定位文件 |
| C10 | toDataURL 位于 html_canvas_element.cc | s4 03-webgl-fingerprint-randomization.md:329 | unknown | chromium-webgl | 不限于 WebGL 画布 |

<a id="parameters"></a>
## 扰动参数

作者把 `getSupportedExtensions` 的返回列表打乱，并认为脚本收走后再哈希就会每次不同。第二篇不再改参数枚举，而是裁剪读像素的宽高：随机分布写成 0 到 9，`width` 减去这个数。作者把这说成裁掉部分像素以改变 `ReadPixelsHelper` 的返回值。粘贴的语句没有下界。

`toDataURL` 的意图是给返回值后面加空格。作者写返回的是 base64，随机追加多个空格，并认为功能不变、哈希变乱。作者同时提醒最新源码可能和粘贴略有差异。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C2 | 作者把 getSupportedExtensions 当成这一路的关键函数 | s1 03-webgl-fingerprint-randomization.md:168 | unknown | chromium-webgl | 是对采集脚本的归纳 |
| C3 | 打乱返回列表后，作者认为哈希每次不同 | s1 03-webgl-fingerprint-randomization.md:169 | unknown | chromium-webgl | 未验证只改顺序是否被忽略 |
| C7 | 裁剪用的分布是 0 到 9 | s3 03-webgl-fingerprint-randomization.md:305 | unknown | chromium-webgl | 粘贴没有下界 |
| C8 | width 减去该随机数 | s3 03-webgl-fingerprint-randomization.md:321 | unknown | chromium-webgl | height 另有对称一行 |
| C9 | 作者把裁剪解释成改变 ReadPixelsHelper 的返回值 | s3 03-webgl-fingerprint-randomization.md:325 | unknown | chromium-webgl | 未讨论宽度不足 |
| C11 | toDataURL 的意图是返回值后加空格 | s4 03-webgl-fingerprint-randomization.md:375 | unknown | chromium-webgl | 源码可能略有差异 |
| C12 | 作者在 base64 后追加随机个空格 | s4 03-webgl-fingerprint-randomization.md:419 | unknown | chromium-webgl | 未验收空格是否影响解析 |

<a id="risk-control"></a>
## 作者写下的检测边界

第二篇说明，只改扩展列表顺序只能盖住一部分站点；还有站点用 WebGL 画出的图取指纹。作者直接写上一期没有通过 browserscan。本篇没有该站的响应，也没有把后来的裁剪或空格写成一次新的通过记录。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 作者写上一期未通过 browserscan | s2 03-webgl-fingerprint-randomization.md:188 | unknown | chromium-webgl | 无响应原文 |

## 验证与限制

文末的站点列表不是结果。示例散列不收入这张卡。没有修订号，本次没有编译。作者认为空格不影响功能，这句话没有另给验收。宽高减去 0 到 9 时如果原尺寸更小，来源没有写会怎样。
