---
schema_version: 2
id: koohai-android-webview-debug-force
document_type: reference
original_date: '2024-01-08'
archived_date: '2026-09-06'
scope:
  targets: [android-webview]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./koohai-20240108-01.md#基础篇-webview调试及源码修改"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只保留作者写出的 inspect 地址、布局查看器和 WebView 调试开关。没有应用包名，也没有本次打开页面的记录。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 源码改动是作者放在本地 AOSP 树里的两处赋值。没有版本号、没有补丁前后字节，文末大段构造函数粘贴不作为差分。
relations:
  - type: derived_from
    target: "./koohai-20240108-01.md#基础篇-webview调试及源码修改"
tags: [android-webview, source-report]
---

# Android WebView 强制打开调试的入口

这张卡只回答：作者把内嵌页调试指到哪个入口，以及在 WebView 源码里改哪一个开关。依据停在 source-report。近邻没有 target 为 android-webview 或 webview 的卡片。同主题的 xfq 讲义和 ROM 笔记仍是归档，target 为 unknown，不并进这里。

<a id="interfaces"></a>
## 调试入口

作者用电脑上的 inspect 页看手机里的内嵌页，并用 uiautomatorviewer 看最外层是不是 WebView。调试开关是 `android.webkit.WebView.setWebContentsDebuggingEnabled`。系统没有被魔改时，作者把这里当成一个 Frida hook 点。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 先在 chrome 中打开 `chrome://inspect/#devices`，到这里就可以调试。 | s1 ./koohai-20240108-01.md:41 | source-report | android-webview | 作者步骤，没有本次连接记录 |
| C2 | “最外层的比如 andorid.webkit.webview 有这个标志”，工具是 `android / sdk/tools/bin/ uiautomatorviewer.bat`。 | s1 ./koohai-20240108-01.md:48-50 | source-report | android-webview | 类名按原文拼写，没有控件树 |
| C3 | “如果没有魔改系统可以hook试试”，点名的方法是 `setWebContentsDebuggingEnabled`。 | s1 ./koohai-20240108-01.md:59-68 | source-report | android-webview | 没有给出 hook 脚本 |

<a id="decision-flow"></a>
## 源码里强制打开

作者把改动放在 `frameworks/base/core/java/android/webkit/WebView.java`。静态方法里把参数改成 true，再让各个构造调用一次。编译前要 `make update-api`。参数保持 false 时，作者说看不到 inspect 里的那一页。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 路径是 “pos:/home/xx/bin/aosp/frameworks/base/core/java/android/webkit/WebView.java”，编译前写着 “make  update-api”。 | s1 ./koohai-20240108-01.md:76-78 | source-report | android-webview | 本地路径，没有 AOSP 标签 |
| C5 | “一共约7个构造 每个都加一下”。 | s1 ./koohai-20240108-01.md:94 | source-report | android-webview | 没有逐个对照这 7 处 |
| C6 | 静态方法里写了 “enabled=true;”。 | s1 ./koohai-20240108-01.md:103 | source-report | android-webview | 只看到作者插入的赋值 |
| C7 | 如果是 false，就看不到上图的页面。 | s1 ./koohai-20240108-01.md:73 | source-report | android-webview | 上图不在正文里，不能当通过条件 |

## 验证与限制

文末从过时构造贴到带 `javaScriptInterfaces` 的构造，中间夹着“原创凑字数”，没有逐行差分。没有目标包名、系统版本和失败后的回退。魔改系统只被写成“先不要 hook”，不是失败出口。因此不建流程。
