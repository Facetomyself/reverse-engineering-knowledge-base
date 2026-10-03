---
schema_version: 2
id: grok-web-reverse-benru-web-20260427-01
document_type: procedure
original_date: "2026-04-27"
archived_date: "2026-10-02"
scope:
  targets: [mitmproxy]
  client: python
  version: v11
  observed_at: unknown
sources:
  - id: s1
    ref: "./benru-web-20260427-01.md#四核心事件90-场景只用这三个"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只保留来源对 http_connect、request、response 三个钩子的文档字符串。未对照 v11 之后的 API。
  - name: parameters
    anchor: prerequisites
    sources: [s1]
    basis: source-report
    limits: 监听地址、端口和命令名都是来源文本。未执行 mitmdump --version。
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 分支只整理来源示例里的 host 与 path 条件。示例不改请求主机名。
  - name: validation
    anchor: acceptance
    sources: [s1]
    basis: source-report
    limits: mitm.it 证书页和终端日志都是作者演示。本轮没有启动代理。
relations:
  - type: derived_from
    target: "./benru-web-20260427-01.md#四核心事件90-场景只用这三个"
tags: [mitmproxy, http-proxy]
---

# mitmproxy v11 三个事件与本地代理检查

这份流程只整理来源已经写明的安装检查、三个 HTTP 钩子，以及作者用来判断代理是否生效的 `mitm.it` 页面。它不新增拦截规则，也不把作者对搜索页文字的演示当成当前结果。来源写这是开发调试工具，并且必须由客户端主动信任证书。quote: 你必须主动让客户端信任它的 SSL 证书。

<a id="interfaces"></a>
## 三个事件

来源把范围限定在 mitmproxy v11，并写百分之九十的场景只用下面三个钩子。

| 事件 | 来源写的时机 | 来源写的能力 |
|---|---|---|
| `http_connect` | CONNECT，隧道建立前 | 返回非 2xx 可拒绝连接。quote: 返回非 2xx 响应可拒绝连接。 |
| `request` | 完整读完 HTTP 请求后 | 可改 URL、headers、body。quote: 可修改请求 URL、headers、body。 |
| `response` | 完整读完 HTTP 响应后 | 可改响应内容。quote: 可修改响应内容。 |

插件类放进 `addons` 列表后，用来源的 `mitmweb -s` 启动。quote: mitmweb -s counter.py。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 来源要求 | 不足时 |
|---|---|---|
| 版本 | 正文写基于 mitmproxy v11。quote: 本文基于 mitmproxy v11。 | 不是这一版时，本流程没有依据 |
| 安装 | `pip3 install mitmproxy`，再用 `mitmdump --version` 看安装。quote: mitmdump --version | 命令不存在走 F1 |
| 命令 | `mitmproxy` 给终端交互，`mitmweb` 给 Web 界面，`mitmdump` 给无界面脚本。Windows 上 `mitmproxy` 依赖 curses，来源让改用 `mitmweb`。quote: 依赖 curses 库，直接使用 | 仍要跑 curses 版走 F1 |
| 代理 | HTTP，`127.0.0.1`，端口 `8080`。quote: 127.0.0.1:8080 | 浏览器没指向该地址时，不能做后面的证书页验收 |
| 证书 | 客户端必须信任 mitmproxy 的 SSL 证书 | 未信任时来源不保证 HTTPS 明文可见，走 F2 |

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 按来源安装并执行 `mitmdump --version` | 命令是否有版本输出 | 没有输出版本走 F1；有输出版本走 S2 |
| S2 | 用 `mitmweb -s` 加载带 `addons` 的脚本，浏览器 HTTP 代理设为 `127.0.0.1:8080` | 代理进程是否在听 | 听不到走 F1；听到走 S3 |
| S3 | 用 HTTP 打开 `http://mitm.it` | 是否出现证书下载页 | 出现走 S4；不出现走 F2。quote: 看到证书下载页面 → 代理生效。 |
| S4 | 只在来源已经写的条件上分支。百度条件是 host 与 path 前缀。quote: flow.request.host == "www.baidu.com" and flow.request.path.startswith("/s")。`www.so.com` 时改响应正文；`www.google.com` 的 CONNECT 返回 404 | 三个钩子各自的对象 | 主机或路径对不上就保持原请求。要改主机名不在本例默认路径里，走 F3 |

来源示例在百度搜索分支读取查询参数 `wd`，再 `set_all`。quote: flow.request.query.set_all("wd", ["360搜索"])。360 搜索分支替换响应正文。quote: flow.response.text = flow.response.text.replace("搜索", "请使用谷歌")。谷歌分支在 CONNECT 上构造 404。quote: http.HTTPResponse.make(404)。

<a id="outputs"></a>
## 输出

作者对百度示例的终端句子是 `捕获搜索词: Python`。quote: 捕获搜索词: Python。作者写实际发出的查询从 `wd=Python` 变成 `wd=360搜索`，并写这仍是百度的结果页，不是 360 的站点。360 示例的输出是响应正文里的“搜索”被换成“请使用谷歌”。谷歌示例的输出是连接被 404 拒绝。这些都是作者演示，不是本轮输出。

<a id="acceptance"></a>
## 验收

| 编号 | 通过条件 | 反例 |
|---|---|---|
| A1 | 来源写：用 HTTP 打开 `http://mitm.it` 并看到证书下载页，才算代理生效。quote: http://mitm.it | 打不开该页走 F2，不把进程启动当成通过 |
| A2 | 来源写：证书按系统装进信任位置后，刷新 HTTPS 不再有证书警告 | 本轮没有浏览器，不能把 A2 勾成已通过 |
| A3 | 作者把百度示例的终端日志写成 `捕获搜索词: Python` | 没有这份日志，不能把查询改写当成已发生 |

A1 到 A3 都停在 source-report。

<a id="failure-exits"></a>
## 失败出口

F1：Windows 上直接运行依赖 curses 的 `mitmproxy` 时，来源要求改用 `mitmweb`。quote: 直接使用  ` mitmweb  ` 更省心。版本命令没有输出时同样停止，不继续写钩子已经生效。

F2：`http://mitm.it` 必须用 HTTP。看不到证书下载页时停止，不把 HTTPS 解密写成已经可用。来源的 Windows 信任位置是“受信任的根证书颁发机构”，macOS 是对 `mitmproxy` 证书选择始终信任。手机只写了把代理设为电脑 IP 的 8080 再访问 `mitm.it`，没有系统版本；缺这些材料时不外推。

F3：来源明确写，示例并没有把百度请求跳转到 360 的域名，只改了搜索词。quote: 示例并没有真正把百度请求跳转到 360 域名，而是修改搜索词。若目标是改主机，来源另给 `flow.request.host = "www.so.com"`，并写那只是展示改地址，不是本例已经做到的事。quote: flow.request.host = "www.so.com"。不要把查询改写的验收用来证明主机已经改变。
