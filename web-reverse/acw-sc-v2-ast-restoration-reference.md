---
schema_version: 2
id: web-reverse-acw-sc-v2-ast-restoration-reference
document_type: reference
original_date: "2025-09-26"
archived_date: "2026-10-13"
scope:
  targets: [acw-sc-v2]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./acw-sc-v2-source-archive.md#source-body
    basis: source-report
modules:
  - name: decision-flow
    anchor: ast-restoration
    sources: [s1]
    basis: source-report
    limits: 仅整理来源描述的分层 AST 还原顺序；未取得完整目标脚本、浏览器解密表或完整转换代码，本轮未运行目标代码或验证 Cookie。
relations:
  - type: derived_from
    target: ./acw-sc-v2-source-archive.md#source-body
tags: [acw-sc-v2, babel-ast, binding, deobfuscation, source-report]
---

# ACW `acw_sc_v2` 混淆代码的 AST 还原参考

这张卡只提炼来源文章中可定位的 AST 操作顺序；清洗后的来源正文与缺口见 [ACW 来源归档](./acw-sc-v2-source-archive.md#source-body)。原文只报告一个目标版本，不据此推断其他 `acw_sc_v2` 实现。

<a id="ast-restoration"></a>
## 分层还原

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源先规约能静态求值的数字表达式，再识别对象属性表达式及其声明绑定。 | s1，AST 解析部分 | source-report | 来源所述的单个 `acw_sc_v2` 脚本 | 原始 AST 与完整脚本不在本批，未复核转换覆盖面。 |
| C2 | 来源通过 Babel scope / binding 追踪声明及引用，定位字符串解码调用，再用从浏览器取得的解密字符串表替换调用节点。 | s1，字符还原部分 | source-report | 来源描述的特定混淆形态 | 字符表依赖外部取得；不是只靠 AST 自动解密，原文没有完整数组或转换器。 |
| C3 | 来源在字符串恢复后回读对象查表和参数装配，解释 Cookie 生成逻辑。 | s1，代码流程与还原部分 | source-report | 来源对单目标的分析 | 完整算法输入、输出夹具与 byte-exact parity 未提供。 |

来源所述顺序可概括为：

1. 还原可静态求值的数字表达式；
2. 识别对象属性及 binding / reference 关系；
3. 用外部取得的解密字符串表替换解码调用；
4. 再分析恢复后的查表和最终表达式。

第 3 步明确依赖额外材料；不能把它写成纯 AST 自动完成字符串解密。

## 验证与限制

- 来源文件声明日期为 2025-09-26；本轮没有运行目标代码、目标请求或 Cookie 复现。
- 目标 URL 已从公共归档中脱敏，完整代码、浏览器解密表及可复算夹具均未提供。
- 本文是 `source-report` 参考，不声称当前服务端仍接受来源实现。
