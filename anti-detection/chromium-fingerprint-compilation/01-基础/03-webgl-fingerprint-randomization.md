# Chromium 源码随机 WebGL 指纹（一～二）：getSupportedExtensions 打乱与 ReadPixelsHelper / toDataURL

## 收录说明

本文由「Chromium 指纹浏览器编译系列」（CSDN：w1101662433 / fivcan）中同一主题的 2 篇合并而成（2026-09-26 整理）：原系列第 3 篇与第 13 篇「（二）」。各节标题为「篇次：原标题」，原文内容与标题层级未改动、未删减；原文链接与发布日期在原归档中未记录。合并前文件：`03-webgl-fingerprint-randomization.md`（保留路径）、`13-webgl-fingerprint-v2.md`（已删除）；系列目录保留原编号，第 13 篇位置改为指向本文。

## 第一篇：修改 Chromium 源码随机 WebGL 指纹

来源：CSDN 博客系列（w1101662433 / fivcan）· 原系列第 3 篇 · 原文链接与发布日期未随归档记录

#### 一、WebGL指纹是什么

*   WebGL：全称为Web Graphics Library，是一个JavaScript API，无需使用任何额外插件，就可以在网页浏览器中渲染高性能的2D和3D图像。
*   WebGL指纹：WebGL指纹是基于网页浏览器中的WebGL API生成的唯一标识符。它利用了图形处理单元（GPU）不同程度的差异来创建一个可以用来跟踪用户的设备指纹。由于不同设备的GPU有细微的差异，例如渲染能力、性能等，WebGL指纹可以作为区分用户设备的一种手段。

#### 二、获取浏览器的WebGL指纹

*   有攻才有防，先看看网站是如何通过js获取你的WebGL指纹的。
*   将下面的代码复制到F12控制台，就可以获取显示你的WebGL指纹了

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

function getWebGLFingerprint() {
    // 尝试创建一个canvas元素并获取WebGL渲染上下文
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

    if (!gl) { // 如果无法获取到WebGL上下文，则无法生成指纹
        return null;
    }

    // 创建一个可以用来生成指纹的函数
    const getGlParam = function(parameter) {
        // WebGL参数值可以通过调用gl.getParameter()获取
        const value = gl.getParameter(parameter);
        return value ? value.toString() : 'null';
    };

    // 收集一系列WebGL参数的值
    const webglParams = [
        // 表示GPU驱动和硬件的字符串
        gl.VENDOR,
        gl.RENDERER,
        // WebGL版本字符串
        gl.VERSION,
        // 支持的WebGL扩展列表
        gl.getSupportedExtensions(),
        // 其他一些可能影响指纹的特性
        gl.MAX_TEXTURE_SIZE,
        gl.MAX_RENDERBUFFER_SIZE,
        // ...可以根据需要获取更多的参数
    ];

    // 遍历并收集参数值
    const glValues = webglParams.map(param => {
        if (Array.isArray(param)) {
            return param.join('-');
        }
        return getGlParam(param);
    });

    // 拼接得到的参数值作为一个长字符串，这就是我们的WebGL指纹
    const webglFingerprint = glValues.join('_');

    return webglFingerprint;
}

sha256(getWebGLFingerprint()).then(hash => console.log(hash));

```

*   输出：

```
dfe89f41416faecf0ab4be2ddeccdc79999aafd3577a0e14e9b3e5265e72d6e7
```

#### 三、编译随机webGL指纹

*   [第一篇文章](https://blog.csdn.net/w1101662433/article/details/137949705)写了如何编译chromium，假设你已经编译成功了。
*   找到源码 `third_party/blink/renderer/modules/webgl/webgl_rendering_context_base.cc`

###### 1.头部加上(随便加在一个`#include`后面)

```c
#include <algorithm> // std::shuffle
#include <random>    // std::default_random_engine
#include <chrono>    // std::chrono::system_clock
```

###### 2.替换掉原有代码

```c
std::optional<Vector<String>>
WebGLRenderingContextBase::getSupportedExtensions() {
  if (isContextLost())
    return std::nullopt;

  Vector<String> result;

  for (ExtensionTracker* tracker : extensions_) {
    if (ExtensionSupportedAndAllowed(tracker)) {
      result.push_back(tracker->ExtensionName());
    }
  }

  return result;
}
```

###### 替换为

```c
std::optional<Vector<String>>
WebGLRenderingContextBase::getSupportedExtensions() {
  if (isContextLost())
    return std::nullopt;

  Vector<String> result;

  for (ExtensionTracker* tracker : extensions_) {
    if (ExtensionSupportedAndAllowed(tracker)) {
      result.push_back(tracker->ExtensionName());
    }
  }

  // 使用当前时间作为随机数生成的种子
  unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
  std::default_random_engine engine(seed);

  // 打乱result中的元素顺序
  std::shuffle(result.begin(), result.end(), engine);
  
  return result;
}
```

> 可以看到，获取webGL指纹的关键函数就是`getSupportedExtensions`,返回当前WebGL上下文对象支持的所有扩展名称的列表。  
> 我们将返回列表打乱随机，js收集的指纹信息hash自然每次都不一样啦。

#### 四、在线指纹验证网站：

*   [https://browserleaks.com/webgl](https://browserleaks.com/webgl)
*   [https://abrahamjuliot.github.io/creepjs/](https://abrahamjuliot.github.io/creepjs/)

## 第二篇：指纹浏览器开发：修改 WebGL 指纹（二）

来源：CSDN 博客系列（w1101662433 / fivcan）· 原系列第 13 篇 · 原文链接与发布日期未随归档记录

#### 一、webGL指纹是什么

*   之前介绍过webGL指纹和常见网站绕过webGL指纹，[插眼传送](https://blog.csdn.net/w1101662433/article/details/137962776)

#### 二、为啥有的webGL指纹-二期

*   上期我们通过修改gl的参数，`getSupportedExtensions()`函数返回值列表的顺序，绕过部分网站的指纹检测。
*   但还有些网站通过webGL生成图形来获取指纹，我们就需要再出一期了。
*   还有就是：上期指纹检测未通过browserscan这个网站。

#### 三、获取浏览器的webGL指纹(通过生成图像)

*   有攻才有防，先看看网站是如何通过js获取你的webGL指纹的。
*   将下面的代码复制到F12控制台，就可以获取显示你的webGL指纹了。

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

function getWebGLFingerprint() {
    var canvas = document.createElement('canvas');
	var gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");

    // 设置清除颜色为黑色，不透明
    gl.clearColor(0.0, 0.0, 0.0, 1.0);
    // 清除颜色缓冲区
    gl.clear(gl.COLOR_BUFFER_BIT);

    // 创建顶点着色器
    var vsSource = `
        attribute vec4 aVertexPosition;
        void main(void) {
          gl_Position = aVertexPosition;
        }
    `;
    var vertexShader = gl.createShader(gl.VERTEX_SHADER);
    gl.shaderSource(vertexShader, vsSource);
    gl.compileShader(vertexShader);

    // 创建片段着色器
    var fsSource = `
        void main(void) {
            gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);
        }
    `;
    var fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
    gl.shaderSource(fragmentShader, fsSource);
    gl.compileShader(fragmentShader);

    // 创建着色器程序
    var shaderProgram = gl.createProgram();
    gl.attachShader(shaderProgram, vertexShader);
    gl.attachShader(shaderProgram, fragmentShader);
    gl.linkProgram(shaderProgram);
    gl.useProgram(shaderProgram);

    // 定义三角形的顶点
    var vertices = new Float32Array([
         0.0,  1.0,  0.0,
        -1.0, -1.0,  0.0,
         1.0, -1.0,  0.0
    ]);

    // 创建顶点缓冲区对象
    var vertexBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);

    // 将缓冲区对象绑定到着色器变量
    var vertexPositionAttribute = gl.getAttribLocation(shaderProgram, "aVertexPosition");
    gl.enableVertexAttribArray(vertexPositionAttribute);
    gl.vertexAttribPointer(vertexPositionAttribute, 3, gl.FLOAT, false, 0, 0);

    // 绘制三角形
    gl.drawArrays(gl.TRIANGLES, 0, 3);

    // 读取渲染结果并生成指纹
    //var pixels = new Uint8Array(gl.drawingBufferWidth * gl.drawingBufferHeight * 4);
    //gl.readPixels(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
    //return pixels;

	var res = canvas.toDataURL()
	return res
}

sha256(getWebGLFingerprint()).then(hash => console.log(hash));

```

> 可以看到：获取图像数据有2种方式，关键函数是`readPixels()`和`toDataURL()`。

#### 四、修改源码的readPixels()函数

*   打开源码文件 `\third_party\blink\renderer\modules\webgl\webgl_rendering_context_base.cc`

###### 1.找到下面的代码

```c
void WebGLRenderingContextBase::ReadPixelsHelper(GLint x,
                                                 GLint y,
                                                 GLsizei width,
                                                 GLsizei height,
                                                 GLenum format,
                                                 GLenum type,
                                                 DOMArrayBufferView* pixels,
                                                 int64_t offset) {
  if (isContextLost())
    return;
```

###### 2.替换为

```c
int getRandomIntForFoo12Modern() {
    static std::mt19937 generator(static_cast<unsigned long>(time(NULL))); // 静态以确保只初始化一次
    std::uniform_int_distribution<int> distribution(0, 9);
    return distribution(generator);
}

void WebGLRenderingContextBase::ReadPixelsHelper(GLint x,
                                                 GLint y,
                                                 GLsizei width,
                                                 GLsizei height,
                                                 GLenum format,
                                                 GLenum type,
                                                 DOMArrayBufferView* pixels,
                                                 int64_t offset) {
  if (isContextLost())
    return;

  //追加2行
  width = width - getRandomIntForFoo12Modern();
  height = height - getRandomIntForFoo12Modern();
```

> 注意：这里我们通过裁剪了部分像素来实现改变`ReadPixelsHelper`方法的返回值

#### 五、修改源码的toDataURL()函数

*   打开源码文件 `\third_party\blink\renderer\core\html\canvas\html_canvas_element.cc`

###### 1.头部加上(随便加在一个`#include`后面)

```c
#include <algorithm>
#include <random>
#include <chrono>
```

###### 2.找到下面的代码

```c

String HTMLCanvasElement::toDataURL(const String& mime_type,
                                    const ScriptValue& quality_argument,
                                    ExceptionState& exception_state) const {
  if (ContextHasOpenLayers(context_)) {
    exception_state.ThrowDOMException(
        DOMExceptionCode::kInvalidStateError,
        "`toDataURL()` cannot be called with open layers.");
    return String();
  }

  if (!OriginClean()) {
    exception_state.ThrowSecurityError("Tainted canvases may not be exported.");
    return String();
  }

  double quality = kUndefinedQualityValue;
  if (!quality_argument.IsEmpty()) {
    v8::Local<v8::Value> v8_value = quality_argument.V8Value();
    if (v8_value->IsNumber())
      quality = v8_value.As<v8::Number>()->Value();
  }

  String data = ToDataURLInternal(mime_type, quality, kBackBuffer);

  TRACE_EVENT_INSTANT(
      TRACE_DISABLED_BY_DEFAULT("identifiability.high_entropy_api"),
      "CanvasReadback", "data_url", data.Utf8());

  return data;
}
```

> 注意：最新源码可能和当前代码有略微差异，但基本逻辑是一样。要做的是给返回值后面加空格

###### 3.替换为

```c
String HTMLCanvasElement::toDataURL(const String& mime_type,
                                    const ScriptValue& quality_argument,
                                    ExceptionState& exception_state) const {
  if (ContextHasOpenLayers(context_)) {
    exception_state.ThrowDOMException(
        DOMExceptionCode::kInvalidStateError,
        "`toDataURL()` cannot be called with open layers.");
    return String();
  }

  if (!OriginClean()) {
    exception_state.ThrowSecurityError("Tainted canvases may not be exported.");
    return String();
  }

  double quality = kUndefinedQualityValue;
  if (!quality_argument.IsEmpty()) {
    v8::Local<v8::Value> v8_value = quality_argument.V8Value();
    if (v8_value->IsNumber())
      quality = v8_value.As<v8::Number>()->Value();
  }

  String data = ToDataURLInternal(mime_type, quality, kBackBuffer);

  TRACE_EVENT_INSTANT(
      TRACE_DISABLED_BY_DEFAULT("identifiability.high_entropy_api"),
      "CanvasReadback", "data_url", data.Utf8());

  //这里追加几行
  std::srand(std::time(nullptr));
  int randomNum = std::rand() % 100 + 1;
  std::string spaces(randomNum, ' ');
  data = data + String(spaces);
  //LOG(ERROR) << "data:('" << data << "') data";

  return data;
}
```

> 注意：data返回的是`base64`字符串，我们随机给后面加多个空格，这样不但不影响函数的功能，hash的也就是乱的了。

###### 4.编译

```
ninja  -C  out/Default chrome
```

#### 六、在线指纹验证网站：

*   https://abrahamjuliot.github.io/creepjs/
*   https://www.browserscan.net/
