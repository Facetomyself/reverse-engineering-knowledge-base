# AST 语法树硬刚某宝（七篇）：原理、Babel 修复格式、多层三元拆解、提取控制器与无用分支

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2025-10-17 ~ 2026-01-29（7 篇，逐篇日期见各节）
> 归档日期: 2026-07-13
> 分类: web-reverse
>
> 本文合并同一作者的 7 篇连载：第一篇「AST 语法树硬刚某宝第一弹：先干原理」、第二篇「AST 语法树硬刚某宝第二弹：Babel修复格式（一）」、第三篇「AST 语法树硬刚某宝第二弹：Babel修复格式（二）」、第四篇「AST 语法树硬刚某宝第三弹：Babel修复格式（三）」、第五篇「AST 语法树硬刚某宝第四弹：多层三元表达式拆解」、第六篇「AST 语法树硬刚某宝：提取控制器」、第七篇「AST 语法树硬刚某宝：无用分支破解思路」。

## 收录说明

本文由原先分开归档的 7 篇连载合并而成（2026-09-26 整理）。各节标题为「篇次：原标题」，下方一行保留该篇自己的来源与发布日期；原文标题层级整体下调，正文未删减。原各篇文件头部的自动摘要只是正文开头的节选，合并时不再重复保留。原文编号为「第一弹」「第二弹（一）」「第二弹（二）」「第三弹（三）」「第四弹」及两篇未编号续作，这里按发布日期顺序编为第一～七篇，各节保留原标题。合并前文件：`anti-crawler-web-20251017-01.md`（保留路径）、`anti-crawler-web-20251021-01.md`、`anti-crawler-web-20251023-01.md`、`anti-crawler-web-20251026-01.md`、`anti-crawler-web-20251101-01.md`、`anti-crawler-web-20260122-01.md`、`anti-crawler-web-20260129-01.md`（已删除）。

## 第一篇：AST 语法树硬刚某宝第一弹：先干原理

来源：微信公众号：反爬破解社 · 原始发布时间：2025-10-17 · 归档日期：2026-07-13

想了很久后续更新的内容，还是决定把之前搞某宝225算法的思路整理一下分享给大家，虽然现在更新到231版本了，但整体算法逻辑改变不大的情况下，破解思路是共通的，无非检测环境变多了，或者加了一点反制手段。之前搞225算法的时候就是觉得无从下手，多层控制流平坦化跳来跳去，根本就没办法直接阅读。后来查了很多资料，最终决定用ast脱混淆之后再研究。这里分享一下我的ast跳坑之路，同时附上对我帮助最大的开源工具
---哲哥分享的自己的ast_tools(  https://github.com/sml2h3/ast_tools  )。哲哥牛批！！！

今天第一篇就先讲述一下ast语法树到底是啥，为啥用它来进行ast反混淆。

首先，被混淆过的 JS 代码 —— 变量名变成无意义的字母组合、函数嵌套层层叠加、逻辑被冗余代码包裹，直接阅读如同 “看天书”。此时，  ** AST
语法树（Abstract Syntax Tree，抽象语法树）  ** 就成了破解混淆的核心工具。

###  一、先搞懂：为什么 AST 能破解 JS 混淆？

在讲具体类型前，先简单理解 AST 的本质：它是 JS 代码经过 “词法分析”“语法分析” 后生成的  ** 树形结构抽象表示  **
。打个比方，混淆代码是 “揉成一团的毛线”，AST 就是把毛线拆解成 “一根根有序的线”，每根线对应代码的一个逻辑单元（比如变量声明、函数调用、条件判断）。

JS 混淆的核心手段，本质是 “破坏代码的可读性，但不改变代码的语法结构”—— 比如把  let username = "admin"  改成  let a
= "admin"  ，变量名变了，但 “变量声明” 这个语法类型没变；把  if (x > 10) { fn() }  改成  x>10&&fn()
，写法变了，但 “条件判断 + 函数调用” 的逻辑结构没变。

而 AST 能直接 “穿透” 这些表面修改，提取出代码的  ** 语法类型和逻辑关系  ** ，我们只要基于 AST
修改、还原这些结构，就能实现混淆破解（比如批量重命名变量、删除冗余代码、还原逻辑）。

###  二、核心：AST 语法化后的 JS 代码类型（附实例）

AST 的结构遵循统一的规范（如ESTree 规范，大多数 JS 解析器如 Acorn、Babel
都基于此）。我们不需要记住所有类型，只需掌握日常破解中最常见的 10 种，就能应对 80% 以上的场景。

以下所有实例，都可以在AST Explorer（在线 AST 可视化工具）中输入代码查看对应结构，建议边看边实操。

####  1\. 变量声明类：  VariableDeclaration + VariableDeclarator

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

####  2\. 字面量类：Literal

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

####  3\. 标识符类：Identifier

** 作用  ** ：对应代码中的 “名称”，比如变量名、函数名、属性名（如username、getUser、obj.name中的name），是 AST 中
“引用” 的核心载体。

** 关键属性  ** ：

name：标识符的名称（如username、getUser）。

** 实例  ** ：

函数名function getUser() {} → {"type":"Identifier","name":"getUser"}
属性访问obj.name → {"type":"Identifier","name":"name"}（作为MemberExpression的子节点）

** 破解场景  ** ：混淆的核心就是修改Identifier的name（如getUser→f1），我们可以通过
“跟踪变量使用场景”（比如f1的参数是username，返回token），反向推断name的真实含义，再批量修改。

####  4\. 函数声明类：FunctionDeclaration

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

####  5\. 函数调用类：CallExpression

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

####  6\. 成员访问类：MemberExpression

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

####  7\. 条件判断类：IfStatement

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

####  8\. 二元表达式类：BinaryExpression

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

####  9\. 返回语句类：ReturnStatement

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

####  10\. 块语句类：BlockStatement

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

###  逐行拆解：AST 如何映射混淆代码？

####  1\. 顶层结构：Program（根节点）

所有 JS 代码的 AST 根节点都是Program，它的body属性是一个数组，包含代码中所有顶层语句（如变量声明、函数定义）。

我们实例代码的Program.body包含 4 个元素，对应 4 行核心代码：

  *   *   *   *


    VariableDeclaration（var a = "user"）VariableDeclaration（const b = (x) => {}，箭头函数）VariableDeclaration（let d = {name: "admin123"}）ExpressionStatement（console["log"](...)，函数调用语句）

####  2\. 第一行：var a = "user" → VariableDeclaration+VariableDeclarator+Literal

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

####  3\. 第二行：const b = (x) => {} → 箭头函数相关类型

箭头函数在 AST 中对应ArrowFunctionExpression，它被包裹在VariableDeclaration中（因为用const b =
...声明）：

#####  （1）外层：VariableDeclaration（声明箭头函数变量 b）


  *   *   *   *   *   *   *   *   *   *   *


    {  "type": "VariableDeclaration",  "kind": "const",  "declarations": [    {      "type": "VariableDeclarator",      "id": { "type": "Identifier", "name": "b" }, // 函数名b（混淆后）      "init": { "type": "ArrowFunctionExpression" } // 初始值是箭头函数    }  ]}


#####  （2）内层：箭头函数 → ArrowFunctionExpression+BlockStatement

init的ArrowFunctionExpression结构（核心部分）：

  *   *   *   *   *   *   *   *   *   *


    {  "type": "ArrowFunctionExpression", // 箭头函数类型  "params": [{"type": "Identifier", "name": "x"}], // 函数参数x（混淆后）  "body": {    "type": "BlockStatement", // 函数体（{}包裹）    "body": [      // 函数体内的语句：let c = x["na"+"me"]、return ...    ]  }}


#####  （3）函数体内第一句：let c = x["na"+"me"] → 多类型联动

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

#####  （4）函数体内 return：return c ? (c.length>3 ? true:false) : false → 多条件类型

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

####  4\. 第四行：let d = {name: "admin123"} → ObjectExpression

这一行是对象字面量声明，AST 中对应ObjectExpression类型：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    {  "type": "VariableDeclaration",  "kind": "let",  "declarations": [    {      "type": "VariableDeclarator",      "id": { "type": "Identifier", "name": "d" }, // 变量名d（混淆后）      "init": {        "type": "ObjectExpression", // 对象字面量        "properties": [          {            "type": "Property", // 对象属性            "key": { "type": "Literal", "value": "name", "raw": "\"name\"" }, // 属性名name            "value": { "type": "Literal", "value": "admin123", "raw": "\"admin123\"" } // 属性值          }        ]      }    }  ]}


** 关联类型  ** ：ObjectExpression（对象）包含Property（属性），key和value都是Literal。

** 破解提示  ** ：通过对象属性key: "name"和值"admin123"，可推断变量d是 “用户信息对象”，重命名为userInfo。

####  5\. 第五行：console["log"](b(d) ? ...) → 多类型嵌套

这一行是函数调用语句，是整个代码的 “执行入口”，AST 结构最复杂但也最关键：

#####  （1）外层：ExpressionStatement（表达式语句）

函数调用本身是 “表达式”，需要包裹在ExpressionStatement中才能成为顶层语句：


  *   *   *   *


    {  "type": "ExpressionStatement",  "expression": { "type": "CallExpression" } // 函数调用表达式}

#####  （2）中层：CallExpression（调用 console ["log"]）


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

###  总结：AST 如何 “破解” 这段混淆代码？

通过上面的拆解，我们基于 AST 还原了混淆代码的真实逻辑，最终可将原代码优化为：


  *   *   *   *   *   *   *   *


    // 基于AST还原：变量名有意义、删除冗余、还原点访问var userKey = "user";const checkUsername = (userInfo) => {  let username = userInfo.name; // 还原为点访问（AST计算字符串拼接结果）  return userInfo.name && userInfo.name.length > 3; // 删除冗余条件};let userInfo = { "name": "admin123" };console.log(checkUsername(userInfo) ? "通过" : "拒绝"); // 还原console.log


这个过程中，AST 的核心作用是：

  1. ** 穿透混淆  ** ：无论变量名多乱、字符串如何拼接，AST 的type和value属性都会暴露真实逻辑；

  2. ** 结构化拆解  ** ：将嵌套的代码（如多层三元、函数调用）拆分为独立节点，便于定位冗余和修改；

  3. ** 精准还原  ** ：基于节点类型（如BinaryExpression的字符串拼接、MemberExpression的方括号访问），可批量自动化还原代码可读性。

###  四、实操建议：用 AST 工具批量处理混淆

如果遇到更复杂的混淆（如几百行代码），手动拆解不现实，可基于 AST 工具批量处理：

  1. ** 解析代码  ** ：用 Acorn/Babel Parser 将 JS 代码解析为 AST；

  2. ** 遍历修改  ** ：用@babel/traverse遍历 AST 节点，批量重命名变量（如将a改为userKey）、删除冗余节点（如冗余三元表达式）；

  3. ** 生成代码  ** ：用@babel/generator将修改后的 AST 重新生成可读性高的 JS 代码。

后续我们会专门讲解如何用这些工具编写自动化破解脚本，让 AST 从 “分析工具” 变成 “破解工具”。

如果大家在实际操作中遇到复杂混淆场景（如带加密 state 的多层平坦化），或者想了解其他混淆技术（如字符串加密、控制流伪造）的 AST
反混淆方法，欢迎在评论区留言讨论！

## 第二篇：AST 语法树硬刚某宝第二弹：Babel修复格式（一）

来源：微信公众号：反爬破解社 · 原始发布时间：2025-10-21 · 归档日期：2026-07-13

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

## 第三篇：AST 语法树硬刚某宝第二弹：Babel修复格式（二）

来源：微信公众号：反爬破解社 · 原始发布时间：2025-10-23 · 归档日期：2026-07-13

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

####  代码关键点说明

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

####  代码核心逻辑说明

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

###  使用示例：

我们用测试代码验证工具的转换效果：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    const babel = require("@babel/core");const { fix } = require("./your-script");// 测试代码const testCode = `function demo() {    let x = 0;    return x++, x * 2, console.log(x), x + 1;}switch (a) {    case 1:        return a++, b--, a + b;}`;// 执行转换const result = babel.transformSync(testCode, {    plugins: [{ visitor: fix }]});console.log(result.code);

转换后的输出如下

  *   *   *   *   *   *   *   *   *   *   *   *   *


    function demo() {    let x = 0;    x++;    x * 2;    console.log(x);    return x + 1;}switch (a) {    case 1:        a++;        b--;        return a + b;}

可以看到，原 return 后的逗号表达式被拆分为多个独立语句。
js的语法千奇百怪，我这边也只是在自己做ast的时候发现的一些很常见的对我们用ast分析语法的时候有影响的语法格式问题，如果你也有什么关于ast分析时因js代码的格式导致的问题，欢迎在评论区留言探讨。
码字不易，如果真的有帮助可以顺手点个赞，你们的喜欢就是我更新的动力！

## 第四篇：AST 语法树硬刚某宝第三弹：Babel修复格式（三）

来源：微信公众号：反爬破解社 · 原始发布时间：2025-10-26 · 归档日期：2026-07-13

今天我们接着之前的内容，继续进行js代码格式修复，  在 JavaScript 中，我们常会见到这样的代码：一行声明多个变量。  先看两个常见示例：

  *   *   *   *


    // 示例1：多变量声明let a = 1, b = getValue(), c = a + b;// 示例2：逗号表达式赋值x = 10, y = x * 2, z = (y++, y + 5);

这种情况，对于我们用ast分析js代码是很不友好的，而且调试起来也麻烦，对于代码的可读性也差，容易漏掉一些细节性的代码。

理想的代码应该是每个声明 / 赋值单独成行：

  *   *   *   *   *   *   *


    // 拆分后let a = 1;let b = getValue();let c = a + b;x = 10;y = x * 2;z = (y++, y + 5);

###  实现思路：精准拆分与节点重构

核心目标是将复合语句拆分为独立语句，步骤如下：

  1. 遍历两种目标节点：  ` VariableDeclaration  ` （变量声明）和  ` ExpressionStatement  ` （表达式语句）
  2. 对多变量声明（如  ` let a=1, b=2  ` ）：拆分为多个单变量声明（  ` let a=1; let b=2;  ` ）
  3. 对逗号表达式赋值（如  ` x=1, y=2  ` ）：拆分为多个独立赋值语句（  ` x=1; y=2;  ` ）
  4. 将拆分后的语句插入原节点位置，替换原复合语句

###  核心代码解析

下面是实现该功能的完整代码，我们分模块解读：

####  1\. 遍历规则：锁定目标节点

  *   *   *   *   *   *   *   *   *   *   *   *   *   *


    const types = require("@babel/types");/** * 遍历规则：处理两种复合结构 * - VariableDeclaration：多变量声明（如 let a=1, b=2;） * - ExpressionStatement：逗号表达式赋值（如 x=1, y=2;） */const traverseConditionalVariableDeclarator = {    VariableDeclaration(path) {        fix(path, 'variable'); // 处理变量声明    },    ExpressionStatement(path) {        fix(path, 'assignment'); // 处理赋值表达式    }};

通过 Babel 的遍历机制，精准定位需要处理的节点类型，分别标记为 variable（变量声明）和 assignment（赋值表达式）。

####  2\. 核心处理函数：分发拆分逻辑


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    /** * 核心处理函数：拆分复合结构为独立语句 * @param {NodePath} path - 节点路径 * @param {'variable' | 'assignment'} type - 处理类型 */function fix(path, type) {    const node = path.node;    const splitNodes = []; // 存储拆分后的节点    // 根据类型拆分节点    if (type === 'variable') {        // 多变量声明：至少包含2个变量才需要拆分        if (node.declarations.length < 2) return;        splitNodes.push(...splitVariableDeclarations(node));    } else if (type === 'assignment') {        // 逗号表达式赋值：必须是逗号表达式且至少2个表达式        if (!types.isSequenceExpression(node.expression) || node.expression.expressions.length < 2) {            return;        }        splitNodes.push(...splitAssignmentExpressions(node.expression));    }    // 插入拆分后的节点    if (splitNodes.length > 0) {        insertSplitNodes(path, node, splitNodes);    }}

函数首先判断节点是否符合拆分条件（如多变量声明需包含至少 2 个变量），然后调用对应拆分函数生成独立节点，最后插入到代码中。

####  3\. 拆分逻辑：生成独立节点


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    /** * 拆分多变量声明为单个变量声明 * @param {VariableDeclaration} node - 变量声明节点 * @returns {VariableDeclaration[]} 拆分后的节点列表 */function splitVariableDeclarations(node) {    return node.declarations.map(declarator =>         // 保留原声明类型（let/const/var），每个声明只包含一个变量        types.variableDeclaration(node.kind, [declarator])    );}/** * 拆分逗号表达式赋值为单个表达式语句 * @param {SequenceExpression} expr - 逗号表达式节点 * @returns {ExpressionStatement[]} 拆分后的节点列表 */function splitAssignmentExpressions(expr) {    return expr.expressions.map(assignment =>         // 每个表达式单独作为一个表达式语句        types.expressionStatement(assignment)    );}

多变量声明拆分：将 let a=1, b=2 拆分为 let a=1 和 let b=2，保留原声明关键字（let/const/var）

逗号表达式拆分：将 x=1, y=2 拆分为 x=1 和 y=2，每个表达式  作为独立语句

####  4\. 节点插入：替换原复合语句


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    /** * 将拆分后的节点插入原位置，替换原节点 * @param {NodePath} path - 原节点路径 * @param {Node} originalNode - 原节点 * @param {Node[]} splitNodes - 拆分后的节点列表 */function insertSplitNodes(path, originalNode, splitNodes) {    const parentPath = path.parentPath;    if (!parentPath) return;    const parentNode = parentPath.node;    const { container, index } = getContainerAndIndex(path, parentNode);    if (!container || index === -1) {        console.warn(`无法处理父节点类型：${parentNode.type}`);        return;    }    // 替换原节点：删除原节点，插入拆分后的节点    container.splice(index, 1, ...splitNodes);}/** * 获取节点所在的容器（语句数组）和索引 * @param {NodePath} path - 节点路径 * @param {Node} parentNode - 父节点 * @returns {{ container: Node[] | null, index: number }} 容器和索引 */function getContainerAndIndex(path, parentNode) {    switch (parentNode.type) {        case 'Program': // 全局作用域        case 'BlockStatement': // 代码块（如函数体、if块）            return { container: parentNode.body, index: path.key };        case 'SwitchCase': // switch case 分支            return { container: parentNode.consequent, index: path.key };        case 'ForStatement': // for循环的init部分（如 for(let a=1, b=2;;)）            if (parentNode.init === path.node) {                const grandParent = path.parentPath.parent;                if (types.isBlockStatement(grandParent) || types.isProgram(grandParent)) {                    return { container: grandParent.body, index: path.parentPath.key };                }            }            console.warn('for循环中的复合结构未在init部分，无法处理');            return { container: null, index: -1 };        default:            return { container: null, index: -1 };    }}


这部分逻辑负责将拆分后的节点插入到正确位置，支持多种父节点场景（全局作用域、函数体、switch 分支、for
循环初始化部分等），确保拆分后的代码结构正确。

###  使用示例：

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

## 第五篇：AST 语法树硬刚某宝第四弹：多层三元表达式拆解

来源：微信公众号：反爬破解社 · 原始发布时间：2025-11-01 · 归档日期：2026-07-13

搞某宝的时候我们经常能看到下面的  “反人类”  代码，  一行代码里塞了四五个三元表达式，夹杂着数组
push、字符串反转和变量赋值，盯着看十分钟还没理清逻辑分支：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    void (  3 == a ?     (li.push(_i.alert, _i[vi], Yi, Dn, ev, un, _i[Bv], Cv, _i[Wn]),     Xi = li, li = [], Dn = "Sc", Dn += "ree",     (Yi = []).push(_i[Dn += "n"], ai), Dn = Yi, Yi = [], n = 48) :     a < 3 ?       1 == a ?         (Av = Yi[Cv], n = Av ? 41 : 51) :         a < 1 ? (li++, n = 33) : (Cv++, n = 36) :       5 == a ?         (mr = gr <= hr, kv = 0 !== $.length,          n = (Cr = (hr = mr * mr) > -126) ? 49 : 1) :         a < 5 ?           (Yi = Xi.join(Zk), si = Xi = li = Yi, n = 9) :           (ev = "MouseEvent", un = "x", Yi.push(_i[ev], un), un = Yi, Yi = [],           Cv = (Cv = "Xtnemevom").split("").reverse().join(""),           Yi.push(_i[ev], Cv), ev = Yi, Yi = [], n = 17));break;

这种嵌套多层、操作密集的三元表达式，堪称 “代码阅读理解题” 的天花板。今天我们就用 Babel 打造一个 “代码翻译官”，把它自动拆成直观的 if-
else 语句，让逻辑一目了然。


###  为什么要拆？嵌套三元的 3 个致命问题

先别急着写工具，我们得先搞清楚：为什么要花时间拆解这种代码？

  1. ** 调试像 “拆盲盒”  ** 假设这段代码里  ` n  ` 的值不对，你想打断点看是哪一步赋值出了问题 —— 但三元表达式是 “一行执行”，你根本没法定位到是  ` 3 == a  ` 分支，还是  ` 1 == a  ` 分支导致的问题，只能靠 “注释大法” 逐段排查。

  2. ** 修改容易 “牵一发而动全身”  ** 要是想在  ` 3 == a  ` 的分支里加一句  ` console.log(Dn)  ` 调试，得先在一堆括号里找到正确的位置，稍不注意漏个逗号或括号，整个表达式就报错了。

而拆解成 if-else 后，这些问题会迎刃而解：每个分支独立、每个操作单行、断点想加就加。

###  工具核心逻辑：用 Babel 拆解三元的 3 步走

我们要实现的工具，核心是 “识别三元表达式 → 拆解分支逻辑 → 生成 if-else 节点”。下面结合核心代码，一步步看它是怎么工作的。

####  第一步：准备 “基础工具”—— 生成标准 if-else 节点

首先得有个函数，能把任意分支逻辑包装成带大括号的标准 if-else 节点，避免拆完后格式混乱：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    const types = require("@babel/types");/** * 创建标准 if-else 节点（确保分支是块级语句） * @param {Object} test 条件表达式（如 3 == a） * @param {Object} consequent 真分支逻辑 * @param {Object} alternate 假分支逻辑 * @returns {Object} if-else 节点 */function createIfStatement(test, consequent, alternate) {  // 不管传入的分支是不是块级语句，统一转成带大括号的形式  const consequentBlock = types.isBlockStatement(consequent)     ? consequent     : types.blockStatement([consequent]);
      const alternateBlock = types.isBlockStatement(alternate)     ? alternate     : types.blockStatement([alternate]);
      return types.ifStatement(test, consequentBlock, alternateBlock);}

比如你传入一个单行赋值  ` n = 48  ` ，它会自动转成  ` { n = 48; }  ` ，保证格式统一。

####  第二步：识别目标 —— 找到要拆解的三元表达式

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

####  第三步：处理特殊情况 —— 逗号表达式拆分行

示例中每个分支里有很多用逗号分隔的操作（如  ` li.push(...), Xi = li, li = []  ` ），这种叫
“逗号表达式”，需要拆成独立语句。

上面的  ` handleNestedConditional  ` 函数里已经处理了这种情况：通过  `
types.isSequenceExpression(node)  ` 识别逗号表达式，然后用  ` map  ` 把每个操作转成独立的表达式语句（如  `
li.push(...)  ` 转成  ` li.push(...);  ` ）。

###  拆解效果：从 “天书” 到 “说明书”

把我们的工具作用于开头的复杂三元表达式，最终会生成这样的代码：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    void (function () {  if (3 == a) {    // 原 3 == a 为真的分支    li.push(_i.alert, _i[vi], Yi, Dn, ev, un, _i[Bv], Cv, _i[Wn]);    Xi = li;    li = [];    Dn = "Sc";    Dn += "ree";    (Yi = []).push(_i[Dn += "n"], ai);    Dn = Yi;    Yi = [];    n = 48;  } else {    if (a < 3) {      if (1 == a) {        Av = Yi[Cv];        // 原 Av ? 41 : 51 拆成 if-else        if (Av) {          n = 41;        } else {          n = 51;        }      } else {        if (a < 1) {          li++;          n = 33;        } else {          Cv++;          n = 36;        }      }    } else {      if (5 == a) {        mr = gr <= hr;        kv = 0 !== $.length;        hr = mr * mr;        Cr = hr > -126;        // 原 Cr ? 49 : 1 拆成 if-else        if (Cr) {          n = 49;        } else {          n = 1;        }      } else {        if (a < 5) {          Yi = Xi.join(Zk);          si = Xi = li = Yi;          n = 9;        } else {          ev = "MouseEvent";          un = "x";          Yi.push(_i[ev], un);          un = Yi;          Yi = [];          Cv = (Cv = "Xtnemevom").split("").reverse().join("");          Yi.push(_i[ev], Cv);          ev = Yi;          Yi = [];          n = 17;        }      }    }  }})();break;

可以看到通过上面的代码可以直接把阅读性极为复杂的三目表达式直接转换成更容易读懂的if-else语句，当然
这并不是我们搞定某宝的终点，借用一下举个例子，也是想让大家了解ast语法树对于处理多层三目表达式的优势。

之后我们继续研究ast语法树的其他能力，如果对于ast语法树有什么疑问的  欢迎在评论区留言探讨。

###  码字不易，如果真的有帮助可以顺手点个赞，你们的喜欢就是我更新的动力！

## 第六篇：AST 语法树硬刚某宝：提取控制器

来源：微信公众号：反爬破解社 · 原始发布时间：2026-01-22 · 归档日期：2026-07-13

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

###  码字不易，如果真的有帮助可以顺手点个赞，你们的喜欢就是我更新的动力！


内容含AI生成图片

## 第七篇：AST 语法树硬刚某宝：无用分支破解思路

来源：微信公众号：反爬破解社 · 原始发布时间：2026-01-29 · 归档日期：2026-07-13

应大家的要求，今天先分享一下某宝无用分支的破解思路。
某宝的多层控制流平坦化也是国内数一数二知名的反爬手段了。之前140版本的时候哲哥大神写过一套ast源码，可以完美解决多层控制流平坦化，可以一键还原代码，还原成顺序执行的逻辑，加强阅读性。

但所有上有政策，下有对策，爬虫跟反爬一直在互相斗争。后续加密措施中就加上了无用分支来针对这套源码。
要想解决无用分支，就要先了解无用分支，某宝的无用分支到底是啥，就是在多层控制流平坦化中，加上了不会执行的一些逻辑。就如下：

  *   *   *   *   *   *   *   *   *


    hr = yr + hr;yr = mr * mr;hr *= yr += gr = or * or;ur = (yr = Cr * mr) + (gr = ur * or);if (or = hr >= (ur *= ur)) {l = 7087104;} else {l = 1180160;}

为什么说上面的代码是无用分支呢，就是因为  这段代码的结果同样固定，和所有变量初始值无关，最终 l 必然被赋值为 7087104
而整个加密逻辑里面增加了很多这种无用代码，这种无用代码，在代码执行的时候没有任何影响，因为不会执行，但对于我们用ast去还原混淆代码的时候就会发现因为无用分支的原因，我们在用控制器分析执行逻辑的时候会陷入死循环中。
所以，如果要用ast去还原执行逻辑，那我们就得先剪除无用分支。那我们就得分析特征，因为要在各个地方插入大量的无用分支，所以为了不影响到代码的整体逻辑，我猜弄加密的人，一定会用固定的参数去负责无用分支的判断，毕竟那么多无用分支，要是用运算逻辑的参数，那很容易出现问题。所以依照这个思想去全局判断一下，发现所有相关参数都是无用分支。那既然有这个特征我们就更容易操作了。只要依照变量名称筛选出所有有关这些变量的if语句就可以找到所有无用分支了。

在223的时候，混淆的无用分支做的还不够完美，当时所有无用分支执行的都是if语句的同一分支，但迭代到现在，可以发现现在分支可能走if 也可能走else。

  *   *   *   *   *   *   *   *


    yr = ur ^ ur;gr = !mr;gr |= 447;if (ur = (yr *= yr) > (gr <<= 24)) {l = 6885632;} else {l = 1514496;}

像上面的代码，我们逐句分析一下：

那我们就可以直接把上面的if语句直接全部替换成：

  *


    l = 1514496;

这样就减去了无用分支，避免了我们之后使用控制器整理执行逻辑的时候走入无用分支，造成死循环。
爬虫跟反爬，一直都是在互相成就，今天破解这个加密手法，明天又会研究出新的加密措施，没有可以永远一劳永逸的办法。所以加强自身的基础才是硬道理。
码字不易，如果真的有帮助可以顺手点个赞，你们的喜欢就是我更新的动力！
任何读者依据本公众号内容进行的技术实践（包括但不限于代码部署、系统配置、工具使用、项目开发等），所产生的一切风险（如数据丢失、系统故障、业务中断、版权纠纷、经济损失等）均由读者自行承担。本公众号及作者不对因使用内容而导致的任何直接或间接损失承担责任。
