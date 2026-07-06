修改chromium源码随机webGL指纹
---------------------

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
