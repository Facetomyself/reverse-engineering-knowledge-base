---
schema_version: 2
id: grok-yuanrenxue-match28-rsa-fixed-padding
document_type: reference
original_date: '2026-08-04'
archived_date: '2026-10-02'
scope:
  targets: [match.yuanrenxue.cn, yuanrenxue-match-28]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ai-assisted-20260804-01.md#环境"
    basis: source-report
  - id: s2
    ref: "./ai-assisted-20260804-01.md#填充写死0x01确定性从哪来"
    basis: source-report
  - id: s3
    ref: "./ai-assisted-20260804-01.md#n怎么从操作数栈里重建"
    basis: source-report
  - id: s4
    ref: "./ai-assisted-20260804-01.md#vm执行栈机"
    basis: source-report
  - id: s5
    ref: "./ai-assisted-20260804-01.md#52个handler做什么"
    basis: source-report
  - id: s6
    ref: "./ai-assisted-20260804-01.md#站点的反调试手段"
    basis: source-report
  - id: s7
    ref: "./ai-assisted-20260804-01.md#落地验证"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s3]
    basis: source-report
    limits: 明文拼接、e=65537 和填充字节固定为 0x01 是来源原句。模数 N 的数值、填充长度和 jsbn limb 数组都不在正文里。
  - name: interfaces
    anchor: interfaces
    sources: [s1, s7]
    basis: source-report
    limits: 只记录来源点名的两个路径和 token、now、page 这三个名字。没有请求样本。
  - name: risk-control
    anchor: risk-control
    sources: [s4, s5, s6]
    basis: source-report
    limits: 52 个 handler、XOR-85、自修改和 opcode 漂移是结构描述。handler 编号每次访问会变，不能当成固定断点。
  - name: validation
    anchor: validation
    sources: [s7]
    basis: source-report
    limits: 返回 200 和真实题目是作者自述。本次没有请求。
relations:
  - type: derived_from
    target: "./ai-assisted-20260804-01.md#yuanrenxue-match28逆向rsa-1024填充写死0x01"
tags: [yuanrenxue, match28, rsa, source-report]
---

# yuanrenxue match/28 的固定填充

这张卡回答 match/28 的 token 在来源里哪一段是标准 RSA-1024，哪一段被写成固定填充。近邻查询没有同一目标的参数或接口卡。依据停在 `source-report`。

<a id="parameters"></a>
## 参数

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 算法本身是标准的RSA-1024,没有自定义密码原语 | s1，第 40 行 | source-report | match/28 的 token | 不是对库实现的复核 |
| C2 | /api/question/28 | s1，第 50 行 | source-report | 明文里的路径 | 同行还拼 now、题号和 page |
| C3 | RSA-1024, e=65537 | s1，第 50 行 | source-report | 1024 位块 | 同行还有 token = base64(密文)；未给 N |
| C4 | 填充字节全部固定成0x01,不是随机的 | s2，第 90 行 | source-report | PKCS#1 v1.5 type-2 的非零段 | 填充长度未给出 |
| C5 | jsbn把RSA大数拆成若干个28位一组的limb | s3，第 81 行 | source-report | 操作数栈上的数组 | limb 数值未列出 |
| C6 | 在h[49]调用modPow前后截一次操作数栈快照 | s3，第 85 行 | source-report | 作者的取 N 位置 | N 本身不在正文 |

第 50 行还写了 `00 02` 和 `[填充字节×N]`。随机字节被写死之后，来源称同一明文得到同一密文，因此可以不跑当次 VM。这是作者的推断，不是本次计算。

<a id="interfaces"></a>
## 接口

第 47 行写 match/28的接口是GET /api/question/28,签名参数是token。第 52 行写 now来自服务端接口/api/getTime下发,不是本地时钟。第112行的流程把 now、明文、token 和 page 串在同一次对照里，并写填充固定0x01。

<a id="risk-control"></a>
## 反分析

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | RSA运算不是明文调库,是塞进一台52-handler的JSVMP栈机 | s4，第 43 行 | source-report | match/28 | 52 个 handler 没有逐条列出 |
| C8 | h[n[o++]]() | s4，第 65 行 | source-report | 函数 p 的分派 | 来源称一次签名递归 2984 次，未复现 |
| C9 | h[7]这个字符串解码器 | s5，第 77 行 | source-report | 字符串常量 | 同行写 h[12] 会替换程序数组；编号会漂移 |
| C10 | XOR-85隐藏字符串常量 | s6，第 100 行 | source-report | API 路径等常量 | 解码表未给出 |
| C11 | opcode编号会跟着漂 | s6，第 105 行 | source-report | 每次访问重新生成的 VM | 结构性结论作者称不随编号变 |

<a id="validation"></a>
## 验证与限制

第 43 行和第 114 行写离线换算 token 后请求真实接口拿到200，并称不依赖浏览器运行时。这是作者自述。正文没有模数、没有填充长度、没有 limb 快照，不能从这篇单独算出 token。opcode 编号不能跨访问硬编码。
