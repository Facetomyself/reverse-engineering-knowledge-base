---
schema_version: 2
id: yuanrenxue-web-20260319-jsreverser-mcp-setup
document_type: procedure
original_date: '2026-03-19'
archived_date: '2026-10-02'
scope:
  targets:
    - JSReverser-MCP
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./yuanrenxue-web-20260319-01.md#1安装nodejs-管理工具-fnm"
    basis: source-report
  - id: s2
    ref: "./yuanrenxue-web-20260319-01.md#2安装codex"
    basis: source-report
  - id: s3
    ref: "./yuanrenxue-web-20260319-01.md#1安装并构建-jsreverser-mcp"
    basis: source-report
  - id: s4
    ref: "./yuanrenxue-web-20260319-01.md#2-配置-codex参数"
    basis: source-report
  - id: s5
    ref: "./yuanrenxue-web-20260319-01.md#启动浏览器与mcp检查"
    basis: source-report
modules:
  - name: interfaces
    anchor: prerequisites
    sources: [s1, s3, s4, s5]
    basis: source-report
    limits: 仓库、端口和检查地址来自来源。未克隆、未构建、未打开 9222。示例里的本机用户目录不抄。
  - name: decision-flow
    anchor: steps
    sources: [s1, s2, s3, s4, s5]
    basis: source-report
    limits: 步骤停在来源已经写出的安装和端口检查。两个案例的截图、token 和 a_bogus 不在本流程里。
  - name: validation
    anchor: acceptance
    sources: [s1, s5]
    basis: source-report
    limits: 「返回24」和「如有返回就对了」是作者的检查句。本轮没有执行这些命令。
relations:
  - type: derived_from
    target: "./yuanrenxue-web-20260319-01.md#启动浏览器与mcp检查"
tags:
  - JSReverser-MCP
  - source-report
---

# JSReverser-MCP 在这篇笔记里的本地接通检查

这份流程只回答：来源如何把 fnm、Node、Codex CLI、JSReverser-MCP 和本机 Chrome 调试端口接到「可以写提示词」之前。它不还原任何签名，不收录后文的长提示词，也不把 30 分钟或 42 分钟的截图当成验收。

抖音请求面和 a_bogus 卡片已经覆盖那些目标的参数与链路。本篇只在标题里点了 a_bogus，没有字段可补。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 来源要求 | 不足时 |
|---|---|---|
| PowerShell | 当前用户 ExecutionPolicy 设为 RemoteSigned。quote: Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force | 命令不能执行则走 F1 |
| Node 管理 | winget 安装 Schniz.fnm，再 `fnm install 24` 与 `fnm use 24`。quote: winget install Schniz.fnm | 没有 winget 或 fnm 失败则走 F1 |
| 持久化 | 来源把同一条 fnm env 管道写进 PowerShell profile，并写每次打开 shell 也要执行一次。quote: 每次打开shell都要执行一次 | profile 没写成时，不要把一次性会话当成已持久化 |
| Codex CLI | `npm install -g @openai/codex`。quote: npm install -g @openai/codex | 装不上走 F1。登录方式本卡不写 |
| 仓库 | `git clone  https://github.com/NoOne-hub/JSReverser-MCP.git`。没有 git 则改为下载项目。quote: 没有git就直接去把项目下载下来也可以 | 目录里没有构建入口走 F1 |
| 浏览器 | 来源用 Chrome 打开远程调试端口 9222。quote: --remote-debugging-port=9222 | 检查地址没有返回走 F1 |
| 配置 | 来源示例把 MCP 服务名写成 js-reverse，browserUrl 写成 `http://127.0.0.1:9222`。quote: http://127.0.0.1:9222 | 与仓库当前配置不一致走 F2，不粘贴笔记里的折叠 toml |

CODEX_HOME 在来源里是临时环境变量。quote: 这个是设置codex的临时环境变量
具体目录不抄。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 按来源放开当前用户脚本策略，安装 fnm，执行它要求的 env 初始化，再安装并使用 Node 24 | `node -v` 的输出 | 输出被来源接受为 24 则走 S2，否则 F1 |
| S2 | 全局安装 Codex CLI | 能够进入 `codex` | 命令存在走 S3，否则 F1。如何取得登录本卡不写 |
| S3 | 克隆或下载 JSReverser-MCP，在该目录执行来源的 npm install 和 npm run build | 构建是否完成 | 完成走 S4，否则 F1 |
| S4 | 先读仓库里的配置，再决定是否采用笔记中的 js-reverse 与 browserUrl | 配置与仓库说明是否还一致 | 一致走 S5；作者写明策略会变，不一致走 F2 |
| S5 | 用来源的远程调试端口启动 Chrome，访问 `http://127.0.0.1:9222/json/version` | 该地址是否有返回 | 有返回走 S6，否则 F1 |
| S6 | 执行 `codex mcp list`，再在 codex 里看 `/mcp` | 列表里是否出现来源配置的服务 | 出现则进入验收，否则 F1 |

案例一的练习页提示词、案例二的截图，以及后文那条长示例，都不是上表的步骤。

<a id="outputs"></a>
## 输出

接通检查的交付只有三件：`node -v` 被来源写成返回 24，`http://127.0.0.1:9222/json/version` 有返回，以及 `codex mcp list` 和 `/mcp` 能看到服务。quote: codex mcp list

不交付 token、页码、a_bogus 或任何采集脚本。案例用时 30 分钟和 42 分钟是作者对截图过程的自述。

<a id="acceptance"></a>
## 验收

1. Node 检查的原文是：返回24即安装成功。不是 24 就不算这一项通过。
2. 调试端口的原文是：如有返回就对了。没有返回就不算 Chrome 侧通过。
3. MCP 侧用来源点名的 `codex mcp list` 和 `/mcp`。本卡没有另定成功文案。
4. 反例：案例截图、本地执行效果图、30 分钟或 42 分钟，都不能代替上面三项。

本轮没有执行这些命令。

<a id="failure-exits"></a>
## 失败出口

F1：策略、fnm、Node 24、Codex CLI、构建或 `json/version` 任一检查没有来源所写的结果时停止。不要用后文截图补这一缺口。

F2：配置不能照抄。quote: 这个配置策略很有可能随着项目的更新有所调整，请读懂项目配置之后再自己弄
与仓库不一致时停止，先读项目自己的配置。

模型拒绝之后改提示词再试的段落不进入失败出口，也不写成步骤。后记里的其它 skill 链接原文写没有做详细测试，效果仅供参考，不纳入本流程。
