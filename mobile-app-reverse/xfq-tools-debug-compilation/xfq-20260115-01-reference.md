---
schema_version: 2
id: xfq-android9-cleartext-egress
document_type: reference
original_date: "2026-01-15"
archived_date: "2026-10-02"
scope:
  targets: [android-cleartext-http]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260115-01.md#正文"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录来源对 usesCleartextTraffic 和 Network Security Configuration 的版本概述。没有样例 manifest，也没有对照平台源码。
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只记录来源写下的进程外出口。广播没有 action，curl 没有读取输出，hook 反射没有试成功。
relations:
  - type: derived_from
    target: "./xfq-20260115-01.md#正文"
tags: [android, cleartext, lsposed]
---

# 安卓明文 HTTP 的版本默认值和进程外出口

这张卡只回答一个检索问题：来源如何用 usesCleartextTraffic 的默认值解释安卓 9 以后的明文 HTTP，以及 LSPosed 插件进程发不出去时改走哪两个进程外入口。证书信任和代理读回不在本卡。

<a id="parameters"></a>
## 明文开关的版本说法

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 安卓 9 之后被写成默认禁止 HTTP 明文。quote: 安卓9之后默认禁止http明文流量 | s1 ./xfq-20260115-01.md:37 | source-report | 来源的开篇判断 | 属性名见 C4 |
| C2 | 安卓 6 被写成引入 usesCleartextTraffic。quote: 引入 usesCleartextTraffic 属性 | s1 ./xfq-20260115-01.md:52 | source-report | 来源的版本表 | 同一段写默认仍允许 HTTP |
| C3 | 安卓 7 被写成引入 Network Security Configuration。quote: 引入 Network Security Configuration | s1 ./xfq-20260115-01.md:55 | source-report | 来源的版本表 | 没有域名列表示例 |
| C4 | 安卓 9 把 usesCleartextTraffic 的默认值写成 false。quote: usesCleartextTraffic 默认值改为 false | s1 ./xfq-20260115-01.md:59 | source-report | 来源的版本表 | 未对照框架源码 |
| C5 | 安卓 10 及以后被写成某些系统 API 完全拒绝 HTTP。quote: 某些系统 API 完全拒绝 HTTP | s1 ./xfq-20260115-01.md:62 | source-report | 来源的版本表 | 没有 API 名单 |

<a id="interfaces"></a>
## 进程外出口

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 失败现场是插件去访问 http://ip:port/ 这种形式。quote: http://ip:port/形式 | s1 ./xfq-20260115-01.md:38 | source-report | 来源自己的插件 | 没有真实主机或报错 |
| C7 | 一条出路是 LSPosed 插件发广播，把 JS 交给 autojs。quote: lsp插件发广播携带js脚本代码给到autojs框架 | s1 ./xfq-20260115-01.md:40 | source-report | 来源给出的进程外方案 | 没有 action 和脚本 |
| C8 | hook 反射改配置被写成没有试成功。quote: 这个我没试成功过 | s1 ./xfq-20260115-01.md:41 | source-report | 来源的否定结果 | 没有钩点 |
| C9 | 另一条是 Runtime.getRuntime().exec。quote: Runtime.getRuntime().exec | s1 ./xfq-20260115-01.md:43 | source-report | 来源贴出的调用 | 没有读取输出 |
| C10 | 参数里有 curl 的 -m 和 5 秒。quote: "-m", "5" | s1 ./xfq-20260115-01.md:46 | source-report | 这一段数组 | url 变量没有定义 |

## 验证与限制

`kb_catalog.py query` 对 android-cleartext-http 的 parameters、interfaces 都是 0。环境搭建参考卡的 validation 是证书和代理，不是这条明文出口。来源没有成功读回，hook 一条明确没试成。本次没有安装插件或执行 curl。
