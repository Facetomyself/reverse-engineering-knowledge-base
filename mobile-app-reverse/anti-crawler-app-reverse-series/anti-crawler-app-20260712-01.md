# 第6章：So层逆向——从汇编到Python

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2026-07-12
> 归档日期: 2026-07-13
> 分类: mobile-app-reverse
>
> 当加密逻辑从Java层下沉到So层，很多人的逆向之路就戛然而止了。但实际上，So层逆向并没有想象中那么可怕。这一章 跳过IDA的基础操作 （你自己摸索半小时就能上手），直接给你四个 生产级的关键技能 ：定位JNI函数、Hook native参数、识别加密库、对抗OLLVM混淆。最后用一个完整的游戏App案例，展示如何从So中还原签名算法并用Python复现。

当加密逻辑从Java层下沉到So层，很多人的逆向之路就戛然而止了。但实际上，So层逆向并没有想象中那么可怕。这一章  ** 跳过IDA的基础操作  **
（你自己摸索半小时就能上手），直接给你四个  ** 生产级的关键技能  ** ：定位JNI函数、Hook
native参数、识别加密库、对抗OLLVM混淆。最后用一个完整的游戏App案例，展示如何从So中还原签名算法并用Python复现。


##  一、如何找到JNI函数映射表：Hook RegisterNatives


###  场景


App使用  ` System.loadLibrary("native-lib")  ` 加载So，然后通过  ` native  `
方法调用。但在So中，JNI函数的命名并非一定是标准的  ` Java_com_example_xxx_method  ` ，而是通过  `
RegisterNatives  ` 动态注册。你不知道So里到底注册了哪些Java方法，也不知道它们的函数指针。

###  解法


Hook  ` JNI_RegisterNatives  ` 函数，拦截动态注册过程，打印出所有注册的Java方法名、签名和对应的Native函数地址。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // frida脚本：hook RegisterNativesvar RegisterNatives_addr = Module.findExportByName("libart.so", "_ZN3art3JNI15RegisterNativesEP7_JNIEnvP7_jclassPK15JNINativeMethodi");// 如果上述符号找不到，可以尝试 libnativehelper.so 或直接搜索模式if (RegisterNatives_addr == null) {    RegisterNatives_addr = Module.findExportByName("libnativehelper.so", "jniRegisterNativeMethods");}if (RegisterNatives_addr) {    Interceptor.attach(RegisterNatives_addr, {        onEnter: function(args) {            var env = args[0];            var clazz = args[1];            var methods = ptr(args[2]);            var numMethods = args[3].toInt32();            // 获取类名            var GetClassName = new NativeFunction(env.add(ptr(0x18)), 'pointer', ['pointer', 'pointer']);            var class_name_ptr = GetClassName(env, clazz);            var class_name = Memory.readCString(class_name_ptr);            console.log("[RegisterNatives] class: " + class_name);            // 遍历每个方法            for (var i = 0; i < numMethods; i++) {                var method_offset = methods.add(i * 12); // JNINativeMethod 结构体大小（name, signature, fnPtr）                var name_ptr = Memory.readPointer(method_offset);                var sig_ptr = Memory.readPointer(method_offset.add(4));                var fnPtr = Memory.readPointer(method_offset.add(8));                var name = Memory.readCString(name_ptr);                var sig = Memory.readCString(sig_ptr);                console.log("\t[" + i + "] " + name + " " + sig + " -> " + fnPtr);            }        }    });} else {    console.log("[-] Cannot find RegisterNatives");}


** 输出示例：  **

  *   *   *


    [RegisterNatives] class: com/example/game/NativeBridge	[0] init (Ljava/lang/String;)V -> 0x7a3e4c00	[1] getSign (Ljava/lang/String;J)Ljava/lang/String; -> 0x7a3e5100


这样你就拿到了所有动态注册的native方法及其地址，可以直接用这些地址进行后续Hook。

###  踩坑提醒

  * 不同Android版本的  ` libart.so  ` 中  ` RegisterNatives  ` 符号名不同，建议使用  ` Module.enumerateExports("libart.so")  ` 先扫描一遍

  * 如果So是加固的，可能在运行时才加载，需要延迟Hook或Hook  ` dlopen  `

  * 有些So使用  ` JNI_OnLoad  ` 中注册，可以先Hook  ` JNI_OnLoad  `

`
`


##  二、用Frida打印native函数参数和返回值


###  场景

你已经知道了native函数的地址（通过上面RegisterNatives或通过  ` findExportByName  `
），但不知道参数的含义。你需要打印每次调用时的参数值和返回值。

###  解法

使用  ` Interceptor.attach  ` ，在  ` onEnter  ` 中打印参数，在  ` onLeave  ` 中打印返回值。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    var nativeFunc = Module.findExportByName("libgame.so", "Java_com_example_game_NativeBridge_getSign");// 或者用上面获取到的地址// var nativeFunc = ptr(0x7a3e5100);Interceptor.attach(nativeFunc, {    onEnter: function(args) {        console.log("[+] getSign called");        // JNI函数参数约定：args[0]=JNIEnv*, args[1]=jclass/jobject, args[2..n]=实际参数        var env = args[0];        var thiz = args[1];        // 打印参数（根据方法签名）        // 假设签名是 (Ljava/lang/String;J)Ljava/lang/String;        // args[2] 是 jstring (input), args[3] 是 jlong (timestamp)        if (args[2] != null) {            var input = Java.vm.getEnv().getStringUtfChars(args[2], null).readCString();            console.log("\tInput string: " + input);        }        console.log("\tTimestamp: " + args[3].toInt32()); // jlong 是64位，toInt32()可能截断，用toUInt64()    },    onLeave: function(retval) {        // 返回值是 jstring        if (retval != null) {            var result = Java.vm.getEnv().getStringUtfChars(retval, null).readCString();            console.log("\tReturn value: " + result);        }    }});


###  处理不同类型的参数

JNI类型  |  Frida读取方式
---|---
jstring  |  ` Java.vm.getEnv().getStringUtfChars(args[N], null).readCString()  `
jbyteArray  |  ` Java.vm.getEnv().getByteArrayElements(args[N], null)  ` 返回指针
jint  |  ` args[N].toInt32()  `
jlong  |  ` args[N].toUInt64()  `
jboolean  |  ` args[N].toInt32() == 1  `
指针/结构体  |  ` Memory.readByteArray(args[N], size)  `

###  踩坑提醒

  * ` getStringUtfChars  ` 返回的指针需要及时释放，否则内存泄漏，但短期调试无所谓

  * 如果函数参数中有  ` jobject  ` （非String），需要根据实际类型调用相应JNI函数读取

  * 对于大型数组，建议只打印前几个字节


##  三、识别常见加密库的符号


###  场景

你在So中看到了很多函数，但不知道哪些是加密函数。如果能识别出OpenSSL、mbedTLS、Crypto++等加密库的符号，就能快速定位加密入口。

###  常见加密库特征

库  |  典型导出符号  |  特征
---|---|---
OpenSSL  |  ` EVP_EncryptInit_ex  ` ,  ` EVP_DecryptFinal_ex  ` ,  ` HMAC_CTX_new  ` ,  ` RSA_public_encrypt  ` |  函数名以  ` EVP_  ` 、  ` HMAC_  ` 、  ` RSA_  ` 开头
mbedTLS  |  ` mbedtls_aes_init  ` ,  ` mbedtls_sha256_starts_ret  ` |  函数名以  ` mbedtls_  ` 开头
Crypto++  |  ` CryptoPP::AES::Encrypt  ` ,  ` CryptoPP::SHA256::CalculateDigest  ` |  C++命名空间，IDA中可见
BoringSSL  |  ` CRYPTO_gcm128_encrypt  ` ,  ` ECDSA_sign  ` |  Google自家，符号类似OpenSSL但略有不同

###  快速识别方法

  1. ** IDA Strings窗口  ** ：搜索  ` OpenSSL  ` 、  ` mbedtls  ` 、  ` CryptoPP  ` 等关键词

  2. ** 导出表查看  ** ：用  ` Module.enumerateExports()  ` 列出所有导出函数

  3. ** 特征字节匹配  ** ：OpenSSL的  ` EVP_EncryptInit_ex  ` 通常有一段固定prologue

  *   *   *   *   *   *   *   *   *   *


    // 用Frida枚举so的所有导出函数，筛选可能的加密函数var module = Process.findModuleByName("libgame.so");module.enumerateExports().forEach(function(exp) {    if (exp.name.indexOf("EVP_") !== -1 ||        exp.name.indexOf("HMAC") !== -1 ||        exp.name.indexOf("RSA_") !== -1 ||        exp.name.indexOf("mbedtls_") !== -1) {        console.log(exp.name + " @ " + exp.address);    }});


###  如果符号被strip了怎么办？

  * 使用  ** 特征码搜索  ** ：比如OpenSSL的  ` EVP_EncryptInit_ex  ` 函数开头通常是  ` push rbp; mov rbp, rsp; ...  ` ，可以用Frida的  ` Memory.scan  ` 搜索特征字节

  * 动态跟踪：Hook  ` malloc  ` 或  ` memcpy  ` ，观察加密过程中分配的内存和拷贝的数据


##  四、遇到OLLVM混淆怎么办？——去混淆思路


###  OLLVM做了什么

OLLVM（Obfuscator-LLVM）会对控制流进行  ** 控制流平坦化  ** （CFG
Flattening），将一个函数变成一个大循环+switch-case结构，代码无法直接阅读。

###  去混淆的核心思路：Trace + 等价变换

####  方法一：Frida Trace（最实用）

利用Frida Stalker跟踪函数执行，记录实际走过的指令序列，然后重构出简化后的控制流。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    var module = Process.findModuleByName("libgame.so");var funcStart = module.base.add(0x1234); // 目标函数偏移var funcEnd = module.base.add(0x5678);Stalker.follow(Process.getCurrentThreadId(), {    transform: function(iterator) {        var instruction = iterator.next();        do {            if (instruction.address >= funcStart && instruction.address <= funcEnd) {                console.log(instruction.address + ": " + instruction.toString());            }            iterator.keep();        } while ((instruction = iterator.next()) !== null);    }});// 5秒后停止setTimeout(function() {    Stalker.unfollow();}, 3000);


** 分析trace日志  ** ：你会发现虽然代码有很多分支，但实际执行的路径是有限的。将多次trace合并，可以得到函数实际的控制流图。

####  方法二：符号执行（自动化）

使用工具如  ** Unicorn  ** \+  ** angr  ** 或  ** deflat.py  **
（一个专门针对OLLVM平坦化的去混淆脚本）。deflat.py的原理是：通过符号执行找出每个block之间的真实跳转关系，然后移除分发器。

** deflat.py使用步骤：  **

  1. 用IDA找到目标函数，记录起始地址和结束地址

  2. 导出函数的汇编代码

  3. 运行deflat.py：  ` python deflat.py target_file 0x1234 0x5678  `

  4. 输出还原后的函数

####  方法三：等效替换（手工）

对于OLLVM，你不需要理解整个控制流，只需要关注  ** 关键变量的赋值和返回值  ** 。比如：

  *   *   *   *   *   *   *   *   *


    // 混淆后的伪代码while (state) {    switch(state) {        case 0: a = input[0]; state = 2; break;        case 1: result = a ^ 0x7F; state = 3; break;        case 2: b = a + 5; state = 1; break;        case 3: return result;    }}


实际上等价于：

  *   *   *   *


    a = input[0];b = a + 5;result = a ^ 0x7F;return result;


** 做法  ** ：在trace中找出所有对结果有贡献的指令，忽略分发器。


##  五、实战：某游戏App的登录签名算法藏在libgame.so中

###  背景

一款手机网游，登录时需要提交  ` sign  ` 参数。Java层调用  ` NativeBridge.getSign(userId,
timestamp)  ` ，返回值即为sign。

###  步骤

####  1\. Hook RegisterNatives 定位函数

运行前面提供的RegisterNatives Hook脚本，得到：

  *   *


    [RegisterNatives] class: com/example/game/NativeBridge	[0] getSign (Ljava/lang/String;J)Ljava/lang/String; -> 0x7a3e5100


####  2\. 打印参数和返回值

使用第二节的脚本，发现：

  * 输入：  ` userId=123456&timestamp=1700000000  `

  * 输出：  ` a1b2c3d4e5f6789012345678abcdef01  `

####  3\. 定位加密逻辑

由于函数是动态注册的，我们直接在IDA中跳转到  ` 0x7a3e5100  ` （基址+偏移）。发现函数很大，且有明显的OLLVM控制流平坦化特征（大量
` switch  ` 和  ` mov  ` 指令）。

####  4\. Hook strlen 定位输入

我们不知道输入字符串是如何被处理的。一个通用的技巧是  ** Hook  ` strlen  ` ** ，因为几乎所有字符串操作都会先调用  `
strlen  ` 获取长度。

  *   *   *   *   *   *   *   *   *   *   *   *


    var strlenPtr = Module.findExportByName("libc.so", "strlen");Interceptor.attach(strlenPtr, {    onEnter: function(args) {        var str = Memory.readCString(args[0]);        // 过滤掉无关的字符串（只关注包含userId的）        if (str.indexOf("userId") !== -1) {            console.log("[strlen] Input string: " + str);            // 打印调用栈            console.log(Thread.backtrace(this.context, Backtracer.ACCURATE).map(DebugSymbol.fromAddress).join('\n'));        }    }});


运行后，发现  ` strlen  ` 被调用时传入的字符串正是  ` userId=123456&timestamp=1700000000  `
，并且调用栈指向了  ` libgame.so  ` 中的某个地址。这说明签名算法直接对这个拼接字符串进行了处理。

####  5\. 进一步Hook memcpy/memcmp

继续Hook  ` memcpy  ` 和  ` memcmp  ` ，观察数据流动：

  *   *   *   *   *   *   *   *   *   *   *   *   *


    var memcpyPtr = Module.findExportByName("libc.so", "memcpy");Interceptor.attach(memcpyPtr, {    onEnter: function(args) {        var dest = args[0];        var src = args[1];        var len = args[2].toInt32();        if (len > 0 && len < 1024) {            var data = Memory.readByteArray(src, len);            console.log("[memcpy] from " + src + " to " + dest + " len=" + len);            console.log(hexdump(data, {offset: 0, length: len, header: false, ansi: false}));        }    }});


通过分析memcpy的源数据，我们发现了一段固定字节：  ` 0x6b6579736563726574  `
（ASCII："keysecret"）。这很可能就是HMAC的密钥。

####  6\. 还原算法

综合以上信息，签名算法推测为：

  *


    sign = HMAC-SHA256(key="keysecret", message=userId + "&" + timestamp)


用Python验证：

  *   *   *   *   *   *


    import hmacimport hashlibkey = b"keysecret"msg = "userId=123456&timestamp=1700000000".encode()sign = hmac.new(key, msg, hashlib.sha256).hexdigest()print(sign)


输出与App生成的sign一致，还原成功。

####  7\. 最终Python脚本

  *   *   *   *   *   *   *   *   *   *   *   *


    import hmacimport hashlibimport timedef get_sign(user_id):    ts = int(time.time() * 1000)  # 注意单位    msg = f"userId={user_id}&timestamp={ts}"    key = b"keysecret"    sign = hmac.new(key, msg.encode(), hashlib.sha256).hexdigest()    return sign, ts# 测试sign, ts = get_sign("test_user")print(f"sign={sign}, ts={ts}")


###  踩坑提醒

  * 密钥可能不是简单的字符串，而是经过Base64解码或异或处理

  * 时间戳单位可能是秒或毫秒，需要从抓包中确认

  * 有些App会对拼接顺序做字典序排列，需要仔细分析


##  六、本章小结

技能  |  适用场景  |  关键工具
---|---|---
Hook RegisterNatives  |  动态注册的native方法  |  Frida + libart
打印native参数  |  分析函数输入输出  |  Interceptor.attach
识别加密库  |  快速定位加密入口  |  导出表枚举
OLLVM去混淆  |  控制流平坦化  |  Stalker trace / deflat.py
Hook strlen/memcpy  |  追踪数据流  |  通用字符串Hook

So层逆向的核心不是读懂每一行汇编，而是  ** 找到输入和输出的关系  ** ，然后用标准库复现。


##   风险提示

So层逆向涉及对二进制代码的分析，请仅在法律允许的范围内进行。未经授权逆向商业游戏的安全保护机制，可能违反《著作权法》及《计算机软件保护条例》。
