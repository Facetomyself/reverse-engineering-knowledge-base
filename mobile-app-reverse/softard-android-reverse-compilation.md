---
schema_version: 2
id: mobile-app-reverse-softard-android-reverse-compilation
document_type: archive
scope:
  targets:
  - unknown
  client: android
  version: unknown
  observed_at: unknown
sources:
- id: s1
  ref: null
  basis: source-report
  citation: 微信公众号：Softard（Wossoneri）
  reason: 原归档明确记载出处，但未提供可定位的公开来源链接；本轮只保留来源自述。
source_completeness: unknown
tags:
- Android权限
- ELF
- ART
- Smali
- OLLVM
- IDA
- UnCrackable
- DEX string_ids
original_date: 多篇合集
archived_date: '2026-09-06'
---

# Softard Android 逆向笔记合集

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: 微信公众号：Softard（Wossoneri）
> 原始发布时间: 多篇合集
> 归档日期: 2026-09-06
> 分类: mobile-app-reverse
</details>
>
> Android 权限模型、ELF/SO、ART、Smali、OLLVM 与 IDA 追算法路径。只收技术稿，不含订阅/会员推广。

## 收录说明

本合集来自微信公众号 Softard（Wossoneri）。只吸收权限系统、ELF/SO、ART、Smali patch、
反调试、OLLVM 与 IDA 追 native 算法的技术笔记。同源 DOCX/HTML/MHTML/PDF 与图片未纳入。
未收录「我需要更多 token」、Claude/ChatGPT 会员推广稿。

## 文章目录（13 篇）

| 日期 | 文章 |
|------|------|
| 2019-01-14 | [Android Framework 权限底层实现概览](softard-android-reverse-compilation/softard-20190114-01.md) |
| 2019-11-18 | [Android 权限系统一](softard-android-reverse-compilation/softard-20191118-01.md) |
| 2025-12-31 | [DEX string_ids_off 崩溃：用汇编对齐 string_data_off](softard-android-reverse-compilation/softard-20251231-01.md) |
| 2026-04-29 | [某厂安全研发的逆向笔记（三）：SO 文件剖析——必须搞懂的 ELF 格式](softard-android-reverse-compilation/softard-20260429-01.md) |
| 2026-05-01 | [某厂安全研发的逆向笔记（5）：ART 虚拟机，你的代码到底怎么跑的](softard-android-reverse-compilation/softard-20260501-01.md) |
| 2026-05-04 | [某厂安全研发的逆向笔记（7）：读懂 Smali，就是读懂 Android 的"汇编"](softard-android-reverse-compilation/softard-20260504-01.md) |
| 2026-05-06 | [某厂安全研发的逆向笔记（8）：新手村实战2，改 Smali 绕过 root 检测，顺便讲点别人不讲的](softard-android-reverse-compilation/softard-20260506-01.md) |
| 2026-05-11 | [某厂安全研发的逆向笔记（9）：新手村实战3，刚出村遇见一只拦路猫](softard-android-reverse-compilation/softard-20260511-01.md) |
| 2026-05-19 | [某厂安全研发的逆向笔记（10）：看不懂伪 C？试试直接读汇编](softard-android-reverse-compilation/softard-20260519-01.md) |
| 2026-05-26 | [某厂安全研发的逆向笔记（11）：IDA 里的"幻觉"——认识代码混淆Ollvm](softard-android-reverse-compilation/softard-20260526-01.md) |
| 2026-06-01 | [某厂安全研发的逆向笔记（11.1）：更多混淆手法与对抗工具](softard-android-reverse-compilation/softard-20260601-01.md) |
| 2026-06-04 | [某厂安全研发的逆向笔记（12）：IDA 逆向 SO 算法的路径](softard-android-reverse-compilation/softard-20260604-01.md) |
| 2026-06-06 | [某厂安全研发的逆向笔记（12.1）：对抗算法特征检索的简单攻防](softard-android-reverse-compilation/softard-20260606-01.md) |

## 提炼说明（472）
TOC hub archive-only。
13 篇子文已逐篇 retain 或 archive。
本轮不另建合集卡。

## 同目录窄参考

本段只挂同目录提炼卡。

- [Android permission 名怎样对到 Linux gid](softard-android-reverse-compilation/softard-20190114-01-reference.md)
- [Android 框架权限的落点与授权分支](softard-android-reverse-compilation/softard-20191118-01-reference.md)
- [DEX string id 崩溃的寄存器对齐](softard-android-reverse-compilation/softard-20251231-01-reference.md)
- [Android SO 的 ELF 字段和 JNI 入口分叉](softard-android-reverse-compilation/softard-20260429-01-reference.md)
- [ART 方法入口与壳介入时机](softard-android-reverse-compilation/softard-20260501-01-reference.md)
- [Dalvik Smali 的寄存器和调用形式](softard-android-reverse-compilation/softard-20260504-01-reference.md)
- [UnCrackable Level 2：libfoo.so 的校验入口、口令门闩和 sub_918](softard-android-reverse-compilation/softard-20260511-01-reference.md)
- [Android SO 混淆：三种进阶手法和工具顺序](softard-android-reverse-compilation/softard-20260601-01-reference.md)
- [IDA 中用特征常量区分 SO 里的标准算法](softard-android-reverse-compilation/softard-20260604-01-reference.md)
- [findcrypt 扫不到常量时，来源怎么把值藏起来又怎么认回去](softard-android-reverse-compilation/softard-20260606-01-reference.md)
