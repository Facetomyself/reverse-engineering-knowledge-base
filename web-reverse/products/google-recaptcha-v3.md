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

## 请求链（可复用）

```text
GET 业务页
  定位 /recaptcha/api.js?render=<sitekey>
GET recaptcha.net 或 www.google.com /recaptcha/api.js?render=<sitekey>
  从 po.src 抽出当前 release，下载 recaptcha__<lang>.js 与 api2/webworker.js?v=<release>
GET /recaptcha/api2/anchor
  query: ar, k=<sitekey>, co=base64(origin:443), hl, v=<release>,
         size=invisible, anchor-ms, execute-ms, cb=<per-round>
  HTML 含 hidden#recaptcha-token 与 recaptcha.anchor.Main.init(...)
本地执行 grecaptcha.execute(sitekey, {action})
  主 window + anchor iframe + worker 协同生成 reload 请求面
POST /recaptcha/api2/reload?k=<sitekey>
  Content-Type: application/x-protobuffer
  body 为 runtime 编码后的 rreq（不要把 JS 直接发网当默认路线）
响应以 )]}' 前缀开头的 JSON，字段 rresp
业务把 rresp 注入 g-recaptcha-response / recaptchaToken / 站点同义字段
siteverify 或原业务接口检查 success / score / action / hostname
```

`co` 是 `https://<host>:443` 的 Base64，通常无 padding。`cb` 每轮随机。`release`/`v` 必须与当轮 api.js 一致，不能写死旧 pin。

## 参数谱系

| 名称 | 位置 | 分类 | 来源 | 可固定 |
|---|---|---|---|---|
| sitekey（`render` / `k`） | 页、query | static | `api.js?render=` | 页面未换 key 前可缓存 |
| release（`v`） | api.js `releases/<v>/` | server-issued | 当前 api.js | 否 |
| `co` | anchor query | derived | `base64(origin:443)` | 同源可固定 |
| `cb` | anchor query | derived | 每轮随机 | 否 |
| `hl` / `size` | anchor query | static | 站点语言 / `invisible` | 随站点 |
| `action` | `grecaptcha.execute` 第二参，折进 rreq | static | 业务动作名 | 随动作 |
| `recaptcha-token` | anchor HTML | server-issued | 当前轮 anchor | 否；不是最终交付 |
| `rreq` body | POST protobuf | challenge-bound | runtime + worker + token + 宿主采集 | 否 |
| `rresp` | reload JSON | server-issued | 当前 reload | 否；最终 token |

protobuf field number 随 release 变，不要把旧样本数组下标当当前 wire 合同。已能出可验证 rresp 时，body 长度量级差异不是阻塞。

## 风控面

无感通过是多维得分，不能把「IP 好/坏」当成单一归因。

| 维度 | 落在哪 | 误判 |
|---|---|---|
| 环境指纹 | rreq 内宿主采集（UA、DOM、iframe、worker、部分 Canvas/WebGL） | 只补 UA 或只换指纹浏览器 |
| 行为/时序 | v3 默认无滑块；站点仍可能看停留与事件 | 把 trace 卡顿写进 timer |
| 出口与会话 | reload 与后续业务应同出口、同 cookie 域 | 轮换 IP 后复用旧 rresp |
| token 绑定 | sitekey + action + hostname + 短 TTL + 单次 | 历史 rresp、anchor `recaptcha-token`、跨 action 重放 |
| 业务验收 | siteverify 的 success/score/action/hostname，或原站不再返回验证失败 | reload 200 或非空 token 当 serverAccepted |

v3 是评分，不是「没出图就 bypass」。要用会触发低分的出口对照，而不是只看自己这轮没弹挑战。验证链（若降级到 v2 图/音频）与结算链（业务 cookie / 登录放行）分开定性。

高并发采集仍要 per-session sticky。本产品 token 不能跨会话复用。

## Node 补环境落点

本地执行层只跑当前 release 的 runtime，输出 reload 请求面（URL、headers、bodyBase64）。Python/TLS client 负责 GET 当前 anchor、POST reload、解析 rresp。不要让 JS 发 reload 或业务请求。

最小宿主面：主 window、anchor iframe、`Worker.importScripts`、MessagePort/postMessage、XHR/fetch 捕获 reload。禁止进 VM/opcode。看见 worker 继续喂宿主。

Node 20 起不能把 `Proxy` 当 `globalThis.crypto` 等 native getter 的 `this`。若沿用课程 `rtwatch(global)`，Reflect get/set 的 receiver 必须是真正的 global，只读属性 set 失败时陷阱仍要返回 true。

## 2026-09-08 Weverse SIGNIN 实测

来源项目 `workspace/google-recaptcha-v3-node-demo`（课程 googlev3 Node 桥接复用，允许使用课程 JS）。

- 公开登录页仍加载 sitekey `6LdHW1kpAAAAAMQ4itbdu1urGNh9v86jzGdLBMrM`，`action=SIGNIN`
- 当前 release `8x-4t2pegToiW8KmThtO4AQt`；课程 pin `A7KpaEASfhDcK0nXxgQEyyYv` 已失效
- 运行时 sha256 `25068be5bad4bf87c01c5bef4c33825addea39e12d99aa7b55b52288fd0631a6`（844493 字节）
- Node 出 POST `/recaptcha/api2/reload` 请求面；Python HTTP/1.1 实发 200，body 前缀 `)]}'["rresp`
- `--twice`：reload body 8747 / 8831 字节，rresp 长度 2105 / 2126，hash 不同
- Weverse 历史业务字段把 rresp 当作 `otpSessionId`；本轮不登录，`serverAccepted=not-run`
- 证据：`evidence/web/parity/live-reload-20260908/receipt.json`

换站点复用：改 pageUrl、sitekey、action、origin/`co`。不要把本轮 rresp 写进 runner。
