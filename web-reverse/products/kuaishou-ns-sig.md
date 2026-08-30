# 快手 __NS_sig3 / hxfalcon / webweapon

> 来源: `workspace/cv-cat`（KuaiShou-Spider 2026-08-30 只读对照）
> 原始发布时间: 2026-08-30
> 归档日期: 2026-08-30
> 分类: web-reverse
>
> 快手 Web 的签名与换票链：发布 `__NS_sig3`、浏览 `__NS_hxfalcon`、webweapon `kwfv1`/`kwscode`、gdfp 遥测与滑块。分层验收，不把验证码失败归因到业务签名。

## 命中特征

- 站点 `www.kuaishou.com`、`live.kuaishou.com`、`cp.kuaishou.com`、`captcha.zt.kuaishou.com`、`gdfp.gifshow.com`
- Query 出现 `__NS_sig3`（56 hex）、`__NS_hxfalcon`（`HUDR_` / `$HE_` 段）、`caver=2`
- Cookie / header 出现 `kwfv1`、`kwscode`、`kwssectoken`、`kww`
- 脚本名 `kwf-*.js`、`kws-*.js`；栈或注释出现 `$encode`、Brook / weapon、`KsGuard`
- 换票接口路径形态 `/s/w/c`，响应含 `fpUrl`、`signUrl`、`secToken`
- 验证码 `350014 anti check err` 常与 gdfp 遥测未完成有关，不是 sig3 算错的充分证据

产品名在对照实现里按站点隔离：www `kuaishou-vision`、CP `onvideo-cp`、Live `PCLive`、验证码 `verification-captcha`。三站票据不可合并。

## 常见链路

```text
登录 / Cookie
→ webweapon 换票 /s/w/c → {fpUrl, signUrl, secToken}
→ 跑 kwf 得 kwfv1（写 localStorage + cookie）；kww header 在页面初始化时冻结
→ 跑 kws 得 kwscode（TTL 约 6 分钟），不得用过期 signUrl 的离线副本
→ www 白名单 /rest/v/* ：query 附加 __NS_hxfalcon + caver=2
→ CP /rest/cp、rest/v2/creator、/rest/kd ：query 附加 __NS_sig3
→ Live：签名算 realUrl，实际请求发 /live_api/* 映射
→ 滑块前 gdfp 遥测 /s/u/v /n/a/b /p/z/s 必须先上报
```

落地分流（对照结论，不是要求照搬实现）：

| 参数 | 形态 | 说明 |
|------|------|------|
| `__NS_sig3` | 纯算候选 | 输入是 query+body 的 JS 值语义（UTF-16 排序、`encodeURI`），**不含 path/method**。引擎是 vm.js + 压缩 AST，不是字节码 VMP |
| `__NS_hxfalcon` | 纯算候选 | sig4；设备 blob 与 45 字节容器分段；Live 必须按 realUrl 签 |
| `kwfv1` / `kwscode` | 隔离黑盒 | Brook 字节码，体积大、变体多；对照用 Node 跑官方脚本。有 `navigator` 可写 canary 与 `div.offsetHeight` 布局 canary |
| gdfp 换票 | 协议 | `/s/w/c` 配置解密后得到脚本 URL，不是业务签名 |
| 滑块 | 独立链 | 缺口图 + 轨迹；与 falcon 不是同一密钥 |

`kww` header 是初始化快照。后续 Cookie 轮换 **不得覆盖** 该头，否则与浏览器分叉。

## 观察优先级

1. 先画白名单：这条 URL 要 sig3、hxfalcon、两者都要，还是只要 weapon Cookie。
2. 核对 `kww` 与 `kwfv1` 是否被后续 Set-Cookie 冲掉。
3. kws 是否绑定**当次** `signUrl`；仓库里的历史 `kws-N-*.js` 只是离线夹具。
4. kwf 代际（对照见过 174 与 218 两种长度）选错会立刻风控。
5. Live 是否用 realUrl 签名、用 `/live_api/*` 发送。
6. 验证码失败时先查 gdfp 遥测 identity UUID 是否贯通，再查 sig。
7. JSON body 键序必须与 `JSON.stringify` 一致；数字格式走 JS 值语义，不是 Python `str`。

## 常见坑

- 把 path/method 算进 sig3 输入
- 用离线 kws 变体签线上 `signUrl`
- 合并 www / CP / Live 的 Cookie 与 `did`
- 指纹几何、GPU、脚本数量与 `did` 不是同一台浏览器会话
- 把 captcha 或 400 推荐流全部归因到「签名算法过时」
- 反编译 VM 源不在对照树里时，仍声称「已完整还原引擎」

## 验证口径

- 目标 `/rest/*` 返回业务 JSON；记录站点、参数名、`caver`、weapon TTL、是否走 Live 映射
- 滑块链与业务签名链分开留证
- Brook VM 路径的出参 provenance 记 runtime，不得标纯算完成

落地选型见 [平台签名落地方法](../sign-landing-methods.md)。
