---
schema_version: 2
id: nuitka-onefile-payload-recovery-procedure
document_type: procedure
original_date: 2026-07-08 至 2026-07-16
archived_date: '2026-10-02'
scope:
  targets: [Nuitka onefile]
  client: Windows
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./nuitka-onefile-payload-recovery.md#适用与不适用"
    basis: source-report
  - id: s2
    ref: "./nuitka-onefile-payload-recovery.md#外层onefile-bootstrap"
    basis: source-report
  - id: s3
    ref: "./nuitka-onefile-payload-recovery.md#内层仍然是-nuitka-native"
    basis: source-report
  - id: s4
    ref: "./nuitka-onefile-payload-recovery.md#不要做的"
    basis: source-report
modules:
  - name: parameters
    anchor: prerequisites
    sources: [s1, s2]
    basis: source-report
    limits: 识别串、RT_RCDATA 和 KAY 前缀都是来源对 Windows onefile 样本的描述。偏移 3 只在核过魔数之后才适用，不是下一个样本的默认值。
  - name: decision-flow
    anchor: steps
    sources: [s2, s3]
    basis: source-report
    limits: 只保留来源点名的检查顺序。scripts/recovery/ 下的脚本正文不在本文，本卡不补命令实现。
  - name: validation
    anchor: acceptance
    sources: [s1, s3, s4]
    basis: source-report
    limits: 完成门是作者写下的成功标准。本轮没有抽取样本，也没有核对 SHA-256。
relations:
  - type: derived_from
    target: "./nuitka-onefile-payload-recovery.md#适用与不适用"
tags: [nuitka, onefile, zstandard]
---

# Nuitka onefile 外层 payload 与内层 constants

这份流程只回答来源自己如何区分 Nuitka `--onefile` 和外层释放器，以及它把什么当成做完。它不还原 `.py`，也不覆盖微信公众号 HTTP 面；那两张卡的目标是 `wechat-official-account`。query `--target "Nuitka onefile"` 的 decision-flow、parameters、validation、interfaces 都是 0。

<a id="prerequisites"></a>
## 前提与输入

| 输入 | 来源要求 | 不足时 |
|---|---|---|
| 分发形态 | Windows GUI/CUI 的 Nuitka `--onefile`。quote: `NUITKA_ONEFILE_PARENT` | 不是这种分发走 F1 |
| 识别串 | strings 同时能解释 `NUITKA_ONEFILE_PARENT`、`onefile_%PID%_%TIME%`、`__nuitka_version__`。quote: `NUITKA_ONEFILE_PARENT` | 对不上就不要套本流程 |
| 外层资源 | `.rsrc` 里的 `RT_RCDATA` 高熵 blob。本样本是 `10/27/0`，约 34 MiB。quote: `RT_RCDATA 10/27/0` | 没有这块资源就没有外层 payload |
| 压缩前缀 | 本样本前缀是 `KAY`，从偏移 3 起按 Zstandard 解压。quote: `从偏移 3 起可按 Zstandard 解压` | 魔数不同走 F2 |

来源明确排除 PyInstaller `PYZ` / `MEI`、普通 CPython zipapp，以及没有 onefile bootstrap 的目录版 Nuitka。quote: `已经是目录版 Nuitka（无 onefile bootstrap）`。

<a id="steps"></a>
## 步骤与分支

下表只整理来源已经写出的顺序。脚本名属于原项目的 `scripts/recovery/`，换项目时复用的是步骤，不是把产物写到仓库外。

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | `pe_probe`：确认 PE、Nuitka 字符串和节区 | 是否符合前提里的分发形态 | 符合走 S2，否则 F1 |
| S2 | `extract_resources`：抽出 `RT_RCDATA` | 高熵资源 blob | 抽到走 S3，否则 F2 |
| S3 | `probe_payload`：扫 `KAY` / zstd / `MZ` / `PK` | 实际魔数 | 与本样本的 `KAY` 加偏移 3 的 zstd 一致才走 S4，否则 F2 |
| S4 | `decompress`：只按核过的编解码出 blob | 解压结果 | 解压失败走 F2，不要改假定成 zstd |
| S5 | `extract_payload_full`：落到项目的 `payload_extracted_full/` | 第二层 `*.exe` 以及 DLL/PYD | 内层出现后走 S6；写到仓库外走 F3 |
| S6 | 内层不再当 `.pyc`。用字符串和常量池，按协议 URL 做 context window，再看函数名或伪代码骨架 | constants 窗口里的业务 URL/字段 | 窗口能稳定读出字段则进入验收；读不出走 F4 |

来源对内层的原句是：大量导入 `python310.dll`，strings 能见到原模块名和 `__nuitka_version__`，但不能当普通 `.pyc` 用反编译器出源。quote: `用反编译器出源`。定向窗口的例子是 `profile_ext?action=getmsg` 一类字符串的 xref；字段表本身不在本流程里。

<a id="outputs"></a>
## 输出

交付两样东西：抽出的内层主程序，以及从 constants 窗口稳定读出的业务 URL 或字段。quote: `抽出内层主程序并核对 SHA-256`。来源对这个微信下载器样本还写了解压后 128 个运行时文件（85 DLL、41 PYD、1 PEM，加第二层主程序）。这些计数是该样本的形状，不是通用配额。原始 EXE、payload 和解压树只留在 owning workspace 的 `evidence-manifest.json`，不进 Git。

<a id="acceptance"></a>
## 验收

通过只表示两件事同时成立：内层主程序已抽出并核对了 SHA-256；constants 窗口能稳定读出业务 URL 或字段。quote: `能从 constants 窗口稳定读出业务 URL/字段`。

明确不算通过：还原出 `.py` 源码。来源把内层字节码标成 L4 triage-only。quote: `L4 triage-only 对内层字节码成立`。本轮没有样本，也没有哈希对照。

<a id="failure-exits"></a>
## 失败出口

F1：分发不是 Windows Nuitka `--onefile`，或者是 PyInstaller `PYZ` / `MEI`、zipapp、目录版 Nuitka。停止这条流水线，不和 pyinstxtractor 混用。quote: `已经是目录版 Nuitka（无 onefile bootstrap）`。另一句原话是不要混用同一条流水线。quote: `混用同一条流水线`。

F2：资源不是高熵 `RT_RCDATA`，或者前缀不是已核对的 `KAY`，或者不能从偏移 3 按 Zstandard 解开。先重核魔数。quote: `换样本先核魔数，不要假定永远是 zstd`。

F3：把解压目录提交 Git，或用固定盘符把 `extract_payload_full` 写到仓库外。停止交付，产物只留 owning workspace。

F4：把外层 EXE 修导入表、找 OEP 当成脱壳完成，或者对内层声称已经完整还原源码。quote: `把 onefile 外层当业务程序去修导入表、找 OEP 当脱壳完成`。这两件事都不是完成门。
