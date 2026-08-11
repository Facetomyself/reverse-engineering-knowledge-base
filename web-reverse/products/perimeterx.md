# PerimeterX / HUMAN Security PX

> 来源: JS终结计划课程方法论（clean-room 重写）
> 原始发布时间: 多篇合集
> 归档日期: 2026-08-11
> 分类: web-reverse
>
> PerimeterX / HUMAN Security PX 链路：_px3、collector、bundle、PX captcha、payload/OB 协议与高信任补环境流程。

## 命中特征

- Cookie、响应体、脚本或日志中出现 `_px3`、`_pxvid`、`pxcts`、`_pxAppId`、`pxvid`
- 响应体或 captcha context 中出现 `jsClientSrc`、`collector`、`uuid`、`vid`、`did`、`hostUrl`、`blockScript`、`altBlockScript`、`firstPartyEnabled`
- 请求链出现 px-cloud.net 的 `/api/v2/collector`、`/assets/js/bundle`、`/ns`、`/d/p`
- collector 或 bundle POST 响应中出现 `do`、`ob`，OB 解码后可见 `_px3/_pxvid/pxcts` 或 server-state 命令形态
- 日志或目标中出现 `collector-notouch`、`bundle-press`、`blocked-page-press`、`xhr-press`

三层结果必须分开记录：

```text
_px3 issuance    = collector 或 bundle 返回 set-cookie 命令
PX acceptance    = 同一 _px3 打回触发 PX 的原始请求后不再返回 PX block
business acceptance = 真实业务链继续推进，而不是只拿到 cookie
```

PX 不暴露公开数值评分。客户侧可验证的信任代理只能是原始失败请求 exact retry 后推进到预期业务状态，不要把 `_px3` 签发称为"高评分"。

## 先判门再解 PX

失败响应先分类：HTML/JSON 含 `_pxAppId`、PX captcha、`jsClientSrc`、collector → PX；出现 `_abck`、`bm_sv`、`ak_bmsc` → Akamai 门（改 PX 字段无效）；结构化 JSON 业务错误码（GraphQL 类 data/errors/code）且无 PX 标记 → 业务层，先对齐请求体、变量、同轮 session/header/cookie；下游结构化风控码 → 非 PX 算法问题。HTTP 200 JSON 不是自动通过，必须判断业务 operation 是否推进到预期步骤（如进入 OTP/下一步状态），仅字段名存在但对象为空或带业务错误码不能判定已进入。

## 常见链路

collector-notouch：

```text
请求受保护入口 → 获取 app id、collector、SDK 脚本、初始 Cookie/storage
→ SDK 生成 EV1/EV2（必要时 EV3 cookie confirmation）
→ POST /api/v2/collector → 服务端经 do/ob 下发 state 或 set-cookie 命令
→ 写入 _px3 / _pxvid / pxcts / server-state
→ 带当前 Cookie exact retry 原始 PX-gated 请求
```

bundle-press / blocked-page-press / xhr-press：

```text
业务请求返回 PX block 或嵌套 captcha context
→ 加载 blockScript / altBlockScript / captcha.js / bundle
→ SDK 创建真实 challenge target/listeners、iframe 或 XHR press 上下文
→ 采集 pointer/mouse、PoW/WASM、large payload、/d/p 或 bundle telemetry
→ 发送 2-4 个 bundle 或 XHR press 请求
→ 服务端签发 _px3 / _pxvid / pxcts 或推进 server-state
→ 必要 post-solve delay 后 exact retry 原始业务动作
```

## 观察优先级

1. 归因 source host，建立 profile 矩阵（app id、captcha/main hash、collector、command map、cookie scope），不跨 host 混用
2. 多批（建议 6+）同 SDK hash 的 cold-visit 样本做字段分类：STATIC / DYNAMIC / CONDITIONAL；state.* 到 EV key 的 value-match；HMAC/MD5 公式逐字段验证命中才写入
3. 跨事件规则：CONSTANT（页面加载时间戳、uuid、platform 跨 EV 不变）/ MONOTONIC（performance、时间戳、counter 递增）/ DICT（counter 子字段合法组合空间）
4. payload 链：serialize → XOR → UTF-8 base64 → padding；OB 解码按 base64 → binary → XOR → 分隔符 split 形态；command 按参数形状识别而非函数名
5. 环境面按模块推进，优先采集真实浏览器种子；no-touch preflight 返回 did 时后续 press/XHR solve 带上
6. 传输与 session：/ns、collector、业务请求尽量同一 Chrome-like TLS 持久 session；UA/sec-ch-ua/ALPN/HTTP2 一致；Cookie 按 source host 与 domain scope 发送；干净住宅 IP 优先，不用单 IP 高频 mint 后判算法失败

## 常见坑

- 把 Akamai、GraphQL 业务错误或下游风控误判为 PX
- 混用不同 host 的 profile、Cookie scope、command map 或模板
- 只看 _px3 签发，不做原始 PX-gated 请求 exact retry
- 用 JSON.stringify 替代 PX serialize；用 Latin-1 替代 UTF-8 base64；解析时把 base64 中的 + 转成空格
- state.no 等数字字段类型不匹配模板；anti-tamper delete 后 append 而非原位替换
- 真抓有 EV3/hid/cookie confirmation beacon 却跳过；没有则不要主动造
- post-solve delay 不足；Cookie scope 错发到另一个 host；IP/TLS/UA/client hints 不自洽
- 长期保留大范围 VM tracer、全局 Proxy、全局 Hook 或 VMP 探针

## 验证口径

- 分层标签：`_px3` issuance N/N（独立运行、每次新 uuid、值不同）、PX acceptance N/N（原始 PX-gated 请求 exact retry 不再 block）、end-to-end business N/N（完整业务链无未解决 PX block，且非 PX 门已正确分类）
- 验收间隔：单 IP 每次运行至少间隔 10-30 秒；高信任目标每个 cookie 尽量换干净 IP
- 4-way trust 矩阵定位签发后仍 block：真浏览器 cookie+真浏览器请求 / 真 cookie+脚本请求 / 本地 cookie+真浏览器请求 / 本地 cookie+脚本请求
- 不保存 live _px3、raw payload、raw ob、账号、代理、OTP、OAuth 一次性值，只保存 hash、命令形状、profile 与验收结论
