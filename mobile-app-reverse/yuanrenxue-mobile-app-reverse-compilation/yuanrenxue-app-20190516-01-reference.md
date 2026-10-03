---
schema_version: 2
id: maimai-wechat-share-card-reference
document_type: reference
original_date: '2019-05-16'
archived_date: '2026-10-02'
scope:
  targets:
    - 脉脉
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./yuanrenxue-app-20190516-01.md#让你的爬虫无障碍抓取上千万需登录的app数据"
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 三面判断只是来源的分析顺序。脉脉一步没有版本。作者的成功叙述不是本次验收。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 只保留两条路径和作者对免登录的陈述。不记录查询串，响应字段名未写。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录参数名和“值来自抓包”。没有头名、体字段或令牌样例。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 频率和 IP 归属地都是作者测试叙述，没有提示文案、时间窗或失效样本。
relations:
  - type: derived_from
    target: "./yuanrenxue-app-20190516-01.md#让你的爬虫无障碍抓取上千万需登录的app数据"
tags:
  - maimai
  - share-card
  - source-report
---

# 脉脉分享路径与免登录名片路径

这张卡只回答来源对登录墙的三面判断，以及脉脉分享路径、返回路径和参数名各写了什么。不收录账号数量，也不把作者的抓取成功写成验收。来源写明讨论的是内容没加密、但要登录才能看的情况，并写职业信息不要直接商用。

来源没有可公开定位的原文 URL。出处只保留为微信公众号自述。

<a id="decision-flow"></a>
## 三面判断

来源先把分析写成三面，再只用脉脉走完这三面。第一步在登录面上没有下手处，第三步才转到分享。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 制定正确的抓取策略，包括使用和熟悉被抓对象的产品形态（PC，H5，APP）和功能；测试被抓对象账号登录后对不同频道的访问频率控制边界（比如有的只对产品详细页做频率控制，对频道页，分类页的控制较弱）。分析被抓对象分享到微信等渠道后，从微信打开页面是否需要授权，需登录等情况。 | s1 第 54 行 | source-report | 脉脉这篇里的分析顺序 | 不是已验收流程 |
| C2 | 初步分析，脉脉的PC网站需要登录，没有专门的H5网站，APP也需要登陆才能查看。 | s1 第 62 行 | source-report | 来源当时的脉脉 | 无版本 |
| C3 | 我把详细页分享到微信后，在微信里试着打开看看，发现可以不登陆就能访问详细页。 | s1 第 71 行 | source-report | 来源当时的详情分享 | 作者观察，本次未复现 |

<a id="request-chain"></a>
## 分享路径与返回路径

来源只写出路径，没有写出响应字段名。查询串在来源里已是占位，这里不抄。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | https://open.taou.com/maimai/user/v3/share_other | s1 第 83 行 | source-report | 来源写的分享触发 | 不含查询串 |
| C5 | 这个URL会返回另一个URL，即https://maimai.cn/contact/share/card | s1 第 86 行 | source-report | 来源写的返回结果 | 字段名未知 |
| C6 | 这个URL可以不用登录就能访问。 | s1 第 87 行 | source-report | 返回的名片 URL | 无状态码或页面样本 |

<a id="parameters"></a>
## 登录参数名

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | 上面那个分享微信接口的URL参数里只需传递一个ID和access_token就认为你登录了，id和token通过抓包可以很好拿到。 | s1 第 101 行 | source-report | 来源写的 share_other 查询 | 无头名、无样例 |

<a id="risk-control"></a>
## 频率与失效

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 测试结果是对个人的详细页频率控制强，还有对搜索功能控制强。对分类等频道页控制很弱。大约一个账号快速访问200多次详细页，就会有提示了。 | s1 第 64 行 | source-report | 来源当时的脉脉频道 | 无提示文案或时间窗 |
| C9 | 点击分享这个功能的频率控制经过测试，是比较弱的。 | s1 第 91 行 | source-report | 分享功能 | 无次数阈值 |
| C10 | 一个账号频繁变换IP也是有问题的，尤其是IP归属地一会是江苏，一会是江西就更有问题了。 | s1 第 68 行 | source-report | 同一账号换 IP | 无检测字段 |
| C11 | 随着被抓对象的产品改版，或者频率控制改变，这种方法会失效。 | s1 第 112 行 | source-report | 来源自己写的失效条件 | 无失效样本，无替代路线 |

## 验证与限制

本次只读到文本，没有运行证据。作者写的上千万条、一百万页保持 source-report。后续抓取被指向另一篇文章，本篇没有抓取步骤、输出和验收，所以不是流程。账号数量估算和模拟器注册没有接口，不进入模块。
