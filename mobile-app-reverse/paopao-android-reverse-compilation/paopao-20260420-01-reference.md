---
schema_version: 2
id: unidbg-ioresolver-reference
document_type: reference
original_date: '2026-04-20'
archived_date: '2026-10-02'
scope:
  targets: [unidbg-ioresolver]
  client: unidbg
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./paopao-20260420-01.md#文件访问的两大用途分清动机
    basis: source-report
  - id: s2
    ref: ./paopao-20260420-01.md#resolve-方法的三种返回语义
    basis: source-report
  - id: s3
    ref: ./paopao-20260420-01.md#proc-伪文件系统深入最关键的一片战场
    basis: source-report
  - id: s4
    ref: ./paopao-20260420-01.md#pid-一致性问题一个隐蔽的坑
    basis: source-report
  - id: s5
    ref: ./paopao-20260420-01.md#验证闭环怎么知道自己补对了
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s2]
    basis: source-report
    limits: 注册点和三种 FileResult 来自来源对 IOResolver 的描述。未对照 unidbg 源码确认失败码或责任链顺序。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s2, s3, s4]
    basis: source-report
    limits: 动机分流、文件载体选择和 PID 匹配是来源规则。真机模板如何清洗没有逐步验收。
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2, s3]
    basis: source-report
    limits: 沉默失败和默认 maps 缺库是来源举的检测面。不收录路径清单，也不把示例返回标记写成通用魔数。
relations:
  - type: derived_from
    target: ./paopao-20260420-01.md#resolve-方法的三种返回语义
  - type: derived_from
    target: ./paopao-20260420-01.md#proc-伪文件系统深入最关键的一片战场
  - type: derived_from
    target: ./paopao-20260420-01.md#验证闭环怎么知道自己补对了
tags: [unidbg, ioresolver, source-report]
---

# Unidbg 文件访问用 IOResolver 的三种返回

这张卡回答文件通道怎么答复：信息收集和环境保护的返回不同，`resolve` 的 success、null、failed 不能混用，proc 文件还要跟着当前 PID 走。它不覆盖 JNI 包装，也不覆盖某一应用的签名算法。

<a id="interfaces"></a>
## 注册点与三种返回

文件钩子注册在 syscall handler 的 IOResolver 链上，先注册的先被问。`FileResult.success` 表示有内容，`null` 表示交给下一个，`FileResult.failed` 表示确定没有并且不要再读磁盘。体积大且固定的内容用 `SimpleFileIO`，小或要现造的用 `ByteArrayFileIO`。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C1 | 文件通道走 addIOResolver | emulator.getSyscallHandler().addIOResolver(resolver) | s2，第 198 行 | source-report | 注册点 | 与 JNI 的 setJni 对称，只在这一行 |
| C2 | 多个 resolver 按注册顺序问 | 先遍历  ** 所有注册的 IOResolver  ** | s2，第 201 行 | source-report | 责任链 | 原文写第一个有效回答获胜 |
| C3 | success 表示内容由这里给 | FileResult.success(fileIO) | s2，第 287 行 | source-report | 返回值 1 | 表里的语义是“有，内容是这个” |
| C4 | failed 表示确定不存在 | 这个路径  ** 确定不存在  ** ，不要再交给后续任何 resolver | s2，第 260 行 | source-report | 返回值 3 | 示例错误码未单独复核 |
| C5 | null 不能代替 failed | 为什么不能用 null 代替 FileResult.failed？ | s2，第 277 行 | source-report | 反检测路径 | 原因是 null 还会落到后续或真实磁盘 |
| C6 | 反检测路径必须 failed | 反检测路径必须用  ` failed  ` ，不能用  ` null  ` | s2，第 291 行 | source-report | 来源称为顶级原则 | 未在本地触发磁盘回落 |
| C7 | 大文件用 SimpleFileIO，小的用 ByteArrayFileIO | 内容 > 1KB 且固定 → SimpleFileIO (文件准备一次, 永久复用) | s2，第 331 行 | source-report | 载体选择 | 下一行才写小于 1KB 的分支 |

<a id="decision-flow"></a>
## 先分动机，再按运行时 PID 填 proc

信息收集要一个稳定且看起来合理的值。环境检测要一份干净状态：相关路径报不存在，maps 不含注入痕迹，status 里的 TracerPid 为 0。`/proc/self/status` 不能原样塞真机 pull 的结果，只能当模板，替换 Pid、Tgid、TracerPid。cmdline 末尾要有 NUL。路径要同时认 `/proc/self/` 和 `/proc/{当前 pid}/`，PID 用 `emulator.getPid()`，不能写死真机 PID。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C8 | 两种动机的返回不同 | 信息收集 = 伪造一个合理值；环境检测 = 伪造一份干净的设备状态 | s1，第 186 行 | source-report | 文件用途 | 合理范围没有数值边界 |
| C9 | Root 路径要报不存在 | Root 相关路径必须  ** 报不存在  ** | s1，第 180 行 | source-report | 环境检测 | 具体路径表不抄 |
| C10 | 小于 1KB 或动态内容用字节数组 | 内容 < 1KB 或需要动态生成 → ByteArrayFileIO (代码中直接构造) | s2，第 332 行 | source-report | 载体选择 | 与 C7 成对 |
| C11 | status 只能当模板 | 不能一字不改地 | s3，第 350 行 | source-report | /proc/self/status | 同句要求替换 Pid、Tgid、TracerPid |
| C12 | cmdline 末尾的 NUL 不能省 | 忘记末尾的  ` \0  ` | s3，第 373 行 | source-report | /proc/self/cmdline | 来源称 strlen 路径会不稳定 |
| C13 | 当前 PID 用 emulator.getPid | emulator.getPid() | s3，第 406 行 | source-report | status 模板补丁 | 同段还要求 TracerPid 写 0 |
| C14 | getpid 返回的是宿主 JVM 的 PID | 它返回  ** 宿主 JVM 的 PID  ** | s4，第 491 行 | source-report | PID 来源 | 未核对 UnixSyscallHandler 当前实现 |
| C15 | 运行时 PID 不能写死 | 用  ` emulator.getPid()  ` 拿到运行时 PID | s4，第 555 行 | source-report | 动态匹配 | 同段要求同时拦 self 和数字 PID |

<a id="risk-control"></a>
## 文件打不开往往没有异常

来源用 `/proc/self/maps` 打不开来说明：fopen 得到空之后，SO 可以安静走检测分支，结果偏离真机，过程没有异常。默认 maps 还可能缺基础库，这种缺失本身会被当成特征。端口文件被要求只留下正常端口或直接当不存在。这些是来源描述的风险，不是本次观察。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C16 | 默认找不到 maps 时 fopen 为空 | Unidbg 默认找不到  ` /proc/self/maps  ` ，  ` fopen  ` 返回 NULL | s1，第 96 行 | source-report | 沉默失败例子 | 后续分支是来源虚构的检测函数 |
| C17 | 这个空结果会进入后续计算 | 这个值进入后续签名算法，让最终结果偏离真机 | s1，第 98 行 | source-report | 同一例子 | 没有真实签名样本 |
| C18 | 没看到失败就会走错分支 | 你没注意到一个失败，SO 走了错分支，最终结果错了 | s1，第 130 行 | source-report | 三个原因的合取 | 未统计真实样本 |
| C19 | 默认 maps 不够干净 | 直接用 Unidbg 默认返回的 maps 往往不够干净 | s3，第 453 行 | source-report | /proc/self/maps | 后文说缺基础库本身是特征 |
| C20 | 必须看起来像真实设备 | 必须看起来  ** 像真实设备  ** | s3，第 434 行 | source-report | maps 伪造要点 | 库名和地址范围只在来源括号里 |
| C21 | 端口表只留正常端口或当不存在 | 只包含正常端口 | s3，第 470 行 | source-report | /proc/net/tcp 与 tcp6 | 默认端口数字不单列成规则 |
| C22 | failed 是为了不读真实磁盘 | 用 failed 而不是 null, 防止 Unidbg 默认去查真实磁盘 | s2，第 596 行 | source-report | 模板注释 | 位于最小模板，不是新规则 |
| C23 | 路径列表被要求完全一致 | 两者必须完全一致 | s5，第 693 行 | source-report | 作者的检验句 | 不一致时只解释了两种可能，没有停止出口 |

## 验证与限制

验收句要求 Frida 的 open、fopen、access 路径和 Unidbg 日志一致，但没有“缺真机路径列表就停止”的前提，也没有失败出口，所以不建流程。Unidbg 版本未知。反检测路径表和示例返回标记不抄入本卡。文末“修改于”没有日期，不提供技术内容。
