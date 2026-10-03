---
schema_version: 2
id: paopao-20260410-unidbg-gap-map-reference
document_type: reference
original_date: '2026-04-10'
archived_date: '2026-10-02'
scope:
  targets:
    - unidbg
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260410-01.md#第五层文件系统ioresolver"
    basis: source-report
  - id: s2
    ref: "./paopao-20260410-01.md#从一次报错开始"
    basis: source-report
  - id: s3
    ref: "./paopao-20260410-01.md#第二层linux-系统调用syscallhandler"
    basis: source-report
  - id: s4
    ref: "./paopao-20260410-01.md#缺失五没有-art-虚拟机不能执行-dex-代码"
    basis: source-report
  - id: s5
    ref: "./paopao-20260410-01.md#一张地图哪些由-unidbg-处理哪些由你处理"
    basis: source-report
relations:
  - type: derived_from
    target: "./paopao-20260410-01.md#第五层文件系统ioresolver"
tags:
  - unidbg
  - source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 三种返回值是来源对 IOResolver 的语义说明，未对某个 Unidbg 版本调用核对。
  - name: parameters
    anchor: parameters
    sources: [s2, s4, s5]
    basis: source-report
    limits: 30% 和 150 都是来源约数。不收录示例进程名或手写返回值。
  - name: risk-control
    anchor: risk-control
    sources: [s3, s4]
    basis: source-report
    limits: 暴露面是来源的推断。没有样本证明某个 SO 会做这些检查。
---

# Unidbg 已实现层、文件返回值和来源点名的缺口

这张卡只回答：来源认为 Unidbg 自动覆盖到哪一层，IOResolver 的三种返回值各表示什么，以及哪些缺口会被目标看成「不像真机」。后端速度与追踪的选择见前一篇。不收录调用骨架，不收录为缺口填返回值的步骤。

来源没有可公开定位的原文 URL。覆盖率是作者的约数。

<a id="interfaces"></a>
## IOResolver 的三种返回

来源把虚拟文件写成按路径回答，而不是完整文件系统。三种返回值不能混用：

| 返回 | 来源写的含义 |
|---|---|
| FileResult | 文件存在，内容由该对象给出 |
| -1 | 明确告诉 SO 这个文件不存在 |
| null | 交给 Unidbg 默认逻辑 |

未注册且默认逻辑也不认识的路径，来源另写最终是文件不存在。本卡不给出路径清单。

<a id="parameters"></a>
## 来源给出的覆盖约数

| 项 | 来源原句 |
|---|---|
| 未实现的 JNI 静态方法 | 报错里出现 callStaticObjectMethod not implemented，表示调用没有自动应答 |
| 系统调用 | 已实现部分写成 约 30% |
| JNI | 约 150 个核心 JNI 函数 |
| 具体 Java 方法 | 被划入「需要你手动实现」 |
| ART | 不能执行 Java/Kotlin 代码 |
| 系统属性 | 对照表写 无属性数据库 |

字符串、数组和引用计数被写成自动处理。没有 ART 时，具体方法的返回值只能从外部给出。本卡不写该返回值是什么。

<a id="risk-control"></a>
## 来源点名的不像真机之处

这些是暴露面的名字，不是检测实现，也不是掩盖步骤。

| 缺口 | 来源怎么写 |
|---|---|
| 指令差异 | 可能被用作 Unicorn 引擎指纹检测 |
| 时钟 | clock_gettime 不是模拟出的 Android；慢几十倍时时间差检查就会暴露 |
| 地址布局 | 可能会检查内存布局是否符合真机特征 |
| 其他进程 | 遍历其他进程信息会得到不存在其他进程 |
| 线程 | JNI_OnLoad 中创建后台线程并等待，可能导致死锁 |
| 网络 | 发起网络请求会被写成全部失败 |

死锁一行的处理办法、属性读取的挂钩，以及文末的问答示例，都不在本卡里。

## 验证与限制

约数没有对上某个提交。Binder 缺失被来源解释成通常被 JNI 层挡住，这仍是未验证的结构说明。加载走查表与文末对照表是同一张图的重复，不另增字段。没有本地运行记录。
