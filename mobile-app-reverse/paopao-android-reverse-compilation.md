---
schema_version: 2
id: mobile-app-reverse-paopao-android-reverse-compilation
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
  citation: 微信公众号：泡泡以安
  reason: 原归档明确记载出处，但未提供可定位的公开来源链接；本轮只保留来源自述。
source_completeness: unknown
tags:
- Frida
- Unidbg
- ARM64
- JNI
- Stalker
- SSL Pinning
- Protobuf
- DEX脱壳
- Root检测
original_date: 多篇合集
archived_date: '2026-07-13'
---

# 泡泡以安 Android 逆向技术合集

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: 微信公众号：泡泡以安
> 原始发布时间: 多篇合集
> 归档日期: 2026-07-13
> 分类: mobile-app-reverse
</details>
>
> 覆盖 Android 抓包、密码算法、ARM64、Unidbg、Frida、Native Hook、脱壳与协议分析的系统资料。

## 收录说明

本合集只吸收具有逆向工程复用价值的技术稿。平台导航、封面、二维码、头像、广告、招聘、抽奖和带货内容未纳入；同源的 DOCX、HTML、MHTML、PDF 重复导出件不重复保留。

## 文章目录（67 篇，连载合并后 57 条）

| 日期 | 文章 |
|------|------|
| 2026-03-02 | [风控对抗中的浏览器指纹技术（上）：协议层、应用层与行为检测](paopao-android-reverse-compilation/paopao-20260302-01.md) |
| 2026-03-03 | [安卓端某音乐类 APP 逆向分享（一～五，缺四）：协议抓包、协议分析、params 与 NMDI 参数加密](paopao-android-reverse-compilation/paopao-20260303-01.md) |
| 2026-03-10 | [汇编基础介绍——ARMv8指令集（二～五，缺一）](paopao-android-reverse-compilation/paopao-20260310-01.md) |
| 2026-03-16 | [逆向某音乐 App：用 Frida + unidbg 还原 AES+RSA 混合加密的设备指纹 dfid](paopao-android-reverse-compilation/paopao-20260316-01.md) |
| 2026-03-17 | [AES 加密算法详解：从原理到安卓逆向实战](paopao-android-reverse-compilation/paopao-20260317-01.md) |
| 2026-03-18 | [深入MD5：逆向工程师如何识别和还原标准与魔改算法](paopao-android-reverse-compilation/paopao-20260318-01.md) |
| 2026-03-19 | [某音乐 App 逆向（一～三）：加密通信全解析与 calc 签名算法还原](paopao-android-reverse-compilation/paopao-20260319-01.md) |
| 2026-03-23 | [ARM 汇编全解（八）：特权级与处理器模式](paopao-android-reverse-compilation/paopao-20260323-01.md) |
| 2026-03-24 | [安卓 App 抓包实战指南：从基础原理到内核级对抗](paopao-android-reverse-compilation/paopao-20260324-01.md) |
| 2026-03-25 | [TEA 加密算法逆向全攻略：从原理到实战密钥提取](paopao-android-reverse-compilation/paopao-20260325-01.md) |
| 2026-03-26 | [字节系音乐产品 SSL Pinning 逆向分析与抓包方案](paopao-android-reverse-compilation/paopao-20260326-01.md) |
| 2026-03-27 | [DES 加密算法详解：从原理到安卓逆向实战](paopao-android-reverse-compilation/paopao-20260327-01.md) |
| 2026-03-30 | [Frida进阶——指令级追踪工具 Stalker 使用教程](paopao-android-reverse-compilation/paopao-20260330-01.md) |
| 2026-03-31 | [Frida进阶——安卓应用 9 种 SSL Pinning 绕过方案](paopao-android-reverse-compilation/paopao-20260331-01.md) |
| 2026-04-01 | [Android 逆向视角下的 Protobuf 协议分析（上中下篇）：编码原理、解码还原与 Frida Hook 实战](paopao-android-reverse-compilation/paopao-20260401-01.md) |
| 2026-04-08 | [RSA 加密算法详解：从原理到安卓逆向实战](paopao-android-reverse-compilation/paopao-20260408-01.md) |
| 2026-04-09 | [Unidbg学习笔记（一）：为什么需要用户态模拟器](paopao-android-reverse-compilation/paopao-20260409-01.md) |
| 2026-04-10 | [Unidbg学习笔记（二）：Unidbg 的世界观](paopao-android-reverse-compilation/paopao-20260410-01.md) |
| 2026-04-13 | [Unidbg学习笔记（三）：五个后端引擎的性能与取舍](paopao-android-reverse-compilation/paopao-20260413-01.md) |
| 2026-04-14 | [Unidbg学习笔记（四）：一条 SVC 指令引发的连锁反应](paopao-android-reverse-compilation/paopao-20260414-01.md) |
| 2026-04-15 | [Unidbg学习笔记（五）：第一次让 SO 跑起来](paopao-android-reverse-compilation/paopao-20260415-01.md) |
| 2026-04-16 | [Unidbg学习笔记（六）：补环境的思维框架](paopao-android-reverse-compilation/paopao-20260416-01.md) |
| 2026-04-17 | [Unidbg学习笔记（七）：JNI 层补环境](paopao-android-reverse-compilation/paopao-20260417-01.md) |
| 2026-04-20 | [Unidbg学习笔记（八）：文件系统层补环境](paopao-android-reverse-compilation/paopao-20260420-01.md) |
| 2026-04-21 | [Unidbg学习笔记（九）：系统调用层补环境](paopao-android-reverse-compilation/paopao-20260421-01.md) |
| 2026-04-24 | [Unidbg学习笔记（十）：库函数层补环境](paopao-android-reverse-compilation/paopao-20260424-01.md) |
| 2026-04-25 | [Unidbg学习笔记（十一）：初始化问题](paopao-android-reverse-compilation/paopao-20260425-01.md) |
| 2026-04-27 | [Unidbg学习笔记（十二）：Trace 的三个层次](paopao-android-reverse-compilation/paopao-20260427-01.md) |
| 2026-04-28 | [Unidbg学习笔记（十三）：固定随机干扰项](paopao-android-reverse-compilation/paopao-20260428-01.md) |
| 2026-04-29 | [Unidbg学习笔记（二十）：Unidbg 的未来与替代方案](paopao-android-reverse-compilation/paopao-20260429-01.md) |
| 2026-04-29 | [Unidbg学习笔记（十七）：Hook 框架选型与实战](paopao-android-reverse-compilation/paopao-20260429-02.md) |
| 2026-04-29 | [Unidbg学习笔记（十九）：生产化](paopao-android-reverse-compilation/paopao-20260429-03.md) |
| 2026-04-29 | [Unidbg学习笔记（十八）：从模拟调用到算法还原](paopao-android-reverse-compilation/paopao-20260429-04.md) |
| 2026-04-30 | [Unidbg学习笔记（完结）：EPUB/PDF 附件下载](paopao-android-reverse-compilation/paopao-20260430-01.md) |
| 2026-05-05 | [Frida学习笔记（一）：Frida 入门 · 原理与架构](paopao-android-reverse-compilation/paopao-20260505-01.md) |
| 2026-05-06 | [Frida学习笔记（二）：环境搭建一条龙](paopao-android-reverse-compilation/paopao-20260506-01.md) |
| 2026-05-08 | [Frida学习笔记（三）：第一个 Hook · Java 方法拦截](paopao-android-reverse-compilation/paopao-20260508-01.md) |
| 2026-05-09 | [Frida学习笔记（四）：Hook 进阶 · 构造、内部类、字段、对象搜索](paopao-android-reverse-compilation/paopao-20260509-01.md) |
| 2026-05-11 | [Frida学习笔记（五）：Java 层 API 全解](paopao-android-reverse-compilation/paopao-20260511-01.md) |
| 2026-05-12 | [Frida学习笔记（六）：Native 层 API 全解](paopao-android-reverse-compilation/paopao-20260512-01.md) |
| 2026-05-13 | [Frida学习笔记（七）：调用栈、日志与 Hook 排错](paopao-android-reverse-compilation/paopao-20260513-01.md) |
| 2026-05-14 | [Frida学习笔记（八）：SSL Pinning 绕过全攻略](paopao-android-reverse-compilation/paopao-20260514-01.md) |
| 2026-05-18 | [Frida学习笔记（十）：gRPC、Protobuf 协议逆向](paopao-android-reverse-compilation/paopao-20260518-01.md) |
| 2026-05-19 | [Frida学习笔记（十一）：Android 系统级 Hook](paopao-android-reverse-compilation/paopao-20260519-01.md) |
| 2026-05-26 | [Frida学习笔记（十四）：算法自吐 · 一个脚本监控所有加密](paopao-android-reverse-compilation/paopao-20260526-01.md) |
| 2026-05-28 | [Frida学习笔记（十五）：算法自吐 · Native 层 OpenSSL/BoringSSL Hook](paopao-android-reverse-compilation/paopao-20260528-01.md) |
| 2026-05-29 | [Frida学习笔记（十六）：Root 检测绕过](paopao-android-reverse-compilation/paopao-20260529-01.md) |
| 2026-06-04 | [Frida学习笔记（十七）：反调试与反检测对抗（上）· 网易云音乐易盾实战](paopao-android-reverse-compilation/paopao-20260604-01.md) |
| 2026-06-05 | [Frida学习笔记（十八）：反调试与反检测对抗（下）· 招商银行三套 SDK 实战](paopao-android-reverse-compilation/paopao-20260605-01.md) |
| 2026-06-11 | [Frida学习笔记（十九）：Frida Gadget 注入 · 网易云音乐易盾实战](paopao-android-reverse-compilation/paopao-20260611-01.md) |
| 2026-06-15 | [Frida学习笔记（二十）：ARM 汇编速成](paopao-android-reverse-compilation/paopao-20260615-01.md) |
| 2026-06-18 | [Frida学习笔记（二十一）：未导出函数定位 · 让脚本跨版本复用](paopao-android-reverse-compilation/paopao-20260618-01.md) |
| 2026-06-25 | [Frida学习笔记（二十二）：JNI 函数追踪](paopao-android-reverse-compilation/paopao-20260625-01.md) |
| 2026-06-26 | [Frida学习笔记（二十三）：SO Dump 与内存 Dump](paopao-android-reverse-compilation/paopao-20260626-01.md) |
| 2026-06-29 | [Frida学习笔记（二十四）：Stalker 指令级追踪](paopao-android-reverse-compilation/paopao-20260629-01.md) |
| 2026-07-07 | [Frida学习笔记（二十五）：签名校验绕过](paopao-android-reverse-compilation/paopao-20260707-01.md) |
| 2026-07-08 | [Frida学习笔记（二十六）：DEX 脱壳实战](paopao-android-reverse-compilation/paopao-20260708-01.md) |

## 提炼说明（448）
archive-only。合集 TOC hub。
子篇已逐篇处置。
不建合集卡。

## 同目录窄参考

本段只挂同目录提炼卡。

- [JA3、TCP 选项顺序与 HTTP/2 被动指纹](paopao-android-reverse-compilation/paopao-20260302-01-reference.md)
- [目标音乐 App 的 eapi 搜索：路由直连、params 入口与 NMDI 外形](paopao-android-reverse-compilation/paopao-20260303-01-reference.md)
- [安卓逆向里如何识别 AES、模式和近邻算法](paopao-android-reverse-compilation/paopao-20260317-01-reference.md)
- [musics.fcg 与 libmer.so calc 的字段边界](paopao-android-reverse-compilation/paopao-20260319-01-reference.md)
- [TEA 家族的识别参数](paopao-android-reverse-compilation/paopao-20260325-01-reference.md)
- [Android 上识别 DES 与 3DES 的常量与字符串](paopao-android-reverse-compilation/paopao-20260327-01-reference.md)
- [Frida Stalker 的事件、队列和插桩边界](paopao-android-reverse-compilation/paopao-20260330-01-reference.md)
- [Android SSL Pinning 的症状、pin 对象和声明位置](paopao-android-reverse-compilation/paopao-20260331-01-reference.md)
- [安卓逆向笔记里用来认出 RSA 的标记](paopao-android-reverse-compilation/paopao-20260408-01-reference.md)
- [Unidbg 后端按追踪或速度二选一](paopao-android-reverse-compilation/paopao-20260409-01-reference.md)
- [Unidbg 已实现层、文件返回值和来源点名的缺口](paopao-android-reverse-compilation/paopao-20260410-01-reference.md)
- [Unidbg Backend 选型边界](paopao-android-reverse-compilation/paopao-20260413-01-reference.md)
- [Unidbg 的 SVC 分发](paopao-android-reverse-compilation/paopao-20260414-01-reference.md)
- [第一次 Unidbg 调用的排错闭环](paopao-android-reverse-compilation/paopao-20260415-01-procedure.md)
- [Unidbg 补环境先分流再决定返回值](paopao-android-reverse-compilation/paopao-20260416-01-reference.md)
- [Unidbg JNI override 的类型、取值和逻辑](paopao-android-reverse-compilation/paopao-20260417-01-reference.md)
- [Unidbg 文件访问用 IOResolver 的三种返回](paopao-android-reverse-compilation/paopao-20260420-01-reference.md)
- [Unidbg 系统调用缺口：何时介入，以及两套编号](paopao-android-reverse-compilation/paopao-20260421-01-reference.md)
- [Unidbg 库函数层：框架边界和系统属性注册](paopao-android-reverse-compilation/paopao-20260424-01-reference.md)
- [Unidbg 初始化边界：JNI_OnLoad 和 Java 主动 init](paopao-android-reverse-compilation/paopao-20260425-01-reference.md)
- [Unidbg Trace 的三层接口和读法](paopao-android-reverse-compilation/paopao-20260427-01-reference.md)
- [Unidbg 的边界、替代方向和 Frida 痕迹对照](paopao-android-reverse-compilation/paopao-20260429-01-reference.md)
- [Unidbg 六种 Hook 的挂载点和选型边界](paopao-android-reverse-compilation/paopao-20260429-02-reference.md)
- [Unidbg 生产服务：模拟器实例池与销毁边界](paopao-android-reverse-compilation/paopao-20260429-03-procedure.md)
- [Frida 注入架构：ArtMethod、补丁宽度与 Spawn 时点](paopao-android-reverse-compilation/paopao-20260505-01-reference.md)
- [Frida Android 实验环境：版本对齐、验收与停止条件](paopao-android-reverse-compilation/paopao-20260506-01-procedure.md)
- [Frida Java.perform 与 overload 类型串](paopao-android-reverse-compilation/paopao-20260508-01-reference.md)
- [Frida 里对象和混淆方法怎么定位](paopao-android-reverse-compilation/paopao-20260509-01-reference.md)
- [Frida Java 桥的主动调用面](paopao-android-reverse-compilation/paopao-20260511-01-reference.md)
- [Frida Native 指针、拦截与导出查找边界](paopao-android-reverse-compilation/paopao-20260512-01-reference.md)
- [Frida Hook 不触发时的诊断顺序](paopao-android-reverse-compilation/paopao-20260513-01-reference.md)
- [Android 系统 API 的 Frida 汇聚点](paopao-android-reverse-compilation/paopao-20260519-01-reference.md)
- [Java JCE 算法自吐：实例关联、重载取舍和无输出边界](paopao-android-reverse-compilation/paopao-20260526-01-reference.md)
- [BoringSSL/OpenSSL：两套 API、参数落点和找不到符号时的分支](paopao-android-reverse-compilation/paopao-20260528-01-reference.md)
- [本地 Root 痕迹检测面，以及来源说 Hook 到不了的边界](paopao-android-reverse-compilation/paopao-20260529-01-reference.md)
- [网易云音乐 9.2.80 上「进程还在、agent 被卸」怎么分层](paopao-android-reverse-compilation/paopao-20260604-01-reference.md)
- [招商银行 cmb.pb 上三套检测为什么不能只挡界面](paopao-android-reverse-compilation/paopao-20260605-01-reference.md)
- [网易云音乐 9.2.80 上免 Root 重签和注入方式怎么选](paopao-android-reverse-compilation/paopao-20260611-01-reference.md)
- [JNI RegisterNatives 的定位与反向调用边界](paopao-android-reverse-compilation/paopao-20260625-01-reference.md)
- [内存 SO dump 的时机、ELF 修复和 IDA 验收](paopao-android-reverse-compilation/paopao-20260626-01-procedure.md)
- [Frida Stalker 的事件字段、追踪范围和失效条件](paopao-android-reverse-compilation/paopao-20260629-01-reference.md)
- [DEX 加固代际、头字段和脱壳后怎么判断没取到正文](paopao-android-reverse-compilation/paopao-20260708-01-reference.md)
