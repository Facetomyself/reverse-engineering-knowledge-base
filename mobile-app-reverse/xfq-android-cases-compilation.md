---
schema_version: 2
id: mobile-app-reverse-xfq-android-cases-compilation
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
  citation: 知识星球：逆向学习交流
  reason: 原归档明确记载出处，但未提供可定位的公开来源链接；本轮只保留来源自述。
source_completeness: unknown
tags:
- Unidbg
- NS_sig3
- 白盒AES
- 小黑盒
- 趣头条
- AppsFlyer
- 安居客 nsign
- 陌陌 x-sign
- 纯算
- signature
original_date: 多篇合集
archived_date: '2026-09-04'
---

# 逆向学习交流安卓实战案例合集

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: 知识星球：逆向学习交流
> 原始发布时间: 多篇合集
> 归档日期: 2026-09-04
> 分类: mobile-app-reverse
</details>
>
> 快手白盒/NS_sig3、小黑盒 hkey、马蜂窝魔改 SHA1、AppsFlyer、安居客 nsign、陌陌 x-sign、趣头条等 App 签名与 unidbg 补环境案例。保留算法定位、hook 点和复现路径，隐去附件、设备字段与可直接跑的过检测脚本。

## 收录说明

本合集只吸收具有逆向工程复用价值的技术稿。星球导航、评论头像、二维码、号池/续杯、破解版软件、附件 zip/PDF 与业务爬取脚本未纳入。

## 文章目录（15 篇）

| 日期 | 文章 |
|------|------|
| 2025-09-22 | [xxss直聘13.160（讲义）](xfq-android-cases-compilation/xfq-20250922-01.md) |
| 2025-09-23 | [x恋爱 笔记（讲义）](xfq-android-cases-compilation/xfq-20250923-01.md) |
| 2025-10-23 | [小黑盒_1.3.368（讲义）](xfq-android-cases-compilation/xfq-20251023-01.md) |
| 2025-11 | [陌陌 x-sign 第一参 AES-CBC](xfq-android-cases-compilation/momo-x-sign-aes.md) |
| 2025-11 | [马蜂窝 xPreAuthencode hook 窗口](xfq-android-cases-compilation/mafengwo-xpreauthencode-hook.md) |
| 2025-11-22 | [安居客 17.28.1 nsign](xfq-android-cases-compilation/xfq-20251122-01.md) |
| 2025-12-05 | [微博绿洲 纯算分析（讲义）](xfq-android-cases-compilation/xfq-20251205-01.md) |
| 2025-12-06 | [16. 最右（讲义）](xfq-android-cases-compilation/xfq-20251206-01.md) |
| 2025-12-14 | [18. 小猿口算 (2)（讲义）](xfq-android-cases-compilation/xfq-20251214-01.md) |
| 2026-01-12 | [18_南银法巴消金（讲义）](xfq-android-cases-compilation/xfq-20260112-01.md) |
| 2026-03-11 | [趣头条签名分析（讲义）](xfq-android-cases-compilation/xfq-20260311-01.md) |
| 2026-04-18 | [航班管家 ai还原 全过程（讲义）](xfq-android-cases-compilation/xfq-20260418-01.md) |
| 2026-05-23 | [AppsFlyer androidevent PBKDF2+AES-CBC](xfq-android-cases-compilation/xfq-20260523-01.md) |
| 2026-07-23 | [不同渠道apk/xapk/apks下载 汇总](xfq-android-cases-compilation/xfq-20260723-01.md) |
| 2026-08-28 | [聊聊ks的白盒](xfq-android-cases-compilation/xfq-20260828-01.md) |

## 提炼说明（493）
TOC hub archive-only。
子文已逐篇处置。
本轮不另建合集卡。

## 同目录窄参考

本段只挂同目录提炼卡。

- [陌陌 x-sign 第一参的 AES-CBC 形状](xfq-android-cases-compilation/momo-x-sign-aes-reference.md)
- [BOSS直聘 13.160：sig 加盐 MD5 与 sp 的 LZ4、RC4、码表替换](xfq-android-cases-compilation/xfq-20250922-01-reference.md)
- [cn.xla 短信头：nonce、did、ts 与 sign 截取](xfq-android-cases-compilation/xfq-20250923-01-reference.md)
- [小黑盒 1.3.368：hkey 的路径 Base64、HMAC-SHA1 与 MixColumns 校验位](xfq-android-cases-compilation/xfq-20251023-01-reference.md)
- [安居客 17.28.1 nsign 的四段与一位改写](xfq-android-cases-compilation/xfq-20251122-01-reference.md)
- [最右 5.7.3 NetCrypto.sign 的形状](xfq-android-cases-compilation/xfq-20251206-01-reference.md)
- [小猿口算 3.93.2 的五轮 MD5 顺序](xfq-android-cases-compilation/xfq-20251214-01-reference.md)
- [南银法巴消金 7.4.4：native 密文入口和三段布局](xfq-android-cases-compilation/xfq-20260112-01-reference.md)
- [快手 Android：48 字节白盒的两套用途](xfq-android-cases-compilation/xfq-20260828-01-reference.md)
