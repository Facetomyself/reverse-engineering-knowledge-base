# 爬虫技巧：逆向破解js代码加密，代码混淆不是难事

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2019-05-13
> 归档日期: 2026-07-16
> 分类: web-reverse
>
> 爬虫解析网页数据时，最棘手的问题莫过于关键数据被加密，被混淆。加大了解析难度，常见的诸如登陆密码，token等被混淆成了一个长长的字符串。好在这些加密都是javascript在浏览器中进行，找到这些js代码并破解并不是难事。

爬虫解析网页数据时，最棘手的问题莫过于关键数据被加密，被混淆。加大了解析难度，常见的诸如登陆密码，token等被混淆成了一个长长的字符串。好在这些加密都是javascript在浏览器中进行，找到这些js代码并破解并不是难事。

谷歌的Chrome浏览器有个开发工具（DevTools），可以帮助前端开发者完成调试JavaScript代码等工作。这个工具非常棒，也是爬虫开发者的有力工具，对于研究复杂网站（通过大量的js混淆、加密数据及其访问接口）的爬取很有帮助。

今天，猿人学Python就来讲讲， **如何利用Chrome调试JavaScript的功能来找到js加密相关的代码。**

为了防止爬虫，网站开发者们也是费尽了心思：

**首先** ，他们使用JavaScript把一些数据接口通过多次请求、加密生成token等方式来生成数据接口的访问URL；

**然后** ，他们又把这些JavaScript压缩、混淆使得它们晦涩难懂，或者分成很多不同的js文件，让你要找到某些关键的代码如同大海捞针。

**最后** ，就把一部分爬虫开发者拒之门外了。

不服输的程序员，利用有力的工具，加上不服输的精神就开始了钻研之旅。

接下来，我们钻研一下如何通过Chrome调试js代码来找到Google中文翻译的请求接口。

下面是https://translate.google.cn/ 的截图，这个网站在国内可以无障碍访问。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceaCUMibp0x4GVzUoCO5iaeVtNFK6KPqwgSQPJnpmfWpGQWTRQ8AewMiajfpUwY7fjibxOCHfsf2Jb0nw/640?wx_fmt=png)

在左边输入“Python”，右边立马出现“蟒蛇”，而整个网页并没有刷新，这是通过一个ajax请求实现的翻译。

那么问题来了： **这个ajax请求的URL是什么？**

通过Chrome的开发工具（按F12调出）的“Networks”可以看到，请求的是：

https://translate.google.cn/translate_a/single?client=webapp&sl=auto&tl=zh-
CN&hl=zh-
CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&otf=1&ssel=0&tsel=0&kc=1&tk=606016.1025355&q=Python

这个URL里面有个参数:  tk=606016.1025355

观察发现，这个参数的值每次请求既然还不一样！  这个参数是如何生成的呢？为了能使用这ajax翻译接口，我们得需要好好钻研一番。

## 第一步：观察网页加载了哪些js文件，猜猜哪个文件可能包含tk生成的代码。

在Networks里面看看都加载了哪些js文件，可以通过点击 Filter 右边的“js”按钮只显示js文件。

按住Ctrl（非Mac）或Command（Mac）来选择多个过滤器。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceaCUMibp0x4GVzUoCO5iaeVtTJ2icMZeg479TQGC3sbXwMHoFCtpVI2IPBONZxv6jC1tYYIyQzibDLUQ/640?wx_fmt=png)

观察它们的名字，我猜是“translate_m_zh-CN.js”。别问是怎么猜的，就是看名字凭感觉。

打开这个js一看，诶呀妈呀，密密麻麻一大片，完全没法读！！！（多亏不能读，如果能清晰的读起来，就没有后面的故事了）

## 第二步：了解“Sources”工具

切换到开发工具的“Sources”，可以看到如下窗口：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceaCUMibp0x4GVzUoCO5iaeVtoZdiayRpuKZoC2hicBYbZ3TBXIby97qNWd5HBr54lcPfibqPZ4mBzQfUQ/640?wx_fmt=png)

（1）上部左边的“Page”是各种资源文件的路径，js就在这里找。

（2）上部右边是显示代码的窗口，可以打开多个代码文件，每个文件一个标签页，标签页标题显示文件名称。当打开一个被压缩过的js文件时，它会提醒“Pretty-
print this minified file?”（要格式化代码吗？），点击后面的“more”可以看到如何操作，也就是点击代码页下边的
**花括号“{}”**即可。可以**点击代码左边的行号设置断点** 。

（3）下部左边是调试窗口，比较重要的有：

**XHR/fetch Breakpoints :** 在请求某个URL时设为断点；

**Call Stack：** 运行到断点时，函数调用的栈，从上到下按离断点近远排序；

（4）下部右边是运行到断点时，“Scope”显示局部变量和全局变量，“Watch”可以添加要观察的变量。

上面这4部分的布局会随着整个devtools窗口的宽窄而变化，把devtools窗口拉宽，它们可能会排成一排。

## 第三步：调试JavaScript，探寻关键代码

我们的目的是要找到“tk”这个变量的生成方法，从而可以使用ajax翻译接口。前面我们已经探讨出，tk是ajax接口（即前面列的那个包含“/translate_a/single”的URL），那我们就设置断点，在访问这个URL前停止。具体做法如下：

（1）设置 **XHR/fetch Breakpoints** 断点，点击它后面的加号“+”，把这个URL添加上，问号后面的参数就不用填了。

（2）在Google翻译的输入框随便输入个单词，比如“Python”，然后网页就变灰（锁死），上方出现“Paused in debugger”，如下图：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceaCUMibp0x4GVzUoCO5iaeVtYEx7Qk02Iwnj0bAUojOmAkqicUiajGPVYo7Z05JJNwia9JbRS6Picyn1ng/640?wx_fmt=png)

这时候，我们观察程序目前的状态：

（a）源代码那里，停止在"this.xa.send(a)"；

（b）“Call Stack”显示了调用关系，最上面的就是源码那里的send函数。

**小技巧** ：把devtools拉宽，让Call Stack和代码两个窗口并列，更容易查看。

从上往下依次点击Call Stack的每一行，每次点击都会显示对应的代码片段。当点击到第三个时发现似乎找到了答案：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceaCUMibp0x4GVzUoCO5iaeVt6b8QtywckUIQqicRqgWOxEEpmoKO3BQkn7xKIxUToDcibtzhhubxPVwA/640?wx_fmt=png)

（注意：上面截图的行数和变量名称有可能和你看到的不一样）

棕色背景列出了变量的当前值，可以看到8332行的b包含了tk参数，而这个参数明显是来自c，再往上到8329行找到了c来自函数Uo()，鼠标放到Uo上面停一会儿，就可以跳到它的定义处，也就是8323行，同样鼠标悬停在$n()函数并跳到它的定义：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceaCUMibp0x4GVzUoCO5iaeVt7Uvom50ACkXW2tQ0NDDiacnC01XYFYSprrxzZu1pm6qQvXHwOTI2qYg/640?wx_fmt=png)

观察这个函数，这是一段算法，请求返回的字符串就是tk值那样的形如“a.b”的一串数字，那么它就是我们要找的tk值的生成算法。至此，我们就通过Chrome调试JavaScript找到了js中我们想要的代码。

要弄明白这段算法，你就要懂得JavaScript语言，及时不会js如果你会Python，在搜索引擎的帮助下也可以很快弄明白它并用Python来实现。

再来看看这段代码，它是如何让人“看不懂”它的，也就是下面的“不好好写程序大法”，掌握此法有助于你破解它，拨开迷雾见真相。

## 扩展：如何不好好写程序

**（1）String.fromCharCode()**

这个函数就是Python的chr()，把数字变成字母。看7504行，函数Xn的参数是个字母，不直接写偏偏要通过函数转化一下。真有一种脱裤子放屁的赶脚。

**（2）闲着没事儿就写个函数**

在看那个函数Xn的实现：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceaCUMibp0x4GVzUoCO5iaeVtsDMiaDm2ZibuKErLmQqKBzz7SAcdQp8wqDsu5zJkPVSMkWkzon8e9Rdg/640?wx_fmt=png)

真是闲的蛋疼！

**（3）eval函数**

除了上面两个方法，eval也常用。这个JavaScript的eval和Python的eval一样。

写爬虫避免不了和复杂的网页（网站）打交道，它们以各种方法“防”，爬虫以各种方法“攻”。攻防之间可以说是道高一尺魔高一丈，来回较量。

本文通过Chrome调试JavaScript是一种“攻”的方法，还可以使用抓包工具（比如
Charles）进行更复杂的分析，Charles提供了更丰富的搜索功能等。

这两种方法基本上算是一种策略，另外比较省事的就是使用Selenium的Chrome
driver，开发起来简单很多，但运行效率会低一些，适合抓取频次低（有些封得你没办法频次高）的网站。

\--------------------------------

最近想开了，打算教人写爬虫。我写了十余年Python爬虫和Web开发，国内外大大小小的网站/app撸了个遍。反爬虫策略，反频率/账号控制，世面上的我几乎见了个遍。

全以实战为主，真正做到学完即能动手开发那种。

猿人学Python公众号菜单栏-联系我，你能找到我。非诚勿扰~~

爬虫精华文章拓展阅读：

[ 如何让爬虫一天抓取100万张网页
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548659&idx=1&sn=d2a8dd3544bfd7980c8ab1fbb0c5dd4b&chksm=b2e8fc7e859f7568b41fcc55b384e9d78a4c4503707ac34c890a3be17ecfe2d40df4bc3602d5&scene=21#wechat_redirect)

[ robots.txt快速抓取网站的小窍门
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548110&idx=1&sn=eed95141eae2c24eec8cfe2ff927a971&chksm=b2e8fe43859f77554409558eb5f6b55012bd23112e079df53cb0b0819fe4186ac8984f411438&scene=21#wechat_redirect)

[ 爬虫小偏方：绕开登陆和访问频率控制
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548014&idx=1&sn=b77ee2c67a68bd395edb91be78e794bd&chksm=b2e8ffe3859f76f533c97bd38946cf68dfd82b097cb963744e97531a176773800be3864c809a&scene=21#wechat_redirect)
