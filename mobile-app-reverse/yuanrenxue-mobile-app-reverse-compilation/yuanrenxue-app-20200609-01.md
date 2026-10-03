---
schema_version: 2
id: mobile-app-reverse-yuanrenxue-mobile-app-reverse-compilation-yuanrenxue-app-20200609-01
document_type: reference
scope:
  targets:
  - anonymized iOS quotation app sign parameter
  client: iOS app
  version: 10.5.5 source report; exact build unknown
  observed_at: unknown
sources:
- id: s1
  ref: null
  basis: source-report
  citation: 微信公众号：猿人学Python
  reason: 原归档明确记载出处，但未提供可定位的公开来源链接；本轮只保留来源自述。
source_completeness: unknown
modules:
- name: parameters
  anchor: ios-sign-input-boundary
  sources: [s1]
  basis: source-report
  limits: 样本 serialid/sign 已脱敏；完整 canonicalization 与字段规范化未公开。
- name: decision-flow
  anchor: ios-cc-md5-observation
  sources: [s1]
  basis: source-report
  limits: CC_MD5 hook 对照是来源教程路线；本轮未连接设备或运行 Frida。
- name: validation
  anchor: ios-sign-acceptance-boundary
  sources: [s1]
  basis: source-report
  limits: 单样本输入/输出对应关系不等于跨版本复现或 serverAccepted。
tags: [ios, cc-md5, sign, frida-trace]
original_date: '2020-06-09'
archived_date: '2026-07-16'
---

# iOS逆向抓取-巧破某报价大全APP加密参数

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2020-06-09
> 归档日期: 2026-07-16
> 分类: mobile-app-reverse
</details>
>
> iOS作为一种闭源系统，没有Android那么多的packers和so库，iOS官方封装了自己统一的Crypto库，所以我们HOOK起来也很方便。我以某报价大全 iOS v10.5.5版为例，记录一下巧破加密参数的过程和一些知识点。 此次逆向教程使用到的工具如下：。

**一、前言**

* * *

iOS作为一种闭源系统，没有Android那么多的packers和so库，iOS官方封装了自己统一的Crypto库，所以我们HOOK起来也很方便。我以某报价大全
iOS v10.5.5版为例，记录一下巧破加密参数的过程和一些知识点。
此次逆向教程使用到的工具如下：

  * 一部越狱iPhone或iPad
  * 抓包工具：Charles
  * Hook 框架：frida v12.8.11

**二、抓包分析**

* * *

通过Charles抓取目标APP列表页请求的数据，我们发现含有32位的“sign”参数，且向下滑动加载更多时“sign”参数都会变化。两次抓包请求参数对比如下图：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfGR6VezTicMIMcV87libFaek8h3UmpwjVRibbjEiaCJRX52W37B880bW46zxaYXuJh9wYM4v9kJzX6Cw/640?wx_fmt=png)
通过对比抓包数据，我们猜测可能使用了MD5加密算法，接下来我们就用frida-
trace监控iOS系统封装的CC_MD5加密函数，看能不能巧破该APP的“sign”参数。
**三、frida-trace分析**

* * *

首先通过 frida-ps -Ua （请自行安装frida）查看目标APP的进程id为4934：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfGR6VezTicMIMcV87libFaekyDebte2jS5gK7MctMGkcMOlLbt4msddElCZPMkRGEfDxTYMPibxScjQ/640?wx_fmt=png)

再通过frida-trace跟踪“CC_MD5”函数，命令如下：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfGR6VezTicMIMcV87libFaekTGDLn8nMlGnhwyqNofMd11kB2QOjQXichR4O5Bia8GJxHqJicEg6CdlCQ/640?wx_fmt=png)

frida-trace参数说明如下：  -U 使用USB数据线连接设备  -i 追踪函数  “CC_MD5” 要追踪的函数名  4934 目标APP进程id
接着在终端界面按 Ctrl+C
停止运行。然后在__handlers__/ASEProcessing文件夹中找到CC_MD5.js文件，将代码修改为如下并保存：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfGR6VezTicMIMcV87libFaekfn1nPOib5lsLWE442LYTleBkjEetiagJORvFFO04ic10AbojemY5ytJwQ/640?wx_fmt=png)

以上代码会在追踪到CC_MD5函数步入时打印待加密的参数值，步出时打印加密后的md5返回值。
接着我们继续使用之前的命令运行frida-trace，然后在目标APP列表页继续滑动即可看到frida-
trace追踪到的参数和返回值。然后我们用Charles抓包看到的sign值到frida-trace窗口中搜索即可找到对应参数，如下图：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfGR6VezTicMIMcV87libFaekae0t2zibtLwjaz2rpNQ3JYMwCMGh5BSv1L4icCOJAFj98RD9OobhtQcg/640?wx_fmt=png)
对比请求的url和加密参数：
- 请求 URL 样式：`api.ashx?...&serialid=<serialid>&sign=<sign>`
- Hook 输入样式：`?...&serialid=<serialid>`

作者根据同一请求中 URL 与 Hook 输入的字段对照，判断 `serialid` 参与 sign 输入；样本值已脱敏。完整 canonical 串、字段顺序与规范化规则仍需针对目标版本复核。
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfGR6VezTicMIMcV87libFaekE9KCmWlPtlpUAa01M1TRic6CWPIpKlP7Y47tnWJH2eclNEUeygd0ksQ/640?wx_fmt=png)

**四、总结**

* * *

本文重点在通过Charles抓包看到“sign”参数为32位字符串，猜测是md5加密，从而使用frida-
trace监控目标APP是否使用了iOS系统封装的CC_MD5加密函数。之后一击即中巧破了“sign”参数加密算法。
对于我们爬虫工作者在抓取数据时遇到加密“sign”参数，首先可以猜测其大致的算法，之后用frida-
trace去监测系统默认的加密函数，比如iOS系统的：CC_MD5，CC_SHA1，CCHmac等，有可能会有意想不到的收获。如果此方法行不通，我们可以再去想办法逆向分析。

<a id="ios-sign-input-boundary"></a>
## 可复用提炼：用系统加密入口缩小 sign 输入

来源案例的观察顺序是：先比较同接口不同翻页请求，发现 32 位 sign 随请求变化；再跟踪 iOS `CC_MD5` 的输入与输出；最后将 Hook 输出和抓包 sign 对照，定位参与计算的参数片段。作者在该 10.5.5 样本中把 `serialid` 识别为参与 sign 的字段。

<a id="ios-cc-md5-observation"></a>
### 调试观察方法

先记录目标包与版本、请求字段和响应样本，再在授权测试设备上观察系统 Crypto API 的入参/出参，并按请求逐一对齐。若多个调用都命中，必须用对应请求的输出匹配来筛选；原文截图中的 handler 实现未保存在本文，因此不能把此处当作可直接执行的 hook 脚本。

<a id="ios-sign-acceptance-boundary"></a>
### 适用边界

这是来源报告中的单版本方法示例，不证明其他版本仍调用相同 Crypto API。若观察结果不匹配，应继续静态/动态定位完整 canonicalization；单次本地匹配不等于跨版本 parity 或服务端接受。本轮未运行 Frida、未复现请求，也未验证服务端。

## 提炼说明（550）
retain existing reference。CC_MD5 sign 边界已在本文。
未审图不作证据，不扩卡。
