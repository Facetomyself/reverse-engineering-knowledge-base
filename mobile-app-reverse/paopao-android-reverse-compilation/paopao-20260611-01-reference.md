---
schema_version: 2
id: paopao-20260611-ncm-injection-choice-reference
document_type: reference
original_date: '2026-06-11'
archived_date: '2026-10-02'
scope:
  targets:
    - com.netease.cloudmusic
  client: android
  version: 9.2.80
  observed_at: '2026-06-11'
sources:
  - id: s1
    ref: "./paopao-20260611-01.md#三场景转变绕过签名校验是一场时间竞赛"
    basis: source-report
  - id: s2
    ref: "./paopao-20260611-01.md#七选择指南与总结"
    basis: source-report
  - id: s3
    ref: "./paopao-20260611-01.md#六gadget-并不比-frida-server-隐蔽"
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s2, s3]
    basis: source-report
    limits: 重签对照和注入方式对照都是作者在 9.2.80、Android 13 上的自述。证书指纹和设备串不在本卡。慢层快层不在本卡重复展开。
relations:
  - type: derived_from
    target: "./paopao-20260611-01.md#三场景转变绕过签名校验是一场时间竞赛"
tags:
  - com.netease.cloudmusic
  - source-report
---

# 网易云音乐 9.2.80 上免 Root 重签和注入方式怎么选

这张卡只回答选择：什么时候免 Root 重打包会在签名校验上失败，不重签之后 Gadget 和 frida-server 有没有存活差。不收录重签脚本、证书原值或明文样本。运行时两层检测面见 2026-06-04 那张卡，这里不重复。

<a id="decision-flow"></a>
## 重签本身，以及不重签之后怎么选

来源把易盾壳的签名校验写成又早又深。免 Root 的三种塞入方式都改 APK，没有原私钥就只能重签，签名就变了。

> 易盾这种把校验做得又早又深的顶级壳

> 免 Root 注入 = 改 APK = 重签 = 签名变了

零逻辑改动、不放 Gadget、只重签的对照同样退出。来源因此把触发条件收成重签本身，而不是注入手法。Java 层替换来不及，自带 MD5 和内联比较又让标准比较函数钩不到。这被限定为实现层走不通，不是逻辑上不可能。

> 触发条件是 **重签本身**

> 赛跑必输

> libpoison 不走 libcrypto，用自己加密代码里的 MD5

> 比较是 **内联在加密代码** 里的

> 自实现 MD5 + 内联比较 + 代码段运行时解密

> 这是「实现层不可行」，不是「逻辑上不可能」

另一类是校验晚、在 Java 层、甚至拖到联网之后。来源把免 Root 只留给不校验自身签名的应用。对这个易盾样本，签名墙是靠不重签消失的。ZygiskFrida 没有 ptrace 和 memfd，但抹掉 maps 名字挡不住直接走 linker solist 的检测。

> 唯一适合免 Root 的场景

> 靠「不重签」直接绕过，而不是靠 Hook 绕过

> 无 ptrace、无 memfd

> 直接遍历 linker solist 链表的检测照样能发现

同机、同原版的对照里，带 memfd/ptrace 的 frida-server 并不更差。来源称注入结构那道墙这次没出现，Gadget 没有可证明的存活优势，并写 frida-server 与 ZygiskFrida 存活等价。这和 2026-06-04 第 9 节「Android 13 约 1 秒杀死裸 agent」冲突，两篇都只是作者自述。

> 活得和无这些结构的 Gadget 一样好

> 这次根本没观测到

> 没有任何可证明的存活优势

> 与 ZygiskFrida 存活等价，无隐身劣势

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C2 | 免 Root 注入 = 改 APK = 重签 = 签名变了 | 正文第 148 行 | source-report | 没有原签名私钥 | 不外推有私钥的官方包 |
| C3 | 触发条件是 **重签本身** | 正文第 213 行 | source-report | 本篇重签对照 | 作者自述 |
| C8 | 这是「实现层不可行」，不是「逻辑上不可能」 | 正文第 273 行 | source-report | 易盾这一类早校验 | 更早加载并未做成 |
| C11 | 靠「不重签」直接绕过，而不是靠 Hook 绕过 | 正文第 366 行 | source-report | 装回原版之后 | 证书原值不收录 |
| C14 | 没有任何可证明的存活优势 | 正文第 497 行 | source-report | 这次 Gadget 与 server 对照 | 不是所有应用 |
| C15 | 唯一适合免 Root 的场景 | 正文第 516 行 | source-report | 不校验自身签名的应用 | 表内上一列限定范围 |
| C16 | 与 ZygiskFrida 存活等价，无隐身劣势 | 正文第 518 行 | source-report | 有签名校验且使用原版 | 只针对这次对照 |

## 验证与限制

没有本地重签或注入。墙 C 的慢层和快层、以及 native-only 的秒数，留在 2026-06-04 的 risk-control，本卡不把它们再建成一个模块。配置示例、线程名替换和请求样本不收录。
