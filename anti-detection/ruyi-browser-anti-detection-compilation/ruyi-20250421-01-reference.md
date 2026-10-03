---
schema_version: 2
id: ruyi-blink-embed-surface
document_type: reference
original_date: '2025-04-21'
archived_date: '2026-10-02'
scope:
  targets: [blink]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ruyi-20250421-01.md#chromium指纹浏览器开发教程之blink渲染引擎"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只整理这篇未标注版本的章节里写明的进程边界、Content 公共 API 和点名目录。图 2-12 至 2-16 不在正文。没有本地树、编译或运行对照，也不把“指纹修改集中于 Blink 目录”写成具体文件或符号。
relations:
  - type: derived_from
    target: "./ruyi-20250421-01.md#chromium指纹浏览器开发教程之blink渲染引擎"
  - type: derived_from
    target: "./ruyi-20250421-01.md#231-blink-运行方式"
  - type: derived_from
    target: "./ruyi-20250421-01.md#232-blink-模块"
  - type: derived_from
    target: "./ruyi-20250421-01.md#233-blink-目录结构"
  - type: derived_from
    target: "./ruyi-20250421-01.md#234-blink-线程创建"
tags: [blink, chromium, content-api, source-report]
---

# Blink 嵌入 Content 的公共面

这篇参考只回答一个检索问题：如意私塾 2025-04-21 的章节把 Blink 放在哪个进程里、通过哪组公共 API 嵌入、点了哪些目录，以及渲染线程之间怎么通信。它不覆盖 Canvas、WebGL 或其他指纹补丁文章里的具体 `.cc` 路径，也不核对任何 Chromium 版本。

<a id="interfaces"></a>
## 接口

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 每一个  Renderer  进程当中都会包含一个  Blink  实例 | s1 第 42 行 | source-report | 本篇对多进程的叙述 | 未写 Renderer 数量或版本 |
| C2 | 进程是沙盒化的，因此  Renderer  进程需要向  Browser  进程请求系统调用 | s1 第 43 行 | source-report | 本篇的 Renderer/Browser 边界 | 没有 Mojo 接口名 |
| C3 | 这些跨进程请求通信就是通过  Mojo | s1 第 43 行 | source-report | 同上 | 图 2-12 不在正文 |
| C4 | 还存在大量  IPC  通信代码 | s1 第 44 行 | source-report | 本篇对遗留 IPC 的一句说明 | 没有文件列表 |
| C5 | Mojo  通信所取代了。 | s1 第 45 行 | source-report | 作者对 IPC 与 Mojo 关系的判断 | 未给替换完成度 |
| C6 | 可以被多个不同平台嵌入使用，而使用的途径就是通过  content | s1 第 64 行 | source-report | 嵌入途径 | 下一行才写完“公用 API” |
| C7 | /  /content/public APIs  是暴露给  Content  模块嵌入者的  API | s1 第 70 行 | source-report | Content 嵌入者可见的 API 层 | 路径写法带空格，不是已核对的 checkout 路径 |
| C8 | src  目录下的  third_party/blink | s1 第 103 行 | source-report | 本篇给出的代码位置 | 无 commit |
| C9 | 后续的指纹修改也集中于  Blink  目录之中 | s1 第 104 行 | source-report | 作者对后续章节的范围声明 | 本篇没有修改点 |
| C10 | public/common | s1 第 115 行 | source-report | 公共 API 的第一部分 | 只说明渲染器与浏览器都可引用 |
| C11 | 核心接口是  Platform  ，它是  Blink  获取其他接口的纯虚拟接口 | s1 第 119 行 | source-report | public/platform | 未列其他接口 |
| C12 | blink/renderer/platform/exported | s1 第 120 行 | source-report | Platform 的实现目录 | 无符号 |
| C13 | 中心接口是  WebView | s1 第 123 行 | source-report | public/web | 未展开 DOM 接口 |
| C14 | blink/renderer/{core,modules}/exported | s1 第 124 行 | source-report | public/web 的实现目录 | 花括号是原文，不是已展开的两个路径证明 |
| C15 | 公共  API  不使用  STL | s1 第 126 行 | source-report | 公共 API 的类型约束 | 原文把 std 与 pair 拆到相邻行，这里不拼回 std::pair |
| C16 | 大多数情况下  API  使用  WTF | s1 第 127 行 | source-report | 同上 | 未列容器类型 |
| C17 | platform/scheduler  实现了用于管理所有  Blink  任务的任务调度器 | s1 第 134 行 | source-report | renderer/platform | 无类名 |
| C18 | core/  ：实现了  Web  平台规范和接口的核心功能 | s1 第 136 行 | source-report | renderer/core | 原文说与 DOM 紧密耦合，依赖图不在正文 |
| C19 | modules/crypto  实现了 | s1 第 140 行 | source-report | renderer/modules 的例子 | 下一行才是 WebCrypto API |
| C20 | WebCrypto API | s1 第 141 行 | source-report | modules/crypto 的例子 | 没有算法或调用点 |
| C21 | bindings/  ：包含了大量使用  V8 API  的文件 | s1 第 146 行 | source-report | renderer/bindings | 原文称与其他代码分开是因为复杂且涉及安全性 |
| C22 | controller/  ：  这是一组使用  core/  和  modules/  的高级库 | s1 第 143 行 | source-report | renderer/controller | 原文说 Web 平台功能不应放这里 |
| C23 | extensions/  ：包含了嵌入器特定的、不会暴露给  Web  的  API | s1 第 149 行 | source-report | renderer/extensions | 无具体 API |
| C24 | build/  ：包含了一些构建  Blink  引擎的脚本。 | s1 第 152 行 | source-report | renderer/build | 无脚本名 |
| C25 | Blink  只有一个主线程，但是有多个工作线程和大量的内部线程 | s1 第 167 行 | source-report | 渲染进程内线程 | 无线程名 |
| C26 | 主线程负责执行  JavaScript  代码（除了在  Web Workers | s1 第 169 行 | source-report | 主线程职责 | 句子在下一行继续 DOM、CSS 和布局 |
| C27 | 用于运行  Web Workers | s1 第 173 行 | source-report | 工作线程 | 同一句把 Service Worker 拆开书写，不把拆词当成标识符 |
| C28 | 用于处理诸如  Web  Audio  、数据库、垃圾回收等任务 | s1 第 176 行 | source-report | Blink 与 V8 的内部线程 | 没有线程创建点 |
| C29 | 通信通常通过消息传递来实现，而不是使用共享内存 | s1 第 178 行 | source-report | 本篇描述的线程间通信 | 图 2-16 不在正文；Erlang 只是类比 |

## 验证与限制

V8 在本篇是 Blink 送去执行 JavaScript 的引擎，Skia 是绘制时调用的图形库；二者没有头文件或函数名。跨进程网络拉取被写成“实用进程 Service”，没有进程类名。`Blink  目录下存在着  7` 个文件夹这句话指向缺席的图 2-14，正文另行列出的是 `public` 与 Renderer 子目录，不能把这两套名单合成一张已核对的目录树。

已有 `chromium-startup-validation` 与 `chromium-startup-cookie` 参考卡的 interfaces 模块分别是启动期 JWT 校验和 CookieManager，不覆盖本表。指纹编译系列里的补丁文会点到 `third_party/blink/renderer/...` 下的具体文件，那些路径不属于本模块。
