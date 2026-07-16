# 某文APP逆向抓取分析

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2020-05-07
> 归档日期: 2026-07-16
> 分类: mobile-app-reverse
>
> 以某 App 为例串联抓包、脱壳、jadx、Frida 与 Python 复现，定位多组请求签名和 3DES 响应解密流程。


在学习了一段时间的爬虫逆向后，正好有需求要采集某某文书的一些数据，因此就以此app为例，给大家介绍一下如何使用frida找加密代码的思路，从而实现自动化采集。特此说明，本文仅供学习交流，请勿用作其他用途。

**主要使用的工具和环境如下：**
设备：一部root的手机或者手机模拟器（本人使用nexus6p真机）;
抓包工具：fiddler；
分析工具：jadx-gui 1.1.0；
脱壳工具：xposed+fdex2；
执行代码: pycharm + python3.6；
hook框架：frida；

**抓包初步分析**

** 首先手机与电脑连在同一个网络，设置好代理和端口，打开fiddler，运行手机app，我们随意搜索某个关键词查看下抓包结果：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccibDzl1YTJQXGzEN2Ulhpv0JzG1owVQ67bHO0cl3H7UElK75ibbjsIibOvH6VjYTWxcKy1NXzKmMLJA/640?wx_fmt=png)

从上图我们可以看出他是发出一个post请求，data是一个以request=开头的一长串加密字符，返回值是由两部分组成，一个serectkey，一个content。我们再输入一个不同的关键词，抓包得到结果与这次结果进行对比。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccibDzl1YTJQXGzEN2Ulhpv0gp1XVxH2uUicibHRbjrW6aUfV2jmDJvAqhrGPuLJ4VgoMzaZJITPBaVQ/640?wx_fmt=png)

由于参数不是很多，就不借用对比差异工具了。对比两张图，我们可以很明显得到以下几点信息：

1.请求的url不发生改变；

2.headers这部分没有加密；

3.post请求的data部分是改变的，全是由字母和数字组成，初步观察有点像base64；

4.返回值部分 初步猜测 content是由serectkey钥匙解密得到，可能是aes、des等等加密；

由上面初步分析，我们就有方向去找加密的代码。主要寻找的就是request=后面那部分到底是什么东西，返回值是由什么加密而成的。

**请求参数java代码分析**

我们使用xposed+fdex2进行脱壳，得到dex源码（这边就不演示过程了），发现只有一个dex，看来app还是挺轻量级的。

小tips：因为这边只有一个dex文件，所以源代码肯定在内。如果有多个dex文件的话，建议先从文件最大的那个开始排查，这样会节省点时间。
使用jadx打开dex文件，点击导航->搜索文本。从上文分析来看，我们该搜索request这个关键词，看看能不能返回一些结果。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccibDzl1YTJQXGzEN2Ulhpv0QfoStSvfWTdQicyrWmiblRfRGzGWmKJLE11PUsZUTaySYaIBPsfKcmMg/640?wx_fmt=png)

发现搜索结果又200多个，要么一个个去排查，实在是太浪费时间，要么换个搜索方式。其实经常查看源码的小伙伴，可能会对变量赋值这一块搜索比较有经验，通常这种字符串，都会以以下几种方式去搜索：
“request”
“request”:
“request”,
使用上面的全文搜索，我们可以很快定义到代码赋值的地方，

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccibDzl1YTJQXGzEN2Ulhpv0FniaaktKPn1yzo8Micf0hBbCI3NTWhxWO1qtZib1R6oVrTHP8ibKkQz4rA/640?wx_fmt=png)

我们点击进去查看，发现调用了com.lawyee下面的b方法，传进去的参数是str.getBytes()，因此我们首先想知道传进去的值是什么，发现上文在g.b这一块调用了了str，经过查看可知，g.b就是一个log函数，输出日志用的，我们通过firda
hook这一块方法，可以查看str是什么。hook代码如下

          1. Java.perform(function(){

      2. varAndroidLog=Java.use("android.util.Log")

      3. varAndroidException=Java.use("java.lang.Exception")

      4. function printStackTrace(){

      5.         console.log(AndroidLog.getStackTraceString(AndroidException.$new()));

      6. }

      7. varMainActivity=Java.use('com.lawyee.***.util.g');

      8. MainActivity.b.overload('java.lang.String','java.lang.String').implementation =function(params1,params2){

      9.         send("Hook Start...")

      10. //send("stack"+printStackTrace())

      11.         send("params1:"+params1)

      12.         send("params2:"+params2)

      13. var result =this.b(params1,params2)

      14.         send("result"+result)

      15. }

      16. });

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccibDzl1YTJQXGzEN2Ulhpv07LgFicdcxOXiaykbnWj9HIGBQXAia71IDibAb1R4ia1uR321ffGCws0rLqA/640?wx_fmt=png)

其实从这边我们就可以看出，str就是request加密前的明文。经过多次输入不同关键词，可以得知一下几个关键信息：
id 是变化的，经观察和时间有关；
command = 固定参数；
pageNum = 页数；
pageSize = 一页显示的数量
sortFields = “s50:desc” 固定参数；
ciphertext = 变化的，需要找到其加密方式；
pageSize = 每页的个数，可自行构造；
devid = 猜想是设备id，不发生改变；
queryCondition = [{“key”:”s21”,”value”:”小米”}] # 关键词 + 搜索文本的类型；

下面我们就需要构造这些参数，组成完整的请求data，主要是两个参数ciphertext
以及id，又开始我们的全局搜索大法，发现在这里对ciphertext和id赋值。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccibDzl1YTJQXGzEN2Ulhpv0gVib2iaBx5XXQXzeHhYicRib9gy9fT6raSYveyE6ZfkUuH5DRjh9KMZVibA/640?wx_fmt=png)
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccibDzl1YTJQXGzEN2Ulhpv0GeuBQBLGUnA9FZRJibJsJpTWVwyQkQ64JpTVqpmYwIo81gDwx1gY0Lg/640?wx_fmt=png)

ciphertext = d.a();
id 相当于是当前年月日小时分钟和秒组合而成，可构造;

我们进入d.a()，发现代码有点长，这一块我们使用frida.rpc去调用，写一个web服务，每次请求的使用调用一次这个方法。

          1. rpc.exports ={

      2.     getsig:function(){

      3. var ciphertext ="";

      4. Java.perform(function(){

      5.             send("here")

      6. varMainActivity=Java.use('com.lawyee.****.util.d');

      7.             ciphertext =MainActivity.a()

      8. })

      9. return ciphertext

      10. }

      11. };

走到这一步，我们已经可以实现自动化构造参数，下面就是要找到如何加密得到request，从文章开始我们猜测使用的base64。机智的我就把加密后的request经过base64.decode()
发现和我们构造的参数一模一样，这样就可以实现请求获取数据了。还有一种方法就是去也是用rpc调用c.a().b方法，实现获取post
data。这边我选择直接使用base64。

          1. req_url ='http://127.0.0.1:5001/getsigs?data={}'.format("11")# 请求web服务获取ciphertext

      2. response = requests.get(req_url)# ciphertext

      3. id = time.strftime("%Y%m%d%H%M%S")

      4. pagenum =1

      5. pageSize =20#

      6. keyword ="小米"# 关键词

      7. ori_data ={"id":"%s"% id,"command":"queryDoc","params":{"pageNum":"%s"% str(pagenum),"sortFields":"s50:desc","ciphertext":"%s"% get_cipher(),"devtype":"1","devid":"5b1a4e4ffdf54c4996b00b6f57ae14f9","pageSize":"%s"% str(pageSize),"queryCondition":[{"key":"s21","value":"%s"% keyword}]}}

      8. bytes_data = json.dumps(ori_data).encode("utf-8")# 二进制

      9. str_data = base64.b64encode(bytes_data)# 被编码的参数必须是二进制数据

      10. data ="request="+str_data.decode()# 加密后的参数

由此我们就用python实现了文书网的请求，得到加密前的数据。

**返回结果加密解析**

哈哈哈，又开始我们的猜测大法，所有加密全靠猜。一个key，一个加密后的content，让人浮想联翩。一般开发app不会自己去写一个加密算法，那样太浪费时间并且消耗成本了。其实百度搜索java常用的加密算法，我们就可以大概猜出来答案，后面无非就是一个一个去全局搜索。我们首先排除base64、MD5，这些不需要key值，常用到key值的就是des和aes这两种了，在java中，调用这两类算法需要使用调用这两个类，我们投机取巧全局搜索了一下发现了新大陆!!!

          1. import javax.crypto.Cipher;

      2. import javax.crypto.SecretKey;

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccibDzl1YTJQXGzEN2Ulhpv0EvRHPKV1dsU5BMV9BsNex9jczAaRcf9WIyP3W9cn2406EcHJT6TnNg/640?wx_fmt=png)

上图中，m.a(str,str1,str2)是des3加密函数，m.b是解密函数，大概看下这一部分的代码，只需要知道iv是偏移量，使用上面第一个a方法返回而来（yyyyMMdd年月日），key就是请求返回的值，content也是，我们使用frida
hook一下

          1. Java.perform(function(){

      2. varMainActivity=Java.use('com.lawyee.***.util.m');

      3. MainActivity.b.overload('java.lang.String','java.lang.String','java.lang.String').implementation =function(params1,params2,params3){

      4.         send("Hook Start... here7")

      5.         send("params1:"+params1)

      6.         send("params2:"+params2)

      7.         send("params3:"+params3)

      8. var result =this.b(params1,params2,params3)

      9.         send("result:"+result)

      10. return result

      11. }

      12. });

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccibDzl1YTJQXGzEN2Ulhpv0yDt4w78dico3GKEUVh35TBMsEV7LGUWStTvhnHqPl6mlEpkDpDKBkNg/640?wx_fmt=png)

params1 就是请求返回的content
params2 是key
params3 是iv(偏移量)
result 是的des3解密后的结果

到此为止，所有的加密都已经找出来啦，本来准备把des3这段代码考出来的用java执行，不过想起来之前对该网页端网站写爬虫的时候，用python实现了des3加密，今天也算用上了。

          1. fromCryptodome.Cipherimport DES3

      2. fromCryptodome.Util.Paddingimport unpad

      3. def des3decrypt(cipher_text, key, iv):

      4.     des3 = DES3.new(key=key.encode(), mode=DES3.MODE_CBC, iv=iv.encode())

      5.     decrypted_data = des3.decrypt(base64.b64decode(cipher_text))

      6.     plain_text = unpad(decrypted_data, DES3.block_size).decode()

      7. return plain_text

      8.

这样子就可以完整的构造请求了并且获得数据了，我们尝试请求了一下，获得的结果如下：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccibDzl1YTJQXGzEN2Ulhpv09XS5cbVpW5WUiasQZ2ClXN7l985PJQmhlxo4wCcFLVTX6vIA30OadoQ/640?wx_fmt=png)

感兴趣的童鞋可以自己去尝试一下，整体不是很难哦。

**总结**

这个app从刚拿到手到解密结束，没有什么特别的坑，比较适合新手去练练手。主要的就是找到自己hook代码的思路以及找加密方法的一些小技巧。此app还没有涉及到so层面上的调用，难度下降了不少。

总结起来就是如果平常逆向app的时候遇到加密参数比较多的，不要慌张，一步一步去找到加密地址的所在，合理的利用frida
hook技巧，靠打印参数能够得到不少有效信息。逆向app一定要多练习，这样才能在实践中找到自己的不懂之处，才能够成长。好啦，今天的逆向小文章就到此结束啦，童鞋们下篇文章再见咯。
