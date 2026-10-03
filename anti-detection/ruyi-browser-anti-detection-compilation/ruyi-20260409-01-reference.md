---
schema_version: 2
id: ruyi-20260409-ads-attach-window
document_type: reference
original_date: '2026-04-09'
archived_date: '2026-10-02'
scope:
  targets: [ads]
  client: web
  version: '151'
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260409-01.md#如果想要-接管任意指纹浏览器自动化-以ads为例需要打开火狐
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 窄扫描的 port 没有绑定。宽扫描三个参数之间有非断行空白，本卡不把它们连成可执行调用。
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只保留第一个 address 的接管、随机端口这句说明，以及不关闭浏览器。没有 ADS 端口算法。
relations:
  - type: derived_from
    target: ./ruyi-20260409-01.md#如果想要-接管任意指纹浏览器自动化-以ads为例需要打开火狐
tags: [ruyipage, ads, static-review]
---

# ruyiPage 接管 ADS 示例的端口边界

这篇卡检索的是：2026-04-09 的示例在已打开的火狐上如何分支，宽扫描写了哪些数，以及它是否关闭浏览器。不提供扫描实现。

<a id="parameters"></a>
## 两段端口

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 窄扫描写的是：find_exist_browsers(start_port=port, end_port=port + | s1，源文件第 65 行 | source-report | 同一次粘连示例 | port 没有前文赋值 |
| C2 | 宽扫描起点原文：start_port=6000 | s1，源文件第 65 行 | source-report | auto_attach 的参数 | 与后两个参数不相邻成无空白源码 |
| C3 | 宽扫描终点原文：end_port=20000 | s1，源文件第 65 行 | source-report | 同上 | 没有占用处理 |
| C4 | 单次超时原文：timeout=0.15 | s1，源文件第 65 行 | source-report | 同上 | 没有单位，也没有总超时 |

<a id="interfaces"></a>
## 接管与不关闭

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 有实例时的调用：attach_exist_browser(browsers[0]["address"], latest_tab=True) | s1，源文件第 65 行 | source-report | find_exist_browsers 返回非空时 | 不说明 address 的形状 |
| C6 | 宽扫描的适用句：ADS / FlowerBrowser 这类会把 remote port 改成随机值的场景。 | s1，源文件第 65 行 | source-report | 未发现实例之后的打印 | 没有这两类产品的端口算法 |
| C7 | 结束句：不自动关闭浏览器，便于继续手工观察。 | s1，源文件第 65 行 | source-report | 该示例的 finally 说明 | 正文没有 page.quit |

## 验证与限制

`ads` 的 interfaces 和 parameters 没有已有卡。`ruyipage` 与 `firefox` 的 interfaces 也是 0。采集器稳定性卡没有 interfaces；它写的是端口探测的跨进程竞态，不是 6000 到 20000 这组参数。第 32-36 行的 BiDi 口号和 151 不另建模块。正文没有 ready 或地址验收，宽扫描失败也没有出口，所以不是流程。
