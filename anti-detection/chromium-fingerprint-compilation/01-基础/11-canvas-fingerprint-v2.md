指纹浏览器开发-修改canvas指纹(二)
---------------------

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

> 注意：由于browserscan会同一时间点生成2次canvas指纹，进行对比，纯随机的话会无法绕过反修改指纹检测。  
> 所以这里巧妙的运用了rand()，同一时间点生成的随机数是相同的，完美绕过。

###### 4.编译

```
ninja  -C  out/Default chrome
```

#### 五、绕过creepjs的反修改指纹检测

*   编译后发现，creepjs检测到了我们修过指纹  
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
