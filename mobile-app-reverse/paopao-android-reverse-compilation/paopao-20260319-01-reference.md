---
schema_version: 2
id: paopao-musics-fcg-calc-boundary-reference
document_type: reference
original_date: '2026-03-19'
archived_date: '2026-10-02'
scope:
  targets:
    - musics.fcg
    - libmer.so
  client: Android
  version: v20.x.x（第三篇；包名与补丁位在正文中脱敏）
  observed_at: 2026-03-17 ~ 2026-03-19
sources:
  - id: s1
    ref: "./paopao-20260319-01.md#22-三类-cgi-端点"
    basis: source-report
  - id: s2
    ref: "./paopao-20260319-01.md#243-m-encoding-编码--requestt"
    basis: source-report
  - id: s3
    ref: "./paopao-20260319-01.md#核心结论"
    basis: source-report
  - id: s4
    ref: "./paopao-20260319-01.md#164-待完成工作"
    basis: source-report
  - id: s5
    ref: "./paopao-20260319-01.md#43-差分分析结论"
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s1, s2]
    basis: source-report
    limits: 端点、头字段和 M-Encoding 形状来自作者对已脱敏包名的静态阅读与抓包自述。本卡不收录解压脚本、账号样例或令牌。
  - name: parameters
    anchor: parameters
    sources: [s3, s4, s5]
    basis: source-report
    limits: 20 字节哈希的密钥在正文中被写成占位符。12 字节前缀和 104 字节 mask 来源自己标为未完成。本卡不能当作签名器。
  - name: validation
    anchor: validation
    sources: [s3, s4, s5]
    basis: source-report
    limits: 17/17 与“不能离线”都是作者前后两篇的自述。本次只读文本，没有重算向量，也不把第二篇的差分结论当成仍有效。
relations:
  - type: derived_from
    target: "./paopao-20260319-01.md#某音乐-app-逆向一三加密通信全解析与-calc-签名算法还原"
tags:
  - musics-fcg
  - libmer
  - source-report
---

# musics.fcg 与 libmer.so calc 的字段边界

这张卡只回答三件事：签名 CGI 和另外两条 CGI 怎么分、请求体的 M-Encoding 在来源里是什么形状、`sign` / `mask` 哪些部分来源声称已经还原。包名在正文里保持脱敏。来源有一处把应用称作 QQ 音乐，但不提供可定位的版本补丁位。

不收录 Frida 脚本、JNI 序号、盐值原文、账号字段样例或可调用的签名实现。豆瓣的 HMAC-SHA1 卡是另一个应用，不覆盖本接口。

<a id="request-chain"></a>
## 请求链

来源把抓包起点写成发往 `u6.y.qq.com` 的 `musics.fcg` POST。配置类里还有 `musicu.fcg` 与 `musicw.fcg`。`musics.fcg` 被标成需要签名的 CGI。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 观察起点是该主机上的 musics.fcg POST | https://u6.y.qq.com/cgi-bin/musics.fcg | s1 paopao-20260319-01.md:105 | source-report | 只说明作者抓到的主机，不代表全部域名 |
| C2 | musics.fcg 需要 M-Encoding 和 sign | 签名接口，需要 M-Encoding + sign | s1 paopao-20260319-01.md:168 | source-report | 触发条件还依赖业务标记和服务端配置，正文没有给出配置表 |
| C3 | 签名在编码之前，编码是 Deflate 加 5 字节前缀 | M-Encoding：Deflate 压缩 + 5 字节随机前缀 | s2 paopao-20260319-01.md:198 | source-report | 前缀每字节范围来自作者阅读的 Java，本次未复算 |
| C4 | 作者把 m1 写成压缩加混淆头，而不是密码学加密 | 不是密码学加密 | s2 paopao-20260319-01.md:299 | source-report | 这是作者结论。本卡不给还原步骤 |
| C5 | 响应侧把五个 0x00 开头标成跳过 5 字节再 Inflate | 跳过 5 字节 + Inflate | s2 paopao-20260319-01.md:324 | source-report | 同段还列出明文 JSON、gzip 和其它二进制，不能把所有响应都当成 m1 |

`calc` 的 Java 声明是 `content` 与 `params` 两个字节数组进、字符串出。`params` 的字段顺序被写成 `ct&cv&uid&qq&timestamp&udid&android`。样例值在正文里已打码，这里不抄。

<a id="parameters"></a>
## 参数机制

`sign` 和 `mask` 都来自 `libmer.so` 里动态注册的 `calc`。来源把入口放在相对 SO 基址 `0x6e098`。第二篇把原始 `sign` 写成 32 字节：12 字节会话前缀加 20 字节哈希，`mask` 原始长度为 104 字节，Base64 后 140 字符。

第三篇把这 20 字节改判为标准 HMAC-SHA1：密钥是固定的 12 字节 ASCII，正文已脱敏；消息是对 content 做 base64 后再反转字符串。第三篇同时写 17/17 测试向量通过，并用三行 Python 声称可以离线计算这 20 字节。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C6 | 第三篇把 20 字节算法写成标准 HMAC-SHA1 | 标准 HMAC-SHA1 | s3 paopao-20260319-01.md:1596 | source-report | 密钥未出现在正文中 |
| C7 | 消息预处理是 base64 后反转 | 对 content 做 base64 编码后反转字符串 | s3 paopao-20260319-01.md:1598 | source-report | 只覆盖 content 哈希，不覆盖前缀和 mask |
| C8 | 密钥被写成固定 12 字节并已脱敏 | 固定 12 字节 ASCII 字符串（已脱敏 | s3 paopao-20260319-01.md:1597 | source-report | 占位符不是密钥，不能拿来计算 |
| C9 | sign 的外部拼接是 12 字节前缀加 20 字节哈希 | session_prefix（12B） + sign_hash（20B） | s5 paopao-20260319-01.md:1426 | source-report | 前缀的生成算法未还原 |
| C10 | 12 字节前缀和 104 字节 mask 仍打开 | 12 字节前缀生成 | s4 paopao-20260319-01.md:2613 | source-report | 同表把 mask 标为未分析，完整离线 calc 依赖这两项 |

<a id="validation"></a>
## 验证与限制

第二篇用差分实验把 `sign_hash` 写成自定义非线性函数，并写明不是标准 SHA1、MD5、HMAC 或 CRC 的已知组合，离线计算不可行，因为依赖会话状态。第三篇推翻了这一判断，改写成标准 HMAC-SHA1 加固定密钥和 base64 反转，并称哈希不依赖 params、时间戳和会话状态。两篇都留在同一篇合并正文里，后写的第三篇是作者自己的更正，但密钥不在文本中，17/17 不能在本次阅读里复核。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C11 | 第二篇曾排除标准 HMAC | 非标准 SHA1/MD5/HMAC/CRC 的任何已知组合 | s5 paopao-20260319-01.md:1298 | source-report | 被第三篇改判，不能再当最终结论 |
| C12 | 第二篇写离线签名不可行 | 无法脱离设备计算 | s5 paopao-20260319-01.md:1529 | source-report | 只代表第二篇结束时的判断 |
| C13 | 第三篇声称向量全部通过 | 17/17 已知测试向量全部通过 | s3 paopao-20260319-01.md:1599 | source-report | 作者自述。密钥脱敏后，本次无法重算 |
| C14 | 第三篇的收束句确认 HMAC-SHA1 与 base64 反转 | 算法最终被确认为标准 HMAC-SHA1 | s3 paopao-20260319-01.md:2626 | source-report | 同一句把安全性主要归于 CFF，不是算法保密。前缀和 mask 仍未完成 |

第一篇还写过一条 MD5 盐链，并给出一串硬编码值。第二篇后文改口说盐值和 APK 哈希不予公开完整值。第三篇不再用这条 MD5 链解释 20 字节哈希。该字面量不进入本卡。

因此可复用的边界只有：M-Encoding 的形状、`sign` 的 12+20 分段，以及“20 字节被作者改判为 HMAC-SHA1，但密钥、前缀、mask 都不在可复用材料里”。缺任何一段都不能把 `calc` 当成已闭合实现。
