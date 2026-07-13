# 第3章：静态分析——快速定位加密函数

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2026-07-09
> 归档日期: 2026-07-13
> 分类: mobile-app-reverse
>
> 很多新手打开jadx，面对几万个类和几十万行代码，完全不知道从哪里下手。翻半天源码，眼睛都看花了，也没找到sign是怎么生成的。

很多新手打开jadx，面对几万个类和几十万行代码，完全不知道从哪里下手。翻半天源码，眼睛都看花了，也没找到sign是怎么生成的。

这一章不讲jadx的基本操作（那个你自己摸索十分钟就会了），而是教你一套  ** 高效的搜索和定位方法论  **
。学完之后，你拿到一个陌生APK，能在15分钟内找到加密函数所在的位置。


##  一、建立你的关键词库

静态分析的第一步不是读代码，而是  ** 搜索  ** 。搜索的效率决定了逆向的速度。

###  1.1 核心关键词清单

以下是我整理的关键词库，按优先级排序：

优先级  |  关键词  |  说明  |  命中率
---|---|---|---
  |  ` sign  ` |  最常见的签名参数名  |  >90%
  |  ` encrypt  ` |  加密方法命名  |  >80%
  |  ` md5  ` |  MD5哈希  |  >70%
  |  ` aes  ` |  AES对称加密  |  >60%
  |  ` rsa  ` |  RSA非对称加密  |  >40%
  |  ` secret  ` |  密钥/秘密值  |  >50%
  |  ` token  ` |  令牌参数  |  >60%
  |  ` hmac  ` |  HMAC消息认证码  |  >30%
  |  ` sha  ` |  SHA系列哈希  |  >20%
  |  ` key  ` |  密钥变量  |  >40%（噪声大）
  |  ` base64  ` |  Base64编码（常被误认为加密）  |  >50%
  |  ` salt  ` |  盐值  |  >20%

** 搜索技巧：  **

  * 先搜最高优先级的关键词，缩小范围

  * 如果搜索结果太多，加限定条件：比如搜索  ` "sign"  ` 时排除  ` "signature"  ` （因为签名文件类名经常包含signature）

  * 搜索时注意大小写，jadx默认区分大小写，但很多App用驼峰命名（如  ` getSign  ` 、  ` encryptData  ` ）

###  1.2 进阶关键词（针对混淆代码）

当App使用了ProGuard或混淆器，类名和方法名会被改成a、b、c之类的短名。此时常规关键词失效，需要用  ** 特征搜索  ** ：

特征  |  搜索方式  |  说明
---|---|---
常量字符串  |  搜索  ` "sign="  ` 、  ` "token="  ` |  参数拼接时的固定字符串
异常日志  |  搜索  ` "encrypt error"  ` 、  ` "sign fail"  ` |  开发人员留下的调试信息
反射调用  |  搜索  ` Class.forName  ` 、  ` Method.invoke  ` |  混淆后常通过反射调用加密方法
Native方法  |  搜索  ` native  ` 关键字  |  加密逻辑在so层时会有native声明


##  二、调用链回溯：从网络请求出发

这是定位加密函数最核心的方法论。思路很简单：  ** 找到网络请求发出的地方，然后反向追踪参数来源。  **

###  2.1 定位网络请求入口

现代Android App几乎都用OkHttp。在jadx中搜索以下类名或方法名，可以快速找到网络请求的入口：

  *   *   *   *   *   *   *   *   *   *


    // 搜索类名 OkHttpClient Retrofit Volley
    // 搜索方法名 enqueue // 异步请求 execute // 同步请求 newCall // OkHttp构建请求 create // Retrofit创建Service


找到  ` OkHttpClient.newCall()  ` 或  ` enqueue()  ` 的调用处后，向上追溯，看  `
Request.Builder  ` 是如何构建的。

###  2.2 逆向追踪参数来源

假设你找到了这样的代码：

  *   *   *   *   *   *


    Request request = new Request.Builder()     .url(url)     .header("X-Sign", signValue)     .header("X-Timestamp", timestamp)     .post(body)     .build();


那么  ` signValue  ` 和  ` timestamp  ` 就是你的目标。现在向上追溯：

  1. 看  ` signValue  ` 来自哪里——可能是局部变量、成员变量、或者某个方法的返回值

  2. 如果是方法返回值，跳到那个方法内部

  3. 重复这个过程，直到找到最终的加密计算逻辑

** 实战案例：  **

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 第1层：网络请求 String signValue = SignUtils.getSign(params, timestamp); Request request = new Request.Builder()     .header("X-Sign", signValue)     ...     // 第2层：SignUtils.getSign public static String getSign(Map<String, String> params, long timestamp) {     String raw = buildRawString(params, timestamp);     return MD5Util.md5(raw + SECRET_KEY); } // 第3层：MD5Util.md5 public static String md5(String input) { // 实际MD5计算 ... }


这样三层追踪下来，你就找到了加密逻辑：  ` MD5(拼接参数 + 密钥)  ` 。

###  2.3 使用jadx的交叉引用功能

jadx提供了非常强大的交叉引用功能，可以帮助你快速跳转。

  * ** 查找调用者  ** ：选中一个方法或变量，右键 → Find Usage（或快捷键Ctrl+G）

  * ** 查看调用链  ** ：选中方法名，右键 → Show Call Graph

  * ** 跳转到定义  ** ：Ctrl+B 跳转到变量/方法的定义处

用好这三个功能，调用链回溯的效率能提升十倍。


##  三、混淆代码阅读技巧

当App开启了ProGuard或更高级的混淆器（如阿里Arsc、360加固），jadx反编译出来的代码会变得难以阅读。这里给出几种常见混淆模式的应对方法。

###  3.1 字符串加密

混淆器会把代码中的所有字符串常量加密成一段乱码，运行时再解密。你看到的代码可能是这样的：

  *   *   *   *


    String str = a.b.c("0x1234abcd"); if (str.equals(a.b.c("0x5678efgh"))) {       ... }


** 应对方法：  **

  * 在jadx中搜索  ` a.b.c  ` 这类解密方法，看它的实现逻辑

  * 用Frida Hook这个解密方法，打印出入参和返回值，就能得到原始字符串

  * 或者直接搜索  ` 0x1234abcd  ` ，看这个值在哪里被使用，从而推断原始含义

###  3.2 控制流平坦化

正常的代码是顺序执行的，但经过控制流平坦化后，代码变成一个大循环+switch-case的结构：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    while (true) {     switch (var) {         case 0:             // 原来的第一段逻辑             var = 2;             break;         case 1:             // 原来的第二段逻辑             var = 3;             break;         case 2:             // 原来的第三段逻辑             var = 1;             break;           ...     } }


** 应对方法：  **

  * 不要试图理解整个控制流，那是编译器做的事

  * 重点关注  ** 关键变量的赋值和返回值  ** 。比如找到  ` return  ` 语句，看返回值是怎么算出来的

  * 使用Frida动态Hook，直接打印输入输出，绕过控制流分析

  * 高级方案：使用deflat脚本（如  ` deflat.py  ` ）尝试还原原始控制流

###  3.3 字段名和方法名混淆

类名变成a、b、c，方法名变成a()、b()、c()。

** 应对方法：  **

  * 依赖  ** 方法签名  ** 而不是方法名来识别。比如  ` void a(String, int)  ` 和  ` String b(int)  ` 是不同的

  * 关注  ** 参数类型和返回值类型  ** 。加密方法通常接收String或byte[]，返回String或byte[]

  * 利用  ** 常量字符串  ** 作为锚点。即使方法名变了，里面引用的字符串常量不会变

###  3.4 反射与动态调用

混淆后的代码经常使用反射来调用方法，增加静态分析的难度：

  *   *   *


    Class clz = Class.forName("com.example.a"); Method method = clz.getDeclaredMethod("b", String.class); Object result = method.invoke(null, input);


** 应对方法：  **

  * 在jadx中搜索  ` Class.forName  ` 和  ` getDeclaredMethod  ` ，定位动态调用的位置

  * 使用Frida Hook  ` java.lang.reflect.Method.invoke  ` ，打印所有反射调用的详细信息

  * 结合动态调试，在运行时获取真实的类名和方法名


##  四、实战：从混淆后的APK中找到真实sign生成逻辑

现在我们用一个虚构但贴近真实的案例，把上面的方法串起来。

###  4.1 背景

目标App：某新闻客户端（已开启ProGuard混淆）

已知：登录接口需要POST参数  ` {"phone": "138xxxx", "password": "xxx"}  ` ，还有一个额外的Header参数
` X-Sign: 32位十六进制字符串  `

###  4.2 第一步：搜索关键词

在jadx中搜索  ` sign  ` ，结果太多（上千个）。改用更精确的搜索：搜索  ` "X-Sign"  ` （带引号表示搜索字符串常量）。

结果只有5处。逐一点击查看上下文，发现其中一个在  ` OkHttpClient  ` 的Builder中：

  *


    builder.addInterceptor(new a());


` a  ` 是一个混淆后的类名。双击进入。

###  4.3 第二步：分析Interceptor

看到如下代码（经过手动格式化）：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *


    public class a implements Interceptor {     public Response intercept(Chain chain) {         Request original = chain.request();         String body = bodyToString(original.body());         String sign = b.c(body); // 调用b类的c方法         Request modified = original.newBuilder()             .header("X-Sign", sign)             .build();         return chain.proceed(modified);     }     private String bodyToString(RequestBody body) {         // 将RequestBody转为字符串     } }

关键点：  ` sign = b.c(body)  ` 。  ` b  ` 是另一个混淆类，  ` c  ` 是它的方法。

###  4.4 第三步：追踪加密方法

跳转到  ` b.c  ` 方法：

  *   *   *   *   *   *   *


    public class b {     private static final String d = a.b.c("0xA1B2C3D4"); // 解密后的字符串     public static String c(String input) {          String raw = input + d; // 拼接密钥          return c.a(raw); // 调用c类的a方法     }  }


这里出现了两个新的混淆元素：

  * ` a.b.c("0xA1B2C3D4")  ` ：字符串解密调用

  * ` c.a(raw)  ` ：另一个加密方法

###  4.5 第四步：处理字符串加密

搜索  ` a.b.c  ` 方法，发现它是一个解密函数：

  *   *   *   *   *   *   *   *   *   *


    public class a {     public static String c(String hex) {         // 将十六进制字符串解码，然后进行异或运算         byte[] data = hexStringToBytes(hex);         for (int i = 0; i < data.length; i++) {             data[i] ^= 0x7F; // 异或密钥         }         return new String(data);     } }


手动计算或写个小脚本解密  ` "0xA1B2C3D4"  ` （异或0x7F），得到原始字符串：  ` "news_app_secret_2024"  `
。

###  4.6 第五步：追踪最终加密

跳转到  ` c.a  ` 方法：

  *   *   *   *   *   *   *   *   *   *   *


    public class c {    public static String a(String input) {        try {            MessageDigest md = MessageDigest.getInstance("MD5");            byte[] digest = md.digest(input.getBytes("UTF-8"));            return bytesToHex(digest);        } catch (Exception e) {            return "";        }    }}

至此，sign的生成逻辑完全清晰：

  *


    sign = MD5(请求体 + "news_app_secret_2024")


###  4.7 第六步：验证

用Python复现：

  *   *   *   *   *   *   *


    import hashlib
    body = '{"phone":"138xxxx","password":"xxx"}'secret = "news_app_secret_2024"raw = body + secretsign = hashlib.md5(raw.encode()).hexdigest()print(sign)  # 应与抓包得到的X-Sign一致


验证通过，逆向完成。


##  五、本章小结

静态分析的核心不是读代码，而是  ** 高效地找到关键代码  ** 。记住三个要点：

  1. ** 关键词搜索  ** ：建立自己的关键词库，从最高优先级开始搜

  2. ** 调用链回溯  ** ：从网络请求入口出发，反向追踪参数来源

  3. ** 混淆不可怕  ** ：字符串加密用Hook解，控制流平坦化只看输入输出，反射调用靠动态调试

掌握了这些，即使面对混淆严重的APK，你也能在半小时内找到加密函数。


##   风险提示

本文所述技术仅供学习和研究使用。未经授权逆向他人App可能违反相关法律法规及平台服务条款。请在法律允许的范围内开展技术实践。
