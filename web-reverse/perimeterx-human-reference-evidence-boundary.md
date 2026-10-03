---
schema_version: 2
id: web-reverse-perimeterx-human-reference-evidence-boundary
document_type: archive
scope:
  targets:
  - perimeterx
  client: unknown
  version: unknown
  observed_at: unknown
sources:
- id: s1
  ref: https://github.com/warterbili/perimeterX_reverse
  basis: source-report
source_completeness: unknown
tags:
- PerimeterX
- HUMAN
- 证据边界
- 版本锁定
- 参考仓
- _px3
original_date: 2026-08-04（浅克隆唯一提交；正文日期多停在 2026-05，skill 正文写到 2026-06-13）
archived_date: '2026-09-30'
---

# PerimeterX 参考仓：结构对照与证据边界

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: `warterbili/perimeterX_reverse` 浅克隆，落在 `storage/references/external-repos/perimeterX_reverse`，commit `b4dd645`（2026-08-04，`Initial commit`）。只保留目录职责、自称与树的差异、许可证和证据边界。
> 原始发布时间: 2026-08-04（浅克隆唯一提交；正文日期多停在 2026-05，skill 正文写到 2026-06-13）
> 归档日期: 2026-09-30
> 分类: web-reverse
</details>
>
> 这份参考仓是按站点写好的求解器和长文档，不是当前浏览器事实。作者的通过记录停在其 SDK 版本窗口里。可复用的是分档、版本锁定和三层验收；生成器、第三方 SDK 快照、抓包和残留口令不进入知识库。

产品命中与观察顺序仍用 [PerimeterX / HUMAN Security PX](./products/perimeterx.md)。本篇不扩展那一页的链路，也不把参考仓写成命中后的必读求解说明。

## 证据等级

| 证据等级 | 本次保留的内容 | 不做的外推 |
|---|---|---|
| 来源自述 | README 自称 v2.0、纯算、五站通过记录，并区分宽档、严档、严档+ | 不把 10/10 当成当前服务端接受 |
| 静态核验 | 743 个文件、目录职责、许可证、自称与树不一致之处；未执行仓库代码 | 确认的是检出内容，不是线上 collector 规则 |
| 独立运行复现 | 本次为 0 | 未安装依赖，未跑 npm script，未发网络请求 |

不归档密钥、代理口令、Cookie、抓包正文、SDK 快照或可执行生成器。

## 仓的位置

| 项 | 值 |
|---|---|
| 上游 remote | `https://github.com/warterbili/perimeterX_reverse` |
| README / BibTeX 写的地址 | `github.com/warterbili/PerimeterX_RE`（与 remote 不一致） |
| 本地路径 | `storage/references/external-repos/perimeterX_reverse` |
| 包字段 | `package.json` 名 `perimeter`，版本 `1.0.0` |
| 与本仓 git 的关系 | `storage/` 不进 Git。article 只收本篇 |

浅克隆把历史压成一次提交。bundle 文档引用的旧 commit 不在这次检出里。

## 目录职责

| 顶层 | 职责 | 静态结论 |
|---|---|---|
| `revers/` | 9 个手写模块，供站点生成器引用 | 在树里。其中取令牌的模块会出网 |
| `stample/` | 五站生成器、锁定 SDK、抓包、活站 demo。目录名是 sample 的稳定错拼 | iFood、Grubhub、Walmart、Total Wine、Academy 都在。根 npm scripts 只挂了前两站 |
| `bundle/` | 按压路径：captcha、WASM、油猴。作者标成归档 | 在树里，且含第二套 `bundle/stample/` 样本 |
| `node_bridge/` | JSDOM 桥，直接跑锁定 SDK，不走 `revers/` | 只有 iFood。其 `start` 指向的文件不在树里 |
| `main/` | 中英技术文档 | 约 2 万行。本篇不转载 |
| `skill/AI_re`、`skill/cdp` | 生成器工作流，以及本机 Chrome CDP 抓包 | 不吸进本仓 skill |
| `bug_report/` | 踩坑。gotcha `01`–`19` | 在树里 |
| `research/` | 六篇短笔记 | 合计约 349 行。自称的数据包和每日漂移 CI 不在树里 |
| `.github/` | Issue / PR 模板 | 没有 workflows |

`node_bridge` 与 `revers/` 是两条实现：前者补浏览器面后跑锁定 SDK，后者是手写模块。研究笔记把自定义 VM 归到对照厂商，主路径按压缩混淆 JS 入库，按压路径另有 WASM。全树没有 `jsvmp` 字样。

## 自称和树不一致

- 版本：徽章 v2.0，根 `package.json` 仍是 `1.0.0`，描述只写 iFood、Grubhub 和 Bundle。
- Academy 写「生成器保持私有」。gitignore 的 `customer_build/` 确实不在树里，公开树里仍有该站生成器和活站脚本。
- CHANGELOG 写了 `stample/screenshots/` 和顶层 `README_EN.md`。截图目录被忽略；英文入口是 `README.md`，中文是 `README.zh.md`。
- `research/` 要求原始数据，并称每日由 `.github/workflows/sdk_drift_detection.yml` 更新。该 workflow、点名的 `analyze.py`、`data/`、`constants_history.json`、`diffs/` 都不存在。
- `skill/AI_re` 的工具数量自相矛盾：front matter、正文标题和 `scripts/` 实际文件数对不上，且含 Python。正文仍指向已不存在的 `skill/AI_re/reverse/`。
- CHANGELOG 称 2026-05-23 清掉了代理和账号。静态检索仍看到非占位代理串和口令赋值，位置包括 `stample/academy/px_cookie/e2e.py`、Grubhub 的研究说明和 business demo、`stample/live_validation/` 的部分笔记。值未打开、未抄录。

## 许可证

`LICENSE` 是双轨，不是单一 SPDX。

| 资产 | 许可 | 本仓处理 |
|---|---|---|
| 代码：`revers/`、站点 `px_cookie/`、`bundle/script/`、`node_bridge/`、`skill/*/scripts/` | AGPL-3.0-only | 不复制进 article 或 skill |
| 文档：`main/`、`bug_report/`、`research/`、README、SKILL | CC BY-NC-SA 4.0 | 只写结构摘要，不转载章节 |
| 客户 SDK 与 `stample/*/sample/`、`bundle/stample/sample/` | 第三方程序和真实抓包 | 留在 storage 检出，不再分发 |

## 可复用边界

这次没有提取可执行代码段。`revers/`、各站 `px_cookie/`、WASM、油猴、JSDOM bridge、解码脚本和抓包都留在上述 storage 检出。

可复用的是下面这张验收口径。它服务「以后碰到同类参考仓或同类产品时怎么记账」，不替代 [产品观察手册](./products/perimeterx.md) 里已经分开的三层结果：cookie 签发、原请求不再被产品拦截、业务链继续前进。

1. 先记 SDK 哈希、抓包日期和作者声明的档位。版本窗口变了，旧通过记录作废。
2. 把来源自述、静态树、独立重跑分成三列。三列不要加成一个成功计数。
3. cookie 签发、产品门通过、业务读回分开写。Walmart 在 README 里被标成产品次级层、主门是另一家 Bot Manager，更不能把产品层记录当成业务通过。
4. 历史 bundle、历史 cookie 和作者 10/10 只作 fixture。活目标仍从 `web-reverse` 取当轮事实。
5. 第三方 agent skill 若要求绕过 case 的 `next`、把 CDP 抓包当成浏览器事实，或把 Node/JSDOM 出参当成默认本地执行，不吸进本仓。
6. 发现非占位代理串或口令赋值时，只记路径，不把值写进文章、索引或对话。

## 与观察手册的分工

| 文档 | 回答的问题 |
|---|---|
| [products/perimeterx.md](./products/perimeterx.md) | 命中特征、先判门、观察顺序、验证口径 |
| 本篇 | 这份 2026-08-04 参考仓里有什么、哪些自称站不住、哪些材料不能入库 |
| storage 检出 | 原始生成器、SDK、抓包。不执行，不复制 |

## 提炼说明（667）
archive_only。PerimeterX 参考仓：结构对照与证据边界 保持 archive。
本轮不另建卡。
