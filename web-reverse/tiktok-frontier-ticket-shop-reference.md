---
schema_version: 2
id: web-reverse-tiktok-frontier-ticket-shop-reference
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
    ref: ./tiktok-frontier-ticket-shop-case.md#frontier-reference
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 仅整理来源报告中的三个旁路进程/输出合同；未运行 Node runner、浏览器或目标服务，不能视为当前接口可用性。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录参数来源、字段位置和形状约束；不收录口令、盐、私钥、ticket、Cookie/session、浏览器指纹或签名样值。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 归纳 IM frame、Creator HTTP 和 Shop URL 的来源链路；protobuf schema、完整 endpoint、fixture、响应验收和可运行实现均未提供。
relations:
  - type: derived_from
    target: ./tiktok-frontier-ticket-shop-case.md#frontier-reference
tags: [tiktok, frontierSign, tt-ticket-guard, Shop-BSID, request-chain, fail-closed, source-report]
---

# TikTok 旁路签名接口与请求链参考

这张卡从 [TikTok 旁路签名来源归档](./tiktok-frontier-ticket-shop-case.md#frontier-reference)提炼三条不应和 HTTP 查询签名混用的链：IM 的 `frontierSign`、Creator 写请求的 `tt-ticket-guard`，以及 Shop 的 OEC BSID。它是来源报告级的模块卡，不是可直接运行的 signer，也不提供业务风控规则。

<a id="interfaces"></a>
## 接口合同

| 平面 | 来源报告中的边界 | 失败/形状约束 | 证据边界 |
|---|---|---|---|
| IM | 独立 Node 进程按一行 JSON 输入，输出合格的 frontier marker；marker 写入 frame header map | 输入 stub 需为小写十六进制 MD5 形状；调用方只接受 `ok` 且 marker 长度合格，否则失败 | 未检查 runner、protobuf wire capture 或当前 SDK |
| Creator | 先生成新 ticket-guard 头，再把签名字段交给 HTTP query/body signer | 五个 guard 头不复放；body 需保持浏览器原样 JSON，成功口径为来源报告所述 JSON 状态字段 | 未执行请求，未验证服务端响应 |
| Shop | 独立 Node OEC loader 生成 BSID，并将结果写入 Shop 请求 URL | browser material、UA、body 和 token 形状需满足来源约束；BSID 另有输出长度检查 | 未检查 loader、Cookie 或线上拒绝响应 |

这三条输出合同不能用 legacy HTTP `X-Bogus` 字面量相互替代。名称相近不表示输入、写回位置或验收条件相同。

<a id="parameters"></a>
## 参数与字段位置

### IM frontierSign

来源报告将请求 bytes 先压成脱敏的 MD5-shaped stub，交给独立 Node signer。返回的 16 字符 marker 被写进 IM protobuf/frame 的 header map，而不是 URL query；具体 protobuf 字段和 wire bytes 不在来源中闭合。

### Creator ticket-guard

来源报告描述了以下角色：

- encrypted ticket 的密文前 12 字节作为 IV；16 字节密钥由 PBKDF2-SHA256 派生；口令和盐是 SDK 快照常量，不复制。
- ticket、path、timestamp 参与 client-data；私钥以 ECDSA P-256/SHA-256 生成签名，公钥字段为 65 字节未压缩点形状。
- `tt-ticket-guard` 前缀下有 web/version/iteration/client-data 等五个头。fresh private key、encrypted ticket 和 timestamp-sign material 需在同一操作中生成；从新 client-data 取出的 timestamp 供后续 HTTP signing 使用。

这里记录的是字段角色和字节形状，不是密钥恢复或 ticket 解密教程。

### Shop BSID

来源报告将 `oec_lucifer` 和 `msToken` 视为浏览器侧输入，要求非空 UA 与 UTF-8 body；写入 URL 的 `msToken` 使用能保留 Base64 padding 的 safe set `-._~=`。Shop 的 X-Bogus 使用来源窗口中的 endpoint-specific ubcode 14，与 Creator 的 136 不合并。BSID 只保留长度约束的形状描述，不复制值。

<a id="request-chain"></a>
## 请求链路与有界失败行为

```text
IM:
  request bytes -> MD5-shaped stub -> Node frontierSign
    -> 16-char frame marker -> protobuf/frame header map -> IM transport

Creator:
  fresh ticket-guard inputs -> five tt-* headers
    -> client-data timestamp -> query/body signing -> Creator HTTP write

Shop:
  browser OEC material + padded-msToken URL -> Node OEC BSID
    -> output shape check -> Shop request URL
```

来源报告支持一个窄的 freshness/fail-closed 边界：已消费的五个 guard 头不能直接复放；缺输入、进程超时、输出形状不合格或 runner 失败时调用方不应把旧签名填回请求。这是请求完整性与 anti-replay 的来源报告描述，不是业务 `risk-control` 模型、challenge 结果或 server acceptance。

## 限制

本卡的三个模块均为 `source-report`。来源 active client/version/observed_at 未知，原始本地项目未公开，本轮没有运行 Node、浏览器、网络、parity fixture 或目标服务。不要把 shape/length gate 当作当前服务端验收；换 SDK、端点或版本时必须重新核对字段位置和输出形状。
