---
schema_version: 2
id: momo-x-sign-aes-cbc
document_type: reference
original_date: 附件笔记（随 2025 安卓案例索引）
archived_date: '2026-09-06'
scope:
  targets:
    - momo-x-sign
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./momo-x-sign-aes.md#案例边界"
    basis: source-report
  - id: s2
    ref: "./momo-x-sign-aes.md#派生规则"
    basis: source-report
  - id: s3
    ref: "./momo-x-sign-aes.md#x-sign-本体与-map_id"
    basis: source-report
  - id: s4
    ref: "./momo-x-sign-aes.md#边界"
    basis: source-report
  - id: s5
    ref: "./momo-x-sign-aes.md#收录说明"
    basis: source-report
  - id: s6
    ref: "./momo-x-sign-aes.md#hook-窗口只记点不贴脚本"
    basis: source-report
  - id: s7
    ref: "./momo-x-sign-aes.md#陌陌-x-sign-第一参aes-cbc-与-sha1-拼接"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s7]
    basis: source-report
    limits: Java、JNI 和 SO 名字来自来源笔记。未打开样本包，未核对当前导出。
  - name: parameters
    anchor: parameters
    sources: [s2, s3, s6]
    basis: source-report
    limits: key/IV 切片、7 字节前缀、SHA1 拼接和 map_id 形状都是来源观察。未重算，样本 RVA 不能外推。不收录设备 JSON 和 invoke。
  - name: validation
    anchor: validation
    sources: [s4, s5, s6]
    basis: source-report
    limits: 第一参闭合、空桩和 RVA 重核是来源自己的边界。未做对照，也不能把来源的失败常量当成当前包的验收。
relations:
  - type: derived_from
    target: "./momo-x-sign-aes.md#陌陌-x-sign-第一参aes-cbc-与-sha1-拼接"
tags:
  - momo
  - x-sign
  - AES-128-CBC
---

# 陌陌 x-sign 第一参的 AES-CBC 形状

这张卡只回答：来源笔记把陌陌 `x-sign` 第一参放在哪几个符号上，key 材料怎么切，以及本体 SHA1 和 `map_id` 与这段 AES 不是同一个函数。不提供主动调用，不收录设备字段。

tag `x-sign` 命中的参数卡是阿里 MTOP / InnerSignImpl，target 不是 `momo-x-sign`。本篇没有从前提走到失败出口的五段，所以不是流程。

<a id="interfaces"></a>
## 入口与 SO

Java 入口是 `com.immomo.momoenc.e.a(byte[], Map, String)`。JNI 封装是 `com.immomo.momo.util.jni.Coded`。Native 名是 `a49kdEba83h(byte[] in, int inLen, byte[] keyMat, int keyMatLen, byte[] out)`，返回值是 `out` 的有效长度。

`aesEncode` 在 `libcoded_jni.so` 里是导入。实现在 `libcoded.so`，轮密钥和 CBC 在 `libmmcrypto.so`。正常加载顺序是 `mmcrypto`、`mmssl`、`coded`、`coded_jni`；调试开关改走 `testcoded`。`coded_jni` 里的空桩是导入函数，要按导入表进 `libcoded.so`，不要对着空实现猜 key 长度。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 第一参从 Java `e.a` 进 `Coded.aesEncode` | s7 第 33 行：Java 入口 `com.immomo.momoenc.e.a` 先把一段 JSON 明文送进 `Coded.aesEncode` | source-report | 来源样本的第一参 | 未附加进程 |
| C2 | Native 符号接收 keyMat 并返回 out 长度 | s1 第 45 行：`a49kdEba83h(byte[] in, int inLen, byte[] keyMat, int keyMatLen, byte[] out) -> int` | source-report | 来源记的 JNI 名 | 未对当前包导出 |
| C3 | 真正的 aesEncode 在 libcoded.so，CBC 在 libmmcrypto.so | s1 第 46 行：`libcoded.so` 真正做 `aesEncode`；轮密钥/CBC 在 `libmmcrypto.so` | source-report | 来源样本的加载链 | 未读导入表 |
| C4 | 正常加载四名，调试开关改走 testcoded | s1 第 47 行：正常路径依次 `mmcrypto` / `mmssl` / `coded` / `coded_jni` | source-report | 来源写的正常路径 | 未观察加载 |
| C5 | 空桩是导入，不能用来猜 key 长度 | s1 第 49 行：不要对着空实现猜 key 长度。 | source-report | `coded_jni` 里的 `aesEncode` | 未读导入表 |

<a id="parameters"></a>
## 缓冲区与两段摘要

来源把第一参记成 AES-128-CBC，不是整包自定义算法。`keyMat` 观察长度 48：前 16 字节是 key，16–31 是已经填好的 IV，其余不进 CBC。IV 在 `libcoded.so` 的 `aesEncrypt` 一层生成或填入。来源写的派生是：key 取 `keyMat[0:16]`；IV 是 4 字节伪随机的 SHA1 前 16 字节；CBC 之后再拼 7 字节前缀；笔记所称 mzip 实为标准 Base64。`rand4` 来自 `time(0)` 加 `srand` / `rand()+1`，作者认为可以换成任意 4 字节。

`AES_set_encrypt_key` 的样本 RVA 是 `0x843A0`，初始 key 等于 `keyMat[0:16]`。`AES_cbc_encrypt` 的样本 RVA 是 `0x85848`，IV 等于 `keyMat[16:32]`。`aesEncode` 样本 RVA `0x2EDC`，输出比内层 CBC 多 7 字节前缀。

`x-sign` 本体不是这段 AES。来源写扁平化函数在校验魔数后做 `SHA1( src[0:n] || uint64_from(a2) )`，对应导语里的「明文后拼 8 字节」。`a5 == -871603923` 时直接失败返回。其余同类 native 头没有继续拆。

`map_id` 在 Java：`now_ms % 1_000_000`，小于 `100_000` 则加 `100_000`，再拼 `randint(1000, 9999)` 的十进制串。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 初始 key 是 keyMat 前 16 字节 | s6 第 59 行：初始 key = `keyMat[0:16]` | source-report | 来源样本的 AES_set_encrypt_key | RVA `0x843A0` 必须重核 |
| C7 | CBC 的 IV 是 keyMat 的 16:32 | s6 第 60 行：IV = `keyMat[16:32]` | source-report | 来源样本的 AES_cbc_encrypt | RVA `0x85848` 必须重核 |
| C8 | aesEncode 输出比内层 CBC 多 7 字节前缀 | s6 第 57 行：输出比内层 CBC 多 7 字节前缀 | source-report | 来源样本的 libcoded.so aesEncode | RVA `0x2EDC` 必须重核 |
| C9 | 笔记把 IV 写成 4 字节伪随机的 SHA1 前 16 字节 | s2 第 68 行：`iv      = SHA1(rand4)[:16]` | source-report | 来源文本里的派生块 | 未重算 SHA1 |
| C10 | keyMat 观察长度为 48，32 字节之后不进 CBC | s2 第 74 行：`keyMat` 观察长度为 48：前 16 是 key，16–31 是填好的 IV，其余未参与 CBC。 | source-report | 来源当时的缓冲区 | 未重新采样 |
| C11 | x-sign 本体是明文拼接 8 字节后的 SHA1 | s3 第 81 行：`SHA1( src[0:n] || uint64_from(a2) )` | source-report | 来源写的扁平化函数 | 不是第一参 AES |
| C12 | 该魔数使函数直接失败返回 | s3 第 84 行：`a5 == -871603923` 时直接失败返回。 | source-report | 来源未继续拆的 native 头 | 未在当前包核对立即数 |
| C13 | map_id 是毫秒尾数再拼四位随机十进制 | s3 第 91 行：`map_id = str(t) + str(randint(1000, 9999))` | source-report | 来源写的 Java map_id | 未采样时钟 |

<a id="validation"></a>
## 什么不能当成闭合

作者只闭合了第一参。同类 native 参数没有拆完。样本 RVA 必须按当前 `libcoded.so` / `libmmcrypto.so` 重核，不能套观察偏移。`onLeave` 当时经常打不出来，以 `onEnter` 缓冲和返回长度为准，不要把「没 leave」写成函数没跑完。第一参闭合不等于整个 `x-sign` 头已经验收。来源明确不收录设备 JSON、主动调用字节数组和完整 invoke。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C14 | 来源只闭合第一参 | s5 第 37 行：作者只闭合了 `x-sign` 第一参 | source-report | 这篇附件笔记 | 其余 native 头未知 |
| C15 | RVA 必须按当前 SO 重核 | s6 第 62 行：RVA 必须按当前 SO 重核。 | source-report | 表内全部观察 RVA | 未重核 |
| C16 | 换包先重核两个 SO 的导出，不套观察偏移 | s4 第 98 行：换包先重核 `libcoded.so` / `libmmcrypto.so` 导出与 RVA，不要套观察偏移。 | source-report | 后续换包 | 未换包 |
| C17 | 没打出 onLeave 不等于函数没跑完 | s6 第 62 行：不要把「没 leave」写成函数没跑完。 | source-report | 来源当时的 hook 观察 | 未复挂 |

## 验证与限制

未打开 APK，未计算 SHA1 或 AES，未核对魔数。设备字段名和原值都不进入本卡。阿里 MTOP 的 `x-sign` 不能填到这条链。样本当时有没有抓包或 Frida 检测，只是来源对那一个包的自述，不能外推。
