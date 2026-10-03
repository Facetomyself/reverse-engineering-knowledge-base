---
schema_version: 2
id: mobile-app-reverse-xfq-aosp-rom-compilation
document_type: archive
scope:
  targets:
  - unknown
  client: unknown
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
- AOSP
- APatch
- WebView
- 系统CA
- GMS
- adb
- ROM
original_date: 多篇合集
archived_date: '2026-09-04'
---

# 逆向学习交流 AOSP 与 ROM 笔记合集

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: 知识星球：逆向学习交流
> 原始发布时间: 多篇合集
> 归档日期: 2026-09-04
> 分类: mobile-app-reverse
</details>
>
> AOSP 预置 CA、APatch、WebView 调试、GMS、adb RSA、投屏黑屏与 Java/Native 插桩笔记。只保留可复用的 ROM 改造路径，不写具体业务目标。

## 收录说明

本合集只吸收具有逆向工程复用价值的技术稿。星球导航、评论头像、二维码、号池/续杯、破解版软件、附件 zip/PDF 与业务爬取脚本未纳入。

## 文章目录（13 篇）

| 日期 | 文章 |
|------|------|
| 2026-01-17 | [MoveCertificate 二改模块，更优雅地管理证书](xfq-aosp-rom-compilation/xfq-20260117-01.md) |
| 2026-02-05 | [root管理器的 常用shell命令，下面以狐妖面具为例，请看截图](xfq-aosp-rom-compilation/xfq-20260205-01.md) |
| 2026-06-13 | [Wi-Fi 网络验证优化](xfq-aosp-rom-compilation/xfq-20260613-01.md) |
| 2026-06-14 | [Pixel 7 AOSP 开发者默认项与亮度默认值](xfq-aosp-rom-compilation/xfq-20260614-01.md) |
| 2026-06-14 | [XF ROM 内置 CA 证书基础设施](xfq-aosp-rom-compilation/xfq-20260614-02.md) |
| 2026-06-18 | [xf-rom 日志基建（log-infra + log-v2）](xfq-aosp-rom-compilation/xfq-20260618-01.md) |
| 2026-06-24 | [2026-06-24 user build adb RSA policy](xfq-aosp-rom-compilation/xfq-20260624-01.md) |
| 2026-06-26 | [20260626 WebView Debug ROM 控制与 Chromium 内核方案](xfq-aosp-rom-compilation/xfq-20260626-01.md) |
| 2026-06-26 | [APatch / KernelPatch 集成总览（唯一入口）](xfq-aosp-rom-compilation/xfq-20260626-02.md) |
| 2026-06-30 | [20260630 GMS preload suite](xfq-aosp-rom-compilation/xfq-20260630-01.md) |
| 2026-07-02 | [20260702 Pixel Launcher 预置与默认 HOME/Recents 切换](xfq-aosp-rom-compilation/xfq-20260702-01.md) |
| 2026-07-10 | [屏幕采集 / 投屏黑屏绕过总览](xfq-aosp-rom-compilation/xfq-20260710-01.md) |
| 2026-07-11 | [aosp魔改笔记：bypass投屏/录屏黑屏保护、伪装 scrcpy/adb 点击事件](xfq-aosp-rom-compilation/xfq-20260711-01.md) |

## 提炼说明（508）
TOC hub archive-only。
子文已逐篇处置。
本轮不另建合集卡。

## 同目录窄参考

本段只挂同目录提炼卡。

- [AOSP Captive Portal 默认探测改到国内可达地址](xfq-aosp-rom-compilation/xfq-20260613-01-procedure.md)
- [Panther 开发者默认项与第一次亮度不被 float 默认值覆盖](xfq-aosp-rom-compilation/xfq-20260614-01-procedure.md)
- [Android 13 REL 上把用户 CA 并入系统证书目录](xfq-aosp-rom-compilation/xfq-20260614-02-procedure.md)
- [xf-rom 插装日志的双通道约定](xfq-aosp-rom-compilation/xfq-20260618-01-reference.md)
- [按包强开 AOSP WebView DevTools，且不在本功能里做隐藏](xfq-aosp-rom-compilation/xfq-20260626-01-procedure.md)
- [panther user 构建把 APatch 收进 ROM](xfq-aosp-rom-compilation/xfq-20260626-02-procedure.md)
- [panther 原厂 GMS 预置：提取、user 构建与路径验收](xfq-aosp-rom-compilation/xfq-20260630-01-procedure.md)
- [panther 预置 Pixel Launcher 并切换 Recents](xfq-aosp-rom-compilation/xfq-20260702-01-procedure.md)
- [AOSP 屏幕采集黑屏绕过：开关、验收与停止条件](xfq-aosp-rom-compilation/xfq-20260710-01-procedure.md)
