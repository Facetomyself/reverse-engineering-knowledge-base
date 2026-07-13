# Akamai难点第一弹：mst参数的vmp混淆解决思路

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2025-09-23
> 归档日期: 2026-07-13
> 分类: web-reverse
>
> 上一篇文章我们了解了Akamai的整体加密套路。 [ 被 Akamai 反爬虐到哭？Akamai 反爬 JS 逆向：从抓包到解密，四步拆穿加密套路！ ](https://mp.weixin.qq.com/s?biz=MzU2NTI5MTU5OA==&mid=2247483672&idx=1&sn=a59f56b139dd1a0db63389022a593d5。

上一篇文章我们了解了Akamai的整体加密套路。 [ 被 Akamai 反爬虐到哭？Akamai 反爬 JS 逆向：从抓包到解密，四步拆穿加密套路！
](https://mp.weixin.qq.com/s?__biz=MzU2NTI5MTU5OA==&mid=2247483672&idx=1&sn=a59f56b139dd1a0db63389022a593d50&scene=21#wechat_redirect)
这一篇我们接着上面的内容来分析当中一个重要的加密参数mst。

通过上次解混淆我们发现，mst参数传入的是whK这个值。我们进入代码查找看一下whK值生成的位置：

然后再对他解混淆可以发现whK这里是生成一个字典。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    var mst = [        {            "kevl": BO(hZK, 1)        },        {            "mevl": BO(gwK, 32)        },        {            "tevl": BO(kgK, 32)        },        {            "devl": dxK        },        {            "dmvl": QOK        },        {            "pevl": WLK        },        {            "tovl": mMK        },        {            "delt": nZK        },        {            "it": M6K        },        {            "sts": window.bmak['startTs']        },        {            "fct": hvK['td']        },        {            "dd2": WbK        },        {            "kc": AxK        },        {            "mc": tZK        },        {            "ww8": F5K        },        {            "pc": UEK        },        {            "tc": YxK        },        {            "ssts": KSK        },        {            "tst": LbK        },        {            "rval": hvK['rVal']        },        {            "rcfp": hvK['rCFP']        },        {            "nfas": lMK        },        {            "jsrf": qwK        },        {            "jsrf1": vVK[0]        },        {            "jsrf2": vVK[1]        },        {            "signals": Mq(NM, [])        },        {            "mwd": nP()        },        {            "hea": ""        },        {            "dvc": ''['concat'](zEK, ',')['concat'](nOK, ',')['concat'](tCK)        },        {            "srd": Q6K        }    ];

今天我们就主要讲dvc这个参数的生成逻辑，因为其他的参数稍微认真找一下都是很轻松可以找到的，而且有些是固定不变的。
通过解混淆的代码发现是由zEK，nOK，tCK3个参数拼接而成，所以我们全局查找一下，可以发现

zEK是通过j8函数生成的，nOK解混淆就是时间戳的差值，而tCK经过对比也是一个固定值，所以我们主要就是要解析zEK的生成逻辑。所以断点打到zEK我们跟进去看看：

可以看到这里面的代码不断的循环跳转，完全没有可读性，莫名奇妙的就生成了参数，这就是典型的vmp加密。我们这里就使用最常用的方式来搞定它的加密逻辑----
插桩。  单步调试到函数内部我们可以发现Cv的223是一个很长的list，那大概率指令就存在这里面。

所以接下来就围绕这个进行研究看看我们插桩的点选在哪里，我这里打了5个断点来进行日志监控：

输入输出断点，因为这个函数多次循环调用，我们需要监控他传入跟传输出去的值，看看有什么不同。

这个断点为了监控每次生成的字符串是什么，很多想length等就是在这里生成的。

这个是最重要的断点，这里是主要位置，在这里可以看到他调用的code值，同时监控一下这里值的变化情况

这个断点用来监控一下AG这个值的情况。  注意断点要选日志断点，不要选错条件断点，日志断点是红色，条件断点是橙色。
断点打好后我们就可以执行来看看插桩点的日志输出了，注意，因为日志输出的非常多，我这里建议在上面的蓝色断点那里也打一个。把每次的日志记录下来看，直接在浏览器，容易直接崩溃。。。。。。
接下来就是根据日志来逆推加密逻辑了，首先先看最后生成加密参数的位置

第一步我们可以看到最后生成的  a3igYgdaakkd9fmilpip 是由  milpip以及  a3igYgdaakkd9f2部分拼接而成，我们先看
a3igYgdaakkd9f2这段的生成逻辑


通过上面的逻辑可以看到，  a3igYgdaakkd9f2是由  01758520099234和
["a","3","d","9","f","g","h","i","Y","k","l","m","7","p","q","s","1","w","Q","y","B","z","2"]
这个列表生成的，用js实现一下就是：

  *   *   *   *   *   *   *


    result_long = [];list_1 = ["a","3","d","9","f","g","h","i","Y","k","l","m","7","p","q","s","1","w","Q","y","B","z","2"]const str_5 = String(C6K).concat(window.bmak['startTs']+nZK);//01758520099234for (let i = 0; i < str_5.length; i++) {    result_long.push(list_1[str_5[i]])    }result_long.join('')

那第二步就要去研究这个类似时间戳的值和列表的值是怎么生成的。
接着进行全局查找网上查看  01758520099234值生成的地放可以看到是由startTs的时间戳加上初始传入的时间戳差值  nZK值生成的

而列表则是由一个二进制数以及

  *


    ["a","3","c","d","9","e","f","g","h","i","Y","j","k","l","m","7","o","p","q","r","s","1","u","v","w","Q","x","y","B","z","2"]

这个长列表生成的


通过对于日志的分析可以用js实现一下生成逻辑就是：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    var str_2 = beg.toString(2);//二进制数var list1 = ["a","3","c","d","9","e","f","g","h","i","Y","j","k","l","m","7","o","p","q","r","s","1","u","v","w","Q","x","y","B","z","2"]var list_1 = [];for (let i = 0; i < str_2.length; i++) {    if (str_2[i] == '1'){        if (list1[i]){            list_1.push(list1[i])        }    }    else{        if (i%3 == 0){            if (list1[i]){                list_1.push(list1[i])            }        }    }}console.log(list_1)

第三步就是去研究上面的二进制数是怎么生成的


通过上面的日志可以看到这个二进制数是由十进制的3651628127转换过来的，而  3651628127则是由时间戳+  )
Chrome/140.0.0.0 Safari/537.364经过一系列运算生成的，我是通过日志分析出的运算逻辑，太罗嗦就不一一叙述了，上生成实现的代码：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *


    const str = String(mMK).concat(window.bmak['startTs']).concat(') Chrome/140.0.0.0 Safari/537.364');var beg = 5381; //看日志每次都是同样的值 写死// 方法1: 使用 for 循环for (let i = 0; i < str.length; i++) {    cha = str.charCodeAt(i)    beg = beg*33    beg = beg^cha
    }if (beg < 0){    beg = beg >>> 0;}console.log(`十进制数'${beg}' 的值`);var str_2 = beg.toString(2); //十进制转换为二进制

第四步我们研究那个长列表是怎么生成的，全局检索可以看到是由字符串a3cd9efghiYjklm7opqrs1uvwQxyBz2通过split生成的，而这个字符串又是由ua去生成的也就是说ua不变的情况下这个值就是固定的。所以测试时我就直接先写死。


到这里  a3igYgdaakkd9fmilpip中的  a3igYgdaakkd9f2部分算是解析完成了，接下来就是研究
milpip这个短字符串的生成位置。  第五步依旧是全局检索  milpip
看看这个值又是在日志的哪里生成的（因为文章太长直接的日志丢失，这里重新生成了一次日志，  milpip 值换成了  7Y9mqi，不影响我们的逻辑推导  ）


这个值是由另外一个二进制数字以及短列表生成的，通过对日志数值的变化我们可以推导运算逻辑是：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    var str_3 = linshi.toString(2); //二进制数console.log(str_3)
    result_short = [];for (let i = 0; i < 6; i++) {    cha1 = list_1[i].charCodeAt(0);    num1 = cha1>>str_3[i];    if(str_3[i]==0){        num2 = cha1;        num7 = cha1+2;    }    else{        num2 = cha1<<3;        num7 = 7 ^ (cha1+2);    };    num3 = num2-cha1;    num4 = cha1<<5;    num5 = num4|num1;    num6 = num3*num5;
        num8 = (Math.abs(num6-num7))%list_1.length;    result_short.push(list_1[num8]);    console.log(num1, num2, num3, num5 ,num6, num7,num8);}result_short.join('')//最后生成的字符串


第六步就是研究二进制数的生成逻辑，依旧全局检索日志，发现是由45468682081转化生成的。接着往上检索发现
45468682081是由917053954+3651628127得到的，  3651628127我们上面已经接近知道是怎么生成的，接下来就是研究
917053954的生成逻辑


依旧全局检索可以发现  917053954值是由这个函数传入的参数经过类似第三步的系列算法生成的


接下来就是js复现运算逻辑：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    const str_1 = cMK; //函数传入的参数cMKvar beg1 = 5381;// 方法1: 使用 for 循环for (let i = 0; i < str_1.length; i++) {    cha = str_1.charCodeAt(i)    beg1 = beg1*33    beg1 = beg1^cha}
    if (beg1 < 0){    beg1 = beg1 >>> 0;}console.log(`字符 '${beg1}' 的 charCodeAt`);linshi = (beg1 + beg);if (linshi < 0){    linshi = linshi >>> 0;}console.log(`字符 '${linshi}' 的 charCodeAt`);var str_3 = linshi.toString(2);console.log(str_3)

到这里我们也就全部完成了  dvc下的  zEK这个参数的全部生成逻辑，也算是Akamai加密里面的一个小难点。
其实整理坐下来vmp并不是什么洪水猛兽，相反，如果理解他的逻辑其实是非常轻松非常简单的，还是要找准插桩位置，这里我给大家几个建议，不要怕错，多试多练。经验多了，插桩自然就会了。
偷懒小技巧，有些时候看不懂数字直接的逻辑的时候，直接上deepseek（打钱）


如果你们在实操时碰到问题，欢迎在评论区留言，咱们一起拆解！后续还会出 “各个参数的实战案例”，教你用 Python 完整复现 Akamai 加密逻辑，
这里是爬虫虐我千百遍，我待爬虫如初恋的爬虫任。  点赞关注，下次实战不迷路～，


关注该公众号

[ 知道了 ](javascript:;)

使用小程序


宋来自广东

大有裨益[胜利]
