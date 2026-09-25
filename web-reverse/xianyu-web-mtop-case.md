# 闲鱼 Web 案例：H5 sign、空 sign 换票、tfstk

> 来源: `workspace/cv-cat`（XianYuApis，HEAD 日期 2026-08-18，只读对照）
> 原始发布时间: 2026-08-18
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> 闲鱼 Web 和淘宝 H5 共用 `token&t&appKey&data` 的 MD5 形状，但 appKey、域名、HTTP 方法和 `_m_h5_tk` 的来源都不同。Web `sign` 不能填进 App 的 `x-sign`。

淘宝分链见 [淘宝 H5 案例](./taobao-h5-mtop-lwp-case.md)。App RPC 见 [闲鱼 Android 签名案例](./xianyu-android-sign-rpc-case.md)。产品命中见 [阿里 MTOP H5](./products/alibaba-mtop-h5.md)。

## 和淘宝的同构与分叉

| 点 | 闲鱼 Web | 淘宝 H5 对照仓 |
|----|----------|----------------|
| 计算 | execjs 调 `generate_sign` | 同形 |
| 明文 | `token&t&appKey&data` 的 MD5 hex | 同形 |
| H5 appKey | `34839810` | `12574478` |
| 网关 | `h5api.m.goofish.com` | `h5api.m.taobao.com` |
| 形态 | POST `originaljson`，body `data=` | get_token 是 GET JSONP |
| accountSite | `xianyu` | token 路径没有这个字段 |
| `_m_h5_tk` | 仓内用空 sign POST 换票 | 只接受外部 Cookie |
| 设备 Cookie | `tfstk` 由 Node `vm` 跑页面脚本 | 本仓没有对等模块 |
| WS | `wss-goofish.dingtalk.com`，uid `@goofish` | `wss-cntaobao`，uid `@cntaobao` |

## 案例：空 sign 换 `_m_h5_tk`

`utils/build_cookies.py` 的引导顺序：

1. GET `log.mmstat.com/eg.js`，取出 `cna`，写到 `.goofish.com`。
2. 对两个 mtop API POST `h5api.m.goofish.com/h5/{api}/1.0/`。query 含 `jsv=2.7.2`、`appKey=34839810`、`t`、空的 `sign`、`sessionOption=AutoLoginOnly`。body 是 `data=%7B%7D`。
3. 源码注释：第一次拿 `_m_h5_tk`，第二次拿 `cookie2`。本知识库没有重放，Set-Cookie 名以源码注释和返回 dict 的键为准。
4. `tfstk` 用 `subprocess` 调 `node gen_tfstk.js`。脚本建 `vm` 上下文，加载页面 `et_f.js`。失败就不要造一个随机 `tfstk`。

返回键包括 `cna`、`_m_h5_tk`、`_m_h5_tk_enc`、`cookie2`、`tfstk`。`tfstk` 的 provenance 是 runtime，不是本地可造。

## 案例：业务 get_token

`XianyuApis.get_token`：

```text
token = cookies["_m_h5_tk"].split("_")[0]
t = now_ms()
data = json(deviceId, business_app_key, ...)
sign = js.generate_sign(t, token, data)
POST h5api.m.goofish.com/h5/mtop.taobao.idlemessage.pc.login.token/1.0/
     params: jsv, appKey=34839810, t, sign, v=1.0,
             type=originaljson, accountSite=xianyu, api
     body: data=<urlencoded json>
```

body 里的业务 appKey 和 query 里的 H5 appKey `34839810` 不是同一个字段。扫码登录后，源码会再打 mtop 刷新 `_m_h5_tk`。

实时消息在 `goofish_live.py`，连接闲鱼钉钉 WSS，帧里用 MTOP 返回的 token，不再计算 H5 `sign`。

## 不能和 App x-sign 互换

| 面 | 产出 | 网关 | appKey |
|----|------|------|--------|
| Web | query `sign`，32 位 hex | `h5api.m.goofish.com/h5/` | `34839810` |
| App | `x-sign` / `x-sgext` / `x-mini-wua` | `g-acs.m.goofish.com/gw/` | 客户端默认 `21407387` |

同一份 data JSON 不能把 Web `sign` 填进 `x-sign`。App 路径见 InnerSignImpl RPC。

## 证据边界

`gen_tfstk.js` 和 `et_f.js` 的环境快照不入库。空 sign 换票是这份对照仓的引导步骤，是否仍被服务端接受要以当前抓包为准。本库没有打线上。
