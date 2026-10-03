---
schema_version: 2
id: web-khbox-arraylike-media-stubs
document_type: reference
original_date: '2026-03-13'
archived_date: '2026-10-02'
scope:
  targets:
    - khbox
  client: node
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./koohai-20260313-01.md#近期更新"
    basis: source-report
  - id: s2
    ref: "./koohai-20260313-01.md#botsannysoftcom-的fingerprint"
    basis: source-report
  - id: s3
    ref: "./koohai-20260313-01.md#正文"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留来源贴出的类名名单、initialize 调用和 canPlayType 函数名。filteredConfig、mediaCapsData、ERROR 都没有定义。未替换 Node，未运行 main_test.js。
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2, s3]
    basis: source-report
    limits: onload 提前调用只针对作者所说的 sannysoft 图片检测。检测函数未完整贴出，data-URL 不收录。作者写明 demo 未测试结果是否可用。
relations:
  - type: derived_from
    target: "./koohai-20260313-01.md#近期更新"
tags:
  - khbox
  - source-report
---

# khbox 1.2 里点名的数组型类和媒体能力桩

这张卡只回答：2026-03-13 这篇 khbox 更新把哪些类名传进 `addon.initialize`，音视频桩叫什么，以及作者说 sannysoft 图片检测要在设置 src 时调用 onload。它不提供某数站点的加密，也不提供已经通过检测的结果。

`kb_catalog.py query` 里 target `khbox` 的 parameters、risk-control、interfaces、decision-flow、validation 均为 0。`bot.sannysoft.com` 与 `browserleaks` 的 parameters、risk-control 也是 0。没有可并入的同目标同模块卡片。

<a id="parameters"></a>
## 初始化名单和媒体返回桩

来源说 C 层默认已经有一些 array-like 类，初始化时再把名单传进去，避免遗漏。音视频段同时给出了 video 元素桩和 media 元素桩，按类型字符串的子串选择 `mediaCapsData` 里的值。缺省词出现了 `probably` 和 `maybe`，对不上则返回空串。本卡不逐项抄分支，也不抄图片 data-URL。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 类名变量原文含 arrayLikeClasses，名单原文含 PluginArray、MimeTypeArray、Plugin，调用原文是 addon.initialize(filteredConfig, arrayLikeClasses) | s1，近期更新 | source-report | 这篇所说的 khbox 初始化 | 没列出 C 层已有默认值。filteredConfig 未见 |
| C2 | 两个桩的函数名原文是 HTMLVideoElement_canPlayType 和 HTMLMediaElement_canPlayType | s1，近期更新 | source-report | 同一段音视频桩 | 返回值依赖未见定义的 mediaCapsData。本次未逐项复跑子串 |
| C3 | 构建标签原文是编译的版本是v25.2.2-pre ，建议原文含建议本地用24版本+ | s1，近期更新 | source-report | 作者自己的 Node 构建 | 不写入 scope.version。未核对这个二进制 |

<a id="risk-control"></a>
## 图片 onload 和作者点名的测试页

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 图片检测的处理原文是就是在src设置的时候 就调用onload | s1，近期更新 | source-report | 作者所说的 sannysoft 图片检测 | 没有给出被改的宿主函数 |
| C5 | 紧接着的原因原文是避免onload无法被触发的情况。 | s1，近期更新 | source-report | 同上 | 只解释作者为什么要提前调用 |
| C6 | 测试页原文含 https://browserleaks.com/ 和 https://bot.sannysoft.com/ | s1，近期更新 | source-report | 作者说源码里测过的页面 | 没有页面版本、脚本哈希或通过记录 |
| C7 | 开篇边界原文是未测试结果是否可用，仅出结果 | s3，正文 | source-report | 这篇的两个站点 demo | 后文的跑通和没有 bug 都不抬高依据 |
| C8 | demo 入口原文是运行main_test.js （这个只针对测试demo文件夹） | s2，fingerprint 一节 | source-report | 作者的 demo 文件夹 | 日志只写「如图」，图不在正文 |

## 验证与限制

某数一节只写把获取环境脚本复制到网站，以及我删掉了cookie相关的内容，然后直接run。没有站点名、脚本或字段，本卡不收录任何 cookie 值，也不把这段当成环境流程。

加密被写成还没看。上半部分 JS 没有贴出。给 AI 一份浏览器调用日志再让它自己对比，只有一句话，没有验收和失败出口，不建流程。

目前测试下来，node层基本没有什么bug了。这是作者自述。本次没有运行证据。
