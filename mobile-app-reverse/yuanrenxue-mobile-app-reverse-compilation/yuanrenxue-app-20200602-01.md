# APP爬虫-某APP iOS版逆向过程

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2020-06-02
> 归档日期: 2026-07-16
> 分类: mobile-app-reverse
>
> 跟着猿人学王平大佬学了一段时间安卓APP逆向，刚刚入门。由于我使用Mac和iOS更频繁，所以我以某汽车 iOS 版为例，记录一下逆向过程和一些知识点。

本篇来自周小鱼同学的投稿

跟着猿人学王平大佬学了一段时间安卓APP逆向，刚刚入门。由于我使用Mac和iOS更频繁，所以我以某汽车 iOS 版为例，记录一下逆向过程和一些知识点。

此次逆向教程使用到的工具如下：

  * 一部越狱iPhone或iPad

  * 抓包工具：Charles

  * 反编译分析工具：IDA64_v7.0

  * Hook 框架：objection v1.9.1

https://github.com/sensepost/objection

  * 调试工具：LLDB，Debugserver

**1 抓包分析**

抓包发现含有32位数的“_r”参数(可能为MD5加密)以及34位数的sign参数，且每次请求都会变化。经过反复抓包对比测试，发现无论修改任何参数再提交服务器都会返回url签名错误，并且发现sign参数最后2位数不变，猜测是32位数MD5密文加字符串“01”组成。接下来的重点就是分析“sign”和“_r”是怎么生成的。

两次抓包参数文本对比效果图：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceB6tUVZ8Kpvx57dMYJvMiabV1PhyK3zibiawWPNTKajw75Y8kWaEcKWgpZqHBQecgj7wntNscE8e4cQ/640?wx_fmt=png)

**2 逆向分析“sign”和“_r”参数**

使用 frida-iOS-dump
一键砸壳后，将砸壳后的二进制文件拖入到IDA中进行分析。由于“sign”关键字可能存在太多干扰不利于分析，所以我们从一个可能干扰比较少的关键字“ttDna”
开始分析。

在IDA strings 窗口搜索ttDna，有且只有一个结果完全吻合，如下图：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceB6tUVZ8Kpvx57dMYJvMiabaCZzqI48VzfMphFfc41Miau58J7UuEjLtia52Mf0J56PovY9BklZAnAQ/640?wx_fmt=png)

通过这个关键字，我们进入到了函数：-[CBDBaseApi extraParams]，果断使用 objection（如何使用请自行查阅资料）
对此函数进行hook，查看其参数、返回值和调用堆栈，截图如下：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceB6tUVZ8Kpvx57dMYJvMiabuJsL8VFqEibu0ia5X17icOqEe36cgdzAUrnTqLBhsHZBpWUzqajfOdEjQ/640?wx_fmt=png)

返回值确实包含了我们抓包中看到的信息，但是不完整，需要继续追踪调用函数。

通过第一个堆栈地址 0xc4ed40 + IDA64头部偏移量 0x100000000 = 0x100c4ed40
找到IDA64中相应地址调用的地方，发现在函数：-[MCCBaseApi buildFullUrl:] 内部。我们继续使用 objection 对此函数进行
hook，发现返回值与我们抓包看到的完全吻合：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceB6tUVZ8Kpvx57dMYJvMiabziac7Nhdy0SW2AQJQrCnkUPovIFDrZQXwibkwaSia6GYNYT9I6K7BdzQQ/640?wx_fmt=png)

从上面返回值的截图可以看出完整的url是由此函数拼装而成，接下来我们在IDA64中按F5键查看该函数的伪代码，逆向由下往上分析：

return=v21=v20=v14=v13，

发现返回值是

+[MCCURLManager buildUrlString:withParams:sign:]

生成的：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceB6tUVZ8Kpvx57dMYJvMiabOHq8KCW9myHuYDqDliaOkw9jOxOQicibxmxqQ9Zib8yURmFoNo9IibCwBXw/640?wx_fmt=png)

继续追踪

-[MCCURLManager buildUrlString:withParams:sign:] ，

发现来自于

-[MCCURLManager buildUrlString:withParams:sign:useBasicParam:usePublicParam:]。

在此函数中，我们发现了“_r”参数。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceB6tUVZ8Kpvx57dMYJvMiabDc9U61PGYg7370WMxHvyIDq1lWibg5mFE0DBhYPpFU9diaibYj40W9ibOQ/640?wx_fmt=png)

经过分析“_r”参数是随机生成的UUID经过MD5加密得到。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceB6tUVZ8Kpvx57dMYJvMiabBesyPlGpAJvES8gKNd5lx469IXCyJ2pWjtxBj3ueDKzH6zFou7AUaA/640?wx_fmt=png)

继续一路追踪sign参数，发现到了一个跟sign有关的函数：+[MCCSignURLManager signUrl1:withKey:]，果断使用
objection hook该函数，参数和返回值仅仅只多了一串sign参数，由此可以判断sign在此函数内生成，并且发现key值是：

SW+SaqSibZdCmqNyh4WYlW+l，

截图如下：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceB6tUVZ8Kpvx57dMYJvMiabwIk4azSTfeQicPxhuNTewSln4NeSHWibf2BUbFBOlVMey3Nvnr7gnFIA/640?wx_fmt=png)

继续分析该函数的伪代码，我们看到一个自定义的函数 SignUrl1，如下图：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceB6tUVZ8Kpvx57dMYJvMiab8ZXThBc07hmcUpQ9STdGFNwX0wdm99l2kwVoojna3icIomkcKe6FPIQ/640?wx_fmt=png)

双击进入SignUrl1，我们又看到另一个自义定函数 SignUrl0，如下图：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceB6tUVZ8Kpvx57dMYJvMiabO4qnemic0PkPZM1XaoIvOrmGOM6c2ZIs3Ju0c2BxoZww2NRCZssJOAw/640?wx_fmt=png)

双击进入SignUrl0，我们看到熟悉的MD5加密算法，如下图：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceB6tUVZ8Kpvx57dMYJvMiabm9uicTl3tBG6JicSiasF949g5CD7ibxZ7JNquBuriagH4RKGxcibPFhwN2ibA/640?wx_fmt=png)

逆向分析到此，我们可以大胆猜测，SignUrl1是在组装加密参数，之后将参数传递给 SignUrl0 进行MD5加密之后再将密文返回给SignUrl1。

现在我们只需要查看SignUrl0函数的具体参数就可以知道如何加密了。接下来我们使用LLDB+debugserver（具体如何使用请自行查阅资料）在图下位置下断点并查看传入的具体参数：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceB6tUVZ8Kpvx57dMYJvMiabQR5Bvn2bxyBbbQ8jtFnkBH3UpaxetGZxkADpth6c9ibNYicuS3iaEdbYQ/640?wx_fmt=png)

参数1为不包含sign参数部分的请求内容，部分截图如下：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceB6tUVZ8Kpvx57dMYJvMiabJmTB1nqq8s4c05187dNXOeLlrGV50b6OVtVwYfM0aH5IDdZWxtqMYQ/640?wx_fmt=png)

参数2为key值经过base64decode等步骤转换而来的固定字符串：

5oBjPRiG2ZSbwqDAoQ，

也就是MD5加密的盐。这里我们无需深究key是如何转换的，只需拿到key的固定字符串即可：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceB6tUVZ8Kpvx57dMYJvMiabdtQaDklHXYgSJt6Ricb12TLSzOEKicO1ic7hlZ4RFudG9egcsfjsJxgdg/640?wx_fmt=png)

所以sign参数算法就是由函数SignUrl0的入参1+入参2经MD5加密后与“01”拼接得到。接下来我们验证一下我们猜测的算法与抓包是否一致：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceB6tUVZ8Kpvx57dMYJvMiabJcxg0U3xouUAZ0wwDFdxUODCulxYheTEeiaTibxXmW8yDJoibfUAMuF8A/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceB6tUVZ8Kpvx57dMYJvMiabe3ZBiaERKpvPp3WcyUCxWku7bW3u47dQOpB1N7MKZwnaGvTE66iaeVeg/640?wx_fmt=png)

由上面2张图可以看出sign参数算法完全正确，至此sign参数和“_r”参数全部告破。接下来就可以使用Python实现算法然后自由爬取文章了。

**3 总结**

本篇文章的案例用到了Charles抓包，frida-iOS-dump砸壳，IDA64反编译，objection
HOOK框架，以及LLDB+debugserver调试等工具。每一个工具的使用都需要花大量时间研究，本文并未对以上工具的使用进行详细说明，感兴趣的同学可以自行查阅相关资料。

案例中的APP也算是大厂开发的，而我们对其二进制文件的加密函数分析并不是太难，没有对关键字加密，没有复杂的算法，也没有对函数名进行混淆，直接使用IDA64进行静态分析，以及使用objection
hook查看参数和返回值就追踪到了加密的函数。

所以做爬虫工作碰到APP逆向这个事情，首先不要害怕，其实市场上大多数APP的加密参数都可以通过我们这种方式搞定。当然很难的也有很多，比如关键字加密，函数名混淆，反调试检测，多线程循环发包，网络发包封装第三方库等等，面对这些只要有信心有耐心，多学习实操总结，慢慢积累经验，会有所成的，大家共勉！

**PS：广而告之：

**把猿人学·爬虫高阶课又更新了，加入了安卓群控，详情点击源文查看**
