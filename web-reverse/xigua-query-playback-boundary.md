---
schema_version: 2
id: web-reverse-xigua-query-playback-boundary-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-01'
scope:
  targets: [xigua]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./xigua-unsigned-query-case.md#案例作品列表-query
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 仅转述未公开原始项目的来源报告；版本未知，未独立检查源码或验证服务端行为；空字段不代表接口可接受或无需签名。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 请求链是来源报告中的示意；无精确 endpoint、抓包、响应或当前线上验证；播放 helper 不等同列表/评论请求步骤。
relations:
  - type: derived_from
    target: ./xigua-unsigned-query-case.md#案例作品列表-query
tags: [query-parameters, request-chain, playback-boundary]
---

# 西瓜 query 字段与播放解密边界（来源报告）

本卡仅把一份未公开原始项目的报告整理成可检索条目。以下结论均为 `source-report`，不是对当前西瓜客户端、接口或服务端的描述；客户端、版本与观测时间均未知。

<a id="parameters"></a>
## 参数边界

来源报告称，该项目的 `builder/params.py` 为作品、评论和搜索参数写入 `aid="1768"`，并将 `msToken`、`X-Bogus`、`_signature` 留为空字符串。报告还称主请求路径没有 `with_a_bogus`，没有编译头条的 `dy.js`；虽然工具文件导入了 `execjs`，主路径没有用它生成签名。这里的“空”只描述被报告的项目代码快照，不说明服务端是否接受、忽略或条件校验这些字段，也不能外推到其他版本。

报告把头条 feed 的 `aid=24`、`get_ab` 与 `genserate_sign` 作为另一条代码路径的对照，并明确不应把该路径的 `execjs` 输出直接填进西瓜字段。这个对照不是两个产品的服务端协议等价证明。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源报告称作品、评论、搜索参数包含 `aid="1768"`，`msToken`、`X-Bogus`、`_signature` 为空。 | s1；[参数描述](./xigua-unsigned-query-case.md#案例作品列表-query)，lines 41–50 | source-report | 未明确版本的 Xigua 来源项目 | 原始源码不可用；不证明字段可省略或服务端不校验。 |
| C2 | 报告称 `x-secsdk-csrf-token` 在所述 header builder 中为空占位。 | s1；[参数描述](./xigua-unsigned-query-case.md#案例作品列表-query)，line 52 | source-report | 同一来源项目快照 | 不是已取得的 CSRF 值，也不描述当前 header 要求。 |
| C3 | 报告区分头条 feed 的签名代码路径与西瓜字段快照，未支持跨产品复制签名输出。 | s1；[代码路径对照](./xigua-unsigned-query-case.md#案例作品列表-query)，line 61 | source-report | 报告所述的两个未明确版本路径 | 未验证任一当前客户端或服务端行为。 |

<a id="request-chain"></a>
## 请求与播放边界

报告把请求画成 `browser_cookie()` 取得 Cookie、与 query 合并后访问 ixigua API，再解析 JSON 或 HTML；文字称这组 query 用于用户、作品、评论、搜索调用。该片段没有列出具体 endpoint 路径、完整业务字段或抓包响应，因此只能作为来源报告里的请求形状，不能直接当作接口规格或重放脚本。

同一来源另描述 `aes_decrypt(data, key)` 播放解密 helper：对 `data` 做一次 Base64 操作；取 key 的 UTF-8 前 16 字节同时作为 AES key 与 CBC IV；解密并 unpad 后再做一次 Base64 操作，最后按 UTF-8 读取。来源原文没有交代两次 Base64 操作的方向，因此本卡不推定具体编码/解码调用。来源报告称列表/评论函数没有调用这个 helper，`__main__` 中的捕获样本和 `ptk` 是夹具而非稳定协议常量。本卡不复述这些样本值；helper 的存在不证明列表或评论响应包含需按此方式解密的播放地址。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 报告示意 Cookie + query → GET ixigua API → 解析 JSON 或 HTML。 | s1；[query 案例](./xigua-unsigned-query-case.md#案例作品列表-query)，lines 50、55–59 | source-report | 报告所述的未明确版本项目路径 | 无精确 endpoint、实际请求/响应或当前可用性证据。 |
| C5 | 报告描述了 AES-CBC 播放 helper，并称列表/评论函数未调用它；样本值为夹具。 | s1；[播放解密函数](./xigua-unsigned-query-case.md#播放解密函数的形状)，lines 65–71 | source-report | 被报告项目中的 helper 与调用关系 | 未查看源码或复算；不代表当前播放器、播放地址或接口行为。 |

## 验证与限制

来源文章明确说明没有访问西瓜线上，并指出空签名位不是“服务端不校验”的证明；若新抓包显示这些字段非空，报告中的字段结论即过期。当前接口接受情况、签名/加密机制、播放器可用性与风控策略均未知。本卡没有 runtime、parity 或 server-accepted 证据。
