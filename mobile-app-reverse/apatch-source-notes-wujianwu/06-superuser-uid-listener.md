---
schema_version: 2
id: apatch-source-note-06-superuser-uid-listener
document_type: archive
original_date: "2026-09-05"
archived_date: "2026-10-08"
scope:
  targets: [apatch, kernelpatch]
  client: Android
  version: "APatch main@6ec140e; KernelPatch 0.13.8 bcc8498"
  observed_at: unknown
sources:
  - id: s1
    ref: "https://mp.weixin.qq.com/s?__biz=MzI5NDkwNTAyOQ%3D%3D&mid=2247484795&idx=2&sn=74348f914d39184423a16cb8eb33f521&chksm=ec5af0d1db2d79c7e9f2687ef141c30f636a01f407552e550e70d82a765a53077fe1956efde2#rd"
    basis: source-report

source_completeness: partial
relations: []
tags: [apatch, kernelpatch, source-report]
---

# APatch 源码笔记（六）：谁有资格拿 Root——SuperUser 授权与 uid-listener

吴见午公开笔记，发布日 2026-09-05。来源把结论绑在 APatch `main@6ec140e` 与 KernelPatch `0.13.8`（`bcc8498`）。归档不把作者读源码的结论升级成刷机或运行时验收。

## 清洗与完整性说明

正文用已导出的 Markdown，没有从同伴 HTML 重抽。MD 中的 mmbiz 图为 2 张远程 URL，HTML 中不重复的 mmbiz URL 为 14 个；差额未逐张鉴定，可能含页面装饰，也可能含未进入 MD 的图。缺图没有用文字补。MD 表格分隔行 1，HTML `<table>` 1。远程图未本地化。代码围栏、行号和「源码明确行为 / 作者推测」的原词保留。

<a id="source-body"></a>
## 来源正文

![](https://mmbiz.qpic.cn/mmbiz_png/VRGugOBdueYCWF90mldEsHibOebImzjuEhXWOoIrAUibpGAiaZ44Bo6RjdBq7bAFJsbMqMEfE2oS7lCAJ6hQcmFnVjsH88hghKhA2Buwj5JHCE/640?wx_fmt=png&from=appmsg)

本文基于双仓库交叉核实：**APatch** `main@6ec140e` + **KernelPatch** `tag 0.13.8`（HEAD `bcc8498`）。所有结论附 `仓库:文件:行号`。

## 01 这一篇我们要解决什么问题？

第 5 篇的 `handle_before_execve` 里有一行门禁：`is_su_allow_uid(uid)`——查一张"谁有资格 su"的表。当时我们没有打开它。这张表就是本篇的主角：**SuperUser 授权体系**。

围绕它有三个实际问题：

1. 你在管理器里点一下"允许 Root"，这个决定**流向了哪里**？为什么立刻生效？
2. 手机重启后，**谁还记得**你授过权？授权数据存在哪、会不会丢？
3. App 更新、卸载、多用户切换都会导致 **uid 变化**，授权怎么跟着变而不出错？

## 02 为什么从这里开始？

因为这是整个 Root 体系的"账本"。第 5 篇的提权门禁查它，第 3 篇的 supercall 授权命令写它，第 1 篇的 uid-listener 一辈子都在同步它——三篇埋的线在这里收拢。而且这一篇会解释一个实际使用中的现象：为什么授权过的 App 卸载重装后，权限能"跟"着它走。

## 03 数据模型：一张 CSV，两张内核表

授权体系的存储只有两样东西。**磁盘上一张 CSV**（`/data/adb/ap/package_config`），表头写死在管理器里（`APatch:PkgConfig.kt:17`）：

```
private const val CSV_HEADER = "pkg,exclude,allow,uid,to_uid,sctx"
```

apd 侧有逐字段对应的 Rust 结构（`APatch:apd/src/package.rs:12-20`）：

```
pub struct PackageConfig {
    pub pkg: String,      // 包名
    pub exclude: i32,     // 是否从模块中排除
    pub allow: i32,       // 是否允许 root
    pub uid: i32,         // 目标应用 uid
    pub to_uid: i32,      // 提权到的 uid
    pub sctx: String,     // SELinux 上下文
}
```

**内核里两张哈希表**（kstorage 分组，`KP:scdefs.h:59-60`）：组 0 是 su 授权表（`su_allow_uid_profile` 查的就是它），组 1 是排除表。每条记录都是一个完整的 104 字节 `su_profile`——第 3 篇解剖过的那张"提权名片"。

记住这个分层：**CSV 是权威源（持久），kstorage 是工作副本（易失）**。接下来所有的"同步"，本质都是这两者之间的搬运。

![图1：SuperUser 授权数据流——一次双写、两条重建路径](https://mmbiz.qpic.cn/sz_mmbiz_png/VRGugOBdueZvqWSGwticO6jW595ZlJsRJSUL4s03SJdwbibMNRcG0d01Yaf8og198RiaGdibcDwupqZOgZfso1JZamxKR9ba8U8eU87ib6hS9y7E/640?wx_fmt=png&from=appmsg)

图1：SuperUser 授权数据流——一次双写、两条重建路径

## 04 写入端：点下"允许"的那一瞬间

`SuperUserViewModel.setRootGranted`（`APatch:SuperUserViewModel.kt:198-218`）是授权按钮的落点，它做的是一次**双写**：

```
PkgConfig.changeConfig(newConfig)                        // ① 磁盘：写 CSV
if (granted) {
    Natives.grantSu(app.uid, 0, newConfig.profile.scontext)  // ② 内核：立即生效
    Natives.setUidExclude(app.uid, 0)
} else {
    Natives.revokeSu(app.uid)
}
```

② 通过 JNI 直发 supercall `SUPERCALL_SU_GRANT_UID`（第 3 篇的 0x1100），**当场改写内核表**——这就是"点了立刻生效"的原因。① 负责让这个决定活过重启。

`changeConfig`（`PkgConfig.kt:82-101`）有几个值得停下来看的细节：

```
synchronized(PkgConfig.javaClass) {
    Natives.su()                       // 先给自己提权——写 /data/adb 需要它
    ...
    // Root App should not be excluded
    if (config.allow == 1) {
        config.exclude = 0             // 授权与排除互斥，授权赢
    }
    if (config.allow == 0 && configs[uid] != null && config.exclude != 0) {
        configs.remove(uid)            // ⚠ 排除操作：把整个条目从 CSV 移除！
    } else {
        configs[uid] = config
    }
    writeConfigs(configs)
}
```

那个 `⚠` 标记的分支是一个**双仓库对读才能发现的行为**：把某个 App 设为"排除"时，管理器做的是**删除 CSV 条目**（新的排除状态不落盘），然后只通过 `Natives.setUidExclude` 推进内核的组 1。结合 apd 侧 `write_ap_package_config` 也从不添加排除行，可以得出一个重要推论：**当前写入端语义下，CSV 里永远只有 allow=1 的行；"排除"状态只存在于内核运行时，重启后不会被 CSV 重播恢复**（"内核开机重播不会恢复排除"是基于两侧写入/加载逻辑的推断，源码没有注释说明这是有意还是缺陷——如实记录，不下结论）。

还有一处对比很有意思：apd 的 `write_ap_package_config`（`package.rs:57-100`）写 CSV 用的是**临时文件 + rename 原子替换**（`:60,:92`），最多重试 5 次、每次睡 1 秒；而管理器的 `writeConfigs`（`PkgConfig.kt:68-80`）是普通 `FileWriter` 直写。同一个文件，两个写入端，一种原子一种非原子——谁先谁后写入，就可能读到中间态。这也是 `readConfigs` 里 `Skip malformed package config line`（`:59`）这类防御存在的原因。

## 05 开机重播：内核自己读 CSV

重启之后 kstorage 全空（第 3 篇说过它无持久化），谁来重建？答案可能出乎意料——**是内核自己**。

第 1 篇讲过：内核收到 `post-fs-data before` 事件时执行 `load_ap_package_config()`。这次我们打开它（`KP:kernel/patch/android/userd.c:1214-1403`），它是一个**内核态的 CSV 解析器**：

- `kernel_read_file` 整读文件，超过 10MB 直接拒绝（`:1223-1226`）；
- 逐行解析 6 个字段（`:1268-1274`），uid/to_uid 必须 `kstrtoull` 成功且不超 `UINT_MAX`（`:1287-1312`），sctx 超长截断并警告（`:1360-1369`）——注释还自称 *"CRITICAL FIX"*；
- 然后**按列分派**（`:1372-1385`）：

```
        // Apply configuration with safe sctx buffer
        if (allow) {
            int rc = su_add_allow_uid(uid, to_uid, sctx_buf);
            ...
        }
        // Set exclude flag
        if (exclude) {
            set_ap_mod_exclude(uid, exclude);
        }
```

也就是说，**开机时间线上的"授权重播"根本不经过 apd**：init 注入的 rc 拉起 apd，apd 发出 `post-fs-data before` 回执，内核收到后自己读文件、自己解析 CSV、自己填表。apd 在这个环节只贡献了一声"开始吧"。这是第 1 篇那个"对称设计"（同一份数据两条加载路径）的完整版。

顺带把上一节的推论接上：解析器明明支持 exclude 列（`:1383-1385`），但写入端从不产生这样的行——**两边的管道都修好了，只是上游没水**。

## 06 运行时同步：uid-listener 与"全撤重播"

开机之后，变化还在继续：App 更新、卸载、多用户克隆，都会让 uid 漂移。负责跟进的就是第 1 篇认识过的 uid-listener。这次我们钻进它每次触发的核心动作 `refresh_ap_package_list`（`APatch:apd/src/supercall.rs:202-261`），它是一个教科书式的"**全撤重播**"：

```
let _lock = mutex.lock().unwrap();                   // 进程内互斥

let num = sc_su_uid_nums(skey)?;                     // ① 问内核：现在表里多少人
let mut uids = vec![0 as uid_t; num];
let n = sc_su_allow_uids(skey, &mut uids)?;          // ② 把名单要回来

for uid in &uids {
    if *uid == 0 || *uid == 2000 {
        warn!("[refresh_ap_package_list] Skip revoking critical uid: {}", uid);
        continue;                                    // ③ 关键 uid 跳过（思考题 1）
    }
    sc_su_revoke_uid(skey, *uid);                    // ④ 其余全部撤销
}

synchronize_package_uid()?;                          // ⑤ 修正 CSV（下面细讲）

let package_configs = read_ap_package_config();
for config in package_configs {
    if config.allow == 1 && config.exclude == 0 {
        sc_su_grant_uid(skey, &profile);             // ⑥ 按 CSV 重播授权
    }
    if config.allow == 0 && config.exclude == 1 {
        sc_set_ap_mod_exclude(skey, config.uid, 1);  // ⑦ 重播排除（当前 CSV 不会有这种行）
    }
}
```

不搞增量 diff，直接"清桌重摆"——因为授权条目几十条而已，全量重放的成本远小于增量比对的出错概率，换来的是**内核表永远收敛到 CSV 的状态**。

⑤ 的 `synchronize_package_uid`（`APatch:package.rs:109-180`）是这套机制的"翻译官"，干三件事：

1. **清理**：读 `/data/system/packages.list`，把 CSV 里已经卸载的包 retain 掉（`:131`）——这就是"权限跟着卸载消失"的实现；
2. **改号**：App 重装后 uid 变了，但**只改后半段**（`:152-158`）：

```
if config.uid % 100000 != uid % 100000 {
    let new_uid = config.uid / 100000 * 100000 + uid % 100000;
```

这是 Android 多用户语义：uid = `userId * 100000 + appId`。重播时保留"哪个用户"（前段），只更新"哪个应用"（后段）——**分身 100（工作资料）里装的 App 重装后授权不掉**。

3. **防御**：`:116-118` 有一行难得的注释，值得整段引用：

```
// Skip bad lines instead of `map_while(Result::ok)`: truncating
// at the first error would drop the tail of the list, and the
// retain() below would then revoke grants for those packages.
```

翻译：如果解析 `packages.list` 遇到坏行就截断，列表尾巴会被丢掉，随后 `retain` 会把"看似已卸载"的正常包从 CSV 删掉——**一次解析容错不足，就会变成一次错误撤销授权**。系统间同步代码的容错，从来不只是"优雅"问题。

至于触发端（inotify 盯 `packages.list.tmp` 重命名、1 秒防抖、SIGTERM/SIGINT/SIGPWR 兜底），第 1 篇已逐行精读过，不重复。当时留下的"双启动疑案"（rc 直启一个 + `run_uid_monitor` 再拉一个）现在可以给出完整答案了：两个 uid-listener 进程各自 inotify、各自持**进程内** mutex（`:203`），同一事件会让两者各做一轮"全撤重播"——**冗余但幂等**（重播结果只由 CSV 决定，做两遍结果一样；这是作者推测，源码未声明）。全撤重播的幂等性，恰好把双启动的并发风险吸收掉了。

## 07 kstorage：这张表长什么样

最后看一眼账本本体的实现（`KP:kernel/patch/common/kstorage.c`）：**4 组 × 256 桶**的哈希表（`:19-26`），哈希用黄金分割常数 `did * 0x9e3779b97f4a7c15`（`:31-35`），每组一把 spinlock，删除靠 RCU 回收（`:37-41`）。第 5 篇的 `is_su_allow_uid` 读表时还有一道二次校验（`sucompat.c:87-97`）：取出的 profile 还要 `profile->uid == uid` 才算数。写入函数 `write_kstorage` 里有一行很专业的注释（`:70-72`）：*"Do the potentially-sleeping allocation/copy before entering the RCU read-side critical section below, since vmalloc()/memdup_user() may sleep..."*——先做可能睡眠的分配，再进不可睡眠的 RCU 临界区。内核代码的注释里，最值钱的就是这种"为什么不能换一种写法"。

## 08 常见误区

1. **"授权存在内核里，重启也在"**——错。kstorage 每次开机清空，权威是 CSV；重启后的"记得"全靠内核自己重播 CSV。
2. **"开机时 apd 负责同步授权"**——不，开机重播是内核收到 `post-fs-data before` 后自己读文件（`userd.c:1214`）；apd 只在运行时经手。
3. **"排除列表持久保存"**——当前写入端把排除项从 CSV 移除（`PkgConfig.kt:92-93`），排除只活在内核运行时（重启后的行为是推断项，见第 04 节）。
4. **"授权和排除可以同时设置"**——互斥，授权强制清排除（`PkgConfig.kt:88-91`）。
5. **"refresh 是增量 diff"**——全撤重播，跳过 0/2000，结果幂等。

## 09 本篇源码地图

| 文件 | 本篇中扮演的角色 |
| --- | --- |
| `APatch:apd/src/package.rs` | CSV 权威源：原子读写 + `synchronize_package_uid`（多用户 uid 修正） |
| `APatch:apd/src/supercall.rs` | `refresh_ap_package_list`：全撤重播（跳过 0/2000） |
| `APatch:util/PkgConfig.kt` | 管理器侧 CSV 读写；排除项不落盘的关键分支 |
| `APatch:ui/viewmodel/SuperUserViewModel.kt` | 授权/排除按钮的双写：CSV + JNI 即时生效 |
| `KP:kernel/patch/android/userd.c` | `load_ap_package_config`：内核态 CSV 解析器与开机重播 |
| `KP:kernel/patch/common/kstorage.c` | 4×256 哈希表、RCU 回收、按 offset 写入 |
| `KP:kernel/patch/common/sucompat.c` | `is_su_allow_uid` / `su_add_allow_uid` 等表的读写封装 |

## 10 总结与思考题

这一篇把授权体系的账本翻了个底朝天：**CSV 是唯一的权威源，内核 kstorage 是每次开机由内核自己重建的工作副本**；写入端"双写"（磁盘持久 + supercall 即时生效）；同步端"全撤重播"（跳过关键 uid、幂等、防抖）；`synchronize_package_uid` 用 `% 100000` 语义让授权在卸载清理和多用户重装之间精确存活。以及一个如实记录的发现：排除项当前不落盘，它的持久化管道两端都通、唯独中间断了水。

三道思考题，前提均已核实：

1. `refresh_ap_package_list` 重播时跳过 uid 0 和 2000（`supercall.rs:217-224`）——如果哪天有人"优化"掉了这个跳过，第一次 refresh 后会发生什么？（提示：这两个 uid 的授权是内核开机种子，**不在 CSV 里**，重播不会恢复它们。）
2. `synchronize_package_uid` 的 `config.uid / 100000 * 100000 + uid % 100000`（`package.rs:153`）——为什么不直接采用系统 `packages.list` 给的新 uid？构造一个"直接采用会出错"的场景。
3. 第 06 节引用的那条坏行注释（`package.rs:116-118`）描述了一条事故链：坏行 → 截断 → 错误 retain → 错误撤销。请完整推演一遍：如果 `packages.list` 中间有一行乱码，哪些已授权 App 会丢权限？什么时候能恢复？

下一篇进入安全模型的核心：**《APatch 源码笔记（七）：SuperKey——一把钥匙的安全模型》**。第 3 篇我们看过 `auth_superkey` 的门禁位置，这一篇打开它的实现：为什么说 `hash_key()` 在内核里是个"没人调用的装饰品"？`-S` 存进去的 SHA-256 哈希是怎么"首次命中自动晋升"的？不设密钥时内核生成的随机密钥用的是什么随机源？以及最关键的——管理器 APK 签名是怎么被内核解析验证的，"新默认签名授权"的安全边界到底在哪？

## 复用边界

文件名和行号属于来源阅读的那两份树。作者标明「作者推测」的句子保持为推测。panther user 镜像把 APatch 收进 ROM 的流程是另一篇，目标不同，不要从本篇推出刷机步骤。
