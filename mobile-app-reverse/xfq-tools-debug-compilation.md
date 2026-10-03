---
schema_version: 2
id: mobile-app-reverse-xfq-tools-debug-compilation
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
- xfqtrace
- Frida
- Gadget
- jadx
- 抓包
- WebView
- MCP
original_date: 多篇合集
archived_date: '2026-09-04'
---

# 逆向学习交流工具与调试合集

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: 知识星球：逆向学习交流
> 原始发布时间: 多篇合集
> 归档日期: 2026-09-04
> 分类: mobile-app-reverse
</details>
>
> xfqtrace、Frida/Gadget、jadx、证书、WebView Hook、抓包对比与 AI/MCP 辅助分析笔记。去掉续杯、号池、破解版和社群闲聊。

## 收录说明

本合集只吸收具有逆向工程复用价值的技术稿。星球导航、评论头像、二维码、号池/续杯、破解版软件、附件 zip/PDF 与业务爬取脚本未纳入。

「利用uiautomator全自动点击隐私同意按钮」原有两份重复副本（2026-06-08 版与日期未知版），2026-09-26 去重后只保留主文 [uiautomator-privacy-consent-tap.md](uiautomator-privacy-consent-tap.md)，目录条目直接指向主文。

## 文章目录（41 篇）

| 日期 | 文章 |
|------|------|
| 2025-11-06 | [lsp 拦截 系统账号写入](xfq-tools-debug-compilation/xfq-20251106-01.md) |
| 2025-11-23 | [jadx优化: 真一键frida脚本](xfq-tools-debug-compilation/xfq-20251123-01.md) |
| 2025-12-04 | [ai辅助逆向（讲义）](xfq-tools-debug-compilation/xfq-20251204-01.md) |
| 2025-12-05 | [std__string 内存结构详解](xfq-tools-debug-compilation/xfq-20251205-01.md) |
| 2025-12-18 | [trace_natives_plus](xfq-tools-debug-compilation/xfq-20251218-01.md) |
| 2025-12-22 | [frida-server经典报错 not a function](xfq-tools-debug-compilation/xfq-20251222-01.md) |
| 2026-01-05 | [常见 证书安装 方案 与 对应常见问题](xfq-tools-debug-compilation/xfq-20260105-01.md) |
| 2026-01-12 | [binary ninja的mcp配置](xfq-tools-debug-compilation/xfq-20260112-01.md) |
| 2026-01-15 | [安卓9以上 lsp中发http包](xfq-tools-debug-compilation/xfq-20260115-01.md) |
| 2026-02-16 | [静态住宅ip 代理配置教程](xfq-tools-debug-compilation/xfq-20260216-01.md) |
| 2026-03-09 | [bug：某些手机在特定fridaserver运行的时候会出现下列报错](xfq-tools-debug-compilation/xfq-20260309-01.md) |
| 2026-03-18 | [WORD到底几个字节？为啥IDA是2字节，别的是4字节？](xfq-tools-debug-compilation/xfq-20260318-01.md) |
| 2026-03-18 | [最近一些开源trace工具](xfq-tools-debug-compilation/xfq-20260318-02.md) |
| 2026-03-21 | [webview部分参考文章](xfq-tools-debug-compilation/xfq-20260321-01.md) |
| 2026-03-22 | [webview深度分析(一)（讲义）](xfq-tools-debug-compilation/xfq-20260322-01.md) |
| 2026-03-24 | [FinClip小程序 的三进程保护](xfq-tools-debug-compilation/xfq-20260324-01.md) |
| 2026-03-24 | [三进程保护demo逆向](xfq-tools-debug-compilation/xfq-20260324-02.md) |
| 2026-03-29 | [改系统语言设置的两种方案](xfq-tools-debug-compilation/xfq-20260329-01.md) |
| 2026-03-31 | [记录几篇支付宝小程序逆向的文章](xfq-tools-debug-compilation/xfq-20260331-01.md) |
| 2026-04-11 | [优酷抓包 js 脚本](xfq-tools-debug-compilation/xfq-20260411-01.md) |
| 2026-05-27 | [ccswitch使用](xfq-tools-debug-compilation/xfq-20260527-01.md) |
| 2026-05-28 | [xfQtrace 真机trace工具：极致的使用体验与优化](xfq-tools-debug-compilation/xfq-20260528-01.md) |
| 2026-06-08 | [利用uiautomator全自动点击隐私同意按钮](uiautomator-privacy-consent-tap.md) |
| 2026-06-17 | [P2-A：ART/bionic JNI 插装](xfq-tools-debug-compilation/xfq-20260617-01.md) |
| 2026-06-20 | [Java 算法 Hook：libcore 采集 + ROMManager 日志页](xfq-tools-debug-compilation/xfq-20260620-01.md) |
| 2026-06-25 | [xfqtrace v2.0：快速/稳定/全面/隐藏](xfq-tools-debug-compilation/xfq-20260625-01.md) |
| 2026-07-08 | [xfqtrace 2.1 修一些稳定性bug](xfq-tools-debug-compilation/xfq-20260708-01.md) |
| 2026-07-09 | [aosp魔改笔记：组合拳 无痕抓包](xfq-tools-debug-compilation/xfq-20260709-01.md) |
| 2026-07-10 | [frida-gadget（讲义）](xfq-tools-debug-compilation/xfq-20260710-01.md) |
| 2026-07-11 | [scrcpy常用命令](xfq-tools-debug-compilation/xfq-20260711-01.md) |
| 2026-07-12 | [Reqable MCP 配置](xfq-tools-debug-compilation/xfq-20260712-01.md) |
| 2026-07-30 | [技巧分享：协议设备注册链路与真实抓包对比怎么做更优雅？](xfq-tools-debug-compilation/xfq-20260730-01.md) |
| 2026-08-14 | [xfqtrace v2.2 初步bypass一些检测](xfq-tools-debug-compilation/xfq-20260814-01.md) |
| 2026-08-18 | [算法推理是啥意思？](xfq-tools-debug-compilation/xfq-20260818-01.md) |
| — | [flatbuf 基本结构解析](xfq-tools-debug-compilation/xfq-undated-01.md) |
| — | [gadget_trace](xfq-tools-debug-compilation/xfq-undated-02.md) |
| — | [hook frida检测](xfq-tools-debug-compilation/xfq-undated-03.md) |
| — | [从抓包到纯 Python：Kimi `device_register` 接口完整还原](xfq-tools-debug-compilation/xfq-undated-04.md) |
| — | [你要注入的 JS 脚本内容](xfq-tools-debug-compilation/xfq-undated-05.md) |
| — | [函数花指令.js](xfq-tools-debug-compilation/xfq-undated-06.md) |
| — | [逗号表达式.js](xfq-tools-debug-compilation/xfq-undated-08.md) |

## 提炼说明（541）
archive_only。
工具与调试 TOC 枢纽；子文本轮起逐篇处置，枢纽不升卡。
本轮不另建卡。

## 同目录窄参考

本段只挂同目录提炼卡。

- [IDA 与 JADX 的 MCP 接线入口](xfq-tools-debug-compilation/xfq-20251204-01-reference.md)
- [unidbg 里 libc++ std::string 的对象边界](xfq-tools-debug-compilation/xfq-20251205-01-reference.md)
- [Binary Ninja MCP 的安装入口](xfq-tools-debug-compilation/xfq-20260112-01-reference.md)
- [安卓明文 HTTP 的版本默认值和进程外出口](xfq-tools-debug-compilation/xfq-20260115-01-reference.md)
- [Android WebView：四个类、调试入口和两代桥](xfq-tools-debug-compilation/xfq-20260322-01-reference.md)
- [AOSP 内 ART/bionic 的 JNI 可观测插装点](xfq-tools-debug-compilation/xfq-20260617-01-reference.md)
- [libcore XfCryptoHook 的放行顺序和事件字段](xfq-tools-debug-compilation/xfq-20260620-01-reference.md)
- [Frida Gadget 的 listen 配置与连接时机](xfq-tools-debug-compilation/xfq-20260710-01-reference.md)
- [scrcpy 常见录制与音频旗标](xfq-tools-debug-compilation/xfq-20260711-01-reference.md)
- [未优化 flatbuf 的布局对照](xfq-tools-debug-compilation/xfq-undated-01-reference.md)
- [xfqtrace Gadget 脚本的武装顺序](xfq-tools-debug-compilation/xfq-undated-02-procedure.md)
- [单返回函数调用何时内联、何时放弃](xfq-tools-debug-compilation/xfq-undated-06-reference.md)
- [逗号表达式按父节点外提还是只删纯值](xfq-tools-debug-compilation/xfq-undated-08-reference.md)
