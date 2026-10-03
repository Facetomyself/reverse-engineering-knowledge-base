---
schema_version: 2
id: grok-benru-anti-20260306-font-anti-crawl
document_type: reference
original_date: '2026-03-06'
archived_date: '2026-10-02'
scope:
  targets: [font-anti-crawl]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./benru-anti-20260306-01.md#11-现象看得见摸不着"
    basis: source-report
  - id: s2
    ref: "./benru-anti-20260306-01.md#12-原理偷梁换柱"
    basis: source-report
  - id: s3
    ref: "./benru-anti-20260306-01.md#13-技术演进从静态到动态"
    basis: source-report
  - id: s4
    ref: "./benru-anti-20260306-01.md#21-原理"
    basis: source-report
  - id: s5
    ref: "./benru-anti-20260306-01.md#22-核心代码实现"
    basis: source-report
  - id: s6
    ref: "./benru-anti-20260306-01.md#23-优缺点"
    basis: source-report
  - id: s7
    ref: "./benru-anti-20260306-01.md#31-原理"
    basis: source-report
  - id: s8
    ref: "./benru-anti-20260306-01.md#32-实现步骤"
    basis: source-report
  - id: s9
    ref: "./benru-anti-20260306-01.md#33-优缺点"
    basis: source-report
  - id: s10
    ref: "./benru-anti-20260306-01.md#四两种方案对比"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2, s3, s4]
    basis: source-report
    limits: 四阶段和“页面正常、源码乱码”是作者对字体反爬的描述。点名的站点只是举例，本卡不提供这些站点的字体地址。
  - name: interfaces
    anchor: interfaces
    sources: [s5, s8]
    basis: source-report
    limits: 只记录 fontTools 存 XML、fontforge 导出图片、ddddocr 识别这三个入口。不补字体 URL、标注采集或命令行参数。
  - name: parameters
    anchor: parameters
    sources: [s5, s8]
    basis: source-report
    limits: 字形序过滤、零填充、n_neighbors=1 和 uni 到 HTML 实体的替换，都按作者示例记录。训练标签从哪来，来源写的是假设。
  - name: decision-flow
    anchor: decision-flow
    sources: [s6, s9, s10]
    basis: source-report
    limits: 数字走 KNN、汉字走 OCR、混合用 OCR 兜底，是作者的分流。大更新要重训、复杂字形会认错，只说明边界，不是失败出口。
  - name: validation
    anchor: validation
    sources: [s5, s10]
    basis: source-report
    limits: 准确率打印和对照表里的 95%+ 是作者写法。没有通过阈值，也没有本次测量。
relations:
  - type: derived_from
    target: "./benru-anti-20260306-01.md#字体反爬别慌knn和ocr两套方案直接拿下"
tags: [font-anti-crawl, knn, ocr, fonttools, source-report]
---

# 自定义字体反爬的两条还原路径

这张卡回答作者如何描述字体反爬、用哪些库入口、坐标特征怎么对齐，以及数字和汉字分别走哪条路。训练集的真实数字从哪来，来源没有交代。依据停在 `source-report`。近邻查询没有同目标卡片。

<a id="risk-control"></a>
## 字体反爬在说什么

作者把现象写成页面上看得到字、源码里却是自定义字体的编码，并配 `.woff` 或 `.ttf`。演进被分成静态映射、动态文件、字形坐标随机、再叠加 CSS 和伪元素。KNN 路径依赖“同一个数字在不同文件里的坐标更像”。点名的电影、点评和征信站点只是现象举例。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 页面显示正常，源码全是乱码 | s1 ./benru-anti-20260306-01.md:55 | source-report | 字体反爬现象 | 作者概括 |
| C2 | 自定义字体文件（.woff或.ttf） | s2 ./benru-anti-20260306-01.md:62 | source-report | 字体容器 | 没有具体文件 |
| C3 | 阶段一（静态映射） | s3 ./benru-anti-20260306-01.md:70 | source-report | 演进阶段 | 难度星级是作者标注 |
| C4 | 阶段二（动态加载） | s3 ./benru-anti-20260306-01.md:71 | source-report | 演进阶段 | 同上 |
| C5 | 阶段三（字形随机） | s3 ./benru-anti-20260306-01.md:72 | source-report | 演进阶段 | 同上 |
| C6 | 阶段四（复合干扰） | s3 ./benru-anti-20260306-01.md:73 | source-report | 演进阶段 | 同上 |
| C7 | 同一个数字（比如“3”）在不同字体文件里的坐标 | s4 ./benru-anti-20260306-01.md:81 | source-report | KNN 的相似性前提 | 作者原理，未复核轮廓 |

<a id="interfaces"></a>
## 三个库入口

KNN 路径用 fontTools 把字体存成 XML。OCR 路径用 fontforge 把字形导出成图片，再用 ddddocr 做分类。来源没有字体下载地址，fontforge 片段也不是一条闭合的安装说明。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | font.saveXML(xml_path) | s5 ./benru-anti-20260306-01.md:106 | source-report | fontTools.ttLib.TTFont | 只定位保存调用 |
| C9 | fontforge | s8 ./benru-anti-20260306-01.md:198 | source-report | 字形转图片 | 工具名，没有版本 |
| C10 | ddddocr.DdddOcr() | s8 ./benru-anti-20260306-01.md:249 | source-report | OCR | 构造调用，没有模型参数 |
| C11 | ocr.classification(img_bytes) | s8 ./benru-anti-20260306-01.md:264 | source-report | OCR | 只定位识别调用 |

<a id="parameters"></a>
## 坐标与实体映射

作者丢掉 glyph order 的前两项，把坐标拉平后用 0 补到同样长度，KNN 取 `n_neighbors=1`。编码名从 `uni` 换成 HTML 实体前缀。真实标签被写成“假设 training_data 已经带好”，所以这组参数不能单独复现。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C12 | font.getGlyphOrder()[2:] | s5 ./benru-anti-20260306-01.md:113 | source-report | 字形序 | 过滤理由只是注释“前两个无用项” |
| C13 | [0]*(max_len - len(x)) | s5 ./benru-anti-20260306-01.md:145 | source-report | 坐标对齐 | 零填充会改变距离，作者未讨论 |
| C14 | n_neighbors=1 | s5 ./benru-anti-20260306-01.md:154 | source-report | KNN | 作者说这个参数通常最好，未复现 |
| C15 | uni.lower().replace('uni', '&#x') | s5 ./benru-anti-20260306-01.md:175 | source-report | KNN 映射键 | 实体格式按示例 |
| C16 | code.lower().replace('uni', '&#x') | s8 ./benru-anti-20260306-01.md:282 | source-report | OCR 映射键 | 与 KNN 同一替换 |

<a id="decision-flow"></a>
## 两条路怎么选

数字、结构稳定的字体走 KNN。汉字走 OCR。混合站点用 OCR 兜底。KNN 在字体大更新后要重新训练。OCR 慢，复杂字形可能认错。来源没有“低于某准确率就停止”的出口。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C17 | 数字类网站（猫眼票房）→ KNN坐标法 | s10 ./benru-anti-20260306-01.md:308 | source-report | 分流 | 站点是举例 |
| C18 | 汉字类网站（大众点评评价）→ OCR识别法 | s10 ./benru-anti-20260306-01.md:309 | source-report | 分流 | 站点是举例 |
| C19 | 混合型网站 → OCR兜底 | s10 ./benru-anti-20260306-01.md:310 | source-report | 分流 | 没有混合判定 |
| C20 | 每次字体大更新可能需要重新训练 | s6 ./benru-anti-20260306-01.md:182 | source-report | KNN 维护 | 不是可执行的失败步骤 |
| C21 | 个别字形复杂时可能识别错误 | s9 ./benru-anti-20260306-01.md:294 | source-report | OCR 边界 | 没有错误样本 |

<a id="validation"></a>
## 作者写下的准确率

代码只打印测试集分数。对照表把 KNN 写成高（95%+），把 OCR 写成受图片质量影响。这不是通过门槛，也不是本次结果。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C22 | 模型准确率: {knn.score(X_test, y_test)} | s5 ./benru-anti-20260306-01.md:157 | source-report | KNN 分数打印 | 没有输出值 |
| C23 | 高（95%+） | s10 ./benru-anti-20260306-01.md:302 | source-report | 对照表中的 KNN | 作者表格，不是测量 |
| C24 | 受图片质量影响 | s10 ./benru-anti-20260306-01.md:302 | source-report | 对照表中的 OCR | 同上 |

## 验证与限制

缺训练标签的来源、缺字体样本、缺通过阈值，也缺失败后改走另一条路的停止条件，所以不能写成流程。fontforge 示例里的笔对象没有接到导出上。本卡不把这些缺口补成可运行步骤。
