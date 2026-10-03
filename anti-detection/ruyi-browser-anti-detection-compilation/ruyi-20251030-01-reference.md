---
schema_version: 2
id: ruyi-chromium-fingerprint-ipc-reference
document_type: reference
original_date: '2025-10-30'
archived_date: '2026-10-02'
scope:
  targets: [chromium-fingerprint-ipc]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20251030-01.md#chromium内核教程--指纹浏览器的多进程指纹传递问题
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只保留来源点名的进程、类和符号。Mojo 绑定、共享内存句柄传递和 socket 地址在归档里不完整。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录开关名、环境变量名、共享内存长度和页面属性名。不复制来源里的示例种子或 JSON 样值。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 沙盒限制是作者对 Chromium 沙盒的陈述，归档没有 SandboxPolicy 片段。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 六条通道是并列草图，不是已验收的选择流程。命令行读写使用了两个不同的开关名。
relations:
  - type: derived_from
    target: ./ruyi-20251030-01.md#chromium内核教程--指纹浏览器的多进程指纹传递问题
tags: [chromium, ipc, sandbox, source-report]
---

# Chromium 指纹跨进程传递通道参考

这张卡检索来源列出的 Browser 到 Renderer 指纹通道：命令行、Mojo、环境变量、共享内存、本地 socket、V8 属性。它不提供可粘贴的注入实现，也不复制示例种子。

<a id="risk-control"></a>
## 沙盒边界

来源把 Browser、Renderer、GPU、Utility、Network Service 写成各自隔离的进程，并要求数据穿越沙盒。作者写渲染进程和 GPU 进程不能直接读环境变量或共享内存。指纹在 Browser 生成、在 Renderer 使用，因此同步问题被说成穿越沙盒。

环境变量一节进一步写：沙盒会阻止渲染进程读系统环境变量，必须关闭沙盒或在 `SandboxPolicy` 里放行。归档没有给出策略代码。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 跨进程数据必须穿越沙盒边界 | s1 `ruyi-20251030-01.md:54`，quote: `必须穿越沙盒系统的边界` | source-report | chromium-fingerprint-ipc | 作者概括 |
| C2 | 来源称渲染侧不能直接读环境变量或共享内存 | s1 `ruyi-20251030-01.md:67`，quote: `不能直接读取环境变量或共享内存` | source-report | chromium-fingerprint-ipc | 无策略片段 |
| C3 | 环境变量通道被写成需要关闭沙盒或改 SandboxPolicy | s1 `ruyi-20251030-01.md:149`，quote: `SandboxPolicy` | source-report | 仅环境变量方案 | 无放行代码 |

<a id="parameters"></a>
## 名字与长度

命令行写入使用 `fingerprint-seed-ruyi`，渲染进程读取使用 `fingerprint-seed`。两个字符串在归档里并不相同，不能当成已经对齐的合同。

环境变量名是 `CHROMIUM_FP`。共享内存创建长度是 `Create(1024)`。渲染层属性名是 `window.__fingerprint__`，V8 侧用同一属性名。来源里的种子和 JSON 样值不进入本卡。

作者把命令行方案说成启动后指纹一般不变，一个账号一个指纹，所以“难以动态变化”仍够用。这是适用条件，不是测量结果。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 写入开关名是 fingerprint-seed-ruyi | s1 `ruyi-20251030-01.md:85`，quote: `fingerprint-seed-ruyi` | source-report | 命令行写入片段 | 不记录样值 |
| C5 | 读取开关名是 fingerprint-seed | s1 `ruyi-20251030-01.md:93`，quote: `GetSwitchValueASCII("fingerprint-seed")` | source-report | 命令行读取片段 | 与写入名不一致 |
| C6 | 环境变量名是 CHROMIUM_FP | s1 `ruyi-20251030-01.md:140`，quote: `CHROMIUM_FP` | source-report | 环境变量片段 | 不记录样值 |
| C7 | 共享内存长度参数是 1024 | s1 `ruyi-20251030-01.md:164`，quote: `UnsafeSharedMemoryRegion::Create(1024)` | source-report | 共享内存片段 | 未写溢出处理 |
| C8 | 页面属性名是 window.__fingerprint__ | s1 `ruyi-20251030-01.md:203`，quote: `window.__fingerprint__` | source-report | V8 注入片段 | 无注入时机证明 |
| C9 | 作者把命令行方案限制为指纹不动态变化 | s1 `ruyi-20251030-01.md:57`，quote: `指纹难以动态变化` | source-report | 命令行方案 | 作者陈述 |

<a id="interfaces"></a>
## 通道符号

命令行节点名 `ChildProcessHostImpl`，并用 `base::CommandLine` 追加开关。作者称这条路不修改 IPC，也不受沙盒约束。

Mojo 节定义 `fingerprint.mojom` 与 `FingerprintService`，Browser 侧类名是 `FingerprintServiceImpl`，Renderer 侧调用 `GetRemoteFingerprintService`。来源称数据走 IPC，不依赖外部文件或环境变量。绑定函数和接口注册没有给出。

共享内存节写出 `UnsafeSharedMemoryRegion`、`PassPlatformHandle()`，以及 Renderer 侧 `ReadOnlySharedMemoryRegion::Deserialize`。socket 节只有 `AF_UNIX` 的 `socket` 草图和 `Named Pipe` 这个名字，`bind` / `connect` 用省略号。V8 节是 `gin::ConvertToV8`，作者称发生在 V8Context 初始化。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C10 | 命令行节点名 ChildProcessHostImpl | s1 `ruyi-20251030-01.md:79`，quote: `ChildProcessHostImpl` | source-report | 命令行方案 | 无调用点 |
| C11 | 作者称命令行不改 IPC 且不受沙盒约束 | s1 `ruyi-20251030-01.md:96`，quote: `不需要修改 IPC，也不受沙盒约束` | source-report | 命令行方案 | 作者陈述 |
| C12 | Mojo 文件名 fingerprint.mojom | s1 `ruyi-20251030-01.md:108`，quote: `fingerprint.mojom` | source-report | Mojo 方案 | 无 BUILD 接线 |
| C13 | 实现类名 FingerprintServiceImpl | s1 `ruyi-20251030-01.md:117`，quote: `FingerprintServiceImpl` | source-report | Mojo 方案 | 不记录 JSON 样值 |
| C14 | 渲染侧获取函数名 GetRemoteFingerprintService | s1 `ruyi-20251030-01.md:125`，quote: `GetRemoteFingerprintService` | source-report | Mojo 方案 | 无绑定实现 |
| C15 | 来源称 Mojo 不依赖外部文件或环境变量 | s1 `ruyi-20251030-01.md:129`，quote: `不依赖外部文件或环境变量` | source-report | Mojo 方案 | 作者陈述 |
| C16 | 句柄移交符号 PassPlatformHandle | s1 `ruyi-20251030-01.md:167`，quote: `PassPlatformHandle()` | source-report | 共享内存方案 | 接收端接线不完整 |
| C17 | 读取侧符号 ReadOnlySharedMemoryRegion::Deserialize | s1 `ruyi-20251030-01.md:174`，quote: `ReadOnlySharedMemoryRegion::Deserialize` | source-report | 共享内存方案 | 句柄类型未闭合 |
| C18 | socket 草图使用 AF_UNIX | s1 `ruyi-20251030-01.md:190`，quote: `AF_UNIX` | source-report | socket 方案 | bind 参数是省略号 |
| C19 | 作者同时点名 Named Pipe | s1 `ruyi-20251030-01.md:184`，quote: `Named Pipe` | source-report | socket 方案 | 没有管道路径 |
| C20 | V8 写入使用 gin::ConvertToV8 | s1 `ruyi-20251030-01.md:210`，quote: `gin::ConvertToV8` | source-report | V8 方案 | 无调用栈 |
| C21 | 作者把注入时机写成 V8Context 初始化 | s1 `ruyi-20251030-01.md:213`，quote: `V8Context` | source-report | V8 方案 | 作者陈述 |

<a id="decision-flow"></a>
## 方案并列

来源把命令行写成自己教过的、基于参数传递的注入机制，并说它最简单稳定。其余五条是并列的 IPC 草图，不是同一条必经路径。没有统一的成功判据，也没有某一条失败后改走另一条的出口。读写开关名不一致，因此不能把命令行方案收成流程。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C22 | 命令行被写成基于参数传递的注入机制 | s1 `ruyi-20251030-01.md:56`，quote: `基于参数传递的指纹注入机制` | source-report | 命令行方案 | 与后五条并列 |

## 验证与限制

`browser-fingerprint` 只覆盖 Web 宿主对象的检测面。`chromium-startup-cookie` 与 `chromium-startup-validation` 是启动 Cookie 和 JWT，不是这六条指纹通道。本卡不并入它们。

进程名 Browser、Renderer、GPU、Utility、Network Service 都在来源列表里。示例种子、UA 字面量和 JSON 样值故意不收录。没有版本、没有可运行接线，也不能写成流程。
