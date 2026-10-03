---
schema_version: 2
id: anjuke-17281-nsign-four-part
document_type: reference
original_date: '2025-11-22'
archived_date: '2026-10-02'
scope:
  targets: [com.anjuke.android.app]
  client: Android
  version: '17.28.1'
  observed_at: unknown
sources:
  - id: s1
    ref: ./xfq-20251122-01.md#四段结构
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 四段形状和一位改写只按来源对 17.28.1 的描述。fixed32 原文不给值，key 顺序也没有被证明。
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: Java 名和两处 RVA 只对作者当时的 32 位 libsignutil.so。未重核导出。
  - name: risk-control
    anchor: load-window
    sources: [s1]
    basis: source-report
    limits: 只记加载期观察点。同族判断已在豆瓣卡，本卡不写替换脚本。
  - name: validation
    anchor: boundaries
    sources: [s1]
    basis: source-report
    limits: 来源把本地 56 字符只当作形状。本轮没有业务回读。
relations:
  - type: derived_from
    target: ./xfq-20251122-01.md#四段结构
tags: [nsign, md5, libsignutil, source-report]
---

# 安居客 17.28.1 nsign 的四段与一位改写

这份参考卡回答：`com.anjuke.android.app` 17.28.1 的 `nsign` 在来源里被拆成哪四段，以及 `SignUtil.getSign0` 落在哪个 SO。它不提供 `fixed32`，不提供设备字段取值，也不提供过检测脚本。来源是 [安居客 nsign 归档](./xfq-20251122-01.md#四段结构)。

<a id="parameters"></a>
## 参数机制

来源把输出写成 56 字符：`固定 `1000` + 改写后的 32 位 MD5 + 12 位长度/计数 nibble + `str3` UUID 前 8 位`。结构式是 `nsign = "1000" + mutated_md5(32) + nibbles(12) + uuid[:8]`。前缀在 SO 里是 `0x31 0x30 0x30 0x30`。

明文被写成 `fixed32 || path || bodyHash || concat(map_kv)`。`fixed32` `必须从当前 SO 回读，文内不写具体值`。key 顺序 `不是` 已证明的 `TreeMap` / `LinkedHashMap` 排序。搜索列表的名字只说明字段集合，`不进知识库`。

`SIGNMD5` 先出标准 32 hex，再 `d[ord(d[0]) & 0xF] = d[0]`。汇编对应把 `utf[4]` 写回 `utf[4 + (first & 0xF)]`。

`utf[36:48]` 用 `'0123456789abcdef'` 编码三个 16 位量：Java `flag`、map 的 key/value 字节长度和、`map.size()`。`utf[48:56] = str3[:8]`，来源说这是去掉连字符的 `UUID.randomUUID()` 前 8 个十六进制字符。

<a id="interfaces"></a>
## 调用面

Java 入口是 `com.anjuke.mobile.sign.SignUtil.getSign0`。Native 是 `libsignutil.so`，`观察样本为 32 位 Thumb`，静态注册。

`getSign0(path, bodyHash, map, uuid, flag)`：`path` 是接口路径，`map` 是 `Map<String, byte[]>`，`uuid` 是本次随机 `str3`，`flag` `观察为 `0``。空 POST 体的 `bodyHash` 来源写成标准空串 MD5。

`SIGNMD5` 的观察 RVA 是 `0x10FC`，Thumb 入口 `+1`。一位改写的观察指令点是 `0x1B30`。来源写明 `不要把 `base+0x10FC` 抄到新包`。

<a id="load-window"></a>
## 加载期观察

17.28.1 上，来源说通用抓包插件可以过证书校验，Frida 则可能在 `libmsaoaidsec.so` 加载期闪退。可复用的判断与豆瓣同族，已有卡片是 `../reversenotes-android-compilation/douban-hmac-sig.md`，目标不是本包。

本篇只多记三件观察：`dlopen` / `android_dlopen_ext` 上该 SO `常有 enter 无 leave`；下一步看 `soinfo::call_constructors`；再看 `pthread_create` 的 `start_routine` 是否落在 `libmsaoaidsec.so`。作者当时的三个 RVA 是 `0x11e1d` / `0x127f1` / `0x19c09`，`换 SO 必须重核`。来源写明不收录把这些地址替换成空函数的脚本。

<a id="boundaries"></a>
## 验证与限制

来源写 `本地拼出 56 字符只证明形状`，业务回读仍然要做。58 同系即使共用 `libsignutil.so`，也要先核版本和 `fixed32`，`不要直接套 17.28.1`。本轮没有打开该 SO，也没有业务回读。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 输出是 `固定 `1000` + 改写后的 32 位 MD5 + 12 位长度/计数 nibble + `str3` UUID 前 8 位`。 | s1 第 33 行 | source-report | 17.28.1 的 nsign | 未按该形状组包 |
| C2 | `fixed32` `必须从当前 SO 回读，文内不写具体值`。顺序 `不是` 已证明的 TreeMap / LinkedHashMap。 | s1 第 79 行 | source-report | 该样本的拼接 | 常量值不在正文 |
| C3 | 改写是 `d[ord(d[0]) & 0xF] = d[0]`，写回 `utf[4 + (first & 0xF)]`。 | s1 第 95、99 行 | source-report | 来源描述的标准 MD5 之后 | 未对压缩函数做静态对照 |
| C4 | `utf[36:48]` 编码 flag、字节长度和、`map.size()`。`utf[48:56] = str3[:8]`。 | s1 第 103、107 行 | source-report | 56 字符的后 20 位 | 未核对 nibble 端序 |
| C5 | 入口是 `SignUtil.getSign0`，SO 为 `libsignutil.so`，样本 `32 位 Thumb`。 | s1 第 45、46 行 | source-report | 17.28.1 | 未重核导出 |
| C6 | `SIGNMD5` 观察 RVA `0x10FC`，改写点 `0x1B30`。`不要把 `base+0x10FC` 抄到新包`。 | s1 第 56、57、59 行 | source-report | 作者当时的 SO | 换版本即失效 |
| C7 | `libmsaoaidsec.so` 可能在加载期闪退。三个 start_routine RVA `换 SO 必须重核`。 | s1 第 111、117 行 | source-report | 17.28.1 的观察窗口 | 不提供替换脚本 |
| C8 | `本地拼出 56 字符只证明形状`。同系 SO `不要直接套 17.28.1`。 | s1 第 121、123 行 | source-report | 来源自己的边界 | 本轮没有业务回读 |
