---
schema_version: 2
id: ruyi-webkit-webdriver-startup
document_type: reference
original_date: '2025-04-22'
archived_date: '2026-10-02'
scope:
  targets: [webkit-webdriver]
  client: webkit
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ruyi-20250422-01.md#01浏览器自动化webdriver源码分析之启动函数"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录粘贴片段里连续出现的环境变量和参数名。粘贴把源码收成带 NBSP 的单行，不重建被拆开的空格。作者关于“必须先打开浏览器”的句子不是这段解析代码本身。
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只记录启动调用、监听顺序和粘贴中的 Win32 消息循环。platformInit 的函数体、浏览器进程如何被拉起、以及 GetMessage 之后的命令处理都不在正文。
relations:
  - type: derived_from
    target: "./ruyi-20250422-01.md#01浏览器自动化webdriver源码分析之启动函数"
tags: [webkit, webdriver, startup, static-review]
---

# WebKit WebDriver 进程的启动参数与监听入口

这篇参考只回答：2025-04-22 这篇源码摘录里，WebKit WebDriver 进程从哪个入口启动、接受哪些地址和端口参数、监听失败时如何退出，以及消息循环在粘贴中长什么样。它不是 ChromeDriver 或 Selenium 的 `cdc_` 检测说明，也不提供会话命令的处理函数。

<a id="parameters"></a>
## 参数

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| P1 | getenv("WEBDRIVER_TARGET_ADDR") | s1 第 69 行 | source-report | 粘贴中的环境变量读取 | 没写变量缺失时的默认值 |
| P2 | --port= | s1 第 78 行 | source-report | 命令行端口 | 与 `-p` 分支同在这一行；这里只引用连续出现的长选项 |
| P3 | --host= | s1 第 78 行 | source-report | 监听主机 | 未引用带空格的默认主机串 |
| P4 | --target= | s1 第 78 行 | source-report | 目标浏览器地址 | 与环境变量写入同一个 targetString 角色，粘贴后半有 reverseFind |
| P5 | --bidi-port= | s1 第 78 行 | source-report | 位于 WEBDRIVER_BIDI 条件编译里的 BiDi 端口 | 未启用该宏时这段不存在 |
| P6 | --replace-on-new-session | s1 第 78 行 | source-report | 新会话替换开关 | 只看到赋给 m_replaceOnNewSession |
| P7 | m_replaceOnNewSession | s1 第 78 行 | source-report | 同上 | 没有后续读取点 |
| P8 | portString.isNull() | s1 第 78 行 | source-report | 端口缺失分支 | 同一行在该分支调用 printUsageStatement 并返回 EXIT_FAILURE |
| P9 | Invalid port | s1 第 78 行 | source-report | 端口解析失败时的 stderr 文本 | 不记录格式串里的其他占位 |
| P10 | bidiPortIncrement | s1 第 78 行 | source-report | BiDi 端口无效时的相邻端口回退 | 只在 WEBDRIVER_BIDI 片段中出现 |
| P11 | EXIT_FAILURE | s1 第 78 行 | source-report | 参数失败出口 | 第 85 行的监听失败同样返回它 |

<a id="interfaces"></a>
## 接口

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| I1 | WebKit::WebDriverProcessMain | s1 第 54 行 | source-report | 粘贴中的 Android 入口名 | 同一行还有非 Android 分支，不把空格已被 NBSP 替换的签名重拼出来 |
| I2 | OS(ANDROID) | s1 第 54 行 | source-report | 入口的平台条件 | 没有对应的 Android 监听实现 |
| I3 | platformInit(); | s1 第 54 行 | source-report | main 路径上的第一次调用 | 函数体不在粘贴中 |
| I4 | initializeMainThread | s1 第 54 行 | source-report | 启动时的 WTF 主线程初始化 | 第 85 行在进入监听前又调用一次 |
| I5 | service.run(argc, | s1 第 54 行 | source-report | 创建 WebDriverService 后的进入点 | 只引用逗号前的连续片段 |
| I6 | WEBDRIVER_BIDI | s1 第 85 行 | source-report | BiDi 监听的编译开关 | 第 78 行的参数解析也使用该宏 |
| I7 | m_bidiServer.listen | s1 第 85 行 | source-report | 先监听 WebSocket BiDi | 失败时打印 FATAL 并 EXIT_FAILURE |
| I8 | m_server.listen | s1 第 85 行 | source-report | 随后监听 HTTP | 失败文本是 FATAL: Unable to listen for HTTP server |
| I9 | FATAL: Unable to listen for HTTP server | s1 第 85 行 | source-report | HTTP 监听失败出口 | 不表示已经完成过一次成功监听 |
| I10 | RunLoop::run | s1 第 85 行 | source-report | 两次 listen 都返回后进入循环 | 循环体在第 108 行的另一段粘贴 |
| I11 | singleton() | s1 第 92 行 | source-report | HTTPServer::listen 取 RemoteInspectorSocketEndpoint 单例 | 作者称这是为了复用同一监听端点 |
| I12 | RemoteInspectorSocketEndpoint::listenInet | s1 第 101 行 | source-report | 单例上的 TCP 监听函数 | 不成功时返回空，不在这里展开锁和 ID |
| I13 | ::GetMessage | s1 第 108 行 | source-report | 粘贴的 RunLoop::run | 同一行还有 TranslateMessage 与 DispatchMessage |
| I14 | ::TranslateMessage | s1 第 108 行 | source-report | 同上 | 这是 Win32 消息循环片段 |
| I15 | ::DispatchMessage | s1 第 108 行 | source-report | 同上 | 看不到窗口过程里如何分发 WebDriver 命令 |

## 验证与限制

作者写 `platformInit源码里空白无实现`，但粘贴只有调用。作者写 `需要先把浏览器打开，然后webdriver回去链接，而不是先运行webdriver`，片段只证明会读取 `WEBDRIVER_TARGET_ADDR` 和 `--target=`。作者写 BiDi 双向、HTTP 单向，以及 `纯粹的win32的函数接口`；双向/单向是作者的归纳，Win32 API 只出现在 `RunLoop::run` 这段，而入口同时有 `OS(ANDROID)`。最后一句 `就要控制浏览器自动化了` 没有处理函数。因此本文没有步骤、验收和失败出口五段，不能当作操作流程。

同目录的 Chromedriver/Selenium 归档讲的是浏览器里的自动化特征，不是这个 WebKit 进程入口。`chromium-startup-validation` 与 `chromium-startup-cookie` 也不是 WebDriver 监听面。
