---
schema_version: 2
id: chromium-closed-shadow-root-reference
document_type: reference
original_date: unknown
archived_date: "2026-10-02"
scope:
  targets: [chromium]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./27-shadow-dom-closed-access.md#二js操作shadow-dom"
    basis: unknown
  - id: s2
    ref: "./27-shadow-dom-closed-access.md#三如何获取closed的shadowroot里的内容"
    basis: unknown
  - id: s3
    ref: "./27-shadow-dom-closed-access.md#四还可以优化"
    basis: unknown
  - id: s4
    ref: "./27-shadow-dom-closed-access.md#五追加给element追加shadowroot2属性"
    basis: unknown
  - id: s5
    ref: "./27-shadow-dom-closed-access.md#2替换为"
    basis: unknown
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2, s4, s5]
    basis: unknown
    limits: 只记录来源点名的 Blink 文件、函数和 IDL 属性。强制改 mode 的替换片段在文本上注释掉了声明；其余函数体没有贴出。作者所说的编译结果没有在本次阅读之外核对。
  - name: risk-control
    anchor: risk-control
    sources: [s2, s3]
    basis: unknown
    limits: 只保留来源对 closed 模式和 shadowRoot 非空检测的说法，没有具体站点、检测脚本或返回体。
relations:
  - type: derived_from
    target: "./27-shadow-dom-closed-access.md#二js操作shadow-dom"
  - type: derived_from
    target: "./27-shadow-dom-closed-access.md#三如何获取closed的shadowroot里的内容"
  - type: derived_from
    target: "./27-shadow-dom-closed-access.md#四还可以优化"
  - type: derived_from
    target: "./27-shadow-dom-closed-access.md#五追加给element追加shadowroot2属性"
  - type: derived_from
    target: "./27-shadow-dom-closed-access.md#2替换为"
tags: [chromium, shadow-dom, blink]
---

# Chromium closed Shadow DOM 的两处源码改动

这张卡只回答：这篇归档为了读到 closed shadow tree，先后改了 Blink 的哪些符号。前面的 open 模式脚本是普通用法复述，不单独成模块。

来源先把 `Element::attachShadow` 的 mode 字符串改成 `open`。后文又说站点会检查 `shadowRoot` 是否为 null，于是改成新增 `shadowRoot2`，并写明这样就可以不再改 `attachShadow`。两套写法的取舍停在原文，没有验收步骤。

<a id="interfaces"></a>
## 接口

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C1 | closed 模式下，来源认为外部读宿主的 `shadowRoot` 会得到 null。 | 宿主元素`的shadowRoot`属性在外部代码中将会返回null | s1 27-shadow-dom-closed-access.md:47 | unknown | 来源对 mode 的说明 | 反引号位置按原文保留。这是平台行为的复述，不是补丁本身。 |
| C2 | 第一套改动是把 `shadowRoot` 的 mode 强行变成 open，文件点在 `element.cc`。 | 修改chromium源码，使`shadowRoot`的mode强行变为open | s2 27-shadow-dom-closed-access.md:55 | unknown | `Element::attachShadow` | 没有 Chromium 版本。 |
| C3 | 贴出的替换行注释掉 mode 字符串的声明后，下一行仍给 `mode_string` 赋值。 | //String mode_string = shadow_root_init_dict->mode(); | s5 27-shadow-dom-closed-access.md:77 | unknown | 第二节替换片段的文本 | 只说明粘贴形态。函数其余部分没有出现，不能据此补全或判断能否编过。 |
| C4 | 作者把编译后的结果写成所有 shadowRoot 都变成 open。 | 编译完成后，可以发现所有的shadowRoot状态全部变成open啦。 | s2 27-shadow-dom-closed-access.md:87 | unknown | 作者对第一套改动的说法 | 本次只读到这句话，没有编译产物。 |
| C5 | 第二套不再改 `attachShadow`，改为新增属性。 | 既然要新增一个属性，上面的`attachShadow()`函数我们就可以不要了。 | s4 27-shadow-dom-closed-access.md:98 | unknown | 第五节开头 | 没有写两套补丁如果都留下会怎样。 |
| C6 | 新函数把 `GetShadowRoot()` 的结果直接返回，不再看 open/closed。 | ShadowRoot* Element::OpenShadowRoot2() const { | s4 27-shadow-dom-closed-access.md:110 | unknown | `element.cc` 追加 | 同段 `return root;` 没有 mode 判断；声明在 `element.h`。 |
| C7 | IDL 用 `OpenShadowRoot2` 实现只读属性 `shadowRoot2`。 | [PerWorldBindings, ImplementedAs=OpenShadowRoot2] readonly attribute ShadowRoot? shadowRoot2; | s4 27-shadow-dom-closed-access.md:132 | unknown | `element.idl` | 没写绑定生成器还要不要别的产物。 |

<a id="risk-control"></a>
## 检测说法

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C8 | 来源把不愿被脚本读到的数据写成会使用 closed。 | 一定会是使用closed模式，让我们无法js访问 | s2 27-shadow-dom-closed-access.md:51 | unknown | 作者对网页的概括 | 不是对某个站点的定位。 |
| C9 | 若 `shadowRoot` 不再是 null，来源称站点会返回错误信息，所以另加 `shadowRoot2`。 | 如果发现`shadowRoot`返回的不是null后，就返回一些错误信息。 | s3 27-shadow-dom-closed-access.md:91 | unknown | 第四节的优化动机 | 没有检测脚本、错误文本或具体站点。 |

## 验证与限制

open 模式示例和 Shadow DOM 定义是复述，不能独立复用。第一套替换在文本上不完整。第二套只点了 `element.cc`、`element.h`、`element.idl` 和一条编译较慢的说明。没有“怎样算读到 closed 内容”的验收，也没有补丁失败时的退出步骤。
