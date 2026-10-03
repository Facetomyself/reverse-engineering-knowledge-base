---
schema_version: 2
id: grok-paopao-20260708-dex-unpack-reference
document_type: reference
original_date: "2026-07-08"
archived_date: "2026-10-02"
scope:
  targets: [dex-unpack]
  client: android
  version: "frida-16.x"
  observed_at: "2026-07-08"
sources:
  - id: s1
    ref: "./paopao-20260708-01.md#十综合决策表"
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 代际到工具的对应是来源的选择表。未对任何加固包执行。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录来源引用的 DEX 头常量和它声称的 Frida 17 更名。不收录内存扫描或磁头修复脚本。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: jadx 能打开业务类、重叠段和可疑 native 计数都是来源的判断句。不抄测试机序列号，也不把体积数字当成本次测量。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留来源的加固库文件名和 Android 14 对可写 DEX 的限制句。单应用检测对抗叙事不进入本卡。
relations:
  - type: derived_from
    target: "./paopao-20260708-01.md#十综合决策表"
tags: [dex-unpack, android, frida]
---

# DEX 加固代际、头字段和脱壳后怎么判断没取到正文

这张卡只回答一个检索问题：来源如何按壳的代际选择内存扫描、ART 反查或方法回填，以及它用哪些 DEX 头字段和打开结果判断产物。范围是这篇归档里可脱离单个应用复用的句子。第八章的检测对抗、槽位表和补丁工时不进入卡片。作者对两个应用的体积和类数量保持为来源陈述。

<a id="decision-flow"></a>
## 代际对应的取法

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 一代整体加密，来源写成内存里已有完整明文 DEX，按 magic 可取。quote: 内存里就有完整明文 DEX，搜 magic 就能取 | s1 ./paopao-20260708-01.md:65 | source-report | 来源定义的一代壳 | 未扫描进程 |
| C2 | 二代抽取后，来源写成方法体被 return-void 或单条 goto 占位，要等首次调用前回填。quote: 方法体被 ` return-void ` 或单条 ` goto ` 占位 | s1 ./paopao-20260708-01.md:69 | source-report | 来源定义的二代壳 | 未看到占位字节码 |
| C3 | 三代 VMP，来源写成 dump 出的方法体只剩跳向自定义解释器。quote: 方法体里也只看到对壳自定义解释器的 | s1 ./paopao-20260708-01.md:73 | source-report | 来源定义的三代壳 | 未逆向解释器 |
| C4 | 决策表把一代整体加密的首选写成 frida-dexdump，备选 dexCache 枚举。quote: 一代壳 / 整体加密 | s1 ./paopao-20260708-01.md:1490 | source-report | 来源决策表 | 工具版本以来源表为准 |
| C5 | 方法体为空时，来源首选 FART 的 AOSP 形态，并写 Frida 形态受 LoadMethod 时机限制。quote: 二代壳 / 方法体空 | s1 ./paopao-20260708-01.md:1494 | source-report | 来源决策表 | 未刷 ROM，未跑 Frida 版 |
| C6 | 来源的实战顺序是先跑 frida-dexdump，业务类找不到再换 dexCache 枚举。quote: 如果 jadx 打开后类一堆但你想要的业务类找不到 | s1 ./paopao-20260708-01.md:492 | source-report | 假 DEX 或误匹配 | 未对照两份 dump |
| C7 | FART 的主动触发，来源写不必真的调用方法，只要 ART 走到 LoadMethod。quote: 只需要让 ART 走到 | s1 ./paopao-20260708-01.md:518 | source-report | 来源对二代回填点的描述 | 未挂钩 LoadMethod |

<a id="parameters"></a>
## 来源使用的头字段和 API 更名

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 来源的 magic 扫描图案是 64 65 78 0a 30 加两个通配字节再加 00。quote: 64 65 78 0a 30 ?? ?? 00 | s1 ./paopao-20260708-01.md:182 | source-report | 来源对 frida-dexdump search.ts 的摘录 | 未跑扫描 |
| C9 | fast 校验被来源解释成 string_ids 紧贴 header 尾部。quote: string_ids 紧贴 header 尾部 | s1 ./paopao-20260708-01.md:209 | source-report | 来源注释中的 0x3C 比较 | 未读 DEX 头 |
| C10 | map 项类型 0x1000 被来源写成 DEX 自身。quote: 0x1000 = DEX 自身 | s1 ./paopao-20260708-01.md:224 | source-report | verify_by_maps 注释 | 未走 deep 校验 |
| C11 | magic 被抹掉时，来源改走 deep_search 反向搜索。quote: 如果壳把 DEX magic 也抹掉 | s1 ./paopao-20260708-01.md:247 | source-report | frida-dexdump 的 -d 描述 | 未构造损坏 magic |
| C12 | 磁头修复来源写明不校验 checksum 和 signature，因为 jadx 默认不校验这两项。quote: 不校验 checksum 和 signature | s1 ./paopao-20260708-01.md:338 | source-report | 来源对 fix_header 的说明 | 未打开 jadx |
| C13 | DefineClass 的符号，来源写成不同 Android 版本签名细节不同，所以用特征词匹配。quote: 不同 Android 版本签名细节不同 | s1 ./paopao-20260708-01.md:424 | source-report | 来源称 Android 8 到 11 | 12 及以后来源称未实测 |
| C14 | ArtMethod 在 Android 10 及以后被来源写成 dex_code_item_offset_ 并入 data_ 联合体，正 8 偏移不再稳定。quote: Android 10+ ART 重构 ArtMethod | s1 ./paopao-20260708-01.md:595 | source-report | 来源对 Android 6-9 布局的对照 | 未按 API level 核对头文件 |
| C15 | Frida 17 表把旧的按指针读 32 位改成指针方法 ptr.readU32()。quote: ptr.readU32() | s1 ./paopao-20260708-01.md:1436 | source-report | 来源的迁移表一行 | 未在 17 上运行旧脚本 |

<a id="validation"></a>
## 打开结果和重复段

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C16 | 来源把 jadx 能反编译并显示业务类当成脱壳成功。quote: 如果 jadx 能成功反编译并显示业务类 | s1 ./paopao-20260708-01.md:777 | source-report | 基本验证句 | 未打开样本 |
| C17 | 文件大小等于头里的 file_size，来源写这只说明按头读了那么多字节，不代表是独立业务 DEX。quote: 不代表这些字节是独立的业务 DEX | s1 ./paopao-20260708-01.md:883 | source-report | 来源对一次裸 DEX 扫描的复盘 | 体积和哈希不抄入本卡 |
| C18 | 业务包里可疑 native 方法超过 10 个时，来源建议改用 FART。quote: 建议上 FART | s1 ./paopao-20260708-01.md:815 | source-report | 来源脚本里的阈值 | 未枚举类 |

<a id="risk-control"></a>
## 库文件名和可写 DEX 限制

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C19 | 来源把一对库文件名标成 360 加固，并写新版本改名。quote: 360 加固（新版本改名为 jgdtc） | s1 ./paopao-20260708-01.md:92 | source-report | 来源称 2022-2024 主流版本 | 未解包核对 |
| C20 | targetSdk 34 下可写 DEX 被来源写成会抛出 Writable dex file is not allowed。quote: Writable dex file is not allowed | s1 ./paopao-20260708-01.md:1459 | source-report | 来源对 Android 14 的转述 | 未触发该异常 |

## 验证与限制

第 6.2 节只有决策树图题，没有可引用的分支正文，所以不能把本篇收成流程。第七章含测试机序列号，证据和卡片都不抄。第八章是一个已命名应用上的多轮检测对抗，含间接指针表和补丁估时，不构成可脱离该应用复用的模块。目录查询在目录仍可加载时，dex-unpack 的 decision-flow、frida-dexdump 的三个模块以及 FART 的 parameters 和 decision-flow 都没有命中；随后同目录被另一篇无关稿件的锚点错误挡住，parameters、validation 和 risk-control 的补查没有返回命中列表。
