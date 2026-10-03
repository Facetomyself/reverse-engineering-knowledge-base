---
schema_version: 2
id: anti-detection-chromium-clientrects-noise-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-clientrects]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./20-clientrects-fingerprint.md#一什么是clientrects指纹
    basis: unknown
  - id: s2
    ref: ./20-clientrects-fingerprint.md#二js如何获取clientrects指纹
    basis: unknown
  - id: s3
    ref: ./20-clientrects-fingerprint.md#三编译
    basis: unknown
  - id: s4
    ref: ./20-clientrects-fingerprint.md#3编译
    basis: unknown
  - id: s5
    ref: ./20-clientrects-fingerprint.md#四在线指纹验证网站
    basis: unknown
  - id: s6
    ref: ./20-clientrects-fingerprint.md#五感谢
    basis: unknown
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2]
    basis: unknown
    limits: 只保留 getClientRects 被当作指纹的来源说明。控制台演示的具体小数在正文里没有，截图未审查，不记录测量原值。
  - name: interfaces
    anchor: interfaces
    sources: [s3]
    basis: unknown
    limits: 只定位贴出的 `DOMRect::FromRectF`。其他构造 DOMRect 的路径来源没有写。
  - name: parameters
    anchor: parameters
    sources: [s3]
    basis: unknown
    limits: 种子和加减公式只按贴出的表达式整理。缺头文件是否能编过、以及固定种子下刷新是否改变结果，都没有运行证据。
  - name: validation
    anchor: validation
    sources: [s4, s5, s6]
    basis: unknown
    limits: 刷新随机和 creepjs 通过都是作者自述。本轮未编译，也未打开验证站。
relations:
  - type: derived_from
    target: ./20-clientrects-fingerprint.md#三编译
tags: [chromium, clientrects, DOMRect, unknown]
---

# Chromium ClientRects FromRectF 噪声

这张卡检索 ClientRects 噪声被接在哪个函数、种子从哪来、哪些矩形不会被改。它不提供可编译补丁，也不记录任何一次测量得到的矩形原值。

<a id="risk-control"></a>
## 指纹面

来源把 `getClientRects()` 写成读取元素 CSS 边界框的入口，并用字体、渲染引擎和分辨率造成的小数差异做 hash。演示是在页面里插入一个 SVG `rect` 再读 `getClientRects()[0]`。正文只说小数很长、浏览器之间有细微差别，没有写出具体坐标。

作者把噪声限制在 `rect.x() > 0`。说明文字写的是 `x < 0` 保持不变、`x > 0` 才加一个很小的量，没有讨论 `x == 0`。贴出的条件是 `rect.x() > 0`，所以 `x == 0` 走保持宽高的分支。`x` 和 `y` 本身没有被改写。

<a id="interfaces"></a>
## 落点

文件是 `third_party\blink\renderer\core\geometry\dom_rect.cc`，函数是 `DOMRect::FromRectF`。来源假设读者已经按系列第一篇编过 Chromium。贴出的替换只给这个函数加了 `base/command_line.h`；表达式用到的 `istringstream`、`chrono` 和 `time_t` 没有对应的 include。这只说明贴码不完整，不是编译失败的运行结论。

<a id="parameters"></a>
## 种子与公式

有 `--fingerprints` 时，种子来自该开关的 ASCII 值经 `istringstream` 读入的 `int`。没有开关时，种子是调用时刻的 `system_clock` 转成 `time_t` 再转成 `int`。

`rect.x() > 0` 时：

- 宽度加上 `seed % 103 / 100000.0`
- 高度加上 `seed % 97 / 100000.0`

否则宽高原样返回。这是由种子决定的加减，不是每次调用重新抽样。开关固定时，同一次进程里的种子不变。没有开关时，种子粒度是秒。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 采集入口是 `getClientRects()` | s1，`20-clientrects-fingerprint.md:24` | unknown | 来源对 ClientRects 指纹的说明 | 无测量原值 |
| C2 | 改写点是 `dom_rect.cc` 的 `FromRectF` | s3，`20-clientrects-fingerprint.md:53` | unknown | 贴出的这一个函数 | 其他构造路径未知 |
| C3 | 仅 `rect.x() > 0` 时改宽高 | s3，`20-clientrects-fingerprint.md:86` | unknown | 贴出的分支 | 与“x<0 才不变”的说明不完全一致 |
| C4 | 宽度增量是 `seed % 103 / 100000.0` | s3，`20-clientrects-fingerprint.md:87` | unknown | 贴出的表达式 | 固定种子下不是每刷一次一抽 |

<a id="validation"></a>
## 作者验收与缺口

作者写编译后每次刷新 ClientRects 指纹都是随机的，并点名 `https://browserleaks.com/rects` 和 `https://www.browserscan.net/`。感谢段说此前一直没绕过 creepjs，所以才补这一处。这些都是自述。

按贴出的种子规则，`--fingerprints` 固定时刷新不应改变种子；无开关时同一秒内的 `time_t` 也不变。因此“每次刷新都随机”不能从代码形态推出来。creepjs 具体查了哪一项，来源没有写。构建目标仍是 `out/Default` 的 chrome，命令间距以来源围栏为准。这里同样没有失败出口。
