
### 一、目标：

*   实现传入参数`--disable-css-animation`，禁用css动画
*   实现传入参数`--disable-canvas`，禁用canvas渲染

> 阅读此篇博客前，请确保已具备chromium编译基础。

### 二、为何禁用动画

*   浏览器做自动化有几个硬伤，1.带宽占用高，2.cpu占用高，3.内存占用高。
*   虽然我们是用空间换时间，但还是希望cpu占用再降一点
*   禁止图片访问可以节约大量带宽。禁用css动画和canvas渲染，对于有动画的网页，则可以**节约大量cpu**.

### 三、css动画案例

*   创建一个有css动画的测试页面，将下面的代码复制到随便一个html，比如111.html

```html
<!DOCTYPE html>   
<html lang="en">   
<head>
    <meta charset="UTF-8">
    <title>无限CSS动画示例</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background-color: #1a1a1a;
        }

        .animated-box {
            width: 100px;
            height: 100px;
            background-color: #ff4757;
            animation: 
                rotate 3s linear infinite,
                color-change 5s ease-in-out infinite;
        }

        @keyframes rotate {
            from {
                transform: rotate(0deg);
            }
            to {
                transform: rotate(360deg);
            }
        }

        @keyframes color-change {
            0% {
                background-color: #ff4757;
            }
            50% {
                background-color: #2ed573;
            }
            100% {
                background-color: #5352ed;
            }
        }
    </style>   
</head>   
<body>
    <div class="animated-box"></div>   
</body>   
</html>

```

> 用浏览器打开这个页面，发现一个浏览器的cpu占用率就有大概5%左右。

### 四、修改chromium源码

*   打开 `\third_party\blink\renderer\core\css\resolver\style_resolver.cc`

###### 1.引用：

```c
#include "base/command_line.h"
```

###### 2.找到：

```c
bool StyleResolver::ApplyAnimatedStyle(
    StyleResolverState& state,
    StyleCascade& cascade,
    const StyleRecalcContext& style_recalc_context) {
```

###### 3.替换为：

```c
bool StyleResolver::ApplyAnimatedStyle(
    StyleResolverState& state,
    StyleCascade& cascade,
    const StyleRecalcContext& style_recalc_context) {
  // 开始追加 =================================
  base::CommandLine* cmdLine = base::CommandLine::ForCurrentProcess();
  if (cmdLine->HasSwitch("disable-css-animation")) {
      return false;
  }
  // 结束追加 =================================
```

###### 4.给render进程追加参数

*   打开：`/content/browser/renderer_host/render_process_host_impl.cc`

```c
command_line->AppendSwitchASCII(switches::kProcessType,
                                  switches::kRendererProcess);
                                  
  // 开始追加 =====================================
  const base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();

  if (base_command_line->HasSwitch("disable-css-animation")) {
      command_line->AppendSwitch("disable-css-animation");
  }

//结束追加 ===================================
```

###### 5.编译

```
ninja  -C  out/Default chrome
```

### 五、检测：

*   编译完成后再次检测刚刚页面的cpu占用，提示cpu占用大约只有0.2%左右了
*   测试页面2：[https://www.python-spider.com/challenge/login](https://www.python-spider.com/challenge/login), 也是css动画导致cpu占用较高  
    ![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/5f1af417404c4e02ac22446efd4176f5.png)
*   这里一个滑块动画就要占用将近5%的cpu，因此需要禁用css动画。

### 六、如何禁用canvas

> 这里我就不多说了，和css动画原理相同。直接提供修改地址：

*   打开 `\third_party\blink\renderer\modules\canvas\htmlcanvas\html_canvas_element_module.cc`

```c
#include "base/command_line.h"

V8RenderingContext* HTMLCanvasElementModule::getContext(
    HTMLCanvasElement& canvas,
    const String& context_id,
    const CanvasContextCreationAttributesModule* attributes,
    ExceptionState& exception_state) {
        
  // 开始追加 =================================
  base::CommandLine* cmdLine = base::CommandLine::ForCurrentProcess();
  if (cmdLine->HasSwitch("disable-canvas")) {
      return nullptr;
  }
  // 结束追加 =================================

```

