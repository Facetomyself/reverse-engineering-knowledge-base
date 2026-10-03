---
schema_version: 2
id: anti-detection-ruyi-20251019-chromium-141-fetch-procedure
document_type: procedure
original_date: '2025-10-19'
archived_date: '2026-10-02'
scope:
  targets: [chromium]
  client: windows
  version: 141.0.7390.37
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20251019-01.md#3-使用-depot_tools-下载指定版本源码
    basis: source-report
  - id: s2
    ref: ./ruyi-20251019-01.md#windows-11-sdk版本要正确
    basis: source-report
  - id: s3
    ref: ./ruyi-20251019-01.md#五运行你编译出来的-chromium
    basis: source-report
  - id: s4
    ref: ./ruyi-20251019-01.md#1-编译-chrome-主程序
    basis: source-report
modules:
  - name: parameters
    anchor: prerequisites
    sources: [s2]
    basis: source-report
    limits: 只整理作者写下的 Windows 11 虚拟机、VS2022、SDK 10.0.26100.4654、Debugging Tools 下限和 141.0.7390.37 修订。未安装、未拉取、未编译。
  - name: decision-flow
    anchor: steps
    sources: [s1, s4]
    basis: source-report
    limits: 归档命令行含 U+00A0，并且把 cd 与 git clone、git 与 config--global 粘在一起。本卡不把粘连改写成可执行脚本，也不补作者没写的编译失败分支。
  - name: validation
    anchor: acceptance
    sources: [s3]
    basis: source-report
    limits: 两句成功都是作者自述。本轮没有源码树、没有 chrome.exe，不能把自述当成已编译。
relations:
  - type: derived_from
    target: ./ruyi-20251019-01.md#3-使用-depot_tools-下载指定版本源码
tags: [chromium, windows, depot-tools, source-report]
---

# Windows 上拉取并编译 Chromium 141.0.7390.37

这份流程只回答一个检索问题：如意私塾 2025-10-19 这篇归档，把哪一套 Windows 前提、哪一个修订号，以及哪几条工具调用，写成指定版本 Chromium 的拉取和编译。它不覆盖其他里程碑，也不覆盖 macOS 或 Linux。

`../chromium-fingerprint-compilation/01-基础/01-chromium-compilation-guide.md` 是另一篇归档，目标写成 unknown，SDK 写成 10.0.22621.2428，且没有 141.0.7390.37。近邻查询 `target=chromium` 与 `target=chromium module=decision-flow` 都是 0 条。不要把两套 SDK 并成一张卡。

适用前提是按作者点名的虚拟机和工具链对齐。作者没写的版本、被粘连破坏的命令文本、或想换成 qemu / 另一套代理时，不适用。本文不提供修好空格后的脚本。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 作者写下的要求 | 不足时 |
|---|---|---|
| 机器 | VMware、win11、内存 32G（可增加）、硬盘 300G（可增加）、8 核（可增加），并且禁止系统自动更新 | F1 |
| 编译器 | Visual Studio 2022 社区版，版本 >= 17.0.0；勾选 Desktop development with C++，以及 MFC 和 ATL 支持 | F1 |
| SDK | Windows 11 SDK，版本号 10.0.26100.4654 | F1 |
| 调试工具 | Windows SDK Debugging Tools，版本 >= 10.0.26100.3323；没有则在“程序和功能”里更改 Windows Software Development Kit，勾选 Debugging Tools for Windows | F1 |
| Git | 安装 Git for Windows，作者用 `git version` 检查 | F1 |
| depot_tools | 目录示例 `C:\src\depot_tools`，克隆 `https://chromium.googlesource.com/chromium/tools/depot_tools.git`，Path 放在最前面 | F1 |
| 环境变量 | `DEPOT_TOOLS_WIN_TOOLCHAIN=0`；`vs2022_install` 指到本机 VS2022 Community，示例路径是 `C:\Program Files\Microsoft Visual Studio\2022\Community` | F1 |
| Git 全局与代理 | 作者要求一次全局配置，键包括 core.autocrlf false、core.filemode false、core.preloadindex true、core.fscache true、branch.autosetuprebase always、core.longpaths true；http 与 https 代理都写成 `http://127.0.0.1:7890` | 不按这个代理或环境变量走 F1 |

身份那两行是占位姓名和占位邮箱，本卡不抄。归档里 `config--global` 与 `srcgit` 是粘连，见失败出口 F1 的文本限制，不要当成已经可粘贴的命令。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 对照前提表。作者把换 VM、不关更新、不按要求设置科学上网和环境变量，写成远程后看到的失败原因 | 缺项清单 | 齐备走 S2，否则 F1 |
| S2 | 只按来源已写出的键做一次全局 git 配置，并把 http/https 代理指到作者写的 `http://127.0.0.1:7890`。不补空格，不另选端口 | 配置键清单 | 键与代理都按来源走 S3，否则 F1 |
| S3 | 进入作者命名的 chromium 目录。`gclient config` 的 URL 是 `https://chromium.googlesource.com/chromium/src.git`。同步行原文是 `gclient sync --revision src@ 141.0.7390.37 --with_tags --with_branch_heads`（`src@` 与版本号之间有空格） | 同步是否报错 | 报错、休眠或断网走 F2；否则走 S4 |
| S4 | 进入 `src`。作者把这一步写成源码已经下载成功 | `src` 是否出现 | 没有目录走 F2；有目录走 S5 |
| S5 | `gn gen` 的目录是 `out\Default`。可选参数原文是 `is_debug=true is_component_build=true`。别的名字可以，但必须放在 `out` 下 | `out` 下的构建目录 | 不在 `out` 下走 F3，否则走 S6 |
| S6 | 作者点名的编译行是 autoninja、`-C`、`out\Default`、`chrome`。归档用 U+00A0 连接这些词。加速手段只包括把 `out\Default` 放上 SSD、让防御软件不扫代码目录、使用多核 | 是否看到作者点名的 `out\Default\chrome.exe` | 看不到走 F3；看得到才进入验收。可选 VS 分支不是验收 |

可选分支，不进入验收：`gn gen --ide=vs`，ninja 可执行文件写成 autoninja，输出 `out\Default`；要过滤时原文还有 `--filters=//chrome --no-deps`。作者只说 `.sln` 有几千个项目、加载会很慢。

<a id="outputs"></a>
## 输出

| 产物 | 作者怎么定位 | 本卡不声称的事 |
|---|---|---|
| 源码树 | 进入 `src` 后，作者写“到这里，你已经成功下载了 Chromium 的源代码” | 本轮没有这份树 |
| 构建目录 | `gn gen` 生成 `out\Default`，且必须在 `out` 下 | 没有生成记录 |
| 主程序 | 编译成功后运行 `out\Default\chrome.exe` | 没有这个文件 |
| 可选工程 | `out\Default\all.sln`，或带 `//chrome` 过滤的 VS 工程 | 过滤是否可加载未知 |

<a id="acceptance"></a>
## 验收

1. 拉取验收只采用作者原句：“到这里，你已经成功下载了 Chromium 的源代码”。这是 source-report。
2. 编译验收只采用作者原句：“你已经成功编译并运行了自己版本的 Chromium”，并且作者把可运行文件写成 `out\Default\chrome.exe`。这也是 source-report。
3. 反例：只有 gclient 的 URL、只有 `gn gen` 参数、或只有 VS 的 `.sln`，都不够。作者没有把 `.sln` 能打开写成通过。
4. 本轮没有执行拉取或编译。上面两句不能改写成已观察到的构建结果。

<a id="failure-exits"></a>
## 失败出口

F1：作者写的失败原因是自己替换工具、随意改步骤。原文点名把 VM 换成 qemu、对禁止更新不管、对某版本科学上网及其环境变量不管。先停，把前提表对齐后再从 S1 重来。另外，`srcgit` 与 `config--global` 是归档粘连；要先把命令分成作者点名的那几条，而不是直接粘贴粘连行。本卡不提供改写后的脚本。

F2：同步时不要休眠或断网。出错时作者只给了重跑“上边这一串” `gclient sync`。硬件卡顿、网络时断时续被写成外因。重跑仍失败就停。作者说的“我重新做一遍又可以”不是可复用出口。

F3：构建目录不在 `out` 下，或叙述里没有 `out\Default\chrome.exe`。来源没有 autoninja 失败后的补救步骤，这里停止，不另编编译修复。
