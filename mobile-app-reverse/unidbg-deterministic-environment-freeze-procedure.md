---
schema_version: 2
id: mobile-app-reverse-unidbg-deterministic-environment-freeze-procedure
document_type: procedure
original_date: '2026-04-28'
archived_date: '2026-10-02'
scope:
  targets: [Android native deterministic-analysis harness]
  client: Android Unidbg and Frida
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./paopao-android-reverse-compilation/paopao-20260428-01.md#完整工作流
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 这是从一篇 Unidbg 方法文章提炼的确定性基线流程，不代表任意 Android 版本、Unidbg 实现或目标 SO 均可直接复用。
  - name: parameters
    anchor: source-inventory
    sources: [s1]
    basis: source-report
    limits: 仅登记随机源和环境指纹的来源层级；不发布目标设备值、请求样值、密钥或具体签名输入。
  - name: validation
    anchor: acceptance
    sources: [s1]
    basis: source-report
    limits: 验收项是来源方法中的证据门，不是本轮对设备、SO、Frida、Unidbg 或服务端的运行验证。
relations:
  - type: derived_from
    target: ./paopao-android-reverse-compilation/paopao-20260428-01.md#完整工作流
tags: [android, unidbg, frida, deterministic, entropy-sources, vDSO, source-report]
---

# Android Native 确定性基线与环境冻结流程

本文把来源文章中的“先消除变化，再谈补环境和算法对照”整理成一条可复用流程。目标是把同一输入下的 Unidbg 输出、Frida 真机输出和 trace 对拍变成可解释的证据面；它不提供目标签名器，也不把固定值或示例 Hook 当作当前样本的实现。

<a id="prerequisites"></a>
## 前提与输入

- 明确 native 入口、固定输入、输出边界和每次 run 的重置条件；没有稳定输入时不能判断“环境是否补对”。
- Unidbg harness 能分别记录 JNI、libc、syscall 和文件访问；Frida 侧能观察 Java 与 native/libc 两条可能路径。
- 每次运行都保留 run ID、输入摘要、输出摘要和 trace/日志位置；原始设备材料与敏感 fixture 留在受限证据区。
- 预先定义基准设备的环境画像，包括 Android ID、Build、显示、安装时间、电池和 UID/GID 等跨设备变化项；不把未知值默认为一致。

<a id="source-inventory"></a>
## 变化源分层

| 层级 | 需要盘点的变化源 | 来源建议的观察/控制面 | 关键边界 |
|---|---|---|---|
| JNI | 时间、`Random`、`UUID`、`SecureRandom` 等 | Unidbg `AbstractJni`；Frida Java 层 | `callXxxMethod` 与 `callXxxMethodV` 都要核对；`SecureRandom` 不能因覆盖 `Random` 而视为已覆盖 |
| libc | `time`、`clock`、`rand/srand`、`arc4random` | Unidbg 的 HookZz/xHook 类入口；Frida native 入口 | 先看 `srand` 的种子和调用关系，再决定是否覆盖 `rand`；不要用恒定返回破坏原生 PRNG 序列 |
| syscall | `clock_gettime`、`getrandom`、UID/PID 等 | `SyscallHandler` 记录与最小覆盖 | `CLOCK_MONOTONIC` 必须保持单调语义，不能与墙钟和开机时间混为一个常量 |
| 文件 | `/dev/urandom`、`/dev/random`、`/proc/uptime`、`/proc/stat` 等 | `IOResolver` 记录并按需返回虚拟内容 | 文件层未观察到时不能假定 JNI 或 syscall 覆盖了它 |
| 设备环境 | Android ID、Build、显示、安装时间、电池、UID/GID | 基准真机采集后在 Unidbg 建立同一画像 | 值之间需要内部一致；设备画像不是“随机数”，但跨运行对照同样必须固定 |

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 固定输入、native 入口、输出边界和 run reset 规则。 | run manifest、输入/输出摘要、环境版本。 | 边界闭合走 S2；缺入口或重置条件走 F1。 |
| S2 | 按 JNI、libc、syscall、文件和设备环境五层建立变化源清单。 | source inventory、控制点与未覆盖项。 | 每项有观察路径走 S3；只凭猜测归类走 F2。 |
| S3 | 先在 Unidbg 侧逐层固定，并用全新 VM/进程运行同一输入多次。 | 每次输出、JNI/syscall/文件日志和差异摘要。 | N 次输出及相关 trace 完全一致走 S4；仍有差异回 S2。 |
| S4 | 在 Frida 真机上以相同语义镜像已固定的层，包括 Java、libc/vDSO 和文件/系统调用可见面。 | Frida 控制清单、基准设备画像和 run 记录。 | 控制面对应走 S5；仅固定 Java 而 native 仍变走 F3。 |
| S5 | 用相同输入对照 Unidbg、Frida 和必要的指令 trace，按字段标记固定项、输入相关项和剩余变化。 | cross-run matrix、trace diff、未解释项清单。 | 所有差异有来源解释走 S6；出现新差异回 S2。 |
| S6 | 只有确定性基线闭合后，才进入补环境、算法还原或 parity 分析。 | 可复核的基线回执和下一阶段假设。 | 基线未闭合时停止，不把输出差异归因于算法。 |

<a id="outputs"></a>
## 输出

1. `run manifest`：入口、输入摘要、环境版本、重置方式和每次 run ID。
2. `source inventory`：五层变化源、观察点、控制点、未覆盖项及其证据定位。
3. Unidbg 与 Frida 的控制清单：明确 Java 与 native/libc/vDSO 是否分别覆盖。
4. `cross-run matrix` 与 trace diff：区分固定、输入相关、随机和未解释变化。
5. 受限环境画像快照及清理记录；Public 文档只保留类别和证据边界，不复制设备值或请求材料。

<a id="acceptance"></a>
## 验收

| 门 | 通过条件 | 不能代替它的东西 |
|---|---|---|
| A1 输入稳定 | 同一输入、同一入口和相同 reset 规则可被多个 run 重复执行 | 只看到一次输出、只记录调用成功 |
| A2 Unidbg 稳定 | 多次全新运行的目标输出和相关 trace 无未解释差异 | 只固定 `currentTimeMillis` 或只比较最终字符串 |
| A3 跨层覆盖 | JNI 的 V/非 V 路径、libc 入口、syscall 与可能的 vDSO、文件层均有观察或明确 unknown | 只做 Java Hook、只拦 syscall、只看日志关键词 |
| A4 跨运行时可比 | Frida 与 Unidbg 使用同一组控制语义和基准设备画像，差异能定位到环境或实现层 | 两边使用不同随机/时间策略、设备画像随意填写 |
| A5 结论可追溯 | 每个剩余差异有 run ID、层级、调用点或文件访问证据；未知继续保留 | 把相似值、单次命中或“看起来像算法”当作通过 |

以上是来源报告提炼的流程与验收定义。本轮没有运行设备、Unidbg、Frida、目标 SO、parity fixture 或服务端请求，因此不报告 runtime、local parity 或 server acceptance。

<a id="failure-exits"></a>
## 失败出口

- **F1：输入或运行边界不闭合。** 先补入口、固定输入、输出范围和 reset 规则；不以一次成功调用替代基线。
- **F2：变化源未定位。** 回到 JNI/libc/syscall/文件/设备五层逐项加观察，保留差异 run；不直接猜算法或强行固定所有函数。
- **F3：跨层控制不等价。** 分开核对 Java、native/libc、vDSO、syscall 和文件路径；必要时将该项标为 unknown，不能宣称 Unidbg 与 Frida 可比。
- **F4：时间语义被破坏。** 检查单调时钟递增、超时计算和 `srand`/PRNG 状态；不要用恒定值掩盖时序或状态机问题。
- **F5：来源证据不足。** 若只有教学代码或作者自述，保留 `source-report` 流程和限制，不升级成当前设备、算法或服务端结论。
