# 谈下微信小程序的抓取技巧

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2019-09-02
> 归档日期: 2026-07-16
> 分类: web-reverse
>
> 今天聊下微信小程序的抓取，其实小程序的抓取不难，主要解决抓包和如何调试小程序这两个问题。如果你运用chrome调试已经比较熟练了的话，就手到擒来。

今天聊下微信小程序的抓取，其实小程序的抓取不难，主要解决抓包和如何调试小程序这两个问题。如果你运用chrome调试已经比较熟练了的话，就手到擒来。

**先来说小程序抓包问题**
不用破解的办法如何抓到小程序的包？破解是个费劲的事，一不小心微信账号还可能被封。

小程序抓不到包通常就是你手机的安卓系统版本太高和微信APP的版本太高了。版本越高，通常它的安全性就越好。换用安卓系统是4.4的手机和微信APP版本在6.7左右的版本。使用Fiddler或Charles抓包妥妥的。

如果你实在没有低安卓系统版本手机和低版本微信，继续看下面的文字，待会再介绍一种抓包方法。

只要抓包搞定了，很多小程序也就能抓取了，剩下就是解决IP问题。还有一部分小程序在前端有反爬措施，对请求参数加密或混淆了。所以就还得解决小程序调试问题。

**再说下小程序调试问题**
首先得对小程序有一点理解，小程序简单来说也是一个网站，只是它只能在微信里打开，不能在浏览器里打开。

我们都知道一个网站的前端页面是由html、css、javascript组成，小程序的前端页面也是由类似这样的来组成的。小程序里的数据交互也是由javascript来负责的。所以爬虫调试小程序也主要是调试javascript。

那怎么调试小程序的javascript呢？
当我们在微信里点击小程序时，微信会把这个小程序的前端代码下载到你的手机上。我们只要拿到这个小程序前端代码，就能在微信提供的小程序开发者工具上进行调试。

小程序代码的路径在：
/data/data/com.tencent.mm/MicroMsg/微信号id文件夹/appbrand/pkg/

该路径下以.wxapkg结尾的文件就是小程序前端代码被编译之后的形式。
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcddcEnCv6BDzHyXic8JiaRzG40dbibEENhBoJPOk8bx8opdHO68QxJ0Ij0DUQFDljvatwibkvJ11ibVibpA/640?wx_fmt=png)

你会看到很多个.wxapkg文件，因为你打开过很多小程序，最好是你把这个文件下的文件全都删除，重新打开目的小程序。然后里面的.wxapkg文件就都是该小程序的了。

你需要把.wxapkg的文件都拷贝到你的电脑上来。（拷贝该目录需要你拥有root权限，所以你得先把手机root了，或者在安卓模拟器里面使用微信，进行如上操作，模拟器默认是root了的）。

**解包wxapkg**
我们的目的是拿到小程序的前端代码在小程序开发者工具里面调试，wxapkg是编译之后的小程序，所以还得反编译，让wxapkg解包出源代码。

要感谢开源的世界，已经有爱好者开发出了.wxapkg的解包程序，我们就直接拿过来用。

解包程序的github地址是：  https://github.com/qwerty472123/wxappUnpacker

解包程序是由node.js开发的，所以你得先安装node.js，然后再安装node.js的一些依赖包，作者已经在文字里说得很清楚了。我就不再赘述，网上也有很多该程序的用法文章。

最后你只需要运行命令：

    node xxxxxx.wxapkg

node是运行node.js的命令，即可把小程序前端源代码还原了。类似下图这样的。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcddcEnCv6BDzHyXic8JiaRzG4Vc9Ec612GhSbxuibod6APozibUbjqqgEaicjWwtBs6vjaN83BqwBLnTtw/640?wx_fmt=png)

**调试小程序** 注册一个小程序开发者账号  注册地址：https://mp.weixin.qq.com/cgi-
bin/registermidpage?action=index&lang=zh_CN&token=
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcddcEnCv6BDzHyXic8JiaRzG4yVoPwtXbxoCVYWstFS9OOKOicZMMdUp3WTbzQ104oyQrA8gAtXevc1Q/640?wx_fmt=png)
下载小程序开发者工具：
https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcddcEnCv6BDzHyXic8JiaRzG4Yzv9NxbVxY3jvdw4f5hCOxZHhGf6vXJcZ8ia81U1N0TEz5LHMcwJndg/640?wx_fmt=png)
打开小程序开发者工具，选择导入已有项目，就是选择上面解包出来的那个文件夹。
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcddcEnCv6BDzHyXic8JiaRzG40lfIERmic8aicdMDzdHSR7R5LWSMibS9iaIdwZJvK74q3Wvp8r2JuLncHQ/640?wx_fmt=png)
点击确定。就出现以下界面。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcddcEnCv6BDzHyXic8JiaRzG4IIibsiapyVedyDGuiaexiamIJ7uOBJ9G0Mzh8L1NJQPpjnMBF2ZZuQ0USQ/640?wx_fmt=png)

这就可以对该小程序做调试了，界面是不是很熟悉，是不是跟chrome浏览器的调试很相似。你可以点选sources面板，然后对js打断点，也可以在console里直接运行一段js代码。想要知道请求的URL是如何加密的，跟chrome一样，打断点调试即可。具体怎么打断点调试，我已在猿人学公众号上写了好几篇，你可以回头再去看看。

另外我文章上半部分说了一个抓包问题，还没有解答，如果是高版本安卓系统，高微信版本如何抓包小程序。一种小技巧就是借助小程序开发者工具来抓包，细看上图红框，有个Network面板，跟chrome的功能是一样的，这个小程序的网络请求在Network面板里能看到。

另外因为这个小程序是别人开发的，你要把这个小程序运行起来，要让它不去验证域名和ssl证书那些，如下。
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcddcEnCv6BDzHyXic8JiaRzG4gFmddY4M0tXl5lD5EickWQiaDSA7PN3sW8Tb0laTRvib5vRebvgsib6jkg/640?wx_fmt=png)

综上解决了抓包和调试小程序问题，就能抓取绝大部分小程序了。还有一些小程序必须要微信登陆才能访问，要大规模抓取，你还是得解决大量账号的问题。

PS：上述对.wxapkg文件解包，还有一些小细节我没有全部写出来，诸如运行解包程序报错，还有解分包的问题。这些很琐碎，偏离了主题。感兴趣的可以自行搜索。
相关知识拓展阅读：  [ JS逆向方法论-反爬虫的四种常见方式
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548987&idx=1&sn=75a610751d641c9d7cc7bb0ea1649015&chksm=b2e8fb36859f72203dfdfd58ead1c4ff348c0d1fe3cb17b1e4c6f587cac515221bb3f76e3cce&scene=21#wechat_redirect)
[ 写爬虫，免不了要研究JavaScript设置cookies的问题
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548910&idx=1&sn=32614354251cd767b6a5d9a2cf485b84&chksm=b2e8fb63859f727501692ebcf4552819b1deda0c58cd2a39642a9db9b36c638937fd75ccbb26&scene=21#wechat_redirect)
[ 爬虫技巧：逆向破解js代码加密，代码混淆不是难事
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548692&idx=1&sn=ccd73a67ee615c8111eb28319d388919&chksm=b2e8fc19859f750f972d9e9e954576bdef0fe2ea2f3252e42aeb979b853dd642a9488b7898b8&scene=21#wechat_redirect)
[ 如何让爬虫一天抓取100万张网页
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548659&idx=1&sn=d2a8dd3544bfd7980c8ab1fbb0c5dd4b&chksm=b2e8fc7e859f7568b41fcc55b384e9d78a4c4503707ac34c890a3be17ecfe2d40df4bc3602d5&scene=21#wechat_redirect)
