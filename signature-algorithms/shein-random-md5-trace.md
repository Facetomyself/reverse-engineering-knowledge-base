---
schema_version: 2
id: signature-algorithms-shein-random-md5-trace-reference
document_type: reference
original_date: '2026-04-14'
archived_date: '2026-10-01'
scope:
  targets:
    - Shein random parameter (source report; unverified)
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./xfq-crypto-notes-compilation/xfq-20260414-01.md#正文
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 仅记录来源描述的 trace 特征和算法状态字；目标归属、请求字段语义及当前版本行为未独立确认。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 只记录作者自述的中间排查结果；缺原始 trace、预期 digest、独立 parity 和 server-accepted 证据。
relations:
  - type: derived_from
    target: ./xfq-crypto-notes-compilation/xfq-20260414-01.md#正文
tags: [md5, trace, shein, source-report]
---

# 来源报告：random 参数中的 MD5 变体 trace 线索

本文只整理来源报告中可定位的算法线索。来源正文把样本称为 Shein 的 random 参数（s1，第 37 行）；这不是对目标归属或当前服务行为的独立确认。以下结论全部为 `source-report`，不构成可运行实现、服务端接受结果或本轮 runtime 观察。

<a id="parameters"></a>
## 参数机制

来源给出的候选分析线索：

1. 将 trace 中疑似 16 字节状态按四个 32-bit word 观察，并按小端解释后搜索相关寄存器运算（s1，第 43–50 行）。
2. 代码用 `orr.*lsl #24` 一类指令文本筛选寄存器写入；作者将每 16 个 4 字节值分组为一个 64 字节块，并以 little-endian 写入字节序列（s1，第 95–121 行）。这是依赖该来源日志格式及匹配顺序的提取线索，不是通用 trace parser。
3. Python 草稿覆写 `T[24] = 0x21e1ce4a`、`T[27] = 0x455a18d5`，并使用 `0x1fca7fb2`、`0x51b69c44`、`0xc4661e83`、`0x2dd4275f` 作为该样本的起始状态字（s1，第 145–159 行）。这些值只按来源原样记录，尚未独立校验。
4. 草稿中的 B 累积表达式写为 `self.C + self.B + b`（s1，第 197–201 行）。正文稍后把对齐关系描述为 `c+B0+b`（第 270–273 行）；两个表述的变量边界在归档中没有充分定义，本篇不把它们归并为确定公式。

| claim_id | 来源结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源以 16 字节状态和小端 word 视图回查寄存器运算 | s1，第 43–50 行 | source-report | 仅该来源所述 trace | 原始 trace 未公开，状态对应关系未独立验证 |
| C2 | 来源脚本按特定 ORR/LSL 文本提取写入值，并按 16 个值组成 64 字节块 | s1，第 95–121 行 | source-report | 匹配该来源日志格式时 | 未证明其他日志格式、分支或漏匹配行为 |
| C3 | 来源草稿包含两处 T 表覆写值及四个起始状态字 | s1，第 145–159 行 | source-report | 来源所述单一样本 | 不证明其他轮常数、函数、索引或目标版本 |
| C4 | 草稿的 B 更新表达式包含 `self.C` | s1，第 199 行 | source-report | 来源代码文本 | 与正文的 `c+B0+b` 变量表述关系未闭合 |

<a id="validation"></a>
## 验证记录

作者记录了首块拼接和填充后的计算暂时不匹配，随后追查第 63 轮的 B 状态；文末称找到额外状态项后“对上了”（s1，第 249–273 行）。这只证明来源作者报告了这段排查过程。文章没有给出可复算的预期 digest 与实际 digest 配对，也未附原始 trace。

归档代码行中有语句粘连，例如第 172 行把状态赋值与 `for`/`if` 连在一起（s1，第 172 行）；因此当前代码块不能直接作为可运行 Python 实现。正文虽调用 `print(md5_obj.hexdigest())`（第 241–246 行），但未记录该调用输出或独立比对结果。

## 范围与限制

- 来源正文声称样本来自 Shein，但目标归属未经独立确认；没有包名、应用版本、请求接口、完整请求上下文或当前目标证据。
- 来源只标注“知识星球：逆向学习交流”，没有可公开定位的原始文章链接；作者提到的原始 trace 未随文归档。
- 不能据此推断当前 Shein 是否仍使用该算法、服务端是否接受其输出，或该算法已被完整还原。
- 来源概述提示 F 函数或索引仍有魔改点待确认（s1，第 41–42 行）；加上代码语句粘连，现有材料不能形成可独立复核的完整差异。修复排版并取得已知输入/输出及原始 trace 前，不应复制为实现或宣称 parity。
- 本篇只覆盖 `parameters` 与 `validation`。来源没有足够证据建立接口、请求链路、风控结论或 procedure。
