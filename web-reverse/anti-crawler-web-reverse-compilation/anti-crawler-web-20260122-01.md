# AST 语法树硬刚某宝：提取控制器

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2026-01-22
> 归档日期: 2026-07-13
> 分类: web-reverse
>
> 前面的几篇内容我们算是了解了一下ast解混淆的基本操作。接下来我们开始研究某宝的加密逻辑。

这段时间有点忙，来不及更新，抽空接着再写几篇。

前面的几篇内容我们算是了解了一下ast解混淆的基本操作。接下来我们开始研究某宝的加密逻辑。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 模拟高度混淆的多层控制流平坦化代码（复刻淘宝/电商类加密混淆风格）(function() {    // 初始化混淆变量（无意义命名，模拟真实混淆特征）    var vi, mi, pi, zv, bv, Tv, Jv, dn, lk, Yn, wn, lv, cv, dv, Zv;    var Wv = [{ "href": "https://example.com?a=1&b=2", "onclick": "test()" }, { "href": "https://test.com", "connect-grid-id": "grid_123456" }];    var kk = 0, tk = "href", vk, Vv, Lv, Uv, Ek = 1, ok, $i;    // 核心状态机循环（完全复刻你提供的代码结构）    for (var l = 3997696; void 0 !== l;) {        // 位运算拆分大整数l为d(低8位)、x(中8位)、L(高8位)        var d = 255 & l;        var t = l >> 8;        var x = 255 & t;        var c = t >> 8;        var L = 255 & c;        switch (d) {            case 0:                (function() {                    switch (x) {                        case 0:                            if (76 == L) {                                // 分支1：状态跳转逻辑                                if (vi = mi = pi) {                                    l = 2361600; // 状态值1                                } else {                                    l = 7274752; // 状态值2                                }                            } else if (L < 76) {                                if (37 == L) {                                    // 分支2：字符串拼接+反转混淆                                    zv = bv;                                    bv = "HEAD";                                    Tv = "appendChild";                                    Jv = (Jv = "yxorPon").split("").reverse().join(""); // 反转成 "noProxy"                                    dn = Jv;                                    Jv = "https://";                                    lk = "n";                                    Yn = lk += "oUM"; // "noUM"                                    l = 8201728; // 跳转新状态                                } else if (L < 37) {                                    if (18 == L) {                                        // 分支3：变量拼接+乱码字符                                        wn = "get";                                        lv = "cdc_adoQpoasnfa76pfcZLmcfl_Symbol";                                        cv = "docum";                                        dv = cv += "ent"; // "document"                                        cv = "createElement";                                        Zv = "SCRIPT";                                        zv = "\xc1\xbf\xce\x9f\xc6\xbf\xc7\xbf\xc8\xce\xcd\x9c\xd3\xae\xbb\xc1\xa8\xbb\xc7\xbf"; // 乱码占位                                        bv = "";                                        l = 1648128; // 跳转新状态                                    } else if (L < 18) {                                        if (8 == L) {                                            // 分支4：简单运算                                            $i = -vi;                                            l = 4526592; // 跳转新状态                                        } else {                                            if (L < 8) {                                                if (3 == L) {                                                    // 分支5：数组取值+字符串拼接                                                    xv = Wv[kk];                                                    (Uv = xv[tk]) && (vk = xv[tk], Vv = "c", Vv += "on", Vv += "ne", Vv += "ct-g", Vv += "rid-", Lv = vk.indexOf(Vv), Uv = Lv >= 0);                                                    (vk = Uv) && (Ek = 0, ok = xv);                                                    kk++;                                                    l = 1507328; // 跳转新状态                                                } else {                                                    // 兜底分支：终止循环                                                    l = void 0;                                                }                                            }                                        }                                    }                                }                            } else {                                // L > 76 分支：终止循环                                l = void 0;                            }                            break;                        default:                            // x非0分支：跳转到初始状态                            l = 3997696;                            break;                    }                })();                break;            case 1:                // 扩展分支：模拟更多状态逻辑                (function() {                    if (x == 10 && L == 50) {                        // 模拟加密逻辑片段                        var fakeEncrypt = Jv + Yn + dn; // "https://noUMnoProxy"                        console.log("模拟加密结果：", fakeEncrypt);                        l = void 0; // 终止循环                    } else {                        l = 3997696; // 回到初始状态                    }                })();                break;            default:                // d非0/1分支：终止循环                l = void 0;                break;        }    }    // 最终执行：模拟创建DOM元素（还原混淆后的真实逻辑）    if (dv && cv && Zv) {        var el = window[dv][cv](Zv);        el.src = Jv + "example.com/script.js";        document["HEAD"][Tv](el);    }})();

上面这段代码是我模仿某宝的混淆方式写的一个小例子。这种多层控制流平坦化。分析这段的逻辑可以发现，控制代码执行逻辑的，就是

  *   *   *   *   *


     var d = 255 & l; var t = l >> 8; var x = 255 & t; var c = t >> 8; var L = 255 & c;

通过这段代码，每次根据l的值，计算出d,x,L的值进行switch-
case的分支执行。那么我们要进行反混淆，这里的思路就是可以通过上面的运算代码，以及提取每个分支最后给的l值。不断的按照顺序遍历，来复现代码的运行逻辑，通过运行逻辑再把代码还原成可读性更高的顺序执行的代码。
接下来第一步，先定位，查看代码中是否有类似结构的混淆代码：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


        const node = path.node;    const scope = path.scope;    if (types.isBlockStatement(node.body)) {        // 检测判断是否未for后var + switch的代码形式        let flag = true;        let _body = node.body.body        let _cal_list = []        for (var idx = 0; idx < _body.length; idx++) {            if (types.isVariableDeclaration(_body[idx])) {                _cal_list.push(_body[idx])            } else {                if (types.isSwitchStatement(_body[idx])) {                    break                } else {                    flag = false                    break                }            }        }

这里的逻辑就是判断  for后var + switch的代码形式。然后再进行解混淆处理。
第二步，进行判断for后面跟的是否是运算代码：

  *   *   *   *   *   *   *   *   *   *   *


    let args = null;const initNode = first_line.declarations[0].init;// 先检查左侧if (types.isIdentifier(initNode.left)) {  args = initNode.left;} // 左侧不是则检查右侧else if (types.isIdentifier(initNode.right)) {  args = initNode.right;}// 都不是则保持null

` types.isIdentifier(node)是 Babel 提供的工具函数，用于判断传入的 AST
节点是否是「标识符类型」（简单说就是变量名、函数名等，比如  ` ` a  ` 、  ` foo  ` 、  ` bar  ` ）。  `
init.left/  ` ` init.right  ` ：二元表达式节点的「左侧」和「右侧」子节点（比如 255 & l  中，  ` left  `
是  ` 255  ` ，  ` right  ` 是 l  ）。  第三步，提取控制器参数：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    let _prop = []let _prop_names = []for (var ids = 0; ids < _cal_list.length; ids++) {    var _prop_name = _cal_list[ids].declarations[0].id.name;    _prop.push(types.objectProperty(types.stringLiteral(_prop_name), types.identifier(_prop_name)))    _prop_names.push(_prop_name)}let _ret = types.returnStatement(types.objectExpression(_prop));_cal_list.push(_ret)var get_param_func = types.expressionStatement(    types.callExpression(        types.functionExpression(            null,            [],            types.blockStatement(                [                    types.functionDeclaration(                        types.identifier('getparam'),                        [args],                        types.blockStatement(                            _cal_list                        )                    ),                    types.returnStatement(                        types.identifier('getparam')                    )                ]            )        ),        []    ))get_param_func = generator(get_param_func).codeconsole.log(get_param_func);get_param_func = eval(get_param_func)get_param_func = eval(get_param_func)let control_param = node.init.declarations;if (control_param.length === 1) {    let control_param_value = control_param[0].init.value;    console.log("控制器参数为 " + args.name + ", 且初始值为" + control_param_value);

通过上面的逻辑我们可以获取到控制器的执行代码并包装成一个函数，方便我们后续调用。

到这里我们就完成了对这段混淆代码逻辑的控制器的提取。后续我们接着讲解，获取控制器后如何进行代码执行逻辑的破解。

##  码字不易，如果真的有帮助可以顺手点个赞，你们的喜欢就是我更新的动力！


内容含AI生成图片


关注该公众号

[ 知道了 ](javascript:;)

使用小程序
