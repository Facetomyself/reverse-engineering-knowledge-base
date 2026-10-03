---
schema_version: 2
id: login1-scrape-center-base64-token
document_type: reference
original_date: "2026-05-13"
archived_date: "2026-10-02"
scope:
  targets: [login1.scrape.center]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./benru-web-20260513-01.md#第四步一眼认出加密算法"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只记录来源写出的站点和 login 请求只有 token 字段。post 的 URL 在摘录里是省略号。未打开站点。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录 chunk、模块号、js-base64 版本和一行 encode。库实现被省略。不记录样例编码。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 搜索、断点和复制模块是来源的定位顺序。作者称本地结果与浏览器一致，本轮未运行。
relations:
  - type: derived_from
    target: "./benru-web-20260513-01.md#第四步一眼认出加密算法"
tags: [login1.scrape.center, webpack, js-base64, token]
---

# login1.scrape.center 的 token 只有一行 Base64

这张卡只回答：来源把 login1.scrape.center 的登录 token 定位到哪个 webpack 模块，以及它准备用哪句 Node 替代。不记录示例账号，也不记录样例编码。作者称两者一致，保持为来源陈述。

<a id="interfaces"></a>
## 登录请求

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源打开的目标是 https://login1.scrape.center/。quote: https://login1.scrape.center/ | s1 ./benru-web-20260513-01.md:48 | source-report | login1.scrape.center | 未复现 |
| C2 | 来源称 Login 之后有一条名为 login 的请求，载荷只有一行。quote: 你会看到一个叫  ` login  ` 的请求，Payload 就一行： | s1 ./benru-web-20260513-01.md:51 | source-report | 该次点击 | 没有方法、路径和响应 |
| C3 | 来源称这一行不是明文用户名字段，只有 token。quote: 只有一个  ` token  ` 。 | s1 ./benru-web-20260513-01.md:55 | source-report | 该条 login 请求 | 不排除其他接口 |
| C4 | 摘录里的提交是 this.$http.post 的 token 字段，URL 写成省略号。quote: this.$http.post(..., { token: e }) | s1 ./benru-web-20260513-01.md:133 | source-report | 模块 a55b 的摘录 | 路径未知 |

<a id="parameters"></a>
## webpack 模块与编码

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 来源把所在 chunk 写成 chunk-cc71364c。quote: chunk-cc71364c | s1 ./benru-web-20260513-01.md:120 | source-report | 这篇摘录 | chunk 全文未附 |
| C6 | 模块 27ae 被写成 js-base64，版本 2.5.1。quote: 版本 2.5.1 | s1 ./benru-web-20260513-01.md:141 | source-report | 模块 27ae | 实现被注释省略 |
| C7 | 模块 a55b 用 require("27ae") 取出 Base64。quote: require("27ae") | s1 ./benru-web-20260513-01.md:142 | source-report | Vue 登录组件摘录 | 只有这一行引用 |
| C8 | token 的表达式是 c.encode(JSON.stringify(this.form))。quote: c.encode(JSON.stringify(this.form)) | s1 ./benru-web-20260513-01.md:143 | source-report | 模块 a55b | 未运行 |
| C9 | 来源给出的 Node 替代是 Buffer.from(str).toString('base64')。quote: Buffer.from(str).toString('base64') | s1 ./benru-web-20260513-01.md:179 | source-report | 来源的 reverse.js 草稿 | 不记录样例编码 |

<a id="decision-flow"></a>
## 定位顺序与停止点

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C10 | 来源先在 Sources 用 Ctrl+Shift+F 搜 token。quote: Ctrl+Shift+F | s1 ./benru-web-20260513-01.md:60 | source-report | 这篇演示 | 脚本 URL 未写出 |
| C11 | 断点打在 var e = c.encode(JSON.stringify(this.form));。quote: var e = c.encode(JSON.stringify(this.form)); | s1 ./benru-web-20260513-01.md:71 | source-report | 该行 | 命中是作者叙述 |
| C12 | 断点未命中时，来源只说重新搜索或检查别的请求。quote: 如果断点没命中？那就重新搜索别的位置 | s1 ./benru-web-20260513-01.md:83 | source-report | 搜索失败 | 没有第二条接口名 |
| C13 | 来源要求确认输入输出，不要钻进那个 400 行的 Base64 实现。quote: 别钻进那个 400 行的 Base64 实现里 | s1 ./benru-web-20260513-01.md:157 | source-report | 已认出 Base64.encode 时 | 400 行是作者说法 |
| C14 | 若依赖不是 Base64，来源要求把整个 webpack 模块复制出来。quote: 把整个 webpack 模块 | s1 ./benru-web-20260513-01.md:205-206 | source-report | 自定义库 | 本例被说成不必复制，函数体未附全 |
| C15 | 作者称 node 结果和浏览器里的一模一样。quote: 得到的 token 和浏览器里的一模一样 | s1 ./benru-web-20260513-01.md:201 | source-report | 作者自述 | 本轮未运行，不能当验收 |

## 验证与限制

近邻查询里，login1.scrape.center 和 scrape.center 没有 parameters、interfaces、decision-flow 或 request-chain 卡片。147 到 155 行的 RSA、AES、MD5 关键字没有出现在这个登录里，不进入模块。POST 路径仍是省略号。作者的“一模一样”保持 source-report。
