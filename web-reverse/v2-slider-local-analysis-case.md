---
schema_version: 2
id: v2-slider-local-analysis
document_type: case
original_date: unknown
archived_date: unknown
scope:
  targets: [v2-slider]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: notes
    ref: null
    basis: source-report
    citation: 本地教学笔记（定位不公开）
    reason: 正式入库不保留讲次与公开定位；原始材料未随本文公开。
tags: [v2-slider]
---

# 网页端 V2 滑块的本地分析边界

这是一次网页端老版本滑块的本地分析案例。厂商名不稳定，不升格。它不与 [V2Pro 补环境](./v2pro-env-completion-case.md) 合并，也不与已有的阿里云验证码 V2 文章合并，不抄那批参数名、密钥或请求字段。

没有 parameters 模块。轨迹、工作量证明、点击注入和算法名都不稳定，空模块会把它们写成参数。

## 问题与范围

范围是网页端老版本滑块。不装移动端。URL 和版本读音不采用。时间和费用不核对。工具版本号不采用。

## 过程与关键证据

过程轮廓：只装网页端能力；让模型访问站点；在开发者工具里走验证码登录并滑动；出现请求后下载到本地目录。材料被说成抓包，再用 Python 调本地包，少用远程调试，因为远程调试慢、费额度。这些都是未验证轮廓，不是本仓库的抓包。

分步停在三处：先解析出一些参数；再做轨迹，但风控或工作量证明仍未完成；后面还需要鼠标点击注入。参数名不采用。报告里写过打包层次和多种可还原算法。算法名不写成某种分组算法，也不记密钥。

演示里称纯协议或纯算法可运行且校验通过。这里只记 source-report。不记 server-accepted，不记 local-parity。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 本地材料是验证码滑动后的抓包，再用 Python 调本地包 | notes | source-report | 材料轮廓 | 无 URL；本仓库没有这份抓包 |
| C2 | 分析停在未命名参数、未完成的轨迹或工作量证明、以及还需要的点击注入 | notes | source-report | 未完成的分析 | 参数名和算法名不采用 |
| C3 | 纯协议或纯算法校验通过，只是演示中的声称 | notes | source-report | 演示口径 | 不升成 server-accepted 或 local-parity |
| C4 | 本案例不是 V2Pro，也不是阿里云验证码 V2 | notes | source-report | 目标边界 | 不抄另一批参数来填空 |

## 结论与反例

正结果只有演示中的口头声称。反结果是轨迹之后的风控或工作量证明仍未完成，点击注入也还需要。没有参数表可以当作反例样本。

## 未决项与复用启示

可复用的是证据边界：口头「校验通过」不等于目标接受，抓包材料不等于本文持有请求序列。不可复用的是轨迹算法、encryption 模式、signature、token 和密钥。缺 locator，未复现。不建 request-chain。
