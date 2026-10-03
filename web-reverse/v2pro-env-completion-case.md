---
schema_version: 2
id: v2pro-env-completion
document_type: case
original_date: unknown
archived_date: unknown
scope:
  targets: [v2pro]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: notes
    ref: null
    basis: source-report
    citation: 本地教学笔记（定位不公开）
    reason: 正式入库不保留讲次与公开定位；原始材料未随本文公开。
modules:
  - name: validation
    anchor: validation
    sources: [notes]
    basis: source-report
    limits: 缺 locator，未复现。只保留成功定义和三条路径的结果差异。不是 server-accepted，也不是 local-parity。不写环境 API、参数名、signature、token、密钥或 URL。
relations:
  - type: supplements
    target: ./js-obfuscation-boundaries-reference.md#parameters
tags: [v2pro, validation, env-completion]
---

# V2Pro 补环境的成功口径

这是一次 V2Pro 补环境演示的案例，不是普适方法。范围收成 V2Pro、自动化、纯算和补环境。它和网页端 V2 滑块不是同一目标，也不并入已有的阿里云验证码 V2 文章，不抄那批参数。版本号不从标题里的数字去猜。

<a id="validation"></a>

## 问题与范围

V2 与 V2Pro 的差别是多了一种模式。模式的正式枚举值未知。

成功标准是：必须看到数据返回，或页面源码侧的有效结果。只出现滑动成功、验证通过、没有数据，算失败。这个标准不是服务端接受。本仓库没有按它复跑。

## 过程与关键证据

三条路径：

- 浏览器自动化做出过结果。
- 仿人工滑动能到成功态，但不回数据，算失败。
- 纯算法能滑过，但少一段生成，最终也没有数据。字段名未知。纯算因此也没有达到上面的成功标准，更不能写成服务端已接受或批量可用。

材料是已下载包里的图片、脚本和另一种打包文件。扩展名未知，不写成 wasm 或其他后缀。集成方式是从文件夹导入，用命令行调用，少做反复编码。命令本身不进入本文。更早版本里已有一部分同类细节，所以 Pro 这一档更快。算法和密钥未知。

费用上，先解混淆再送模型，否则费用花在解混淆上。这句只和 [混淆边界](./js-obfuscation-boundaries-reference.md) 建立补充关系，不把解混淆步骤写进来。耗时和金额不核对。

没有独立观察，没有请求记录，没有环境 API 名单。能推出的只有：成功定义和「验证通过」不是一回事。材料分不清是不是混入了别的站点经验，所以结论不外推到滑块案例。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 成功是看到数据或页面源码侧的有效结果；只有滑动成功或验证通过算失败 | notes | source-report | 这次演示的口径 | 不是 server-accepted |
| C2 | 浏览器自动化出过结果；仿人工滑动到成功态但无数据，算失败 | notes | source-report | 前两条路径 | 未复现；无 URL |
| C3 | 纯算法能滑过，但缺一段生成，最终没有数据 | notes | source-report | 第三条路径 | 字段名未知；不能写成纯算已通过 |
| C4 | 材料是已下载包里的图片、脚本和另一种打包文件 | notes | source-report | 材料形态 | 扩展名和命令未知 |
| C5 | 先解混淆再送模型是费用上的顺序，不是算法细节 | notes | source-report | 与混淆文的一句关系 | 不把混淆参数写进本案例 |

## 结论与反例

正结果只存在于浏览器自动化这一条，而且没有数据样本。反结果是仿人工滑动和纯算法都没有数据。缺字段、密钥和 URL 是边界，不是待补的参数表。已有阿里云验证码 V2 的请求链和动态 key 是另一批材料，不能拿来填这个缺口。

## 未决项与复用启示

可复用的是成功口径：没有业务数据，就不能把验证通过写成成功。不可复用的是任何环境补丁、signature、token 或 encryption。缺 locator，未复现。
