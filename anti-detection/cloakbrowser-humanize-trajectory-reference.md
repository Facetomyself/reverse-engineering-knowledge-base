---
schema_version: 2
id: anti-detection-cloakbrowser-humanize-trajectory-reference
document_type: reference
original_date: '2026-09-24'
archived_date: '2026-10-03'
scope:
  targets: [cloakbrowser]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./cloakbrowser-humanize-trajectory.md#reference-extraction-199
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 仅整理包装层轨迹计划器的几何与默认可调区间；不是 Chromium 补丁参数，也不证明目标站点接受这些样本。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 点击/滚动/键盘顺序来自来源对包装层的描述；提取模块不含 Playwright 补丁、隔离世界和 CDP 按键旁路。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: chrome.dll 无 humanize 符号、仅开 CDP 不生成轨迹、ElementHandle 绕过补丁，均为来源静态结论；本轮未运行 Playwright 或页面。
relations:
  - type: derived_from
    target: ./cloakbrowser-humanize-trajectory.md#reference-extraction-199
tags: [cloakbrowser, humanize, bezier, mouse-trajectory, playwright, source-report]
---

# CloakBrowser humanize 轨迹计划器参考

用于区分 **包装层鼠标计划器** 与 Chromium/指纹补丁。曲线在官方 Python/JS 包装进程内算完，再交给原始 `mouse.move`。本机 Pro 二进制的定制面不包含这条曲线。

<a id="parameters"></a>
## 计划器参数

Python 入口为 `cloakbrowser/human/mouse.py`，JS 平行实现为 `js/src/human/mouse.ts`。两边都是三次贝塞尔、三次 ease-in-out、法线偏移控制点、中间抖动、burst 停顿和概率过冲。

| 字段 | 来源 default | careful 差异 | 限制 |
|---|---|---|---|
| 步数 | `round(距离 / 8)` 再夹到 25–80，采样个数 = 步数 + 1 | 相同 | 距离 &lt; 1px 不采样。 |
| 控制点 | 线段 25%/75%，法线 `uniform(-0.3, 0.3) * 距离` | 相同 | 不是页面内计算。 |
| ease-in-out | `t&lt;0.5` 为 `4t³`，否则 `1-(-2t+2)³/2` | 相同 | 只描述采样参数，不是浏览器物理。 |
| wobble | `sin(π * progress) * 1.5` | 相同 | 中间最大、两端为 0。 |
| burst | 每 3–5 点停 8–18 ms，末点不停 | pause 12–25 ms | 执行等待在样本 `delay_ms`。 |
| overshoot | 概率 0.15，冲出 3–6 px，停 30–70 ms，拉回 ±2 px | 概率 0.10 | 逻辑光标写成目标点，不是最后一个采样。 |

输入框瞄准点取宽度 5%–30%、高度 30%–70%；按钮两类取 35%–65%。瞄准/按住时长分输入框与按钮两套区间。单次调用可用 `human_config` 覆盖字段；预设只有 `default` 与 `careful`。

滚动按加速、巡航、减速三段取增量后再拆成 20–40 的小滚轮事件。键盘间隔为 `typing_delay ± typing_delay_spread`，字母数字可邻键误触后 Backspace。提取模块把非 ASCII 记为 `insert_text`，不含上游 Shift 符号的 CDP 旁路。

<a id="decision-flow"></a>
## 包装层点击顺序

`humanize=True` 是包装开关：`launch()` 解析 `HumanConfig` → `patch_browser` → 包住 `new_context` / `new_page` → `patch_page` 替换 `click` / `mouse.*` / `keyboard.*`。

来源所述 `page.click(selector)`：

1. `careful` 可先做一小段 idle 漂移；`default` 关闭。
2. 元素不在视口 20%–80% 带内时，先移到视口中部再滚轮送入；已可见且该方向顶到头则不再空转滚动。
3. 在元素盒内取点。
4. `human_move` 画到该点。
5. 隔离世界做 pointer-events 命中检查；`force=True` 跳过。
6. 瞄准停顿后 `mouse.down` / `mouse.up`。

每个 page 一份光标状态：第一次动作先放到地址栏一带，之后从逻辑光标出发。几何读取走 CDP 隔离世界，路径计算不在页面里。

公开计划函数（主仓 `tools/cloakbrowser_human`）只产出样本：`plan_mouse_path`、`plan_click`、`plan_scroll`、`plan_scroll_into_view`、`plan_typing`、`plan_idle` 等。不挂页面、不发 CDP。

<a id="validation"></a>
## 边界

| 观察 | 来源允许的最小结论 | 不允许的外推 |
|---|---|---|
| Pro `chrome.dll` 无 `humanize` / `trajectory` 符号 | 曲线不在该二进制定制面 | 所有 Cloak 构建都相同 |
| 只开 CDP / 许可证注入不导入 human 包 | 不会生成这条轨迹 | 页面行为已被 humanize |
| `get_by_role`、`>>` 链式选择器、`query_selector()` ElementHandle | 来源称仍不支持或会绕过补丁 | 已覆盖全部 Playwright API |
| 计划器输出样本 | 本地几何样本 | 目标站点、风控或 Playwright 运行时已接受 |

## 验证与限制

- 来源指向 CloakHQ/CloakBrowser 包装层；本轮未读取上游仓库、未运行 CLI 或浏览器。
- 不收录绝对本机路径、许可证、CDP 口或鼠标坐标样值。
- 不能把计划器当成反检测 procedure：缺少页面挂接、失败出口和目标验收。
