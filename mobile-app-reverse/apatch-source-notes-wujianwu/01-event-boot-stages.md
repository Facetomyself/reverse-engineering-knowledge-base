---
schema_version: 2
id: apatch-source-note-01-event-boot-stages
document_type: archive
original_date: "2026-09-02"
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
relations: []
tags: [apatch, kernelpatch, source-report]
---

# APatch 源码笔记（一）：从 event.rs 看懂开机四阶段

吴见午公开笔记，发布日 2026-09-02。来源把结论绑在 APatch `main@6ec140e` 与 KernelPatch `0.13.8`（`bcc8498`）。归档不把作者读源码的结论升级成刷机或运行时验收。

## 清洗与完整性说明

正文用已导出的 Markdown，没有从同伴 HTML 重抽。MD 中的 mmbiz 图为 10 张远程 URL，HTML 中不重复的 mmbiz URL 为 46 个；差额未逐张鉴定，可能含页面装饰，也可能含未进入 MD 的图。缺图没有用文字补。MD 表格分隔行 1，HTML `<table>` 1。远程图未本地化。代码围栏、行号和「源码明确行为 / 作者推测」的原词保留。

<a id="source-body"></a>
## 来源正文

![](https://mmbiz.qpic.cn/sz_mmbiz_png/VRGugOBduebZk6TggDrP91ibiciam4YOLJichRbJd1QwsV36wVtup3FyiaA1ChuyPOpmDSgyaM8LHRZ4rPE1icYztichibKkMB1za8jaYicYwqLV7ajQ/640?wx_fmt=png&from=appmsg)

> 本文基于：**APatch** `main@6ec140e` 与 **KernelPatch** `tag 0.13.8`（HEAD `bcc8498`，与 APatch 内置版本号完全一致）。所有结论均给出 `仓库:文件:行号`；无法从源码直接得出的判断，一律以「作者推测」标注，与「源码明确行为」严格区分。

## 01 开篇：为什么从 event.rs 开始？

很多人想学 APatch 源码，但第一次打开仓库都会有一种感觉：Rust、C、Kotlin 混在一起，`apd/` 里二十多个 `.rs` 文件，`app/` 里一大片 Kotlin，还有 JNI、shell 脚本——根本不知道从哪里开始。

我第一次打开时也是这样。我的经验是：**不要一上来通读源码，而是先找一条"主线"**。对 APatch 来说，最适合建立全局认知的一条线，就是 Android 的开机流程——因为你会发现，这个项目的几乎所有核心组件（SELinux 处理、模块系统、Root 授权、与内核的通信）都是被开机流程串起来的。

而这条主线在源码里的"入口"，我选了 `apd/src/event.rs`。

为什么是它？因为它回答了学任何 Root 方案都绕不开的三个问题：**APatch 在什么时候启动？启动之后做什么？为什么偏偏挑那个时间点？** 看懂这个文件，你就有了继续往下钻的所有抓手。

这次读源码有个先天优势：APatch 实际上是两个项目——`APatch` 仓库（apd + 管理器 App）和 `KernelPatch` 仓库（内核补丁本体）。两边我都有本地克隆源码，版本号已经对齐（0.13.8），所以这篇文章可以把"用户态收到事件之后做了什么"和"内核怎么把事件送过来、收到回执又做了什么"**两边对上**。这种双仓库对读的方法，后面每篇都会用。

不过先说好：这篇文章不是 Rust 教程，也不是官方文档翻译。我会带着你一起读代码，遇到 Rust 语法只讲"为什么这里要这么写"，多一句都不展开。

## 02 先补背景：Android 开机时发生了什么

假设你完全没接触过 Android 启动流程，我们用三十秒过一遍：

![图1：Android 开机流程与 APatch 的两个关键时机](https://mmbiz.qpic.cn/mmbiz_png/VRGugOBdueYgmiaAg1uWsnKWvMWFrmg5qf3sicgwibZ5E8Ta1t8ZFDia25G20AkdtWCibKEeMkUWzoCotEOSNPCU9U9uWSQAcHYnpiaJ3heWpXmibs/640?wx_fmt=png&from=appmsg)

图1：Android 开机流程与 APatch 的两个关键时机

这张图里有两个时间点对本文至关重要：

- `post-fs-data` 时机：`/data` 分区挂好之后、zygote 和所有 Java 世界的东西跑起来**之前**。这是整个开机过程里唯一一个"文件系统还归你管、系统还没开始跑"的窗口。
- `boot-completed` 时机：System Server 全部就绪后，`sys.boot_completed` 属性被置为 1，宣告开机完成。此后做的事都不再阻塞开机。

那么 APatch 站在哪里？

答案是**两层都站**。APatch 的名字拆成了两个项目：

- **KernelPatch（内核补丁）**：编译成 `kpimg` 嵌入内核镜像，负责内核侧——新增一个超级系统调用（SuperCall），并 hook 掉一些关键路径。APatch 的 README 写得很直接："APatch relies on KernelPatch"（`APatch:README.md:18`）。
- **APatch 仓库**：`apd/` 是一个 Rust 写的用户态守护进程/命令行工具，装在手机的 `/data/adb/apd`；`app/` 是 Kotlin 写的管理器。

分工是：

![图2：APatch 三件套分工（KernelPatch / apd / 管理器 App）](https://mmbiz.qpic.cn/mmbiz_png/VRGugOBdueaYmGry1NicZRQtUiaVg60N7wcJgtWickzd9aaIpLbVTMlIpTCc1l2Ejdg3cDSAzmpgAAvurNRECcbpCTRicy7ejl2c7BlhzTtherM/640?wx_fmt=png&from=appmsg)

图2：APatch 三件套分工（KernelPatch / apd / 管理器 App）

那 apd 是怎么被"召唤"的呢？这是整个开机故事里最精彩的一段，答案比我想象的巧妙得多。

## 03 初见 event.rs：一个"没有事件的事件系统"

按直觉，一个叫 event 的文件里应该有个像样的 `enum Event`，加一个事件循环，一个 channel，对吧？

我第一次打开 `apd/src/event.rs` 时也这么以为。结果 391 行代码翻完，**没有 Event 枚举，没有事件总线，也没有分发循环**（唯一一个循环在文件末尾，后面会讲）。整个文件就是 8 个平平无奇的函数：

```
report_kernel(superkey, event, state)      // event.rs:26  向内核汇报状态
on_post_data_fs(superkey)                  // event.rs:43  post-fs-data 阶段
run_stage(stage, superkey, block)          // event.rs:216 阶段脚本执行器（私有）
on_services(superkey)                      // event.rs:248 service 阶段
run_uid_monitor()                          // event.rs:255 拉起 uid 监听进程
on_boot_completed(superkey)                // event.rs:277 开机完成阶段
start_uid_listener()                       // event.rs:286 授权同步监听（唯一的循环）
soft_reboot(superkey)                      // event.rs:351 软重启
```

那"事件"从哪来？看 `apd/src/cli.rs:33-43` 的子命令定义：

```
/// Trigger `post-fs-data` event
PostFsData,

/// Trigger `service` event
Services,

/// Trigger `boot-complete` event
BootCompleted,

/// Start uid listener for synchronizing root list
UidListener,
```

注意注释里的用词——**Trigger（触发）**。这些子命令不是给人敲的，是给"某个触发者"用的接口。触发者是谁？我原本以为是"内核直接 exec apd"——直到我把 KernelPatch 的源码翻了一遍，发现真相更有意思。

### 真相：内核把"闹钟"塞进了 init 的闹钟本

**源码明确行为**（`KernelPatch:kernel/patch/android/userd.c`）：

KernelPatch hook 了 init 进程的 `openat` 调用。当 init（uid 0）第一次打开 `/system/etc/init/hw/init.rc` 这几个原始 rc 文件时（`userd.c:106-111`、`before_openat` `userd.c:1723`），内核把原文件内容加上自己的一段追加文本，合并写进 `/dev/user_init.rc`（`userd.c:1763-1786`），然后**把 init 手里的文件名参数原地改写**成这个新文件（`userd.c:1793-1802`）。init 毫无察觉地解析了一个"被做过手脚"的 rc。

追加的那段文本是静态模板 `user_rc_data`（`userd.c:113-134`），原文如下（`%s` 会被替换成 SuperKey）：

```
"on early-init\n"
"    exec -- " SUPERCMD " %s event early-init before\n"
"on init\n"
"    exec -- " SUPERCMD " %s event init before\n"
"on late-init\n"
"    exec -- " SUPERCMD " %s event late-init before\n"
"on post-fs-data\n"
"    exec -- " SUPERCMD " su -Z " MAGISK_SCTX " exec " APD_PATH " -s %s post-fs-data\n"
"on nonencrypted\n"
"    exec -- " SUPERCMD " su -Z " MAGISK_SCTX " exec " APD_PATH " -s %s services\n"
"on property:vold.decrypt=trigger_restart_framework\n"
"    exec -- " SUPERCMD " su -Z " MAGISK_SCTX " exec " APD_PATH " -s %s services\n"
"on property:sys.boot_completed=1\n"
"    exec -- " SUPERCMD " su -Z " MAGISK_SCTX " exec " APD_PATH " -s %s boot-completed\n"
"    exec -- " SUPERCMD " su event boot-completed\n"
"    exec -- " SUPERCMD " su -Z " MAGISK_SCTX " exec " APD_PATH " uid-listener &\n"
"    rm " REPLACE_RC_FILE "\n"
```

其中 `SUPERCMD` 是 `/system/bin/truncate`（`scdefs.h:114`），`APD_PATH` 是 `/data/adb/apd`（`scdefs.h:101`）。翻译成人话：**APatch 把自己的启动时机完全托付给了 Android init 的标准 rc 触发器**——`on post-fs-data`、`on nonencrypted`、`on property:sys.boot_completed=1`，这些本来就是 init 自己的机制。内核不掐表、不轮询，只负责递纸条。

但纸条上写的执行命令是 `truncate`——一个平平无奇的系统工具。这就是第二层机关：内核还 hook 了 `execve`（`sucompat.c:517-533`，连 `execveat` 都 hook 了，注释明说 *"Android init may execute commands through execveat()"*）。当 init 执行 `/system/bin/truncate` 时，内核的 `handle_supercmd`（`supercmd.c:329`）会：

1. 校验 argv[1] 里的 SuperKey（`auth_superkey`，`supercmd.c:347`）；
2. 看到 `exec /data/adb/apd` 就**把这次 exec 的目标原地改写成 apd**（`supercmd_exec`，`supercmd.c:34-41`），argv 也同步改写；
3. 于是 init 启动的那个进程摇身一变，成了 `/data/adb/apd -s <密钥> post-fs-data`。

所以 apd 被召唤的完整链路是：

![图3：apd 被召唤的完整链路](https://mmbiz.qpic.cn/mmbiz_png/VRGugOBduebPvzlk9xXZiac42nYOibR4wuV2bhb6KGVPKwZJdC2sJqbKjpZIcoW54n0zvMxawQKxdyeH21Hga7gS4ibpt5nMouUZnGeaI8GNVo/640?wx_fmt=png&from=appmsg)

图3：apd 被召唤的完整链路

**这个设计的聪明之处值得停一停**：什么时候启动，交给最懂开机节奏的 init 决定；内核只做两件它擅长的事——改文件名和校验身份。没有任何自造的时机探测逻辑，Android 版本升级改了 init 行为？触发器语法是通用的，天然兼容。

回到 event.rs。于是"事件系统"的真面目是：

![图4：Event 的真身——一次独立的进程启动](https://mmbiz.qpic.cn/sz_mmbiz_png/VRGugOBdueaeFpRVibmjx9GnkobITgC4SEKCC25ap2XvYxGyPX9vM3Z5f3KDtx5bWu8Fb6HKgKBjbIHz1boAIFct58tmNQ0u6EjViaEPWa7c0/640?wx_fmt=png&from=appmsg)

图4：Event 的真身——一次独立的进程启动

**这里有个很值得想想的设计**：为什么不用 enum + 事件循环？我的理解（作者推测 + 架构分析）：因为"事件"的源头是**进程边界之外的 init + 内核**，传递媒介是 `exec` 的命令行参数。enum 只在一个进程内部才有意义。APatch 的做法是把 enum 放在进程门口——`cli.rs` 里的 `enum Commands`，clap 把命令行字符串解析成它（`cli.rs:227` 的 `Args::parse()`），然后一个 `match` 分发出去（`cli.rs:235-244`）：

```
let result = match cli.command {
    Commands::PostFsData => event::on_post_data_fs(cli.superkey),
    Commands::BootCompleted => event::on_boot_completed(cli.superkey),
    Commands::UidListener => event::start_uid_listener(),
    ...
```

所以准确说法是：**APatch 有 enum，但它站在进程门口当门卫，而不是坐在事件中心当调度员。**

还有一个细节：每次调用 apd 都可能带一个 `--superkey` 参数（`cli.rs:14-20`），类型是 `Option<String>`——"可能有也可能没有"，因为像 `uid-listener` 这样的子命令就不需要密钥。而且看 rc 模板你会发现，init 执行时密钥是作为 `-s` 参数传进来的。拿到 superkey 后 apd 第一件事是自证身份（`cli.rs:231-233`）：

```
if let Some(ref _superkey) = cli.superkey {
    supercall::privilege_apd_profile(&cli.superkey);
}
```

`privilege_apd_profile`（`supercall.rs:263`）通过 SuperCall 告诉内核："把我自己这个进程的 SELinux 上下文提到 `u:r:magisk:s0`"。也就是说，**apd 每次被唤醒，都要先向内核"刷脸"，然后才开始干活**。这是 SuperKey 机制在开机链路里的第一个作用。

## 04 确认"开机四阶段"：以源码为准

标题说了"四阶段"，现在对着源码数一遍。**源码明确行为**如下：

- init 触发器启动的 apd 子命令有三个：`post-fs-data`、`services`、`boot-completed`（rc 模板 + `cli.rs:33-40`）——对应三个独立进程；
- 第四个阶段 `post-mount` **不是独立进程**，它是嵌在 post-fs-data 进程里的一次执行（`event.rs:209`）。

所以准确的定义是：**一次开机中，apd 的事件处理共经历四个阶段：post-fs-data → post-mount → service → boot-completed。其中三个是 init 触发的独立进程，post-mount 内嵌在第一个进程里。**

顺带两个诚实的补充。第一，注入的触发器其实不止四个：rc 模板里还有 `early-init`、`init`、`late-init` 三条**纯通知事件**——它们只执行 `truncate su event <阶段> before`，不起 apd 进程，是直接报给内核的（后面 06 节会看到内核拿它们做什么）。第二，`services` 阶段挂了两个触发器：`on nonencrypted` **和** `on property:vold.decrypt=trigger_restart_framework`（`userd.c:121-124`）——不同加密方案（FDE/FBE）的设备走到框架重启的路径不同，两个都挂上才保险（"为什么"部分是作者推测，事实本身源码明确）。第三，源码里还有个小瑕疵恰好证明这些字符串是"活的"：`cli.rs:39` 的注释写 "boot-complete"，而实际阶段字符串全程用 `"boot-completed"`（`event.rs:280`）。读源码看到这种不一致别慌，以实际执行的字符串为准。

![图5：开机四阶段（post-fs-data → post-mount → service → boot-completed）](https://mmbiz.qpic.cn/sz_mmbiz_png/VRGugOBduebVvcKnODGxPWMWDbzcJf7rqgfKGuIFPdSvaU1rVPBh8g48wKwLLzltGXBphDTJavdVkOvfL9mnb7XzarT8ZJGALE29BWjhYKM/640?wx_fmt=png&from=appmsg)

图5：开机四阶段（post-fs-data → post-mount → service → boot-completed）

四个阶段，每个都要回答四个问题：什么时候触发？谁触发？执行什么？为什么必须在这个时机？前两个问题已经回答了——**时机由 init 的标准 rc 触发器决定，内核只负责改写 exec**。下面把重点放在"执行什么"和"为什么"。

## 05 主菜：on_post_data_fs 的十七步

`on_post_data_fs`（`event.rs:43-214`）是整个文件里最长、信息量最大的函数——APatch 在"系统起来之前"要做的所有事都在这 172 行里。我们按执行顺序逐段读。

### 第一段：报到与自证（event.rs:44-57）

```
pub fn on_post_data_fs(superkey: Option<String>) -> Result<()> {
    utils::umask(0);
    report_kernel(superkey.clone(), "post-fs-data", "before");
    ...
    init_load_su_path(&superkey);

    let mut sepol = get_policy_main(&["magiskpolicy".to_string(), "--live".to_string()])?;
    sepol.magisk_rules();
    sepol
        .to_file("/sys/fs/selinux/load")
        .context("Cannot apply policy")?;

    info!("Re-privilege apd profile after injecting sepolicy");
    supercall::privilege_apd_profile(&superkey);
```

第一行 `umask(0)`——放开文件权限掩码，后面创建的所有文件都按显式权限来，避免脚本之间互相读不了对方的产物。

第二行就开始向内核汇报：`report_kernel(superkey, "post-fs-data", "before")`。这个函数值得完整看一眼（`event.rs:26-41`）：

```
pub fn report_kernel(superkey: Option<String>, event: &str, state: &str) {
    let args = [
        superkey.unwrap_or("su".to_string()),
        "event".to_string(),
        event.to_string(),
        state.to_string(),
    ];
    ...
    // Best-effort notification to the kernel; a failed report must not abort
    // boot stages such as post-fs-data.
    if let Err(e) = utils::run_command("truncate", &args_ref, None)
        .and_then(|mut child| child.wait().map_err(anyhow::Error::from))
    {
        warn!("report kernel event {event}/{state} failed: {e}");
    }
}
```

它执行 `/system/bin/truncate`，参数是 `[密钥或"su", "event", "post-fs-data", "before"]`。现在我们双仓库对读，这条链路可以完整闭环了：

```
apd 执行 truncate su event post-fs-data before
   ↓
内核 execve hook 识别 SUPERCMD，校验密钥或"su"身份（supercmd.c:329,347-355）
   ↓
命中 "event" 命令分支（supercmd.c:473-479）
   ↓
report_user_event(event, args)                    （user_event.c:17）
```

**内核收到 "post-fs-data before" 后做什么？** `user_event.c:23-48` 给出了完整答案（下面是按源码结构简化后的示意，函数名均真实存在）：

```
// event == "post-fs-data" 时：
if (state 是 "before") {
    load_ap_package_config();                        // 内核自己读 /data/adb/ap/package_config！
    sucompat_init();                                 // su/truncate 相关 hook 的安装入口
    if (!android_is_safe_mode) load_ap_kpm_modules(); // 加载 /data/adb/ap/kpm/ 下的 KPM
}
selinux_hide_post_fs_data(...);                      // before/after 任意状态都执行
```

（`boot-completed` 事件的内核处理是**空的**——只有日志和广播；`uid_listener/package-list-updated` 会触发 `refresh_trusted_manager_state()` 刷新管理器 uid 缓存。所有事件最后都会经过 `extra_event_init_args` 广播给所有已加载的 KPM 模块，`patch.c:127-134`。）

注意这里有个漂亮的对称：apd 在 post-fs-data 里通过 SuperCall 告诉内核 su 路径和自己的身份；而内核在同一条事件的 "before" 时点，自己把 `/data/adb/ap/package_config` 授权规则读进了内核的 kstorage。同一份磁盘数据，两个消费者，两条加载路径。如果只读 APatch 一个仓库，你永远看不到后一半。

还注意源码注释里的 *"Best-effort notification"*——**尽力而为的通知，失败绝不中断**。整个函数没有 `?`，出错只打一行 warn。为什么？因为这是开机路径，通知发不出去顶少丢条日志（内核侧少了授权预加载），但如果让 post-fs-data 中断，手机可能就起不来了。

回到主线。`init_load_su_path`（`supercall.rs:278`）从 `/data/adb/ap/su_path` 读出用户配置的 su 路径并通过 SuperCall 告知内核（内核侧默认路径是 `/system/bin/kp`，`KernelPatch:sucompat.c:46`）——这解释了为什么 APatch 允许自定义 su 路径。

接下来的三行是 SELinux 重头戏：加载 `/sys/fs/selinux/policy`、套用一组内置的 magisk 规则、写回 `/sys/fs/selinux/load` 完成热加载。一句话概括：**在系统服务起来之前，先把 SELinux 规则改好，给后面的提权、模块执行扫清障碍**。（规则内容和 SELinux 机制本身是第 8 篇的主题；内核侧配套的 enforcement 绕过逻辑在 KernelPatch 的 `accctl.c:240-260`，它 hook 了 `avc_denied`——同样留到第 8 篇。）

### 第二段：清理与共存检查（event.rs:59-68）

```
    // Clear all temporary module configs early
    if let Err(e) = crate::module_config::clear_all_temp_configs() {
        warn!("clear temp configs failed: {e}");
    }

    if utils::has_magisk() {
        warn!("Magisk detected, skip post-fs-data!");
        report_kernel(superkey.clone(), "post-fs-data", "after");
        return Ok(());
    }
```

先清掉上次开机遗留的临时模块配置。然后是共存检查：`has_magisk()`（`utils.rs:203`）其实就是 `which magisk` 能不能找到。如果 Magisk 在场，APatch **直接让路**——两个都想改文件系统和 SELinux 的方案同时跑，等于互相拆台。这是把"不把你手机搞变砖"排在第一位的工程判断。注意 "before" 在函数开头就已经发过了（`event.rs:45`），所以让路分支的 "after" 依然与开头成对，内核侧的 `selinux_hide_post_fs_data` 照常收到两个状态。

### 第三段：搭日志环境（event.rs:70-126）

这一段 50 多行做的事情很朴素：创建 `/data/adb/ap/log/` 目录、把旧日志轮转成 `.old.log`、然后起两个带 `timeout` 的子进程：`timeout 45s logcat`（45 秒）和 `timeout 120s dmesg -w`（120 秒），把开机最初一分钟的内核日志抓下来存档。

细节在 `pre_exec` 回调里的 `switch_cgroups()`——把子进程挪到合适的 cgroup，避免被系统的冻结/限制机制干扰。为什么开机日志这么重要？因为 **Root 方案的大部分"翻车"（模块冲突、SELinux 拒绝）都发生在开机最初一分钟**，没有这段日志，用户反馈"手机无限重启"时你两眼一抹黑。

### 第四段：safe mode 三重门（event.rs:140-174）

```
    let safe_mode = utils::is_safe_mode(superkey.clone());

    if safe_mode {
        warn!("safe mode, skip common post-fs-data.d scripts");
        // Not redundant with the disable below: ensure_binaries /
        // handle_updated_modules can still fail with `?` before reaching it,
        // and returning early with modules left enabled risks a bootloop.
        if let Err(e) = module::disable_all_modules() {
            warn!("disable all modules failed: {}", e);
        }
    } else {
        // Then exec common post-fs-data scripts
        if let Err(e) = module::exec_common_scripts("post-fs-data.d", true) {
            warn!("exec common post-fs-data scripts failed: {}", e);
        }
    }
```

`is_safe_mode`（`utils.rs:71-94`）检查两条通道：系统属性 `persist.sys.safemode`，以及直接问内核（SuperCall `SUPERCALL_SU_GET_SAFEMODE`）。内核侧那个标志位怎么来的？`KernelPatch:userd.c:1905-1918` 给出答案：hook 了按键事件处理函数 `input_handle_event`，音量下键按满三次，`android_is_safe_mode = 1`。也就是说，开机时连按三下音量下，就等于告诉内核"进安全模式"。顺带一个考古发现：`SAFE_MODE_FLAG_FILE "/dev/.safemode"`（`scdefs.h:116`）在内核代码里**只有定义、没有任何读写**，是遗留常量——双仓库对读才看得出来的死代码。

进了 safe mode，所有模块立刻被禁用（写 `disable` 旗标），公共脚本也不跑。那段英文注释值得读：为什么 safe mode 判断和 `disable_all_modules` 出现了两次？ 注释自己回答了：因为中间的 `ensure_binaries()` 和 `handle_updated_modules()` 可能带着 `?` 提前失败返回，如果只禁一次，某些失败路径会把"模块还开着"的状态留到下次开机——那就是 bootloop。注释甚至写明 "Not redundant"（不是冗余）。读源码看到看似重复的防御代码，注释往往是作者留给你的解释。

### 第五段：模块的正戏（event.rs:158-207）

这是 post-fs-data 的核心业务，顺序严格：

```
    if Path::new(defs::MODULE_UPDATE_DIR).exists() {
        module::handle_updated_modules()?;      // 1. 上次安装的新模块落地
        fs::remove_dir_all(module_update_dir)?;
    }

    if let Err(e) = module::prune_modules() { ... }          // 2. 清理待删除模块
    if let Err(e) = restorecon::restorecon() { ... }         // 3. 修 SELinux 标签
    if module::load_sepolicy_rule().is_err() { ... }         // 4. 加载模块自带策略规则
    if let Err(e) = metamodule::exec_mount_script(module_dir) { ... }  // 5. metamodule 挂载
    if let Err(e) = module::exec_stage_script("post-fs-data", true) { ... } // 6. 各模块 post-fs-data.sh
    if let Err(e) = lua::exec_stage_lua("post-fs-data", true, ...) { ... }  // 7. 各模块 Lua
    if let Err(e) = module::load_system_prop() { ... }       // 8. 加载 system.prop
```

**为什么是这个顺序？** 因为它们之间有真实依赖：新模块要先落地（1）才谈得上清理（2）；文件就位后才能修标签（3）；标签修好、策略规则加载完（4），后面的挂载脚本和模块脚本才有权限跑；挂载完成（5）之后，模块的 `post-fs-data.sh` 才能看到自己要操作的系统文件（6）；最后 `system.prop`（8）设置的系统属性会在稍后 System Server 起来时被读到。

注意第 5 步：**apd 自己不做模块挂载**，而是交给 `metamodule::exec_mount_script` 执行一个叫 `metamount.sh` 的脚本——挂载这件事被"外包"给了 metamodule 机制（这是第 12 篇的主题，这里先记住这个事实）。还有一处双仓库联动：第 6 步的模块 `post-fs-data.sh` 跑之前，内核侧的 `load_ap_kpm_modules()` 已经在 "before" 事件里把 `/data/adb/ap/kpm/` 下的 KPM 装进内核了（`userd.c:1459`）——**KPM 永远比 APM 脚本先就位**。

注意错误处理的分层：第 1 步用了 `?`（失败就中止整个 post-fs-data），后面 7 步全是"失败打 warn 继续"。**源码明确行为**：只有"新模块落地"这一步是不可妥协的，其余步骤都被设计成尽力而为。开机路径的哲学就是：宁可部分功能失效，不能让手机起不来。

### 第六段：内嵌的第四阶段（event.rs:209-213）

```
    run_stage("post-mount", superkey.clone(), true);

    env::set_current_dir("/").with_context(|| "failed to chdir to /")?;
    report_kernel(superkey, "post-fs-data", "after");
    Ok(())
}
```

`run_stage("post-mount", ..., true)`——第四个阶段在这里执行，第三个参数 `true` 表示阻塞等它跑完。然后 `chdir("/")` 把工作目录挪出 `/data`（因为 post-fs-data 结束后某些场景 `/data` 可能被重新挂载），最后向内核汇报 "after"。至此进程 1 功成身退。

### 第七段：run_stage——四层固定的脚本洋葱（event.rs:216-246）

进程 1 功成身退，但它退场时调用的那台"脚本发动机"值得单独拆开：`post-mount`、`service`、`boot-completed` 三个阶段共用同一个执行器 `run_stage`（`event.rs:216-246`），它就是四层固定顺序的"洋葱"：

```
fn run_stage(stage: &str, superkey: Option<String>, block: bool) {
    utils::umask(0);
    if utils::has_magisk() { /* 让路 */ return; }
    if utils::is_safe_mode(superkey.clone()) { /* 禁模块 */ return; }

    // execute metamodule stage script first (priority)
    metamodule::exec_stage_script(stage, block)              // 层1: metamodule 优先
    module::exec_common_scripts(&format!("{stage}.d"), block) // 层2: /data/adb/<stage>.d 公共脚本
    module::exec_stage_script(stage, block)                   // 层3: 各模块的 <stage>.sh
    lua::exec_stage_lua(stage, block, ...)                    // 层4: 各模块的 Lua 函数
}
```

这里有个精妙的设计值得点名：`stage` 参数是个**字符串**而不是 enum，因为它是"数据"而不只是"标签"——它同时是脚本文件名后缀（`<stage>.sh`）、公共脚本目录名（`{stage}.d`）、Lua 函数名（转成下划线风格如 `post_fs_data`）。一个字符串贯穿三种约定，加一个新阶段不需要改任何分发逻辑。

`block` 参数则控制是否等待脚本跑完：post-mount 是 `true`（挂载必须完成才能继续），service 和 boot-completed 都是 `false`（模块的服务脚本不该拖住开机）。`on_services`（`event.rs:248-253`）整个函数就一行有效逻辑，最能说明各阶段共享同一套机制：

```
pub fn on_services(superkey: Option<String>) -> Result<()> {
    info!("on_services triggered!");
    run_stage("service", superkey, false);
    Ok(())
}
```

## 06 第三进程与唯一的循环：boot-completed 和 uid-listener

```
pub fn on_boot_completed(superkey: Option<String>) -> Result<()> {
    info!("on_boot_completed triggered!");
    run_stage("boot-completed", superkey, false);
    run_uid_monitor();
    Ok(())
}
```

前半段老套路：跑一轮 `boot-completed` 阶段的脚本（依然走四层洋葱，非阻塞）。有意思的是后半句——`run_uid_monitor()`（`event.rs:255-275`）会**再拉起一个独立进程**：`Command::new("/data/adb/apd").arg("uid-listener")`。

对照 rc 模板你会发现一个双仓库对读才可见的细节：init 注入的 rc 在 `sys.boot_completed=1` 时也直接拉起了一个 `apd uid-listener &`（`userd.c:130`）。也就是说这个监听进程有两条启动路径——init 拉一个，apd 的 boot-completed 处理器再拉一个（"这是冗余还是有意为之"，源码没有注释，属于开放问题；两边的 `refresh_ap_package_list` 各自有进程内互斥锁）。读源码时遇到这种"看起来多余"的地方，先记录事实，别急着替作者圆。

为什么开机都完成了还要起常驻进程？因为 Android 系统在运行期间会不断重装、更新 App，**授权过的应用 uid 会变**，Root 授权必须跟着变。这个进程就是干这个的，它也是整个 event.rs 里唯一的"循环"（`event.rs:286-346`）。

它监听什么？一个文件的重命名：

```
const SYS_PACKAGES_LIST_TMP: &str = "/data/system/packages.list.tmp";
...
let mut watcher = INotifyWatcher::new(
    move |ev: notify::Result<Event>| match ev {
        Ok(Event {
            kind: EventKind::Modify(ModifyKind::Name(RenameMode::Both)),
            paths,
            ..
        }) => {
            if paths.contains(&sys_packages_list_tmp) {
                info!("[uid_monitor] System packages list changed, sending to tx...");
                tx_clone.send(false).unwrap()
            }
        }
        ...
```

Android 的 `packages.list`（所有应用与 uid 的对照表）更新时，系统是先写 `packages.list.tmp` 再原子重命名覆盖。inotify 抓住这个重命名动作，就等于抓住了"系统的应用列表刚变了"。**用一个文件系统事件代替轮询**，这是 Linux 用户态程序的经典手法。

抓到事件后不是马上干活，而是走一个 1 秒防抖（`event.rs:331-343`）：

```
    let mut debounce = false;
    while let Ok(delayed) = rx.recv() {
        if delayed {
            debounce = false;
            let skey = c"su";
            refresh_ap_package_list(skey, &mutex);
            report_kernel(None, "uid_listener", "package-list-updated");
        } else if !debounce {
            thread::sleep(Duration::from_secs(1));
            debounce = true;
            tx.send(true)?;
        }
    }
```

读这段代码有个小惊喜：同一个 mpsc channel 里的 `bool` 被玩出了两义性——收到 `false` 表示"刚发生了变化"，睡 1 秒后自己给自己发一个 `true`；收到 `true` 才真正执行刷新。1 秒内连发的多次事件被自然合并成一次，没有定时器、没有额外状态机，用一个 bool 和一个 channel 就实现了防抖。这是我第一次觉得 event.rs 很有意思的地方：**简单原语组合出的机制，往往比复杂机制更可靠**。

真正的刷新逻辑 `refresh_ap_package_list`（`supercall.rs:202`）策略简单粗暴：先把内核里**所有**已授权 uid 全部撤销，再从磁盘上的 `/data/adb/ap/package_config`（授权持久化文件）按配置重新授权一遍，跳过 uid 0（root）和 2000（shell）。**"先清空再重放"而不是"增量比对"**——授权条目最多几十条，全量重放的成本可以忽略，换来的是任何情况下内核态和磁盘状态强一致。最后 `report_kernel(None, "uid_listener", "package-list-updated")` 通知内核，内核收到后刷新受信任管理器的 uid 缓存（`user_event.c:42-45`）。

还有一个兜底值得注意（`event.rs:300-309`）：它同时监听了 `SIGTERM/SIGINT/SIGPWR` 信号，关机信号到来时也强制刷新一次授权列表——确保关机前的最后状态是干净的。

至此，四个阶段全部读完。把完整调用链收拢成三张图。

**链 1：开机触发主链（双仓库接力）**

![图6：链1——开机触发主链（双仓库接力）](https://mmbiz.qpic.cn/sz_mmbiz_png/VRGugOBdueYJ4VibQibftfyzCd3aNfibRmptHgDw4ARo62l5p2BjSF3ibD5W28m2Cj8JNlIspRicDvTxehAfX8BibWiaW8jmqmrP3LBexPJ0zaYTSY/640?wx_fmt=png&from=appmsg)

图6：链1——开机触发主链（双仓库接力）

**链 2：授权同步链**

![图7：链2——授权同步链（uid-listener）](https://mmbiz.qpic.cn/mmbiz_png/VRGugOBdueay90Dicd0vY2KByibjQqqW3yAdaErxpBbmPHvIuNJ3jrzwpqnrQD0p3NibMnMiaiaxicTZczK3uuFiblpYIA2J9adxEcsJwQh50icozbY/640?wx_fmt=png&from=appmsg)

图7：链2——授权同步链（uid-listener）

**链 3：反向通知链（贯穿所有阶段）**

![图8：链3——反向通知链（贯穿所有阶段）](https://mmbiz.qpic.cn/mmbiz_png/VRGugOBdueZrxC4oQqqtInuvqAVT7mw222xduzY5abhR7w4xHeqpiaIX9dqSCvPy9YicpeBNRLcABmf1ibJxkUiaPTKhGtdCzlm4cGrbrHbzh8w/640?wx_fmt=png&from=appmsg)

图8：链3——反向通知链（贯穿所有阶段）

## 07 顺手学到的 Rust：三个服务于源码的设计

这节把文中出现的 Rust 知识收个尾，全部服务于"理解 APatch 为什么这么写"：

1. `Option<String>` 与 `unwrap_or("su")`：superkey 可有可无（`uid-listener` 不需要），`report_kernel` 里没有密钥时用 `"su"` 兜底——内核侧对字面量 `"su"` 的处理是"不验密钥，但要求调用者本身就是已授权 uid 或受信任管理器"（`supercmd.c:349-351`）。一个 `Option` 承载了两种调用者身份。
2. `Result` 与 `warn!` 的分层使用：看到 `?` 就意味着"这步失败就别继续了"；看到 `if let Err(e) = ... { warn!(...) }` 就意味着"尽力而为"。通读 event.rs 你会发现作者用这套语言精确标注了每一步的"死亡权限"：只有 sepolicy 加载和模块落地是致命的，其余全是可牺牲的。**错误处理风格就是架构文档。**
3. **为什么没有 Event enum**：事件源头是跨进程的 `exec` 命令行，字符串是天然的跨进程协议；enum 留在进程门口（`cli.rs` 的 `Commands`）做解析。而 `run_stage` 的 stage 参数保持字符串，是因为它要直接拼进文件路径和 Lua 函数名。

## 08 源码阅读方法论：这篇用到的五招

把这篇文章里实际用过的阅读手法总结成可复用的套路：

**第一招：找入口。** 不确定程序从哪开始时，直接看 `main.rs`——23 行，只有一个 `cli::run()`。大型项目不要怕从 main 开始，怕的是从 main 一路顺序读完。正确姿势是：main → 找到分发点（`match cli.command`）→ 挑一条你关心的分支跳进去。

**第二招：找调用者（向上追）。** 想知道 `on_post_data_fs` 什么时候被调，用 rg 一搜便知：

```
rg "on_post_data_fs" apd/src
# 只有两个结果：cli.rs:236（init+内核触发）和 event.rs:377（soft_reboot 内部复用）
```

搜索结果本身就是架构信息：一个函数只有两个调用者，说明"开机触发"和"软重启复用"是它仅有的两个生命周期入口。

**第三招：找被调用者（向下追）。** 从 handler 继续 `rg "exec_stage_script"`、`rg "refresh_ap_package_list"`，每追一层就在纸上记一行调用链。追到 FFI 边界（如 `libc::syscall`）或 exec 边界（如 `Command::new("truncate")`）就停下来标注"跨语言/跨进程，另一侧另找源码"。

**第四招：识别跨语言调用边界。** APatch 里共有四类边界，每类都有自己的"接头暗号"：

```
init + 内核 → apd：exec 二进制 + 命令行参数（argv[0] multicall / 子命令）
apd  → 内核：syscall 45（supercall）+ truncate exec 事件通知
App  → apd：libsu root shell 执行 CLI（没有 socket、没有 binder）
App  → 内核：JNI 直发 supercall（Natives.kt → apjni.cpp）
```

遇到任何"这个功能是谁触发的"问题，先判断它在哪类边界上跳转，再顺着对应的暗号追，比在单一语言里漫无目的翻文件快得多。

**第五招：双仓库对读（本篇新增）。** 当调用链跨过 exec/syscall 边界后，去对方的仓库接上另一半：在 KernelPatch 里 `rg "SUPERCMD"`、`rg "APD_PATH"`、`rg "post-fs-data"`，就能从 `sucompat.c` 跳到 `supercmd.c` 再跳到 `user_event.c`，把"apd 发的通知"和"内核做的事"焊在一起。很多只读单仓库时的"作者推测"，对读之后就升级成了"源码明确行为"——本篇的触发机制就是最好的例子。

## 09 本篇源码地图

当前已经分析过的部分：

![图9：本篇源码地图（两个仓库的关键文件）](https://mmbiz.qpic.cn/mmbiz_png/VRGugOBdueamXwUkF8mMP4QBbWCCWibECHoGKT95v34icicZ6xA7YfQ0v3Hcq69nK5vtQmJK8XQgHNokOnMicBAmIrKXpl3pO8HU9xtUA5jvlvw/640?wx_fmt=png&from=appmsg)

图9：本篇源码地图（两个仓库的关键文件）

本篇涉及文件速查表：

| 文件 | 本篇中扮演的角色 |
| --- | --- |
| `APatch:apd/src/event.rs` | 四阶段处理器 + uid-listener，全篇主角 |
| `APatch:apd/src/main.rs` | apd 入口（23 行） |
| `APatch:apd/src/cli.rs` | 子命令定义与分发，事件在此从字符串变成函数调用 |
| `APatch:apd/src/supercall.rs` | 向内核刷脸（privilege_apd_profile）、授权同步（refresh_ap_package_list） |
| `APatch:apd/src/module.rs` / `metamodule.rs` / `lua.rs` | 各阶段实际执行者：模块脚本与挂载 |
| `APatch:apd/src/sepolicy.rs` | 开机内置 SELinux 规则注入 |
| `APatch:apd/src/defs.rs` | `/data/adb/...` 全部路径常量 |
| `APatch:apd/src/utils.rs` | is_safe_mode / has_magisk / 日志轮转 |
| `KP:kernel/patch/android/userd.c` | 注入 rc 触发器、音量下键 safe mode |
| `KP:kernel/patch/common/sucompat.c` + `supercmd.c` | 拦截 truncate/su 的 exec 并改写 |
| `KP:kernel/patch/common/user_event.c` | 事件回执的内核侧动作 |

## 10 十二个核心问题收口

1. **APatch 到底是什么？** 一个"内核补丁（KernelPatch）+ 用户态守护进程 apd + 管理器 App"的三件套，通过给内核打补丁获得超级系统调用，从而实现 Root 与模块系统。
2. **为什么需要参与开机流程？** 因为改 SELinux 策略、挂载模块、装载 KPM 都必须发生在系统服务起来之前，错过窗口就再也改不了了。
3. **Kernel 部分和 userspace 部分分别做什么？** 内核侧提供 SuperCall、exec hook、uid 提权，并负责"递纸条"注入 rc 触发器；用户态 apd 负责四阶段业务、模块管理、授权持久化；App 负责 UI 与操作入口。
4. **apd 是什么？** 装在 `/data/adb/apd` 的 Rust 单二进制 multicall：既是四阶段事件处理器，也是 su/resetprop/magiskpolicy 的实现体。
5. **event.rs 是什么？** 四个开机阶段的处理函数集合；没有 enum、没有事件循环（除 uid-listener），"事件"即 init+内核接力 exec 出来的子命令。
6. **APatch 在什么时候介入开机？** 三个独立进程时机：post-fs-data（/data 挂载后、zygote 前）、service（两个触发器兜底）、boot-completed；外加内嵌的 post-mount。**时机由 init 的标准 rc 触发器决定**（`userd.c:113-134`），内核不自己掐表。
7. **每个阶段为什么选这个时机？** post-fs-data 是改文件系统的唯一窗口；service 非阻塞跑长任务；boot-completed 后做不紧急的事并启动授权监听。选标准触发器意味着时机语义随 Android 升级自动保持正确。
8. **Event 是怎么触发的？** init 按触发器执行 truncate → 内核 execve hook 校验密钥并改写目标为 apd → clap 解析成 `Commands` 枚举后 match 分发。
9. **Event 最终调用了什么？** 用户态：SELinux 注入（sepolicy.rs）、模块操作（module.rs/metamodule.rs/lua.rs）、授权同步（supercall.rs）；内核态：授权规则加载、KPM 装载、selinux_hide、管理器缓存刷新（user_event.c）。
10. **如何从 userspace 与内核建立联系？** 正向：syscall 45 携带 SuperKey 与命令号；反向：exec truncate 让内核 hook 收事件。两条通道都在 post-fs-data "before" 时就绪——而且"before"正是内核主动装好 sucompat hook 和 KPM 的时点。
11. **为什么从生命周期/调用链入手读源码？** 因为 APatch 的代码组织本身就是按生命周期切的：事件层（event.rs）→ 业务层（module/sepolicy/supercall）→ 契约层（scdefs.h 两仓库同源）。顺着生命周期读，等于顺着作者的心智模型读。
12. **下一篇追哪条链？** 我们已经知道 apd 在开机时被"召唤"，但 apd 这个二进制本身还有一堆没解开的谜：argv[0] 怎么让它一人分饰 su/resetprop/magiskpolicy 四角？`--superkey` 到底把它送到了什么权限级别？下一集就从那 23 行的 `main.rs` 和 386 行的 `cli.rs` 开始。

## 11 总结与思考题

这一篇我们其实只读懂了一个文件，但收获超出一个文件：**APatch 不是启动后把所有事一次做完，而是把自己的初始化精确拆进了 Android 开机生命周期的不同阶段**——而且拆的方式极其克制：内核只递一次"纸条"（注入 rc），时机判断完全交给 init；apd 每个阶段做完自己的事就退出，用"尽力而为 + 分级容错"守住"手机必须能开机"的底线；用户态与内核之间用 SuperCall 和 truncate 两条通道保持双向对话，连"before"回执都在内核侧有实事求是的动作（装 hook、载 KPM）。

留三道思考题，答案都能在本文引用的两个仓库的源码里找到：

1. 内核在收到 `post-fs-data` 的 "before" 时加载授权规则和 KPM（`user_event.c:27-31`），收到 "after" 时却什么都不做——**为什么这两件事必须卡在 "before" 而不能等到 "after"？** 提示：想想 post-fs-data 阶段结束时哪个东西要开始跑了。
2. `run_stage` 的 `block` 参数传 `false` 时脚本异步执行，那 service 阶段一个脚本死循环会怎样？去 `module.rs` 的 `exec_script` 找答案——apd 有没有兜底？
3. 内核对 `boot-completed` 事件的处理函数是**空的**（`user_event.c:39-41`），但 rc 模板里依然专门发了 `truncate su event boot-completed`——**一条没有处理器逻辑的通知，它的意义在哪？** 提示：看 `extra_event_init_args` 把事件广播给了谁。

下一篇：**《APatch 源码笔记（二）：apd 到底是什么？从 main.rs 追踪守护进程的启动与 multicall 设计》**。我们会解开机开到一半你就该问的那个问题：`su`、`resetprop`、`magiskpolicy`、开机事件处理器——凭什么都是同一个二进制？以及，apd 到底是不是一个"常驻"的守护进程？

---

## 复用边界

文件名和行号属于来源阅读的那两份树。作者标明「作者推测」的句子保持为推测。panther user 镜像把 APatch 收进 ROM 的流程是另一篇，目标不同，不要从本篇推出刷机步骤。
