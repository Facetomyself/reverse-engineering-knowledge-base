---
schema_version: 2
id: frida-android-environment-setup-procedure
document_type: procedure
original_date: '2026-05-06'
archived_date: '2026-10-02'
scope:
  targets: [frida-android-environment-setup]
  client: Android
  version: source example pin 16.5.2; rule is three-part equality, not that pin
  observed_at: unknown
sources:
  - id: s1
    ref: ./paopao-20260506-01.md#frida学习笔记二环境搭建一条龙
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 只保留来源的安装、验收和停止条件。改名、非标端口和 Gadget 是条件分支，不延伸成检测对抗。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: ABI 对照、默认端口和示例版本号都是来源文本。本轮没有下载或安装。
  - name: validation
    anchor: acceptance
    sources: [s1]
    basis: source-report
    limits: 三条验收是来源定义的观察句。本轮没有设备输出。
relations:
  - type: derived_from
    target: ./paopao-20260506-01.md#frida学习笔记二环境搭建一条龙
tags: [frida, frida-server, android, source-report]
---

# Frida Android 实验环境：版本对齐、验收与停止条件

这份流程回答：来源怎样判断电脑端和设备端已经对齐，以及哪些报错必须停住。它不覆盖某一款 App 的检测绕过，也不把示例版本 16.5.2 写成唯一可用版本。来源是 [Frida 环境搭建归档](./paopao-20260506-01.md#frida学习笔记二环境搭建一条龙)。

原理篇已经记录 ArtMethod、补丁宽度和 Spawn 时点。本卡只处理安装和验收。`unknown` 目标上的 Hook 技巧卡、未导出函数定位卡都不是这条安装流程。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 来源要求 | 不足时 |
|---|---|---|
| 设备 | 初学 `正在学习 Frida 的基本用法，  ** 用模拟器  **`；有模拟器检测、Native 加密或要贴近线上时用真机 | 不按这个分流就不要把模拟器上的 Native 结果当成线上结果 |
| 解释器 | `建议使用 Python 3.7 或以上版本`。第 112 行是被折行误标成标题的半句，不是一节版本说明 | 多套 Python 时先隔离环境，再谈版本对齐 |
| 架构 | 模拟器 CPU 是 x86 时，`frida-server 也应该选择  ** x86 或 x86_64 版本  **`，与 App 内部 SO 的 ABI 无关 | ABI 未读就走 F1 |
| 权限 | frida-server 需要 root 才能 ptrace。放置目录的理由包括 `不受 SELinux 的 neverallow 规则限制` | 不能 root 时只评估 Gadget 分支，失败走 F5 |

<a id="parameters"></a>
## 参数口径

电脑端 `frida` 与 `frida-tools` 必须是同一个三段版本：`这两个版本号必须完全一致`，而且 `严格三段对齐是稳态做法`。来源用 16.5.2 做例子，不是规定只能装这个修订号。

`adb shell getprop ro.product.cpu.abi` 的对照是：`arm64-v8a` 对应 `frida-server-X.Y.Z-android-arm64`，`armeabi-v7a` 对应 `android-arm`，`x86_64` 对应 `android-x86_64`，`x86` 对应 `android-x86`。Apple Silicon 上的 ARM AVD 仍走 arm64，来源明确反对把模拟器一律当成 x86。

来源写 `frida-server 默认监听 TCP 端口 27042`。守护启动用 `-D`，并用来源所说的 `&` 防止个别设备上 shell 不返回。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 按前提选定真机或模拟器，并读到 CPU ABI | ABI 字符串和对应的 frida-server 文件名 | ABI 读不到走 F1 |
| S2 | 把命令行包和 Python 绑定装到同一三段版本，再把同版本、同 ABI 的 frida-server 推到 `/data/local/tmp` 并以 root 和 `-D` 启动 | `这两个版本号必须完全一致`；进程监听 `TCP 27042` | 版本不一致走 F1，不进入验收 |
| S3 | 做来源的三步观察：列出进程、附加到已经打开的系统设置、用 Spawn 跑到 Java 层 | 见验收三条 | 任一条看不到就走 F1 或 F2，不宣称环境就绪 |
| S4 | 只有默认端口或进程名挡住时，才使用来源的非标端口或改名。没有 root 时才评估 Gadget | 改名仅 `绕过基于字符串匹配`；来源接着写 `这些只是基础的反检测手段` | 需要抹掉内存特征或 maps 时走 F4，本卡不继续 |

<a id="outputs"></a>
## 输出

输出是三句话能对上的实验环境：进程列表可见、附加后脚本能执行、Spawn 后 Java 桥能挂上。不输出目标 App 的参数、密钥或检测绕过结果。来源的一键脚本只是把「没有设备就退出、`frida-ps -U` 失败就退出」固化下来，脚本本身不是验收证据。

<a id="acceptance"></a>
## 验收

1. `frida --version`、Python 里的 `frida.__version__`、设备上 `frida-server --version` 三段都相同。示例输出 16.5.2 只说明来源当时的针，换修订号时三处一起换。
2. `frida-ps -U` 能列出进程。来源把这句当作 `frida-tools -> USB -> frida-server 的通信链路正常`。
3. Spawn 路径打印 `Java VM attached!`。这只说明 Java 桥挂上，不说明任何业务 Hook 正确。
4. 设置进程不在前台时，来源把 `unable to find process` 归为还没打开应用，而不是版本故障。

<a id="failure-exits"></a>
## 失败出口

F1：`unable to communicate`。先确认进程在、三段版本一致、`adb devices` 不是 unauthorized 或 offline。缺任何一项就停止，不去改 App。

F2：`unable to access zygote64`。来源的临时动作是 `setenforce 0`，并且写明 `只是临时修改，重启设备后会恢复为 Enforcing`。重启后旧结论作废。

F3：`Trace/BPT trap` 或闪退。先换成只打印日志的脚本。来源把「空脚本也会闪退」判成 App 自己的检测，并指向别篇。本卡停在这个出口，不补检测修改。

F4：端口或进程名分支仍然不够。来源写明内存里的特征串和 `frida-agent.so` 的 maps 映射还在。停止把改名或换端口写成已经隐藏。

F5：Gadget。它 `不涉及  ` ptrace  ` ，所以不需要 Root 权限`，但 `这会改变 APK 的签名`。签名校验拒绝时停止，不把重打包记成已接入。重载对不上时用 `.overload()` 指定参数；方法名不存在就停止，不猜混淆后的名字。

Wi-Fi 只替换传输。来源写延迟通常比 USB 高，Stalker 这类场景仍建议 USB。它不是一条检测对抗路径。
