# 快手案例：资料接口的 hxfalcon 装配

> 来源: `workspace/cv-cat`（KuaiShou-Spider，HEAD 日期 2026-08-30，只读对照）
> 原始发布时间: 2026-08-30
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> 快手 www 资料接口把 webweapon 会话、冻结的 `kww` 头和 `__NS_hxfalcon` 焊在同一次 GET 上。CP 发布改走 `__NS_sig3`。滑块和签名失败不是同一条链。命中特征见 [快手 NS 签名](./products/kuaishou-ns-sig.md)。本篇写一条真实 API 的装配，不抄 `$encode` 表。

## 案例：GET `/rest/v/profile/get`

`KuaishouAPI.get_profile` 只转给 `_get`。`_get` 的合同：

1. 这条 GET 不允许业务自己再带 query。Chrome 上只有签名器生成的 `__NS_hxfalcon` 和 `caver`。
2. `headers.with_kww(auth)`。`kww` 是页面初始化时冻结的头，不是 Cookie 里的 `kwfv1`。Cookie 轮换之后不能重读并覆盖这个头。
3. `Params.with_hxfalcon(path, method="GET", body=None)`。path 不在白名单且没有 `force` 时不注入。
4. 签名器是进程级单例，计数器逐次自增。每次请求新建签名器会和浏览器页面会话分叉。
5. 注入成功则写 `__NS_hxfalcon` 和 `caver`。`CAVER` 常量是 `"2"`。
6. query 编码保留 `$`。`__NS_hxfalcon` 里有 `$HE_` 段，默认 `requests` 会把它编成 `%24`。

`kww` 缺失时才走 webweapon：`/s/w/c` 换到当次的 `fpUrl` / `signUrl` / `secToken`，再用 Node oracle 跑官方 kwf/kws。离线历史脚本不能签当前 `signUrl`。www、CP、Live 的 Cookie 和产品名不能合并；www 的产品名是 `kuaishou-vision`。

```text
auth = prepare(cookie)                     # per-auth weapon signer, not process-global
headers.kww = frozen_kww(auth)             # do not refresh from later Set-Cookie
if need_sign("/rest/v/profile/get"):
    sig = hxfalcon(path, "GET", query={}, body=None)
    query = {__NS_hxfalcon: sig, caver: "2"}
GET axios_encode(query)                    # keep '$'
    Cookie = path-scoped wire order
    header kww
if code == 400002:
    captcha plane                          # not a sig3 bug
```

## CP 与直播

`with_cp_sign` 按 path 在 sig3 和 sig4 之间选。CP 大多数 `/rest/cp/*` 走 `__NS_sig3`，输入是 query 加 body 的 JS 值语义，不含 path 和 method。直播要按 realUrl 签名，实际请求发到映射后的 `/live_api/*`。这两条都不能用资料接口的 hxfalcon 单例去签。

## 成本判断在代码里的位置

- `__NS_hxfalcon` / `__NS_sig3`：Python 纯算模块，调用点只传 path、method、query、body。
- kwf/kws：注释写明 Brook 字节码，走 `weapon_oracle`，并检查 `navigator` 可写和布局 canary。
- 验证码：`_get` 把 400002 转成滑块处理，不把这个码当成签名算错。

53KB 量级的字节码留在 Node oracle，是对照仓的明确选择。把 oracle 出参标成 purecalc，或把作者机器的 canvas 贴到另一份 Cookie 上，都会和这个合同冲突。

## 证据边界

白名单和 `caver=2` 来自当前树。换 kwf 代际要重抓 `signUrl`，不能用仓库里的历史 `kws-N-*.js` 签线上。
