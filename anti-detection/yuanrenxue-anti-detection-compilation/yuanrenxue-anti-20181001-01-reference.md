---
schema_version: 2
id: yuanrenxue-browsercookie-loader-reference
document_type: reference
original_date: '2018-10-01'
archived_date: '2026-10-02'
scope:
  targets:
    - browsercookie
  client: python
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./yuanrenxue-anti-20181001-01.md#安装"
    basis: source-report
  - id: s2
    ref: "./yuanrenxue-anti-20181001-01.md#使用方法"
    basis: source-report
  - id: s3
    ref: "./yuanrenxue-anti-20181001-01.md#支持"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2, s3]
    basis: source-report
    limits: 只保留三个加载函数、cookiejar 交给谁，以及来源点名的平台。未运行，不记录 jar 内容。Windows 的 sqlite 处理只有一句另装 pysqlite。
  - name: decision-flow
    anchor: decision-flow
    sources: [s2]
    basis: source-report
    limits: 只保留「知道浏览器就点名入口，不知道就 load」这一支。没有搜索顺序，也没有多个浏览器同时命中时的规则。
relations:
  - type: derived_from
    target: "./yuanrenxue-anti-20181001-01.md#python爬虫使用浏览器的cookiesbrowsercookie"
tags:
  - browsercookie
  - cookiejar
  - source-report
---

# browsercookie 的三个加载入口

这张卡只回答：2018 年这篇教程把哪个函数当成 Firefox、Chrome 和「不确定浏览器」的入口，返回的 cookiejar 交给哪个标准库或 requests 参数，以及它自己划了哪些平台。不记录 cookie 内容，也不把示例页标题当成通用验收。

Web 宿主上的 cookie 检测面、以及 Chromium 启动期的 CookieManager，是别的目标，这里不覆盖。

<a id="interfaces"></a>
## 加载入口与平台

来源把库定义成：把浏览器已经保存的 cookies 装进一个 cookiejar，再去取需要登录的页面。安装句只有 `pip install browsercookie`。没有库版本。

三个入口：

| 来源入口 | 来源怎么用返回值 | 来源附加的条件 |
|---|---|---|
| `browsercookie.firefox()` | Python 2 放进 `urllib2.HTTPCookieProcessor`；后文 Python 3 改用 `urllib.request` 的同名处理器 | 示例写的是已经登录过的 Firefox |
| `browsercookie.chrome()` | 作为 requests 的 cookies 参数 | 示例写要事先用 Chrome 登录 |
| `browsercookie.load()` | 同样交给 requests 的 cookies 参数 | 不知道或不关心是哪个浏览器 |

> 通过加载你浏览器的cookies到一个cookiejar对象里面

> cj = browsercookie.firefox()

> cj = browsercookie.chrome()

Windows 上，来源写内置 sqlite 加载 Firefox 数据库会抛错，需要另装 pysqlite。没有错误原文。

平台只列了两行：Chrome 与 Firefox，各自是 Linux、OSX、Windows。作者同时写测试过的浏览器版本不多。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 通过加载你浏览器的cookies到一个cookiejar对象里面 | s2 ./yuanrenxue-anti-20181001-01.md:40 | source-report | browsercookie | 不记录 jar 内容 |
| C2 | 内置的sqlite模块在加载FireFox数据库时会抛出错误 | s1 ./yuanrenxue-anti-20181001-01.md:46 | source-report | browsercookie | 只点名 pysqlite |
| C3 | cj = browsercookie.firefox() | s2 ./yuanrenxue-anti-20181001-01.md:67 | source-report | browsercookie | 下一行交给 HTTPCookieProcessor；Python 3 示例改用 urllib.request |
| C5 | Firefox: Linux, OSX, Windows | s3 ./yuanrenxue-anti-20181001-01.md:101 | source-report | browsercookie | 上一行是 Chrome 的同一组系统；作者写版本覆盖不多 |

<a id="decision-flow"></a>
## 选哪个入口

来源的分支只有一句：如果不知道或不关心哪个浏览器里有需要的 cookies，就调用 `browsercookie.load()`，而不先调用 `firefox()` 或 `chrome()`。它没有写 load 先看哪一个浏览器，也没有写两边都有 cookies 时留下哪一边。

> 如果你不知道或不关心那个浏览器有你需要的cookies，你可以这样操作：

> cj = browsercookie.load()

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 如果你不知道或不关心那个浏览器有你需要的cookies | s2 ./yuanrenxue-anti-20181001-01.md:89 | source-report | browsercookie | 紧接着的调用是 browsercookie.load()；没有搜索顺序 |

## 验证与限制

- 作者用示例页标题里出现用户名，说明 Firefox 那一次加载成功。这是 source-report，不是通用验收，本卡不转写该标题。
- 空 jar、数据库被锁、cookies 过期，文中都没有行为。
- 文末只说遇到问题可以向作者提交，并给了项目页。这不是失败出口。
- 未运行。不记录 cookie 原值。
