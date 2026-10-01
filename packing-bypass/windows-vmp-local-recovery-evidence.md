---
schema_version: 2
id: packing-bypass-windows-vmp-local-recovery-evidence
document_type: archive
scope:
  targets:
  - unknown
  client: unknown
  version: unknown
  observed_at: unknown
sources:
- id: s1
  ref: null
  basis: source-report
  citation: null119 提供的 Windows 逆向方法资料，`vmp-unpack-playbook.md` 与 `vmp-devirt-playbook.md`；另核对文末上游项目说明。
  reason: 原归档明确记载出处，但未提供可定位的公开来源链接；本轮只保留来源自述。
source_completeness: unknown
tags:
- Windows
- VMProtect
- OEP
- IAT
- handler
- 局部语义
- 证据边界
original_date: 未知
archived_date: '2026-09-27'
---

# Windows VMProtect：局部语义恢复的证据边界

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: null119 提供的 Windows 逆向方法资料，`vmp-unpack-playbook.md` 与 `vmp-devirt-playbook.md`；另核对文末上游项目说明。
> 原始发布时间: 未知
> 归档日期: 2026-09-27
> 分类: packing-bypass
</details>
>
> 本篇是方法资料的静态提炼，不是某个 Windows 样本的成功去虚拟化案例。核心是分开识别保护、恢复可运行映像和恢复局部语义，避免把 OEP、dump 或 IAT 修复当成 VM 已经消失。

## 来源能支持什么

| 证据等级 | 本篇采用的内容 | 不能外推的内容 |
|---|---|---|
| 来源自述 | 保护分诊、handler 分割、VM 状态追踪和局部对拍流程 | 流程写得完整不表示某版 VMProtect 已被处理 |
| 静态核验 | 对照两份方法文，确认其明确区分 runtime 依赖、dump、IAT 与语义恢复；核对上游 README 的工具边界 | 没有通过这些文档证实当前机器工具可用 |
| 独立运行复现 | 本次为 0 | 不宣称任何目标去虚拟化成功 |

范围限定 Windows Native PE。Web JSVMP、CLR 方法虚拟化与其他平台保护需要各自的 VM 状态、ABI 和运行时证据，不能共用一份 handler 配方。

## 三个不同问题

| 当前问题 | 最小必要证据 | 常见误判 |
|---|---|---|
| 是否存在虚拟化 | VM entry、bytecode 读取、context 更新与 dispatch 的关联 | 看到节名或高熵就断言版本与保护模式 |
| dump 是否可运行 | 初始化链、重定位、TLS、导入、runtime/thunk 依赖与干净启动结果 | OEP 可达或 PE 能打开就算修复完成 |
| 局部语义是否恢复 | 输入边界、VM 状态、候选语义、原始目标对拍和未覆盖路径 | 伪代码可读或输出一次相同就宣称全函数等价 |

先分 `pack-only`、`mutation-only`、`virtualized`、`mixed`、`unknown`。非 VM 或证据不足时，不为了走完流程而强做 handler 恢复。

## 有界恢复应保留的状态

把目标收窄到函数、分支簇或可复用边界，固定样本身份与 RVA，再追踪实际存在的 vpc、vsp、key、虚拟寄存器或 context 映射。映射应携带有效区间；寄存器轮换、保存恢复和 key 演化不能当常量省略。

handler 分割依赖 bytecode 读取、状态写回与调度边界，不要求所有 VM 都有中央 dispatcher。输出导向切片仍须保留影响内存、副作用、flags、异常及外部调用的指令。CPU 特征、计时与随机指令不能仅因结果难解释就当垃圾删除。

恢复到 IR 后检查位宽、截断、符号扩展、移位、溢出和别名。对于 `cmp/test/jcc/cmov`，既要解释 flags 来源，也要明确分支目标和覆盖范围。VM exit 还可能是 native callout 后重入；停止条件应来自目标边界，而非第一个退出指令。

## 工具路线不是能力证明

- [NoVmp](https://github.com/can1357/NoVmp) 的 README 将范围限定为 x64 VMProtect 3.0–3.5 的实验性路线，要求输入已 unpacked；original image base、jump table 与 relocation 有限制。其重编译演示不应默认当成稳定产物生成器。
- [VMProtect-devirtualization](https://github.com/JonathanSalwan/VMProtect-devirtualization) 描述的是 VMProtect 3.x 的实验动态方法，面向纯函数与少量路径，不支持 user-dependent memory。循环展开和单条路径结果不能证明一般等价。
- [titan](https://github.com/archercreat/titan) 自述适用于 VMP <3.8 且输出仍不理想；适合参考 VM 状态、handler、CFG、IR 的分层，不宜外推所有版本与架构。

上述范围来自 2026-09-27 静态核验时的上游说明，不是未来兼容性承诺，也不是本次工具 smoke 结果。

## 收口与停止

只报告证据支持的等级：识别线索、可复现 trace、handler 映射、局部语义片段、已测路径一致或黑盒边界复用。黑盒方案应列输入、输出、副作用、异常、时序以及仍依赖的保护 runtime，不能换个名字就称为纯算。

验证记录绑定样本、范围、输入集合、trace 与候选版本；任一上游变化均须复审。文件 hash 能发现错配，不能证明日志真实或语义正确。没有可用采集器时，留下最小缺口即可，不必先穷尽所有历史工具才允许结束。
