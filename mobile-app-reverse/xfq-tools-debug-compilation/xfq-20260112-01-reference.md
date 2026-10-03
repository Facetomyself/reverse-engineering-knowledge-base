---
schema_version: 2
id: xfq-binary-ninja-mcp-installer
document_type: reference
original_date: "2026-01-12"
archived_date: "2026-10-02"
scope:
  targets: [binary-ninja-mcp]
  client: desktop
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260112-01.md#正文"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只记录来源写下的软件内入口和 mcp_client_installer.py。图 1 不在归档里，clone 行是 Markdown，未执行。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录手写 python 路径、py 路径、mcps_config.json 和 tools 超过 100 的说法。不重复 Reqable 卡里的 command、args、profiles。
relations:
  - type: derived_from
    target: "./xfq-20260112-01.md#正文"
  - type: derived_from
    target: "./xfq-20260112-01.md#复用边界"
tags: [binary-ninja, mcp, gateway]
---

# Binary Ninja MCP 的安装入口

这张卡只回答一个检索问题：这篇归档里的 Binary Ninja MCP 从哪条脚本进客户端，以及作者把配置收进哪一个 Gateway 文件。它不是安装流程。Reqable 的 gateway 字段在另一张卡。

<a id="interfaces"></a>
## 安装入口

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 软件内部安装被写成照着图 1。quote: 照着图1的步骤在软件内部安装mcp | s1 ./xfq-20260112-01.md:36 | source-report | 来源的第一步 | 归档没有这张图 |
| C2 | 仓库名被写成 fosdickio/binary_ninja_mcp，所在行是 Markdown 链接。quote: fosdickio/binary_ninja_mcp | s1 ./xfq-20260112-01.md:38 | source-report | 来源给出的仓库 | 不是已执行的 shell 行 |
| C3 | 进入目录后的安装命令被写成 python scripts/mcp_client_installer.py --config。quote: python scripts/mcp_client_installer.py --config | s1 ./xfq-20260112-01.md:40 | source-report | 来源写下的脚本入口 | 没有参数说明或输出 |

<a id="parameters"></a>
## 路径和 Gateway 文件

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 作者认为 installer 生成的 json 用处不大，改为自己写 python 路径和 py 路径。quote: 可以自己写 python路径和 py路径 | s1 ./xfq-20260112-01.md:41 | source-report | 来源对生成文件的态度 | 没有字段名或示例路径 |
| C5 | Gateway 侧被写成只编辑 mcps_config.json，再在 kiro 里 reconnect。quote: mcps_config.json即可，然后kiro里面reconnect | s1 ./xfq-20260112-01.md:42 | source-report | 来源自己的聚合方式 | 没有 JSON 正文 |
| C6 | 这样做被写成用来解决 tools 超过 100 个，或工具过多让模型变差。quote: tools超过100个的限制 | s1 ./xfq-20260112-01.md:42 | source-report | 来源给出的动机 | 没有实际工具计数 |

## 验证与限制

`kb_catalog.py query` 对 binary-ninja-mcp 的 interfaces、parameters 都是 0。reqable 的 interfaces 与 parameters 只覆盖 Reqable，不覆盖本安装脚本。来源写明缺少图示、软件版本和独立验收记录，不应升格为通用安装流程。本次没有执行 clone、installer 或 reconnect。
