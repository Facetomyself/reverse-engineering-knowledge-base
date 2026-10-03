---
schema_version: 2
id: node-dom-env-library-selection
document_type: reference
original_date: "2026-05-19"
archived_date: "2026-10-02"
scope:
  targets: [node-dom-env, happy-dom, jsdom, vm2]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./benru-web-20260519-01.md#一张表看清楚"
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只记录来源的选择界限和库缺口。没有目标站点，也没有库版本。Canvas 一句不扩展成检测面。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 体积和首次加载都是来源数字。对照表使用约数。本轮没有称重或计时。
relations:
  - type: derived_from
    target: "./benru-web-20260519-01.md#一张表看清楚"
tags: [node-dom-env, happy-dom, jsdom, vm2]
---

# Node 补环境四条路线的来源界限

这张卡只回答：来源如何在手补、happy-dom、jsdom、vm2 之间划分场景，以及它写下的体积和首次加载。不记录示例 UA 或 cookie。附录的玩具函数没有摘要值，不单列参数。

<a id="decision-flow"></a>
## 按缺口选择

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源把补环境定义成在 Node 里模拟缺失 API。quote: 补环境，就是在 Node 里把这些缺失的 API 模拟出来。 | s1 ./benru-web-20260519-01.md:78 | source-report | 这篇比较 | 清单不是某站调用集 |
| C2 | canvas 在清单里被注明为绘图（指纹检测）。quote: canvas         — 绘图（指纹检测） | s1 ./benru-web-20260519-01.md:74 | source-report | API 清单 | 没有指纹算法 |
| C3 | 手补的适合场景写成依赖不超过 10 个浏览器 API。quote: 不超过 10 个 | s1 ./benru-web-20260519-01.md:103 | source-report | 手补 | 作者划分，未测量 |
| C4 | 手补的 cookie 被写成只是字符串，不会联动更新，有些网站会检测这些细节。quote: 只是个字符串，不会联动更新。有些网站会检测这些细节。 | s1 ./benru-web-20260519-01.md:101 | source-report | 手补 | 未点名站点 |
| C5 | 十几个 DOM API 时，来源写手补就有点遭不住了。quote: 如果加密函数调了十几个 DOM API，手补就有点遭不住了。 | s1 ./benru-web-20260519-01.md:111 | source-report | 从手补换库 | 十几个没有精确数 |
| C6 | happy-dom 被写成不模拟 Canvas、WebGL。quote: Canvas、WebGL 这些它不模拟。 | s1 ./benru-web-20260519-01.md:128 | source-report | happy-dom | 未核对库版本 |
| C7 | happy-dom 的适合区间写成 10-30 个 DOM API。quote: 10-30 个 DOM API | s1 ./benru-web-20260519-01.md:130 | source-report | happy-dom | 更复杂时没有另给界限 |
| C8 | jsdom 一段写改 cookie 之后也会同步。quote: 也会同步 | s1 ./benru-web-20260519-01.md:147 | source-report | jsdom | 比较对象在上一行，本轮未跑 |
| C9 | 来源写 jsdom 跑不了 Webpack 打包后的 Vue/React 应用。quote: 跑不了 Webpack 打包后的 | s1 ./benru-web-20260519-01.md:149-150 | source-report | jsdom | 下一物理行才是 Vue/React 应用。没有失败栈 |
| C10 | vm2 被写成在隔离的 V8 虚拟机里运行不可信代码。quote: 在一个隔离的 V8 虚拟机里运行不可信代码 | s1 ./benru-web-20260519-01.md:160 | source-report | vm2 | 没有版本 |
| C11 | 来源写隔离是它的核心价值，不是补环境本身。quote: 隔离是它的核心价值，不是补环境本身 | s1 ./benru-web-20260519-01.md:172 | source-report | vm2 | 只是这段评价 |
| C12 | 来源写 2023 年曝过逃逸漏洞，虽然已经修复了。quote: 2023 年曝过逃逸漏洞，虽然已经修复了 | s1 ./benru-web-20260519-01.md:168 | source-report | vm2 | 没有漏洞编号，未核对修复 |

<a id="parameters"></a>
## 来源写下的体积和加载

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C13 | happy-dom 写成体积只有 3MB，首次加载 200ms。quote: 体积只有 3MB，首次加载 200ms。 | s1 ./benru-web-20260519-01.md:124 | source-report | happy-dom | 表内是约数，未测量 |
| C14 | jsdom 写成 15MB，首次加载 800ms。quote: 15MB，首次加载 800ms | s1 ./benru-web-20260519-01.md:149 | source-report | jsdom | 表内是约数 |
| C15 | 对照表把 vm2 写成 ~3MB。quote: ~3MB | s1 ./benru-web-20260519-01.md:183 | source-report | vm2 | 作者表格 |
| C16 | 同一行把 vm2 首次加载写成 ~100ms。quote: ~100ms | s1 ./benru-web-20260519-01.md:183 | source-report | vm2 | 没有测试环境 |

## 验证与限制

近邻查询里，node-dom-env、happy-dom、jsdom、vm2 的 decision-flow 和 parameters 都没有已有卡片。happy-dom 不模拟 Canvas 和 WebGL 只说明库缺口，不新增 canvas 检测模块。附录称四种写法结果相同，但没有摘要，不能当验收。体积、加载时间和 2023 年逃逸都保持 source-report。
