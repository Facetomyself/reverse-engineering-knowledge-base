---
schema_version: 2
id: android-webkit-webview-bridge-reference
document_type: reference
original_date: '2026-03-22'
archived_date: '2026-10-02'
scope:
  targets:
    - android.webkit WebView
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260322-01.md#1-webview-基础概念与内核演进-"
    basis: source-report
  - id: s2
    ref: "./xfq-20260322-01.md#2-安卓正向开发webview-全景指南-"
    basis: source-report
  - id: s3
    ref: "./xfq-20260322-01.md#3-官方-web-app-调试方案-"
    basis: source-report
  - id: s4
    ref: "./xfq-20260322-01.md#4-深度解析webview逆向中的数据流向-"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s4]
    basis: source-report
    limits: 只保留来源写的内核分代、两个 WebSettings 开关和 WebMessage 的源站允许列表这个参数位置。没有系统版本、WebView APK 版本或一次设置日志。
  - name: interfaces
    anchor: interfaces
    sources: [s2, s4]
    basis: source-report
    limits: 只保留来源点名的类和方法。代码围栏被拆行，本卡不还原成可编译片段，也不重建第 5 节没有附上的脚本。
  - name: decision-flow
    anchor: decision-flow
    sources: [s3]
    basis: source-report
    limits: 只保留来源对官方 inspect 入口的描述。没有设备上的 inspect 记录，因此不是流程。
  - name: request-chain
    anchor: request-chain
    sources: [s4]
    basis: source-report
    limits: 只保留来源用滑块页说明的 Java 与 JS 两个调用方向。不收录令牌样值，也不提供截获脚本。
  - name: risk-control
    anchor: risk-control
    sources: [s2]
    basis: source-report
    limits: 只保留来源点名的三类隐患和那个文件协议开关的名字。不写读取私有目录或构造参数的步骤。
relations:
  - type: derived_from
    target: "./xfq-20260322-01.md#2-安卓正向开发webview-全景指南-"
tags:
  - webview
  - jsbridge
  - source-report
---

# Android WebView：四个类、调试入口和两代桥

这张卡只回答：来源把 `android.webkit` 的哪几个类、哪两个调用方向，以及官方调试入口写成可定位的观察点。第 5 节点名但没有附上的脚本不重建。文件协议和未消毒参数只保留隐患名字。

来源没有可公开定位的原文 URL。作者自称的成功只保留为 source-report。示例域名不是一次观测到的部署。

<a id="parameters"></a>
## 版本与设置

来源按系统版本把内核分成四段，没有给出具体 WebView APK 版本：

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 4.3 及以前被写成早期 WebKit，使用 JSCore。 | Android 4.3 及以前(早期 WebKit 时代) | s1，第 84 行 | source-report | 没有该时代的样本 |
| C2 | 4.4 起被写成切到 Chromium，并带上 V8 和 Blink，更新仍绑系统。 | 将 WebView 内核切换为Chromium | s1，第 85 行 | source-report | 未核对 AOSP 提交 |
| C3 | 5.0 起被写成可单独升级的系统组件。 | WebView 被剥离为一个可单独通过 Google | s1，第 86 行 | source-report | 句子在行末断开，包名不完整 |
| C4 | 8.0 起被写成渲染进入独立子进程。 | 引入了分离的渲染子进程(Renderer Process) | s1，第 93 行 | source-report | 不讨论如何附加该进程 |
| C5 | 白屏一节把 JavaScript 写成要显式打开。 | settings.setJavaScriptEnabled(true); | s2，第 168 行 | source-report | 来源标成正向配置，不是测量结果 |
| C6 | 同一节把 DOM storage 写成默认关闭。 | settings.setDomStorageEnabled(true); | s2，第 175 行 | source-report | 没有对应的页面报错日志 |
| C7 | WebMessage 监听器带一组允许的源站。 | Arrays.asList("https://example.com") | s4，第 471 行 | source-report | example.com 是来源示例，不是观测主机 |

<a id="interfaces"></a>
## 类与桥

来源把 `android.webkit` 收成四个类，并说安全测试或抓包时这四类是审计对象：

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C8 | WebSettings 被写成引擎配置。 | WebSettings(底层引擎配置) | s2，第 135 行 | source-report | 后文只展开了少数开关 |
| C9 | WebViewClient 被写成资源加载和导航。 | WebViewClient(网络请求与路由总管) | s2，第 141 行 | source-report | 未列出全部回调 |
| C10 | WebChromeClient 被写成页面与系统 UI 的桥。 | WebChromeClient(系统交互与 UI 桥梁) | s2，第 147 行 | source-report | 未列出全部回调 |
| C11 | JavascriptInterface 被写成 JS 与 Java 的通道。 | JavascriptInterface(双端通信交互通道) | s2，第 154 行 | source-report | 不重建注入代码 |
| C12 | 非 http/https 的导航被写到 shouldOverrideUrlLoading。 | public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequestrequest) | s2，第 200 行 | source-report | 围栏被拆行，本卡不补全 |
| C13 | 文件选择被写到 onShowFileChooser。 | public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> | s2，第 246 行 | source-report | 只是回调名，没有相册实现 |
| C14 | Java 调 JS 被写成 evaluateJavascript。 | evaluateJavascript 接口向网页环境执行指定的全局 JS 方法 | s4，第 387 行 | source-report | 示例方法名不是某次抓到的符号 |
| C15 | JS 调 Java 的旧入口被写成 addJavascriptInterface。 | 依靠 addJavascriptInterface 等机制 | s4，第 442 行 | source-report | 来源同时把它标成旧通道 |
| C16 | 替代入口被写成 addWebMessageListener。 | 基于 addWebMessageListener 开发 | s4，第 463 行 | source-report | 没有实际注册日志 |

<a id="decision-flow"></a>
## 调试入口

来源把官方调试写成：KitKat 及以上调用 `WebView.setWebContentsDebuggingEnabled(true)`，电脑打开 `chrome://inspect/#devices`，再点 inspect，从而看 DOM、Network 和断点。来源另写商业 App 会把该参数预设为 false，并把逆向的第一步说成用 Frida 改这个方法的入参，然后再打开 inspect。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C18 | 来源给出的打开调试的调用。 | WebView.setWebContentsDebuggingEnabled(true); | s3，第 322 行 | source-report | 没有本机调用记录 |
| C19 | 来源给出的桌面入口。 | chrome://inspect/#devices | s3，第 324 行 | source-report | 没有页面是否出现的记录 |
| C20 | 来源把商业 App 的预设写成 false，并把改这个方法说成第一步。 | setWebContentsDebuggingEnabled(false) 保护。所以逆向的话最核心的第一步就是:利用 | s3，第 342 行 | source-report | 第 348–377 行的脚本不抄入本卡 |

这三句没有前提版本、可见产物的验收，也没有「inspect 里没有页面时停止」的失败出口，所以不是流程。另外三种排错（把 console 打到 logcat、加载局域网页面、安装 WebView DevTools App）来源自己把前两种写成辅助，本卡不升成步骤。

<a id="request-chain"></a>
## 进程内交接

来源用登录页里的滑块说明两条方向，而不是给出某个 App 的协议：

1. 原生经 `evaluateJavascript` 调页面里的方法。
2. 页面经已经挂上的 JSBridge 调回 Java。来源写外层 HTTP/HTTPS 包往往看不全这次交接。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C21 | 回调用旧桥交回原生。 | 前端必须通过预先建立的接口通道(JSBridge)反向调用 | s4，第 393 行 | source-report | 没有令牌样值 |
| C22 | 来源认为只抓外层 HTTP 不够。 | 单纯抓取外层的 HTTP/HTTPS 协议包往往难以连贯追溯 | s4，第 431 行 | source-report | 后半句的内存 Hook 没有脚本，本卡不重建 |

<a id="risk-control"></a>
## 来源点名的隐患

这一节被来源标成追数据流时可以不看。本卡只保留名字：

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C23 | 回收被写成要在 onDestroy 里结束到 destroy。 | webView.destroy() | s2，第 269 行 | source-report | 没有泄漏复现 |
| C24 | 文件协议的全局访问开关被标成隐患。 | settings.setAllowUniversalAccessFromFileURLs(true); | s2，第 278 行 | source-report | 不写该开关打开后的读取步骤 |
| C25 | 第三类只保留混合内容与 XSS 这个标题。 | 隐患 3:混合资源挂起屏蔽与 XSS 注入命令 | s2，第 288 行 | source-report | 不写参数如何变成命令 |

## 验证与限制

- 同目标 `android.webkit WebView` 的 interfaces、parameters、decision-flow、request-chain、risk-control 近邻查询都没有命中。
- `Android WebView child-process attach` 命中的是 FinClip 三进程笔记的 decision-flow，只讲 ptrace 和 attach，不包含这四个类，也不把本篇补进那张卡。8.0 的渲染子进程在这里只是内核分代，不是 attach 方法。
- 第 488 行写「直接使用我编写的深度监控脚本」，正文没有这份脚本。第 559 行的 `ReactNativeWebView.postMessage`、以及后面的 Cookie 与文件权限探针，因此都不进入模块。
- 代码围栏多次在语句中间换行。本卡不把它们补成可执行片段。
- 文首三枚外链只是链接，没有摘出其中的做法。
