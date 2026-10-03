---
schema_version: 2
id: ruyi-gclid-navigation-tracking-reference
document_type: reference
original_date: '2026-02-13'
archived_date: '2026-10-02'
scope:
  targets: [gclid]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ruyi-20260213-01.md#浏览器指纹风控国外论文研读--点击浏览器广告之后为什么广告一直死追着用户-2026年印度理工学院论文"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录长度、编码、内容角色、查询键名和 Cookie 名角色。不复制 gclid 样例字符串，也不复制 Cookie 值。
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只记录来源流程图里的路径角色和三种泄露渠道。不把接收方排名当成当前域名清单。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 只保留点击、生成、跳转、落地和泄露的来源顺序。没有抓包，也没有失败分支。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 跨站关联、同意弹窗和浏览器剥离都是来源转述。不提供关联脚本，不把 Brave 的 0% 升成已复测。
relations:
  - type: derived_from
    target: "./ruyi-20260213-01.md#浏览器指纹风控国外论文研读--点击浏览器广告之后为什么广告一直死追着用户-2026年印度理工学院论文"
tags: [gclid, navigational-tracking, source-report]
---

# gclid 导航追踪参考

检索这份研读归档里，广告点击标识 gclid 的形态、传播路径、泄露渠道，以及来源对 Cookie 弹窗和参数清洗的判断。样例标识字符串不进入本卡。来源里的剥离函数和提取函数缺失败出口，不建成 procedure。

<a id="parameters"></a>
## 标识形态与存放位置

来源把 gclid 写成带签名的结构化点击标识，并在后文用查询键集合和若干 Cookie 名作为读取位置。这里只保留角色。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源写长度为 80-120 字符。 | s1 原文子串 长度：80-120字符；./ruyi-20260213-01.md:86 | source-report | 来源对 gclid 外形的描述 | 未用样本复核长度 |
| C2 | 来源写格式是 Base64 编码的 Protocol Buffer。 | s1 原文子串 格式：Base64编码的Protocol Buffer；./ruyi-20260213-01.md:87 | source-report | 同一外形描述 | 未解码，不记录字段编号 |
| C3 | 来源写内容角色是时间戳、广告系列 ID、用户会话标识和加密签名。 | s1 原文子串 内容：时间戳 + 广告系列ID + 用户会话标识 + 加密签名；./ruyi-20260213-01.md:88 | source-report | 来源给出的内容角色 | 没有 protobuf 布局 |
| C4 | 来源强调它不是随机字符串，带上下文和防伪造签名。 | s1 原文子串 gclid不是随机字符串，它包含了丰富的上下文信息，而且有签名防伪造。；./ruyi-20260213-01.md:91 | source-report | 来源的关键点 | 未验证签名算法 |
| C5 | 来源的清洗集合从 gclid 这个查询键写起。 | s1 原文子串 TRACKING_PARAMS = {'gclid',；./ruyi-20260213-01.md:224 | source-report | 来源草稿里的查询键集合 | 同行还有其他键名；不发布清洗函数 |
| C6 | 来源从名为 _gcl_aw 的 Cookie 里取标识。 | s1 原文子串 '_gcl_aw'；./ruyi-20260213-01.md:236 | source-report | 来源草稿的 Cookie 名 | 不记录 Cookie 值；同行还有另外两个名字 |

<a id="interfaces"></a>
## 生成路径与泄露渠道

流程图把生成和可选中转写成两条路径。渠道表把后续泄露分成 URL、Referer 和 Cookie 同步。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | 来源流程图把 gclid 的生成路径写成 /pagead/aclk。 | s1 原文子串 /pagead/aclk；./ruyi-20260213-01.md:106 | source-report | 来源绘制的 YouTube 广告点击路径 | 未抓包确认主机和状态码 |
| C8 | 同一张图把可选中转写成 /dbm/clk。 | s1 原文子串 /dbm/clk；./ruyi-20260213-01.md:106 | source-report | 来源标注为可选的中转 | 比例是图中文字，未复测 |
| C9 | URL 渠道被写成广告主页面的 JS 主动把 gclid 发给第三方。 | s1 原文子串 广告主页面的JS主动把gclid发给第三方；./ruyi-20260213-01.md:113 | source-report | 来源的三种渠道之一 | 影响范围数字未复测 |
| C10 | Referer 渠道被写成浏览器自动发送完整 URL。 | s1 原文子串 浏览器自动发送，包含完整URL；./ruyi-20260213-01.md:114 | source-report | 来源的 Referer 渠道 | 没有具体头样本 |

<a id="request-chain"></a>
## 从点击到泄露的顺序

来源把这条链称为从生成到泄露的全过程，并称广告点击一律携带该标识。顺序停在渠道分类，没有失败出口。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C11 | 来源写广告点击携带 gclid 无一例外。 | s1 原文子串 100%，无一例外；./ruyi-20260213-01.md:54 | source-report | 来源转述的测量 | 未复测点击样本 |
| C12 | 来源把后文定义为从生成到泄露的全过程。 | s1 原文子串 完整追踪了gclid从生成到泄露的全过程；./ruyi-20260213-01.md:99 | source-report | 该研读的传播路径一节 | 图是示意，不是抓包 |

<a id="risk-control"></a>
## 关联、弹窗与清洗

来源把它当作比浏览器指纹更稳的跨站信号，并认为只拦 Cookie 不够。Brave 的剥离和爬虫侧去掉查询键都是来源建议。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C13 | 来源认为 gclid 不是 Cookie，但比 Cookie 更持久、更难防护。 | s1 原文子串 gclid是一个被严重低估的用户标识符。它不是Cookie，但比Cookie更持久、更难防护。；./ruyi-20260213-01.md:60 | source-report | 来源对爬虫和指纹读者的评价 | 持久性数字在另一张表，未复测 |
| C14 | 来源写只拦截 Cookie 不够，URL 参数和 Referer 才是主要泄露渠道。 | s1 原文子串 光拦截Cookie是不够的，URL参数和Referer头才是主要泄露渠道。；./ruyi-20260213-01.md:117 | source-report | 来源的反追踪判断 | 不是检测规则 |
| C15 | 来源写 gclid 比浏览器指纹更可靠，因为是 Google 签发的。 | s1 原文子串 gclid比浏览器指纹更可靠，因为它是Google签发的；./ruyi-20260213-01.md:140 | source-report | 来源对反欺诈读者的判断 | 没有签发或验签证据 |
| C16 | 来源写 gclid 是 URL 参数，不是 Cookie，所以弹窗管不到。 | s1 原文子串 gclid是URL参数，不是Cookie；./ruyi-20260213-01.md:167 | source-report | 来源解释同意弹窗失效的第一条 | 不覆盖图中的另外两条原因 |
| C17 | 来源在浏览器对比里把 Brave 写成主动剥离。 | s1 原文子串 主动剥离；./ruyi-20260213-01.md:185 | source-report | 来源的浏览器表 | 同一行的存储率未单独复测 |
| C18 | 来源建议爬虫主动剥离 gclid 参数。 | s1 原文子串 在爬虫中主动剥离gclid参数；./ruyi-20260213-01.md:146 | source-report | 来源对爬虫的建议 | 函数草稿没有失败出口，本卡不发布实现 |
| C19 | 来源认为 GDPR 有威慑，但只降低了约 16 个百分点。 | s1 原文子串 GDPR确实有威慑作用，但只降低了约16个百分点；./ruyi-20260213-01.md:210 | source-report | 来源的地区比较结论 | 各国存储率表未复测 |
| C20 | 来源写 Cookie 拦截已经过时，URL 参数清洗才是新战场。 | s1 原文子串 Cookie拦截已经过时了，URL参数清洗才是新战场。；./ruyi-20260213-01.md:290 | source-report | 来源的延伸判断 | 不是实施步骤 |

## 验证与限制

目录里没有同目标 gclid 卡片。本卡不复制落地页上的示例标识，不发布提取或清洗代码。比例、133 个域名和浏览器存储率都停留在 source-report。同意弹窗、自动标记和第一方 Cookie 的另外两条原因只在来源图里，没有单独改写成已验证规则。
