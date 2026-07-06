
自定义chormium-修改屏幕尺寸
------------------

> 屏幕尺寸信息雷同太大，用作指纹信息，作用不多。  
> 但多个类似小信息组合在一起的话，也就是成唯一指纹了。积少成多吧。

### 一、如何使用js获取屏幕信息

```js
console.log("screen.width", screen.width)
console.log("screen.height", screen.height)
console.log("screen.availWidth", screen.availWidth)
console.log("screen.availHeight", screen.availHeight)

// 获取设备的像素比
let pixelRatio = window.devicePixelRatio;
console.log('设备像素比为：' + pixelRatio);
console.log('屏幕像素为：', screen.width*pixelRatio, screen.height*pixelRatio );
```

输出：

```js
screen.width 1707
screen.height 1067
screen.availWidth 1707
screen.availHeight 1019
设备的像素比为：1.350000023841858
屏幕像素为： 2560.5 1600.5
```

### 二、如何更改源码：

*   打开 `/third_party/blink/renderer/core/frame/screen.cc`

###### 1.头部加上(随便加在一个`#include`后面)

```c
#include "base/command_line.h"
```

###### 2.找到：

```c
int Screen::availHeight() const {
  if (!DomWindow())
    return 0;
  return GetRect(/*available=*/true).height();
}
```

###### 3.替换为：

```c
int Screen::availHeight() const {
  if (!DomWindow())
    return 0;

  // 追加
  base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  int seed;
  if (base_command_line->HasSwitch("fingerprints")) {
    std::istringstream(base_command_line->GetSwitchValueASCII("fingerprints")) >> seed; 
  }else{
    auto now = std::chrono::system_clock::now();
    std::time_t now_time_t = std::chrono::system_clock::to_time_t(now);
    seed = static_cast<int>(now_time_t);
  }
  return GetRect(/*available=*/true).height() - 10 - seed%10;
  
  //return GetRect(/*available=*/true).height();
}
```

###### 4.编译

```
ninja  -C  out/Default chrome
```

> 注意：这里只更改了`Screen::availHeight()`函数，剩下的几个函数，小伙伴们按需更改。

*   `Screen::height()`
*   `Screen::width()`
*   `Screen::availHeight()`
*   `Screen::availWidth()`

### 三、反检测

> 要注意：`Screen::height()`和`Screen::width()`修改时有反检测手段。

*   creepjs会报错`failed matchMedia`

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/45d12fefc6ae4cc6aa6063204ddf8983.png)

*   有攻必有防，看看js如何检测屏幕尺寸是否篡改的。

```js
let { width, height, availWidth, availHeight, colorDepth, pixelDepth, } = (window.screen || {})
let lie_js = `(device-width: ${width}px) and (device-height: ${height}px)`
console.log("lie_js",lie_js)
let matchMediaLie = window.matchMedia(lie_js).matches
if (matchMediaLie){
    console.log("屏幕数值正常")
}else{
    console.log("发现篡改")
}
```

输出：

```js
lie_js (device-width: 1707px) and (device-height: 1067px)
屏幕数值正常
```

### 四、反反检测

*   打开 `\third_party\blink\renderer\core\css\media_query_evaluator.cc`

###### 1.找到

```c
static bool DeviceHeightMediaFeatureEval(const MediaQueryExpValue& value,
                                         MediaQueryOperator op,
                                         const MediaValues& media_values) {
  if (value.IsValid()) {
    return ComputeLengthAndCompare(value, op, media_values,
                                   media_values.DeviceHeight());
  }

  // ({,min-,max-}device-height)
  // assume if we have a device, assume non-zero
  return true;
}

static bool DeviceWidthMediaFeatureEval(const MediaQueryExpValue& value,
                                        MediaQueryOperator op,
                                        const MediaValues& media_values) {
  if (value.IsValid()) {
    return ComputeLengthAndCompare(value, op, media_values,
                                   media_values.DeviceWidth());
  }

  // ({,min-,max-}device-width)
  // assume if we have a device, assume non-zero
  return true;
}
```

##### 2.替换为

```c
static bool DeviceHeightMediaFeatureEval(const MediaQueryExpValue& value,
                                         MediaQueryOperator op,
                                         const MediaValues& media_values) {
  //if (value.IsValid()) {
  //  return ComputeLengthAndCompare(value, op, media_values,
  //                                 media_values.DeviceHeight());
  //}

  // ({,min-,max-}device-height)
  // assume if we have a device, assume non-zero
  return true;
}

static bool DeviceWidthMediaFeatureEval(const MediaQueryExpValue& value,
                                        MediaQueryOperator op,
                                        const MediaValues& media_values) {
  //if (value.IsValid()) {
  //  return ComputeLengthAndCompare(value, op, media_values,
  //                                 media_values.DeviceWidth());
  //}

  // ({,min-,max-}device-width)
  // assume if we have a device, assume non-zero
  return true;
}
```

> 这里强制将`window.matchMedia(lie_js).matches`返回值改为true了。

###### 3.编译

```
ninja  -C  out/Default chrome
```

### 五、还需要优化

> 部分站点只允许常用分辨率通过，不常用的分辨率则会进入风控

*   可以建个常用分辨率的数组，从中随机挑选：

```c
std::vector<int> arr = {800, 1152, 1280, 1366, 1600, 1680, 1920, 2560};
std::vector<int> arr2 = {600, 864, 720, 768, 900, 1050, 1080, 1440};
```
