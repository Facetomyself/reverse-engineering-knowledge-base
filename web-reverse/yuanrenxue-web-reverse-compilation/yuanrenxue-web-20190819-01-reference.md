---
schema_version: 2
id: web-js-antibot-four-patterns
document_type: reference
original_date: '2019-08-19'
archived_date: '2026-10-02'
scope:
  targets:
    - js-anti-bot-patterns
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./yuanrenxue-web-20190819-01.md#js逆向方法论-反爬虫的四种常见方式"
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 四种对策都是来源的分类，不是实测通过的步骤。反调试没有函数名。改一个字母仍得到正文时，来源没有说该参数还算不算加密参数。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 521 只说明第一次是 JS、第二次是 HTML，并称 cookie 不是第一次响应发来的。不收录 cookie 名。cl.gif 的参数列表不在正文里。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 服务端是否核对，只保留来源的说法。本次没有请求，不能把来源的“认为合法”写成已验证的拦截结果。
relations:
  - type: derived_from
    target: "./yuanrenxue-web-20190819-01.md#js逆向方法论-反爬虫的四种常见方式"
tags:
  - js-anti-bot
  - source-report
---

# JS 反爬四种现象及来源给出的对策

这张卡只回答：2019-08-19 这篇如何把 JS 反爬分成四类，每一类的对策句子是什么，以及点击链路和来源所谓的认可条件怎样分开记。它不把四类收成一条可执行流程。

cookie 名、eval 改写和解释器分叉不在本篇，不要把本卡当成 clearance 案例。

<a id="decision-flow"></a>
## 四种对策

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 页面返回 JS 而不是 HTML 时，对策是研究那段 JS，找到生成 cookie 的算法 | s1，JS 写 cookie | source-report | 来源描述的这类页面 | 没有算法，也没有 cookie 名 |
| C2 | 无意义参数是否重要，来源用把该参数随便改一个字母再访问来判断 | s1，JS 加密 ajax 参数 | source-report | 来源所说的那类 URL | 没有样例 URL 或参数名。改完仍成功时没有下一跳 |
| C3 | 找加密算法的关键被写成在 Chrome 里设置 XHR/fetch Breakpoints | s1，同一节对策 | source-report | Chrome 调试 | 没有断点 URL 片段 |
| C4 | 反调试对策是通过 Call Stack 找到带入死循环的函数并重新定义它 | s1，JS 反调试 | source-report | 来源描述的 debugger 循环 | 函数名不在正文 |
| C5 | 同一行先把陷阱函数举例为重新定义成空函数，再写在调用处下断点、刷新到函数运行前、在 Console 重新定义后继续运行以跳过陷阱 | s1，JS 反调试后文 | source-report | 已经停在该陷阱里的那次调试 | 未复现。函数名不在正文。重定义不生效时没有出口 |
| C6 | cl.gif 这类点击校验，来源称几乎不用研究 JS，访问链接前先访问 cl.gif，并把参数带上；同时提醒 JS 可能改被点击的链接 | s1，鼠标点击事件 | source-report | 来源描述的这类点击 | 参数表不在正文。“万事大吉”不是验收 |

<a id="request-chain"></a>
## 两次文档请求，以及点击前的 cl.gif

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | 来源称浏览器运行 JS 生成一个或多个 cookie，再带着 cookie 做二次请求 | s1，JS 写 cookie | source-report | 这类页面的来源模型 | 没有具体请求 |
| C14 | 示例第一次打开 index.html 时返回的是 521 | s1，同一节的 Network 说明 | source-report | 来源附图对应的那次加载 | 这一行停在逗号，内容是 JS 写在下一行。未重放 |
| C8 | 下一行写内容是一段 JS；第二次得到正常 HTML；这次的 cookie 不是第一次请求时服务器发过来的，来源称其实就是 JS 生成的 | s1，同一节的下一行 | source-report | 来源附图对应的那次加载 | 图本身没有文字请求。未重放 |
| C9 | 点击链接前先访问 cl.gif，把当前页面信息发给服务器，然后再打开链接 | s1，点击事件的逻辑梳理 | source-report | 来源描述的这条点击链 | 参数键名不在正文 |

<a id="risk-control"></a>
## 来源所说的认可条件

这里只记录来源如何描述服务器的判断。basis 保持 source-report，不把这些句子当成当前服务端行为。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C10 | 来源称服务器收到这个 cookie 就认为访问是浏览器过来的合法访问 | s1，JS 写 cookie | source-report | 来源的说法 | 未请求 |
| C11 | 来源称服务器用同样的算法验证加密参数，通过了才认为请求来自浏览器 | s1，ajax 参数 | source-report | 来源的说法 | 算法未给出 |
| C12 | 来源称如果之前已经通过 cl.gif 把对应信息发来，就认为是合法的浏览器访问并给出正常网页 | s1，点击事件的逻辑梳理 | source-report | 来源的说法 | 未请求 |
| C13 | 来源称 requests 没有鼠标事件、因此没有 cl.gif，直接访问链接会被服务器拒绝 | s1，同一节的下一句 | source-report | 来源对 requests 的解释 | 未请求。不是已记录的状态码 |

## 验证与限制

四类没有共用的验收，也没有“断点没停住、重定义无效、cl.gif 参数对不上”时的出口。反调试段最接近步骤，仍然缺这些出口，所以整篇不建流程。

结尾只重复攻防不会结束，并带一张交流图。没有新的模块事实。
