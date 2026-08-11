# Google reCAPTCHA v3 / invisible

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> Google reCAPTCHA v3 / invisible 链路：grecaptcha.execute、anchor、reload、rresp、g-recaptcha-response 与最终业务验证。

## 命中特征

- 页面加载 `/recaptcha/api.js?render=<sitekey>`（www.google.com 或 recaptcha.net）
- 页面调用 `grecaptcha.execute(<sitekey>, {action})` 或 `grecaptcha.enterprise.execute(...)` 变体
- 请求链出现 `/recaptcha/api2/anchor`、`/recaptcha/api2/reload`（及 enterprise 变体）
- reload 响应体以 `)]}'` 前缀开头，数组中出现 `"rresp"`，其值被注入为 `g-recaptcha-response`
- 最终业务/验证接口提交字段名为 `g-recaptcha-response`、`recaptchaToken`、`recaptcha_response` 或同义 token 字段
- 最终验证响应中出现 `success`、`score`、`action`、`challenge_ts`、`hostname`、`error-codes`

隐藏 input `recaptcha-token` 通常是 anchor 页面内部状态或快照 token，不能当作最终 `g-recaptcha-response` 交付。

## 常见链路

```text
业务页面加载 api.js?render=<sitekey>
→ grecaptcha.ready / grecaptcha.execute(sitekey, {action})
→ runtime 加载 anchor 和 release 脚本
→ runtime / worker / iframe 生成 reload 请求体
→ POST /recaptcha/api2/reload?k=<sitekey>
→ 响应返回 rresp
→ 页面把 rresp 注入业务验证接口
→ 业务/verify 口径检查 success / score / action / hostname
```

边界建议：本地执行层负责运行当前 release 的 runtime 并输出 reload 请求面（URL、headers、bodyBase64），请求面验证负责真实 POST reload 与业务验证；不要把 JS 直接发 reload 或业务接口当默认路线。

## 观察优先级

1. 固定目标配置：页面 URL、sitekey、action、release 版本、api.js/anchor/webworker 当前资源
2. 当轮动态生成：rresp、reload body、anchor 内部 token、cb、时间窗口与证明字段
3. 定位 reload 请求边界（XHR open/send、postMessage、MessageChannel、Worker、iframe 通信顺序）
4. MessagePort / Worker / iframe 消息模型：只补推动 reload 边界所需的最小语义；证据不足时不猜消息队列、不同步调用另一端 onmessage
5. 执行模型优先级高于字段缺失：currentScript 附着时机、script append/load 与 iframe load 时机、anchor runtime 不能被跳过或 fallback 短路
6. 硬编码核查：连续运行确认 token、reload body hash、response hash 每轮不同

## 常见坑

- 把历史 rresp、浏览器侧 token、anchor 的 recaptcha-token 当最终交付
- 只看 reload status=200，不验证最终 score/action/hostname
- body 长度与通过样本不完全一致就盲补字段；已拿到可验证 rresp 时长度差异不是阻塞
- 跳过 anchor runtime 或用 fallback token 短路，导致没有真实 reload
- 把 trace 时间戳、长卡顿或密集日志写进本地 timer/等待节奏
- 在混淆/VMP/opcode/handler 内部插装推进；用浏览器自动化跑 token 替代本地实现
- 冷启动时间要求脱离实际（reload 与 verify 网络是主要瓶颈）

## 验证口径

- 本地执行输出 reload 请求面；请求面验证实发 reload 并解析 fresh rresp
- 连续两次运行 token、reload body hash、response hash 不同（非常量回放）
- 最终注入验证接口：success=true、score 达标、action 与目标一致、hostname 与目标站一致
- 目标要求业务放行时回到原业务接口，确认不再返回验证码拦截或风控失败
