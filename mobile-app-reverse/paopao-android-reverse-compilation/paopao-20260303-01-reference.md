---
schema_version: 2
id: paopao-music-xxx-eapi-reference
document_type: reference
original_date: '2026-03-03'
archived_date: '2026-07-13'
scope:
  targets: [interface3.music.xxx.com]
  client: android
  version: '8.8.50'
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260303-01.md#二目标音乐app-的防抓包策略路由直连"
    basis: source-report
  - id: s2
    ref: "./paopao-20260303-01.md#二请求结构分析"
    basis: source-report
  - id: s3
    ref: "./paopao-20260303-01.md#13-定位核心加密函数-serialdata"
    basis: source-report
  - id: s4
    ref: "./paopao-20260303-01.md#附录caesarson-与标准-aes-gcm-对比"
    basis: source-report
  - id: s5
    ref: "./paopao-20260303-01.md#unidbg-验证结果"
    basis: source-report
  - id: s6
    ref: "./paopao-20260303-01.md#一参数定位"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只记录这篇里目标音乐 App 的路由直连。附录里的证书固定属于另一款短视频样本，不是这个 host 的控制面。Postern 绕过没有验收。
  - name: interfaces
    anchor: interfaces
    sources: [s2]
    basis: source-report
    limits: 只覆盖歌曲搜索这一条 eapi。域名已按来源脱敏。Cookie 原值不收录。
  - name: request-chain
    anchor: request-chain
    sources: [s3, s6]
    basis: source-report
    limits: 类名按来源脱敏。params 的「下」篇未归档，所以链停在 native 入口和导出表，不包含可独立计算的 params 算法。
  - name: parameters
    anchor: parameters
    sources: [s2, s3, s4, s5]
    basis: source-report
    limits: deviceId、NMCID、NMDI 外形来自来源报告。不收录 so 内密钥字节、Cookie、Token 或指纹原值。作者给出的 caesarson 实现本轮未复算。
relations:
  - type: derived_from
    target: "./paopao-20260303-01.md#二请求结构分析"
tags: [eapi, serialdata, nmdi, source-report]
---

# 目标音乐 App 的 eapi 搜索：路由直连、params 入口与 NMDI 外形

这张卡只回答三件事：歌曲搜索请求长什么样，`params` 和响应解密停在哪个 native 入口，以及 Cookie 里的 NMDI 被来源描述成什么外形。来源是合并后的 [协议抓包到 NMDI](./paopao-20260303-01.md#二请求结构分析)。近邻 `anonymous Android music App (source report)` 的卡是另一篇 dfid 注册，不覆盖这个 host。

params 算法的下篇和系列第四篇都没有归档。来源末尾的 Python 框架仍是 `TODO`。没有验收，也没有失败出口，所以不是 procedure。依据保持 source-report。

<a id="risk-control"></a>
## 防抓包

来源把目标音乐 App 的现象写成路由直连：系统代理配好后 Charles 没有该 App 的条目，但播放和搜索仍可用。反编译里搜索 `http.route.default-proxy`，构建 `HttpClient` 时把该参数设为不使用代理。同文的策略表还列了代理检测、VPN 检测和证书固定，但后文只把路由直连落到这个 App。证书固定附录写的是另一款短视频样本的 native 校验，不能算这个 host 的控制。

来源的绕过叙述是用 Postern 的 TUN 把流量转到 Charles。这是作者步骤，没有通过条件。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 策略表里的路由直连是在 HttpClient 层禁用系统代理 | `在 HttpClient 层显式禁用系统代理` | s1 ./paopao-20260303-01.md:65 | source-report | 表是综述，落实点在下一行 |
| C2 | 该 App 把 http.route.default-proxy 设为不走代理 | `http.route.default-proxy` | s1 ./paopao-20260303-01.md:89 | source-report | 原句后半在下一物理行，图中的代码未随文保存 |

<a id="interfaces"></a>
## 歌曲搜索接口

样本版本写的是 `8.8.50`。搜索是 `POST`，域名 `interface3.music.xxx.com`，路径 `/eapi/search/song/page`，`Content-Type` 为 `application/x-www-form-urlencoded`。`/eapi/` 被写成 Android 客户端命名空间，用来区别网页端 `/api/`。

来源点名的头有 `user-agent`、`cmpageid`、`mconfig-info`、`x-mam-custommark`（值为 `cronet`）。正文只有一个字段 `params`。响应体也被写成加密，不是明文 JSON。Cookie 字段名可作检索，原值不进入本卡。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C3 | 搜索方法是 POST | `POST` | s2 ./paopao-20260303-01.md:263 | source-report | 只这一条接口 |
| C4 | 路径是 /eapi/search/song/page | `/eapi/search/song/page` | s2 ./paopao-20260303-01.md:264 | source-report | 与下文 serialdata 的入参路径不是同一个字符串 |
| C5 | /eapi/ 被写成 Android 专用命名空间 | `/eapi/` | s2 ./paopao-20260303-01.md:268 | source-report | 网页端对照是同句里的 /api/ |

<a id="request-chain"></a>
## 调用链

`params` 由 OkHttp 拦截器 `com.example.music.network.retrofit.q.a.intercept` 生成，最终调用 `MusicUtils.serialdata(String, String)`。Hook 到的两个入参是路径和明文 JSON，返回大写十六进制。RegisterNatives 把 `serialdata` 放在 `libmusic_core.so` 偏移 `0x4e041`，响应解密 `deserialdata` 在同库 `0x4e125`。该偏移在修复后的 so 里仍不能 F5。导出表有明文 `MD5_*` 与 `AES_encrypt` 等符号。来源把算法判断停在 AES 加 MD5，并写明下篇才还原明文和密钥。打包 so 的 ELF 头被破坏，来源的修复顺序是内存 dump、手工补魔数、再跑 SoFixer。

NMDI 不走这条链。Jadx 搜到 `com.example.music.core.security.c.intercept`，再进 native `CaesarsonCryptor.encrypt`，实现在 `libcaesarson.so`。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C6 | params 拦截器类名 | `com.example.music.network.retrofit.q.a.intercept` | s3 ./paopao-20260303-01.md:573 | source-report | 包名已脱敏 |
| C7 | 核心函数是两个字符串参数的 serialdata | `MusicUtils.serialdata(String str1, String str2)` | s3 ./paopao-20260303-01.md:586 | source-report | 入参路径样例是 `/api/search/song/page`，不是线上 `/eapi/` |
| C8 | serialdata 在 libmusic_core.so 的偏移 | `0x4e041` | s3 ./paopao-20260303-01.md:768 | source-report | 同库响应解密在下一行 |
| C9 | deserialdata 偏移 | `0x4e125` | s3 ./paopao-20260303-01.md:769 | source-report | 只给偏移，没有算法 |
| C10 | NMDI 的 Java 拦截器 | `com.example.music.core.security.c.intercept` | s6 ./paopao-20260303-01.md:989 | source-report | 真正加密在 libcaesarson.so |

<a id="parameters"></a>
## params、设备字段与 NMDI 外形

`params` 是十六进制大写载荷。来源猜测明文含关键词和分页，但本篇没有把密钥和拼接定下来。`serialdata` 的路径样例是 `/api/search/song/page`，请求体样例含 `keyword`、`offset`、`limit`、`e_r`。

`deviceId` 的明文被写成四个制表符字段：15 位 IMEI、MAC、16 位十六进制 android_id、native_id，再做 Base64。来源称 `JNIFactory` 的 native_id 可以传空字符串。`NMCID` 的形状是 `{6位随机字符串}.{13位毫秒时间戳}.01.4`，字符集仍写着待确认。`__csrf`、`MUSIC_A`、`NMTID` 只有长度印象，没有算法。

NMDI 的加密输入是 JSON，键为 `ie`、`mc`、`ydid`。来源对 `ie` 保留 TAC 前 8 位，对 `mc` 保留 OUI 前 3 字节，并把 `ydid` 暂当 32 位十六进制。输出被描述为 AES-GCM 变体：魔数 `CSJM`，12 字节 nonce，CTR 的 counter 从 2 开始，末尾 16 字节认证标签，整体 Base64。so 内的固定密钥字节不写入本卡。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C11 | params 是大写十六进制核心载荷 | `核心加密载荷` | s2 ./paopao-20260303-01.md:279 | source-report | 密文样例不收录 |
| C12 | deviceId 明文是四段制表符拼接 | `<IMEI(15位)>\t<MAC地址>\t<android_id(16位hex)>\t<native_id(16位hex)>` | s2 ./paopao-20260303-01.md:334 | source-report | 没有真实设备值 |
| C13 | NMCID 的可见形状 | `{6位随机字符串}.{13位毫秒时间戳}.01.4` | s2 ./paopao-20260303-01.md:350 | source-report | 随机串字符集来源自己标成未确认 |
| C14 | serialdata 入参路径样例带 /api/ 而不是 /eapi/ | `/api/search/song/page` | s3 ./paopao-20260303-01.md:632 | source-report | 只是一次 Hook 样例 |
| C15 | caesarson 被写成 AES-GCM 变体 | `AES-GCM 变体` | s5 ./paopao-20260303-01.md:1323 | source-report | 认证是来源说的自实现 GHASH，不是已对照的标准 GCM |
| C16 | CTR 的 counter 从 2 开始 | `CTR（counter 从 2 开始）` | s4 ./paopao-20260303-01.md:1793 | source-report | 对照表是作者归纳 |
| C17 | 输出魔数是 CSJM | `CSJM` | s5 ./paopao-20260303-01.md:1312 | source-report | 同行字节是 0x43 0x53 0x4a 0x4d |

## 验证与限制

不覆盖 dfid 注册那张卡。params 的密钥、填充和 MD5 输入不在本篇。`deviceIdYD`、`deviceIdZX` 未定。响应解密只给了偏移。作者的 unidbg 字节对照和 Python 类没有在本轮运行。so 密钥、Cookie、Token 和指纹原值故意不抄。
