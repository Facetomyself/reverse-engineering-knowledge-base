---
schema_version: 2
id: grok-web-reverse-capture-alignment-traps
document_type: reference
original_date: "2026-09-23"
archived_date: "2026-10-02"
scope:
  targets: [capture-alignment]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./capture-alignment-traps.md#表"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录来源偏差表里的形态规则。不收录 Cookie、样例 hex、端别常量或各站签名算法。站点协议卡仍管各自目标。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 只记录签完之后如何交给客户端。没有统一客户端、头序样本或可执行发送器。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 对照清单和空 body 分流是来源文本。本轮没有浏览器字节对照，也没有服务端结果。
relations:
  - type: derived_from
    target: "./capture-alignment-traps.md#表"
tags: [capture-alignment, empty-query, duplicate-key, percent-encoding]
---

# 抓包对齐时对照实现自己改掉的形态

这张卡只回答：签名算法之外，对照实现会把抓包形态改成哪些可检索的偏差，以及字节对齐之后失败该怎么分流。范围是来源偏差表和它下面的两段伪代码。不替代各站签名卡，也不把伪代码升级成可执行流程。

<a id="parameters"></a>
## 参数形态

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 偏差来自对照实现改写了抓包形态，不是算法没还原。quote: 这些偏差不是算法没还原，而是对照实现自己把抓包形态改掉了 | s1 ./capture-alignment-traps.md:38 | source-report | capture-alignment | 各条是否仍成立要重抓 |
| C2 | 空值不能用会丢空值的解析来判断浏览器没发。quote: `parse_qsl` 丢掉空值 | s1 ./capture-alignment-traps.md:46 | source-report | query 空值 | 不记录示例字段原值 |
| C3 | 排序只进入签名串；线上 query 保持原序。quote: `enc_wbi` 只对签名串 `sorted`，线上保持原序 | s1 ./capture-alignment-traps.md:47 | source-report | 签名串与 URL 分离 | 不展开 WBI 混合常量 |
| C4 | 剔除特殊字符只发生在签名串，不改原值。quote: 剔除只发生在签名串 | s1 ./capture-alignment-traps.md:48 | source-report | 签名串字符集 | 未列出服务端剔除实现 |
| C5 | 公共模板不得覆盖单接口版本，回退要写在该接口上。quote: 公共组之外按接口覆盖 | s1 ./capture-alignment-traps.md:49 | source-report | 接口版本字段 | 版本数字留在来源，不提升为当前值 |
| C6 | 直播与主站差异要保留，不能为统一抹平。quote: `with_live_platform` 保持差异 | s1 ./capture-alignment-traps.md:50 | source-report | 直播与主站模板 | 不复制四处具体值 |
| C7 | 票据字段的相对位置以该接口抓包为准，不能写死。quote: 以该接口抓包为准 | s1 ./capture-alignment-traps.md:51 | source-report | query 字段顺序 | 各接口实录不在本卡 |
| C8 | 同名键用列表保留，重试再追加，不用会合并键的 dict。quote: 键值列表送到客户端，重试再追加一个 `t` | s1 ./capture-alignment-traps.md:52 | source-report | 重复 query 键 | 京东同名键的业务预哈希另有站点卡 |
| C9 | 按来源所述的 axios 口径保留 `$`，不把它百分号编码。quote: axios 口径保留 `$` | s1 ./capture-alignment-traps.md:53 | source-report | `$` 编码 | 不记录参数内片段 |
| C10 | Base64 填充的 `=` 留在 safe 集合里。quote: `quote` 的 safe 保留 `=` | s1 ./capture-alignment-traps.md:54 | source-report | 预签 URL 填充 | 不记录票据样值 |
| C11 | JSON 摘要使用无空格分隔符。quote: `separators=(",", ":")` | s1 ./capture-alignment-traps.md:55 | source-report | body 定形 | 不证明当前摘要仍被接受 |
| C12 | 样例签名会被后续生成覆盖，以覆盖后的调用为准。quote: 以覆盖后的调用为准 | s1 ./capture-alignment-traps.md:57 | source-report | 样例与生成结果 | 不记录样例 hex |
| C13 | JS 文件里的 Cookie 样例是捕获残留，不是盐或默认会话。quote: 被当成盐或默认会话 | s1 ./capture-alignment-traps.md:58 | source-report | 示例文件 | 不抄录任何 Cookie |
| C14 | 同名 token 函数要分开，随机值不是另一条签发。quote: `generate_msToken` 与 `get_mstoken` 分开 | s1 ./capture-alignment-traps.md:60 | source-report | 同名函数 | 不记录 token 原值 |
| C15 | referer 模板里的历史材料不是运行时设备指纹。quote: referer 样例不是设备指纹 | s1 ./capture-alignment-traps.md:63 | source-report | 模板头 | 不记录该样例 |

<a id="request-chain"></a>
## 签完之后怎么交出去

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C16 | 受保护 path 只发送签名函数返回的 URL。quote: 受保护 path 只发 `sign_url()` | s1 ./capture-alignment-traps.md:56 | source-report | 受保护 path | 未受保护分支不在本句 |
| C17 | 需要规范化形式时发签名器给出的 URL，否则发键值列表。quote: send pair_list(pairs) | s1 ./capture-alignment-traps.md:92 | source-report | 伪代码发送分支 | 不是可执行客户端 |
| C18 | 初始化头快照不得被后续 Set-Cookie 覆盖。quote: 初始化快照不得覆盖 | s1 ./capture-alignment-traps.md:61 | source-report | 冻结头 | 不记录轮换后的头值 |
| C19 | host-only Cookie 不能进扁平 dict 后带到别的 host。quote: `HostCookieStore` | s1 ./capture-alignment-traps.md:62 | source-report | Cookie 作用域 | 不记录 Cookie 原值 |

<a id="validation"></a>
## 对齐时先比什么

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C20 | 先比 query 键序，不只比键集合。quote: compare query key order, not only key set | s1 ./capture-alignment-traps.md:69 | source-report | browser_wire 与 local_wire | 未实际做 diff |
| C21 | 空值要单独比。quote: compare empty values | s1 ./capture-alignment-traps.md:70 | source-report | 同上 | 未实际做 diff |
| C22 | 重复键按列表比。quote: compare duplicate keys as a list | s1 ./capture-alignment-traps.md:71 | source-report | 同上 | 未实际做 diff |
| C23 | `$`、`=`、`/` 和空格的百分号编码要单独比。quote: compare percent-encoding of '$', '=', '/', space | s1 ./capture-alignment-traps.md:72 | source-report | 百分号编码 | 未实际做 diff |
| C24 | 头序以及哪些头缺失要单独比。quote: compare header order and which headers are absent | s1 ./capture-alignment-traps.md:73 | source-report | 头 | 没有头样本 |
| C25 | HTTP/2 上的 cookie 拆分要单独比。quote: compare cookie crumbling on HTTP/2 | s1 ./capture-alignment-traps.md:74 | source-report | HTTP/2 cookie 字段 | 不记录 cookie 原值 |
| C26 | 字节已经一致而服务端仍失败时，改按面翻译，而不是再改编码。quote: if bytes match and server still fails: | s1 ./capture-alignment-traps.md:75 | source-report | 对齐后的失败 | 没有响应样本 |
| C27 | 浏览器也返回同样的空 body 或业务码时，先当目标逻辑。quote: 先当目标逻辑，不要当本地缺环境 | s1 ./capture-alignment-traps.md:79 | source-report | 空 body 与业务码 | 失败面翻译另有相邻卡 |
| C28 | 滞后错误文案不能当成当前实现缺失。quote: `check_risk_response` 仍写 acrawler 未纯算 | s1 ./capture-alignment-traps.md:59 | source-report | 错误文案 | 未打开该函数 |
| C29 | 解析抓包时不要用会丢空值的默认解析。quote: do not use parse_qsl defaults | s1 ./capture-alignment-traps.md:85 | source-report | raw query 解析 | 伪代码未运行 |

## 验证与限制

写回总合同、端别常量和各站算法不在本卡重复。京东同名键与 body 预哈希、抖音请求面、失败面翻译已有各自目标的卡片；本卡目标只是跨站形态偏差。作者写下的后果保持 source-report。本轮没有重跑来源仓库，也没有浏览器或服务端对照。
