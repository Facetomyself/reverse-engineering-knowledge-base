---
schema_version: 2
id: ruyi-mobile-web-sensor-api-reference
document_type: reference
original_date: '2026-02-07'
archived_date: '2026-10-02'
scope:
  targets: [mobile-web-sensor-api]
  client: mobile-web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ruyi-20260207-01.md#浏览器指纹风控国外论文研读--移动端指纹之传感器指纹在识别机器和真人上的普遍应用--2018年的北卡罗来纳州立大学研究"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只保留来源点名的第一方脚本路径和 POST 路径。不把论文里的第三方域名表当成当前接口清单。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录测量用的固定基值加噪声、低级特征名和统计量角色。不复制传感器样值，不提供伪造采样器。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 比例和拦截率都是来源转述的论文测量，未复测。浏览器矩阵的传感器列在归档里没有保留单元格文字。
relations:
  - type: derived_from
    target: "./ruyi-20260207-01.md#浏览器指纹风控国外论文研读--移动端指纹之传感器指纹在识别机器和真人上的普遍应用--2018年的北卡罗来纳州立大学研究"
tags: [sensor-api, openwpm, source-report]
---

# 移动网页传感器脚本测量参考

检索 2018 年移动网页传感器测量在这份研读归档里留下了哪些可定位事实：测量工具怎么标记传感器值、脚本特征怎么命名、第一方路径长什么样，以及来源对真机和静止传感器的判断。数字均保持 source-report。

<a id="interfaces"></a>
## 第一方脚本路径

来源把一个电商站点上的混淆脚本写成从第一方加载，而不是第三方域名。这是路径形状，不是一份当前站点清单。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C9 | 来源写该脚本路径固定为 /_bm/async.js。 | s1 原文子串 /_bm/async.js；./ruyi-20260207-01.md:239 | source-report | 来源提到的 homedepot.com、staples.com 一类页面 | 未复核这些站点现在是否仍加载该路径 |
| C10 | 来源写编码后的传感器数据 POST 到 /_bm/_data。 | s1 原文子串 /_bm/_data；./ruyi-20260207-01.md:241 | source-report | 同一案例的上报路径 | 没有请求体字段或响应 |

<a id="parameters"></a>
## 测量特征与传感器值标记

测量侧用固定基值加微小噪声，以便认出被送走的基值。脚本侧用低级调用名，部分脚本先算均值和方差再发送。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C3 | 来源把测量浏览器称为 OpenWPM-Mobile。 | s1 原文子串 OpenWPM-Mobile；./ruyi-20260207-01.md:83 | source-report | 该论文的测量工具 | 没有工具版本或源码定位 |
| C4 | 固定基值用来追踪数据有没有被发到远程服务器。 | s1 原文子串 基础值固定，方便追踪数据是否被发送到远程服务器；./ruyi-20260207-01.md:99 | source-report | 来源描述的传感器模拟 | 不复制具体基值 |
| C5 | 随机噪声被用来让数据看起来像真实传感器输出。 | s1 原文子串 随机噪声让数据看起来像真实传感器输出；./ruyi-20260207-01.md:100 | source-report | 同一测量设计 | 没有噪声幅度或分布 |
| C6 | 低级特征包含读取属性的 get_symbolName。 | s1 原文子串 get_symbolName；./ruyi-20260207-01.md:116 | source-report | 来源列出的特征格式 | 同表还有写入、调用和事件名，见相邻行 |
| C7 | 低级特征包含 addEventListener_eventName。 | s1 原文子串 addEventListener_eventName；./ruyi-20260207-01.md:119 | source-report | 来源列出的事件监听特征 | 没有具体事件名清单 |
| C8 | 来源写有的脚本会先计算均值和方差再发送，并认为这样更难被检测。 | s1 原文子串 有些脚本甚至会计算传感器数据的统计特征（均值、方差）再发送，这种方式更难被检测。；./ruyi-20260207-01.md:182 | source-report | 来源对论文案例的转述 | 未复现计算或检测难度 |

<a id="risk-control"></a>
## 来源对检测和防护的判断

传感器被来源当成被低估的追踪维度。拦截列表比例、静止传感器和真机手持都是来源判断，不是本卡复测结果。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源认为传感器数据是被严重低估、几乎没有有效防护的追踪维度。 | s1 原文子串 传感器数据是一个被严重低估的追踪维度，而且几乎没有有效防护。；./ruyi-20260207-01.md:66 | source-report | 来源对该论文的评价 | 不是当前网站普查 |
| C2 | 来源转述 EasyList、Disconnect 只能拦住约 2.5% 到 3.3% 的传感器追踪脚本。 | s1 原文子串 只能拦住2.5%-3.3%的传感器追踪脚本；./ruyi-20260207-01.md:62 | source-report | 来源转述的名单效果 | 后文还有分名单的比例表，未复测 |
| C11 | 来源把传感器数据写成识别真机和模拟器、以及是否有手持动作的维度。 | s1 原文子串 传感器数据是识别真机vs模拟器的有效维度，可以检测是否有真实的手持动作；./ruyi-20260207-01.md:294 | source-report | 来源的风控启示表 | 没有阈值、样本或分类器 |
| C12 | 来源写静止的传感器数据是明显的机器人特征。 | s1 原文子串 静止的传感器数据是明显的机器人特征；./ruyi-20260207-01.md:303 | source-report | 来源对指纹浏览器的启示 | 不提供运动采样方法 |
| C13 | 来源写 Brave 和 Firefox Focus 反而比普通 Safari 和 Firefox 做得更差。 | s1 原文子串 比普通的Safari和Firefox做得更差；./ruyi-20260207-01.md:273 | source-report | 来源对论文当时浏览器的转述 | 归档矩阵的传感器列没有保留单元格文字，不能补出允许或拒绝 |

## 验证与限制

`android-app-device-fingerprint` 讲的是 Android 应用画像一致性，不是这份移动网页传感器测量，所以不并入该卡。论文里的网站数、域名表和聚类比例都未复测。传感器数值样例不抄。本卡不把“需要模拟手持”扩成采样步骤。
