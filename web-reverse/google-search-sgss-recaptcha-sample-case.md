---
schema_version: 2
id: web-reverse-google-search-sgss-recaptcha-sample-case
document_type: case
original_date: unknown
archived_date: "2026-10-16"
scope:
  targets: [google-search, google-recaptcha]
  client: web
  version: unknown
  observed_at: "2026-10-16"
sources:
  - id: s1
    ref: ./google-search-sgss-recaptcha-sample-source-archive.md#source-body
    basis: source-report
  - id: s2
    ref: https://github.com/QS-qinshaowen/Coding
    basis: static-review
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2]
    basis: static-review
    limits: 只覆盖样本声明的本机 RPC/CDP 口与 Python 类方法；未把该口接到当前 Google 搜索页。
  - name: parameters
    anchor: parameters
    sources: [s1, s2]
    basis: static-review
    limits: 只登记 SG_SS / userverify token 的角色与读取位置；不含算法恢复或样值。
  - name: request-chain
    anchor: request-chain
    sources: [s1, s2]
    basis: static-review
    limits: 静态阅读样本控制流；本轮未对 Google 发搜索或 recaptcha 请求。
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2]
    basis: static-review
    limits: 记录样本自称的隔离上下文、离线代理与 UA 画像；未验证这些选择对服务端评分的作用。
  - name: validation
    anchor: validation
    sources: [s1, s2]
    basis: static-review
    limits: 模块按静态阅读登记。本轮本机探测回执留在项目笔记，不作为 Public runtime-observation 来源，也不把打包 JSON 升为当前服务端接受。
relations:
  - type: derived_from
    target: ./google-search-sgss-recaptcha-sample-source-archive.md#source-body
  - type: supplements
    target: ./products/google-recaptcha-v3.md#验证口径
tags: [google-search, google-recaptcha, SG_SS, enterprise, iv8, CDP, static-review]
---

# Google 搜索 SG_SS 与 reCAPTCHA Enterprise 样本能力（案例）

## 问题与范围

范围限定为公开仓库 `QS-qinshaowen/Coding`（`main` / `fdee33e`）展开后的三份实现：reCAPTCHA Enterprise 用户验证入口、Chrome CDP `SG_SS` RPC、iv8 `SG_SS` 客户端。操作是静态阅读加本机语法/依赖检查；不对 `www.google.com` / `www.google.com.hk` 发搜索或验证码请求。reCAPTCHA v3 invisible 的产品口径仍以 [Google reCAPTCHA v3 / invisible](./products/google-recaptcha-v3.md) 为准，本文不把 Enterprise `userverify` 链与 v3 `reload`/`rresp` 合并，也不与知识库中尚未入库的 reCAPTCHA 73 VMP 笔记合并。

<a id="interfaces"></a>
## 接口

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | sgss_chrome 对外是本机 `POST /sgss` JSON（html、url、timeoutMs、可选 cookies），另有健康检查。Python `execute()` / `get_sg_ss()` 只打该口；`get_cookie()` 才会做 HTTP 搜索。 | s2，客户端与 RPC 入口 | static-review | 该样本默认 4083/9491 | 未在 Windows 上把服务跑到 ready。 |
| C2 | recaptcha 样本的可导入类型是 `EnterpriseUserVerifyClient`；成功字段走 `userverify` 解析而不是 grecaptcha 回调。 | s1/s2，run_enterprise 头部与解析函数 | static-review | 该 zip 内脚本 | 未在本轮启动 Node runner。 |

<a id="parameters"></a>
## 参数

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C3 | 搜索挑战页的判定是 HTML 同时出现 `SG_SS` 与 `knitsail`。执行结果字段包括 `sg_ss`、`sg_ss_len`、`source`。 | s2，`is_challenge` 与 RPC 返回 | static-review | 该客户端 | 未取得真实挑战 HTML。 |
| C4 | `SG_SS` 的读取顺序是控制台 `SGSS_RESULT` 优先，否则当前 `document.cookie`。iv8 版显式声明 `browser_equivalent` 为假。 | s2，CDP evaluate 与 iv8 `__sgss_read` | static-review | 该两份实现 | 不是 Google 挑战脚本的算法说明。 |
| C5 | Enterprise 样本把最终交付定在 `uvresp` token，成功还要求响应码为 1 且没有后续 `rresp` 挑战。打包结果里业务校验状态为 `not_performed`。 | s2，`parse_userverify_response` / `normalize_result_evidence` | static-review | 该脚本合同 v3 | 打包 JSON 不是本轮 live 验收。 |

<a id="request-chain"></a>
## 请求链

```text
sgss_chrome get_cookie:
  curl_cffi GET 搜索 URL（impersonate chrome133a）
  → is_challenge(html)
  → POST 本机 /sgss {html, final url}
  → 常驻 Chrome 新 BrowserContext，Fetch 把主文档换成传入 HTML
  → 读 SG_SS
  → 带 cookie 再 GET retry_url(sei=eid)
  → 接受条件：2xx 且 URL 不含 /sorry/ 且不再是挑战页

recaptchaV3 run_enterprise:
  Node runner + JS 核心
  → POST /recaptcha/enterprise/userverify
  → 解析 )]}' / uvresp
  → 写 output/results/enterprise_result.json
```

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 上述两条链是样本里写死的控制流，彼此独立。 | s1/s2 | static-review | 该 commit | 未对外部主机复现。 |

<a id="risk-control"></a>
## 风控面

样本为 Chrome 任务建隔离 BrowserContext，并用本机离线代理挡住非主文档请求。UA / Client Hints 写成 macOS Chrome 155 画像。iv8 侧复制同一类 navigator/GPU 元数据，但实现自己列出 canvas/WebGL/导航 timing 缺口。这些是客户端自洽选择，不是已验证的过检条件。

<a id="validation"></a>
## 结论与反例

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | 七个入口语法检查通过；Python 依赖与 iv8 模块可导入。 | s2 文件存在性 | static-review | 本机工具链 | 不等于挑战通过。 |
| C8 | Windows 上 Chrome 启动器进程会以 exit 0 结束，CDP 口仍可能存活；样本把 `exitCode !== null` 当成失败，因此自带 RPC 服务到不了 ready。 | s2 启动循环 | static-review | Windows Chrome 155 启动器行为 | 未改样本；macOS 路径未测。 |
| C9 | 打包 `enterprise_result.json` 自报 `ok` 与 `protocol_completed`，token 长度非零，业务校验 `not_performed`。 | s2 结果文件字段名 | static-review | 该 zip 内历史产物 | 不能当成当前 Google 接受。 |
| C10 | README 中的本地集成测试文件不在 zip 里，不能按文档宣称测试套件已随仓库交付。 | s1/s2 | source-report + static-review | 该 commit |  |

本轮另用仓库 Node 22 与 iv8 0.1.4 做了不连 Google 的探测：iv8 对写入 `SG_SS` 的 mock HTML 能读回同长度标记；Chrome RPC 按原脚本无法 ready。这些回执只在项目 `workspace/google/agent-notes/`，Public 模块不升 `runtime-observation` 或 `server-accepted`。

## 未决项与复用启示

- 真实 `SG_SS` 挑战 HTML 与 Google 搜索重试是否放行，仍缺。
- Enterprise 样本与知识库现有 v3 `reload`/`rresp` 参考不是同一条请求链。
- 若要在 Windows 上跑 CDP 服务，需要改启动等待（以 `/json/version` 为准而不是 launcher exitCode），这超出本案例的静态阅读范围。
- zip 缺 mock HTML，不能把 README 的 10 项集成测试当成可运行资产。
