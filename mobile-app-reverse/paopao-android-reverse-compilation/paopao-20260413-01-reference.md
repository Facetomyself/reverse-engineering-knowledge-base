---
schema_version: 2
id: paopao-20260413-unidbg-backend-reference
document_type: reference
original_date: '2026-04-13'
archived_date: '2026-07-13'
scope:
  targets: [unidbg-backend]
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260413-01.md#unidbg学习笔记三五个后端引擎的性能与取舍"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留来源对接口、自动优先级和各 Backend 能力边界的描述。耗时表是作者自述，本轮未重跑。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 推荐表和四步切换来自来源正文。决策树图没有落到文字，不能当成闭合流程。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 切换后要重对输出，是来源建议。没有本轮对照记录，也不把作者的毫秒数当成验收阈值。
relations:
  - type: derived_from
    target: "./paopao-20260413-01.md#unidbg学习笔记三五个后端引擎的性能与取舍"
tags: [unidbg, backend, source-report]
---

# Unidbg Backend 选型边界

这张卡只回答：来源如何按用途在五个 Backend 里选，以及哪些分析能力只留在 Unicorn 系列。它不把缺图的矩阵或决策树补全，也不把作者的耗时表当成可复现基准。

<a id="parameters"></a>
## 五个执行后端

来源把 Backend 写成真正执行 ARM 指令的一层，接口是 `com.github.unidbg.arm.backend.Backend`。不指定时，自动优先级写成 Dynarmic、Hypervisor、KVM、Unicorn2、Unicorn。

Unicorn 被写成 QEMU TCG 解释执行，能在翻译时插入指令级回调，但不支持多线程。Unicorn2 被写成保留这些分析能力，并且是来源所说唯一同时支持指令级 Trace、内存断点和多线程的 Backend。Dynarmic 被写成跨基本块的 JIT，来源明确写它不支持指令级 Hook、内存监控和 Trace。Hypervisor 只写了 macOS 加 Apple Silicon、仅 ARM64。KVM 写的是 ARM Linux 上的 `/dev/kvm`，并写它支持 ARM32。

作者把测试机写成 MacBook Pro（Apple M2 Pro）、OpenJDK 17、未点名 commit 的主分支，样本是未点名电商 App 的 ARM64 签名 SO。热调用一行把 Unicorn、Unicorn2、Dynarmic、Hypervisor 写成约 120ms、100ms、3ms、1.5ms。KVM 不在这张表里。这些数字保持作者自述。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C1 | 接口名 | com.github.unidbg.arm.backend.Backend | s1 :45 | source-report | 未对源码 |
| C2 | 自动优先级 | Dynarmic → Hypervisor → KVM → Unicorn2 → Unicorn | s1 :66 | source-report | 未核版本 |
| C3 | Unicorn 无多线程 | 不支持多线程 — Unicorn 的 TCG 翻译器不是线程安全的 | s1 :107 | source-report | 未复现死锁 |
| C4 | Unicorn2 的分析定位 | Unicorn2 是唯一同时支持这些分析能力 | s1 :132 | source-report | “唯一”是作者断言 |
| C5 | Dynarmic 无指令 Hook | 不支持指令级 Hook | s1 :173 | source-report | 未在 JIT 上试 Hook |
| C6 | Hypervisor 平台 | 仅支持 macOS + Apple Silicon | s1 :201 | source-report | 未在 Intel Mac 上试 |
| C7 | KVM 需要 ARM Linux | 需要 ARM 架构的 Linux 服务器 | s1 :218 | source-report | 未在 Graviton 上试 |
| C8 | ARM32 一行对照 | ARM32 支持 | s1 :231 | source-report | 同行写 Hypervisor 不支持、KVM 支持 |
| C9 | Hook 示例的适用范围 | 仅在 Unicorn/Unicorn2 上可用 | s1 :339 | source-report | 示例不是实测日志 |

<a id="decision-flow"></a>
## 按用途选择，不是选最快

来源的正文推荐是：日常分析用 Unicorn2；不需要 Trace 的快速验证用 Dynarmic；Apple Silicon 开发用 Hypervisor；部署时 x86 用 Dynarmic、ARM 用 KVM。ARM32 要排除 Hypervisor。

它还写了一条工作顺序：调试和补环境留在 Unicorn2，验证时切到 Dynarmic 看结果是否一致，生产再用 Dynarmic 或 KVM。标题下的“Backend 选择决策树”和“五个 Backend 能力矩阵”在正文里只有图题，没有树或表，所以这里不补画。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C10 | 日常分析推荐 | 分析能力完整，多线程支持，性能够用 | s1 :440 | source-report | 同一行对应 Unicorn2 |
| C11 | ARM32 排除 Hypervisor | ARM32（armeabi-v7a） | s1 :431 | source-report | 生产侧来源改指 Dynarmic 或 KVM |
| C12 | 验证步要换 Backend | 确认结果一致 | s1 :450 | source-report | 没有给出一致的判定样本 |

<a id="validation"></a>
## 切换后的核对

来源写 Trace 或 Code Hook 不能无条件留在 Dynarmic、Hypervisor、KVM 上，并用 `instanceof Unicorn2Backend` 或捕获 `UnsupportedOperationException` 做降级。它同时写不同 Backend 在浮点、未对齐访问和特殊指令上可能有差异，切换后要重新核对输出。Unicorn 上 `JNI_OnLoad` 里建线程会失败或死锁；Unicorn2 是协作式伪多线程；另外三个被写成多线程更好。这些都是来源的风险说明，不是本轮运行记录。

作者把 Dynarmic 对 Unicorn 的热调用写成约 40 倍、Hypervisor 约 80 倍。样本未点名，KVM 被注明不在本次测试中。不能把这张表当成选型验收。

| claim_id | 结论 | quote | 来源与定位 | basis | 限制 |
|---|---|---|---|---|---|
| C13 | 热调用倍数是作者算法 | Dynarmic 比 Unicorn 快约 40 倍 | s1 :277 | source-report | 样本与 commit 未给出 |
| C14 | Trace 范围建议 | 一次 Trace 可能产生数百万行输出 | s1 :393 | source-report | 未保存 Trace |
| C15 | 切换后重对结果 | 重新验证输出结果是否一致 | s1 :479 | source-report | 没有差异样本 |
| C16 | Unicorn 的线程失败 | JNI_OnLoad 中的线程创建会失败或死锁 | s1 :483 | source-report | 未复现 |

## 验证与限制

完整能力矩阵和决策树图没有进入正文。耗时依赖作者未公开的 SO 和未固定的主分支。本卡不覆盖某一版 Unidbg 的工厂类是否仍叫这些名字。
