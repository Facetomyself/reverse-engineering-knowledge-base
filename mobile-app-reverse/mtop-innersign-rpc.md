# MTOP InnerSignImpl Frida RPC

> 来源: `workspace/cv-cat`（XianyuAndroidApis 2026-04-13 只读对照）
> 原始发布时间: 2026-04-13
> 归档日期: 2026-08-30
> 分类: mobile-app-reverse
>
> 阿里系 App 网关签名的默认路径：Hook `mtopsdk.security.InnerSignImpl.getUnifiedSign`，把实例当 RPC 工厂，而不是先还原 SG / AVMP / SO。对照样本是闲鱼 `com.taobao.idlefish`。

## 适用边界

Web H5 MTOP 的 query `sign` 走 [_m_h5_tk MD5](../web-reverse/products/alibaba-mtop-h5.md)，与本页 **不能互换**。本页只覆盖 Android 网关头族：`x-sign`、`x-sgext`、`x-mini-wua`、`x-umt`、`x-wua` / `wua`。

出现这些标记时走本页：

- 包内 `mtopsdk.security.InnerSignImpl`
- 网关 `g-acs.m.goofish.com/gw/` 或同族 `acs.m.*` / `gw.api.taobao.com` 的 App 形态
- 请求头 `x-sign`、`x-sgext`、`x-mini-wua`、`x-appkey`、`x-ttid`、`x-utdid`、`x-app-ver`、`x-t`
- 设备参数 `utdid`、`umid`、`uid`、`sid`、`ttid`、`app_ver` 必须同源

## 工作流

```text
设备可达（USB 或 remote frida-server）
→ spawn 目标包名
→ 枚举 ClassLoader（MTOP 常不在主 loader）
→ hook getUnifiedSign，只拦第一次，抓住实例与 unifiedSign Method
→ 立刻摘 hook，降低反 Frida 碰撞
→ Python RPC：传入 appKey / api / v / data / 设备字段
→ 头字段按 App 原样 URL 编码（含 + 与 /）
→ HTTP 客户端清掉 Python 默认头，verify 仅实验室关闭
```

对照闲鱼窗口里的绑定示例（会过期，只说明「必须成套」，不要当永久常量）：`appkey`、`ttid`（含渠道与版本）、`app_ver` 来自同一安装。`uid` / `sid` / `utdid` / `umid` 不匹配时接口大概率直接失败，不要先怀疑 Hook 点。

SSL Pinning 绕过是抓包前置，不是签名完成。通用 Java 层路径包括 `SSLContext.init`、OkHttp `CertificatePinner`、`TrustManagerImpl.verifyChain`、Cronet pin。公开 TrustManager 类名容易被完整性扫描；Flutter / native MAC 不在这张清单里。unpin 成功 ≠ `x-sign` 已过。

## 观察优先级

1. `frida-server` 与客户端主版本是否匹配；远程设备是否真是目标包。
2. 是否捕获到 sign 实例。超时优先查：进程未到业务页、ClassLoader 未枚举、方法 overload 已变。
3. 返回 `signInstance is null` / `unifiedSignMethod is null` 时不要改 HTTP，先修 Hook 时机。
4. 网关失败时先核对设备参数套件和 `data` 字节，再怀疑算法。
5. Web 仓的 MD5 `sign` 不能填进这些头。

## 常见坑

- 一上来 IDA / Unidbg 还原 SG，忽略可 RPC 的 Java 门面
- Hook 长期挂着打印，增加反 Frida 命中
- `requests` 默认 `User-Agent` / `Accept-Encoding` 破坏头集合
- 签名字段未按 App 做百分号编码
- 用模拟器会话的 `utdid` 配真机 `x-sign`
- 把通用 unpin 脚本当成「已过证书绑定 + 请求体 MAC」

## 验证口径

- RPC 返回的头能让目标 `mtop.*` 接口给出业务 JSON，而不是 `FAIL_SYS_SESSION_EXPIRED` / 签名错误
- 记录包名、App 版本、`ttid`、`appkey`、Hook 类名与 overload
- 版本升级后本页方法仍适用，但脚本必须重适配；无 `script loaded` + 业务读回只能标 `static-verified / runtime-pending`

落地选型见 [平台签名落地方法](../web-reverse/sign-landing-methods.md)。
