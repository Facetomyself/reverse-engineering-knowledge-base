---
schema_version: 2
id: web-reverse-cloudflare-5s-v2-fo-pipeline-reference
document_type: reference
original_date: '2026-07'
archived_date: '2026-10-03'
scope:
  targets: [cloudflare]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./cloudflare-5s-v2-fo-pipeline.md#reference-extraction-205
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅整理 /fo 与 form.submit 完成门、Python/Node 分工和主站/子站分计；未跑 ruyitrace 或目标 challenge。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录 _cf_chl_opt 字段角色与 3 hidden 对照；不收录 Cookie、cf_clearance、hidden 名/值或 /fo body。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 状态机、A/B 形态和补环境阶段是来源排查顺序，不是已验证实现或五门 procedure。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 业务 200 非 challenge 才是完成；cf_clearance、reload、第 N 次 /fo、子站 accepted 都不是完成。本轮无 runtime。
relations:
  - type: derived_from
    target: ./cloudflare-5s-v2-fo-pipeline.md#reference-extraction-205
  - type: supplements
    target: ./products/cloudflare-5s-challenge.md#常见链路
tags: [Cloudflare, /fo, form.submit, orchestrate, Turnstile, document.all, source-report]
---

# Cloudflare 5s v2 `/fo` 与 form.submit 参考

这张窄卡只整理来源 archive 对 **`cFPWv=g` / `cType=managed` 的 `/h/<g|b>/fo/`** 路径：Python/Node 分工、主站与 Turnstile 子 `/fo` 分计、accepted 后 3 hidden 的 form.submit。课程材料的 `flow/ov1` 命中与分层成功口径仍以 [Cloudflare 5s 产品索引](./products/cloudflare-5s-challenge.md) 为准；产品卡已把本路径留给这篇 archive。

<a id="request-chain"></a>
## 完成门与分工

来源报告的完整成功只有一条：业务 GET → 403 `_cf_chl_opt` HTML → 本轮 fresh orchestrate → Node 自然发出每次 `/fo` → Python 真实发送并把完整 XHR envelope 回灌 → 主站 accepted（`text/html` + `Set-Cookie: cf_clearance`）→ orchestrate 自己 `createElement(form/input)` 并 `HTMLFormElement.submit()` → 同一会话 POST 原业务 URL → 业务 200 且不再是 challenge。

`cf_clearance` 之后若只有 `location.reload()`，或带着 cookie 再 GET 仍 403，记失败。业务通过后的 JSD 是后续检测，不并入 5s 主状态机。

| 层 | 做 | 不做 |
|---|---|---|
| Python | 真实 HTTP、解析 opt、选 `/h/g/` 或 `/h/b/`、会话/TLS/头序、分类回灌、最终业务 POST | 构造 `/fo` body、猜 proof、硬拼 clearance 或 3 hidden、无 form.submit 时冒充 POST |
| Node | DOM/BOM、跑本轮 orchestrate、自然出 `/fo` body 与 form.submit telemetry | 直连目标、发最终 POST、屏蔽 debugger Worker、用固定 sleep 换顺序 |

主站与 Turnstile 子 `/fo` 会交错。request id 按 host + 路径三元组 + `cRay` + `cH` + 序号，不用全局 `fo_index`。子站 `text/html` accepted 无主站 cookie，不当主站通过。`GET /pat/` 401 与 brunhild `/i/` status 0 是子链探测。

<a id="parameters"></a>
## 字段角色

Python 每轮把 HTML 字段转给 Node，不拿它们拼 `/fo` body，也不跨轮复用：

| 字段 | 来源描述的角色 |
|---|---|
| `cFPWv` | 路径族 `/h/g/` 或 `/h/b/`，不区分无感/点击 |
| `cRay` / `cH` | orchestrate 与 `/fo` URL |
| `cUPMDTk` | 恢复路径里的 `__cf_chl_tk` |
| `cITimeS` | 本轮时间片 |
| `md` / `mdrd` | 本批最终 POST 前两个 hidden value 的来源；长度是样本形态 |
| `__cf_chl_tk` | Referer / challenge URL |

accepted 之后创建 form：`method=POST`、urlencoded、三个 type=hidden（name 长度 64）。来源对照：`hidden[0].value` 对应本轮 `md`，`hidden[1]` 对应 `mdrd`，`hidden[2]` 不是二者、时间片晚于初始 HTML。三个 name 都不是 `sha256(value)`。字段名和第三个 value 必须由 accepted 分支自然生成。POST body 长度只是本批对照，不是跨版本常数。

<a id="decision-flow"></a>
## 形态、阶段与分类

近期四份 trace 都是 `cFPWv=g`、`cType=managed`。orchestrate 每轮变，不能缓存。

| 类型 | `/fo` 计数 | clearance | 最终动作 |
|---|---|---|---|
| A 无感 | 主站 2 + 子站 2 | 主站第 2 次 | 四阶段 `form_submit`，未直接命中 `HTMLFormElement.submit()` call |
| B 点击 | 仅主站 3，无子 `/fo` | 主站第 3 次 | 直接 `HTMLFormElement.submit()` |

`api.js?render=explicit` 只说明 Turnstile runtime 在；出现子 iframe 和子 `/fo` 才进 widget 子 challenge。类型 B 只有 `api.js` 时不能删掉 Turnstile 支持，也不能强行补子链。预置假 `window.turnstile` 会走进 duplicate/upgrade。

补环境按阶段退出：先闭环 fo1 `loadend`，再迁 Worker/Blob（`createObjectURL` → Worker → eval → `postMessage`）、srcdoc iframe、事件（合成 `isTrusted=false`，真实 `pointermove` `isTrusted=true`）、timer、Form。没有同阶段 trace 读取不补。`document.all` 在本批 jscall 无读取窗口，命中后再按表达式最小补，禁止补成普通对象。

分类键是 host、三元组、`cRay`、`cH`、Content-Type、是否 clearance、是否 `form.submit`。`text/plain` 大材料是 `FO_CONTINUE`；主站约 3440 HTML + clearance 是 `FO_ACCEPTED`；约 3112 HTML + reload + 再 403 是失败循环。不能用单一首包大小判失败。

<a id="validation"></a>
## 验收口径与限制

| 观察 | 来源允许的最小结论 | 不允许的外推 |
|---|---|---|
| 业务 POST 200 且非 challenge | 本轮 5s 完成 | 当前站点或版本仍如此 |
| 主站 Set-Cookie `cf_clearance` | accepted 中间态 | 业务已放行 |
| 子站 `/fo` HTML accepted | 子链材料 | 主站通过 |
| `location.reload()` / 第 N 次 `/fo` | 需继续等 form 或判失败 | 完成 |
| 模块有 smoke + 指定 trace 回放 | 来源准入建议 | 本轮已验证实现 |

禁止：硬拼 `/fo` body、clearance、3 hidden、Turnstile token；在 Node 发真实网络；把旧 trace 业务 body 当 live body。

## 验证与限制

- 来源不可公开定位；`client` / `version` / `observed_at` 均为 unknown。样本业务页与字段值不收录。
- 未运行 ruyitrace、浏览器或目标 challenge；证据优先级以 live 403/orchestrate/`/fo` 为 P0。
- 不构成 procedure。产品索引的 Turnstile token / WAF clearance / business accepted 三层口径仍然有效，本卡只补 `/fo` 形态。
