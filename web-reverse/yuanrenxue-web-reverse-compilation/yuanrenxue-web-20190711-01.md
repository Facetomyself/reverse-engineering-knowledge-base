# 写爬虫，免不了要研究JavaScript设置cookies的问题

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2019-07-11
> 归档日期: 2026-07-16
> 分类: web-reverse
>
> 网页端抓数据免不了要跟JavaScript打交道，尤其是JS代码有混淆，对cookie做了手脚。找到cookie生成的地方要费一点时间。

网页端抓数据免不了要跟JavaScript打交道，尤其是JS代码有混淆，对cookie做了手脚。找到cookie生成的地方要费一点时间。

那天碰到这样一个网页，用浏览器打开很正常。然而用requests下载URL却得到“521”的状态码，返回的内容是一串压缩混淆的JavaScript代码。就是下面这个样子：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfmqH2cs7G2BDz012FwHTu2O4PR0ZJITpOyGwEicU0x5p1SMiaSia0Tse5yZfuhHyVuzxlibAiaic3zdjDA/640?wx_fmt=png)

返回的是JavaScript就好说了。肯定是浏览器运行这段JavaScript后，再次加载就可以得到真实网页内容了。

那么问题来了，这段js代码都做了些什么呢？

我们先观察一下浏览器的加载过程。因为你已经成功打开了这个网页，浏览器已经记住了某些关键的cookies，所以你要先把cookies删除。

**如何删除Chrome浏览器记录的某个网站的cookies呢？**

打开Chrome的settings，按这个路径寻找cookies删除的地方：Advanced -> Content Settings -> Cookies
-> See all cookies and site data 。

然后在右上角的搜索栏搜索 mps.gov 就可以看到这个网站对应的cookies，把它们都删除即可。

打开浏览器的Network，选中“Preserve log”，记住加载的历史，然后用浏览器重新打开这个网址：

http://www.mps.gov.cn/n2253534/n2253535/index.html

可以看到Network记录的加载过程：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfmqH2cs7G2BDz012FwHTu2Zc4T140VRfcOicNpSAl9L0CvmoZztRGCCoRppxNic0HUyWjOT2UIibdAQ/640?wx_fmt=png)

观察发现，第一次返回了521，然后停顿片刻（实际上是1.5秒，后面js代码可以看到）再次加载该网页，可以得到正确的网页内容。

对比两次请求的cookies，可以发现第二次多了些cookies。 **这些cookies有可能就是521时返回的js写进去的**
。那么我们就来研究一下这段js代码。

**首先** ，我们需要一个js格式化的工具来帮助我们研究这段js代码。  工具很多，我们使用 https://beautifier.io/
。把代码copy到beautifier的网页格式化一下：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfmqH2cs7G2BDz012FwHTu2Zdb56QpZazEGjXYy1Q1ya2FHp9Y1cibOwF8lbU5pk1kPJnYPXoh2YfA/640?wx_fmt=png)

先来理解一下这段代码，1-16行没什么特别的。16行要eval()一段js代码字符串，这个很关键，看看它是什么。把 eval 改成
console.log，然后按F12调出Chrome的开发者工具，把全部js代码copy到 Chrome的Console运行一下：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfmqH2cs7G2BDz012FwHTu2QRS163UGf52OHbdj5w8jrHrxiaYlwNibUHeccOxmsuoe2QhmEaBIrzjQ/640?wx_fmt=png)

这时候，我们可以看到控制台输出了一段js的代码，把这段代码再copy到beautifier网页格式化一下：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfmqH2cs7G2BDz012FwHTu2cibGBMFaLSEr9kpytjibJeuKWX0XcNpydPeibKCarcmnGx8dhpNR8ZUYw/640?wx_fmt=png)

第4行可以看到，是给 document.cookie 赋值了，也就是给浏览器写入的一个名为 __jsl_clearance
的cookie。这个cookie的生成跟第4行最后那个 function 有关，看代码的样子，又是一段加密算法。

我们可以读懂这个function的实现用Python实现算法，但实际上这段代码太难读懂了。我们可以借助Python的
ExecJS、PyV8这样的模块来运行这段js同样也可以得到cookie的值。

有了cookie的值，我们在Python里面使用requests.Session
就可以来加载这个网页了。在Python中得到那个cookies并正确加载网页内容，是对你Python能力的考验，如果遇到什么问题可以留言讨论讨论。

**时常有读者在公众号留言给我交流，多次留言比较麻烦，这里开放我微信10个朋友圈名额，可以在微信上跟我交流，只限前10个好友申请。**

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEceYsrOvOkOLKXBO0JWPyluJkdXaAqa0YZH15ZH5p45bKEtLQ2qUKbfBeSPl1Wiboich4pw8A9tDYmHA/640?wx_fmt=png)
