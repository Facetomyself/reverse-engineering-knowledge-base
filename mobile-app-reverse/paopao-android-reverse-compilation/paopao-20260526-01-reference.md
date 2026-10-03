---
schema_version: 2
id: android-jce-crypto-monitor-reference
document_type: reference
original_date: '2026-05-26'
archived_date: '2026-10-02'
scope:
  targets:
    - android-jce-crypto-monitor
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260526-01.md#二核心挑战cipher-实例关联"
    basis: source-report
  - id: s2
    ref: "./paopao-20260526-01.md#32-cipher-监控"
    basis: source-report
  - id: s3
    ref: "./paopao-20260526-01.md#33-messagedigest-监控"
    basis: source-report
  - id: s4
    ref: "./paopao-20260526-01.md#34-mac--hmac-监控"
    basis: source-report
  - id: s5
    ref: "./paopao-20260526-01.md#31-骨架配置与辅助函数"
    basis: source-report
  - id: s6
    ref: "./paopao-20260526-01.md#55-已知失效场景"
    basis: source-report
  - id: s7
    ref: "./paopao-20260526-01.md#六与-objection-的对比"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s2, s3, s4, s7]
    basis: source-report
    limits: 重载清单来自来源贴出的脚本。未在设备上安装这些 hook，也不覆盖第 13 篇的 Provider 路径。
  - name: parameters
    anchor: parameters
    sources: [s1, s5]
    basis: source-report
    limits: hashCode 关联和 CONFIG 默认值只是这份脚本的约定。截图里的密钥字节未收录。
  - name: validation
    anchor: validation
    sources: [s6, s5]
    basis: source-report
    limits: 无输出分支是来源的排查表。真机截图是作者报告，本轮未复跑。
relations:
  - type: derived_from
    target: "./paopao-20260526-01.md#二核心挑战cipher-实例关联"
tags:
  - jce
  - frida
  - source-report
---

# Java JCE 算法自吐：实例关联、重载取舍和无输出边界

这张卡只回答三件事：同一 Cipher 的三步怎么配成一次事件，哪些便捷重载来源故意不挂，以及完全没有输出时先排除什么。不收录 `crypto_monitor.js` 正文，也不收录截图里的密钥字节。ROMManager 的 Java Crypto Hook 是另一套 UI property，不在这张卡里。

来源把「算法自吐」定义成工作模式，不是某个 Frida API 的名字。

> 「算法自吐」不是一个 Frida API 的名字，而是一种 **逆向工作模式** ：

<a id="interfaces"></a>
## 挂上的入口和故意不挂的便捷重载

来源的范围是标准类：`Cipher`、`MessageDigest`、`Mac`、`Signature`，外加 `SecretKeySpec` / `IvParameterSpec` 和 `SecretKeyFactory.generateSecret`。业务类即使混淆，仍要走到这些类。

Cipher 侧把 `getInstance`、`init`、`doFinal` 收成同一条事件。`getInstance` 写了三个重载（仅 transformation、加 provider 名、加 Provider 对象）。`init` 的共享逻辑再接到多个重载。`doFinal` 接无参、`byte[]`、以及 `byte[]/offset/len`。

摘要和 HMAC 不挂「update 再收尾」的便捷重载，否则一次调用打两次：

> // 不 hook digest(byte[]):它内部 = update(byte[]) + digest()。

> >   4. 故意 **不** hook ` doFinal(byte[]) ` —— 它内部 = ` update + doFinal() ` ，hook

`Mac.update(ByteBuffer)` 在来源脚本里只记下 `remaining`，不把缓冲区内容拆出来。Signature 的 `update` / `sign` / `verify` 各自打事件，不做 Cipher 那种上下文表。

和 Objection 的差别，来源收成一句：Objection 用来确认有没有调用，这份脚本用来把一次操作的字段配齐。版本以来源注明的 v1.11 之前印象为限。

> **选型口诀** ：Objection 验证调用， ` crypto_monitor ` 还原方案。

<a id="parameters"></a>
## 上下文键和输出控制

关联键是 Cipher 实例的 `hashCode`。来源的理由是 Frida JS 端没有可跨 `getInstance` 与 `doFinal` 复读的标准 WeakRef，自增号也拿不回去。

> 对象自带、跨方法可复读的身份标识——最适合做"查 ctx"的 key。

上下文里放算法串、模式、密钥字节和 IV。`doFinal` 打完报告就删掉这条：

> > doFinal ` 输出报告后立刻 ` delete cipherCtxMap[id] `

来源同时写明代价：同一实例连续多次 `doFinal` 时，第二次没有上下文。它把这当成可接受，因为多数业务是一次性 `doFinal`。`hashCode` 是 32 位 identity hash，不同对象理论上会撞；删除是为了把同时活着的实例数压小，不是证明不会撞。

输出控制写在 `CONFIG`：六个功能开关、调用栈行数、`maxDataLength`、`filterPackage`、`rateLimitPerSecond`、`useColor`。限速用令牌桶。桶空时整条事件丢掉，不是只丢掉后半行。设为 0 表示不限速。

> 设为 ` 0 ` 表示完全不限速。

开关为 false 时，对应的 `Java.perform` 整块不执行，hook 不装进进程。包名过滤只剪调用栈，事件的算法、密钥、IV、输入和输出仍打印。

密钥字节的提取顺序是：先按 `SecretKeySpec` 取 `getEncoded()`，失败再对 Key 调 `getEncoded()`，再失败则 `toString()`。IV 先按 `IvParameterSpec`，再按 `GCMParameterSpec`。PBKDF2 路径额外读密码、盐、迭代次数和密钥位数。这些是脚本字段，不是某一 App 的参数表。

<a id="validation"></a>
## 无输出时先看什么

来源给的自检只有两步：启动横幅里有没有 `[OK]`，以及是不是要加 `Java.deoptimizeEverything()`。后者会把已 JIT 的方法拉回解释执行，来源写启动时会卡 1–3 秒，只在确实没有事件时再用。

两步都做了仍没有 Cipher / Hash，来源不再改这份脚本，改为下表。本轮没有复跑。

| 来源场景 | 来源看到的现象 | 来源给出的下一步 |
|---|---|---|
| AndroidKeyStore | 看得到 Cipher，密钥字段是对象而不是字节 | `getEncoded()` 为 null，Java 层读不出 |
| 只在 SO 里加密 | 本脚本完全无输出 | 转到 Native 层入口 |
| Conscrypt EngineSpi | 不走 `javax.crypto.Cipher` | 来源指向第 13 篇，本篇没有补 hook |
| 自定义 Provider | 标准类被换掉 | 先看 `Security.getProviders()` |

> 硬件密钥不可导出（ ` getEncoded() ` 返回 null）,Frida Java 层读不出。

> App 不走 Java JCE，直接在 SO 里调 OpenSSL / Mbedtls / BoringSSL

> 某些 OkHttp/TLS 实现直连 ` ConscryptEngineSocket ` ，不走 ` javax.crypto.Cipher `

来源对一张真机 Cipher 事件的读法是：算法串为 `AES/CBC/PKCS5Padding · ENCRYPT`，IV 与密钥字节相同，输入以 gzip 魔数开头。这是单次样本的读法，不是算法规则。密钥原文不进入本卡。

## 验证与限制

- 第 3.1–3.7 节要按顺序拼进同一个 IIFE。文末完整单文件在公众号关键词之后，本卡不补那份文件。
- 工作流图和架构图没有可引用的正文。
- 多线程只保证同一事件的行在一次 `console.log` 里，不保证事件之间的顺序。
- 未运行 Frida，不能把 `[OK]` 或截图当成这次审阅的通过条件。
