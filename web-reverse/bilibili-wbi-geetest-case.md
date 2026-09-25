# B 站案例：WBI 原序写回、极验本地载荷、correspondPath

> 来源: `workspace/cv-cat`（BilibiliApis，HEAD 日期 2026-09-13，只读对照）
> 原始发布时间: 2026-09-13
> 归档日期: 2026-09-23
> 分类: web-reverse
>
> 这份对照仓已经去掉整包 `static/bili.js`。WBI、票据和 correspondPath 在 Python 里闭合；极验 v3 的 `w` 载荷本地计算，点选识别是另一层。排序只用于算 `w_rid`，发出去的 query 保持原序。

## 案例：WBI

材料：

- `img_key` / `sub_key` 来自 nav 或 `gen_web_ticket` 响应里的 `nav.img` / `nav.sub`。文件名每天轮换，不能硬编码。
- mixin 由 `img_key + sub_key` 按下标表取前 32 字符。下标表在 `utils/wbi.py` 的 `MIXIN_KEY_ENC_TAB`，表体不入库。日更的是文件名，不是这张下标表。
- `BiliAuth.mixin_key` 有约 30 分钟缓存。过期再拉 nav。

`enc_wbi` 的两条约定已经写在函数注释里，并且对过浏览器抓包：

1. `sorted` 只用于拼签名串。发出去的 dict 保持调用方顺序，末尾先追加 `w_rid`，再追加 `wts`。早先把排序后的 dict 当 URL，签名仍能过，但请求形态是错的。
2. 剔除 `!'()*` 只发生在签名串的值上。发出去的原值不动。服务端做同样的剔除再校验。

`Params.with_wbi` 必须是链式调用的最后一步。之后再 `add_param`，`w_rid` 就没有覆盖新字段。

```text
img, sub = nav.wbi_img or ticket.nav
mixin = permute(img_filename + sub_filename, MIXIN_INDEX)[:32]
to_sign = copy(params); to_sign.wts = now_s
canon = urlencode(sorted(strip_filter_chars(to_sign)))
w_rid = md5(canon + mixin)
wire = original_order(params) + w_rid + wts
```

## 案例：极验 v3 的边界

登录默认走到 `tools/geetest_solve.py`。模块分工：

| 模块 | 职责 |
|------|------|
| `utils/geetest_w.py` | fullpage / click 的 `w` 明文和加密，本地计算 |
| `utils/geetest_vision.py`、`geetest_ocr.py`、`geetest_metric.py` | 点选切图、框匹配、度量 |
| `tools/geetest_solve.py` | fullpage 无感，失败再降级 click，再 validate |
| `tools/geetest_helper.py` | 本机页面兜底，不是主路径 |

`w` 的密钥和 AES/RSA 表不入库。可复用的是分流：无感载荷可以纯算；点选坐标来自图像，不是再跑一遍 `w` 就能过。fullpage 的 type 要用 `gettype.php` 确认，不能假设每次都是 click。

## 案例：correspondPath 是续期入场券

`utils/correspond.py` 说明：每日首访 `cookie/info`，若 `data.refresh` 为真，页面用 iframe 打开 `www.bilibili.com/correspond/1/{correspondPath}`，从 HTML 取一次性 `refresh_csrf`，再换 SESSDATA / bili_jct。

明文是 `refresh_{毫秒时间戳}`。算法是页面里那把 1024 位公钥的 RSA-OAEP-SHA256，密文小写 hex，定长 256 字符。公钥写在前端 wasm 和这份 Python 里，会随页面轮换，不抄进知识库。OAEP 有随机填充，同一时间戳两次结果不同是正常的；服务端解密后比的是时间戳，不能拿两次 hex 对拍。

`bili_ticket` 是另一条链：`gen_web_ticket` 同时可以带出 nav 的 img/sub，供 WBI 使用。ticket、WBI、correspond 不要合成一个「B 站签名」。

## 传输

请求走 curl_cffi，关掉默认头，头序按抓包 tuple。设备 Cookie 里只有部分字段是首访时服务端下发的，其余按本地规则维护。伪造的 `dm_img` 采样进 WBI 后会被风控拒绝；默认空采样是抓包对齐的结果，不是「这个字段不重要」。

## 证据边界

本库没有重放登录。mixin 下标表、RSA 公钥、极验密钥留在源码对照，不作为长期 SDK 常量。
