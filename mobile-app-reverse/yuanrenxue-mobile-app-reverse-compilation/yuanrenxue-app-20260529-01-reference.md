---
schema_version: 2
id: yuanrenxue-app-20260529-01-zdefend-reference
document_type: reference
original_date: '2026-05-29'
archived_date: '2026-10-02'
scope:
  targets: [ZDefend]
  client: iOS
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./yuanrenxue-app-20260529-01.md#ai-逆向实战flutter--swift-混合型-app-的-jailbreak-检测分析与绕过"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 规则名、系统调用和 threat 文案都是这篇来源对一个混合 App 样本的描述。地址和子函数号不外推到别的构建。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 三层分法和“不把全部检测函数改成良性返回”是来源的路线说明。本卡不把它写成可执行补丁步骤。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: getter 偏移、threat ID 和来源写下的指令只属于文中那个二进制。本轮没有改 Mach-O，也没有重打包。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: UI 文案和 access violation 都是作者自述。本轮没有 Frida，也没有 UI tree。
relations:
  - type: derived_from
    target: "./yuanrenxue-app-20260529-01.md#ai-逆向实战flutter--swift-混合型-app-的-jailbreak-检测分析与绕过"
tags: [zdefend, ios, jailbreak]
---

# ZDefend 越狱检测的消费层字段

这张卡检索一篇来源里，ZDefend 如何把 rule 收成 threat，以及宿主为什么看 `activeThreats` 和 `internalThreatID`，而不是直接看某一次 `lstat`。query `--target ZDefend` 的 risk-control、decision-flow、parameters、validation 都是 0。同目录 20200609 的报价 App 卡目标是 sign 参数，不覆盖这里。

来源没有独立的验收口径，也没有“偏移对不上就停止”的失败出口。作者写下的进入主界面是 source-report，所以只发 reference。第 89 行是另贴的登录提示词，0.5 已把账号和服务端交互排除，不进入模块。

<a id="risk-control"></a>
## 检测链与已确认调用

来源把阻断收成一条链，而不是主二进制里的明文 `isJailbroken`。quote: `ZDefend rule -> 系统检测函数 -> threat/status -> TargetApp 消费点 -> UIKit alert`。更细的一跳是 native rule 先变成 `device_status_base64`，再进 `ZDeviceStatus` / `ZDefendThreat`，然后才到 App 的 `activeThreats` 和 alert builder。quote: `ZDefend native rule / classifier  -> device_status_base64`。

未做结果层处理时，来源记录了两类 active threat：`DEVICE_ROOTED` 对应 rule `JB Dopamine-Roothide` 和 `ios_combined_classifier`，`internalThreatID` 39；`APP_TAMPERING` 仍可由 `ios_combined_classifier` 映射出来，ID 75。quote: `39 表示  DEVICE_ROOTED；  75 表示 APP_TAMPERING`。这些名字被写成运行时 status/policy 产物，不是主二进制里的普通明文字符串。

`JB Dopamine-Roothide` 的来源链路停在 `lstat` / `lstat64(path)`，再得到 `triggered=true` 和 `legacyThreatId=39`。quote: `lstat / lstat64(path)`。`ios_combined_classifier` 的来源特征是 `sysctlbyname(security.mac.*_enforce)`，以及 `open + fcntl(fd, 61)`。quote: `open + fcntl(fd, 61)`。事件 ID `0x0e` 被来源对到 `com.zimperium.fs.mounted_all`。来源没有把 `ptrace`、`fork`、`dladdr`、`csops` 列成已确认导入。

App 侧静态解密表里，39 的标题是越狱阻断文案。quote: `` ` Jailbroken Device Detected  ` |  越狱设备 ``。75 是 App Tampering。builder 地址 `0x100902864` 只属于这个样本。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 阻断链经过 rule、系统调用、status，再到 App 弹窗 | `ZDefend rule -> 系统检测函数 -> threat/status -> TargetApp 消费点 -> UIKit alert` | s1 yuanrenxue-app-20260529-01.md:58 | source-report | 下一行的 builder 仍是同一句，不是第二个机制 |
| C2 | Dopamine/Roothide 这条 rule 用 lstat/lstat64 | `lstat / lstat64(path)` | s1 yuanrenxue-app-20260529-01.md:272 | source-report | 路径清单是该样本的命中，不外推 |
| C3 | 综合分类器包括 sysctlbyname 和 fcntl 61 | `open + fcntl(fd, 61)` | s1 yuanrenxue-app-20260529-01.md:288 | source-report | 同一分类器可映射成两种 threat |

<a id="decision-flow"></a>
## 三层，以及不改全部检测函数

来源把机制写成检测、归一化、App 消费。检测层是 rule VM 调 `lstat/lstat64`、`sysctlbyname` 和 `fcntl(fd,61)`。归一化层收成 `ZDDRuleResult`、`device_status_base64`、`ZDeviceStatus`、`ZDefendThreat`。消费层读 `activeThreats`，在 ID 39 且未缓解时进 alert builder。quote: `1. **检测层**：ZDefend rule VM 调用系统 primitive`。

路线选择写在结果字段，而不是把每一次系统调用都改成良性返回。quote: `这次绕过没有删除底层检测函数`。来源给的理由是 rule VM 点多，全量替换会带出 `APP_TAMPERING / apptampering_hooked`，而宿主最终看的是 `activeThreats`、`allThreats`、`internalThreatID`、`severity`、`mitigated`。quote: `APP_TAMPERING / apptampering_hooked`。

因此来源把策略叫做结果消费层 sanitize：检测继续跑，宿主看到的 threat 变成良性或不可阻断。quote: `因此采用“结果消费层 sanitize”策略`。这是路线说明。来源没有写偏移变化时的停止条件，所以这里不是 procedure。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C4 | 检测、归一化、消费是三层 | `1. **检测层**：ZDefend rule VM 调用系统 primitive` | s1 yuanrenxue-app-20260529-01.md:510 | source-report | 该段是原理复述，不是新的测量 |
| C5 | 不把全部检测函数删掉，也不把每次系统调用改成良性返回 | `这次绕过没有删除底层检测函数` | s1 yuanrenxue-app-20260529-01.md:430 | source-report | 同一句后半写的是 lstat/sysctl/fcntl，副作用是作者自述 |

<a id="parameters"></a>
## 字段、偏移和来源写下的 getter 改动

`ZDeviceStatus` 的来源偏移：`allThreats` 在 `0x70`，`activeThreats` 在 `0x78`，`mitigatedThreats` 在 `0x80`，`activeNewThreats` 在 `0x88`。地址分别是 `0x10d90`、`0x10dd4`、`0x10e18`、`0x10e5c`。quote: `让 allThreats  指向通常为  空的  activeNewThreats`。未缓解的项进 `activeThreats`。

`ZDefendThreat` 的来源映射：`internalThreatID` 来自 `legacyThreatId`，`severity` 里 `CRITICAL` 映射成 3，`mitigated` 决定是否离开 active 列表，`ruleName` 来自顶层 `internalName`。quote: `39 表示  DEVICE_ROOTED；  75 表示 APP_TAMPERING`。

来源写下的结果层改动，只作为该样本的原句保留：`allThreats` 和 `activeThreats` 改读 `0x88`；`internalThreatID` 的目的是避开 39/75；`isMitigated` 和 `mitigated` 被写成返回 1；`severity` 和 `threatSeverity` 被写成返回 0。quote: `避免命中 39/75`。这些指令和偏移都不可挪到别的构建。本轮没有应用它们。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C6 | allThreats 被改去读通常为空的 activeNewThreats | `让 allThreats  指向通常为  空的  activeNewThreats` | s1 yuanrenxue-app-20260529-01.md:456 | source-report | 同一行的偏移只属于这个二进制 |
| C7 | ID 39 表示 DEVICE_ROOTED，75 表示 APP_TAMPERING | `39 表示  DEVICE_ROOTED；  75 表示 APP_TAMPERING` | s1 yuanrenxue-app-20260529-01.md:247 | source-report | 数值映射是这篇 status 的描述 |

<a id="validation"></a>
## 来源所称的闭环和反例

来源用来确认弹窗的做法，是拿真实 `ZDefendThreat`，把 `internalThreatID` 固定为 39、`severity` 为 3、`isMitigated` 为 0，再调用样本里的 `TargetAppProd +0x902864`。quote: `ZDefendThreat.internalThreatID = 39`。作者称随后的 UI tree 标题是 `Jailbroken Device Detected`。quote: `title   = Jailbroken Device Detected`。这是作者自述，不是本轮观察。

反例：自定义 fake ObjC class 即使实现了 `internalThreatID` selector，builder 仍会因为对象布局不兼容出错。quote: `access violation`。下一行写的是 `accessing 0x1c`。quote: `accessing 0x1c`。来源据此认为 builder 要的是真实 `ZDefendThreat` 或 Swift-ObjC 兼容布局，不是只认 selector。

来源还写，本轮没有在原始 imports 里确认 `ptrace`、`fork`、`dladdr`、`csops`。taxonomy 里有 `com.zimperium.proc.*` 名字，但正文不把它们当成已确认调用。

| claim_id | 结论 | 原文 | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C8 | 参数级验证把三个 getter 固定成 39、3、0 | `ZDefendThreat.internalThreatID = 39` | s1 yuanrenxue-app-20260529-01.md:399 | source-report | 同一行还有 severity 和 isMitigated，仍是作者的脚本参数 |
| C9 | 假类进入 builder 会在 0x1c 处访问失败 | `accessing 0x1c` | s1 yuanrenxue-app-20260529-01.md:420 | source-report | 只说明该 builder 要真实对象布局 |

## 验证与限制

没有 request-chain。第 89 行的登录提示词使用占位符，而且 0.5 写明账号体系和服务端交互不在本文展开。

未单列成模块的部分：工具清单、AI 协作过程、截图，以及最终调用链的重复总结。调用链没有新的字段。

需要重验的变化：ZDefend 或宿主二进制一换，`0x10d90`、`0x100902864` 和 ivar 偏移都作废。`activeNewThreats` 并非总是空列表；来源只写“通常为空”，没有给出非空时的出口。全量 hook 会不会打出 `apptampering_hooked`，也只是这篇样本的自述。
