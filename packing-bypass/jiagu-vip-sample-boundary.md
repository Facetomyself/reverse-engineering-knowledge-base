---
schema_version: 2
id: packing-bypass-jiagu-vip-sample-boundary
document_type: reference
original_date: "2026-07-02"
archived_date: unknown
scope:
  targets: [qidian, jiagu]
  client: android
  version: "qidian 7.9.464; libjiagu_vip.so; LDPlayer 9 Android 9; Frida 17.15.3"
  observed_at: "2026-07-02..2026-07-15"
sources:
  - id: s1
    ref: "./jiagu-bypass-analysis.md#技术摘要"
    basis: source-report
  - id: s2
    ref: "./jiagu-bypass-analysis.md#11-elf-结构"
    basis: source-report
  - id: s3
    ref: "./jiagu-bypass-analysis.md#12-反检测面"
    basis: source-report
  - id: s4
    ref: "./jiagu-bypass-analysis.md#二动态绕过时间线"
    basis: source-report
  - id: s5
    ref: "./jiagu-bypass-analysis.md#三先判断是否真的需要脱-dex"
    basis: source-report
  - id: s6
    ref: "./jiagu-bypass-analysis.md#五脱壳分流矩阵"
    basis: source-report
  - id: s7
    ref: "./jiagu-bypass-analysis.md#42-状态语义"
    basis: source-report
  - id: s8
    ref: "./jiagu-bypass-analysis.md#43-2026-07-14-实测"
    basis: source-report
  - id: s9
    ref: "./jiagu-bypass-analysis.md#七当前结论"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2, s3, s4]
    basis: source-report
    limits: 只覆盖来源对起点 7.9.464 / libjiagu_vip.so 的静态导入、XOR 字符串和两次 Frida 时间线。direct syscall、匿名 RX 与第二段解密代码未 dump。不能外推到其他 Jiagu 代际或 ARM64 真机。
  - name: decision-flow
    anchor: decision-flow
    sources: [s5, s6, s9]
    basis: source-report
    limits: 分流是来源给出的路线选择，不是本轮执行结果。产品命中仍以 app-protectors 的 protectorKind 为准；本卡不重复 QDSign 算法。
  - name: validation
    anchor: validation
    sources: [s1, s5, s7, s8, s9]
    basis: source-report
    limits: 数字来自来源称为项目级实测、且未把原始 dump 放入公开知识库的记录。本轮没有样本、没有 panda 输出，不能把作者写的“已验证”升成本次 runtime。
relations:
  - type: derived_from
    target: "./jiagu-bypass-analysis.md#12-反检测面"
  - type: supplements
    target: "./app-protectors.md#产品一览"
tags: [Jiagu, qidian, whole-DEX, panda, source-report]
---

# 起点 Jiagu VIP 的检测面、脱壳分流与证明边界

这张卡检索的是：面对 `libjiagu_vip.so` 时，哪些反注入现象已经被来源分开，以及 whole-DEX 扫描能证明什么、不能证明什么。它不替代 [加固产品命中](./app-protectors.md#产品一览) 的观察顺序，也不重复 [Qidian Native SO](../native-analysis/qidian-so-analysis.md#jiagu-与运行时边界) 里的 QDSign 结论。

<a id="risk-control"></a>
## 检测与断连

来源把绕过和脱壳拆开。磁盘上的 `libjiagu_vip.so` 被描述为含运行时解密段、XOR 字符串、`prctl`、direct syscall 和多条终止路径。`LOAD[7]` 在磁盘上是零，由 `DynCryptor` 在运行时解密。字符串侧没有明文 `frida` / `debug` / `ptrace` / `xposed` / `hook`，`sub_6D34` 被记为对 `0xA5` 的 NEON XOR。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 磁盘镜像同时含运行时解密段、XOR 字符串、prctl、direct syscall 和多条终止路径 | s1，技术摘要第 1 点 | source-report | 来源所称 libjiagu_vip.so | 未在本轮打开该 SO |
| C2 | LOAD[7] 磁盘为零，运行时由 DynCryptor 解密 | s2，ELF 结构 | source-report | 同一磁盘镜像 | 解密后的第二代码段未 dump |
| C3 | 反调试相关字符串经 XOR(0xA5)，磁盘无 frida/debug/ptrace/xposed/hook 明文 | s3，反检测面 | source-report | 该磁盘文件 | 不能推出运行时字符串集合 |
| C4 | raise(9) 是一条真实终止链，但 PID 存活不等于 Frida 会话可用 | s4，2026-07-02 | source-report | LDPlayer 9 / Android 9 / Frida 17.15.3 的该次 spawn | 约 5 秒断开会话的后半机制未定位 |
| C5 | 静默 PR_SET_PTRACER、PR_SET_DUMPABLE、PR_SET_SECCOMP 后仍只算终止链部分绕过 | s4，2026-07-05 | source-report | 同一次 prctl 压制 | transport 仍约 2 秒断开 |
| C6 | 重打包 patch kill_0 会因签名变化走到 StubApp / interface20 的 UnsatisfiedLinkError | s4，已否定路线 | source-report | 该次重打包 | 不代表其他补丁点同样失败 |
| C7 | x86_64 native bridge 上 System.loadLibrary 成功，不等于 ARM64 libfock.so 的 JNI 注册完成 | s4，已否定路线 | source-report | LDPlayer x86_64 + libnb.so | 未在 ARM64 真机复核 |
| C8 | 第二代码段未 dump/fix 前，不能把断连归因于单一 libc API | s3，反检测面末 | source-report | 该样本的静态推断 | direct syscall 号与返回路径仍缺 |

<a id="decision-flow"></a>
## 先分流，再选 dumper

来源要求先看 APK 里的业务 DEX，而不是默认脱壳。方法体完整就走 Java/Kotlin/smali，检测链另走 native。只有 stub、真实 DEX 在运行时才出现时，才用 whole-DEX。方法体为空、nop 或 native stub 时，走方法抽取 / CodeItem，而不是指望标准 DEX magic 扫描把方法体补回来。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C9 | 业务 DEX 可读且方法体完整时，应直接做 Java/Kotlin/smali，而不是先脱 DEX | s5，脱壳前判断 | source-report | 来源给出的分流 | 未对其他加固产品复跑 |
| C10 | panda 只认标准 DEX magic/header；把 CDEX 字节直接存下来不等于可反编译 DEX | s6，分流矩阵 | source-report | panda whole-DEX | CDEX 转换器未被来源实测 |
| C11 | whole-DEX 扫描不能自动修复被抽取的方法体，需要主动调用或 CodeItem 路线 | s6 分流矩阵；s9 结论表 | source-report | 方法抽取形态 | FART/JDex2 在来源中仍是候选，不是本样本的修复结果 |

VMP 只应得到壳或 dispatcher，Dex2C 的 Java 方法已在 SO。强 anti-Frida / anti-pause / direct syscall 时，来源要求先做 syscall、匿名 RX 和运行时 SO dump/fix，避免把工具断连写成业务结论。这些是路线限制，不是已经完成的修复。

<a id="validation"></a>
## 这份样本证明了什么

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C12 | 起点 7.9.464 的 12 个 APK 内 DEX 安装前后 SHA-256 一致，业务 DEX 没有被加密掉 | s1，技术摘要第 2 点 | source-report | 该版本 APK 与安装包 | 不证明方法体未被抽取 |
| C13 | whole-DEX 能力被来源称为已验证，Jiagu Native 对抗未闭环，不是完整通杀 | s1，技术摘要结论 | source-report | 该次 panda 与 Frida 记录 | 作者的“已验证”不是本轮 runtime |
| C14 | metadata 状态 complete-enough 只表示本轮文件过了本地结构校验且 dumper/pull 正常结束 | s7，状态语义 | source-report | 来源定义的 dump-dex 状态字 | 不是完整脱壳证明 |
| C15 | 起点/Jiagu VIP 这次导出 13 个 DEX，仍有大量反编译错误，只标部分运行时恢复 | s8，2026-07-14 | source-report | 该次 LDPlayer 扫描 | 第 13 个 DEX 的来源未对齐 |
| C16 | 原始 dump 与 metadata.json 不在公开知识库，数字只是项目级记录 | s8，实测说明 | source-report | 该次数字的可复现性 | 没有公开 fixture 就不能独立重放 |
| C17 | panda 对这个 Jiagu 样本的完整脱壳未被证明 | s9，结论表 | source-report | 该样本 | 与 C15 同一边界 |

partial、invalid、no-dex 分别表示“有有效 DEX 但阶段不完整”、“有输出但没有通过结构校验的 DEX”、“没有拉到 DEX”。数量从 12 变成 13 不能证明业务更完整，也不能证明原来加密过。

## 验证与限制

- 与 `qidian-so-analysis` 重叠的句子（12 个 DEX 未加密、Frida 会话未持久、panda 不能反推加密）保持为来源报告，不在本卡升格。
- `app-protectors` 已经把 360 Jiagu 收到产品表；本卡只补 VIP 样本的检测面、被否定路线和 dump 状态字。
- 未知：断连前的 syscall / fd / watchdog、LOAD[7] 解密结果、第 13 个 DEX 的归属、关键方法是否为空。
- 其他 Jiagu 版本、ARM64 真机和其他业务 SO 不在范围内。
