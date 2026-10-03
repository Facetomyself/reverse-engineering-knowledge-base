---
schema_version: 2
id: paopao-20260604-ncm-kill-layers-reference
document_type: reference
original_date: '2026-06-04'
archived_date: '2026-10-02'
scope:
  targets:
    - com.netease.cloudmusic
  client: android
  version: 9.2.80
  observed_at: '2026-06-04'
sources:
  - id: s1
    ref: "./paopao-20260604-01.md#十方法学沉淀"
    basis: source-report
  - id: s2
    ref: "./paopao-20260604-01.md#八快层检测面与-winning-recipe"
    basis: source-report
  - id: s3
    ref: "./paopao-20260604-01.md#二战场五个半安全库"
    basis: source-report
  - id: s4
    ref: "./paopao-20260604-01.md#三libnesec逆清持续猎杀者"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2, s4]
    basis: source-report
    limits: 分层、检测面和退出现象都是作者对 9.2.80 一次实验的自述。秒数未复跑。指令编码和脚本不在本卡。
  - name: parameters
    anchor: parameters
    sources: [s3, s4]
    basis: source-report
    limits: 偏移来自作者一次内存 dump。来源写明会随版本和重打包漂移。没有签名算法。
relations:
  - type: derived_from
    target: "./paopao-20260604-01.md#十方法学沉淀"
tags:
  - com.netease.cloudmusic
  - source-report
---

# 网易云音乐 9.2.80 上「进程还在、agent 被卸」怎么分层

这张卡只回答两件事：来源把这次易盾反调试分成哪两层，以及快层认什么、不认什么。不收录 hook、NOP 列表或补丁编码。Web 易盾验证码不是这条 native 面。

样本是来源写下的 `com.netease.cloudmusic` 9.2.80、arm64、易盾壳。同系列 2026-06-11 对 Android 13 另有自述，本卡不合并裁决。

<a id="parameters"></a>
## 签名入口和会漂移的偏移

来源把要观察的 Java 入口写成下面这个形态，并说明喂路径和 JSON、吐十六进制。

> serialdata(String apiPath, String jsonParams) -> String

> 喂它一个接口路径 + 一段 JSON 参数，吐出一串十六进制签名。

真身不在导出表。来源把它指到 `libpoison + 0x7a28c`，同时写明偏移不是稳定地址。

> 会随版本 / 重打包漂移

`0xa1ab4` 在来源里不是检测函数，而是 208 字节的任务描述符调度器。字段表不抽成可复用布局。

> 208 字节，结构是这样：

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | serialdata(String apiPath, String jsonParams) -> String | 正文第 61 行 | source-report | 9.2.80 来源样本 | 未复现算法 |
| C2 | 喂它一个接口路径 + 一段 JSON 参数，吐出一串十六进制签名。 | 正文第 64 行 | source-report | 同上 | 未核对接口字段 |
| C3 | libpoison + 0x7a28c | 正文第 99 行 | source-report | 作者那一次 dump | 会漂移 |
| C4 | 会随版本 / 重打包漂移 | 正文第 124 行 | source-report | 文中全部偏移 | 不能当 ABI |
| C5 | 208 字节，结构是这样： | 正文第 196 行 | source-report | 0xa1ab4 的 job | 字段未逐项收录 |

<a id="risk-control"></a>
## 两层击杀和快层检测面

现象不是进程自杀。来源写进程还在前台，会话却在大约 1 到 90 秒之间被卸；挂在 libc 终止类函数上的钩子没有命中。

> app 进程还在前台好好跑，Frida 会话却在 +1～90 秒之间被「卸载」

> 会话被卸之前， **零命中**

libnesec 的 SIGTRAP 自检看信号有没有被截走。线程名扫描对 status 第一行是逐字节读。调度器上的 verdict 只记账。inline svc 的有无用来区分谁能绕开 libc：MSA 被写成静态 0 个。

> 它检测的不是「有没有 ptrace」

> 逐字节

> verdict 只是 libnesec「判没判我」的记账，不是「怎么卸我」的开关

> MSA 没有 inline svc（静态确认 0 个），任何动作只能走 libc

同意之前不全量启动反调试。纯 Java、不改 native 文本，仍然被杀，所以「一改代码就自校验」不是这条基线的解释。重建后的两层是：

> 反调试是在「同意之后」才全量启动的

> 纯 Java、零 native .text 修改，照样被杀

> 慢层** = MSA 构造函数检到 agent

> 快层** = 随「装了任何 gum hook」即触发的 agent 内存损坏

慢层被说成 solist 上的注入名查询，来源希望它永远返回 0。快层曾经被误当成 maps 扫描。后来的检测面只保留三类，并且明确不把匿名可执行页本身算进去。

> 最干净的补丁：让它永远返回 0

> 我一度认定快层 = libnesec 的 maps 扫描

> 快层只检测三类

> 硬件断点 / 调试寄存器

> 也不检测匿名 r-x 映射本身

作者把非安全库上的 native 会话写成满 240 秒仍在。这只是自述。同一做法换 Android 版本或换设备状态就不成立；本篇还把同意页窗口写成 Android 14 专属。

> 会话满 240 秒不被杀

> recipe 不是对「这个 app」生效

> Android 14 的「同意页干净窗口」是 Android 14 专属

退出对照只保留现象分类：进程还在而被报终止，表示 agent 被损坏。

> agent 被损坏，进程没事

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | app 进程还在前台好好跑，Frida 会话却在 +1～90 秒之间被「卸载」 | 正文第 67 行 | source-report | 本篇第一次现象 | 未复跑 |
| C7 | 会话被卸之前， **零命中** | 正文第 73 行 | source-report | libc 终止类挂钩 | 未核对清单 |
| C10 | verdict 只是 libnesec「判没判我」的记账，不是「怎么卸我」的开关 | 正文第 219 行 | source-report | libnesec verdict | 单次自述 |
| C14 | 慢层** = MSA 构造函数检到 agent | 正文第 336 行 | source-report | 来源的慢层 | 秒数未复跑 |
| C15 | 快层** = 随「装了任何 gum hook」即触发的 agent 内存损坏 | 正文第 337 行 | source-report | 来源的快层 | 凶手二选一 |
| C17 | 快层只检测三类 | 正文第 409 行 | source-report | 晚挂实验之后的模型 | 全文跨三行 |
| C22 | recipe 不是对「这个 app」生效 | 正文第 459 行 | source-report | 三台设备对照 | 未复跑 |
| C24 | agent 被损坏，进程没事 | 正文第 487 行 | source-report | 退出现象分类 | 不是步骤 |

## 验证与限制

没有本地运行。240 秒、97 秒和 Android 13 约 1 秒都是作者计时。NOP 偏移、补丁字节和 SSL 钩子不在本卡。2026-06-11 笔记称干净设备态下 Android 13 并没有秒杀裸 agent，那条冲突留在那一篇的 decision-flow，不在这里改写成已裁决。
