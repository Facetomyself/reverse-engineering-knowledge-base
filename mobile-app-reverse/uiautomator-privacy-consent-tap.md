# 用 uiautomator 自动点击隐私同意按钮

> 来源: 微信公众号：Softard（Wossoneri）
> 原始发布时间: unknown
> 归档日期: 2026-09-06
> 分类: mobile-app-reverse
>
> pm clear / 首次启动后的隐私协议与权限弹窗，用 uiautomator dump 解析 UI 树，按 text/content-desc 打分后对 bounds 中心做 adb input tap。这是界面问题，不必先 Frida/LSPosed；服务于设备注册或 native trace 前的无人值守。

## 正文

为啥要搞这个，因为需求是 这几天我做 trace 工具让ai全自动修bug然后验证的一个真实场景。 有些app的设备注册会采集指纹，触发时机如下：

- 某些样本必须先 `pm clear`
- 重启 app 之后还得连上网
- 然后点掉隐私协议页
- 点完以后，目标 native 路径才会真正触发

这就导致一个很烦的现实： 然后每次ai修改完之后编译成so之后进行自动化trace时，我都要抽时间注意到并且手点一次，那这个过程效率很低


然后我觉得这个东西对大家应该是有用的，所以写一个文章分享分享；

注意，这篇文章不是教你做一个万能 Android 自动化框架。它解决的是一个很具体、但真的很折磨人的问题：

- `pm clear` 之后重新启动 app
- 首次启动会弹隐私协议页、权限页、前台遮挡弹窗
- 我们只想把“同意 / 允许 / 继续”这些按钮自动点掉
- 这样后面的自动化流程才能稳定往下跑


所以最后落地的方案很简单：

- 用 `uiautomator dump` 拿当前页面的 UI 树
- 从 XML 里找最像“同意按钮”的控件
- 算出它的屏幕坐标
- 再用 `adb shell input tap x y` 去点

这条链不花哨，但非常实用。


## 一、为什么选它

一开始当然也想过别的方案：

1. 用 Frida 分析 app，直接找到协议页点击函数，然后 RPC 调用
2. 用 LSPosed 或别的 hook 方案改页面逻辑
3. 用 AutoJS 之类工具单独写脚本

这些方案不是不能做，而是对这个问题来说太重了。

因为我们要处理的很多场景，本质上都是“界面交互问题”：

- 首启协议页
- 系统权限弹窗
- 前台更新弹窗
- 遮挡在最上层的确认框

既然它们本来就是 UI 问题，那就没必要一上来先反编译、先 hook、先改逻辑。

这里最顺手的办法反而是：

- 先看见页面
- 再决定点哪里

`uiautomator` 刚好就很适合干这个事。

它最有用的能力是：

1. 导出当前界面的 UI 树
2. 拿到控件的 `text`、`content-desc`、`resource-id`、`class`、`bounds`
3. 让我们能在脚本里做一次“猜哪个才是目标按钮”

然后真正执行点击的，再交给系统自带的 `input tap` 就够了。

## 二、uiautomator 到底提供了什么

命令本身很简单：

```bash
adb shell uiautomator dump /sdcard/xfqtrace_ui.xml
adb shell cat /sdcard/xfqtrace_ui.xml
```

第一条命令让设备把当前页面导出成 XML。

第二条命令把这个 XML 读出来。

导出的内容大概会是这种结构：

```xml
<node
    text="同意"
    resource-id="com.xxx:id/confirm"
    class="android.widget.Button"
    clickable="true"
    enabled="true"
    bounds="[120,1600][960,1744]" />
```

这个 XML 最重要的不是它“长得像控件树”，而是它给了我们两个真正能用的信息：

1. 这个控件像不像我们要找的按钮
2. 这个控件在屏幕上的位置到底在哪

## 三、真正的点击是怎么完成的

`adb shell input tap x y` 点的是屏幕坐标，不是控件 id。

所以中间一定要先把控件的 `bounds` 变成坐标。

例如：

```text
bounds="[120,1600][960,1744]"
```

那它的中心点就是：

- `x = (120 + 960) / 2 = 540`
- `y = (1600 + 1744) / 2 = 1672`

最后执行：

```bash
adb shell input tap 540 1672
```

整条链路其实就这么直接：

```text
启动 app
  -> dump 当前 UI 树
  -> 解析每个 node 的 text / resource-id / class / bounds
  -> 给候选控件打分
  -> 选一个最像“同意 / 允许 / 继续”的控件
  -> 算中心点
  -> input tap
```

所以这个方案的核心从来不是“怎么点”。

真正的核心其实是：

- 怎么从一堆 node 里挑出那个最该点的

## 四、核心 Python 代码

它只做几件事：

1. 启动 app
2. `uiautomator dump` 导出 XML
3. 解析控件树
4. 给候选控件打分
5. 点击“最像同意/允许/继续”的那个
6. 处理前台 blocker 和重复点击

```python
#!/usr/bin/env python3
import re
import subprocess
import time
import xml.etree.ElementTree as ET

UIAUTOMATOR_DUMP_PATH = "/sdcard/xfqtrace_ui.xml"
POLL_SEC = 1.0
TIMEOUT_SEC = 35.0
MIN_READY_SEC = 4.0
READY_STABLE_POLLS = 2
ACTION_REPEAT_COOLDOWN_SEC = 6.0

UI_PRIMARY_KEYWORDS = [
    "同意", "接受", "允许", "始终允许", "继续", "下一步", "进入", "开始",
    "确认", "确定", "好的", "知道了", "我知道了", "立即开启", "去开启",
    "仅在使用该应用时允许", "使用期间允许", "while using the app",
    "allow", "allow only while using the app", "agree", "accept", "continue",
    "next", "ok", "confirm", "start", "got it",
]

UI_BLOCKER_APPROVE_KEYWORDS = [
    "允许", "始终允许", "仅在使用该应用时允许", "使用期间允许",
    "allow", "allow only while using the app", "ok", "continue", "confirm",
]

UI_NEGATIVE_KEYWORDS = [
    "不同意", "拒绝", "不允许", "deny", "donotallow", "don't allow",
    "cancel", "取消", "退出",
]

UI_CHECKBOX_KEYWORDS = [
    "隐私", "协议", "条款", "policy", "privacy", "consent", "agreement",
    "checkbox", "check", "勾选",
]

TRANSIENT_ACTIVITY_KEYWORDS = [
    "splash", "launch", "startup", "welcome", "guide", "loading",
    "boot", "init", "advert", "adactivity",
]


def adb(*args, serial=None):
    cmd = ["adb"]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(args)
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",
    )
    return proc.stdout or "", proc.stderr or "", proc.returncode


def adb_shell(command, serial=None):
    return adb("shell", command, serial=serial)


def launch_app(serial, package):
    out, err, rc = adb(
        "shell", "monkey", "-p", package,
        "-c", "android.intent.category.LAUNCHER", "1",
        serial=serial,
    )
    if rc != 0:
        text = "\n".join(x for x in [out, err] if x).strip()
        print(f"[!] failed to launch {package}: {text or 'unknown error'}")
        return False
    print(f"[*] Launch requested: {package}")
    return True


def adb_pidof(serial, package):
    out, _, rc = adb_shell(f"pidof {package}", serial=serial)
    if rc == 0 and out.strip():
        try:
            return int(out.strip().split()[0])
        except ValueError:
            pass

    short = package.rsplit(".", 1)[-1]
    out, _, rc = adb_shell("ps -A", serial=serial)
    if rc != 0 or not out:
        return None
    for line in out.splitlines():
        cols = line.split()
        if len(cols) < 2:
            continue
        name = cols[-1]
        if name != package and name != short:
            continue
        for token in cols[1:-1]:
            if token.isdigit():
                return int(token)
    return None


def get_top_activity(serial):
    out, _, rc = adb_shell("dumpsys activity activities", serial=serial)
    if rc != 0 or not out:
        return None
    for line in out.splitlines():
        if "topResumedActivity" not in line and "mResumedActivity" not in line:
            continue
        m = re.search(r"([A-Za-z0-9._$]+/[A-Za-z0-9._$]+)", line)
        if m:
            return m.group(1)
    return None


def parse_bounds(bounds):
    m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds or "")
    if not m:
        return None
    x1, y1, x2, y2 = map(int, m.groups())
    if x2 <= x1 or y2 <= y1:
        return None
    return (x1 + x2) // 2, (y1 + y2) // 2


def parse_rect(bounds):
    m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds or "")
    if not m:
        return None
    x1, y1, x2, y2 = map(int, m.groups())
    if x2 <= x1 or y2 <= y1:
        return None
    return x1, y1, x2, y2


def dump_ui_hierarchy(serial):
    _, err, rc = adb("shell", "uiautomator", "dump", UIAUTOMATOR_DUMP_PATH, serial=serial)
    if rc != 0:
        err = err.strip()
        if err:
            print(f"[!] uiautomator dump failed: {err}")
        return None
    out, _, rc = adb_shell(f"cat {UIAUTOMATOR_DUMP_PATH}", serial=serial)
    if rc != 0 or not out:
        return None
    xml_start = out.find("<?xml")
    if xml_start >= 0:
        out = out[xml_start:]
    return out if out.lstrip().startswith("<?xml") else None


def iter_ui_nodes(xml_text):
    if not xml_text:
        return []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    nodes = []
    for node in root.iter("node"):
        center = parse_bounds(node.attrib.get("bounds", ""))
        if center is None:
            continue
        nodes.append({
            "text": (node.attrib.get("text") or "").strip(),
            "desc": (node.attrib.get("content-desc") or "").strip(),
            "resource_id": (node.attrib.get("resource-id") or "").strip(),
            "class_name": (node.attrib.get("class") or "").strip(),
            "package": (node.attrib.get("package") or "").strip(),
            "enabled": node.attrib.get("enabled", "true") == "true",
            "clickable": node.attrib.get("clickable", "false") == "true",
            "checkable": node.attrib.get("checkable", "false") == "true",
            "checked": node.attrib.get("checked", "false") == "true",
            "center": center,
            "bounds": node.attrib.get("bounds", ""),
            "rect": parse_rect(node.attrib.get("bounds", "")),
        })
    return nodes


def _normalize_ui_value(value):
    return (value or "").strip().lower().replace(" ", "")


def _ui_keyword_hit(haystack_lower, normalized, keyword):
    key = keyword.lower()
    if " " in key:
        return key in haystack_lower or key.replace(" ", "") in normalized
    if len(key) <= 2:
        return re.search(rf"(?<![a-z]){re.escape(key)}(?![a-z])", haystack_lower) is not None
    return key in haystack_lower or key in normalized


def score_ui_node(node):
    if not node["enabled"]:
        return -1, None

    text = node["text"]
    desc = node["desc"]
    resource_id = node["resource_id"]
    class_name = node["class_name"]
    haystack = " ".join(v for v in [text, desc, resource_id, class_name] if v)
    normalized = _normalize_ui_value(haystack)
    text_len = len(text or desc or "")
    rect = node.get("rect")
    width = (rect[2] - rect[0]) if rect else 0
    height = (rect[3] - rect[1]) if rect else 0

    if any(_ui_keyword_hit(haystack.lower(), normalized, keyword) for keyword in UI_NEGATIVE_KEYWORDS):
        return -1, None

    if "已阅读并同意" in text and not node["checkable"] and "button" not in class_name.lower():
        return -1, None
    if (
        text_len >= 24
        and not node["checkable"]
        and "button" not in class_name.lower()
        and any(token in text for token in ["协议", "隐私", "政策", "登录", "服务"])
    ):
        return -1, None

    score = 0
    reason = None

    if node["checkable"] and not node["checked"]:
        checkbox_hits = 0
        for keyword in UI_CHECKBOX_KEYWORDS:
            if _ui_keyword_hit(haystack.lower(), normalized, keyword):
                checkbox_hits += 1
        if checkbox_hits > 0:
            score += 70 + checkbox_hits
            reason = "checkable-agreement"

    for keyword in UI_PRIMARY_KEYWORDS:
        if _ui_keyword_hit(haystack.lower(), normalized, keyword):
            score += 100
            reason = reason or f"primary:{keyword}"

    if node["clickable"]:
        score += 5
    if "button" in class_name.lower():
        score += 10
    if node["checkable"]:
        score += 15
    if resource_id:
        rid = resource_id.lower()
        if any(token in rid for token in ["allow", "agree", "accept", "confirm", "continue", "next", "ok", "privacy"]):
            score += 20
            reason = reason or f"resource:{resource_id}"

    if text_len >= 18 and not node["checkable"] and "button" not in class_name.lower():
        score -= 80
    if width >= 700 and height <= 140 and not node["checkable"] and "button" not in class_name.lower():
        score -= 60

    return score, reason


def choose_ui_action(nodes):
    best_node = None
    best_score = 0
    best_reason = None
    for node in nodes:
        score, reason = score_ui_node(node)
        if score > best_score:
            best_node = node
            best_score = score
            best_reason = reason
    if best_node is None or best_score < 40 or best_reason is None:
        return None
    return best_node, best_reason, best_score


def is_blocking_top_activity(top_activity, package):
    if not top_activity:
        return False
    lowered = top_activity.lower()
    if package.lower() in lowered:
        return False
    return (
        "permissioncontroller" in lowered or
        "popupdialog" in lowered or
        "permission.ui" in lowered or
        "packageinstaller" in lowered or
        "gms" in lowered or
        "systemupdateactivity" in lowered or
        "update.phone" in lowered
    )


def is_safe_blocker_action(node):
    label = " ".join(
        value for value in [
            node.get("text", ""),
            node.get("desc", ""),
            node.get("resource_id", ""),
        ] if value
    )
    lowered = label.lower()
    normalized = _normalize_ui_value(label)
    if not node.get("clickable") and "button" not in node.get("class_name", "").lower():
        return False
    return any(_ui_keyword_hit(lowered, normalized, keyword) for keyword in UI_BLOCKER_APPROVE_KEYWORDS)


def is_transient_app_activity(top_activity, package):
    if not top_activity:
        return True
    lowered = top_activity.lower()
    if package.lower() not in lowered:
        return True
    return any(keyword in lowered for keyword in TRANSIENT_ACTIVITY_KEYWORDS)


def top_activity_package(top_activity):
    if not top_activity or "/" not in top_activity:
        return None
    return top_activity.split("/", 1)[0]


def tap_point(serial, x, y):
    adb("shell", "input", "tap", str(x), str(y), serial=serial)


def send_key(serial, keycode):
    adb("shell", "input", "keyevent", str(keycode), serial=serial)


def ui_action_key(node):
    label = node["text"] or node["desc"] or node["resource_id"] or node["class_name"]
    return f"{node['bounds']}|{node['resource_id']}|{label}"


def drive_first_launch_ui(serial, package):
    print(f"[*] Auto first-launch UI handling enabled ({TIMEOUT_SEC:.0f}s timeout)")
    if not launch_app(serial, package):
        return False

    deadline = time.time() + TIMEOUT_SEC
    start_ts = time.time()
    stable_ready_polls = 0
    action_history = {}

    while time.time() < deadline:
        pid = adb_pidof(serial, package)
        top_activity = get_top_activity(serial)
        blocker = is_blocking_top_activity(top_activity, package)

        xml_text = dump_ui_hierarchy(serial)
        nodes = iter_ui_nodes(xml_text)
        action = choose_ui_action(nodes)

        if blocker:
            if action is not None:
                node, reason, score = action
                if is_safe_blocker_action(node) and node.get("package") == top_activity_package(top_activity):
                    x, y = node["center"]
                    label = node["text"] or node["desc"] or node["resource_id"] or node["class_name"]
                    print(f"[*] UI blocker action: tap '{label}' ({reason}, score={score}) @ ({x},{y}) top={top_activity or '?'}")
                    tap_point(serial, x, y)
                    time.sleep(1.2)
                    continue
            print(f"[*] Foreground blocker detected: {top_activity}; sending BACK")
            send_key(serial, 4)
            time.sleep(1.0)
            continue

        if action is not None:
            node, reason, score = action
            action_key = ui_action_key(node)
            last_ts = action_history.get(action_key)
            if last_ts is not None and (time.time() - last_ts) < ACTION_REPEAT_COOLDOWN_SEC:
                print(f"[*] Skip repeated UI action within cooldown: {reason} {node['bounds']}")
                time.sleep(1.0)
                continue

            x, y = node["center"]
            label = node["text"] or node["desc"] or node["resource_id"] or node["class_name"]
            print(f"[*] UI action: tap '{label}' ({reason}, score={score}) @ ({x},{y}) top={top_activity or '?'}")
            tap_point(serial, x, y)
            action_history[action_key] = time.time()
            stable_ready_polls = 0
            time.sleep(1.2)
            continue

        if pid is not None and top_activity and package in top_activity and not blocker:
            if not is_transient_app_activity(top_activity, package) and (time.time() - start_ts) >= MIN_READY_SEC:
                stable_ready_polls += 1
                if stable_ready_polls >= READY_STABLE_POLLS:
                    print(f"[*] App looks stable now: pid={pid} top={top_activity}")
                    return True
            else:
                stable_ready_polls = 0
                print(f"[*] Waiting for non-transient app activity: top={top_activity}")
        else:
            stable_ready_polls = 0

        if pid is None:
            print("[*] Target process is not running; relaunching")
            if not launch_app(serial, package):
                return False
            time.sleep(1.5)
            continue

        time.sleep(POLL_SEC)

    top_activity = get_top_activity(serial)
    pid = adb_pidof(serial, package)
    print(f"[!] Auto first-launch UI handling timed out: pid={pid} top={top_activity or '?'}")
    return pid is not None


if __name__ == "__main__":
    serial = None
    package = "com.example.app"
    drive_first_launch_ui(serial, package)
```

如果你只是想把文章里的思路拿去自己改代码，这一段已经足够了。

它的特点是：

- 逻辑完整
- 没有掺 trace 注入、pull 日志、frida attach 那些东西
- 保留了真正有价值的部分：dump、解析、打分、防误点、防重复点、处理 blocker

## 五、当前脚本怎么找目标控件

当前实现不是写死某一个控件 id，而是走一套比较轻量的打分逻辑。

会优先看这些信息：

- `text`
- `content-desc`
- `resource-id`
- `class`
- `clickable`
- `checkable`
- `checked`
- `bounds`

然后给一些关键词加分。

主关键词大概是这些：

- `同意`
- `接受`
- `允许`
- `始终允许`
- `继续`
- `下一步`
- `进入`
- `开始`
- `allow`
- `accept`
- `continue`
- `agree`

如果命中了这些词，而且控件本身可点击、像按钮、或者本来就是 checkbox / confirm 控件，那分数就会上去。

反过来，明确负向的词会直接排掉，比如：

- `不同意`
- `拒绝`
- `不允许`
- `deny`
- `don't allow`

这样做的目的很单纯：

- 宁可少点一次，也不要把“拒绝”点下去

## 六、为什么不能只看按钮文本

如果事情真有这么简单，那这个文档都没必要写了。

实际页面里最烦的地方在于：

- 不是所有包含“同意”的东西都是按钮

最典型的协议页文案就是：

```text
已阅读并同意《用户协议》《隐私政策》
```

这里面也有“同意”，但它常常根本不是最终提交按钮。

很多时候它只是：

- 一整行说明文本
- 一个可切换勾选状态的协议项
- 或者一个会触发 checkbox 勾选/取消的区域

如果脚本只靠“文本里有同意”就乱点，就很容易出现这种蠢事：

1. 第一次点，把勾选框点上
2. 第二次又点到同一行，把勾选框取消
3. 第三次再点回去

最后看起来像脚本在发疯。

这不是 `adb` 不准，而是候选规则太糙了。

## 七、当前怎么减少误点

现在主要做了几层收敛。

### 7.1 先排掉“长得像整段文案”的节点

如果一个节点：

- 文本特别长
- 不是 `checkable`
- 类名里也不像 `button`
- 还带着“协议 / 隐私 / 政策 / 服务”这种说明词

那大概率就不是最终确认按钮。

这类节点会被强降权，甚至直接排除。

还有一种很常见的情况是：

- 这行文字特别宽
- 但高度不高
- 很像一条铺满横向区域的说明文案

这种节点也会继续降权。

现在脚本更偏向点的是：

- 真按钮
- 明确 checkbox
- 带清晰 `resource-id` 的确认控件

而不是点整段协议文字。

### 7.2 对 checkbox 做单独处理

有些协议页不是“直接点同意”。

它会要求先勾选：

- 已阅读并同意协议

然后底下的大按钮才会变成可点击。

所以 `checkable=true` 且 `checked=false` 的节点不能被忽略。

如果它本身又命中了协议相关关键词，脚本会把它视作一个高优先级候选。

也就是说，当前逻辑不是一味找“最终大按钮”，而是会接受这种两步走：

1. 先勾协议
2. 再点继续 / 同意

### 7.3 对 `resource-id` 补一层加权

如果一个控件的 `resource-id` 里自带这些词：

- `allow`
- `agree`
- `accept`
- `confirm`
- `continue`
- `next`
- `ok`
- `privacy`

那它通常比单纯命中文本更可信。

因为文本可能会变，资源命名很多时候更稳定一些。

## 八、为什么还要防重复点击

哪怕已经选到了正确候选，实际跑起来还是会遇到另一个问题：

- 页面动画还没结束
- 新 XML 还没刷新
- 同一个控件又被识别了一次

如果这时候继续点，就容易产生副作用：

- checkbox 来回翻转
- 同一个按钮被连点
- 某些弹窗刚开始消失，又被脚本当成还在

所以当前实现又加了一层冷却时间。

它会用下面这几个字段拼一个 action key：

- `bounds`
- `resource-id`
- `label`

同一个 key 在短时间内不会重复点击。

这个保护很朴素，但很有效。

因为很多 UI 自动化看起来“逻辑没问题”，其实就是死在重复点击上。

## 九、为什么不能只盯着 app 自己的页面

首启时挡在最上面的，不一定是 app 自己的协议页。

还可能是：

- 系统权限弹窗
- 安装器相关弹窗
- Google 服务更新页
- 系统更新确认页

如果最上层 blocker 还没处理掉，就直接按 app 页面里的坐标点，通常只有两种结果：

1. 点了没反应
2. 点错地方

所以当前顺序是：

1. 先判断前台是不是 blocker
2. 如果 blocker 自己有明确的“允许 / 继续”按钮，就先点它
3. 如果没有合适按钮，就先发一个 `BACK`
4. 前台恢复后，再继续处理 app 自己页面

这点很重要。

因为“真正挡在最前面的页面是谁”，比“我们想点谁”优先级更高。

## 十、为什么不能太早判断页面已经结束

自动化脚本很容易犯一个错：

- 看到 activity 名字像是首页了，就以为流程结束了

但真实情况往往没这么简单。

有些页面名字看起来已经像登录页、首页、落地页了，但协议按钮其实还在。

如果这时候脚本过早退出，结果就是：

- 页面没完全处理干净
- 自动化后续流程还会卡住

所以更稳的做法不是只看 activity 名字，而是一起看：

1. 当前前台 activity 是什么
2. `uiautomator dump` 出来的真实 UI 上还有没有可操作控件
3. 页面是否已经连续几轮稳定

只有当这些信号同时说明“真的结束了”，才应该停掉 UI driver。

## 十一、Windows 下还有一个编码坑

这个问题不大，但真能把整条链直接打断。

`uiautomator dump` 导出的 XML 通过 `adb` 拉回来时，可能带有本机默认编码解不了的字节。

如果在 Windows 上直接这样写：

```python
subprocess.run(..., text=True)
```

很容易碰到：

- `UnicodeDecodeError`
- `stdout` 为空
- 后续解析再触发二次异常

所以稳妥做法是固定：

```python
encoding="utf-8"
errors="replace"
```

这不是锦上添花，而是保证脚本别因为编码直接死掉。

## 十二、这套方案的边界

这条 `uiautomator + input tap` 方案很好用，但它也不是无敌的。

它更适合下面这些场景：

1. 首启隐私协议页
2. 首启权限页
3. 系统标准弹窗
4. 前台有标准控件、能被 UI 树正常看见的确认页面

不太适合的情况包括：

1. 目标按钮根本不在 UI 树里
2. 页面是完全自绘的
3. 要处理的不是“点一下按钮”，而是要绕过某段 Java / Native 逻辑

如果遇到这些情况，就别硬逼 `uiautomator` 了。

更合理的做法通常是：

- 通用流程继续保留 `uiautomator` 主线
- 对个别特殊包再补 Frida / hook 的专用方案

## 十三、最后的结论

如果只记几句话，那就记这些：

1. `uiautomator dump` 解决的是“看见当前页面”的问题。
2. `input tap` 解决的是“把点击落到屏幕上”的问题。
3. 真正麻烦的从来不是点击本身，而是怎么少误点、少重复点、别被前台 blocker 带偏。
4. 对首启协议页、权限页、标准确认弹窗，这条链已经足够轻，也足够实用。

所以这篇文章真正想说的不是“Android 自动化多高级”。

而是：

- 如果你的需求只是把首启的隐私同意按钮自动点掉，那先别急着上重武器。
- 先把 `uiautomator dump + input tap` 这条最便宜、最稳、最容易维护的路走通，很多时候就够了。
