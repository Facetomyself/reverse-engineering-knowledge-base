# 方法论：缺字段失败，成功口径分开写

> 来源: `workspace/cv-cat`（TiktokApis `SignerError`、DouYin_Spider acrawler/create_v2、Spider_XHS 签参、JdApis tk03）
> 原始发布时间: 2026-09-23
> 归档日期: 2026-09-24
> 分类: web-reverse
>
> 签名器缺材料时应该失败，而不是补一个长度对的随机串或回放抓包。HTTP 200、进程退出码 0、oracle 有输出，各自都不是 `serverAccepted`。完成门要写成业务读回，并标明哪一层只是 `localReproduced`。

材料出处见 [出处账本](./material-provenance-ledger.md)。失败分面见 [请求面翻译](./request-plane-failure-translation.md)。

## 失败要发生在发送之前

对照仓里已经这样做的门：

| 缺口 | 行为 |
|------|------|
| TikTok 空 headers、POST 没有 body、URL 上没有浏览器 `msToken` | `SignerError`，不签名 |
| TikTok 长度和 `expected_lengths` 不一致 | 失败，不用抓包值去垫 |
| TikTok 无 unsigned URL | 静态抓包签名已禁用 |
| TikTok `post_project` 只有五个已发出的 ticket 头 | 拒绝复放，只接受私钥 + encrypt_ticket + ts_sign 重算 |
| 抖音写接口 ticket 与 Cookie 不同源 | 抛错，请求不发 |
| 抖音发布缺 CSRF、Cookie 或 dtrait | 各自返回，请求不发 |
| 抖音 acrawler 无 nonce / 无 Node / sig 不以 `_` 开头 | strict 抛错，且异常里不带 stdout（里面可能有 Cookie） |
| 小红书缺 `a1` / `web_session`、Creator 缺 `dsProgram`、签参失败 | `ValueError`，注释写明无短签兜底 |
| 小红书 `ordered_wire_headers` 缺键或多键 | `RuntimeError` |
| 京东 h5st 第 4 段不是 `tk03` | warmup 重签；仍不是就不把这次当业务 token |
| Shop 缺 160 hex 的 `oec_lucifer` 或浏览器长度的 `msToken` | `ShopBSIDError` |

```text
sign(request):
    missing = [field for field in required(request.path) if not request[field]]
    if missing:
        raise FailClosed(missing)          # do not random, do not replay capture
    values = compute(request)
    if expected_lengths and lengths(values) != expected_lengths:
        raise FailClosed("length")
    return values
```

无签名 path 是另一条规则：required 为空元组时，计算函数不应被调用。补字段和缺字段一样都是合同破坏。

## 三层完成门

| 层 | 名字 | 证据 |
|----|------|------|
| 本地形状对 | `localReproduced` | oracle 长度、前缀、与浏览器差分对拍 |
| 请求发出且传输层像浏览器 | 传输通过 | impersonate、头序、Cookie 拆分。仍不是业务成功 |
| 业务读回 | `serverAccepted` | JSON 字段、`status_code == "0"`、`base_resp.ret == 0`、列表里真有条目 |

币安公告轮询直接 `response.json()`，没有看业务码。这是薄封装的缺口，不是可以抄的成功口径。汽车之家 JSONP 剥壳成功只说明外壳还在，不说明登录态有效。

抓包签名、浏览器里复制的 `a_bogus`、复放的 ticket `client-data`，都停在「这一次字节对过」。它们不能当下一请求的输入。TikTok 注释写明复放 ticket 头会破坏抗重放。

## 伪代码：验收记录

```text
result = {
  plane: "query_sign",
  landing: "purecalc" | "oracle" | "rpc",
  local: "matched" | "failed",
  wire_sent: true | false,
  server: "accepted" | "captcha" | "empty" | "business_code" | "not_sent"
}
if result.wire_sent is false:
    # 材料门拦住了，不要改算法
if result.local == "matched" and result.server != "accepted":
    # 换一面查，见请求面翻译
```

把 `local == matched` 写成任务完成，是这套对照仓反复避开的结论。
