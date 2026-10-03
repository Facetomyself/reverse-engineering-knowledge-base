---
schema_version: 2
id: boringssl-native-crypto-reference
document_type: reference
original_date: '2026-05-28'
archived_date: '2026-10-02'
scope:
  targets:
    - boringssl-native-crypto
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260528-01.md#二opensslboringssl-的两套-api--选择策略"
    basis: source-report
  - id: s2
    ref: "./paopao-20260528-01.md#22-jce--opensslboringssl-函数对照表"
    basis: source-report
  - id: s3
    ref: "./paopao-20260528-01.md#三三步定位法从-java-到-so-函数"
    basis: source-report
  - id: s4
    ref: "./paopao-20260528-01.md#段-1--入口--配置--辅助函数"
    basis: source-report
  - id: s5
    ref: "./paopao-20260528-01.md#段-5--aes-低级-api--aes_set_encrypt_key--aes_cbc_encrypt"
    basis: source-report
  - id: s6
    ref: "./paopao-20260528-01.md#62-hook-boringssl-的注意事项"
    basis: source-report
  - id: s7
    ref: "./paopao-20260528-01.md#63-flutter-app-的特殊处理"
    basis: source-report
  - id: s8
    ref: "./paopao-20260528-01.md#九适用边界三类例外场景"
    basis: source-report
  - id: s9
    ref: "./paopao-20260528-01.md#段-3--evp-哈希--evp_digest"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2, s3, s4, s6, s7]
    basis: source-report
    limits: 对照表和符号回退是来源对 OpenSSL/BoringSSL 导出名的整理。未在样例 SO 上复挂。
  - name: parameters
    anchor: parameters
    sources: [s2, s5, s9]
    basis: source-report
    limits: 参数落点和摘要长度对照来自来源脚本与读法。样例密钥、模数和截图字节未收录。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s8]
    basis: source-report
    limits: 分支是来源的选择顺序。三类例外的修复步骤指向后文，本卡不把它们写成已完成的流程。
relations:
  - type: derived_from
    target: "./paopao-20260528-01.md#二opensslboringssl-的两套-api--选择策略"
tags:
  - boringssl
  - openssl
  - source-report
---

# BoringSSL/OpenSSL：两套 API、参数落点和找不到符号时的分支

这张卡只回答：Java 层算法自吐没有输出时，Native 层先挂哪套导出，参数在第几个指针，以及导出表为空时来源还承认哪三种失败。不收录 `native_crypto_monitor.js` 正文，不收录样例密钥和模数。未导出函数的多策略定位在后文另一张卡，这里只保留来源自己的分支。

<a id="interfaces"></a>
## 先覆盖哪套导出

来源先用第 14 篇的 Java 脚本做分流：有 Cipher/HMAC 就留在 Java；没有输出但抓包仍是密文，才进 Native。

两套都要挂，因为事先不知道目标走哪条：

> **Hook 策略** ：实战中两套都要 Hook——你不知道目标 App 走哪条。三步：第三章定位到 SO 里的 crypto 函数 →

| 来源列的风格 | 来源举的入口 | 来源说何时遇到 |
|---|---|---|
| EVP | `EVP_EncryptInit_ex`、`EVP_DigestUpdate`、`HMAC_Init_ex` | 新代码、Conscrypt、Flutter、Chromium |
| 低级 | `AES_set_encrypt_key`、`AES_cbc_encrypt`、`RSA_public_encrypt`、`MD5_Update` | 老代码、嵌入式、自带定制 BoringSSL |

Java 侧 `Cipher.init`（AES）对应 `AES_set_encrypt_key`，抓原始 key 和 bits。EVP 路径用一组 Init/Update/Final 覆盖对称算法。来源写明优先 EVP，只有 SO 没有 EVP 导出才退回低级 API。

算法名不靠 NID 数字硬编码。段 1 用三步反查：

> EVP_CIPHER_CTX_cipher ` \+ ` EVP_CIPHER_nid ` \+ ` OBJ_nid2sn ` 三步反查算法名（

版本差异写在回退顺序里，不是另一套脚本：

> EVP_CIPHER_CTX_cipher      ← OpenSSL 1.x

> EVP_CIPHER_CTX_get0_cipher ← OpenSSL 3.x / BoringSSL 新版

> EVP_CIPHER_get_nid         ← OpenSSL 3.x

从 Java native 方法走到 SO 时，来源的 RegisterNatives 记录有五列：类名、方法名、JNI 签名、函数地址加 SO 偏移、以及谁在 `JNI_OnLoad` 里注册。看到 `AES_cbc_encrypt` 这类名字就直接挂导出；没有名字才去常量。

默认搜索列表只有 `libcrypto.so`。Flutter 的 BoringSSL 在 `libflutter.so`，Cronet 在 `libcronet.so`。

> Flutter 内嵌的 BoringSSL 在 **` libflutter.so ` ** 中而不是系统的 ` libcrypto.so ` ，本篇 `

只想知道有没有打到导出、不要参数时，来源把 `frida-trace` 的 `AES_*` / `RSA_*` / `EVP_*` 当成互补，不代替这份脚本的参数输出。

<a id="parameters"></a>
## 参数落在哪

EVP Init 的来源注释是：`ctx`、`type`、`impl`、`key`、`iv` 依次为参数 0、1、2、3、4。密钥长度按算法名里的 128/192/256 猜 16/24/32，猜不中就用 16。IV 在这段脚本里按 16 字节读。`retval !== 1` 的调用丢掉。

摘要不挂 Init。最终长度用来反推算法：

> SHA-256=32 ` / ` SHA-512=64 ` ）反推即可。

来源同一段还写了 MD5 为 16、SHA-1 为 20。这是输出长度对照，不是测量到的样本。

AES-CBC 的第 4 个参数不能当原始密钥：

> ` AES_cbc_encrypt ` 的第 4 参是 key schedule 展开后的扩展密钥（176/240 字节，反推不出来），必须同时 hook

原始 key 和 bits 在 `AES_set_encrypt_key` / `AES_set_decrypt_key`。CBC 的方向在最后一个 `enc` 参数。

`BN_mod_exp_mont` 的来源读法：第 3、4 个参数是指数和模数。指数的 hex 短于 16 个字符时，来源把它当成公钥指数，更长则当成私钥指数。读不出 BIGNUM 就跳过，因为 DH/DSA 也会进这个函数。样例模数不进入本卡。

MD5 低级路径用来源的 `MD5_CTX*` 指针把多次 Update 攒到 Final。EVP/HMAC 的正文脚本是分段各打一行；「按 ctx 合成一条」写在完整版清单里，不在这 7 段正文里。

完整版清单还写了多副本 `libcrypto.so`、TLS 握手噪声、spawn 时 `dlopen` 早于 SO 加载、以及库自检向量。这些是来源说生产环境会踩到的坑，不是上面 7 段已经包含的行为。

<a id="decision-flow"></a>
## 没有导出时的分支

1. Java 脚本已有 Cipher/HMAC：停在 Java 层。
2. Java 无输出且抓包仍是密文：挂 EVP；没有 EVP 导出再挂低级 API。
3. 导出表没有这些名字，但导入表还有：来源称为 strip，改用常量。AES S-Box 以 `63 7c 77 7b` 开头，SM4 S-Box 以 `d6 90 e9 fe` 开头。
4. `Memory.scan` 在加固 SO 上报 access violation：来源称为 `.rodata` 被标成 `PROT_NONE`，跳过该 SO，不当成脚本错误。
5. 常量也没有，或 S-Box 位置和字节序不像标准表：来源称为魔改或白盒，常量分支失效。

> **第一类，符号被 strip** 。SO 里 ` AES_cbc_encrypt ` 、 ` MD5_Update ` 、 ` EVP_* `

> **第二类，SO 被加固** （360、爱加密、梆梆等）。SO 文件磁盘内容是壳代码，真正的加密逻辑解密后才出现在内存里， `

> **第三类，算法被魔改或自实现** 。S-box 被换了、轮数被改了、用了查表法白盒，常量识别也失效。 **识别信号** ：第 7.3

段 7.4 的 `libnative.so+0x4A8C` 是来源假设的偏移，不是从样例里定位到的地址。

## 验证与限制

- 酷狗音乐 v20.6.4 被来源声明为 BoringSSL 的说明载体，不是这张卡的目标。
- 第五章截图读法依赖作者的真机输出。本轮未挂脚本，也未核对模数或密钥。
- 壳修复、SoFixer 和魔改还原都指向后文，这里没有步骤、验收或失败出口。
- 未运行 Frida。`[OK]` 行和截图都只是来源报告。
