---
schema_version: 2
id: apatch-source-note-08-selinux
document_type: archive
original_date: "2026-09-06"
archived_date: "2026-10-08"
scope:
  targets: [apatch, kernelpatch]
  client: Android
  version: "APatch main@6ec140e; KernelPatch 0.13.8 bcc8498"
  observed_at: unknown
sources:
  - id: s1
    ref: "https://mp.weixin.qq.com/s?__biz=MzI5NDkwNTAyOQ%3D%3D&mid=2247484826&idx=2&sn=1862c1159606772bab6e45b05012c0ae&chksm=ec5af030db2d792640cedec01eff981d7a5d0b878b5b2ffdeb6df56d5ec468aa5e49a95411a8#rd"
    basis: source-report

source_completeness: partial
relations: []
tags: [apatch, kernelpatch, source-report]
---

# APatch 源码笔记（八）：SELinux——APatch 如何在 enforcing 模式下生存

吴见午公开笔记，发布日 2026-09-06。来源把结论绑在 APatch `main@6ec140e` 与 KernelPatch `0.13.8`（`bcc8498`）。归档不把作者读源码的结论升级成刷机或运行时验收。

## 清洗与完整性说明

正文用已导出的 Markdown，没有从同伴 HTML 重抽。MD 中的 mmbiz 图为 3 张远程 URL，HTML 中不重复的 mmbiz URL 为 18 个；差额未逐张鉴定，可能含页面装饰，也可能含未进入 MD 的图。缺图没有用文字补。MD 表格分隔行 1，HTML `<table>` 1。远程图未本地化。代码围栏、行号和「源码明确行为 / 作者推测」的原词保留。

<a id="source-body"></a>
## 来源正文

![](https://mmbiz.qpic.cn/mmbiz_png/VRGugOBdueaicWJfkg2BJic64iaJmahs1XHtvWA8udkmBicFEGUPwneDutulc2BJFicr6ic4KLYYTtXCQXkuP63TTkibycsRicauvQTiasPfOBA2ye84/640?wx_fmt=png&from=appmsg)

本文基于双仓库交叉核实：**APatch** `main@6ec140e` + **KernelPatch** `tag 0.13.8`（HEAD `bcc8498`）。所有结论附 `仓库:文件:行号`。

## 01 这一篇我们要解决什么问题？

到本篇为止，Root 权限体系阶段还剩最后一堵墙。前几篇我们已经把 uid 提到 0、capability 拉满、seccomp 关掉——但 Android 上真正的"最终 Boss"是 SELinux：即使你是 root，策略里没写的操作照样被拒。APatch 对付它的方式出乎意料地"双轨"：**既改"法律"（用户态注入规则），又换"法官"（内核替换执法函数）**。

三个问题：

1. 提权成 root 之后，还有哪些操作会被 SELinux 拦住？为什么需要**两层**机制，一层不行吗？
2. 管理器设置里那个"隐藏 SELinux 状态"的开关，内核里到底藏了什么、怎么藏的？
3. 模块自带的 `sepolicy.rule` 是怎么被逐条执行的？文件标签又是谁在修？

## 02 背景：SELinux 三十秒

SELinux 是强制访问控制（MAC）：每个进程带**安全上下文**（如 `u:r:magisk:s0`），每个文件带**类型标签**（如 `u:object_r:system_file:s0`，存在 xattr `security.selinux` 里）；能不能访问，由策略里的一条条 `allow` 规则说了算，与 uid 无关。Android 全系统 enforcing 模式。运行链路上有三个关键节点：**判定函数** `avc_denied`（说"不"的地方）、**审计函数** `slow_avc_audit`（把拒绝写成 `avc denied` 日志）、**热加载接口** `/sys/fs/selinux/load`（写入新策略立即生效，不用重启）。记住这三个名字，本篇反复出现。

## 03 第一层：改"法律"——规则注入

开机四阶段的第一阶段里（第 1 篇 17 步的头部），apd 做了这件事（`APatch:apd/src/event.rs:50-54`）：

```
let mut sepol = get_policy_main(&["magiskpolicy".to_string(), "--live".to_string()])?;
sepol.magisk_rules();
sepol
    .to_file("/sys/fs/selinux/load")
    .context("Cannot apply policy")?;
```

三步：**读现行策略 → 套用一组内置规则 → 写回热加载**。逐层拆：

`get_policy_main`（`APatch:apd/src/sepolicy.rs:98-121`）是 magiskpolicy 的解析入口，不给 `--load` 时默认 `SePolicy::from_file("/sys/fs/selinux/policy")`——**把内核正在执行的策略原文读出来**。`SePolicy` 这个类型来自外部的 `policy` crate（Cargo.toml 里以固定 rev 锁定的 `ap_policy`），是 Magisk magiskpolicy 的 Rust 移植。`magisk_rules()` 套用的就是与 Magisk 同源的那组规则：放行 magisk 域对各类文件类型的操作、允许 `setcon` 等等（规则本体在 crate 里，本仓库不展开）。

`to_file("/sys/fs/selinux/load")` 是内核的标准热加载接口——改完即生效，System Server 还没起来就已经活在"新法律"之下。

**一段值得知道的版本史**：这套逻辑曾经是"调外部二进制"——早期代码用 `fork_for_result` 执行 `/data/adb/ap/bin/magiskpolicy --magisk --live`（git 历史 31e2d61 之前），后来才内置为进程内调用（commit 31e2d61 *"apd: Built in implementation of magiskpolicy"*）。但 `/data/adb/ap/bin/magiskpolicy` 这个 symlink 至今仍在创建（第 2 篇的 `ensure_binaries`）——它服务的是另一条路：模块脚本和用户直接敲 `magiskpolicy` 命令。同一个内置实现，两个入口：进程内函数调用（开机自用）和 argv[0] multicall（对外 CLI，`sepolicy.rs:71-76` 的 `policy_main -> !`，第 2 篇的 never 类型）。

模块的**私有规则**走的是第三条路（`APatch:apd/src/module.rs:184-198`）：

```
pub fn load_sepolicy_rule() -> Result<()> {
    foreach_active_module(|path| {
        let rule_file = path.join("sepolicy.rule");
        if !rule_file.exists() {
            return Ok(());
        }
        let mut _sepol = get_policy_main(&[
            "magiskpolicy".to_string(),
            "--live".to_string(),
            "--apply".to_string(),
            rule_file.display().to_string(),
        ])?;
        ...
```

每个启用模块的 `sepolicy.rule` 逐个"重读现行策略 → 追加本模块规则 → live 加载"。注意语义：**每条规则都基于"上一条加载完"的最新现行策略**，模块之间互不覆盖。

## 04 第二层：换"法官"——执法函数替换

如果规则注入就够了，KernelPatch 不会再去 hook 判定函数。第 5 篇我们逐行读过 `avc_denied_replace`（`KP:accctl.c:181-211`），这次从架构视角重新看它。判定被拒时，替换函数做两级检查：

1. **全局白名单**：调用者进程的 secid 等于 `all_allow_sid`（默认上下文 `u:r:kp:s0`，`scdefs.h:86`，可经 `SUPERCALL_SU_SET_ALLOW_SCTX` 换）→ 全放行；
2. **任务级标记**：`task_ext` 上的 `sel_allow` / `priv_sel_allow` 标志（第 5 篇 `commit_su` 时打上）→ 全放行；

都命中不了？调用原函数照常拒绝。放行的同时 `avd->allowed = 0xffffffff`、审计清零（`:203-210`）——`slow_avc_audit` 也被换成静音版（`:217-238`），两者都在 `before_rest_init` 的 `bypass_selinux` 安装（`patch.c:79`，第 4 篇时间线）。

**为什么两道防线缺一不可？** 我的理解（作者推测 + 架构分析）：规则注入改的是"静态法律"，覆盖不到两类场景——策略加载完成**之前**的时间窗口，以及未来运行中出现的、规则没穷举到的上下文组合。而执法替换不修改策略本身：**策略保持原封不动**——这一点看似保守，实则是为下一节的 `selinux_hide` 铺路：只有"法律真的没改"，才谈得上"对外展示没改过的法律"。两层各司其职：规则让系统**合作**，替换让合作**不打折**。

顺带一个精妙细节：`commit_common_su` 里那句 `ext->sel_allow = !!set_security_override_from_ctx(new, sctx)`（`accctl.c:113`）——`sel_allow` 标志**只有在上下文转换成功时才是 1**。转换失败（比如策略里根本没这个域）意味着提权进程的 secid 没换成功、执法标记也没了——双层机制自动退回"老实人"状态，宁可不可用也不留一个上下文混乱的特权进程。

## 05 selinux_hide：改完法律，还要装作没改

管理器设置里有个开关（写标记文件 `/data/adb/ap/selinux_hide`），内核侧对应一整个 553 行的特性模块 `selinux_hide.c`。它的头注释（`KP:selinux_hide.c:1-25`）浓缩得像论文摘要：

> *"On the 4.19..6.3 range the context/access/setprocattr hooks answer against a deep copied [clean policy] ... while the live policy is still untouched, so a root app sees the pre-modification policy. Apps (uid >= 10000) also see a fake /sys/fs/selinux/status (enforcing=1, clean seqno), hiding permissive / disabled SELinux and policy reloads."*

翻译成检查清单，它对普通 App（uid ≥ 10000）隐藏了三样东西：**策略被改过**（回答查询时用快照里的干净策略）、**SELinux 被放过假**（伪造的 status 文件：永远 enforcing=1、序列号干净）、**策略被重载过**（seqno 不涨）。仅支持 4.19+ 内核，更低版本强开也是空操作。

而它的驱动方式，正是第 1 篇埋的那条线——**post-fs-data before/after 双事件**（`selinux_hide.c:463-490`）：

```
    if (lib_strcmp(args, "before") == 0 || args[0] == '\0') {
        struct file *filp = filp_open(KP_SELINUX_HIDE_FILE, KP_O_RDONLY, 0);
        if (!IS_ERR(filp)) {
            ...
            selinux_hide_init();              // 解析 SELinux 子系统符号
            int src = selinux_sepolicy_snapshot();  // 趁"法律"还没改，拍快照
            selinux_hide_approved = true;
        }
    } else if (lib_strcmp(args, "after") == 0) {
        if (selinux_hide_approved) {
            int rc = selinux_hide_enable();   // 等改完了，再装"说谎"的钩子
```

注释把时序动机写得明明白白：*"the live policy is still the untouched boot policy here: deep-copy it ... Hooks are installed at 'after', once apd/Magisk have finished their policy reloads."*——**快照必须抢在 apd 注入规则之前拍**（晚了拍到的就是脏的），**钩子必须等注入完成再挂**（早了谎就圆不上）。第 1 篇思考题问过"内核为什么在 before 干活、after 什么都不干"，现在答案完整了：before/after 这对回执，就是为这种"改之前取证、改之后动工"的需求设计的。

开关的控制通道有两条：标记文件（开机判定）+ supercall `CONTROL_FEATURE` 命令传 `"selinux_hide"`（`sucompat.c:67-69` → `selinux_hide_control`，支持运行时查询/开/关）。至于"为什么要藏"——对齐到使用场景，这是 Root 检测对抗（策略篡改和 status 异常是常见检测点）的组成部分；源码不评论动机，本文也不越界。

## 06 restorecon：文件标签的善后组

前两节解决"进程域"的问题，还有"文件类型"的一半：模块安装进 `/data/adb` 的文件，标签要么是 `adb_data_file`（太宽，策略不认它当系统文件），要么干脆是 `unlabeled`。`restorecon.rs`（全文 82 行）负责贴标签：

```
pub const SYSTEM_CON: &str = "u:object_r:system_file:s0";
pub const ADB_CON: &str = "u:object_r:adb_data_file:s0";
pub const UNLABEL_CON: &str = "u:object_r:unlabeled:s0";
```

开机时的 `restorecon()`（`:77-81`）只做两件事：给 `/data/adb/apd` 本体贴 `adb_data_file`（它必须能被 init 域执行），然后遍历 `MODULE_DIR`，只把 unlabeled/空的补成 `system_file`（`restore_syscon_if_unlabeled`，`:65-75`）——注意"只补缺、不覆盖"：模块自己设过标签的文件一律尊重。而模块**安装时**走的是另一个更强的函数 `restore_syscon`（`:56-63`），把模块 `system/` 树全部强制贴成 `system_file`（第 10 篇安装流程会再见到它）。遍历用 jwalk 且显式 `Serial`——SELinux xattr 写入是慢操作，这里不开并行是刻意的保守。

## 07 时序总图

![图1：SELinux 双轨总图——用户态改法律、内核换法官、回执管叙事](https://mmbiz.qpic.cn/mmbiz_png/VRGugOBduea3Fhklibj8GfqffZfn7MypibccCPF9lnP6Umdk9YHgTrSvicT8zKmnnbUApOTPIic2oEiaX09TdYhjGoAgrG0qdFiaaUMuZucpWdJ14/640?wx_fmt=png&from=appmsg)

图1：SELinux 双轨总图——用户态改法律、内核换法官、回执管叙事

把 SELinux 相关的所有动作钉回第 1 篇的 17 步时间线（全部已核实）：

![图2：SELinux 动作钉回 17 步时间线（更早 → post-fs-data → 事件回执）](https://mmbiz.qpic.cn/mmbiz_png/VRGugOBdueavMRem1yzL67OhSVFIupdaA2uIhuAJ2x0YXwP2nf0a4kRgpyjlhzicCtMgcQ36ZcqQXhqqAVwvGkMJcVVmo0ALSsgprDicWhAwY/640?wx_fmt=png&from=appmsg)

图2：SELinux 动作钉回 17 步时间线（更早 → post-fs-data → 事件回执）

四类角色、三个层次，各就各位——这就是"enforcing 模式下生存"的完整答案：**法律可以改但要趁早且留证（快照），法官被换但只对持标记者网开一面，文件标签靠善后组逐个补齐**。

## 08 常见误区

1. **"APatch 把 SELinux 调成了 permissive"**——没有。全局 enforcing 原样保持；放行是 `avc_denied` 替换函数对持标记进程的点状行为，伪造的 status 甚至坚称 enforcing=1。
2. **"规则注入是唯一的防线"**——还有执法替换层；且"策略保持干净"本身是 selinux_hide 的前提，两层互为因果。
3. **"提权后能从 avc denied 日志看到痕迹"**——放行路径审计清零（`accctl.c:208-209`），审计函数也被静音。
4. **"sepolicy.rule 是模块标配"**——可选；有就逐个加载，没有跳过（`module.rs:187-189`）。
5. **"restorecon 会覆盖模块文件的自定义标签"**——开机路径只补 unlabeled，已设标签的不动（`restorecon.rs:68-72`）。

## 09 本篇源码地图

| 文件 | 本篇中扮演的角色 |
| --- | --- |
| `APatch:apd/src/sepolicy.rs` | magiskpolicy 内置实现：规则注入三步、`--apply`、multicall 入口 |
| `APatch:apd/src/restorecon.rs` | 文件标签善后：三常量、lsetfilecon、只补 unlabeled |
| `APatch:apd/src/module.rs:184` | per-module `sepolicy.rule` 增量加载 |
| `KP:kernel/patch/common/accctl.c` | `bypass_selinux`：avc_denied/slow_avc_audit 替换与两级放行 |
| `KP:kernel/patch/common/selinux_hide.c` | 干净策略快照 + 伪造 status + context/access 钩子 |
| `KP:kernel/patch/common/sucompat.c:60` | `kp_control_feature_sc`：selinux_hide 的运行时开关 |

## 10 总结与思考题

这一篇合上了 Root 权限体系阶段的最后一页。APatch 对 SELinux 的策略是一套精密的双层系统：**用户态改"法律"（读现行 → 注规则 → 热加载，模块规则增量叠加），内核换"法官"（avc_denied 只对持标记进程网开一面，审计同步清零）**；在两者之上还有第三层叙事管理——selinux_hide 趁"法律"未改时拍快照、改完再挂说谎钩子，让 root 检测者看到的是一个"从未被动过"的 SELinux。而文件标签的善后组（restorecon）遵循"只补缺、不越权"的克制。三层各自的时序都卡在 post-fs-data before/after 这对回执上——第 1 篇那个"尽力而为的通知"，到这里你看懂了它真正的分量。

三道思考题，前提均已核实：

1. `selinux_hide_post_fs_data` 的注释说快照在 "before" 拍、钩子在 "after" 装（`selinux_hide.c:476-490`）——如果反过来（before 装钩子、after 拍快照），各会错在哪一步？（提示：apd 在两者之间干了什么。）
2. `restorecon.rs` 开机路径只补 unlabeled（`:65-75`），而模块安装路径 `restore_syscon` 全量强制覆盖——两种策略分别匹配什么场景？（提示：安装时模块 `system/` 树的标签是谁写的、可不可控。）
3. `accctl.c:113` 的 `ext->sel_allow = !!set_security_override_from_ctx(new, sctx)`——如果传入的 sctx 在策略里不存在，转换失败后这个提权进程处于什么状态？它的 uid、capability、SELinux 各是什么？这是缺陷还是自洽设计？

至此"Root 权限体系"阶段（第 5～8 篇）收官。下一篇开启"模块系统"阶段：**《APatch 源码笔记（九）：APModule 全景——目录、约定与生命周期总览》**。我们终于要正面回答那个从第 1 篇就反复擦肩而过的问题：`/data/adb/modules/` 里那一堆文件夹，凭什么就能改变系统？`disable`/`update`/`remove` 三个旗标文件的协议、module.prop 的字段、与 Magisk 模块的兼容边界——模块世界的地图将在下一篇完全展开。

## 复用边界

文件名和行号属于来源阅读的那两份树。作者标明「作者推测」的句子保持为推测。panther user 镜像把 APatch 收进 ROM 的流程是另一篇，目标不同，不要从本篇推出刷机步骤。
