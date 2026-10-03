---
schema_version: 2
id: ruyi-20260415-action-visual-reference
document_type: reference
original_date: '2026-04-15'
archived_date: '2026-10-02'
scope:
  targets: [ruyipage]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ruyi-20260415-01.md#自动化过检测web自动化鼠标行为可视化分析"
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只保留鼠标可视化开关、显示项和动作名。不把「无法被检测」或「过一切检测」当成检测结论。
relations:
  - type: derived_from
    target: "./ruyi-20260415-01.md#自动化过检测web自动化鼠标行为可视化分析"
tags: [ruyipage, action-visual, source-report]
---

# ruyiPage 鼠标可视化调试面

这篇卡只回答：ruyiPage 的鼠标调试开关打开后显示什么、覆盖哪些动作。不回答检测是否能被绕过。

<a id="interfaces"></a>
## 调试开关

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 开关写成 action_visual=True | s1，源文件第 58 行 | source-report | ruyiPage 的鼠标调试模式 | 没有轨迹算法 |
| C2 | 显示包含 BiDi 鼠标移动轨迹可视化，同一行还写点击高亮、当前鼠标坐标和当前点击目标元素高亮 | s1，源文件第 59 行 | source-report | 开启该模式之后 | 没有坐标从哪读来 |
| C3 | 动作名从 page.actions.move_to() 起，同一行覆盖 move、human_move、click、drag、ele.click.by_js 和 by_js=True 的输入定位 | s1，源文件第 60 行 | source-report | 来源列出的鼠标动作 | 没有逐个参数 |
| C4 | 用户鼠标接入不影响，只会显示脚本内鼠标行为轨迹 | s1，源文件第 61 行 | source-report | 脚本指针与用户指针同时存在时 | 没有区分方法 |
| C5 | 示例调用是 enable_action_visual(True) | s1，源文件第 67 行 | source-report | FirefoxOptions | 同句的 headless(False) 不是这个开关的失败分支 |

## 验证与限制

`ruyipage`、`firefox`、`bidi` 的 interfaces 查询没有命中。采集器稳定性卡讲的是崩溃和内存，不是这个调试面。安装命令、仓库地址，以及「过一切检测」「无检测点」都不在本卡。没有验收步骤，也没有失败出口。
