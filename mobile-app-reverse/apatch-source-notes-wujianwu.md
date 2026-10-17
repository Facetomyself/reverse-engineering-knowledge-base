---
schema_version: 2
id: apatch-source-notes-wujianwu
document_type: archive
original_date: "2026-09-02/2026-09-07"
archived_date: "2026-10-08"
scope:
  targets: [apatch, kernelpatch]
  client: Android
  version: "APatch main@6ec140e; KernelPatch 0.13.8 bcc8498"
  observed_at: unknown
sources:
  - id: s1
    ref: "https://mp.weixin.qq.com/s?__biz=MzI5NDkwNTAyOQ%3D%3D&mid=2247484751&idx=1&sn=33a39f61aa89b8661225cf5b846e8718&chksm=ec5af0e5db2d79f3f33260f79949d1e460be24000bb7622454871db9f2396f96d907e54b98dc#rd"
    basis: source-report
source_completeness: partial
relations:
  - type: supplements
    target: ./xfq-aosp-rom-compilation/xfq-20260626-02-procedure.md#prerequisites
tags: [apatch, kernelpatch, source-notes]
---

# 吴见午 APatch 源码笔记（一至十）

这是十篇公开笔记的目录，不是新的源码结论。每篇仍单独成文。来源版本是 APatch `main@6ec140e` 与 KernelPatch `tag 0.13.8`（HEAD `bcc8498`）。作者把「源码明确行为」和「作者推测」分开写；归档不把任一处升级成运行时事实。

已有的 [panther user 构建集成流程](./xfq-aosp-rom-compilation/xfq-20260626-02-procedure.md#prerequisites) 回答的是把某一版 APatch 收进指定 ROM。那不是这十篇的目标，版本针脚也不同。

## 清洗与完整性说明

笔记八的带日期 Markdown 与 `unknown-time_` Markdown 字节相同，只收带日期那一份。两份 HTML 哈希不同，都留在 pending，不从 HTML 重抽正文。

下表是图和表的核对。表格分隔行与 HTML `<table>` 数量一致。图只保留 MD 里已经出现的远程 mmbiz URL，差额不补写。

| 篇 | MD mmbiz | HTML 不重复 mmbiz | MD 表 | HTML table |
|---|---:|---:|---:|---:|
| `01-event-boot-stages.md` | 10 | 46 | 1 | 1 |
| `02-apd-multicall.md` | 3 | 18 | 3 | 3 |
| `03-supercall.md` | 5 | 26 | 2 | 2 |
| `04-bootimg-kpimg.md` | 5 | 26 | 1 | 1 |
| `05-su-execve.md` | 2 | 14 | 1 | 1 |
| `06-superuser-uid-listener.md` | 2 | 14 | 1 | 1 |
| `07-superkey.md` | 2 | 14 | 2 | 2 |
| `08-selinux.md` | 3 | 18 | 1 | 1 |
| `09-apmodule.md` | 3 | 18 | 3 | 3 |
| `10-module-zip-install.md` | 2 | 14 | 1 | 1 |

系列没有单独的前提、步骤、输出、验收和失败出口，所以不另写 procedure，也不把十篇压成一张模块卡。

<a id="source-body"></a>
## 篇目

| 发布日 | 篇 | 来源要回答的问题 |
|---|---|---|
| 2026-09-02 | [APatch 源码笔记（一）：从 event.rs 看懂开机四阶段](apatch-source-notes-wujianwu/01-event-boot-stages.md) | event.rs 开机四阶段 |
| 2026-09-03 | [APatch 源码笔记（二）：apd 到底是什么？从 main.rs 追踪守护进程的启动与 multicall 设计](apatch-source-notes-wujianwu/02-apd-multicall.md) | apd multicall |
| 2026-09-04 | [APatch 源码笔记（三）：没有 ioctl、没有 netlink——supercall 通信机制解剖](apatch-source-notes-wujianwu/03-supercall.md) | supercall |
| 2026-09-04 | [APatch 源码笔记（四）：boot.img 是怎么被改的——kptools 注入与 kpimg 的开机自举](apatch-source-notes-wujianwu/04-bootimg-kpimg.md) | boot.img / kpimg |
| 2026-09-05 | [APatch 源码笔记（五）：su 是怎么来的——从 execve hook 到 root_shell](apatch-source-notes-wujianwu/05-su-execve.md) | su / execve |
| 2026-09-05 | [APatch 源码笔记（六）：谁有资格拿 Root——SuperUser 授权与 uid-listener](apatch-source-notes-wujianwu/06-superuser-uid-listener.md) | SuperUser / uid-listener |
| 2026-09-06 | [APatch 源码笔记（七）：SuperKey——一把钥匙的安全模型](apatch-source-notes-wujianwu/07-superkey.md) | SuperKey |
| 2026-09-06 | [APatch 源码笔记（八）：SELinux——APatch 如何在 enforcing 模式下生存](apatch-source-notes-wujianwu/08-selinux.md) | SELinux |
| 2026-09-07 | [APatch 源码笔记（九）：APModule 全景——目录、约定与生命周期总览](apatch-source-notes-wujianwu/09-apmodule.md) | APModule 生命周期 |
| 2026-09-07 | [APatch 源码笔记（十）：一个模块 ZIP 的安装之旅本文基于双仓库交叉核实](apatch-source-notes-wujianwu/10-module-zip-install.md) | 模块 ZIP 安装 |

## 复用边界

行号会随仓库提交变化。思考题是作者留下的练习，不是本库已经做完的实验。不收录 SuperKey 样值；来源讨论的是模型，不是一把可用的钥匙。
