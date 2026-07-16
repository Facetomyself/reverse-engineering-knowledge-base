# 不还原token算法抓取APP最简单的Hook方法

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2019-11-13
> 归档日期: 2026-07-16
> 分类: mobile-app-reverse
>
> 抓APP有三个麻烦的地方，一个是APP脱壳，二个是抓包问题，三个是请求头里signature/token的还原。 前两个问题要好一点，有现成的工具使用，绝大部分APP都能搞定。 第三个问题sig/token还原是最麻烦的，没有一个工具能自动化搞定，有的生成sig/token的代码写在Java层里，有的写在Native层里。 要完全破解，还原出生成逻辑，还是比较考验你的基本功。

偷懒了一阵，今天写篇抓取APP的文章，用最简单的Hook方法抓取APP。

抓APP有三个麻烦的地方，一个是APP脱壳，二个是抓包问题，三个是请求头里signature/token的还原。
前两个问题要好一点，有现成的工具使用，绝大部分APP都能搞定。
第三个问题sig/token还原是最麻烦的，没有一个工具能自动化搞定，有的生成sig/token的代码写在Java层里，有的写在Native层里。
要完全破解，还原出生成逻辑，还是比较考验你的基本功。

对于大部分爬虫er来说，还是比较棘手。  有没有一种方法/工具直接调用APP里的token生成代码，而不去还原生成逻辑呢？

嗯，是有的，如果token是在so文件里，最强大的工具莫过于Unicorn；  也有使用AndServer充当Web
Server把待抓取APP以http接口的形式暴露给开发者。
不过这两种形式，我认为对于爬虫选手来说，还是比较繁复，配置和使用麻烦，可能还要自己编译apk，在开发调试阶段费时。

还有一种直接调用app里so代码或java代码的方式是Frida rpc。

终于铺垫完了。
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfSjYp8T6uJFGW74ict74V6acOoPOKedsibKBzFmwYhnhkHcd98XiaUZkUhFDIHuzicd72IyVGvjjVJ0Q/640?wx_fmt=gif)

frida是个全能Hook框架，iOS/Mac/Windows/Linux/Android全能Hook，frida
rpc可以直接调用上述操作系统代码，开发语言是Python+Javascript，对于爬虫er来说，这两门语言应该都比较熟悉，容易上手使用。

文字描述比较繁琐，直接上程序/图示，更容易理解。

下图是某个APP的代码
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfSjYp8T6uJFGW74ict74V6aNOZsdHXPAM8mKOw9yprshWlUJWy0BamiaEl6xeI4e6hicB7GgiaK89H2w/640?wx_fmt=png)
从上图可以看到需要调用getAS方法，它会返回一个字符串，这个字符串就是signature。  但是getAS在libnative-lib.so文件里。
我们不用去分析这个so文件，当作一个黑匣子，直接使用frida rpc来调用getAS方法即可。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfSjYp8T6uJFGW74ict74V6aObQhFcCEIAo28TIbD68ATpWldPnHtL9BrwCiayiatQuG4JxJZichqtCcQ/640?wx_fmt=png)

上述是使用JS代码进行Hook，写好后用frida注入到设备里，用Python直接调用getas这个函数，即可驱动frida调用该APP的getAS方法，返回signature。
每次你想获取sig的时候，调用一下getas即可，只需几行代码，就可搞定。

它的思路就是Hook住相关的类和方法，让我们拥有该方法的控制权，然后我们自己来调用该方法。

这个过程你要费点时间的地方是构造传入getAS的形参，从第一张图可以看到getAS需要传入两个参数，一个Context类型，一个String，你需要构造出这两个类型的参数传入getAS。

Hook开发的时候，需要写的代码其实较少，只要你找准了Hook点。

上述写好的获取signature代码，还只能本地调用，不能远程调用。
如果你的爬虫程序是运行在内部局域网内，还可以这样使用，如果是运行在云服务器上，想要通过公网远程调用，就还需要用Python构造一个web
server，以http的形式把接口暴露出来，供远程调用。

非常无聊中，欢迎撩骚，我的个人微信：
![](https://mmbiz.qpic.cn/mmbiz_jpg/GrTTsqWuEccnpLUwbaRX1RPgOic7kIHa3NNT3ZSgPnrnGH8GA4gHaibHw6TurEKszXSRPQhgcibFUficr1AsaPjJjw/640?wx_fmt=jpeg)
