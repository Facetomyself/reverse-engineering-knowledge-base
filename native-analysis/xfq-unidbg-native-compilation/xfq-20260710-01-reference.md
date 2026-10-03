---
schema_version: 2
id: xfqtrace-gadget-injection-routes
document_type: reference
original_date: '2026-07-10'
archived_date: '2026-10-02'
scope:
  targets:
    - xfqtrace
    - com.xiaofeng.qbdi
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./xfq-20260710-01.md#gadget注入xfqtrace实现trace
    basis: source-report
modules:
  - name: interfaces
    anchor: routes
    sources: [s1]
    basis: source-report
    limits: 只保留两条 gadget 的版本、脚本名和 frida 连接句。辅助脚本、图和 gadget_trace.js 正文不在本篇。设备序列号不收录。
  - name: decision-flow
    anchor: choice
    sources: [s1]
    basis: source-report
    limits: 「跟 server 没啥区别」和「更推荐 xfinject」都是作者判断。xfinject 的步骤不在本篇。
  - name: validation
    anchor: boundaries
    sources: [s1]
    basis: source-report
    limits: 开屏卡住只被用来表示 zygisk 模块生效。trace 是否真的写出，正文只写「正常触发」。本轮未连接设备。
relations:
  - type: derived_from
    target: ./xfq-20260710-01.md#gadget注入xfqtrace实现trace
tags:
  - xfqtrace
  - frida-gadget
  - source-report
---

# xfqtrace 的两条 gadget 连接，以及作者为什么仍推荐 xfinject

这张卡回答：要把 `examples/com.xiaofeng.qbdi/gadget_trace.js` 接到 Gadget 上时，来源写了哪两个构建，以及作者实际推荐哪条路。它不替代 gadget 讲义，也不收录 `gadget_trace.js` 的脚本正文。来源是 [gadget注入xfqtrace实现trace](./xfq-20260710-01.md#gadget注入xfqtrace实现trace)。

<a id="choice"></a>
## 先选注入方式

作者写明更推荐 xfinject，认为没有必要用 gadget。gadget 只是因为有人问才写。后文又说实际操作跟 server 没区别。因此本篇的 gadget 步骤是对照，不是作者的默认路线。xfinject 本身的命令不在这里。

<a id="routes"></a>
## 两条 gadget

rusda 这条是 `rusda-gadget-16.2.1`。来源指向 `https://github.com/taisuii/rusda` 的 16.2.1 `gadget.so`。辅助脚本名是 `inject_rusda_gadget.py`：把 xfqtrace 和 rusda-gadget 的 so 推到合适位置，再用 xfinject 把 gadget 注入 app，然后卡住等 frida-cli。连接句是 `frida -H 127.0.0.1:14725 -n Gadget -l examples/com.xiaofeng.qbdi/gadget_trace.js`。作者说细节看图，图不在正文。

小佳这条是 `gadget-16.5.7`。先装对应 zygisk 模块，在小工具里启用目标 app 并配置 config。so 要推到应用的 files 使用路径；正文写的是先推到 `/data/local/tmp/libxfqtrace.so`，再复制到 `/data/data/com.xiaofeng.qbdi/libxfqtrace.so`，并 `chmod 755`，失败也继续 `restorecon`。端口是 `forward tcp:14725 tcp:14725`。frida 连接句与 rusda 相同。来源里的 `adb -s` 序列号不写入本卡。

<a id="boundaries"></a>
## 验证与限制

zygisk 是否生效，作者只给了一个现象：手动打开 app，确认卡在开屏。之后写「后面就跟 server 差不多」，最后是「正常触发 trace 即可」。没有失败时怎么退、端口占用怎么办，也没有 trace 文件的验收。`inject_rusda_gadget.py` 和 `gadget_trace.js` 的正文都不在本篇。同名日期的 frida-gadget 讲义是另一篇，目标与模块都没有落成这张卡所查询的 xfqtrace 条目。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 作者 `推荐xfinject注入`，并写 gadget `压根没有必要`；操作上 `跟server没啥区别`。 | s1 第 38–38 行 | source-report | 本篇的路线选择 | xfinject 步骤不在本篇 |
| C2 | rusda 构建是 `rusda-gadget-16.2.1`，下载页是 `https://github.com/taisuii/rusda`。 | s1 第 41–41 行 | source-report | 作者点名的 16.2.1 | 发布文件名以正文的 gadget.so 为准 |
| C3 | `inject_rusda_gadget.py` 负责推 so、用 xfinject 注入，并卡住等 frida-cli。 | s1 第 43 行 | source-report | 这个辅助脚本的职责 | 脚本正文不在本篇 |
| C4 | 连接命令是 `frida -H 127.0.0.1:14725 -n Gadget -l examples/com.xiaofeng.qbdi/gadget_trace.js`。 | s1 第 44 行 | source-report | 两条 gadget 的 frida-cli | 主机与端口来自该句 |
| C5 | 小佳构建是 `gadget-16.5.7`，走 zygisk 模块和小工具里的 app config。 | s1 第 46–46 行 | source-report | 这条付费 gadget 的启用方式 | 模块包本身不在正文 |
| C6 | 开屏卡住被当成 `zygisk模块生效`。 | s1 第 47 行 | source-report | 小佳这条的现象 | 不是 trace 结果验收 |
| C7 | so 落到 `libxfqtrace.so`，权限写了 `chmod 755`，并带 `restorecon`。 | s1 第 51–51 行 | source-report | `com.xiaofeng.qbdi` 这个包路径 | 不收录 adb 序列号 |
| C8 | 端口转发是 `forward tcp:14725 tcp:14725`，之后 `正常触发trace即可`。 | s1 第 54、57 行 | source-report | 小佳这条的收尾 | 没有失败出口 |
