# App 逆向的全局视角

> 来源: 公众号 PDF 归档（反爬破解社 / 爬虫任）
> 原始发布时间: 2026-07-05
> 归档日期: 2026-07-07
> 分类: 移动 App 逆向 — 方法论与切入点
>
> 本文建立 App 逆向的基础地图：从一次请求的生命周期出发，梳理 UI、业务、网络、加密、JNI、SO、网络发送各层的切入点，并总结定位加密点、还原算法、模拟请求三类核心任务。

## 一条 App 请求的完整生命周期

很多初学者学 App 逆向，上来就装模拟器、配 Frida、看 jadx，结果折腾一星期，连一个 App 的登录接口都没调通。根本原因是没有地图。

一次 App 请求从点击到发出去，通常会经过下面这条链路：

```text
用户点击按钮
    ↓
Activity（UI 层）—— 接收事件，调用业务逻辑
    ↓
Service / Presenter（业务层）—— 组装请求参数
    ↓
OkHttp / Retrofit（网络层）—— 构建 Request 对象
    ↓
加密层（Interceptor）—— 给参数加签、给 body 加密
    ↓
JNI 层（Native 方法）—— 调用 C/C++ 代码执行加密
    ↓
SO 层（动态库）—— 真正的加密算法执行
    ↓
网络发送 —— TCP/TLS 握手，发出 HTTP 请求
```

这七个环节，每一个都可能成为逆向突破口，也可能埋下防御陷阱。

### 1. Activity / UI 层

用户点击“登录”按钮，触发 `onClick` 事件，调用对应的 `Presenter.login()` 方法。

逆向关注点：这一层通常不会有加密逻辑，但可以通过它找到业务入口。在 jadx 里搜索 `setOnClickListener`，可以快速定位按钮对应的回调函数。

### 2. Service / Presenter 业务层

这一层负责组装参数。比如登录时需要传入 `username`、`password`、`timestamp`。

逆向关注点：观察参数来源。`password` 是从 `EditText` 直接拿的明文，还是已经被加密过一次？有些 App 会在这一层做第一层加密，比如前端先 MD5 一次，然后再传给下层。

### 3. OkHttp / Retrofit 网络层

现代 Android App 几乎都用 OkHttp 作为网络框架。它会构建一个 `Request` 对象，包含 URL、Header、Body。

逆向关注点：这是最容易被 Hook 的地方。用 Frida Hook 住 `OkHttpClient.newCall()`，可以直接打印出所有请求参数和响应。很多 App 的加密就在这一步之前的 `Interceptor` 里完成。

### 4. 加密层 Interceptor

OkHttp 的 `Interceptor` 机制允许开发者在请求发出前拦截并修改 `Request`。大部分 App 的签名算法就写在这里。

逆向关注点：找到自定义的 `Interceptor` 类。在 jadx 里搜索 `intercept` 关键字，或者搜索 `addInterceptor`，通常能定位到加密逻辑所在的类。

### 5. JNI 层

如果加密逻辑写在 Java 层容易被反编译，开发者会把它移到 Native 层。Java 通过 `System.loadLibrary("xxx")` 加载 SO 文件，然后调用 `native` 方法。

逆向关注点：搜索 `System.loadLibrary`，找到加载的 SO 文件名。然后在 jadx 里搜索 `native` 关键字，找到对应的 `native` 方法声明。这些方法的实现在 SO 文件里。

### 6. SO 层

真正的加密算法在这里执行。C/C++ 代码编译成 ARM 汇编，反编译难度远高于 Java。

逆向关注点：用 IDA 或 Ghidra 打开 SO 文件，找到对应的导出函数。或者用 Frida Hook `dlopen`，在 SO 加载时注入。

### 7. 网络发送

最终，加密后的请求通过 Socket 发出。如果是 HTTPS，还会经过 TLS 层。

逆向关注点：如果前面的加密都搞不定，可以考虑在网卡层面抓包。但这种情况很少见，而且涉及底层驱动，一般不作为首选。

## 逆向的核心任务

理解了生命周期，逆向的核心任务就非常清晰，主要是三步。

### 第一步：定位加密点

要回答的问题是：这个 App 在哪里对参数做了手脚？

- 是在 Java 层的 `Interceptor` 里？
- 还是在 JNI 的 SO 文件里？
- 或者是两者结合，Java 层做一层，Native 层再做一层？

定位方法：

- 静态分析：jadx 搜索关键词，例如 `sign`、`encrypt`、`md5`、`aes`
- 动态 Hook：用 Frida Hook 所有可疑函数，打印入参和返回值
- 对比法：抓包拿到加密后的参数，然后在代码里搜索这个值的生成逻辑

### 第二步：还原算法

定位到加密点之后，要搞清楚它是怎么算出来的。

- 是简单的 `MD5(参数 + 盐值)`？
- 还是 AES-CBC 加密，Key 和 IV 藏在 SO 里？
- 或者是魔改的 HMAC-SHA256？

还原方法：

- 读代码逻辑，用 Python 重写
- Hook 函数的入参，直接拿到明文和密钥
- 对于 SO 层算法，可以用 Unicorn 模拟执行

### 第三步：模拟请求

算法还原后，用 Python / Go 构造同样的请求头、请求体并发送给服务器。如果能正常返回数据，就算成功。

这三步就是 App 请求逆向的主线。听起来简单，但每一步都有很多坑，后续分析都可以放回这张地图里定位。

## 常见防御手段

### 1. SSL Pinning 证书锁定

App 只信任特定的服务器证书，用 Charles / Fiddler 抓包时会看到证书错误或连接失败。

常见绕过方式：

- 使用 JustTrustMe Xposed 模块
- 用 Frida Hook `checkServerTrusted` 方法
- 重打包，替换证书校验逻辑

### 2. 参数签名

每次请求都带上一个 `sign` 参数，由所有请求参数、盐值、时间戳计算得出。服务器收到请求后重新计算一遍，如果不一致就拒绝。

常见绕过方式：找到签名算法，用 Python 复现。难点在于盐值可能藏在 SO 里，或者每次都不一样。

### 3. 时间戳校验

请求中携带时间戳，服务器判断是否在合理范围内，例如前后 5 分钟。如果时间偏差太大，直接拒绝。

常见绕过方式：同步系统时间，或者在 Frida 里 Hook `System.currentTimeMillis()` 返回伪造时间。

### 4. 设备指纹

服务器记录设备的 IMEI、MAC 地址、Android ID 等信息。如果同一台设备频繁请求，可能被封禁。

常见绕过方式：用 Frida Hook `TelephonyManager.getDeviceId()` 等 API，返回随机值。或者直接用虚拟机配合改机工具。

### 5. SO 层加壳

SO 文件被加密或压缩，运行时才解密加载。直接用 IDA 打开看到的是一堆无效内容。

常见绕过方式：

- 用 Frida 在 SO 加载完成后 dump 内存中的原始 SO
- 使用 frida-dexdump 等工具自动脱壳

### 6. VMP 虚拟机保护

核心算法被翻译成自定义字节码，然后用内置解释器执行。逆向难度极高。

常见绕过方式：这属于进阶内容，基础阶段不展开。一般思路是 trace 执行轨迹，或者直接 Hook 输入输出，绕过算法本身。

## 逆向地图速查

| 请求阶段 | 常用技术 | 逆向切入点 | 常见防御 |
|----------|----------|------------|----------|
| UI 层 | Activity / Fragment | 查找按钮回调 | 无 |
| 业务层 | Presenter / ViewModel | 参数组装逻辑 | 前端加密 |
| 网络层 | OkHttp / Retrofit | Hook `newCall()` | 无 |
| 加密层 | Interceptor | 搜索 `intercept` | 混淆代码 |
| JNI 层 | `native` 方法 | 搜索 `native` 关键字 | 动态注册 |
| SO 层 | C/C++ | IDA / Frida 分析 | 加壳、OLLVM |
| 网络层 | Socket / TLS | 抓包 | SSL Pinning |

拿到任何一个新 App，不要急着开干。先过一遍这张表：

1. 先抓包，看看请求长什么样，有没有签名参数
2. 用 jadx 打开，搜 `sign`、`encrypt`、`loadLibrary`
3. 确定加密在哪一层，然后针对性下手

这就是 App 逆向的基础地图。后续每个具体技术点，都可以落到这张地图上的某个坐标。
