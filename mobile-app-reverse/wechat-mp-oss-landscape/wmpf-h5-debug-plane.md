# WMPF H5 调试面与 WeixinJSBridge Mock

> 来源: GitHub 对照 xuange520/WeChat-H5-DevTools、WMPFDebugger 族；对照 `workspace/weixin_download` 发证审计
> 原始发布时间: 2026-09-15
> 归档日期: 2026-09-15
> 分类: mobile-app-reverse
>
> 微信 4.x 关掉内置浏览器物理 F12 后，开源工具用 Frida / 透明代理 / JSBridge Mock 做 H5 调试。这是观察面，不是 `getmsg` 发证面。外部 Chrome 注入 30+ `WeixinJSBridge` 只能过「请在微信客户端打开」的 JS 门，签发不了真 `uin/key`。小程序 CDP（`wechat-miniapp-re-mcp` / `flue.dll`）与公众号 H5 不要混成一个入口。

## 工具分面

| 能力 | 代表 | 对归档的意义 |
|------|------|----------------|
| Frida 给 4.x renderer 开调试通道 | WeChat-H5-DevTools `hook`；WMPFDebugger / WeChatOpenDevTools | 能看 Network，不能当产品发证器；锁微信大版本 |
| 本机透明代理注入 vConsole / Eruda | `wx-h5 proxy`（默认 8899） | 接近 wxdown-service：人打开页面，工具观察/收证 |
| 外部浏览器 + UA + JSBridge Mock | `wx-h5 open` | 调试「必须在微信打开」的 **页面 JS**；下载会拿到验证页 |
| Webpack dump / AST / SourceMap / 国密扫描 | `dump` / `deobfuscate` / `scan` | 适合业务 H5 SPA；公众号推文页是服务端 HTML，不是解包题 |
| 小程序 CDP / `flue.dll` 偏移 | reverse_ENV `wechat-miniapp-re-mcp`、`wmpf-offset-adaptation` | `.wxapkg` / AppService，不管 `profile_ext` |

[xuange520/WeChat-H5-DevTools](https://github.com/xuange520/WeChat-H5-DevTools) 源码分 `injector/`、`sandbox/`、`extractor/`，依赖 `frida` + `websockets`。CLI：`doctor` / `hook` / `proxy` / `open` / `dump` / `deobfuscate` / `restore` / `scan`。

## 4.x 内核事实（避免套 3.9 偏移）

README 兼容矩阵（作者声称测到 4.1.13.12）：

| 客户端 | 内核线索 | 进程 | 注入 |
|--------|----------|------|------|
| 4.1.x | RadiumWMPF **25560 / 25510** 等 | `WeixinExt.exe`、`Weixin.exe --type=renderer` | Frida 拦 `CreateProcessW` + 代理注入 vConsole |
| 4.0.x | 16389 / 16203 一带 Blink 重构 | `Weixin.exe`、`WeChatAppEx.exe` | 多点命令行注头 |
| 3.9.x | XWeb / Chromium 85–108 | `WeChat.exe`、`WeChatAppEx.exe` | `--xweb-enable-inspect=1` |
| 外部沙箱 | 本机 Chrome/Edge | 浏览器自身 | `document_start` 注入 Mock |

本机内核目录：`%AppData%\Tencent\xwechat\XPlugin\Plugins\RadiumWMPF\<纯数字>`。3.9 `WeChatWin.dll` 地址表不得直接套 4.x。CreateProcess 命令行注入比硬编码 RVA 更抗小版本，仍要随大版本失效。

同族：[Bai-Ye-Yi/WMPFDebugger-kiss](https://github.com/Bai-Ye-Yi/WMPFDebugger-kiss) 文档写明 H5 调试往往要先开一个小程序会话，再 `Target.getTargets` 附加内置浏览器页。这是 CDP 借道，不是 HTTPS 发证。

## Mock ≠ 签发

`WeixinJSBridge` 是客户端注入给页面的 native 桥（分享、扫码、支付、定位）。外部沙箱 Mock 30+ API 的目标是让页面 `typeof WeixinJSBridge !== 'undefined'`，从而不跳「请在微信客户端打开」。

`getmsg` 的 `key` 来自原生 `NetSceneGetA8Key`（见 [GetA8Key](./geta8key-native-cgi.md)）。页面 JS 算不出来。因此：

- `wx-h5 open` 打开的推文 URL，不能当登录态正文。
- vConsole Network 里若出现 `profile_ext` / `uin=`，那是**真 WebView 流量**，价值在观察，不在 Mock。
- 同一 URL：外部沙箱 → 验证页；微信内置浏览器 + 有效会话 → 真正文。这是内容校验的对照样本，不是新的历史源。

## 和归档仓的衔接

若只要验证「本机 4.x 打开一篇后能否收到 key」：

```text
wx-h5 proxy --port 8899
  -> 微信走 127.0.0.1:8899
  -> 人手打开 profile_ext?action=home
  -> 记录脱敏后的 query 形状与 getmsg ret
```

这与 wxdown-service 同类，仍要人打开页面。不要把 Frida `hook` 写进纯 HTTP 下载主链。小程序调试继续走 WMPF MCP，不要用 H5-DevTools 去补 `flue.dll` 偏移。
