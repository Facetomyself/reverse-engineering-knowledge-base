---
schema_version: 2
id: recaptcha-v2-audio-boundary-reference
document_type: reference
original_date: '2026-04-01'
archived_date: '2026-10-02'
scope:
  targets: [recaptcha-v2-audio]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260401-01.md#准确率
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留来源报告的通过标准和 v2 音频评测上限，以及 v3 没有音频挑战。不记录采集、回填或模型用法。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 整句准确率不是端到端通过率。回退到 v2 没有比例。反制措施未验证。
relations:
  - type: derived_from
    target: ./ruyi-20260401-01.md#准确率
tags: [recaptcha-v2-audio, source-report]
---

# reCAPTCHA v2 音频评测的覆盖边界

这篇卡检索的是：来源把什么算作音频挑战通过，该评测覆盖到哪一层，以及为什么不能把结果当成整条 reCAPTCHA 判定已经测完。不收录解题步骤。

<a id="risk-control"></a>
## 评测所覆盖的控制

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C1</td><td>只有所有数字全部正确才算对。这是实际通过验证码的标准。</td><td>s1，源文件第 98 行</td><td>source-report</td><td>该文的整句准确率</td><td>逐字准确率不能代替通过</td></tr>
<tr><td>C2</td><td>** Whisper large-v2  ** |  ** 99.99%  ** |  ** 100%  **</td><td>s1，源文件第 102 行</td><td>source-report</td><td>1000 个 v2 音频样本的来源表</td><td>不是端到端结果，也不提供用法</td></tr>
<tr><td>C3</td><td>音频验证码作为一种安全机制已经没有存在的理由了。</td><td>s1，源文件第 168 行</td><td>source-report</td><td>来源对音频挑战的判断</td><td>反制措施没有实验；无障碍要求仍在后文</td></tr>
<tr><td>C4</td><td>v3没有音频挑战——它根本没有挑战。论文的攻击只对v2有效。</td><td>s1，源文件第 179 行</td><td>source-report</td><td>来源对 v3 的范围声明</td><td>不覆盖 v3 行为评分</td></tr>
</table>

<a id="validation"></a>
## 未测部分

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C5</td><td>很多网站在v3评分不通过时会回退到v2作为fallback。</td><td>s1，源文件第 181 行</td><td>source-report</td><td>来源对部署形态的转述</td><td>没有回退比例，不能套到单个站点</td></tr>
<tr><td>C6</td><td>论文只攻击了第3步中的音频挑战，但没有评估在完整流程中</td><td>s1，源文件第 192 行</td><td>source-report</td><td>来源承认的评测缺口</td><td>整句准确率不是走到挑战之后的通过率</td></tr>
</table>

## 验证与限制

`google-recaptcha` 已有的 risk-control、parameters、validation 是 v3 请求链和风控面，不包含这段 v2 音频评测，所以本卡用单独目标。`recaptcha` 与 `captcha` 没有同模块卡片。采集回填、速度、成本和模型选型都不在本卡。所有数字保持 source-report。
