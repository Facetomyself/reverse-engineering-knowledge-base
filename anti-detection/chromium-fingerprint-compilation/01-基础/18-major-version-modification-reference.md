---
schema_version: 2
id: anti-detection-chromium-major-version-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-major-version]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./18-major-version-modification.md#一源码位置"
    basis: unknown
  - id: s2
    ref: "./18-major-version-modification.md#3反指纹检测验证"
    basis: unknown
  - id: s3
    ref: "./18-major-version-modification.md#二新旧版本差异"
    basis: unknown
  - id: s4
    ref: "./18-major-version-modification.md#三看creepjs源码"
    basis: unknown
  - id: s5
    ref: "./18-major-version-modification.md#四总结"
    basis: unknown
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: unknown
    limits: 只定位两个 cc 文件，以及 reduced UA 拼接和 SetBrandVersionList 被改写的形状。版本字面量不写入本卡。没有对照 Chromium 修订。
  - name: validation
    anchor: validation
    sources: [s2]
    basis: unknown
    limits: 浏览器大版本变更和两个站点不能通过，都是作者自述。截图未做视觉审查。本轮没有复测。
  - name: risk-control
    anchor: risk-control
    sources: [s3, s4]
    basis: unknown
    limits: 只保留特性差这个失败原因，以及 creepjs features/index.ts 这一出处。JS、CSS、window 三张表不复制。来源声明表不是全部。
  - name: decision-flow
    anchor: decision-flow
    sources: [s5]
    basis: unknown
    limits: 三条去向是作者建议。没有抹除特性的步骤、旧源码输入，也没有通过条件，不能当 procedure。
relations:
  - type: derived_from
    target: "./18-major-version-modification.md#二新旧版本差异"
tags: [Chromium, major-version, creepjs, unknown]
---

# Chromium 大版本替换与特性差

这张卡检索来源如何替换内核大版本，以及它为什么说 browserscan 和 creepjs 仍不通过。依据只到 `source-report`。版本字面量不转入本卡。总结三条缺步骤和通过条件，不升为 procedure。

<a id="interfaces"></a>
## 两个写入点

来源点名 `\components\version_info\version_info_with_user_agent.cc` 和 `\third_party\blink\renderer\core\frame\navigator_ua.cc`。reduced UA 那段把原来的 `GetMajorVersionNumber()` 拼接注释掉。`navigator_ua.cc` 里把 `SetBrandVersionList(metadata.brand_version_list)` 注释掉，改为本地 `UserAgentBrandList` 再 `SetBrandVersionList`。同一段也替换了 `SetUAFullVersion`。具体版本字面量不转入本卡。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 大版本写入点之一是 version_info_with_user_agent.cc | s1 `18-major-version-modification.md:30` 原文：\components\version_info\version_info_with_user_agent.cc | unknown | chromium-major-version | 未对照修订 |
| C2 | 另一写入点是 navigator_ua.cc | s1 `18-major-version-modification.md:31` 原文：\third_party\blink\renderer\core\frame\navigator_ua.cc | unknown | chromium-major-version | 未对照修订 |
| C3 | 来源注释掉按主版本拼接的 reduced UA | s1 `18-major-version-modification.md:37` 原文：//{"Chrome/", GetMajorVersionNumber(), ".0.", build_version, ".0"}); | unknown | chromium-major-version | 不复制替换字面量 |
| C4 | 来源改为本地 UserAgentBrandList 再写回 | s1 `18-major-version-modification.md:46` 原文：ua_data->SetBrandVersionList(uabl); | unknown | chromium-major-version | 不复制品牌版本字面量 |

<a id="validation"></a>
## 作者用来对照的站点

来源称编译后可以看到大版本已经变更，随后用 browserscan 和 creepjs 做反指纹检测，并写两者都不能通过。变更成功和检测失败都是作者自述。三张截图没有做视觉审查。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 作者称编译后大版本已经变更 | s1 `18-major-version-modification.md:52` 原文：编译后可以看到，浏览器的大版本已成功变更。 | unknown | chromium-major-version | 作者自述，未复现 |
| C6 | 作者称 creepjs 和 browserscan 都不能通过 | s2 `18-major-version-modification.md:66` 原文：内核更改是成功了，但发现creepjs和browserscan都无法通过反指纹检测。 | unknown | chromium-major-version | 不是本轮站点结果 |

<a id="risk-control"></a>
## 特性差

来源把不能通过的原因写成：所声称的较低版本特性和当前浏览器特性不一致。例子是 `JSON.rawJSON`：来源称它是更高版本才有的函数，出现在更低版本声称里就被看成篡改。特性列表来自 creepjs 的 `\creepjs\src\features\index.ts`，分成 JS、CSS、window 三节。来源写明只是部分例举。三张表不转入本卡。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | 来源把失败归因于版本特性不一致 | s3 `18-major-version-modification.md:70` 原文：v106的版本特性和当前浏览器的版本特性有差异 | unknown | chromium-major-version | 作者对 creepjs 的读法 |
| C8 | 来源用 JSON.rawJSON 说明高版本函数暴露篡改 | s3 `18-major-version-modification.md:72` 原文：这里拿`JSON.rawJSON`函数举例，106版本内核没有这个函数，因为它是115版本的新特性。 | unknown | chromium-major-version | 只此例子 |
| C9 | 特性表来自 creepjs features/index.ts | s4 `18-major-version-modification.md:81` 原文：\creepjs\src\features\index.ts | unknown | chromium-major-version | 未对照仓库修订 |
| C10 | 来源声明这些特性不是全部 | s4 `18-major-version-modification.md:182` 原文：以上新特性也只是部分例举，不代表是全部。 | unknown | chromium-major-version | 不复制三张表 |

<a id="decision-flow"></a>
## 作者给出的三条去向

来源的总结是：大版本从高改到低需要酌情抹除高版本特性，反过来也一样；邻近大版本作者认为几乎没变化；跨多个版本时，作者推荐下载旧版本 Chromium 源码重新编译。抹除哪些符号、旧树如何取、编译后怎样算通过，正文都没有。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C11 | 高改低被写成要抹除高版本特性 | s5 `18-major-version-modification.md:186` 原文：想要将大版本从高改到低，需要将这些高版本的特性进行酌情抹除才行。 | unknown | chromium-major-version | 没有抹除步骤 |
| C12 | 邻近大版本被写成可以微调 | s5 `18-major-version-modification.md:187` 原文：但大版本是可以微调的，比如123-125版本几乎没啥变化 | unknown | chromium-major-version | 作者判断 |
| C13 | 跨多版本时来源推荐重编旧源码 | s5 `18-major-version-modification.md:188` 原文：要跨多个版本，我个人推荐的最终解决方案是：下载旧版本chromium源码，重新编译。 | unknown | chromium-major-version | 没有旧树输入 |

## 验证与限制

上篇小版本链接和手机端、微信端动机只说明为什么要降大版本，不单建模块。公开来源 URL 未知。本轮没有编译，没有打开 browserscan 或 creepjs，也没有核对 features/index.ts 的上游修订。
