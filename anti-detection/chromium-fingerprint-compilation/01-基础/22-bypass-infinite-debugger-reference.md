---
schema_version: 2
id: chromium-v8-debugger-keyword-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-v8-keyword]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./22-bypass-infinite-debugger.md#二如何使debugger关键字变得无效"
    basis: unknown
  - id: s2
    ref: "./22-bypass-infinite-debugger.md#三新增debuggel关键字"
    basis: unknown
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: unknown
    limits: 只记录作者点名的生成头和 debugger 表项角色。没有 V8 版本、源码 checkout 或编译结果。
  - name: parameters
    anchor: parameters
    sources: [s2]
    basis: unknown
    limits: 长度 8 与 key 127 只绑定作者贴出的那一张生成表。表体不抄，换版本即失效。
relations:
  - type: derived_from
    target: "./22-bypass-infinite-debugger.md#二如何使debugger关键字变得无效"
  - type: derived_from
    target: "./22-bypass-infinite-debugger.md#三新增debuggel关键字"
tags: [chromium, v8, keywords-gen, unknown]
---

# V8 关键字表里的 debugger 角色

这张卡只回答：这篇归档把 `debugger` 关键字改到哪一个生成头、原 token 和替换 token 各是什么，以及 `debuggel` 如何绑进同一张表。它不是补丁脚本，也不证明任一 Chromium 版本能够编译或暂停。

<a id="interfaces"></a>
## 接口位置

作者打开的文件是 `\v8\src\parsing\keywords-gen.h`。贴出的原表项是 `{"debugger", Token::kDebugger}`，替换表项是 `{"debugger", Token::kFalseLiteral}`。作者接着写“debugger关键字就等于false了”，这是编译成功后的自述，本卡保持 source-report。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 改动文件是 `\v8\src\parsing\keywords-gen.h` | s1 22-bypass-infinite-debugger.md:33 | unknown | 作者点名的生成头 | 无版本 |
| C2 | 原表项含 `{"debugger", Token::kDebugger}` | s1 :38 | unknown | 作者贴出的片段 | 未与上游表核对 |
| C3 | 替换表项含 `{"debugger", Token::kFalseLiteral}` | s1 :45 | unknown | 同一片段 | 未编译 |
| C4 | 作者写有 `debugger关键字就等于false了` | s1 :54 | unknown | 作者自述 | 不能当成已观察到的结果 |

<a id="parameters"></a>
## 参数角色

同一文件的表尾被写成 `{"debuggel", Token::kDebugger}`。作者把长度表最后一个数改成 8，原句是“这个8代指debuggel的长度是8”。`GetToken` 里用 `strncmp(str, "debuggel", 8) == 0` 识别该词，注释写“127代指刚刚改掉的最后一行”。128 项长度表是这一份生成结果，不进入本卡。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 表尾含 `{"debuggel", Token::kDebugger}` | s2 :70 | unknown | 作者这份表 | 未核对哈希仍完美 |
| C6 | 原句 `这个8代指debuggel的长度是8` | s2 :98 | unknown | 该表最后一格 | 表体不移植 |
| C7 | 比较式含 `strncmp(str, "debuggel", 8) == 0` | s2 :118 | unknown | GetToken 追加分支 | 不证明槽位仍空 |
| C8 | 原句 `127代指刚刚改掉的最后一行` | s2 :119 | unknown | 作者对 key 的说明 | 换版本不能沿用 |

## 验证与限制

效果节只有图片，没有文字验收，也没有失败出口，所以不能当成流程。没有 Chromium/V8 版本，生成头被直接修改。本轮没有编译。
