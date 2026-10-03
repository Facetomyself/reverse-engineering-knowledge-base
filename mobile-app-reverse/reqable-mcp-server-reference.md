---
schema_version: 2
id: mobile-app-reverse-reqable-mcp-server-reference
document_type: reference
scope:
  targets: [reqable]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./xfq-tools-debug-compilation/xfq-20260712-01.md#reqable-mcp-extraction
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 仅整理来源报告中的本地 MCP server 接入面；Reqable 版本、OS发行包与当前可用性未核验。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: command/args/profiles 是示例配置形状；安装路径需按本机配置，本文不把样例路径视为默认值。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: status/search/capture 工具调用只是来源报告中的检查项；没有 expected outputs、失败出口或本轮调用结果。
relations:
  - type: derived_from
    target: ./xfq-tools-debug-compilation/xfq-20260712-01.md#reqable-mcp-extraction
tags: [Reqable, MCP, local-server, gateway]
---

# Reqable MCP Server 接入参考

本文将一篇 Reqable MCP 配置归档整理为本地 stdio server 注册面的窄参考。内容仅为 `source-report`，不是 Reqable 当前版本的接入保证。

<a id="interfaces"></a>
## Server 接口面

来源描述 Reqable 随安装提供 MCP server，可直接注册到客户端，或由 Gateway MCP 作为下游 server 配置。server 可执行文件位置依赖安装环境；本文不固化来源中的本机路径。

来源还描述 GUI 中可通过工具配置页选择 AI 客户端，但没有提供 GUI 版本、保存位置或配置导出证据。

<a id="parameters"></a>
## 配置参数面

来源展示的 Gateway 配置字段包括 `command`、`args`、`profiles` 与 `disabled`。具体字段如何被当前 Gateway 版本解析、profile 是否影响工具可见性，均未在来源中以输出验证。

配置示例的路径应视为安装位置占位，不是跨平台固定值。命令行注册和 JSON 配置形状仅按来源文本记录，不声称在当前环境已运行。

<a id="validation"></a>
## 来源报告的检查项

来源建议配置后重新连接客户端，再检查 server status、搜索工具并调用 live-capture 状态/过滤工具。它没有附带这些调用的实际输出、期望 schema、成功判定或失败恢复步骤，因此不构成 procedure。

来源另称 Gateway 必须透传 MCP `structuredContent` 才能读取结构化响应；该陈述未由本轮运行验证。来源中对工具数量和 Gateway 修复状态的描述均未绑定可复核版本。

## 证据与限制

- 来源：同名 archive 的 `s1`，`source-report`。
- 未记录 Reqable/Gateway/客户端版本、目标 OS、预期 JSON schema 或失败出口。
- 本文不含凭据、Cookie、token 或私有路径；不说明如何访问任何远程业务目标。
- 未进行安装、MCP server 启动、工具调用、网络请求或服务端验收。
