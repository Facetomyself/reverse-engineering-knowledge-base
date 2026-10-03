---
schema_version: 2
id: anti-detection-ruyi-20260425-risk-boundary-reference
document_type: reference
original_date: '2026-04-25'
archived_date: '2026-10-02'
scope:
  targets: [yunpian-captcha]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-browser-anti-detection-compilation/ruyi-20260425-01.md#reference-extraction-121
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 仅整理 JSONP get/verify 的角色、浏览器信息字段类别和响应角色；不含端点、应用 ID、token、回调值、图片 URL 或当前接口清单。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 仅记录 fingerprint/session/callback、AES/RSA 字段关系及轨迹字段类别；不含 key、iv、公钥、Cookie、UA、Referer、密文、坐标或其他样值。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅保留 get → 识别 → 轨迹 → verify 的来源报告链路；不提供可执行客户端、解析失败合同、当前版本兼容或服务端接受证据。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 仅整理响应成功/失败字段类别与作者列出的待排查方向；不把任何字段、状态或失败原因升级为当前服务端规则。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 仅记录速度、轨迹、会话一致性和 token 时效等来源级检查清单；无特征权重、阈值、分类器、挑战结果或规避结论。
relations:
  - type: derived_from
    target: ./ruyi-browser-anti-detection-compilation/ruyi-20260425-01.md#reference-extraction-121
tags: [yunpian-captcha, JSONP, AES, RSA, fingerprint, session, trajectory, risk-control, source-report]
---

# 云片滑块验证码 JSONP 与风控边界参考

这是一张 provider-specific 的窄范围 `source-report` reference，整理来源文章中的接口角色、混合加密字段关系、会话/指纹/轨迹分层、响应验证和风险假设。它不复制配置字面量、凭据、token、图片或轨迹样值，也不把来源代码草图变成可运行 procedure。

<a id="interfaces"></a>
## 接口与字段角色

来源报告把流程分成 get、缺口识别、轨迹生成与 verify 四个角色，并以 JSONP GET 作为传输边界。get 负责返回挑战材料、令牌和几何信息类别；verify 消费轨迹与距离类别并返回业务验证结果类别。回调包装、会话 Cookie 与请求字段应作为同一轮上下文观察，不能仅凭字段名认定当前接口。

<a id="parameters"></a>
## 加密、身份与轨迹参数

来源报告描述紧凑 JSON 先由随机对称 key/IV 进入 AES-CBC/PKCS7，再把密文 Base64 放入一个参数；key 与 IV 的拼接值再由 RSA PKCS#1 v1.5 包装并 Base64 放入另一参数。这里登记的是 envelope 的字段角色，不登记公钥、密钥、IV、明文、密文或服务端解密结果。

身份材料至少分成三层：浏览器 fingerprint 字段、跨请求保持的 session/追踪 Cookie，以及每次请求注册的 JSONP callback。轨迹则单列为绝对 x/y 与时间偏移等字段，来源还描述持续时间、步数、纵向变化、过冲和回弹等模型类别；没有可复核轨迹、事件日志或分类器输出，因此不提供人类轨迹生成器。

<a id="request-chain"></a>
## JSONP 请求链

来源级链路可写成：

```text
get challenge
  -> read challenge geometry / token roles
  -> recognize gap (source lists several alternatives)
  -> build trajectory categories
  -> verify with the same session and callback context
```

callback 解析、token 续接、浏览器字段和加密 envelope 是同一请求面的组成部分，但来源没有当前抓包、回调注册 trace、超时/畸形响应处理或 response receipt。第三方识别服务、OCR 和图像材料只保留“方法类别”这一层，不进入本卡。

<a id="validation"></a>
## 响应验证边界

来源文章给出 JSONP 成功/失败字段的类别，并把缺口位置、轨迹机械性、token 过期和频率限制列为可能失败方向。这些是作者的排查假设；没有服务端响应、状态码、业务读回、字段必填矩阵或版本对照，不能据此判断成功，也不能把某个失败原因当作风控规则。

<a id="risk-control"></a>
## 风控检查清单

可检索的来源级检查维度包括轨迹速度与时间分布、纵向变化、过冲/回弹、请求间隔、fingerprint 格式、UA/Referer 一致性、token 年龄和缺口精度。它们只构成待验证的观测清单，不是权重或阈值模型；本卡不提供规避建议，不声称模拟身份或行为即可通过。

## 验证与限制

- 来源没有可定位公开原文、SDK 快照、当前网络捕获或独立响应证据；target、version、observed_at 和 source completeness 保持未知或来源级描述。
- 原文含应用/端点、公钥、指纹、Cookie、token、图片、第三方 credential、坐标和响应样例；本卡只保留角色类别，不复制任何字面样值或私有 endpoint。
- 本轮未运行浏览器、SDK、JSONP、AES/RSA、图像识别、local parity、请求重放或服务端验证；不构成 procedure、runtime case、server-accepted 或通用风控结论。
