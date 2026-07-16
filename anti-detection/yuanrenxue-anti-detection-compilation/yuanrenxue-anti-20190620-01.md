# 大规模爬虫为什么要管理DNS缓存

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2019-06-20
> 归档日期: 2026-07-16
> 分类: anti-detection
>
> 10年前学爬虫看的第一个开源爬虫叫Larbin ，一个法国程序员用c++开发的，那时用Larbin简单配置一下，因为它能自动遍历抓取，一天几乎能镜像一个中型网站，感叹实在高效，但是那会不懂为什么爬虫要有一个dns模块，一是因为那会自己网络知识的匮乏，二是没有感受过超大规模抓取，对dns缓存节省的域名解析时间没有感觉。

10年前学爬虫看的第一个开源爬虫叫Larbin
，一个法国程序员用c++开发的，那时用Larbin简单配置一下，因为它能自动遍历抓取，一天几乎能镜像一个中型网站，感叹实在高效，但是那会不懂为什么爬虫要有一个dns模块，一是因为那会自己网络知识的匮乏，二是没有感受过超大规模抓取，对dns缓存节省的域名解析时间没有感觉。

感受过大规模抓取后，对涉及到网络性能的每个点都想要极大优先，对域名解析到IP这个过程的时间消耗自然不能放过。

今天的话题就是说道：大规模爬虫为什么要管理DNS缓存？

**DNS是什么？**

DNS是一个域名解析服务，负责解析域名对应的IP。我们在访问网站时都是在浏览器里输入的一个个域名，但是在网络传输协议中都只是认一个个IP，所以在输入域名的时候，先要做域名解析，这就是DNS要做的事情。

可以简单的把访问网页看成如下这样：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfEhovr6ibicYd4iaH42MEHtaT2fT81aT5Kh8U2nT01yD76ibDA26xfviaoobrO7EmjzNIibpIr8WT8Lb6A/640?wx_fmt=png)

**DNS具体是怎么把域名解析成IP的？**

有专门的DNS服务商，这些服务商通常就是电信运营商，比如中国电信这样的。系统会访问DNS服务商的IP，获得对应域名的IP。DNS服务商的IP我们很熟悉，最为大家所熟知的就是114.114.114.114，在你的电脑上可以查看你的DNS服务器IP是多少。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfEhovr6ibicYd4iaH42MEHtaTZRbD3Ngdn6VYvQogZMIZrYp3bWAvu6Eax65W0EOQAzibbsoqsiaOa2SQ/640?wx_fmt=png)

DNS服务商那里有一份域名对应IP的列表，它会把域名的IP返回给系统。

**DNS解析耗时吗？**

相对于请求下载网页的时间，DNS解析的耗时是很少的。通常是几十毫秒。但是因为访问一个IP的时候，会在不同的路由节点间跳转，有可能要跳转很多次才能路由到IP对应的机器上，所以有的DNS解析会耗时数百秒乃至数秒时间。

我们可以在Chrome浏览器的开发者工具中简单测试下DNS解析耗时，下面是访问一个网站Chrome记录的各项耗时，红框出DNS
Lookup就是耗时151.59毫秒，这个耗时还算长的了。（因为浏览器和操作系统本身可能要做DNS缓存，所以你访问测算出的DNS耗时可能非常的短）

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfEhovr6ibicYd4iaH42MEHtaTFrUkyOxnrgibtyOFF7uruRYvWso9gdEe5GMUaQCKfzBKUmqcjumVaIQ/640?wx_fmt=png)

如果每次访问都要做一次DNS解析，那我们一天要抓取一千万张网页，就算每次解析只耗时30毫秒，一千万次抓取光做DNS解析就要30万秒=3.47天。这是非常浪费的。

PS:Linux下面也可以使用dig命令来查看dns解析耗时：

    dig www.yuanrenxue.com

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccU4wevhBcL1C53ibicWBjUDMAAVW4Fib2iarL5PV5CBeibsvmsjib1YLMxMWuT7fqRkEb2eSSFIsJr7ia2A/640?wx_fmt=png)

Query time就是dns的解析耗时，89毫秒。

**为什么要做DNS缓存？**

上面我们算过当大规模抓取，每次都要做DNS解析时，浪费的时间是非常大的。所以如果能在本地做DNS缓存，每次系统都读本地DNS的话，这个时间消耗估计是微妙级别，是能够接受的。其实Windows本身是有DNS缓存机制的，访问一个域名后，系统会缓存下域名对应的IP。我们的爬虫通常是运行在Linux上的，Linux本身一般是没有DNS缓存的。

**如何做DNS缓存？**

一种最简单的方法就是修改/etc/hosts文件，在文件里直接添加IP和域名，这样：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfEhovr6ibicYd4iaH42MEHtaTIOdDtDK3VhIFicanicYAibRhk6iaAueicjG2R0nL2Xz5Rf58k0xhtIK6Omg/640?wx_fmt=png)

但是如果域名很多，一个一个手动添加比较繁琐，万一对方IP改变了，那就会大面积抓取错误。

另一种方法使用DSN缓存工具，诸如DNSmasq
，是一个小巧的DNS管理工具，配置方便，当你访问过一个域名后，就会把域名对应的IP缓存起来。一种自助式的，你配置好了就行，用起来挺方便。

第三种方法就是我开篇提到的，像Larbin爬虫一样，在自己的爬虫程序中添加一个DNS模块，自己管理DSN缓存。好处是不依赖其它的工具。像Scrapy爬虫框架就有自己的DNS缓存管理模块。感兴趣的可以去看它源代码是如何实现的。

把dns管理加到我在猿人学Python写的《  [ 如何让爬虫一天抓取100万张网页
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548659&idx=1&sn=d2a8dd3544bfd7980c8ab1fbb0c5dd4b&chksm=b2e8fc7e859f7568b41fcc55b384e9d78a4c4503707ac34c890a3be17ecfe2d40df4bc3602d5&scene=21#wechat_redirect)
》中就更加如虎添翼了。

话说有道面试题叫着《从浏览器输入url到看到页面》这里面发生了什么，如果你能弄懂里面的细节的话，在网络优化上还有一些优化空间，并且还能找到一些反反爬的窍门。

当然抓取规模比较小的话，其实DNS解析这点浪费时间没多少，当抓取规模很大时，你拿笔算一下浪费的时间，哗哗的。

**还是广而告知：**

我最近在教学爬虫：

一对一教学Python爬虫，学会如何设计抓取海量数据的爬虫；

学会如何高效分析/制定抓取策略；

学会APP/JS逆向；

传授我用爬虫技术的挣钱经验，我的职场经验。

全以实战为主，学完能自己真实动手开发那种。

在公众号菜单栏-联系我，找到我的微信

**爬虫相关精彩文章：**

[ 大规模异步新闻爬虫的分布式实现
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548782&idx=1&sn=d94410db4dbb3ea143ba07635db758b8&chksm=b2e8fce3859f75f5ce1551cfc6dfb1dc2ad1116a42aaf663944431b2fefbe6f4676bf97eadd9&scene=21#wechat_redirect)

[ 如何让爬虫一天抓取100万张网页
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548659&idx=1&sn=d2a8dd3544bfd7980c8ab1fbb0c5dd4b&chksm=b2e8fc7e859f7568b41fcc55b384e9d78a4c4503707ac34c890a3be17ecfe2d40df4bc3602d5&scene=21#wechat_redirect)

[ 大规模异步新闻爬虫的实现思路
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548722&idx=1&sn=b25b5ea8748523f966ce430845133252&chksm=b2e8fc3f859f7529cfcd85864e06daab3910bd731318d6fa4b8a1d92d36fdc0320362a7fd300&scene=21#wechat_redirect)

[ 爬虫技巧：逆向破解js代码加密，代码混淆不是难事
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548692&idx=1&sn=ccd73a67ee615c8111eb28319d388919&chksm=b2e8fc19859f750f972d9e9e954576bdef0fe2ea2f3252e42aeb979b853dd642a9488b7898b8&scene=21#wechat_redirect)

[ 爬虫挣钱系列：数据整合之--结构化人名的机会
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548293&idx=1&sn=6c90e19bcb64ca02a12f7fbc91694714&chksm=b2e8fe88859f779e2fc86b0bec24ef327a24f4ff77741f277bf103d6932a97def66acfb0345e&scene=21#wechat_redirect)

[ 爬虫小偏方系列：robots.txt快速抓取网站的小窍门
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548110&idx=1&sn=eed95141eae2c24eec8cfe2ff927a971&chksm=b2e8fe43859f77554409558eb5f6b55012bd23112e079df53cb0b0819fe4186ac8984f411438&scene=21#wechat_redirect)
