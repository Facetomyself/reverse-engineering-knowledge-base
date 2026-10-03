---
schema_version: 2
id: grok-benru-anti-20260208-stealth-js
document_type: reference
original_date: '2026-02-08'
archived_date: '2026-10-02'
scope:
  targets: [stealth-js]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./benru-anti-20260208-01.md#指纹检测爬虫工程师的噩梦"
    basis: source-report
  - id: s2
    ref: "./benru-anti-20260208-01.md#方案一playwright--stealthjs补丁"
    basis: source-report
  - id: s3
    ref: "./benru-anti-20260208-01.md#方案二selenium--cdp直接调用"
    basis: source-report
  - id: s4
    ref: "./benru-anti-20260208-01.md#方案三pyppeteer的天然集成"
    basis: source-report
  - id: s5
    ref: "./benru-anti-20260208-01.md#1-补丁加载时机至关重要"
    basis: source-report
  - id: s6
    ref: "./benru-anti-20260208-01.md#3-定期更新stealthjs补丁"
    basis: source-report
  - id: s7
    ref: "./benru-anti-20260208-01.md#4-验证反检测效果"
    basis: source-report
  - id: s8
    ref: "./benru-anti-20260208-01.md#stealthjs从nodejs世界传来的火种"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1, s8]
    basis: source-report
    limits: 只保留作者点名的指纹类别和 stealth.js 的目标句。检测是否仍成立、以及代理是否无效，都没有本次运行证据。
  - name: interfaces
    anchor: interfaces
    sources: [s2, s3, s4]
    basis: source-report
    limits: 只记录三个注入入口的函数名。Playwright 示例里的 stealth 正文是注释占位，Selenium 示例只演示从本地文件读入，本卡不补脚本正文。
  - name: parameters
    anchor: parameters
    sources: [s2, s3]
    basis: source-report
    limits: 只保留作者写出的 webdriver 取值和三项 Chrome 启动参数。按站点改硬件或时区的示例没有闭合派发，且不转写那些赋值。
  - name: decision-flow
    anchor: decision-flow
    sources: [s5, s6]
    basis: source-report
    limits: 补丁必须先于导航，以及 2-4 周更新，都是作者建议。没有版本对照，也没有失败后的回退步骤。
  - name: validation
    anchor: validation
    sources: [s7]
    basis: source-report
    limits: 作者只要求打开三个检测页并截图。没有判定规则、阈值或失败出口，不能把截图当成通过。
relations:
  - type: derived_from
    target: "./benru-anti-20260208-01.md#你的selenium又被识别了-可能是没用对stealthjs反检测技术"
tags: [stealth-js, playwright, selenium, pyppeteer, source-report]
---

# stealth.js 的 Python 注入面

这张卡只回答：作者把 stealth 补丁接到 Playwright、Selenium、Pyppeteer 的哪个调用上，点了哪些启动参数，以及补丁和导航谁先谁后。来源是公众号转写，stealth 脚本正文不在文中。依据停在 `source-report`。近邻 `51job` 风控卡是另一个目标，不覆盖这里的注入面。

<a id="risk-control"></a>
## 风控面

作者把浏览器指纹写成爬虫要面对的日常检测，并认为多项特征合在一起时，换代理 IP 仍会被认成同一个脚本。stealth.js 被写成 Puppeteer 一侧的补丁，目标是让自动化浏览器看起来像真人浏览器。文中列举的特征名没有采样值。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | “浏览器指纹”不再是科幻概念，而是每个爬虫工程师必须面对的日常挑战。 | s1 ./benru-anti-20260208-01.md:41 | source-report | stealth-js | 作者定性，没有检测清单的当前有效性 |
| C2 | 即使使用代理IP轮换，服务器也能轻易识别：“嘿，又是那个脚本！” | s1 ./benru-anti-20260208-01.md:59 | source-report | stealth-js | 未复现，不能外推到具体站点 |
| C3 | 让自动化浏览器看起来像真人浏览器 | s8 ./benru-anti-20260208-01.md:63 | source-report | stealth-js | 目标句，不是实现 |

<a id="interfaces"></a>
## 注入入口

三个方案都是在打开目标页之前把脚本塞进新文档。Playwright 同时写了 `page.add_init_script` 和 CDP `Page.addScriptToEvaluateOnNewDocument`。Selenium 用 `execute_cdp_cmd` 调同一个 CDP 方法。Pyppeteer 走 `pyppeteer_stealth.stealth`。Playwright 代码块里的 stealth 正文只有注释，不能当成可执行补丁。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | page.add_init_script(stealth_js) | s2 ./benru-anti-20260208-01.md:106 | source-report | Playwright | stealth_js 变量的正文是占位注释 |
| C5 | Page.addScriptToEvaluateOnNewDocument | s2 ./benru-anti-20260208-01.md:110 | source-report | Playwright CDP | 只定位命令名 |
| C6 | Page.addScriptToEvaluateOnNewDocument | s3 ./benru-anti-20260208-01.md:144 | source-report | Selenium CDP | 脚本来自未附带的本地 stealth.min.js |
| C7 | from pyppeteer_stealth import stealth  # 专门为pyppeteer封装的stealth包 | s4 ./benru-anti-20260208-01.md:176 | source-report | Pyppeteer | 未核对包版本 |
| C8 | await stealth(page) | s4 ./benru-anti-20260208-01.md:183 | source-report | Pyppeteer | 调用点，没有参数表 |

<a id="parameters"></a>
## 启动参数

作者在 Selenium 路径里把 `navigator.webdriver` 的 getter 写成 `undefined`，并给了三项 Chrome 选项。这是作者写出的参数，不是一份指纹采样。后文按站点改权限、硬件并发和时区的片段没有派发代码，本卡不收录那些赋值。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C9 | get: () => undefined | s2 ./benru-anti-20260208-01.md:100 | source-report | navigator.webdriver | 示例赋值，不是测到的原值 |
| C10 | chrome_options.add_argument("--disable-blink-features=AutomationControlled") | s3 ./benru-anti-20260208-01.md:157 | source-report | Chrome 启动参数 | 未验证该开关仍有效 |
| C11 | chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) | s3 ./benru-anti-20260208-01.md:158 | source-report | Chrome 实验选项 | 同上 |
| C12 | chrome_options.add_experimental_option('useAutomationExtension', False) | s3 ./benru-anti-20260208-01.md:159 | source-report | Chrome 实验选项 | 同上 |

<a id="decision-flow"></a>
## 时序与更新

错误示例是先 `driver.get` 再打补丁，作者标明太晚。正确示例是先打补丁再访问。另建议每 2-4 周更换 stealth.js，并点名一个 GitHub raw 路径和 npm 包名作为来源，没有锁定 commit。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C13 | apply_stealth_patch(driver)  # 后应用补丁 → 太晚了！ | s5 ./benru-anti-20260208-01.md:201 | source-report | 补丁时序 | 只否定“先导航后补丁”，没有别的失败出口 |
| C14 | apply_stealth_patch(driver)  # 先应用补丁 | s5 ./benru-anti-20260208-01.md:205 | source-report | 补丁时序 | 函数体不在来源中 |
| C15 | driver.get(url)  # 后访问页面 | s5 ./benru-anti-20260208-01.md:206 | source-report | 补丁时序 | url 未给出 |
| C16 | 我建议每2-4周更新一次stealth.js版本： | s6 ./benru-anti-20260208-01.md:251 | source-report | 更新周期 | 作者建议，没有版本差异 |

<a id="validation"></a>
## 作者的检测页

作者要求部署前打开三个公开检测页并按主机名截图。没有写哪一项变绿才算通过，也没有失败后停止或回退的步骤。因此不能升成流程卡。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C17 | 部署前务必在检测网站验证： | s7 ./benru-anti-20260208-01.md:263 | source-report | 作者自述的验证动作 | 没有通过条件 |
| C18 | https://bot.sannysoft.com | s7 ./benru-anti-20260208-01.md:268 | source-report | 检测页名单 | 只是名单项 |
| C19 | https://arh.antoinevastel.com/bots/areyouheadless | s7 ./benru-anti-20260208-01.md:269 | source-report | 检测页名单 | 只是名单项 |
| C20 | https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html | s7 ./benru-anti-20260208-01.md:270 | source-report | 检测页名单 | 只是名单项 |

## 验证与限制

来源没有附带 stealth.min.js 正文，组合示例里的随机 UA 函数也没有定义。性能节的 15%–20% 开销是作者写的“典型结果”，不是本次测量。未来展望只点名 Playwright 原生 stealth、Undetected ChromeDriver 和自改 Chromium，没有步骤。本卡不补这些缺口。
