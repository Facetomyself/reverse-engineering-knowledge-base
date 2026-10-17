---
schema_version: 2
id: apatch-source-note-09-apmodule
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
    ref: "https://mp.weixin.qq.com/s?__biz=MzI5NDkwNTAyOQ%3D%3D&mid=2247484833&idx=1&sn=f55f1fdcfd41c4e15d89a2d72df42c16&chksm=ec5af00bdb2d791d7c58687e7bd4ce42f635c18a3f3fec5bce8d4d73f65c2fff7b823fdf62b6#rd"
    basis: source-report

source_completeness: partial
relations: []
tags: [apatch, kernelpatch, source-report]
---

# APatch 源码笔记（九）：APModule 全景——目录、约定与生命周期总览

吴见午公开笔记，发布日 2026-09-07。来源把结论绑在 APatch `main@6ec140e` 与 KernelPatch `0.13.8`（`bcc8498`）。归档不把作者读源码的结论升级成刷机或运行时验收。

## 清洗与完整性说明

正文用已导出的 Markdown，没有从同伴 HTML 重抽。MD 中的 mmbiz 图为 3 张远程 URL，HTML 中不重复的 mmbiz URL 为 18 个；差额未逐张鉴定，可能含页面装饰，也可能含未进入 MD 的图。缺图没有用文字补。MD 表格分隔行 3，HTML `<table>` 3。远程图未本地化。代码围栏、行号和「源码明确行为 / 作者推测」的原词保留。

<a id="source-body"></a>
## 来源正文

![](https://mmbiz.qpic.cn/sz_mmbiz_png/VRGugOBduealiclaibyvaFDaX3vjibn6ICMreG0HicZq5RNiaEr9CmdIOWW63w3NOKia7ykpCyJl2IaP6hvYicQZdkxAyDTz8wZYnsE8JyWb9Lys7w/640?wx_fmt=png&from=appmsg)

本文基于双仓库交叉核实：**APatch** `main@6ec140e` + **KernelPatch** `tag 0.13.8`（HEAD `bcc8498`）。所有结论附 `仓库:文件:行号`。

## 01 这一篇我们要解决什么问题？

前八篇里，模块世界和我们打了好几次照面：post-fs-data 十七步里的 `exec_stage_script`（第 1 篇）、挂载被外包给的 metamodule（第 1 篇第 05 节）、模块自带的 `sepolicy.rule`（第 8 篇）——每次都擦肩而过。从这篇起，我们正式走进去。

作为"模块系统"阶段（第 9～13 篇）的开篇，本篇不钻细节，先立起三张地图：

1. **解剖图**：一个模块由哪些文件组成？"文件协议"是什么？
2. **状态机图**：模块从安装到卸载经历哪些状态？靠什么流转？
3. **关系图**：APatch 模块和 Magisk 模块到底是什么关系？兼容边界在哪？

## 02 为什么从这里开始？

因为模块是 APatch 对普通用户最有价值的部分，也是前八篇所有机制的最大"客户"：它消费 post-fs-data 的执行窗口（第 1 篇）、依赖 SELinux 规则注入和 restorecon（第 8 篇）、被授权体系保护（第 6 篇）。**没有模块地图，前面这些机制就只是散落的零件；有了它，你会看到每个零件都是为某个模块环节而生的。**

先给一句总纲，出自官方文档（`APatch:docs/cn/ap_module.md`）：

> "APatch 的模块运作机制与 Magisk 几乎是一样的……APatch 的模块实现是从 KernelSU 模块复制并修改而来。"

模块机制的祖源是 KernelSU 的 `ksud`（userspace 守护进程），被整体移植为 `apd`——而 ksud 的模块协议又承自 Magisk。所以**模块世界的"宪法"是三方共享的**，这决定了它的兼容面极宽：一个标准 Magisk 模块大概率不加修改就能在 APatch 上跑。

## 03 解剖图：模块的文件协议

官方文档给出的标准结构（`docs/cn/ap_module.md`，有删节）：

![图1：模块解剖图——module.prop 身份证、system/ 内容与五类成员的文件协议](https://mmbiz.qpic.cn/mmbiz_png/VRGugOBdueaoPwnfiavDxaaibDRZu960ibIr9AfA1eLy1ZHgHxg6gtqLEfa0ib2mTEzy6TGOD9Oj9TwX1spKPw0t5dKAUbXQQF7V56peOztEE2Q/640?wx_fmt=png&from=appmsg)

图1：模块解剖图——module.prop 身份证、system/ 内容与五类成员的文件协议

几条**硬协议**值得划重点：

- `module.prop` 是身份证：没有它，"这个文件夹将不被认为是一个模块"（文档原文）。字段有严格的 id 正则 `^[a-zA-Z][a-zA-Z0-9._-]+$`、`versionCode` 必须是整数、必须 LF 换行。代码侧的读取在 `read_module_prop`（`APatch:apd/src/module.rs:601-621`），按 UTF-8 properties 格式解析成 HashMap。
- **三个"自动化"的符号链接**（vendor/product/system_ext）由安装流程生成，文档明确警告"不要手动创建或修改"——它们是 overlayfs 挂载方案的配套件（第 12 篇）。
- **所有脚本跑在 BusyBox ash 的 standalone 模式**：`ASH_STANDALONE=1`（第 1 篇的 `get_common_script_envs` 注入过），命令一律用 BusyBox 内建实现，保证任何 Android 版本上行为可预测。有趣的是这个 BusyBox **直接采用 Magisk 项目编译的二进制**（文档原文："他们是完全一样的！"）——兼容性从工具链根上就锁死了。

`module.prop` 里还有一个 APatch 特有的暗号：`metamodule=1`。带这个字段的模块不是普通模块，而是"管理其他模块如何挂载"的 metamodule——`is_metamodule`（`APatch:apd/src/metamodule.rs:19`）就是查这个字段。它是第 12 篇的主角，这里先记个名字。

## 04 模块的"三种武器"：怎么改变一个系统

按改变系统的方式，模块的能力分三类，也是后续三篇的路线图：

**武器一：systemless 叠加（声明式，最常用）**。把想替换的文件放进 `system/` 对应路径，开机后由 metamodule 以 overlayfs 叠加到真 `/system` 之上：同名文件被覆盖、同名目录合并，**真分区一个字节不动**。删系统文件不能直接删——要放一个 `mknod filename c 0 0` 创建的字符设备节点（overlayfs 的 whiteout 语义）；整目录替换则用 `setfattr -n trusted.overlay.opaque -v y`。安装脚本里可以用 `REMOVE`/`REPLACE` 变量让安装器代劳（文档 155-172 节）。**谁来实现这套挂载？apd 自己不做**——它执行 metamodule 的 `metamount.sh`（第 1 篇第 05 节），默认实现同样是 overlayfs。这是第 12 篇的全篇主题。

**武器二：脚本（命令式，最灵活）**。四个开机阶段脚本对应第 1 篇的四阶段时序——post-fs-data.sh 阻塞抢窗口、post-mount.sh 阻塞收尾挂载、service.sh 和 boot-completed.sh 非阻塞跑服务。外加 `action.sh`（管理器按钮触发）和 `uninstall.sh`（清算）。执行器 `exec_stage_script` 的四层洋葱顺序（metamodule → `<stage>.d` 公共脚本 → 各模块 → Lua）第 11 篇逐行精读。

**武器三：声明式杂项**。`system.prop`（经 resetprop 改属性）、`sepolicy.rule`（第 8 篇）、`webroot` WebUI（第 13 篇）——各自有独立的加载通路。

## 05 状态机：三个旗标文件撑起的生命周期

模块没有数据库，**状态全部用旗标文件表达**——这是整个设计里我最欣赏的部分：状态即文件系统，崩溃恢复零成本。三个旗标加一个全局标记：

| 旗标 | 位置 | 写入者 | 语义 |
| --- | --- | --- | --- |
| `disable` | `<模块>/disable` | `disable_module`（`module.rs:678`） | 下次脚本执行时跳过此模块 |
| `remove` | `<模块>/remove` | `uninstall_module`（`:553`） | 下次开机清算移除 |
| `update` | `<模块>/update` | 安装落地流程 | 本次开机刚升级（prune 时清掉，`:306`） |
| `update` | `/data/adb/ap/update` | `mark_update`（`:134-136`） | 全局"有变更已落盘" |

状态变更的实现朴素到近乎简陋（`_change_module_state`，`:633-653`）：启用 = 删 `disable` 文件，禁用 = 创建它。`uninstall_module` 创建 `remove` 旗标后立刻 `mark_update()`；反悔用 `undo_uninstall_module`（`:594-599`）——扫描目录、按 `module.prop` 的 id 匹配、删掉 remove 旗标，**一步反悔，不用重装**。

画成状态机：

![图2：模块状态机——三个旗标文件撑起的生命周期（安装/生效/禁用/待移除/清算）](https://mmbiz.qpic.cn/sz_mmbiz_png/VRGugOBdueYmRqkeyNGMqa9CWKrf3RqP902APQ9RT5oEL11uJ6TnicTC5Az1IL9KiaWkibjHU3tqzHkmyMibd0sFDooQibiauYXcmHyzvIna0IwLI/640?wx_fmt=png&from=appmsg)

图2：模块状态机——三个旗标文件撑起的生命周期（安装/生效/禁用/待移除/清算）

## 06 生死簿：开机那一下的三场戏

状态机里最重的两次流转都发生在开机 post-fs-data（第 1 篇 17 步的第 1、2 步），值得单独看。

**第一场：A/B 交换 + 旗标继承**。`handle_updated_modules`（`module.rs:63-98`）把 `modules_update/<id>` 换到 `modules/<id>`，中间有个容易被忽略的保护：

```
    if module_dir.exists() {
        // If the old module is disabled, we need to also disable the new one
        disabled = module_dir.join(defs::DISABLE_FILE_NAME).exists();
        removed = module_dir.join(defs::REMOVE_FILE_NAME).exists();
        remove_dir_all(&module_dir)?;
    }
    std::fs::rename(updated_module, &module_dir)?;
    if removed { ...创建 remove 旗标... } else if disabled { ...创建 disable 旗标... }
```

**旧模块的禁用/待移除状态会被"继承"给新版本**。没有这段保护，升级一个已禁用模块的那次重启，会让它悄然复活。

**第二场：清算**。`prune_modules`（`:304-335`）先清掉所有模块的 `update` 旗标，然后对带 `remove` 旗标的模块执行两步送别：先跑 metamodule 的 `metauninstall.sh`（或清理 metamodule 符号链接），再跑模块自己的 `uninstall.sh`（阻塞等待），最后 `remove_dir_all`（`:344`）——先撤它在系统里的痕迹（挂载相关），再送走它自己。这个顺序是第 12 篇的重要伏笔。

**第三场：全局标记退场**。还记得第 1 篇 17 步的第 207 行吗——`fs::remove_file(module_update_flag)`。现在你知道 `/data/adb/ap/update` 这个全局标记的完整生命了：`mark_update` 在每次安装/卸载/启停后创建它（`:504,555,596,703`），开机 17 步走完删除它（`event.rs:207`）。**但我在两个子仓库里都没有找到它的读取方**——apd 只写只删，管理器侧 grep 不到消费代码。它像一枚"从 0 点到 0 点的邮票"（源码明确行为），读者是谁是个开放问题（思考题 3）。

## 07 与 Magisk 的兼容面：一张对照表

综合官方文档的差异标注与源码事实：

| 维度 | 兼容情况 |
| --- | --- |
| 目录结构 / 旗标 / 脚本约定 | 几乎一致（三方同源：Magisk → KernelSU ksud → apd） |
| BusyBox | 直接用 Magisk 编译的二进制，行为完全一致 |
| 安装脚本 installer.sh | 源自 Magisk 的 module_installer.sh（`apd/assets/installer.sh` 头注释自述） |
| 路径 | `/data/adb/ap/` 系（Magisk 是 `/data/adb/magisk/`） |
| 环境变量 | 额外注入 `APATCH=true`、`APATCH_VER`、`APATCH_VER_CODE` |
| SELinux | 直接使用 magiskpolicy（文档明示，第 8 篇） |
| Zygisk | 无内置支持（文档差异标注） |
| 独有面 | metamodule 机制、Lua 模块、KPM（内核模块，另一物种） |

一句话结论：**协议兼容、路径不同、暗号有别**。模块作者的最大迁移成本是路径和环境变量判断。

## 08 常见误区

1. **"点了禁用，脚本立刻停了"**——不。旗标只影响**下一次**脚本分发（`foreach_active_module` 过滤）；正在跑的脚本、已加载的属性都不受影响，直到下次开机或软重启。
2. **"卸载 = 删掉模块文件夹"**——危险。正确路径是 `remove` 旗标：重启时 prune 会先跑 `metauninstall.sh` 和 `uninstall.sh` 做善后（卸挂载、清文件），直接 rm 目录会跳过全部清算。
3. **"system/ 修改了真分区"**——overlayfs 叠加，`/system` 完好；这也是 OTA 后需要重装模块的根源（overlay 在新系统镜像上重建）。
4. **"删系统文件 = 放个同名空文件"**——必须是 `mknod filename c 0 0` 的 whiteout 节点，普通空文件只会以空文件覆盖。
5. **"没有 module.prop 也能跑脚本"**——不能被识别为模块，连脚本都不会被执行。

## 09 本篇源码地图

| 文件 | 本篇中扮演的角色 |
| --- | --- |
| `APatch:apd/src/module.rs` | 模块世界的全部逻辑（799 行）：状态机（553-706）、目录遍历（149-182）、清算（304）、清单（708-799） |
| `APatch:apd/src/defs.rs` | 模块路径与三个旗标文件名的唯一权威 |
| `APatch:docs/cn/ap_module.md` | 文件协议的官方权威（与代码一致） |
| `APatch:apd/assets/installer.sh` | 安装脚本模板（源自 Magisk，第 10 篇主角） |

## 10 总结与思考题

这一篇立起了模块世界的三张地图：**文件协议**（module.prop 身份证 + system/ 内容 + 旗标与脚本的目录宪法，三方共享自 Magisk）；**旗标状态机**（状态即文件，A/B 交换时旗标继承、清算时先 metamodule 后自身）；**兼容边界**（协议兼容、路径不同、暗号有别）。还清了两笔旧账：第 1 篇 17 步里 `handle_updated_modules`/`prune_modules`/`remove update flag` 三步的完整语义，以及全局 `update` 旗标"只写只删、未见读者"的开放问题。

三道思考题，前提均已核实：

1. `handle_updated_modules` 把旧目录的 `disable`/`remove` 旗标继承给新目录（`module.rs:70-95`）——推演一次"升级已禁用模块"的完整时间线，如果删掉继承逻辑，用户会观察到什么异常？
2. `prune_modules` 先执行 metamodule 的 `metauninstall.sh`、再执行模块自己的 `uninstall.sh`（`:314-330`）——如果顺序反过来，模块的卸载脚本会在什么"危险环境"里运行？
3. 全局旗标 `/data/adb/ap/update` 在 apd 侧只写（`mark_update`）只删（`event.rs:207`），两个子仓库均未见读取方——推测它的预期消费者是谁？给出一个用 rg 验证猜想的具体命令。

下一篇进入模块的一生中最惊险的旅程：**《APatch 源码笔记（十）：一个模块 ZIP 的安装之旅》**。安装为什么分"当场解压到 `modules_update/` + 下次开机生效"两步？installer.sh（那个源自 Magisk 的三百行脚本）在 busybox 里到底跑了什么？`customize.sh` 的 `REMOVE`/`REPLACE` 变量是谁在解析？以及第 05 节那个"身份校验"的正则在代码里的真身。我们从 `apd module install <zip>` 这条命令的第一行开始。

## 复用边界

文件名和行号属于来源阅读的那两份树。作者标明「作者推测」的句子保持为推测。panther user 镜像把 APatch 收进 ROM 的流程是另一篇，目标不同，不要从本篇推出刷机步骤。
