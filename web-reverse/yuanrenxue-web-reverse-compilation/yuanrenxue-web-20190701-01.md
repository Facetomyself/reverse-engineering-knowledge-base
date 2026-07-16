# 写爬虫时常见的五种字符串加密特征

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2019-07-01
> 归档日期: 2026-07-16
> 分类: web-reverse
>
> 今天偷个懒写篇总结性的文章，我们在写爬虫，对网络抓包或逆向一些token参数时常常遇到一长串的字符，看到一长串不知其意义的字符串往往有点懵圈。如果你靠肉眼能从这一长串字符中看出一些特征或含义，那么会加快你写爬虫解析网络参数的步伐，也能给你提供分析思路。

今天偷个懒写篇总结性的文章，我们在写爬虫，对网络抓包或逆向一些token参数时常常遇到一长串的字符，看到一长串不知其意义的字符串往往有点懵圈。如果你靠肉眼能从这一长串字符中看出一些特征或含义，那么会加快你写爬虫解析网络参数的步伐，也能给你提供分析思路。

这篇文章就是总结一下常见的字符串编码的格式和特征。

**URL编码**

请求URL的时候通常看见以%开头的字符串，这一般是对字符做了URL编码处理。

    http%3A%2F%2Fwww.yuanrenxue.com%2F

比如上面字符串，经常看的话其实你就知道上面的含义，%3A是: %2F是/ 。

解码后的完整URL其实是：

    http://www.yuanrenxue.com/

可以使用urllib.parse.quote做URL编码，用urllib.parse.unquote做解码。比如我们对 猿人学 三个字做一下URL编码：

    >>import urllib>>st = '猿人学'>>enc_st = urllib.parse.quote(st)>>print(enc_st)>>%E7%8C%BF%E4%BA%BA%E5%AD%A6>>>>urllib.parse.unquote(enc_st)>>猿人学

%E7%8C%BF%E4%BA%BA%E5%AD%A6 这一串就是猿人学URL编码

再用urllib.parse.unquote对这一串解码就是猿人学三个字。

Python中做URL编码一般是对特殊字符做编码处理，你可以简单认为对非英语字符做编码处理，实际上我们在写爬虫分析对方JS时，你会发现对方把英语字符也做了编码处理。

同样的 http://www.yuanrenxue.com/ 这串在Python一般编码后是：

    http%3A%2F%2Fwww.yuanrenxue.com%2F

在Javascript中可以是这样：

    %68%74%74%70%3A%2F%2F%77%77%77%2E%79%75%61%6E%72%65%6E%78%75%65%2E%63%6F%6D%2F

它是对所有字符都做了编码。

**Unicode转义**

有时你打开一张网页，想分析下它的网页结构，发现网页里全都是密密麻麻的&#开头的字符，完全不认识，例如是这样的：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfQDicoYARiancx4JfEu9AQ0O9yerSSzVgEuSLiaYUA0hA1g0t34ic4iajdqlMCGAsTdyFSGSmRA4SNhcQ/640?wx_fmt=png)

看得人头晕，但是它有一个特征都是以&#开头，以;结尾的。这是HTML中一种Unicode转义，在网页中做Unicode编码就是这样子的。

我们来测试一下：

    >>import html>>>>s = '''&#20170;&#22825;&#20599;&#20010;&#25042;&#20889;&#31687;&#24635;&#32467;&#24615;&#30340;&#25991;&#31456;&#65292;&#25105;&#20204;&#22312;'''>>>>print(html.unescape(s))>> 今天偷个懒写篇总结性的文章，我们在

如上代码，我们使用html.unescape可以还原这些文字，还原出来的文字是我这篇文章的开篇词。

**16进制Unicode转义**

上面的Unicode转义是 这样：

&#20170;&#22825;&#20599;&#20010;&#25042;

&#后面是的数字是10进制的，还有一种&#后面是16进制的，比如：

    >>import html>>>>s = '''&#x4ECA;&#x5929;&#x5077;&#x4E2A;&#x61D2;&#x5199;&#x7BC7;&#x603B;&#x7ED3;&#x6027;&#x7684;&#x6587;&#x7AE0;&#xFF0C;&#x6211;&#x4EEC;&#x5728;'''>>>>print(html.unescape(s))>>今天偷个懒写篇总结性的文章，我们在

也是用html.unescape可以还原。

**UTF-8编码**

\u4eca\u5929\u5077\u4e2a\u61d2\u5199\u7bc7\u603b\u7ed3\u6027\u7684\u6587\u7ae0\uff0c\u6211\u4eec\u5728

\u后面加四个字符的是UTF-8编码

转换很简单：

    >>s = '\u4eca\u5929\u5077\u4e2a\u61d2\u5199\u7bc7\u603b\u7ed3\u6027\u7684\u6587\u7ae0\uff0c\u6211\u4eec\u5728'>>print(s)>> 天偷个懒写篇总结性的文章，我们在

Python内部会转换。

**base64编码**

写爬虫抓取时，常常会看到token里带有类似：eXVhbnJlbnh1ZS5jb20=

这样的字符串，常常字符串后面以=结尾的，很可能就是base64编码了的。

    >>import base64>>str = 'yuanrenxue.com'>>bytesStr = str.encode(encoding='utf-8')>>b64str = base64.b64encode(bytesStr)>>print(b64str)>>b'eXVhbnJlbnh1ZS5jb20='

如上代码，我们对yuanrenxue.com做base64编码出来的是以=结尾的。

**总结：**

1.以%开头的一般是做了URL编码的，用urllib.parse.unquote()解码。

2.以&#开头的一般是做了Unicode转义处理，html.unescape()做反转义。

3.以&#x开头的是做了Unicode 16进制转义，也用html.unescape()做反转义。

4.以\u开头的是一般是UTF-8编码。

5.字符串后面以=结尾的，通常是做了base64编码处理的。

\--------------

PS：最近晚上都忙着给跟着我学习爬虫的同学上课，上周只写了一篇公众号，这周会应能恢复一周两篇。

持续三个月的爬虫课，只教了一个半月左右，已有几个同学找到爬虫工作，自我感觉还是不错。七月我会继续教，教会你：

1.海量爬虫的抓取策略和抓取窍门

2.JS/APP逆向

3.自己动手设计分布式爬虫框架

适合致力于找爬虫工作，和爬虫技能进阶的同学。  在公众号菜单栏你能找到我的微信。

关于我：

[ 分享我曾经的学习和找工作经历
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548394&idx=1&sn=ea69e18918d25b1a54b43b4cbaa7dfbe&chksm=b2e8fd67859f74714d635fd57b00e64aaed34616843ef146274f971c5321b59b31da9a46eedc&scene=21#wechat_redirect)

爬虫过往好文：

[ 如何让爬虫一天抓取100万张网页
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548659&idx=1&sn=d2a8dd3544bfd7980c8ab1fbb0c5dd4b&chksm=b2e8fc7e859f7568b41fcc55b384e9d78a4c4503707ac34c890a3be17ecfe2d40df4bc3602d5&scene=21#wechat_redirect)

[ 大规模爬虫为什么要管理DNS缓存
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548842&idx=1&sn=f15ed2a129c3137b3411859285f48998&chksm=b2e8fca7859f75b1260376b2adc1ba5a0c5587dbfcd8e5b4e573163f07e530c884c20d0b1c54&scene=21#wechat_redirect)

[ 大规模异步新闻爬虫的分布式实现
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548782&idx=1&sn=d94410db4dbb3ea143ba07635db758b8&chksm=b2e8fce3859f75f5ce1551cfc6dfb1dc2ad1116a42aaf663944431b2fefbe6f4676bf97eadd9&scene=21#wechat_redirect)

[ 大规模异步新闻爬虫的实现思路
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548722&idx=1&sn=b25b5ea8748523f966ce430845133252&chksm=b2e8fc3f859f7529cfcd85864e06daab3910bd731318d6fa4b8a1d92d36fdc0320362a7fd300&scene=21#wechat_redirect)

[ 爬虫技巧：逆向破解js代码加密，代码混淆不是难事
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548692&idx=1&sn=ccd73a67ee615c8111eb28319d388919&chksm=b2e8fc19859f750f972d9e9e954576bdef0fe2ea2f3252e42aeb979b853dd642a9488b7898b8&scene=21#wechat_redirect)

[ 浅谈利用爬虫技术成就的那些商业公司
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548376&idx=1&sn=5a2e18c1857671a4bc230b00a1920987&chksm=b2e8fd55859f7443b6c4dfab1e92e9db5b7b09fcf107d9be00d49690e76c2bae43e1373b4178&scene=21#wechat_redirect)
