# 抖音 webSign：钩宿主 MD5，再纯算规范化 query

> 来源: `workspace/cv-cat`（DouYin_Spider `utils/secsdk_web_sign.py`，注释中的逆向窗口 2026-08-16）
> 原始发布时间: 2026-08-16
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> stack VM 的 opcode 读不动时，先在宿主哈希入口读明文，再只复刻规范化规则。抖音 `x-secsdk-web-signature` 是这条方法的完整案例：签名是 MD5，真正容易错的是 query 规范化，以及签完之后不能再编码。

本篇不收录 VM 常量池里的盐。源码把它命名为会话无关的固定盐；知识库只写成 `VM_CONST`。换 Cookie、清空 storage 后它仍不变，才把它从会话材料里排除。字母表、keystream 同样不进库。请求面怎么把这条链接上，见 [抖音 Web 请求面](./douyin-web-request-planes.md)。

## 案例怎么定位到 MD5

源码文件头记录的路径：

1. CDP hook `XMLHttpRequest.prototype.open`，调用栈落到 security SDK 的 `webSignUrl`。策略把整条 URL 交给它重写。
2. `webSignUrl` 本体是 stack VM。静态放弃 opcode。它最终调用 `window.CryptoJS.MD5`。
3. 在 MD5 入口读到明文形状：`{uifid}_{timestamp}_{VM_CONST}_{canonical_query}`。
4. 探针：换 `uifid`、清空 Cookie 后盐不变，且盐不出现在 Cookie、localStorage 或策略配置里。于是盐归入 VM 常量池，不归入会话。
5. MD5 十六进制小写 32 位就是头字段 `x-secsdk-web-signature`。

这是「认定 VM 之后钩宿主原语」的正面例子。同一招适用于其他最终落到 `MD5` / `SM3` / `SubtleCrypto` 的 stack VM。完成门是与浏览器 oracle 对拍规范化边界，不是拆完 opcode。

## 规范化规则

`canonical_query` 的实测规则写在 `secsdk_web_sign.py`：

| 规则 | 行为 |
|------|------|
| 顺序 | 保持原始参数顺序，不排序；重复参数原样保留 |
| value | 先解码（`+` 当空格、`%XX` 当字节），再用等价于 `encodeURIComponent` 的规则重编码 |
| 不编码集合 | `A-Za-z0-9` 以及空格对应的 `%20` 之前的 `! * ' ( ) - _ . ~` |
| 空格 | 变成 `%20`，不是 `+` |
| key | 只解码，不重编码。带空格的 key 原样留下 |
| 裸参数 | 无等号的 `k` 补成 `k=` |
| timestamp | 以 `&timestamp={秒}` 追加到规范化 query 末尾，再参与哈希 |
| uifid | query 里没有时，用调用方传入的 UIFID Cookie 追加到末尾再签 |
| 幂等 | 已有的 `timestamp` 和 `x-secsdk-web-signature` 先剥掉，可以重复调用 |

Python 侧用 `urllib.parse.quote(value, safe="!*'()")` 对齐 JS `encodeURIComponent`。`quote` 本身已经放过 `_.-~`，补上 `!*'()` 才等价。

明文：

```text
plain = uifid + "_" + ts + "_" + VM_CONST + "_" + signed_query
signature = md5_hex(utf8(plain))
wire_url = base + "?" + signed_query + "&x-secsdk-web-signature=" + signature
```

`signed_query` 含 `timestamp`，不含签名字段。服务端按收到的 query 校验，所以必须发送 `sign_url()` 的返回值。

## 策略表决定谁要加签

`is_protected(path, method)` 查两张表，不是全站每个 XHR 都加签。

- GET 表含 detail、post、favorite、listcollection、mix、tab/feed、music、collects 等 path。
- POST 表是 GET 表的前 6 条，不是同一张表。

评论列表不在表里，所以 [请求面案例](./douyin-web-request-planes.md) 里评论可以 `params=` 重编码，作品详情不可以。策略表来自当时的 SDK 配置，换版本要重抓 `webSign` 策略，不能把这张表当成永久白名单。

## 真实接入

`Params.signed_url`：

```text
uifid = auth.cookie["UIFID"]
return sign_url(base_url + "?" + params.toString(), ts, uifid)
```

调用方：

```text
url = params.signed_url(origin + api, auth)
GET url, headers, cookies
# 不传 params=
```

`toString()` 不编码。签名函数内部再做解码和重编码。如果先 `quote` 再交给 `sign_url`，百分号会被再编码一次，明文和线上 query 一起漂。

## 源码自己的回归，以及本库没有重跑的部分

文件头声称：

- 5 条抓包样本（mix/listcollection、favorite、post、detail、listcollection）逐字节命中。
- 与浏览器内 `webSignUrl` oracle 差分 20 组以上边界：百分号、空格、分号、中文、空值、无等号、无 uifid、重复参数。

这些是对照仓注释里的回归记录。本知识库归档时没有重放线上样本，也没有重跑 oracle。复用时用当前浏览器的 `CryptoJS.MD5` 入口重新对拍，再决定盐和策略表是否还成立。

## 可复用探针

```text
hook XHR.open → 找到改写 URL 的函数
if 函数体是 stack VM:
    hook CryptoJS.MD5 / SubtleCrypto.digest / SM3
    记录明文模板、字段顺序、哪些段随 Cookie 变
    换 Cookie、清 storage：
        变的段 = 会话材料
        不变且不在存储里的段 = VM 常量，记名不入库
    只移植规范化与哈希
    用 oracle 对拍：空格、+、%、中文、裸 key、重复 key、已有签名字段
    发送函数返回的 URL，禁止 HTTP 客户端二次编码
```

## 误用

| 误用 | 实际会怎样 |
|------|------------|
| 拆 opcode 当作完成门 | 明文已经在 MD5 入口闭合 |
| 把 `VM_CONST` 写进长期 SDK | 它是抓包窗口的常量池，换包可能变 |
| 对 query 排序后再签 | 规则是保持原序 |
| 用 `quote_plus` 或把空格编成 `+` | 浏览器是 `%20` |
| 签完再 `params=` | 线上 query 与哈希输入分叉 |
| 给评论接口也套 webSign | 策略表没有这条 path，多字段同样偏离浏览器 |
