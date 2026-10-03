---
schema_version: 2
id: ruyi-cdp-http-client-hints-reference
document_type: reference
original_date: '2025-12-26'
archived_date: '2026-10-02'
scope:
  targets: [cdp-http-client-hints]
  client: chromium-cdp
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ruyi-20251226-01.md#浏览器指纹模拟--纯cdp框架模拟浏览器指纹"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只记录来源点名的 CDP 方法、本地调试列表和远程调试端口前提。未运行，不复制 UA 或 Client Hints 样值。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录 userAgentMetadata 与 sec-ch-ua-* 的角色。不记录品牌串、完整 UA、语言或平台样值。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 只保留来源示例的本地连接顺序。归档代码缩进被压扁，不能当可执行客户端。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 来源声称本地服务能看到修改结果，但正文没有附上打印出的请求头。作者成功保持 source-report。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 检测点只写到来源的差异判断。JS 注入被声称有效，但脚本不在正文里。
relations:
  - type: derived_from
    target: "./ruyi-20251226-01.md#浏览器指纹模拟--纯cdp框架模拟浏览器指纹"
tags: [cdp, client-hints, source-report]
---

# CDP HTTP 层 Client Hints 覆盖参考

检索纯 CDP 示例如何在 HTTP 层覆盖 User-Agent 与 Client Hints，以及它和内核改指纹的差别。本卡只保留来源原句能支撑的方法名和字段角色，不提供可运行覆盖脚本，也不复制指纹样值。

<a id="interfaces"></a>
## CDP 方法与本地调试入口

来源用自写的 `send_cdp` 发送命令。HTTP 层覆盖点名了两个网络方法和一次导航；连接前提是本地浏览器打开远程调试端口。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C3 | 来源用 Network.setUserAgentOverride 覆盖 User-Agent 与 Client Hints。 | s1 原文子串 Network.setUserAgentOverride；./ruyi-20251226-01.md:123 | source-report | 该示例的 HTTP 层覆盖 | 未运行；不包含参数样值 |
| C4 | 来源接着用 Network.setExtraHTTPHeaders 强制附加 HTTP 头。 | s1 原文子串 Network.setExtraHTTPHeaders；./ruyi-20251226-01.md:140 | source-report | 同一条本地 websocket | 未证明这些头会覆盖浏览器随后补上的头 |
| C5 | 导航前调了 Network.enable。 | s1 原文子串 Network.enable；./ruyi-20251226-01.md:162 | source-report | 该示例主流程 | 注释写 DOM 代理，调用本身只有 Network.enable |
| C6 | 页面导航封装为 Page.navigate。 | s1 原文子串 Page.navigate；./ruyi-20251226-01.md:147 | source-report | 该示例的打开 URL | 没有加载完成或失败分支 |
| C7 | 连不上时，来源要求浏览器开启远程调试端口 9222。 | s1 原文子串 --remote-debugging-port=9222；./ruyi-20251226-01.md:158 | source-report | 来源示例的本地浏览器 | 不是通用启动参数清单 |

<a id="parameters"></a>
## Client Hints 字段角色

覆盖分成元数据和额外头两段。元数据决定 `sec-ch-ua-*` 的值；额外头被写成要在请求里保持一致。具体品牌、版本和 UA 字符串是样值，不进入本卡。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 来源把 Client Hints 元数据定义成决定 sec-ch-ua-* 请求头的那一组字段。 | s1 原文子串 sec-ch-ua-*；./ruyi-20251226-01.md:100 | source-report | 该示例的 HTTP 头 | 不记录具体头值 |
| C9 | 覆盖参数里有 userAgentMetadata，和 userAgent 分开传递。 | s1 原文子串 userAgentMetadata；./ruyi-20251226-01.md:127 | source-report | Network.setUserAgentOverride 的参数角色 | 未核对 CDP 版本是否仍接受该字段 |

<a id="request-chain"></a>
## 本地连接顺序

来源顺序是：取本地调试列表里的 page websocket，启用网络，调用覆盖函数，再导航到本地页面并收一段事件。这是示例顺序，不是业务站点请求链。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C10 | 调试目标来自本地 9222 的 /json 列表。 | s1 原文子串 http://127.0.0.1:9222/json；./ruyi-20251226-01.md:153 | source-report | 来源机器上的本地浏览器 | 没有页面类型缺失时的分支，除了外层连接异常 |

<a id="validation"></a>
## 观察面与作者结论

来源先用 FastAPI 打印请求头，最后声称 HTTP 层 Client Hints/UA 已经改好。正文没有贴出打印结果，所以不能把这句当成已验收。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C11 | 来源打算用本地 FastAPI 查看收集到的请求头。 | s1 原文子串 我先使用fastapi模拟服务器，这样可以直观看到服务器端搜集到的用户请求头信息：；./ruyi-20251226-01.md:50 | source-report | 该示例的本地观察面 | 打印循环被压成一行，本卡不把它当可执行验收 |
| C12 | 作者写 HTTP 层 client hints/UA 已经完美修改，并对比内核修改说更方便。 | s1 原文子串 HTTP层的client hints/UA指纹信息已经得到完美修改了；./ruyi-20251226-01.md:187 | source-report | 作者对该示例的自述 | 正文没有请求头打印；保持 source-report |

<a id="risk-control"></a>
## 检测面与内核路线的差别

来源把 CDP 的检测面放在自动化和真人操作的差异上，并把 CDP 描述成不想改 Chromium 源码时的指纹浏览器启动器。JS 注入只被声称有效。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源认为 CDP 被检测的点是自动化框架和真人操作不同的地方。 | s1 原文子串 它被检测的点是自动化框架和人真实操作不同的地方；./ruyi-20251226-01.md:40 | source-report | 来源对自写 CDP 框架的判断 | 没有列出检测点 |
| C2 | 来源把 CDP 指纹浏览器写成相对内核源码的另一条修改路线。 | s1 原文子串 用CDP做指纹浏览器给那些畏惧chromium源码的人开了一条研究指纹修改的新路。；./ruyi-20251226-01.md:42 | source-report | 来源自述的研究路线 | 没有内核补丁或版本对照 |

## 验证与限制

近邻 `chromium-startup-cookie` 是启动期 CookieManager，不是这组 CDP 网络方法，所以不并入该卡。本卡没有本地运行。连接失败只有远程调试端口这一种明确出口；头不一致、命令被拒绝、页面类型缺失都没有验收。归档里的 UA、品牌和 sec-ch-ua 样值故意不抄。
