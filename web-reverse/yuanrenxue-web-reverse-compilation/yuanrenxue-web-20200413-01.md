# Python 的控制流代码混淆

> 来源: 微信公众号：猿人学Python
> 原始发布时间: 2020-04-13
> 归档日期: 2026-07-16
> 分类: web-reverse
>
> 聊下 Python 的代码混淆，对 Python 的代码做混淆感觉是不伦不类，但是对于外包项目交付型的，又有一些需要。 混淆的目的就是加大别人分析你代码逻辑和流程的难度，让代码看上去杂乱，逻辑混乱。但是程序要能正常运行。 一般混淆 对 Python 代码做简单点混淆的就是变量名/类名/字符串/常量做混淆，把名称变成很长或者近似。

聊下 Python 的代码混淆，对 Python 的代码做混淆感觉是不伦不类，但是对于外包项目交付型的，又有一些需要。
混淆的目的就是加大别人分析你代码逻辑和流程的难度，让代码看上去杂乱，逻辑混乱。但是程序要能正常运行。
**一般混淆**
对 Python 代码做简单点混淆的就是变量名/类名/字符串/常量做混淆，把名称变成很长或者近似。

这类的混淆库很多，比如 Intensio-Obfuscator 这个库，这个库分简单和复杂混淆，来看下用它的简单模式来混淆 Python 代码：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccibNydHDueNfm9UYoqgDV2djtkujfJpHSR0zAicyTNZxfvB6SYU3j2GbO1Ip1cztia6GMVzDALsZuMg/640?wx_fmt=png)
左边是混淆前，右边是混淆后，只是把变量名方法名混淆并且加长了。

这种简单混淆的意义不大，字符串和常量都一目了然，代码结构，就靠静态分析，代码的脉络也看得还是清楚。

再复杂一点的混淆就是把关键代码藏起来，和在代码里加一些无效代码。
还是 Intensio-Obfuscator 这个库的复杂混淆模式，我们来看看：
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccibNydHDueNfm9UYoqgDV2dvTef0ubjCoOCnULOoTg8L9ZJicTrEZD0FhVLWpb3NSh0QzADQb8iaB1w/640?wx_fmt=png)
右边初看，貌似不像是 Python 代码，实际上右边那串字符串就是左边的 Python 代码，只不过是 unicode 码。 因为 Python
有个内置函数 exec() 可以执行字符串程序，像这样：

    >> exec("1+1")>> 2

我们把这个字符串里的内容打印成 utf8 看看里面的内容：

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccibNydHDueNfm9UYoqgDV2dxMPt796zvibRv1T8LeI3sDz84MCLwRA0Tpx65jWhqxL1KkX1IqOzCUA/640?wx_fmt=png)
如上图，它的混淆一是把变量名做得更长，二是代码里加了些干扰代码，看标红处，原始代码本来没有 for 和 if
语句，混淆后的代码有了。看上去如果要静态分析这个代码很困难了，实际如果把变量名重名命和变短后，这部分多余的 for 和 if
通过静态分析，还是较容易跳过去。
总结下 Intensio-Obfuscator
库复杂混淆模式，先是把代码变量函数名弄得很长，然后是在代码里加入了无效代码，最后是把源代码压缩当成一个字符串，用 exec 来执行。

**抽象语法树混淆**
上面的混淆方式相对简单，通过静态分析就能反混淆出来。更复杂一点的混淆就是控制流混淆。通常程序的执行流程都是很有条理的，控制流混淆就是把程序的执行流程混淆。
比如代码里多了很多 while for if 乃至 lamdb
语句，把赋值，加减操作，变成位运算等等。让你通过静态分析的方式，很难看出代码的目的和逻辑是什么。
怎么做到控制流混淆，要通过抽象语法树 （AST）
，通过抽象语法树，可以做到用程序来修改程序。通过抽象语法树，可以很精确的知道程序在做什么操作，这样就能很精准的修改代码。
先看一下简单的通过抽象语法树来混淆程序的例子，还是拿上面的程序来举例。

![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccibNydHDueNfm9UYoqgDV2dC2bzxicdy1zLcQiacE60RiaAjrKwuEzbuD0trpu5XYSYjammqHkWaqemw/640?wx_fmt=png)
左边是混淆前的代码，后面是混淆后的。这个例子也是把变量名混淆了，然后是把字符串和常量，还有 import
也混淆了。反混淆的难度比上面大了一点，要通过动态调试才知道程序在干嘛。

**什么是抽象语法树**

见名知意就是把程序抽象成一棵树，代码里的语句被拆成了树上的一个个节点。Python 里有个 AST 模块就是用来干这个的，还是上面的源代码，看下被 AST
拆成节点后是什么样。
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccibNydHDueNfm9UYoqgDV2dMZ3eDiaMoswsWNOoMWQBnIQjwrMQrWej7pwRz5k2lX8QsEpQ2kQrX2g/640?wx_fmt=png)
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccibNydHDueNfm9UYoqgDV2dLYemMs2TeMroribKESEIU9U2ibRXXofiaLxlRVQQCcAFmZVqC0cRgh6rA/640?wx_fmt=png)
第二张图就是把第一张图创建为了抽象语法树，并且把源代码按树的节点打印出来了。

红箭头标注了，有 Import 节点，Assign 节点， 函数节点， 加法节点等等。这颗树可以完全表达上述程序。我们可以通过访问这颗树，来用程序修改程序。
![](https://mmbiz.qpic.cn/mmbiz_png/GrTTsqWuEccibNydHDueNfm9UYoqgDV2d4Yiciap1jQhuMDiaYmMDYGxiaaDX8PA6e8Lia90Av5zibtsLLn0mK6kUUTuQ/640?wx_fmt=png)
自定义一个类，继承 ast.NodeTransformer ，比如你想访问字符串，就实现visit_Str这个方法，想访问 Import 就实现
visit_ImportFrom 这个方法。在实现的方法里，你可以用一些混淆算法去混淆，（注意只能是混淆，不能改变结果）。这样就能做到精细化和更复杂的混淆。
有一个 ASTObfuscate 第三方混淆库就是通过操作 AST 来混淆代码，不过对程序逻辑流的混淆没有，要实现更复杂的控制流混淆，要完整实现这颗解析树。
当然 Python 的代码混淆更难的话，应该是通过混淆字节码，或者把关键代码做成 so 文件，这样的混淆难度更大。 字节码和 so 文件都是汇编指令。
