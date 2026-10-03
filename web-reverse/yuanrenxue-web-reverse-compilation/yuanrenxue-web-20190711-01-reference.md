---
schema_version: 2
id: web-jsl-clearance-521-chain
document_type: reference
original_date: '2019-07-11'
archived_date: '2026-10-02'
scope:
  targets:
    - jsl-clearance
    - mps.gov.cn
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./yuanrenxue-web-20190711-01.md#写爬虫免不了要研究javascript设置cookies的问题"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只有来源写出的这一个页面路径。未重放，不能推断该路径今天的状态码。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 第二次多出的 cookie 被写成“有可能”由 521 的 JS 写入。1.5 秒来自来源对后文脚本的转述，脚本正文不在本篇文字里。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留 cookie 名。来源没有 cookie 值，本卡也不写值。生成函数只有“又是一段加密算法”，没有函数体。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: eval 改写和 ExecJS、PyV8 都是来源建议。本次未运行。留言讨论不是失败出口。
relations:
  - type: derived_from
    target: "./yuanrenxue-web-20190711-01.md#写爬虫免不了要研究javascript设置cookies的问题"
tags:
  - jsl-clearance
  - source-report
---

# 521 页面里来源点名的 clearance cookie

这张卡只回答三件事：来源用哪个页面观察 521，第二次加载和 cookie 差在哪里，以及内层脚本读不懂时来源改走哪条执行方式。它不提供 cookie 值，也不提供生成代码。

瑞数 RS6 的请求链是另一个目标。这篇没有写瑞数或 rs6。

<a id="interfaces"></a>
## 来源打开的页面

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 重新打开的网址原文是 http://www.mps.gov.cn/n2253534/n2253535/index.html | s1，删除 cookie 之后的 Network 段 | source-report | 2019-07-11 这篇案例 | 未重放 |

<a id="request-chain"></a>
## 521 之后的第二次加载

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C10 | 来源称浏览器打开正常，用 requests 下载同一 URL 得到 521，内容是压缩混淆的 JavaScript | s1，案例开头 | source-report | 这篇点名的那个网页 | 未重放。压缩脚本只在后文截图 |
| C2 | 第一次返回 521，停顿被写成实际上是 1.5 秒，再次加载得到正确网页内容 | s1，Network 观察 | source-report | 该次浏览器记录 | 1.5 秒的脚本依据不在正文。未重放 |
| C3 | 第二次请求多了些 cookies，来源用“有可能”把它们归于 521 时返回的 JS | s1，两次请求对比 | source-report | 该次对比 | 不是已定位的 Set-Cookie 字段，只是来源的可能判断 |

<a id="parameters"></a>
## 内层脚本里的 cookie 名

格式化后的内层脚本不在正文里，只在截图。文字只点了赋值位置和名字。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 来源称第 4 行给 document.cookie 赋值，名字是 __jsl_clearance | s1，内层脚本说明 | source-report | 来源看到的那份内层脚本 | 没有 cookie 值。行号属于格式化后的截图，本文不能复核 |
| C5 | 生成被说成和第 4 行最后那个 function 有关，看起来又是一段加密算法 | s1，同一段说明的下一行 | source-report | 来源的读法 | 函数体不在文字里，不能当成已还原算法 |

<a id="decision-flow"></a>
## 暴露脚本，以及读不懂时的分叉

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 观察前要在站点数据里搜索 mps.gov 并删除该站 cookies | s1，Chrome 设置段 | source-report | 来源的观察步骤 | 只说明要清掉已记住的 cookie，不涉及读取他人 cookie |
| C7 | 外层第 16 行要 eval() 一段 JS 代码字符串，来源接着写把 eval 改成 | s1，格式化之后 | source-report | 这份外层脚本 | 字符串内容不在正文。替换后的调用写在下一行 |
| C11 | 紧接着的一行从 console.log 写起，并要求把全部 JS 复制到 Chrome Console 运行 | s1，同一段的下一行 | source-report | 来源的改写建议 | 上一行才写到把 eval 改成。未运行 |
| C12 | 格式化工具被写成 beautifier.io | s1，研究脚本之前 | source-report | 来源选用的网页工具 | 不是脚本位置 |
| C8 | 来源写可以借助 ExecJS 或 PyV8 运行这段 JS，同样得到 cookie 的值 | s1，解释器替代 | source-report | 来源的替代建议 | 未运行。没有写出用哪一段 JS |
| C9 | 有了 cookie 的值之后，来源在 Python 里面使用 requests.Session | s1，收尾 | source-report | 来源的下一步 | 没有会话代码，也没有写出怎样带上 cookie |

## 验证与限制

来源把“可以得到正确的网页内容”当作观察结果，但没有定义失败时停止还是换路线。文末只说遇到问题可以留言。缺失败出口，不建流程。

微信广告段没有技术事实。留言讨论不能当成失败出口。
