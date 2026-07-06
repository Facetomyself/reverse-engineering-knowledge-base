### 一、什么是字体指纹

*   Font fingerprinting，即字体指纹技术，是一种在线跟踪用户行为的方法。
*   当你访问一个网页时，网站可能会使用JavaScript程序来检查你的系统中安装了哪些字体。
*   由于每个人安装的字体可能因操作系统的不同、个人喜好或工作需要而有所差异，因此通过收集的字体列表数据可以生成一个相对独特的"指纹"。

### 二、如何获取字体指纹

*   有攻才有防，先看看网站是如何通过js获取你的fonts指纹的。
*   将下面的代码复制到F12控制台，就可以获取显示你的fonts指纹了

```js
var baseFonts = ['monospace', 'sans-serif', 'serif'];
var testString = "mmmmmmmmmmlli";
var testSize = '72px';

var h = document.getElementsByTagName('body')[0];

// 创建一个span元素用于测试字体
var s = document.createElement('span');
s.style.fontSize = testSize;
s.innerHTML = testString;
var defaultWidth = {};
var defaultHeight = {};

// 获取并记录基准字体的宽度和高度
for (var index in baseFonts) {
    // 设置基准字体样式
    s.style.fontFamily = baseFonts[index];
    h.appendChild(s);
    defaultWidth[baseFonts[index]] = s.offsetWidth;
    defaultHeight[baseFonts[index]] = s.offsetHeight;
    h.removeChild(s);
}

function detectFont(font) {
    var detected = false;
    for (var i = 0; i < baseFonts.length; i++) {
        s.style.fontFamily = font + ',' + baseFonts[i]; // 以逗号分隔添加潜在字体和基准字体
        h.appendChild(s);
        var matched = (s.offsetWidth != defaultWidth[baseFonts[i]] || s.offsetHeight != defaultHeight[baseFonts[i]]);
        h.removeChild(s);
        detected = detected || matched;
    }
    return detected;
}

async function sha256(message) {
    // 把字符串转换为Uint8Array
    const msgBuffer = new TextEncoder().encode(message);
    // 计算散列值
    const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
    // 转换为数组
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    // 转换为16进制字符串
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return hashHex;
}

var fonts = ["Andale Mono", "Arial", "Arial Black", "Arial Hebrew", "Arial MT", "Arial Narrow", "Arial Rounded MT Bold", "Arial Unicode MS", "Bitstream Vera Sans Mono", "Book Antiqua", "Bookman Old Style", "Calibri", "Cambria", "Cambria Math", "Century", "Century Gothic", "Century Schoolbook", "Comic Sans", "Comic Sans MS", "Consolas", "Courier", "Courier New", "Garamond", "Geneva", "Georgia", "Helvetica", "Helvetica Neue", "Impact", "Lucida Bright", "Lucida Calligraphy", "Lucida Console", "Lucida Fax", "LUCIDA GRANDE", "Lucida Handwriting", "Lucida Sans", "Lucida Sans Typewriter", "Lucida Sans Unicode", "Microsoft Sans Serif", "Monaco", "Monotype Corsiva", "MS Gothic", "MS Outlook", "MS PGothic", "MS Reference Sans Serif", "MS Sans Serif", "MS Serif", "MYRIAD", "MYRIAD PRO", "Palatino", "Palatino Linotype", "Segoe Print", "Segoe Script", "Segoe UI", "Segoe UI Light", "Segoe UI Semibold", "Segoe UI Symbol", "Tahoma", "Times", "Times New Roman", "Times New Roman PS", "Trebuchet MS", "Verdana", "Wingdings", "Wingdings 2", "Wingdings 3"]; /* 可继续添加需要探测的字体 */

// 检查并记录检测到的字体
var fontList = {};
for (var i = 0; i < fonts.length; i++) {
    var result = detectFont(fonts[i]);
    fontList[fonts[i]] = result;
}
var sFontList = JSON.stringify(fontList);
// 输出字体指纹结果
console.log('sFontList', sFontList);

sha256(sFontList).then(hash => console.log(hash));

```

*   输出：

```
d3bd8aa98d226562b16984e0d5525047887547379db35f6f7557b4831d212ca5
```

### 三、字体指纹原理

*   写段文字"mmmmmmmmmmlli"，先测量标准字体的宽度，浏览器的标准字体是`['monospace', 'sans-serif', 'serif']`。
*   再依次测量字体列表中的所有字体的宽度，如果系统中没有这个字体，就会默认显示标准字体。
*   所以当前字体的宽度和标准字体宽度相同时，就代表系统中没有当前字体。

> 注意：字体指纹获取的方法实在太多，这里只用到了offsetWidth和offsetHeight。文章结尾时我会再列出一些：

### 四、编译随机fonts指纹

*   我在第一篇文章写了如何编译chromium的大概流程，网上的教程也一抓一大把，假设你已经编译成功了。
*   找到源码 `third_party\blink\renderer\core\html\html_element.cc`

###### 1.头部加上(随便加在一个`#include`后面)

```c++
#include <random>
```

###### 2.找到

```c
int HTMLElement::offsetWidthForBinding() {
  GetDocument().EnsurePaintLocationDataValidForNode(
      this, DocumentUpdateReason::kJavaScript);
  int result = 0;
  if (const auto* layout_object = GetLayoutBoxModelObject()) {
    result = AdjustedOffsetForZoom(layout_object->OffsetWidth());
    RecordScrollbarSizeForStudy(result, /* is_width= */ true,
                                /* is_offset= */ true);
  }
  return result;
}

DISABLE_CFI_PERF
int HTMLElement::offsetHeightForBinding() {
  GetDocument().EnsurePaintLocationDataValidForNode(
      this, DocumentUpdateReason::kJavaScript);
  int result = 0;
  if (const auto* layout_object = GetLayoutBoxModelObject()) {
    result = AdjustedOffsetForZoom(layout_object->OffsetHeight());
    RecordScrollbarSizeForStudy(result, /* is_width= */ false,
                                /* is_offset= */ true);
  }
  return result;
}

```

2.替换掉原有代码

```c
int getRandomIntForFoo2Modern() {
    static std::mt19937 generator(static_cast<unsigned long>(time(NULL))); // 静态以确保只初始化一次
    std::uniform_int_distribution<int> distribution(0, 9);
    int tmp = distribution(generator);
	if (tmp > 0){
		return 0;
	}else{
		return 1;
	}
}

int HTMLElement::offsetWidthForBinding() {
  GetDocument().EnsurePaintLocationDataValidForNode(
      this, DocumentUpdateReason::kJavaScript);
  int result = 0;
  if (const auto* layout_object = GetLayoutBoxModelObject()) {
    result = AdjustedOffsetForZoom(layout_object->OffsetWidth());
    RecordScrollbarSizeForStudy(result, /* is_width= */ true,
                                /* is_offset= */ true);
  }
  result = result + getRandomIntForFoo2Modern();
  return result;
}

DISABLE_CFI_PERF
int HTMLElement::offsetHeightForBinding() {
  GetDocument().EnsurePaintLocationDataValidForNode(
      this, DocumentUpdateReason::kJavaScript);
  int result = 0;
  if (const auto* layout_object = GetLayoutBoxModelObject()) {
    result = AdjustedOffsetForZoom(layout_object->OffsetHeight());
    RecordScrollbarSizeForStudy(result, /* is_width= */ false,
                                /* is_offset= */ true);
  }
  result = result + getRandomIntForFoo2Modern();
  return result;
}

```

> 原理：这里的操作时js每次调用offseWidth和offseHeight时，每次我们都有随机小概率给其结果+1，使网站对字体指纹产生误判。

###### 3.编译

```
ninja  -C  out/Default chrome
```

*   找到`out/Default chrome`下新编译的执行文件`chrome.exe`执行
*   再次看看fonts指纹，是不是每次访问都变成随机了。

### 五、太low了？

> 是的，确实太low了，这种ele.offsetWidth修改只是最简单的fonts指纹检测。  
> 但也能通过许多fonts指纹检测了，如https://browserleaks.com/fonts

> 我再列出一些其他的获取font指纹的方法

*   `ele.getBBox()`
*   `document.fonts.check()`
*   `window.FontFace()`
*   `canvas.measureText()`
*   `window.getComputedStyle()`
*   `style.transformOrigin`
*   `ele.scrollWidth`
*   `ele.scrollHeight`
*   `ele.clientWidth`
*   `ele.clientHeight`
*   `getBoundingClientRect()`
*   …

> 下节讲webRTC。
