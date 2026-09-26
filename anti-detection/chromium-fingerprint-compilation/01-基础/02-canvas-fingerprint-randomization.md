# Chromium 源码随机 Canvas 指纹（一～二）：fillText 偏移与 setFillStyle 颜色微调

## 收录说明

本文由「Chromium 指纹浏览器编译系列」（CSDN：w1101662433 / fivcan）中同一主题的 2 篇合并而成（2026-09-26 整理）：原系列第 2 篇与第 11 篇「（二）」。各节标题为「篇次：原标题」，原文内容与标题层级未改动、未删减；原文链接与发布日期在原归档中未记录。合并前文件：`02-canvas-fingerprint-randomization.md`（保留路径）、`11-canvas-fingerprint-v2.md`（已删除）；系列目录保留原编号，第 11 篇位置改为指向本文。

## 第一篇：通过源码编译随机 Canvas 指纹

来源：CSDN 博客系列（w1101662433 / fivcan）· 原系列第 2 篇 · 原文链接与发布日期未随归档记录

#### 一、什么是canvas指纹

*   Canvas 指纹技术是一种在网站追踪用户行为和识别用户身份的方法。
*   网站可以要求浏览器创建一个隐形的画布，并在这个画布上绘制图形，使用文字或其他视觉元素。
*   绘制出的图像可能在像素级别上有微妙的差异。这些差异可以用来生成一个几乎独一无二的标识符——即所谓的"Canvas 指纹"。

#### 二、获取浏览器的canvas指纹

*   有攻才有防，先看看网站是如何通过js获取你的canvas指纹的。
*   将下面的代码复制到F12控制台，就可以获取显示你的canvas指纹了。

```js
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

function getCanvasFingerprint() {
    var canvas = document.createElement('canvas');
    var ctx = canvas.getContext('2d');
    
    // 绘制一个简单的图形 —— 例如，文本。
    ctx.textBaseline = "top";
    ctx.font = "14px 'Arial'";
    ctx.textBaseline = "alphabetic";
    ctx.fillStyle = "#f60";
    ctx.fillRect(125, 1, 62, 20);
    
    // 设置一些canvas属性用来增加差异性
    ctx.fillStyle = "#069";
    ctx.fillText("Hello World!", 2, 15);
    ctx.fillStyle = "rgba(102, 204, 0, 0.7)";
    ctx.fillText("Hello World!", 4, 17);

    // 绘制更多复杂的东西，比如变换或者路径
    ctx.strokeStyle = "rgba(0,0,0,0.2)";
    ctx.beginPath();
    ctx.lineTo(50, 100);
    ctx.stroke();
    
    // 尝试获取canvas图像数据
    var data = canvas.toDataURL(); // 获取图像的data URL
    
    // 创建一个hash值，比如使用SHA256或其他算法
    return data; // 假设sha256()是你的hash函数
}
sha256(getCanvasFingerprint()).then(hash => console.log(hash));

```

*   输出：

```
62a60d12f6688e2f53425fa4e35d74d2afd61d30e9e1bfe58e47c7abc72bc2d7
```

> 注意：如果网站通过获取了你的canvas指纹，就算退出登录，网站基本也能确定，这个用户就是你了。信息就是这么泄漏的。

#### 三、编译随机canvas指纹

*   [上篇文章](https://blog.csdn.net/w1101662433/article/details/137949705)写了如何编译chromium，假设你已经编译成功了。
    
*   找到源码 `\third_party\blink\renderer\modules\canvas\canvas2d\base_rendering_context_2d.cc`
    

###### 1.头部加上(随便加在一个`#include`后面)

```c
#include <random>
```

###### 2.替换掉原有代码

```c
void BaseRenderingContext2D::fillText(const String& text, double x, double y) {
  DrawTextInternal(text, x, y, CanvasRenderingContext2DState::kFillPaintType);
}

void BaseRenderingContext2D::fillText(const String& text,
                                      double x,
                                      double y,
                                      double max_width) {
  DrawTextInternal(text, x, y, CanvasRenderingContext2DState::kFillPaintType,
                   &max_width);
}

```

###### 替换为

```c
int getRandomIntForFoo4Modern() {
    static std::mt19937 generator(static_cast<unsigned long>(time(NULL))); // 静态以确保只初始化一次
    std::uniform_int_distribution<int> distribution(0, 2);
    return distribution(generator);
}

void BaseRenderingContext2D::fillText(const String& text, double x, double y) {
  x = x + getRandomIntForFoo4Modern();
  y = y + getRandomIntForFoo4Modern();
  DrawTextInternal(text, x, y, CanvasRenderingContext2DState::kFillPaintType);
}

void BaseRenderingContext2D::fillText(const String& text,
                                      double x,
                                      double y,
                                      double max_width) {
  x = x + getRandomIntForFoo4Modern();
  y = y + getRandomIntForFoo4Modern();
  DrawTextInternal(text, x, y, CanvasRenderingContext2DState::kFillPaintType,
                   &max_width);
}
```

> `getRandomIntForFoo4Modern()`函数是在0-2之间取一个随机数  
> 系统每次调用`fillText`时加上随机偏移，偏移不宜太大，会导致图形混乱。

###### 3.编译

```
ninja  -C  out/Default chrome
```

*   找到`out/Default chrome`下新编译的执行文件`chrome.exe`执行
*   再次看看canvas指纹，是不是每次访问都变成随机了。

#### 四、还不够随机?

*   将函数`BaseRenderingContext2D::measureText`替换成下面的代码

```c
TextMetrics* BaseRenderingContext2D::measureText(const String& text) {
  // The style resolution required for fonts is not available in frame-less
  // documents.

  HTMLCanvasElement* canvas = HostAsHTMLCanvasElement();
  if (canvas) {
    if (!canvas->GetDocument().GetFrame()) {
      return MakeGarbageCollected<TextMetrics>();
    }

    canvas->GetDocument().UpdateStyleAndLayoutTreeForElement(
        canvas, DocumentUpdateReason::kCanvas);
  }

  const Font& font = AccessFont(canvas);

  const CanvasRenderingContext2DState& state = GetState();
  TextDirection direction = ToTextDirection(state.GetDirection(), canvas);
  
  //return MakeGarbageCollected<TextMetrics>(
  //   font, direction, state.GetTextBaseline(), state.GetTextAlign(), text);
  
  int tmp = getRandomIntForFoo4Modern();
  String tmp_text;
  if (tmp == 0 && text.length() != 0) {
    tmp_text = text + " ";
  }else{
	tmp_text = text;
  }
  
  return MakeGarbageCollected<TextMetrics>(
      font, direction, state.GetTextBaseline(), state.GetTextAlign(), tmp_text);
}
```

> 上述代码的意思是每次渲染文字时，随机给文字追加一个空字符。  
> 这样每次测量canvas尺寸肯定就是随机啦。

#### 五、在线指纹验证网站：

*   [https://browserleaks.com/canvas](https://browserleaks.com/canvas)
*   [https://abrahamjuliot.github.io/creepjs/](https://abrahamjuliot.github.io/creepjs/)

## 第二篇：指纹浏览器开发：修改 Canvas 指纹（二）

来源：CSDN 博客系列（w1101662433 / fivcan）· 原系列第 11 篇 · 原文链接与发布日期未随归档记录

#### 一、canvas指纹是什么

*   之前介绍过canvas指纹和常见网站绕过canvas指纹，插眼： https://blog.csdn.net/w1101662433/article/details/137959179

#### 二、为啥有的canvas指纹-二期

*   上期我们假定网站获取canvas指纹时会随机填写文字，所以通过修改fillText()函数实现修改指纹。
*   但部分网站通过单纯的色彩来获取指纹，我们就需要再出一期了。
*   还有就是：众所周知，creepjs和browserscan这2个网站对指纹的检测比较严格，随机修改了指纹后，很容易无法通过网站的反指纹修改检测，被识别到指纹被篡改。

#### 三、获取浏览器的canvas指纹(只通过色彩)

*   有攻才有防，先看看网站是如何通过js获取你的canvas指纹的。
*   将下面的代码复制到F12控制台，就可以获取显示你的canvas指纹了。

```js

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

function getCanvasFingerprint() {
    // 创建canvas元素
var canvas = document.createElement('canvas');
var ctx = canvas.getContext('2d');

// 绘制一个简单的矩形
ctx.fillStyle = "#f0f"; // 设置颜色
ctx.fillRect(10, 10, 50, 50);

// 应用渐变
var gradient = ctx.createLinearGradient(0, 0, 100, 100);
gradient.addColorStop(0, 'rgba(255, 0, 0, 0.5)');
gradient.addColorStop(1, 'rgba(0, 255, 0, 0.5)');
ctx.fillStyle = gradient;
ctx.fillRect(10, 70, 50, 50);

// 获取像素数据
var imageData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
return imageData ;
}
sha256(getCanvasFingerprint()).then(hash => console.log(hash));

```

#### 四、修改源码

*   打开源码文件 `\third_party\blink\renderer\modules\canvas\canvas2d\base_rendering_context_2d.cc`

###### 1.头部加上(随便加在一个`#include`后面)

```c
#include <string>
#include <iostream>
#include <cstdlib>
#include <ctime>
```

###### 2.找到下面的代码

```c
void BaseRenderingContext2D::setFillStyle(v8::Isolate* isolate,
                                          v8::Local<v8::Value> value,
                                          ExceptionState& exception_state) {
  V8CanvasStyle v8_style;
  if (!ExtractV8CanvasStyle(isolate, value, v8_style, exception_state))
    return;

  ValidateStateStack();

  UpdateIdentifiabilityStudyBeforeSettingStrokeOrFill(v8_style,
                                                      CanvasOps::kSetFillStyle);

  CanvasRenderingContext2DState& state = GetState();
  switch (v8_style.type) {
    case V8CanvasStyleType::kCSSColorValue:

      state.SetFillColor(v8_style.css_color_value);
      break;
    case V8CanvasStyleType::kGradient:
      state.SetFillGradient(v8_style.gradient);
      break;
    case V8CanvasStyleType::kPattern:
      if (!origin_tainted_by_content_ && !v8_style.pattern->OriginClean())
        SetOriginTaintedByContent();
      state.SetFillPattern(v8_style.pattern);
      break;
    case V8CanvasStyleType::kString: {
      if (v8_style.string == state.UnparsedFillColor()) {
        return;
      }
      Color parsed_color = Color::kTransparent;
      if (!ExtractColorFromV8ValueAndUpdateCache(v8_style, parsed_color)) {
        return;
      }
      if (state.FillStyle().IsEquivalentColor(parsed_color)) {
        state.SetUnparsedFillColor(v8_style.string);
        return;
      }
      state.SetFillColor(parsed_color);
      break;
    }
  }

  state.SetUnparsedFillColor(v8_style.string);
  state.ClearResolvedFilter();
}
```

> 注意：最新源码可能和当前代码有略微差异，但基本逻辑是一样。通过改变canvas颜色来改变指纹。

###### 3.替换为

```c
void BaseRenderingContext2D::setFillStyle(v8::Isolate* isolate,
                                          v8::Local<v8::Value> value,
                                          ExceptionState& exception_state) {
  V8CanvasStyle v8_style;
  if (!ExtractV8CanvasStyle(isolate, value, v8_style, exception_state))
    return;

  ValidateStateStack();

  UpdateIdentifiabilityStudyBeforeSettingStrokeOrFill(v8_style,
                                                      CanvasOps::kSetFillStyle);

  CanvasRenderingContext2DState& state = GetState();

  // 这里追加2行，这里可以过creepjs
  srand((int)time(NULL));
  state.SetStrokeColor(Color::FromRGBALegacy(rand() % 5, rand() % 6,rand() % 7, rand() % 255));

  switch (v8_style.type) {
    case V8CanvasStyleType::kCSSColorValue:

      state.SetFillColor(v8_style.css_color_value);
      break;
    case V8CanvasStyleType::kGradient:

      state.SetFillGradient(v8_style.gradient);
      break;
    case V8CanvasStyleType::kPattern:

      if (!origin_tainted_by_content_ && !v8_style.pattern->OriginClean())
        SetOriginTaintedByContent();
      state.SetFillPattern(v8_style.pattern);
      break;
    case V8CanvasStyleType::kString: {
      if (v8_style.string == state.UnparsedFillColor()) {
        return;
      }
      Color parsed_color = Color::kTransparent;
      if (!ExtractColorFromV8ValueAndUpdateCache(v8_style, parsed_color)) {
        return;
      }
      if (state.FillStyle().IsEquivalentColor(parsed_color)) {
        state.SetUnparsedFillColor(v8_style.string);
        return;
      }

		  //这里追加1行，这里用来过browserscan
	      parsed_color = Color::FromRGBALegacy(parsed_color.Param1() + rand() % 5, parsed_color.Param1()+ rand() % 6, parsed_color.Param2() + rand() % 7, parsed_color.Alpha()*255);

		  state.SetFillColor(parsed_color);
      break;
    }
  }

  state.SetUnparsedFillColor(v8_style.string);
  state.ClearResolvedFilter();
}
```

> 注意：由于browserscan会同一时间点生成2次canvas指纹，进行对比，纯随机的话会无法绕过反修改指纹检测。\
> 所以这里巧妙的运用了rand()，同一时间点生成的随机数是相同的，完美绕过。

###### 4.编译

```
ninja  -C  out/Default chrome
```

#### 五、绕过creepjs的反修改指纹检测

*   编译后发现，creepjs检测到了我们修过指纹\
    ![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/ad9047d4f88634988ed5f73cf23edb3d.png)
*   他的检测原理就是生成2张一样的图，然后着帧对比，发现不同，就认为有篡改。

为了绕过他的检测，继续修改源码：

##### 1.找到

```c
ImageData* BaseRenderingContext2D::getImageDataInternal(
    int sx,
    int sy,
    int sw,
    int sh,
    ImageDataSettings* image_data_settings,
    ExceptionState& exception_state) {
```

##### 2.改成：

```c
ImageData* BaseRenderingContext2D::getImageDataInternal(
    int sx,
    int sy,
    int sw,
    int sh,
    ImageDataSettings* image_data_settings,
    ExceptionState& exception_state) {

  // 这里追加一行
  if (sh==1){return nullptr;}
```

> 注意：就是追加了一行代码，由于检测是着帧对比，所以我们让sh==1时，canvas的getImageDate会返回null，完美绕过creepjs的检测。

###### 3.再编译

```
ninja  -C  out/Default chrome
```

#### 六、在线指纹验证网站：

*   https://abrahamjuliot.github.io/creepjs/
*   https://www.browserscan.net/
