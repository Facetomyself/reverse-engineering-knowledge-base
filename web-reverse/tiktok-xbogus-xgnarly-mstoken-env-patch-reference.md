---
schema_version: 2
id: web-reverse-tiktok-webmssdk-env-export-reference
document_type: reference
original_date: '2025-10-31'
archived_date: '2026-10-03'
scope:
  targets: [tiktok]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./tiktok-xbogus-xgnarly-mstoken-env-patch.md#reference-extraction-208
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅整理 webmssdk 加载、fetch 重写与 report 下发 msToken 的来源顺序；未跑 SDK、浏览器或评论接口。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 记录 X-Bogus / X-Gnarly / msToken / strData 的角色与导出点；不收录签名样值、响应头值或环境数组。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: fetch setter hook、赋值导出与 VMP 寄存器长度条件断点是来源排查顺序，不是已验证补环境清单。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 作者截图与“出值”均为自述；纯算未完成；本轮无 runtime 或 server-accepted。
relations:
  - type: derived_from
    target: ./tiktok-xbogus-xgnarly-mstoken-env-patch.md#reference-extraction-208
  - type: supplements
    target: ./tiktok-web-signing-planes-reference.md#parameters
tags: [tiktok, X-Bogus, X-Gnarly, msToken, webmssdk, byted_acrawler, strData, source-report]
---

# TikTok webmssdk 补环境导出与 strData 定位参考

这张窄卡只整理来源 archive 对 **评论接口三个字段如何从 `webmssdk.js` 里定位、补环境后导出，以及 msToken 改由 report 响应头下发** 的路径。[TikTok Web 端点签名面](./tiktok-web-signing-planes-reference.md) 负责 path 路由、legacy/project 字段合同与 fail-closed 写回；旁路进程见 [frontier / ticket-guard / Shop](./tiktok-frontier-ticket-shop-reference.md)。本文不收录编码器内部常量，也不是可运行 signer。

<a id="request-chain"></a>
## 加载与签发顺序

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 报告称评论接口主要看三个字段：`X-Bogus`、`X-Gnarly`、`msToken`。验证码与 verifyFp 不在本文。 | s1，「逆向目标」「分析过程」 | source-report | 来源所述 Web 评论接口 | 目标站点只以 archive 内 base64 原文为准，本文不解码。 |
| C2 | 报告称 `X-Bogus` 与 `X-Gnarly` 同在 `webmssdk.js`：执行 SDK 生成 `window.byted_acrawler` → `byted_acrawler.init` 多次重写 `window.fetch` → 调用被重写的 fetch 才出值。 | s1，「分析过程」三步梳理 | source-report | 来源写文时的 SDK | 作者注明版本有小更新，截图可能对不上。 |
| C3 | 报告称较新的 `msToken` 不再用随机数，而由日志上报接口 report 在校验通过后写入响应头；请求体里的 `strData` 由同一 SDK 的 VMP 生成。 | s1，「msToken分析」 | source-report | 来源对比“早些版本” | 未复现 report 或头字段。 |

<a id="parameters"></a>
## 字段角色

| 字段 | 来源描述的角色 | 类别 | 边界 |
|---|---|---|---|
| X-Bogus | 重写后的 fetch 路径里一个导出函数的返回值（来源调试名 `encrypt_x_b.v`） | signature | 调用形态是 `.call(void 0, param, undefined)`；不收录 param 或样值。 |
| X-Gnarly | 同一路径的另一个导出函数（`encrypt_x_g.v`），来源多传一个 url 实参 | signature | 与签名面卡的 path 分叉独立；本文不写回 query。 |
| msToken | report 响应头下发的会话材料，不是本地随机 | token | 不能当 fingerprint 或签名输出。 |
| strData | report 载荷密文，VMP 产出 | encoding | 全局搜索命中时值已生成，要再往上跟栈。 |

签名面卡里 legacy `X-Bogus` 可为字面量 `1`；本 archive 走 SDK 导出函数。两套来源不要合成一个实现。

<a id="decision-flow"></a>
## 定位与导出

1. 用 `Object.defineProperty` hook `window.fetch` 的 setter 找重写点；控制台偶发钩不住时改注入时机。SDK 会重写多次，每次用 `fetch.toString()` 对照，直到与加密栈一致。
2. 从重写点往上到 `byted_acrawler.init`；`webmssdk.js` 自执行结束才有 `window.byted_acrawler`。
3. 整包拿到本地补环境。来源称约二百行，重点是 canvas 与 toString 保护，没有复杂原型链。出值后再在加密点把两个函数赋到 `window` 导出，而不是手写算法。
4. `strData`：总流程调用处日志会爆且信息少。再上一层看寄存器函数 `C`（参数里已有 strData）。按参数长度大于 4000 打条件日志，用环境关键字收窄，记下每次断住的 `n.o`，直到 strData 生成后再收紧条件，最后同样赋值导出。
5. 作者称 AST 插桩只抽出方法、逻辑运算插桩未完成，纯算未交付。

<a id="validation"></a>
## 验证与限制

- 「结果验证」只有截图，不升级为评论接口验收。
- 35 张来源图未审，不当证据；图中的 token、用户名与评论不收录。
- 不收录 Cookie、msToken、X-Bogus、X-Gnarly、strData、环境数组或解码后的站点 URL。
- 端点该签哪些字段、缺字段是否 fail-closed，仍以签名面参考为准。
