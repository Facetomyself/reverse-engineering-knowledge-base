---
schema_version: 2
id: web-reverse-google-search-sgss-recaptcha-sample-source-archive
document_type: archive
original_date: unknown
archived_date: "2026-10-16"
scope:
  targets: [google-search, google-recaptcha]
  client: web
  version: unknown
  observed_at: "2026-10-16"
sources:
  - id: s1
    ref: https://github.com/QS-qinshaowen/Coding
    basis: source-report
source_completeness: partial
tags: [google-search, google-recaptcha, SG_SS, enterprise, iv8, CDP, source-report, partial]
---

# Google 搜索 SG_SS 与 reCAPTCHA Enterprise 样本（来源归档）

## 清洗与完整性说明

公开仓库 `QS-qinshaowen/Coding` 在 `main` / `fdee33e` 以四个 zip 交付。展开后 `Google/` 目录无可读实现；`sgss_chrome` README 提到的 `test_rpc.py`、`examples/*.html`、`start.command` 不在 zip 内。macOS `__MACOSX` 元数据已忽略。token、Cookie、指纹 JSON 原值与 sitekey 常量不进入本文。完整性 `partial`。

<a id="source-body"></a>
## 来源正文（结构摘要）

仓库 README 称样本覆盖 Google 搜索专项：reCAPTCHA v3 与 sgss 参数，并提供内部实现供参考。实际展开后的可读入口是三份：

1. `recaptchaV3`：Python `run_enterprise.py` 加同级 `browser_core.js` / `recaptcha_runner.js`。注释写明 Python 3.10+ 与 Node.js 22。协议解析认 `)]}'` 前缀与 `uvresp`，成功口径是 `userverify` 响应而不是 SDK 回调。打包目录含 `output/results/enterprise_result.json` 与若干 challenge 截图。
2. `sgss_chrome`：独立 Node HTTP RPC（默认 `127.0.0.1:4083/sgss`）加上常驻 Chrome CDP（默认 9491）。README 写明不是 `eval(html)` / `setContent`；用 Fetch 拦截主文档并 `fulfillRequest` 回传入 HTML，再从 `document.cookie` 的 `SG_SS` 或控制台 `SGSS_RESULT` 取值。Python `get_cookie()` 才会用 curl_cffi 拉搜索页并重试。
3. `sgss_iv8`：单文件 Python 客户端，用 `iv8.JSContext` 加载同一类 HTML 快照，注释写明 `browser_equivalent` 为假，WebGL/导航 timing 等与 CDP 不等价。

Chrome 启动等待循环在 `chrome.exitCode !== null` 时直接失败。Node 查找在 recaptcha 入口优先环境变量 `NODE_EXE`，否则 macOS 固定路径，再 `PATH`。
