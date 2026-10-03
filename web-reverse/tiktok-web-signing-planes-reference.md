---
schema_version: 2
id: web-reverse-tiktok-web-signing-planes-reference
document_type: reference
original_date: '2026-09-23'
archived_date: '2026-10-02'
scope:
  targets: [tiktok]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./tiktok-web-signing-planes.md#路由
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 仅整理来源报告中的 path 路由与字段合同；未运行 signer、浏览器或目标服务，不能视为当前接口可用性。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 记录字段角色、版本分叉和输入依赖，不收录 Cookie、token、设备指标、编码器内部常量或签名样值。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅保留 unsigned query、body、签名计算和写回的来源链；未提供可运行 fixture、网络重放或服务端验收。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: fail-closed 与长度/字段检查是来源实现口径，不代表当前版本的 parity 或 server acceptance。
relations:
  - type: derived_from
    target: ./tiktok-web-signing-planes.md#路由
tags: [tiktok, X-Bogus, X-Gnarly, X-Dynosaur, msToken, fail-closed, source-report]
---

# TikTok Web 端点签名面参考

这张卡从 [TikTok Web 签名面来源归档](./tiktok-web-signing-planes.md) 提炼 path 路由、两代 Web signer 的输入边界和写回合同。它补充旁路签名卡未覆盖的 HTTP query 签名面，不收录编码器内部实现，也不是可直接运行的 signer。

<a id="interfaces"></a>
## 接口分面

| 请求面 | 来源报告中的字段合同 | 版本/路由边界 |
|---|---|---|
| 无签名名单 | path 命中显式名单时保持 URL 不变 | 不能按“看起来短”或抓包结果临时补字段 |
| Creator project | `msToken`、`X-Bogus`、`X-Gnarly` | project path 使用 5.1.0 / `ubcode=136` 形态，不产生 `X-Dynosaur` |
| 其他 legacy Web API | `X-Dynosaur`、`msToken`、`X-Bogus`、`X-Gnarly` | 默认 Web path 使用 5.3.2 形态；`X-Bogus` 在该来源快照中是字面量 `1` |

路由由 path 子串决定，Creator project 和 legacy Web 不能共用同一个字段集合。直播 frontier、Creator ticket-guard 与 Shop BSID 属于旁路进程，见 [旁路签名接口与请求链参考](./tiktok-frontier-ticket-shop-reference.md)。

<a id="parameters"></a>
## 参数机制

- legacy signer 先从 unsigned query 中排除已有签名字段，再要求原始 query 已有 `msToken` 和非空 User-Agent；Dynosaur 绑定文档 URL，缺省时才按来源报告的 referer host/path 形成 URL。
- `X-Gnarly` 使用已拼入 Dynosaur 与 `msToken` 的 query，再结合 body 和 User-Agent；运行时槽可以来自浏览器快照，缺省值只能保持形状，不能视为可复制设备指纹。
- project signer 使用整段 query、body、User-Agent 与 project 版本约束，`X-Bogus` 和 `X-Gnarly` 写入 values；project 不产生 Dynosaur。
- body 必须保持浏览器原样 JSON 字符串。重建对象可能改变键序、空格或 Unicode 转义，进而改变签名输入。

这里区分 signature、token、fingerprint 与 body encoding：`msToken` 是输入材料，不能把它和 signer 输出或浏览器环境槽位混成“加密参数”。

<a id="request-chain"></a>
## 请求链与写回

```text
path -> required_signature_keys
  -> 保留 unsigned query，并确认 msToken / body / User-Agent 前提
  -> 按 project 或 legacy 选择 signer
  -> 生成字段 values
  -> 按 required 顺序写回 params
  -> 对最终 params 做一次 to_query() 后发送
```

通用写回合同是：签名计算使用完整 unsigned URL；签名结果通过 `params.update()` 回填；最终 URL 由统一 `to_query()` 生成，HTTP 调用不再把 params 交给另一层重复编码。来源报告特别指出签名键有独立的 safe 集合，重复编码或改变键顺序会破坏输入一致性。

Creator POST 还要求浏览器原样 body，并在同一操作中生成新鲜的 ticket-guard 材料；已有 guard 头不能直接复放。HTTP 成功口径按来源报告使用 JSON `status_code == "0"`，不是单凭 HTTP 200 判定。

<a id="validation"></a>
## Fail-closed 验收

调用前应拒绝以下不完整状态：缺 `msToken`、缺 User-Agent、body 前提不满足、签名字段缺失、长度元数据不匹配、unsigned URL 不完整，或浏览器 profile 缺来源报告要求的显式设备证据。抓包中的旧签名不能作为缺材料时的回填值。

这些检查只表达来源实现的本地完整性门。`X-Bogus="1"` 仅是该来源快照中的端点合同，不是所有 TikTok API 的永久事实；更换 SDK、端点或版本后需重新核对 path、字段集合、编码与响应完成门。

## 限制

本卡全部模块均为 `source-report`。来源项目定位不公开，当前 signer、浏览器、版本窗口、runtime/parity fixture 与目标服务行为均未在本轮复核；不把字段/长度检查升级为 runtime、parity 或 server acceptance。
