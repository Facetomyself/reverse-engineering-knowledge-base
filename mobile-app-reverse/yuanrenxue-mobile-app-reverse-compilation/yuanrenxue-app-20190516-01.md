# 让你的爬虫无障碍抓取上千万需登录的APP数据

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2019-05-16
> 归档日期: 2026-07-16
> 分类: mobile-app-reverse
>
> 爬虫论抓取难度，一是抓取对内容有加密的，难度很大，尤其是在app端的内容加密。有的可能需要逆向app。二是抓取必须要登陆后才能看的内容，再加上对登陆账号做IP访问次数控制的。这可能会难道一大片爬虫选手。

爬虫论抓取难度，一是抓取对内容有加密的，难度很大，尤其是在app端的内容加密。有的可能需要逆向app。二是抓取必须要登陆后才能看的内容，再加上对登陆账号做IP访问次数控制的。这可能会难道一大片爬虫选手。

本文不讨论app逆向问题，这种问题似乎也不宜公开说，《刑法》第286条中阐述了反编译软件属于破坏计算机信息系统罪。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcd5LcUOE2Mr2ic06AW6mkgxncbeXqrOcZwmIJH0z9HLwfDpNzAM98BYs1hTL8u9xynUhLW2me3DEmA/640?wx_fmt=png)

如果是被举证了，风险挺大的，尤其是竞品之间的抓取行为或者太高调的。我在猿人学Python这两篇文章中有写到爬虫抓数据的法律风险。《  [
写网络爬虫的法律边界
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548074&idx=1&sn=af01bfd939d4c54802bd12c365c81ac9&chksm=b2e8ffa7859f76b11f84cdbc9022a31c048960a513bb0981cd4b65eb4961247871f4b651b038&scene=21#wechat_redirect)
》、 《  [ 再续：网络爬虫的法律边界和数据风险
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548089&idx=1&sn=24922535fb21ea512db5c3333a5af8e4&chksm=b2e8ffb4859f76a240a3f6b54f8440425846c10e0ad3189811991bf36e7a2af8bfd7e7d7ad5a&scene=21#wechat_redirect)
》

**本文讨论第二种，内容没加密，但要登陆才能看的app如何抓取。**

写爬虫没有学校教授，所以没有统一的武功套路，基本是八仙过海，各显神通。厉害的数据公司各种武功套路的人才齐备，账号，IP，机器等渠道资源充足。一般的公司资源和人才不够，又想大规模数据抓取，用取巧的方式是一种可行的办法。

本文说的取巧抓取方式，就是正确的设计抓取策略， **通过制定正确的抓取策略来高效抓取需要登录的APP。**

制定正确的抓取策略，包括使用和熟悉被抓对象的产品形态（PC，H5，APP）和功能；测试被抓对象账号登录后对不同频道的访问频率控制边界（比如有的只对产品详细页做频率控制，对频道页，分类页的控制较弱）。分析被抓对象分享到微信等渠道后，从微信打开页面是否需要授权，需登录等情况。

这是一套通用的抓取策略分析手法， **我运用这种策略对多数APP都能做到抓取上千万条数据。**

理论说的比较晕，我们拿脉脉APP来举例，如何来分析和制定抓取策略。

我们的目标是想要抓取脉脉上的个人职业信息（这类数据不要直接商用，简历也算是个人隐私数据）。

按照三面的分析步骤，首先分析脉脉的产品形态。初步分析，脉脉的PC网站需要登录，没有专门的H5网站，APP也需要登陆才能查看。初步分析，没有可以下手的地方。

第二步分析对各版块的频率控制情况。这要自己花点时间去点击观察。测试结果是对个人的详细页频率控制强，还有对搜索功能控制强。对分类等频道页控制很弱。大约一个账号快速访问200多次详细页，就会有提示了。

这就意味着如果一天想抓10万张脉脉详细页，需要注册10万/200=500个账号。如果是一天抓100万张页面就要5000个账号。这样算下来其实公司出钱买几百个账号，也要不到几个钱，但是好些公司不愿意出这个钱。

所以通过批量注册账号的方式，就打住了。另外上面说的这种用大量账号抓取的方式，我简化了IP问题，一个账号频繁变换IP也是有问题的，尤其是IP归属地一会是江苏，一会是江西就更有问题了。

上面第一二步都分析了，似乎没有找到什么好方法，接着分析第三步，观察详细页的分享功能。
**我把详细页分享到微信后，在微信里试着打开看看，发现可以不登陆就能访问详细页。**

![](https://mmbiz.qpic.cn/mmbiz_jpg/GrTTsqWuEcd5LcUOE2Mr2ic06AW6mkgxnlPVqSU9icITiaRicXeHV3j5VHsWrPvPR9nHsbeCtfwuZWxRnGlDyR0prg/640?wx_fmt=jpeg)

这下似乎找到了抓取突破口，赶紧抓包具体观看一下。

通过抓包分享到微信这个过程的数据可以分析出：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcd5LcUOE2Mr2ic06AW6mkgxnxIlAAVE3U5wWpVKuwZ1KYR8Uiaa4wtdz31XwenawmC7czH5TTKesAsw/640?wx_fmt=png)

点击分享到微信，会触发访问

https://open.taou.com/maimai/user/v3/share_other?u=xxxxx&access_token=xxxxxxx&u2=xxxxxx
这个URL。

这个URL会返回另一个URL，即https://maimai.cn/contact/share/card?u=2k6qxxxxxxxx （如图），
**这个URL可以不用登录就能访问。**

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcd5LcUOE2Mr2ic06AW6mkgxnI7nFI4jQaHAuf4sWoZs8OVHHVwdTbhicWiaZrSWOh5r4HXwcLIFqic7KQ/640?wx_fmt=png)

而且点击分享这个功能的频率控制经过测试，是比较弱的。

所以抓取策略慢慢就清晰了：登录APP后，把要抓取的对象分享到微信里（即，访问这个URL

https://open.taou.com/maimai/user/v3/share_other?u=xxxxx&access_token=xxxxxxx&u2=xxxxxx）。

得到无需登录就能访问的这串URL。

https://maimai.cn/contact/share/card?u=2k6qxxxxxxxx。有了这个无需登录的URL，就可以靠我写的这篇《如何让爬虫一天抓一百万张网页》的方法，欢快的抓了。

脉脉登录问题很好解决，上面那个分享微信接口的URL参数里只需传递一个ID和access_token就认为你登录了，id和token通过抓包可以很好拿到。

**这样我只需要登录的账号不停的访问微信分享功能**
，其他的抓取事情就可以交给无需登录，只需大量IP就能抓取到了。这样就大大缓解了对登录账号的访问频率控制。

但是依然要自己注册一些账号，只是不用注册几百个那么多，我自己手动注册二十来个就可以每天抓一百万个页面了。

因为注册要检查你手机上的电话号码，电话号码都是一样的，注册会有问题。所以可以用安卓模拟器去注册账号。

上述介绍的就是一种取巧的抓取策略，不过适用面还挺大的。在一个公司的资源不够，不肯出钱解决问题时，上述是 **一种低成本的抓取策略。**

但是随着被抓对象的产品改版，或者频率控制改变，这种方法会失效。但是一款产品总有能找到的抓取软肋，因为一个公司的技术和市场部门是分开的。市场承担的产品日活，访问量责任更大，所以会倾向于用户分享到微信的页面能够直接打开。利于他们做拉新，裂变之类的，所以控制力度就不大。

猴赛雷的数据公司不屑于用这个取巧的抓取策略，因为这种抓取方法遇到改版或爬策略改变，就会失效，导致抓取失败。这些公司是直接卖数据给客户，要保证服务质量，会使用暴力的方式来抓取，后面可以聊聊这类的爬虫江湖暗战。

你懂的，我最近在教爬虫，一对一教会你如何设计大型爬虫，我十余年的经验倾囊相授。 感兴趣的在菜单里你能找到我。

**近期爬虫好文推荐**

[ 如何让爬虫一天抓取100万张网页
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548659&idx=1&sn=d2a8dd3544bfd7980c8ab1fbb0c5dd4b&chksm=b2e8fc7e859f7568b41fcc55b384e9d78a4c4503707ac34c890a3be17ecfe2d40df4bc3602d5&scene=21#wechat_redirect)

[ 爬虫技巧：逆向破解js代码加密，代码混淆不是难事
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448548692&idx=1&sn=ccd73a67ee615c8111eb28319d388919&chksm=b2e8fc19859f750f972d9e9e954576bdef0fe2ea2f3252e42aeb979b853dd642a9488b7898b8&scene=21#wechat_redirect)

一个十年Python码奴与运营汪的结合体

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcc7Za1a7QsXkVtF1M39yqf1D4fkPlVCNZgq8y9y5988NFqZ7wEhQMian6W795zMbkdib6TtUIsnPb8Q/640?wx_fmt=png)

长按扫码关注
