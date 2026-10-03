---
schema_version: 2
id: unidbg-boundary-and-alternatives-reference
document_type: reference
original_date: '2026-04-29'
archived_date: '2026-10-02'
scope:
  targets:
    - unidbg
    - frida
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260429-01.md#unidbg-目前的边界"
    basis: source-report
  - id: s2
    ref: "./paopao-20260429-01.md#替代-1-qiling-framework"
    basis: source-report
  - id: s3
    ref: "./paopao-20260429-01.md#替代-3-frida--rpc"
    basis: source-report
  - id: s4
    ref: "./paopao-20260429-01.md#工具选型决策矩阵"
    basis: source-report
  - id: s5
    ref: "./paopao-20260429-01.md#趋势-4-so-保护技术的演进"
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s2, s4, s5]
    basis: source-report
    limits: 边界和选型表是系列收束时的作者判断。文件数、commit 节奏和成本表都没有版本钉，成本数字不进入本模块。
  - name: risk-control
    anchor: risk-control
    sources: [s3]
    basis: source-report
    limits: 只记录来源列出的 Frida 进程内痕迹和对 TracerPid 的稳态限制。不提供隐藏步骤，也没有某个 SDK 的当前检测规则。
relations:
  - type: derived_from
    target: "./paopao-20260429-01.md#unidbg-目前的边界"
tags:
  - unidbg
  - frida
  - source-report
---

# Unidbg 的边界、替代方向和 Frida 痕迹对照

这张卡只回答两件事：来源认为 Unidbg 在什么目标上不该继续用，以及它把 Frida 的哪些进程内痕迹当成检测面。Trace 三层接口和六种 Hook 框架不在这里。大模型、Rust 重写和 KVM 三段是预测，不收成模块。成本表来源自己标成数量级估计，也不收成参数。

来源没有可公开定位的原文 URL，也没有 unidbg commit。

<a id="decision-flow"></a>
## 什么时候离开 Unidbg

来源列了四条结构边界。

单模块视野：另一个 SO 可以再加载进来调用，但两个 SO 靠全局状态、共享内存或 binder 协作时，来源写「Unidbg 就抓瞎了」。举例是风控 SDK 初始化要通过 binder 向系统服务要 SIM 卡序列号，Unidbg 没有这条通路。`dlopen` 之后互相回调被写成可以做但很麻烦。

Java 嵌入：来源写它不能当 IDA / Ghidra 插件，也不能当 Python 库 import，JVM 启动要 1 到 2 秒。对照句是 Qiling 选在 Python 生态。来源给出的幻想代码是 `import unidbg`，并明确那是幻想，不是可用绑定。

维护阶段：大功能被写成集中在 2019–2022，2023 之后 commit 变慢、PR 仍在合并。没有 commit 列表，只能当作者对仓库节奏的叙述。

iOS：`unidbg-ios/src` 被写成 287 个 java 文件，`unidbg-android/src` 231 个，但来源的结论不是「iOS 实现更完整」，而是开箱兼容性更差、系列案例都是 Android。原句级建议是：没有人用 Unidbg 跑通过该 iOS 样本时，直接走 Frida 加越狱机。

替代的分界只保留来源写死的不适配，不保留主页宣传：

| 方向 | 来源写的分界 |
|---|---|
| Qiling | Python，可嵌 IDA；`qiling.os.android` 有 JNIEnv / RegisterNatives / JNI_OnLoad，但 Android JNI 覆盖低于 AbstractJni。纯 Android JNI 仍选 Unidbg |
| ExAndroidNativeEmu | 代码量小，适合读原理；AbstractJni、文件系统、Backend 切换和 Trace 都更弱。主仓库被写成基本停滞 |
| Frida + RPC | 真环境，单设备不能撑高并发，且有下面的进程内痕迹 |
| 云手机 + Frida | 来源认为环境更真，成本和管理是限制。不把「绕过几乎所有模拟器检测」当成已测结果 |
| 自定义 QEMU | 来源写成团队半年以上，不适合个人或小团队 |

选型表里和本卡有关的几行是作者给出的查表结果，不是测量：深度算法分析推荐 Unidbg + Unicorn2 + Trace，并写 Frida 没法 Trace；跨架构和 Windows PE 推荐 Qiling，不推荐 Unidbg；iOS 推荐 Frida 加越狱机。甜蜜点原句是「Android Native + 算法分析 + 中等并发」。三个条件缺一个，来源就改派到 Qiling、真机或算法还原。

VMP 改变的是 Trace 的用途，不是再加一个 hook。来源写：解释器循环里 Trace 到的是 `ldr/cmp/b.eq`，Unidbg「仍然有用，但用法完全变了」，从白盒分析工具变成「高速日志收集器」，语义还原它做不了。TEE 被写成进程侧只能看到调用的输入输出，Unidbg 拿不到放在 TrustZone 里的密钥。这两句是保护形态判断，没有样本。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 两个 SO 通过某个全局状态、共享内存、binder 互动时，来源写 Unidbg 就抓瞎了 | s1，`paopao-20260429-01.md:61` | source-report | unidbg 的进程模型 | 没有该风控 SDK 的复现 |
| C2 | iOS 树被写成 287 个 java 文件，Android 树 231 个，但开箱兼容性结论相反 | s1，`:124-125` | source-report | 来源计数当时的仓库 | 无 commit，未数文件 |
| C3 | Qiling 的 `qiling.os.android` 有 JNI 基础设施，覆盖仍被写成低于 AbstractJni | s2，`:160` | source-report | Android JNI 选型 | 未对照两边源码 |
| C4 | 深度算法分析一行推荐 Unidbg + Unicorn2 + Trace，并把 Frida 写成没法 Trace | s4，`:309` | source-report | 来源的选型表 | Trace 接口细节不在本卡 |
| C5 | 遇到 VMP 时，来源把 Unidbg 改称为高速日志收集器，而不是白盒分析工具 | s5，`:438-439` | source-report | 来源描述的自定义字节码保护 | 没有 VMP 样本 |

<a id="risk-control"></a>
## Frida 进程内痕迹

这段只服务「Frida 为什么不是不可检测方案」。来源列出六类痕迹，并单独把 TracerPid 从稳态检测里拿掉。不写如何改这些痕迹。

| 序 | 来源点名的痕迹 | 来源写的观察点 |
|---|---|---|
| 1 | 线程名 | `gmain`、`gdbus`、`gum-js-loop`、`pool-frida-*`，读 `/proc/self/task/<tid>/comm` |
| 2 | 默认端口 | `127.0.0.1:27042` |
| 3 | 注入期管道 | `/data/local/tmp/` 下 `linjector-` / `binjector-` 前缀，查 `/proc/net/unix` |
| 4 | 入口改写 | `Interceptor.replace` 写跳转；`Interceptor.attach` 也会改被 hook 函数前若干字节 |
| 5 | 映射名 | `/proc/self/maps` 里名字含 `frida`，点名 `libfrida-agent.so` / `libfrida-gadget.so` |
| 6 | 字符串 | `frida:rpc`、`re.frida.server` |

TracerPid 的限制原意是：frida-server 注入时用 ptrace，完成后 `PTRACE_DETACH`，稳态下 TracerPid 回到 0，所以它抓不住已经注入完的 frida-server；能抓住的是 frida-trace、frida CLI attach、GDB/IDA 这类长期附着。来源把前两条叫 Frida 特有，后面几条叫被 hook 进程的通用痕迹。

选型表里「完全无法被检测」一行把云手机加 Frida 隐身写成推荐，只点了 hluda、strongR-frida、patchless-hook 这些名字。本卡不展开这些名字背后的做法。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | frida-server 默认监听被写成 `127.0.0.1:27042` | s3，`:222` | source-report | 来源描述的默认配置 | 未扫描端口，改端口后的行为未知 |
| C7 | frida-server 只在注入瞬间用 ptrace，稳态下 TracerPid 会回到 0，对已注入的 frida-server 不可靠 | s3，`:228-230` | source-report | 来源对 ptrace 窗口的描述 | 未在设备上读 TracerPid |

## 验证与限制

287 与 231 没有日期和 commit。2019–2022 的维护叙述没有附提交。日调用 50 万次、50ms、200ms 那张表，来源写明是数量级估计且可有 2 到 5 倍偏差，所以不进模块。LLM 准确率 60% 到 80%、Rust 重写要 2 到 3 年、KVM 快 10 到 100 倍，都是预测。系列 20 篇回顾和文末链接是目录。本轮没有运行 Unidbg、Qiling 或 Frida。
