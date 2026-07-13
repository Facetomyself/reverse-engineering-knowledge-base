# Akamai难点第二弹：ajr参数得混淆解密

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2025-09-25
> 归档日期: 2026-07-13
> 分类: web-reverse
>
> 上一篇我们完成了的dvc参数得解密。 [ Akamai难点第一弹：mst参数的vmp混淆解决思路 ](https://mp.weixin.qq.com/s?biz=MzU2NTI5MTU5OA==&mid=2247483717&idx=1&sn=2c7b5eed3f74f693084545bf43d8b75b&scene=21#wechatredirect)。

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


关注该公众号

[ 知道了 ](javascript:;)

使用小程序


宋来自广东

[强]
