---
schema_version: 2
id: web-reverse-acw-sc-v2-source-archive
document_type: archive
original_date: "2025-09-26"
archived_date: "2026-10-13"
scope:
  targets: [acw-sc-v2]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "https://mp.weixin.qq.com/s/P0x9xe9r6ruAlB1UwSFJqg"
    basis: source-report
source_completeness: partial
relations: []
tags: [acw-sc-v2, babel-ast, binding, deobfuscation, source-report]
---

# Python 爬虫进阶：acw_sc_v2 加密 AST 解混淆全流程（来源归档）

## 清洗与完整性说明

原文件没有 H1；归档标题按已审输入文件名补入。正文声明日期为 2025-09-26，但没有完整复现代码；导出中有 9 个 1×1 SVG 占位图而无独立图片附件。以 Base64 表示的目标网址不解码、不复制，替换为脱敏标记。保留原始可见文字与代码片段，不补齐缺失 decoder、浏览器解密数组或 AST 转换器。 来源可定位到 metadata 中的原文链接；链接只按来源材料记录，本轮未访问原站。该 `archive` 只归档 pending 可见内容，`source_completeness: partial` 不替代原文以外的图片、附件或原始 runtime 证据。

<a id="source-body"></a>
## 来源正文

#### 声明

###### 本文写于2025年9月26日,仅做技术学习交流。本文章中所有内容仅供学习交流使用，不用于其他任何目的，不提供完整代码，抓包内容、敏感网址、数据接口等均已做脱敏处理，严禁用于商业用途和非法用途，否则由此产生的一切后果均与作者无关！

#### 一、前言

听说v2出新版了。刚好面了个公司用v2站做的测试，那么我们就看下新版的全流程。

网站：

`[目标 URL 已脱敏；原文为 Base64 编码]`

这网站有v2和v3,v2一个代理能采5页就会出v3。

我们本次先看v2。

#### 二、代码流程解析

我们打`cookie`断点就可以看到从如下函数

```
dv()[W4(nj.xc)+'d'](k6);
```

进入了`VM`代码，里面的vm代码就是我们生成cookie的地方。通过代码可以看到是一个ob混淆。

其中如下就是生成cookie的核心代码

```
var b = t[yX(oK.C)](I,JSON[yX(oK.H)](K)),P=(Math[yX(oK.N)]= t[yX(oK.R)](C, b),T[yX(oK.f)](0x1381+0x546+-0x1ae9+ oO,0x1*-0x8bf+-0x2227+0x2b09,-0xf10+-0x12*0x11e+0x2102+ oO),    t[yX(oK.I)](j,T)[yX(oK.j)]('')), b = k['e'],T=[t[yX(oK.A)](void(0x11ef*-0x2+-0x10d*-0xe+0x1528), b[yX(oK.n)]), t[yX(oK.Y)](void(0x1b9e+-0x1e22+-0x7*-0x5c), b[yX(oK.n)])&& b[yX(oK.n)][yX(oK.T)], t[yX(oK.z)](b, b[yX(oK.F)]),!(-0x5*-0x573+-0x36b*-0x1+-0x20fc+ oO),!(-0x1276+-0x1a25*-0x1+-0xa00+ oO)];    k['e'][yX(oK.w)][yX(oK.b)]= x,O? k['e'][yX(oK.P)][yX(oK.s)][yX(oK.a)]=O:delete k['e'][yX(oK.i)][yX(oK.s)][yX(oK.c)],JSON[yX(oK.k)]=B;for(var q,G,L=0x191*-0x17+0x17f1*-0x1+-0x65*-0x98; t[yX(oK.r)](L,T[yX(oK.x)]);++L)P+=(q =T[L],G=void(-0x2f9*0xd+-0x1881+0x89*0x76),G=Math[yX(oK.q)](t[yX(oK.G)](0x3d*0x85+-0x611+-0x192*0x10,Math[yX(oK.L)]())),(q && t[yX(oK.v)](t[yX(oK.U)](G,0x1*-0xe60+0x5*-0xce+-0x26*-0x7c),0x2b*-0xe3+0x1*-0x1b24+-0x1f*-0x21b)||!q && t[yX(oK.E)](t[yX(oK.g)](G,0x1581+0x1dd+-0x1a*0xe6),-0xb3*0xb+0xc5a+-0x1*0x4a9))&&G++,        q = t[yX(oK.V)](-0x1a1*0x17+-0x6*0x32a+0x3622+ oO,(q =G[yX(oK.K)](-0xc81+-0x253f+0x2f7e+ oO))[yX(oK.x)])? t[yX(oK.J)]('0', q): q);P= t[yX(oK.D)](t[yX(oK.l)](this['h'](),'-'),P[yX(oK.d)+'e']())
```

可以看到是严重的混淆，那么我们就先解混淆，再看代码。

#### 三、AST解析

我们可以看到最里面的是oK.q这样的代码，我们直接搜下，可以看到是如下形式

[图片缺失：pending 导出中仅保留 1×1 SVG 占位图，本批无原图附件。]

  

ob混淆

那么就很明了了

我们先还原进制符

可以看到是`ObjectProperty`类型

[图片缺失：pending 导出中仅保留 1×1 SVG 占位图，本批无原图附件。]

  

ObjectProperty

我们就先直接判断，然后在把参数写道一个对象里面

```
types.isObjectExpression(path.node.init)
```

接下来就是查找绑定，然后取出对象里面响应的值即可。

[图片缺失：pending 导出中仅保留 1×1 SVG 占位图，本批无原图附件。]

  

数字还原

我们可以看到数字此时就还原成功了

接下我们再看第二层，可以看到调用逻辑如下

```
y3 = myX = y3yX(573)
```

其中的m就是我们的解密函数，那就就很清楚。直接跟之前的AST思路一样。

多层查找绑定，然后调用m出值即可。这个解密要说明的是，他的解密字符我们需要到浏览器拿才行，当浏览器的解密值出来后生成的大字符数组才是我们需要的。

我们先复制浏览器的解密数组测试后，在写到我们的还原函数中，可以看到经过测试一摸一样

[图片缺失：pending 导出中仅保留 1×1 SVG 占位图，本批无原图附件。]

  

解密数组测试

有了完整的数组，我们就可以写还原代码了，类代码如下

```
traverse(ast,{VariableDeclarator(path){if(types.isIdentifier(path.node.init)){if(path.node.init.name==='m'){let bd=path.scope.getBinding(path.node.id.name);let repath=bd &&bd.referencePathsfor(let i =0; i < repath.length; i++){let rep = repath[i].parentPathif(types.isCallExpression(rep)){                        argsm=m.call(null,rep.node.arguments[0].value)                        rep.replaceWith(types.valueToNode(argsm));}
```

可以看到此时字符也还原了

[图片缺失：pending 导出中仅保留 1×1 SVG 占位图，本批无原图附件。]

  

字符还原

接下来就是如下代码

```
t["CUMDW"](void0, b["navigator"])
```

我们点击t跳转过去可以看到t是个对象，里面有函数和字符串

[图片缺失：pending 导出中仅保留 1×1 SVG 占位图，本批无原图附件。]

  

t对象

具体的大家看我之前一篇文章，因为一摸一样，此处就不重复讲了

[某招投标服务平台AST详解](https://mp.weixin.qq.com/s?__biz=MzI1MjE1NjIyMw==&mid=2650861960&idx=1&sn=33bffa75c8efae9f0070a79c28206091&scene=21#wechat_redirect)

可以看到还原后的代码已经很清晰了

[图片缺失：pending 导出中仅保留 1×1 SVG 占位图，本批无原图附件。]

  

还原后的代码

我们直接把P的代码，复制下来，纯算或者调用皆可。此处我就直接调用js了。

[图片缺失：pending 导出中仅保留 1×1 SVG 占位图，本批无原图附件。]

  

列表以及详情页

可以看到列表以及详情页都可以正常获取

  

[图片缺失：pending 导出中仅保留 1×1 SVG 占位图，本批无原图附件。]

页数

至此我们的v2已经全部解决。但是基本上获取5页左右就会出v3。如果不怕浪费IP的话，45页换个IP也可以一直获取。

v3的话我们下期在讲

###### 本文章未经许可禁止转载，禁止任何修改后二次传播，擅自使用本文讲解的技术而导致的任何意外，作者均不负责，若有侵权，请在公众号联系作者立即删除！

本文转自 <https://mp.weixin.qq.com/s/P0x9xe9r6ruAlB1UwSFJqg>，如有侵权，请联系删除。

## 复用边界

来源中的分析过程、代码片段、样值和成功 / 失败结果均为作者自述，依据统一标记为 `source-report`。本轮只做文字清洗和脱敏；未运行目标代码、未请求目标服务、未复现来源结果，也不把来源结论升级为 `runtime-observation`、`local-parity` 或 `server-accepted`。
