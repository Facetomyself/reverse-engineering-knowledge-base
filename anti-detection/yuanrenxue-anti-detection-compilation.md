---
schema_version: 2
id: anti-detection-yuanrenxue-anti-detection-compilation
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
- Squid
- Cookie
- Referer
- 响应编码
- DNS缓存
- Akamai
- JA3
- JA4
- HTTP/2指纹
original_date: 多篇合集
archived_date: '2026-07-16'
---

# 猿人学请求一致性与反检测合集

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: 微信公众号：猿人学Python
> 原始发布时间: 多篇合集
> 归档日期: 2026-07-16
> 分类: anti-detection
</details>
>
> 汇总多 IP 代理、浏览器 Cookie、Referer/频率控制、响应编码、DNS 缓存、爬虫难度分层以及 Akamai TLS/JA3/JA4 指纹对抗。

## 收录说明

本合集只吸收与逆向工程、协议恢复和反检测直接相关的技术稿。平台导航、评论、二维码、招聘、课程推广和商业广告未纳入；同源 DOCX、HTML、MHTML、PDF 与图片附件不重复保留。

## 文章目录（8 篇）

| 日期 | 文章 |
|------|------|
| 2017-04-07 | [「运维」Linux单台机器配置多IP的squid3 http代理](yuanrenxue-anti-detection-compilation/yuanrenxue-anti-20170407-01.md) |
| 2018-10-01 | [Python爬虫使用浏览器的cookies：browsercookie](yuanrenxue-anti-detection-compilation/yuanrenxue-anti-20181001-01.md) |
| 2018-12-06 | [爬虫小偏方：绕开登陆和访问频率控制](yuanrenxue-anti-detection-compilation/yuanrenxue-anti-20181206-01.md) |
| 2018-12-07 | [爬虫小偏方二：修改referer后可以不用登录了](yuanrenxue-anti-detection-compilation/yuanrenxue-anti-20181207-01.md) |
| 2019-01-04 | [不要相信requests返回的text](yuanrenxue-anti-detection-compilation/yuanrenxue-anti-20190104-01.md) |
| 2019-06-20 | [大规模爬虫为什么要管理DNS缓存](yuanrenxue-anti-detection-compilation/yuanrenxue-anti-20190620-01.md) |
| 2019-12-30 | [写网络爬虫程序的四种难度](yuanrenxue-anti-detection-compilation/yuanrenxue-anti-20191230-01.md) |
| 2026-07-13 | [Akamai对抗的隐秘战线——TLS指纹](yuanrenxue-anti-detection-compilation/yuanrenxue-anti-20260713-01.md) |

## 提炼说明（379）
archive-only。合集 TOC 枢纽。
子篇已逐篇处置。
不把目录当模块。

## 同目录窄参考

本段只挂同目录提炼卡。

- [Squid3 按本地地址选择出口](yuanrenxue-anti-detection-compilation/yuanrenxue-anti-20170407-01-reference.md)
- [browsercookie 的三个加载入口](yuanrenxue-anti-detection-compilation/yuanrenxue-anti-20181001-01-reference.md)
- [requests 文本解码把中文解乱的来源边界](yuanrenxue-anti-detection-compilation/yuanrenxue-anti-20190104-01-reference.md)
- [Firefox NSS ClientHello 与 requests 出厂握手的字段边界](yuanrenxue-anti-detection-compilation/yuanrenxue-anti-20260713-01-reference.md)
