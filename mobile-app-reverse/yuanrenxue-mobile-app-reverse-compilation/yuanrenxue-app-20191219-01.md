# 搞定某APP的TCP抓包，并实现Hook抓取

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2019-12-19
> 归档日期: 2026-07-16
> 分类: mobile-app-reverse
>
> APP抓包比较繁琐，尤其是对方优先走socket，发TCP包，而不是走应用层发http/https协议。 这种抓包更烦躁，绝大部分利用中间人攻击原理这种代理抓包软件都抓不到tcp请求，代理抓包软件大都只能抓应用层协议。

APP抓包比较繁琐，尤其是对方优先走socket，发TCP包，而不是走应用层发http/https协议。
这种抓包更烦躁，绝大部分利用中间人攻击原理这种代理抓包软件都抓不到tcp请求，代理抓包软件大都只能抓应用层协议。

今天写篇搞定发TCP包的APP和实现Hook抓取的文章。

抓TCP包常用的工具是wireshark和tcpdump。
tcpdump可以运行在手机上抓包，但没有界面，wireshark有界面，过滤数据包较方便，就用这两个工具来打配合抓TCP包吧。

tcpdump是命令行工具，运行起来是这样子。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccOoUN1bb8yd6wNJohYmLwekCzjTWG8dvoOH58NxfykrtUwbU5RbwN1SEbHrsia4m8vrg5NMvhwfibQ/640?wx_fmt=png)

把抓完的数据包保存为pcap格式，并拉到本地电脑上来，用wirseshark打开该文件，过滤出相应APP的数据包。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccOoUN1bb8yd6wNJohYmLweC7v5ic5VrlWw7C8qQIKPAj1lsllAzHXU9vk7dD2XEzXOZHdGTqibSJBg/640?wx_fmt=png)

用TCP流打开Continuation Data，里面绝大部分都是乱码，因为tcp里的数据是对方的私有协议或有加密，没办法解析。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccOoUN1bb8yd6wNJohYmLwe46szKyN2RDxOlhCQQJq5VbEy66O6VVgMZTKW28G2ibgYiaMs7dugXYpA/640?wx_fmt=png)

通过观察还是有一些可见字符，诸如：  "b" "s"等等，这给了一丝线索。
使用反编译工具打开apk，用万能的搜索大法，在代码里各种搜索这些可见字符，找到了如下代码。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccOoUN1bb8yd6wNJohYmLwe23EjqhnCS4ypBzufFnFfhw8rsrNibTOw0yL6sDGEgtiabjTvM54aXvQQ/640?wx_fmt=png)

已经找到看似有用的代码啦，等等， **我们上面一顿猛如虎的操作的用意是什么呢** ？

我们是想通过抓取TCP包，观察包里的数据，给我们线索。
用这些线索来找到APP发TCP的代码位置，通过Hook手段不让该APP发TCP，迫使其发http(s)协议，然后可以使用代理抓包软件正常抓包。

定位到如上代码了，就写段Hook代码，Hook上述方法，把调用堆栈打印出来，碰碰运气，看能否追踪到发送数据包的代码位置。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccOoUN1bb8yd6wNJohYmLweRKFFVcOQx7NbpR7Is7zBAFZDGONNOB66Pdl5gialwzpDqiaZZ7UzbKFA/640?wx_fmt=png)

通过下面打印出来的调用堆栈，

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccOoUN1bb8yd6wNJohYmLweurUOnxCRmZgibNCSGQD15LjMuxSmic0nobLl9WvTxTXcvaoWG2LjLj4A/640?wx_fmt=png)

再一顿猛点，运气不错，定位到一段可疑代码（如下），大大的socketConnected字样非常显眼，猜也能猜到它的作用。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccOoUN1bb8yd6wNJohYmLweCx2spCVDWicica677Ll2OyL0GicYbWvBJ7LKE2crdDzLDE0NAJ197kuibg/640?wx_fmt=png)

isSocketConnected为true就会进入if语句，为false就不会进入if语句。  果断Hook
isSocketConnected方法让它返回false，不进入if语句里。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccOoUN1bb8yd6wNJohYmLweZIVIhSSZQI5sPX00aFPGAjeejp37In8r2WCqv4PjTvNv6aB8tTvOKw/640?wx_fmt=png)

这时再来打开Fiddler抓包软件抓包试试？  bingo，关闭tcp成功，抓到http协议啦。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccOoUN1bb8yd6wNJohYmLweAgic6vib0OANr7jhUaRtic7nOzlFN1O1ia48lqqV7mxqWibwHHVR8FWAnZA/640?wx_fmt=png)

抓到包是关键一步，接下来就该模拟请求参数去抓数据了。  But，请求的参数里如下参数随便构造会请求失败，那就只有继续Hook咯，在代码里找到参数构造的地方。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccOoUN1bb8yd6wNJohYmLweUqze44lq3R0ujxWI4lIu96hOS1TZdpuibBJLMnngrxqUpB3C94g6Eeg/640?wx_fmt=png)

还是那个套路，先用搜索大法一顿搜，运气不错，搜到参数构造的地方。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccOoUN1bb8yd6wNJohYmLweIYhFGw3A6RkcKs7Bg9WNW4WFTWibzbzZiaHKaV7p3MO8bfwAeRib2BQTg/640?wx_fmt=png)

一顿惊喜后，发现该方法是写在so文件里，难不成要去分析so文件？  NO，才不想去分析so文件，直接用Hook大法调用so里的方法就好啦。
嗯，管他三七二十一，先撸几行Hook代码搞一搞。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccOoUN1bb8yd6wNJohYmLwedCicWBPnZuZ4Zn9nwx6A4AKLyKsFTBjmkvu1JADNrFmvO7dGdqkpWVQ/640?wx_fmt=png)

Hook开发，难点是找对Hook点，Hook点找对后，代码非常简短和优美。  嗯，几行代码搞定，直接Hook调用so文件里的方法。  程序运行一下试试？

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccOoUN1bb8yd6wNJohYmLwek1PKhe4nicajaeBtEXHMo7vXhKViaUhEGTHcmAQdgswd6GlJIo3xtQHQ/640?wx_fmt=png)

还不错的样子。

嗯，Hook开发相对来说要麻烦一点，需要逆向思维，别人的代码你正着看，大概率是懵圈的，因为代码都被混淆成abc啦，要靠线索和经验去找代码片段，从结果反向推导对方可能的程序逻辑，再辅与Hook的手段打印程序运行时的数据和调用堆栈等手段来排除和寻找代码确切的位置。
