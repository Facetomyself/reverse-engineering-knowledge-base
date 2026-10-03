---
schema_version: 2
id: web-reverse-koohai-reverse-notes-compilation
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
  citation: 微信公众号：零基础爬虫第一天
  reason: 原归档明确记载出处，但未提供可定位的公开来源链接；本轮只保留来源自述。
source_completeness: unknown
tags:
- KhBox
- 补环境
- Illegal invocation
- Canvas
- jsdom
- JSVMP
- FART
- WebView
- IDA MD5
original_date: 多篇合集
archived_date: '2026-09-06'
---

# 零基础爬虫第一天 逆向笔记合集

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: 微信公众号：零基础爬虫第一天
> 原始发布时间: 多篇合集
> 归档日期: 2026-09-06
> 分类: web-reverse
</details>
>
> 17 篇 koohai 笔记：KhBox 补环境（原型链 / Illegal invocation / Canvas / Node 编译）、BrowserLeaks 检测面、AST 到 JSVMP、以及 FART、WebView 调试和 IDA 识别 MD5。保留实现要点，不收录项目仓库附件和图片。

## 收录说明

目录名是账号名，内容以补环境和 Native/脱壳笔记为主，不是爬虫入门课。平台控件、课程推销、同源导出格式和图片未纳入。

## 文章目录（17 篇）

| 日期 | 文章 |
|------|------|
| 2023-10-08 | [某麦小程序sign解密](koohai-reverse-notes-compilation/koohai-20231008-01.md) |
| 2024-01-08 | [基础篇-webview调试及源码修改](koohai-reverse-notes-compilation/koohai-20240108-01.md) |
| 2024-01-09 | [fart源码分析以及改进](koohai-reverse-notes-compilation/koohai-20240109-01.md) |
| 2024-06-23 | [md5在ida中的识别及使用方法](koohai-reverse-notes-compilation/koohai-20240623-01.md) |
| 2026-01-05 | [node源码-8：node源码接入jsdom](koohai-reverse-notes-compilation/koohai-20260105-01.md) |
| 2026-01-12 | [khbox补环境-3：原型链与 Illegal Invocation 保护机制](koohai-reverse-notes-compilation/koohai-20260112-01.md) |
| 2026-01-25 | [khbox补环境-5：addon补环境 v0版完成](koohai-reverse-notes-compilation/koohai-20260125-01.md) |
| 2026-02-05 | [khbox-6：V0.1 功能实现](koohai-reverse-notes-compilation/koohai-20260205-01.md) |
| 2026-02-09 | [khbox-7：v1完善](koohai-reverse-notes-compilation/koohai-20260209-01.md) |
| 2026-02-25 | [khbox-9：KhBox node版重构](koohai-reverse-notes-compilation/koohai-20260225-01.md) |
| 2026-03-03 | [khbox-11：Canvas 指纹对抗解析](koohai-reverse-notes-compilation/koohai-20260303-01.md) |
| 2026-03-05 | [最短路径把khbox代码编译进 Node.js](koohai-reverse-notes-compilation/koohai-20260305-01.md) |
| 2026-03-08 | [详解 BrowserLeaks - JavaScript 检测及api分析](koohai-reverse-notes-compilation/koohai-20260308-01.md) |
| 2026-03-13 | [khbox1.2更新](koohai-reverse-notes-compilation/koohai-20260313-01.md) |
| 2026-03-15 | [从AST到JSVMP（入坑记录）](koohai-reverse-notes-compilation/koohai-20260315-01.md) |
| 2026-03-18 | [vmp-1：rs-while的构造器初探](koohai-reverse-notes-compilation/koohai-20260318-01.md) |
| 2026-04-02 | [khbox补环境案例-2：yrx2内存爆破分析](koohai-reverse-notes-compilation/koohai-20260402-01.md) |

<a id="reference-extraction-214"></a>
## 提炼说明

本合集页只列 17 篇子文目录，没有独立接口、参数或验收模块正文。子篇「某麦小程序sign解密」已在 reviewed-no-extraction-29 记 archive-only（正文不足以支撑 sign 参考）。kb_catalog.py query --tag KhBox --type reference 为 0。合集导航页不另建 reference。其余子篇需单独全文核验。

## 同目录窄参考

本段只挂同目录提炼卡。

- [Android WebView 强制打开调试的入口](koohai-reverse-notes-compilation/koohai-20240108-01-reference.md)
- [FART 抽取壳的脱壳点与目录开关](koohai-reverse-notes-compilation/koohai-20240109-01-reference.md)
- [IDA 里认出 MD5 以及 findhash 的 32 位边界](koohai-reverse-notes-compilation/koohai-20240623-01-reference.md)
- [KhBox 接入 jsdom 时的查找顺序与 envFuncs 键](koohai-reverse-notes-compilation/koohai-20260105-01-reference.md)
- [KhBox 的原型链、native toString 与 Illegal invocation](koohai-reverse-notes-compilation/koohai-20260112-01-reference.md)
- [KhBox addon 的 jsDispatch 与 V8 Context 隔离](koohai-reverse-notes-compilation/koohai-20260125-01-reference.md)
- [KhBox V0.1：context 拆开和没做完的 in/delete](koohai-reverse-notes-compilation/koohai-20260205-01-reference.md)
- [KhBox v1：VM 内 bootstrap 和新增的调用、堆栈检查](koohai-reverse-notes-compilation/koohai-20260209-01-reference.md)
- [KhBox node 重构：内部绑定、jsDispatch 和两条回读](koohai-reverse-notes-compilation/koohai-20260225-01-reference.md)
- [KhBox 笔记里的 Canvas 扣分标志和 toDataURL 分支](koohai-reverse-notes-compilation/koohai-20260303-01-reference.md)
- [KhBox 编进 Node 内置 binding 时被点名的四处](koohai-reverse-notes-compilation/koohai-20260305-01-reference.md)
- [BrowserLeaks JavaScript 计分脚本和三处 KhBox getter](koohai-reverse-notes-compilation/koohai-20260308-01-reference.md)
- [khbox 1.2 里点名的数组型类和媒体能力桩](koohai-reverse-notes-compilation/koohai-20260313-01-reference.md)
- [rs while 代码生成器：组装机和静态引擎怎么分开](koohai-reverse-notes-compilation/koohai-20260318-01-reference.md)
- [yrx2 里来源点名的四处内存检查](koohai-reverse-notes-compilation/koohai-20260402-01-reference.md)
