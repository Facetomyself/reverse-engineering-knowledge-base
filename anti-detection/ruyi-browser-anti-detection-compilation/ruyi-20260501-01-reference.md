---
schema_version: 2
id: ruyi-20260501-local-frame-origin-reference
document_type: reference
original_date: '2026-05-01'
archived_date: '2026-10-02'
scope:
  targets: [local-frame]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260501-01.md#一local-frame是什么为什么能绕过拦截
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留继承规则、算错归属、普及率和 73.7% 通过比例的转述，以及密码填充与同域复制的边界。不收录投放或反爬用法，不抄环境值。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留父级比较、祖先 URL、两条取 origin 路径、注入竞态和测量代码的错法。修复日期不是复测结果，也不能当成流程。
relations:
  - type: derived_from
    target: ./ruyi-20260501-01.md#一local-frame是什么为什么能绕过拦截
tags: [local-frame, source-report]
---

# local frame 的 origin 归属边界

这篇卡检索的是：来源转述的论文里，about:blank 这类 local frame 的 origin 应该跟谁，以及内容拦截器被写成哪几种算错。不提供把追踪脚本放进 frame 的做法。

<a id="risk-control"></a>
## 归属算错时拦截会漏

local frame 在这里指 source 不是普通 URL 的 iframe。创建 about:blank 本身不发请求，内容可以事后注入。规范上的归属和工具实际使用的归属不是一回事。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 规范行为被写成：继承创建它的文档的origin | s1，源文件第 66 行 | source-report | about:blank iframe | 未对照当前规范文本 |
| C2 | 失效原因被写成：内容拦截器在判断local frame的origin时搞错了 | s1，源文件第 74 行 | source-report | 文中点名的内容拦截工具 | 各工具错法不同 |
| C3 | 请求比例：73.7%应该被拦截但因为local frame的origin混淆问题而通过了 | s1，源文件第 140 行 | source-report | 文中 adblock-rs 对三份名单的检查 | 未重跑 |
| C4 | 普及范围：超过一半的网站使用了local frame | s1，源文件第 102 行 | source-report | 文中 Tranco 爬取 | 不是拦截失败率 |
| C11 | 填充边界：根本不在iframe里做autofill | s1，源文件第 247 行 | source-report | 这一句点名的 Chrome、Brave、Firefox、Safari | 不覆盖下一行的 DuckDuckGo |
| C12 | 同域复制失败：从父级frame复制指纹值以保持同域一致性 | s1，源文件第 256 行 | source-report | 来源点名的 Firefox 扩展沙箱 | 不写对比步骤；补丁未复测 |

<a id="decision-flow"></a>
## 该跟父级比，还是跟顶级页面比

四项能力（请求拦截、资源替换、scriptlet、样式过滤）不是同一个 bug。有的工具根本不在 local frame 里跑规则，有的把第三方判成第一方，有的只是注入比页面慢。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 父级才是比较对象：而不是对比直接父级 | s1，源文件第 81 行 | source-report | 来源对 Safari party-ness 的归类 | 不是所有工具 |
| C6 | 修复口径：向上遍历父级找到第一个非local的ancestor document，用它的URL来确定origin。 | s1，源文件第 216 行 | source-report | 来源所述 AdGuard 最终方案 | 没有回归步骤 |
| C7 | 一个标志盖不住两种能力：两者的origin获取走的是不同代码路径 | s1，源文件第 215 行 | source-report | scriptlet 与 cosmetic filter | 标志名在上一行 |
| C8 | 竞态不是算错 origin：问题不在origin计算逻辑，而在浏览器扩展的生命周期管理 | s1，源文件第 199 行 | source-report | 来源所说的 Chrome 上 uBlock Origin | 注入成功时来源称 scriptlet 是对的 |
| C9 | 替代路径：这个代码路径里origin计算是错的 | s1，源文件第 191 行 | source-report | 来源所说的 Brave iOS 四项能力 | 后文有修复日期，未复测 |
| C10 | 测量代码同样会错：5篇全部没有正确处理local frame的origin | s1，源文件第 226 行 | source-report | 7 篇里提供了代码或工具的 5 篇 | 不是全文献审计 |

## 验证与限制

`iframe` 已有卡片只建模子 realm 的 window、document 和 storage，不判断内容拦截器把 about:blank 算成无主 origin 还是第一方。`browser-fingerprint` 只讲宿主对象怎么组成指纹，没有这四项拦截能力，也没有祖先遍历。`local-frame` 与 `content-blocker` 查询没有卡片。

73.7%、14.3% 和“超过一半”都保持 source-report。Table 6 的修复日期不升成当前版本已修好。来源写明不能判断站点是有意还是无意，breakage 只看了 50 个网站，而且只测了 about:blank。密码管理器一节的“全部安全”只沿用 C11 这一句的四个浏览器。反指纹一节只保留同域复制被沙箱拦住，不收录“拿主页面和 local frame 对照即可识别扩展”。第八节给投放和反爬的用法不进入本卡。
