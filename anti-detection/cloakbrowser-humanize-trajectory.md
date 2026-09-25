# CloakBrowser humanize 轨迹：包装层三次贝塞尔计划器

> 来源: CloakHQ/CloakBrowser MIT 包装层 `cloakbrowser/human`（https://github.com/CloakHQ/CloakBrowser）
> 分析日期: 2026-09-24
> 归档日期: 2026-09-24
> 分类: 反检测/风控对抗 — CloakBrowser humanize 轨迹
>
> 鼠标曲线在官方 Python/JS 包装进程里算完，再交给 Playwright 原来的 `mouse.move`。本机 Pro `chrome.dll` 没有 `humanize` / `trajectory` 符号。可调用实现在主仓 `tools/cloakbrowser_human`，只产出样本，不挂页面、不发 CDP。

## 定位

`humanize=True` 是包装层开关，不是 Chromium 补丁名。`launch()` 解析 `HumanConfig` 后调用 `patch_browser`，再包住 `new_context` / `new_page`。每个 page 的 `patch_page` 先存下原始 `click`、`mouse.*`、`keyboard.*`，再换成 human 版本。

Python 入口是 `cloakbrowser/human/mouse.py`，JavaScript 平行实现是 `js/src/human/mouse.ts`。两边都是三次贝塞尔、三次 ease-in-out、法线偏移控制点、中间抖动、burst 停顿和概率过冲。

本机 `tools/cloakbrowser` 与 `cloakbrowser-control` 只注入许可证环境并交付 CDP 口，不导入这个包。只开 CDP 不会生成轨迹。外部 Playwright 要显式调用上游的 `patch_page` / `patch_browser`。

几何读取走 CDP `Page.createIsolatedWorld`，用来避开主世界的 `querySelector` 钩子。路径计算不在页面里。鼠标点仍然走原始 `mouse.move`。Shift 符号在上游有一条 CDP `Input.dispatchKeyEvent` 旁路；提取出的模块不包含这条旁路。

## 点击链

每个 page 有一份 `_CursorState`。第一次动作把光标直接放到地址栏一带（默认 x 400–700、y 45–60），之后的移动从这一点画曲线。

`page.click(selector)` 的顺序：

1. `careful` 预设可先做一小段 idle 漂移；`default` 默认关闭。
2. 元素不在视口目标带（默认高度的 20%–80%）时，先把光标移到视口中部，再用滚轮把元素中心送进带内。已经完全可见、但页面在需要的方向上已经顶到头时，不再空转滚动。
3. 在元素盒子里取点。输入框 x 取宽度的 5%–30%，y 取 30%–70%；按钮两类都取 35%–65%。
4. `human_move` 画到这个点。
5. 隔离世界做 pointer-events 命中检查。`force=True` 跳过可操作性检查和这一步。
6. 瞄准停顿后 `mouse.down` / `mouse.up`，按住时长按输入框或按钮两套区间抽取。

包装层在 `human_move` 返回后把逻辑光标写成目标点。过冲修正的最后一个采样可以偏离目标约 2 像素。下一次若要和包装层一致，从逻辑光标出发，不从最后一个采样出发。

## 曲线

距离小于 1 像素时不采样。

步数是 `round(距离 / mouse_steps_divisor)`，再夹到 `mouse_min_steps` 与 `mouse_max_steps`。默认除数 8，上下限 25 和 80。采样个数是步数加 1。

两个控制点放在起点到终点的 25% 和 75%，再沿线段法线偏移 `uniform(-0.3, 0.3) * 距离`。采样参数先做三次 ease-in-out：`t < 0.5` 时为 `4t³`，后半段为 `1 - (-2t+2)³ / 2`。

每个点再加横向抖动。幅度是 `sin(π * progress) * mouse_wobble_max`，中间最大、两端为 0。点按 burst 送出，每送 `mouse_burst_size` 个点停 `mouse_burst_pause` 毫秒，最后一点不停。

到达后以 `mouse_overshoot_chance` 的概率沿接近方向冲出 `mouse_overshoot_px`，停 30–70 毫秒，再拉回终点附近 `±2` 像素。

## 滚动与键盘

滚轮按加速、巡航、减速三段取增量。加速段约 80–100，减速段约 60–90，巡航用 `scroll_delta_base`，再乘 `scroll_delta_variance`。每一档再拆成 20–40 的小滚轮事件，间隔 8–20 毫秒。可选过冲后再反向修正 1–2 次。视口里是否已经进入目标带，由调用方每几步回读；纯计划器只给出给定像素距离的滚轮序列。

键盘按字符按下、保持、抬起。间隔是 `typing_delay ± typing_delay_spread`，以 `typing_pause_chance` 插入长停顿。字母和数字有邻键误触，随后 Backspace。大写和 Shift 符号先按 Shift。非 ASCII 记为 `insert_text`。上游对 Shift 符号可以改走 CDP；本模块只产出按键样本。

## 默认可调区间

| 字段 | default | careful 差异 |
|------|---------|----------------|
| `mouse_steps_divisor` / min / max | 8 / 25 / 80 | 相同 |
| `mouse_wobble_max` | 1.5 | 相同 |
| `mouse_overshoot_chance` | 0.15 | 0.10 |
| `mouse_overshoot_px` | 3–6 | 相同 |
| `mouse_burst_size` / pause | 3–5 / 8–18 ms | pause 12–25 ms |
| 输入框瞄准 / 按住 | 60–140 / 40–100 ms | 80–180 / 60–140 ms |
| 按钮瞄准 / 按住 | 80–200 / 60–150 ms | 120–280 / 80–200 ms |
| `scroll_delta_base` | 80–130 | 相同 |
| 快 / 慢滚停顿 | 30–80 / 80–200 ms | 100–200 / 250–600 ms |
| `scroll_target_zone` | 0.20–0.80 | 相同 |
| `typing_delay` ± spread | 70 ± 40 ms | 100 ± 50 ms |
| `mistype_chance` | 0.02 | 相同 |
| idle between actions | 关 | 开，0.4–1.0 s |

单次调用可以盖掉字段，上游参数名是 `human_config`。预设只有 `default` 和 `careful`。

## 可调用模块

主仓路径：`tools/cloakbrowser_human`。把 `D:\reverse_ENV\tools` 放进 `sys.path` 后：

```python
from cloakbrowser_human import make_rng, plan_mouse_path, resolve_config

plan = plan_mouse_path(0, 0, 400, 300, resolve_config("default"), make_rng(1))
```

公开函数：`plan_mouse_path`、`plan_click`、`plan_scroll`、`plan_scroll_into_view`、`plan_typing`、`plan_idle`、`click_point`、`initial_cursor`、`element_in_zone`、`scroll_offset`。命令行：

```powershell
& "D:\reverse_ENV\.venv\Scripts\python.exe" "D:\reverse_ENV\tools\cloakbrowser_human\cli.py" mouse --start 0,0 --end 400,300 --seed 1
```

`delay_ms` 是该样本执行之后、下一样本之前的等待。`Plan.cursor` 是逻辑光标。

## 边界

- 本机 Pro 二进制的定制面是 `components/ungoogled/license_runtime.cc` 和 `fingerprint-*` 开关。曲线不在 `chrome.dll`。
- 提取模块不复制上游的 Playwright 猴子补丁、隔离世界和 CDP 按键派发。
- `get_by_role` 与 `>>` 链式选择器在上游 humanize 里仍不支持。Playwright 的 `query_selector()` 返回的 ElementHandle 会绕过补丁。
