---
schema_version: 2
id: grok-web-reverse-benru-web-20260330-01
document_type: reference
original_date: "2026-03-30"
archived_date: "2026-10-02"
scope:
  targets: [fanyideskweb]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./benru-web-20260330-01.md#二让ai帮我写解密脚本不用再手动翻译"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录来源贴出的有道网页翻译签名字段和一则 CryptoJS 示例的模式描述。未请求接口。示例里的 User-Agent 字面量不收录。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 来源承认 AI 译文的时间戳格式和随机数范围可能不对，也写明 AI 不会自动找到加密入口或绕过反爬。这不是可执行的验收流程。
relations:
  - type: derived_from
    target: "./benru-web-20260330-01.md#二让ai帮我写解密脚本不用再手动翻译"
tags: [fanyideskweb, md5, youdao]
---

# 有道网页翻译 sign 字段与 AI 译文边界

这张卡只定位来源里的 `fanyideskweb` 签名字段，以及作者自己标出的 AI 译文失败点。不把“让 AI 读混淆”收成方法，也不收录示例里的浏览器版本字面量。

<a id="parameters"></a>
## 参数机制

来源把有道网页翻译函数的返回值写成四个字段。`bv` 是 `navigator.appVersion` 的 MD5。quote: var t = n.md5(navigator.appVersion)。`ts` 是当前时间毫秒串。quote: r = "" + (new Date).getTime()。`salt` 是这个时间串再接一位随机整数。quote: i = r + parseInt(10 * Math.random(), 10)。返回对象里 `salt` 就是 `i`，`ts` 就是 `r`，`bv` 就是 `t`。quote: salt: i。quote: ts: r。quote: bv: t。

`sign` 是固定前缀、输入文本、salt 和固定后缀的 MD5。quote: sign: n.md5("fanyideskweb" + e + i + "Y2FYu%TNSbMCxc3t2u^XT")。后文用自然语言重述了同一顺序。quote: sign是"fanyideskweb" + 输入文本 + salt + 固定字符串，然后取MD5。

作者贴出的 Python 把 `ts` 写成毫秒整数再转字符串，把 salt 写成 `ts` 加 `random.randint(0, 10)`。quote: ts = str(int(time.time() * 1000))。quote: salt = ts + str(random.randint(0, 10))。所示片段使用 `word` 参与拼接，片段内没有给 `word` 赋值。示例里的 `app_version` 字面量不写入本卡；`bv` 仍只按来源记为 `appVersion` 的 MD5。

同一篇后半还有一段 CryptoJS 示例。来源转述为 AES-CBC，key 和 iv 都是 16 字节，输出是 Base64。quote: mode: CryptoJS.mode.CBC。quote: key和iv都是16字节，输出是Base64格式。key 和 iv 的示例字面量不收录。这不是有道签名的字段。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | `bv` 来自 `navigator.appVersion` 的 MD5 | s1 第 63 行 | source-report | fanyideskweb | 未取真实 appVersion |
| C2 | `ts` 是 `Date.getTime()` 的字符串，`salt` 是 `ts` 再接 `parseInt(10 * Math.random(), 10)` | s1 第 64–64 行 | source-report | 来源这段 JS | 随机数分布未抽样 |
| C3 | `sign` 为 `fanyideskweb`、输入、salt、固定后缀的 MD5 | s1 第 68 与 113 行 | source-report | 来源点名的网页翻译函数 | 未请求接口 |
| C4 | 作者的 Python 用 `randint(0, 10)` 接在毫秒串后面 | s1 第 82–82 行 | source-report | 来源贴出的片段 | `word` 在片段内无赋值 |
| C5 | CryptoJS 示例被说成 AES-CBC、16 字节 key/iv、Base64 输出 | s1 第 96 与 101 行 | source-report | 该示例函数 | 不收录 key 字面量，也不并进有道 sign |

<a id="decision-flow"></a>
## 译文不能直接当通过

作者写 AI 生成的 Python 有时时间戳格式不对、随机数范围不同，要把错误贴回去再改。quote: 随机数范围不同。JS 的 `parseInt(10 * Math.random(), 10)` 与 Python 的 `randint(0, 10)` 已经并排出现在来源里，不能把这两段写成同一分布。

作者同时写，AI 不会自动找到加密入口，也不会绕过反爬。quote: 它不会自动帮你找到加密入口，也不会绕过反爬策略。因此“基本可以直接用”只保留为作者句子，不能当成字段已对齐。

## 验证与限制

没有本地请求，也没有把 JS 与 Python 的 salt 分布对齐。自定义加密一节只写“不一定完全准确”，没有输入输出样例，不单列模块。混淆代码被 AI 解释成 `console.log("Hello World!")` 只是作者转述，不能支撑另一个反混淆模块。
