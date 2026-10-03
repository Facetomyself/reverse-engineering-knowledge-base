---
schema_version: 2
id: web-reverse-yuanrenxue-match10-m-reference
document_type: reference
original_date: '2026-07-30'
archived_date: '2026-10-02'
scope:
  targets: [yuanrenxue]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ai-assisted-20260730-01.md#环境"
    basis: source-report
  - id: s2
    ref: "./ai-assisted-20260730-01.md#加密流程"
    basis: source-report
  - id: s3
    ref: "./ai-assisted-20260730-01.md#reqdata里一个带bug的sha-1"
    basis: source-report
  - id: s4
    ref: "./ai-assisted-20260730-01.md#第一次误判"
    basis: source-report
  - id: s5
    ref: "./ai-assisted-20260730-01.md#落地验证"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只保留来源点名的 path 和参数名。未请求该接口，不表示当前仍拒绝错误的 m。
  - name: parameters
    anchor: parameters
    sources: [s2, s3]
    basis: source-report
    limits: 只保留来源对组成、密钥长度记号、长度字和材料来源的句子。字母表、密钥字节和 config 键名不在正文，未复算。
  - name: risk-control
    anchor: risk-control
    sources: [s4]
    basis: source-report
    limits: 反调试三条措施的清单不在正文。时间窗口大小未知。指纹原值不收录。
  - name: validation
    anchor: validation
    sources: [s5]
    basis: source-report
    limits: 新会话对拍和按页重算时间常量都是作者叙述。本轮没有对拍，也不把作者的成功当成当前接口结果。
relations:
  - type: derived_from
    target: "./ai-assisted-20260730-01.md#加密流程"
tags:
  - yuanrenxue
  - match10
  - source-report
---

# yuanrenxue match/10 参数 m 的寿命与误判

这张卡只回答：来源如何描述 match/10 的参数 m 由哪些原语组成、哪些材料不能按标准 SHA-1 或按静态字面量就是服务端源码来理解，以及调试字符串为什么不能当成指纹读取。不提供签名器。字母表、密钥字节、config 键名、页面数据和指纹原值都不进入本卡。

近邻查询里 yuanrenxue 与 match10 没有已发布的 parameters、interfaces、risk-control 或 validation 卡。

<a id="interfaces"></a>
## 接口

来源把题目接口和签名参数写成一对：没有 m 或 m 算错就拒绝。页面脚本被写成可读的标准 JS，标识符带 `_yrx` 前缀，不是自定义字节码 VM。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | match/10接口/api/question/10带一个签名参数m,不带或算错直接拒。 | s1 第 44 行 | source-report | yuanrenxue match/10 | 未请求该接口 |

<a id="parameters"></a>
## 参数机制

来源把 m 写成前缀 4 加上自定义 base64。括号里的材料按它的句子分成：65 字节会话数据与校验和逐字节异或、1 字节 CRC-8、一段 AES-256-CBC 会话块、一段逐请求 AES-CBC 尾部。多项式只被点名，不展开实现。

> chk 1B CRC-8(多项式0x07)

plaintext 被写成 16 字节时间、4 字节会话和 48 字节请求常量段。尾部密钥扩展被写成非标准长度，并与标准 AES 的 Nk=8 对照。展开轮函数不在正文。

> Nk=16, Nr=22

reqData 前 16 字节被写成对大写请求 URL 做哈希。来源称标准 SHA-1 对不上，因为末块的长度字段没有写入，空位按 0 处理。

> 复现要求:刻意把W[14]/W[15]置0,不能按RFC算出真实长度再填进去

字段来源被分成池字符串、写死的老时间加当前时间戳、会话 4 字节、请求常量段和两段 SHA-1 交错的 aesKey。作者先说这些都能离线算出，随后撤回第一版结论：静态字面量是一次运行时反混淆快照，下载响应里的配置对象并不存在。

> 的结论站不住

> 静态字面量来自一次运行时反混淆快照

<a id="risk-control"></a>
## 不能当成指纹读取的字符串

fn-io 里出现 `__webdriver_evaluate` / `__selenium_evaluate` 时，来源改口说该函数是字符串解码器，返回混淆数据里的常量，真正读 navigator 的函数不在 m 的调用路径上。前四个哈希初值不能单独判成 MD5，来源用第五个常量和轮常量改判 SHA-1。常量值是公开算法初值，不在这里重列。

> 实际:该函数是字符串解码器,返回的是混淆数据里的常量串

> 真正读navigator的函数不在m的调用路径上

反调试小节说前三条挡的是分析手段、不挡 m，但这三条的清单是空的。唯一留下的产出限制是时间窗口，大小没有文档。

> 真正卡产出的只有最后一条时间窗口,窗口大小没有文档,只能试探。

<a id="validation"></a>
## 作者用来排除凑巧的对照

来源用另一个会话、从静态配置加 URL 加时间重算，并称全部字段对上真实 m，用来排除凑巧对上旧捕获。这是作者的对拍叙述。

> 凑巧对上旧会话捕获值

翻页规则被写成：会话里的时间相关常量（sec/IV）只定一次，按页重算会对不上作者所写的会话时间；每页要更新的是一次性随机值和该页 URL 的哈希。页面返回样值不收录。作者另称去掉浏览器后请求得到 200，本卡不把这句当成当前结果。

> 每页重算反而对不上服务端记录的会话时间

## 验证与限制

- 没有字母表、密钥字节、IV 推导和 config 键名，不能按本卡算出 m。
- 反调试三条措施缺失，时间窗口大小未知，所以这不是流程卡。
- 没有本轮对拍，也没有本轮请求。作者的 200 和五页数据只留在来源。
- vmtrace 未开源。配置要先由运行时解码一次，这一步的输入不在正文。
