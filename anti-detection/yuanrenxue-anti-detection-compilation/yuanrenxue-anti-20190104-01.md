# 不要相信requests返回的text

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2019-01-04
> 归档日期: 2026-07-16
> 分类: anti-detection
>
> Python的requests库是一个非常好用的库，这应该已经是大多写过爬虫的人的共识了。它的简洁易用给我们带来很大方便。然而，它也并不是非常完美。今天我们就说说它在处理中文编码方面的不足。

Python的requests库是一个非常好用的库，这应该已经是大多写过爬虫的人的共识了。它的简洁易用给我们带来很大方便。然而，它也并不是非常完美。今天我们就说说它在处理中文编码方面的不足。

requests的使用非常简单，如下：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdnynlYefHGbBic9Dy9Zh0UUN0dibWmiaSLjSBn2vOdFZkjsIzyEr0uQaCIhE0zDtgA08otsicibL5iaC4g/640?wx_fmt=png)

一句函数调用，就可以获得请求结果的对象response，通过response.content
可以得到原始的二进制数据，通过response.text可以得到解码后的文本数据，解码是根据response.encoding进行的。然而，requests对这个encoding（编码）的获取是有问题的。

它获取编码的过程分为两步，不幸的是每一步都有问题：

**第一步：从http返回的headers里面找编码。**

这一步的代码在源文件utils.py里面是get_encoding_from_headers(headers)函数：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdnynlYefHGbBic9Dy9Zh0UUTPSvDF3RAicEa2BmAZSib8D6xuB9wdaywS8icIUQUAzazRAcOyJr4VOZQ/640?wx_fmt=png)

最后两行代码，它认为headers里面的‘Content-Type’包含‘text’就是‘ISO-8859-1’编码。这种想法是不严谨的。

我们用chrome浏览器打开最开始代码中的那个网址，这是一个中文网页：

**http://epaper.sxrb.com/**

在用Chrome的F12查看http响应的头，如下：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdnynlYefHGbBic9Dy9Zh0UUZnqvztEx3ZvkichL52MXPCM3xAb2AAYhjSXpRicSJumicahUxicNx689Dw/640?wx_fmt=png)

这个网站给出的Content-Type不是下面的正规格式：

**Content-Type: text/html; charset=UTF-8**

然后，requests的get_encoding_from_headers函数就得到了
ISO-8859-1的编码，再用这个编码去解码中文，当然就会出现乱码。

**第二步：如果不能从响应headers得到编码，就用chardet从二进制的content猜测**

严格讲，这步出现的编码问题不是requests的，而是chardet的，就判requests一个失察之责吧。

在requests的源码models.py中定义了requests.get()返回的类Response。我们再看看其中text()的定义：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdnynlYefHGbBic9Dy9Zh0UUicJ2oa59l1YxOlQmBpE9OEAQm71MmFGico1SXb2UtfeOV1RL1qQg0ia2Q/640?wx_fmt=png)

响应头找不到编码时，self.encoding就是None。它就会通过self.apparent_encoding获得编码，那就再看看这个apparent_encoding是怎么来的：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdnynlYefHGbBic9Dy9Zh0UU3kl3kxXxT3KNYuibbGxGNcpx25icNBVAwichtZVribroVIkY06kicTAgZqQ/640?wx_fmt=png)

很简单，就是通过chardet检测的。问题就出现在这个chardet上面。那我们就打破砂锅问到底，去看看chardet的代码。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdnynlYefHGbBic9Dy9Zh0UU1XY42op3Q7HGImbYrqfDJ37IKjmMLEwl1bD6H1XDL83uOfjyPheNBQ/640?wx_fmt=png)

上图是chardet的全部源代码。其中处理国标中文编码的gb2312开头的两个文件。我们用grep再看看全部代码中含有gb的部分：

** grep -i gb *py  **

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdnynlYefHGbBic9Dy9Zh0UUorDib9sxLHTUrRh3iaiaBVSARibibpNXQHRqcc6gCHjN1zHUnMFI6xE8RBQ/640?wx_fmt=png)

以上说明，chardet对国标中文编码返回的就是（只是）GB2312。那么问题就来了，国标不只是GB2312，还有GBK，GB18030编码。

**（1）GB 2312 标准共收录 6763 个汉字**

**（2）GBK 即汉字内码扩展规范，共收入 21886 个汉字和图形符号，兼容GB2312**

**（3）GB 18030 与 GB 2312-1980 和 GBK 兼容，共收录汉字70244个**

由此可知，三种国标中文编码的汉字个数是如下关系：

**GB2312 < GBK < GB18030 **

如果不属于GB2312的汉字用GB2312去编解码会出现上面问题呢？我们来做个实验：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz0r4A2iaX1FR7PccWffVCVTqTjFuOcbXAlR4N4N12Yy6qZnVc0Kps2Vcc3SkTjjMiaNp5XvtfHpWA/640?wx_fmt=png)

例子中的“镕”字不在GB2312中，用这个编码时就会报错，用GBK编码后的二进制数据再用GB2312解码时同样会报错，都是因为“镕”不是GB2312里面的汉字。

这时候，我们像requests那样把errors设置为replace再用GB2312解码得到的文本就会有乱码出现，“镕”字变成乱码了。

最后我们用chardet检验二进制数据的编码，得到的是GB2312，但应该是GBK或GB18030编码。当然，chardet的这个bug已经有人在github提出issues，最早是2014年的#33，
后来有#99，#168，但是不懂中文的老外一直没有merge到master。

问题弄明白了，那么建议是什么呢？在爬虫中，尤其是抓取中文网页（非英文网页）时用cchardet检验response.content，而不是直接用response.text。

cchardet是uchardet的Python绑定，后者是用C++实现的字符编码检测库，来自Mozilla组织，质量过硬，速度更快，值得信赖。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdnynlYefHGbBic9Dy9Zh0UUvPXN1e1NpZXe84ib8290ASdOOtf8IESWFrM9eeZeAicozF9yicS5YySgg/640?wx_fmt=png)

\--------------------------------------------------------------

一个写Python十余年的码奴

\-------------------------------------------------------------

![](https://mmbiz.qpic.cn/mmbiz_jpg/GrTTsqWuEce2yoT3xt5Oo8wFb4u5tpRxBMomDWxdleyLLlIJUFcdDQYzWJbFl3nG2EH246Vfb4Jg7tXfnZ2uKA/640?wx_fmt=jpeg)
