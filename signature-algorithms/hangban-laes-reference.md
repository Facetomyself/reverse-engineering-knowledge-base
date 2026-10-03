---
schema_version: 2
id: signature-algorithms-hangban-laes-reference
document_type: reference
archived_date: '2026-10-01'
scope:
  targets: [hangban]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./hangban-laes-encrypt.md#分析目标
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 仅描述来源所报 JNI wrapper/native 边界；不是 HTTP API，未核验 APK、SO 或 byte[] 参数语义。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 仅对应来源报告的 HangBan 样本分支；完整自定义表和算法脚本未取得，不能跨输入或版本外推。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 仅记录作者对单一样本的回放陈述；本轮未独立复跑，无 local-parity 或 server-accepted 证据。
relations:
  - type: derived_from
    target: ./hangban-laes-encrypt.md#分析目标
tags: [HangBan, LAES, JNI, ECB, PKCS7, native-analysis]
---

# HangBan JNI 加密入口与单样本算法线索

本文用于检索来源文章中报告的 Java/JNI 入口、参数处理和 native 算法线索。它只描述 HangBan 这一份材料中的单一样本分析，不是外部业务 API 说明，也不代表通用算法实现。原归档引用的 PDF 没有公开 locator；本文所有技术结论都保留为 `source-report`。

<a id="interfaces"></a>
## 接口边界

来源将 `laesEncryptStringWithBase64(String, String, byte[])String` 描述为 Java/JNI 入口：明文字符串以 UTF-8 形式进入 native，第二个字符串按 hex 解码后作为 key material 传入 native 加密函数，输出再经自定义 Base64 包装。原文还列出 JNI wrapper 到 native dispatcher、单分组轮函数的内部调用关系。这里的链路是 native 函数调用链，不是网络请求链。

签名中的第三个 `byte[]` 参数在原文样本表中对应的 IV 值为 null；现有材料不足以确认该参数在其他调用或模式中的语义，不能据此认定 IV 普遍被忽略。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源报告了 Java/JNI 方法签名及返回类型 | s1，`hangban-laes-encrypt.md` L47 | source-report | 本文所述 HangBan 样本入口 | 未核验 APK、方法声明或 JNI 注册；不是 HTTP API |
| C2 | JNI wrapper 报告执行 UTF-8 获取、hex 解码、native 调用和 Base64 输出包装 | s1，L85-L92 | source-report | 来源所述 wrapper 边界 | 非法输入、空值、异常及第三参数语义未知 |
| C3 | 来源报告了 JNI wrapper → native 加密函数 → dispatcher → 单分组轮函数的内部调用关系 | s1，L78-L83 | source-report | 来源所述 SO 样本 | 偏移和函数布局未核验，不能跨构建复用 |

<a id="parameters"></a>
## 参数与算法线索

原文报告某一分支将 key material 的前四字节用于模式/路径选择，而非普通密钥前缀；所述分支使用 16-byte block、ECB 和 PKCS7 padding。它还描述了一个非标准 AES key schedule 的滚动异或关系：

```python
round_keys[i] = key_material[i + 4] ^ key_material[(i + 1) % 3]  # i = 0..175
```

以上是来源作者对目标样本的描述，不是本轮确认过的算法事实。原文进一步报告初始轮 nibble lookup、中间轮自定义 T-box/mixing tables 和末轮替换表；完整表内容没有随本文提供。不能仅凭这些结构描述重建可执行算法，也不能称其为标准 AES 或推广为通用加密实现。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 来源将前四字节描述为模式头，并报告一个分支使用 16-byte block、ECB、PKCS7 | s1，L106-L110 | source-report | 原文指定分支 | 分支条件、其他模式和边界输入未知；样本头部值不在此复述 |
| C5 | 来源报告 180-byte key material 到 176-byte round-key material 的滚动异或派生 | s1，L112-L118 | source-report | 来源所述算法路径 | 未核验输入布局、轮次、字节序或索引规则；不包含任何样本 key 值 |
| C6 | 来源报告 nibble mixing、custom T-box、替换表和 AES-like 结构相似性 | s1，L138-L171 | source-report | 来源所述单分组实现 | 完整表与代码缺失；结构相似不证明与标准 AES 兼容 |
| C7 | 来源给出的样本 IV 字段为 null | s1，L53-L55 | source-report | 该单一样本 | 不证明其他输入的 IV 取值，也不证明 IV 参数被忽略 |

<a id="validation"></a>
## 验证与限制

原文称作者的 Python 回放与同一样本的官方 JNI trace 输出一致，并称同一输入/输出对排除了“标准 AES 套壳”假设。这里仅记录来源作者的验证陈述；本轮没有取得 PDF、`hangban_algo.py`、完整查表数据、APK/SO 或 trace 原件，也没有独立运行 native 或复跑脚本。因此不能把该陈述升级为本地 `local-parity`。来源亦明确把服务端接受与离线/JNI 对比区分，需独立业务 readback；当前没有 `server-accepted` 证据。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 来源称其离线脚本对单一样本的输出与 JNI trace 一致 | s1，L173-L177 | source-report | 作者报告的单一样本 | 没有脚本、trace 或独立复跑；不构成本轮 parity |
| C9 | 来源要求以独立业务 readback 判断 server acceptance | s1，L189-L191 | source-report | 来源定义的验证口径 | 本文没有请求业务服务端，接受状态仍未知 |

适用范围、版本和观测时间均未知。样本明文、静态 key material 和 Base64 输出值不在本卡复制。对其他版本、模式、输入或服务端行为的结论均未建立。
