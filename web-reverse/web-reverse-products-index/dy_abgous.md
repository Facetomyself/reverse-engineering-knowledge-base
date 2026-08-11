# 抖音 a_bogus

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> 抖音 / ByteDance Web 体系中 a_bogus 补参链路的通用识别、链路与验收参考。

## 命中特征

- 目标参数为 `a_bogus`；目标接口路径常见 `/aweme/v1/`、`/aweme/v2/`、`/webcast/` 等
- 页面或运行链出现 `webmssdk`、`sdk-glue`、`bdms`、`SecureSDK`、`web_protect`
- 初始化链出现 `_SdkGlueInit(...)`、`window.byted_acrawler.init(...)`、`window.bdms.init(...)`
- 目标请求最终被追加 `a_bogus`、`msToken`、`verifyFp`、`fp`
- `URLSearchParams.has/append/set` 能观察到这些参数
- 业务代码里找不到直接返回 `a_bogus` 的函数，但请求发出前 URL 被安全链改写

注意：`a_bogus` 不等同于 `X-Bogus`。存在 frontierSign 到 X-Bogus 的签名能力，不能直接推断它就是当前接口的 `a_bogus` 生成逻辑。

## 常见链路

```text
业务请求入口（组装 item_id / comment_id / cursor / count 等业务参数）
→ 统一请求包装器
→ SecureSDK / web_protect 判断是否需要保护
→ sdk-glue 接管 fetch / XHR
→ bdms 或相关运行时执行补参
→ URLSearchParams.append("a_bogus", value)
→ fetch / XHR 发出最终请求
```

脚本角色拆分：`webmssdk / byted_acrawler` 是安全运行时基础能力（init、状态、token、webid、ttwid、签名上下文）；`sdk-glue` 是请求接管和调度层；`bdms` 是常见补参执行层；`SecureSDK / web_protect` 是保护策略层；业务 client-entry 是业务参数组装层，不应默认认为它直接生成 `a_bogus`。

## 观察优先级

1. 定位 `a_bogus` 最终出现的位置（URL Query / Header / Body / Cookie），以及是谁执行了 append/set
2. 确认追加前是否检查了 `has("a_bogus")` 或 `has("msToken")`
3. 记录 `msToken`、`verifyFp`、`fp` 与 `a_bogus` 的同链关系；同一页面不同请求的 `a_bogus` 是否不同
4. 记录请求前后的 Cookie / Storage / Header / Body 变化
5. 若目标链路涉及 VMP 或高度混淆，只在请求边界观察：最终值来源、参与最终值的 query 串、是否多阶段补参、哈希输入输出与编码表、随机数与时间戳是否可复放
6. 本地异常与浏览器同触发步骤对照：浏览器也有同样异常则视为目标逻辑正常行为，浏览器没有才按缺环境排查

## 常见坑

- 把 `a_bogus` 和 `X-Bogus` 混为一谈
- 只搜业务入口，忽略请求出口包装层
- 忽略 `msToken / verifyFp / fp` 与 `a_bogus` 的同链关系
- 写死一次请求里的 `a_bogus`
- 用旧项目的 UA、宽高、语言、webid、ttwid、uifid、msToken 直接套新目标
- 用浏览器跑出来的最终参数替代本地实现；用 VMP 探针或改写后执行结果当作值基准
- 只验证参数能生成，不验证真实接口返回

## 验证口径

- 最终 URL 参数顺序和编码一致；`msToken / verifyFp / fp` 与当前会话匹配；headers/cookies 与当前会话匹配
- 请求命中真实目标接口，返回正常业务 JSON，而不是风控、空数据、重定向或验证码状态
- 多次请求、翻页请求或不同业务参数下仍能稳定生成
