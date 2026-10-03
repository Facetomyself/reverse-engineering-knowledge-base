---
schema_version: 2
id: web-reverse-tencent-tdc-collect-env-patch-reference
document_type: reference
original_date: '2025-12-23'
archived_date: '2026-10-03'
scope:
  targets: [tencent-captcha]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./tencent-tdc-slider-vmp-part1-env-patch.md#reference-extraction-208
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅整理官网 demo 的 prehandle → 动态 tdc.js → new_verify 顺序；未请求 captcha 域。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 记录字段角色与 collect 可选校验；不收录 sess、collect、ticket 或 ua 样值。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: RTCPeerConnection / matchMedia / DOM 标签操作是来源补环境重点，不是通用清单或已验证实现。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: errorCode 0/50 与“多站不校验 collect”均为作者自述；明文正确性放到下篇算法互验，本轮无 runtime。
relations:
  - type: derived_from
    target: ./tencent-tdc-slider-vmp-part1-env-patch.md#reference-extraction-208
  - type: supplements
    target: ./products/tencent-captcha.md#常见链路
tags: [TCaptcha, TDC, collect, cap_union_prehandle, RTCPeerConnection, createElement, source-report]
---

# 腾讯 TDC collect 补环境检测点参考

这张窄卡只整理来源 archive 对 **官网 demo 滑块链上 collect 的入口、三接口字段角色，以及补环境时 RTCPeerConnection / matchMedia / DOM 标签与 canvas** 的检测点。[产品索引](./products/tencent-captcha.md) 负责命中特征、同轮绑定和 ticket 口径；XTEA 半纯算见 [琴殇 archive 参考](./tencent-tdc-slider-xtea-purecalc-reference.md)；CHAOS_VM 与魔改 TEA 见 [vmp 下篇](./tencent-tdc-slider-vmp-part2-tea-collect-pow.md)。作者未公开补环境代码。

<a id="request-chain"></a>
## 三接口顺序

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 报告称链是 `cap_union_prehandle` → 用返回的 `tdc_path` 拉动态 `tdc.js` → `cap_union_new_verify`。 | s1，「抓包分析」 | source-report | 来源官网 demo | 站点地址只以 archive 内 base64 原文为准，本文不解码。 |
| C2 | 报告称 collect 入口是搜索 `collect:` 后进入 `getTdcData`：先 `TDC.setData`（来源记为方法 a 的固定入参），再 `TDC.getData(!0)`，随后进入约三百行的 jsvmp `tdc.js`。 | s1，「加密入口定位」 | source-report | 来源 collect 路径 | 不收录 setData 入参样值。 |
| C3 | 报告称补环境只为出 collect；算法与轨迹写入留给下篇。本地出值约 900 字符、浏览器约 1700，作者归因于未加轨迹。 | s1，「补环境」收尾、「前言」 | source-report | 作者本地对比 | 长度不是跨版本常数。 |

<a id="parameters"></a>
## 字段角色

| 字段 | 来源描述的角色 | 类别 | 边界 |
|---|---|---|---|
| ua | prehandle 查询里的 User-Agent 的 base64 | encoding | 来源称 demo 其它查询可写死；不外推当前服务端。 |
| sess / prefix / md5 | prehandle 返回，校验时要用 | token | 不收录样值。 |
| tdc_path | 本轮 tdc.js 地址 | 配置 | 动态，不固定旧脚本。 |
| img_url / sprite_url | 背景图与滑块图 | 题面 | 识别不在本篇。 |
| collect | `getData(!0)` 输出 | encoding / fingerprint | 是否强校验看客户配置；作者称官网 demo 与实测多站不校验。 |
| tlg | collect 长度 | encoding | 与产品卡一致。 |
| eks | 从动态 tdc.js 提取 | token | 本篇未给提取步骤。 |
| ans | 前段固定，data 为缺口 x、y | 题面 | errorCode 50 表示距离不对。 |
| pow_answer / pow_calc_time | 井号前段来自 prehandle，后段与耗时要算 | PoW | 算法在下篇。 |

collect 不是“加密参数”统称：它是 TDC 对当前环境（及可选轨迹）的编码输出；是否进入风控由站点配置决定。

<a id="decision-flow"></a>
## 补环境重点

来源称普通属性靠代理就能看见，难点在 DOM。按对象分：

1. `RTCPeerConnection` 原型：`createDataChannel`、`createOffer`、`setLocalDescription`；后两者要返回 Promise。
2. `matchMedia`：多条件查询并读对象属性。具体查询串未在正文展开。
3. `document.getElementById`：按 id 取节点。
4. `document.createElement`：创建之外还要插入、删除、克隆、设/删属性。canvas 还要 WebGL 信息与绘图取图。

作者未列出完整标签表；缺啥补啥，不以本卡当通用浏览器对象清单（后者见 [browser-env-objects.md](./browser-env-objects.md)）。

<a id="validation"></a>
## 验证与限制

- `errorCode` 为 0 返回 ticket；50 表示滑块距离不对。这是来源对 demo 校验响应的报告。
- collect 在 demo 上不校验时，作者把「明文能否逆回去」放到下篇，不把“出值长度接近”当成通过。
- 18 张来源图未审，不当证据。
- 不收录 Cookie、sess、collect、ticket、ua 原文或解码后的云产品 URL。
- 产品卡的 UA 一致性、同轮 sess/`tdc_path`/`pow_cfg` 仍然有效；本篇“查询可写死”只覆盖作者 demo 观察。
