# Cloudflare 5s / WAF Challenge

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> Cloudflare 5s / WAF Challenge / Challenge Page 链路：_cf_chl_opt、challenge-platform、内部 Turnstile、cf_clearance 与最终业务回打。

## 命中特征

- 初始业务页出现 "Just a moment..."、连接安全检查、人机验证等 challenge HTML
- HTML 内联 `_cf_chl_opt`，字段常见 `cvId`、`cZone`、`cType`、`cRay`、`cH`、`cUPMDTk`、`cFPWv`、`cITimeS`、`cTplC`、`cTplV`、`cTplB`、`fa`、`md`、`mdrd`
- 请求链出现 challenge-platform 的 `/orchestrate/chl_page/v1` 与 `/flow/ov1.../{cRay}/{cH}` 路径
- POST header 出现 `cf-chl`、`cf-chl-ra`；响应或 Cookie 出现 `cf_clearance`
- `_cf_chl_opt.cUPMDTk` 或 URL 中出现 `__cf_chl_tk`
- 页面或子链加载 challenges.cloudflare.com 的 Turnstile 资源；出现 `sitekey`、`chlPageData`、`page_data`、`cData`、`action`
- 业务响应头出现 `cf-mitigated: challenge`，失败时一直回到 challenge 页

仅看到 Cloudflare CDN 响应头不等于命中 5s，必须有 challenge 页、`_cf_chl_opt`、flow/ov1、Turnstile 子链或 `cf_clearance` 类链路证据。

## 常见链路

```text
业务 URL
→ Cloudflare Challenge HTML，内含 _cf_chl_opt
→ GET /cdn-cgi/challenge-platform/h/{branch}/orchestrate/chl_page/v1?ray={cRay}
→ 反混淆/解析当前版本 orchestrate，得到 init payload 动态 key 和压缩字符集
→ POST /cdn-cgi/challenge-platform/h/{branch}/flow/ov1.../{cRay}/{cH}
→ 返回 main VM / challenge runtime
→ 提取内部 Turnstile sitekey、page_data、token 字段名
→ Turnstile token 子链（action 通常取 cType，cData 通常取 cRay）
→ 组装 WAF final payload（Turnstile token、__cf_chl_tk、md、时间、环境 entry）
→ POST 同类 flow 路径 → Set-Cookie: cf_clearance
→ 用同 UA、同代理、同 header/TLS 指纹回打原业务 URL
```

三种成功口径必须分层：

```text
Turnstile token issued = 提取到 0. 或 1. 开头 token
WAF clearance issued   = WAF final 响应 Set-Cookie 出现 cf_clearance
business accepted      = 同轮 clearance + 同 UA/代理/header/TLS 指纹回打原业务 URL 成功
```

## 观察优先级

1. 固定目标上下文：业务 URL、cZone、当前 HTML 的 `_cf_chl_opt` 字段、当前 orchestrate 资源、内部 Turnstile 的 sitekey/page_data 提取位置
2. 当轮动态生成：cRay、cH、`__cf_chl_tk`、flow body、Turnstile token、payload 中的时间/性能/环境 entry、`cf_clearance`
3. 环境面按当前 VM 实际命中的 entry 补：UA/UA-CH 与 headers 一致、navigator 基础、Intl 与语言、DOM/CSSOM、Worker/Blob/postMessage、performance、canvas/WebGL/WebGPU、audio/WebRTC、native toString/descriptor/Error.stack
4. 传输一致性：UA、sec-ch-ua、Accept-Language 与 JS 环境自洽；challenge/Turnstile/业务回打同代理或同出口 IP；`cf_clearance` 对 UA、IP、TLS/HTTP 指纹和 Cookie scope 敏感
5. `__cf_chl_tk` 往往来自 `cUPMDTk`，不要当成独立固定配置
6. `600010` 类返回通常表示 Turnstile/challenge 被标记，不要误判为 token

## 常见坑

- 只拿到 `cf_clearance` 不等于业务通过，必须回打原业务 URL
- 只完成内部 Turnstile token 不等于 WAF 通过，WAF final 仍可能失败
- 动态 key 名、payload key、orchestrate 字符集、flow path 都是版本相关，不要跨版本写死
- WAF final 中某些数组不能直接照搬内部 Turnstile payload（如 cookie 名数组应为空数组）
- `hardwareConcurrency`、DOM rect、WebGL/Audio hash、performance timing、click trace 都需要当前证据校准
- 为匹配 trace 卡顿强行拉长 timer、performance.now 或事件间隔；trace 时间通常只能作为阶段顺序证据

## 验证口径

- `cf_clearance` 只是 challenge 阶段成功；最终结论看原业务 URL 或原业务接口返回真实业务内容，不再返回 challenge/block
- 同轮 clearance 必须配合同 UA、同代理、同 header/TLS 指纹使用，不能只复制 Cookie 到另一个客户端就断言可用
