随机指纹chromium定制-如何通过传参来固定指纹
--------------------------

> 由于要所有的类型的指纹都实现固定，工作量太大，这里我只用`plugins指纹`作为示例。

#### 一、为什么要固定指纹

*   目标：启动浏览器时，加上参数`--fingerprints="xxxxxxx"`, 参数变化时，指纹也会跟着变化。打开网页后的后续访问指纹都不会再变化。
*   广泛用于一些电商平台

#### 二、什么是plugins指纹：

*   之前有介绍过`plugins指纹`和如何修改：[插眼传送](https://blog.csdn.net/w1101662433/article/details/138058525)

#### 三、重新修改源码

*   打开源码 `third_party/blink/renderer/modules/plugins/dom_plugin.cc`

###### 1.头部加上(随便加在一个`#include`后面，之前加过就不用加了)

```c
#include <random>
#include <string>
#include "base/command_line.h"
```

###### 2.找到下面的代码

```c
String DOMPlugin::description() const {
  return plugin_info_->Description();
}
```

###### 3.替换为

```c
String DOMPlugin::description() const {
  //return plugin_info_->Description();
  base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  std::string tmp;
  if (base_command_line->HasSwitch("fingerprints")) {
	  tmp = base_command_line->GetSwitchValueASCII("fingerprints"); 
  }else{
	  tmp = base_command_line->GetSwitchValueASCII("type"); 
  }
  // LOG(ERROR) << "tmp:('" << tmp << "') tmp";
  String res = plugin_info_->Description();
  return res + String(tmp);
}
```

> 代码的原理是给每个plugin的description末尾追加上`--fingerprints`获取的字符串。

###### 4.编译

```
ninja  -C  out/Default chrome
```

#### 四、render进程追加参数

> 打开资源管理器，就可以发现，chromium默认使用的是多进程，只有一条主进程，有`--type`的都是子进程

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/3bced07583c7935dc8ef88a13a4ab235.png)

> 启动浏览器的参数默认又只能传给主进程，所以我们还要改进程创建程序，将参数传给子进程。

*   打开源码：`\content\browser\renderer_host\render_process_host_impl.cc`

###### 1.找到下面的代码

```c
command_line->AppendSwitchASCII(switches::kProcessType,
                                  switches::kRendererProcess);
```

###### 2.替换为

```c
command_line->AppendSwitchASCII(switches::kProcessType,
                                  switches::kRendererProcess);

//追加					  
const base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
if (base_command_line->HasSwitch("fingerprints")) {
  const std::string tmp = base_command_line->GetSwitchValueASCII("fingerprints");
  command_line->AppendSwitchASCII("fingerprints", tmp);
}	

```

###### 3.编译

```
ninja  -C  out/Default chrome
```

> 可以了，后续每次启动chromium时改变 `--fingerprints="xxxxxxx"` 参数值，就会有不同的plugins指纹

#### 五、验证一下

*   将`navigator.plugins`复制到F12控制台

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/40fd061199c45afdce3c6d9d838878d6.png)

*   发现description中成功追加了我们的参数。固定plugins指纹成功。

> 相信我这里起个头，其他指纹如何固定，你应该跃跃欲试了。
