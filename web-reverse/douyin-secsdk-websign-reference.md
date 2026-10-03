---
schema_version: 2
id: web-reverse-douyin-secsdk-websign-reference
document_type: reference
original_date: '2026-08-16'
archived_date: '2026-10-03'
scope:
  targets: [douyin]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./douyin-secsdk-websign-case.md#reference-extraction-202
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录明文模板、canonical_query 规则与头字段角色；不收录 VM_CONST 值、字母表、keystream、Cookie 或签名样值。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: XHR.open → webSignUrl → 宿主 MD5 → 发送返回 URL 是来源定位路径；未跑 CDP 或目标服务。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: GET/POST 策略表是当时 SDK 配置快照，换版本须重抓，不能当永久白名单。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 作者自称 5 条抓包与 20 组 oracle；本库未重跑。opcode 拆完不是完成门。
relations:
  - type: derived_from
    target: ./douyin-secsdk-websign-case.md#reference-extraction-202
  - type: supplements
    target: ./douyin-request-plane-matrix-reference.md#parameters
  - type: supplements
    target: ./vmp-host-primitive-to-purecalc.md#何时用
tags: [douyin, webSignUrl, CryptoJS.MD5, canonical-query, x-secsdk-web-signature, source-report]
---

# 抖音 webSign 规范化与宿主 MD5 参考

这张窄卡只整理来源 archive 对 **`x-secsdk-web-signature`** 的明文模板、query 规范化、受保护 path 策略和写回纪律。[请求面矩阵](./douyin-request-plane-matrix-reference.md) 不重复本算法；[VMP 钩宿主原语](./vmp-host-primitive-to-purecalc.md) 只保留方法，字段规则放在这里。盐记名 `VM_CONST`，不入库。

<a id="parameters"></a>
## 明文与规范化

来源在 `CryptoJS.MD5` 入口看到的明文形状：

```text
plain = uifid + "_" + ts + "_" + VM_CONST + "_" + signed_query
signature = md5_hex(utf8(plain))
```

`signature` 是头字段 `x-secsdk-web-signature` 的小写 32 位 hex。`signed_query` 含 `timestamp`，不含签名字段。

| 规则 | 行为 | 类别 |
|---|---|---|
| 顺序 | 保持原始参数顺序，不排序；重复参数原样保留 | encoding |
| value | 先解码（`+` 当空格、`%XX` 当字节），再按 `encodeURIComponent` 重编码 | encoding |
| 空格 | `%20`，不是 `+` | encoding |
| key | 只解码，不重编码；带空格的 key 原样留下 | encoding |
| 裸参数 | 无等号的 `k` 补成 `k=` | encoding |
| timestamp | 以 `&timestamp={秒}` 追加到规范化 query 末尾再哈希 | token / 时间 |
| uifid | query 没有时，用调用方 UIFID Cookie 追加后再签 | session |
| 幂等 | 先剥已有 `timestamp` 与 `x-secsdk-web-signature` | 重入 |

Python 侧来源用 `urllib.parse.quote(value, safe="!*'()")` 对齐 JS `encodeURIComponent`（`quote` 已放过 `_.-~`）。这是对齐说明，不是本轮 parity。

<a id="request-chain"></a>
## 定位与写回

```text
CDP hook XMLHttpRequest.prototype.open
  -> 策略把 URL 交给 webSignUrl
  -> webSignUrl 为 stack VM，最终调 window.CryptoJS.MD5
  -> 规范化 query 后追加 timestamp 与签名
  -> HTTP 客户端发送 sign_url() 的返回值，不再传 params=
```

调用方 `params.toString()` 不编码，由签名函数内部解码再重编码。若先 `quote` 再交给 `sign_url`，百分号会被再编码一次。换 Cookie、清空 storage 后盐不变且不出现在 Cookie / localStorage / 策略配置里时，来源把它归入 VM 常量池。

<a id="decision-flow"></a>
## 谁要加签

`is_protected(path, method)` 查两张表，不是全站每个 XHR 都加签。来源窗口里 GET 表覆盖 detail / post / favorite / listcollection / mix / tab/feed / music / collects 一类 path；POST 表是 GET 表的前 6 条，不是同一张表。评论列表不在表里，因此请求面案例里评论可以 `params=` 重编码，作品详情不可以。

策略表来自当时的 SDK 配置。换版本要重抓 `webSign` 策略，不能把类别名单当成永久白名单。

<a id="validation"></a>
## 验收口径与限制

| 观察 | 来源允许的最小结论 | 不允许的外推 |
|---|---|---|
| MD5 入口能读到明文模板 | 完成门可以停在宿主原语 | 必须拆完 opcode |
| 作者 5 条抓包 / 20 组 oracle | 对照仓注释中的回归记录 | 本轮 parity 或当前盐仍有效 |
| 发送函数返回的 URL | 与哈希输入同一份 query | 客户端再 `params=` 仍安全 |
| 评论接口未加签 | 当时策略表没有这条 path | 其它未点名 path 可套用 |

误用：把 `VM_CONST` 写进长期 SDK；对 query 排序后再签；`quote_plus` 或空格编成 `+`；签完再 `params=`；给评论接口套 webSign。

## 验证与限制

- 来源不可公开定位；`client` / `version` / `observed_at` 均为 unknown。
- 不收录盐、字母表、keystream、Cookie 值、签名输出或完整 path 白名单。
- 会话材料（msToken、ticket、dtrait）与 `a_bogus` 不在本卡。未运行浏览器、CDP 或目标服务。
