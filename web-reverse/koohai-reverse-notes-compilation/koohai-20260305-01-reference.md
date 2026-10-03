---
schema_version: 2
id: khbox-node-builtin-binding
document_type: reference
original_date: '2026-03-05'
archived_date: '2026-10-02'
scope:
  targets:
    - KhBox
  client: node
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./koohai-20260305-01.md#1-nodegyp--把-khbox-的源文件纳入编译"
    basis: source-report
  - id: s2
    ref: "./koohai-20260305-01.md#2-srcnode_bindingcc--注册-khbox-为内置模块"
    basis: source-report
  - id: s3
    ref: "./koohai-20260305-01.md#4-libinternalbootstrapnodejs--挂载全局变量"
    basis: source-report
  - id: s4
    ref: "./koohai-20260305-01.md#编译和验证"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2, s3, s4]
    basis: source-report
    limits: 只保留四个触摸点和能读全的符号。node.gyp 清单后半被省略，宏注册行已损坏，不能据此编译。
  - name: parameters
    anchor: parameters
    sources: [s3]
    basis: source-report
    limits: 只保留 globalThis.khBox 的 enumerable 与 configurable。未在进程里枚举键。
  - name: decision-flow
    anchor: decision-flow
    sources: [s2, s4]
    basis: source-report
    limits: 选择魔改 node、跳过 node_contextify.cc，以及快照声明缺失会崩溃。崩溃句不是失败后的恢复步骤。
relations:
  - type: derived_from
    target: "./koohai-20260305-01.md#2-srcnode_bindingcc--注册-khbox-为内置模块"
tags:
  - KhBox
  - node
  - source-report
---

# KhBox 编进 Node 内置 binding 时被点名的四处

这张卡只回答：这篇笔记把 khBox 收进 Node 源码时改哪些文件、内置模块叫什么、全局属性如何隐藏。它不提供可编译源码。文末的指纹状态表没有规则，不收成检测面。

<a id="interfaces"></a>
## 四个文件和能读到的符号

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C3 | 构建清单的插入锚点原文是 `src/node_i18n.cc` | s1，node.gyp | source-report | 这篇笔记的 node.gyp | 只有这一处插入 |
| C4 | 清单在四个 cc 之后写成其余文件 | s1，同一片段 | source-report | 被点名的四个文件 | 省略部分不能补 |
| C5 | 新增头文件原文是 `khbox/khbox_binding.h` | s2，include | source-report | node_binding.cc | 未见其它 include |
| C6 | 宏列表里能读到的新增原文是 `V(khbox)` | s2，宏列表 | source-report | 该损坏行 | 行首已坏，不能粘贴编译 |
| C7 | 展开后的注册函数原文是 `_register_khbox()` | s2，同一行 | source-report | 该说明 | 没有展开结果 |
| C8 | 快照注册原文是 `khbox::RegisterExternalReferences` | s2，外部引用 | source-report | RegisterExternalReferences | 未做快照编译 |
| C11 | JS 侧取值原文是 `internalBinding('khbox')` | s3，bootstrap | source-report | node.js 引导文件末尾 | 未启动进程 |
| C15 | 源文件目录原文是 `src/khbox/` | s4，编译 | source-report | 编译前的放置 | 目录内容不在本文 |
| C16 | 编译命令原文是 `vcbuild.bat` | s4，编译 | source-report | Windows 构建 | 没有日志 |
| C17 | 产物替换前的原文要求先备份 | s4，编译 | source-report | Release 下的 node.exe | 备份不是恢复流程 |

<a id="parameters"></a>
## globalThis.khBox 的属性描述符

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C12 | `defineProperty` 把 `enumerable` 设为 false | s3，引导片段 | source-report | globalThis.khBox | 未调用 Object.keys |
| C13 | 同一对象的 `configurable` 为 false | s3，同一片段 | source-report | 该属性 | 未尝试重定义 |
| C14 | 原文解释这样是为了不暴露在键枚举里 | s3，片段后的说明 | source-report | 该属性 | 只是作者说明 |

<a id="decision-flow"></a>
## 哪些改动算数

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 原文在 addon 与魔改 node 之间选择了魔改 node | s1 之前的正文 | source-report | 这篇笔记的方案选择 | 没有 addon 失败记录 |
| C2 | 原文说核心只有四处，完整源码在知识星球 | 正文起句 | source-report | 这篇笔记的边界 | 所以不能当流程 |
| C9 | 不声明外部引用时，原文写带快照编译时会崩溃 | s2，注册说明 | source-report | 带快照的构建 | 没有回退步骤 |
| C10 | `node_contextify.cc` 原文写不需要改 | s2 后的可选点 | source-report | 当前 KhBox | 以后的 hook 没有实现 |
| C18 | 成功标准原文是输出对象信息而不是报错 | s4，验证 | source-report | `console.log(khBox)` | 报错后怎么停，正文没有 |
| C19 | 四处之外还要求把代码放到目录里 | s3 末句 | source-report | 编译前 | 目录内容缺失就停 |

## 验证与限制

`node -e` 那一句只定义成功。宏行损坏、源文件列表截断、完整源码不在正文，这三件任何一件都使编译步骤不闭合。文末 Canvas、WebGL、WebRTC、字体和 V8 拦截器只有状态，不进入本卡。
