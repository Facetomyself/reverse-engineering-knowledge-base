---
schema_version: 2
id: shumei-js-format-detection-reference
document_type: reference
original_date: unknown
archived_date: "2026-10-08"
scope:
  targets: [shumei-captcha]
  client: web
  version: "captcha-sdk v1.0.4-208"
  observed_at: unknown
sources:
  - id: s1
    ref: ./shumei-js-format-detection.md#source-body
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 缺公开 locator。只覆盖来源点名的 v1.0.4-208 captcha SDK。未加载脚本，未看服务端解密结果。密钥字节不在来源里。
relations:
  - type: derived_from
    target: ./shumei-js-format-detection.md#source-body
tags: [shumei, isJsFormat, risk-control]
---

# 数美 captcha SDK 的格式化行数检测

这张卡只回答：来源说 `isJsFormat` 在看什么，以及命中之后加密密钥选择怎么变。它不是 Android `deviceprofile/v4` 的字段卡。

<a id="risk-control"></a>
## 行数检测与密钥切换

来源把文件定为 `castatic.fengkongcloud.cn/pr/auto-build/v1.0.4-208/captcha-sdk.min.js`。检测函数数一个诱饵函数 `toString()` 再按 `\n` 切开后的段数，大于 2 就视为格式化过。压缩文件里该函数是一行，格式化后变成三行。来源写明：只格式化、不改逻辑也会命中。

命中后的后果在来源里是 encryption，不是 signature：原来的 DES 密钥变量被换成另一个变量，再用这个密钥去加密。服务端解不开就失败。来源没有给出任一密钥的字节。来源提出的本地改法是把 `isJsFormat` 的函数体换成 `return false`。那是来源的写法，本轮没有执行。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | `isJsFormat` 用诱饵函数源码行数是否大于 2 判断格式化 | s1 | source-report | 来源点名的 v1.0.4-208 | 未复跑 toString |
| C2 | 命中后替换 DES 密钥变量，失败推迟到服务端 | s1 | source-report | 同一则来源 | 无密钥字节，无服务端样本；这不是 signature |
| C3 | 来源的改法是该函数恒返回 false | s1 的 visitor | source-report | 来源贴出的 AST 片段 | 未执行，不表示当前 SDK 仍是这个形状 |

## 验证与限制

没有 interfaces、parameters、request-chain 或 validation 模块。不记录 fingerprint 原值。Android 数美 v4 封装不由本卡补充或否定。
