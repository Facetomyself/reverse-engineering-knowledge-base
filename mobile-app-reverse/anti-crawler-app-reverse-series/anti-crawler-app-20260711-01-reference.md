---
schema_version: 2
id: java-crypto-key-material-reference
document_type: reference
original_date: '2026-07-11'
archived_date: '2026-10-02'
scope:
  targets:
    - Java javax.crypto key-material hooks
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./anti-crawler-app-20260711-01.md#一aes-cbcpkcs7从内存中dump出key和iv"
    basis: source-report
  - id: s2
    ref: "./anti-crawler-app-20260711-01.md#二rsa区分公钥加密与私钥签名提取模数n和指数e"
    basis: source-report
  - id: s3
    ref: "./anti-crawler-app-20260711-01.md#三hmac-sha256找盐值salt的来源"
    basis: source-report
  - id: s4
    ref: "./anti-crawler-app-20260711-01.md#四国密sm2sm3sm4识别特征并调用开源库"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s3, s4]
    basis: source-report
    limits: 只保留来源对填充、密钥长度、RSA 操作分类、盐值来源和国密密文排列的描述。没有目标 App、版本或运行对照。
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2, s3, s4]
    basis: source-report
    limits: 只保留来源点名的 Java 类和构造器。归档代码围栏粘成单行，本卡不还原成可执行脚本，也不收录示意密钥。
relations:
  - type: derived_from
    target: "./anti-crawler-app-20260711-01.md#一aes-cbcpkcs7从内存中dump出key和iv"
tags:
  - aes
  - rsa
  - hmac
  - sm2
  - source-report
---

# Java 层密钥材料：构造器、填充和盐值来源

这张卡只回答：来源在看见算法名、却看不见 Key、IV 或盐时，把哪些 `javax.crypto` 构造器和分类当成提取点。不提供可运行复现，也不把文末短视频请求头案例当成已定位算法。

来源没有可公开定位的原文 URL。作者自称的成功只保留为 source-report。示意十六进制、示例请求头和设备标识不进入本卡。

<a id="parameters"></a>
## 参数机制

AES 一节把 `AES/CBC/PKCS5Padding` 的密钥材料放在 `SecretKeySpec` 和 `IvParameterSpec`。来源写 PKCS5 与 PKCS7 在 AES 里相同，并写 Python 的 `Crypto.Cipher.AES` 默认 PKCS7。Key 长度被写成必须是 16、24 或 32 字节。解密成乱码时，来源要检查的是 Key、IV、是否真为 CBC，以及有没有额外填充。

RSA 被分成四格，而不是一个“加密”：

| 来源称呼 | 类 | 模式 | 来源对用途的说法 |
|---|---|---|---|
| 公钥加密 | Cipher | ENCRYPT_MODE | 加密数据，私钥解密 |
| 私钥签名 | Signature | SIGN | 签名数据，公钥验签 |
| 私钥解密 | Cipher | DECRYPT_MODE | 少见，除非 App 有私钥 |
| 公钥验签 | Signature | VERIFY | 验证签名 |

来源写通常 App 只有公钥，私钥在服务器。长度上限写成密钥长度/8 减 11，并举例 2048 位最多 245 字节。填充写成 PKCS1_v1_5 最常见，也可能是要指定 hash 的 OAEP。本地私钥签名被写成通常提不到私钥。

HMAC 的盐被分成四类：固定串、密钥里带当前时间戳、每次不同的 UUID 或 SecureRandom、登录接口下发。来源另写密钥可能先 MD5 或 Base64，拼接顺序通常是字典序或固定顺序，时间戳要分秒和毫秒。

国密只给识别特征，不给曲线参数。SM2 对上 `SM2Engine` 或 `SM2KeyPairGenerator`，输出通常 C1C2C3。SM3 对上 `SM3Digest` 或 `sm3_hash`，256 位，类似 SHA256 但不同。SM4 对上 `SM4Engine` 或 `SM4_Encrypt`，分组和密钥都是 128 位。密文排列要区分 C1C2C3 和 C1C3C2。SM4 填充可能是 PKCS7 或 ZeroPadding。来源写有的 App 会魔改，不能直接套标准库。

<a id="interfaces"></a>
## 来源点名的构造器

| 材料 | 来源点名的入口 |
|---|---|
| AES Key / IV | `SecretKeySpec`、`IvParameterSpec` 构造器；字符串再转时还有 `String.getBytes()` 或 `Base64.decode()` |
| RSA 公钥 DER | `KeyFactory.generatePublic` 或 `X509EncodedKeySpec` |
| HMAC-SHA256 | `Mac.getInstance("HmacSHA256")`，再看 `Mac.init` 和 `Mac.doFinal` |
| 国密类名 | 搜索 `SM2`、`SM3`、`SM4`、`sm2_encrypt`；BouncyCastle 被写成 `org.bouncycastle.crypto.engines.SM2Engine` |

这些是来源给出的观察点。归档里的 Frida 和 Python 示例粘在同一行，含占位十六进制，本卡不重建。

## 验证与限制

- 没有目标包名、版本、SO 或一次实际构造器日志。
- 文末 `X-Gorgon` 案例不进入模块：正文写 40 位十六进制，围栏里的示例长度并不是 40；类名和 native 名没有版本；密钥是示意串；作者用“服务器返回 200”当作还原成功。这些都只是 source-report，而且缺失败出口，所以也不是流程。
- 同目标的 parameters 与 interfaces 近邻查询没有命中。产品自己的 AES 卡、第 3 章的 OkHttp 静态定位，都不是这一组构造器。
- 本章小结只是把上面四行再列成表。
