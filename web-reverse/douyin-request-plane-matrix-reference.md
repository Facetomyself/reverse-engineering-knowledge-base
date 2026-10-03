---
schema_version: 2
id: web-reverse-douyin-request-plane-matrix-reference
document_type: reference
original_date: '2026-09-20'
archived_date: '2026-10-02'
scope:
  targets: [douyin]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./douyin-web-request-planes.md#request-plane-matrix
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 仅整理来源报告中的 detail、comment、live commerce、creator publish 与 WebSocket 分支；不构成当前接口清单，不复制端别常量值，也未验证服务端接受。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录 host、编码、body/query 与票据来源的结构关系；不收录 Cookie、ticket、私钥、设备画像或签名样值，版本与常量需随 SDK 重核。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 这是来源代码路径的窄范围装配摘要；没有统一 fixture、输出 schema、当前浏览器 oracle、runtime、parity 或 server-accepted 证据，不能直接执行。
relations:
  - type: derived_from
    target: ./douyin-web-request-planes.md#request-plane-matrix
tags: [douyin, request-plane, a_bogus, webSign, TicketGuard, source-report]
---

# 抖音 Web 请求面矩阵参考

本文从[抖音 Web 请求面来源归档](./douyin-web-request-planes.md#request-plane-matrix)提取可检索的接口面、参数边界和请求装配差异。它不重复既有 a_bogus、webSign、会话材料或通用 wire contract 的算法说明；所有结论保持 `source-report`。

<a id="interfaces"></a>
## 接口面

来源文章的标题写“七条链”，但“链怎么切开”表实际有八行：查询签名、子域常数、会话 token、URL 完整性、只读票据、写入票据、直播长连和传输。这里保留这个计数差异，不把只读/写入票据合并成同一接口面。

| 调用分支 | 可复用的区分 | 来源定位 |
|---|---|---|
| 作品详情 | 受保护 path 先构造签名 URL，再把该 URL 作为最终请求目标 | [案例 A](./douyin-web-request-planes.md#案例-a作品详情签完的-url-才是要发的-url) |
| 评论列表 | 只读票据与非受保护 GET 分支组合，允许客户端按 `params` 发送 | [案例 B](./douyin-web-request-planes.md#案例-b评论列表只读票据允许-params-重编码) |
| 直播商品 | 使用 live host 的平台模板；无商品时空 body 先按业务空结果处理 | [案例 C](./douyin-web-request-planes.md#案例-c直播电商host-绑定-a_bogus空-body-不是签名错误) |
| 创作者发布 | `create_v2` 发送前经过材料门、creator origin CSRF、body 定形和 Cookie 分片 | [案例 D](./douyin-web-request-planes.md#案例-d创作者发布材料不齐就不发) |
| 直播 WebSocket | 长连 `signature` 与主站 HTTP 的 `a_bogus` 分轨 | [链路表](./douyin-web-request-planes.md#链怎么切开) |

这张矩阵只登记调用面差异，不声称上面分支覆盖抖音当前全部接口。

<a id="parameters"></a>
## 参数边界

- `a_bogus` 的签名输入需要消费目标 `host`；来源同时区分 query 中的 aid、证书/read aid 与签名内嵌的端别标识，不能把它们压成一个全局常量。具体数值留在来源归档，不在本卡复制。
- detail 分支把 `splice_url` 形成的签名输入与最终 `signed_url` 分开；受保护 path 发送预构造 URL，comment 分支则允许 HTTP 客户端再次编码 `params`。两者不能用同一个写回策略。
- live 分支对 `entrance_info` 做整体编码，WS `signature` 另走独立链；creator 分支把紧凑 JSON body 同时作为签名输入，并要求 creator origin 的 CSRF 材料。
- 票据层按只读/写入分支选择头集合；写入分支还要求 ticket、`ts_sign` 与 `private_key` 同源。这里记录材料关系，不复制任何材料值。

<a id="request-chain"></a>
## 请求装配链

来源伪代码可压缩成以下检索顺序，节点只对应已有来源事实：

```text
plane + path + biz + auth + body
  -> choose browser headers and read/write ticket branch
  -> choose host-bound a_bogus input
  -> choose protected signed-URL write-back or ordinary params write-back
  -> choose live empty-business-result handling or response risk translation
  -> creator branch additionally requires origin CSRF, compact body and split Cookie
```

三个边界应单独保留：

1. 受保护 detail 的签名 URL 不能再交给 HTTP 客户端二次重编码；comment 的非受保护路径与此相反。
2. live 商品接口的 HTTP 200 空 body 先可能表示未挂商品，不能直接套通用签名/风控失败翻译；有内容时才进入来源所述响应分类。
3. creator 材料不齐时来源代码在发送前返回或抛错；这说明一个 fail-closed 分支，但缺少统一错误码、fixture 和验收回执，不能晋升为 procedure。

## 证据边界

- 来源是未公开本地 `DouYin_Spider` 对照材料，版本、观测时间和完整性保持 unknown；本轮没有访问目标站点、运行来源代码或重放请求。
- 表格“七/八”计数差异按来源原样记录；端别版本、host 常量和策略 path 仅属于来源窗口，换 SDK 必须重核。
- 本卡未登记 `risk-control` 或 `validation` 模块。`check_risk_response` 的信号翻译仍是来源代码描述，不是当前响应样本或服务端风控结论。
- 不收录 a_bogus 字母表、RC4 key、secsdk salt、Cookie、ticket、私钥、设备画像和签名输出样值。
