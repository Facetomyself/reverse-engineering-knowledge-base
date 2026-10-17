---
schema_version: 2
id: shumei-js-format-detection
document_type: archive
original_date: unknown
archived_date: "2026-10-08"
scope:
  targets: [shumei-captcha]
  client: web
  version: "captcha-sdk v1.0.4-208"
  observed_at: unknown
sources:
  - id: s1
    ref: null
    basis: source-report
    citation: "数美 JS 格式化检测；文件 castatic.fengkongcloud.cn/pr/auto-build/v1.0.4-208/captcha-sdk.min.js"
    reason: "原始材料未提供作者名或可公开定位的链接"

source_completeness: complete
relations: []
tags: [shumei, isJsFormat, risk-control]
---

# 数美 JS 格式化检测

来源点名 `captcha-sdk.min.js` 的 `v1.0.4-208`，没有作者和公开文章链接。正文把行数检测和后续 DES 密钥选择写成同一段来源观察。

## 清洗与完整性说明

无图、无表。函数片段、行号和 visitor 按原文保留。原文没有密钥字节，归档也不补。

<a id="source-body"></a>
## 来源正文

文件:`castatic.fengkongcloud.cn/pr/auto-build/v1.0.4-208/captcha-sdk.min.js`


数美在 SDK 里放了个方法叫 `isJsFormat`,用来判断这份 JS 有没有被格式化过。

判断方式很简单:**数一个函数源码有几行**。

代码

先在某处定义一个没用的函数,专门用来当诱饵(3.js 第 9841 行):

```js
_0x1daaf1 = function _0x2f72bf() {
    return console["log"]("1"), "a";
};
```

然后数它的行数(3.js 第 10547 行):

```js
"isJsFormat": function () {
    return _0x1daaf1["toString"]().split("\n").length > 2;
}
```

`toString()` 拿到的是这个函数的源代码文本,`split("\n")` 按换行切开,数有几段。


线上的 `captcha-sdk.min.js` 是**压缩过的,整个文件就一行**。

所以 `_0x1daaf1.toString()` 拿到的是:

```
function _0x2f72bf(){return console["log"]("1"),"a"}
```

一行,`split("\n").length` 等于 **1**,不大于 2,检测通过。

而你格式化之后,这个函数变成:

```
function _0x2f72bf() {
    return console["log"]("1"), "a";
}
```

三行,`length` 等于 **3**,大于 2 → **被发现了**。

注意:只要格式化过就会中招,跟你有没有反混淆、改没改代码**完全无关**。拿原始文件格式化一下再替换,照样中招。



它只是把加密用的 DES 密钥悄悄换成另一个(3.js 第 5595 行附近):

```js
var _0x20e86f = _0x3c8070 || _0x52c8e;        // 正常密钥
isJsFormat() && (_0x20e86f = _0x5cb6a7);      // 中招了就换成这个
_0x507e37 = DES(_0x20e86f, _0x38ce5b, 1, 0);  // 拿它去加密
```



因为前端用错误的密钥加密,服务端解不开,直接判失败。所有异常都推迟到服务端,前端查不出任何线索。

解决

让 `isJsFormat` 永远返回 false 就行。在 AST 流程里加一步:

```js
// 干掉格式化检测
function sm_killcheck(path) {
    let key = path.node.key.type === "StringLiteral"
            ? path.node.key.value : path.node.key.name
    if (key !== "isJsFormat") return;
    if (!path.node.value) return;
    if (path.node.value.type !== "FunctionExpression") return;
    // 函数体整个换成 return false
    path.node.value.body = types.blockStatement([
        types.returnStatement(types.booleanLiteral(false))
    ])
}

traverse(ast, {ObjectProperty: sm_killcheck});
```

跑完检查一下,应该变成这样:

```js
"isJsFormat": function _0x19a9d2() { return false; }
```

## 复用边界

与 Android `deviceprofile/v4` 不是同一条材料。`isJsFormat` 命中后换的是 encryption 用的 DES 密钥，不是 signature、encoding 或 fingerprint 字段。本轮没有加载该 SDK。
