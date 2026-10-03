---
schema_version: 2
id: benru-bilibili-text-click-yolo-siamese-procedure
document_type: procedure
original_date: '2026-04-29'
archived_date: '2026-10-02'
scope:
  targets: [bilibili-text-click-captcha]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./benru-anti-20260429-01.md#一技术原理
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [s1]
    basis: source-report
    limits: 只保留检测、匹配、按字库排序这三步的来源顺序。点击运动没有实现，不补轨迹。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 置信度、IoU、相似度和训练命令都是来源常数。排查表里的 0.2 与 0.4 是另一套调整方向，不覆盖训练命令。
  - name: validation
    anchor: acceptance
    sources: [s1]
    basis: source-report
    limits: 通过口径来自来源的阈值和排查表。配图上的序号是作者自述，本轮没有分数表。
relations:
  - type: derived_from
    target: ./benru-anti-20260429-01.md#一技术原理
tags: [bilibili, text-click-captcha, yolo, siamese, source-report]
---

# B 站文字点选：YOLO 与孪生网络的训练边界

这份流程回答：来源如何把“依次点击文字”收成它所说的 `两个模型接力`（检测框、字形匹配、字库顺序），以及什么情况下必须停。它不覆盖 B 站评论分页，也不提供点击运动实现。来源是 [文字点选归档](./benru-anti-20260429-01.md#一技术原理)。

作者把示例放在 B 站登录图上，并说结构相似的点选可以换训练数据。换数据仍然要走下面的前提，不能直接复用未重训的阈值。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 来源要求 | 不足时 |
|---|---|---|
| 图片 | 目标站至少 `200-300 张` 截图 | 只有演示仓库的预训练权重、且字体已变时走 F2 |
| 标签 | 题干要你点的字标 `target`，背景干扰字标 `char`，保存 YOLO 文本 | 两类颠倒则检测输出不能进入匹配 |
| 检测后处理 | `先丢掉置信度低于 0.25`；NMS IoU 用到 `0.3，否则会把紧邻的不同字误并成一个。` | 漏检或多检走 F1，不直接改标签含义 |
| 路径 | `模型路径别带中文，Windows 下容易读取出错` | 读模型失败走 F1 |
| 点击运动 | 来源只有 `贝塞尔曲线 + 随机延迟` 这一句 | 材料停在排序、还要浏览器点击时走 F3 |

<a id="parameters"></a>
## 参数口径

检测不识字，只出框和 `target` / `char`。孪生网络不做几千类汉字分类，而是输出 0 到 1 的相似度。

训练检测模型时，来源命令是 `python train.py --data data.yaml --weights yolov5s6.pt --img 640 --batch 16 --epochs 100`。数据文件里的类别名是 `char` 与 `target`。作者另写 `YOLO 最低要求 320×320`，这是排查分辨率用的下限，不是把训练尺寸改成 320。

相似度：`相似度 ≥0.7 判定为同一字，≤0.3`。中间地带不判通过。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 按前提表收图并标注。预训练 demo 只用来确认仓库能标出序号，不能代替目标站标签 | 图像目录和 YOLO 标签 | 数量或标签类别不够走 F2 |
| S2 | 按来源命令训练检测模型 | `runs/train/exp/weights/best.pt` | 路径或读取失败走 F1；权重出来后走 S3 |
| S3 | 用检测框裁字，同字目录做正样本对，不同字做负样本对，再按来源点名的孪生仓库训练 | 匹配模型 | 来源没有学习率和轮数；这些未知不能填成默认值，缺了就停止在 S3 |
| S4 | 只把 `target` 框送去匹配，`配对成功的位置按字库顺序输出，就是点击顺序。换个验证码类型需要重训` | 有序坐标 | 分数落在中间地带走 F2；还要发出点击走 F3 |

<a id="outputs"></a>
## 输出

检测侧交付 `runs/train/exp/weights/best.pt`。匹配侧交付按字库顺序排列的目标框。不交付点击事件、请求或登录结果。重复训练时来源没写 exp 目录如何递增，输出路径以当次训练目录为准。

<a id="acceptance"></a>
## 验收

| 观察 | 来源口径 | 不算通过 |
|---|---|---|
| 同字 | 相似度不低于 0.7 | 单张演示图上的序号不能代替分数 |
| 排除 | 相似度不高于 0.3 | 排除不是“点下一个” |
| 字体 | `全卡 0.4~0.6 就是字体不匹配` | 整段灰区分数不能标成点击顺序 |
| 检测框 | 漏检与多检分别对照 F1 的两个方向 | 把相邻字并成一个框仍算失败 |

<a id="failure-exits"></a>
## 失败出口

F1：Windows 中文路径按来源会读失败。检测框不合适时，来源写 `漏检→降 IoU（0.2）；多检→提置信度（0.4）`。这是下一次训练或后处理的方向，不是在同一次点击里改分数。分辨率不够时对照 320×320 的下限。

F2：`换个验证码类型需要重训`。字体一变，匹配阈值会失效。没有目标站的 200 到 300 张新图和两类标签时，停止，不用演示权重解释新站。

F3：排序之后的浏览器点击没有实现。看到 `贝塞尔曲线 + 随机延迟` 不能补曲线、延迟或选择器。Playwright 段只指向仓库里的脚本名，没有页面合同。
