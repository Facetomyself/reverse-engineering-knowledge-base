---
schema_version: 2
id: web-opaque-string-prefix-decoder
document_type: reference
original_date: '2019-07-01'
archived_date: '2026-10-02'
scope:
  targets:
    - opaque-string-encoding
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./yuanrenxue-web-20190701-01.md#写爬虫时常见的五种字符串加密特征"
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留来源的前缀归类。未运行 unquote、unescape 或 base64 解码。百分号或结尾等号不是充分条件。示例域名只是被编码的样本文本，不代表该站参数。
relations:
  - type: derived_from
    target: "./yuanrenxue-web-20190701-01.md#写爬虫时常见的五种字符串加密特征"
tags:
  - encoding
  - source-report
---

# 不透明字符串按前缀选哪一种解码

这张卡只回答：2019-07-01 这篇把抓包或 token 参数里的长字符串分成哪五种肉眼特征，以及每种特征对应来源点名的哪个 Python 函数。它不恢复任何站点的签名。

来源没有可公开定位的原文链接。文末课程广告和相关文章外链没有编码规则，不进入结论，也不收录那些链接上的查询串。

<a id="decision-flow"></a>
## 前缀归类

来源的总结是一张五选一的表。JS 百分号编码和 Python `quote` 的差别单独占一行，因为总结表没写这一点。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 以 % 开头一般是 URL 编码，解码函数写成 urllib.parse.unquote() | s1，五种特征总结 | source-report | 来源所说的参数或页面字符串 | 未运行。% 开头不是充分条件 |
| C2 | 以 &# 开头一般是 Unicode 转义，用 html.unescape() 反转义 | s1，五种特征总结 | source-report | 同上 | 十进制实体。未运行 |
| C3 | 以 &#x 开头是 Unicode 十六进制转义，同样用 html.unescape() | s1，五种特征总结 | source-report | 同上 | 未运行 |
| C4 | 以 \u 开头被来源写成一般是 UTF-8 编码 | s1，五种特征总结 | source-report | 来源的命名 | 同文示例并不是 UTF-8 字节解码，见 C7 |
| C5 | 字符串后面以 = 结尾，通常是 base64 | s1，五种特征总结 | source-report | 来源所说的 token 外观 | “通常”不是判定。未运行 b64decode |
| C6 | Python 的 URL 编码被说成一般处理特殊字符或非英语字符；对方 JS 也会把英语字符编码 | s1，URL 编码 | source-report | 对比 Python quote 与页面 JS | 没有给出 JS 函数名 |
| C8 | 来源把那份对每个字符都编码的 JS 结果概括为对所有字符都做了编码 | s1，URL 编码末尾 | source-report | 紧挨着的那个 JS 百分号示例 | 示例原文不抄入本卡。未解码核对 |
| C7 | \u 示例行是 Python 字面量后的 print(s)，不是 UTF-8 解码调用 | s1，UTF-8 编码一节的代码行 | static-review | 这一行的文本形态 | 未执行。来源仍在 101 行和总结里把它叫 UTF-8 |

## 验证与限制

五条规则都没有失败出口：解码抛错、结果仍不可读，或等号来自填充以外的字符时，来源没有说下一步。因此不建流程。

C7 只读代码形态。作者写出的解码成功保持 source-report，本次没有本地运行。示例里的长编码串不收录。
