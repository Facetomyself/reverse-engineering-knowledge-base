# AST 语法树硬刚某宝第二弹：Babel修复格式（二）

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2025-10-23
> 归档日期: 2026-07-13
> 分类: web-reverse
>
> 之前我们用babel完成了对if语句的格式修复。 [ 统一 ](https://mp.weixin.qq.com/s?biz=MzU2NTI5MTU5OA==&mid=2247483765&idx=1&sn=7dcc2788bf34dc2ac14ad39b28b3901e&scene=21#wechatredirect) [ if ](https://mp.。

之前我们用babel完成了对if语句的格式修复。  [ 统一
](https://mp.weixin.qq.com/s?__biz=MzU2NTI5MTU5OA==&mid=2247483765&idx=1&sn=7dcc2788bf34dc2ac14ad39b28b3901e&scene=21#wechat_redirect)
` [ if
](https://mp.weixin.qq.com/s?__biz=MzU2NTI5MTU5OA==&mid=2247483765&idx=1&sn=7dcc2788bf34dc2ac14ad39b28b3901e&scene=21#wechat_redirect)
` [ 语句的格式，避免因分支是否带大括号导致的语法歧义或风格不一致问题。
](https://mp.weixin.qq.com/s?__biz=MzU2NTI5MTU5OA==&mid=2247483765&idx=1&sn=7dcc2788bf34dc2ac14ad39b28b3901e&scene=21#wechat_redirect)
今天我们接着之前的内容继续，讲解使用  Babel修复for等其他语句的格式。  废话少说，上代码：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    const types = require("@babel/types");// 定义遍历规则：只处理 ForStatement 节点const traverse_forexpress = {    ForStatement(path) {        fix(path); // 遇到 for 循环节点时，调用修复函数    }};

    /** * 处理for循环体无大括号的情况，统一包裹为BlockStatement * @param {Object} path - Babel路径对象 */function fix(path) {    // 确保路径存在且是ForStatement节点    if (!path || !path.isForStatement()) {        console.warn('无效的ForStatement路径');        return;    }
        const node = path.node;    const loopBody = node.body;
        // 如果已经是块语句，则无需处理    if (types.isBlockStatement(loopBody)) {        return;    }
        // 处理空循环体情况    if (loopBody === null) {        node.body = types.blockStatement([]);        return;    }
        // 处理表达式语句作为循环体的情况    if (types.isExpressionStatement(loopBody)) {        node.body = types.blockStatement([loopBody]);        return;    }
        // 处理其他合法但不常见的循环体类型    if (types.isStatement(loopBody)) {        node.body = types.blockStatement([loopBody]);        console.log('已将非表达式语句的循环体转换为块语句');        return;    }
        // 处理未知类型    console.warn('发现未知的for循环体类型:', loopBody.type);}

    module.exports = {    fix: traverseForExpress,    // 导出修复函数方便测试    fixForLoopBody};
    exports.fix = traverse_forexpress;

###  代码关键点说明

  1. ** 前置校验  ** ：通过  ` path.isForStatement()  ` 确保只处理合法的 for 循环节点，避免无效输入导致的错误。

  2. ** 跳过已处理节点  ** ：如果循环体已是  ` BlockStatement  ` （带大括号），直接返回不做处理，提高效率。

  3. ** 空循环体处理  ** ：针对  ` for(;;);  ` 这类空循环体，转换为  ` for(;;) {}  ` ，保持逻辑不变的同时规范化格式。

  4. ** 多类型兼容  ** ：

     * 处理最常见的  ` ExpressionStatement  ` （如  ` console.log(i)  ` ）
     * 支持所有合法的语句类型（  ` IfStatement  ` 、  ` BreakStatement  ` 等），通过  ` types.isStatement()  ` 统一判断
  5. ** 错误处理  ** ：对未知类型的循环体输出警告，便于调试和扩展。

依旧创建转换脚本：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    const babel = require("@babel/core");const { fix } = require("./your-script");// 测试代码const testCode = `// 表达式语句for (let i = 0; i < 5; i++)    console.log(i);// if语句for (let i = 0; i < 10; i++)    if (i % 2 === 0) doSomething();// 空循环体for (let i = 0; i < 3; i++);// break语句for (let i = 0; i < 10; i++)    if (i > 5) break;`;// 转换后输出console.log(babel.transformSync(testCode, {    plugins: [{ visitor: fix }]}).code);

转换结果如下（自动补全大括号）：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 表达式语句for (let i = 0; i < 5; i++) {    console.log(i);}// if语句for (let i = 0; i < 10; i++) {    if (i % 2 === 0) doSomething();}// 空循环体for (let i = 0; i < 3; i++) {}// break语句for (let i = 0; i < 10; i++) {    if (i > 5) break;}


接下来我们进行对return语句中的逗号表达式的格式修复  上代码：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    const types = require("@babel/types");// 遍历规则：处理 ReturnStatement 节点const traverseReturnSeqFix = {    ReturnStatement(path) {        fix(path);    }};/** * 修复 return 语句中的逗号表达式（SequenceExpression） * 将 return a, b, c 拆分为 a; b; return c * @param {import('@babel/traverse').NodePath} path - ReturnStatement 节点的路径对象 */function fix(path) {    const returnNode = path.node;    // 仅处理 return 后是逗号表达式的情况    if (!types.isSequenceExpression(returnNode.argument)) {        return;    }    // 提取逗号分隔的所有表达式（如 [a, b, c]）    const expressions = returnNode.argument.expressions;    // 至少需要两个表达式才需要拆分（单个表达式无需处理）    if (expressions.length <= 1) {        return;    }    // 前 N-1 个表达式转为独立的语句，最后一个作为 return 的值    const prefixStatements = expressions.slice(0, -1).map(expr =>         types.expressionStatement(expr)    );    const finalExpr = expressions[expressions.length - 1];    // 获取父节点的语句容器（如 BlockStatement 的 body、SwitchCase 的 consequent）    const parentPath = path.parentPath;    const parentNode = parentPath.node;    const containerKey = getContainerKey(parentNode.type);    if (!containerKey) {        console.warn(`未处理的父节点类型：${parentNode.type}，无法拆分 return 中的逗号表达式`);        return;    }    // 获取语句容器（存放 return 节点的数组）    const statementContainer = parentNode[containerKey];    // 获取 return 节点在容器中的索引（使用 path 定位，比 indexOf 可靠）    const returnIndex = path.key;    // 将前缀语句插入到 return 节点之前    statementContainer.splice(returnIndex, 0, ...prefixStatements);    // 更新 return 的参数为最后一个表达式    returnNode.argument = finalExpr;}/** * 根据父节点类型获取语句容器的 key（如 'body' 或 'consequent'） * @param {string} parentType - 父节点类型 * @returns {string|undefined} 容器 key，未处理的类型返回 undefined */function getContainerKey(parentType) {    switch (parentType) {        case 'BlockStatement':        case 'Program':            return 'body';        case 'SwitchCase':            return 'consequent';        default:            return undefined;    }}exports.fix = traverseReturnSeqFix;

###  代码核心逻辑说明

  1. ** 精准匹配目标场景  ** ：

     * 用  ` types.isSequenceExpression(returnNode.argument)  ` 判断 return 后是否为逗号表达式
     * 仅当表达式数量 >1 时才处理（单个表达式无需拆分）
  2. ** 拆分表达式  ** ：

     * 前 N-1 个表达式通过  ` map(expr => types.expressionStatement(expr))  ` 转为独立语句（如  ` a++  ` 转为  ` a++;  ` ）
     * 最后一个表达式作为新的 return 值（如  ` a + b  ` ）
  3. ** 定位插入位置  ** ：

     * 通过  ` getContainerKey  ` 适配不同父节点（函数体、switch case 等）的语句容器（如  ` BlockStatement  ` 的  ` body  ` 数组）
     * 用  ` path.key  ` 获取 return 语句在容器中的索引，确保前缀语句插入到正确位置
  4. ** 重构节点  ** ：

     * 用  ` splice  ` 将前缀语句插入到 return 之前
     * 更新 return 节点的参数为最后一个表达式，完成拆分

##  使用示例：

我们用测试代码验证工具的转换效果：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    const babel = require("@babel/core");const { fix } = require("./your-script");// 测试代码const testCode = `function demo() {    let x = 0;    return x++, x * 2, console.log(x), x + 1;}switch (a) {    case 1:        return a++, b--, a + b;}`;// 执行转换const result = babel.transformSync(testCode, {    plugins: [{ visitor: fix }]});console.log(result.code);

转换后的输出如下

  *   *   *   *   *   *   *   *   *   *   *   *   *


    function demo() {    let x = 0;    x++;    x * 2;    console.log(x);    return x + 1;}switch (a) {    case 1:        a++;        b--;        return a + b;}

可以看到，原 return 后的逗号表达式被拆分为多个独立语句。
js的语法千奇百怪，我这边也只是在自己做ast的时候发现的一些很常见的对我们用ast分析语法的时候有影响的语法格式问题，如果你也有什么关于ast分析时因js代码的格式导致的问题，欢迎在评论区留言探讨。
码字不易，如果真的有帮助可以顺手点个赞，你们的喜欢就是我更新的动力！
