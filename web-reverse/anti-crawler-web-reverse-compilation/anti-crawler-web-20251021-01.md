# AST 语法树硬刚某宝第二弹：Babel修复格式（一）

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2025-10-21
> 归档日期: 2026-07-13
> 分类: web-reverse
>
> 在我们想要用ast语法树处理很多很复杂的逻辑时，我们要先清洗一下代码的格式，众所周知，js或许不是世界上最好的语言，但一定是世界上最骚的语言，js能做出来的骚操作层出不穷。 就比如。

在我们想要用ast语法树处理很多很复杂的逻辑时，我们要先清洗一下代码的格式，众所周知，js或许不是世界上最好的语言，但一定是世界上最骚的语言，js能做出来的骚操作层出不穷。
就比如：

####  1\. 不带大括号的写法：  ` if (a > 10) a = 0;  `

其 AST 中，  ` IfStatement  ` 的  ` consequent  ` （分支主体）是一个  **`
AssignmentExpression  ` 节点  ** （直接对应  ` a = 0  ` 这条语句）。

简化的 AST 结构：

  *   *   *   *   *   *   *   *   *   *   *


    {  type: "IfStatement",  test: { type: "BinaryExpression", operator: ">", left: { type: "Identifier", name: "a" }, right: { type: "NumericLiteral", value: 10 } },  consequent: {     type: "AssignmentExpression",  // 直接是赋值表达式节点    operator: "=",    left: { type: "Identifier", name: "a" },    right: { type: "NumericLiteral", value: 0 }  },  alternate: null  // 没有else分支}

####  2\. 带大括号的写法：  ` if (a > 10) { a = 0; }  `

其 AST 中，  ` IfStatement  ` 的  ` consequent  ` 是一个  **` BlockStatement  ` 节点
** （块语句），而  ` a = 0  ` 被包裹在  ` BlockStatement  ` 的  ` body  ` 数组中。

简化的 AST 结构：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    {  type: "IfStatement",  test: { /* 与上面相同：a > 10 的表达式 */ },  consequent: {     type: "BlockStatement",  // 块语句节点    body: [      {         type: "ExpressionStatement",  // 包裹赋值表达式的语句节点        expression: {           type: "AssignmentExpression",  // 内部才是a = 0          operator: "=",          left: { type: "Identifier", name: "a" },          right: { type: "NumericLiteral", value: 0 }        }      }    ]  },  alternate: null}

这种差异就可能导致我们在处理很多很复杂的js代码时，出现不可预料的问题，所以，在真正进行ast语法树解混淆之前，我们都会先对其进行格式修复。同时规范化后的代码阅读起来也更流畅。统一
` if  ` 语句的格式，避免因分支是否带大括号导致的语法歧义或风格不一致问题。

接下来我们就要用到Babel来进行处理，我们需要：

  * 识别 IfStatement 节点
  * 检查它的分支是否为 BlockStatement（代码块）
  * 对非代码块的分支进行包裹处理

下面是实现这个功能的核心代码，我们逐行解读：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    const types = require("@babel/types");// 定义遍历规则：只处理 IfStatement 节点const traverse_ifexpress = {    IfStatement(path) {        fix(path);    }};/** * 处理 if 语句分支无大括号的情况，统一包裹为 BlockStatement * @param {Object} path - Babel 路径对象 */function fix(path) {    const node = path.node;    // 处理 if 分支（consequent）    if (!types.isBlockStatement(node.consequent)) {        // 若分支为空（null），则创建空块；否则用块包裹当前语句        node.consequent = types.blockStatement(            node.consequent ? [node.consequent] : []        );    }    // 处理 else 分支（alternate）    if (node.alternate) {        // 特殊处理：若 else 分支是 if 语句（即 else if），则不包裹        if (!types.isBlockStatement(node.alternate) && !types.isIfStatement(node.alternate)) {            node.alternate = types.blockStatement([node.alternate]);        }    } else {        // 若 else 分支为空，可选择创建空块（按需开启）        // node.alternate = types.blockStatement([]);    }}exports.fix = traverse_ifexpress;

###  代码关键点说明

  1. ** 类型判断  ** 使用  ` types.isBlockStatement()  ` 检查分支是否已用大括号包裹
  2. ** 节点转换  ** 通过  ` types.blockStatement()  ` 创建新的代码块节点
  3. ** 特殊处理  ** 对  ` else if  ` 结构做了兼容（不包裹内部的 if 语句）
  4. ** 空分支处理  ** 考虑了分支为空的边界情

接下来就是运行测试，注意我们这里是必须要先安装依赖：

  *


    npm install @babel/core @babel/traverse @babel/generator

然后就可以运行测试,写个调用文件：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    const babel = require("@babel/core");const { fix } = require("./your-script-file");function transformCode(code) {  return babel.transformSync(code, {    plugins: [{      visitor: fix    }]  }).code;}// 测试转换效果const testCode = `if (a) console.log(a);else if (b) console.log(b);else console.log(c);`;console.log(transformCode(testCode));

可以看到我们输出得结果是：

  *   *   *   *   *   *   *   *   *   *


    if (a) {  console.log(a);} else if (b) {  console.log(b);} else {  console.log(c);}//if (a) console.log(a);//else if (b) console.log(b);//else console.log(c); 对比之前成功增加了大括号

当然我们还可以增加更多功能，这里我们只先实现得最常见的情况，之后我们还会更新更多的修复格式的小脚本。
码字不易，如果真的有帮助可以顺手点个赞，你们的喜欢就是我更新的动力！
