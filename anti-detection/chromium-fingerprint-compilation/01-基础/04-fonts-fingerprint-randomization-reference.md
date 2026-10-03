---
schema_version: 2
id: chromium-blink-font-offset-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-blink-font-offset]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./04-fonts-fingerprint-randomization.md#三字体指纹原理"
    basis: unknown
  - id: s2
    ref: "./04-fonts-fingerprint-randomization.md#四编译随机fonts指纹"
    basis: unknown
  - id: s3
    ref: "./04-fonts-fingerprint-randomization.md#五太low了"
    basis: unknown
  - id: s4
    ref: "./04-fonts-fingerprint-randomization.md#3编译"
    basis: unknown
  - id: s5
    ref: "./04-fonts-fingerprint-randomization.md#四编译随机fonts指纹"
    basis: unknown
modules:
  - name: parameters
    anchor: parameters
    sources: [s2, s5]
    basis: unknown
    limits: 只读到归档里的替换文本。没有 Chromium 版本，未编译，未运行。作者“小概率 +1”的概括保持 source-report。
  - name: risk-control
    anchor: risk-control
    sources: [s1, s3]
    basis: unknown
    limits: 比较规则和未覆盖接口都是作者列举。探测脚本的摘要输出不转写。合集首页提到的字体替换文件不在本篇。
  - name: validation
    anchor: validation
    sources: [s3, s4]
    basis: unknown
    limits: browserleaks 能通过是作者自述。本轮没有打开该页，也不能写成已验收。
relations:
  - type: derived_from
    target: "./04-fonts-fingerprint-randomization.md#四编译随机fonts指纹"
tags: [chromium, blink, font]
---

# Chromium Blink 字体 offset 绑定的随机偏移

这张卡只回答一个检索问题：这篇归档把字体指纹随机化钩在哪个 Blink 绑定上、加的是什么、作者自己承认没盖住哪些接口。宿主对象卡 [CSS / Layout / Font 对象参考](../../../web-reverse/browser-env-objects/css-layout-font.md) 的目标是 css、layout、font，模块只有风险控制检测面，不包含 `HTMLElement` 的 offset 绑定。

来源没有可定位的逐篇原文 URL。编译步骤被作者推到“第一篇文章”，本篇不构成可独立执行的流程。

<a id="parameters"></a>
## 参数机制

作者点名 `third_party\blink\renderer\core\html\html_element.cc`。读到的替换文本在 `HTMLElement::offsetWidthForBinding` 和 `HTMLElement::offsetHeightForBinding` 的原结果上各加一次 `getRandomIntForFoo2Modern()`。抽样是 `std::uniform_int_distribution<int> distribution(0, 9);`。`tmp > 0` 时走 `return 0;`，否则 `return 1;`。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 钩子文件是 third_party\blink\renderer\core\html\html_element.cc | s2，编译随机 fonts 一节 | unknown | 本篇粘贴的路径 | 无版本号 |
| C2 | 两个 binding 的返回前都有 result = result + getRandomIntForFoo2Modern(); | s2，替换后的两个函数 | unknown | 归档中的替换文本 | 未编译 |
| C3 | 分布上界写的是 distribution(0, 9)，分支是 tmp > 0 则 return 0，否则 return 1 | s2，getRandomIntForFoo2Modern | unknown | 该辅助函数文本 | 未跑分布 |
| C4 | 作者把上述分支概括为随机小概率给其结果+1 | s5，原理引用句 | unknown | 作者对本段替换的说明 | 错写了 offset 的拼写，未对照二进制 |

<a id="risk-control"></a>
## 检测面与未覆盖接口

作者先测量标准字体宽度，基准是 `monospace`、`sans-serif`、`serif`。当前字体的宽度和标准字体宽度相同时，就代表系统中没有当前字体。作者写明这里只用到了 offsetWidth 和 offsetHeight。

未写入替换的接口包括 `ele.getBBox()`、`document.fonts.check()`、`window.FontFace()`、`canvas.measureText()`、`window.getComputedStyle()`、`style.transformOrigin`、`ele.scrollWidth`、`ele.scrollHeight`、`ele.clientWidth`、`ele.clientHeight` 和 `getBoundingClientRect()`。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 先测量标准字体的宽度，再靠与标准宽度相同判断未安装 | s1，字体指纹原理 | unknown | 作者描述的这一种宽高比较 | 不是全部字体探测实现 |
| C6 | 这里只用到了offsetWidth和offsetHeight | s1，原理段注意 | unknown | 本篇自限 | 结尾列表说明还有别的接口 |
| C7 | 未覆盖示例里点了 ele.getBBox() 和 getBoundingClientRect() | s3，太 low 一节 | unknown | 作者列出的接口名 | 没有这些接口的补丁 |

<a id="validation"></a>
## 验证与限制

作者只要求再次看看 fonts 指纹是不是每次访问都变成随机了，并称这种最简单的 `ele.offsetWidth` 修改也能通过许多 fonts 指纹检测，例如 browserleaks 的 fonts 页。两句都是自述。没有通过样本、反例或停止条件。探测脚本末尾的摘要原值不转写。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 再次看看fonts指纹，是不是每次访问都变成随机了。 | s4，编译后的检查句 | unknown | 作者的口头检查 | 问句，不是验收记录 |
| C9 | 但也能通过许多fonts指纹检测了，如https://browserleaks.com/fonts | s3，局限性段落 | unknown | 作者点名的一页 | 本轮未打开，未复现 |
