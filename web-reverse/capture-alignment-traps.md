# 技巧：抓包对齐时容易自己引入的偏差

> 来源: `workspace/cv-cat`（DouYin_Spider、BilibiliApis、JdApis、KuaiShou-Spider、TiktokApis 源码注释里的已踩坑）
> 原始发布时间: 2026-09-23
> 归档日期: 2026-09-24
> 分类: web-reverse
>
> 这些偏差不是算法没还原，而是对照实现自己把抓包形态改掉了。每条都有源码里的真实失误或防护。复用时先对这张表，再改签名。

写回总合同见 [签完即线上](./signed-query-wire-contract.md)。端别数见 [常量表](./endpoint-constant-table.md)。

## 表

| 偏差 | 真实后果 | 对照仓怎么处理 |
|------|----------|----------------|
| `parse_qsl` 丢掉空值 | 浏览器发了 `whale_cut_token=`、`rcFT=`，本地判断成「没发」 | 抖音评论显式 `add_param(..., "")` |
| 排序后的 dict 当 URL | WBI 签名仍能过，请求形态和浏览器不同 | `enc_wbi` 只对签名串 `sorted`，线上保持原序，末尾 `w_rid` 再 `wts` |
| 剔除 `!'()*` 改了原值 | 服务端是自己剔除后再校验 | 剔除只发生在签名串 |
| 公共模板覆盖接口版本 | detail 的 `version_code` 从 190500 被降成 170400 | 公共组之外按接口覆盖，并在注释里写回退 |
| 为统一抹平直播/主站 | `support_dash`、rtt、version 四处不同 | `with_live_platform` 保持差异 |
| `verifyFp` 相对 `msToken` 的位置写死 | 各接口实录不同 | detail 把 verifyFp 放在 msToken 前，以该接口抓包为准 |
| dict 合并同名键 | 京东 searchWare 有两个 `t` | 键值列表送到客户端，重试再追加一个 `t` |
| `$` 被编成 `%24` | 快手 `__NS_hxfalcon` 含 `$HE_` | axios 口径保留 `$` |
| Base64 填充被编码 | Shop 预签 URL 里 `==` 变成 `%3D%3D`，BSID 结构合法但被拒 | `quote` 的 safe 保留 `=` |
| JSON 带空格 | 京东 body 的 SHA-256 和浏览器不一致，403 | `separators=(",", ":")` |
| 签完再 `params=` | 抖音 webSign 的规范化 query 被客户端重编码 | 受保护 path 只发 `sign_url()` |
| 样本 sign 先写死再覆盖 | 读代码时把样例 hex 当成算法输出 | 淘宝 `get_token` 先写样例，再被 `generate_sign` 覆盖。以覆盖后的调用为准 |
| JS 文件里的 Cookie 样例 | 被当成盐或默认会话 | 头条 `sign.js`、飞书示例文件里的 Cookie 是捕获残留 |
| 错误文案滞后 | 去找一个已经存在的实现 | `check_risk_response` 仍写 acrawler 未纯算，同仓已有 Node runner |
| 同名函数 | 随机 msToken 被当成 mssdk 签发 | `generate_msToken` 与 `get_mstoken` 分开 |
| 冻结头被 Set-Cookie 覆盖 | 快手 `kww` 和后续 `kwfv1` 轮换分叉 | 初始化快照不得覆盖 |
| host-only Cookie 进了扁平 dict | 小红书 `acw_tc` 被带到错误 host | `HostCookieStore` |
| referer 模板里的历史 token | 被当成运行时 fingerprint | 公众号 `get_common_headers` 的 referer 样例不是设备指纹 |

## 对齐流程

```text
diff(browser_wire, local_wire):
    compare query key order, not only key set
    compare empty values
    compare duplicate keys as a list
    compare percent-encoding of '$', '=', '/', space
    compare header order and which headers are absent
    compare cookie crumbling on HTTP/2
    if bytes match and server still fails:
        translate by plane                      # not another encoding tweak
```

浏览器也返回同样的空 body 或业务码时，先当目标逻辑，不要当本地缺环境。抖音直播未挂商品就是这种：真实浏览器也是 HTTP 200 空 body。

## 伪代码：空值与同名键

```text
parse_capture(raw_query):
    # do not use parse_qsl defaults
    return split_pairs(raw_query)              # keep "k=" and repeated "t"

send(pairs):
    if signer_needs_canonical_form:
        send signer.wire_url
    else:
        send pair_list(pairs)                  # not dict(pairs)
```
