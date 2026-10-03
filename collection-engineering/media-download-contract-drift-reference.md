---
schema_version: 2
id: collection-engineering-media-download-contract-drift-reference
document_type: reference
original_date: '2026-09-27'
archived_date: '2026-10-01'
scope:
  targets:
    - DouYin_Spider media downloader (source report)
    - Spider_XHS media downloader (source report)
  client: Python media collection
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./media-download-contract-drift.md
    basis: source-report
modules:
  - name: request-chain
    anchor: media-request-context
    sources: [s1]
    basis: source-report
    limits: 仅记录固定提交的来源报告；未重放请求或核验 CDN 对请求头的处理。
  - name: decision-flow
    anchor: media-candidate-and-item-failure
    sources: [s1]
    basis: source-report
    limits: 仅描述来源报告中的候选字段顺序与单项异常边界；不代表完整下载流程或通用站点契约。
  - name: validation
    anchor: http-status-boundary
    sources: [s1]
    basis: source-report
    limits: 状态检查不证明响应内容有效或文件完整；未做 CDN、媒体解码或交付验证。
tags:
  - DouYin_Spider
  - Spider_XHS
  - media download
  - Referer
  - encoding fallback
  - backup URL
  - raise_for_status
  - per-item failure isolation
---

# 媒体下载变更参考：请求上下文、候选流与失败隔离

本篇只汇总两处固定源码提交中的媒体下载变化：DouYin_Spider `b17b12ee` 与 Spider_XHS `ebb6c4fb`。二者是不同来源项目的局部报告，不拼成同一站点的端到端请求链。所有结论均为 `source-report`，没有在本轮重放采集、检查上游提交内容或验证 CDN 交付。

<a id="media-request-context"></a>
## 请求上下文

归档报告称 DouYin_Spider 的 `download_media` 为媒体请求补充 `Referer`。这记录的是该固定提交的请求上下文增量，不代表 API 签名变化，也不推出所有 CDN 均要求 `Referer`。

<a id="media-candidate-and-item-failure"></a>
## 候选流与单项失败隔离

归档报告称 Spider_XHS 从只读 `stream.h264` 第一项，改为优先检查 `h264`、`EF4`、`h265`、`EF5`，再遍历未知编码键。每个流依次查 `master_url`、`url`、`backup_urls` 的第一项，随后仍保留旧 consumer 兜底。报告同时明确：这里只选第一个非空候选，不会逐个尝试所有备用地址，也没有验证媒体类型、可解码性或时效。

另一处 DouYin_Spider 变化由 `safe_download_work()` 将下载异常限制在单作品，使已累积的元数据导出和后续作品处理能够继续。这是异常隔离边界，不代表该作品的媒体已交付、批次全部成功或存在持久重试队列。

<a id="http-status-boundary"></a>
## HTTP 状态检查边界

归档报告称图片和视频在打开输出文件前调用 `raise_for_status()`。这可把 HTTP 状态检查放在文件写入之前，但不能证明 2xx 响应就是有效媒体，也不能证明流式响应完整或文件已经完整交付。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 媒体请求补充 `Referer`。 | s1，源文第 43–50 行 | source-report | DouYin_Spider `b17b12ee` | 未重放请求；不代表所有 CDN 的校验规则。 |
| C2 | 媒体流按已知编码优先、未知编码回退，并按字段顺序选择首个 URL 候选。 | s1，源文第 52–56 行 | source-report | Spider_XHS `ebb6c4fb` | 未逐个尝试备用地址；URL 有效性、媒体类型、解码和时效未知。 |
| C3 | 图片、视频在打开文件前检查 HTTP 状态。 | s1，源文第 43–48、58–64 行 | source-report | 源文所述下载补丁；该表项未进一步区分唯一仓库 | 未提供响应或文件样本；不证明 2xx 内容正确或写入完整。 |
| C4 | 单作品下载异常不会直接中断后续作品和已累积元数据导出。 | s1，源文第 68–72 行 | source-report | DouYin_Spider `b17b12ee` | 未运行采集器；成功计数、持久恢复和全批交付未知。 |

## 去重与边界

- 文件落盘、marker、ACK、崩溃恢复和完成门沿用[可重放 spool 与 NAS 交付](./reliable-mac-nas-spool-delivery.md)，本篇不重复这些机制。
- 并发控制、代理租约、一般 HTTP 失败分类、重试与连接池恢复沿用[高并发 HTTP 采集控制面](./high-concurrency-http-collector-control-plane.md)，本篇只记录媒体候选选择和该来源的单作品异常边界。
- 不从上述补丁推断接口 schema、签名或加密参数、设备指纹、风控规则、当前 CDN 行为或服务端接受状态。
