---
schema_version: 2
id: benru-ddddocr-captcha-routing-reference
document_type: reference
original_date: '2026-03-11'
archived_date: '2026-10-02'
scope:
  targets: [ddddocr]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./benru-anti-20260311-01.md#二最基础的图文验证码
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只记录 classification 与 detection 的调用形态。不记录语音接口的密钥占位，也不把作者提到的识别率当成已核对结果。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 颜色过滤、框形状和 3/4 轨迹分界来自来源草稿。滑块距离没有换算公式。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 点选无标签、旋转改推外部平台，都是分流结论，不是可执行求解器。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留 AutomationControlled 开关这一个可定位名字。不摘 renderer、vendor 或平台字面量，也没有通过条件。
relations:
  - type: derived_from
    target: ./benru-anti-20260311-01.md#二最基础的图文验证码
tags: [ddddocr, captcha-routing, source-report]
---

# ddddocr 验证码分流：接口、轨迹参数与未闭合分支

这张卡只回答：来源把哪几类验证码收成了可定位的 ddddocr 调用，哪些分支作者自己没有做完。来源是 [2026-03-11 验证码归档](./benru-anti-20260311-01.md#二最基础的图文验证码)。云片 JSONP 卡记录的是另一家的字段角色，不覆盖这里的检测接口。

适用面是来源点名的 ddddocr 图文识别和滑块检测。点选标签、旋转角度、语音密钥、短信和邮箱登录都不在本卡里补完。

<a id="interfaces"></a>
## 接口

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 图文入口是全局初始化的 `DdddOcr()`，注释写明别每次都 new | s1 `ocr = ddddocr.DdddOcr()  # 全局初始化，别每次都new` | source-report | 来源的图文示例 | 未复现当前库 |
| C2 | `classification` 直接吃图片字节 | s1 `res = ocr.classification(img_bytes)` | source-report | 同上 | 未复现识别结果 |

检测入口是 `DdddOcr(det=True)` 的 `detection`。来源把它和 classification 分成两次构造，没有给出同一对象同时做两件事的合同。

<a id="parameters"></a>
## 参数

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C3 | 红字过滤参数是 `color_filter_colors=['red']` | s1 同一片段 | source-report | 来源举的红字例子 | 没有其他颜色 |
| C4 | 检测注释写明 `返回 [[x1,y1,x2,y2], ...]`，单缺口取第一个 | s1 滑块检测段 | source-report | 来源假定只有一个缺口 | 多框时没有选择规则 |
| C5 | 轨迹以 `mid = distance * 3 / 4` 划分加速段 | s1 轨迹函数 | source-report | 这段草稿 | distance 不是由缺口算出的 |
| C6 | 加速段步长是 `random.randint(2, 5)` | s1 同一函数 | source-report | 来源称入门够用 | 不是已验收模型 |

减速段在来源里是 1 到 2，纵向抖动是 -1 到 1。示例拖动距离写成 300，旁边注明要自己计算。本卡不把 300 当成缺口距离。

<a id="decision-flow"></a>
## 分流

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C7 | 点选检测 `只返回坐标，不返回物体的标签`，所以坐标本身不能完成按提示点击 | s1 点选段 | source-report | ddddocr 检测模式 | 来源没有标签模型 |

旋转段的结论是改用外部平台或另找角度模型，没有角度公式。语音段有采样率形态，但密钥占位不进入本卡。短信和邮箱段没有做完的提取规则。

<a id="risk-control"></a>
## 风控开关

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 无感段唯一定位到的启动开关是 `--disable-blink-features=AutomationControlled` | s1 无感段 | source-report | 来源的 Selenium 草稿 | 没有通过条件 |

`selenium-stealth` 的其余关键字来源列了名字，但本卡不摘 renderer 和 vendor 字面量。拖动前晃动鼠标、随机延迟和 2 到 5 秒间隔都是建议，没有失败后的判定。

## 验证与限制

缺的部分：缺口到距离的换算、点选分类、旋转角度、邮箱正则、任何一次实际识别结果。作者写下的“识别率还不到 60%”和“成功率会高不少”保持叙述，不作为本卡结论。
