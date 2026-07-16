# 某书新版登录流程逆向分析

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2020-09-08
> 归档日期: 2026-07-16
> 分类: mobile-app-reverse
>
> 某书网近些天，数据改成了只有登录才能查看。本以为登录轻轻松松就可以解决，没想到它竟然自己写了一段加密。所以写篇流程分享出来，希望能够帮助到大家；本文阅读前提，已悉知某数4代如何处理，而且网上还是有很多类似的教程，这里就不多加赘述了。

直接上干货

**一、前言**

某书网近些天，数据改成了只有登录才能查看。本以为登录轻轻松松就可以解决，没想到它竟然自己写了一段加密。所以写篇流程分享出来，希望能够帮助到大家；本文阅读前提，已悉知某数4代如何处理，而且网上还是有很多类似的教程，这里就不多加赘述了。

**具体流程：**

**1、请求登录页面**

熟悉的第一次202，第二次200（这里大家都知道，这202是某数的特点。首先，这个网站的cookie是不需要接后缀的，只要217位的cookie就能够正常

访问了）

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfDuL6QKBMBG5DDPgHgYCIvhAicSHnibEodEN5bAriaGADdQBRdu9IwkuFkO7I7ic3mmNabWNRGmD0cibQ/640?wx_fmt=png)

解决的思路当然是：处理第一次返回的content和js文件，拿到cookies，再请求一次该页面，此步骤只有一个目的，session保持，因为这个网站全站都有这个保护。只有先解开某数，做好session保持才能进行到下一步。

**2、请求登录api**

直接拿fiddler等抓包工具抓包登录接口，查看传值如下图

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfDuL6QKBMBG5DDPgHgYCIvFqJeiblH63TFau37xsKxVYzgek0XfBnfJkk9gtK72TiaNjHGz04quibcw/640?wx_fmt=png)

很明显，密码加密了，所以可以轻易判断，在请求登录的api之前，密码已经先加密了。下面分析密码加密：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfDuL6QKBMBG5DDPgHgYCIvHZXO1xdwCEf7EiaFMYOw9XicZst06wgdbSzQ0iasVVFgGDoy8oP0aO9qg/640?wx_fmt=png)

首先，登录页面打开F12，过掉debugger，全局搜索"password",在如图位置打上断点（我也找了一会，具体流程，跟一次就知道了，也可以打xhr断点），输入用户名，密码，点击登录断在这个地方，然后单步F11进入，就到图3所在函数，然后所需要做的就是扣下JSEncrypt，这里我采用的一把嗦原理，跟进JSEncrypt所在文件（图4），复制整个JSEncrypt所在文件，对加密函数稍作修改（图5），运行会发现缺少环境，补上

    navigator = { appName: 'Netscape'}window = global;

就能正常执行了，密码加密就算完成了，然后请求登录api，返回图6数据登录成功。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfDuL6QKBMBG5DDPgHgYCIv05yVNdOwsvjqVtTibRvBfibwDlHnG3Fa2wP34bLAQLQnmH8JUdSWBib3g/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfDuL6QKBMBG5DDPgHgYCIv3R8VDmvmEMBmSaEjrrIqcXuGibNJYI7zxeDkQ3eQyhyicr4AD1JDk7ow/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfDuL6QKBMBG5DDPgHgYCIv6ric0AZ2E4ZicSMIicZibVa9yIpwMbQdT6iblTjt14qbqKS5SWiac0B63r8A/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfDuL6QKBMBG5DDPgHgYCIvVBUxIyMA9gogJS95lMpOnISdO1zHsahSNe8HiabavYWE1fS1F6Q4f6Q/640?wx_fmt=png)

这里补充说明一下，如果不想费劲儿的找函数入口的话，可以直接全局搜索“AAOCAQ”

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfDuL6QKBMBG5DDPgHgYCIv9d1staHc5bMyIMuwU7kCCQdLic88xZbrYxz2oIBruVBtoMMeDZWeJPQ/640?wx_fmt=png)

直接就定位到这里。

**3、请求成功后请求验证api**

如图1所示，tongyilogin；返回url，如图2所示，session访问返回url，验证成功（暂时没发现改url返回数据怎么处理，session访问后，不做任何处理最后也能得到数据）

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfDuL6QKBMBG5DDPgHgYCIveLDpYoLMunZunl4jGdIDiaFg7Jdq7YIXZgW82EQ3BbtMSvLURRGs6icQ/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfDuL6QKBMBG5DDPgHgYCIv6daQxoicVtGbNspyVfFyFuhB6ibaNSrAanHhHKesuXSsuZ3L4oJMNYvA/640?wx_fmt=png)

**4、更新某数cookie(此步骤可以不要，但是最后可能出现202状态)**

步骤：session访问首页拿出content和js文件（或者处理第3步第二个url返回的content和js），然后像第一次生成cookie那样去更新cookie（提示：记得传入之前生成的某数cookie充当假cookie，否则会出现下图所示的cookie）

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfDuL6QKBMBG5DDPgHgYCIvkAIxQucYcoNHFUibRkf6Yib8cZZoRzhcWI4SL5BHdBQtnmiaqgkibxw7Vw/640?wx_fmt=png)

**5、请求用户状态接口**

如图1所示，用户信息接口返回的数据如图2所示，显示手机号或者邮箱则说明验证成功，如果是匿名用户则失败

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfDuL6QKBMBG5DDPgHgYCIvc2LOROwugzaI0KdLBib9icWvSUQzmvHmWiaIrjrmicUhrXKbmgKGaFJQMw/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfDuL6QKBMBG5DDPgHgYCIvofYvesJsbTBBRaRpQQA3WUjcuIw46WibWqdAHDynhdWzMKFdyicxl7Hw/640?wx_fmt=png)

**6、请求数据接口**

pid和token需和请求用户信息的数据保持一致，请求代码如图1，返回数据如图2，然后对得到数据进行解密就是最后的数据了，如图3所示

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfDuL6QKBMBG5DDPgHgYCIvKWMiadrur3GVsbh8kLLAzcyo1yEkAibeOByWGUWS1UGW2Gv0HCu9fltA/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcfDuL6QKBMBG5DDPgHgYCIvEc2lgeZ4nVDebLaunstkkIA3pPAqx6WyLvSTPEkXh5uOhciarUuB5aQ/640?wx_fmt=png)

**总结：整个某数的登录流程就是**

1\. 通过api/login 接口，传入账号密码（其中密码是密文），并获取返回的set-cookie HOLDONKEY

2\. 访问authorize 接口，传入 ‘client_id’、 ‘redirect_uri’ ‘response_type’ 、‘scope’、
‘signature’、 ‘state’、 ‘timestamp’。此时该接口会自然302跳转到接口CallBackController
接口，并且两个get传值已经自动配置好：’ code’ 和 ’ state’
（此时这个接口会有一个某数的html，个人建议利用这个某数接口（或者请求首页）再次 更新下443 cookie，避免cookie失效弹202）

3\. 随后访问数据接口/website/parse/rest.q4w

即可获取到个人信息

（这里要注意，获取数据的接口一定要重点关注的传值：

pageId cfg __RequestVerificationToken

缺任一都会报没有权限的错误）

4\. 继续访问/website/parse/rest.q4w接口，传入查询参数：如 ciphertext 即可获取到数据。

**写在最后**

一开始我以为改版后会在cookie里面添加用户信息，重新跟了一些发现并没有，并且和之前一样没有检测后缀；然后关键位置在登录后的请求验证api；用户信息和最后请求数据pid、token保持一致，数据api检测的是data中cfg，不需要后缀。（其中pid，token，ciphertext和最后的数据解密在改版之前就有涉及在此就不再赘述）

本篇来自noob（不是noob啦）的投稿。

PS：偶跟virjar出了个爬虫进阶课，包含JS/APP逆向抓取、安卓群控，爬虫工程经验。感兴趣戳下面。

[ 把爬虫高阶课又更新了
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448549536&idx=2&sn=fa53201a28ff10d8020587e75bf7f930&chksm=b2e8f9ed859f70fb4850a9598bc4ea182b62cb98d0acdafe8abadf646e87ad5ef9fa3a40caa2&scene=21#wechat_redirect)
