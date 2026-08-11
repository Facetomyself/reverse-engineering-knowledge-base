# DataDome

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> DataDome 保护链路：无感 interstitial、captcha iframe、滑块/audio challenge、datadome Cookie 更新与最终业务放行。

## 命中特征

- Cookie 出现 `datadome`；响应头出现 `x-datadome`、`x-datadome-cid`、`x-dd-b`
- 保护页 HTML 出现 `var dd={...}` 或 `var ddm={...}`；响应体出现 "You have been blocked" / "Please enable JS"
- 请求链出现 `ct.captcha-delivery.com/c.js`、`/i.js`、`geo.captcha-delivery.com/interstitial/`、`/captcha/`、`/captcha/check`
- 题面资源出现图片/audio challenge 与静态像素资源；页面通过后加载 `js.datadome.co/tags.js`
- interstitial 请求体/query 出现 `payload`、`plv3`、`ps`
- captcha 校验请求出现 `ddCaptchaChallenge`、`ddCaptchaEncodedPayload`、`ddCaptchaResponse`、`ddCaptchaEnv`、`ddCaptchaAudioChallenge`、`plv3`
- interstitial 响应出现 `view:"redirect"`、`view:"captcha"`、`ir` 原因码；check 成功返回 `{"cookie":"datadome=..."}`

先分链路：当前轮是无感 interstitial 还是 captcha/slider fallback。live 已返回 `view:"captcha"` 时转 captcha fallback 链，不能继续盲补 interstitial。

## 常见链路

interstitial 无感链：

```text
入口 403 / challenge 上下文 → var dd → GET i.js → GET /interstitial/?
→ 目标 JS 生成 payload / plv3 / ps → POST /interstitial/
→ 成功返回 view:"redirect" + datadome cookie → 带 cookie 回到原页面验证
```

captcha 滑块链：

```text
入口 403 → var dd(rt:"c") → GET c.js → GET /captcha/?initialCid=...&hash=...&cid=...&referer=...
→ iframe HTML 内生成 var ddm → 滑块/audio 行为完成 → window.captchaCallback()
→ GET /captcha/check?... → 返回 datadome cookie → 带 cookie 回到原页面验证
```

## 观察优先级

1. 区分三个 cid：首页 403 里的 `dd.cookie`、captcha iframe 下发的 `ddm.cid`、最终通过后的 `datadome` Cookie，不要混成一个字段
2. 动态字段（`ddCaptchaEncodedPayload`、`ddCaptchaResponse`、`plv3`）是当前轮 JS 产物，不能从历史 trace 硬编码；下发字段（icid、hash、s、dm、referer、parent_url、challenge 字段）从 captcha iframe HTML 或前置响应取
3. 行为链：slider 起点/终点、轨迹、耗时、`document.hasFocus()`、isTrusted 形态；只识别滑块 offset 不等于通过，须把答案、轨迹、耗时与环境证明交给目标 JS 生成校验字段
4. Header 边界：document navigation 的 `Upgrade-Insecure-Requests`、`Sec-Fetch-User` 等头不能带到 XHR；`Referer` 必须是完整 captcha iframe URL
5. 请求在 JS 执行前出现 HTTP/2 reset、TLS 指纹不匹配、连接层 400 或代理注入 Header 时，修复位置在请求传输层（TLS/ALPN、HTTP 版本、Header 管理、连接复用），不在本地执行层
6. 检查响应 `ir` 原因码判断升级原因

## 常见坑

- 固定 trace 中的 `datadome` Cookie、payload、plv3 到 live 会话
- 把 interstitial 固定样本字节级对齐，误认为 live 必须返回 `view:"redirect"`
- 只看验证码校验接口 200，不验证原页面或业务接口是否放行
- 只解滑块 offset，不生成当前目标 JS 要求的行为证明
- 忽略 Referer 必须为完整 captcha iframe URL；把 document navigation Header 错带到 XHR
- 把 TLS/HTTP/连接复用问题误判为 JS 补环境问题
- 没有当前证据就批量补 canvas、WebGL、audio、font、plugin；把 Google/GTM/GA 背景流量当主因

## 验证口径

- interstitial 返回 `view:"redirect"` 或 captcha/check 返回 `datadome` Cookie 只是保护链中间口径
- 最终成功口径：带返回的 `datadome` Cookie 请求原页面或原业务接口，不再返回 DataDome challenge，返回正常业务内容
