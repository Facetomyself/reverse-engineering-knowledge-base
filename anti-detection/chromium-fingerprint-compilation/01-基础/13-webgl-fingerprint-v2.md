指纹浏览器开发-修改webGL指纹(二)
--------------------

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
