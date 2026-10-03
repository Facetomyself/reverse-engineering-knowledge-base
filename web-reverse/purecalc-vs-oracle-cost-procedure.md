---
schema_version: 2
id: web-purecalc-oracle-cost-procedure
document_type: procedure
original_date: '2026-09-23'
archived_date: '2026-10-02'
scope:
  targets:
    - purecalc-oracle-cost
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./purecalc-vs-oracle-cost.md#成本账怎么填"
    basis: source-report
  - id: s2
    ref: "./purecalc-vs-oracle-cost.md#预言机也有验收"
    basis: source-report
  - id: s3
    ref: "./purecalc-vs-oracle-cost.md#伪代码"
    basis: source-report
  - id: s4
    ref: "./purecalc-vs-oracle-cost.md#账本里要写的一句"
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [s1, s3, s4]
    basis: source-report
    limits: 只整理来源的分流和伪代码。不包含签名器。快手与京东的产品卡已有各自的 validation，本卡不把它们再列成目标。
  - name: validation
    anchor: acceptance
    sources: [s2, s3]
    basis: source-report
    limits: canary 与 tk03 都是来源句子。本轮没有跑 oracle，也没有重签。
relations:
  - type: derived_from
    target: "./purecalc-vs-oracle-cost.md#伪代码"
tags:
  - purecalc
  - oracle
  - provenance
  - source-report
---

# 纯算还是预言机：先写成本账

这份流程只回答来源如何决定移植还是跑官方脚本，以及出参该标什么 provenance。它不提供签名实现。快手产品卡已经记下隔离黑盒和两类 canary 的名字；京东 h5st 产品卡和 body 预哈希卡已经分开服务端材料与本地兜底。来源 front matter 的 target 是 unknown，而 unknown 上已有别的 decision-flow，所以本卡的目标用问题名，不并进那些卡。

<a id="prerequisites"></a>
## 前提与输入

对每个参数先有四件事的答案，缺一则不能选落地。quote: 对每个参数问四件事：输入是否已在请求边界闭合、原语是不是标准库、移植量、失败时能不能安全降级。

| 输入 | 来源要求 | 不足时 |
|---|---|---|
| 边界 | 明文和标准原语能否在请求边界读到 | 不能就不要先标 purecalc |
| 原语 | 是不是标准库 | 未知则停在 F1 |
| 移植量 | 字节码是否又大又多变体 | 大则走 oracle，并写明为什么不移植 |
| 降级 | 失败时能不能安全停下 | 不能造签名，走 F1 |

总规则。quote: 能在请求边界读到明文和标准原语，就纯算。字节码大、变体多、或出参只在 cookie 边界闭合，就用隔离程序当预言机，并在账本上写明为什么不移植。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 按四件事填这一参数 | 一句原因 | 四件事都有答案才到 S2，否则 F1 |
| S2 | 若宿主原语处明文已闭合 | 只移植规范化 | 来源伪代码返回 purecalc(canonical_rules_only)，然后 S5 |
| S3 | 若反编译体积小且夹具对得上 | 纯算候选 | 来源写 return purecalc，然后 S5 |
| S4 | 否则跑官方脚本 | oracle 出参，provenance 标 runtime | 先过 canary 和当次 URL，见验收；失败走 F1 |
| S5 | 写账本一行 | 落地、为什么不移植、完成门 | 行写完才结束；标错走 F3 |

S2 的原文是 `return purecalc(canonical_rules_only)`。S4 要求 `require canaries_pass`，注释写 navigator writable 与 layout，并且 `require inputs.sign_url is this round`。

来源表里的站点行只是 2026-09-23 的账本例子，不是本流程要执行的请求。其中 Cookie 边界的一行写明 strict 失败不造签名。quote: strict 失败不造签名

<a id="outputs"></a>
## 输出

每个参数一行。落地只能是 purecalc、oracle、execjs_bundle、rpc 四者之一，后面还要写两段原因。原文用的词是：

quote: 为什么不移植

quote: 完成门

oracle 出参不能标成 purecalc。原文是：

quote: 预言机出参的 provenance 是 runtime，不能标 purecalc。

伪代码另写：

quote: oracle 出参永远不是 purecalc

来源用快手约 53KB 字节码留在 Node 作为这句的例子。quote: 快手把 53KB 字节码留在 Node，就是这句。

<a id="acceptance"></a>
## 验收

隔离执行不是把脚本丢进空 Node。quote: 隔离执行不是把脚本丢进空 Node。

| 编号 | 通过条件 | 反例 |
|---|---|---|
| A1 | `navigator.platform`、`userAgent`、`appCodeName` 在真实浏览器上是 getter-only。脚本写入标记串再读回。quote: 在真实浏览器上是 getter-only | 普通对象字面量会被真写进去，VM 走异常分支，`kwscode` 里出现非 hex |
| A2 | `div` 设 `height:20px` 挂到 `body` 后，`offsetHeight` 应为 20。quote: `offsetHeight` 应为 20 | 未挂载是 0 |
| A3 | `did` 必须和 Cookie 一致，因为 `kwfv1` 明文里带它。quote: `did` 必须和 Cookie 一致 | 过期的 `signUrl` 不能拿历史 `kws-N-*.js` 去签 |
| A4 | 京东侧验收是 h5st 第 4 段以 `tk03` 开头。quote: h5st 第 4 段以 `tk03` 开头 | `tk04` / `tk06` 是库的本地兜底。第一次出参不是完成 |

A1 到 A4 都是来源句子。本轮没有执行 canary，也没有重签。产品卡已经覆盖快手 validation 和京东 validation，这里不把通过条件写成当前服务端结果。

<a id="failure-exits"></a>
## 失败出口

F1：canary 不过、当次 sign URL 不是这一轮、或 strict 失败。伪代码是失败就 raise。注释原文是：

quote: no random fallback

同一行的选择原文是：

quote: strict 失败不造签名

停止，不造签名。

F2：h5st 第一次不是 tk03。warmup 重签直到 tk03，而不是把第一次出参当完成。quote: 而不是把第一次出参当完成。

F3：oracle 出参被写成 purecalc。回到 S5 改标，不把这次失败当成算法回归。原文是：

quote: 写成 purecalc 会让下一轮把 oracle 失败当成算法回归。
