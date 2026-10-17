---
schema_version: 2
id: apatch-source-note-05-su-execve
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
    ref: "https://mp.weixin.qq.com/s?__biz=MzI5NDkwNTAyOQ%3D%3D&mid=2247484795&idx=1&sn=06f90629839034035b8b8e5aecc43b87&chksm=ec5af0d1db2d79c7814c724c667a998fc5910638c5a269e6dac279edafec528932dd776a9dc0#rd"
    basis: source-report

source_completeness: partial
relations: []
tags: [apatch, kernelpatch, source-report]
---

# APatch 源码笔记（五）：su 是怎么来的——从 execve hook 到 root_shell

吴见午公开笔记，发布日 2026-09-05。来源把结论绑在 APatch `main@6ec140e` 与 KernelPatch `0.13.8`（`bcc8498`）。归档不把作者读源码的结论升级成刷机或运行时验收。

## 清洗与完整性说明

正文用已导出的 Markdown，没有从同伴 HTML 重抽。MD 中的 mmbiz 图为 2 张远程 URL，HTML 中不重复的 mmbiz URL 为 14 个；差额未逐张鉴定，可能含页面装饰，也可能含未进入 MD 的图。缺图没有用文字补。MD 表格分隔行 1，HTML `<table>` 1。远程图未本地化。代码围栏、行号和「源码明确行为 / 作者推测」的原词保留。

<a id="source-body"></a>
## 来源正文

![](https://mmbiz.qpic.cn/mmbiz_png/VRGugOBdueYIXAbByxXsqml9bkEUzG8VWZ4aCGIAvkNVX4TP1gBj0SOyb2LZ19KwUl4kpqkQFjRPPdBfcAhZvI3um1Q7MvAG7YKtC87zeac/640?wx_fmt=png&from=appmsg)

本文基于双仓库交叉核实：**APatch** `main@6ec140e` + **KernelPatch** `tag 0.13.8`（HEAD `bcc8498`）。所有结论附 `仓库:文件:行号`。

## 01 这一篇我们要解决什么问题？

前四篇我们把地基全部打完了：execve hook 在开机早期就位（第 4 篇）、supercall 门铃已挂好（第 3 篇）、apd 学会了 argv[0] 变身（第 2 篇）。这一篇让它们在一个用户每天都在用的动作里会师——在终端敲下 `su`，回车，拿到一个 root shell。

这中间不到一秒的时间里，有三个问题值得刨根问底：

1. `/system/bin/su` 这个文件到底存在吗？谁拦下了这次 exec？
2. **提权发生在哪个进程、哪个时间点**——是 apd 帮你提的权，还是别人？
3. `apd.rs:52` 那行注释说 "we are root now, this was set in kernel!"，那 `root_shell` 里后面的 `set_identity` 又在设什么、设给谁？

## 02 为什么从这里开始？

因为 su 是整个 APatch 里唯一一个**用户直接感知**的功能入口，也是前四篇所有机制的唯一"全须全尾"汇聚点：内核侧的 execve hook 在 `before_rest_init` 里由 `su_compat_init()` 安装（第 4 篇时间线的 `:91`）；授权判据查的是 supercall 维护的 kstorage 表（第 3 篇命令 `0x1100` 的写入端）；拦截后改写 exec 指向 apd，靠 argv[0] 完成多合一变身（第 2 篇）。**读懂 su，等于把前四篇串成了一条项链。**

## 03 背景：su 的三种实现思路

传统 Linux 的 su 是一个 **setuid root 二进制**：文件真实存在、带 s 位，exec 后由内核把 euid 提到 0，再由它验证密码。Magisk 的 su 是**真二进制 + 守护进程**：su 客户端通过 socket 找 magiskd 要授权，再由 daemon 侧完成提权（背景知识，不作源码断言）。

APatch 的思路最激进：**su 可以根本不是一个文件**。它的 su 路径只是个"暗号"——被补丁的内核盯着所有 exec，看到有人执行这个暗号路径，就在内核里完成提权，再把 exec 偷偷改写到别处。用户态不需要 su 文件存在（甚至还要主动让它"看起来不存在"，第 08 节）。理解了这个"暗号"模型，后面所有奇怪的代码都顺理成章。

## 04 内核侧第一层：handle_before_execve 逐段精读

拦截函数在 `KP:kernel/patch/common/sucompat.c:225-314`，它是 execve/execveat 的 before-hook（第 4 篇 `su_compat_init` 安装）。逐段看。

门禁（`:227-228`）——就两行：

```
uid_t uid = current_uid();
if (!is_su_allow_uid(uid) && !is_trusted_manager_uid(uid)) return;
```

不在授权表、也不是受信任管理器的调用者？钩子看都不看，直接放行。**这就是"adb shell 刷机后天生能 su"的原因**：第 4 篇讲过 `su_compat_init` 开机就往授权表里塞了 uid 0 和 uid 2000 两条默认记录（`sucompat.c:500-504`），shell（2000）天然在名单里。

路径匹配（`:240-246`）：

```
    // Match the configured su path (default /system/bin/kp) and the legacy
    // /system/bin/su that shells and detectors also exec. execve does not go
    // through getname_flags, so this before-hook is the only place to redirect
    // a real exec of /system/bin/su to sh/apd.
    if (strcmp(filename, current_su_path) && strcmp(filename, legacy_su_path)) {
        if (!strcmp(SUPERCMD, filename)) {
            handle_supercmd(u_filename_p, uargv);   // truncate 暗号转交第 1 篇的处理器
        }
        return;
    }
```

两个 su 路径都认：当前配置的（默认 `/system/bin/kp`，可被 `SUPERCALL_SU_RESET_PATH` 改，第 2 篇的 `init_load_su_path`）和传统 `/system/bin/su`。注释顺便交代了一个内核细节：execve 不经过 getname_flags，所以**这里是拦截真实 su exec 的唯一机会**。命中 truncate 则转交给 supercmd（第 1 篇的 truncate 改写）。

取出授权档案（`:256-264`）——注意这里有个"二次验证"：

```
    struct su_profile profile = { .to_uid = 0 };
    if (is_trusted_manager_uid(uid)) {
        strncpy(profile.scontext, all_allow_sctx, sizeof(profile.scontext) - 1);
        ...
    } else if (su_allow_uid_profile(0, uid, &profile)) {
        return;                                     // 查无此人 → 不提权
    }
```

门禁那行只回答"在不在名单里"，这里才把完整档案取出来——提权目标 `to_uid` 和 SELinux 上下文 `scontext` 都来自档案本身，不是写死的 root。授权管理器给某个 App 授权时定的上下文，就是在这里生效的。

提权（`:268`）——全篇最重要的一行：

```
    uid_t to_uid = profile.to_uid;
    const char *sctx = profile.scontext;
    commit_su(to_uid, sctx);
```

停下来想清楚时序：此刻我们还在**调用者的进程**里，execve 还没真正开始、新程序映像还没加载。`commit_su` 直接把当前进程的凭证改成 root。也就是说——**提权发生在 exec 的前夜、发生在旧进程里**。等 apd 的 main() 开始执行时，它一出生就是 root。这就是 `apd.rs:52` 那行注释的完整含义，也回答了第 02 节的问题 2：**提权不发生在 apd 里，apd 从来没"帮你"提过权——它只是生来就是 root**。这相当于把 setuid 位的活儿搬进了内核，而且没有文件。

改写 exec（`:270-311`）：先 `filp_open` 探测 `/data/adb/apd` 存不存在——

- **存在**：把 filename 改写成 apd 路径，并且当执行的不是 legacy 路径时，把 argv[0] 用 `set_user_arg_ptr` 写回 su 路径（`:295-308`）——第 2 篇讲过的"保留名片"，两个仓库在此握手。
- **不存在**：filename 改写成 `/system/bin/sh`（`:274-277`）——apd 还没装好时，至少给你一个提了权的 shell，而不是一句 "not found"。

## 05 内核侧第二层：commit_su 的两条路径

`commit_su`（`KP:kernel/patch/common/accctl.c:123-130`）很短，但分岔值得看：

```
int commit_su(uid_t to_uid, const char *sctx)
{
    if (all_allow_sid != SECSID_NULL && !to_uid) {
        return commit_kernel_su();          // 快路径
    } else {
        return commit_common_su(to_uid, sctx);
    }
}
```

快路径 `commit_kernel_su`（`:73-78`）：如果全局"万能上下文"已配置且目标是 uid 0，直接 `prepare_kernel_cred(0)`——克隆 init 进程的凭证——再 `commit_creds`。三行，最省事。

**常规路径 `commit_common_su`（`:80-121`）**才是值得精读的，它揭示了 KP 与内核相处的方式：

```
    struct thread_info *thi = current_thread_info();
    thi->flags &= ~(_TIF_SECCOMP);                        // ① 摘掉 seccomp 标志位

    struct seccomp *seccomp = (struct seccomp *)((uintptr_t)task + task_struct_offset.seccomp_offset);
    seccomp->mode = SECCOMP_MODE_DISABLED;                // ② seccomp 彻底关闭

    ext->sel_allow = 1;                                   // ③ task_ext 打上 sel_allow 标记
    struct cred *new = prepare_creds();
    su_cred(new, to_uid);                                 // ④ 直写凭证
    set_groups(new, groups_alloc(0));                     // ⑤ 清空附加组
    if (sctx && sctx[0]) {
        ext->sel_allow = !!set_security_override_from_ctx(new, sctx);  // ⑥ 上下文转 secid 写进 cred
    }
    commit_creds(new);
```

④ 的 `su_cred`（`:34-51`）写得极其"莽"——**不调用任何内核 API，直接按偏移量往 cred 结构体里写**：五个 capability 组（inheritable/permitted/effective/bset/ambient）全部写成 `full_cap`，八个身份字段（uid/euid/fsuid/suid + gid/egid/fsgid/sgid）全部写目标值：

```
    *(kernel_cap_t *)((uintptr_t)cred + cred_offset.cap_inheritable_offset) = full_cap;
    ...
    *(uid_t *)((uintptr_t)cred + cred_offset.uid_offset) = uid;
    *(uid_t *)((uintptr_t)cred + cred_offset.euid_offset) = uid;
    ...
```

为什么这么莽？因为 KP 不能调用"编译时不存在"的内核内联函数——这些偏移量是第 4 篇里 `resolve_struct` 在开机时探测出来的（`before_rest_init` 的 `resolve_struct`，`patch.c:76`）。**离线/开机时探测结构布局，运行时按偏移直写**——这是整个 KernelPatch 和内核相处的通用模式，第 4 篇的 preset 偏移表、这一篇的 cred 直写、后面 KPM 的符号重定位，全是这一个思想。

①② 顺手把 seccomp 摘干净了（很多 App 带着 Chromium 系 seccomp 沙箱，不关掉 root shell 会莫名崩溃）。③ 的 `sel_allow` 标记和 ⑥ 是 SELinux 双保险的一半，下一节。

## 06 第三层：SELinux 双保险

第一道保险在第 05 节的 ⑥：目标上下文字符串经 `set_security_override_from_ctx` 转成 secid **写进新凭证**——新进程的 SELinux 身份从出生就是 `u:r:magisk:s0`（或档案里定的任意上下文）。

第二道保险是**强制力兜底**。内核的 SELinux 判定最终走 `avc_denied`，KP 在开机早期就把它换掉了（`before_rest_init` 的 `bypass_selinux`，`patch.c:79`；替换函数在 `KP:accctl.c:181-211`）：

```
static int avc_denied_replace(...)
{
    ...
    struct task_ext *ext = get_current_task_ext();
    if (unlikely(task_ext_valid(ext) && (ext->sel_allow || ext->priv_sel_allow))) {
        goto allow;
    }
    return avc_denied_backup(...);        // 普通进程：原样判定

allow:
    avd->allowed = 0xffffffff;            // 被标记的进程：全部允许
    avd->auditallow = 0;
    avd->auditdeny = 0;                   // 审计也清零——不留 avc denied 痕迹
    return 0;
}
```

看清楚了：**SELinux 仍然在 enforcing，对所有普通进程照常执法**；只有 cred 或 task_ext 上带着标记的提权进程才被全面放行，而且连审计日志都被抹掉。`slow_avc_audit` 同样被替换成静音版（`:217-238`）。这套"标记 + 执法函数替换"的完整展开是第 8 篇的主题，这里记住分工：**cred 上的 secid 决定"我是谁"，avc_denied 替换决定"查我时放行"**。

![图1：一次 su 的完整旅程——shell → 内核 execve hook → apd](https://mmbiz.qpic.cn/mmbiz_png/VRGugOBdueaoiaWhGUibc2AA4CNqa8UWlBfHEhfIzzeDm3wolABmqPxVUib0NjibjicK6mab7ibB5ib2BuHq0Tjic13kWtO9h8ABSeaG43HdtyYhhrE/640?wx_fmt=png&from=appmsg)

图1：一次 su 的完整旅程——shell → 内核 execve hook → apd

## 07 apd 侧：root_shell 逐段精读

现在镜头切回用户态。`root_shell()`（`APatch:apd/src/apd.rs:51-292`）接手时进程已经是 root + magisk 上下文，它做的全是"shell 体验"工程。

**参数解析用 getopts 而不是 clap**（`:68-111`），因为要兼容 su 的传统参数和 Magisk 习惯：`-c` 命令、`-s` shell、`-l` login shell、`-p` 保留环境、`-M` 全局挂载命名空间、`-g/-G` 主组/附加组。还有一段"改名兼容"（`:113-125`）：`-mm` → `-M`、`-cn`/`-z` → `-Z`——注释写明 *"same as Magisk"*。

`-Z` 的真相：选项定义直接写着 `"(ignored)"`（`:105-110`），命中后只打一行警告（`:156-160`）：*"per-session context switching is not supported, ignoring"*。这回收了第 2 篇的伏笔：提权上下文在内核 `commit_su` 时就已经写进 cred 了，root shell 想换也换不了（per-session 切换没实现），经典脚本里 `su -Z u:r:magisk:s0 -c ...` 能工作，纯粹是因为上下文本就是它。

`set_identity` 之谜揭晓（`:187-214`）：

```
    // use current uid if no user specified, these has been done in kernel!
    let mut uid = unsafe { libc::getuid() };       // 已经是 0！
    let mut gid = unsafe { libc::getgid() };
    if free_idx < matches.free.len() {
        let name = &matches.free[free_idx];
        ...
        (uid, gid) = ... getpwnam 或数字解析 ...
            Err(_) => {
                eprintln!("su: unknown user: {name}");
                std::process::exit(1);             // "Refuse to start rather than silently handing out uid 0"
            }
```

注释把答案写明了：不指定用户时，`getuid()` 返回的就是内核给好的 0，`set_identity(0, 0)` 只是例行确认；`su <username>` 指定用户时，set_identity 才有真正的工作——从内核给的 0 降权到目标用户。这就是为什么未知用户名要直接拒绝退出（注释说和 Magisk 行为一致）：拿着 root 身份静默运行才是事故。

剩下的是体验细节，每一条都有出处：环境变量 HOME/USER/LOGNAME/SHELL 按 passwd 设置（`:233-252`，上面还留着一行作者自己的吐槽注释 *"This is actually incorrect, I don't know why."*，`:234`）；PATH 追加 `/data/adb/ap/bin` 让 resetprop/magiskpolicy 分身可见（`:254-256`，第 2 篇的伏笔）；`.aprc` 存在时注入 ENV 变量实现"root shell 自动脚本"（`:258-261`）；默认分配 PTY（`:262-267`，`--no-pty` 可关）；`pre_exec` 里 umask 022、切 cgroup、按需切全局挂载命名空间（`-M` 或 `/data/adb/.global_namespace_enable`，`:271-288`）；最后 `arg0` 按 login shell 约定置 `"-"`（`:228-229`，注释直接链接了 Magisk 的对应源码行），`command.exec()`（`:291`）——exec 成功就不返回了。

## 08 猫鼠游戏：su 的"隐身术"

既然 su 路径只是暗号，那反过来——**让探测者看不见 su**——也是内核的活。两个钩子（都在 `KP:sucompat.c`）：

探测重定向 `after_getname_flags`（`:390-416`）：授权用户对 su 路径做 stat/exec 类路径解析时，内核把解析结果里的路径名**原地改写**成 `/system/bin/sh`：

```
    const char *name = fn->name;
    if (!name || strcmp(name, su_get_path())) return;
    if (strlen(sh_path) <= strlen(name)) {
        strcpy((char *)name, sh_path);           // 原地改写——sh 更短，塞得下
        return;
    }
    ... kfunc(getname_kernel) 造一个新的换上     // 兜底：原路径太短塞不下 sh
```

于是授权 shell 里 `ls -l /system/bin/su` 看到的是 sh 的属性，`which su` 类探测被引到别处。兜底分支还处理了"用户把 su 路径改得太短、塞不下 sh"的边界。

真文件隐藏 `after_security_inode_getattr`（`:426-455`）：如果设备上真实存在一个第三方 su 文件，stat 类调用会命中它。钩子把路径解析出来比对，未授权调用者一律返回 `-ENOENT`——文件系统对你说"查无此文件"；授权调用者则正常可见（注释原文解释了这套"对授权者显示、对其余隐藏"的策略，`:418-422`）。

两钩子合起来的效果：未授权的 Root 检测逻辑在这个体系里既 exec 不到、stat 不到，也看不到 su 的影子——**因为从文件系统的视角看，su 确实"不存在"**。

## 09 常见误区

1. "`/system/bin/su` 是 APatch 装的文件"——不是，这个路径很可能根本没有真实文件，它只是内核 execve hook 认的暗号；系统里如果有真 su 文件，反而会被 getattr 钩子对未授权者隐藏。
2. **"apd 帮我提了权"**——不。`commit_su` 发生在 exec 改写之前、调用者的旧进程里（`sucompat.c:268`）；apd 生而 root，只负责 shell 体验。
3. "`su -Z` 能换 SELinux 上下文"——解析但忽略（`apd.rs:105-110,156-160`），上下文由授权档案在内核侧决定。
4. **"提权会留 avc denied 日志"**——审计被清零（`accctl.c:208-209`），日志里干干净净。
5. **"所有 root shell 都一样"**——`su <user>` 会用 `set_identity` 从 0 降权到目标用户；未知用户直接拒绝，绝不静默给 0（`apd.rs:207-210`）。

## 10 本篇源码地图

| 文件 | 本篇中扮演的角色 |
| --- | --- |
| `KP:kernel/patch/common/sucompat.c` | `handle_before_execve`（门禁/匹配/提权/改写）、`after_getname_flags`（探测重定向）、`after_security_inode_getattr`（真文件隐藏） |
| `KP:kernel/patch/common/accctl.c` | `commit_su` 双路径、`su_cred` 按 offset 直写、seccomp 关闭、`task_su` 跨进程版、`avc_denied/slow_avc_audit` 替换 |
| `APatch:apd/src/apd.rs` | `root_shell` 全文：getopts 参数、-Z 忽略、set_identity 真相、pre_exec 四件套 |
| `APatch:apd/src/pty.rs` | root shell 的伪终端会话（`prepare_pty`） |

## 11 总结与思考题

这一篇把 su 从"敲下回车"到"root 提示符"的全链路打通了：**内核的 execve hook 在门禁（授权表/受信任管理器）之后、exec 生效之前，用档案里的 to_uid 和 scontext 对调用者进程完成凭证改写**（全量 capability、八个身份字段、关 seccomp、SELinux secid + avc 放行标记），再把 exec 悄悄改写到 apd；apd 的 `root_shell` 生而 root，只做参数兼容、环境整理和身份微调（`su <user>` 降权），最后把 shell 交还给用户。**提权没有发生在任何用户态程序里——这就是"内核级 Root"的字面意思。**

三道思考题，前提均已核实：

1. `handle_before_execve` 在门禁（`:228`）之后、`commit_su`（`:268`）之前，又做了一次 `su_allow_uid_profile` 查询且查不到就 `return`（`:262-263`）——门禁已经确认过"在名单里"了，这一次查询多拿了什么信息、防住了什么？
2. 经典脚本写 `su -Z u:r:magisk:s0 -c xxx` 能正常工作，但 `-Z` 实际被 apd 忽略——脚本作者的意图是被什么机制满足的？（提示：回看 `:256-268`，档案里的 `scontext` 是谁写的。）
3. `after_getname_flags` 的原地改写有前提：`strlen(sh_path) <= strlen(name)`（`:401`）。默认 su 路径 `/system/bin/kp`（14 字节）恰好等于 `/system/bin/sh`（14 字节）——如果用户通过 `SUPERCALL_SU_RESET_PATH` 把 su 路径改成了 `/su`，授权用户 `ls -l /su` 会走到哪个分支、最终看到什么？

下一篇回答一个上篇刚埋下的问题：授权表里的记录是从哪来的？**《APatch 源码笔记（六）：谁有资格拿 Root——SuperUser 授权与 uid-listener》**。管理器里点"允许"之后数据流向哪？`/data/adb/ap/package_config` 这个 CSV 文件的格式和消费方是谁？内核的 kstorage 每次开机清空重播，两条加载路径怎么保证一致？以及第 1 篇见过的 uid-listener 双启动"冗余"，到底是不是 bug？我们从 `package.rs` 和管理器的授权操作两端同时开挖。

## 复用边界

文件名和行号属于来源阅读的那两份树。作者标明「作者推测」的句子保持为推测。panther user 镜像把 APatch 收进 ROM 的流程是另一篇，目标不同，不要从本篇推出刷机步骤。
