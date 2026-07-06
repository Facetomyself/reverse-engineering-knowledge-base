自定义指纹chromium-随机tls指纹(ja4指纹)
----------------------------

### 一、什么是JA4指纹

*   JA4指纹可以理解成：将加密算法顺序排序后的ja3指纹。
*   之前写过一篇博客介绍ja3指纹：[插眼传送](https://blog.csdn.net/w1101662433/article/details/138301698)
*   由于之前打乱算法顺序，只会改变ja3指纹和akamai指纹，ja4指纹并不会变。所以这次我们对加密算法进行随机增减。

### 二、如何在线获取自己的ja4指纹

*   网址1：https://tls.peet.ws/

### 三、chromium编译-随机tls指纹

*   首先假设你已经编译成功了，我也在第一篇文章写了如何编译chromium的大概流程。
*   打开源码文件`\net\socket\ssl_client_socket_impl.cc`

###### 1.头部加上(随便加在一个`#include`后面)

```c
#include <random>
```

###### 2.定义一个获取随机数的函数

```c
int getRandomIntForFoo12Modern() {
    static std::mt19937 generator(static_cast<unsigned long>(time(NULL))); 
    std::uniform_int_distribution<int> distribution(0, 1);
    return distribution(generator);
}
```

###### 3.找到下面的代码

```c
  std::string command("ALL:!aPSK:!ECDSA+SHA1:!3DES");
```

> 可以看到加密方式在chromium中是写死的，顺序也是。我们不能随意删减加密方式，但我们给他随机打乱还是可以的。

###### 替换为

```c
//std::string command("ALL:!aPSK:!ECDSA+SHA1:!3DES");
std::string command("ALL");
if (getRandomIntForFoo12Modern() == 0)command.append(":!aPSK");
if (getRandomIntForFoo12Modern() == 0)command.append(":!kRSA");
if (getRandomIntForFoo12Modern() == 0)command.append(":!ECDSA");
if (getRandomIntForFoo12Modern() == 0)command.append(":!ECDSA+SHA1");
if (getRandomIntForFoo12Modern() == 0)command.append(":!3DES");
```

> 这样加密算法就进行了随机增减。

###### 3.编译

```
ninja  -C  out/Default chrome
```

*   编译后每次刷新时ja4指纹也都是随机的了。
