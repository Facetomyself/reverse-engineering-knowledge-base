---
schema_version: 2
id: unnamed-book-site-login-chain
document_type: reference
original_date: "2020-09-08"
archived_date: "2026-10-02"
scope:
  targets: [unnamed-book-site-login]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./yuanrenxue-app-20200908-01.md#某书新版登录流程逆向分析"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 站点名未写出。某数生成和最终数据解密来源说不再赘述。公钥、密文和 cookie 值都在图里，这里只保留字段名和检索标记。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 请求体、响应体在截图中，正文没有 URL 主机。顺序是来源陈述，本轮未发请求。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 手机号、邮箱、匿名和 202 都是来源用的判定，不是本轮观察到的响应。
relations:
  - type: derived_from
    target: "./yuanrenxue-app-20200908-01.md#某书新版登录流程逆向分析"
tags: [login, jsencrypt]
---

# 未点名站点的登录链与字段

这张卡只回答一个检索问题：这篇归档把未点名站点的登录分成哪几跳，密码和数据接口各自依赖哪些能在正文里定位的字段。不提供某数脚本，也不提供数据解密。

<a id="parameters"></a>
## 登录和数据接口上的字段

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源写这个站的 cookie 不需要接后缀。quote: cookie是不需要接后缀的 | s1 ./yuanrenxue-app-20200908-01.md:45 | source-report | 来源所称的某数 4 代站点 | 没有 cookie 名和值 |
| C2 | 来源写 217 位 cookie 就能访问。quote: 只要217位的cookie就能够正常 | s1 ./yuanrenxue-app-20200908-01.md:45 | source-report | 同一句里的长度说法 | 未核对真实长度 |
| C3 | 密码加密被写成扣下 JSEncrypt。quote: 扣下JSEncrypt | s1 ./yuanrenxue-app-20200908-01.md:63 | source-report | 登录前的密码字段 | 函数体在图里 |
| C4 | 来源补的环境只有 Netscape 这个 appName。quote: navigator = { appName: 'Netscape'} | s1 ./yuanrenxue-app-20200908-01.md:65 | source-report | 来源说缺环境时补的一行 | 未运行 |
| C5 | 来源给的函数入口检索标记是 AAOCAQ。quote: AAOCAQ | s1 ./yuanrenxue-app-20200908-01.md:77 | source-report | 不想单步时的搜索词 | 不是密钥 |
| C6 | 登录接口返回的 set-cookie 名被写成 HOLDONKEY。quote: set-cookie HOLDONKEY | s1 ./yuanrenxue-app-20200908-01.md:115 | source-report | api/login 的响应 | 没有 cookie 值 |
| C7 | authorize 的查询参数里点了 client_id。quote: client_id | s1 ./yuanrenxue-app-20200908-01.md:117 | source-report | 登录后的 authorize | 同行还有 redirect_uri、response_type、scope，值不在正文 |
| C8 | authorize 被写成 302 到 CallBackController。quote: CallBackController | s1 ./yuanrenxue-app-20200908-01.md:118 | source-report | 来源的跳转说法 | 未看响应头 |
| C9 | 数据接口缺一不可的三个名字是 pageId、cfg、__RequestVerificationToken。quote: pageId cfg __RequestVerificationToken | s1 ./yuanrenxue-app-20200908-01.md:128 | source-report | /website/parse/rest.q4w | 没有字段值 |
| C10 | pid 和 token 要与用户信息请求一致。quote: pid和token需和请求用户信息的数据保持一致 | s1 ./yuanrenxue-app-20200908-01.md:107 | source-report | 数据接口相对用户信息接口 | 两个值都未给出 |
| C11 | 第二次数据请求的查询参数例子是 ciphertext。quote: ciphertext | s1 ./yuanrenxue-app-20200908-01.md:132 | source-report | 同一数据接口的后续查询 | 解密不在本文 |
| C12 | 来源写数据接口检查的是 data 里的 cfg，并且不需要后缀。quote: 数据api检测的是data中cfg | s1 ./yuanrenxue-app-20200908-01.md:136 | source-report | 来源对改版后的收束 | 与 RS6 动态后缀不是同一条规则 |

<a id="request-chain"></a>
## 从 202 到数据接口

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C13 | 来源把第一次写成 202、第二次写成 200。quote: 第一次202，第二次200 | s1 ./yuanrenxue-app-20200908-01.md:45 | source-report | 登录页的前两跳 | 未复现状态码 |
| C14 | 第二次请求只为保住 session。quote: 再请求一次该页面，此步骤只有一个目的，session保持 | s1 ./yuanrenxue-app-20200908-01.md:51 | source-report | 处理第一次 content 和 js 之后 | 某数算法不在本文 |
| C15 | 密码加密之后才请求登录 api。quote: 然后请求登录api | s1 ./yuanrenxue-app-20200908-01.md:67 | source-report | 来源称登录成功的那一跳 | 成功是作者自述 |
| C16 | 登录后再请求 tongyilogin，用 session 访问它返回的 url。quote: tongyilogin | s1 ./yuanrenxue-app-20200908-01.md:85 | source-report | 来源说的验证 api | 返回 url 在图里 |
| C17 | cookie 更新被写成再按第一次的方式生成，并带上已有某数 cookie。quote: 像第一次生成cookie那样去更新cookie | s1 ./yuanrenxue-app-20200908-01.md:93 | source-report | 来源标成可以省略的一步 | 省略后的后果见验证 |
| C18 | 个人信息以及后续数据都走 /website/parse/rest.q4w。quote: /website/parse/rest.q4w | s1 ./yuanrenxue-app-20200908-01.md:122 | source-report | 总结里的第三跳和第四跳 | 主机名未知 |

<a id="validation"></a>
## 来源用来判断成败的句子

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C19 | 用户信息里出现手机号或邮箱算验证成功，匿名用户算失败。quote: 显示手机号或者邮箱则说明验证成功，如果是匿名用户则失败 | s1 ./yuanrenxue-app-20200908-01.md:99 | source-report | 用户状态接口 | 响应在图里 |
| C20 | 三个字段缺任一，来源写会报没有权限。quote: 缺任一都会报没有权限的错误 | s1 ./yuanrenxue-app-20200908-01.md:130 | source-report | pageId、cfg、__RequestVerificationToken | 未看到错误体 |
| C21 | 不更新某数 cookie 时，来源写最后可能出现 202。quote: 可能出现202状态 | s1 ./yuanrenxue-app-20200908-01.md:91 | source-report | 来源标成可选的更新步 | 未复现 |

## 验证与限制

`kb_catalog.py query` 对 unnamed-book-site-login 的 parameters、request-chain、validation 都是 0。ruishu 的 request-chain 和 validation 命中 RS6 两张卡；那两张是动态后缀和挑战页，不是这篇写的无后缀登录字段，所以不并进去。微信课程链接的查询串未写入本卡。没有本地运行证据。
