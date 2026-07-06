
### 一、什么是ClientRects指纹

*   ClientRects指纹获取的核心方法是DOM元素方法`getClientRects()​` 。
*   `getClientRects()​` 可以返回一个元素的所有 CSS 边界框（ClientRect对象数组），包括其大小、位置等信息。每个边界框由其左上角的 x, y 坐标和宽高定义。
*   因为不同的设备和浏览器因字体、渲染引擎、屏幕分辨率等因素会有细微的渲染差异，这些差异被用来生成独一无二的指纹。

### 二、js如何获取ClientRects指纹

*   将下面的代码复制到F12控制台，画个矩形，使用`getClientRects()`显示矩形尺寸信息。

```js
let parentElement = document.getElementsByTagName('body')[0]
let newElement = document.createElement('div');
newElement.innerHTML = `
<svg width="100" height="100">
  <rect id="myRect" x="10" y="10" width="30" height="30" />
</svg>
`
parentElement.appendChild(newElement);
let svgRectElement = document.getElementById('myRect');
svgRectElement.getClientRects()[0]
```

*   输出：  
    ![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/4582b0cfde1545aeb3f56136725e29d6.png)

> 可以看到：小数位非常长，不同的浏览器之间存在细微差异。以此hash，则可以获取clientRects指纹

### 三、编译

*   我在第一篇文章写了如何编译chromium的大概流程，假设你已经编译成功了。
*   打开源码 `third_party\blink\renderer\core\geometry\dom_rect.cc`

###### 1.头部加上(随便加在一个`#include`后面)

```c
#include "base/command_line.h"
```

###### 2.找到下面的代码

```c
DOMRect* DOMRect::FromRectF(const gfx::RectF& rect) {
  return MakeGarbageCollected<DOMRect>(rect.x(), rect.y(), rect.width(),
                                       rect.height());
}
```

###### 替换为

```c
DOMRect* DOMRect::FromRectF(const gfx::RectF& rect) {
  base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  int seed;
  if (base_command_line->HasSwitch("fingerprints")) {
      std::istringstream(base_command_line->GetSwitchValueASCII("fingerprints")) >> seed; 
  }else{
      auto now = std::chrono::system_clock::now();
      std::time_t now_time_t = std::chrono::system_clock::to_time_t(now);
      seed = static_cast<int>(now_time_t);
  }
  
  float new_width;
  float new_height;
  if (rect.x() > 0){
	  new_width = rect.width() + (seed % 103 / 100000.0);
	  new_height = rect.height() + (seed % 97 / 100000.0);
  }else{
	  new_width = rect.width();
	  new_height = rect.height();
  }
  
  return MakeGarbageCollected<DOMRect>(rect.x(), rect.y(), new_width, new_height);
  //return MakeGarbageCollected<DOMRect>(rect.x(), rect.y(), rect.width(), rect.height());
}
```

> 原理是rect.x()<0时，则保持不变，>0时随机加上0.00000a。

###### 3.编译

```
ninja  -C  out/Default chrome
```

*   编译后每次刷新时ClientRects指纹都是随机的了。

### 四、在线指纹验证网站：

*   https://browserleaks.com/rects
*   https://www.browserscan.net/

### 五、感谢

*   之前一直没绕过creepjs检测，所以到现在才修改后再发出来。
*   感谢读者的反馈，指纹浏览器功能渐渐更加完善。
