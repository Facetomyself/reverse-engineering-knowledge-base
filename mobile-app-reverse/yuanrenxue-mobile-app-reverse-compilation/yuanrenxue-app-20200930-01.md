# APP 中的 JS 加密逆向解析

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2020-09-30
> 归档日期: 2026-07-16
> 分类: mobile-app-reverse
>
> 使用木木模拟器，安装好app刚准备愉快的抓个包。竟然检测到root，不能进入。那就先把这个给他hook掉。

**抓取登录包**

****解决安全检测** **

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyN85AjENBcWbrVGctPWiaM5oGdCIJhFZTQv3CCpSOtLTmQcTx9u2Bv3BA/640?wx_fmt=png)

使用木木模拟器，安装好app刚准备愉快的抓个包。竟然检测到root，不能进入。那就先把这个给他hook掉。

用jadx打开apk，全局搜索一下，提示的文字。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyNUjq33EkePCk01OhnicfR5kV4m71HnqclVAcpIaBTiclB3AGL5Yuickb3Q/640?wx_fmt=png)

可以看到这里进行了几种检测，编写frida hook代码，直接把 initCheckSafe 方法置空

    Java.perform(  function () {    var SecurityBuilder =    Java.use('XXXXXXXX.SecurityBuilder');    var initCheckSafe =    SecurityBuilder['initCheckSafe'].overload('android.content.Context','java.lang.String');    initCheckSafe.implementation = function () {     send("hook initCheckSafe");    };}

解决完毕，我们再进入app

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyNBqQHXMQZm8k8r271qCnySufPVDJxAichZ4KsFdCVc44LHg7ymfn2aHA/640?wx_fmt=png)

又提示要跟新，事是真的多。那就更新吧。点击更新后，加载了一些东西，然后进入了登录页面。（!!! 后面发现这里的坑）

**抓包分析**

配置好代理，直接抓包。

可以看到请求的数据模式都是

action=xxxx&data=json

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyN0mPUomiaf4pvVVOSzsYA5dE4wmg9AGMoJAiagtkJiaTP4iagHjVpewia4gg/640?wx_fmt=png)

把这个json数据拿出来看看，多尝试几次发现密码不变这个password不变，其他的参数都可以写死。到这里，如果账号少的话，手动抓一次包后续使用就可以了。但是咱能满足于此吗，盘它！

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyNT0L4hcT1gWkCOpmoNxicIjpYjSw1XxDrTMSsRT4pRTfWicvt9ZicniaMwQ/640?wx_fmt=png)

**寻找加密位置**

**盲狙碰运气**

这个参数看着像是，某种加密后base64的结果。先base64解码看看啥情况。将加密后的值urldecode之 后再base64解码

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyNZGzbsgsLC0NmzRslSYiaVVLGT2vea16ZSn13XMm3BwNFbqW4qicdaeNw/640?wx_fmt=png)

一堆乱码看不懂。那我们使用南山大佬写的xposed的模块把常见加密hook一波，尝试快速定位。激活xposed
plus模块，然后打开ddms，查看日志信息。

![](https://mmbiz.qpic.cn/mmbiz_jpg/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyNo9nFo1oWkpj8rYfe1TwjoiaPOtBdYy2LAfKh1T5Ifnj7nMlvIRLtboQ/640?wx_fmt=jpeg)

![](https://mmbiz.qpic.cn/mmbiz_jpg/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyNk7a9fgqPuMyB6iaoHLl1fxs2DmlKJYE8mtPOyFAaW3mkHic19iaiabknzA/640?wx_fmt=jpeg)

可以看到常见的加密类都被hook到了，但是在保存的日志中尝试搜索输入的密码，抓包的加密结果等， 都一无所获。

**搜索反编译代码**

看来好事多磨，快的不行那我们去分析代码吧。

尝试搜索 登录链接 登录参数字段值等，都寻找不到有用的信息，事情好像陷入了僵局。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyNxB1g7DiazEiaQY71xgbXTbibuJchXeDaot4jdmbkboYE2rXdfcML6NKeg/640?wx_fmt=png)

**巧计寻出路**

静静思考一会，回想到登录接口参数data后面的值是一个json类型，也就是字典类型。那能不能hook java中这个类，看看有没有password赋值的操作

百度一波，得到如下hook代码

    var print = console.log;function hoon_map(cName, mName, args) {  Java.perform(function () {    var clz = Java.use(cName);    if (clz == null) {    throw "java.use()==null"    };      var method = null;  method = clz[mName].overload(args[0], args[1]);  method.implementation = function () {    print(cName + " " + arguments[0] + " " + arguments[1]);    var ret = method.apply(this, arguments);    return ret  }})}  function main() {  print("runing");  hoon_map("java.util.HashMap", "put", ["java.lang.Object","java.lang.Object"]);  hoon_map("java.util.LinkHashMap", "put", ["java.lang.Object","java.lang.Object"]);}main()

把这代码灵活运用一下，我们再登录一次看看结果。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyNM68hKicAyTNMXThHFAP06Qxv72sE1QLL4qStPEcVUdGFxZpDdnoywsA/640?wx_fmt=png)

果然发现了赋值操作，那就过滤一下无用的信息，再把这个操作的调用栈打印出来，顺藤摸瓜，那不就 能找到加密位置了嘛。感觉看到了希望。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyNrgnc92eyhPHlcEc3iaUxyRUbH7ns8kVatsmXehzu6KXb5ZqMef1BKBw/640?wx_fmt=png)

还好调用栈不是很多，去掉 java开头的和proxy，剩下的我们从上面开始一个个看一下，有没有加密的地方。

一直找到最下面这个方法,参数可以看到是从 exec 这个函数的参数传来的。那么hook这个exec的入参看一下。

![](https://mmbiz.qpic.cn/mmbiz_jpg/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyN2nmNHZstWqvJ2Jt6FNmT03jFRrtpicgBhq2omfGzXsibbV81ySA5nquQ/640?wx_fmt=jpeg)

hook 结果：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyN9zD4Q3EI3B1qozznP7Q981dyP05swZ7rXWsKm1Wic2w8UscA8Il3ZiaA/640?wx_fmt=png)

这下蒙蔽了，都追到根了，咋还是加密过的值呢。

**再肯硬骨头**

**发现线索一**

有困难但是也不能放弃。再自己端详一下exec的代码，发现它头部有个@JavascriptInterface好像装饰 器一样的东西，和别的函数都不一样。

不懂咱就去搜索一下，然后发现这个是可以让 js 和 java 互相调用的一个东西。

![](https://mmbiz.qpic.cn/mmbiz_jpg/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyNickb8N4ZUuMV6ibMIp6TmeMZZFVllc8bzg4fNyvITAO49DvlCUa1tQnw/640?wx_fmt=jpeg)

那就知道方向了，加密是在js中进行的，然后js中调用java里的exec方法，将值传了进来。

将apk反编译，先去找找那些js中，有cbPassInfo setOfflineCache这些信息。

![](https://mmbiz.qpic.cn/mmbiz_jpg/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyNuodLdad7bZ41jF99GKSTgkcOCUaUnTbabLjjcztZ2cCDdcANYc3F7w/640?wx_fmt=jpeg)

哟呵，搜到了这两个里面有。把他俩拖出来瞅一瞅。

![](https://mmbiz.qpic.cn/mmbiz_jpg/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyNkmWumnvaLJxdt9ZAypN23OVzj9epD5wzFKbGlKZVlOwx4qghJsdHuQ/640?wx_fmt=jpeg)

在 login.js 里面只有这两处。先验证一下这里是不是传加密值的地方。

我把这里的 cbPassInfo 改成别的字符串，然后重新打包签名apk，安装，再抓取一次登录包，如果出现的是我修改的字符，那说明这就是调用的位置。

信心满满，又抓了一次包。结果啪啪打脸。还是 cbPassInfo 。

**发现线索二**

突然想到，重新安装打开后，有个提示框，更新资源，难道它又重新下载了这个文件，把我修改的重置 了。

卸载，重装后，抓包查看下它更新的资源，发现果然是这样。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyNGjCtymo4fJf9fOr9vuTJn7GUUZVJia9gFUXNKl1dZ5uZrtuzQR6Df8A/640?wx_fmt=png)

既然修改apk不行，js又是静态文件，那直接在模拟器中搜索login.js

结果有3，4个，把文件重命名，app打开没了登录界面，那就是它了。

**模拟加密**

**分析js**

先分析一下js，密码就是通过蓝框两个方法加密的。

![](https://mmbiz.qpic.cn/mmbiz_jpg/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyNAcyXORxSicOvKDyyeS58ialKdQbicS4OKpOf9TuQIhroRica5AhUwYrMYw/640?wx_fmt=jpeg)

先搜索一下 D 和 Base64，Base64没有获得有效的信息。发现D应该和 sha1 有关系

![](https://mmbiz.qpic.cn/mmbiz_jpg/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyN8YpuCVpllGyBteuJGe2LauaibPkuU6ia99nib23F6o2KyiaOnJSFV4uibibA/640?wx_fmt=jpeg)

这里js不好调试，我们利用js调用java的流程，把我们想要的值传给java层，然后去hook接收的函数。这 里把我把用到的函数，各种结果都打印了一下。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyNmL5zU6cticqKz0AWZhkHmUNek8S56OLIv2nckrdS1JJiaYlYU9OJDCibw/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_jpg/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyNycptZ2MwXS7bn3YtQOYBqtYgqDS5fHwlzlyOvlv2LmyrznIzhqTeNg/640?wx_fmt=jpeg)

这个D刚才看是和sha1相关的，用标准的sha1对比一下。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyNxrD1xPiamtRmTxSuxyAOnTGkgokruNOLGJwhLpsG83sIazUWeIknsOQ/640?wx_fmt=png)

发现和上面结果相同。那就只剩base64这个函数了。看打印出来的代码，发现这不是一个标准的base64，运行报错缺少 c 变量。

搜素函数内的代码，在common.js中发现了

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyNRvwELt3WGRu1niaoQiamoiapPnHVuRicIuLmbuBZEarCSPURM58gdZK1LA/640?wx_fmt=png)

现在逻辑清楚了，把c的值拿过来，用js来实现加密。可以看到结果和抓包一致，收工。

![](https://mmbiz.qpic.cn/mmbiz_jpg/GrTTsqWuEcf8HYxhDU2iaZpmibbVQRhOyNRnW28fIRNOhCohiaTPAqiaDqo1n8MjKuBztMKYoohX9flcZ5edGsma6A/640?wx_fmt=jpeg)

**总结**

之前遇到的app都是在java代码中加密，或者 so库里面。在js中的这是第一次遇到。

幸运的是js没有做处理，如果把web端的反扒应用在这，手机端又不好对js进行调试，那真是够秃头的了，可怕。

**这篇来自小伙伴 ID: 浮生 的投稿。**

**安利下偶的爬虫逆向进阶课，包含 安卓逆向抓取/安卓群控/JS逆向抓取/爬虫框架设计与工程经验，国庆时正好学习下，目前熟悉安卓逆向抓取技术拿个20K+ 的
offer 还是容易。**

**具体点击下面连接**

[ 把爬虫高阶课又更新了
](http://mp.weixin.qq.com/s?__biz=MjM5NjE0NTY5OA==&mid=2448549536&idx=2&sn=fa53201a28ff10d8020587e75bf7f930&chksm=b2e8f9ed859f70fb4850a9598bc4ea182b62cb98d0acdafe8abadf646e87ad5ef9fa3a40caa2&scene=21#wechat_redirect)
