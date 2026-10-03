---
schema_version: 2
id: app-webview-js-login-locator
document_type: reference
original_date: "2020-09-30"
archived_date: "2026-10-02"
scope:
  targets: [app-webview-js-login]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./yuanrenxue-app-20200930-01.md#app-中的-js-加密逆向解析"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只记录来源点名的检测方法和常见加密 hook 没有命中密码。脚本不收录，类名在来源里是占位。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: D 与 sha1 的对照、以及 c 的字符表都在截图里。这里只保留正文写明的关系，不重建加密函数。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 调用栈和 login.js 路径没有地址。改包失败和资源重下是来源陈述，本轮未安装样本。
relations:
  - type: derived_from
    target: "./yuanrenxue-app-20200930-01.md#app-中的-js-加密逆向解析"
tags: [javascriptinterface, sha1]
---

# App 登录加密落在 JS 而不是 Java 加密类

这张卡只回答一个检索问题：当常见 Java 加密 hook 看不到口令时，来源如何把登录加密追到 JS，以及哪些正文事实还能复用。不收录 hook 脚本，也不给出 c 的码表。

<a id="risk-control"></a>
## 进入前的检测和没命中的加密类

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源把安全检测写到 initCheckSafe，并说把该方法置空。quote: 直接把 initCheckSafe 方法置空 | s1 ./yuanrenxue-app-20200930-01.md:47 | source-report | 来源这个未点名 App 的进入检查 | 类名是占位，脚本不收录 |
| C2 | 常见加密类被 hook 到之后，日志里仍搜不到口令和抓包密文。quote: 都一无所获 | s1 ./yuanrenxue-app-20200930-01.md:86 | source-report | 来源先试的 Java 加密类 | 没有类名列表 |

<a id="parameters"></a>
## 登录体和 JS 侧的两段变换

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C3 | 请求体形式被写成 action 加 json。quote: action=xxxx&data=json | s1 ./yuanrenxue-app-20200930-01.md:63 | source-report | 来源抓到的登录请求 | action 的具体值未写出 |
| C4 | 口令字段跨次不变，其它参数来源说可以写死。quote: 其他的参数都可以写死 | s1 ./yuanrenxue-app-20200930-01.md:67 | source-report | 来源多次抓包的比较 | 没有字段清单 |
| C5 | exec 头部有 JavascriptInterface。quote: @JavascriptInterface | s1 ./yuanrenxue-app-20200930-01.md:128 | source-report | 来源追到的 Java 入口 | 未看注解实现 |
| C6 | 来源据此把加密放在 JS，再由 JS 调用 exec。quote: 加密是在js中进行的 | s1 ./yuanrenxue-app-20200930-01.md:134 | source-report | 这条登录链 | 不是所有接口 |
| C7 | 用来在 JS 里搜索的字符串包含 cbPassInfo 和 setOfflineCache。quote: cbPassInfo setOfflineCache | s1 ./yuanrenxue-app-20200930-01.md:136 | source-report | 反编译包内的 JS | 改 cbPassInfo 后来源说没有生效 |
| C8 | 函数 D 被写成和 sha1 有关。quote: 发现D应该和 sha1 有关系 | s1 ./yuanrenxue-app-20200930-01.md:170 | source-report | 来源点名的 D | 对照图未进入正文 |
| C9 | 来源写对照结果相同，并写剩下的 base64 不是标准实现。quote: 发现和上面结果相同。那就只剩base64这个函数了。看打印出来的代码，发现这不是一个标准的base64 | s1 ./yuanrenxue-app-20200930-01.md:184 | source-report | 来源打印出的 D 和 base64 | 码表未进入正文 |
| C10 | 单独运行该函数会缺变量 c。quote: 缺少 c 变量 | s1 ./yuanrenxue-app-20200930-01.md:184 | source-report | 与 C9 同一函数 | c 的值不抄录 |
| C17 | c 的定义被写在 common.js。quote: common.js | s1 ./yuanrenxue-app-20200930-01.md:186 | source-report | 来源搜索函数体之后 | 不抄录 c 的值 |

<a id="decision-flow"></a>
## 从 exec 到模拟器里的 login.js

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C11 | 调用栈底部的入参来自 exec。quote: 从 exec 这个函数的参数传来的 | s1 ./yuanrenxue-app-20200930-01.md:114 | source-report | 来源过滤 java 和 proxy 之后的栈 | 栈本身在图里 |
| C12 | 来源曾改包内 cbPassInfo 后重签，用来检验是不是调用点。quote: 重新打包签名apk | s1 ./yuanrenxue-app-20200930-01.md:146 | source-report | 这一次反证 | 随后抓包仍是原字符串 |
| C13 | 来源把改包无效解释为更新资源时重新下载了文件。quote: 难道它又重新下载了这个文件 | s1 ./yuanrenxue-app-20200930-01.md:152 | source-report | 带资源更新提示的这次安装 | 下载 URL 未写出 |
| C14 | 接下来改为在模拟器里搜 login.js。quote: 直接在模拟器中搜索login.js | s1 ./yuanrenxue-app-20200930-01.md:158 | source-report | 来源说改名后登录界面消失的那份 | 没有文件路径 |
| C15 | 来源写按 JS 实现后的结果与抓包一致。quote: 结果和抓包一致 | s1 ./yuanrenxue-app-20200930-01.md:190 | source-report | 作者的收工句 | 密文在图里，本轮未对照 |
| C16 | 来源把这次和以往 Java 或 so 加密区分开。quote: 在js中的这是第一次遇到 | s1 ./yuanrenxue-app-20200930-01.md:196 | source-report | 作者自己的样本范围 | 不能外推到其它 App |

## 验证与限制

`kb_catalog.py query` 对 app-webview-js-login 的 parameters、decision-flow、risk-control 都是 0。HashMap 的 hook 正文不收录。微信课程链接的查询串未写入本卡。没有本地运行证据。
