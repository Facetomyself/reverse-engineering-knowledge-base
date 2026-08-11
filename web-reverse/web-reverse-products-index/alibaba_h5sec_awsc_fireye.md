# 阿里 H5Sec / AWSC / Fireye（140/231/234 / x5sec）

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 阿里系业务请求前置风控 headers/metas/cookie 与 x5sec 处罚链路，不等同于验证码题面校验或站点业务加密。

## 命中特征

- 页面加载 alsc-h5-sec `securityHeader.min.js`、AWSC awsc.js、fireyejs（1.231.x / 1.234.x）、uab collina.js、et_f.js、WebUMID um.js、baxiaCommon.js
- 运行链出现 `securityHeader.initSecurity` / `getSecurityHeaders`、`AWSC.configFYEx`、`AWSC.configFY`、`AWSCInner.register`
- Header 出现 `bx-ua`（`231!` 或 `234!` 前缀）、`bx-umidtoken`；body/metas 出现 `AsuraId`、`fire_ua`（`140#` 前缀）、`fire_umid`
- Cookie 出现 `tfstk`、`cna`；storage 出现 `tfstk__`
- 响应头/体出现 `bxpunish: 1`、`x5secdata`、punish 类标记；业务请求返回 `FAIL_SYS_USER_VALIDATE`、处罚 URL 或挤爆类错误

先拆清楚当前请求依赖哪一类阿里组件，不要只因为出现 `AWSC` 就判成滑块验证码：

```text
验证码 v2  = captcha-pro-open / device.captcha-open / requestInfo / StaticPath / FeiLin / Result / verify
noCaptcha  = nc.js 滑块或无感 challenge
H5Sec/AWSC/Fireye 140/231/234 = securityHeader / bx-ua=231!/234! / AsuraId / fire_ua / bx-umidtoken / fire_umid
Baxia/x5sec punish = baxiaCommon / x5secdata / bxpunish / punish 标记
1036/WAF    = refer__1036 / ssxmod_itna / ssxmod_itna2 / acw_tc / WAF HTML
业务加密    = 站点自己的 req/res 加解密，不代表风控已通过
```

## 常见链路

```text
业务页面
→ 加载 securityHeader / AWSC / fireyejs / uab / et_f / WebUMID / Baxia
→ initSecurity 初始化 dependHeaders → AWSC.configFYEx 初始化 231 → AWSC.configFY 初始化 140
→ 浏览器环境和行为日志进入采集器 → WebUMID 生成 token → et_f 写 tfstk
→ 组装 metas（AsuraId / fire_ua / fire_umid）→ getSecurityHeaders 生成 bx-ua / bx-umidtoken
→ 包装 XHR/fetch 注入 headers → 业务请求发出
→ 任一环节不稳定时：业务接口返回 FAIL_SYS_USER_VALIDATE → 响应头 bxpunish 或 Set-Cookie x5secdata
```

## 观察优先级

1. 定位 `getSecurityHeaders` / `configFY` 的调用序号与消费边界，出现两次调用时按真实顺序保存中间状态
2. 确认 `cna`、`tfstk` Cookie 与 storage 在请求前后的读写变化
3. 对比 token 长度量级与浏览器证据：`bx-ua` / `AsuraId` / `fire_ua` 存在但明显偏短时，优先查行为采集窗口、performance entries、media/WebGL 分支和初始化等待
4. 同一套参数用标准 HTTP 客户端仍返回 punish 时，检查 TLS/HTTP 传输指纹
5. 确认是否真的触发了验证码题面；没有题面时不要继续找滑块

## 常见坑

- 把 `231!` / `140#` 链路误认为阿里云 v2 滑块验证码
- 复用历史 token、旧 `tfstk` / `cna` / `x5secdata`，回放常被判为 punish
- 只生成 `bx-ua` 漏掉 `AsuraId/fire_ua/fire_umid`，或只补 metas 漏掉 Cookie
- 只看 token 前缀正确，不看长度级别、body 长度和服务端响应
- 只改 HTTP Header UA，漏掉 JS 环境里的 `navigator.userAgent / appVersion / language / screen`
- 用标准 HTTP 客户端发送忽略 TLS 指纹；把"用户名密码错误"误判为失败（随机账号场景下这是通过风控后的正常业务响应）

## 验证口径

- headers、metas、cookie 在同一轮运行/同一会话内动态生成
- 最终业务接口不再返回 `bxpunish` / `x5secdata` / punish URL，返回正常业务 JSON、正常错误码或目标数据
- 传输层与浏览器指纹相容；`140#` 等前缀属于案例观察形态，个别链路字段名或前缀可能不同，以当前目标实测为准
