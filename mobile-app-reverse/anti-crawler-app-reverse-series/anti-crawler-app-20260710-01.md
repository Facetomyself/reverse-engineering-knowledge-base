# 第4章：Frida高级Hook——不止于打印参数

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2026-07-10
> 归档日期: 2026-07-13
> 分类: mobile-app-reverse
>
> 很多人学Frida停留在hook一个方法然后console.log参数的水平。这在对付简单App时够用，一旦遇到混淆、加固、native层加密，立刻抓瞎。

很多人学Frida停留在hook一个方法然后console.log参数的水平。这在对付简单App时够用，一旦遇到混淆、加固、native层加密，立刻抓瞎。

这一章不讲Frida安装和Hello
World（那些你自己搜一下就有），而是直接给你五个在生产环境中高频使用的进阶技巧。每一个技巧都对应一种真实场景，学完你就能处理市面上80%以上的逆向需求。

## 一、Hook构造函数获取对象实例

场景

你定位到一个加密类Encryptor，它的加密方法encrypt(String)是非静态的，需要先有一个Encryptor对象才能调用。但你不知道这个对象在哪里创建的，也没办法直接调用静态方法。

解法

Hook构造函数，在对象创建时捕获实例，存到全局变量里供后续使用。


  *   *   *   *   *   *   *   *   *   *   *   *


    var EncryptorCls = Java.use('com.example.Encryptor');
    var instance = null;
    EncryptorCls.$init.overload('java.lang.String', 'int').implementation = function(str, num) {    console.log('[+] Encryptor constructor called with:', str, num);    // 调用原构造函数    this.$init(str, num);    // 保存实例    instance = this;    console.log('[+] Saved Encryptor instance:', this);};

之后在其他Hook中就可以直接使用instance调用方法：


  *   *   *   *


    if (instance) {    var result = instance.encrypt('hello');    console.log('[+] encrypt result:', result);}

踩坑提醒

• 如果构造函数有多个重载，需要分别overload指定参数类型

• 对象可能在子线程中创建，instance可能被覆盖，建议用数组或Map存储多个实例

• 如果构造函数内部调用了其他方法，可以在this.$init()前后打印调用栈

## 二、替换方法实现绕过校验

场景

App在请求前会检查设备是否Root、是否在模拟器中运行，如果检测到就拒绝请求。你想绕过这个检测。

解法

直接替换检测方法的实现，让它永远返回“安全”的值。


  *   *   *   *   *   *   *   *   *   *   *   *


    // 假设检测方法返回boolean，true表示检测到风险var DetectorCls = Java.use('com.example.SecurityDetector');
    DetectorCls.isRooted.implementation = function() {    console.log('[+] isRooted called, returning false');    return false;};
    DetectorCls.isEmulator.implementation = function() {    console.log('[+] isEmulator called, returning false');    return false;};

进阶：替换整个方法体

有时候你需要完全重写一个方法的行为，而不是简单地改返回值。例如，App在加密前会拼接一个固定的盐值，你想把这个盐值改成自己的。


  *   *   *   *   *   *   *   *   *   *


    var SignUtilCls = Java.use('com.example.SignUtil');
    SignUtilCls.generateSign.implementation = function(params) {    console.log('[+] generateSign called with params:', params);    // 调用原方法拿到原始签名    var originalSign = this.generateSign(params);    console.log('[+] Original sign:', originalSign);    // 你也可以直接返回自己计算的签名    return originalSign;};

踩坑提醒

•
替换实现后，原方法逻辑完全丢失。如果你只是想观察而不改变行为，应该在implementation内部调用原方法（this.methodName(args)）

• 注意overload的使用：如果方法有多个重载，必须指定参数类型

• 替换后如果App崩溃，检查是否漏掉了某些必要的初始化步骤

## 三、主动调用：$new 和 $dispose

场景

你想在不触发App原有逻辑的情况下，主动调用某个对象的加密方法，传入自己构造的参数，拿到加密结果。或者你想构造一个对象实例，用来测试。

解法

使用Frida的$new创建一个对象实例，然后调用它的方法。用完记得$dispose释放内存。


  *   *   *   *   *   *   *   *   *   *   *


    var EncryptorCls = Java.use('com.example.Encryptor');// 创建对象实例（调用无参构造函数）var enc = EncryptorCls.$new();// 或者调用带参数的构造函数var encWithParams = EncryptorCls.$new('key_string', 128);// 主动调用加密方法var ciphertext = enc.encrypt('plaintext_data');console.log('[+] Encrypted:', ciphertext);// 使用完毕后释放enc.$dispose();encWithParams.$dispose();

进阶：调用静态方法

如果方法是静态的，直接通过类名调用即可，不需要创建实例：

  *   *   *


    var SignUtilCls = Java.use('com.example.SignUtil');var sign = SignUtilCls.signStatic('param1', 'param2');console.log('[+] Static sign:', sign);

踩坑提醒

•
有些类的构造函数可能需要传入Context或其他系统对象，此时需要先获取这些对象（比如通过Java.use('android.app.ActivityThread').currentApplication().getApplicationContext()）

• 主动调用可能触发副作用（比如写入数据库、发送网络请求），注意隔离

• $dispose不是必须的，但如果大量创建对象不释放，可能导致内存泄漏

## 四、Hook Native层：Interceptor.attach + Process.findModuleByName

场景

加密逻辑不在Java层，而是在so文件的C/C++函数里。你想Hook这个native函数，打印它的参数和返回值。

解法

先找到so模块基址，再用Interceptor.attach挂钩导出函数或偏移地址。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 1. 找到目标so模块var module = Process.findModuleByName('libnative-encrypt.so');console.log('[+] Module base:', module.base);
    // 2. 获取导出函数地址（假设函数名为 Java_com_example_NativeBridge_encrypt）var encryptPtr = module.findExportByName('Java_com_example_NativeBridge_encrypt');console.log('[+] encrypt address:', encryptPtr);
    // 3. Hook该函数Interceptor.attach(encryptPtr, {    onEnter: function(args) {        console.log('[+] Native encrypt called');        // 参数通常是JNIEnv*, jobject, jstring等        // args[0] = JNIEnv*, args[1] = thiz, args[2] = input string        if (args[2]) {            var input = Memory.readCString(Java.vm.getEnv().getStringUtfChars(args[2], null));            console.log('[+] Input:', input);        }    },    onLeave: function(retval) {        // retval是返回值（jstring）        if (retval) {            var output = Memory.readCString(Java.vm.getEnv().getStringUtfChars(retval, null));            console.log('[+] Output:', output);        }    }});

进阶：Hook未导出函数（通过偏移）

如果函数没有被导出（比如被strip掉了），你可以通过模块基址+偏移来Hook：


  *   *   *   *   *   *   *   *   *   *   *   *


    var offset = 0x1234; // 从IDA或Ghidra中查到的偏移var funcAddr = module.base.add(offset);
    Interceptor.attach(funcAddr, {    onEnter: function(args) {        console.log('[+] Hooked unexported function at offset 0x1234');        // 读取参数...    },    onLeave: function(retval) {        // 处理返回值...    }});

踩坑提醒

• 必须在so加载之后才能Hook。可以在Java.perform中延迟执行，或者Hook dlopen在加载时触发

• 参数类型处理：JNI函数参数需要根据JNI规范解析，建议先用args[0].toInt32()等方式试探

• 如果函数被OLLVM混淆，Hook点可能不准，建议先用Frida Stalker跟踪确认

## 五、Frida Stalker：跟踪指令执行

场景

某个native函数被严重混淆（控制流平坦化），静态分析完全看不懂。你想知道它实际执行了哪些指令，特别是加密循环和关键比较。

解法

使用Stalker对目标线程进行指令级跟踪，记录所有执行的指令地址和汇编。


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    // 1. 获取目标线程ID（通常是主线程）var targetThreadId = Process.getCurrentThreadId();
    // 2. 启动Stalkervar stalker = Stalker.follow(targetThreadId, {    events: {        call: true,     // 跟踪call指令        ret: false,     // 跟踪ret指令        exec: false     // 跟踪所有指令（慎用，数据量极大）    },    transform: function(iterator) {        var instruction = iterator.next();        do {            // 可以在这里过滤感兴趣的指令            if (instruction.mnemonic === 'bl' || instruction.mnemonic === 'b') {                // 记录分支指令                console.log('[+] Branch at:', instruction.address, instruction.toString());            }            iterator.keep(); // 保持该指令        } while ((instruction = iterator.next()) !== null);    }});
    // 3. 一段时间后停止跟踪setTimeout(function() {    Stalker.unfollow(targetThreadId);    console.log('[+] Stalker stopped');}, 5000);

更实用的场景：跟踪特定函数范围内的指令

通常我们只关心某个函数内部的执行流，可以使用Stalker.follow配合transform过滤地址范围：


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    var module = Process.findModuleByName('libtarget.so');var startAddr = module.base.add(0x1000); // 函数起始偏移var endAddr = module.base.add(0x2000);   // 函数结束偏移
    Stalker.follow(Process.getCurrentThreadId(), {    transform: function(iterator) {        var instruction = iterator.next();        do {            if (instruction.address >= startAddr && instruction.address <= endAddr) {                console.log('[+] Exec:', instruction.address, instruction.toString());            }            iterator.keep();        } while ((instruction = iterator.next()) !== null);    }});

踩坑提醒

• Stalker会产生海量日志，建议只跟踪小范围（单个函数）或短时间内

• 不要在UI线程长时间使用Stalker，会导致App卡死

• Stalker在ARM64上表现较好，ARM32可能有兼容性问题

##  本章小结

五个技巧对应五种常见困境：

困境  |  技巧
---|---
需要对象实例但找不到  |  Hook构造函数
需要绕过检测逻辑  |  替换方法实现
需要主动测试加密  |  主动调用  ` $new  `
加密在so层  |  Interceptor.attach
混淆严重看不清逻辑  |  Stalker指令跟踪

实战案例展示了如何将这些技巧组合使用：Hook构造函数获取密钥对象 → 替换公钥 → 主动调用加密 → 最终在Python中解密。

 风险提示

本章涉及的动态Hook技术仅可用于自己拥有权限的设备或已获得授权的安全测试。未经授权替换他人App的加密逻辑属于违法行为，请严格遵守法律法规。
