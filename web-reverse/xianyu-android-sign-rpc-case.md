# 闲鱼 Android 案例：InnerSignImpl 实例 RPC

> 来源: `workspace/cv-cat`（XianyuAndroidApis，HEAD 日期 2026-04-13，只读对照）
> 原始发布时间: 2026-04-13
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> 闲鱼 App 的网关签名走设备上的 `InnerSignImpl.getUnifiedSign`。对照仓的做法是 spawn 后等类加载、hook 一次抓住实例、立刻摘 hook，再按六参 overload 重放。这不是还原 SO，也不是 Web H5 `sign`。

方法总览见 [InnerSignImpl RPC](../mobile-app-reverse/mtop-innersign-rpc.md)。Web 分叉见 [闲鱼 Web 案例](./xianyu-web-mtop-case.md)。本篇不贴可投产的 hook 正文，也不收录设备标识原值。

## 案例流程

`goofish_client.py`：

1. `frida` 连接 USB 或 remote。
2. `device.spawn(["com.taobao.idlefish"])`，加载脚本后再 `device.resume(pid)`。
3. 等待 RPC `ping` 从 `not ready` 变成 `ready`，表示实例已被第一次真实调用抓住。
4. 业务请求发到 `https://g-acs.m.goofish.com/gw/`。query/头里的 `appkey`、`ttid`、`app_ver` 必须和被 hook 的进程一致。

`goofish_rpc.js` 的捕获合同：

1. 枚举 ClassLoader，`factory.use("mtopsdk.security.InnerSignImpl")`。
2. 绑定 overload：两个 `HashMap`、两个 `String`、一个 `boolean`、再一个 `String`。
3. 第一次进入时保存 `this` 和 factory，然后把 `implementation` 设回 `null`。后续 RPC 调用保存下来的 method ref，不再留 hook。
4. 类还没加载就 2 秒后重试。脚本在 3 秒后开始第一次尝试，给 spawn 留启动时间。

RPC 组参时，第一个 HashMap 放 `t`、`appKey`、`ttid`、经纬度占位、`extdata`、`x-features`。第二个 HashMap 放空的 `pageId` / `pageName`。调用是：

```text
unifiedSignMethod.call(instance, map1, map2, appKey, "", useWua, "r_1")
```

默认 appKey 字面量是 `21407387`。`ttid` 的形状是 `700502@fleamarket_android_<version>`，版本必须和当前包一致。`r_1` 是这份对照里的最后一参，换 SDK 要重新对 overload，不能当成永久魔数。

返回对象用 `get` 取出 `x-sign`、`x-sgext`、`x-mini-wua` 等头。null 返回记为错误，不补空签名。

## 和 Web 的边界

| 项 | App 案例 | Web 案例 |
|----|----------|----------|
| 运行时 | 真机/已安装进程里的签名实例 | execjs 或 Node vm |
| 产出 | 多个 `x-*` 头 | query `sign` |
| 网关 | `g-acs.m.goofish.com/gw/` | `h5api.m.goofish.com/h5/` |
| appKey | `21407387` | `34839810` |
| 设备字段 | 与被 hook 进程同源 | Cookie `_m_h5_tk` / `tfstk` |

客户端源码里还写死了一组 utdid / umid。那是作者设备的捕获值，换进程必须换成当前设备，不能抄进另一份会话。

## 伪代码

```text
pid = spawn("com.taobao.idlefish")
load_script()
resume(pid)
wait until ping() == "ready"          # first real getUnifiedSign captured, hook removed
headers = rpc.sign(
    t, appKey=PROCESS_APPKEY, ttid=PROCESS_TTID,
    data, useWua, tail="r_1"
)
GET g-acs.m.goofish.com/gw/{api}/{ver}/
    with headers x-sign, x-sgext, x-mini-wua, ttid, app_ver
```

版本一变，overload 和 `ttid` 都要重适配。未知版本仍走实例 RPC，不把某次抓包的 `x-sign` 当纯算完成。SG 四头的 byte-exact 纯算另有会话画像前提，见 [阿里 SG 70102 四头](../signature-algorithms/alibaba-mtop-four-headers.md)。
