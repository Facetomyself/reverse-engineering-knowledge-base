---
schema_version: 2
id: web-reverse-hcaptcha-invisible-hsw-env-patch-reference
document_type: reference
original_date: '2026-01-14'
archived_date: '2026-10-03'
scope:
  targets: [hcaptcha]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./hcaptcha-invisible-hsw-env-patch.md#reference-extraction-211
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅整理 hcaptcha.html → checksiteconfig → hsw.js/WASM → 校验接口的来源顺序；未请求 hCaptcha 域。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 记录载荷字段角色与 n 的入口；不收录 JWT、sitekey、generated_pass_UUID 或 demo URL。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: Promise 链反跟、WASM 交互大数组对照与九类检测点是来源方法，不是已验证补环境实现。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: P1 前缀通过与失败出验证码图均为作者自述；本轮无 runtime、parity 或 server-accepted。
relations:
  - type: derived_from
    target: ./hcaptcha-invisible-hsw-env-patch.md#reference-extraction-211
  - type: supplements
    target: ./browser-env-objects.md
tags: [hCaptcha, hsw.js, WASM, checksiteconfig, n, motionData, env-patch, source-report]
---

# hCaptcha 无感 hsw.js / WASM 出 n 与环境检测点参考

这张窄卡只整理来源 archive 对 **无感链上 n 值入口（xhr → Promise 链 → `hsw.js` / WASM）以及九类补环境检测点**。作者未公开补环境代码。通用浏览器对象面见 [browser-env-objects.md](./browser-env-objects.md)。RTCPeerConnection 在腾讯滑块上的同类检测见 [TDC collect 补环境参考](./tencent-tdc-slider-vmp-part1-env-patch-reference.md)。catalog 此前无 `hcaptcha` reference。本文不收录 JWT、sitekey、通过 UUID 或 demo 站点 URL。

<a id="request-chain"></a>
## 无感链路与 n 入口

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 报告称 demo 为 Steam 注册页无感勾选。链是 `hcaptcha.html`（`v1/` 后为约一周更新的版本号）→ `checksiteconfig`（响应 `c.req` 为 JWT）→ `hsw.js` → 最终校验接口。 | s1，「目标网站」「抓包分析」 | source-report | 来源 Steam demo | 不收录或解码站点 URL。 |
| C2 | 报告称校验请求体与响应体默认是 ArrayBuffer。改 `hcaptcha.html` 两处（序列化位置、头部 CSP 只留 worker）可走明文 JSON。 | s1，「最后的验证接口」 | source-report | 来源本地改页观察 | 不是官方支持的调试面。 |
| C3 | 报告称 n 的入口：全局 xhr 断点 → 沿 Promise 链反跟 `l ← s ← e.proof` → `Promise.all` 迭代里的 `xr` → `n(i.req, o)` 进入 `hsw.js`，先解码 JWT，再由 `aG` 加载 WASM。 | s1，「逆向分析」 | source-report | 来源所见 hsw.js | 标识符随版本变。 |

<a id="parameters"></a>
## 字段角色

分开 encoding、token、fingerprint：

| 字段 | 来源描述的角色 | 类别 | 边界 |
|---|---|---|---|
| v | hCaptcha 版本号 | 配置 | 随 `hcaptcha.html` 路径更新。 |
| sitekey | 站点唯一 key | token | 不收录样值。 |
| host / hl | 域名与语言 | 配置 | 来源明文 JSON 列表。 |
| pdc / pem | 含时间相关参数 | encoding | 未展开算法。 |
| c | 来自 checksiteconfig | token | JWT 不收录。 |
| motionData | 时间戳、轨迹等环境信息 | fingerprint | 不收录轨迹样值。 |
| n | `hsw.js` / WASM 核心输出 | encoding | 入口如上；内部算法未恢复。 |
| generated_pass_UUID | 响应；以 `P1` 开头表示通过 | token | 不收录 UUID。 |

n 不是“加密参数”统称：它是 hsw/WASM 对挑战 JWT 与环境材料的编码输出。

<a id="decision-flow"></a>
## 插桩对照与检测点

来源把入口定位和补环境对照分开：

1. WASM 与 JS 持续交互。一处大数组在 `kc.Ob` → `fm`（WASM 导出）里 `Mv`；另一处是首参为数字串的检测函数写入的环境数组。两处都用来对照本地与浏览器差异。
2. 九类检测点（来源列举，不是完整清单）：`RTCPeerConnection`；`RTCRtpSender` / `RTCRtpReceiver`；`OfflineAudioContext`；`WebGL2RenderingContext`；描述符（`"prototype" in AudioBuffer.prototype.getChannelData`，要用箭头函数）；Math 精度；字体；canvas；Worker / SharedWorker。
3. 作者称补了三千多行；环境不过会返回验证码图片链接。

<a id="validation"></a>
## 验证与限制

- 通过口径是响应 `generated_pass_UUID` 以 `P1` 开头；失败出验证码图。这是来源自述，不是本轮 server-accepted。
- `source_completeness=partial`：50/54 张图已替换为隐私占位，4 张通用 API 结构图保留。图片不当证据。
- 不收录 Cookie、JWT、sitekey、pass UUID、demo URL 或补环境实现。
- 证据-80 已全文阅读并完成图片隐私，当时因重叠待审未发 reference；本批定向 query `--target hcaptcha --type reference` 仍为 0，故发布本窄卡。
