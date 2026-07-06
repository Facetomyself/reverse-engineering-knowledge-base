
### 一、目标：

*   1.了解js是如何获取windows版本的。
*   2.如何从c++层面修改chromium源码，修改win系统版本

### 二、js是如何获取 windows 系统版本：

*   将下面的js复制到F12控制台

```js
async function detectWindowsVersion() {
  let userAgent = navigator.userAgent;
  if (/Windows NT 10.0/.test(userAgent)) {
  
     ua = await navigator.userAgentData.getHighEntropyValues(["platformVersion"])
     
       if (navigator.userAgentData.platform === "Windows") {
         const majorPlatformVersion = parseInt(ua.platformVersion.split('.')[0]);
         if (majorPlatformVersion >= 13) {
           return "Windows 11";
          }else if (majorPlatformVersion > 0) {
            return "Windows 10";
          }
       }

  } else if (/Windows NT 6.3/.test(userAgent)) {
    return "Windows 8.1";
  } else if (/Windows NT 6.2/.test(userAgent)) {
    return "Windows 8";
  } else if (/Windows NT 6.1/.test(userAgent)) {
    return "Windows 7";
  } else if (/Windows NT 6.0/.test(userAgent)) {
    return "Windows Vista";
  } else if (/Windows NT 5.1|Windows XP/.test(userAgent)) {
    return "Windows XP";
  } else {
    return "未知";
  }
}
let version = await detectWindowsVersion();
console.log(version)

```

*   输出：

```
Windows 11
```

> 注释：js获取win系统版本分为2部分：  
> 1是win10之前的版本区分，通过`navigator.userAgent`中的NT版本数字来区分，  
> 2是win10和win11的区分，通过`navigator.userAgentData`来区分

### 三、修改源码：

*   前面的博客写了如何编译chormium，这里假设你都已经是个编译成功了

> 由于现在用户基本都是Win10+了，我这里只提供Win10和Win11随机切换的源码修改。

###### 1.打开 `\third_party\blink\renderer\core\frame\navigator_ua.cc`

*   找到源码：

```c
  ua_data->SetPlatform(String::FromUTF8(metadata.platform),
                      String::FromUTF8(metadata.platform_version));
```

###### 2.替换为：

```c
  //ua_data->SetPlatform(String::FromUTF8(metadata.platform),
                       //String::FromUTF8(metadata.platform_version));
  // 开始更改======================== 
  base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  

  int seed = 123123123;
  if (base_command_line->HasSwitch("fingerprints")) {
      std::istringstream(base_command_line->GetSwitchValueASCII("fingerprints")) >> seed;
  }
  int platfrom_v = 7;
  if (base_command_line->HasSwitch("fingerprints")) {
    platfrom_v = seed % 7 + 10;
  }
  ua_data->SetPlatform(String::FromUTF8(metadata.platform), String::FromUTF8(std::to_string(platfrom_v) + ".0.0"));
  // 结束更改========================  

```

> 注意：这里platfrom\_v的随机取值范围是7~16，大于12为`Win11`，反之则为`Win10`

###### 3.编译

```c
ninja -C out/Default chrome
```
