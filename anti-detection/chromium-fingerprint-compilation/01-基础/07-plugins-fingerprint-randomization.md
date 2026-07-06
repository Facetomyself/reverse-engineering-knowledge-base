### 一、什么是plugins指纹

*   "Plugins 指纹"(browser plugin fingerprinting)是一种在线追踪技术。
*   它根据已安装的插些信息，汇总起来创建出一个独特的指纹。
*   plugins指纹唯一性不是特别高，需要配合其他指纹一起使用。

### 二、如何获取自己的plugins指纹

*   有攻才有防，先看看网站是如何通过js获取你的plugins指纹的。
*   将下面的代码复制到F12控制台，就可以获取显示你的plugins指纹了

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

function getPluginsString() {
    if (navigator.plugins === undefined || navigator.plugins.length === 0) {
        return 'no plugins'; // 指示没有插件或无法访问插件信息
    }
    var pluginsString = [];
    
    // 遍历插件列表
    for (var i = 0; i < navigator.plugins.length; i++) {
        var plugin = navigator.plugins[i];
        var pluginString = plugin.name + '::' + plugin.description + '::' + plugin.filename;
        var mimeTypes = [];
        
        // 遍历并列出每个插件支持的MIME类型
        for (var j = 0; j < plugin.length; j++) {
            var mimeType = plugin[j];
            mimeTypes.push(mimeType.type + '~' + mimeType.suffixes);
        }
        
        // 如果有MIME类型，添加至插件信息字符串中
        if (mimeTypes.length > 0) {
            pluginString += '::' + mimeTypes.join(',');
        }
        
        // 将完整的插件信息字符串加入列表中
        pluginsString.push(pluginString);
    }
    
    // 返回一个总的插件信息字符串，用分号隔开各插件
    return pluginsString.join(';');
}

var pluginsFingerprint = getPluginsString();
//这个字符串可以用作插件指纹的一部分

sha256(pluginsFingerprint).then(hash => console.log(hash));
```

*   输出：

```
e336f0bfce56a91fd1fd0a88530f3bf323ad23cf6155769cc89b09092880cde9
```

### 三、chromium编译-随机plugins指纹

*   首先假设你已经编译成功了，我也在第一篇文章写了如何编译chromium的大概流程。
*   打开源码 `third_party/blink/renderer/modules/plugins/dom_plugin.cc`

###### 1.头部加上(随便加在一个`#include`后面)

```c
#include <random>
#include <string>
```

###### 2.找到下面的代码

```c
String DOMPlugin::description() const {
  return plugin_info_->Description();
}
```

###### 替换为

```c
int getRandomIntForFoo8Modern() {
    static std::mt19937 generator(static_cast<unsigned long>(time(NULL))); // 静态以确保只初始化一次
    std::uniform_int_distribution<int> distribution(0, 9);
    return distribution(generator);
}
String DOMPlugin::description() const {
  //return plugin_info_->Description();
  String tmp = plugin_info_->Description();
  return tmp + String(std::to_string(getRandomIntForFoo8Modern()));
}
```

> 此处原理是给每个plugin的description末尾加个随机数，实现hash的指纹随机  
> ![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/9e70b1be3f4ee80e9d51b9ce9669d153.png)

###### 3.编译

```
ninja  -C  out/Default chrome
```

*   编译后每次刷新时plugins指纹都是随机的了。

### 四、在线指纹验证网站：

*   https://abrahamjuliot.github.io/creepjs/
*   https://ip77.net/
