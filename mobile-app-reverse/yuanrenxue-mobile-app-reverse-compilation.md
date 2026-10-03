---
schema_version: 2
id: mobile-app-reverse-yuanrenxue-mobile-app-reverse-compilation
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
  citation: 微信公众号：猿人学Python
  reason: 原归档明确记载出处，但未提供可定位的公开来源链接；本轮只保留来源自述。
source_completeness: unknown
tags:
- Token Hook
- TCP抓包
- Protobuf
- 双向认证
- Android
- iOS
- Flutter
- Jailbreak检测
original_date: 多篇合集
archived_date: '2026-07-16'
---

# 猿人学移动 App 逆向与抓包合集

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: 微信公众号：猿人学Python
> 原始发布时间: 多篇合集
> 归档日期: 2026-07-16
> 分类: mobile-app-reverse
</details>
>
> 覆盖登录态与 Token Hook、TCP/HTTPS 抓包、Protobuf、双向认证、Native 参数还原、iOS、Flutter 与 Jailbreak 检测分析。

## 收录说明

本合集只吸收与逆向工程、协议恢复和反检测直接相关的技术稿。平台导航、评论、二维码、招聘、课程推广和商业广告未纳入；同源 DOCX、HTML、MHTML、PDF 与图片附件不重复保留。

## 文章目录（17 篇）

| 日期 | 文章 |
|------|------|
| 2019-05-16 | [让你的爬虫无障碍抓取上千万需登录的APP数据](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20190516-01.md) |
| 2019-05-20 | [爬虫技巧：使用Charles和requests模拟微博登录](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20190520-01.md) |
| 2019-11-13 | [不还原token算法抓取APP最简单的Hook方法](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20191113-01.md) |
| 2019-12-19 | [搞定某APP的TCP抓包，并实现Hook抓取](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20191219-01.md) |
| 2020-02-20 | [爬虫之-某生鲜APP加密参数逆向分析](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200220-01.md) |
| 2020-03-04 | [APP爬虫之-Protobuf协议逆向解析](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200304-01.md) |
| 2020-03-26 | [APP爬虫-双向认证抓包的两种方法](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200326-01.md) |
| 2020-04-09 | [Android 7.0 Https抓包单双向验证解决方案汇总](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200409-01.md) |
| 2020-05-07 | [某文APP逆向抓取分析](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200507-01.md) |
| 2020-05-24 | [分析app的登陆协议](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200524-01.md) |
| 2020-06-02 | [APP爬虫-某APP iOS版逆向过程](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200602-01.md) |
| 2020-06-09 | [iOS逆向抓取-巧破某报价大全APP加密参数](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200609-01.md) |
| 2020-08-03 | [安卓逆向之Luac解密反编译](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200803-01.md) |
| 2020-09-08 | [某书新版登录流程逆向分析](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200908-01.md) |
| 2020-09-30 | [APP 中的 JS 加密逆向解析](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200930-01.md) |
| 2026-03-24 | [使用 AI 实现最新版本 Flutter HTTPS 明文抓包](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20260324-01.md) |
| 2026-05-29 | [AI 逆向实战：Flutter + Swift 混合型 App 的 Jailbreak 检测分析与绕过](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20260529-01.md) |

## 提炼说明（556）
archive_only。
猿人学移动 App 合集 TOC 枢纽；17 篇子文已逐篇处置。
本轮不另建卡。

## 同目录窄参考

本段只挂同目录提炼卡。

- [脉脉分享路径与免登录名片路径](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20190516-01-reference.md)
- [不还原算法时的 getAS 调用边界](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20191113-01-reference.md)
- [Android 7 抓包分支](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200409-01-procedure.md)
- [com.lawyee 查询请求的 base64 体和 3DES 响应](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200507-01-reference.md)
- [某汽车 iOS：sign 与 _r 的函数链](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200602-01-reference.md)
- [Cocos2dx-lua：luac 头里的 sign 和 so 里的 key](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200803-01-reference.md)
- [未点名站点的登录链与字段](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200908-01-reference.md)
- [App 登录加密落在 JS 而不是 Java 加密类](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20200930-01-reference.md)
- [libflutter.so 的文件偏移和两种落点](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20260324-01-reference.md)
- [ZDefend 越狱检测的消费层字段](yuanrenxue-mobile-app-reverse-compilation/yuanrenxue-app-20260529-01-reference.md)
