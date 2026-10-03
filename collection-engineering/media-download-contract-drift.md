---
schema_version: 2
id: collection-engineering-media-download-contract-drift
document_type: archive
scope:
  targets:
  - unknown
  client: unknown
  version: unknown
  observed_at: unknown
sources:
- id: s1
  ref: null
  basis: source-report
  citation: '`本地项目分析材料（定位不公开）`（`4479ea78` → `b17b12ee`）、`本地项目分析材料（定位不公开）`（`7077c88f` → `ebb6c4fb`），公开源码增量对照'
  reason: 出处来自原归档来源字段；本地路径已省略，原始材料未随本文公开，本轮未重跑来源实验。
source_completeness: unknown
tags:
- Referer
- CDN
- 编码别名
- 备用 URL
- raise_for_status
- 失败隔离
original_date: '2026-09-27'
archived_date: '2026-09-27'
---

# 媒体下载故障分层：请求上下文、流选择与单项失败隔离

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: `workspace/cv-cat/DouYin_Spider`（`4479ea78` → `b17b12ee`）、`workspace/cv-cat/Spider_XHS`（`7077c88f` → `ebb6c4fb`），公开源码增量对照
> 原始发布时间: 2026-09-27
> 归档日期: 2026-09-27
> 分类: collection-engineering
</details>
>
> 元数据 API 返回成功不代表媒体交付成功。两处下载修复分别落在 CDN 请求上下文与响应结构漂移，不涉及签名算法更新；排障应把 URL 选择、HTTP 响应、文件落盘、批次进度拆开。

## 同样是“视频不能下”，根因可能不在同一层

| 分层 | 本轮源码增量 | 不能从补丁推出的结论 |
|---|---|---|
| 请求上下文 | 抖音下载函数对媒体请求补 `Referer` | API 签名失效，或所有 CDN 都统一校验 Referer |
| HTTP 门 | 图片、视频先 `raise_for_status()` 再开文件 | 2xx 内容一定是正确媒体 |
| URL 选择 | 小红书按编码候选、主 URL、备用 URL 查找 | 候选存在就能下载，或字段永远不改名 |
| 批次隔离 | 抖音重试耗尽后捕获单作品异常，继续后续作品 | 全部媒体已经完成交付 |

上游抖音注释称其在当日遇到无 Referer 的视频 CDN 403；本库没有重发请求，只确认新增请求头和状态检查的调用位置。

## 先找候选流，再区分是否已经下载

小红书旧逻辑只读取 `stream.h264` 第一项。新逻辑优先遍历 `h264`、`EF4`、`h265`、`EF5`，再遍历未识别的编码键；每个流按 `master_url`、`url`、`backup_urls` 第一项选 URL，之后仍保留旧 consumer 兜底。

这里复用的是“偏好列表 + 未知字段回退 + 多字段选择”，不是把别名映射当永久协议。还要注意：代码只选第一个非空候选，没有逐一尝试所有备用地址，也没有验证媒体类型、可解码性或时效。提取成功与下载成功仍须两个状态。

## HTTP 检查要早，交付确认要晚

在 `open()` 前检查 HTTP 状态能防止把明显错误页保存为目标媒体，但不能覆盖：

- 2xx 响应实际为 HTML 或空内容。
- 流式响应中断，已创建的目标文件成为半成品。
- 原子落盘、预期长度或内容摘要未确认。

如需可靠交付，建议使用临时文件、内容检查和完成标记，验证后再发布最终文件；这些并非本次上游补丁已实现的能力。交付链的一般合同见 [spool 与完成标记](./reliable-mac-nas-spool-delivery.md)。

## 单项失败隔离不是“全批成功”

`safe_download_work()` 把下载异常限制在单作品；元数据列表已经积累，Excel 导出和后续作品得以继续。这解决批次中断，却不保证成功计数准确或具备持久重试队列。

更稳妥的复用方式是分别维护 `metadata_ready`、`media_selected`、`download_failed`、`delivered` 等状态，记录可脱敏的错误类别与恢复游标，不把“已写入元数据表”计为“媒体已交付”。本篇没有复制任何生产 URL、会话字段、业务区间或下载日志。

## 固定版本证据与限制

- [DouYin_Spider @ b17b12ee](https://github.com/cv-cat/DouYin_Spider/tree/b17b12ee)：`utils/data_util.py::download_media`、`main.py::safe_download_work`。
- [Spider_XHS @ ebb6c4fb](https://github.com/cv-cat/Spider_XHS/tree/ebb6c4fb)：`xhs_utils/data_util.py::handle_note_info`。

两仓其余增量主要是 README、logo 和赞助信息，不进入技术知识库。本轮只完成静态差异审阅，未运行采集器或验证 CDN 行为。

## 本轮提炼评估

Referer 请求上下文、媒体候选字段回退、HTTP 状态检查位置及单作品失败边界已整理为[媒体下载变更 reference](./media-download-contract-drift-reference.md)。该卡不合并两个项目为同一站点行为，也不把来源差异升级成本轮运行或 CDN 交付验证。

## 提炼说明（379）
retain existing reference。媒体下载变更卡已发布。
来源稿保持 archive。
不扩 CDN 验证。
