---
schema_version: 2
id: benru-canvas-todataurl-call-accounting-procedure
document_type: procedure
original_date: '2026-04-25'
archived_date: '2026-10-02'
scope:
  targets: [canvas-todataurl-call-accounting]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./benru-anti-20260425-01.md#写个检测器看看谁在画你
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 只整理检测脚本里的挂钩、等待和异常分支。不复述后文的伪装赋值，也不把示例站的调用次数写成步骤结果。
  - name: validation
    anchor: acceptance
    sources: [s1]
    basis: source-report
    limits: 次数阈值是作者脚本中的常数。作者配图里的站点次数不作为验收数据。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录挂钩点、安装命令和判定常数。不记录 UA、地理坐标或任何 toDataURL 返回值。
relations:
  - type: derived_from
    target: ./benru-anti-20260425-01.md#写个检测器看看谁在画你
tags: [canvas, todataurl, call-accounting, source-report]
---

# Canvas toDataURL 调用记账

这份流程只判断：按来源脚本，一次页面访问里 `toDataURL` 被谁调用、调用了几次、算不算作者定义的疑似采集。它不回答如何改画布输出，也不解释京东 h5st 或易盾验证码产品卡。来源是 [Canvas 指纹检测归档](./benru-anti-20260425-01.md#写个检测器看看谁在画你)。

作者后文的浏览器伪装没有闭合验收。那一支在 F3 停止。论文比例和各站次数保持作者自述，不进入验收。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 来源要求 | 不足时 |
|---|---|---|
| 运行面 | `playwright install chromium --with-deps`，再用 Playwright 启动 Chromium | F1 类环境缺失时不解释调用次数 |
| 挂钩时机 | 在 `page.goto` 之前注入，替换 `HTMLCanvasElement.prototype.toDataURL` | 页面脚本先画完再挂钩，计数没有意义，停止 |
| 等待 | `wait_until="networkidle"`，另外等 document complete 和一段固定延时 | 导航超时不是零调用，见 S3 |
| 不做的事 | 不把 UA、时区、语言、地理坐标或画布数据写进记录 | 材料里只有这些字面量时走 F3 |

<a id="parameters"></a>
## 参数口径

挂钩保存宽度、高度、类型参数、堆栈前 300 字和时间戳，然后调用原方法。来源按堆栈里的源站聚合；匹配不到地址就记成 inline。

判定常数：同一来源 `src["count"] >= 3` 为最高档，不少于 2 为中间档。`fp_sources` 是次数不少于 2 的来源。总次数 `total >= 3 and len(fp_sources) >= 1` 才打印疑似采集。总次数不少于 2 但够不上前一档时，打印低度可疑。

指纹组合示例在 `split("x")[0]), ...` 处截断。这个省略号说明伪装参数表不完整，不能拿来当输入。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 确认 Chromium 安装命令和导航前挂钩这两项都在材料里 | 前提表 | 缺任一项走 F1 |
| S2 | 按来源脚本屏蔽图片和字体，注入挂钩，再打开页面 | 调用记录列表 | 导航开始后走 S3 |
| S3 | `networkidle` 超时则保留已有调用并继续；其他访问异常则关闭浏览器 | 调用列表或空 | 超时走 S4；异常走 F1 |
| S4 | 按源站汇总次数、尺寸和首尾时间差，套用次数阈值 | 三类判定之一 | 需要伪装结论时走 F3，不把判定改写成伪装成功 |

<a id="outputs"></a>
## 输出

交付的是一次访问的调用总数、按源站拆开的次数、画布尺寸集合、重复调用的时间跨度，以及作者脚本的三句判定文案之一。不交付画布数据，也不交付示例站的历史次数。

<a id="acceptance"></a>
## 验收

| 观察 | 来源口径 | 不算通过 |
|---|---|---|
| 无调用 | 打印未检测到指纹行为 | 挂钩注入失败却得到 0，无法区分 |
| 有数据但总次数低于 2 | 打印正常 | 不能解释成站点没有其他指纹面 |
| 疑似 | `total >= 3 and len(fp_sources) >= 1` | 作者配图里的 5 次、19 次不是本条验收 |
| 空结果 | 分析函数看到空数据时打印 `检测失败` | 空结果不是“未检测到” |

作者写“如果是true，你的爬虫已经被认出来了”，指的是 `navigator.webdriver`。这只是否定自检，不能当成 S4 的通过条件。

<a id="failure-exits"></a>
## 失败出口

F1：访问异常时来源执行 `return None`。空结果进入分析后打印检测失败。不把异常改记成零次调用。

F2：导航超时的原文是“页面超时，用已有数据分析”。已有数据仍走 S4；完全没有数据则与 F1 一样停止，不发明调用。

F3：问题若是改 Playwright 特征、轮换指纹或加载用户目录，停止。来源的视口行被省略号截断，插件列表是占位数组，除 webdriver 布尔值外没有验收。京东和易盾在文中只是作者对某次检测输出的解释，不把本流程并进那两张产品卡。
