---
schema_version: 2
id: ruyi-chromium-32bit-fiber-reference
document_type: reference
original_date: '2025-10-28'
archived_date: '2026-10-02'
scope:
  targets: [chromium-32bit-fiber]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20251028-01.md#chromium内核教程--fiber用户态轻量级线程
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只记录来源粘连代码里的 Win32 Fiber 调用名。没有 Chromium 修订号、源文件路径或可编译片段。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 栈大小只保留来源写出的 4MiB 常量与作者对 1MB、8MB 的对比，未对照当前 Windows 或 Chromium 默认栈。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 32 位才包裹主入口是作者对这段代码的解释。文末 Canvas 示例不是指纹算法，失败 return 只出现在该示例。
relations:
  - type: derived_from
    target: ./ruyi-20251028-01.md#chromium内核教程--fiber用户态轻量级线程
tags: [chromium, fiber, win32, source-report]
---

# Chromium 32 位入口 Fiber 栈扩展参考

这张卡只回答一个检索问题：来源把哪一段 Win32 Fiber 调用说成 32 位 Chromium 主入口的大栈包装。它不提供可编译补丁，也不把文末示例当成 Canvas 指纹实现。

<a id="interfaces"></a>
## 入口调用

来源把这段调度放在 `ARCH_CPU_32_BITS` 下的 `wWinMain`。线程还不是 Fiber 时，先 `ConvertThreadToFiberEx`，再用 `CreateFiberEx` 把 `FiberBinder` 跑在新 Fiber 上，然后 `SwitchToFiber`。回来之后来源写了 `DeleteFiber` 和 `ConvertFiberToThread`，并把 `fiber_state.fiber_result` 返回。

`FiberBinder` 用参数里的 `FiberState` 再调用 `wWinMain`，然后 `SwitchToFiber` 回原来的 Fiber。归档把这些调用挤在少数物理行里，中间有省略号，不能还原完整控制流。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 32 位分支先判断 `IsThreadAFiber()` | s1 `ruyi-20251028-01.md:47`，quote: `IsThreadAFiber()` | source-report | chromium-32bit-fiber | 无修订号 |
| C2 | 转换 API 是 `ConvertThreadToFiberEx` | s1 `ruyi-20251028-01.md:47`，quote: `ConvertThreadToFiberEx` | source-report | chromium-32bit-fiber | 标志位见参数节 |
| C3 | 新 Fiber 的例程名是 `CreateFiberEx` 的回调 | s1 `ruyi-20251028-01.md:47`，quote: `CreateFiberEx` | source-report | chromium-32bit-fiber | 归档行含省略号 |
| C4 | 回调里写回 `fiber_state->fiber_result` 再切回 | s1 `ruyi-20251028-01.md:55`，quote: `fiber_state->fiber_result` | source-report | chromium-32bit-fiber | 未还原结构体定义 |

<a id="parameters"></a>
## 栈与标志

来源把栈常量写成 `kStackSize`，注释是 `// 4 MiB`，并在后文再次把 4MB 说成 32 位大栈。`CreateFiberEx` 与 `ConvertThreadToFiberEx` 都带 `FIBER_FLAG_FLOAT_SWITCH`。提交大小在片段里是 0，保留大小指向该常量。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 栈注释为 `// 4 MiB` | s1 `ruyi-20251028-01.md:47`，quote: `// 4 MiB` | source-report | chromium-32bit-fiber | 未核对头文件 |
| C6 | 切换标志是 `FIBER_FLAG_FLOAT_SWITCH` | s1 `ruyi-20251028-01.md:47`，quote: `FIBER_FLAG_FLOAT_SWITCH` | source-report | chromium-32bit-fiber | 未解释标志语义 |

<a id="decision-flow"></a>
## 何时走 Fiber

来源的对比是：线程由内核调度，Fiber 由用户态手动切换。作者解释 32 位主线程栈大约只有 `~1MB`，V8 递归会耗栈，所以用 Fiber 扩栈；64 位默认 `8MB` 就不用。这是作者对动机的陈述，不是一份已核对的平台栈合同。

后文示例用同一个 4MB `CreateFiberEx` “模拟 JS 复杂 Canvas 绘制”。示例只填充整数 buffer 并打印长度；创建失败时打印 `CreateFiberEx failed:` 和 `GetLastError()` 后返回。它不产生 Canvas 指纹，也不能当成入口 Fiber 的失败合同。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | 作者称 64 位默认 8MB 栈所以不用 Fiber | s1 `ruyi-20251028-01.md:77`，quote: `默认 8MB 栈已经够大` | source-report | chromium-32bit-fiber | 作者陈述 |
| C8 | 作者称 32 位栈大约只有 ~1MB | s1 `ruyi-20251028-01.md:79`，quote: `32 位栈本来就只有 ~1MB` | source-report | chromium-32bit-fiber | 作者陈述 |
| C9 | Canvas 字样只是示例框架 | s1 `ruyi-20251028-01.md:94`，quote: `模拟 JS 复杂 Canvas 绘制` | source-report | chromium-32bit-fiber | 不是指纹算法 |
| C10 | 示例失败分支打印创建失败 | s1 `ruyi-20251028-01.md:109`，quote: `CreateFiberEx failed:` | source-report | 仅示例 main | 不代表 Chromium 入口 |

## 验证与限制

近邻 `chromium-startup-validation` 与 `chromium-startup-cookie` 分别是 JWT switch 和 CookieManager，没有 Fiber 入口。本卡不合并进那两张卡。

来源没有 Chromium 版本、`wWinMain` 所在文件、省略号所代表的分支，也没有构建或运行记录。不能据此写流程卡。
