### 通过源码编译随机canvas指纹

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
