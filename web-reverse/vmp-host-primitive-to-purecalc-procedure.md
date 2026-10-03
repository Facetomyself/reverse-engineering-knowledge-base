---
schema_version: 2
id: web-stack-vm-host-primitive-procedure
document_type: procedure
original_date: '2026-08-16'
archived_date: '2026-10-02'
scope:
  targets:
    - stack-vm-host-primitive
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./vmp-host-primitive-to-purecalc.md#何时用"
    basis: source-report
  - id: s2
    ref: "./vmp-host-primitive-to-purecalc.md#方法论vmp-先钩宿主原语再决定要不要纯算"
    basis: source-report
  - id: s3
    ref: "./vmp-host-primitive-to-purecalc.md#探针表"
    basis: source-report
  - id: s4
    ref: "./vmp-host-primitive-to-purecalc.md#完成门"
    basis: source-report
  - id: s5
    ref: "./vmp-host-primitive-to-purecalc.md#反面"
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [s1, s2, s3]
    basis: source-report
    limits: 步骤只到来源已经写明的钩原语、单变量探针和完成门。不收录盐、字母表或 opcode 表，也不写 hook 脚本。
  - name: validation
    anchor: acceptance
    sources: [s2, s4, s5]
    basis: source-report
    limits: 对拍条数是作者注释。本知识库没有重跑。业务 JSON 读回只表示来源所说的那一层。
relations:
  - type: derived_from
    target: "./vmp-host-primitive-to-purecalc.md#完成门"
tags:
  - stack-vm
  - host-primitive
  - source-report
---

# stack VM：先钩宿主原语，再决定要不要纯算

这份流程回答：已经认定 stack VM 之后，什么时候停在宿主原语，什么时候才拆 opcode。抖音 `webSignUrl` 只是来源点名的工作样例。字段规则在 webSign 案例里。抖音请求面参考卡的 parameters 不收这套探针，所以本卡的目标是这个方法，不是 douyin。原文是：

quote: 本篇不收录盐、字母表和 opcode 表。

<a id="prerequisites"></a>
## 前提与输入

四件事同时成立才进入步骤。缺调用栈就停在 F1，不去猜 opcode。

| 输入 | 来源要求 | 不足时 |
|---|---|---|
| 改写点 | 请求发出前被解释器改写，业务代码里搜不到返回签名的函数 | F1 |
| 静态终点 | 阅读停在 `switch (opcode)`。quote: 静态阅读停在 `switch (opcode)` | 还没停在这里就不要当 stack VM 已认定 |
| 宿主入口 | 调用栈或 hook 进入下面四类之一 | 四类都看不到则 F1 |
| 工作样例边界 | 盐不写进本流程 | 不要把 `VM_CONST` 这个名字换成具体盐 |

四类入口，每行都是来源原句：

quote: `CryptoJS.MD5` / `SHA256` / `HmacSHA256`

quote: `SubtleCrypto.digest` / `sign` / `encrypt`

quote: `encodeURIComponent`、`btoa`、`JSON.stringify`

quote: `sm3`、`md5` 等页面自己挂到 `window` 的函数

来源把这四类叫做宿主原语，并写明文在进原语之前已经排好，VM 只是在调度它们。quote: 明文在进原语之前已经排好

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 从 XHR.open 或 fetch 找到改写 URL 的函数 | 函数是否为 stack VM | 是则 S2；不是则本流程不适用 |
| S2 | 在四类宿主入口读明文 | 明文模板和字段顺序 | 读到模板走 S3；钩不到明文走 F2 |
| S3 | 一次只换一个变量 | 哪一段变、哪一段不变 | 同时换了两个变量走 F3 |
| S4 | 把变的段记成会话材料；不变且不在存储里的段只记名字 | provenance；常量名用 `VM_CONST` | 该段出现在 Cookie 或配置里就从那里取，不要硬编码 |
| S5 | 只移植已经闭合的规范化，加上标准哈希 | 这一层的纯算边界 | 与 oracle 对拍；不要求拆 opcode |
| S6 | 发送签名函数返回的字节 | 发送用的 URL 字节 | 客户端再编码一次，来源写会作废，走 F1 |

S2 的分支原文是 `→ 若函数体是 stack VM:`。S5 的原文是 oracle 对拍边界，不要求拆 opcode。quote: 不要求拆 opcode

工作样例里，探针是换 `uifid`、清空 Cookie 和 storage。盐不变，且不出现在 Cookie、localStorage、策略配置里，就归入常量池，记名 `VM_CONST`，不写进长期 SDK。quote: 记名 `VM_CONST`，不写进长期 SDK。

这是样例句子，不是本卡补上的盐或字母表。原文写到：

quote: 裸参数补 `=`、`timestamp` 追加到末尾。

<a id="outputs"></a>
## 输出

交付四样，缺一只记未知，不补：

- 明文模板和字段顺序。
- 每段的 provenance：会话材料，或只记名字的 VM 常量。
- 已闭合的那一层规范化。未闭合的不写进纯算。
- 一句完成门状态，用下一节的四行，而不是「拆完 opcode」。

来源写 opcode 解释不是完成门。quote: opcode 解释不是完成门。

<a id="acceptance"></a>
## 验收

| 编号 | 来源状态 | 通过时能说什么 | 不能说什么 |
|---|---|---|---|
| A1 | 钩到明文模板 | 定位完成 | 还不是纯算。quote: 定位完成，还不是纯算 |
| A2 | 规范化与 oracle 逐边界一致 | 边界格式闭合，可以纯算这一层 | 其他链自动闭合 |
| A3 | 业务 JSON 读回 | 这一层过了服务端 | 其它链仍要单独验收。quote: 其它链仍要单独验收 |
| A4 | 拆完 opcode | 只有明文钩不到，或原语本身被改写时才需要 | 不是默认完成门。quote: 只有明文钩不到、或原语本身被改写时才需要 |

工作样例另写与浏览器内 `webSignUrl` 对拍空格、`+`、`%`、中文、重复参数、已有签名字段。源码注释称 5 条抓包逐字节命中、20 组以上边界一致。A2 因此保持 source-report，本轮没有对拍。原文是：

quote: 本知识库没有重跑这组回归。

<a id="failure-exits"></a>
## 失败出口

F1：前提不齐，或发送时又把已签名 URL 编码一次。停止，不把静态 opcode 阅读当成完成。

F2：钩到的「MD5」可能不是标准 MD5。对拍一组已知输入。标准库对得上才继续纯算；对不上就先记录差分轮次，不要把标准库结果当 oracle。quote: 不要把标准库结果当 oracle。

F3：这次探针作废，回到 S3，只留一个变量。原文是：

quote: 一次换 Cookie 又换 query，就分不清盐和规范化。

F4：把巨型 DOM stub 加冻住的 canvas data URL 当成已经纯算。来源把这条标成预言机：页面 VM 隔离执行，provenance 记 `node_page_js`。改走预言机成本账，不标宿主原语纯算。原文是：

quote: 失败不写随机签名。
