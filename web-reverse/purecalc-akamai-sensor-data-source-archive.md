---
schema_version: 2
id: akamai-purecalc-sensor-data-dvc-vmp-source-archive
document_type: archive
original_date: unknown
archived_date: '2026-10-13'
scope:
  targets: [akamai]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: null
    basis: source-report
    citation: AI纯算akamai
    reason: 原稿末尾注明转载，但本 Public 归档不保留来源 URL，且未对外部出处作独立核验。
source_completeness: partial
tags: [akamai, sensor-data, dvc, vmp, source-report]
---

# AI 纯算 Akamai

## 收录说明

原稿记录了一条 Akamai `sensor_data` 脱混淆、生成链分析与 `mst.dvc` VMP 反编译思路。本文按来源材料提取可复用的算法关系和作者自述的验证边界，不是独立复现报告，也不是当前目标的运行时事实。

## 清洗与完整性说明

- 原稿中的浏览器/硬件指纹对象、User-Agent 字面量、事件轨迹、Cookie/会话值、生成样本和目标 URL 均未复制到 Public 文档。
- 代码、混淆常量、字符表、密钥值及原始 trace 片段未完整保留；本文仅整理足以定位来源结论的结构性描述，因此标为 `partial`。
- 作者报告的 opcode 覆盖、对拍结果及浏览器样本相等均保持 `source-report`；本轮未运行目标脚本、VM、浏览器或服务端请求。

## 来源正文

<a id="deobfuscation"></a>
### 一、AST 反混淆与定位

来源先将 JS 处理成可读结构，再沿 `sensor_data` 的明文对象和生成位置定位逻辑。作者列出的静态处理顺序包括文件 hash 校验、静态求值字面量、变量提升与函数内联、常量替换和折叠、闭包还原、数组引用简化、控制流平坦化还原及运行时字符串解密。字符串还原后，来源称可直接按字段名追到对象组装处。

这只是来源作者描述的分析路径；本文不声称每个 AST 变换均在本轮复跑，也不补写缺失代码。

<a id="sensor-data-generation"></a>
### 二、`sensor_data` 的变换链

来源把明文环境对象序列化后描述为三步变换：

1. 以 `JSON.stringify` 序列化对象。
2. 以 `key1` 调用来源标记为 `fAt(902)` 的变换；作者描述为按冒号分段并两两交换。
3. 以 `key0` 调用 `Tg` 做字符替换；来源称该步骤在 92 字符表中循环移位。

来源随后把版本信息、计时/状态字段和变换后的正文拼成 `sensor_data`。本文不保存具体字段值、字符表、密钥或密文样本；上述只说明来源声称的处理顺序，不等于算法已复现或服务端接受。

<a id="dvc-vmp"></a>
### 三、`mst.dvc` 首段与 VMP

来源指出 `mst.dvc` 的首段由 VMP 字节码产生，并称反编译后识别出四个函数入口：`Fz`（目标 `dvc` 段）、`GU`（清理 User-Agent）、`VI`（字符串 hash）和 `ms`（转二进制串）。作者给出的纯算概述是：将 User-Agent、起始时间和事件数参与 hash；再用自定义字符表及另一层 hash 构造头尾片段。来源还称某个 `Math.random()` 中间项会代数抵消。

上面的输入类别与算法概述来自作者文本，未保留原始指纹、样本、字符表、字节码或实现代码；它们不能用于推断其他版本或其他 Akamai 部署。

<a id="validation-and-limits"></a>
### 四、来源自述的验证与失败边界

作者自述已判定 42 个 opcode，且称运行时指令 trace 与静态反汇编逐条吻合；还报告纯算结果与原 VM 在 312 组输入上相同，并与一条浏览器观测值相同。上述数字与结果仅是来源自述：本文没有测试夹具、日志或代码可供独立复核，因此不得写成当前验证事实。

来源同时明确说，本地生成的 `sensor_data` 曾未被服务端接受；其反解程序用于把浏览器值与本地生成值还原后逐字段比较，定位环境对象和事件生成差异。原文把后续 `abck` 状态变化及 `sbsd` 补环境仍列为待完成内容，本归档不声称已跑通完整链路或达到 `serverAccepted`。

## 复用边界

这份材料适合为 Akamai `sensor_data` 字段参考提供来源线索，尤其是“对象序列化 → 重排 → 字符替换”的作者描述，以及 `mst.dvc` 首段的 VMP 来源边界。来源没有为本轮提供可审计实现，动态环境字段、事件轨迹、Cookie、目标版本和服务端接受条件均未知；需要使用时应重新针对当前版本取证与验收。
