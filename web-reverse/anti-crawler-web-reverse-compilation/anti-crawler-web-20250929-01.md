# Akamai难点第四弹：获取xCK字典后的混淆解密思路

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2025-09-29
> 归档日期: 2026-07-13
> 分类: web-reverse
>
> 之前我们分析了Akamai加密就是解析获取xCK字典， [ 被 Akamai 反爬虐到哭？Akamai 反爬 JS 逆向：从抓包到解密，四步拆穿加密套路！ ](https://mp.weixin.qq.com/s?biz=MzU2NTI5MTU5OA==&mid=2247483672&idx=1&sn=a59f56b139dd1a0db63389022a59。

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


关注该公众号

[ 知道了 ](javascript:;)

使用小程序
