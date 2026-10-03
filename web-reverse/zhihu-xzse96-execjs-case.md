---
schema_version: 2
id: web-reverse-zhihu-xzse96-execjs-case
document_type: archive
scope:
  targets:
  - zhihu
  client: unknown
  version: unknown
  observed_at: unknown
sources:
- id: s1
  ref: null
  basis: source-report
  citation: '`本地项目分析材料（定位不公开）`（ZhihuApis，HEAD 日期 2026-08-18，只读对照）'
  reason: 出处来自原归档来源字段；本地路径已省略，原始材料未随本文公开，本轮未重跑来源实验。
source_completeness: unknown
tags:
- x-zse-96
- x-zse-93
- d_c0
- execjs
- tv
original_date: '2026-08-18'
archived_date: '2026-09-23'
---

# 知乎案例：x-zse-96 走整包 execjs

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: `workspace/cv-cat`（ZhihuApis，HEAD 日期 2026-08-18，只读对照）
> 原始发布时间: 2026-08-18
> 归档日期: 2026-09-23
> 分类: web-reverse
</details>
>
> 知乎评论接口的鉴权头在这份对照仓里不是纯算。Python 编译整包 `static/zhihu.js`，把 URL 和 Cookie 里的 `d_c0` 交给导出函数 `tv`，再给返回的 signature 加上 `2.0_` 前缀。

<a id="comment-header"></a>
## 案例：评论头

`utils/zhihu_utils.py`：

1. 启动时 `execjs.compile` 读 `static/zhihu.js`。路径按运行目录试三次。这是整包，不是拆开的算法模块。
2. `get_comment_headers()` 先放固定的 `x-zse-93: 101_3_3.0`，`x-zse-96` 为空占位。
3. `get_x_zse_96(url, params, d_c0)` 把 query 拼成 `url?k=v&...`，不另做排序。
4. 调用 `js.call('tv', er, eo, ei, ec)`。`ei` 里 `zse93` 仍是 `101_3_3.0`，`dc0` 是 Cookie 的 `d_c0`，`xZst81` 为 `None`。另外两个参数是空串。
5. 返回值取 `res['signature']`，头写成 `2.0_` + signature。

`apis/zhihu_apis.py` 在文章评论、回答评论等请求发出前把这个头写进 `headers['x-zse-96']`。README 写明必须是登录后的 Cookie，缺 `d_c0` 签名无法算。

```text
d_c0 = cookies["d_c0"]
plain_url = url + "?" + join(k=v for k, v in params)
signature = execjs("zhihu.js").tv(plain_url, "", {zse93: "101_3_3.0", dc0: d_c0, xZst81: null}, "")
headers["x-zse-93"] = "101_3_3.0"
headers["x-zse-96"] = "2.0_" + signature.signature
GET comment API with Cookie
```

`static/other.js` 在这条 Python 路径里没有被 compile。不能把未接入的脚本当成现行签名。

## 落地判断

| 观察 | 结论 |
|------|------|
| 签名函数在混淆 JS 的 `tv` | 现行落地是 execjs 整包 |
| 明文输入能在 Python 边界看见：URL、`d_c0`、版本串 | 可以钩 `tv` 的入参做对拍 |
| 仓内没有把 `tv` 译成 Python | 不能把这次出参标成 purecalc |

版本串 `101_3_3.0` 和前缀 `2.0_` 是这份快照的合同。换知乎前端后先看响应头里的 `x-zse-93` 是否还是这个值，再决定 JS 包要不要换。

## 误用

把 `d_c0` 随机生成、用未登录 Cookie、或把 `x-zse-96` 留空，请求会在签名层失败。这和评论翻页逻辑无关。`zhihu.js` 的函数体不入库。

## 关联提炼

- [知乎 Web x-zse-96 ExecJS 参考](./zhihu-xzse96-execjs-reference.md#interfaces)：只拆评论相关接口面、URL/query 与 `tv` 输入结构、whole-bundle 请求链；不复制 Cookie、user、signature 样值或 bundle 内容。

## 提炼说明（742）
retain_existing_reference。既有卡 web-reverse/zhihu-xzse96-execjs-reference.md。
本轮不另建卡。不复制 Cookie/token/指纹原值。未审图片不作证据。
