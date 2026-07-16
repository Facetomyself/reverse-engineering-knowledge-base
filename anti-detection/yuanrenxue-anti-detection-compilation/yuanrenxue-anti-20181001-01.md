# Python爬虫使用浏览器的cookies：browsercookie

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2018-10-01
> 归档日期: 2026-07-16
> 分类: anti-detection
>
> 很多用Python的人可能都写过网络爬虫，自动化获取网络数据确实是一件令人愉悦的事情，而Python很好的帮助我们达到这种愉悦。然而，爬虫经常要碰到各种登录、验证的阻挠，让人灰心丧气（网站：天天碰到各种各样的爬虫抓我们网站，也很让人灰心丧气～）。爬虫和反爬虫就是一个猫和老鼠的游戏，道高一尺魔高一丈，两者反复纠缠。

很多用Python的人可能都写过网络爬虫，自动化获取网络数据确实是一件令人愉悦的事情，而Python很好的帮助我们达到这种愉悦。然而，爬虫经常要碰到各种登录、验证的阻挠，让人灰心丧气（网站：天天碰到各种各样的爬虫抓我们网站，也很让人灰心丧气～）。爬虫和反爬虫就是一个猫和老鼠的游戏，道高一尺魔高一丈，两者反复纠缠。

由于http协议的无状态性，登录验证都是通过传递cookies来实现的。通过浏览器登录一次，登录信息的cookies就会被浏览器保存下来。下次再打开该网站时，浏览器自动带上保存的cookies，只要cookies还未过期，对于网站来说你就还是登录状态。

browsercookie
模块就是这样一个从浏览器提取保存的cookies的工具。它是一个很有用的爬虫工具，通过加载你浏览器的cookies到一个cookiejar对象里面，让你轻松下载需要登录的网页内容。

## 安装

` pip install browsercookie `

在Windows系统中，内置的sqlite模块在加载FireFox数据库时会抛出错误。需要更新sqlite的版本：
` pip install pysqlite `

## 使用方法

下面是从网页提取标题的例子：

    >>> import re
    >>> get_title = lambda html: re.findall('<title>(.*?)</title>', html, flags=re.DOTALL)[0].strip()

下面是未登录状况下下载得到的标题：

    >>> import urllib2
    >>> url = 'https://bitbucket.org/'
    >>> public_html = urllib2.urlopen(url).read()
    >>> get_title(public_html)
    'Git and Mercurial code management for teams'

接下来使用browsercookie从登录过Bitbucket的FireFox里面获取cookie再下载：

    >>> import browsercookie
    >>> cj = browsercookie.firefox()
    >>> opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    >>> login_html = opener.open(url).read()
    >>> get_title(login_html)
    'richardpenman / home &mdash; Bitbucket'

上面是Python2的代码，再试试 Python3:

    >>> import urllib.request
    >>> public_html = urllib.request.urlopen(url).read()
    >>> opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

你可以看到你的用户名出现在title里面了，说明browsercookie模块成功从FireFox加载了cookies。

下面是使用requests的例子，这次我们从Chrome里面加载cookies，当然你需要事先用Chrome登录Bitbucket：

    >>> import requests
    >>> cj = browsercookie.chrome()
    >>> r = requests.get(url, cookies=cj)
    >>> get_title(r.content)
    'richardpenman / home &mdash; Bitbucket'

如果你不知道或不关心那个浏览器有你需要的cookies，你可以这样操作：

    >>> cj = browsercookie.load()
    >>> r = requests.get(url, cookies=cj)
    >>> get_title(r.content)
    'richardpenman / home &mdash; Bitbucket'

## 支持

目前，该模块支持以下平台：

Chrome: Linux, OSX, Windows
Firefox: Linux, OSX, Windows

目前该模块测试过的浏览器版本还不是很多，你使用过程中可能会遇到问题，可以向作者提交问题：

https://bitbucket.org/richardpenman/browsercookie/

如无特殊说明，本号均为原创，转载请注明：来自微信公众号“一再学习”

![](https://mmbiz.qpic.cn/mmbiz_jpg/GrTTsqWuEcf0gicwByDpgFGF9RY4NsG95BOo3rEMtqibjNga7jSdzowp6A2eibvuZ2YtcVFhl7iazgevdylu6vhb7A/640?wx_fmt=jpeg)

欢迎关注微信公众号阅读最新文章
