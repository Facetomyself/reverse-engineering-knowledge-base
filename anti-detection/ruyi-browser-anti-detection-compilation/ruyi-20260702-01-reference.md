---
schema_version: 2
id: ruyi-20260702-firefox-taskbar-window-badge
document_type: reference
original_date: '2026-07-02'
archived_date: '2026-10-02'
scope:
  targets: [firefox-taskbar-window-badge]
  client: firefox
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260702-01.md#核心结论
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留来源对 overlay 位置、SVG 解码和 canvas PNG 的取舍。来源写的验证通过和测试名保持 source-report，本次没有构建或运行。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留编号单调性、跳过的窗口、group id 形态和 99 显示上限。不复制图标像素或测试桩。
relations:
  - type: derived_from
    target: ./ruyi-20260702-01.md#核心结论
tags: [firefox, taskbar, source-report]
---

# Firefox 任务栏窗口编号怎么拆开

这篇卡检索的是：Windows 上多个普通 Firefox 窗口要各自占一个底部带编号的任务栏图标时，来源放弃了哪条 API，以及编号和 group id 按什么规则走。不提供可直接打进源码树的补丁。

<a id="decision-flow"></a>
## 图标路径

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 系统固定了 overlay 位置：Windows 的 taskbar overlay icon 位置由系统固定，Firefox 侧不能把 overlay 从右下角移动到底部居中。 | s1，源文件第 52 行 | source-report | Windows 任务栏 overlay | 不是通用窗口装饰接口 |
| C2 | 先拆任务栏身份：给每个浏览器窗口设置独立 AUMID，让任务栏拆成多个 Firefox 图标。 | s1，源文件第 56 行 | source-report | 普通 Firefox 窗口 | 正文落到 setGroupIdForWindow，没有另一套未写出的调用 |
| C3 | data SVG 丢了原图标：结果任务栏里只显示数字，Firefox 原始图标消失。 | s1，源文件第 341 行 | source-report | 内嵌 chrome://branding 的 data SVG | 随后的 data URL SVG 也没让数字稳定出现 |
| C4 | 原因被写成解码吃不到内部图片：内部引用的  ` chrome://branding/...  ` 图片没有可靠进入最终 Windows icon。 | s1，源文件第 343 行 | source-report | 同一 SVG 尝试 | 不是对所有 SVG 的结论 |
| C5 | 最终载体：最终使用 canvas 直接生成自包含 PNG。这是目前验证通过的方式： | s1，源文件第 347 行 | source-report | 来源描述的 64 像素合成图 | 验证通过只是来源自述 |
| C6 | 交给窗口图标而不是 overlay：拿到的是已经合成完成的 PNG，不需要 Windows 或 image decoder 再解析 SVG 内部依赖。 | s1，源文件第 351 行 | source-report | setWindowIcon 的 small 与 big 用同一张图 | 不包含该接口的实现 |

<a id="parameters"></a>
## 编号与分组

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | 关闭不回收编号：新窗口编号只递增，不因为关闭旧窗口而重新编号。 | s1，源文件第 45 行 | source-report | 普通 browser window | 来源举例是关掉 2 之后新窗口为 4 |
| C8 | 跳过非普通窗口：跳过 popup 窗口和 taskbar tab 窗口。 | s1，源文件第 48 行 | source-report | 无普通 toolbar 的 popup，以及带 taskbartab 的窗口 | 已关闭窗口另被过滤 |
| C9 | group id 后缀使用 `${groupId}.window-${number}` | s1，源文件第 248 行 | source-report | 每个被编号的窗口 | 普通窗口与隐私窗口的前缀不同 |
| C10 | 隐私窗口走另一组：taskbar.defaultPrivateGroupId | s1，源文件第 246 行 | source-report | PrivateBrowsingUtils 判定为隐私的窗口 | 普通窗口用 defaultGroupId，本卡不展开组名常量从哪来 |
| C11 | 超过 99 的显示合并：因此 100、101、102 等窗口共用同一个  ` 99+  ` 图标。 | s1，源文件第 373 行 | source-report | 编号大于 99 | 共用的是显示图标，不代表任务栏按钮被系统合并 |

## 验证与限制

来源点名 test_window_numbers_are_monotonic，并写跳过非 browser window 时不为这些窗口设置 group id。本次只读到说明，没有构建 Firefox，也没有跑 browser test。Chromium 任务栏数字徽标是另一客户端的 overlay 归档，scope target 为 unknown，不能承接这篇。查询 firefox、gecko、firefox-taskbar-window-badge 的 decision-flow 与 parameters 都没有命中。引言提到排查要点，正文没有失败时停在哪里，所以不建流程。文末广告，以及来源明确排除的 domtrace 和时区改动，都不属于本功能。
