---
schema_version: 2
id: wechat-windows-sendmsg-static-case
document_type: case
original_date: unknown
archived_date: "2026-10-08"
scope:
  targets: [wechat-windows]
  client: windows
  version: "4.1.13.65"
  observed_at: unknown
sources:
  - id: s1
    ref: ./wechat-windows-sendmsg-static.md#source-body
    basis: source-report
relations:
  - type: derived_from
    target: ./wechat-windows-sendmsg-static.md#source-body
tags: [wechat, sendmsg, static]
---

# 微信 Windows 4.1.13.65 发送消息的静态定位

## 问题与范围

来源要定位 `4.1.13.65`（原文写 2025-09-17 构建）里“发送消息”停在哪一层。范围是静态：PE、已加载模块表、字符串和 localhost 端口。来源写明没有注入、没有 hook、没有发出消息。地址不能挪到别的构建。

## 过程与关键证据

来源描述的布局：安装目录里的 `Weixin.exe` 是启动器，运行时代码在 `%APPDATA%\Tencent\xwechat\xplugin\plugins\` 下按组件解压。`Weixin.dll` 的 RTTI 被来源归到 Skia、ICU、SkSL 等第三方库，`mmui::` 没有 RTTI 类，但 `.rdata` 仍有类名字符串。`.pdata` 被来源当作剥离符号后的函数边界。

字符串锚点包括 `micromsg.SendMsgRequestNew`、CGI `sendmsg` / `sendappmsg` / `newsendmsg`，以及 `message::send_message` 和 JSON 键 `to_user_name`、`content_xml_base64`、`msg_type`。来源用 RIP 相对引用加 `.pdata` 复核，写出一条单调用者链，底部函数 `0x1854b7a00` 被它解释为真正的发送实现。该函数没有直接 `call rel32` 调用者，来源认为入口在命令注册表里。

传输层是另一条路：`ilink2.dll` 的 `ilink::zidl_export::*`，包括 `NetworkManager::SendRequest`。来源把它对应到 macOS `mars` `req2buf` 的位置，这是对照陈述，不是本篇抓到的包。

反例同样来自原文：主进程五个 `127.0.0.1` 端口对 `/` 和 `/json/version` 无响应；结合 `mmmojo_64.dll`，来源判断这是 Mojo IPC，不是外部 HTTP。因此 `message::send_message` 被写成进程内接口。

## 结论与反例

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 4.x 运行时按插件 ZIP 解压，`Weixin.dll` 的 RTTI 扫不到 `mmui::` | s1 架构节 | source-report | 该次模块表 | 未复核 DLL |
| C2 | 发送实现被定位到 `0x1854b7a00`，上面是 JSON 命令注册 | s1 调用链 | source-report | 仅 4.1.13.65 | 未动态确认参数布局 |
| C3 | 五个 localhost 端口不是可直接调用的 HTTP | s1 外部可达性 | source-report | 该次 PID 的端口表 | 端口号是一次观察 |
| C4 | 来源没有注入，也没有发出消息 | s1 文首和风险节 | source-report | 该篇自述 | 不能当成发送已成功 |

## 未决项与复用启示

来源自己列出的下一步是注入后只读观察 `0x1854b7a00` 的入参，再决定是否调用。那一步没有做，本文不把它写成流程。部分 `.rdata` 字符串来源称运行时才解密。`ilink2.dll` 导出可能只是 zidl 代理。公众号 Web 会话平面不是这条客户端链路。
