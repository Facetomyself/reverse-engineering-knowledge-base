---
schema_version: 2
id: ida-jadx-mcp-server-wiring-reference
document_type: reference
original_date: '2025-12-04'
archived_date: '2026-09-04'
scope:
  targets:
    - ida-pro-mcp
    - jadx-mcp
  client: local-ide
  version: "IDA Pro 9.1 as named; 9.2 path also named"
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20251204-01.md#12-ida-mcp"
    basis: source-report
  - id: s2
    ref: "./xfq-20251204-01.md#13-jadx-mcp"
    basis: source-report
  - id: s3
    ref: "./xfq-20251204-01.md#11-调整好的mcp配置文件"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2, s3]
    basis: source-report
    limits: 只保留安装入口、配置键和作者写成连上的现象。本机绝对路径、续杯与账号轮换不进入本卡。粘贴的 JSON 混有行号，不能加载。未在本机启动。
relations:
  - type: derived_from
    target: "./xfq-20251204-01.md#12-ida-mcp"
tags:
  - ida-pro-mcp
  - jadx-mcp
  - source-report
---

# IDA 与 JADX 的 MCP 接线入口

这张卡只回答：来源怎样把 IDE 接到 ida-pro-mcp 和 jadx-mcp-server，以及它把什么现象写成已经连上。不提供可加载的配置文件，也不涉及编辑器续杯或账号轮换。

来源没有可公开定位的原文 URL。成功与否只到作者自述。

<a id="interfaces"></a>
## 接线入口

IDA 侧的安装对象是 mrexodia/ida-pro-mcp。配置由命令生成，而不是手写一份新协议。

> pip install --upgrade git+https://github.com/mrexodia/ida-pro-mcp

> ida-pro-mcp --config

手动安装时，来源要求先切到 IDA 自己的 Python，再用那个 `python.exe` 安装。它点名 `idapyswitch.exe`，并写明不用这套环境就认为 pip 不可用。

> ./python.exe -m pip install --upgrade git+https://github.com/mrexodia/ida-pro-mcp # 一定要这样装,否则pip用不了

样本里的配置键是 `command`、`args`、`timeout`、`disabled`。`command` 指向本机 `python.exe`，`args` 指向 `ida_pro_mcp` 生成的 `server.py`，或已安装的 `jadx_mcp_server.py`。超时样本是：

> "timeout": 1800,

这些句子里的本机绝对路径不转写。围栏把行号和 JSON 粘在一起，不能当配置文件保存。

作者把 IDA 里 Plugins 的 MCP 启动后、输出栏出现 server 和端口，写成 IDA 侧启动成功。

> 输出栏(output)会弹出提示说mcp的server启动,有一个

> 端口,这就代表启动成功;

JADX 侧来源要求安装 jadx-ai-mcp 的 jar 与 zip，在 GUI 里装插件，再装两个 Python 包。连上与否只剩一次询问。

> pip install httpx fastmcp

> cursor和jadx都重启一下,然后问他连上了没

作者样本另外打开了 MCP 自动审批。本卡不抄工具名单，也不把自动审批写成接线的必要条件。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 安装对象是 mrexodia/ida-pro-mcp | `pip install --upgrade git+https://github.com/mrexodia/ida-pro-mcp` | source-report | ida-pro-mcp | 未在本机安装 |
| C2 | 配置由生成命令得到 | `ida-pro-mcp --config` | source-report | ida-pro-mcp | 未保存生成结果 |
| C3 | 必须用 IDA 自带的 python.exe | `一定要这样装,否则pip用不了` | source-report | IDA 当前 Python | 未复现失败形态 |
| C4 | 输出栏出现 server 与端口被写成启动成功 | `端口,这就代表启动成功;` | source-report | 作者的 IDA GUI | 只是作者自述 |
| C5 | JADX 侧依赖 httpx 与 fastmcp | `pip install httpx fastmcp` | source-report | jadx-mcp | 未安装 |
| C6 | JADX 侧只询问重启后是否连上 | `cursor和jadx都重启一下,然后问他连上了没` | source-report | 作者使用的 IDE | 没有失败出口 |
| C7 | 样本超时为 1800 | `"timeout": 1800,` | source-report | 作者粘贴的样本 | JSON 不可加载 |

## 验证与限制

没有独立失败出口：来源没有写端口缺失、插件未出现或 IDE 回答未连上时停在哪一步。因此这不是流程卡。

续杯、改机和账号轮换整段不进入本卡。本机用户目录和软件绝对路径也不进入本卡。Kiro 段的 `autoApprove` 只说明样本里有一份工具名列表，不构成第二套接口。
