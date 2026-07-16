# iOS逆向抓取-巧破某报价大全APP加密参数

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2020-06-09
> 归档日期: 2026-07-16
> 分类: mobile-app-reverse
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
-请求的url：  api.ashx?cateid=3&cityid=&method=news.list&pageindex=3&pagesize=25&productid=7&serialid=&sign=fbe1c8222424f38371f0b59592a6293b  -加密的参数：  ?cateid=3&cityid=&method=news.list&pageindex=3&pagesize=25&productid=7&serialid=2CB3147B-D93C-964B-47AE-EEE448C84E3C
请求url中标注部分与加密参数标注部分完全一致，我们可以确定盐值为：2CB3147B-D93C-964B-47AE-
EEE448C84E3C。至此“sign”参数md5加密算法不攻自破了。
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfGR6VezTicMIMcV87libFaekE9KCmWlPtlpUAa01M1TRic6CWPIpKlP7Y47tnWJH2eclNEUeygd0ksQ/640?wx_fmt=png)

**四、总结**

* * *

本文重点在通过Charles抓包看到“sign”参数为32位字符串，猜测是md5加密，从而使用frida-
trace监控目标APP是否使用了iOS系统封装的CC_MD5加密函数。之后一击即中巧破了“sign”参数加密算法。
对于我们爬虫工作者在抓取数据时遇到加密“sign”参数，首先可以猜测其大致的算法，之后用frida-
trace去监测系统默认的加密函数，比如iOS系统的：CC_MD5，CC_SHA1，CCHmac等，有可能会有意想不到的收获。如果此方法行不通，我们可以再去想办法逆向分析。
