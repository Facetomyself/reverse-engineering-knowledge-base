---
schema_version: 2
id: anti-detection-chromium-plugins-fingerprint-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-plugins-fingerprint]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./07-plugins-fingerprint-randomization.md#一什么是plugins指纹
    basis: unknown
  - id: s2
    ref: ./07-plugins-fingerprint-randomization.md#二如何获取自己的plugins指纹
    basis: unknown
  - id: s3
    ref: ./07-plugins-fingerprint-randomization.md#三chromium编译-随机plugins指纹
    basis: unknown
  - id: s4
    ref: ./07-plugins-fingerprint-randomization.md#四在线指纹验证网站
    basis: unknown
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: unknown
    limits: 只保留作者对 plugins 指纹用途和唯一性的原句。未对照真实站点，也未复现采集结果。
  - name: parameters
    anchor: parameters
    sources: [s2]
    basis: unknown
    limits: 只记录脚本文本里的拼接字段。不收录作者贴出的散列样例，也不把该脚本当成可复用的采集器。
  - name: decision-flow
    anchor: decision-flow
    sources: [s3]
    basis: unknown
    limits: 只记录 DOMPlugin::description 末尾追加一位十进制数这一处文本形态。作者称每次刷新都变，没有失败出口，不能当成已验收流程。
  - name: interfaces
    anchor: interfaces
    sources: [s3, s4]
    basis: unknown
    limits: 文件路径和两个站点名来自原文。站点没有通过条件，ninja 命令也没有错误分支。
relations:
  - type: derived_from
    target: ./07-plugins-fingerprint-randomization.md#二如何获取自己的plugins指纹
  - type: derived_from
    target: ./07-plugins-fingerprint-randomization.md#三chromium编译-随机plugins指纹
tags: [chromium, plugins, blink, unknown]
---

# Plugins 指纹采集串与 description 后缀

这张卡只回答两件事：作者怎样把 `navigator.plugins` 收成一条字符串，以及他在哪一个 Blink 函数末尾追加一位数字。它不覆盖命令行种子，那是另一篇传参固定笔记。`navigator` 的已有参考卡只描述 PluginArray 的集合语义，没有这条源码位置。

<a id="risk-control"></a>
## 检测面

作者把 plugins 指纹写成一种在线追踪：把已安装插件信息收成一条独特指纹，并写明它单独的唯一性不高，要和其他指纹一起用。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C1 | plugins 指纹被写成在线追踪技术 | "Plugins 指纹"(browser plugin fingerprinting)是一种在线追踪技术。 | s1，第 24 行 | unknown | 作者这篇笔记 | 未对照站点实现 |
| C2 | 作者认为单独唯一性不足 | plugins指纹唯一性不是特别高，需要配合其他指纹一起使用。 | s1，第 26 行 | unknown | 作者这篇笔记 | 没有量化 |

<a id="parameters"></a>
## 采集串

控制台脚本遍历 `navigator.plugins`。每个插件先拼 `name`、`description`、`filename`，字段之间是 `::`。插件上的 MIME 再拼成 `type~suffixes`，多项用逗号接在第三个 `::` 后面。全部插件用分号连成一条字符串，再交给 SHA-256。原文随后贴了一段散列，本卡不收录。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C3 | 插件主字段用双冒号连接 | plugin.name + '::' + plugin.description + '::' + plugin.filename | s2，第 55 行 | unknown | 这段脚本 | 空列表时脚本另返回固定短句，本卡不展开 |
| C4 | MIME 用波浪线连接类型和后缀 | mimeType.type + '~' + mimeType.suffixes | s2，第 61 行 | unknown | 这段脚本 | 未验证与 CreepJS 的字段顺序是否相同 |
| C5 | 多插件用分号连接 | return pluginsString.join(';'); | s2，第 74 行 | unknown | 这段脚本 | 只看到文本 |

<a id="decision-flow"></a>
## description 后缀

作者假设 Chromium 已经编译过。改动点是 `third_party/blink/renderer/modules/plugins/dom_plugin.cc` 的 `DOMPlugin::description()`。原文先返回 `plugin_info_->Description()`，替换文本改成原描述加上 `getRandomIntForFoo8Modern()` 的十进制结果。该函数用 `uniform_int_distribution` 取 `0` 到 `9`。作者把原理写成：给每个 plugin 的 description 末尾加随机数，从而让哈希变化。编译命令是 `ninja -C out/Default chrome`。作者接着称每次刷新都随机。这里没有“签名对不上就停止”的失败出口，所以只保留改动位置，不做成流程卡。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C6 | 改动文件是 dom_plugin.cc | third_party/blink/renderer/modules/plugins/dom_plugin.cc | s3，第 92 行 | unknown | 作者点名的树 | 未核对当前树是否仍有该函数 |
| C7 | 随机范围是 0 到 9 | std::uniform_int_distribution<int> distribution(0, 9); | s3，第 114 行 | unknown | 这段替换文本 | 生成器以 time 播种，同秒行为未知 |
| C8 | description 返回原串加该数字 | return tmp + String(std::to_string(getRandomIntForFoo8Modern())); | s3，第 120 行 | unknown | 这段替换文本 | 未编译 |
| C9 | 作者把目的写成改变哈希 | 此处原理是给每个plugin的description末尾加个随机数，实现hash的指纹随机 | s3，第 124 行 | unknown | 作者自述 | 成功句不外推 |

<a id="interfaces"></a>
## 位置与外部页面

除 `dom_plugin.cc` 外，原文只点了两个页面：CreepJS 与 `ip77.net`。没有写哪一项算通过。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C10 | 作者点名 CreepJS | https://abrahamjuliot.github.io/creepjs/ | s4，第 137 行 | unknown | 原文列表 | 无通过条件 |
| C11 | 作者另点 ip77.net | https://ip77.net/ | s4，第 138 行 | unknown | 原文列表 | 无通过条件 |

## 验证与限制

作者写“编译后每次刷新时 plugins 指纹都是随机的了”。这是来源自述，本轮没有编译，也不能把它写成已验收。第 86 行的散列样例故意不进入本卡。函数签名、包含头文件是否仍匹配、以及和传参固定笔记里“追加开关字符串”是否同时存在，都还未知。
