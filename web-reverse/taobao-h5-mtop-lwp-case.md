# 淘宝 H5 案例：MTOP sign 与钉钉 LWP 分链

> 来源: `workspace/cv-cat`（TaoBaoApis，HEAD 日期 2026-08-18，只读对照）
> 原始发布时间: 2026-08-18
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> 淘宝 H5 的 `sign` 是 Cookie 半段、时间戳、appKey 和 data 的 MD5。实时私信是另一条钉钉 LWP WebSocket，不再带这个 sign。仓里残留的闲鱼 URL 不能当成淘宝网关。

产品命中见 [阿里 MTOP H5](./products/alibaba-mtop-h5.md)。闲鱼 Web 的分叉见 [闲鱼 Web 案例](./xianyu-web-mtop-case.md)。

## 落地形态

Python 用 execjs 编译 `static/taobao_js_20260407.js`，调用导出的 `generate_sign(t, token, data)`。JS 里 appKey 字面量是 `12574478`，拼接 `token + "&" + t + "&" + appKey + "&" + data`，再 `crypto.createHash('md5')`。这是整包 JS 出参，不是把算法重写成可维护的纯 Python 模块。同文件的 `generate_mid` / `generate_uuid` 给 IM 设备字段用，不产生 MTOP query sign。

## 案例：拿 IM token

`TaobaoApis.get_token`：

1. URL 是 `https://h5api.m.taobao.com/h5/mtop.taobao.login.token.get.h5/2.0/`。
2. query 含 `jsv=2.7.0`、`appKey=12574478`、毫秒 `t`、`api`、`v=2.0`、`type=jsonp`、`callback=mtopjsonp3`。
3. 源码先写了一个样例 sign，再被 `generate_sign` 覆盖。读代码时以覆盖后的值为准。
4. `token` 取 `session.cookies['_m_h5_tk']` 按下划线切开的第一段。本仓没有空 sign 换票实现，首包 Cookie 由调用方从浏览器复制。
5. `data` 是 JSON 字符串，里面的 `imAppKey` 和 `domain=cntaobao` 是 IM 业务字段，不是 H5 appKey `12574478`。
6. GET 之后用正则剥掉 `mtopjsonp3(...)` 再解析 JSON。

```text
cookie = browser_cookie()                  # must already contain _m_h5_tk
token = cookie["_m_h5_tk"].split("_")[0]
t = now_ms()
data = json(domain="cntaobao", deviceId, locale, imAppKey)
sign = js.generate_sign(t, token, data)    # md5(token&t&12574478&data)
GET h5api.m.taobao.com/.../token.get.h5/2.0/?...&sign=sign
accessToken = unwrap_jsonp(response)
```

## 案例：私信是 LWP，不是再签一次 MTOP

`taobao_live.py` 连接 `wss://wss-cntaobao.dingtalk.com/`，Origin 为 `https://www.cntaobao.com`。注册帧 `/reg` 的头里：

- `app-key` 等于 get_token body 里的 IM app-key 字面量
- `token` 等于上一步的 `accessToken`
- 没有 query `sign`，也没有 `_m_h5_tk`

后续拉历史、建会话、发消息、ack 都是 LWP 路径（`/r/MessageManager/...`、`/r/MessageSend/...`、`/r/SyncStatus/ackDiff`）。uid 后缀是 `@cntaobao`。

```text
ws = connect(wss-cntaobao)
send LWP /reg { app-key: IM_APP_KEY, token: accessToken }
on /s/vulcan: pull history
send LWP /r/MessageSend/...
```

## 脏边界

`taobao_apis.py` 里有指向 `h5api.m.goofish.com` 和 `passport.goofish.com` 的 URL 常量，本文件没有对应调用。`taobao_utils.py` 的 `__main__` 样例同时出现 `@goofish` 和 `@cntaobao`。这是拷贝残留。淘宝 token 接口的 host 以 `get_token` 里写死的 `h5api.m.taobao.com` 为准。

## 证据边界

appKey `12574478` 是端别标识，和闲鱼 Web `34839810`、闲鱼 App `21407387` 不是同一个。本库没有重放线上请求。IM app-key 字面量留在源码里，知识库不把它当成可跨站复用的密钥。
