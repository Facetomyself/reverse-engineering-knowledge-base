---
schema_version: 2
id: go-native-reverse-evidence-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-23'
scope:
  targets: [xtun, cftun, golang-native]
  client: native
  version: unknown
  observed_at: unknown
sources:
  - id: carrier-core
    ref: ./xtun-go-reverse-teaching-archive.md#source-core-00
    basis: source-report
  - id: apk-layer
    ref: ./xtun-go-reverse-supplement-archive.md#source-supplement-a1
    basis: source-report
  - id: elf-layer
    ref: ./xtun-go-reverse-supplement-archive.md#source-supplement-a2
    basis: source-report
  - id: address-layer
    ref: ./xtun-go-reverse-supplement-archive.md#source-supplement-a3
    basis: source-report
  - id: function-location
    ref: ./xtun-go-reverse-teaching-archive.md#source-core-05
    basis: source-report
  - id: go-hook
    ref: ./xtun-go-reverse-supplement-archive.md#source-supplement-a5
    basis: source-report
  - id: hook-report
    ref: ../protocols/xtun-cftun-analysis-source-archive.md#source-analysis-14
    basis: source-report
  - id: crypto-core
    ref: ./xtun-go-reverse-teaching-archive.md#source-core-06
    basis: source-report
  - id: crypto-config
    ref: ./xtun-go-reverse-teaching-archive.md#source-core-08
    basis: source-report
  - id: crypto-conflict-a
    ref: ../protocols/xtun-cftun-analysis-source-archive.md#source-analysis-07
    basis: source-report
  - id: crypto-conflict-b
    ref: ../protocols/xtun-cftun-analysis-source-archive.md#source-analysis-09
    basis: source-report
  - id: crypto-conflict-c
    ref: ../protocols/xtun-cftun-analysis-source-archive.md#source-analysis-10
    basis: source-report
  - id: validation-core
    ref: ./xtun-go-reverse-teaching-archive.md#source-core-14
    basis: source-report
  - id: upgrade-report
    ref: ../protocols/xtun-cftun-analysis-source-archive.md#source-analysis-13
    basis: source-report
  - id: history-correction
    ref: ./xtun-go-reverse-supplement-archive.md#source-supplement-a8
    basis: source-report
  - id: missing-artifacts
    ref: ../protocols/xtun-cftun-analysis-source-archive.md#source-analysis-19
    basis: source-report
  - id: go-abi-spec
    ref: https://github.com/golang/go/blob/go1.25.0/src/cmd/compile/abi-internal.md
    basis: source-report
  - id: ghidra-jdk-spec
    ref: https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.1.3_build/GhidraDocs/GettingStarted.md
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [carrier-core, apk-layer, elf-layer, address-layer, function-location, go-hook, history-correction]
    basis: source-report
    limits: 从脱敏且有缺口的教学来源提炼阅读与证据分类要点；原文缺公开 locator、目标二进制及运行日志，未验证具体载体分工、地址或 Hook。
  - name: parameters
    anchor: parameters
    sources: [crypto-core, crypto-config, crypto-conflict-a, crypto-conflict-b, crypto-conflict-c]
    basis: source-report
    limits: 来源对 KDF 输入、输出用途及 AAD 存在冲突，无完整向量；这里只列判读维度，不裁定算法、密钥或当前协议实现。
  - name: validation
    anchor: validation
    sources: [go-hook, hook-report, validation-core, upgrade-report, history-correction, missing-artifacts, go-abi-spec, ghidra-jdk-spec]
    basis: source-report
    limits: 来源成功标签、预期输出和历史修正不是本次运行事实；官方固定版本规范仅支撑自身 ABI/JDK 范围，不能支撑 xTun 或服务器验收。
relations:
  - type: derived_from
    target: ./xtun-go-reverse-teaching-archive.md#source-core-00
  - type: derived_from
    target: ./xtun-go-reverse-teaching-archive.md#source-core-06
  - type: derived_from
    target: ./xtun-go-reverse-teaching-archive.md#source-core-14
  - type: derived_from
    target: ./xtun-go-reverse-supplement-archive.md#source-supplement-a2
  - type: derived_from
    target: ./xtun-go-reverse-supplement-archive.md#source-supplement-a5
  - type: derived_from
    target: ./xtun-go-reverse-supplement-archive.md#source-supplement-a8
  - type: derived_from
    target: ../protocols/xtun-cftun-analysis-source-archive.md#source-analysis-07
  - type: derived_from
    target: ../protocols/xtun-cftun-analysis-source-archive.md#source-analysis-14
tags: [golang, native, PE, ELF, ABIInternal, RVA, load-bias, HKDF, AEAD, WebSocket, evidence-boundary, source-report]
---

# Go Native 逆向阅读与证据边界参考

这张卡帮助阅读混合 PE、ELF、Go 与 Flutter 的教学材料：先弄清结论属于哪个载体、地址体系和验证层，再判断材料实际支撑了什么。它不恢复协议、不提供可运行客户端，也不定义新的工具路由或执行流程。

来源是三篇合并 archive 中保留的 48 篇教学/项目材料。来源作者和原始公开链接缺失，原样本、工程、日志、配置和自述脚本未齐；三个 archive 均为 `partial`。本卡所有模块只采用 **source-report**，没有目标 `runtime-observation`、`local-parity` 或 `server-accepted` 结论。这里的 `native` 同时含 Windows 与 Android 线索，不把两种 ABI 或地址互套。

<a id="decision-flow"></a>
## 载体、定位与历史解释

| 判读问题 | 这批来源可供参考的内容 | 不能跳过的边界 |
|---|---|---|
| UI 和协议逻辑是否在同一文件？ | [核心前言](./xtun-go-reverse-teaching-archive.md#source-core-00) 与 [A1](./xtun-go-reverse-supplement-archive.md#source-supplement-a1) 把 Flutter/Dart UI、Android Go SO 和 Windows Go PE 分开讨论 | 这是来源对该项目的分工自述；未有二进制，不把库名、体积、编译语言或同源代码直接等同为所有平台逻辑完全相同 |
| 看到的是文件结构还是加载结构？ | [A2](./xtun-go-reverse-supplement-archive.md#source-supplement-a2) 同时出现 ELF Section 与 Program Header/Segment | 保留“用于分析/链接的分节”与“加载映射”区别；不能把某个 Section 的文件位置直接当运行时地址 |
| 字符串命中能否确认目标函数？ | [核心 05](./xtun-go-reverse-teaching-archive.md#source-core-05) 以字符串、引用者和调用链定位 | 字符串只给候选；需要知道命中在哪个文件/版本、哪个引用点、函数起点和调用上下文。来源地址未经本次样本核对，不是可直接使用的 Hook 偏移 |
| 材料前后说法冲突时采用哪一段？ | [A8](./xtun-go-reverse-supplement-archive.md#source-supplement-a8) 保留了失败阶段假设和后续修正 | 不把旧结论与新解释拼成同时成立的事实；分别记录阶段、原话、触发修正的证据是否实际提供。后置“攻破”标题本身不证明修正已独立成立 |

### 地址的最小区分

地址线索见 [A3](./xtun-go-reverse-supplement-archive.md#source-supplement-a3) 与 [A2 的编辑说明](./xtun-go-reverse-supplement-archive.md#source-supplement-a2)。本卡只提炼不混用的判读要求，不替缺失映射计算地址：

- PE 的 VA、RVA、文件偏移是不同坐标；它们分别需要对应 ImageBase、节映射与原始数据范围。把反编译器显示地址减去一个“看起来像基址”的数，不足以证明结果正确。
- ELF 的符号/虚拟地址、文件偏移和运行地址需要关联实际加载 Segment；`load bias`、模块映射起点和调用工具口中的“base”未必是同一个概念。不能把 Windows PE 的 VA/RVA 套到 Android SO。
- 证据至少写明目标文件/版本、架构、地址种类、来源工具、映射依据和适用范围。缺一项就把地址标为待核，不用来源文章里的数字充当当前进程事实。

以上不是新的操作门禁；实际取证仍按现有对应工具合同。已有 [Native 函数定位参考](../mobile-app-reverse/paopao-native-function-location.md) 处理通用符号/字符串/调用点线索，本卡不重复建立定位教程。

<a id="parameters"></a>
## 按层绑定密码参数，不替冲突来源选答案

核心 [06](./xtun-go-reverse-teaching-archive.md#source-core-06)、[08](./xtun-go-reverse-teaching-archive.md#source-core-08) 和源分析 [decryptAccessPoint](../protocols/xtun-cftun-analysis-source-archive.md#source-analysis-07)、[Ghidra 总览](../protocols/xtun-cftun-analysis-source-archive.md#source-analysis-09)、[IDA/Capstone 总览](../protocols/xtun-cftun-analysis-source-archive.md#source-analysis-10) 的 KDF 描述并不一致。不能只因某段出现标准算法名、解密成功输出或两工具“确认”就消除冲突。

| 每个加密/编码层需要绑定的内容 | 阅读时应区分的对象 | 当前缺口 |
|---|---|---|
| 输入的实际来源与字节表示 | 配置字段、参数、临时共享值；UTF-8 字符串、hex/base64 文本、已解码 bytes | 已公开脱敏值不能当测试输入；来源描述可能在同文不同段落互换字段 |
| 变换与输出用途 | hash、KDF、复制/拼接、编码；输出到底用作 AEAD key、salt、payload 字段还是别的层输入 | `SHA256(payloadSecret)`、`SHA256(accessPoint)`、`base64(payloadSecret)`、“直接复制无 KDF”并列存在，未调和 |
| AEAD 附加输入 | nonce、AAD、tag 长度/拼接、方向、序号、大小端与初始状态 | 配置响应 AAD 等描述存在差异；缺失完整原向量和逐层中间值 |
| 层间依赖与失败位置 | 配置传输、内部字段解密、握手帧、数据通道是独立层 | 某层 JSON 能解析不能自动证明其他层，也不能证明远端接受 |

保留“具体哪篇、哪段、哪种输入、输出被谁消费”的定位。缺二进制、数据流或完整向量时，结论停留在“来源称这样做”，不补写能消除冲突的算法，也不宣称已经复现。公开占位符不保持原长度、熵或密码关系，不能用来验证解密。

<a id="validation"></a>
## Hook 与通信结果各自证明到哪一层

### Go ABI 和 Hook 观察

[A5](./xtun-go-reverse-supplement-archive.md#source-supplement-a5) 的 Go 调用约定可作为阅读线索。Go `go1.25.0` 固定版本 [ABIInternal 文档](https://github.com/golang/go/blob/go1.25.0/src/cmd/compile/abi-internal.md) 明确指出该 ABI 不稳定，并列出 amd64 寄存器分配规则。这个公开规范只能约束相同版本/架构下的 ABI 讨论，不能替代目标函数原型、wrapper、receiver、内联、返回布局或 Android ARM64 的实际核对。

[源 Frida 报告](../protocols/xtun-cftun-analysis-source-archive.md#source-analysis-14) 一面写 Hook 已安装，一面写未捕获加密调用；另有“Frida 确认”措辞。因此要把下面三种证据分开：

- **安装成功**：只表示观察点被工具接受；没有调用事件时，不能证明偏移命中、参数位置或算法路径正确。
- **发生调用**：还需目标模块/版本、地址坐标、命中上下文、ABI 与参数/返回解释自洽；`onLeave` 的单个 `retval` 不能凭名称猜成完整 Go 多值返回。
- **捕获可解释的数据**：才有资格讨论某次调用的输入/输出；仍不能越级证明后续网络成功。格式正常、长度相符或代码里打印出“OK”均不等价于测试通过。

### 四层通信验收口径

来源定位：[核心 14](./xtun-go-reverse-teaching-archive.md#source-core-14)、[升级报告](../protocols/xtun-cftun-analysis-source-archive.md#source-analysis-13)、[A8 历史与修正](./xtun-go-reverse-supplement-archive.md#source-supplement-a8)。这里只澄清术语，不认证来源中的计数。

| 层次 | 该层结论应对应的材料 | 不能顺带推出 |
|---|---|---|
| WebSocket 升级 | 对应请求/响应和升级条件；不能只看某行命中了字符串 `101` | 自定义协议握手已经成功 |
| 自定义握手 | 对应协商/握手帧、期望响应及失败语义 | AEAD 数据通道已双向互通 |
| 数据通道 | 对应方向、状态、nonce/AAD/tag 与数据语义的可核对记录 | SOCKS5/HTTP 代理与目标业务端到端可用 |
| 代理端到端 | 代理入口、转发链、目标响应、出口与失败场景的同次记录 | 所有节点、版本、网络环境或其他协议均可用 |

5/6、若干 `101`、26/27 `DATA_OK` 分属不同来源阶段与范围，不能合并为同一成功率。部分源报告写 2025-01-30，多数项目文档写 2026-09-16，A8 写 2026-09-18；这批材料的观测时间仍为 unknown，不由整理者统一日期。

### 工具规范和目标事实分开

Ghidra 固定 tag [Ghidra_12.1.3_build / GettingStarted](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.1.3_build/GhidraDocs/GettingStarted.md) 规定 Java 21 64-bit JDK。它只纠正本批教学的 JDK 17+ 环境说法，不证明任何人本次启动了 Ghidra。Go ABI 官方文字同理，不证明示例 Hook 可运行。

## 验证与限制

| claim_id | 本卡保留的结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 载体分层、地址坐标和工具视角需要各自定位 | carrier-core、apk-layer、elf-layer、address-layer、function-location | source-report | 阅读这批 Windows/Android Go 材料 | 未获目标样本与映射，不输出可用偏移 |
| C2 | Go ABI/函数解释和 Hook 安装、命中、返回值不是同一证据 | go-hook、hook-report、go-abi-spec | source-report | 同版本/架构范围内的证据判读 | 目标原型、wrapper、内联与返回布局未核对 |
| C3 | KDF 输入/输出/用途和 AAD 必须逐层分开，冲突不能用成功标签覆盖 | crypto-core、crypto-config、crypto-conflict-a/b/c | source-report | 来源加密链的歧义辨认 | 缺样本、原向量和中间值，不裁定正确算法 |
| C4 | 升级、握手、数据与代理端到端必须分别表述 | validation-core、upgrade-report、history-correction | source-report | 来源结果范围与失败层次 | 未拿到同次原始证据；计数仅来源自述 |
| C5 | 历史假设和后续修正应分阶段保留 | history-correction | source-report | 本批 A8 叙述的前后差异 | 后置成功叙述未由本次独立验证 |
| C6 | 固定版本官方文档只支持 JDK/ABI 本身的有限规范 | ghidra-jdk-spec、go-abi-spec | source-report | 指定 tag 的工具/编译器文档 | 不证明安装、目标算法、Hook 或服务端接受 |

原 [文件索引](../protocols/xtun-cftun-analysis-source-archive.md#source-analysis-19) 只是未随包附件的存在自述，不是二进制/日志证据。来源 locator、日期和工件缺口继续向本卡传递；本卡不是 procedure，不新增 dispatcher、协议客户端或防护绕过，也不改变本仓现行取证工具合同。
