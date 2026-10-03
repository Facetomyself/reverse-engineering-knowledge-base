---
schema_version: 2
id: xfqtrace-gadget-trace-loader
document_type: procedure
original_date: unknown
archived_date: '2026-09-04'
scope:
  targets: [xfqtrace-gadget-trace]
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-undated-02.md#gadget_trace"
    basis: source-report
modules:
  - name: parameters
    anchor: prerequisites
    sources: [s1]
    basis: source-report
    limits: 包名、so 名和偏移只属于这份示例。注释里的设备序列号不进入本卡。
  - name: interfaces
    anchor: exports
    sources: [s1]
    basis: source-report
    limits: 符号名和返回值按脚本来源摘录。本轮没有解析 so。
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 加载顺序和 Java 触发都是脚本里的分支。本轮没有连接进程。
  - name: validation
    anchor: acceptance
    sources: [s1]
    basis: source-report
    limits: 通过只等于脚本来源写下的两个返回值都是 0。没有 trace 文件可核对。
relations:
  - type: derived_from
    target: "./xfq-undated-02.md#gadget_trace"
tags: [xfqtrace, frida, gadget]
---

# xfqtrace Gadget 脚本的武装顺序

这张流程只覆盖 `gadget_trace` 这份示例脚本自己的契约：so 放到哪、缺哪些导出就停、目标模块怎么认、引擎按什么顺序打开、configure 和 start 怎样算过。它不选择注入 Gadget 的方法。另一篇只点到脚本路径和推送命令的笔记不包含这些返回值分支。设备序列号不抄。

<a id="prerequisites"></a>
## 前提与输入

来源注释要求先把 `libxfqtrace.so` 推到临时目录，再复制到 `com.xiaofeng.qbdi` 的库路径并 `chmod 755`，然后把 tcp 14725 转到本机，最后用 frida 连到名为 Gadget 的进程并加载该脚本。缺部署结果就停在 F1 之前的材料检查，不进入脚本。

脚本内的目标是 `libxftest.so` 加示例偏移，输出格式字段是 `traceui`，`max_traces` 为 1。这些值只属于这份示例。进程里还要能找到 `dlopen`、`android_dlopen_ext` 和 `dlsym`。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | so 先推到临时目录 | push bin/libxfqtrace.so /data/local/tmp/libxfqtrace.so | s1 :43 | source-report | 同行的设备序列号不入卡 |
| C2 | 包内副本要可执行 | chmod 755 /data/data/com.xiaofeng.qbdi/libxfqtrace.so | s1 :44 | source-report | 不抄序列号 |
| C3 | 转发脚本使用的端口 | forward tcp:14725 tcp:14725 | s1 :45 | source-report | 不抄序列号 |
| C4 | 连接到名为 Gadget 的进程 | frida -H 127.0.0.1:14725 -n Gadget -l examples/com.xiaofeng.qbdi/gadget_trace.js | s1 :46 | source-report | 只是注释中的命令 |
| C5 | 示例 so 名 | so_name: 'libxftest.so' | s1 :53 | source-report | 同段偏移只属于示例 |
| C6 | 输出格式字段 | out_format: 'traceui' | s1 :58 | source-report | 没有样例文件 |

<a id="exports"></a>
## 引擎符号

引擎加载成功后，脚本按名称取出 `xfqtrace_configure`、`xfqtrace_start`、`xfqtrace_stop`、`xfqtrace_get_last_error` 和 `xfqtrace_set_done_callback`。configure 收一条 JSON 指针并返回 int；start 无参并返回 int。任何一个取不到就抛出 dlsym 失败，走 F3 之后的符号失败，不继续武装。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C7 | 三个加载器导出缺一即停 | throw new Error('dlopen/android_dlopen_ext/dlsym not found'); | s1 :120 | source-report | dlerror 可以没有 |
| C8 | configure 是引擎导出 | xfqtrace_configure | s1 :372-376 | source-report | 同段还有 start、stop、错误和回调 |

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 确认 so 已按注释放到候选路径，端口和 Gadget 进程可用 | 部署记录 | 缺材料停止；齐了才加载脚本 |
| S2 | 脚本启动时解析 dlopen、android_dlopen_ext、dlsym | 三个地址都非空 | 缺一走 F1 |
| S3 | 已加载则直接武装；否则挂住两个 dlopen，等路径里出现目标 so 名且返回值非空 | 模块基址和路径 | 找不到走 F2 |
| S4 | 候选路径先普通 dlopen；只有目标基址非空时，才用带调用方地址的 loader 打开，再试另一种 loader 打开 | 引擎句柄 | 全部失败走 F3；句柄已有则跳过 |
| S5 | 把 target 加上 base 字符串，连同 options 交给 configure，再 start | 两个 int 返回值 | 任一非 0 走 F4；都是 0 则记 trace armed |
| S6 | 若示例开关开着，延迟后调用 MainActivity.triggerAllTests | 日志里的返回值或异常 | 异常只记日志，不撤销已经 armed 的 trace |

找模块时先读 `/proc/self/maps`，路径必须以 so 名结尾，否则再枚举已加载模块。路径后缀不符就忽略，不武装。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C9 | 先普通打开 | if (tryPlainDlopen(p)) return true; | s1 :235 | source-report | 成功就不再往下试 |
| C10 | 其后才是带调用方的打开 | tryLoaderAndroidDlopenExt | s1 :240-241 | source-report | 下一行才是另一种 loader |
| C11 | maps 是第一条查找 | /proc/self/maps | s1 :273 | source-report | 读不到再枚举模块 |
| C16 | 示例会去调 Java 入口 | MainActivity.triggerAllTests(arg) | s1 :341 | source-report | 失败不回滚 |

<a id="outputs"></a>
## 输出

来源把选项里的输出格式写成 `traceui`，并打开 lz4。脚本侧能直接看到的完成信号是回调里的 `trace_done`，以及武装成功日志。本卡不把日志句当成 trace 文件已经生成。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C15 | 完成消息的类型 | send({ type: 'trace_done' }); | s1 :380 | source-report | 引擎何时调用回调没有写 |

<a id="acceptance"></a>
## 验收

同时满足才算脚本自己定义的武装完成：目标路径后缀匹配 so 名；configure 返回 0；start 返回 0；随后出现 trace armed 日志。只看到 Java 触发日志不算。没有 trace 内容可对时，不把武装日志升级成结果已经正确。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C12 | 路径后缀必须匹配 | !pathEndsWithName(targetPath, CONFIG.target.so_name) | s1 :362 | source-report | 空路径不会被这句拒绝 |
| C13 | 非 0 即失败 | if (rc !== 0) { | s1 :389 | source-report | start 之后用了同一判断 |
| C14 | 成功日志 | trace armed! | s1 :407 | source-report | 是日志，不是结果文件 |

<a id="failure-exits"></a>
## 失败出口

F1：dlopen、android_dlopen_ext 或 dlsym 缺失。脚本直接抛错，不武装。

F2：目标模块还没出现，或路径后缀不是配置里的 so 名。保持等待或返回，不调用 configure。

F3：候选路径的普通打开和两种 loader 打开都没有句柄。日志写加载失败，不取引擎符号。

F4：configure 或 start 返回非 0。读取最后错误文本；start 失败时来源还会调用 stop，并清掉完成回调。不进入 Java 触发。

Java 触发失败只记日志。它发生在已经 armed 之后，不能当成 F4，也不能当成验收通过。
