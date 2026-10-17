---
schema_version: 2
id: apatch-source-note-04-bootimg-kpimg
document_type: archive
original_date: "2026-09-04"
archived_date: "2026-10-08"
scope:
  targets: [apatch, kernelpatch]
  client: Android
  version: "APatch main@6ec140e; KernelPatch 0.13.8 bcc8498"
  observed_at: unknown
sources:
  - id: s1
    ref: "https://mp.weixin.qq.com/s?__biz=MzI5NDkwNTAyOQ%3D%3D&mid=2247484794&idx=2&sn=b96342ea7a723bdacf41cabfdc63234e&chksm=ec5af0d0db2d79c626dc9537b057423966b2f13f714e2a132be9bddf6c5e095606f9674afd7d#rd"
    basis: source-report

source_completeness: partial
relations: []
tags: [apatch, kernelpatch, source-report]
---

# APatch 源码笔记（四）：boot.img 是怎么被改的——kptools 注入与 kpimg 的开机自举

吴见午公开笔记，发布日 2026-09-04。来源把结论绑在 APatch `main@6ec140e` 与 KernelPatch `0.13.8`（`bcc8498`）。归档不把作者读源码的结论升级成刷机或运行时验收。

## 清洗与完整性说明

正文用已导出的 Markdown，没有从同伴 HTML 重抽。MD 中的 mmbiz 图为 5 张远程 URL，HTML 中不重复的 mmbiz URL 为 26 个；差额未逐张鉴定，可能含页面装饰，也可能含未进入 MD 的图。缺图没有用文字补。MD 表格分隔行 1，HTML `<table>` 1。远程图未本地化。代码围栏、行号和「源码明确行为 / 作者推测」的原词保留。

<a id="source-body"></a>
## 来源正文

![](https://mmbiz.qpic.cn/mmbiz_png/VRGugOBdueZHUB72DMhYCzVOvhkUIZwIiaNxlVJAewiaoobCQmONCDBzTaeX73IrUlN0XY3LmG5w7veVicYe88N1ib68P8BU7bOXAH1K94YUHpE/640?wx_fmt=png&from=appmsg)

本文基于双仓库交叉核实：**APatch** `main@6ec140e` + **KernelPatch** `tag 0.13.8`（HEAD `bcc8498`）。所有结论附 `仓库:文件:行号`。

## 01 这一篇我们要解决什么问题？

前三篇我们一直站在"内核已经被补过"的世界里：supercall 早已就位（第 3 篇）、rc 触发器早已注入（第 1 篇）。但这一切的前提——**kpimg 是怎么进入内核的？它被塞在镜像的哪个位置？开机第一纳秒它怎么拿到控制权？**——我们从未打开过。

这一篇把时间倒回第 0 秒，回答三个问题：

1. 用户在管理器里点"安装"，`boot.img` 到底被改了哪几个字节？
2. kpimg 塞进一个**没有任何符号、地址随机化**的内核镜像后，开机时怎么找回自己的数据、怎么把控制权交还内核？
3. 第 3 篇的 `supercall_install` 和第 1 篇的 rc 注入，到底谁先谁后？

## 02 背景：boot.img 与两个前提

boot.img 是 Android 的引导镜像，结构大致是：`头部（元数据）→ 内核 → ramdisk → …`，头部里记录各段的加载地址和大小，尾部常带 AVB 签名 footer。APatch 改的就是其中的**内核段**。

动手之前有两个硬前提，都写进了代码：

- `CONFIG_KALLSYMS=y`。`APatch:app/src/main/assets/boot_patch.sh:55-60` 是一个一票否决的检查：内核镜像里必须残留 kallsyms 符号表（哪怕 stripped），否则直接放弃——原因第 05 节见。
- `CONFIG_KALLSYMS_ALL` 最好也开着。没有它脚本不会中止，但会警告 *"APatch has patched but maybe your device won't boot"*（`boot_patch.sh:87-91`）——不完美的支持，如实告知风险。

## 03 管理器视角：一次"安装"的完整流水线

用户在 App 里选择 boot.img 点安装后，`PatchesViewModel.doPatch`（`APatch:PatchesViewModel.kt:398`）开始跑。有三个值得注意的细节：

细节一：密钥的默认值是 `"su"`（`:424`——用户不填或勾选免密钥时）。这个字符串的真正含义要到 kptools 那边才揭晓，先按下不表。

**细节二：执行方式是一次跨仓库的"探测接力"**（`:428-437`）。新内核走 `truncate <key> -Z u:r:magisk:s0 -c ./busybox sh boot_patch.sh ...`——直接借用第 1 篇讲过的 truncate 提权通道拉起打补丁脚本；探测失败（老版本内核）才回退到普通 root shell。安装 App 本身还没提权能力时，是**已安装的旧内核**在给打补丁过程开路。

**细节三：管理器支持往镜像里预埋 KPM**（`:444-465`）。每个附加项转成 kptools 的 `-M 文件 -A 参数 -V 事件 -T 类型` 参数——"编译期预载的内核模块"，事件类型就是第 1 篇见过的 `post-fs-data` 那些。

真正的活由 113 行的 `boot_patch.sh` 干，五步（`APatch:boot_patch.sh`）：

```
./kptools unpack "$BOOTIMAGE"                          # ① 拆包出内核（46 行）
./kptools -i kernel -f | grep CONFIG_KALLSYMS=y        # ② 硬检查（55 行）
./kptools -p -i kernel.ori $KPT_ARGS -k kpimg -o kernel # ③ 核心补丁（75 行）
./kptools repack "$BOOTIMAGE"                          # ④ 重打包（85 行）
flash_image new-boot.img "$BOOTIMAGE"                  # ⑤ 刷入（102 行）
```

现在揭晓 `"su"` 的谜底——第 ③ 步的参数构造（`boot_patch.sh:71-72`）：

```
KPT_ARGS=""
[ "$SUPERKEY" != "su" ] && KPT_ARGS="-S $SUPERKEY"
```

密钥是 `"su"` 时，一个密钥参数都不传；否则用 `-S`（root-skey，只存 SHA-256 哈希）。结合 kptools 的帮助原文（`KP:tools/kptools.c:32-76`）：

![图1：kptools 密钥参数三态——-s 明文 / -S 哈希 / 不传（默认 su）](https://mmbiz.qpic.cn/mmbiz_png/VRGugOBdueb7FbWFOOhkQm2HB59aIKt0F1ZibsaQ9MhsF3bK4hiaHfFLvnCuJxGzyGjjgu78ibjHJmgxSvIwhdXzysBFCOWgURWpYfAruPRsPQ/640?wx_fmt=png&from=appmsg)

图1：kptools 密钥参数三态——-s 明文 / -S 哈希 / 不传（默认 su）

`-s` 存明文，`-S` 只存哈希（之后可用 `-r` 重置）。三种组合对应三代安全模型（与第 3 篇的 `auth_superkey` 双通道完全对上）：`-s` 是远古明文模式；`-S` 是哈希模式——内核侧首次哈希命中后把密钥"晋升"为明文（`KP:predata.c:60-65`）；而**不传任何密钥**时，内核启动自己生成 15 位随机密钥并启用 root-key 校验（`KP:predata.c:350-361`）——密钥通道实质关闭，只剩管理器 APK 签名通道。这就是"新默认签名授权"在打补丁那一刻就注定的结局。

## 04 kptools 解剖：boot.img 被改了哪几个字节

kptools 的 `-p` 命令发现输入是 boot 镜像（`ANDROID!` 魔数）后一步到位：拆包 → 补内核 → 重打包（`KP:tools/bootimg.c:1159-1233`）。外围工作相当繁琐但诚实：内核压缩格式自动识别（gzip/LZ4/bzip2/xz 七种；**zstd 会被明确拒绝**——*"Kernel uses zstd, we have not supported it yet"*，`bootimg.c:870`；xz/LZMA 重打包时转回 gzip）；尾部 AVB footer 迁移、头部的 `id[]` 哈希用 SHA-256/SHA-1 重算（`bootimg.c:1026-1121`）。

真正的手术只有两刀。

**第一刀：kpimg 追加在内核后面。** 不是藏在洞里，也不是放进 ramdisk——kpimg 被原样追加到（4K 对齐后的）内核镜像末尾，kpimg 自带的 `setup_preset` 数据块恰好位于追加区的开头（`KP:tools/patch.c:726-747`）：

```
int align_kimg_len = align_ceil(ori_kimg_len, SZ_4K);
int out_img_len = align_kimg_len + kpimg_len;
...
memcpy(out_kernel_file.kimg + align_kimg_len, kpimg, kpimg_len);
preset_t *preset = (preset_t *)(out_kernel_file.kimg + align_kimg_len);
```

所以"补丁后内核变大"——boot.img 里内核段尺寸字段被改写，其余原样。

**第二刀：改写内核镜像的第一个分支指令。** arm64 内核 Image 的开头是一条跳转指令，CPU 一进来就执行它。kptools 把这条指令改成"跳到 kpimg+4K"（`KP:tools/patch.c:856-860`）：

```
// modify kernel entry
int text_offset = align_kimg_len + SZ_4K;
b((uint32_t *)(out_kernel_file.kimg + kinfo->b_stext_insn_offset),
  kinfo->b_stext_insn_offset, text_offset);
```

`b()` 生成的就是一条 arm64 裸跳转（`tools/common.c:18`）。为什么是 +4K？因为 kpimg 的链接脚本把前 4K 固定留给了 `setup_preset` 数据，代码段 `setup_entry` 紧随其后（`KP:kernel/kpimg.lds:15-29`）。原入口指令被备份进 `header_backup`（`patch.c:831`）， kpimg 用完后原样写回（第 06 节）。

顺带一份"预约单"：kptools 只记录 `paging_init` 的相对跳转偏移（`patch.c:857-858`：`setup->paging_init_offset = relo_branch_func(...)`），真正把这条指令改写成跳转的活，留给开机时的 `setup_entry` 去执行——为什么挑 `paging_init`，第 06 节见分晓。

**preset：塞给未来的自己的包裹单。** 写进镜像的数据块内容极多（`patch.c:763-854`）：密钥、各段尺寸偏移、以及一整张**预解析好的内核符号偏移表** `patch_config`——`rest_init`、`kernel_init`、`copy_process`、`avc_denied`、`slow_avc_audit`、`input_handle_event`……这张表就是第 1、3 篇所有 hook 的靶点清单，全部在打补丁时离线解析好。

![图2：两刀手术——原内核 Image 与补丁后镜像的布局](https://mmbiz.qpic.cn/sz_mmbiz_png/VRGugOBdueZ30zD5nqS5yEdxh46iaQznE1OGYiccIb6fJia7NorfmRfNDu3raicUoy9wZ6NLUGDPuBwn3rp5QBial0kU8b4MJXEZ3z4JODSKxPaM/640?wx_fmt=png&from=appmsg)

图2：两刀手术——原内核 Image 与补丁后镜像的布局

## 05 最难的一步：无符号内核里"认路"

整个方案成立的前提是：kptools 拿到的只是一个 stripped 的内核二进制，却能解析出上面那张符号表。这就是 `tools/kallsym.c`（千余行）的价值——**从零重建内核的 kallsyms 表**。

思路（`kallsym.c:1019-1090`）：内核的 kallsyms 数据（符号名压缩 token 表、地址数组）没有指针、只有纯数据，所以能靠启发式扫描找回来——先 memmem 找 `"Linux version "` banner 解析内核版本（`kallsym.c:47-95`），再找 token 表、名字区、偏移数组，多轮重试并对相对偏移布局做校正。LTO/ICF 内核那些 `foo.cfi_jt` 后缀符号也有专门处理（`symbol.c:28-33`）。这也是 `CONFIG_KALLSYMS=y` 一票否决的原因：没有这张表，kptools 一个符号都解析不出，preset 里的偏移无从填起。

## 06 开机自举：控制权的三次接力

现在把镜头切到刷好镜像后的第一次开机。kpimg 拿到控制权、干完活、把内核还回去，一共**三次接力**（全部 file:line 已核实）：

接力一：入口分支 → `setup_entry`（汇编，无内存可用）。 CPU 执行被改写的分支进入 kpimg（`KP:kernel/base/setup1.S:319-398`）。此时页表未建、内存管理器未起，这段汇编只能用 PC 相对寻址：算出内核物理基址 `kernel_pa`（`setup_offset` 反推，setup1.S:342-345），把 kpimg 本体和 extras 拷到安全位置，执行第 04 节预约的 `paging_init` 补丁，把一段特殊代码拷进"map hole"，**恢复原入口指令**，然后 `br` 跳回内核原入口——内核毫发无损地继续启动。

接力二：`paging_init` → map hole。 内核跑到内存管理初始化调用 `paging_init()` 时，第一条指令已被改成跳进 map hole——一段 kptools 打补丁时"牺牲"某个内核函数体换来的 4K 落脚地。牺牲者有严格的候选名单，首选是 `tcp_init_sock`（`KP:tools/symbol.c:132-148`：`tcp_init_sock → udp_init_sock → inet_create → … → panic`），选一个冷门网络函数，把它的函数体（0x1000 字节）临时换成 KP 的内存迁移代码（GKI 内核还要顺手 NOP 掉里面的 PAC 指令）。`_paging_init`（`KP:kernel/base/map.c:468-593`）在这里完成惊险一跳：用 memblock 分配新内存、构建页表、把 kpimg 本体拷进有映射的新家、恢复被 hook 的那条指令、调用**真正的** `paging_init()` 干完原本的活，最后跳进新家执行 `start()`。之所以选 `paging_init` 当第一个 hook（思考题 2 的答案方向）：它是**内核里第一个"内存管理已可用、但一切还没铺开"的时点**——没有 memblock 和页表，KP 自己连立足之地都造不出来。稍后 `restore_map()`（`start.c:519-541`）把 `tcp_init_sock` 的原始字节从备份里抄回去，被牺牲的函数死而复生。

接力三：`start()` → `patch()`。 在新家里（`KP:kernel/base/start.c:710-759`），kpimg 解析符号、给自己设置页表权限、恢复 map hole、初始化密钥数据（`predata_init`），然后调用 `patch()`（`patch.c:152`）装下一批钩子：panic（为了死时能留下遗言，`patch.c:162-167`）、`rest_init`（找不到符号就退而求其次 hook `cgroup_init`，`:172-177`）、`kernel_init`（`:181-186`）。干完所有事，`patch()` 手写结尾直接返回到 `paging_init` 的调用者——**内核从此感觉不到自己的启动路径被人绕过又绕回来过**。

到这里，回答本篇开头第三问——**完整时间线**：

![图3：完整时间线——从打补丁到 apd 登场](https://mmbiz.qpic.cn/mmbiz_png/VRGugOBduebG0S0biaHwtftT2YnuKWZVcOGsIr06osCyic8dLOZFeOBibyic7ExsR9BQ5BmU1TtefbweyBPIRqWibxbH4wLug66ukl4dLc78xpTQ/640?wx_fmt=png&from=appmsg)

图3：完整时间线——从打补丁到 apd 登场

答案：supercall（`:85`）在前，rc 注入（`:104`）在后——而且顺序是必然的：rc 注入的 openat hook 工作在 init 进程里，它发出的第一条 `truncate su event early-init before` 要靠 supercall 门铃才能被收货。先装门铃，再发传单。

![图4：三次接力——打补丁 → setup_entry → map hole → start()](https://mmbiz.qpic.cn/sz_mmbiz_png/VRGugOBdueaBRXp49MWArbOsdczSCGyKzpIx77RiaibyBCNTQ3dbmibUN5zWuYopRzcPgOITc4S88t6XHTib2SibGek4c3jXbibmzTHldrEaf7jlk/640?wx_fmt=png&from=appmsg)

图4：三次接力——打补丁 → setup_entry → map hole → start()

## 07 澄清一个流传很广的误解：kptools 根本不看 KMI

很多资料说"APatch 要按 KMI（内核模块接口，如 `android14-5.15`）匹配版本"。**源码明确行为**：`tools/` 目录里 grep 不到任何 KMI 字符串——kptools 打补丁时只做三件事：从 banner 解析内核版本号、按 `kver >= 5.10` 判定 GKI 走不同的 map hole 对齐（`patch.c:611`）、对 6.12.23+ 内核做一个 12 字节的 PI_MAP 禁用补丁（`patch.c:613-622`）。缺符号才会中止（没有 `printk`/`panic`/`rest_init`/`copy_process` 直接退出）。

KMI 概念真正的主场是越狱模式的 `.ko` 分发——预编译的 `kernelpatch.ko` 必须按 KMI 匹配目标内核，所以 APatch 的构建脚本才会按 `android12-5.10` 到 `android16-6.12` 逐 KMI 下载。刷 boot.img 的 kpimg 路线是"现场解析、量身定做"，不需要 KMI；拿现成 .ko 的越狱路线是"预制菜"，必须对 KMI。这个对比是第 18 篇的核心，这里先立此存照。

## 08 常见误区

1. **"kpimg 藏在内核的空隙里"**——arm64 上不是。它是追加在内核镜像之后（4K 对齐处），靠改写入口分支直达；藏洞技术（扫 PT_LOAD 零填充区）是 x86_64 路径的专属（`tools/x86_64.c:445-471`）。
2. **"APatch 修改了 /system"**——打补丁阶段只动 boot.img 一个文件；`/system` 的修改全部是运行时挂载（第 12 篇的 systemless 话题）。
3. "`-s` 和 `-S` 是同一个参数的全称/缩写"——不是。`-s` 存明文密钥、`-S` 只存 SHA-256 哈希（且支持事后 `-r` 重置）；`boot_patch.sh` 永远只用 `-S`。
4. **"kptools 需要内核源码"**——不需要，只需要 `CONFIG_KALLSYMS=y` 留下的符号表数据；整个 kallsym.c 就是为"无源码无符号"设计的。

## 09 本篇源码地图

| 文件 | 本篇中扮演的角色 |
| --- | --- |
| `APatch:app/src/main/assets/boot_patch.sh` | 打补丁五步流水线；`su` 密钥 = 不传 key；`-S` 哈希模式 |
| `APatch:PatchesViewModel.kt` | `doPatch`：探测接力拉脚本、KPM 预埋转 `-M/-A/-V/-T` |
| `KP:tools/kptools.c` | CLI：`-p/-u/-r/-d/-f/-l`、`-s/-S`、`-M/-E/-T/-N/-V/-A` |
| `KP:tools/bootimg.c` | boot 镜像拆包/重打包/压缩识别/AVB 与 hash 修复 |
| `KP:tools/patch.c` | kpimg 追加布局、入口分支改写、preset 填充、6.12 补丁 |
| `KP:tools/kallsym.c` | 从 stripped 内核重建 kallsyms（无源码认路） |
| `KP:tools/symbol.c` | map anchor 候选表（tcp_init_sock 优先）、patch_config 填充 |
| `KP:kernel/base/setup1.S` | 接力一：`setup_entry` 汇编自举 |
| `KP:kernel/base/map.c` | 接力二：`_paging_init` 内存自举 |
| `KP:kernel/base/start.c` / `patch.c` | 接力三：`start()` 与 hook 安装链 |

## 10 总结与思考题

这一篇补上了整个故事的"第 0 秒"：**kptools 用两刀（追加 kpimg + 改写入口分支）和一张离线解析的符号偏移表，把一个 stripped 内核变成了带 KP 的内核**；开机后 kpimg 通过三次接力（入口汇编 → map hole 内存自举 → `start()`）完成从"镜像末尾的寄生者"到"内核内部常驻者"的转变；`before_rest_init` 里的安装顺序（supercall → kstorage → sucompat → rc 注入）保证了第 1 篇和第 3 篇的世界在正确的时间就位。而密钥在打补丁那一刻就被写死进 preset——"su"意味着密钥通道自废，哈希意味着可换代，这就是三代安全模型的开端。

三道思考题，前提均已核实：

1. `boot_patch.sh:71-72` 里 superkey 为 `"su"` 时完全不传 `-S`——结合 `KP:predata.c:350-361`（无用户密钥 → 生成随机密钥 + 启用 root-key），推演此时内核里存着什么、普通 App 的 supercall 通道处于什么状态。
2. kptools 为什么选 `paging_init` 作为第一个被 hook 的内核函数，而不是更早的 `start_kernel`？（提示：回看接力二——`_paging_init` 在 map hole 里干了 memblock 分配和页表构建两件事。）
3. `patch.c:831` 把原内核入口的头 8 字节存进 `header_backup`，`setup_entry` 跑完就写回——既然那条分支指令只会被 CPU 执行一次，为什么还要恢复原样？（提示：想想 `kptools -u`（unpatch）要怎么工作，以及 `memmem` 扫 `KP1158` 魔数定位 preset 的前提是什么。）

下一篇回到用户态的主战场：**《APatch 源码笔记（五）：su 是怎么来的——从 execve hook 到 root_shell》**。你在终端敲下 `su` 的那一刻，内核的 execve hook 是在哪个函数里拦住你的？`commit_su` 把 uid、capability、SELinux 上下文改到什么程度？`apd.rs` 里那行 "we are root now, this was set in kernel!" 之后，`set_identity` 又是设给谁的？我们把第 2 篇只看了门牌的 `root_shell` 彻底走一遍。

## 复用边界

文件名和行号属于来源阅读的那两份树。作者标明「作者推测」的句子保持为推测。panther user 镜像把 APatch 收进 ROM 的流程是另一篇，目标不同，不要从本篇推出刷机步骤。
