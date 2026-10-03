---
schema_version: 2
id: web-51job-webpack-module-map
document_type: reference
original_date: '2026-07-03'
archived_date: '2026-10-02'
scope:
  targets:
    - 51job
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./51job-webpack-analysis.md#基本信息"
    basis: source-report
  - id: s2
    ref: "./51job-webpack-analysis.md#加密--签名"
    basis: source-report
  - id: s3
    ref: "./51job-webpack-analysis.md#网络请求"
    basis: source-report
  - id: s4
    ref: "./51job-webpack-analysis.md#api-签名路径推断"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s3]
    basis: source-report
    limits: 模块号和库名来自 2026-07-03 的自吐表。用途列是推测。未打开 factory，未重数 1634 与 1310。重新打包后模块号无效。
  - name: interfaces
    anchor: interfaces
    sources: [s1, s4]
    basis: source-report
    limits: 页面目标写在基本信息表。search-pc 只出现在推测图里，没有请求样本。
  - name: request-chain
    anchor: request-chain
    sources: [s4]
    basis: source-report
    limits: 来源写明签名函数待定位，CryptoJS 一步是“可能经过”。不能当成已确认调用链。
relations:
  - type: derived_from
    target: "./51job-webpack-analysis.md#api-签名路径推断"
tags:
  - 51job
  - webpack
  - source-report
---

# 51job 这次 Webpack 自吐里点名的库和未定位的签名

这张卡只回答：2026-07-03 那份 `we.51job.com/pc/search` 自吐记录把 CryptoJS 和 Axios 标在哪个模块号，以及搜索接口被推测到哪里。它不提供签名算法。风控检测面仍看 51job 风控参考卡；那张卡没有收接口和加密参数。

来源没有可公开定位的材料链接。正文没有出现 front matter 里的 AES、SM4 或国密，这些名字不进入结论。

<a id="parameters"></a>
## 已点名的库模块

来源把包写成 Vue 2.7.14 加 Webpack 4 的 webpackJsonp 模式，并给出 1634 个 factory、1310 个已加载模块。下表只保留和签名候选、HTTP 入口直接相关的两行。其余 UI、地图和字典模块不单列。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 框架行原文是 Vue 2.7.14 + Webpack 4 (webpackJsonp 模式) | s1，基本信息 | source-report | 该次自吐记录 | 未重数 factory。不把版本写进 scope |
| C2 | 模块 8429 的用途推测原文是 API 签名 / token 生成，库名写为 CryptoJS | s2，加密 / 签名 | source-report | 该次模块表 | 未核对函数体。export 名单不逐项当参数 |
| C3 | 模块 cebe 的用途原文是所有 HTTP 请求，库名写为 Axios | s3，网络请求 | source-report | 该次模块表 | 不证明某条业务请求已经挂到这个实例 |

监控表里的 ARMS 与神策只说明这些库被点名。这里不把它们收成检测面。

<a id="interfaces"></a>
## 页面和推测中的搜索路径

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 基本信息的目标原文是 we.51job.com/pc/search | s1，基本信息 | source-report | 来源所写页面 | 没有本次响应或脚本 hash |
| C5 | 推测图末端原文是 we.51job.com/api/job/search-pc | s4，API 签名路径推断 | source-report | 该图中的搜索候选 | 没有请求样本，不能当成已确认接口 |

<a id="request-chain"></a>
## 作者推测的签名路径

来源把搜索点击画成 Vue 组件到 Axios（cebe），再可能到 CryptoJS（8429），然后到上一节的 search-pc。原句是：

> [可能经过] CryptoJS (8429) → 生成签名参数

紧接着写明签名生成函数待定位。因此这条链只保留“可能经过”和“待定位”，不补拼接规则。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 推测图对 CryptoJS 的原文是 [可能经过] CryptoJS (8429) → 生成签名参数 | s4，API 签名路径推断 | source-report | 该次模块推断 | 签名函数未定位。本次未发请求 |

## 验证与限制

- 自吐是作者的 source-report。本卡没有执行 `webpackJsonp.push`，也没有对照 factory。
- 模块号、1634 和 1310 只描述这份记录。bundle 一变就失效。
- 不从标签补 AES、SM4 或国密。正文没有这些算法。
- cookie 工具只有函数名，没有值，不收录。
- 没有签名函数、验收样本或失败出口，所以没有流程卡。
