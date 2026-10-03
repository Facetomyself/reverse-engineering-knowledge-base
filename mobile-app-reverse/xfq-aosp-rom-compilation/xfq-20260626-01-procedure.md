---
schema_version: 2
id: aosp-webview-per-app-devtools-force-procedure
document_type: procedure
original_date: '2026-06-26'
archived_date: '2026-10-02'
scope:
  targets:
    - AOSP WebView per-app DevTools force-enable
  client: AOSP panther WebView
  version: Chromium 109.0.5414.123
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260626-01.md#0-结论先写清楚"
    basis: source-report
  - id: s2
    ref: "./xfq-20260626-01.md#3-方案取舍"
    basis: source-report
  - id: s3
    ref: "./xfq-20260626-01.md#43-chromium-patch"
    basis: source-report
  - id: s4
    ref: "./xfq-20260626-01.md#5-编译与刷机验证"
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [s1, s2, s3]
    basis: source-report
    limits: 只覆盖来源已选择的“替换预编译 WebView 并按 ROMManager 强开”。隐藏、改 socket 名和第七节候选 hook 不在本流程里实现。
  - name: parameters
    anchor: prerequisites
    sources: [s2, s3]
    basis: source-report
    limits: property 名、socket 名和 Chromium tag 来自这份笔记。APK 摘要不写入本卡。子进程名回退规则没有单独的失败样本。
  - name: validation
    anchor: acceptance
    sources: [s1, s4]
    basis: source-report
    limits: prop 切换和前端 URL 回退是作者报告。CDP 的包名与 Browser 行写在“期望”下，实机验收记录没有逐项回显。本轮未连接 DevTools。
relations:
  - type: derived_from
    target: "./xfq-20260626-01.md#3-方案取舍"
tags:
  - aosp
  - webview
  - devtools
  - source-report
---

# 按包强开 AOSP WebView DevTools，且不在本功能里做隐藏

这张流程只处理来源拆出来的前半：目标 App 调用 `WebView.setWebContentsDebuggingEnabled(false)` 时，ROM 仍可按包打开 WebView DevTools。检测和隐藏被来源明确放到另一份笔记。它也不是“WebView 子进程为什么 attach 不上”那张卡。

<a id="prerequisites"></a>
## 前提与输入

- 最终 ROM 以 `user` 为准。来源写明不能依赖 `userdebug` / `eng` 的默认可调试，也不能只在 framework 里调用 `setWebContentsDebuggingEnabled(true)`，因为 App 自己还能把它关掉。
- 预编译基线是 `external/chromium-webview/prebuilt/arm64/webview.apk`，包名 `com.android.webview`，`versionName` `109.0.5414.123`。DevTools socket 仍是 `webview_devtools_remote_%d`。本功能不改这个名字。
- Chromium 源码固定到 tag `109.0.5414.123`，commit `1da24e1281b9ed5d02aa48789f8481ccb9469b13`。完整源码和构建缓存不进补丁仓库。
- 构建默认 `-j2 -l8`，避免和 AOSP 同时把机器打满。
- 配置只有两级：`persist.rommgr.webview_debug=1` 表示全局；否则读 `persist.rommgr.app.<process>.webview_debug=1`。进程名带 `:remote` 时回来源写的 base package。
- 本轮没有 Chromium 树，也没有设备。序列号和 APK 摘要不进入本卡。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 确认目标是 user 构建上的按包强开，而不是 userdebug 本来就能被 `chrome://inspect` 看见。 | 需求里的四条约束。 | 只需要调试自己的 userdebug 系统 WebView，来源认为不必走这条替换；否则 S2。 |
| S2 | 在方案表里排除：继续依赖 userdebug、只改 framework Java API、新造一个 provider 包名、在 Chromium 里改 socket 名或做隐藏。 | 表上的“不采用 / 从本功能剥离”。 | 若需求其实是隐藏 `/proc` 或 CDP，走 F3，不要塞进本功能；否则 S3。 |
| S3 | 用仓库里的 sync/build 脚本在外部目录编 SystemWebView，并发保持 `JOBS=2`。 | `out/XfWebViewArm64/apks/SystemWebView.apk`。 | 与 AOSP 抢满机器或源码要进补丁仓库，停止；否则 S4。 |
| S4 | patch 只保留强开：ROMManager 开启时，`SharedStatics.setWebContentsDebuggingEnabled(false)` 不关闭 DevTools；provider 初始化后即使非 debug build 也读上述 property。 | `patches/20260628_webview_chromium_force_debug/chromium_webview_force_debug.patch`。 | patch 开始改 socket 或加隐藏，走 F3；否则 S5。 |
| S5 | 用 import 脚本把新 APK 灌回 `external/chromium-webview/prebuilt/arm64/webview.apk`，并处理 DevTools 前端 404。 | 本机 `devtools://devtools/bundled/inspector.html?ws=<host>/devtools/page/<id>`。 | `/json/list` 仍是 `serve_rev/@/inspector.html`，走 F1；否则 S6。 |
| S6 | ROMManager 全局开关写 `persist.rommgr.webview_debug`，App 详情开关写 `persist.rommgr.app.<package>.webview_debug`。目标进程重启后 provider 才读到。UI 文案写明当前不做隐藏。 | 两个 property 与现有设置页，不新造复杂页面。 | 开关不能在 0/1 间切换，走 F2；否则 S7。 |
| S7 | `lunch aosp_panther-user` 后编 webview 与 WebViewDebugProbe，再按来源的 product 分区刷法检查 provider 与 CDP。 | 见验收。 | provider 不是 `com.android.webview`，或期望字段对不上，走 F2。 |

第七节的 Java/Blink/V8 候选点只是路线，不进入上表。

<a id="outputs"></a>
## 输出

- 外部目录中的 SystemWebView APK，以及灌回 AOSP `prebuilt/arm64/webview.apk` 的脚本记录。来源另记了一份 APK 摘要，本卡不复制该值。
- 只含强开逻辑的 Chromium patch，和 ROMManager 的两个 property。
- DevTools 前端 URL 从 appspot `serve_rev/@/inspector.html` 改为本机 bundled inspector。
- 作者报告的开关行为：App 详情里的 WebView 调试能在 0 和 1 之间切换。
- 来源写在“期望”里的 CDP 形状：`Android-Package` 为探针包名，`Browser=Chrome/109.0.5414.123`，以及 bundled inspector URL。期望不是实机回显。

<a id="acceptance"></a>
## 验收

basis 保持 source-report。本轮没有执行 adb 或 curl。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | provider 应为 `com.android.webview`，路径指向 ROM 内 WebView APK。 | s4，第 294 行 | source-report | 来源给出的 dumpsys / pm path 期望 | 实机验收记录没有贴出这两条命令的输出。 |
| C2 | 点击 App 详情页 WebView 调试后，prop 能在 `0` / `1` 间切换；打开按包功能时顶部“启用该应用”同步开启。 | 第 316–316 行 | source-report | 来源的 product 分区刷机记录 | 不是 user 构建上“App 调用 false 仍保持开启”的差异证明。 |
| C3 | 前端修复后 `/json/list` 的 `devtoolsFrontendUrl` 被写成 bundled inspector，而不是 appspot 404。 | 第 240-244 行 | source-report | 来源对 LASTCHANGE=0 的修复说明 | 没有保留那次 `/json/list` 全文。 |
| C4 | `m -j8 ROMManager productimage vbmetaimage vbmetasystemimage` 被写成通过，product-only 刷入后启动成功。 | 第 314-315 行 | source-report | 同一次刷机记录 | 未说明刷的是 user 还是 userdebug 产物。 |

反例：userdebug 上本来就能看见 DevTools，不能用来证明“非 debug build 的强开”。来源把这条写成必须改用 user 构建。

<a id="failure-exits"></a>
## 失败出口

F1：inspect 打开 target 跳到 `https://chrome-devtools-frontend.appspot.com/serve_rev/@/inspector.html` 并 HTTP 404。来源把根因写成 checkout 的 `build/util/LASTCHANGE` 为 `LASTCHANGE=0`，而 Android WebView 没有内置 DevTools frontend resources。修复点是 `DevToolsHttpHandler::GetFrontendURLInternal()` 在 Android 上改回本机 bundled frontend。URL 仍是 appspot 时，不要把“APK 已替换”当成 DevTools 可用。

F2：`dumpsys webviewupdate` 的实现包不是 `com.android.webview`，或按包 property 不能在 0/1 切换。停止声称 ROMManager 能控制该包。来源写目标 App 要重启后 provider 才生效；没重启不能当失败或成功。

F3：需求滑进隐藏或深度 hook。来源明确不改 socket 名，因为 `/proc`、connect 和 CDP 检测容易漏，而且 Chromium 维护变重。`/proc/net/unix`、`/proc/self/fd`、主动 `connect()` 和 `/json/list` 检测都不在本文实现。第七节的候选 API 必须另开 feature，不能和强开、Behavior、SSL 或 GMS 塞进同一分支。当前 userdebug 设备默认开启 DevTools 时，也走这条出口：它证明不了 user 上的强开差异。
