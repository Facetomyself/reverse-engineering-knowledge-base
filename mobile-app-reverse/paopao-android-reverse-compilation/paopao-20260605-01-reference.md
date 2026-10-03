---
schema_version: 2
id: paopao-20260605-cmb-detection-routes-reference
document_type: reference
original_date: '2026-06-05'
archived_date: '2026-10-02'
scope:
  targets:
    - cmb.pb
  client: android
  version: 13.2.0+
  observed_at: '2026-06-05'
sources:
  - id: s1
    ref: "./paopao-20260605-01.md#六方法论升级环境伪装-vs-ui-兜底-vs-粗暴-patch"
    basis: source-report
  - id: s2
    ref: "./paopao-20260605-01.md#二cmbshieldnative-反-frida-的四条路径"
    basis: source-report
  - id: s3
    ref: "./paopao-20260605-01.md#一招行的三套独立反检测体系"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s2, s3]
    basis: source-report
    limits: 三套 SDK 和四条路径是作者对 cmb.pb 13.2.0+ 的拆分。弹窗和返回值未复跑。脚本和补丁编码不在本卡。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s3]
    basis: source-report
    limits: 路线排序和时机是作者的取舍。上报通道未被本轮核对。不把服务器是否接受写成事实。
relations:
  - type: derived_from
    target: "./paopao-20260605-01.md#六方法论升级环境伪装-vs-ui-兜底-vs-粗暴-patch"
tags:
  - cmb.pb
  - source-report
---

# 招商银行 cmb.pb 上三套检测为什么不能只挡界面

这张卡只回答：来源如何拆这三套并联检测，以及它为什么把「只挡弹窗」排在「让应用自己读到干净环境」后面。不收录补丁字节、伪装脚本或监听命令。

<a id="risk-control"></a>
## 三套并联和四条路径的性质

来源把样本收成 `cmb.pb`，检测写成三套独立 SDK，任意一套命中都弹窗。注入风险和安全风险不是同一个弹窗。

> 3 套独立 SDK 并联运行

> 「注入风险」和「安全风险」是两个独立弹窗

CmbShield 内部又是四条路径。来源把前两条写成会直接破坏运行环境，不处理的话活不到 Java 侧；后两条是 maps 与 linker 枚举。anti_thread 主动扫线程。kill 路径上的可见现象仍是 `Process terminated`。

> 4 条独立路径并联

> frida 根本活不到

> 主动扫描进程内所有线程

> Process terminated

maps 这条若改行，长度不能变，否则解析位置、读出的字节数或换行数会自己成为信号。`dl_iterate_phdr` 不读 maps 文件，它念的是内存里的清单。命中后也不当场弹窗，先落信号文件。

> 长度不变是关键

> 它念的是内存里的清单

> 不当场弹窗

RootBeer 里来源点了两个易漏点：数组形式的 `which` 不能只看第一个元素；native 探测走的是 fopen，只覆盖 stat/access 会漏。DEC 不在 base dex 里，`getCheckResult` 读 `envc.push`。来源称写者绕开了 libc 写 API，并且这篇没有把写者追完。

> su/busybox/magisk 都拦

> 对 root 路径返 NULL

> envc.push

> 绕开了整个 libc 写 API

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C2 | 3 套独立 SDK 并联运行 | 正文第 51 行 | source-report | cmb.pb 13.2.0+ | 未复跑弹窗 |
| C3 | 「注入风险」和「安全风险」是两个独立弹窗 | 正文第 59 行 | source-report | 两套 UI | 对应 SDK 依来源表 |
| C5 | 4 条独立路径并联 | 正文第 87 行 | source-report | libCmbShield | 名称依速查表 |
| C9 | 长度不变是关键 | 正文第 215 行 | source-report | maps 的 fread 解析 | 不收录替换文本 |
| C10 | 它念的是内存里的清单 | 正文第 230 行 | source-report | dl_iterate_phdr | 不收录回调 |
| C14 | envc.push | 正文第 383 行 | source-report | DEC getCheckResult | 不收录文件内容 |
| C15 | 绕开了整个 libc 写 API | 正文第 394 行 | source-report | envc.push 写者 | 写者未定位 |

<a id="decision-flow"></a>
## 时机和三条路线怎么排

这个样本的早期入口在替身 Application。来源因此写不能 attach，要在 `attachBaseContext` 之前用 spawn。这和上篇同意页再 attach 不是同一条时机。

> 不能 attach

native 库的检测不在 `.init_array` 的静态构造里，而在 `JNI_OnLoad`。来源把 `android_dlopen_ext` 的 onLeave 写成补 native 库的窗口。

> 最佳时机

三条路线里，粗暴改返回值会让应用不知道检测失败，UI 兜底只是用户看不见。来源把环境伪装定义成检测仍跑完，但读到的数据是干净的，于是应用自己判定干净。只挡本机弹窗不够，因为风险事件仍会上报到服务器侧。

> 真的判定** 自己处于干净环境

> 上报到服务器侧风控

追数据时，来源要求先找到写入者。一个看起来像风险标志的持久化值，追下去是分屏开关。

> 先 trace 它的

目标句是让应用自己判定干净，而不是只挡界面。

> 让招行自己判定环境 clean（环境伪装路线），而非挡掉 UI

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 让招行自己判定环境 clean（环境伪装路线），而非挡掉 UI | 正文第 44 行 | source-report | 本篇目标 | 不是验收结果 |
| C4 | 不能 attach | 正文第 83 行 | source-report | 替身 Application 早期检测 | 不适用于同意页样本 |
| C16 | 先 trace 它的 | 正文第 417 行 | source-report | 可疑持久化值 | 键值不收录 |
| C17 | 真的判定** 自己处于干净环境 | 正文第 484 行 | source-report | 环境伪装这一行 | 不收录 API 清单 |
| C18 | 上报到服务器侧风控 | 正文第 486 行 | source-report | 只挡弹窗的后果 | 未核对上报字段 |
| C19 | 最佳时机 | 正文第 508 行 | source-report | dlopen onLeave 补 native SO | 不是通用注入时机 |

## 验证与限制

没有本地运行。`isRooted` 返回值和弹窗清零都是作者自述。`envc.push` 的写者停在「libc 写 API 零命中」这一步，指令级定位来源自己留作以后。第八节的百分比是估计，不能当验收。去指纹构建和端口命令不在本卡。
