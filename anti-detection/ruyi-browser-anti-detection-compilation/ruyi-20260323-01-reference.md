---
schema_version: 2
id: ruyi-20260323-peripheral-timestamp-reference
document_type: reference
original_date: '2026-03-23'
archived_date: '2026-10-02'
scope:
  targets: [peripheral-timestamp]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ruyi-20260323-01.md#相位图像phase-image"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留该文转述的时间戳输入、相位图像形状和 FPNET 的轴约束。没有权重、公式 16 的展开或数据集文件。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 准确率和防御结论都是来源对论文的转述。没有按键样本，不能外推到未测试的计时精度或输入设备。
relations:
  - type: derived_from
    target: "./ruyi-20260323-01.md#相位图像phase-image"
tags: [peripheral-timestamp, source-report]
---

# 外设时间戳相位图像的来源对照

这篇卡检索的是：该文转述的设备指纹从哪些 DOM 时间戳来、相位图像怎么铺、以及来源把哪些计时防御写成有效或无效。不收录自动化注入事件的延迟做法。

<a id="parameters"></a>
## 时间戳与相位图像

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 输入只要事件时间：监听keydown和keyup事件的时间戳（Date.now()） | s1，源文件第 43 行 | source-report | 该文描述的网页采集 | 不包含传感器、Canvas 或 WebGL |
| C2 | 瞬时相位写成 $$\varphi_i = t^R_i \mod T^S$$ | s1，源文件第 111 行 | source-report | 参考时钟读数对目标周期取模 | 符号按来源公式，未重推导 |
| C3 | 不知道真实频率时铺满探针：481个不同的假想周期（对应20Hz到500Hz的整数频率） | s1，源文件第 122 行 | source-report | 相位图像的频率轴 | 600 列对应 600 个事件，正文没有样例图 |
| C4 | 网络不能把频率轴池化掉：池化层只沿时间轴做（1×2 pooling）。 | s1，源文件第 147 行 | source-report | FPNET 的来源描述 | 没有层配置或权重 |
| C5 | 相位要用定点：论文的解决方案是用定点算术计算关键项（公式16），只在最后一步除法时才转浮点。 | s1，源文件第 346 行 | source-report | 该文对附录浮点问题的转述 | 公式 16 本身不在正文 |

<a id="risk-control"></a>
## 来源报告的区分与防御

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 验证数字：只用设备指纹（不用用户行为），就能以0.1%的假阴性率达到87.35%的真阳性率 | s1，源文件第 230 行 | source-report | 10 万台不重叠设备上的来源转述 | 未复核 TPR 定义 |
| C7 | 两套特征近独立：桌面设备：Spearman相关系数 ρ = 0.038 | s1，源文件第 242 行 | source-report | FPNET 与 TAUNET 的 Mantel 检验转述 | 移动设备的 ρ 不在这句 |
| C8 | 不读 UA 也能分操作系统家族：96.5%准确率判断你用的是Windows还是Mac | s1，源文件第 259 行 | source-report | 该文的系统画像表转述 | 浏览器家族和品牌的准确率更低，不在这句 |
| C9 | 粗化时间被写成能挡住测量：Tor Browser把所有时间源精度降到100毫秒（10Hz） | s1，源文件第 266 行 | source-report | Tor Browser 的这一档精度 | 同段写明代价是精确计时功能受影响 |
| C10 | 只抖动 performance.now 不够：KS检验显示补丁前后的嵌入距离分布没有显著差异（p > 0.05） | s1，源文件第 277 行 | source-report | Chrome v63 / Firefox v57 之后、采集仍用 Date.now() | p 值未复核 |
| C11 | 来源点名的软件方案：目前唯一被论文认为可能有效的软件方案 | s1，源文件第 283 行 | source-report | 该句点名的 kloak | 同段写明按键延迟会被人感知，没有效果数字 |

## 验证与限制

`browser-fingerprint` 的风险控制卡把 `performance.now` 列为时间与调度表面，没有相位图像、481 个频率探针或 FPNET。`peripheral-timestamp` 目标下没有已有卡片。给风控的五步没有阈值和失败出口；给自动化的事件延迟建议不进入本卡。准确率保持 source-report。
