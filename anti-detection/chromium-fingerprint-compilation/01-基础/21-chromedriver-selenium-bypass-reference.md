---
schema_version: 2
id: anti-detection-chromedriver-cdc-marker-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromedriver-cdc]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./21-chromedriver-selenium-bypass.md#一selenium简介
    basis: unknown
  - id: s2
    ref: ./21-chromedriver-selenium-bypass.md#三-检测原理
    basis: unknown
  - id: s3
    ref: ./21-chromedriver-selenium-bypass.md#二机器人识别网站
    basis: unknown
  - id: s4
    ref: ./21-chromedriver-selenium-bypass.md#四编译crhomedriverexe
    basis: unknown
  - id: s5
    ref: ./21-chromedriver-selenium-bypass.md#3编译
    basis: unknown
  - id: s6
    ref: ./21-chromedriver-selenium-bypass.md#五验证
    basis: unknown
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2]
    basis: unknown
    limits: CDP 检测被作者明确划到另一篇。这里只保留 window 属性名正则和作者对空数组 / 非空数组的对比，不转写属性名清单。
  - name: interfaces
    anchor: interfaces
    sources: [s3, s4]
    basis: unknown
    limits: 文件路径和两个检测页只按来源命名。没有当前 ChromeDriver 源码对照，也没有打开这两个页面。
  - name: parameters
    anchor: parameters
    sources: [s4, s5]
    basis: unknown
    limits: 只说明注入脚本里的赋值被注释，以及 ninja 目标是 chromedriver。不复制完整脚本、本机浏览器路径或示例种子。
  - name: validation
    anchor: validation
    sources: [s6]
    basis: unknown
    limits: 站点“检测不到”是作者自述。navigator.webdriver、驱动版本和其他自动化信号都没有在这篇闭合。
relations:
  - type: derived_from
    target: ./21-chromedriver-selenium-bypass.md#四编译crhomedriverexe
tags: [chromedriver, selenium, window-properties, unknown]
---

# Chromedriver window 属性标记

这张卡检索 Selenium 这条笔记里，作者把哪一类检测留在篇内、标记写在哪个源文件、作者怎样改注入脚本。它不重放驱动脚本，也不记录示例种子或本机路径。

<a id="risk-control"></a>
## 检测面

作者把 Selenium 机器人检测分成两类：CDP 检测，和 webdriver 特征检测。CDP 被明确写成前面的文章已经讲过，本篇只处理第二类。

篇内探针是 `Object.getOwnPropertyNames(window)`，再用正则 `/^([a-z]){3}_.*_(Array|Promise|Symbol|JSON|Object|Proxy)$/` 过滤。作者写正常浏览器打印 `[]`，被 Selenium 控制时打印匹配这个正则的属性；并称这就是 browserscan 与 BotD 检测 Selenium 的核心。pyppeteer 被写成没有中间驱动，所以作者更建议直接用它；已经有大量 Selenium 代码时才去编驱动。这是取舍说明，不是对比实验。

<a id="interfaces"></a>
## 文件与作者用的页面

注入脚本所在文件是 `\chrome\test\chromedriver\chrome\devtools_client_impl.cc`。脚本字符串经 `params.Set("source", script)` 送出。

作者点名的页面是 `https://www.browserscan.net/bot-detection` 和 `https://fingerprintjs.github.io/BotD/main/`。两张结果图本轮没有审查。

<a id="parameters"></a>
## 注入脚本的改动形态

贴出的原脚本在一个立即执行函数里给 `window` 增加一批属性，属性名符合上一节的正则，右值是对应的内建对象。作者的替换是把这些赋值行改成注释，留下空的函数体，`params.Set("source", script)` 仍在。

构建目标写成 `ninja  -C  out/Default chromedriver`，产物是 `out/Default` 下的 `chromedriver.exe`。验证段里的本机 Chrome 路径、`--no-sandbox` 和示例种子不属于这个标记合同，本卡不收录。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 篇内范围是 webdriver 特征，不是 CDP | s1，`21-chromedriver-selenium-bypass.md:24` | unknown | 作者的分类 | CDP 细节不在本篇 |
| C2 | 探针是 window 属性名上的三段式正则 | s2，`21-chromedriver-selenium-bypass.md:49` | unknown | 贴出的控制台片段 | 不转写命中的属性名 |
| C3 | 赋值位于 `devtools_client_impl.cc` 的注入脚本 | s4，`21-chromedriver-selenium-bypass.md:78` | unknown | 作者点名的这个文件 | 未对照上游版本 |
| C4 | 替换片段把赋值行改成注释 | s4，`21-chromedriver-selenium-bypass.md:100` | unknown | 贴出的替换片段 | 不复制整段脚本或属性名清单 |
| C5 | `params.Set("source", script)` 仍保留 | s4，`21-chromedriver-selenium-bypass.md:107` | unknown | 同一替换片段的发送点 | 不表示其他副本也被注释 |

<a id="validation"></a>
## 作者验收与缺口

作者用改过的 `chromedriver.exe` 打开 BotD，并称页面仍然是自动化控制，但官网已经检测不到，browserscan 也一样。这是自述，配图未审查。

未知项包括：当前驱动是否还注入固定属性名、`navigator.webdriver` 是否另有来源、CDP 检测是否仍会命中，以及注释是否覆盖了文件里其他副本。来源没有失败出口，所以这篇不能当成 procedure。
