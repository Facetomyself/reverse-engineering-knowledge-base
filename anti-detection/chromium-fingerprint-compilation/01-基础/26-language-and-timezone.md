
一、为啥要改时区：
---------

*   使用代理访问网络是，浏览器会出现ip所在地和我们的时区所在地不一致，很容易被识别出们使用了代理。
*   最简单的修改时区的办法是直接将windows时间设置中，找到时区，改成ip所在的时区即可。
*   这里，我还提供下choromium源码中修改时区的方法。

### 二、修改源码

*   找到文件 `\third_party\icu\source\i18n\timezone.cpp`

###### 1.找到

```c
TimeZone *default_zone = TimeZone::detectHostTimeZone();
```

###### 1.替换为：

```c
TimeZone *default_zone = TimeZone::createTimeZone(icu::UnicodeString::fromUTF8("Asia/Tokyo"));
```

> 注意：这里只改成了日本时区，其他自行更换即可。

###### 3.编译

```
ninja  -C  out/Default chrome
```

> 注意：因为这个文件接收不到参数，所以我的解决方案是：启动时将参数写进一个文件中，后续这里再读文件的。小伙伴们有其他好的解决方案可以留言。

### 三、更改语言：

*   这个非常简单，就是追加2个已有的chrome参数即可：`--lang=en-US`和 `--accept-lang=en-US`。

* * *

### 四、2025-01-22追加：通过读文件方式获取时区参数

###### 1.找到 `/content/browser/browser_main_loop.cc`

```c
void BrowserMainLoop::PostCreateThreadsImpl() {
  TRACE_EVENT0("startup", "BrowserMainLoop::PostCreateThreadsImpl");

  // Bring up Mojo IPC and the embedded Service Manager as early as possible.
  // Initializaing mojo requires the IO thread to have been initialized first,
  // so this cannot happen any earlier than now.
  InitializeMojo();

```

###### 2.替换为

```c
void BrowserMainLoop::PostCreateThreadsImpl() {
  TRACE_EVENT0("startup", "BrowserMainLoop::PostCreateThreadsImpl");

  // Bring up Mojo IPC and the embedded Service Manager as early as possible.
  // Initializaing mojo requires the IO thread to have been initialized first,
  // so this cannot happen any earlier than now.
  InitializeMojo();
  
  // 追加===================================================
  base::CommandLine* cmdLine = base::CommandLine::ForCurrentProcess();
  std::string timeZonePath = "./timezone.txt"; 
  if (!cmdLine->HasSwitch("timezone")) {
    std::filesystem::remove(timeZonePath);
  }else{
    std::ofstream outputFileZ(timeZonePath);
    outputFileZ << cmdLine->GetSwitchValueASCII("timezone");
    outputFileZ.close(); 
  }
```

> 这里是浏览器启动时，将`--timezone`获取的值写入`./timezone.txt`

###### 3.再找到：`\third_party\icu\source\i18n\timezone.cpp`

```c
TimeZone *default_zone = TimeZone::detectHostTimeZone()
```

###### 4.替换为

```c
// 修改================================================
	TimeZone *default_zone;
    std::string timeZonePath = "./timezone.txt"; 
    std::ifstream inputFileZ(timeZonePath);
    if (inputFileZ.is_open()) {
		std::string content;
        inputFileZ >> content;
		default_zone = TimeZone::createTimeZone(icu::UnicodeString::fromUTF8(content));
		inputFileZ.close();
		//if(content.size()>4){std::filesystem::remove(timeZonePath);}
	}else{
		default_zone = TimeZone::detectHostTimeZone();
	}
	// 结束修改================================================

```

> 这里是再在文件里读取时区并使用。

###### 5.编译

```
ninja  -C  out/Default chrome
```

#### 五、2025-05-08追加

*   群友提供了更优秀的时区传参位置解决方案：
*   打开 `/base/i18n/icu_util.cc`

```c
#include <iostream>
#include "base/command_line.h"
#include "third_party/icu/source/i18n/unicode/timezone.h"
```

```c
bool InitializeICU() {
#if DCHECK_IS_ON()
  DCHECK(!g_check_called_once || !g_called_once);
  g_called_once = true;
#endif

#if (ICU_UTIL_DATA_IMPL == ICU_UTIL_DATA_STATIC)
  // The ICU data is statically linked.
#elif (ICU_UTIL_DATA_IMPL == ICU_UTIL_DATA_FILE)
  if (!InitializeICUFromDataFile())
    return false;
#else
#error Unsupported ICU_UTIL_DATA_IMPL value
#endif  // (ICU_UTIL_DATA_IMPL == ICU_UTIL_DATA_STATIC)

  // 开始追加 ======================
  base::CommandLine* cmdLine = base::CommandLine::ForCurrentProcess();
  if (cmdLine->HasSwitch("timezone")) {
      std::string timezone_str = cmdLine->GetSwitchValueASCII("timezone");
      std::cerr << "timezone_str: " << timezone_str << std::endl;
      icu::TimeZone *default_zone = icu::TimeZone::createTimeZone(icu::UnicodeString::fromUTF8(timezone_str));
      icu::TimeZone::adoptDefault(default_zone);
  }
  // 结束追加 ======================
  return DoCommonInitialization();
}
```
