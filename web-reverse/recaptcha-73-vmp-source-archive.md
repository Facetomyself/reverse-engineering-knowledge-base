---
schema_version: 2
id: web-reverse-recaptcha-73-vmp-source-archive
document_type: archive
original_date: unknown
archived_date: "2026-10-13"
scope:
  targets: [recaptcha-73]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "https://mp.weixin.qq.com/s/SckvWTplUI9B3gQEqvGGaA"
    basis: source-report
source_completeness: partial
tags: [recaptcha-73, VMP, gpu-fingerprint, time-seed, source-report]
---

# reCAPTCHA 73 算法（来源节选）

## 清洗与完整性说明

原文件无 H1；此标题按审阅后的文件名 `recaptcha 73 算法.md` 与正文主题补入。pending 导出中的 11 张图片均为 1×1 占位图，没有对应原图；文中 `encrypt73_slot` / `parse_vmp_key` 只有函数声明，没有函数体，作者提及的反编译文件也未随输入提供。来源里的 WebGL vendor / renderer / 扩展数量样值已脱敏，未补写缺失算法，所以标记 `partial`。

<a id="source-body"></a>
## 来源正文

recaptcha里有个vmp，搞过的兄弟应该都知道，里面的算法其实非常简单，但通过插桩分析总感觉不太放心，所以通过对其进行了反编译。

先将结果放置在下面

看不懂没关系，分析过程也都在下面

* * *

```
function encrypt73_slot(plaint, slot_salt, vmp_key, timeSeed) {
```

```
function parse_vmp_key(resp) {
```

  

  

* * *

下面开始分析算法，很简单大家不用担心看不懂，想要反编译的文件，可以先滑动到最下面下载。

[图片缺失：pending 导出中仅有 1×1 占位图，没有原图附件。]

首先，我将会写入到73地方的数组，用write\_73赋值，大家可以通过搜索write\_73快速定位到，但有些不会被写入73数组，有些会被写入到73数组里。

[图片缺失：pending 导出中仅有 1×1 占位图，没有原图附件。]

  

其中会有个显卡型号写入到73数组中，因此我们通过分析这块就足够分析算法了。

* * *

[图片缺失：pending 导出中仅有 1×1 占位图，没有原图附件。]

  

可以看到myvar\_1774的生成，就在上面，所以我们去分析myvar\_1774怎么生成的就可以了。

[图片缺失：pending 导出中仅有 1×1 占位图，没有原图附件。]

可以看到myvar\_1774初始化为一个空数组，然后将myvar\_1767这个字符串，不断将charCode写入到myvar\_1774

[图片缺失：pending 导出中仅有 1×1 占位图，没有原图附件。]

而myvar\_1767是JSON.stringify数组myvar\_1766

myvar\_1766由三个元素组成：

*   myvar\_1761是显卡的厂商vendor
    
*   myvar\_1764是显卡具体型号renderer
    
*   myvar\_1754是获取getSupportedExrensions的length
    

  

来源把 `myvar_1767` 描述为由 WebGL vendor、renderer 与支持扩展数量组成的 JSON 数组；该行的设备样值已脱敏。

* * *

  

[图片缺失：pending 导出中仅有 1×1 占位图，没有原图附件。]

下面再看myvar\_1774这个数组怎么变换的。

将字符串的所有charCode先写入到myvar\_1774，然后再while循环中，这里会有变换，我这里一直都是myvar\_1774\[0\]其实是有问题的，实际应该是myvar\_1774\[myvar\_1786\]才对，这里就是反编译的时候存在的一些小问题，不影响咱们分析。

相当于是

```
myvar_1774[0] = (myvar_1774[0] + myvar_1782) % 256;
```

所以可以看出，只需要分析出myvar\_1782怎么来的就行了。

  

[图片缺失：pending 导出中仅有 1×1 占位图，没有原图附件。]

这里可以看出myvar\_1782最终追溯到myvar\_1773，换句话说就是，myvar\_1773生成初始化的值，然后再while循环里又不断迭代变换。

所以我们只需要分析出myvar\_1773怎么来的就可以了。

  

[图片缺失：pending 导出中仅有 1×1 占位图，没有原图附件。]

  

myvar\_1773可以看到是由myvar\_558和myvar\_1771生成。

```
var myvar_553 = Math["trunc"](performance["now"]());
```

```
var myvar_1768 = Math["trunc"](performance["now"]());
```

当我把myvar\_558和myvar\_1771单独拿出来，大家看着应该就很清晰了。

其实myvar\_558可以化简成：

```
var myvar_558 = -36990277 ^ 1310 ^ (Math["trunc"](performance["now"]()) + 939) * 2654435761 ^ 0;
```

myvar\_1771可以化简为：

```
var myvar_1771 = (Math["trunc"](performance["now"]()) + 632) * 2654435761 ^ 0;
```

  

* * *

  

到这里大家可能基本都能看出来一些东西了，那让我们再次化简一下，

```
var myvar_1773 = myvar_558 ^ myvar_1771
```

这个时候我们给他们起个名字

\-36990277这个值，是需要从anchor里解析出来的，每次都会变

1310这个值，每个槽位不同，但是固定的。

后面两次performance\["now"\]获取的值 我们就可以叫做time\_seed

  

* * *

  

到这里再重新看文章最上面贴出来的函数，应该就能看懂了

  

[图片缺失：pending 导出中仅有 1×1 占位图，没有原图附件。]

  

到这其实就差不多了。填充到最后，会把time\_seed，写入到加密数组的最后四位，这样服务端就可以借此对结果进行反解，来验证是否正确。

[图片缺失：pending 导出中仅有 1×1 占位图，没有原图附件。]

  

[图片缺失：pending 导出中仅有 1×1 占位图，没有原图附件。]

可以看到每个槽位对应的这个slot\_salt值 是固定不变的。

  

* * *

  

至于parse\_vmp\_key这个函数，是我让ai蹬的一个，就是为了解析出我前面提到的“\-36990277这个值，是需要从anchor里解析出来的，每次都会变”，就是为了解析出这个值。

* * *

  

  

我反编译的代码也不是很完美，但是能看清算法了，想看看反编译后啥样的兄弟，公众号私信发 recaptcha73

  

希望有哥哥能带我无敌recaptcha大并发，或者有推荐的IP也可以发我，听说recaptcha很吃IP。

本文转自 <https://mp.weixin.qq.com/s/SckvWTplUI9B3gQEqvGGaA>，如有侵权，请联系删除。

## 复用边界

本文只保留 pending 中实际可见的来源文字、声明和缺口。对“73”槽位的来源描述仍为 `source-report`；本轮没有目标脚本、VMP 函数体或输入输出夹具，不声称算法完整恢复，也不将其等同于 Google reCAPTCHA v3 请求链。
