编译自己的指纹浏览器\-随机tls指纹(ja3指纹)
--------------------------

### 一、什么是TLS指纹和JA3指纹

###### TLS指纹：

*   TLS指纹通常是基于TLS握手过程中客户端发送给服务器的TLS客户端Hello消息。
*   这个消息包括了多个字段，比如所支持的加密套件列表、压缩方法、TLS版本以及扩展等。每种浏览器或客户端软件在与服务器建立TLS连接时，因为它们实现TLS标准的方式略有不同，会生成不同的客户端Hello信息。
*   通过收集和分析这些信息，可以生成一个"指纹"。

###### JA3指纹：

*   JA3是一种特定的TLS指纹技术方法，由Salesforce团队开发。
*   它创建了一种结构化的方法来表示TLS握手中的无变量部分，包括TLS版本、可接受的加密算法、扩展等，并将这些元素组合为一个MD5哈希值。
*   不同版本的浏览器会有不同的JA3指纹。

### 二、如何在线获取自己的tls指纹

*   网址1：https://tls.peet.ws/
*   网址2：https://browserleaks.com/tls

### 三、chromium编译-随机tls指纹

*   首先假设你已经编译成功了，我也在第一篇文章写了如何编译chromium的大概流程。
*   打开源码文件`third_party/boringssl/src/ssl/ssl_cipher.cc`

###### 1.头部加上(随便加在一个`#include`后面)

```c
#include <algorithm>
#include <random>
#include <iostream>
```

###### 2.找到下面的代码

```c
  static const uint16_t kLegacyCiphers[] = {
      TLS1_CK_ECDHE_ECDSA_WITH_AES_128_CBC_SHA & 0xffff,
      TLS1_CK_ECDHE_RSA_WITH_AES_128_CBC_SHA & 0xffff,
      TLS1_CK_ECDHE_PSK_WITH_AES_128_CBC_SHA & 0xffff,
      TLS1_CK_ECDHE_ECDSA_WITH_AES_256_CBC_SHA & 0xffff,
      TLS1_CK_ECDHE_RSA_WITH_AES_256_CBC_SHA & 0xffff,
      TLS1_CK_ECDHE_PSK_WITH_AES_256_CBC_SHA & 0xffff,
      TLS1_CK_ECDHE_RSA_WITH_AES_128_CBC_SHA256 & 0xffff,
      TLS1_CK_RSA_WITH_AES_128_GCM_SHA256 & 0xffff,
      TLS1_CK_RSA_WITH_AES_256_GCM_SHA384 & 0xffff,
      TLS1_CK_RSA_WITH_AES_128_SHA & 0xffff,
      TLS1_CK_PSK_WITH_AES_128_CBC_SHA & 0xffff,
      TLS1_CK_RSA_WITH_AES_256_SHA & 0xffff,
      TLS1_CK_PSK_WITH_AES_256_CBC_SHA & 0xffff,
      SSL3_CK_RSA_DES_192_CBC3_SHA & 0xffff,
  };
```

> 可以看到加密方式在chromium中是写死的，顺序也是。我们不能随意删减加密方式，但我们给他随机打乱还是可以的。

###### 替换为

```c
  static uint16_t kLegacyCiphers[] = {
      TLS1_CK_ECDHE_ECDSA_WITH_AES_128_CBC_SHA & 0xffff,
      TLS1_CK_ECDHE_RSA_WITH_AES_128_CBC_SHA & 0xffff,
      TLS1_CK_ECDHE_PSK_WITH_AES_128_CBC_SHA & 0xffff,
      TLS1_CK_ECDHE_ECDSA_WITH_AES_256_CBC_SHA & 0xffff,
      TLS1_CK_ECDHE_RSA_WITH_AES_256_CBC_SHA & 0xffff,
      TLS1_CK_ECDHE_PSK_WITH_AES_256_CBC_SHA & 0xffff,
      TLS1_CK_ECDHE_RSA_WITH_AES_128_CBC_SHA256 & 0xffff,
      TLS1_CK_RSA_WITH_AES_128_GCM_SHA256 & 0xffff,
      TLS1_CK_RSA_WITH_AES_256_GCM_SHA384 & 0xffff,
      TLS1_CK_RSA_WITH_AES_128_SHA & 0xffff,
      TLS1_CK_PSK_WITH_AES_128_CBC_SHA & 0xffff,
      TLS1_CK_RSA_WITH_AES_256_SHA & 0xffff,
      TLS1_CK_PSK_WITH_AES_256_CBC_SHA & 0xffff,
      SSL3_CK_RSA_DES_192_CBC3_SHA & 0xffff,
  };

size_t arraySize = sizeof(kLegacyCiphers) / sizeof(kLegacyCiphers[0]);
std::random_device rd;
std::mt19937 rng(rd());
std::shuffle(kLegacyCiphers, kLegacyCiphers + arraySize, rng);
for (const auto& value : kLegacyCiphers) {
	std::cout << std::hex << value << std::endl;
}
```

> 这样加密顺序就打乱了。

###### 3.编译

```
ninja  -C  out/Default chrome
```

*   编译后每次刷新时tls指纹都是随机的了。
