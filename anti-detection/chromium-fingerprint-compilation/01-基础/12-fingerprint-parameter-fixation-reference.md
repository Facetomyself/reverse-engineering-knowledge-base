---
schema_version: 2
id: anti-detection-chromium-fingerprint-seed-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-fingerprint-seed]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./12-fingerprint-parameter-fixation.md#第一篇随机指纹-chromium-定制通过传参固定指纹
    basis: unknown
  - id: s1b
    ref: ./12-fingerprint-parameter-fixation.md#一为什么要固定指纹
    basis: unknown
  - id: s2
    ref: ./12-fingerprint-parameter-fixation.md#三重新修改源码
    basis: unknown
  - id: s3
    ref: ./12-fingerprint-parameter-fixation.md#四render进程追加参数
    basis: unknown
  - id: s4
    ref: ./12-fingerprint-parameter-fixation.md#五验证一下
    basis: unknown
  - id: s5
    ref: ./12-fingerprint-parameter-fixation.md#目标
    basis: unknown
  - id: s6
    ref: ./12-fingerprint-parameter-fixation.md#注意的点
    basis: unknown
  - id: s7
    ref: ./12-fingerprint-parameter-fixation.md#一固定字体指纹
    basis: unknown
  - id: s8
    ref: ./12-fingerprint-parameter-fixation.md#二固定audio指纹
    basis: unknown
  - id: s9
    ref: ./12-fingerprint-parameter-fixation.md#三webgl指纹
    basis: unknown
  - id: s10
    ref: ./12-fingerprint-parameter-fixation.md#四固定canvas指纹
    basis: unknown
  - id: s11
    ref: ./12-fingerprint-parameter-fixation.md#五固定ja4指纹
    basis: unknown
  - id: s12
    ref: ./12-fingerprint-parameter-fixation.md#六固定plugins指纹
    basis: unknown
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s1b, s5, s6, s7]
    basis: unknown
    limits: 开关合同来自作者目标段。示例整数和占位符不写入本卡。字体名长表不抄录。
  - name: decision-flow
    anchor: decision-flow
    sources: [s2, s3, s7, s8, s9, s10, s11]
    basis: unknown
    limits: 只保留每个面的入口函数和作者用一句话写出的原理。粘贴函数体不重组。旧随机实现被作者要求删掉，但原文没有删改失败时的出口。
  - name: interfaces
    anchor: interfaces
    sources: [s2, s3, s7, s8, s9, s10, s11, s12]
    basis: unknown
    limits: 路径按原文出现的文件名定位。未在本地树核对行号。
  - name: risk-control
    anchor: risk-control
    sources: [s4, s10]
    basis: unknown
    limits: 第一篇只自述 plugins 的 description 里看见了参数。Canvas 的空高度返回只被作者说成应对 CreepJS，没有检测结果。
relations:
  - type: derived_from
    target: ./12-fingerprint-parameter-fixation.md#四render进程追加参数
  - type: derived_from
    target: ./12-fingerprint-parameter-fixation.md#目标
tags: [chromium, fingerprints, blink, unknown]
---

# `--fingerprints` 种子在哪些 Blink 入口上分叉

这张卡记录作者的开关合同：有正整数种子时各面保持该种子对应的结果，没有开关时改用时间做种子。已有的 canvas、WebGL、audio 和指纹总纲卡描述的是脚本侧对象语义，没有这个跨进程开关，所以不把本篇补进那些卡。第一篇只用 plugins 作示例；第二篇才铺到字体、audio、toDataURL、canvas 和 JA4。

<a id="parameters"></a>
## 开关合同

作者要的行为是：启动参数变化时指纹变化，同一进程随后的访问不再变。第二篇把参数收窄成 int，最大值写为 2,147,483,647，并要求删掉此前的随机实现。没有该开关时，第二篇的目标是每个访问各自随机。字体段另有一个跳过条件：`ignores` 开关字符串里含有 `fonts` 时不进入替换。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C1 | 第一篇只拿 plugins 当例子 | 这里我只用`plugins指纹`作为示例。 | s1，第 30 行 | unknown | 第一篇范围 | 其他面在第二篇 |
| C2 | 参数变化后同一次启动内不再变 | 参数变化时，指纹也会跟着变化。打开网页后的后续访问指纹都不会再变化。 | s1b，第 34 行 | unknown | 作者目标 | 占位参数值不收录 |
| C3 | 换正整数才换一套指纹 | 则指纹固定不变。当正整数更换，则获得一个新指纹。 | s5，第 143 行 | unknown | 第二篇目标 1 | 示例整数不收录 |
| C4 | 缺开关时作者要每次随机 | 则每个访问请求的指纹全部随机生成。 | s5，第 144 行 | unknown | 第二篇目标 2 | 与第一篇“启动后不变”是否冲突，原文未解释 |
| C5 | 旧随机代码要删掉 | 之前的随机生成指纹的代码都需要删掉，全部替换新代码。 | s6，第 148 行 | unknown | 第二篇前提 | 没有列出必须删除的函数清单 |
| C6 | 只接受 int，并给出上界 | `--fingerprints`只能传整数，且最大值为2,147,483,647 | s6，第 149 行 | unknown | 作者的解析方式 | 超界时 `istringstream` 的实际结果未知 |
| C7 | ignores 含 fonts 时跳过字体替换 | if(ignores.find("fonts") == std::string::npos){ | s7，第 207 行 | unknown | CSSFontFamilyValue::Create 的追加文本 | 其他面没有对应 ignores 分支 |

<a id="decision-flow"></a>
## 种子如何进入各面

主进程参数默认到不了渲染进程。作者在 `render_process_host_impl.cc` 创建渲染进程命令行时，若当前进程有 `fingerprints`，就原样追加给子进程。plugins 的 `DOMPlugin::description()` 把该字符串接到原 description 后面；没有该开关时，第一篇的文本改去读 `type` 开关。

第二篇的其他面都是同一模式：有开关就用它做种子，否则用当前时间。字体按种子对一份名字表做 `rand() % 2` 保留，命中则把该字体换成 `monospace`。Audio 把种子模 99 后加到 `sample_rate`。`HTMLCanvasElement::toDataURL` 在结果末尾追加若干空格。Canvas 的 `setFillStyle` 用种子微调颜色；`getImageDataInternal` 在高度为 1 时返回空指针。JA4 段先把开关转给 utility 进程，再从 `ALL` 出发按种子抽掉一部分排除项。plugins 在第二篇没有新代码，只指向旧文。字体名长表和排除项原文都在，本卡不抄。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C8 | description 末尾追加开关字符串 | return res + String(tmp); | s2，第 75 行 | unknown | 第一篇 DOMPlugin::description | 缺开关时读取的是 type |
| C9 | 原理是追加 fingerprints 的字符串 | 给每个plugin的description末尾追加上`--fingerprints`获取的字符串。 | s2，第 79 行 | unknown | 作者对第一篇代码的说明 | 未编译 |
| C10 | 必须把参数传给子进程 | 启动浏览器的参数默认又只能传给主进程，所以我们还要改进程创建程序，将参数传给子进程。 | s3，第 93 行 | unknown | 渲染进程 | 其他进程类型要另看 utility 段 |
| C11 | 渲染进程命令行追加同名开关 | command_line->AppendSwitchASCII("fingerprints", tmp); | s3，第 114 行 | unknown | render_process_host_impl.cc | 只在 HasSwitch 为真时追加 |
| C12 | 字体按种子丢一半 | if (rand() % 2 == 0) {  // 随机选择是否保留每个元素 | s7，第 171 行 | unknown | randomlyRemoveElements | 名字表不抄；作者承认页面字体可能变 |
| C13 | 命中的字体换成 monospace | return MakeGarbageCollected<CSSFontFamilyValue>(res_family); | s7，第 230 行 | unknown | 替换文本中 res_family 为 monospace | 未核对缓存是否仍返回旧值 |
| C14 | sample_rate 加上种子模 99 | sample_rate+tmp | s8，第 282 行 | unknown | OfflineAudioContext 构造文本 | 上一行把 tmp 收成模 99 |
| C15 | toDataURL 末尾加空格 | 原理是修改`toDataURL()`函数，给结尾处随机加上多个空格。 | s9，第 345 行 | unknown | HTMLCanvasElement::toDataURL | 作者称这也会带动 canvas 指纹 |
| C16 | canvas 颜色按种子微调 | 原理是随机微调canvas的RGB颜色。 | s10，第 417 行 | unknown | setFillStyle 追加文本 | 同函数还写了 SetStrokeColor，原文未单独解释 |
| C17 | 高度为 1 的 getImageData 返回空 | if (sh==1){return nullptr;} | s10，第 429 行 | unknown | getImageDataInternal 追加行 | 作者只把它说成应对 CreepJS |
| C18 | JA4 从 ALL 起追加被抽中的排除项 | std::string command("ALL"); | s11，第 489 行 | unknown | ssl_client_socket_impl.cc 替换文本 | 排除项列表不抄 |
| C19 | 作者对 JA4 的原理句 | 原理是随机抽取部分加密函数给去掉。 | s11，第 506 行 | unknown | 该段文末 | 未看握手结果 |

<a id="interfaces"></a>
## 文件名

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C20 | plugins 在 dom_plugin.cc | third_party/blink/renderer/modules/plugins/dom_plugin.cc | s2，第 43 行 | unknown | 第一篇 | 第二篇只留了链接 |
| C21 | 渲染进程转发在 render_process_host_impl.cc | render_process_host_impl.cc | s3，第 95 行 | unknown | 第一篇第四节 | 未核对调用点是否仍是这一处 AppendSwitch |
| C22 | 字体在 css_font_family_value.cc | css_font_family_value.cc | s7，第 157 行 | unknown | CSSFontFamilyValue::Create | 长表不抄 |
| C23 | audio 在 offline_audio_context.cc | offline_audio_context.cc | s8，第 251 行 | unknown | OfflineAudioContext 构造函数 | 未核对签名 |
| C24 | toDataURL 在 html_canvas_element.cc | html_canvas_element.cc | s9，第 290 行 | unknown | HTMLCanvasElement::toDataURL | 作者把此段标题写成 webGL |
| C25 | 填色在 base_rendering_context_2d.cc | base_rendering_context_2d.cc | s10，第 350 行 | unknown | setFillStyle 与 getImageDataInternal | 两处都在该文件 |
| C26 | utility 进程转发在 utility_process_host.cc | utility_process_host.cc | s11，第 438 行 | unknown | JA4 前的进程参数 | 与渲染进程转发是另一文件 |
| C27 | 套件串在 ssl_client_socket_impl.cc | ssl_client_socket_impl.cc | s11，第 460 行 | unknown | 替换 `ALL:!aPSK:!ECDSA+SHA1:!3DES` 的位置 | 只保留文件名 |

<a id="risk-control"></a>
## 作者自己的对照

第一篇的对照是把 `navigator.plugins` 打到控制台，看 description 末尾有没有参数，并宣称固定成功。这是来源自述。Canvas 读像素的空返回被单独说成应对 CreepJS 的反指纹检测，没有附检测输出。第二篇其余面没有对照记录。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C28 | 作者只对 plugins 宣称看见参数 | 发现description中成功追加了我们的参数。固定plugins指纹成功。 | s4，第 133 行 | unknown | 第一篇第五节 | 不外推到字体、audio、JA4 |
| C29 | 空 ImageData 被说成对付 CreepJS | 这里追加一行是为了应对creepjs的反指纹检测。 | s10，第 432 行 | unknown | getImageData 的那一行 | 没有 CreepJS 的前后结果 |

## 验证与限制

不能把 C28 当成全篇验收。字体替换可能改变页面字体，这是作者写明的副作用，不是失败后的回退步骤。第二篇没有“种子没进子进程就停止”的出口，因此本篇不建流程卡。未本地编译，Chromium 版本未知。plugins 第二篇只有外链，具体改动以第一篇和更早的 description 笔记为准，不在这里补代码。
