---
schema_version: 2
id: paopao-20260409-unidbg-backend-choice-reference
document_type: reference
original_date: '2026-04-09'
archived_date: '2026-10-02'
scope:
  targets:
    - unidbg
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260409-01.md#第一代调试器--观察者必须介入执行流"
    basis: source-report
  - id: s2
    ref: "./paopao-20260409-01.md#第二代hook-框架--观察者可以驻留在进程内"
    basis: source-report
  - id: s3
    ref: "./paopao-20260409-01.md#五个后端引擎同一个接口不同的执行方式"
    basis: source-report
relations:
  - type: derived_from
    target: "./paopao-20260409-01.md#五个后端引擎同一个接口不同的执行方式"
tags:
  - unidbg
  - source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2]
    basis: source-report
    limits: 只记录来源点名的检查项。没有这些检查的实现，也没有绕过步骤。
  - name: parameters
    anchor: parameters
    sources: [s3]
    basis: source-report
    limits: 速度倍数是来源表内的区间，不是测量值。未核对当前 Unidbg 默认后端。
  - name: decision-flow
    anchor: decision-flow
    sources: [s3]
    basis: source-report
    limits: 只区分要追踪还是要速度。不描述如何把后端做成服务。
---

# Unidbg 后端按追踪或速度二选一

这张卡只回答两件事：来源认为调试器和 Frida 会被哪些检查看见，以及五个 Unidbg 后端里谁保留指令级追踪、谁只追求速度。不收录 Unicorn 调用示例，也不收录绕过步骤。层次缺口和 IOResolver 的返回值在下一篇的卡里，不在这里重复。

来源没有可公开定位的原文 URL。后端名字和倍数都是作者表里的字。

<a id="risk-control"></a>
## 来源点名的检查项

调试器一代被写成必须附加到进程，因此目标可以看见观察者。来源列出的四项是：

| 检查 | 来源原句中的判定 |
|---|---|
| TracerPid | 字段非零，说明有调试器附加 |
| 自占 ptrace | PTRACE_TRACEME，抢占调试位，让外部调试器无法再附加 |
| 软件断点 | 来源点名 ARM 的 BKPT |
| 单步变慢 | 检测执行耗时异常 |

Hook 一代被写成不再走 ptrace。来源仍点名两类 Frida 痕迹：默认端口 27042，以及 frida-agent.so。同句写了要先绕过，正文没有给出做法，本卡也不补。

<a id="parameters"></a>
## 五个后端的来源标注

| 后端 | 来源写的速度 | 来源写的分析能力 | 来源写的场景 |
|---|---|---|---|
| Unicorn | 1x（基准） | 完整 | 兼容性最好 |
| Unicorn2 | 1.2x | 完整 | 分析（推荐默认） |
| Dynarmic | 10-100x | 无 | 生产环境 |
| Hypervisor | 50-200x | 无 | macOS 开发 |
| KVM | 50-200x | 无 | Linux 生产环境 |

来源另写「约 150 个核心 JNI 函数实现」。这是约数，不是函数表。

<a id="decision-flow"></a>
## 追踪和速度不能同时要

来源把分歧写成执行方式，而不是功能名单：

> 所以支持指令级 Hook、内存监控、Trace

> 所以不支持细粒度监控

因此 分析和生产是两种根本不同的需求。要看每条指令就用带来源标注「分析（推荐默认）」的 Unicorn2；只要快，就落到分析能力为「无」的 Dynarmic、Hypervisor 或 KVM。本卡不把「生产」展开成部署步骤。

## 验证与限制

QEMU、Unicorn 的历史和 Qiling 等同赛道对比只说明定位，没有新的字段。速度倍数、1.2x 和约 150 个 JNI 都未复核。没有本地运行记录。
