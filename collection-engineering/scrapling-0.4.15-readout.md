---
schema_version: 2
id: scrapling-0-4-15-readout
document_type: archive
original_date: "2026-10-08"
archived_date: "2026-10-09"
scope:
  targets: [Scrapling]
  client: python
  version: "0.4.15"
  observed_at: unknown
sources:
  - id: s-pyproject
    ref: https://github.com/D4Vinci/Scrapling/blob/aa814a77d942678f1a44f68198a0c88550382d28/pyproject.toml
    basis: static-review
  - id: s-parser
    ref: https://github.com/D4Vinci/Scrapling/blob/aa814a77d942678f1a44f68198a0c88550382d28/scrapling/parser.py
    basis: static-review
  - id: s-storage
    ref: https://github.com/D4Vinci/Scrapling/blob/aa814a77d942678f1a44f68198a0c88550382d28/scrapling/core/utils/_utils.py
    basis: static-review
  - id: s-spider
    ref: https://github.com/D4Vinci/Scrapling/blob/aa814a77d942678f1a44f68198a0c88550382d28/scrapling/spiders/spider.py
    basis: static-review
  - id: s-engine
    ref: https://github.com/D4Vinci/Scrapling/blob/aa814a77d942678f1a44f68198a0c88550382d28/scrapling/spiders/engine.py
    basis: static-review
  - id: s-chrome
    ref: https://github.com/D4Vinci/Scrapling/blob/aa814a77d942678f1a44f68198a0c88550382d28/scrapling/fetchers/chrome.py
    basis: static-review
  - id: s-stealth
    ref: https://github.com/D4Vinci/Scrapling/blob/aa814a77d942678f1a44f68198a0c88550382d28/scrapling/engines/_browsers/_stealth.py
    basis: static-review
  - id: s-pages
    ref: https://github.com/D4Vinci/Scrapling/blob/aa814a77d942678f1a44f68198a0c88550382d28/scrapling/engines/_browsers/_validators.py
    basis: static-review
  - id: s-shell
    ref: https://github.com/D4Vinci/Scrapling/blob/aa814a77d942678f1a44f68198a0c88550382d28/scrapling/core/shell.py
    basis: static-review
  - id: s-docs
    ref: https://github.com/D4Vinci/Scrapling/blob/aa814a77d942678f1a44f68198a0c88550382d28/docs/fetching/stealthy.md
    basis: source-report
source_completeness: partial
tags: [Scrapling, collector-boundary, static-review, source-report]
---

# Scrapling 0.4.15 采集边界阅读摘录

这是对 Scrapling `0.4.15`（commit `aa814a77d942678f1a44f68198a0c88550382d28`，2026-10-08）的选段阅读，不是仓库镜像，也不是运行验收。许可证是 BSD-3-Clause。基础依赖是解析器；`fetchers` extra 才带 `curl_cffi`、Playwright、Patchright、browserforge 和指纹数据。本文不粘贴大段源码。

本地浅克隆只作阅读，不进入采集运行时，不注册 `scrapling-mcp`，不替换 `web_case.py next`。

<a id="scope-read"></a>
## 阅读范围

读过的面：包元数据、`Selector.relocate` / `find_similar`、元素字典、Spider 默认并发与 `is_blocked`、浏览器 fetcher 的启动方式、`PagesCount`、shell 里的页面清洗和 curl 解析器、隐身文档对 Camoufox 的自述。

没读成文的面：测试夹具、Shopify / sitemap 模板、完整 MCP 工具表、广告域名表的逐条内容。作者宣传（过检测、解 Cloudflare）保持 `source-report`。从源码读到的机制是 `static-review`。没有 `runtime-observation`、`local-parity` 或 `server-accepted`。

<a id="relocate"></a>
## 列表元素重定位

上游 `element_to_dict` 保存 tag、去掉空值后的属性、节点自身文本、tag 路径；有父节点时再保存父 tag、父属性和父节点自身文本，以及兄弟 tag、子 tag。`relocate` 给整棵树打分，只返回最高分那一组，且最高分必须不低于 `percentage`。默认 `percentage` 是 40。低于阈值时返回空列表，并在日志里留下 top score。`find_similar` 的默认阈值是 0.2，默认忽略 `href` 和 `src`。指纹可以写入 `scrapling/elements_storage.db`。

本仓库不采用 40、0.2 和这个 sqlite。HTML 列表另有干净实现，路径写在代码里：`tools/web-reverse/html_fingerprint.py`。它不 import Scrapling，不写 `elements_storage.db`，不联网。捕获时绑定响应体 SHA-256。比较用 tag、非空自身文本、属性键和值、已保存的 class/id/href/src、路径、父节点（候选没有父节点时不罚分）和兄弟 tag。子 tag 会随快照保存，但不进入得分。默认阈值 75。`relocate` 只返回不低于阈值且并列最高的节点；低于阈值时 `matches` 为空。`find_similar` 排除源节点本身，返回所有不低于阈值的节点。`replay_frozen` 在字节哈希不一致时返回 `body-drift` 和空 `matches`。

这些命中只是解析候选。列薄于请求字段集仍是 `content_invalid`，不是 `serverAccepted`。选择器或指纹变更先对原响应体做 `replay_frozen`，通过后再进 `collector_canary`。`find_similar` 只在一行已经有业务读回之后使用。

<a id="fetchers"></a>
## 浏览器 fetcher

`DynamicFetcher` 的文档写明通过 Chromium 系浏览器取页，可选 `real_chrome`，也可用 `cdp_url` 接已有浏览器。隐身会话文件用 Patchright 启动浏览器，类型注解仍引用 Playwright 的 Page。文档写 StealthyFetcher 在 0.3.13 之前用过 Camoufox，之后改为 Patchright；同一篇仍告诉读者自行安装 Camoufox 再塞启动参数。`pyproject.toml` 的 `fetchers` extra 没有 Camoufox。`PagesCount` 约束是 1 到 50，对应同时打开的标签页池，不是采集页数上限。

文档和类说明里的“过检测 / 解 Cloudflare / canvas 噪声 / WebRTC”是作者自述，本阅读没有跑这些路径。本仓库的浏览器平面仍是：RuyiTrace 3.3 只提供浏览器事实，RuyiDOM 做本地执行，自动化只走 ruyipage Firefox 151、BitBrowser 或 CloakBrowser。Playwright、Patchright、CDP 连接、Camoufox、Cloudflare solver、canvas/WebRTC 噪声、browserforge 请求头、随机 impersonate、默认 Google referer、丢弃静态资源和广告域名表都不进入 Python 采集器。

<a id="spider"></a>
## Spider 默认值与阻塞重试

`Spider` 类默认 `concurrent_requests = 4`、`concurrent_requests_per_domain = 0`、`download_delay = 0.0`、`robots_txt_obey = False`、`max_blocked_retries = 3`。AutoThrottle 默认关闭。`development_mode` 默认关闭；打开且未指定目录时，引擎把缓存放到 `.scrapling_cache/<spider name>`。

`BLOCKED_CODES` 含 401、403、407、429、444、500、502、503、504。`is_blocked` 只看状态码是否落在这个集合。`retry_blocked_request` 默认原样返回该请求。引擎在重试次数小于 `max_blocked_retries` 时再次调度。这不是“换 IP 再试三次”，也不区分代理认证失败和连接被关闭。

本仓库不收这组默认值，不收 `.scrapling_cache`，不收这三次阻塞重试。已有信号名保持不变：HTTP 407 记 `transport`（代理认证失败），HTTP 444 记 `blocked`（连接被关闭）。采集器仍要 `maxItems`、`maxPages`、`minDelaySec` 不低于 0.2、`oneSession`。并发刻度默认保持关闭，直到单独的 AIMD 门打开。

<a id="sanitize"></a>
## 送模型前的页面文本

`_sanitize_for_ai` 的说明写它去掉内联样式隐藏、`aria-hidden`、`template`、HTML 注释、零宽字符和与 XML 不兼容的控制字符。调用点在“只要正文”的提取路径上，位于去掉 script/style/noscript/svg 之后。它不处理靠 class 隐藏的节点，也不处理仍在可见树里、对比度很低的文字。清洗通过不等于内容可信。

本仓库已有一篇讨论 `display:none` 间接提示注入的合集文章。新的操作卡只补充这块缺口，不复制上游 XPath。

<a id="curl"></a>
## DevTools curl

shell 里有一个 `CurlParser`，注释写明面向开发者工具复制出来的 curl，并把结果交给 Fetcher。本仓库没有这个解析器，本批也不新增。复制出来的 curl 只作为请求形状的材料：方法、URL、头和正文。不执行它。HAR 仍是只读材料的主路径。

<a id="reuse"></a>
## 复用边界

可以留下的只有：HTML 列表指纹和冻结体回放的纪律，以及上面三节写成参考或流程的拒绝项。不可以留下的是整包运行时、浏览器启动、MCP、默认并发、阻塞码重试和任何把作者宣传写成已绕过的句子。
