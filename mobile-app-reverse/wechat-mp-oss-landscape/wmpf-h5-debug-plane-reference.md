---
schema_version: 2
id: wechat-h5-devtools-wmpf-debug-plane
document_type: reference
original_date: '2026-09-15'
archived_date: '2026-09-15'
scope:
  targets:
    - WeChat-H5-DevTools
  client: WeChat Windows
  version: 4.x
  observed_at: '2026-09-15'
sources:
  - id: s1
    ref: "./wmpf-h5-debug-plane.md#工具分面"
    basis: source-report
  - id: s2
    ref: "./wmpf-h5-debug-plane.md#4x-内核事实避免套-39-偏移"
    basis: source-report
  - id: s3
    ref: "./wmpf-h5-debug-plane.md#mock--签发"
    basis: source-report
  - id: s4
    ref: "./wmpf-h5-debug-plane.md#和归档仓的衔接"
    basis: source-report
  - id: s5
    ref: "./wmpf-h5-debug-plane.md#wmpf-h5-调试面与-weixinjsbridge-mock"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: CLI 和默认端口来自来源对 xuange520/WeChat-H5-DevTools 的对照。未安装该工具，未对 4.1.13.12 复跑。
  - name: parameters
    anchor: parameters
    sources: [s2]
    basis: source-report
    limits: 内核号、进程名和注入方式是来源转述的 README 兼容矩阵。RVA 与小版本会失效，本卡未在本机内核目录核对。
  - name: risk-control
    anchor: risk-control
    sources: [s2, s3, s4, s5]
    basis: source-report
    limits: 观察面与发证面的分界是来源结论。未打开页面，未核对任何票据是否出现。
relations:
  - type: derived_from
    target: "./wmpf-h5-debug-plane.md#wmpf-h5-调试面与-weixinjsbridge-mock"
tags:
  - WeChat-H5-DevTools
  - RadiumWMPF
  - WeixinJSBridge
---

# WeChat 4.x H5 调试面不是发证器

这张卡只回答：Windows 微信 4.x 关掉内置浏览器物理 F12 之后，开源调试工具的入口、内核分代，以及哪些结果不能当成 `getmsg` 发证。不覆盖公众号 HTTPS 字段，也不覆盖五套会话划分。

近邻 `wechat-official-account` 已有 HTTP 接口面和会话平面，没有 WeChat-H5-DevTools 的 CLI 或 RadiumWMPF 矩阵。文末的人工打开页面只是边界，不是闭合流程。

<a id="interfaces"></a>
## 工具入口

来源把 WeChat-H5-DevTools 分成 `injector/`、`sandbox/`、`extractor/`，依赖 `frida` 与 `websockets`。CLI 是 `doctor`、`hook`、`proxy`、`open`、`dump`、`deobfuscate`、`restore`、`scan`。

`hook` 给 4.x renderer 开调试通道，能看 Network，不能当发证器，并且锁微信大版本。`wx-h5 proxy` 默认 8899，要人打开页面才观察。`wx-h5 open` 只调试「必须在微信打开」的页面 JS，下载会落到验证页。Webpack dump 适合业务 H5 SPA，不适合服务端 HTML 的公众号推文页。小程序 CDP 与 `flue.dll` 管 `.wxapkg` / AppService，不管 `profile_ext`。

WMPFDebugger-kiss 写明：H5 调试往往要先开一个小程序会话，再 `Target.getTargets` 附加内置浏览器页。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | CLI 分成八个命令，源码三目录 | s1 第 45 行：源码分 `injector/`、`sandbox/`、`extractor/`，依赖 `frida` + `websockets`。CLI：`doctor` / `hook` / `proxy` / `open` / `dump` / `deobfuscate` / `restore` / `scan`。 | source-report | 来源对照的 WeChat-H5-DevTools | 未安装、未跑 CLI |
| C2 | hook 能看 Network，不能当发证器 | s1 第 39 行：能看 Network，不能当产品发证器；锁微信大版本 | source-report | 4.x renderer 调试通道 | 未看 Network |
| C3 | proxy 默认 8899，且要人打开页面 | s1 第 40 行：`wx-h5 proxy`（默认 8899） | source-report | 本机透明代理这一行 | 未监听该端口 |
| C4 | open 只打页面 JS，下载得到验证页 | s1 第 41 行：调试「必须在微信打开」的 **页面 JS**；下载会拿到验证页 | source-report | 外部浏览器 Mock | 未下载页面 |
| C5 | 小程序 CDP 不管 profile_ext | s1 第 43 行：`.wxapkg` / AppService，不管 `profile_ext` | source-report | wechat-miniapp-re-mcp 与偏移适配 | 未打开小程序包 |

<a id="parameters"></a>
## 内核、进程与注入

来源把 README 兼容矩阵记到作者声称的 4.1.13.12，并要求不要把 3.9 偏移套到 4.x。

| 客户端 | 内核线索 | 进程 | 注入 |
|---|---|---|---|
| 4.1.x | RadiumWMPF 25560 / 25510 等 | `WeixinExt.exe`、`Weixin.exe --type=renderer` | Frida 拦 `CreateProcessW`，再代理注入 vConsole |
| 4.0.x | 16389 / 16203 一带 Blink 重构 | `Weixin.exe`、`WeChatAppEx.exe` | 多点命令行注头 |
| 3.9.x | XWeb / Chromium 85–108 | `WeChat.exe`、`WeChatAppEx.exe` | `--xweb-enable-inspect=1` |
| 外部沙箱 | 本机 Chrome/Edge | 浏览器自身 | `document_start` 注入 Mock |

本机内核目录形状是 `%AppData%\Tencent\xwechat\XPlugin\Plugins\RadiumWMPF\<纯数字>`。3.9 的 `WeChatWin.dll` 地址表不能直接套 4.x。命令行注入比硬编码 RVA 更抗小版本，大版本仍会失效。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 4.1.x 进程与注入方式按 RadiumWMPF 25560 / 25510 记 | s2 第 53 行：RadiumWMPF **25560 / 25510** 等 | source-report | 来源矩阵里的 4.1.x | 未在本机目录核对纯数字版本 |
| C7 | 4.0.x 用多点命令行注头 | s2 第 54 行：16389 / 16203 一带 Blink 重构 | source-report | 来源矩阵里的 4.0.x | 未复现注头 |
| C8 | 3.9.x 的开关是 xweb-enable-inspect | s2 第 55 行：`--xweb-enable-inspect=1` | source-report | 来源矩阵里的 3.9.x | 不能套到 4.x |
| C9 | 内核目录是 RadiumWMPF 下的纯数字文件夹 | s2 第 58 行：`%AppData%\Tencent\xwechat\XPlugin\Plugins\RadiumWMPF\<纯数字>` | source-report | 来源写的本机路径形状 | 未列出实际目录 |

<a id="risk-control"></a>
## 观察不等于签发

来源把这套工具定义为观察面，不是 `getmsg` 发证面。外部 Chrome 注入 30 多个 `WeixinJSBridge`，只能让页面通过「请在微信客户端打开」的 JS 门，签发不了真 `uin/key`。Mock 的目标是 `typeof WeixinJSBridge !== 'undefined'`。`getmsg` 的 `key` 来自原生 `NetSceneGetA8Key`，页面 JS 算不出来。

同一 URL：外部沙箱得到验证页；微信内置浏览器加有效会话才是真正文。vConsole 里若出现 `profile_ext`，价值在观察真 WebView 流量，不在 Mock。CDP 附加是借道，不是 HTTPS 发证。不要把 Frida `hook` 写进纯 HTTP 下载主链，也不要用 H5-DevTools 去补 `flue.dll` 偏移。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C10 | H5 调试是观察面，不是 getmsg 发证面 | s5 第 33 行：这是观察面，不是 `getmsg` 发证面。 | source-report | 来源点名的开源 H5 调试工具 | 未对照发证响应 |
| C11 | 外部 Mock 只过 JS 门，签发不了真 uin/key | s5 第 33 行：签发不了真 `uin/key` | source-report | 外部 Chrome 注入的 JSBridge | 字段名不是原值；未采样 |
| C12 | Mock 只求桥对象存在 | s3 第 64 行：`typeof WeixinJSBridge !== 'undefined'` | source-report | 外部沙箱的 30+ API Mock | 未执行页面脚本 |
| C13 | getmsg 的 key 来自 NetSceneGetA8Key，页面 JS 算不出 | s3 第 66 行：页面 JS 算不出来。 | source-report | 来源指向的 GetA8Key 笔记 | 未调用该 CGI |
| C14 | 先开小程序再 getTargets 仍是 CDP 借道 | s2 第 60 行：这是 CDP 借道，不是 HTTPS 发证。 | source-report | WMPFDebugger-kiss 文档所述路径 | 未附加 target |
| C15 | hook 不能写入纯 HTTP 下载主链 | s4 第 83 行：不要把 Frida `hook` 写进纯 HTTP 下载主链。 | source-report | 与 wxdown-service 同类的收证 | 未跑下载链 |

## 验证与限制

未安装 WeChat-H5-DevTools，未打开微信，未核对 RadiumWMPF 目录。4.1.13.12 只是来源转述的 README 声称。会话平面卡已经有一句「调试不能替代发证」，本卡补的是 CLI、内核矩阵和 CDP 借道，不重复五套会话。人工打开 `profile_ext` 的四行草图没有验收条件和失败出口，不能当流程。
