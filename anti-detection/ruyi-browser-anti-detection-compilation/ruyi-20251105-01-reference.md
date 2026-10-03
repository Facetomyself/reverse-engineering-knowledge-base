---
schema_version: 2
id: ruyi-webkit-win-minibrowser-reference
document_type: reference
original_date: '2025-11-05'
archived_date: '2026-10-02'
scope:
  targets: [webkit-win-minibrowser]
  client: webkit
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20251105-01.md#safari内核教程--webkit的环境构建和编译
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 只记录来源点名的安装器、仓库、脚本和解决方案文件。归档把多条命令粘在同一物理行，不能直接当可执行脚本。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 包名、环境变量和输出路径按原文字面保留。代理端口是作者本机端口。没有 WebKit 修订号。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只有 release 构建和生成 sln 两条入口。文末没有失败出口，展示效果也没有内容。
relations:
  - type: derived_from
    target: ./ruyi-20251105-01.md#safari内核教程--webkit的环境构建和编译
  - type: derived_from
    target: ./ruyi-20251105-01.md#编译流程
tags: [webkit, minibrowser, win11, source-report]
---

# Win11 WebKit MiniBrowser 构建入口参考

这张卡检索来源给出的 Win11 虚拟机 WebKit 依赖、环境变量，以及 `build-webkit` 的两条入口。它不把粘连的归档行恢复成可执行脚本。

<a id="parameters"></a>
## 环境与产物

来源把全部步骤限定在 `win11虚拟机纯净环境`。安装器原文写成 `chocolotey`，并要求管理员打开 `Powser Shell`。这两个拼写按原文保留。

依赖行点名 `xampp-81`、`python311`、`pywin32`、`core.autocrlf`，以及 cmake、gperf、llvm。同一物理行把 `ninja` 与 `python`、`pywin32` 与 `git` 粘成 `ninjapython` 和 `pywin32git`。拉源码前作者写本地端口 `7890`，配置行出现 `http://127.0.0.1:7890`，并与下一条 `git` 粘成 `7890git`。仓库地址是 `https://github.com/webkit/webkit.git`。

环境变量名是 `WEBKIT_LIBRARIES` 和 `WEBKIT_OUTPUTDIR`。归档把第一条赋值的结尾和 `set` 粘成 `winset`。bat 里还有 `CC=clang-cl` 与 `vswhere.exe -latest`。作者把产物位置写成 `WebKitBuild/Release/bin64/MiniBrowser.exe`。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 步骤限定在 Win11 虚拟机纯净环境 | s1 `ruyi-20251105-01.md:41`，quote: `win11虚拟机纯净环境` | source-report | webkit-win-minibrowser | 无镜像标识 |
| C2 | 原文包管理器拼写是 chocolotey | s1 `ruyi-20251105-01.md:43`，quote: `chocolotey` | source-report | 安装节 | 保留错字 |
| C3 | 原文要求管理员打开 Powser Shell | s1 `ruyi-20251105-01.md:43`，quote: `Powser Shell` | source-report | 安装节 | 保留错字 |
| C4 | 依赖里有 xampp-81 与 python311 | s1 `ruyi-20251105-01.md:55`，quote: `xampp-81` | source-report | 依赖行 | 与邻接命令粘连 |
| C5 | 同一行把 ninja 与 python 粘在一起 | s1 `ruyi-20251105-01.md:55`，quote: `ninjapython` | source-report | 依赖行 | 不能当干净命令 |
| C6 | 同一行把 pywin32 与 git 粘在一起 | s1 `ruyi-20251105-01.md:55`，quote: `pywin32git` | source-report | 依赖行 | 不能当干净命令 |
| C7 | git 配置里出现 autocrlf | s1 `ruyi-20251105-01.md:55`，quote: `core.autocrlf` | source-report | 依赖行 | 与安装命令同行 |
| C8 | 作者把拉代码的端口写成 7890 | s1 `ruyi-20251105-01.md:59`，quote: `端口是本地的7890` | source-report | 作者本机 | 不是通用端口 |
| C9 | 代理字面量是 127.0.0.1:7890 | s1 `ruyi-20251105-01.md:64`，quote: `http://127.0.0.1:7890` | source-report | 作者本机 | 与下一条命令粘连 |
| C10 | 克隆地址是 WebKit 官方仓库 | s1 `ruyi-20251105-01.md:64`，quote: `https://github.com/webkit/webkit.git` | source-report | 拉源码 | 无修订号 |
| C11 | 库目录变量名是 WEBKIT_LIBRARIES | s1 `ruyi-20251105-01.md:82`，quote: `WEBKIT_LIBRARIES` | source-report | 环境变量 | 与下一条 set 粘连 |
| C12 | 输出目录变量名是 WEBKIT_OUTPUTDIR | s1 `ruyi-20251105-01.md:82`，quote: `WEBKIT_OUTPUTDIR` | source-report | 环境变量 | 见 winset |
| C13 | 两条 set 在归档里粘成 winset | s1 `ruyi-20251105-01.md:82`，quote: `winset` | source-report | 环境变量行 | 文本形态 |
| C14 | 编译器赋值包含 CC=clang-cl | s1 `ruyi-20251105-01.md:89`，quote: `CC=clang-cl` | source-report | bat 行 | 整行被粘连 |
| C15 | 产物路径是 MiniBrowser.exe | s1 `ruyi-20251105-01.md:103`，quote: `WebKitBuild/Release/bin64/MiniBrowser.exe` | source-report | release 产物 | 作者指出的位置 |

<a id="interfaces"></a>
## 工具入口

安装命令指向 `chocolatey.org/install.ps1`，前面有 `Set-ExecutionPolicy`。Visual Studio 被写成新版 `vs2022`，另加两个组件：`LLVM工具集的MSBuild支持` 和 `适用于windows的C++Clang`。

bat 用 `vswhere.exe -latest` 找安装目录，并调用 `vcvars64.bat`。直接编译的命令是 `perl Tools/Scripts/build-webkit --release`。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C16 | 安装器主机是 chocolatey.org/install.ps1 | s1 `ruyi-20251105-01.md:48`，quote: `chocolatey.org/install.ps1` | source-report | 安装节 | 不展开远程脚本 |
| C17 | IDE 版本字面量是 vs2022 | s1 `ruyi-20251105-01.md:71`，quote: `vs2022` | source-report | 编译准备 | 无安装器版本 |
| C18 | 组件一是 LLVM 工具集的 MSBuild 支持 | s1 `ruyi-20251105-01.md:73`，quote: `LLVM工具集的MSBuild支持` | source-report | VS 组件 | 无工作负载 ID |
| C19 | 组件二是适用于 Windows 的 C++ Clang | s1 `ruyi-20251105-01.md:75`，quote: `适用于windows的C++Clang` | source-report | VS 组件 | 无工作负载 ID |
| C20 | 安装路径查询是 vswhere.exe -latest | s1 `ruyi-20251105-01.md:89`，quote: `vswhere.exe -latest` | source-report | bat 行 | 无失败分支 |
| C21 | 环境脚本名是 vcvars64.bat | s1 `ruyi-20251105-01.md:89`，quote: `vcvars64.bat` | source-report | bat 行 | 路径依赖 VSPATH |
| C22 | release 入口是 build-webkit --release | s1 `ruyi-20251105-01.md:98`，quote: `perl Tools/Scripts/build-webkit --release` | source-report | 直接编译 | 无日志判据 |

<a id="decision-flow"></a>
## 两条编译入口

来源先给一条直接 `--release`。调试节改成带 `--no-ninja` 和 `--generate-project-only`，再打开 `WebKit.sln`。归档把 `--generate-project-only` 与 `devenv` 粘成 `onlydevenv`，所以第二条不是干净的两行命令。

文末只有“展示效果”，没有图、没有退出码、也没有失败时停止或改道的句子。因此这里只保留入口形状，不升为流程。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C23 | 调试入口包含 --no-ninja | s1 `ruyi-20251105-01.md:110`，quote: `--no-ninja` | source-report | sln 入口 | 与相邻标记粘连 |
| C24 | 调试入口包含生成工程 | s1 `ruyi-20251105-01.md:110`，quote: `--generate-project-only` | source-report | sln 入口 | 后文与 devenv 粘连 |
| C25 | 解决方案文件名是 WebKit.sln | s1 `ruyi-20251105-01.md:110`，quote: `WebKit.sln` | source-report | sln 入口 | 无打开失败分支 |
| C26 | onlydevenv 表明两条命令被粘连 | s1 `ruyi-20251105-01.md:110`，quote: `onlydevenv` | source-report | 归档文本 | 文本形态 |

## 验证与限制

查询 `webkit`、`safari` 和 `webkit-win-minibrowser` 都没有已有参数卡。本卡不并入 Chromium 编译归档或 JWT、Cookie 启动卡。

没有 WebKit 修订、没有构建日志、没有失败出口。粘连行不能被本卡补全成分号或换行。
