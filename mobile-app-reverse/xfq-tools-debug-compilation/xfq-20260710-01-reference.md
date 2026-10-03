---
schema_version: 2
id: frida-gadget-listen-config-reference
document_type: reference
original_date: '2026-07-10'
archived_date: '2026-10-02'
scope:
  targets:
    - frida-gadget
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260710-01.md#一啥是-frida-gadget"
    basis: source-report
  - id: s2
    ref: "./xfq-20260710-01.md#三gadget-配置解析"
    basis: source-report
  - id: s3
    ref: "./xfq-20260710-01.md#41-spawn-时机启动早期就卡住"
    basis: source-report
  - id: s4
    ref: "./xfq-20260710-01.md#42-attach-时机app-已经跑起来以后再连"
    basis: source-report
  - id: s5
    ref: "./xfq-20260710-01.md#五xfinject-注入-libgadgetso然后-frida-连接注入-js"
    basis: source-report
  - id: s6
    ref: "./xfq-20260710-01.md#44-常见连接问题"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留来源对 frida-server 与 Gadget 形态的对照。注入方案表被导出拆碎，残句不升格为检测结论。未在设备上对比检测结果。
  - name: parameters
    anchor: parameters
    sources: [s2, s5]
    basis: source-report
    limits: 参数表按被拆开的相邻行整理，不重组为可落盘配置。未核对当前 Frida 版本文档，也未推送配置到设备。
  - name: interfaces
    anchor: interfaces
    sources: [s2, s5]
    basis: source-report
    limits: 来源有多处把 adb forward 与 frida 粘成一行。本卡只引用分列步骤里的 frida -H 句子和 xfinjectd 参数形状。未执行注入。
  - name: decision-flow
    anchor: decision-flow
    sources: [s3, s4, s5, s6]
    basis: source-report
    limits: wait、resume 和连接排查是来源的使用建议。没有本地连接记录，缺独立验收，因此不是流程卡。
relations:
  - type: derived_from
    target: "./xfq-20260710-01.md#三gadget-配置解析"
tags:
  - frida-gadget
  - xfinject
  - source-report
---

# Frida Gadget 的 listen 配置与连接时机

这张卡只回答：来源如何区分 frida-server 与 Gadget，listen 配置里哪些字段决定端口和暂停，以及用 xfinjectd 注入时配置文件名必须怎样对应。不提供可执行的注入脚本，也不覆盖 ROM 里持久 jnilog 的开关和 service。

来源是知识星球讲义的 PDF 导出，表格和命令被拆行或粘连。下文只采用完整句或相邻残行能直接读出的字段。设备序列号不进入本卡。作者写的「常用」和「正常」都停留在 source-report。

<a id="risk-control"></a>
## 检测面对照

来源把 frida-server 写成外部 attach，并把注入特征检测当作改用 Gadget 的原因。Gadget 被写成编进 so、嵌在目标进程里的 Frida runtime，主机改为连接进程内部的 endpoint。spawn 仍被写成 attach，只是用来卡住启动时机。

> 众所周知,frida-server 因为注入特征的原因,所以存在一定检测。这时候可以试试 frida-gadget 。

第二节列举了重打包、运行后植入、框架、eBPF、魔改 ROM、zygote trap 和依赖劫持，但表格被拆碎，作者也写明列举不全面。本卡不从残句推出某种注入「检测不到」。

<a id="parameters"></a>
## 参数机制

Android 上的命名对应是 `libgadget.so` 与 `libgadget.config.so`。来源给出的 listen 示例含义是：监听 14725，端口冲突即失败，加载后先暂停，脚本上来之后再继续。官方文档位置写的是 `https://frida.re/docs/gadget/`。

参数表把 `interaction.type` 分成四行：`listen`（进程内开端口，主机用 `frida -H`）、`connect`（Gadget 连 portal）、`script`（自动加载单个 JS）、`script-directory`（扫描目录）。地址示例是 `0.0.0.0 / 127.0.0.1`，并写 forward 常用 `0.0.0.0`，端口示例 14725。`on_port_conflict` 的两个值在同一粘连行里：`fail` 便于排查，`pick-next` 会让实际端口不清楚。

`on_load` 的 `wait` 被写成暂停到 Frida 连接之后，并推荐给早期 hook；`resume` 被写成加载后直接继续。`teardown` 分 `minimal`（Android 默认）和 `full`（主动 unload 时才考虑）。`runtime` 分 `default`、`qjs`、`v8`。`code_signing` 的 `optional` 被写成 Android 默认，`required` 主要给 iOS/macOS。

`inject_frida_gadget.py` 未指定 `--config` 时，按显式路径、so 同名 config、同目录 `libgadget.config.so` 的顺序查找，都没有就生成 listen + wait。推到设备后的名字固定为 `/data/local/tmp/libgadget.config.so`。指定 `--config` 后不再用 `--port`、`--address`、`--on-load` 生成配置。`--on-load` 默认 `wait`，`--port` 默认 14725。`--eternalize` 被写成传给 frida CLI，使脚本在 CLI 退出后仍留在进程。`--vma-hide` 取值 `auto / always / never`，默认 `auto`。`--print-only` 只打印，不执行。

xfinjectd 的 `-lib` 被要求写成 `/data/local/tmp/libgadget.so:libgadget.so`。冒号后的 `libgadget.so` 不能省，因为 Gadget 按自身落地名找 `libgadget.config.so`；落地名若变成临时 so，配置会找不到。

<a id="interfaces"></a>
## 接口

分列步骤里的主机连接句是：

> 5. 主机执行 frida -H 127.0.0.1:14725 -n Gadget -l hook.js。

来源另有多行把 `adb -s <serial> forward tcp:14725 tcp:14725` 和这条 frida 命令粘在一起。那些粘连行不能当成一条可复制命令。forward 本身只在步骤里写成「adb forward 转发端口」。

快速验证不必先做 Zygisk。来源指向 `https://github.com/LunFengChen/xfinject/`，并写方案是 zygote trap、fork 自 gozinject。`inject_frida_gadget.py` 只做三件事：准备 `libgadget.config.so`，用 xfinjectd 注入 `libgadget.so`，可选再执行上面的 `frida -H`。脚本内部命令形状是 `xfinjectd -pkg <package>`，把 config 和 lib 从 `/data/local/tmp/` 带入，并带 `-vma-hide auto`。

<a id="decision-flow"></a>
## 时机选择

抢 `dlopen`、`JNI_OnLoad`、classloader 初始化或早期 native 注册时，来源选择 listen + wait：注入 so，配置暂停，App 启动后先听端口，forward，主机加载 hook，hook 先挂上，再放行。这个模式下卡开屏被写成正常现象，价值是脚本先跑、App 后跑。

不关心早期时机时用 resume。来源明确的代价是早期 `dlopen`、`JNI_OnLoad`、classloader 初始化，以及只在启动阶段调用一次的函数，都可能已经错过。建议句是：要抢早期用 wait，普通 hook 用 resume，不确定时先 wait。

`Java.use()` 找不到类时，来源不把它当成 Gadget 没生效，而是类未加载或在别的 ClassLoader；下一步是 hook `android_dlopen_ext`，再 `Java.enumerateClassLoaders()`。

连接失败时来源只给了六个检查：进程里是否在听端口、forward 是否到了当前设备、Gadget 与主机 Frida tools 版本是否匹配、旧进程是否占端口（滑掉后台不够，要强行停止）、wait 是否已经被一次连接唤醒、配置名是否与 so 对应。脚本路径上，14725 若被当前包占用会先 `am force-stop <package>`；仍被别的进程占用则脚本退出，改 `--port` 或停掉旧 App。wait 时不要等 xfinjectd 退出，因为它可能正等 Gadget 放行。版本不对时，来源写的现象是连上后断开。

## 验证与限制

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | frida-server 因注入特征会被检测；Gadget 是嵌进目标进程的 so，主机直接连它。spawn 仍是 attach。 | s1，第 37、43、45-47 行 | source-report | 这篇讲义对三种形态的定义 | 未做检测对照。注入方案表残缺，不支持「某种注入无特征」。 |
| C2 | listen 示例是端口 14725、冲突即失败、on_load wait；so 与配置必须同基名。 | s2，第 117、121-122、150-151 行 | source-report | 来源给出的 Android listen 示例 | 示例 JSON 被导出拆开，本卡不重组文件。 |
| C3 | interaction.type 四值为 listen、connect、script、script-directory；on_load 分 wait 与 resume。 | s2，第 163-182、205-215 行 | source-report | 来源参数表 | 含义分布在相邻残行，未对照官网字段表。 |
| C4 | 早期用 listen + wait，普通 hook 用 resume；不确定时先 wait。卡开屏在 wait 下被写成正常。 | s3、s4，第 313-319、381-383 行 | source-report | 来源自己的使用偏好 | 没有本次连接或 hook 命中的记录。 |
| C5 | xfinjectd 的 `-lib` 必须保留 `:libgadget.so`，否则按落地名会找不到 config。 | s5，第 603、606、609 行 | source-report | 来源描述的 xfinjectd 注入 Gadget | 未运行 xfinjectd。不覆盖 jnilog 的 ROM 持久开关。 |
| C6 | 端口仍被占时脚本退出；wait 时不能同步等待 xfinjectd 退出。 | s5，第 663–663 行 | source-report | `inject_frida_gadget.py` 的来源注意点 | 未复现端口冲突或版本不匹配。 |

ROM 持久 jnilog 仍以 `../../native-analysis/xfinject-jnilog-rom-procedure.md` 为准，那张卡的目标不是 frida-gadget。Java/Native hook 技巧选择也不是本卡的配置合同。
