---
schema_version: 2
id: android-so-jni-symbol-reference
document_type: reference
original_date: '2026-07-12'
archived_date: '2026-10-02'
scope:
  targets:
    - Android SO JNI registration and crypto-library symbols
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./anti-crawler-app-20260712-01.md#一如何找到jni函数映射表hook-registernatives"
    basis: source-report
  - id: s2
    ref: "./anti-crawler-app-20260712-01.md#处理不同类型的参数"
    basis: source-report
  - id: s3
    ref: "./anti-crawler-app-20260712-01.md#常见加密库特征"
    basis: source-report
  - id: s4
    ref: "./anti-crawler-app-20260712-01.md#去混淆的核心思路trace--等价变换"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s3]
    basis: source-report
    limits: 只保留动态注册的符号候选和加密库导出名。示例地址、教程密钥和粘连脚本不收录。Stalker 的使用边界不在本卡重复。
  - name: parameters
    anchor: parameters
    sources: [s1, s2]
    basis: source-report
    limits: JNI 读法来自来源表格。结构体步长写死在一条粘连脚本里，来源自己也写符号名随 Android 版本变化，不能当成稳定 ABI。
  - name: decision-flow
    anchor: decision-flow
    sources: [s4]
    basis: source-report
    limits: 三条去平坦化路线都是来源点名。没有还原前后的函数对照，deflat 地址是占位，不能当流程卡。
relations:
  - type: derived_from
    target: "./anti-crawler-app-20260712-01.md#一如何找到jni函数映射表hook-registernatives"
tags:
  - jni
  - registernatives
  - openssl
  - ollvm
  - source-report
---

# SO 层动态注册、JNI 读参和加密库符号

这张卡只回答：来源怎样从 `RegisterNatives` 找到动态注册的方法，怎样按 JNI 类型读参数，以及怎样用导出符号认出常见加密库。控制流平坦化只保留三条路线的名字和停止条件。不提供游戏登录签名器。

来源没有可公开定位的原文 URL。示例指针、示例账号串和教程密钥不进入本卡。

<a id="interfaces"></a>
## 注册入口和库符号

动态注册的场景是：`System.loadLibrary` 之后，native 方法不一定叫 `Java_com_example_...`，而是 `RegisterNatives`。来源要打印的是 Java 方法名、签名和 native 函数地址。

符号候选只有两级。先在 `libart.so` 里找；来源写不同 Android 版本符号名不同，建议先 `Module.enumerateExports("libart.so")`。找不到再试 `libnativehelper.so` 的 `jniRegisterNativeMethods`。加固 SO 可能晚加载，来源写要延迟 Hook 或 Hook `dlopen`。有的 SO 在 `JNI_OnLoad` 里注册，来源写可以先 Hook `JNI_OnLoad`。

加密库被写成四行导出特征：

| 库 | 来源点名的符号 | 来源给的辨认 |
|---|---|---|
| OpenSSL | `EVP_EncryptInit_ex`、`EVP_DecryptFinal_ex`、`HMAC_CTX_new`、`RSA_public_encrypt` | 以 `EVP_`、`HMAC_`、`RSA_` 开头 |
| mbedTLS | `mbedtls_aes_init`、`mbedtls_sha256_starts_ret` | 以 `mbedtls_` 开头 |
| Crypto++ | `CryptoPP::AES::Encrypt`、`CryptoPP::SHA256::CalculateDigest` | C++ 命名空间 |
| BoringSSL | `CRYPTO_gcm128_encrypt`、`ECDSA_sign` | 类似 OpenSSL 但略有不同 |

静态找法是 IDA 字符串里搜 `OpenSSL`、`mbedtls`、`CryptoPP`，或 `Module.enumerateExports()` 按这些前缀过滤。符号被 strip 时，来源改口特征码或 Hook `malloc` / `memcpy`。它举的 `EVP_EncryptInit_ex` 开头是 `push rbp; mov rbp, rsp`，这是来源原文里的 x86 形态，没有给出 ARM 字节，本卡不把它当成 Android SO 的特征码。

<a id="parameters"></a>
## JNI 参数怎么读

来源把 native 方法的前两个参数写成 `JNIEnv*` 和 `jclass` / `jobject`，业务参数从后面开始。读法表是：

| JNI 类型 | 来源写的 Frida 读法 |
|---|---|
| jstring | `Java.vm.getEnv().getStringUtfChars(args[N], null).readCString()` |
| jbyteArray | `getByteArrayElements` 返回指针 |
| jint | `args[N].toInt32()` |
| jlong | `args[N].toUInt64()` |
| jboolean | `args[N].toInt32() == 1` |
| 指针或结构体 | `Memory.readByteArray(args[N], size)` |

`getStringUtfChars` 的指针来源写应该释放，但把短期调试里的泄漏写成无所谓。非 String 的 `jobject` 要按真实类型另调 JNI。大数组只打印前几个字节。

同一条粘连脚本把 `JNINativeMethod` 写成 name、signature、fnPtr 三字段，并用固定步长遍历。步长和 `JNIEnv` 上取类名的偏移都写死在这一个例子里。上文已经写符号名随版本变化，所以这张表不能外推到任意 ABI。

<a id="decision-flow"></a>
## 平坦化时先走哪条

来源把 OLLVM 控制流平坦化写成一个大循环加 switch-case，静态读不下去。它给的三条路线是：

1. 跟踪实际走到的指令，把多次跟踪合成有限路径。Stalker 该不该上、跟踪范围和卡顿，已经在 Frida 技巧选择卡里；这里不重复操作边界。来源在这条路线上多说的一句是：只留对结果有贡献的赋值，忽略分发器。
2. 点名 Unicorn、angr 或 deflat.py。deflat 被写成用符号执行找基本块的真实跳转，再去掉分发器。步骤是记下起止地址、导出汇编、跑脚本、看输出。命令里的地址是占位，没有“怎样算还原对了”。
3. 手工等效替换：不恢复整张控制流图，只追踪关键变量的赋值和返回值。

三条都没有验收样本，也没有“还原失败就停”的出口，所以不是流程卡。

## 验证与限制

- 没有 SO、ABI、Android 版本或一次注册日志。
- 文末游戏登录案例不进入模块。它用示例账号串和教程密钥声明 HMAC 对上了，随后又写密钥可能是 Base64 或异或、时间戳单位要看抓包、拼接顺序可能要排序。这些句子互相留着口，不能当成已定位算法。示例串和密钥不收录。
- ARM64 寄存器宽度卡说的是 `x0 = JNIEnv*`，不是这张 Frida 读参表。猿人学 signKey 卡的 RegisterNatives 边界属于那个字段，目标也不是这组库符号。
- 本章小结把 Hook、读参、导出表、平坦化和 strlen/memcpy 再列了一遍。最后一句是找到输入和输出的关系再用标准库复现，没有新的字段规则。
