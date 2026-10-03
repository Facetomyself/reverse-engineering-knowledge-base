---
schema_version: 2
id: ruyi-20260215-survey-antifraud-reference
document_type: reference
original_date: '2026-02-15'
archived_date: '2026-10-02'
scope:
  targets: [online-survey-antifraud]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260215-01.md#31-rust问卷检测效果总览
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留该文转述的标注方法和检测效果对照。没有原始答卷，不外推到其他验证码或站点。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留组合优先级和中间倾向这条来源判断。没有阈值，不能单独当规则。
relations:
  - type: derived_from
    target: ./ruyi-20260215-01.md#31-rust问卷检测效果总览
tags: [survey-antifraud, source-report]
---

# 在线问卷反欺诈检测的来源对照

这篇卡检索的是：该文转述的两份付费问卷里，哪些检测被写成有效，以及单独依赖 CAPTCHA 时来源如何下判断。不收录自动化填写注意点。

<a id="risk-control"></a>
## 检测效果

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C1</td><td>单项排序原文：单项最有效的检测  |  领域知识题（Recall 86.2%）</td><td>s1，源文件第 70 行</td><td>source-report</td><td>Rust 问卷转述</td><td>题目原文不在本篇</td></tr>
<tr><td>C2</td><td>reCAPTCHA v2 在该实验中只拦住了 8 个作弊提交- 还误杀了 2 个正常用户（网络差导致图片加载失败）- Recall = 0.032（3.2%）</td><td>s1，源文件第 140 行</td><td>source-report</td><td>放在问卷末尾的这一次实验</td><td>不外推到其他验证码</td></tr>
<tr><td>C3</td><td>标注故意与技术检测分开：只看开放题的回答质量</td><td>s1，源文件第 95 行</td><td>source-report</td><td>该研究的 ground truth</td><td>四条开放题标准没有答卷</td></tr>
<tr><td>C4</td><td>重复提交对照里，指纹重复抓到95个，同一段写 Cookie 重复只抓到 7 个</td><td>s1，源文件第 152 行</td><td>source-report</td><td>Rust 问卷的重复检测表</td><td>没有指纹算法或标识原值</td></tr>
</table>

<a id="decision-flow"></a>
## 组合判断

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 优先组合而不是单点：领域知识三连 → Precision 95.5%, Recall 97.5% | s1，源文件第 72 行 | source-report | 文中 Test20+21+22 | 数字未复核 |
| C6 | 单点否决：如果你的防线只有CAPTCHA，等于没有防线。 | s1，源文件第 144 行 | source-report | 该文的人机混合样本 | 不是验证码破解分析 |
| C7 | 评分形态：如果一个用户在多个对立维度的评分都集中在中间区域，大概率是敷衍作答。 | s1，源文件第 213 行 | source-report | NASA 负荷指数那组对立题 | 没有切分阈值，不能单独启用 |

## 验证与限制

`yunpian-captcha` 的已有 risk-control 是滑块接口边界，`recaptcha` 目标下没有同模块卡片，都不覆盖这组问卷实验。第六节后半对自动化填写列出的注意点没有输出、验收和失败出口，本卡不收录。所有效果数字保持 source-report。
