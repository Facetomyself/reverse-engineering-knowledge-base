---
schema_version: 2
id: web-reverse-datadome-env-patch-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-03'
scope:
  targets: [datadome]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./datadome-env-patch.md#reference-extraction-199
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅转述来源对无感 interstitial 顺序的报告；未复现 403、Device Check HTML、POST 或业务读回，不能证明当前站点或 captcha 升级链。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录字段角色与动态/稳定分层；不把 payload/plv3 统称为加密参数，不收录密文、Cookie、设备值或可运行采集器。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: iframe 生命周期、Worker 异步链、VM 第一处分叉和 CSS 布局是来源排查顺序，不是通用补环境清单或已验证实现。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 本地字段门、view=redirect、新 Session 业务 200 与次日 Cookie 失效均为作者自述；本轮未请求目标、未做 parity 或 server-accepted。
relations:
  - type: derived_from
    target: ./datadome-env-patch.md#reference-extraction-199
  - type: supplements
    target: ./products/datadome.md#常见链路
tags: [DataDome, interstitial, payload, plv3, iframe-realm, OffscreenCanvas, jsdom, VM-fork, source-report]
---

# DataDome 无感 interstitial 补环境边界参考

这张窄卡只整理来源 archive 对 **无感 interstitial** 的请求顺序、字段分层、排查分叉和验收口径。产品命中与 captcha fallback 仍以 [DataDome 产品索引](./products/datadome.md) 为准；本文不替代该索引，也不把作者“连续 200”升级为本轮 runtime 或服务端验收。

<a id="request-chain"></a>
## 请求链

来源报告的无感链是：空 Cookie 新 Profile 触发设备检查 → 入口页 403 并下发临时 `datadome` Cookie 与 Challenge 上下文 → 拼出 `/interstitial/` 拿到 Device Check HTML/核心 JS → 由原脚本在 jsdom+vm 中自然触发 POST `/interstitial/` → `view=redirect` 且带 Cookie 后，**新建只含该 Cookie 的 Session** 再访问业务页。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 报告称入口 403 页面提供 cid、hash、e/s/b、host 与临时 Cookie，用来拼 Device Check 地址。 | s1，来源「抓包分析」 | source-report | 来源所述无感设备检查 | 未取得 HTML/JS；host 与样值不收录。 |
| C2 | 报告称核心 POST 由原脚本自己触发，本地只替换 XHR 捕获器，不手动调用内部 send 函数。 | s1，来源「加密入口定位」 | source-report | 来源 jsdom+vm 执行器 | 字段顺序、定时器和调用栈依赖未独立验证。 |
| C3 | 报告称 `view=captcha` 表示升级到交互验证，本文不覆盖该分支。 | s1，来源「验证 POST」 | source-report | 无感失败/升级出口 | 升级条件与 captcha 链见产品索引，本文不展开。 |

<a id="parameters"></a>
## 参数分层

| 参数组 | 来源描述的角色 | 类别 | 边界 |
|---|---|---|---|
| payload | 环境采集写入内部容器后再编码的提交字段 | encoding（来源称加密结果，本文不升格 encryption） | 无算法、密钥或密文。 |
| plv3 | 与运行环境、布局和时间相关的另一段提交字段 | encoding | 与 payload 分开记录；VM 分叉会放大差异。 |
| cid / hash / seed | Challenge 页面给出的动态配置 | token / 配置 | 每轮从当前页解析，不硬编码历史值。 |
| env / userEnv | 服务端下发的环境标识 | token | 来源未给出 schema。 |
| ps | 页面尺寸相关数据 | fingerprint / 布局 | 与 CSS 计算宽度相关，不能写死像素。 |
| 稳定环境字段 | 多次 Challenge 都相同、进入 Provider | fingerprint | Chrome 轨迹是校准，不是整包复制。 |
| 异步可选字段 | 字体/Worker 等探针允许缺失 | fingerprint | 须先用多次浏览器结果证明可选，再严格核对其余键与顺序。 |

<a id="decision-flow"></a>
## 排查顺序

来源把“能出值”和“值正确”分开。建议检索时按下列分叉走，不要从最终密文反推：

1. iframe Realm：脚本从 iframe `contentWindow` 读 Math/原型/原生函数。内部加载能力若过早删除或一直保留，都会破坏生命周期；需要分阶段存在，而不是一次性删光 jsdom 内部属性。
2. Worker / OffscreenCanvas：最小通信链是 Blob → 临时 URL → Worker 构造与异步消息，而不是同步返回或写死最终字段。
3. 跨 Challenge 把字段分成稳定、随 Challenge 变化、允许异步缺失三类。
4. 仍不一致时，把范围缩到自定义 VM：对齐随机与时间序列，比较 `(step, pc, sp)`，**修第一处分叉**，而不是末尾差一字节。
5. `offsetWidth` 来自祖先 CSS 自定义属性、`var()` / `calc()` / `clamp()` / px，随 Challenge 变化；写死像素会在下一轮失败。

<a id="validation"></a>
## 验收口径与限制

| 观察 | 来源允许的最小结论 | 不允许的外推 |
|---|---|---|
| 本地字段行数、键集合、顺序与 Provider 队列闭合 | 发送前一致性门（作者自述） | 当前脚本、当前站点或算法已复现 |
| POST 返回 `view=redirect` 并下发 Cookie | 无感保护链的中间口径 | 业务已放行 |
| 新 Session 只带该 Cookie 访问业务页连续 200 | 来源称生成链路有效、不是历史 Cookie | 本轮 server-accepted |
| 次日旧 Cookie 再测 403，重跑 Node 可再签发 | 来源用来排除碰巧有效的历史值 | Cookie TTL 或风控规则已查明 |

## 验证与限制

- 来源不可公开定位，`client` / `version` / `observed_at` 均为 unknown；目标站 URL 已编码，本文不回写。
- 产品索引已覆盖命中特征与 captcha 链；本文只补 interstitial 执行细节，不复制 Cookie、payload/plv3 样值、设备 Profile 或请求体。
- 未运行 jsdom、浏览器、网络或目标服务；截图与内联代码缺口按 source-report 保留，不升级为 procedure。
