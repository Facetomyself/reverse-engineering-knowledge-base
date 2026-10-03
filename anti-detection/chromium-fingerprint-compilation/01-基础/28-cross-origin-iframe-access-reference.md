---
schema_version: 2
id: chromium-cross-origin-iframe-idl-reference
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
    ref: "./28-cross-origin-iframe-access.md#二如何获取document下的内容"
    basis: unknown
  - id: s2
    ref: "./28-cross-origin-iframe-access.md#三如何获取跨域iframe的document里的内容"
    basis: unknown
  - id: s3
    ref: "./28-cross-origin-iframe-access.md#4启动时加上参数必须"
    basis: unknown
  - id: s4
    ref: "./28-cross-origin-iframe-access.md#四风险"
    basis: unknown
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2]
    basis: unknown
    limits: 只记录来源点名的 IDL 属性和它对 CheckSecurity 的注释。没有写 contentWindow 的对应改动、绑定生成器或 Chromium 版本。作者对“忽略安全隔离”的解释保持原文。
  - name: parameters
    anchor: parameters
    sources: [s3]
    basis: unknown
    limits: 只记录来源标成必须的启动开关，以及紧随其后的作者结果句。没有写缺少该开关时的现象。
  - name: risk-control
    anchor: risk-control
    sources: [s4]
    basis: unknown
    limits: 只有两句风险：取消隔离有安全风险，以及有些站可能识别到隔离被去掉。没有检测点。
relations:
  - type: derived_from
    target: "./28-cross-origin-iframe-access.md#二如何获取document下的内容"
  - type: derived_from
    target: "./28-cross-origin-iframe-access.md#三如何获取跨域iframe的document里的内容"
  - type: derived_from
    target: "./28-cross-origin-iframe-access.md#4启动时加上参数必须"
  - type: derived_from
    target: "./28-cross-origin-iframe-access.md#四风险"
tags: [chromium, iframe, site-isolation]
---

# Chromium contentDocument 的跨域 IDL 改动位置

这张卡只回答：这篇归档为了读跨域 iframe 的文档，改了哪个 IDL 属性，以及启动时必须带哪个开关。同源读取示例是背景，不是模块。

来源假设读者已经能编译 Chromium。它把 `contentDocument` 上的 `[CheckSecurity=ReturnValue]` 注释掉，并要求启动参数 `--disable-site-isolation-trials`。随后那句“就可以发现能读到”与风险两句，都停在作者原文。

<a id="interfaces"></a>
## 接口

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C1 | 跨域时，来源写 `contentDocument` 会返回 null。 | `contentDocument`会返回null | s1 28-cross-origin-iframe-access.md:49 | unknown | 同源策略的作者表述 | 这是改动前的行为说明，不是补丁结果。 |
| C2 | 改动文件是 `html_iframe_element.idl` 的 `contentDocument`。 | [CheckSecurity=ReturnValue] readonly attribute Document? contentDocument; | s2 28-cross-origin-iframe-access.md:61 | unknown | 替换前的那一行 | 没写同文件里是否还有别的安全检查。 |
| C3 | 替换是把这一段属性注解注释掉。 | //[CheckSecurity=ReturnValue] readonly attribute Document? contentDocument; | s2 28-cross-origin-iframe-access.md:67 | unknown | 来源给出的替换行 | 只这一行。 |
| C4 | 作者把注释注解解释成忽略安全隔离。 | 把`[CheckSecurity=ReturnValue]`这段注释掉了，意思是忽略掉安全隔离 | s2 28-cross-origin-iframe-access.md:71 | unknown | 作者对这一行的解释 | 解释没有别的调用点支撑。 |

<a id="parameters"></a>
## 参数

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C5 | 启动参数被标成必须。 | --disable-site-isolation-trials | s3 28-cross-origin-iframe-access.md:82 | unknown | 来源标题写了“必须” | 没有写缺少该开关时的具体现象。 |
| C6 | 作者称操作之后跨域文档也能读到。 | 跨域iframe的#document里的内容也可以获取到啦 | s3 28-cross-origin-iframe-access.md:85 | unknown | 作者对结果的说法 | 与输出是同一句，没有单独的验收读数。本次没有运行记录。 |

<a id="risk-control"></a>
## 风险说法

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C7 | 取消跨域隔离被写成有安全风险。 | 取消跨域隔离有一定安全风险 | s4 28-cross-origin-iframe-access.md:89 | unknown | 风险第 1 点 | 没有展开风险场景。 |
| C8 | 来源称有些站会检测安全隔离并可能识别到。 | 有些站会做安全隔离检测，可能会被识别到。 | s4 28-cross-origin-iframe-access.md:90 | unknown | 风险第 2 点 | 没有检测脚本或识别特征。 |

## 验证与限制

前提只有“假设已经可以熟练编译”。步骤能定位到一行 IDL 和一条 `ninja -C out/Default chrome`，但通过条件就是作者那句“就可以发现”，失败时除了两句风险没有退出动作。`contentWindow.document` 出现在同源示例里，补丁没有改它。这些缺口使本文不能当成流程卡。已有的 iframe 环境卡描述的是子 realm 语义，不包含这条 IDL 或这个启动开关。
