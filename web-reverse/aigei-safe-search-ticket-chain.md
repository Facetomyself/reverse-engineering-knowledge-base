# 爱给网 safe-search 票据链：响应体藏票据的翻页 403 根因

> 来源: `workspace/aigei`
> 原始发布时间: 2026-09-18
> 归档日期: 2026-09-18
> 分类: web-reverse
>
> 爱给网筛选列表翻页 403 根因复盘：带 term 列表每页须走 icon.png 签发票据 → /f/d → 列表的搜索授权链，票据藏响应体 base64 尾部且按页绑定；边界已对齐仍非 200 时先做伴随请求响应体数据流审计。

## 摘要

爱给网（aigei.com）3dsmax 人物模型筛选列表：同一 URL（`/3d/max/character_models_2?term=sizem_0_3&page=N`）在浏览器 200，在 Python 客户端无 `term` 200、带 `term` 恒 403「权限不足」（`errorCode=forbidden` JSON）。根因不是风控、不是 SESSION、不是 TLS/HTTP2：带 `term` 的列表走**搜索权限门**，每页必须先完成 safe-search 票据链——`GET /search/icon.png`（签名请求）返回藏在响应体 base64 尾部的授权票据，票据值构造 `POST /f/d` 的 `v`，列表才放行；且票据**按页绑定**。这是「响应体藏数据」类反爬的典型样本：请求边界（URL/method/header/body 量级）全对齐仍非 200 时，答案在伴随请求的**响应体数据流**里。

## 现象与排除实验

| 观察 | 结果 |
|---|---|
| 浏览器带 `term` 翻页（页 2/9/13/17 乱序） | 全 200，每页 40 卡 |
| 采集器无 `term` PJAX | 200，40 卡 |
| 采集器带 `term`（query 与浏览器逐字节一致） | 403 forbidden JSON，54-90ms |
| 同步浏览器同款 SESSION / 长 Cookie 不变 | 仍 403 |
| requests / httpx-h2 / curl_cffi firefox 135-147 三栈 | 仍 403（排除 TLS/ALPN） |
| 补 term_click 统计、onload 探针、随机 rescUrl 的 search visit | 仍 403 |
| 8 小时后重试 | 仍 403（非短窗口） |

结论先行：边界已对齐仍 403 的剩余变量是**伴随请求的数据流**，不是客户端指纹。

## 根因：safe-search 票据链

浏览器每次翻页窗口（RuyiTrace 3.3 http_packet 证据）固定为三步，第三步依赖前两步的响应：

```text
GET /search/icon.png?e=<now+1..5h 格式化 yyyyMMddHH(+08)>&token=<签名串>
  响应 = 1x1 PNG + 77 字节前缀后的 base64(<input .../>)
  解出 input 属性: ftype=search_safe_visit, rurl(32 hex), extime(ms), token(32 hex)
POST /f/d  form v = AES-N({type, rescUrl=rurl, expireTime=extime, token, ...})
  （v 与下载同构：AES-ECB key `cnkierjj`，rounds 1..5 随机，N 插密文下标 32）
GET /3d/max/character_models_2?term=...&page=N&_pjax=%23tab-mount-content
  服务器校验本会话已消费过对应页的票据 → 200；否则 403「权限不足」
```

关键点：

- `GET /search/icon.png` 不是图片：请求带 `e`/`token` 签名参数，响应体是「PNG + HTML input」，内容与 `Content-Type` 语义不符——「响应体藏数据」的强信号。
- 图标请求 token 由站点 JS 生成：`aigei-search.js` 的 `_doSafeSearchWithDynamicToken` 调 `cqbj(genReqParamWithNotNull())`，`aigei.js` 的 `sssssdddttssssStr` = JSON 序列化 → `jkkc` N 轮 → N@32。`jkkc` 是六分支恒假混淆（常量折叠后只有第四分支成立），实际恒为 AES-ECB 加密、key `cnkierjj`——与 `/f/d` 的 `v` 完全同构，可用同一 codec 生成/解密。
- token 明文 = 搜索参数对象（8 键，页 ≥2 加 `page` 键）：`columnVisitCode/columnUrl/type/tab/dim/term/[page]/fromColumnCode/detailTabId`。
- 票据**按页绑定**：页 1 语境的 token 换页 2 → 403；页 2 语境 token → 200。采集器必须每页用本页参数生成新 token。
- `/f/d` 的 `v` 里 rescUrl/token 看似「随机 32 hex」——它们来自 icon 响应的票据，不是页面推导、不是随机值。「看起来随机」的参数优先查上一跳响应。

## 采集侧附带发现（同项目）

| 现象 | 定性 |
|---|---|
| `/f/d` 返回 `isComsumeFund=false` + CDN 401「remote auth failed」 | 免费额度 `freeDownCntRemain=0` 耗尽，条目级失败 |
| 新文件库 `ny4.aigei.com:8443/...GeiFileLocalStore/...pkg/...` 一律 200 + 正文 `token is error` | 站点侧新库签名不匹配（三客户端/三网络变体一致），条目级站点坏件 |
| 同会话连续下载 ~130+ 条后 `/f/d` 回 `status=vcode-normal` | 下载频控弹验证码（验证链路，与列表结算链路分开定性） |

采集策略：条目级 CDN 失败标记 error 继续（不双扣付费条目），连续 5 条才停 lane；硬币地板双保险（扣前预估 + 扣后 remain 复核）。

## 方法论教训

1. **伴随请求响应体数据流审计**：边界已对齐仍非 200 时，先看同窗口全部 200 请求的响应体（体积、与 `Content-Type` 语义一致性、字段是否被下游请求消费），再谈风控归因。本案例被错过的证据三次：icon 的 URL 参数、icon 的响应体、以及「随机 rescUrl 的来源」。
2. **参数谱系逐参数溯源**：`request-parameter-lineage.v1` 的 `sourceKind` 要落到 `previous-response | page-html | local-js | server-issued`；卡点排查阶段即启用，不是协议恢复才填。查不到写 `unresolved`，不得写「随机无法推导」就停。
3. **排除实验留档**：SESSION/cookie 漂移、三客户端栈、HTTP2/TLS 的排除结果至今有效，让根因收敛到「剩余变量」而不是重跑。
4. **JSCall 按需**：本案 HTTP 层 + 站点 JS 即闭环；若卡点持续，补开 JSCall 直接看 `fileGet` 的参数流可当场定位依赖链。

## 复现要点

- 无 `term` 列表是公开目录页（无 SESSION 时 document 301 到 `/3d/max/`）；带 `term` 列表才走票据门。
- token 生成：`gei-v-cli.js icon-token`（`encodeV(params)`，key `cnkierjj`，rounds 随机 1-5，N@32）；`e` 为 +08 时区 now+1..5h 的 `yyyyMMddHH`。
- 每页流程：`term_click` 统计（仅首页）→ icon 签票据 → `/f/d` 票据值 → 列表 → `tabMount/cnt` → `f/d/l/p`。
- 凭证与 token 原值不入文章、不入 Git；站点 cookie 名（`gei_d_1`/`gei_d_u`/`SESSION`/`SERVERID`/混淆名）仅作标识。
