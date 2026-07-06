
一、目标：
-----

*   目标：将cookie的超时时间强制设置成不过期，退出浏览器时不删除cookie，以保持登录状态。

> 阅读此篇博客前，请确保已具备chromium编译基础。

二、为什么要设置cookie的持久化存储：
---------------------

*   众所周知，cookie有过期时间，市面上大部分站点都会设置登录失效时间为1周-1个月
*   然而有些站点设置5分钟即失效，或设置过期时间为session（退出浏览器即失效）。

> 既然站点的cookie是前端可以设置的，那我们开发人员就有了操作空间。这里我们**把过期时间强制设置成1年**，一次性把这个问题给永久解决。

三、修改chromium源码：
---------------

*   打开：`/net/cookies/canonical_cookie.cc`

##### 1.加入头部引用：

```c
#include <iostream>
#include "base/command_line.h"
```

##### 2.修改位置：

*   找到代码：

```c
  Time cookie_expires = CanonicalCookie::ParseExpiration(
      parsed_cookie, creation_time, cookie_server_time);
  cookie_expires =
      ValidateAndAdjustExpiryDate(cookie_expires, creation_time, source_scheme);

  auto cc = std::make_unique<CanonicalCookie>(
      base::PassKey<CanonicalCookie>(), parsed_cookie.Name(),
      parsed_cookie.Value(), std::move(cookie_domain).value_or(std::string()),
      std::move(cookie_path), creation_time, cookie_expires, creation_time,
      /*last_update=*/base::Time::Now(), parsed_cookie.IsSecure(),
      parsed_cookie.IsHttpOnly(), samesite, parsed_cookie.Priority(),
      cookie_partition_key, source_scheme, source_port, source_type);

```

*   替换为：

```c
  Time cookie_expires = CanonicalCookie::ParseExpiration(
      parsed_cookie, creation_time, cookie_server_time);
  
  // 开始追加===========================
  cookie_expires = base::Time::Max();
  // 结束追加 ===========================

  cookie_expires =
      ValidateAndAdjustExpiryDate(cookie_expires, creation_time, source_scheme);

  auto cc = std::make_unique<CanonicalCookie>(
      base::PassKey<CanonicalCookie>(), parsed_cookie.Name(),
      parsed_cookie.Value(), std::move(cookie_domain).value_or(std::string()),
      std::move(cookie_path), creation_time, cookie_expires, creation_time,
      /*last_update=*/base::Time::Now(), parsed_cookie.IsSecure(),
      parsed_cookie.IsHttpOnly(), samesite, parsed_cookie.Priority(),
      cookie_partition_key, source_scheme, source_port, source_type);
```

##### 3.编译

```bash
ninja -C out/Default chrome
```

四、成果测试：
-------

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/8297b0f399894fe29e22077542b1dba6.png)

*   运行`./chrome.exe`后，可以看到，cookie的过期时间全部变成1年后了。

> 现在即使将浏览器关闭后重新打开，依然可以**正常保持登录状态**了，因为我们做了cookie持久化存储。

