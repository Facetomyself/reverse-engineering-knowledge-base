---
schema_version: 2
id: cn-xla-sms-sign-reference
document_type: reference
original_date: '2025-09-23'
archived_date: '2026-10-02'
scope:
  targets:
    - cn.xla
  client: Android
  version: unknown
  observed_at: '2025-09-23'
sources:
  - id: s1
    ref: "./xfq-20250923-01.md#四个参数的分析"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留 nonce、did、ts、sign 的构造叙述。请求样本里的号码、nonce、did 和 sign 结果不收录。正文在最后一次 MD5 对照前停下，没有并排结果。
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: Java 类名和 so 名来自来源。注释里的 sub_35440 和 hook 用的 0x42A10 不一致，且作者写明先看错了 x86 so。
relations:
  - type: derived_from
    target: "./xfq-20250923-01.md#四个参数的分析"
tags:
  - cn-xla
  - md5
  - source-report
---

# cn.xla 短信头：nonce、did、ts 与 sign 截取

这张卡只回答：来源称为「想恋爱」、包名片段 `cn.xla`、主机 `v3.xla8.cn` 的短信登录头里，四个会变的参数各自怎么来。号码和验证码按来源所说是明文，不进入本卡。抓包里的 nonce、did、sign 样本也不进入本卡。作者没有把最后一次 MD5 的计算结果写完。

<a id="parameters"></a>
## 参数机制

来源写没有加固。两次请求之间，号码不变时会变的是 `nonce`、`did`、`ts`、`sign`。

`nonce` 是 32 位，字符表是数字加大写小写字母共 62 个，下标来自 `q1.g0` 的 `SecureRandom`。来源据此认为不能做种子预测，调用时随机生成即可。

`did` 先按本地身份选前缀和原料：有 phone 则前缀 `M`，否则有 wxId 则 `W`，没有 userId 则 10 位 `Random` 数字加前缀 `S`，否则 userId 加前缀 `U`。`g0.b` 对原料做 MD5，再取 `substring(10)`，拼到前缀后面。来源的 hook 样本不收录。

`ts` 是 `System.currentTimeMillis()` 的十进制字符串。

`sign` 的 Java 入口是 `cn.ezdx.authzut.SignUt.getSignStr(context, treeMap.toString())`，再 `substring(10, 20)`，所以头里只留 10 个十六进制字符。native 在 `libauthz-jni.so`。来源把拼接函数的两个字符串对上：一边是 TreeMap 的 `toString()`，另一边是固定后缀 `802-naxyj9ha-802`。来源的结论是这两段连起来再做 MD5。直接对 TreeMap 字符串做 MD5 对不上，所以后缀是在 so 里加上的。正文停在「进行MD5」，没有把算出的摘要和前面记下的 result 写在一起。

作者还写明自己先分析了 x86 so。注释里的 IDA 名是 `sub_35440`，hook 却加的是 `0x42A10`。这两个数不能当成同一份 arm64 偏移。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 号码和验证码按来源所说是明文 | 毕竟手机号和验证码直接是明文 | s1 :84 | source-report | 样本号码不收录 |
| C2 | 会变的四个头是 nonce、did、ts、sign | nonce did ts sign | s1 :85 | source-report | 未复算 |
| C3 | nonce 用 SecureRandom | new SecureRandom() | s1 :114 | source-report | 32 位与 62 字符表在相邻代码里 |
| C4 | 来源因此把 nonce 当成直接随机 | 因此这个nonce随机生成即可 | s1 :118 | source-report | 未检查 SecureRandom 的 provider |
| C5 | phone 分支前缀是 M | str = "M" | s1 :128 | source-report | 其余前缀在 :131、:138、:141 |
| C6 | did 取 MD5 的 substring(10) 再加前缀 | a10.substring(10) | s1 :147 | source-report | hook 出的 did 样本不收录 |
| C7 | ts 是当前毫秒 | System.currentTimeMillis() | s1 :220 | source-report | 未核对时区 |
| C8 | sign 从 getSignStr 再截取 | SignUt.getSignStr | s1 :229 | source-report | 截取结束下标在下一行 |
| C9 | 截取从下标 10 到 20 | substring(10, | s1 :229 | source-report | 结束下标 20 在 :230，该行后部的样本 sign 不收录 |
| C10 | so 拼接的固定后缀 | 802-naxyj9ha-802 | s1 :322 | source-report | 只此一次 hook 读出 |
| C11 | 来源把拼接结果认成 MD5 | 由此可发现就是简单的拼接后进行MD5 | s1 :423 | source-report | 文末没有把 MD5 结果写完 |
| C12 | so 名 | libauthz-jni.so | s1 :292 | source-report | 未做静态复核 |
| C13 | hook 使用的偏移 | 0x42A10 | s1 :295 | source-report | 与 :294 的 sub_35440 不一致 |
| C14 | 作者写明先看了 x86 so | 分析的是x86的so | s1 :287 | source-report | 偏移因此不能当 arm64 基址 |

<a id="interfaces"></a>
## 来源点名的入口

| 材料 | 来源点名的入口 |
|---|---|
| nonce / did | `q1.g0`，`g0.a` 被 hook 打印成 MD5，`g0.b` 做截取拼接 |
| sign | `cn.ezdx.authzut.SignUt.getSignStr` |
| native | `libauthz-jni.so` |
| 主机 | 来源请求头写 `v3.xla8.cn`；签名 map 里出现 `prt=cn.xla` |

quote：`var SignUt = Java.use('cn.ezdx.authzut.SignUt');`（s1 :239）。

## 验证与限制

主动调用被来源说成返回值不变，但那只说明函数对同一输入稳定，不能代替后缀拼接后的 MD5 对照。正文最后一行仍是「进行MD5」。x86 与偏移不一致，所以本卡不把 `0x42A10` 写成可迁移地址。没有验收反例和失败出口，不收成流程。
