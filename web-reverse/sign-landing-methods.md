# 平台签名落地方法：纯算、黑盒与 RPC 分流

> 来源: `workspace/cv-cat`（GitHub cv-cat 公开仓 2026-08-30 只读对照）
> 原始发布时间: 2026-08-30
> 归档日期: 2026-08-30
> 分类: web-reverse
>
> 从公开平台 SDK 对照中提炼签名落地选型：能钩到的宿主原语就纯算，搬不动的 VM 用隔离执行出参，App Native 签名优先实例 RPC。不收录字母表、盐、keystream 或可执行签名器。

公开采集 SDK 的价值不在于「复制就能过」，而在于把一条业务请求拆成可独立验收的产品面，并给每种面选定落地方式。对照窗口是 2026-08；常数、档位和 SDK 版本会过期，方法不过期。

本地镜像只作只读对照，禁止把上游 Cookie / `.env` 写进 knowledge base 或 evidence。目标 case 仍从 `web_case.py next` 进入，browser fact 走 RuyiTrace，本地出参默认 RuyiDOM 黑盒到 cookie / XHR / fetch 边界。

## 落地四分法

对齐 Web 逆向落地合同：纯算、补环境、V8 RPC、自动化。公开 SDK 里实际出现的是下面四种实现形态，不要把它们混成一个 `execjs` 标签。

| 形态 | 何时用 | 对照样本 | 完成门 |
|------|--------|----------|--------|
| 纯算 | 明文格式、哈希/对称加密、canonical 规则已在请求边界闭合 | 抖音 `a_bogus` / `x-secsdk-web-signature`；快手 `__NS_sig3`；小红书 mns / `b1` / `x-rap-param` | 与当前 browser fact 逐字段对齐，业务 JSON 读回 |
| 隔离黑盒（Node `vm` / 最小宿主） | 认定 VM 后，出参仍在 cookie / header / query 边界 | 抖音 acrawler `__ac_signature`；快手 kwf/kws；小红书 `websectiga`、Creator `_dsf` | 出参 provenance 记为 runtime，不得标 `purecalc` |
| execjs 喂整包 | 只适合看参数名和请求边界 | 多数 `*Apis` 的 `static/*.js`；京东旧 `ParamsSign` 壳 | 不能当现行协议，更不能当纯算完成 |
| 设备 RPC | App Native / SG 签名实例可 Hook | 闲鱼 `InnerSignImpl.getUnifiedSign` | 设备、登录态、`ttid`/`app_ver` 同源；版本变则重适配 |

默认路径：能钩到 `MD5` / `SM3` / `encodeURIComponent` 等宿主原语，就不要解释 opcode。字节码 VM 先预言机对拍，再决定是否移植。App 安全库不要一上来还原 SO。

## 产品切开，失败不要单归因

一条「平台请求」通常叠了多条独立链。一个组件正确不能解释整站失败。

```text
业务参数组装
→ 查询签名（a_bogus / x-s / __NS_sig3 / h5st / MTOP sign）
→ 会话 token（msToken / _m_h5_tk / web_session）
→ 请求完整性（TicketGuard / x-secsdk-web-signature）
→ 设备或行为材料（dtrait / b1 / kwfv1 / tfstk）
→ 传输层（TLS impersonate、头序、HTTP/2 Cookie 拆 pair）
→ 业务读回（serverAccepted ≠ HTTP 200）
```

抖音对照把 `a_bogus`、`X-Bogus`、mssdk `msToken`、TicketGuard、`x-tt-session-dtrait`、acrawler Cookie、secsdk URL 签名分成不同模块。`a_bogus` 不是 `X-Bogus`。产品文档见 [抖音 a_bogus](./products/douyin-a-bogus.md) 与 [Ticket Guard](./products/douyin-ticket-guard.md)。

快手对照同样分层：发布链 `__NS_sig3`、www/live `__NS_hxfalcon`、webweapon `kwfv1`/`kwscode`、gdfp 遥测、滑块 captcha。见 [快手 NS 签名](./products/kuaishou-ns-sig.md)。

## 可复用方法

### 1. VMP 先钩宿主原语

认定目标是 stack VM 之后，优先在 `CryptoJS.MD5`、`encodeURIComponent`、原生 `SubtleCrypto` 入口读明文，而不是拆 opcode。抖音 `x-secsdk-web-signature` 的对照路径是：CDP hook `XHR.open` 找到 `webSignUrl` → 静态放弃 VM → 在 MD5 入口得到 `{uifid}_{timestamp}_{CONST}_{canonical_query}` → Python 只复刻 query 规范化。

探针：换 Cookie、清空 storage，看盐是否变化。不变则是 VM 常量池，不是会话材料。

### 2. 签完的 query 就是要发的 query

规范化规则（参数顺序、`+` 与 `%XX` 的 decode/re-encode、裸 key 补 `=`、timestamp 追加位置）属于 RequestShape。签名算在规范化后的串上，服务端也按收到的 query 校验。把 dict 再交给 HTTP 客户端重编码，签名作废。

### 3. Cookie 与材料要记 provenance

| 出处 | 例子 | 纪律 |
|------|------|------|
| 本地可造 | 小红书 `a1` / `webId` / `loadts`；快手 `startupRandom` | 允许纯算，但必须有状态机（seq / count），禁止每次随机 |
| 服务端下发 | 小红书 `web_session`、`_dsl`（ds 接口 `getdss()`）；mssdk Set-Cookie | 不能本地伪造；缓存 TTL 与浏览器一致 |
| 运行时程序 | Creator `_dsf`、`websectiga`、acrawler `__ac_signature`、`tfstk` | provenance 记 runtime；失败不得降级成随机串 |
| 设备绑定 | 闲鱼 App `utdid` / `umid` / `uid` / `sid` | 必须与签名实例同一设备、同一版本 |

随机 `msToken`、假 `webid`、长度对的匿名 Cookie，只能标 `unproven_synthetic`，不能当 `serverAccepted`。

### 4. 子域 / 端别常量表

同一算法常嵌入 `aid` / `page_id` / `appId` / mns 档位。签名函数必须吃 host 或端别，不能用主站常数签登录域。

- 抖音 `www` / `live` / `creator` / `login` 的 `(aid, page_id)` 不同；用错子域会被强校验判人机。
- 小红书 PC `appId=xhs-pc-web` 有 mns0301；Creator `appId=ugc` 没有 0301，0101 还要 DS 程序。
- 阿里 MTOP H5：淘宝 `appKey` 与闲鱼 Web `appKey` 不是同一个；闲鱼 Web `sign` 与 App `x-sign` 网关也不同。见 [阿里 MTOP H5](./products/alibaba-mtop-h5.md) 与 [InnerSignImpl RPC](../mobile-app-reverse/mtop-innersign-rpc.md)。

### 5. 传输层单独验收

JS 对了但 TLS / 头序不对仍会挂。对照仓普遍用 `curl_cffi` impersonate，且关掉默认头，按抓包 tuple 锁 Chrome Client Hints 与 `sec-fetch-*` 顺序。CDP 必须看 ExtraInfo：JS 设置的头不等于网络层后加的头。

HTTP 200 空 body、挑战页、passport decision、bdturing 类响应，要翻译成失败原因，不要 `resp.json()` 当成功。

### 6. 能反编译就纯算，搬不动就预言机

快手 `__NS_sig3` 的 `$encode` 已从 vm.js + LZW AST 反编译，输入只有 query+body、不含 path/method，适合纯算。kwf/kws 是 Brook 字节码（数十 KB × 多变体），对照选择 Node 跑官方脚本，并修 `navigator` 可写 canary 与 `div.offsetHeight` 布局 canary。成本判断写进账本，不要假装已经纯算。

### 7. App Native 签名优先实例 RPC

MTOP `InnerSignImpl.getUnifiedSign` 是标准路径：spawn → 枚举 ClassLoader → hook 一次抓住实例 → 立刻摘 hook → RPC 出 `x-sign` / `x-sgext` / `x-mini-wua`。版本、`ttid`、`app_ver` 一变就要重适配。这不是纯算完成，也不是「已经还原 SG」。

## 反面教材

- 把字母表、盐、mns keystream、RAP AES key、secsdk 常量当长期 SDK vendor。
- 巨型 DOM stub + 冻 canvas data URL 代替真实 Gecko / RuyiDOM。
- PyExecJS 喂整包 `webmssdk` / `h5st` ParamsSign，声称纯算完成。
- 用 2026-04 的小红书 `execjs` 快照当现行 `x-s`（旧 XsCommon 没有 `x12=dsl`）。
- 京东公开仓声称 h5st 4.2、无 `cactus.request_algo`：现行搜索链是 5.3，见 [京东 h5st](./products/jd-h5st.md)。
- 作者机器指纹（分辨率、核数、显卡、canvas CRC）贴到另一份 Cookie 会话。
- 同集团协议直接抄 appKey / 网关 / 票据（淘宝仓混闲鱼 URL 是脏代码信号）。

## 与主线工作流

1. 特征命中 [产品索引](./products.md)，账本写产品名与文档。
2. 每个参数族声明 primary 落地方式；VM 形态继续喂外部宿主，不得立刻 `triage-only`。
3. 纯算只覆盖已闭合的边界格式；隔离执行的 Cookie 出参单独记 provenance。
4. `test.py` 业务读回才是 `serverAccepted`。RuyiDOM / Node vm 出参只是 `localReproduced`。

对照仓刷新后只更新本页的「窗口日期」与产品文档的命中特征，不把新盐写进知识库。
