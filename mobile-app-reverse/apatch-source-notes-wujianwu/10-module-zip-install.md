---
schema_version: 2
id: apatch-source-note-10-module-zip-install
document_type: archive
original_date: "2026-09-07"
archived_date: "2026-10-08"
scope:
  targets: [apatch, kernelpatch]
  client: Android
  version: "APatch main@6ec140e; KernelPatch 0.13.8 bcc8498"
  observed_at: unknown
sources:
  - id: s1
    ref: "https://mp.weixin.qq.com/s?__biz=MzI5NDkwNTAyOQ%3D%3D&mid=2247484845&idx=1&sn=28a9352c0043fc3bcfa2b9534839ca4d&chksm=ec5af007db2d791168f0f39147000e186d381f235f8daee4ef5fa3e2f314b51d428246ba2f3f#rd"
    basis: source-report

source_completeness: partial
relations: []
tags: [apatch, kernelpatch, source-report]
---

# APatch 源码笔记（十）：一个模块 ZIP 的安装之旅本文基于双仓库交叉核实

吴见午公开笔记，发布日 2026-09-07。来源把结论绑在 APatch `main@6ec140e` 与 KernelPatch `0.13.8`（`bcc8498`）。归档不把作者读源码的结论升级成刷机或运行时验收。

## 清洗与完整性说明

正文用已导出的 Markdown，没有从同伴 HTML 重抽。MD 中的 mmbiz 图为 2 张远程 URL，HTML 中不重复的 mmbiz URL 为 14 个；差额未逐张鉴定，可能含页面装饰，也可能含未进入 MD 的图。缺图没有用文字补。MD 表格分隔行 1，HTML `<table>` 1。远程图未本地化。代码围栏、行号和「源码明确行为 / 作者推测」的原词保留。

<a id="source-body"></a>
## 来源正文

![](https://mmbiz.qpic.cn/sz_mmbiz_png/VRGugOBdueZSYNeMJdMTIFDYRy9koxsrpBNRs3mvpfB1qYlYJ56BLzBTIDcLiaUdvjRkMciakaIdCkb7qiaG8z3dV5utvqMickzFjszXywf31ic0/640?wx_fmt=png&from=appmsg)

本文基于双仓库交叉核实：**APatch** `main@6ec140e` + **KernelPatch** `tag 0.13.8`（HEAD `bcc8498`）。所有结论附 `仓库:文件:行号`。

## 01 这一篇我们要解决什么问题？

第 9 篇的模块状态机里有一条最复杂的边：「安装」——从用户在管理器里选中一个 ZIP，到下次开机模块落地生效。这条边内部远比表象热闹：**一次安装里发生了两次解压、两个目录、两个"身份校验"、外加一个 441 行的 shell 脚本**。

三个问题：

1. 安装为什么必须分「当场暂存到 `modules_update/` + 下次开机交换」两段？一段不行吗？
2. apd（Rust）和 installer.sh（shell）各自干了什么？为什么 apparent 上有**两次重复的解压**？
3. 第 9 篇留的谜：模块目录里的 `update` 旗标到底是谁创建的？

## 02 为什么从这里开始？

因为这是状态机的入口边，也是整个模块体系里**用户态脚本与 Rust 宿主协作最复杂的一次**——读懂它，第 11 篇的脚本执行、第 12 篇的 metamodule 就都有了参照物。入口很朴素：`apd module install <zip>`（`APatch:cli.rs:91-94`）直达 `install_module` → `_install_module`（`module.rs:363-506`）。

## 03 第一站：Rust 侧的安检闸门

`_install_module` 开头四道检查（`APatch:apd/src/module.rs:363-434`），每一道都有明确理由：

**检查零：必须在开机完成后**（`:364` → `:124-132`）：

```
// if someone(such as the module) install a module before the boot_completed
// then it may cause some problems, just forbid it
fn ensure_boot_completed() -> Result<()> {
    if getprop("sys.boot_completed").as_deref() != Some("1") {
        bail!("Android is Booting!");
    }
```

注释点名了防范对象——"某些模块自己会试图安装模块"。这也回答了主问题的一半：**安装动作本身要求系统已在正常运行**，"生效"自然只能留给下一次开机，两段式不是设计偏好，是时序约束的必然。

**检查一：身份证直接从 ZIP 里验**（`:376-402`）。apd 用 zip 库直接从压缩包里抽出 `module.prop` 解析，取 `id` 后过正则：

```
    // The id becomes a directory name under MODULE_DIR and is interpolated into
    // shell commands by the manager; reject path traversal at this trust boundary
    // (same rule as KernelSU and module_config.rs).
    let id_re = regex_lite::Regex::new(r"^[a-zA-Z][a-zA-Z0-9._-]+$")?;
    if !id_re.is_match(module_id) {
        bail!("invalid module id: {module_id}");
    }
```

这段注释是全篇最值得抄进笔记本的：模块 id 会变成**目录名**，还会被管理器**插值进 shell 命令**——不校验就是一个路径穿越/命令注入的洞。同一个正则也出现在 `module_config.rs` 的配置键校验里（注释自称 "same rule"），**一个正则守两道门**。

**检查二：是否需要挂载**（`:408-414`）：ZIP 里有 `system/` 且没有 `skip_mount`，则 `needs_mount = true`——这个判断接下来马上要用。

**检查三：metamodule 安全门**（`:417-434`）。如果设备上有一个"自定义安装器"的 metamodule 正处于启用或待生效状态，一个需要挂载的普通模块会被**直接拒绝安装**，并打印一个人工排版过的提示框（"Reboot to apply changes first"）。安装器替用户挡住了"挂载方案悬而未决时又塞一个要挂载的模块"这种自相矛盾的状态。另有检查四：metamodule 全局唯一（`:444-472`），重复安装直接劝退。

## 04 第二站：两次解压的怪事

过了安检，主角登场。第一步，apd 把整个 ZIP 解压到暂存目录（`:482-485`）：

```
    // unzip the image and move it to modules_update/<id> dir
    let file = fs::File::open(zip)?;
    let mut archive = zip::ZipArchive::new(file)?;
    archive.extract(&_module_update_dir)?;
```

第二步，执行安装脚本（`:488` → `exec_install_script`，`:45-61`）。它的实现方式很有意思——**没有脚本文件，是拼接出来的**：

```
const INSTALL_MODULE_SCRIPT: &str = concatcp!(
    INSTALLER_CONTENT,   // 编译期嵌入的 assets/installer.sh 全文
    "\n",
    "install_module",    // 调用其中的函数
    "\n",
    "exit 0",
    "\n"
);
```

然后用 `busybox sh -c "<拼接文本>"` 执行，环境变量里塞进 `ZIPFILE`（规范路径）和 `OUTFD=1`（recovery 模式的 UI 回传通道）。metamodule 可以用 `get_install_script`（`metamodule.rs:174`）把脚本换成自己的 `metainstall.sh`——安装流程的第一个可插拔点。

现在回答"两次解压"：installer.sh 的 `install_module` 函数一进来就——

```
  local MODDIRNAME=modules
  $BOOTMODE && MODDIRNAME=modules_update
  local MODULEROOT=$NVBASE/$MODDIRNAME
  MODPATH=$MODULEROOT/$MODID
  # Create mod paths
  rm -rf $MODPATH
  mkdir -p $MODPATH
```

（`APatch:apd/assets/installer.sh:336-346`）

`rm -rf $MODPATH` 把 apd 刚解压的暂存目录整个删掉，然后自己重新解压一遍（`:375`，排除 META-INF）。也就是说：默认安装路径下，apd 在 `:485` 那次解压是无效功（源码明确行为：两侧代码都摆在这里）。那为什么要先解一次？我的推测：给**非默认**的 metamodule 安装器（`metainstall.sh`）铺底——自定义安装器可能假设文件已就位、只做加工；而默认安装器按 Magisk 传统自成一体、宁可重解。谁对谁错，第 12 篇读到 `metainstall.sh` 时验证（思考题 1）。

## 05 第三站：installer.sh 的十步加工

这个 441 行的脚本头部自述出身——*"mostly from module_installer.sh and util_functions.sh in Magisk"*——它是模块作者的"官方装修队"。`install_module` 的主要工序：

1. **TMPDIR 重置并改标签**：`chcon u:object_r:system_file:s0 $TMPDIR`（`:319`）——连临时目录的 SELinux 上下文都安排了；
2. **环境判定**：`mount_partitions` + `api_level_arch_detect` + `BOOTMODE ? boot_actions : recovery_actions`——**支持在 Recovery 里刷模块**（非 BOOTMODE 走 recovery 动作，`ui_print` 也切换成 recovery 的回传协议，`:9-17`）；
3. **定位目标**：BOOTMODE 时 `MODPATH = /data/adb/…/modules_update/<id>`（`:336-342`）——装修队在暂存区干活，不碰现役目录；
4. **清场重解压**（上一节）；
5. **默认权限矩阵**（`:378-382`）：全树 `0:0 0755/0644`，`system/{bin,xbin,…/bin}` 提到 `0:2000 0755`（系统 bin 的传统属主），vendor bin 还要多贴一个 `u:object_r:vendor_file:s0` 上下文；
6. 执行模块的 `customize.sh`（`:386`）：模块作者的钩子，此时文件已解好、权限已铺好，`SKIPUNZIP=1` 的模块则在此自行解压（**注意：清场发生在判断之前，自定义解压拿到的也是空目录**）；
7. **REPLACE / REMOVE 加工**（`:389-399`）：

```
mark_remove() {
  mkdir -p ${1%/*} 2>/dev/null
  mknod $1 c 0 0            # whiteout：overlayfs 的"删除"语义
  chmod 644 $1
}

mark_replace() {
  # REPLACE must be directory!!!
  # https://docs.kernel.org/filesystems/overlayfs.html#whiteouts-and-opaque-directories
  mkdir -p $1 2>/dev/null
  setfattr -n trusted.overlay.opaque -v y $1   # 不透明目录：整目录替换
}
```

第 9 篇讲的 whiteout 与 opaque 目录，实现就这两段——`mark_replace` 的注释甚至直接给了内核文档链接，shell 脚本里罕见的学术风范；

8. `handle_partition` 三连（`:401-403`）：生成 vendor/product/system_ext 三个自动符号链接（第 9 篇目录树里"不要手动创建"的那几个）；
9. **BOOTMODE 收尾四连**（`:405-410`）——本篇最重要的一段：

```
  if $BOOTMODE; then
    mktouch $NVBASE/modules/$MODID/update            # ← 谜底在这
    rm -rf $NVBASE/modules/$MODID/remove 2>/dev/null
    rm -rf $NVBASE/modules/$MODID/disable 2>/dev/null
    cp -af $MODPATH/module.prop $NVBASE/modules/$MODID/module.prop
  fi
```

第 9 篇的谜底揭晓：现役目录里模块的 `update` 旗标是 installer.sh 创建的（不是 Rust 侧）。同时它清掉现役目录的 `remove`/`disable` 旗标、把新的 `module.prop` 拷过去——管理器的模块列表（读现役目录）立刻能看到"新版本待生效"。

10. **扫尾**：删掉 `customize.sh`/`README.md`/`.git*` 这些不属于运行期的杂物（`:413-415`）。

![图1：模块安装流水线——Rust 安检、暂存解压、installer.sh 装修与下次开机交换](https://mmbiz.qpic.cn/mmbiz_png/VRGugOBduebyNcDUU2NXWXyIoqaiaMW4LibhXZCVgVmdsyzSZP8T91KhOj4Bk1xwhA0XtZY5bttJicyhFj6zcm4xN7BpXkGlkjTLPicrql1x0Cc/640?wx_fmt=png&from=appmsg)

图1：模块安装流水线——Rust 安检、暂存解压、installer.sh 装修与下次开机交换

## 06 "升级即复活"与旗标继承的合谋

第 05 节第 9 步里那句 `rm -rf …/disable` 藏着一个行为契约：**升级一个模块，会重置它的启停状态**（清掉 disable）——这是 Magisk 血统的传统。但第 9 篇讲过 `handle_updated_modules` 会把旧目录的 `disable`/`remove` 继承给新目录（`module.rs:70-95`），两者矛盾吗？

不矛盾，它们**各管一段时间窗**：installer 在"安装瞬间"清旗标 → 默认升级即激活；如果用户在"安装后、重启前"这个窗口里去管理器把模块禁用（disable 旗标写进现役目录），那么重启时 `handle_updated_modules` 读到旧目录的 disable → 继承给新目录 → 升级后的模块保持禁用。**安装器负责默认值，继承逻辑负责保护窗口期内的用户决定**——两个机制一份契约。

## 07 一个诚实的疑点：restorecon 的目标目录

安装收尾处（`:490-496`）对 `system/` 树设置权限并执行 `restore_syscon`（贴 `u:object_r:system_file:s0`，第 8 篇的善后组）。但看仔细：

```
    let module_system_dir = PathBuf::from(module_dir.clone()).join("system");
```

`module_dir` 是**现役目录** `/data/adb/modules/<id>`，不是刚解压的暂存目录。也就是说：新装时这段代码作用于一个刚创建的空目录（`:477-481` 创建的）；升级时作用于**旧版本**的文件。暂存区的文件没有在这里贴标签。这是一个可以如实记录的疑点（源码明确行为），后果评估需要理解 metamodule 挂载时的标签处理——留给第 12 篇验证，本篇只立案不判决。

另外一笔带过：安装过程**不触碰**模块配置系统——`module_config.rs` 那套二进制配置（魔数 `0x4150544D` 即 ASCII "APTM"、版本 1、键 256 字符/值 1MB/条目 32 条的硬限制）是独立于 ZIP 生命周期的持久层，开机时只清临时配置（`event.rs:60`），完整机制在第 16 篇。

## 08 常见误区

1. **"解压完成就是安装完成"**——解压只是原料上架，installer.sh 的权限矩阵、customize.sh、REPLACE/REMOVE 加工、收尾四连才是"装修"。
2. "`SKIPUNZIP=1` 能保住 apd 解压的文件"——不能。`rm -rf $MODPATH` 在判断之前（`installer.sh:345`），`SKIPUNZIP` 模块拿到的是空目录，必须自己解压。
3. **"REMOVE 变量直接删系统文件"**——是创建 whiteout 节点（`mknod c 0 0`），真分区完好。
4. **"升级模块一定保留禁用状态"**——取决于时机：安装瞬间旗标被清（默认复活），仅当禁用发生在"安装后重启前"窗口才被继承保护。
5. **"开机过程中可以装模块"**——`ensure_boot_completed` 直接拒绝（`module.rs:126-132`）。

## 09 本篇源码地图

| 文件 | 本篇中扮演的角色 |
| --- | --- |
| `APatch:apd/src/module.rs:363-506` | `_install_module`：四道安检 + 暂存解压 + 调安装脚本 + mark_update |
| `APatch:apd/src/module.rs:28-61` | 拼接式安装脚本（installer + install_module + exit 0）与 metamodule 覆盖点 |
| `APatch:apd/assets/installer.sh` | 441 行装修队：重解压/权限矩阵/customize/whiteout/收尾四连 |
| `APatch:apd/src/module_config.rs` | "APTM" 二进制配置（安装不碰它，第 16 篇） |
| `APatch:apd/src/metamodule.rs:174` | 安装脚本的可插拔点（metainstall.sh） |

## 10 总结与思考题

一次看似简单的"安装"，拆开是三站流水线：**Rust 安检（开机完成守卫、ZIP 内直读身份证、id 正则守信任边界、metamodule 安全门）→ 暂存解压（ modules_update/，默认路径下注定被重来一次）→ installer.sh 装修（重解压、权限矩阵、customize.sh、whiteout/opaque、收尾四连打上 update 旗标）**。两段式的必然性来自 `ensure_boot_completed` 的时序约束；两次解压的怪事是"默认安装器自成一体"与"为自定义安装器铺路"的叠加；而 `update` 旗标的创建者之谜，谜底藏在 shell 的 `mktouch` 里——这再次验证了本专栏的方法论：**问题的答案经常不在你以为的那门语言里**。

三道思考题，前提均已核实：

1. apd 的预解压在默认安装器下是无效功（`:485` vs `installer.sh:345`）——设计一个最小验证：去读 `metamodule::get_install_script` 及任一真实 metamodule 的 `metainstall.sh`，判断自定义安装器是否依赖预解压的文件；把你的结论写成一段"源码明确行为 vs 作者推测"。
2. 第 06 节的时间窗：模块 A（v1，已启用）正在运行，用户装上 v2，十分钟后在管理器里禁用 A，然后重启。逐步推演 installer 清旗标、用户写旗标、`handle_updated_modules` 继承三个动作的先后与结果。
3. `mark_replace` 的注释链到 overlayfs 官方文档（`installer.sh:278-279`）——从"opaque 目录对合并结果隐藏下层所有条目"出发，解释为什么"整目录替换"必须用 `setfattr` 而不能像 REMOVE 那样逐文件 whiteout。

下一篇拆开模块的"发动机"：**《APatch 源码笔记（十一）：模块脚本在什么时候跑——exec_stage_script 与 run_stage 细读》**。第 1 篇我们知道了四层洋葱的顺序（metamodule → `<stage>.d` → 各模块 → Lua），这一篇下到每一层里面：脚本用什么身份、什么 cwd、什么环境变量执行？`block=false` 的异步脚本死循环了怎么办——apd 有没有超时兜底？`get_common_script_envs` 注入的 `AP_MODULE` 变量在脚本里能干什么？

## 复用边界

文件名和行号属于来源阅读的那两份树。作者标明「作者推测」的句子保持为推测。panther user 镜像把 APatch 收进 ROM 的流程是另一篇，目标不同，不要从本篇推出刷机步骤。
