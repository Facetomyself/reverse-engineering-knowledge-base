---
schema_version: 2
id: ruyi-20260513-odoh-wf-reference
document_type: reference
original_date: '2026-05-13'
archived_date: '2026-10-02'
scope:
  targets: [odoh, website-fingerprinting]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260513-01.md#一odoh解决了什么又没解决什么
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留 ODoH 仍暴露流量形状，以及闭集、15% 合成背景、换解析器、跨地点和六周后的来源数字。不抄逐地点表。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留三类模型加提前退出，以及填充、分片、假包里随机化优于规整的对照。没有参数和失败出口，不能当成流程。
relations:
  - type: derived_from
    target: ./ruyi-20260513-01.md#五核心结果只看加密odoh流量准确率9434
tags: [odoh, website-fingerprinting, source-report]
---

# ODoH 网站指纹还留下什么

这篇卡检索的是：该文转述的 DSN 2025 测量里，ODoH 拆开身份和查询之后还泄漏哪一类信息，以及防御对照停在什么数字。不提供特征或扰动参数。

<a id="risk-control"></a>
## 加密之后还剩形状

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C1</td><td>核心缝隙：就算DNS内容被加密，就算身份和查询被拆开，流量形状还在。</td><td>s1，源文件第 50 行</td><td>source-report</td><td>该文的 ODoH 网站指纹</td><td>同一句后文才点出包大小、数量和时间间隔</td></tr>
<tr><td>C2</td><td>概括：加密DNS解决的是“内容不可见”，不等于“行为不可识别”。</td><td>s1，源文件第 60 行</td><td>source-report</td><td>加密 DNS</td><td>不是新测量</td></tr>
<tr><td>C3</td><td>没隐藏的字段：它只隐藏内容，不隐藏包大小、包数量、请求顺序、响应间隔和整体解析时长。</td><td>s1，源文件第 90 行</td><td>source-report</td><td>ODoH 流量</td><td>没有特征公式</td></tr>
<tr><td>C4</td><td>闭集：E3准确率  ** 94.34%  ** ，F1  ** 94.13%  ** ，FPR只有  ** 0.0006  ** 。</td><td>s1，源文件第 176 行</td><td>source-report</td><td>100 个目标网站都在测试集内</td><td>source-report</td></tr>
<tr><td>C5</td><td>15% 合成背景那一行：15%  |  0.9144  |  0.9187  |  0.0649  |  0.0009</td><td>s1，源文件第 199 行</td><td>source-report</td><td>开放世界表的 E3</td><td>背景不是真实长尾</td></tr>
<tr><td>C6</td><td>换解析器：更换resolver不能减少ODoH流量里的信息泄露。</td><td>s1，源文件第 216 行</td><td>source-report</td><td>Google、Cloudflare、Quad9</td><td>不外推到其他解析器</td></tr>
<tr><td>C7</td><td>跨地点：结果平均准确率是  ** 85.68%  ** 。</td><td>s1，源文件第 231 行</td><td>source-report</td><td>9 个地点训练、1 个地点测试</td><td>不抄逐地点表</td></tr>
<tr><td>C8</td><td>时间：六周后准确率从94.34%降到91.08%，只掉了3.26个百分点。</td><td>s1，源文件第 270 行</td><td>source-report</td><td>文中两轮采集</td><td>不是长期漂移模型</td></tr>
<tr><td>C9</td><td>实验场所：这不是野外大规模测量，而是GENI上的可控测试床</td><td>s1，源文件第 58 行</td><td>source-report</td><td>全文数字</td><td>背景流量是合成的，观察点要靠近代理</td></tr>
<tr><td>C10</td><td>标签边界：只用于确认label，不把解密内容作为模型特征</td><td>s1，源文件第 144 行</td><td>source-report</td><td>可控测试床上的打标签</td><td>不能当成任意链路都能复制</td></tr>
</table>

<a id="decision-flow"></a>
## 模型怎么分，防御对照停在哪

<table>
<tr><th>claim_id</th><th>结论</th><th>来源与定位</th><th>basis</th><th>适用范围</th><th>限制</th></tr>
<tr><td>C11</td><td>三类信号：FCNN负责吃统计特征，比如总包数、包大小统计、解析总时间。CNN负责从包大小和序列里学空间模式。GRU负责学时间序列依赖</td><td>s1，源文件第 152 行</td><td>source-report</td><td>E3 的来源分工</td><td>没有层数或训练参数</td></tr>
<tr><td>C12</td><td>开放世界先筛：这条trace是不是目标集合里的某个网站？如果不是，就提前退出，标成non-</td><td>s1，源文件第 158 行</td><td>source-report</td><td>100 类之前的提前退出</td><td>目标外这个词被拆到下一行</td></tr>
<tr><td>C13</td><td>防御动作名：padding、fragmentation和dummy packet injection</td><td>s1，源文件第 281 行</td><td>source-report</td><td>WFSafe TLS 的来源描述</td><td>没有包长或概率</td></tr>
<tr><td>C14</td><td>k=1 的对照后半：randomization能降到 / ** 7%  **</td><td>s1，源文件第 292–293 行</td><td>source-report</td><td>Fig. 13</td><td>同一句里无防御是 94%，规整是 30%；没有带宽预算</td></tr>
<tr><td>C15</td><td>延迟口径：额外处理延迟只是比无防御多零点几毫秒</td><td>s1，源文件第 307 行</td><td>source-report</td><td>本地处理时间</td><td>带宽还要另算</td></tr>
</table>

## 验证与限制

`browser-fingerprint` 只覆盖浏览器宿主对象，不覆盖 ODoH 的包序列。`dns` 与 `website-fingerprinting` 没有已发布的同名模块。全部准确率保持 source-report。第 58 行已经写明：开放世界背景是合成的，攻击者要能看到 ODoH 代理附近的流量，防御的带宽和真实部署复杂度还没有完整评估。因此防御对照不能当成可执行流程。
