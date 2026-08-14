# Imperva Reese84 — Canadian North 案例

> 来源: canadiannorth-imperva-v1 项目（84 纯算成品吸收）
> 归档日期: 2026-08-14
> 分类: web-reverse
>
> Imperva/Incapsula reese84 在 Canadian North（Sabre 5TDX 航司订票站）的纯算落地案例：
> curl_cffi 管线 + Node vm 执行器契约 + GraphQL 业务层验证。

## 目标画像

- 站点: `bookings.canadiannorth.com/dx/5TDX/`，Sabre Dev Studio 5TDX 前端（bundle 版本 7.1.10-479.7.1）
- 风控: Imperva Incapsula 完整 cookie 家族（`visid_incap_*` / `nlbi_*` / `incap_ses_*`）+ `reese84`
- 业务面: `/api/graphql`（`dcmcInit` 会话初始化 → `bookingAirSearch` 航班搜索）
- 落地方式: 纯算（challenge POST 由本轮动态 JS 在 vm 内产出，TLS 客户端真实提交）

## 完整链路（本案例实证）

```text
GET 首页 (curl_cffi impersonate=firefox135 + UA Firefox 151.0)
  → Set-Cookie: CID / SSWGID / GCLB / visid_incap_* / nlbi_* / incap_ses_*
  → 首页 HTML 提取本轮动态 challenge script src（每轮变化）
GET challenge script（Sec-Fetch-Dest: script / Sec-Fetch-Mode: no-cors）
  → Node vm 执行器（见下节契约）
  → 捕获 challenge JS 自发的 POST（solution.interrogation.p）
POST 同路径 + ?d=<host>（content-type: text/plain; charset=utf-8）
  → 响应 JSON { token, renewInSec, cookieDomain }
  → token 写 reese84 cookie（domain .canadiannorth.com）
POST /api/graphql dcmcInit
  → 响应头 execution 作为会话执行标识
POST /api/graphql bookingAirSearch（带 execution + x-sabre-* 头）
  → originalResponse 含航班数据 = 放行
```

同一轮对应关系必须成立：首页 HTML → 动态 src → 当前 challenge 脚本 → 当前 POST body.p →
当前 token → 当前业务请求。任何一环复用历史值都会导致 challenge 重放失败或业务被拦。

## vm 执行器契约（核心方法论点）

纯算复现 reese84 的关键是让**本轮动态 JS 自己产出 p**，而不是手工拼 body。本案例的执行器
契约：

1. **输入**: challenge 脚本经 stdin 传入（不落盘持久化，临时文件执行后清理）；
   `VA_BROWSER_ENV_CONFIG` JSON 注入 `pageUrl / requestReferer / documentReferrer /
   userAgent / challengeScriptPath / initialCookies` 等本轮事实
2. **伪浏览器环境**: 模拟 document/script 加载、fetch/XHR 包装与 Sec-Fetch-* 头合成；
   canvas toDataURL / audio 等指纹资产从 trace 提取后内嵌兜底
3. **捕获条件**: hook 后的 fetch 仅匹配「method=POST 且 pathname == 本轮 challenge 路径
   且 body JSON 的 `solution.interrogation.p` 为 string」的请求
4. **拦截不真实发网**: 命中后返回占位 200（token 占位值），让 challenge 状态机继续走完
5. **交接**: stdout 输出单行 JSON：`actualPostUrl / actualPostMethod / actualPostBodyText /
   requestPayload / observedRequests`，由 TLS 客户端（curl_cffi）用真实网络栈提交
6. **多请求观察**: challenge 执行中可能发出多个请求，`observedRequests` 记录全部请求边界，
   只截获 p POST，其余放行到伪环境内部处理

这样设计的理由：p 只在 fetch/XHR 请求边界出现，vm 内真实发网会引入 TLS/HTTP 指纹与状态
不一致；把「产 p」与「提交」分离，产 p 用 vm（快、可复跑），提交用 TLS 客户端（指纹可控、
cookie jar 同 session 延续）。

## 风控 cookie 家族与业务头的对应

- 首页带出的 `CID` cookie 值直接用作 GraphQL `conversation-id` 头 —— 会话标识贯穿
  challenge 阶段与业务阶段
- GraphQL 必带头: `x-sabre-storefront: 5TDX` / `x-sabre-path: DC` / `x-sabre-flow: b2c` /
  `application-id` / `x-request-id` / `execution` / `Idempotency-Key`
- `execution` 由 `dcmcInit` 响应头下发，`bookingAirSearch` 必须回带 —— 缺失时业务请求被拒

## 实证坑

- UA 与 impersonate 的浏览器家族必须一致（Firefox 151 UA 配 firefox135 impersonate）；
  家族不一致时 challenge 环节就可能被拦截，轮不到业务层报错
- 初始 `visid_incap_* / incap_ses_* / nlbi_*` 必须由同 session 首页带出，不能手工拼或跨轮复用
- `reese84` 设置时 domain 必须与站点匹配（`.canadiannorth.com`），否则后续 GraphQL 不带 cookie
- challenge 返回 200 + token 不等于放行：`bookingAirSearch.originalResponse` 返回真实航班
  数据才算 serverAccepted
- 业务层还存在 `execution` 这样的会话级头，只补 challenge 不补业务会话链会停在
  challenge-state 而非真正放行

## 验证口径

- 当前轮 src / 脚本 / POST body / token 对应，challenge POST 200 且响应含 token
- `reese84` 写入后，`dcmcInit` 正常返回 `execution` 头
- `bookingAirSearch.originalResponse` 返回航班数据（非空数据、非风控结构）
- 多轮重跑（重新拉首页、新 src、新 POST、新 token）稳定通过
