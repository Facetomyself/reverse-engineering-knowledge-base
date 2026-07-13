# AST 语法树硬刚某宝第三弹：Babel修复格式（三）

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2025-10-26
> 归档日期: 2026-07-13
> 分类: web-reverse
>
> 今天我们接着之前的内容，继续进行js代码格式修复， 在 JavaScript 中，我们常会见到这样的代码：一行声明多个变量。 先看两个常见示例。

今天我们接着之前的内容，继续进行js代码格式修复，  在 JavaScript 中，我们常会见到这样的代码：一行声明多个变量。  先看两个常见示例：

  *   *   *   *


    // 示例1：多变量声明let a = 1, b = getValue(), c = a + b;// 示例2：逗号表达式赋值x = 10, y = x * 2, z = (y++, y + 5);

这种情况，对于我们用ast分析js代码是很不友好的，而且调试起来也麻烦，对于代码的可读性也差，容易漏掉一些细节性的代码。

理想的代码应该是每个声明 / 赋值单独成行：

  *   *   *   *   *   *   *


    // 拆分后let a = 1;let b = getValue();let c = a + b;x = 10;y = x * 2;z = (y++, y + 5);

##  实现思路：精准拆分与节点重构

核心目标是将复合语句拆分为独立语句，步骤如下：

  1. 遍历两种目标节点：  ` VariableDeclaration  ` （变量声明）和  ` ExpressionStatement  ` （表达式语句）
  2. 对多变量声明（如  ` let a=1, b=2  ` ）：拆分为多个单变量声明（  ` let a=1; let b=2;  ` ）
  3. 对逗号表达式赋值（如  ` x=1, y=2  ` ）：拆分为多个独立赋值语句（  ` x=1; y=2;  ` ）
  4. 将拆分后的语句插入原节点位置，替换原复合语句

##  核心代码解析

下面是实现该功能的完整代码，我们分模块解读：

###  1\. 遍历规则：锁定目标节点

  *   *   *   *   *   *   *   *   *   *   *   *   *   *


    const types = require("@babel/types");/** * 遍历规则：处理两种复合结构 * - VariableDeclaration：多变量声明（如 let a=1, b=2;） * - ExpressionStatement：逗号表达式赋值（如 x=1, y=2;） */const traverseConditionalVariableDeclarator = {    VariableDeclaration(path) {        fix(path, 'variable'); // 处理变量声明    },    ExpressionStatement(path) {        fix(path, 'assignment'); // 处理赋值表达式    }};

通过 Babel 的遍历机制，精准定位需要处理的节点类型，分别标记为 variable（变量声明）和 assignment（赋值表达式）。

###  2\. 核心处理函数：分发拆分逻辑


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    /** * 核心处理函数：拆分复合结构为独立语句 * @param {NodePath} path - 节点路径 * @param {'variable' | 'assignment'} type - 处理类型 */function fix(path, type) {    const node = path.node;    const splitNodes = []; // 存储拆分后的节点    // 根据类型拆分节点    if (type === 'variable') {        // 多变量声明：至少包含2个变量才需要拆分        if (node.declarations.length < 2) return;        splitNodes.push(...splitVariableDeclarations(node));    } else if (type === 'assignment') {        // 逗号表达式赋值：必须是逗号表达式且至少2个表达式        if (!types.isSequenceExpression(node.expression) || node.expression.expressions.length < 2) {            return;        }        splitNodes.push(...splitAssignmentExpressions(node.expression));    }    // 插入拆分后的节点    if (splitNodes.length > 0) {        insertSplitNodes(path, node, splitNodes);    }}

函数首先判断节点是否符合拆分条件（如多变量声明需包含至少 2 个变量），然后调用对应拆分函数生成独立节点，最后插入到代码中。

###  3\. 拆分逻辑：生成独立节点


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    /** * 拆分多变量声明为单个变量声明 * @param {VariableDeclaration} node - 变量声明节点 * @returns {VariableDeclaration[]} 拆分后的节点列表 */function splitVariableDeclarations(node) {    return node.declarations.map(declarator =>         // 保留原声明类型（let/const/var），每个声明只包含一个变量        types.variableDeclaration(node.kind, [declarator])    );}/** * 拆分逗号表达式赋值为单个表达式语句 * @param {SequenceExpression} expr - 逗号表达式节点 * @returns {ExpressionStatement[]} 拆分后的节点列表 */function splitAssignmentExpressions(expr) {    return expr.expressions.map(assignment =>         // 每个表达式单独作为一个表达式语句        types.expressionStatement(assignment)    );}

多变量声明拆分：将 let a=1, b=2 拆分为 let a=1 和 let b=2，保留原声明关键字（let/const/var）

逗号表达式拆分：将 x=1, y=2 拆分为 x=1 和 y=2，每个表达式  作为独立语句

###  4\. 节点插入：替换原复合语句


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    /** * 将拆分后的节点插入原位置，替换原节点 * @param {NodePath} path - 原节点路径 * @param {Node} originalNode - 原节点 * @param {Node[]} splitNodes - 拆分后的节点列表 */function insertSplitNodes(path, originalNode, splitNodes) {    const parentPath = path.parentPath;    if (!parentPath) return;    const parentNode = parentPath.node;    const { container, index } = getContainerAndIndex(path, parentNode);    if (!container || index === -1) {        console.warn(`无法处理父节点类型：${parentNode.type}`);        return;    }    // 替换原节点：删除原节点，插入拆分后的节点    container.splice(index, 1, ...splitNodes);}/** * 获取节点所在的容器（语句数组）和索引 * @param {NodePath} path - 节点路径 * @param {Node} parentNode - 父节点 * @returns {{ container: Node[] | null, index: number }} 容器和索引 */function getContainerAndIndex(path, parentNode) {    switch (parentNode.type) {        case 'Program': // 全局作用域        case 'BlockStatement': // 代码块（如函数体、if块）            return { container: parentNode.body, index: path.key };        case 'SwitchCase': // switch case 分支            return { container: parentNode.consequent, index: path.key };        case 'ForStatement': // for循环的init部分（如 for(let a=1, b=2;;)）            if (parentNode.init === path.node) {                const grandParent = path.parentPath.parent;                if (types.isBlockStatement(grandParent) || types.isProgram(grandParent)) {                    return { container: grandParent.body, index: path.parentPath.key };                }            }            console.warn('for循环中的复合结构未在init部分，无法处理');            return { container: null, index: -1 };        default:            return { container: null, index: -1 };    }}


这部分逻辑负责将拆分后的节点插入到正确位置，支持多种父节点场景（全局作用域、函数体、switch 分支、for
循环初始化部分等），确保拆分后的代码结构正确。

##  使用示例：

我们用测试代码验证工具的效果：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    const babel = require("@babel/core");const { fix } = require("./your-script");// 测试代码const testCode = `// 多变量声明let a = 1, b = 2, c = a + b;const x = 10, y = x * 2;// 逗号表达式赋值p = 5, q = p + 3, r = (q++, q * 2);// for循环中的多变量声明for (let i=0, j=10; i<j; i++, j--) {}`;// 执行转换const result = babel.transformSync(testCode, {    plugins: [{ visitor: fix }]});console.log(result.code);

转换后的输出如下：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 多变量声明拆分后let a = 1;let b = 2;let c = a + b;const x = 10;const y = x * 2;// 逗号表达式赋值拆分后p = 5;q = p + 3;r = (q++, q * 2);// for循环中的声明拆分后let i = 0;let j = 10;for (; i < j; i++, j--) {}

可以看到，所有复合结构都被拆分为独立语句。  这样做的意义就是，进行静态分析前置处理，降低复杂语句的解析难度。
js的语法千奇百怪，我这边也只是在自己做ast的时候发现的一些很常见的对我们用ast分析语法的时候有影响的语法格式问题，如果你也有什么关于ast分析时因js代码的格式导致的问题，欢迎在评论区留言探讨。
码字不易，如果真的有帮助可以顺手点个赞，你们的喜欢就是我更新的动力！


修改于
