---
schema_version: 2
id: web-wechat-oa-mp-cgi-query-keys
document_type: reference
original_date: '2026-08-18'
archived_date: '2026-10-02'
scope:
  targets:
    - wechat-official-account
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./wechat-oa-mp-cgi-case.md#公众号后台案例token-透传不是-mmtls"
    basis: source-report
  - id: s2
    ref: "./wechat-oa-mp-cgi-case.md#案例搜号再拉发表列表"
    basis: source-report
  - id: s3
    ref: "./wechat-oa-mp-cgi-case.md#证据边界"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s3]
    basis: source-report
    limits: 键名来自 2026-08-18 的只读对照。来源写明本库没有请求该主机。不记录 cookie 或 token 原值。接口面和完成门仍看已有会话卡与 HTTP 面卡。
relations:
  - type: derived_from
    target: "./wechat-oa-mp-cgi-case.md#案例搜号再拉发表列表"
tags:
  - wechat-official-account
  - searchbiz
  - appmsgpublish
  - source-report
---

# 公众号后台这次对照里的查询键，不是签名

这张卡只回答：2026-08-18 那份 WechatOAApis 只读对照，给 `searchbiz` 和 `appmsgpublish` 写了哪些查询键，以及 `token` 从哪来。它不重新划分会话平面，也不提供可发送的请求。

同一目标的接口面在 `../protocols/wechat-mp-http-surface.md`，`searchbiz` 到 `list_ex` 的平面和「HTTP 200 不是成功」在 `../protocols/wechat-mp-session-planes.md`。这里不重复那两条链。

<a id="parameters"></a>
## 查询键和响应形状

`token` 和 Cookie 由调用方从开发者工具复制。仓内不登录、不刷新、不算 fingerprint。下面只保留键名。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 原文含 token` 和 Cookie 由调用方从开发者工具复制，仓内不登录、不刷新、不算 fingerprint | s1，开篇范围 | source-report | 这次对照仓 | 没有样例值。不是 mmtls 或 getmsg |
| C2 | 键名原文含 action=search_biz`、`query`、`token`、`begin`、`count`、`lang=zh_CN`、`f=json`、`ajax=1 | s2，搜号再拉列表 | source-report | get_fakeid_params | 未发请求。不是完整抓包 |
| C3 | 键名原文含 sub=list`、`fakeid`、`token`、`type=101_1`、`free_publish_type=1`、`sub_action=list_ex | s2，搜号再拉列表 | source-report | get_shop_works | 来源写的是参数含这些键 |
| C4 | 原文含 publish_page` 是字符串，要再 `json.loads` 一次 | s2，搜号再拉列表 | source-report | 列表响应 | 没有响应样本 |
| C5 | 原文是翻页 `begin` 步进 5，直到超过 `total_count`，中间 `sleep`。这是后台频控间隔，不是签名窗口。 | s2，搜号再拉列表 | source-report | 这次翻页写法 | 伪代码另写 count=5。没有间隔秒数 |
| C6 | 原文是那是样例，不是运行时 fingerprint。全仓没有设备指纹计算。 | s2，请求头 | source-report | 这次对照仓 | 数字没有出现，不补 |
| C7 | 原文是届时 `ret != 0` 仍是失败。本库没有请求 mp.weixin.qq.com。 | s3，证据边界 | source-report | 2026 年后的同一 URL | 字段名以当时后台为准 |

`base_resp.ret == 0` 和「不能把 HTTP 200 当搜到了号」是这次调用的响应字段。完成门已经在会话平面卡上，不在这里再开一个 validation 模块。

## 验证与限制

- 对照是作者的 source-report。本卡没有发请求，也没有打开 `wx_apis.py`。
- 公开文章页的 GET 原文是不传 token 和 Cookie。选择器和「两面失败不能互相解释」不另建接口卡：公开正文已在 HTTP 面卡里写成无登录可抽标题、时间和图片。
- 不收录 cookie 名的值，也不补 referer 里没写出来的数字。
- 没有可执行步骤的验收样本，所以没有流程卡。
