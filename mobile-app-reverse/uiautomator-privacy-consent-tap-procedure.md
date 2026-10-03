---
schema_version: 2
id: android-first-launch-consent-tap-procedure
document_type: procedure
original_date: '2026-06-08'
archived_date: '2026-09-06'
scope:
  targets:
    - Android first-launch privacy consent UI
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./uiautomator-privacy-consent-tap.md#一为什么选它"
    basis: source-report
  - id: s2
    ref: "./uiautomator-privacy-consent-tap.md#四核心-python-代码"
    basis: source-report
  - id: s3
    ref: "./uiautomator-privacy-consent-tap.md#十为什么不能太早判断页面已经结束"
    basis: source-report
  - id: s4
    ref: "./uiautomator-privacy-consent-tap.md#十二这套方案的边界"
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [s1, s2, s4]
    basis: source-report
    limits: 顺序来自来源的驱动循环和第九节。没有在本机对任何包跑过。不记录设备指纹原值。
  - name: parameters
    anchor: parameters
    sources: [s2]
    basis: source-report
    limits: 时限、分数和关键词类别按来源代码与第五节。完整词表以源码行为准，本卡不另造词。
  - name: validation
    anchor: acceptance
    sources: [s2, s3]
    basis: source-report
    limits: 通过条件是来源代码里的稳定轮数和第十节的三信号。作者称实用只保留为 source-report。
relations:
  - type: derived_from
    target: "./uiautomator-privacy-consent-tap.md#四核心-python-代码"
tags:
  - uiautomator
  - adb
  - first-launch
  - source-report
---

# 首启隐私页：dump、打分、再决定是否点击

这份流程只处理来源写明的界面问题：`pm clear` 后的首启协议页、权限页和挡在前面的标准弹窗。它不代替 Frida，也不采集指纹。环境准备流程是另一张卡，管的是设备、证书和代理，不是这个点击循环。来源是 [用 uiautomator 自动点击隐私同意按钮](./uiautomator-privacy-consent-tap.md#四核心-python-代码)。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 来源要求 | 不够时 |
|---|---|---|
| 包名 | `drive_first_launch_ui(serial, package)`；示例包名是 `com.example.app` | F1，不把示例包当成目标 |
| 连接 | `adb` 能 `monkey` 拉起 LAUNCHER，并能 `pidof` 或 `ps -A` | F1 |
| 页面形态 | 按钮在 UI 树里，有 text、content-desc、resource-id、class、bounds | F3 |
| 编码 | Windows 拉 XML 时固定 `encoding="utf-8"` 且 `errors="replace"` | F4 |
| 业务前提 | 来源写某些样本必须先 `pm clear`，重启后还要联网，点完协议才走到 native | 这是作者场景，不是本流程的通过条件 |

来源明确不先上 Frida、LSPosed 或 AutoJS，因为要处理的是界面，不是改点击函数。

<a id="parameters"></a>
## 来源常数

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 整段超时 35 秒 | TIMEOUT_SEC = 35.0 | s2 :208 | source-report | 没有说明为何是 35 |
| C2 | 至少过 4 秒才允许判稳定 | MIN_READY_SEC = 4.0 | s2 :209 | source-report | 与瞬态 activity 同时成立 |
| C3 | 连续 2 轮无点击才算稳定 | READY_STABLE_POLLS = 2 | s2 :210 | source-report | 轮询间隔是 POLL_SEC = 1.0 |
| C4 | 同一动作 6 秒内不重复点 | ACTION_REPEAT_COOLDOWN_SEC = 6.0 | s2 :211 | source-report | key 含 bounds、resource-id、label |
| C5 | 主关键词从同意、接受、允许开始 | "同意", "接受", "允许" | s2 :214 | source-report | 同行后面还有中英文词，以源码为准 |
| C6 | 负向词直接淘汰，包括不同意和拒绝 | "不同意", "拒绝" | s2 :227 | source-report | 同行还有不允许、deny、cancel |
| C7 | 最高分低于 40，或没有原因，就不当成点击 | best_score < 40 | s2 :467 | source-report | 未勾选的协议 checkbox 可以先攒分 |
| C8 | 非按钮且文本长度至少 18 要减分 | text_len >= 18 | s2 :449 | source-report | 另一条是宽大于等于 700 且高不超过 140 |
| C9 | dump 文件路径按来源常量 | UIAUTOMATOR_DUMP_PATH = "/sdcard/xfqtrace_ui.xml" | s2 :206 | source-report | 只是路径，不是凭据 |

点击落点是 bounds 中心：`x = (120 + 960) / 2 = 540`（:161）只是讲解用例。`adb shell input tap x y` 的原句是 `点的是屏幕坐标，不是控件 id`（:149）。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 用 monkey 按包名拉起 LAUNCHER。 | 返回码，以及 `Launch requested` 或失败文本。 | 拉起失败走 F1；否则 S2。 |
| S2 | `uiautomator dump` 到 C9 的路径，再 cat。从 `<?xml` 起截取。 | XML 文本，或 None。 | dump 或解析失败只记日志，本轮不点击，继续轮询；编码错误走 F4。 |
| S3 | 解析 node 的 text、content-desc、resource-id、class、bounds。负向词、`已阅读并同意` 且非 checkbox 非 button、以及又长又像协议说明的节点直接 -1。 | 候选和分数。 | 最高分低于 40 走 S5 的稳定判断；否则 S4。 |
| S4 | 若前台是 blocker（权限控制器、安装器、gms、系统更新等，且不是目标包），只点该包上、且标签属于允许类的控件；否则发 BACK。不是 blocker 时，对最高分控件做冷却后点击中心。 | 日志里的 label、reason、score、坐标、top activity。 | 点完重新 dump。冷却期内跳过并等待。 |
| S5 | 没有可点控件时，同时看 pid、top activity 含包名、不是 blocker、不是 splash 一类瞬态，并且已过 MIN_READY_SEC。 | `stable_ready_polls`。 | 连续达到 READY_STABLE_POLLS 走 S6；进程没了则重拉，仍失败走 F1。 |
| S6 | 打印稳定并返回 True。 | `App looks stable now` 那一行里的 pid 和 top。 | 这是来源的通过出口。超时走 F2。 |

第九节把 S4 的 blocker 写成固定顺序：`先判断前台是不是 blocker`，有 `允许 / 继续` 就先点，没有就 `BACK`，然后才回到应用自己的页面。

<a id="outputs"></a>
## 输出

1. 拉起是否成功。
2. 每一次点击的 label、reason、score 和中心坐标；被冷却跳过也要留下。
3. 结束时的 pid 和 top activity。
4. 返回值：稳定为 True；拉起失败为 False；超时返回 `return pid is not None`（:608），进程还在不等于页面已处理完。
5. 若走 F3，记录按钮不在树里、自绘，或问题已经不是点击。

<a id="acceptance"></a>
## 验收

| 门 | 通过条件 | 不能代替它的东西 |
|---|---|---|
| A1 进程与前台 | pid 存在，top activity 含目标包，且不是 blocker | 只看到进程还在 |
| A2 不是瞬态页 | `is_transient_app_activity` 为假 | activity 名字像首页 |
| A3 时间与轮数 | 启动已超过 `MIN_READY_SEC = 4.0`，且连续 `READY_STABLE_POLLS = 2` 轮没有选出点击 | 单次 dump 为空 |
| A4 页面信号 | 第十节要求 activity、dump 里已无可操作控件、连续稳定这三件事同时成立 | 作者说脚本实用 |

本卡没有新增设备日志。A1 到 A4 只是来源文字里的门，不能当成这次已经通过。

<a id="failure-exits"></a>
## 失败出口

F1：monkey 拉起失败，或进程反复不在且再次拉起失败。停止，不点击。补包名、序列号或 LAUNCHER 类别。

F2：到达 `TIMEOUT_SEC = 35.0`。来源打印超时并返回进程是否还在。进程还在只说明没死，不进入 A1 的通过。

F3：`目标按钮根本不在 UI 树里`，或 `页面是完全自绘的`，或 `要绕过某段 Java / Native 逻辑`。停止这条点击链。来源写通用流程仍可保留 dump 主线，个别包再另写 hook。本卡不提供那段 hook。

F4：Windows 上 `text=True` 解 XML 抛解码错误或 stdout 为空。改为 `encoding="utf-8"` 与 `errors="replace"` 后再 dump。未改编码则停止解析。

另外两条来源写明的误点出口，不算通过：负向词直接 -1，原句是 `宁可少点一次，也不要把“拒绝”点下去`（:669）；未勾选的协议项要先当作候选，原句是 `checkable=true`（:746），避免把说明文字点成反复开关。
