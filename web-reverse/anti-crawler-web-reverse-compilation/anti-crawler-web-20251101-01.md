# AST 语法树硬刚某宝第四弹：多层三元表达式拆解

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2025-11-01
> 归档日期: 2026-07-13
> 分类: web-reverse
>
> 搞某宝的时候我们经常能看到下面的 “反人类” 代码， 一行代码里塞了四五个三元表达式，夹杂着数组 push、字符串反转和变量赋值，盯着看十分钟还没理清逻辑分支。

搞某宝的时候我们经常能看到下面的  “反人类”  代码，  一行代码里塞了四五个三元表达式，夹杂着数组
push、字符串反转和变量赋值，盯着看十分钟还没理清逻辑分支：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    void (  3 == a ?     (li.push(_i.alert, _i[vi], Yi, Dn, ev, un, _i[Bv], Cv, _i[Wn]),     Xi = li, li = [], Dn = "Sc", Dn += "ree",     (Yi = []).push(_i[Dn += "n"], ai), Dn = Yi, Yi = [], n = 48) :     a < 3 ?       1 == a ?         (Av = Yi[Cv], n = Av ? 41 : 51) :         a < 1 ? (li++, n = 33) : (Cv++, n = 36) :       5 == a ?         (mr = gr <= hr, kv = 0 !== $.length,          n = (Cr = (hr = mr * mr) > -126) ? 49 : 1) :         a < 5 ?           (Yi = Xi.join(Zk), si = Xi = li = Yi, n = 9) :           (ev = "MouseEvent", un = "x", Yi.push(_i[ev], un), un = Yi, Yi = [],           Cv = (Cv = "Xtnemevom").split("").reverse().join(""),           Yi.push(_i[ev], Cv), ev = Yi, Yi = [], n = 17));break;

这种嵌套多层、操作密集的三元表达式，堪称 “代码阅读理解题” 的天花板。今天我们就用 Babel 打造一个 “代码翻译官”，把它自动拆成直观的 if-
else 语句，让逻辑一目了然。


##  为什么要拆？嵌套三元的 3 个致命问题

先别急着写工具，我们得先搞清楚：为什么要花时间拆解这种代码？

  1. ** 调试像 “拆盲盒”  ** 假设这段代码里  ` n  ` 的值不对，你想打断点看是哪一步赋值出了问题 —— 但三元表达式是 “一行执行”，你根本没法定位到是  ` 3 == a  ` 分支，还是  ` 1 == a  ` 分支导致的问题，只能靠 “注释大法” 逐段排查。

  2. ** 修改容易 “牵一发而动全身”  ** 要是想在  ` 3 == a  ` 的分支里加一句  ` console.log(Dn)  ` 调试，得先在一堆括号里找到正确的位置，稍不注意漏个逗号或括号，整个表达式就报错了。

而拆解成 if-else 后，这些问题会迎刃而解：每个分支独立、每个操作单行、断点想加就加。

##  工具核心逻辑：用 Babel 拆解三元的 3 步走

我们要实现的工具，核心是 “识别三元表达式 → 拆解分支逻辑 → 生成 if-else 节点”。下面结合核心代码，一步步看它是怎么工作的。

###  第一步：准备 “基础工具”—— 生成标准 if-else 节点

首先得有个函数，能把任意分支逻辑包装成带大括号的标准 if-else 节点，避免拆完后格式混乱：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    const types = require("@babel/types");/** * 创建标准 if-else 节点（确保分支是块级语句） * @param {Object} test 条件表达式（如 3 == a） * @param {Object} consequent 真分支逻辑 * @param {Object} alternate 假分支逻辑 * @returns {Object} if-else 节点 */function createIfStatement(test, consequent, alternate) {  // 不管传入的分支是不是块级语句，统一转成带大括号的形式  const consequentBlock = types.isBlockStatement(consequent)     ? consequent     : types.blockStatement([consequent]);
      const alternateBlock = types.isBlockStatement(alternate)     ? alternate     : types.blockStatement([alternate]);
      return types.ifStatement(test, consequentBlock, alternateBlock);}

比如你传入一个单行赋值  ` n = 48  ` ，它会自动转成  ` { n = 48; }  ` ，保证格式统一。

###  第二步：识别目标 —— 找到要拆解的三元表达式

接下来要遍历代码，找到藏在不同语句里的三元表达式。我们主要处理三类场景：

  *   *   *   *   *   *


    // 遍历规则：关联节点类型与处理函数const traverseIfExpress = {  VariableDeclaration: handleVariableDeclaration, // 变量声明中的三元（如 const a = b?c:d）  ExpressionStatement: handleExpressionStatement, // 表达式中的三元（如本文示例）  ReturnStatement: handleReturnStatement          // return 中的三元（如 return b?c:d）};

本文的复杂示例属于 “ExpressionStatement”（表达式语句），所以重点看  ` handleExpressionStatement  `
函数：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    /** * 处理表达式语句中的三元表达式 * @param {Object} path 节点路径 */function handleExpressionStatement(path) {  const node = path.node;  const expression = node.expression;  // 场景1：赋值中的三元（如 a = b?c:d）  if (types.isAssignmentExpression(expression) &&       types.isConditionalExpression(expression.right)) {    // 生成赋值分支，此处省略具体逻辑...  }   // 场景2：直接执行的三元（如本文中的复杂示例）  else if (types.isConditionalExpression(expression)) {    const { test, consequent, alternate } = expression;
        // 关键：递归拆解嵌套三元！    const handledConsequent = handleNestedConditional(consequent);    const handledAlternate = handleNestedConditional(alternate);
        // 用 if-else 替换原三元表达式    path.replaceWith(      createIfStatement(test, handledConsequent, handledAlternate)    );  }}

这里有个关键：  ** 递归拆解嵌套三元  ** 。因为示例中的三元是多层嵌套（  ` 3 == a  ` 的假分支里又有  ` a < 3  `
的三元），所以需要一个  ` handleNestedConditional  ` 函数，逐层拆解直到没有三元表达式为止：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    /** * 递归拆解嵌套的三元表达式 * @param {Object} node 要处理的节点 * @returns {Object} 拆解后的节点 */function handleNestedConditional(node) {  // 如果当前节点还是三元表达式，继续拆解  if (types.isConditionalExpression(node)) {    const { test, consequent, alternate } = node;    // 递归处理真分支和假分支    const handledConsequent = handleNestedConditional(consequent);    const handledAlternate = handleNestedConditional(alternate);    // 生成 if-else 节点    return createIfStatement(test, handledConsequent, handledAlternate);  }   // 如果是逗号表达式（如多个操作用逗号分隔），拆成独立语句  else if (types.isSequenceExpression(node)) {    return types.blockStatement(      node.expressions.map(expr => types.expressionStatement(expr))    );  }  // 其他类型（如赋值、push）直接返回  return node;}

这个递归函数是 “拆解多层嵌套” 的核心 —— 它能把 4 层嵌套的三元，一层一层拆成 4 层 if-else。

###  第三步：处理特殊情况 —— 逗号表达式拆分行

示例中每个分支里有很多用逗号分隔的操作（如  ` li.push(...), Xi = li, li = []  ` ），这种叫
“逗号表达式”，需要拆成独立语句。

上面的  ` handleNestedConditional  ` 函数里已经处理了这种情况：通过  `
types.isSequenceExpression(node)  ` 识别逗号表达式，然后用  ` map  ` 把每个操作转成独立的表达式语句（如  `
li.push(...)  ` 转成  ` li.push(...);  ` ）。

##  拆解效果：从 “天书” 到 “说明书”

把我们的工具作用于开头的复杂三元表达式，最终会生成这样的代码：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    void (function () {  if (3 == a) {    // 原 3 == a 为真的分支    li.push(_i.alert, _i[vi], Yi, Dn, ev, un, _i[Bv], Cv, _i[Wn]);    Xi = li;    li = [];    Dn = "Sc";    Dn += "ree";    (Yi = []).push(_i[Dn += "n"], ai);    Dn = Yi;    Yi = [];    n = 48;  } else {    if (a < 3) {      if (1 == a) {        Av = Yi[Cv];        // 原 Av ? 41 : 51 拆成 if-else        if (Av) {          n = 41;        } else {          n = 51;        }      } else {        if (a < 1) {          li++;          n = 33;        } else {          Cv++;          n = 36;        }      }    } else {      if (5 == a) {        mr = gr <= hr;        kv = 0 !== $.length;        hr = mr * mr;        Cr = hr > -126;        // 原 Cr ? 49 : 1 拆成 if-else        if (Cr) {          n = 49;        } else {          n = 1;        }      } else {        if (a < 5) {          Yi = Xi.join(Zk);          si = Xi = li = Yi;          n = 9;        } else {          ev = "MouseEvent";          un = "x";          Yi.push(_i[ev], un);          un = Yi;          Yi = [];          Cv = (Cv = "Xtnemevom").split("").reverse().join("");          Yi.push(_i[ev], Cv);          ev = Yi;          Yi = [];          n = 17;        }      }    }  }})();break;

可以看到通过上面的代码可以直接把阅读性极为复杂的三目表达式直接转换成更容易读懂的if-else语句，当然
这并不是我们搞定某宝的终点，借用一下举个例子，也是想让大家了解ast语法树对于处理多层三目表达式的优势。

之后我们继续研究ast语法树的其他能力，如果对于ast语法树有什么疑问的  欢迎在评论区留言探讨。

##  码字不易，如果真的有帮助可以顺手点个赞，你们的喜欢就是我更新的动力！


关注该公众号

[ 知道了 ](javascript:;)

使用小程序
