---
schema_version: 2
id: anti-detection-chromium-startup-cookie-manager-reference
document_type: reference
archived_date: '2026-10-02'
scope:
  targets: [chromium-startup-cookie]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./chromium-fingerprint-compilation/02-进阶/04-startup-cookie-injection.md#reference-extraction-117
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 仅整理来源报告中的 `StoragePartitionImpl`、browser-process `CookieManager`、`CanonicalCookie` 与启动参数解析边界；没有源码 checkout、编译或运行时调用链证据。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留启动 switch、JSON list/dict 和 domain/name/value 的角色，不复制 Cookie、域名、命令行或请求样值；字段缺失、类型错误和多值策略未由来源闭合。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 记录启动参数到 `SetCanonicalCookie` 的来源链；这不是业务 HTTP 请求链，未证明后续请求携带、持久化回读或服务端可见。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 来源只给出命令与截图式结果描述；callback 结果、错误处理、数据库回读、后续请求读回和 server acceptance 均未知，末尾图片未做视觉审查。
relations:
  - type: derived_from
    target: ./chromium-fingerprint-compilation/02-进阶/04-startup-cookie-injection.md#reference-extraction-117
tags: [Chromium, startup, CookieManager, StoragePartition, CanonicalCookie, source-report]
---

# Chromium 启动 CookieManager 参考

这是一张窄范围 `source-report` reference，用于检索 Chromium 启动参数到 browser-process Cookie API 的接缝。它不把来源文章中的示例值或“写入成功”表述升级为本轮运行时事实，也不是可直接复用的 Cookie 注入 procedure。

<a id="interfaces"></a>
## 接口边界

来源将入口放在 `StoragePartitionImpl::GetCookieManagerForBrowserProcess()`：当 browser-process 的 CookieManager 未绑定或连接失效时，先通过 `GetNetworkContext()->GetCookieManager(...)` 建立 Mojo receiver。随后来源代码读取启动命令行、解析 JSON，并为每个字典项调用 `net::CanonicalCookie::Create`，最后把对象交给 `network::mojom::CookieManager::SetCanonicalCookie`。

这里要区分三个层次：

1. `base::CommandLine` / `base::JSONReader` 是启动输入解析面。
2. `GURL`、`net::CanonicalCookie` 是本地 cookie 结构化面。
3. browser-process `CookieManager` 是写入请求面，回调只被来源留作日志或错误处理位置。

函数、Mojo 接口和调用位置只对来源所称 Chromium 源码快照有效；本卡没有核对当前 Chromium 分支的签名或线程时序。

<a id="parameters"></a>
## 启动参数与数据形状

来源把启动 switch `set-cookies` 描述为一个 JSON list；列表项预期是 dict，并包含 `domain`、`name`、`value` 三类角色。`domain` 被当作 URL 输入，再参与 cookie line 和 `CanonicalCookie::Create`；`name` 与 `value` 参与 cookie 内容构造。

本卡只保留字段角色，不保留原文的 URL、Cookie name/value、账号材料或完整命令行。来源代码对 JSON 类型做了有限判断，但没有给出缺字段、非法 URL、`Create` 返回空值、重复调用或跨域属性的完整策略，不能把该形状当作通用输入合同。

<a id="request-chain"></a>
## 启动到写入请求链

```text
process command line
  -> read set-cookies switch
  -> JSON list/dict parsing
  -> domain URL + cookie field assembly
  -> CanonicalCookie::Create
  -> browser-process CookieManager::SetCanonicalCookie
  -> source callback boundary
```

这条链描述的是浏览器启动阶段的本地写入调用面，不等同于页面发起的网络请求。来源没有提供 CookieStore 持久化确认、导航后的请求抓包、同源匹配读回或服务端响应，因此不能据此推导登录态建立或业务请求成功。

<a id="validation"></a>
## 验证边界

| 观察 | 最小可保留结论 | 不可外推 |
|---|---|---|
| 来源给出启动命令和结果截图 | 作者报告过一次启动写入观察 | 当前 Chromium 构建、所有 Cookie 属性或后续网络请求均已验证 |
| 代码注册 `SetCanonicalCookie` callback | 存在异步结果回调位置 | callback 成功、持久化完成或服务端接受 |
| 来源提到 Chromium 版本差异 | 接口可能随源码版本变化 | 可跨版本直接编译或线程语义不变 |

本卡全部模块均为 `source-report`。本轮未下载或审查来源图片，未运行 Chromium、未抓取请求、未做本地 parity，也未进行 server acceptance；需要这些证据时应另建有明确前提和失败出口的 procedure/case。
