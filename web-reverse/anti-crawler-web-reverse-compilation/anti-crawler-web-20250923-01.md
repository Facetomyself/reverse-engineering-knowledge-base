# Akamai难点第一～四弹：mst / ajr / ffs / xCK 字典的混淆解密思路

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2025-09-23 ~ 2025-09-29（4 篇，逐篇日期见各节）
> 归档日期: 2026-07-13
> 分类: web-reverse
>
> 本文合并同一作者的 4 篇连载：第一篇「Akamai难点第一弹：mst参数的vmp混淆解决思路」、第二篇「Akamai难点第二弹：ajr参数得混淆解密」、第三篇「Akamai难点第三弹：ffs参数的混淆解密思路」、第四篇「Akamai难点第四弹：获取xCK字典后的混淆解密思路」。

## 收录说明

本文由原先分开归档的 4 篇连载合并而成（2026-09-26 整理）。各节标题为「篇次：原标题」，下方一行保留该篇自己的来源与发布日期；原文标题层级整体下调，正文未删减。原各篇文件头部的自动摘要只是正文开头的节选，合并时不再重复保留。同一作者 2025-09-21 的前置文章「扒一扒 VMP 反爬：从踩坑到破局的实战思路(Akamai)」不属于「难点」编号系列，仍单独保留。合并前文件：`anti-crawler-web-20250923-01.md`（保留路径）、`anti-crawler-web-20250925-01.md`、`anti-crawler-web-20250928-01.md`、`anti-crawler-web-20250929-01.md`（已删除）。

## 第一篇：Akamai难点第一弹：mst参数的vmp混淆解决思路

来源：微信公众号：反爬破解社 · 原始发布时间：2025-09-23 · 归档日期：2026-07-13

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

## 第二篇：Akamai难点第二弹：ajr参数得混淆解密

来源：微信公众号：反爬破解社 · 原始发布时间：2025-09-25 · 归档日期：2026-07-13

上一篇我们完成了的dvc参数得解密。 [ Akamai难点第一弹：mst参数的vmp混淆解决思路
](https://mp.weixin.qq.com/s?__biz=MzU2NTI5MTU5OA==&mid=2247483717&idx=1&sn=2c7b5eed3f74f693084545bf43d8b75b&scene=21#wechat_redirect)
这一篇我们来搞定Akamai参数得ajr参数。  回顾 [ 被 Akamai 反爬虐到哭？Akamai 反爬 JS 逆向：从抓包到解密，四步拆穿加密套路！
](https://mp.weixin.qq.com/s?__biz=MzU2NTI5MTU5OA==&mid=2247483672&idx=1&sn=a59f56b139dd1a0db63389022a593d50&scene=21#wechat_redirect)
的内容，我们来解析

cMK参数的生成逻辑。  第一步，我们依旧是进行全局查找，搜索  cMK的位置  ：

接下来就在这里打断点，然后对着这段语句解混淆可以得到

  *   *   *   *   *   *   *


    var cMK = L7({    "startTimestamp": window.bmak['startTs'],    "deviceData": WL(zhK),    "mouseMoveData": "",    "totVel": 0,    "deltaTimestamp": nZK});

可以看到这里的逻辑是把字典的内容传入到L7函数中运算得到的，接下来我们先分析dict里面的值，  window  .  bmak  [  'startTs'
]是初始化的时候的时间戳。  第二步，我们分析zhK的值，依旧是进行搜索，可以发现：

接下来这里打断点，然后单步执行进行，看看GSK函数执行了什么

然后就是对GSK函数解混淆：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    var GSK = function() {
          var q0K = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36';    var vfK = ''['concat'](T4K(q0K));    var YAK = RC(window.bmak['startTs'], hh[28]);    var tdK = 0    var spK = window['screen']['availWidth'];    var sRK = window['screen']['availHeight'];    var UfK = window['screen']['width'];    var UtK = window['screen']['height'];    var ErK = window['innerHeight'] || window['document']['body']['clientHeight'];    var ItK = window['innerWidth'] || window['document']['body']['clientWidth'];    var fnK = window['outerWidth'];       var lAK = window['parseInt'](RC(window.bmak['startTs'], EA(hh[42], hh[42])), 10);    var WbK = window['parseInt'](RC(lAK, hh[52]), 10);    var DdK = window['Math']['random']();    var kfK = window['parseInt'](RC(EA(DdK, 1000), 2), 10);    var w9K = ''['concat'](DdK);    w9K = BO(w9K['slice'](0, 11), kfK);    var k0K = [window['navigator']['productSub'], window['navigator']['language'], window['navigator']['product'], 5];    var WnK = k0K[hh[5]];    var cAK = k0K[1];    var DqK = k0K[hh[28]];    var FqK = k0K[hh[12]];    var prK = 0;    var b0K = 0;    var f0K = 0;    var ApK =[    {        "xag": 12147    },    {        "wow": fnK    },    {        "tsd": 0    },    {        "pha": prK    },    {        "npl": FqK    },    {        "ash": sRK    },    {        "ran": w9K    },    {        "adp": "cpen:0,i1:0,dm:0,cwen:0,non:1,opc:0,fc:0,sc:0,wrc:1,isc:0,vib:1,bat:1,x11:0,x12:1"    },    {        "ibr": 0    },    {        "ua": q0K    },    {        "nal": cAK    },    {        "nap": DqK    },    {        "nps": WnK    },    {        "ucs": vfK    },    {        "dau": f0K    },    {        "wiw": ItK    },    {        "wdr": b0K    },    {        "swi": UfK    },    {        "wih": ErK    },    {        "asw": spK    },    {        "hal": YAK    },    {        "hz1": lAK    },    {        "she": UtK    }]    return ApK;};

可以了解到这里存储的就是window的一些属性，这里我们就可以直接补环境。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    window = global;
    var screen = {    "availHeight": 1400,    'availLeft': 0,    'availTop': 0,    'availWidth': 2560,    'colorDepth': 24,    'height': 1440,    'isExtended': false,    'onchange': null,    'pixelDepth': 24,    'width': 2560, };
    document = {    "location":location,    "body":{"clientHeight":1533, "clientWidth":2545}};window.document = document; window.screen = screen;

反正就是把需要检查的环境补齐就可以了。  第三步，我们解析WL函数，我这里取巧了，直接发现WL函数执行之后就是把返回的dict
将所有值转换为字符串并拼接。所以直接用js复现了一个：

  *   *   *   *   *   *   *


    function WL(obj, separator = '') {    // 获取对象的所有值    const values = Object.values(obj);        // 将所有值转换为字符串并拼接    return values.map(value => String(value)).join(separator);}


第四步，我们解析nZK的值，依旧是进行全局搜索：

解析一下这段代码就是：

  *


    var nZK = RZ(w1K(), window.bmak['startTs']);

这里w1k函数是生成的当前时间戳，RZ函数则是求两个数的差值，所以这个nZK值是求的现在的时间戳减去初始的时间戳的差值。  第五步，我们解析L7函数：

跟进到L7函数看看里面到底执行了什么，老规矩，继续解混淆可以得到：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    var L7 = function (IJK) {    var GTK = lQK(IJK['mouseMoveData']);    var CkK = GTK[1];    var ZKK = 1;    if (VL(CkK["length"], 0)) {        for (var B7 = 0; qV(B7, CkK['length']); B7++) {            var hDK = window['parseInt'](CkK[B7], 10);            if (hDK && VL(hDK, 0)) {                ZKK = EA(ZKK, hDK);            }        }    };    var LsK = VNK(ZKK);    var GKK = [LsK, GTK[0], CkK];    var l4K;    return l4K = GKK['join']('|'),    l4K;}

可以看到上面还需要解析lQK函数：

解混淆下来是：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    var lQK = function(F4K) {    var rkK = -1;    var VkK = [];    if (!!F4K && typeof F4K === 'string' && F4K["length"] > 0) {        var RIK = F4K["split"](';');        if (RIK["length"] > 1 && RIK[RIK["length"] - 1] === '') {            RIK["pop"]();        }        rkK = window["Math"]["floor"](window["Math"]["random"]() * RIK["length"]);        var ZGK = RIK[rkK]["split"](',');        for (var s8K in ZGK) {            if (!window["isNaN"](ZGK[s8K]) && !window["isNaN"](window["parseInt"](ZGK[s8K], 10))) {                VkK["push"](ZGK[s8K]);            }        }    } else {        var A8K = window["String"](NF(1, 5));        var P1K = '1';        var XIK = window["String"](NF(20, 70));        var GmK = window["String"](NF(100, 300));        var OsK = window["String"](NF(100, 300));        VkK = [A8K, P1K, XIK, GmK, OsK];    }    return [rkK, VkK];};

VNK函数则是：

解混淆下来则是：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    var VNK = function(KRK) {        var mdK = 1;        var RRK = [];        var FFK = window["Math"]["sqrt"](KRK);        while (mdK <= FFK && RRK["length"] < 6) {            if (KRK % mdK === 0) {                if (KRK / mdK === mdK) {                    RRK["push"](mdK);                } else {                    RRK["push"](mdK, KRK / mdK);                }            }            mdK = mdK + 1;        }        return RRK;    };

所以整体逻辑整理好就完成了对L7函数的解混淆，带入需要传入的字典就可以生成得到  ajr的参数。
如果你们在实操时碰到问题，欢迎在评论区留言，咱们一起拆解！后续还会出 “各个参数的实战案例”，教你用 Python 完整复现 Akamai 加密逻辑，
这里是爬虫虐我千百遍，我待爬虫如初恋的爬虫任。  点赞关注，下次实战不迷路～，

## 第三篇：Akamai难点第三弹：ffs参数的混淆解密思路

来源：微信公众号：反爬破解社 · 原始发布时间：2025-09-28 · 归档日期：2026-07-13

上一篇我们完成了的ajr参数的解密。 [ Akamai难点第二弹：ajr参数得混淆解密
](https://mp.weixin.qq.com/s?__biz=MzU2NTI5MTU5OA==&mid=2247483729&idx=1&sn=b58a96889b4f8080412ff3d2fc966852&scene=21#wechat_redirect)
这一篇我们来搞定Akamai参数得ffs参数。  回顾 [ 被 Akamai 反爬虐到哭？Akamai 反爬 JS 逆向：从抓包到解密，四步拆穿加密套路！
](https://mp.weixin.qq.com/s?__biz=MzU2NTI5MTU5OA==&mid=2247483672&idx=1&sn=a59f56b139dd1a0db63389022a593d50&scene=21#wechat_redirect)
的内容，我们来解析

tHK参数的生成逻辑。  第一步，我们依旧是进行全局查找，搜索tHK  的位置  ：

接下来就在这里打断点，我们可以看到tHK是由VSK()函数生成的。我们单步进函数看看：

通过对这个函数解混淆我们可以发现，函数的主要逻辑其实是获取页面html的input元素的各个属性值进行加密，解混淆之后的函数就是：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    var VSK = function(input_list) {    var SvK = "";    var FSK = -1;    var X3K = input_list;    for (var dwK = 0; qV(dwK, X3K['length']); dwK++) {        var x5K = X3K[dwK];        var fLK = T4K(x5K['name']);        var FLK = T4K(x5K['id']);        var xHK = x5K['required'];        var ZVK = c3(xHK, null) ? 0 : 1;        var kZK = x5K['type'];        var QZK = c3(kZK, null) ? -1 : qsK(kZK);        var lEK = x5K['autocomplete'];        if (c3(lEK, null))            FSK = -1;        else {            lEK = lEK['toLowerCase']();            if (MH(lEK, 'off'))                FSK = hh[5];            else if (MH(lEK, 'on'))                FSK = hh[2];            else                FSK = fr;        }        var dhK = x5K['defaultValue'];        var d5K = x5K['value'];        var tEK = hh[5];        var k5K = 0;        if (dhK && S6(dhK['length'], hh[5])) {            k5K = 1;        }        if (d5K && S6(d5K['length'], GT['zQQ']()) && (HO(k5K) || S6(d5K, dhK))) {            tEK = 1;        }        if (S6(QZK, hh[28])) {            SvK =''['concat'](BO(SvK, QZK), ',')['concat'](FSK, ',')['concat'](tEK, ',')['concat'](ZVK, ',')['concat'](FLK, ',')['concat'](fLK, ',')['concat'](k5K, ';');        }    }    var rgK;    return rgK = SvK,    rgK;};

我这里直接对VSK函数进行可改写，因为要使用python调用，我们没办法直接通过js获取到html的input属性，所以这里直接传入一个dict，传入的参数是input元素的各个属性值。而我们则可以使用python去获取原始页面html的input属性。我这里写一个例子：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    from bs4 import BeautifulSoupdef extract_input_attributes(html_content):    """    从HTML内容中提取所有input标签及其属性，返回字典列表        参数:        html_content (str): HTML源码字符串            返回:        list: 包含所有input标签属性的字典列表    """    soup = BeautifulSoup(html_content, 'lxml')  # 也可以使用 'html.parser'    input_tags = soup.find_all('input')        result = []    for input_tag in input_tags:        # 获取所有属性并转换为字典        attrs = dict(input_tag.attrs)        result.append(attrs)        return result# 示例用法if __name__ == "__main__":    html_example = """    <html>        <body>            <input type="text" name="username" id="user" class="form-control" placeholder="Enter username">            <input type="password" name="password" required>            <input type="submit" value="Login">            <div>                <input type="hidden" name="csrf_token" value="abc123">            </div>        </body>    </html>    """        inputs = extract_input_attributes(html_example)    for i, input_dict in enumerate(inputs, 1):        print(f"Input {i}:")        for attr, value in input_dict.items():            print(f"  {attr}: {value}")        print()

这样我们就解决了ffs参数的混淆加密，同时  inf参数的值跟ffs一样，所以这两个参数的加密都解决了。就是验证页面的input元素的属性值。
如果你们在实操时碰到问题，欢迎在评论区留言，咱们一起拆解！后续还会出 “各个参数的实战案例”，教你用 Python 完整复现 Akamai 加密逻辑，
这里是爬虫虐我千百遍，我待爬虫如初恋的爬虫任。  点赞关注，下次实战不迷路～，

## 第四篇：Akamai难点第四弹：获取xCK字典后的混淆解密思路

来源：微信公众号：反爬破解社 · 原始发布时间：2025-09-29 · 归档日期：2026-07-13

之前我们分析了Akamai加密就是解析获取xCK字典， [ 被 Akamai 反爬虐到哭？Akamai 反爬 JS 逆向：从抓包到解密，四步拆穿加密套路！
](https://mp.weixin.qq.com/s?__biz=MzU2NTI5MTU5OA==&mid=2247483672&idx=1&sn=a59f56b139dd1a0db63389022a593d50&scene=21#wechat_redirect)
。而xCK里面的加密字段：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    xCK = {    "ver": 'zGyit7DnuXEJ0P5pq4fuoCPWY3XPnIjATgJm721fMrU=',//jSK,    "fpt": hvK['fpValStr'],    "fpc": Y3K,    "ajr": cMK,    "din": zhK,    "eem": ThK,    "ffs": tHK,    "vev": "",    "inf": tHK,    "ajt": SHK,    "kev": "",    "dme": "",    "mev": "",    "doe": "",    "pur": QbK,    "pev": "",    "mst": whK,    "o9": 0,    "tev": "",    "sde": nEK,    "pmo": "",    "dpw": "",    "pac": "",    "per": "8",    "pde": "",    "oev": "",    "if": "",}

当中较难的字段的加密逻辑我们在前几篇文章中都已经进行了分析破解。今天这一篇我们就研究获得xCK字段后的混淆加密逻辑是怎么样的。

对这段代码解混淆可以看到：

  *   *   *   *   *   *   *   *   *   *   *


    var GOK = LDK();V5K = window['JSON']['stringify'](xCK);var UOK = w1K(); //获取当前的时间戳V5K = Mq([V5K, GOK[1]]); UOK = RZ(w1K(), UOK);  //时间戳的差值var KxK = w1K(); //时间戳V5K = OvK(V5K, GOK[0]);KxK = RZ(w1K(), KxK);var DCK = ''['concat'](RZ(w1K(), zSK), ',')['concat'](0, ',')['concat'](0, ',')['concat'](UOK, ',')['concat'](KxK, ',')['concat'](0);var xhK = nvK(GOK);V5K = ''['concat'](xhK, ';')['concat'](DCK, ';')['concat'](V5K);

这里我们需要先解析LDK函数生成了什么

解混淆可以得到

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    var gTK = function(RUK) {    if (window["document"]["cookie"]) {        var mAK = ""["concat"](RUK, "=");        var znK = window["document"]["cookie"]["split"]('; ');        for (var EtK = 0; EtK < znK["length"]; EtK++) {            var kYK = znK[EtK];            if (kYK["indexOf"](mAK) === 0) {                var NjK = kYK["substring"](mAK["length"], kYK["length"]);                if (NjK["indexOf"]('~') !== -1 || window["decodeURIComponent"](NjK)["indexOf"]('~') !== -1) {                    return NjK;                }            }        }    }    return false;};var LDK = function() {    var ETK = [hh[11], dGK];    var l7 = gTK('bm_sz');    var JkK = window['decodeURIComponent'](l7)['split']('~');    if (mA(JkK['length'], 4)) {        var r1K = window['parseInt'](JkK[hh[28]], hh[29]);        r1K = window['isNaN'](r1K) ? hh[11] : r1K;        ETK[Ih] = r1K;    }    return ETK;};

LDK可以看到就是对cookie进行了系列处理，携带回去进行验证。
继续之后的逻辑可以看到，这里的逻辑是先将xCK转化为字符串，然后获取当前的时间戳之后。把字符串传入到Mq里面。所以我们在Mq这里打断点，看看Mq函数执行的逻辑


我们单步执行，然后对执行的逻辑解混淆可以发现：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    var Mq = function(V5K, GOK1){    var X0 = V5K;    var k9 = GOK1;    var rq;    var SP;    var sR;    var Z9;    var MU = ':';    var qW = X0['split'](MU);    for (Z9 = 0; qV(Z9, qW['length']); Z9++) {        rq = n3(zA(YF(k9, 8), 65535), qW['length']); //'zQI77N7wQQQQQQ'        k9 *= hh[7];        k9 &= hh[8];        k9 += hh[9];        k9 &= hh[10];        SP = n3(zA(YF(k9, 8), hh[6]), qW['length']);        k9 *= 65793;//GT['zQI70LN']();        k9 &= hh[8];        k9 += hh[9];        k9 &= hh[10];        sR = qW[rq];        qW[rq] = qW[SP];        qW[SP] = sR;    }    var TW;    TW = qW['join'](MU)    return TW;}

这里hh是一个固定的数组。接下来我们继续跟进加密逻辑。又获取一次时间戳之后，又对V5K执行了OvK函数，依旧打断点到OvK函数单步进去进行解析：


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    var OvK = function(lBK, R8K) {    if (HO(KvK)) {        for (var YBK = 0; qV(YBK, 127); ++YBK) {            if (qV(YBK, 32) || MH(YBK, 39) || MH(YBK, 34) || MH(YBK, 92)) {                cTK[YBK] = IH(39);            } else {                cTK[YBK] = KvK['length'];                KvK += window['String']['fromCharCode'](YBK);            }        }    }    var DTK = '';    for (var xGK = hh[5]; qV(xGK, lBK['length']); xGK++) {        var NKK = lBK['charAt'](xGK);        var ImK = zA(YF(R8K, 8), hh[6]);        R8K *= hh[7];        R8K &= hh[8];        R8K += hh[9];        R8K &= hh[10];        var BTK = cTK[lBK['charCodeAt'](xGK)];        if (MH(typeof NKK['codePointAt'], 'function')) {            var mKK = NKK['codePointAt'](0);            if (mA(mKK, 32) && qV(mKK, 127)) {                BTK = cTK[mKK];            }        }        if (mA(BTK, 0)) {            var smK = n3(ImK, KvK['length']);            BTK += smK;            BTK %= KvK['length'];            NKK = KvK[BTK];        }        DTK += NKK;    }    var P4K;    return P4K = DTK,    P4K;};

上面便是解混淆之后的执行逻辑，整理成了函数，只需要传入V5K以及GOK的值就可以进行加密。  我们接着往后看，经过一些列拼接操作后我们只需要再破解
nvK函数即可，依旧是跟进函数内部解密混淆逻辑：


  *   *   *   *   *   *   *   *   *   *   *   *


    var nvK = function(SxK) {    var v6K = '3';    var E5K = '0';    var HhK = 1;    var tvK = 0;    var hCK = jSK;    var LZK = [v6K, E5K, HhK, tvK, SxK[0], hCK];    var MOK = LZK['join'](';');    var OxK;    OxK = MOK;    return OxK;};

这里就是生成了sensor_data的前缀。最后将这些字符串拼接即可生成，我们执行一下总统的逻辑可以看到：

sensor_data生成成功 ![](https://res.wx.qq.com/t/wx_fed/we-
emoji/res/assets/newemoji/Party.png) ![](https://res.wx.qq.com/t/wx_fed/we-
emoji/res/assets/newemoji/Party.png) ![](https://res.wx.qq.com/t/wx_fed/we-
emoji/res/assets/newemoji/Party.png)

我们Akamai反爬就告一段落，完结撒花 ![](https://res.wx.qq.com/t/wx_fed/we-
emoji/res/assets/newemoji/Fireworks.png)


如果你们在实操时碰到问题，比如 “XHR 断点不触发”“加密算法看不懂”，欢迎在评论区留言，咱们一起拆解！后续还会出 “各个参数的实战案例”，教你用
Python 完整复现 Akamai 加密逻辑，  这里是爬虫虐我千百遍，我待爬虫如初恋的爬虫任。  点赞关注，下次实战不迷路～，
