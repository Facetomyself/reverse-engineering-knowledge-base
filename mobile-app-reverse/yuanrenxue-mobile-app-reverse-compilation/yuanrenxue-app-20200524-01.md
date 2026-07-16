# 分析app的登陆协议

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2020-05-24
> 归档日期: 2026-07-16
> 分类: mobile-app-reverse
>
> 从登录请求抓包开始，分析账号密码、动态参数、响应数据与 JavaScript 加密调用，形成可复现的模拟登录路径。

本篇来自读者：海边的小米粥投稿。

**1\. 抓包** **
** （1）
抓包前将手机和电脑连接到同一WIFI，在手机设置好代理，装好证书，就可以开始抓包了。之前我遇到抓不到包的情况，换了几个代理工具也不行，最后是开着热点抓到包（一台开热点，另一台和电脑连接热点），或者换成手机抓包工具HttpCanary等也可以抓包。
（2） 抓包环境配置好后，在登陆界面随便填一个账号密码：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TibPTwYUhyfGjpF2iaFb5lrn5MxhHwibqcjwHqpXYTCK4rHmpp5NeBGPwQ/640?wx_fmt=png)
（3） 点击登录，查看Fiddler中的数据包  数据包中的参数：  city=%E5%8C%97%E4%BA%AC%E5%B8%82
&citycode=010  &device=63ac32df-d1c2-3008-828e-ef9f1bb3a96d
&device_model=google%20Pixel%202  &device_name=google%20Pixel%202
&device_os=Android%205.1.1  &device_product=google  &device_size=1080*1920
&device_type=1  &district=%E4%B8%9C%E5%9F%8E%E5%8C%BA  &fake_id=37979341
&interface_code=620  &latitude=39.91640353732639
&longitude=116.41024359809028  &mobile=13426355456
&password=<encrypted-password>
&province=%E5%8C%97%E4%BA%AC%E5%B8%82  &province_code=1582770774000
&version=6.2.0  &securitykey=41de91b2c71d0af71c7a71887e14b57d
一般需要抓两次包来对比数据包参数的变化，观察哪些参数是固定或者容易得到的，哪些是不能直观看出需要进一步分析：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0Tt8tR3IHp0yklqicAQ04mic4DJTN0QGWBsERjFSiaAMr01gP3LIW1gNYnA/640?wx_fmt=png)
对比两个数据包可以看到，手机号没有加密，密码做了加密，还有一个参数securitykey也是加密的。这次逆向的重点也就是分析这两个参数的生成逻辑。
**2\. 脱壳** **
** （1） 直接把apk用jadx反编译，发现做了加固，是legu的壳，相关逻辑代码没法直接看到：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TUZ3q390VpQOe4kmNP1DpehdxEibDoic5zhyfsOaU3bLjJdHY4ObgVVDQ/640?wx_fmt=png)
（2） 这里我使用了一个基于frida编写的脱壳工具：  https://github.com/hluwa/FRIDA-DEXDump
原理是在内存中暴力搜索，根据dex文件的结构特征将其dump下来，启动frida-
server，启动app，运行脚本就可以了。如果使用过程中报错，可以试试重启手机，或者杀死app进程并重启app。
**3.分析加密参数securitykey**
（1）之前抓到的包是分析的入口点，在jadx中反编译dump下来的dex，点击菜单栏的小魔法棒搜索securitykey这个参数：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TmoYVhw2IcLC1FibAbRuGayWlvdibq194MBUia0Dvc0ibLiaEcH5hhI3Z7eQ/640?wx_fmt=png)
结果如下;第四个GLOBAL_PARAMS_KEY = "securitykey"比较显眼，双击打开看看，也可以把右边所有结果挨个点开分析：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TcmYgIUzqa6AxYqjDdFKecBwsHjv8HVO1we7BeRamVtuc4FLjHV7ujQ/640?wx_fmt=png)

观察代码，securitykey参数应该是在其他位置被引用，右键GLOBAL_PARAMS_KEY，选择查找用例，看看哪些地方用了这个参数：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0T9fBMia1dd0zjkYutAQEpXAibGmB99MCRVzuZeHMAglDYicGlCVDEW55Bw/640?wx_fmt=png)
根据经验推测，第二个stringBuffer.append一般是数据包参数构造的位置，双击打开它：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TuAxzPLFS2XHWHrP58gphj2mbwawIfWlPQCriczrfvXF6VE988bQ1K1Q/640?wx_fmt=png)
GLOBAL_PARAMS_KEY的值就是securitykey参数，接着拼接了一个“=”和一个finalSecStr的变量
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TZkzawv5sygZxjRhib2bhuTPFJx2AMe8LYe2bbmichibOgwUvdxTxClsAA/640?wx_fmt=png)
双击这个finalSecStr变量，可以看到finalSecStr在代码中的处理逻辑，可以看到是经过getMD5Str这个方法处理得到的，看函数名感觉是计算MD5：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TiawP9fSSZaHclJMImA7rOlibevoC2QJiafVMsZtnpyBMeaoI1hWaCh21Q/640?wx_fmt=png)

继续看getMD5Str的参数secStr，发现是由this.paramMap处理得到：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0Tqiarw7RhiaZnsHVBeed93bv97mNU9FhFnkWKaqJQ2fnZBIwFRax4qhTA/640?wx_fmt=png)
再往上分析，发现this.paramMap中值就是数据包那些参数：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TIJ25hNOJ3kI12PAnTQkd1Q9J1C828RUgCk3yCvia3PuibOmBXXAdaiaHg/640?wx_fmt=png)
自此，securitykey这个参数的计算逻辑差不多出来了，把this.paramMap中的参数挨个拼接“|”变成secStr，再传给getMD5Str，返回的值就是数据包中securitykey的值。
按住Ctrl键，单击getMD5Str这个方法，可以看到就是MD5  的计算：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TfoAEugMVBC31ViaHN0gL9fLBweMOznMFQT5R7SibracLVjIENxlH3f5g/640?wx_fmt=png)
点击菜单栏中的向左小箭头返回上一层代码：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TUwjclqx6K0g4AykgpMpwLjSjiaEt1LKw44XNAtHPw91KK6eMd67d9lA/640?wx_fmt=png)
我们可以通过hook
getMD5Str方法，将其参数和返回值打印出来，验证我们的分析。这里涉及到一个问题，这个app加了壳，直接去hook会出现“ClassNotFoundError“的错误，这是因为getMD5Str这个方法不是一开始就在内存中的，它是被壳加载起来的。所以hook方法要有所改变。
**4.加壳和MultiDex情况下如何hook**
原理：所有的类都是通过ClassLoader的loadClass方法加载的，于是可以等我们要hook的这个方法所在的类被加载后再去hook，这样就可以百发百中了，多个DEX的情况下也可以使用这个方法
该方法出处：  https://bbs.pediy.com/thread-225190.htm
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0Tx9AFeYUR6eRQlrJtUPCaF6ODwbAYSlJoYD0CJSLWCgRmeTIrU8b9xQ/640?wx_fmt=png)
Hook
getMD5Str方法后打印参数和返回值，编译安装xposed插件，重启手机，结果发现什么也没hook到，确认类名和方法名，参数都没问题。经过长时间的分析也没结论，最后是用ddms发现了问题：jadx反编译得到的类名，方法名不正确，与真实命名不一样。
%1. ddms的使用
ddms是一个AndroidSDK自带的方法追踪工具（一般位于SDK的tools目录下），用于记录app执行过的方法。这里我们需要记录的是点击登陆按钮后app执行的方法。打开ddms后，先选中app对应的进程，然后选择菜单栏中的“开始追踪”
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TOdgvZcwmata5iciaZpsOyQKUIpbxEpicdNT8cnmblx3KWlEKBV12nQ0pQ/640?wx_fmt=png)

选择第二个，记录所有方法
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TPmxCnG9C4NHY7ia0gicaLMpicaTxb3NoxE2ZbtFaLgHkW8XiaSUJkQW82w/640?wx_fmt=png)
接着以最快的手速点击登录按钮（因为ddms会记录系统中在运行的很多进程的方法），等到弹出“该账号不存在”（因为我们随便输入的），立即点击ddms的“停止追踪”按键（跟“开始追踪”是同一个，不过现在变灰了），就能得到从点击登陆按钮后到账号校验完期间app执行的所有方法：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TpPDOIiamA2gC1hX8H01ibyicNA0mVYDScQ9bKt0yTRmvN2e4cllhnVVTw/640?wx_fmt=png)
接着会弹出一个trace文件，就是记录下来的方法：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TAG9paJyvF71JNALib6MerZPBX31OWtffFYo4vfbjibYmCQB1sEHiaQKzA/640?wx_fmt=png)
在最下面find搜索栏中输入app的包名，按回车键挨个观察记录下来的方法，在其中找到了getMD5Str方法的正确类路径，而之前在jadx中反编译得到的是：
com.XXXXXX.common.utils.encrtption.MD5Helper.getMD5Str
所以用jadx中的类路径肯定是hook不到getMD5Str方法了。
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TkxLAGMzZY16Of8C8sKzJPAGHFbgQiabksCnubZ6dgqO0EPtpna2RBXw/640?wx_fmt=png)

把类路径改成ddms记录的正确路径，重新编译hook插件，重启手机，运行app，输入账号密码，点击登录，在ddms的日志中可以发现，这次顺利的打印出了getMD5Str方法的参数和返回值：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0Trb4TWFqTNHY0cYWK2gOHTqNXw6H7ibrbuuTuhgDBjTe5DERkH7gjPVg/640?wx_fmt=png)
对比数据包参数：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TydibTg8znVcPAMeIfjdLfCPySarJlibibicjEoib6SibFWOGJya0Fv1Yhu2w/640?wx_fmt=png)
将getMD5Str方法的参数与数据包中参数对比，发现是一致的，返回值就是参数的MD5值，验证了我们之前的分析是对的：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TZibaNMv83HJY8qrpicSlCBQPsiccMYvAWF48RQ1NNicps4uhw3cR3oEQxQ/640?wx_fmt=png)
%1. password参数的分析
分析完了securitykey这个参数，现在就分析password这个参数，可以发现，并没有在大量参数构造的地方发现password：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TIJ25hNOJ3kI12PAnTQkd1Q9J1C828RUgCk3yCvia3PuibOmBXXAdaiaHg/640?wx_fmt=png)
在jadx中搜索也没有发现：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TRUjRf8WqicwwSoAhMsmPhsyuiciaGxcTFVycQ60vBRBWhTI2z3D2j7vgA/640?wx_fmt=png)

观察上面的参数，他们都是带着双引号的，尝试给password加上双引号搜索，终于看到了：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TNHwjA5jYQPicNYjsqEj9rfOH2P1poiaibpDyrUsu6AJbHhP9BKPpEx8Hw/640?wx_fmt=png)
第二个看着像是AES加密有关的，双击进去看看，果然是：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TzzAtfhEs1nTwurc9F75e0NGQ7Cm0K9MGnbDIJ6PiaUEzzvupDeQ7v6w/640?wx_fmt=png)
按住Ctrl，点开AesEncryptionHelper看看，是"AES/CBC/PKCS5Padding"的加密方法：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TyFibqCvyDaHFYGVtUVbYGRA5bywenTnJRbM9NcP3v2HK1DxOUKfia37w/640?wx_fmt=png)
验证一下：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TVtT68P5JVZ7J5a8Cr6qKGCTtBYy8DCJgicOs2jDNSEVtrsyJuDI6myQ/640?wx_fmt=png)
跟数据包中的password的值是一样的：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcdz7Cuqib2riaWibrWGsXvOQ0TzqPiaLLzUjVeo9fXyzvPkelmlUlDOABUKeGD80H4cZpt8fhBryVKVBw/640?wx_fmt=png)
自此，两个加密参数的分析就完成了。
**PS：自己的广告** [ 正式把爬虫高阶课放在网课平台了
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448549375&idx=1&sn=9726b58dadcc220bbea6aa48eed694ca&chksm=b2e8fab2859f73a4076692e6368b1701371e2f9afa10f4f3bb3725abe51604e49e5b1e82028c&scene=21#wechat_redirect)
[
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448549375&idx=1&sn=9726b58dadcc220bbea6aa48eed694ca&chksm=b2e8fab2859f73a4076692e6368b1701371e2f9afa10f4f3bb3725abe51604e49e5b1e82028c&scene=21#wechat_redirect)
