---
schema_version: 2
id: unidbg-libc-hook-selection-reference
document_type: reference
original_date: '2026-04-24'
archived_date: '2026-07-13'
scope:
  targets:
    - unidbg
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260424-01.md#库函数和系统调用的关系"
    basis: source-report
  - id: s2
    ref: "./paopao-20260424-01.md#选型速查"
    basis: source-report
  - id: s3
    ref: "./paopao-20260424-01.md#三个容易踩的坑"
    basis: source-report
  - id: s4
    ref: "./paopao-20260424-01.md#systempropertyhookunidbg-的快捷通道"
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s2]
    basis: source-report
    limits: 框架边界和 99% 是作者归纳。没有 HookZz、xHook、Whale 或 Unidbg 的版本，也没有运行。
  - name: parameters
    anchor: parameters
    sources: [s3, s4]
    basis: source-report
    limits: 只保留属性 hook 打在哪两个符号、注册顺序和 clock id 7。不收录 setProperty 示例里的 build fingerprint 原值。
relations:
  - type: derived_from
    target: "./paopao-20260424-01.md#选型速查"
tags:
  - unidbg
  - libc-hook
  - source-report
---

# Unidbg 库函数层：框架边界和系统属性注册

这张卡只回答：libc hook 相对 syscall 的边界、三个框架各拦哪里，以及 SystemPropertyHook 要打在哪一层、什么时候注册。不收录 openat、free 或 clock_gettime 的实现。第九篇已经写过优先走库函数层；这里只保留第十篇新增的选型事实。

<a id="decision-flow"></a>
## 四类函数和三个框架

对照表把 libc hook 做不到的唯一情况写成：

> 拦截 SO 内联的 SVC（不走 libc）

包装型函数（open、read、mmap 这一类）通常交给已有 SyscallHandler。例外是：

> 当默认 syscall 行为不对（语义偏差，第九篇类型三）

xHook 的限制是：

> 只能拦截  ** 跨模块调用  **

它改的是调用方的 PLT/GOT，SO 内部调用和 libc 内部再调用都拦不到，而且要 refresh。HookZz 是改被调用函数入口，wrap 保留原函数，replace 跳过原函数。Whale 被写成更适合内存函数：

> 能稳定 hook  ` free  ` /  ` malloc  ` /  ` munmap  `

选型表把系统属性单独指开：

> SystemPropertyHook

加壳 SO 的失败原文是：

> IllegalStateException: free unknown ptr

作者的取舍是先用 Whale 把 free 变成直接返回，并称：

> 99% 的加壳 SO 用方案 A 都能搞定

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 内联 SVC 不经过 libc，库函数层拦不到 | s1，对照表 | source-report | 该篇描述的调用栈 | 无样本比例 |
| C2 | 包装型函数只在语义偏差时才上抬到 libc | s1，类型一 | source-report | 第九篇类型三 | 无新测量 |
| C3 | xHook 只拦跨模块 PLT | s2，xHook 段 | source-report | xHook | 未运行 refresh |
| C4 | Whale 面向 free、malloc、munmap | s2，Whale 段 | source-report | 作者对比的 trampoline 问题 | “稳定”未复现 |
| C5 | 系统属性不用这三个框架，改用内置 hook | s2，选型表 | source-report | __system_property_get | 见参数节 |
| C12 | 加壳场景的失败形态是 free unknown ptr | s2，内存管理段 | source-report | 来源举的加固加载 | 示例地址不收录 |
| C13 | 作者建议先空实现 free | s2，方案取舍 | source-report | 作者说的加壳 SO | 99% 未测量 |

<a id="parameters"></a>
## 系统属性与 clock id 7

来源写 Unidbg 默认机型是：

> 默认 “google_sdk_gphone”

这只说明默认表会暴露模拟器。同篇 setProperty 示例里的 build fingerprint 原值不进入本卡。

SystemPropertyHook 不是去 hook 上层 get。正文写它打在：

> __system_property_find

> __system_property_read

三个注册坑：

> 忘记调用 addHookListener

> 可能在  ` JNI_OnLoad  ` 阶段就被调用

> xHook 拦不到这一层

来源给出的顺序是先注册并 setProperty，再 loadLibrary，再 callJNI_OnLoad。哪些版本必须 addHookListener 没有写出。

clock_gettime 的例子把报错写成：

> not supported clock_id 7

替换函数只处理这一支：

> 我们只处理 BOOTTIME, 其它 clock_id 走原函数

固定加 6 小时是作者假设，与第九篇重复，这里不再展开算法。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 默认 model 被写成模拟器机型字符串 | s4，默认行为段 | source-report | 来源描述的默认表 | 不是设备指纹原值 |
| C7 | hook 打在 __system_property_find | s4，快捷通道 | source-report | 该篇描述的 Bionic 两步读取 | 未对源码版本 |
| C8 | 同时打在 __system_property_read | s4，快捷通道 | source-report | 同上 | 未对源码版本 |
| C9 | 有的版本还要 addHookListener | s3，坑 1 | source-report | “某些版本” | 版本未列出 |
| C10 | JNI_OnLoad 可能已经读过属性 | s3，坑 2 | source-report | 注册顺序 | 未对具体 SO |
| C11 | xHook 打上层 get 可能无效 | s3，坑 3 | source-report | 走属性区的读取 | 未复现 |
| C14 | 不支持的时钟被写成 id 7 | s3，实战报错 | source-report | 该篇例子 | 与第九篇重叠 |
| C15 | 只替换 id 7，其余走原函数 | s3，实战代码注释 | source-report | 该篇 replace 草稿 | 未运行 |

## 验证与限制

没有框架版本，也没有本地运行。空 free 的泄漏是否可接受，只保留作者“进程退出”这句，不把它当成通用内存方案。外部库要虚拟模块的 10% 工作量是作者估计，没有单独的接口合同，所以不单列模块。
