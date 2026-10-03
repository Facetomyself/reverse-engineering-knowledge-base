---
schema_version: 2
id: unidbg-kiro-run-test-wiring
document_type: reference
original_date: '2025-12-05'
archived_date: '2026-10-02'
scope:
  targets:
    - unidbg
    - com.trueapp.oasis.LvZhou
  client: kiro
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./xfq-20251205-01.md#ai-自动化调试unidbg
    basis: source-report
modules:
  - name: interfaces
    anchor: entry
    sources: [s1]
    basis: source-report
    limits: 只保留正文里的 run-test.cmd 与类名。cmd 文件、Java 路径和 .mp3 附件都不在本篇。
  - name: decision-flow
    anchor: wiring
    sources: [s1]
    basis: source-report
    limits: 优点是作者自述。hook 模板没有贴出。没有验收步骤，也没有失败出口。
relations:
  - type: derived_from
    target: ./xfq-20251205-01.md#ai-自动化调试unidbg
tags:
  - unidbg
  - kiro
  - source-report
---

# kiro 跑 unidbg 时，执行入口和改代码分开

这张卡只回答：作者要把 unidbg 交给 IDE 里的模型时，终端命令、权限和改代码各放在哪。它不包含 hook 模板，也不证明自动补环境是对的。来源是 [ai 自动化调试unidbg](./xfq-20251205-01.md#ai-自动化调试unidbg)。

<a id="entry"></a>
## 终端入口

作者认为要先让 vscode 一类 IDE 跑起来，前提是自己的终端已经能跑。贴出的命令会自动编译并执行类。类名写的是 `com.trueapp.oasis.LvZhou`，命令是 `run-test.cmd com.trueapp.oasis.LvZhou`。旁边注明 `.mp3` 后缀要去掉，Java 路径可能要改。这两样的具体文件都不在正文里。

<a id="wiring"></a>
## 交给模型什么，不交给什么

顺序只有三步：终端能跑，给模型执行命令的权限，再告诉它用第 1 步那条命令。作者用的是 kiro，并且只写了给它 `run-test.cmd` 权限。

作者把优点写成：自动补大多数环境、能沿用以前补过的 app、教过之后会 hook、hook 时自动断点并读寄存器。hook 所依的「我自己改的模板」没有附在本篇。可核对的操作建议只有一句：把输出定向到日志，避免漏掉控制台内容。`console debugger` 被说成仍然可用，没有列出哪些命令。

缺点也只有一条：跑起来不等于能改代码。代码提示不够，作者仍然回 IDEA；vscode 一类 IDE 可以自己配提示，但作者没配。历史折叠块是正文的压扁复述，命令以正文的 `run-test.cmd` 为准。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 入口命令是 `run-test.cmd com.trueapp.oasis.LvZhou`。正文写 `运行就会自动编译和执行我们的类`。 | s1 第 39–39 行 | source-report | 作者这次贴出的 cmd | Java 路径和去掉后缀的文件不在正文 |
| C2 | 模型侧用 kiro，只给 `run-test.cmd` 的执行权限，并告诉它用第 1 步的命令。 | s1 第 42–42 行 | source-report | kiro 这种能跑终端命令的 IDE | 没有权限配置截图 |
| C3 | hook 观察时 `最好是把输出定向到日志中`，避免漏控制台。 | s1 第 48 行 | source-report | 作者描述的自动断点流程 | 日志路径没有给出 |
| C4 | `console debugger一样是可以用的`，但改代码仍回 IDEA，因为 `代码提示不够好`。 | s1 第 49、52 行 | source-report | 作者自己的 IDE 分工 | 没有列调试命令，也没有验收 |
