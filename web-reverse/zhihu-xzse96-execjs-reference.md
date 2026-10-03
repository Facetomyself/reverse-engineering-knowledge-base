---
schema_version: 2
id: web-reverse-zhihu-xzse96-execjs-reference
document_type: reference
original_date: '2026-08-18'
archived_date: '2026-10-02'
scope:
  targets: [zhihu]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./zhihu-xzse96-execjs-case.md#comment-header
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 仅记录来源所述评论相关调用方和鉴权头落点；文章没有公开具体 endpoint URL，本卡不补造接口路径，也未验证当前服务端接受。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 仅保留 URL/query 拼接、版本字段、d_c0 字段名和 tv 的结构输入；不包含 Cookie、user、token 或 signature 样值，不恢复整包 JavaScript。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 只描述来源快照的 Python → whole-bundle ExecJS → tv → header → comment request 链；没有 fixture、输出 schema、runtime、parity 或 server-accepted 证据。
relations:
  - type: derived_from
    target: ./zhihu-xzse96-execjs-case.md#comment-header
tags: [zhihu, x-zse-96, x-zse-93, execjs, tv, source-report]
---

# 知乎 Web x-zse-96 ExecJS 参考

本文是[知乎 x-zse-96 来源归档](./zhihu-xzse96-execjs-case.md#comment-header)的窄范围提炼，补充 Web 参数与请求链检索入口。它不重复通用 whole-bundle/纯算方法论，不把整包 ExecJS 出参标成 purecalc，也不收录 Cookie、user 或 signature 样值。

<a id="interfaces"></a>
## 接口面

来源调用方在文章评论、回答评论等请求发出前写入两个鉴权头：一个版本头和一个由 bundle 导出结果包装得到的签名头。文章没有给出可公开定位的 endpoint URL，因此这里只登记“评论相关调用方”这一接口范围，不扩写成全站接口清单。

<a id="parameters"></a>
## 参数机制

- Python 边界读取请求 URL、query 键值对和 Cookie 中的 `d_c0` 字段；来源报告称 query 按调用方顺序拼接，没有额外排序步骤。
- `tv` 通过 whole-bundle ExecJS 调用，版本字段和 `d_c0` 位于其输入对象中，另有来源所述空值/null 位置；bundle 函数体和实际输出不进入本卡。
- 一个独立版本头与 bundle 结果写回的签名头分开维护。固定版本标记和包装前缀只属于该快照，前端变化后必须重新核对，不能把它们当跨版本常量。
- `static/other.js` 不在该 Python 路径中被 compile，不能因为文件相邻就并入当前 signer 链。

<a id="request-chain"></a>
## 请求链

```text
comment caller
  -> load static/zhihu.js as a whole bundle through ExecJS
  -> concatenate URL and query pairs without a separate sort
  -> pass URL/session/version-shaped inputs to export tv
  -> place wrapped result in the signing header
  -> send the comment-related request with the caller Cookie
```

这是一条来源报告的调用链，不是闭合操作流程：缺少 source checkout、bundle 版本 pin、输入输出 fixture、响应验收和统一失败 receipt。缺少 `d_c0` 时来源代码不能完成签名，但该报告没有提供当前服务错误响应或 server acceptance 证据。

## 证据与边界

- 来源项目不可公开定位，active scope 的版本、观测时间和完整性保持 unknown；本轮没有运行 browser、network、device、ExecJS 或 parity。
- 本卡不登记 `risk-control`、`validation` 或 `procedure` 模块；登录 Cookie 前置是来源调用条件，不等于风控模型或服务端判定。
- 不复制 Cookie/user/device/token/secret/signature 样值，也不收录 `zhihu.js` 或其他 bundle 内容。
