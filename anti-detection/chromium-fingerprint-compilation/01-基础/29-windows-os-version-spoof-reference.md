---
schema_version: 2
id: chromium-windows-platform-version-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-ua-platform-version]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./29-windows-os-version-spoof.md#二js是如何获取-windows-系统版本"
    basis: unknown
  - id: s2
    ref: "./29-windows-os-version-spoof.md#三修改源码"
    basis: unknown
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2]
    basis: unknown
    limits: 只记录作者点名的 JS 读取面和 navigator_ua.cc 的 SetPlatform。没有源码 checkout，平台名参数未被这篇笔记改写。
  - name: parameters
    anchor: parameters
    sources: [s2]
    basis: unknown
    limits: 开关名和版本拼接来自粘贴片段。表达式值域与作者注释不一致，这是对文本的 static-review，不是运行结果。不记录种子字面量。
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2]
    basis: unknown
    limits: Win10/Win11 的阈值是作者检测样例里的比较，不是某站点的评分规则。样例输出不是打补丁后的观察。
relations:
  - type: derived_from
    target: "./29-windows-os-version-spoof.md#三修改源码"
tags: [chromium, userAgentData, platformVersion, unknown]
---

# Chromium Win10/Win11 的 platformVersion 接缝

这张卡只回答一个检索问题：这篇笔记把 Windows 10 与 11 的区分放在哪一层，以及源码改写碰到哪个函数。它不是可编译的补丁，也不把控制台样例当成验收。

<a id="interfaces"></a>
## 接口边界

作者把读取拆成两段。Win10 之前靠 `navigator.userAgent` 里的 NT 数字。Win10 和 Win11 在样例里都先匹配 NT 10.0，再调用 `navigator.userAgentData.getHighEntropyValues`，键只有 `platformVersion`。

C++ 侧只打开 `\third_party\blink\renderer\core\frame\navigator_ua.cc`，原调用是 `ua_data->SetPlatform`，两个参数分别来自 `metadata.platform` 和 `metadata.platform_version`。替换片段仍把平台名设成 `metadata.platform`，只改第二个参数。`navigator.userAgent` 字符串不在这个文件的替换范围内。

<a id="parameters"></a>
## 版本参数

启动开关名是 `fingerprints`。有该开关时，粘贴代码把版本整数写成 `seed % 7 + 10`，再交给 `std::to_string(platfrom_v) + ".0.0"`。没有该开关时，同一变量停在初值 `7`。作者注释写取值范围是 7~16，并且大于 12 算 Win11、否则算 Win10。

按粘贴表达式，取模后再加 10，得不到注释里的整个 7~16。无开关时的初值 7 也不在该表达式的值域里。标识符本身写成 `platfrom_v`。种子字面量不收录。Chromium 修订未知，不能把这段当成当前树的函数签名。

<a id="risk-control"></a>
## 读取面

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 样例把 NT 10.0 之后的 Win11 判成 platformVersion 主版本大于等于 13 | s1，来源第 40 行 | unknown | 作者给出的检测函数 | 不是站点规则，也没有打补丁后的对照 |
| C5 | Win10 之前的区分被作者放在 userAgent 的 NT 数字上 | s1，来源第 73 行 | unknown | 该笔记的注释 | 笔记没有改 NT 字符串 |
| C15 | 作者用大于 12 与否区分 Win11 和 Win10 | s2，来源第 113 行 | unknown | 作者对 platfrom_v 的注释 | 与第 106 行表达式的值域不一致 |

## 验证与限制

来源没有命名检测站点，也没有打补丁后的输出。控制台里的 Windows 11 是检测函数自己的样例。文末只有 `ninja -C out/Default chrome`，这不是验收。没有失败出口，因此不建 procedure。本轮没有编译或运行。
