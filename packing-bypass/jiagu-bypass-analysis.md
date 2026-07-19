# 360 Jiagu VIP 绕过与脱壳能力更新

> 来源: `workspace/qidian`
> 原始发布时间: 2026-07-02
> 归档日期: 2026-07-05
> 分类: packing-bypass
>
> 样本: 起点读书 7.9.464 / `libjiagu_vip.so` ｜ 更新: 2026-07-15
>
> 当前状态: 终止链与部分 `prctl` 链已定位；Frida 进程存活不等于会话持久；LDPlayer + panda whole-DEX 路线已跑通

## 技术摘要

这次更新需要把“绕过”和“脱壳”拆成三个独立问题：

1. `libjiagu_vip.so` 的磁盘镜像包含运行时解密代码段、XOR 字符串混淆、`prctl`、direct syscall 和多条终止路径；
2. 起点读书 7.9.464 的 12 个 APK 内 DEX 安装前后 SHA-256 全部一致，该样本并未把业务 DEX 加密掉；
3. 2026-07-14 新增的 `dump-dex.ps1` 已在 LDPlayer x86_64 + `libnb.so` native bridge 上执行 AArch64 panda，并从 Jiagu 进程导出 13 个标准 DEX，但仍有大量 loading/decompile errors，只能标记为部分运行时恢复。

因此，准确结论是“whole-DEX 能力已验证、Jiagu Native 对抗仍未闭环”，不是“360 Jiagu 已完整通杀”。

## 一、`libjiagu_vip.so` 静态证据

### 1.1 ELF 结构

- 文件大小: 889,192 bytes；
- 架构: ARM64 / AArch64；
- 5 个 LOAD 段；
- `LOAD[7]` 位于 `0x257000-0x25f4f8`，磁盘内容为零，运行时由 `DynCryptor` 解密；
- `.init_array` 与 `.fini_array` 在磁盘镜像中为空，不能只按静态数组判断 constructor 链。

| 地址 | 名称 | 已确认用途 |
|------|------|------------|
| `0x8fe0` | `JNI_OoLoad` | 初始 JNI 入口，执行内存保护与 SO 名称处理 |
| `0x9f6c` | `_Z9__arm_a_1...` | JNI 包装与后续初始化 |
| `0x6f60` | `DynCryptor::__arm_c_0` | 解密第二代码段 |
| `0x6d34` | `sub_6D34` | NEON 批量 XOR(`0xA5`)，21 处 xref |
| `0x2790` | `kill_0` | kill PLT 桩，116 处 xref |
| `0x258a38` | `JNI_OnLoad` | 位于运行时解密段的 JNI 入口 |

### 1.2 反检测面

磁盘文件中没有 `frida`、`debug`、`ptrace`、`xposed`、`hook` 明文，相关字符串经 XOR(`0xA5`) 处理。关键导入包括：

| 导入 | 风险点 |
|------|--------|
| `syscall` | 可能绕开 libc 层 hook，需按 syscall number 和返回路径取证 |
| `prctl` | `PR_SET_PTRACER`、`PR_SET_DUMPABLE`、`PR_SET_SECCOMP` 等进程状态控制 |
| `kill` / `raise` / `tgkill` | 终止或信号自毁链 |
| `dl_iterate_phdr` / `dladdr` | 枚举加载模块与地址归属 |
| `inotify_init` | 监控 `/proc` 或文件变化 |
| `mmap` / `mprotect` | 运行时解密段、匿名 RX 与权限切换 |

静态推断只能给出候选链。direct syscall、匿名执行段和解密后的第二代码段未 dump/fix 前，不应把所有断连都归因于某一个 libc API。

## 二、动态绕过时间线

### 2.1 2026-07-02：终止路径拦截

环境：LDPlayer 9、Android 9、Root、Frida 17.15.3。

~~~text
Frida spawn
  -> 安装 kill/tgkill/raise/exit/_exit/abort/syscall hooks
  -> 安装 Process.killProcess/System.exit hooks
  -> 捕获 raise(SIGKILL)
  -> 终止调用被拦截，目标 PID 继续存活
  -> Frida transport 约 5 秒后断开
~~~

该结果证明 `raise(9)` 是一条真实终止链，但“PID 存活”与“Frida session 可持续使用”是两回事。

### 2.2 2026-07-05：`prctl` 链压制

进一步静默处理：

- `PR_SET_PTRACER`；
- `PR_SET_DUMPABLE`；
- `PR_SET_SECCOMP`。

处理后目标进程仍存活，Java 侧 `StubApp.load`、`FockUtil` 类加载和 `System.loadLibrary("fock")` 可以推进；但 Frida transport 仍在约 2 秒内断开。当前只应标记为“终止链部分绕过”，额外断连机制待从 direct syscall、fd/transport 操作、watchdog 和匿名执行代码中定位。

### 2.3 已否定的路线

| 路线 | 结果 | 原因 |
|------|------|------|
| 重打包 patch `kill_0` | 失败 | APK 签名变化触发 StubApp 校验，`interface20()` 出现 `UnsatisfiedLinkError` |
| `LD_PRELOAD` frida-gadget | 失败 | Android 9 进程创建与 `wrap.` 约束，环境没有按预期传入目标进程 |
| 仅拦截 `raise(9)` | 部分有效 | 进程存活，但第二条 transport/反注入链仍断开会话 |
| 在 x86_64 native bridge 中强行执行 ARM64 `libfock.so` JNI | 失败 | `System.loadLibrary` 成功不代表 JNI 注册可在翻译层正确完成 |

## 三、先判断是否真的需要脱 DEX

2026-07-05 对原始 APK 与设备安装版 `base.apk` 做逐文件比较：

- 12 个 DEX 全部为标准格式；
- 12 个 DEX 的 SHA-256 安装前后全部一致；
- jadx 已生成约 46,113 个文件。

对这个样本，Jiagu 保护重点在 SO 层反调试、反注入和运行时解密段，而不是把业务 DEX 从 APK 中移除。继续投入 DEX 脱壳不会自动解决 QDSign Native 调用或 Frida 断连问题。

这条判断应放在所有脱壳动作之前：

~~~text
APK 中业务 DEX 可读且方法体完整
  -> 直接 Java/Kotlin/smali 分析
  -> Native 检测链转 native-reverse

APK 只有 stub / 真实 DEX 运行时出现
  -> whole-DEX dump

DEX 结构在，但关键方法为空、nop 或 native stub
  -> 方法抽取 / CodeItem 恢复
~~~

## 四、新增 whole-DEX 能力：LDPlayer + panda

### 4.1 本地封装

`P4nda0s/panda-dex-dumper` 通过 Root 读取 `/proc/<pid>/mem`，对目标进程发送 `SIGSTOP`，扫描可读映射中的标准 `dex\n0xx\0` magic，按 header/map 推算大小并写出 DEX。上游 1.0.0 发布于 2023-02，源码没有 Frida 依赖，也没有明确 License。

项目封装：

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\reverse_ENV\skill\apk-reverse\scripts\dump-dex.ps1" -Project PROJECT -Package PACKAGE -DeviceSerial SERIAL -Launch
~~~

`dump-dex.ps1` 额外处理：

- 明确 ADB serial、Root、PID 与 `/proc/<pid>/cmdline` 归属；
- 检查 AArch64 dumper 与设备 ABI/native bridge；
- 为 panda 设置超时并保留 stdout/stderr；
- 校验 DEX magic、`header_size=0x70`、header file size、`class_defs` 与 SHA-256；
- 无论 panda 是否正常返回，都 best-effort 执行 `kill -CONT PID`；
- 失败或验证不干净时保留设备端证据。

### 4.2 状态语义

| `metadata.json` 状态 | 含义 |
|----------------------|------|
| `complete-enough` | 本轮拉取文件均通过本地结构校验，且 dumper/pull 正常结束；不是“完整脱壳”证明 |
| `partial` | 至少存在一个有效 DEX，但另有无效文件或工具阶段不完整 |
| `invalid` | 有输出，但没有 DEX 通过结构校验 |
| `no-dex` | 没有拉取到 DEX |

### 4.3 2026-07-14 实测

| 样本 | 输出 | 反编译观察 | 结论 |
|------|------|------------|------|
| 普通 App | 19 DEX / 21,134,420 bytes | 最大 DEX 生成 2,884 个 Java 文件 | whole-DEX 路线可用 |
| 起点读书 / Jiagu VIP | 13 DEX / 73,247,772 bytes | 最佳 DEX 生成 4,181 个 Java 文件，其中 4,073 个为 `com.qidian`；仍有大量 loading/decompile errors | 部分运行时恢复 |

起点原 APK 有 12 个 DEX，而运行时扫描得到 13 个 DEX 并不矛盾：进程可能额外加载壳、SDK、动态模块或内存 DEX。数量增加不能证明业务代码更完整，也不能证明原始 DEX 曾加密。

上述数字已进入主仓 commit `73e55f8` 的 skill、工具 README 和环境文档；原始 dump/`metadata.json` 未收录进 Public 知识库，因此这里将其标为项目级实测记录，不伪装成可独立复现的公开 fixture。

## 五、脱壳分流矩阵

| 目标形态 | 首选路线 | 主要限制 |
|----------|----------|----------|
| 运行时存在标准完整 DEX | `dump-dex.ps1` / panda | 只能恢复当时已加载的 whole DEX；多进程和 lazy loading 要逐 PID/时机验证 |
| 方法体被抽取、`CodeItem` 按需回填 | FART/主动调用 + FartFixer，或 JDex2 类方案 | 需触发方法回填；崩溃、类过滤、Android 版本和检测面复杂 |
| CDEX / CompactDex | 专门的 CDEX 识别、转换或 runtime 路线 | panda 只按标准 DEX magic/header 工作；直接保存 CDEX bytes 不等于可反编译 DEX |
| VMP | 解释器、opcode、trace 与 Native 分析 | DEX dump 只能得到壳层或 dispatcher |
| Dex2C | `native-reverse` / IDA | Java 方法已迁移到 SO，whole-DEX 只保留 native stub |
| 强 anti-Frida / anti-pause / direct syscall | 先做 syscall、匿名 RX、运行时 SO dump/fix | 继续叠加 Java/Frida hook 容易把工具故障当成业务结论 |

## 六、外部工具现状核验

检索时间：2026-07-15。Stars/Forks 是当日快照，只作成熟度辅助，不替代本地验证。

| 项目 | Stars / Forks | 活跃与 License | 可复用能力 | 本地结论 |
|------|---------------|----------------|------------|----------|
| [P4nda0s/panda-dex-dumper](https://github.com/P4nda0s/panda-dex-dumper) | 166 / 26 | 1.0.0，2023-02；License 未声明 | 无 Frida 的标准 DEX 内存扫描 | 已封装并实测；只作为 whole-DEX baseline |
| [TheQmaks/clsdumper](https://github.com/TheQmaks/clsdumper) | 51 / 8 | 0.2.0，2026-02；MIT | Frida 下 9 种策略、`DefineClass`、ART walk、OAT/VDEX、deep CDEX scan、反 Frida helper | 候选，尚未集成；目标本身强反 Frida 时风险较高 |
| [hanbinglengyue/FART](https://github.com/hanbinglengyue/FART) | 2,703 / 635 | 2025-01 最近 push；Apache-2.0 | 主动调用并 dump DEX + 方法 `CodeItem` | 方法抽取基线；原始实现基于 Android 6，移植需版本适配 |
| [J5now/JDex2](https://github.com/J5now/JDex2) | 149 / 35 | 1.6，2026-04；License 未声明 | LSPosed/Xposed 主动调用类级抽取 | 候选；README 明确不覆盖方法粒度抽取、执行后再抽取和即时字节码解密 |
| [CYRUS-STUDIO/FartFixer](https://github.com/CYRUS-STUDIO/FartFixer) | 29 / 5 | 2025-06；License 未声明 | 按 `method_idx + CodeItem` 修复 FART 结果 | 修复器候选，使用前需核对输入格式与授权 |

## 七、当前结论

| Claim | 状态 |
|-------|------|
| `raise(SIGKILL)` 是 Jiagu 终止链之一 | 已验证 |
| 拦截 `raise` 和部分 `prctl` 后进程可存活 | 已验证 |
| Frida 会话已经持久稳定 | 未完成 |
| 起点 7.9.464 的 12 个 APK DEX 被加密 | 已推翻 |
| LDPlayer x86_64 可通过 `libnb.so` 执行 AArch64 panda | 已验证 |
| panda 对该 Jiagu 样本实现完整脱壳 | 未证明，只能标记部分运行时恢复 |
| 方法抽取可由 whole-DEX 扫描自动修复 | 错误，需主动调用/CodeItem 路线 |

## 八、后续工作

1. 用 syscall 证据定位 Frida transport 断开前的 direct syscall、fd close、信号与线程归属。
2. dump/fix `LOAD[7]` 解密代码和匿名 RX/memfd，再分析第二检测链。
3. 将 panda 输出与原 APK 12 个 DEX 按 SHA-256、class_defs、业务包和关键方法逐一对齐，解释第 13 个 DEX 来源。
4. 若关键方法为空，再选择 FART/JDex2/FartFixer 路线；没有方法抽取证据时不引入重型主动调用环境。

## 关联资料

- [Qidian Native SO 分析与结论纠偏](../native-analysis/qidian-so-analysis.md)
- [Qidian 请求签名分析](../signature-algorithms/qidian-fock-signature.md)
- `D:\reverse_ENV\skill\apk-reverse\references\packing-and-unpacking.md`
- `D:\reverse_ENV\tools\panda-dex-dumper\README.md`
