# 阿里云验证码 / AWSC / noCaptcha（含 WAF 1036 / x5sec）

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 阿里云验证码 v2 滑块、AWSC/noCaptcha、阿里系 WAF 1036 与 x5sec 处罚页链路的通用识别与验收参考。

## 命中特征

- 验证码请求域为 `captcha-pro-open.aliyuncs.com` 或 `device.captcha-open.aliyuncs.com`
- 首轮初始化响应含 `StaticPath`，后续按 StaticPath 加载 dynamicJS 脚本与 FeiLin 脚本
- 受保护页面出现 `var requestInfo = {...}`；最终验证码响应含 `Result`
- 页面或脚本出现 `AWSC`、`AWSCInner`、`AWSCFY`、`__awscnc_wrapper_id__`、`nc`；加载 et_f.js、fireyejs.js、nc.js
- 请求 `cf.aliyun.com/nocaptcha/initialize.jsonp` 类 noCaptcha 端点
- WAF/处罚页出现 `aliyun_waf_aa`、`aliyun_waf_oo`、`aliyun_waf_00`、`aliyun_waf_bb`、`sufei-punish`
- 业务链出现 `refer__1036`、`ssxmod_itna`、`ssxmod_itna2`、`acw_tc`、`x5secdata`、punish 类标记

这些特征可能并存，先按请求链确认当前目标依赖的是 v2 滑块、noCaptcha、1036/WAF 还是 x5sec 处罚页，不要只按脚本名猜产品。

## 常见链路

v2 滑块：

```text
请求受保护业务入口
→ 页面返回或内嵌 requestInfo
→ 按 requestInfo 生成首轮 init query
→ POST captcha-pro-open → 响应 StaticPath 与初始化状态
→ 加载 dynamicJS/sg → 定位并加载 FeiLin
→ 执行 sg + FeiLin + 交互事件，产出多段 query
→ 提交设备/行为日志（log2）→ 提交 v2 verify → 检查 Result
→ 回到业务请求验证是否放行
```

1036/WAF：

```text
业务参数加密为 req → req 参与 1036 环境计算
→ 产出 ssxmod_itna / ssxmod_itna2 / refer__1036
→ 带 acw_tc、ssxmod cookie 与 refer__1036 请求业务接口
→ 返回 HTML/WAF 页时用新处罚页更新算法材料，重算后重试
→ 解密业务 res 并验证业务数据
```

## 观察优先级

1. `requestInfo` 是链路起点：sceneId、token、traceid、userId、captchaEndpoint 等字段必须来自当前页面返回，不是静态配置
2. `StaticPath`、sg、FeiLin、log2 query、verify query 必须来自同一轮 init 与同一会话；跨轮复用会导致 Result 失败或验证码通过但业务仍回 WAF/处罚页
3. 本地输出行的语义（哪个输出是 log2 body、哪个是 verify body）以当前证据确认，不盲套固定下标
4. UA 一致性：HTTP Header 的 UA、sec-ch-ua、sec-ch-ua-platform，JS 环境 navigator UA/appVersion/userAgentData，与 TLS impersonation 版本对齐
5. 业务加密（站点自己的 req/res 加解密）与验证码/WAF 参数分开，不要把加密结果当验证码通过参数

## 常见坑

- 只看 HTTP 200，不看 `Result` 和业务接口是否真正放行
- 跳过设备/行为日志上报，直接打 verify
- 复用旧 `StaticPath`、旧 sg、旧 FeiLin、旧 requestInfo 或旧 WAF HTML
- Header 的浏览器版本、JS 环境 UA 与 TLS impersonation 不一致
- 把业务 AES `req/res` 当作验证码参数，或把验证码 `Result` 当作业务数据成功
- 只改 Cookie，漏掉与当前 `req` 绑定的 `refer__1036`
- 只模拟最终 verify query，不还原 init、动态脚本和事件行为的产出顺序

## 验证口径

v2 滑块至少同时满足：init 正常返回 StaticPath；sg 与 FeiLin 是当前 init 对应的动态脚本；设备日志已按真实顺序提交；verify 返回 JSON 且 Result 表示通过；回到业务接口后不再返回 WAF/处罚 HTML；业务字段或解密后的数据符合预期。

1036/WAF 至少同时满足：`ssxmod_itna / ssxmod_itna2 / refer__1036` 与当前业务 req 同步生成；`acw_tc`、业务 Cookie、Header、TLS 指纹与当前会话一致；业务接口返回 JSON 而不是 HTML/WAF 页；加密业务响应能正常解密；业务状态码与数据符合目标接口预期。
