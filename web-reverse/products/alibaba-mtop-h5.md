# 阿里 MTOP H5 sign

> 来源: `workspace/cv-cat`（TaoBaoApis / XianYuApis 2026-08 只读对照）
> 原始发布时间: 2026-08-18
> 归档日期: 2026-08-30
> 分类: web-reverse
>
> 淘宝 / 闲鱼 Web 的 H5 MTOP 查询签名：`_m_h5_tk`、`t`、`appKey`、`data` 拼串后 MD5。与 App `x-sign`、H5Sec/AWSC/Fireye、`tfstk` 不是同一条链。

## 命中特征

- 网关形态 `h5api.m.taobao.com/h5/<api>/<ver>/` 或 `h5api.m.goofish.com/h5/<api>/<ver>/`
- Query 出现 `jsv`、`appKey`、`t`、`sign`、`data`；Cookie 出现 `_m_h5_tk`、`_m_h5_tk_enc`
- 闲鱼 Web 冷启动还出现 `cna`（`log.mmstat.com/eg.js`）与 `tfstk`（`et_f.js`）
- IM 走钉钉 LWP WebSocket：`wss://wss-cntaobao.dingtalk.com/` 或 `wss://wss-goofish.dingtalk.com/`，帧 `/reg`、`/!` 心跳、`/r/MessageSend/...`
- 登录失效时 `_m_h5_tk` 刷新，旧 `sign` 立即失败

这不是 [阿里 H5Sec / AWSC / Fireye](./alibaba-h5sec-awsc-fireye.md) 的 `bx-ua` 链，也不是 [InnerSignImpl RPC](../../mobile-app-reverse/mtop-innersign-rpc.md) 的 App 网关。出现 `FAIL_SYS_USER_VALIDATE` / `x5secdata` 时先走 H5Sec 文档。

## 常见链路

```text
Cookie 中的 _m_h5_tk（过期则空 data 打一次 mtop 种票）
→ t = 当前毫秒时间戳
→ data = 与 POST body 完全一致的 JSON 字符串
→ sign = MD5( tk前半 + "&" + t + "&" + appKey + "&" + data )
→ 带 jsv / appKey / t / sign / data 发 H5 网关

IM：
→ HTTP mtop 换 accessToken
→ WS /reg 注册
→ /! 心跳；业务发送走 LWP 方法名
```

`appKey` 按站点绑定，不能抄错：

| 站点 | Web 网关 | 对照窗口里的 query `appKey` |
|------|----------|------------------------------|
| 淘宝 H5 | `h5api.m.taobao.com` | `12574478` |
| 闲鱼 Web | `h5api.m.goofish.com` | `34839810` |
| 闲鱼 App | `g-acs.m.goofish.com/gw/` | 另一套，走 `x-sign` |

闲鱼 Web IM 的 body 内 `appKey` 还可能与 query `appKey` 不同，按当前抓包确认，不要把两个槽位当成同一个常量。

`tfstk` 来自 `et_f.js` 一类安全 SDK，对照用 Node 补环境黑盒出参（Proxy 记访问面、snapshot 回填、避免 VMP `setTimeout` 竞态）。它不是 MTOP `sign` 的输入公式的一部分，但缺了会在风控面失败。冷启动顺序常见为：`cna` → 空 sign 种 `_m_h5_tk` → 再出 `tfstk`。

## 观察优先级

1. 先读网关 host 与 `appKey`，确认是淘宝、闲鱼 Web 还是 App。
2. `data` 字节是否与 POST body 一致；键序、空格、Unicode 转义差一个字符签名全错。
3. `_m_h5_tk` 是否与当次 `sign` 同轮；扫码登录后必须再打一发 mtop，因为 tk 会变。
4. 有 `bx-ua` / `tfstk` / `x5secdata` 时，把 H5Sec 链与 MTOP sign 分开验收。
5. IM 失败时区分：HTTP token 没换到、WS `/reg` 失败、还是消息体 MessagePack 解码问题。

## 常见坑

- 用淘宝 `appKey` 签闲鱼，或把 Web `sign` 当 App `x-sign`
- 对照仓之间互相复制 URL（淘宝实现里残留 goofish 地址是脏代码信号）
- 把 `decrypt()` 从业务 JS 抽出的 MessagePack 解码器当成加签算法
- 忽略 `jsv` / UA 与当前页面 bundle 的版本差
- 把 `tfstk` 补环境失败写成「MTOP MD5 已失效」

## 验证口径

- H5 接口返回业务 JSON，而不是 `FAIL_SYS_*`、处罚页或空 token
- 记录 host、`appKey`、`jsv`、tk 刷新次数、是否同轮带 `tfstk`
- App 接口必须另走 InnerSignImpl，不能用本页公式

落地选型见 [平台签名落地方法](../sign-landing-methods.md)。
