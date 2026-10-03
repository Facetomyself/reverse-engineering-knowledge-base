---
schema_version: 2
id: windows-vmprotect-local-semantic-boundary
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [VMProtect]
  client: windows
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./windows-vmp-local-recovery-evidence.md#windows-vmprotect局部语义恢复的证据边界"
    basis: source-report
modules:
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 证据等级和三条误判来自方法资料的静态提炼。来源写明独立运行复现为 0。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 只保留保护分型和停止条件。没有可执行的恢复步骤，也没有通过样本。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: VM 状态字段和三份上游说明的版本范围都是来源引述。不是工具 smoke，也不是兼容性承诺。
relations:
  - type: derived_from
    target: "./windows-vmp-local-recovery-evidence.md#windows-vmprotect局部语义恢复的证据边界"
tags: [VMProtect, evidence-boundary]
---

# Windows VMProtect：识别、dump 与局部语义不能互相代替

这张卡只回答：来源允许把哪些观察当成证据，以及三份上游说明各自停在哪一版。它不是某个 Windows 样本的去虚拟化结果。范围是来源写的 Windows Native PE。Web JSVMP 和 CLR 方法虚拟化不共用这份 handler 边界。

来源是 [Windows VMProtect：局部语义恢复的证据边界](./windows-vmp-local-recovery-evidence.md#windows-vmprotect局部语义恢复的证据边界)。

<a id="validation"></a>
## 三条问题各自要的证据

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 开篇写明不是某个 Windows 样本的成功去虚拟化案例，OEP、dump 或 IAT 修复不能当成 VM 已经消失 | s1 开篇句 | source-report | 这篇方法提炼 | 未对样本复现 |
| C2 | 静态核验只核对了方法文和上游 README，`没有通过这些文档证实当前机器工具可用` | s1 证据等级表 | source-report | 2026-09-27 那次核对 | 不是工具可用证明 |
| C3 | 独立运行复现被写成 `本次为 0` | s1 同一表 | source-report | 本篇 | 不能外推任何目标成功 |
| C4 | 虚拟化的最小证据是 VM entry、bytecode 读取、context 更新与 dispatch 的关联；`看到节名或高熵就断言版本与保护模式` 被标成误判 | s1 三问题表 | source-report | Windows Native PE | 没有具体样本的这些关联 |
| C5 | dump 可运行要看初始化链、重定位、TLS、导入、runtime/thunk 和干净启动；`OEP 可达或 PE 能打开就算修复完成` 被标成误判 | s1 同一表 | source-report | 同上 | 没有启动结果 |
| C6 | 局部语义要有输入边界、VM 状态、候选语义、对拍和未覆盖路径；`伪代码可读或输出一次相同就宣称全函数等价` 被标成误判 | s1 同一表 | source-report | 函数或分支簇 | 没有对拍记录 |
| C7 | 文件 hash 只解决错配，不能证明日志或语义 | s1 `文件 hash 能发现错配，不能证明日志真实或语义正确。` | source-report | 验证记录 | hash 只解决错配 |

<a id="decision-flow"></a>
## 先分型，不够就不做 handler

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 先分 `pack-only`、`mutation-only`、`virtualized`、`mixed`、`unknown`；证据不足就不做 handler | s1 `非 VM 或证据不足时，不为了走完流程而强做 handler 恢复。` | source-report | 进入恢复之前 | 没有判定这些类型的样本规则 |
| C9 | VM exit 可能是 native callout 后重入，不能把第一个退出当停止 | s1 `停止条件应来自目标边界，而非第一个退出指令。` | source-report | 有 VM exit 的路径 | 没有具体 callout |
| C10 | 没有可用采集器时可以收口 | s1 `没有可用采集器时，留下最小缺口即可` | source-report | 收口 | 没有列出最小缺口模板 |

可报告的等级只到：识别线索、可复现 trace、handler 映射、局部语义片段、已测路径一致或黑盒边界复用。黑盒仍须列出输入、输出、副作用、异常、时序和仍依赖的保护 runtime。

<a id="parameters"></a>
## 要留下的状态和工具版本边界

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C11 | 追踪实际存在的 vpc、vsp、key、虚拟寄存器或 context 映射，映射带有效区间；轮换、保存恢复和 key 演化不能当常量省掉 | s1 状态段 | source-report | 收窄后的函数、分支簇或边界 | 来源没有给出字段布局 |
| C12 | handler 分割看读取、写回和调度，不要求每个 VM 都有中央 dispatcher | s1 `handler 分割依赖 bytecode 读取、状态写回与调度边界，不要求所有 VM 都有中央 dispatcher。` | source-report | 有这些边界的 VM | 不是通用 opcode 表 |
| C13 | NoVmp 的 README 被限定在 x64 的 3.0–3.5，并且要求已经 unpacked | s1 `x64 VMProtect 3.0–3.5 的实验性路线，要求输入已 unpacked` | source-report | 该上游说明 | 重编译演示不是稳定产物 |
| C14 | VMProtect-devirtualization 只面向纯函数和少量路径 | s1 `面向纯函数与少量路径，不支持 user-dependent memory` | source-report | 该上游说明 | 单条路径不能证明一般等价 |
| C15 | titan 自述停在 3.8 以前，并且承认输出不理想 | s1 `适用于 VMP <3.8 且输出仍不理想` | source-report | 该上游说明 | 不宜外推所有版本与架构 |

CPU 特征、计时和随机指令不能只因难解释就删掉。IR 要检查位宽、截断、符号扩展、移位、溢出和别名。这些范围来自 2026-09-27 的上游说明，`不是未来兼容性承诺，也不是本次工具 smoke 结果`。

## 验证与限制

来源把前提、误判表、报告等级和停止句写在不同节里，但没有一套带通过样本的动作顺序。独立运行复现是 0。Web JSVMP 的宿主原语笔记 target 不是 VMProtect，不能拿来补这张卡的 handler。
