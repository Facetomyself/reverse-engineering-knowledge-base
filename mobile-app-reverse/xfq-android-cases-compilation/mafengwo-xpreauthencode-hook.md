---
schema_version: 2
id: mobile-app-reverse-xfq-android-cases-compilation-mafengwo-xpreauthencode-hook
document_type: reference
scope:
  targets:
  - mafengwo
  client: Android native/JNI
  version: unknown
  observed_at: unknown
sources:
- id: s1
  ref: null
  basis: source-report
  citation: 知识星球：逆向学习交流（安居客/陌陌/马蜂窝附件笔记）
  reason: 原归档明确记载出处，但未提供可定位的公开来源链接；本轮只保留来源自述。
source_completeness: unknown
modules:
- name: parameters
  anchor: mafengwo-xpreauth-canonical
  sources: [s1]
  basis: source-report
  limits: canonical 的动态 host/token/nonce/设备字段须按当前请求重取；未闭合完整输入值。
- name: request-chain
  anchor: mafengwo-hook-observation
  sources: [s1]
  basis: source-report
  limits: Java/native/unidbg 窗口与 RVA 来自来源样本；RVA 必须按当前 libmfw.so 重核。
- name: validation
  anchor: mafengwo-validation-boundary
  sources: [s1]
  basis: source-report
  limits: 40 hex 不等于 serverAccepted；不得把修改返回值跳过校验当成验收。
tags: [mafengwo, xpreauthencode, jni, unidbg]
original_date: 附件笔记（随 2025 安卓案例索引）
archived_date: '2026-09-06'
---

# 马蜂窝 zzzghostsigh：xPreAuthencode hook 窗口

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: 知识星球：逆向学习交流（安居客/陌陌/马蜂窝附件笔记）
> 原始发布时间: 附件笔记（随 2025 安卓案例索引）
> 归档日期: 2026-09-06
> 分类: mobile-app-reverse
</details>
>
> `zzzghostsigh` 的 Java 入口是 `AuthorizeHelper.xPreAuthencode`。动态注册在 `libmfw.so`。入参是 OAuth 风格 canonical 串加包名，出参 40 hex。魔改 SHA1 本身已在签名算法分类闭合，本篇只补 hook 点、JNI 签名和 unidbg 观察窗口。不收录未脱敏 query、设备字段和「改返回值跳过验签」的脚本。

## 收录说明

算法正文见：

- [马蜂窝魔改 SHA1：从 HashFinder 到轮函数分段](../../signature-algorithms/mafengwo-modified-sha1-trace.md)
- [mfw_trace_sha1 学习笔记](../../signature-algorithms/xfq-crypto-notes-compilation/xfq-20260417-02.md)

本篇不重复轮函数差分。附件里的登录 query（含 `oauth_*`、`shumeng_id`、`x_basic_data`）整段去掉。

<a id="mafengwo-xpreauth-canonical"></a>
## 案例边界

| 项 | 内容 |
|---|---|
| Java | `com.mfw.tnative.AuthorizeHelper.xPreAuthencode` |
| JNI | `(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;` |
| Native | `libmfw.so`，观察 RVA `0x396c8` |
| 入参 | `Context`；OAuth canonical 串；包名（观察为 `com.mfw.roadbook`） |
| 出参 | 40 hex（魔改 SHA1） |

canonical 形状：

```text
METHOD & urlencode(url) & urlencode(sorted_params)
```

`METHOD` 观察为 `PUT`。具体 host、token、nonce、设备字段按当前请求重取，不要复用附件原文。

定位路径：搜业务头 → hook 接口实现类（笔记落到 `kh.b` / `kh.a`）→ 跟到上述 native。混淆短名会随版本变，以 `xPreAuthencode` 和 JNI 签名为准。

<a id="mafengwo-hook-observation"></a>
## Hook 窗口（只记点，不贴脚本）

| 点 | 观察样本 | 看什么 |
|---|---|---|
| Java `xPreAuthencode` | 动态注册 | `str` 是否已是 canonical；返回是否 40 hex |
| `libmfw.so` 注册偏移 | `0x396c8` | 与 `RegisterNatives` 对得上再跟 |
| unidbg 压缩入口 | `0x3E1D0` | `x0` 五个魔数、`x1` 输入缓冲；练习输入可用 `123456` |
| unidbg 签名校验 | `sub_3C9C4` | 失败路径 `NewStringUTF(..., "Illegal signature")` |

RVA 必须按当前 `libmfw.so` 重核。练习稿用 `123456` 的对照输出见 SHA1 主文，不要把业务 query 的 40 hex 写进知识库。

## unidbg 观察（不是绕过步骤）

作者在补环境时撞上 APK 签名校验：`!v7` 为真就返回 `"Illegal signature"`。可复用的判断是：

- 先确认失败字符串是不是这条
- 再决定补 `vm.getSignatures()` / v2 签名读取，还是换能取出签名数组的样本

不要把「hook 该函数直接改返回值并跳出」写成已过校验。11.4.4 上 unidbg 取空签名数组的原因见 [修复 unidbg 签名数组为空](../../native-analysis/xfq-unidbg-native-compilation/xfq-20260417-01.md)。

<a id="mafengwo-validation-boundary"></a>
## 边界

- hook 出 40 hex ≠ `serverAccepted`。
- 不收录附件 query、设备字段、以及把校验函数改成恒真的脚本。
- 轮函数魔改（Ch/Parity/Maj 错位、H2/H3 对调）只指向签名算法主文。

## 提炼说明（481）
retain 既有马蜂窝 hook 窗口 reference。
40 hex 不是 serverAccepted。
本轮不另建卡。
