# 第5章：常见加密算法的精确还原

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2026-07-11
> 归档日期: 2026-07-13
> 分类: mobile-app-reverse
>
> 识别出加密算法只是第一步，真正的难点在于 用Python精确复现 。很多人在jadx里看到了 AES/CBC/PKCS5Padding ，但Key和IV藏在so层；或者看到 RSA/ECB/PKCS1Padding ，却分不清公钥加密和私钥签名。这一章不讲理论，直接给 从内存中提取密钥、用Python还原 的生产级方案。

#  识别出加密算法只是第一步，真正的难点在于  ** 用Python精确复现  ** 。很多人在jadx里看到了  `
AES/CBC/PKCS5Padding  ` ，但Key和IV藏在so层；或者看到  ` RSA/ECB/PKCS1Padding  `
，却分不清公钥加密和私钥签名。这一章不讲理论，直接给  ** 从内存中提取密钥、用Python还原  ** 的生产级方案。


##  一、AES-CBC/PKCS7：从内存中dump出Key和IV


###  场景

你在jadx中定位到加密方法：

  *   *


    Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");cipher.init(Cipher.ENCRYPT_MODE, secretKeySpec, ivParameterSpec);

` secretKeySpec  ` 和  ` ivParameterSpec  `
是从某个地方构造的，但源码里看不到具体值。你需要从运行时内存中把它们捞出来。

###  解法：Hook  ` IvParameterSpec  ` 和  ` SecretKeySpec  ` 构造函数

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    Java.perform(function() {    var SecretKeySpec = Java.use('javax.crypto.spec.SecretKeySpec');    var IvParameterSpec = Java.use('javax.crypto.spec.IvParameterSpec');
        SecretKeySpec.$init.overload('[B', 'java.lang.String').implementation = function(keyBytes, algorithm) {        console.log('[+] SecretKeySpec created');        console.log('[+] Algorithm:', algorithm);        console.log('[+] Key (hex):', bytesToHex(keyBytes));        this.$init(keyBytes, algorithm);    };
        IvParameterSpec.$init.overload('[B').implementation = function(ivBytes) {        console.log('[+] IvParameterSpec created');        console.log('[+] IV (hex):', bytesToHex(ivBytes));        this.$init(ivBytes);    };});
    function bytesToHex(bytes) {    var hex = '';    for (var i = 0; i < bytes.length; i++) {        hex += ('0' + (bytes[i] & 0xFF).toString(16)).slice(-2);    }    return hex;}


如果Key/IV是通过字符串转换而来，还可以Hook  ` String.getBytes()  ` 或  ` Base64.decode()  ` 。

###  Python复现

  *   *   *   *   *   *   *   *   *   *   *   *


    from Crypto.Cipher import AESimport base64
    key = bytes.fromhex('你的32位hex密钥')iv = bytes.fromhex('你的32位hexIV')cipher = AES.new(key, AES.MODE_CBC, iv)
    # 解密decrypted = cipher.decrypt(base64.b64decode(ciphertext_b64))# 去除PKCS7填充pad_len = decrypted[-1]plaintext = decrypted[:-pad_len].decode('utf-8')


###  踩坑提醒

  * PKCS5和PKCS7在AES中实际上是一样的，Python的  ` Crypto.Cipher.AES  ` 默认PKCS7

  * 如果解密出来是乱码，检查Key/IV是否正确、加密模式是否为CBC、是否有额外填充

  * 有些App会用  ` SecretKeySpec  ` 的第二个参数指定算法（如"AES"），但Key长度必须是16/24/32字节


##  二、RSA：区分公钥加密与私钥签名，提取模数N和指数E


###  场景

App用RSA加密密码，但代码里既有  ` Cipher.ENCRYPT_MODE  ` 又有  ` Signature.sign  `
。你需要区分哪个是加密、哪个是签名，并提取公钥的模数N和指数E。

###  区分方法

操作  |  类  |  模式  |  用途
---|---|---|---
公钥加密  |  ` Cipher  ` |  ` ENCRYPT_MODE  ` |  加密数据，私钥解密
私钥签名  |  ` Signature  ` |  ` SIGN  ` |  签名数据，公钥验签
私钥解密  |  ` Cipher  ` |  ` DECRYPT_MODE  ` |  解密数据（少见，除非App有私钥）
公钥验签  |  ` Signature  ` |  ` VERIFY  ` |  验证签名

通常App只会持有公钥，所以加密和验签用的是公钥；私钥在服务器端。

###  提取公钥模数和指数

Hook  ` KeyFactory.generatePublic  ` 或直接Hook  ` X509EncodedKeySpec  ` ：

  *   *   *   *   *   *   *   *   *   *


    Java.perform(function() {    var X509EncodedKeySpec = Java.use('java.security.spec.X509EncodedKeySpec');    X509EncodedKeySpec.$init.overload('[B').implementation = function(encoded) {        console.log('[+] X509EncodedKeySpec created');        console.log('[+] Encoded key bytes:', bytesToHex(encoded));        // 解析DER编码的SubjectPublicKeyInfo        // 可以用Python解析，也可以直接打印后离线处理        this.$init(encoded);    };});

得到hex后，用Python解析：

  *   *   *   *   *   *   *


    from Crypto.PublicKey import RSAimport binascii
    der_bytes = binascii.unhexlify('你的hex字符串')key = RSA.import_key(der_bytes)print('N:', hex(key.n))print('E:', key.e)

###  用公钥加密（Python复现）

  *   *   *   *   *   *   *   *


    from Crypto.PublicKey import RSAfrom Crypto.Cipher import PKCS1_v1_5import base64
    pub_key = RSA.import_key(open('public.pem').read())cipher = PKCS1_v1_5.new(pub_key)encrypted = cipher.encrypt(b'plaintext')print(base64.b64encode(encrypted).decode())


###  踩坑提醒

  * RSA加密有长度限制（密钥长度/8 - 11，2048位最多加密245字节）

  * 填充方式：PKCS1_v1_5最常见，也可能是OAEP（需要指定hash）

  * 如果App用的是私钥签名，你需要提取私钥（通常不可能，除非App本地存了私钥）


##  三、HMAC-SHA256：找盐值（salt）的来源


###  场景


请求头有个  ` X-Sign  ` ，看起来像是  ` HMAC-SHA256(参数, 盐值)  `
的结果。盐值可能是硬编码字符串、时间戳、随机数，或者从服务器获取。

###  定位盐值的方法

  1. ** 搜索字符串  ** ：在jadx中搜索  ` salt  ` 、  ` secret  ` 、  ` key  ` 等关键词

  2. ** Hook Mac类  ** ：HMAC在Java中通过  ` Mac.getInstance("HmacSHA256")  ` 实现

     *      *      *      *      *      *      *      *      *      *      *      *      *      *      *      *     Java.perform(function() {    var Mac = Java.use('javax.crypto.Mac');    Mac.init.overload('java.security.Key').implementation = function(key) {        console.log('[+] Mac.init called');        // 打印密钥（SecretKeySpec）        var encoded = key.getEncoded();        console.log('[+] HMAC key (hex):', bytesToHex(encoded));        this.init(key);    };    Mac.doFinal.overload('[B').implementation = function(input) {        console.log('[+] Mac.doFinal input:', bytesToHex(input));        var result = this.doFinal(input);        console.log('[+] Result:', bytesToHex(result));        return result;    };});


###  盐值来源分类

来源  |  特征  |  提取方法
---|---|---
硬编码  |  固定字符串，多次请求不变  |  直接Hook Mac.init拿到密钥
时间戳  |  密钥中包含当前时间戳  |  Hook  ` System.currentTimeMillis()  ` 看是否参与
随机数  |  每次请求不同  |  可能是UUID或SecureRandom生成
服务器下发  |  登录接口返回的token  |  需要先模拟登录

###  Python复现

  *   *   *   *   *   *   *


    import hmacimport hashlib
    key = bytes.fromhex('你的密钥hex')message = '参数拼接字符串'.encode('utf-8')sign = hmac.new(key, message, hashlib.sha256).hexdigest()print(sign)

###  踩坑提醒

  * 有些App会对密钥先做一次MD5或Base64解码，注意观察

  * 参数拼接顺序很重要，通常按字典序或固定顺序拼接

  * 如果盐值包含时间戳，注意时间戳的单位（秒/毫秒）和格式


##  四、国密SM2/SM3/SM4：识别特征并调用开源库


###  场景

国内App越来越多使用国密算法。你需要识别它们并找到合适的Python库。

###  识别特征

算法  |  常见类名/方法名  |  特征
---|---|---
SM2  |  ` SM2Engine  ` 、  ` SM2KeyPairGenerator  ` |  椭圆曲线公钥加密，输出通常为C1C2C3格式
SM3  |  ` SM3Digest  ` 、  ` sm3_hash  ` |  输出256位（32字节）哈希，类似SHA256但不同
SM4  |  ` SM4Engine  ` 、  ` SM4_Encrypt  ` |  对称加密，分组128位，密钥128位

###  Hook定位

搜索  ` SM2  ` 、  ` SM3  ` 、  ` SM4  ` 、  ` sm2_encrypt  `
等关键词。如果App使用了BouncyCastle，类名通常是  ` org.bouncycastle.crypto.engines.SM2Engine
` 。

###  Python复现

国密Python库推荐使用  ` gmssl  ` 或  ` pysmx  ` 。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    # SM3哈希from gmssl import sm3hash_value = sm3.sm3_hash(list('待哈希字符串'.encode('utf-8')))print(hash_value.hex())
    # SM4加密（ECB模式）from gmssl.sm4 import CryptSM4, SM4_ENCRYPTcipher = CryptSM4()cipher.set_key(b'16字节密钥', SM4_ENCRYPT)encrypted = cipher.crypt_ecb(b'16字节明文数据块')print(encrypted.hex())
    # SM2加密from gmssl import sm2private_key = '...'  # 16进制私钥public_key = '...'   # 04开头公钥sm2_crypt = sm2.CryptSM2(public_key=public_key, private_key=private_key)enc_data = sm2_crypt.encrypt(b'待加密数据')print(enc_data.hex())

###  踩坑提醒

  * 国密SM2的密文格式有C1C2C3和C1C3C2两种，注意区分

  * SM4的填充方式可能是PKCS7或ZeroPadding，需要观察

  * 有些App对国密算法做了魔改，不能直接用标准库，需要对照源码调整


##  五、实战：某版本短视频App的请求头X-Gorgon算法还原


###  背景

某短视频App的每个请求都必须带上  ` X-Gorgon  `
参数，它是一个40位的十六进制字符串，由时间戳、设备信息、请求路径等经过魔改HMAC计算得出。

###  步骤

####  1\. 抓包定位

抓包发现  ` X-Gorgon  ` 形如：

  *


    X-Gorgon: 0404e0b00001b0d6e0b00001b0d6e0b0


长度40位（20字节），前4位似乎是版本号。

####  2\. 静态分析

jadx搜索  ` X-Gorgon  ` ，定位到生成类  ` com.ss.android.common.applog.Gorgon  `
。发现核心方法：

  *   *   *   *   *   *   *   *   *   *


    public static String getGorgon(String url, String data, String cookies) {    // 获取时间戳    long ts = System.currentTimeMillis() / 1000;    // 获取设备ID（IMEI/OAID）    String deviceId = DeviceInfo.getDeviceId();    // 拼接字符串    String raw = ts + ":" + deviceId + ":" + url + ":" + data;    // 调用native方法    return nativeGetGorgon(raw, ts);}

####  3\. Hook native层

用Frida Hook  ` nativeGetGorgon  ` ：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    var module = Process.findModuleByName('libcms.so'); // 加密sovar nativeFunc = module.findExportByName('Java_com_ss_android_common_applog_Gorgon_nativeGetGorgon');
    Interceptor.attach(nativeFunc, {    onEnter: function(args) {        // 参数：JNIEnv*, jclass, jstring raw, jlong ts        var env = Java.vm.getEnv();        var rawStr = env.getStringUtfChars(args[2]).readCString();        var ts = args[3].toInt32();        console.log('[+] raw:', rawStr);        console.log('[+] ts:', ts);    },    onLeave: function(retval) {        var env = Java.vm.getEnv();        var result = env.getStringUtfChars(retval).readCString();        console.log('[+] X-Gorgon:', result);    }});

####  4\. 分析native算法

通过IDA分析  ` libcms.so  ` ，发现内部使用了一个魔改的HMAC-
SHA256，密钥是固定的16字节（硬编码在so中），但每次计算前会对密钥做一次异或变换，异或值与时间戳的低4位有关。

####  5\. Python复现


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    import hmacimport hashlibimport time
    # 从so中提取的固定密钥（16进制）base_key = bytes.fromhex('a1b2c3d4e5f6789012345678abcdef01')
    def get_gorgon(url, data, device_id):    ts = int(time.time())    # 密钥异或变换    xor_val = ts & 0x0f    key = bytes([b ^ xor_val for b in base_key])
        raw = f"{ts}:{device_id}:{url}:{data}"    # 魔改HMAC：先SHA256两次    h = hmac.new(key, raw.encode(), hashlib.sha256)    h2 = hmac.new(key, h.digest(), hashlib.sha256)
        # 取前20字节，加上版本前缀    gorgon = '0404' + h2.hexdigest()[:36]    return gorgon
    # 测试print(get_gorgon('/api/feed', '', 'device123'))


####  6\. 验证

将生成的  ` X-Gorgon  ` 放入请求头，服务器返回200，说明算法还原成功。

###  踩坑提醒

  * 不同版本的App，  ` X-Gorgon  ` 算法可能不同（v1/v2/v3），需要对应版本分析

  * 设备ID的获取方式也可能变化（IMEI→OAID→广告ID）

  * 有些请求还依赖  ` X-Khronos  ` （时间戳），需要一并模拟


##  六、本章小结

算法  |  定位技巧  |  提取关键  |  Python库
---|---|---|---
AES-CBC  |  Hook SecretKeySpec/IvParameterSpec  |  Key+IV hex  |  pycryptodome
RSA  |  Hook X509EncodedKeySpec  |  DER字节→模数指数  |  pycryptodome
HMAC  |  Hook Mac.init/doFinal  |  密钥hex  |  hmac
SM2/SM3/SM4  |  搜索SM2/SM3/SM4类名  |  调用gmssl  |  gmssl

核心思想：  ** 不要手动逆向算法细节，而是从内存中提取密钥和参数，然后用标准库复现。  **


##   风险提示

本文涉及的算法分析和复现技术仅可用于学习研究和已获授权的安全测试。未经授权破解他人App的加密通信、获取非公开数据，可能触犯《刑法》第285条及《网络安全法》。请严格遵守法律法规。
