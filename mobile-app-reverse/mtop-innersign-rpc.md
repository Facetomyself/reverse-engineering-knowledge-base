---
schema_version: 2
id: mobile-app-reverse-mtop-innersign-rpc
document_type: reference
scope:
  targets:
  - MTOP InnerSignImpl RPC
  - Xianyu Android signing RPC (source report)
  client: Android app gateway
  version: source report; exact app/SG build unknown
  observed_at: unknown
sources:
- id: s1
  ref: null
  basis: source-report
  citation: '`本地项目分析材料（定位不公开）`（XianyuAndroidApis 2026-04-13 只读对照）'
  reason: 出处来自原归档来源字段；本地路径已省略，原始材料未随本文公开，本轮未重跑来源实验。
- id: s2
  ref: ../web-reverse/xianyu-android-sign-rpc-case.md
  basis: source-report
source_completeness: unknown
modules:
- name: interfaces
  anchor: innersign-rpc-overload
  sources: [s2]
  basis: source-report
  limits: Overload 类型序列只来自未公开的 Xianyu Android 对照报告，不能推广到其他 SDK/版本。
- name: request-chain
  anchor: innersign-rpc-workflow
  sources: [s1, s2]
  basis: source-report
  limits: Hook/RPC 工作流来自来源报告；未提供脚本、调用输出或本轮设备验证。
- name: parameters
  anchor: innersign-rpc-boundary
  sources: [s1, s2]
  basis: source-report
  limits: 设备字段、appkey、ttid 和编码必须同源；具体版本约束未闭合。
- name: validation
  anchor: innersign-rpc-validation
  sources: [s1, s2]
  basis: source-report
  limits: 业务 JSON 是来源定义的验收口径；本轮没有 runtime/server readback。
tags:
- MTOP
- InnerSignImpl
- getUnifiedSign
- x-sign
- x-sgext
- x-mini-wua
- Frida RPC
- 闲鱼
original_date: '2026-04-13'
archived_date: '2026-08-30'
---

# MTOP InnerSignImpl Frida RPC

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: `workspace/cv-cat`（XianyuAndroidApis 2026-04-13 只读对照）
> 原始发布时间: 2026-04-13
> 归档日期: 2026-08-30
> 分类: mobile-app-reverse
</details>
>
> 阿里系 App 网关签名的默认路径：Hook `mtopsdk.security.InnerSignImpl.getUnifiedSign`，把实例当 RPC 工厂，而不是先还原 SG / AVMP / SO。对照样本是闲鱼 `com.taobao.idlefish`。

<a id="innersign-rpc-boundary"></a>
## 适用边界

Web H5 MTOP 的 query `sign` 走 [_m_h5_tk MD5](../web-reverse/products/alibaba-mtop-h5.md)，与本页 **不能互换**。本页只覆盖 Android 网关头族：`x-sign`、`x-sgext`、`x-mini-wua`、`x-umt`、`x-wua` / `wua`。

未知 SG 版本或缺会话画像时，默认仍走本页 RPC。`SG doCommandNative 70102` 已闭合、且手里有 `key24` / `phase2` / 模板 / 计数时，才走 [四头纯算](../signature-algorithms/alibaba-mtop-four-headers.md)。纯算不能从任意新设备字段凭空生成会话；一加捕获只是 byte-exact 夹具。

出现这些标记时走本页：

- 包内 `mtopsdk.security.InnerSignImpl`
- 网关 `g-acs.m.goofish.com/gw/` 或同族 `acs.m.*` / `gw.api.taobao.com` 的 App 形态
- 请求头 `x-sign`、`x-sgext`、`x-mini-wua`、`x-appkey`、`x-ttid`、`x-utdid`、`x-app-ver`、`x-t`
- 设备参数 `utdid`、`umid`、`uid`、`sid`、`ttid`、`app_ver` 必须同源

<a id="innersign-rpc-workflow"></a>
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

<a id="innersign-rpc-overload"></a>
### Xianyu Android 来源报告补充：overload 与类加载

来源 s2 报告其选择的 `getUnifiedSign` overload 参数类型顺序为 `HashMap, HashMap, String, String, boolean, String`（s2，物理行 53–55）。该序列只适用于未公开的 Xianyu Android 对照材料，不能当作其他 App / SG 版本的固定接口签名。

同一来源报告在 spawn 后约 3 秒开始查找类；类尚未加载时每隔约 2 秒重试（s2，物理行 56）。这是来源脚本的时序自述，不是通用 Frida 前置条件或本轮测量值。

对照闲鱼窗口里的绑定示例（会过期，只说明「必须成套」，不要当永久常量）：`appkey`、`ttid`（含渠道与版本）、`app_ver` 来自同一安装。`uid` / `sid` / `utdid` / `umid` 不匹配时接口大概率直接失败，不要先怀疑 Hook 点。

来源 s2 另把 Python RPC 的两个 `HashMap` 分工描述为：第一个承载时间、应用/会话上下文、位置占位及扩展字段；第二个放置空的 `pageId` / `pageName`（s2，物理行 58）。来源未说明各字段必需性、空值语义或序列化规则；这里不补写具体值。

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

<a id="innersign-rpc-validation"></a>
## 验证口径

来源 s2 称签名方法返回对象为 null 时，应记为本地 RPC 调用错误，而不是空签名输出（s2，物理行 66）。这不同于捕获阶段实例为空检查，也不证明签名正确或服务端接受。

- RPC 返回的头能让目标 `mtop.*` 接口给出业务 JSON，而不是 `FAIL_SYS_SESSION_EXPIRED` / 签名错误
- 记录包名、App 版本、`ttid`、`appkey`、Hook 类名与 overload
- 版本升级后本页方法仍适用，但脚本必须重适配；无 `script loaded` + 业务读回只能标 `static-verified / runtime-pending`

落地选型见 [平台签名落地方法](../web-reverse/sign-landing-methods.md)。
