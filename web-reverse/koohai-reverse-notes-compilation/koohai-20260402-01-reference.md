---
schema_version: 2
id: web-yrx2-ob-memory-bomb
document_type: reference
original_date: '2026-04-02'
archived_date: '2026-10-02'
scope:
  targets:
    - yuanrenxue
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./koohai-20260402-01.md#反调试bypass"
    basis: source-report
  - id: s2
    ref: "./koohai-20260402-01.md#khbox-fix"
    basis: source-report
  - id: s3
    ref: "./koohai-20260402-01.md#正则爆破"
    basis: source-report
  - id: s4
    ref: "./koohai-20260402-01.md#console无限输出"
    basis: source-report
  - id: s5
    ref: "./koohai-20260402-01.md#正则检测"
    basis: source-report
  - id: s6
    ref: "./koohai-20260402-01.md#setinterval"
    basis: source-report
  - id: s7
    ref: "./koohai-20260402-01.md#先让ai还原一下"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2, s3, s4, s5, s6]
    basis: source-report
    limits: 只保留来源对 match/2 脚本里四处自述检查的描述。没有打开页面脚本，没有重跑格式化与压缩两种源码，也没有核对 Function 与 console 的当前形态。
  - name: decision-flow
    anchor: decision-flow
    sources: [s7, s1, s2, s6]
    basis: source-report
    limits: 来源选择不抽算法、只写 hook 落点。油猴脚本正文不转载。作者同时写下“有用”和框架被改崩，本次没有运行。
relations:
  - type: derived_from
    target: "./koohai-20260402-01.md#反调试bypass"
tags:
  - yuanrenxue
  - obfuscator
  - source-report
---

# yrx2 里来源点名的四处内存检查

这张卡只回答：2026-04-02 那篇 khbox 笔记把 match/2 的内存检查说成哪几种，以及作者把 hook 放在什么时机。它不提供 cookie 算法，也不转载油猴脚本。补环境对象的通用纪律仍看浏览器对象参考；那一页写明不提供具体站点配方，也没有这四处检查。

来源没有可公开定位的材料链接。正文里的 cookie 原值不进入本卡。

<a id="risk-control"></a>
## 来源点名的四处检查

油猴头里的匹配页是 `https://match.yuanrenxue.cn/match/2`。下面只保留分析节里能直接定位的检查，不把脚本注释当成已执行结果。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 正则节写明：当目标字符串（即代码函数本身）是压缩成一行的（Minified）时，正则匹配会很快失败或结束。 | s3，正则爆破 | source-report | 该节描述的自检 | 未用压缩和格式化两份源码重跑 |
| C2 | 同一节把格式化后的后果写成：如果你格式化了代码，代码中会出现大量的空格和换行符。 | s3，正则爆破 | source-report | 该节描述的自检 | 回溯次数没有测量 |
| C3 | preload 注释把替换后的模式写成 `compile("^([^ ]+( +[^ ]+)+)+[^ ]}")` | s2，khbox fix | source-report | 该注释里的陷阱描述 | 未在页面脚本里搜索这个字面量 |
| C4 | console 节写明：通过hook evla，能知道他是给console重新赋值 | s4，console无限输出 | source-report | 该节的 eval 观察 | 原文拼写就是 evla。未复现赋值 |
| C5 | toString 节写明：字符串直接无限循环while 卡死 | s5，正则检测 | source-report | 该节描述的传参分支 | 未单步 Function 构造器 |
| C6 | 紧接着写明：非字符串 就无限debugger | s5，正则检测 | source-report | 该节描述的另一分支 | 来源称不开调试器就没有影响，本次未验证 |
| C7 | 定时器节写明：已经知道了这两个里面是检测，那就直接把setInterval置空 | s6，setInterval | source-report | 该节点名的两个 setInterval | 不说明置空后页面其他定时器是否还需要 |

<a id="decision-flow"></a>
## 作者把 hook 放在哪

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 还原节写明：我们就不去直接拿算法了，去试下能否通过hook的方式，让它内存爆破失效。 | s7，先让ai还原一下 | source-report | 这篇笔记的路线选择 | 不是算法已经不存在的证据 |
| C9 | 反调试节写明：claude给了个油猴脚本。仅供参考。 | s1，反调试bypass | source-report | 该节草稿 | 脚本正文不转载，也不能当成已执行结果 |
| C10 | preload 注释写明：执行时机：jQuery 注入之后、input.js 之前 | s2，khbox fix | source-report | 作者这份 preload | 未核对 jQuery 是否必须 |
| C11 | 同一注释写明：不修改 input.js | s2，khbox fix | source-report | 作者这份 preload | 后文又说 input.js 原样放进，随后框架被改崩 |
| C12 | ReDoS 注释的处理写成：Fix：让 compile() 变成 no-op | s2，khbox fix | source-report | 作者这份 preload | 油猴草稿是换成永不匹配，两套写法没有对拍 |
| C13 | 定时器注释写明：已同步执行（有括号） | s2，khbox fix | source-report | 带括号调用后再注册的写法 | 只解释调用发生在注册之前 |
| C14 | 正则节的另一选择是：当然，我们不格式化就行 | s3，正则爆破 | source-report | 作者认为格式化才触发回溯的那段 | 未验证不格式化就一定通过 |

## 验证与限制

来源后文写过“有用”，再写框架被改崩、截图仅此一份，最后写“行了”。这些都是作者自述。本次没有运行，没有把 cookie 原值抄进来，也没有验收页面是否还使用同名检查。时间戳加密只是还原节的外观判断，不能写成已提取的参数算法。油猴脚本与 preload 是两套草稿，不能合成一条已经闭合的流程。
