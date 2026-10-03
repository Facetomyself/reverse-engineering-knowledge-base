---
schema_version: 2
id: anti-detection-benru-anti-detection-compilation
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
  citation: 微信公众号：本如笔记
  reason: 原归档明确记载出处，但未提供可定位的公开来源链接；本轮只保留来源自述。
source_completeness: unknown
tags:
- 请求头一致性
- curl_cffi
- TLS指纹
- Selenium stealth
- 登录态
- 字体反爬
- 验证码
- Canvas
original_date: 多篇合集
archived_date: '2026-07-16'
---

# 本如笔记反爬与反检测实战合集

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: 微信公众号：本如笔记
> 原始发布时间: 多篇合集
> 归档日期: 2026-07-16
> 分类: anti-detection
</details>
>
> 覆盖请求头一致性、curl_cffi TLS 指纹、Selenium stealth、登录态持久化、字体反爬、验证码识别与 Canvas 指纹等常见对抗面。

## 收录说明

本合集只吸收与逆向工程、协议恢复和反检测直接相关的技术稿。平台导航、评论、二维码、招聘、课程推广和商业广告未纳入；同源 DOCX、HTML、MHTML、PDF 与图片附件不重复保留。

## 文章目录（8 篇）

| 日期 | 文章 |
|------|------|
| 2026-02-05 | [爬虫为什么总被抓？你的请求头出卖了你！](benru-anti-detection-compilation/benru-anti-20260205-01.md) |
| 2026-02-06 | [Python爬虫利器curl_cffi：轻松模拟浏览器指纹，绕过高级反爬](benru-anti-detection-compilation/benru-anti-20260206-01.md) |
| 2026-02-08 | [你的Selenium又被识别了？—— 可能是没用对stealth.js反检测技术](benru-anti-detection-compilation/benru-anti-20260208-01.md) |
| 2026-02-20 | [爬虫老手才知道的4种登录状态管理绝技，告别反复登录！](benru-anti-detection-compilation/benru-anti-20260220-01.md) |
| 2026-03-06 | [字体反爬？别慌，KNN和OCR两套方案直接拿下](benru-anti-detection-compilation/benru-anti-20260306-01.md) |
| 2026-03-11 | [2026 年了，你的爬虫还在被验证码按在地上摩擦？](benru-anti-detection-compilation/benru-anti-20260311-01.md) |
| 2026-04-25 | [你每次打开网页，浏览器都在偷偷画画](benru-anti-detection-compilation/benru-anti-20260425-01.md) |
| 2026-04-29 | [被“请依次点击图中文字”逼疯了？这套YOLO+孪生网络方案，300张图就能破！](benru-anti-detection-compilation/benru-anti-20260429-01.md) |

## 提炼说明（238）
archive-only。导航页仅 8 条目录。
子篇 20260205–20260429 已在 229/232/235 处置。

## 同目录窄参考

本段只挂同目录提炼卡。

- [HTTP 请求头一致性的来源策略](benru-anti-detection-compilation/benru-anti-20260205-01-reference.md)
- [curl_cffi 的 impersonate 与 JA3 字段检查](benru-anti-detection-compilation/benru-anti-20260206-01-procedure.md)
- [stealth.js 的 Python 注入面](benru-anti-detection-compilation/benru-anti-20260208-01-reference.md)
- [Python 爬虫登录态的四种载体](benru-anti-detection-compilation/benru-anti-20260220-01-reference.md)
- [自定义字体反爬的两条还原路径](benru-anti-detection-compilation/benru-anti-20260306-01-reference.md)
- [ddddocr 验证码分流：接口、轨迹参数与未闭合分支](benru-anti-detection-compilation/benru-anti-20260311-01-reference.md)
- [Canvas toDataURL 调用记账](benru-anti-detection-compilation/benru-anti-20260425-01-procedure.md)
- [B 站文字点选：YOLO 与孪生网络的训练边界](benru-anti-detection-compilation/benru-anti-20260429-01-procedure.md)
