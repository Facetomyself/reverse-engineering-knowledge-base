# AST 语法树硬刚某宝第一弹：先干原理

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2025-10-17
> 归档日期: 2026-07-13
> 分类: web-reverse
>
> 想了很久后续更新的内容，还是决定把之前搞某宝225算法的思路整理一下分享给大家，虽然现在更新到231版本了，但整体算法逻辑改变不大的情况下，破解思路是共通的，无非检测环境变多了，或者加了一点反制手段。之前搞225算法的时候就是觉得无从下手，多层控制流平坦化跳来跳去，根本就没办法直接阅读。后来查了很多资料，最终决定用ast脱混淆之后再研究。这里分享一下我的as。

想了很久后续更新的内容，还是决定把之前搞某宝225算法的思路整理一下分享给大家，虽然现在更新到231版本了，但整体算法逻辑改变不大的情况下，破解思路是共通的，无非检测环境变多了，或者加了一点反制手段。之前搞225算法的时候就是觉得无从下手，多层控制流平坦化跳来跳去，根本就没办法直接阅读。后来查了很多资料，最终决定用ast脱混淆之后再研究。这里分享一下我的ast跳坑之路，同时附上对我帮助最大的开源工具
---哲哥分享的自己的ast_tools(  https://github.com/sml2h3/ast_tools  )。哲哥牛批！！！

今天第一篇就先讲述一下ast语法树到底是啥，为啥用它来进行ast反混淆。

首先，被混淆过的 JS 代码 —— 变量名变成无意义的字母组合、函数嵌套层层叠加、逻辑被冗余代码包裹，直接阅读如同 “看天书”。此时，  ** AST
语法树（Abstract Syntax Tree，抽象语法树）  ** 就成了破解混淆的核心工具。

##  一、先搞懂：为什么 AST 能破解 JS 混淆？

在讲具体类型前，先简单理解 AST 的本质：它是 JS 代码经过 “词法分析”“语法分析” 后生成的  ** 树形结构抽象表示  **
。打个比方，混淆代码是 “揉成一团的毛线”，AST 就是把毛线拆解成 “一根根有序的线”，每根线对应代码的一个逻辑单元（比如变量声明、函数调用、条件判断）。

JS 混淆的核心手段，本质是 “破坏代码的可读性，但不改变代码的语法结构”—— 比如把  let username = "admin"  改成  let a
= "admin"  ，变量名变了，但 “变量声明” 这个语法类型没变；把  if (x > 10) { fn() }  改成  x>10&&fn()
，写法变了，但 “条件判断 + 函数调用” 的逻辑结构没变。

而 AST 能直接 “穿透” 这些表面修改，提取出代码的  ** 语法类型和逻辑关系  ** ，我们只要基于 AST
修改、还原这些结构，就能实现混淆破解（比如批量重命名变量、删除冗余代码、还原逻辑）。

##  二、核心：AST 语法化后的 JS 代码类型（附实例）

AST 的结构遵循统一的规范（如ESTree 规范，大多数 JS 解析器如 Acorn、Babel
都基于此）。我们不需要记住所有类型，只需掌握日常破解中最常见的 10 种，就能应对 80% 以上的场景。

以下所有实例，都可以在AST Explorer（在线 AST 可视化工具）中输入代码查看对应结构，建议边看边实操。

###  1\. 变量声明类：  VariableDeclaration + VariableDeclarator

** 作用  ** ：对应var/let/const声明变量的语句，是 AST 中最基础的类型之一。

** 结构拆解  ** ：

外层VariableDeclaration：表示 “这是一个变量声明语句”，有个关键属性kind（值为var/let/const，区分声明方式）。
内层VariableDeclarator：表示 “单个变量的声明细节”，包含两个核心子节点：
id：变量名（类型为Identifier，比如username）；  init：变量的初始值（可能是字符串、数字、函数等，类型随值变化）。

** 实例  ** ：

代码let username = "admin"; const age = 25;对应的 AST 结构（简化）：


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    {"type": "VariableDeclaration","kind": "let","declarations": [{"type": "VariableDeclarator","id": { "type": "Identifier", "name": "username" },"init": { "type": "Literal", "value": "admin", "raw": "\"admin\"" }}]},{"type": "VariableDeclaration","kind": "const","declarations": [{"type": "VariableDeclarator","id": { "type": "Identifier", "name": "age" },"init": { "type": "Literal", "value": 25, "raw": "25" }}]}

** 破解场景  **
：混淆代码中常把有意义的变量名（如username）改成a/b/x123，我们可以通过VariableDeclarator的init值（比如"admin"），批量将id.name改回有意义的名称。

###  2\. 字面量类：Literal

** 作用  ** ：对应代码中的 “直接值”，比如字符串、数字、布尔值、null，是变量初始值、函数参数的常见类型。

** 关键属性  ** ：

value：字面量的实际值（如"admin"、25、true）；
raw：字面量在代码中的原始写法（如字符串的"admin"、数字的0x19（十六进制））。

** 实例  ** ：

字符串"admin" → {"type":"Literal","value":"admin","raw":"\"admin\""}  十六进制数字0x19
→ {"type":"Literal","value":25,"raw":"0x19"}  布尔值false →
{"type":"Literal","value":false,"raw":"false"}

** 破解场景  ** ：混淆时可能把普通数字改成十六进制（如25→0x19）或
Unicode（如"admin"→"\u0061\u0064\u006D\u0069\u006E"），但Literal的value会直接显示真实值，我们可以基于value还原成可读性更高的写法。

###  3\. 标识符类：Identifier

** 作用  ** ：对应代码中的 “名称”，比如变量名、函数名、属性名（如username、getUser、obj.name中的name），是 AST 中
“引用” 的核心载体。

** 关键属性  ** ：

name：标识符的名称（如username、getUser）。

** 实例  ** ：

函数名function getUser() {} → {"type":"Identifier","name":"getUser"}
属性访问obj.name → {"type":"Identifier","name":"name"}（作为MemberExpression的子节点）

** 破解场景  ** ：混淆的核心就是修改Identifier的name（如getUser→f1），我们可以通过
“跟踪变量使用场景”（比如f1的参数是username，返回token），反向推断name的真实含义，再批量修改。

###  4\. 函数声明类：FunctionDeclaration

** 作用  ** ：对应function xxx() {}的函数声明语句，包含函数名、参数、函数体。

** 核心子节点  ** ：

id：函数名（Identifier类型，如getUser）；
params：函数参数列表（数组，每个元素是Identifier类型，如[{"type":"Identifier","name":"username"}]）；
body：函数体（BlockStatement类型，包含函数内的所有语句，如return token）。

** 实例  ** ：

代码function getUser(username) { return "token_" + username; }对应的 AST（简化）：


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    {  "type": "FunctionDeclaration",  "id": { "type": "Identifier", "name": "getUser" },  "params": [    { "type": "Identifier", "name": "username" }  ],  "body": {    "type": "BlockStatement",    "body": [      {        "type": "ReturnStatement",        "argument": {          "type": "BinaryExpression", // 字符串拼接，下文会讲          "operator": "+",          "left": { "type": "Literal", "value": "token_", "raw": "\"token_\"" },          "right": { "type": "Identifier", "name": "username" }        }      }    ]  }}

** 破解场景  **
：混淆时可能把函数名改成无意义的f/func123，且函数体可能嵌套多层冗余逻辑。我们可以通过params（参数）和body（函数体中的关键操作，如return、fetch请求）推断函数功能，再修改id.name还原函数名，同时删除body中的冗余语句。

###  5\. 函数调用类：CallExpression

** 作用  ** ：对应 “调用函数” 的语句（如getUser("admin")、console.log(123)），是跟踪代码逻辑流的关键。

** 核心子节点  ** ：

callee：被调用的函数（可能是Identifier类型，如getUser；也可能是MemberExpression类型，如console.log）；
arguments：函数参数列表（数组，每个元素的类型随参数类型变化，如Literal、Identifier）。

** 实例  ** ：

代码console.log("user:", username)对应的 AST（简化）：


  *   *   *   *   *   *   *   *   *   *   *   *   *


    {  "type": "CallExpression",  "callee": {    "type": "MemberExpression", // 成员访问，下文会讲    "object": { "type": "Identifier", "name": "console" },    "property": { "type": "Identifier", "name": "log" },    "computed": false // false表示用`.`访问（如console.log），true表示用[]访问（如console["log"]）  },  "arguments": [    { "type": "Literal", "value": "user:", "raw": "\"user:\"" },    { "type": "Identifier", "name": "username" }  ]}

**
**

** 破解场景  **
：混淆时可能把console.log改成window["console"]["log"]（通过MemberExpression的computed:
true实现），或把函数调用嵌套在多层括号中（如((getUser))("admin")）。但CallExpression的结构不会变，我们可以通过callee找到被调用的函数，通过arguments分析参数来源，跟踪逻辑流向（比如找到调用加密函数的地方，进而分析加密逻辑）。

###  6\. 成员访问类：MemberExpression

** 作用  ** ：对应 “访问对象属性”
的语法，如obj.name（点访问）、obj["name"]（方括号访问）、window.document（链式访问）。

** 核心子节点  ** ：

object：被访问的对象（如obj、window，类型为Identifier或MemberExpression）；
property：访问的属性（如name、document，类型为Identifier或Literal）；
computed：是否为方括号访问（true→方括号，false→点访问）。

** 实例  ** ：

点访问obj.name →
{"type":"MemberExpression","object":{"name":"obj"},"property":{"name":"name"},"computed":false}
方括号访问obj["name"] →
{"type":"MemberExpression","object":{"name":"obj"},"property":{"value":"name"},"computed":true}
链式访问window.document.body →
外层MemberExpression的object是内层MemberExpression（window.document）

** 破解场景  ** ：混淆时常用 “方括号 + 字符串拼接”
隐藏属性名，比如把obj.name改成obj["n"+"a"+"m"+"e"]。此时MemberExpression的property会变成BinaryExpression（字符串拼接），我们可以先计算property的实际值（"name"），再将computed改为false，还原成obj.name，提升可读性。

###  7\. 条件判断类：IfStatement

** 作用  ** ：对应if-else条件语句，是代码逻辑分支的核心类型。

** 核心子节点  ** ：

test：条件判断表达式（如x > 10，类型为BinaryExpression等）；
consequent：if成立时执行的代码（类型为BlockStatement，即{}包裹的语句）；
alternate：if不成立时执行的代码（即else部分，类型为BlockStatement或IfStatement，后者对应else if）。

** 实例  ** ：

代码if (age > 18) { console.log("成年"); } else { console.log("未成年"); }对应的
AST（简化）：


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    {  "type": "IfStatement",  "test": {    "type": "BinaryExpression",    "operator": ">",    "left": { "type": "Identifier", "name": "age" },    "right": { "type": "Literal", "value": 18, "raw": "18" }  },  "consequent": {    "type": "BlockStatement",    "body": [/* console.log("成年") 的CallExpression */]  },  "alternate": {    "type": "BlockStatement",    "body": [/* console.log("未成年") 的CallExpression */]  }}

** 破解场景  ** ：混淆时可能在test中加入冗余判断（如(age > 18) &&
true），或在consequent/alternate中插入无意义的代码（如var x = 1; x++;）。我们可以分析test的实际逻辑（删除&&
true这类冗余），并删除body中无实际作用的语句，还原清晰的条件分支。

###  8\. 二元表达式类：BinaryExpression

** 作用  ** ：对应 “二元运算” 语句，即需要两个操作数的运算（如x + y、a > b、c && d、e === f）。

** 核心子节点  ** ：

operator：运算符（如+、>、&&、===）；  left：左操作数（如x、a，类型随操作数变化）；
right：右操作数（如y、b，类型随操作数变化）。

** 实例  ** ：

加法a + b →
{"type":"BinaryExpression","operator":"+","left":{"name":"a"},"right":{"name":"b"}}
全等判断x === "admin" →
{"type":"BinaryExpression","operator":"===","left":{"name":"x"},"right":{"value":"admin"}}
逻辑与isLogin && hasPermission →
{"type":"BinaryExpression","operator":"&&","left":{"name":"isLogin"},"right":{"name":"hasPermission"}}

** 破解场景  ** ：混淆时常用 “多层二元表达式” 隐藏逻辑，比如把if (x > 10 && y < 20)改成x>10&&y<20（对应的 AST
是嵌套的BinaryExpression）。我们可以通过operator判断运算类型，逐步拆解多层表达式，还原成清晰的逻辑判断。

###  9\. 返回语句类：ReturnStatement

** 作用  ** ：对应函数中的return语句，是获取函数返回值、分析函数功能的关键。

** 核心子节点  ** ：

argument：返回的值（类型随返回值变化，如Literal、Identifier、BinaryExpression；若没有返回值，argument为null）。

** 实例  ** ：

return "token"; →
{"type":"ReturnStatement","argument":{"type":"Literal","value":"token"}}
return a + b; →
{"type":"ReturnStatement","argument":{"type":"BinaryExpression","operator":"+",...}}
return; → {"type":"ReturnStatement","argument":null}

** 破解场景  ** ：分析加密函数时，ReturnStatement的argument往往就是加密结果（如return
encryptResult）。我们可以定位到ReturnStatement，向上追溯argument的生成逻辑（比如是哪个函数的调用结果、基于哪些参数计算），从而破解加密算法。

###  10\. 块语句类：BlockStatement

** 作用  ** ：对应{}包裹的代码块（如函数体、if的{}、for循环的{}），是 AST 中 “语句集合” 的载体。

** 核心子节点  ** ：

body：代码块中的语句列表（数组，元素类型为VariableDeclaration、CallExpression、IfStatement等）。

** 实例  ** ：

代码{ let x = 1; console.log(x); }对应的 AST：


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    {  "type": "BlockStatement", // 块语句类型，对应{}包裹的代码块  "body": [    // 第一条语句：let x = 1（VariableDeclaration类型）    {      "type": "VariableDeclaration",      "kind": "let", // 声明方式为let      "declarations": [        {          "type": "VariableDeclarator",          "id": { "type": "Identifier", "name": "x" }, // 变量名x          "init": { "type": "Literal", "value": 1, "raw": "1" } // 初始值1        }      ]    },    // 第二条语句：console.log(x)（ExpressionStatement包裹CallExpression）    {      "type": "ExpressionStatement", // 表达式语句（函数调用需包裹在此类型中）      "expression": {        "type": "CallExpression", // 函数调用类型        "callee": {          "type": "MemberExpression", // 成员访问（console.log）          "object": { "type": "Identifier", "name": "console" }, // 对象console          "property": { "type": "Identifier", "name": "log" }, // 属性log          "computed": false // false=点访问，true=方括号访问        },        "arguments": [          { "type": "Identifier", "name": "x" } // 函数参数x        ]      }    }  ]}

接下来我们用一段代码的实际演示来讲解一下ast在破解js代码混淆中的作用

  *   *   *   *   *   *   *   *


    // 混淆点：变量名无意义（a/b/c/d）、字符串拼接隐藏属性、冗余条件var a = "user";const b = (x) => {  let c = x["na" + "me"]; // 方括号+字符串拼接隐藏属性名  return c ? (c.length > 3 ? true : false) : false; // 多层冗余条件};let d = { "name": "admin123" };console["log"](b(d) ? "通过" : "拒绝"); // 方括号访问console.log

我们构造了一段代码，其中包含了常见的混淆手段：无意义变量名、嵌套函数调用、冗余条件判断、字符串拼接隐藏属性名。  接下来，我们打  开  AST
Explorer  ，将这段代码粘贴进去，逐一拆解 AST 结构中对应的核心类型。

##  逐行拆解：AST 如何映射混淆代码？

###  1\. 顶层结构：Program（根节点）

所有 JS 代码的 AST 根节点都是Program，它的body属性是一个数组，包含代码中所有顶层语句（如变量声明、函数定义）。

我们实例代码的Program.body包含 4 个元素，对应 4 行核心代码：

  *   *   *   *


    VariableDeclaration（var a = "user"）VariableDeclaration（const b = (x) => {}，箭头函数）VariableDeclaration（let d = {name: "admin123"}）ExpressionStatement（console["log"](...)，函数调用语句）

###  2\. 第一行：var a = "user" → VariableDeclaration+VariableDeclarator+Literal

对应代码第一行的变量声明，AST 结构（简化）：


  *   *   *   *   *   *   *   *   *   *   *


    {  "type": "VariableDeclaration", // 变量声明语句  "kind": "var", // 声明方式为var  "declarations": [    {      "type": "VariableDeclarator", // 单个变量声明      "id": { "type": "Identifier", "name": "a" }, // 变量名a（混淆后的无意义名）      "init": { "type": "Literal", "value": "user", "raw": "\"user\"" } // 初始值"user"    }  ]}

**
**

** 关联类型  ** ：

VariableDeclaration（外层声明语句）：确定是var类型声明；
VariableDeclarator（内层变量细节）：id是Identifier（变量名 a），init是Literal（值 "user"）；
Literal：这里是字符串字面量，value直接显示真实值 “user”，不受混淆影响。

** 破解提示  ** ：通过init的value（“user”），可推断变量a的真实含义是 “用户相关标识”，后续可重命名为userKey。

###  3\. 第二行：const b = (x) => {} → 箭头函数相关类型

箭头函数在 AST 中对应ArrowFunctionExpression，它被包裹在VariableDeclaration中（因为用const b =
...声明）：

####  （1）外层：VariableDeclaration（声明箭头函数变量 b）


  *   *   *   *   *   *   *   *   *   *   *


    {  "type": "VariableDeclaration",  "kind": "const",  "declarations": [    {      "type": "VariableDeclarator",      "id": { "type": "Identifier", "name": "b" }, // 函数名b（混淆后）      "init": { "type": "ArrowFunctionExpression" } // 初始值是箭头函数    }  ]}


####  （2）内层：箭头函数 → ArrowFunctionExpression+BlockStatement

init的ArrowFunctionExpression结构（核心部分）：

  *   *   *   *   *   *   *   *   *   *


    {  "type": "ArrowFunctionExpression", // 箭头函数类型  "params": [{"type": "Identifier", "name": "x"}], // 函数参数x（混淆后）  "body": {    "type": "BlockStatement", // 函数体（{}包裹）    "body": [      // 函数体内的语句：let c = x["na"+"me"]、return ...    ]  }}


####  （3）函数体内第一句：let c = x["na"+"me"] → 多类型联动

这一句是混淆的核心（方括号 + 字符串拼接隐藏属性名），AST 结构涉及 4 种类型：


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // let c = x["na"+"me"] 对应的VariableDeclaration{  "type": "VariableDeclaration",  "kind": "let",  "declarations": [    {      "type": "VariableDeclarator",      "id": { "type": "Identifier", "name": "c" }, // 变量名c（混淆后）      "init": {        "type": "MemberExpression", // 成员访问（x["na"+"me"]）        "object": { "type": "Identifier", "name": "x" }, // 对象x        "property": {          "type": "BinaryExpression", // 二元表达式（字符串拼接）          "operator": "+",          "left": { "type": "Literal", "value": "na", "raw": "\"na\"" },          "right": { "type": "Literal", "value": "me", "raw": "\"me\"" }        },        "computed": true // true=方括号访问，false=点访问      }    }  ]}

**
**

** 关联类型拆解  ** ：

MemberExpression：对应x["na"+"me"]，computed: true表示方括号访问；
BinaryExpression：对应"na"+"me"，operator: "+"表示字符串拼接，left和right都是Literal（真实值 “na”
和 “me”）；  其他类型：VariableDeclaration（let 声明）、Identifier（变量 c、x）。

** 破解关键  ** ：AST 中BinaryExpression的value直接显示 “na” 和 “me”，可计算出拼接结果是
“name”，因此x["na"+"me"]实际是x.name，可还原为点访问提升可读性。

####  （4）函数体内 return：return c ? (c.length>3 ? true:false) : false → 多条件类型

这一句包含多层冗余条件（混淆手段），AST 结构涉及ReturnStatement+ConditionalExpression（三元表达式，对应? :）：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    {  "type": "ReturnStatement", // return语句  "argument": {    "type": "ConditionalExpression", // 外层三元表达式（c ? ... : false）    "test": { "type": "Identifier", "name": "c" }, // 条件1：c是否存在    "consequent": {      "type": "ConditionalExpression", // 内层三元表达式（c.length>3 ? ...）      "test": {        "type": "BinaryExpression", // 二元表达式（c.length>3）        "operator": ">",        "left": {          "type": "MemberExpression", // 成员访问（c.length）          "object": { "type": "Identifier", "name": "c" },          "property": { "type": "Identifier", "name": "length" },          "computed": false // 点访问        },        "right": { "type": "Literal", "value": 3, "raw": "3" }      },      "consequent": { "type": "Literal", "value": true }, // 结果true      "alternate": { "type": "Literal", "value": false } // 结果false    },    "alternate": { "type": "Literal", "value": false } // 外层else结果false  }}


** 关联类型拆解  ** ：

ReturnStatement：确定是 return 语句，argument是返回的三元表达式；  ConditionalExpression：对应?
:三元表达式，test是条件，consequent是 true 分支，alternate是 false 分支；
BinaryExpression：对应c.length > 3，operator: ">"是比较运算符；
MemberExpression：对应c.length，点访问属性。

** 破解关键  ** ：AST 暴露了冗余逻辑 —— 内层三元表达式c.length>3 ? true :
false完全等价于c.length>3，可直接删除冗余，还原为return c && c.length>3。

###  4\. 第四行：let d = {name: "admin123"} → ObjectExpression

这一行是对象字面量声明，AST 中对应ObjectExpression类型：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    {  "type": "VariableDeclaration",  "kind": "let",  "declarations": [    {      "type": "VariableDeclarator",      "id": { "type": "Identifier", "name": "d" }, // 变量名d（混淆后）      "init": {        "type": "ObjectExpression", // 对象字面量        "properties": [          {            "type": "Property", // 对象属性            "key": { "type": "Literal", "value": "name", "raw": "\"name\"" }, // 属性名name            "value": { "type": "Literal", "value": "admin123", "raw": "\"admin123\"" } // 属性值          }        ]      }    }  ]}


** 关联类型  ** ：ObjectExpression（对象）包含Property（属性），key和value都是Literal。

** 破解提示  ** ：通过对象属性key: "name"和值"admin123"，可推断变量d是 “用户信息对象”，重命名为userInfo。

###  5\. 第五行：console["log"](b(d) ? ...) → 多类型嵌套

这一行是函数调用语句，是整个代码的 “执行入口”，AST 结构最复杂但也最关键：

####  （1）外层：ExpressionStatement（表达式语句）

函数调用本身是 “表达式”，需要包裹在ExpressionStatement中才能成为顶层语句：


  *   *   *   *


    {  "type": "ExpressionStatement",  "expression": { "type": "CallExpression" } // 函数调用表达式}

####  （2）中层：CallExpression（调用 console ["log"]）


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    {  "type": "CallExpression", // 函数调用  "callee": {    "type": "MemberExpression", // 成员访问（console["log"]）    "object": { "type": "Identifier", "name": "console" }, // 对象console    "property": { "type": "Literal", "value": "log", "raw": "\"log\"" }, // 属性log    "computed": true // 方括号访问（混淆手段）  },  "arguments": [    // 函数参数：b(d) ? "通过" : "拒绝"（三元表达式）    {      "type": "ConditionalExpression",      "test": {        "type": "CallExpression", // 调用函数b(d)        "callee": { "type": "Identifier", "name": "b" }, // 被调用函数b        "arguments": [{"type": "Identifier", "name": "d"}] // 参数d      },      "consequent": { "type": "Literal", "value": "通过" },      "alternate": { "type": "Literal", "value": "拒绝" }    }  ]}

** 关联类型拆解  ** ：

CallExpression：两次出现 —— 一次是调用console.log，一次是调用b(d)；
MemberExpression：对应console["log"]，computed: true是混淆手段，可还原为console.log；
ConditionalExpression：对应b(d) ? "通过" : "拒绝"，判断函数调用结果；
Identifier：b（函数名）和d（参数名）都是混淆后的无意义名。

** 破解关键  **
：通过CallExpression的arguments（参数是d，即用户信息对象）和返回值判断（"通过"/"拒绝"），可推断函数b的作用是
“校验用户名”，重命名为checkUsername。

##  总结：AST 如何 “破解” 这段混淆代码？

通过上面的拆解，我们基于 AST 还原了混淆代码的真实逻辑，最终可将原代码优化为：


  *   *   *   *   *   *   *   *


    // 基于AST还原：变量名有意义、删除冗余、还原点访问var userKey = "user";const checkUsername = (userInfo) => {  let username = userInfo.name; // 还原为点访问（AST计算字符串拼接结果）  return userInfo.name && userInfo.name.length > 3; // 删除冗余条件};let userInfo = { "name": "admin123" };console.log(checkUsername(userInfo) ? "通过" : "拒绝"); // 还原console.log


这个过程中，AST 的核心作用是：

  1. ** 穿透混淆  ** ：无论变量名多乱、字符串如何拼接，AST 的type和value属性都会暴露真实逻辑；

  2. ** 结构化拆解  ** ：将嵌套的代码（如多层三元、函数调用）拆分为独立节点，便于定位冗余和修改；

  3. ** 精准还原  ** ：基于节点类型（如BinaryExpression的字符串拼接、MemberExpression的方括号访问），可批量自动化还原代码可读性。

##  四、实操建议：用 AST 工具批量处理混淆

如果遇到更复杂的混淆（如几百行代码），手动拆解不现实，可基于 AST 工具批量处理：

  1. ** 解析代码  ** ：用 Acorn/Babel Parser 将 JS 代码解析为 AST；

  2. ** 遍历修改  ** ：用@babel/traverse遍历 AST 节点，批量重命名变量（如将a改为userKey）、删除冗余节点（如冗余三元表达式）；

  3. ** 生成代码  ** ：用@babel/generator将修改后的 AST 重新生成可读性高的 JS 代码。

后续我们会专门讲解如何用这些工具编写自动化破解脚本，让 AST 从 “分析工具” 变成 “破解工具”。

如果大家在实际操作中遇到复杂混淆场景（如带加密 state 的多层平坦化），或者想了解其他混淆技术（如字符串加密、控制流伪造）的 AST
反混淆方法，欢迎在评论区留言讨论！


关注该公众号

[ 知道了 ](javascript:;)

使用小程序
