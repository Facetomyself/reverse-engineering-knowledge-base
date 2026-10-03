---
schema_version: 2
id: grok-dewux-web-sign-layers
document_type: reference
original_date: '2026-09-01'
archived_date: '2026-09-06'
scope:
  targets: [dewux-web-sign]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ai-assisted-20260901-01.md#一一页纸"
    basis: source-report
  - id: s2
    ref: "./ai-assisted-20260901-01.md#二sign-和-hsn签名套签名"
    basis: source-report
  - id: s3
    ref: "./ai-assisted-20260901-01.md#三重定位grep-0-命中不代表字符串每次重编码"
    basis: source-report
  - id: s4
    ref: "./ai-assisted-20260901-01.md#四data-上报aes-的-key-藏在一个母串的-substr-里"
    basis: source-report
  - id: s5
    ref: "./ai-assisted-20260901-01.md#五设备握手-websk响应是五层套娃"
    basis: source-report
  - id: s6
    ref: "./ai-assisted-20260901-01.md#六魔改-rc4标准骨架加两个整数扰动"
    basis: source-report
  - id: s7
    ref: "./ai-assisted-20260901-01.md#七kdf-纯离线和一个抗漂移的定位技巧"
    basis: source-report
  - id: s8
    ref: "./ai-assisted-20260901-01.md#八验证以及做到哪为止"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s4, s6, s7]
    basis: source-report
    limits: 只保留来源对字段算法和母串切片的原句。SALT、AES 母串和 RC4 密钥在来源中是占位，本卡不补常量，也不把草图补成可运行实现。
  - name: request-chain
    anchor: request-chain
    sources: [s1, s2, s5, s7]
    basis: source-report
    limits: 只保留签名顺序和响应剥离次序。五层里的密钥材料仍是占位名，未逐层验字节。
  - name: interfaces
    anchor: interfaces
    sources: [s1, s5]
    basis: source-report
    limits: 只点到作者写出的路径和头字段名。第三方设备指纹与文件头自报的加固被作者划出本文，不单列模块。
  - name: validation
    anchor: validation
    sources: [s7, s8]
    basis: source-report
    limits: 逐字节一致和冷启动对照都是作者自述。本次没有重跑。作者写明用复现值去要业务成功响应没有走通。
  - name: decision-flow
    anchor: decision-flow
    sources: [s3, s4, s7, s8]
    basis: source-report
    limits: 这些是作者的排查顺序，不是闭合流程。没有验收步骤，也没有失败后的停机出口，因此不另建 procedure。
relations:
  - type: derived_from
    target: "./ai-assisted-20260901-01.md#某-dewux-web-签名逆向三层签名逐字节复现最硬的是一次五层套娃的握手"
tags: [dewux-web-sign, source-report]
---

# 某 dewuX Web 签名字段与握手边界

这张卡只回答来源里能定位的字段落点、签名顺序、握手响应层次，以及作者自己停下的边界。站点以来源的「某 dewuX」为准，常量保持占位。`md5-1038` 那张卡来自另一篇稿，目标不同，不并入。依据停在 `source-report`。

<a id="parameters"></a>
## 参数

`sign` 是排序拼接后再接盐的 MD5。`hsn` 签的是已经含 `sign` 的完整 body 串。`data` 是指纹 JSON 的 AES，key 和 iv 从同一条占位母串上切。`ltk` / `adi` 共用 RC4 再编码。握手用的 RC4 被写成标准骨架加两个整数扰动，扰动落点由 `c % 5` 选择。KDF 的两个输出，来源只明确一个跨会话不变、一个随 `d` 变。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | MD5(参数按 key 排序拼 key+value + SALT) | s1 ./ai-assisted-20260901-01.md:56 | source-report | 来源所称 body 首键 sign | 盐是占位，未复算 |
| C2 | 含 sign 的完整 body 串 | s1 ./ai-assisted-20260901-01.md:57 | source-report | 来源所称请求头 hsn | 不代表其它头也这样签 |
| C3 | AES-128-CBC/Pkcs7(JSON.stringify(指纹)) | s4 ./ai-assisted-20260901-01.md:58 | source-report | 来源所称 data 上报 | 指纹字段表不在本文 |
| C4 | key/iv 从一个母串 substr 切出来 | s4 ./ai-assisted-20260901-01.md:58 | source-report | 同一条 data | 母串原文未给出 |
| C5 | key = M.substr(5, 16) | s4 ./ai-assisted-20260901-01.md:122 | source-report | 来源给出的占位母串 M | M 不是实值 |
| C6 | M.substr(10, 16) | s4 ./ai-assisted-20260901-01.md:123 | source-report | 同一条 data 的 iv | 与 key 的切片重叠，母串仍是占位 |
| C7 | 32 字符母串，占位 | s4 ./ai-assisted-20260901-01.md:123 | source-report | 来源对 M 的长度说明 | 不是密钥本身 |
| C8 | RC4(key) → UTF-8 → base64 | s1 ./ai-assisted-20260901-01.md:59 | source-report | 来源所称 ltk 与 adi | 具体 key 未给出 |
| C9 | c % 5 决定把 v % 64 加在算法的哪一步 | s6 ./ai-assisted-20260901-01.md:155 | source-report | 来源所称握手内层 RC4 | 只有步骤选择，没有每步算式 |
| C10 | 主体结构一字不动，就在某一两个固定位置注入一个和环境相关的扰动量。 | s6 ./ai-assisted-20260901-01.md:159 | source-report | 作者对这类魔改的认法 | 不是已核对的字节级差分 |
| C11 | 由一个 KDF 从 | s7 ./ai-assisted-20260901-01.md:165 | source-report | deNewKey1 / newKey3 的来源描述 | 输入写成 (sk, sm, ua)，式子未闭合 |
| C12 | 跨会话不变 | s7 ./ai-assisted-20260901-01.md:176 | source-report | 来源所称 newKey3 | 不外推到其它 key |
| C13 | 随 d 变 | s7 ./ai-assisted-20260901-01.md:177 | source-report | 来源所称 deNewKey1 | d 的取值顺序没有独立核对 |

<a id="request-chain"></a>
## 请求顺序与响应层次

先有 `sign`，再把实际发出的 body 字符串交给 `hsn`。设备凭证来自 `/webSk` 响应，来源按 gzip、大写 hex、AES-256-CBC、base64、魔改 RC4 的次序剥到 JSON。来源还写：这条解密链可变输入已经在自己发出的 `dsn` 里。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C14 | 严格的顺序依赖 | s2 ./ai-assisted-20260901-01.md:84 | source-report | sign 与 hsn | 改业务参数会同时带动两层 |
| C15 | 要用实际发出去的那个 body 串。 | s2 ./ai-assisted-20260901-01.md:90 | source-report | hsn 的 requestBody | 来源禁止自行重排序列化 |
| C16 | 响应五层解密后才拿得到 | s1 ./ai-assisted-20260901-01.md:60 | source-report | sk / ak / sm | 层密钥不是本卡补全的 |
| C17 | 因为它套了五层： | s5 ./ai-assisted-20260901-01.md:135 | source-report | /webSk 响应 | 作者给出的长度是自述 |
| C18 | gzip（网络传输层） | s5 ./ai-assisted-20260901-01.md:138 | source-report | 五层中的第一层 | 来源标成传输层 |
| C19 | 大写 hex 解码成字节 | s5 ./ai-assisted-20260901-01.md:139 | source-report | 五层中的第二层 | 未保存样本密文 |
| C20 | AES-256-CBC/Pkcs7 解密 | s5 ./ai-assisted-20260901-01.md:140 | source-report | 五层中的第三层 | key 名是 deNewKey1 |
| C21 | iv = key 的前 16 字符 | s5 ./ai-assisted-20260901-01.md:140 | source-report | 同一层 iv | 不套用到 data 那条 AES |
| C22 | base64 解码 | s5 ./ai-assisted-20260901-01.md:141 | source-report | 五层中的第四层 | 只是次序名 |
| C23 | 魔改 RC4 | s5 ./ai-assisted-20260901-01.md:142 | source-report | 五层中的第五层 | key 名是 newKey3 |
| C24 | 本来就在自己发出去的 | s7 ./ai-assisted-20260901-01.md:179 | source-report | 来源对 sm 与 dsn 的关系 | 不表示业务请求已被接受 |

<a id="interfaces"></a>
## 接口与载体

开页时 POST `/webSk`，body 复用第二节的 `sign`。请求头 `dsn` 带 `sm`、`sk` 和 SDK 版本号。载体是 eval 出来的混淆脚本，来源写明 CryptoJS 调用看得见，并且不是 JSVMP。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C25 | POST 一个握手接口 | s5 ./ai-assisted-20260901-01.md:131 | source-report | 来源所称 /webSk | 没有完整 URL |
| C26 | 复用第二节那个函数 | s5 ./ai-assisted-20260901-01.md:132 | source-report | 握手 body 的 sign | 不是另一套签名 |
| C27 | SDK 版本号 | s5 ./ai-assisted-20260901-01.md:132 | source-report | dsn 里的 bcv | 版本串的值未记录 |
| C28 | obfuscator.io 控制流平坦化 | s1 ./ai-assisted-20260901-01.md:62 | source-report | 来源所称约 515KB SDK | 不覆盖同页其它脚本 |
| C29 | CryptoJS 的调用明文可见 | s1 ./ai-assisted-20260901-01.md:63 | source-report | 同一 SDK | 来源同时写明不是 JSVMP |

<a id="validation"></a>
## 作者对照

作者把通过标准写成逐字节相同，而不是请求跑通。冷启动后凭证会变，加密 key 被写成不变，并据此推断加密方向的 key 来自静态母串。同一段写明：算法复现和离线解密做到了，拿业务成功响应这一步没走通。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C30 | 验证是逐字节对的，不是"跑通了"就算： | s8 ./ai-assisted-20260901-01.md:193 | source-report | 作者的验收口径 | 本次未重跑 |
| C31 | 逐字节相同 | s8 ./ai-assisted-20260901-01.md:195 | source-report | 作者对 sign / hsn 的自述 | 没有附请求样本 |
| C32 | 逐字节一致 | s8 ./ai-assisted-20260901-01.md:196 | source-report | 作者对 KDF 十个输出的自述 | 十个名字没有在本卡展开 |
| C33 | 冷热完全相同 | s7 ./ai-assisted-20260901-01.md:188 | source-report | 作者的四次冷启动对照 | 只涉及客户端加密 key |
| C34 | 是静态母串算出来的 | s7 ./ai-assisted-20260901-01.md:189 | source-report | 作者对加密方向 key 的推断 | 与握手解密 key 不是同一句话 |
| C35 | 用复现值去发真实请求拿 200 | s8 ./ai-assisted-20260901-01.md:198 | source-report | 作者未完成的下一步 | 不能当成已经通过 |
| C36 | 这一步我没走通，卡在一个服务端会话校验上 | s8 ./ai-assisted-20260901-01.md:199 | source-report | 同一边界 | 会话校验的字段来源没有定位 |

<a id="decision-flow"></a>
## 排查顺序

常量 grep 不到时，来源先改判断书写形态，而不是先假定运行时重编码。同一页多条 AES 不能混用母串。断点锚在稳定属性名上。断点计数为零不能当成该层没发生。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C37 | 常量在源码里写成了 | s3 ./ai-assisted-20260901-01.md:99 | source-report | 来源这次的 SALT、母串、RC4 key | 转义只是三种书写形态之一 |
| C38 | grep 不中，先怀疑常量的书写形态 | s3 ./ai-assisted-20260901-01.md:109 | source-report | 作者给出的排查顺序 | 不是所有混淆都如此 |
| C39 | 同一个页面里同一个算法有多把 key | s4 ./ai-assisted-20260901-01.md:126 | source-report | 来源遇到的并发 AES | 没有列出每把 key 的用途表 |
| C40 | KDF 输出对象的属性名是稳定的 | s7 ./ai-assisted-20260901-01.md:182 | source-report | 作者的断点锚点 | 变量名仍会漂 |
| C41 | 别把"断点没记到"当成"没发生" | s8 ./ai-assisted-20260901-01.md:202 | source-report | 作者挂在加密块上的计数 | 漏计原因来源写明没查清 |

## 验证与限制

不把本卡当成签名器或握手解密器。`newKey1` 在式子里出现，但同段没有从四条母串推出它的步骤；RC4 扰动只写了落在哪一类步骤。作者的逐字节自述保持来源报告。业务响应那一步来源自己写了没走通。换脚本版本后，占位常量、属性名和切片都要重对。
