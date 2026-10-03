---
schema_version: 2
id: softard-findcrypt-evasion-recovery-reference
document_type: reference
original_date: '2026-06-06'
archived_date: '2026-09-06'
scope:
  targets:
    - Android SO findcrypt evasion
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./softard-20260606-01.md#一运行时计算"
    basis: source-report
  - id: s2
    ref: "./softard-20260606-01.md#二静态加密"
    basis: source-report
  - id: s3
    ref: "./softard-20260606-01.md#三时机对抗"
    basis: source-report
  - id: s4
    ref: "./softard-20260606-01.md#四魔改常量"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1, s2, s3, s4]
    basis: source-report
    limits: 只整理来源列出的四类藏常量做法。来源自己写成抛砖，不是完整防护，也没有对应 SO。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s2, s3, s4]
    basis: source-report
    limits: 恢复动作停留在来源原句：F5 还原、解密后扫、hook 数据流、用输出长度认骨架。没有本机命中。
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s4]
    basis: source-report
    limits: 数学来源、MD5 IV 字节序和输出长度是来源给的判别参数。示例异或数不是某个产品的密钥。
relations:
  - type: derived_from
    target: "./softard-20260606-01.md#一运行时计算"
tags:
  - findcrypt
  - constant-hiding
  - md5
  - aes
  - source-report
---

# findcrypt 扫不到常量时，来源怎么把值藏起来又怎么认回去

这张卡只回答：标准常量不在静态文件里时，来源用哪三个维度藏，以及对应的认回口径。识别表本身在前一篇，目标不同，不并进那张常量卡。来源写明这是抛砖，不是系统化对抗。出处是 [对抗算法特征检索](./softard-20260606-01.md#一运行时计算)。

<a id="risk-control"></a>
## 四种藏法

总前提是 `常量一定存在于内存某处`（:40）。差别只是位置、出现时间和形式。

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C1 | 运行时才算出标准值，静态文件里不放原值 | 原始值不出现在代码里 | s1 :51 | source-report | 异或或拆分赋值 | 示例右值不是产品密钥 |
| C2 | 也可以按数学来源现算，例如 SHA1 轮常量 | floor(sqrt(2) * 2^30) | s1 :58 | source-report | 来源点名的 SHA1 轮常量 | 未给另外三个根 |
| C3 | 静态扫描期间原常量不在，findcrypt 落空 | findcrypt 什么也找不到 | s1 :69 | source-report | 上一节四种写法的共同点 | 只针对自动化扫描 |
| C4 | .rodata 整段加密时，静态文件里的特征全部消失 | 特征常量全部消失 | s2 :87 | source-report | 爱加密一类，以及 LLVM -ecs | 没有具体壳版本 |
| C5 | 用完清零或放在栈上，扫描窗口被压到毫秒 | 扫内存的窗口被压缩到毫秒级 | s3 :120 | source-report | 堆和全局仍可扫，栈帧返回即没 | 没有测到的窗口 |
| C6 | 换掉标准 IV 或 S-Box 后，findcrypt 和标准库都对不上 | 自定义置换表 | s4 :151 | source-report | 两端用同一张表 | 来源写弱点说不清楚 |

<a id="decision-flow"></a>
## 来源给出的认回分支

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C7 | 异或和拆分赋值，F5 之后能拼回原值，只能骗扫描器 | 脚本算一下马上还原 | s1 :79 | source-report | 认真读伪代码 | 后半句在 :80，对 AI 也几乎无障碍是作者说法 |
| C8 | 段加密只是推迟出现时间，JNI_OnLoad 或 .init_array 返回后再看内存 | JNI_OnLoad | s2 :97 | source-report | SO 必须先解密才能跑 | 没有解密函数偏移 |
| C9 | 不找常量时，改为在清零前 hook 算法入口或数据流入口 | md5_update_addr | s3 :133 | source-report | 来源点名的 update 入口 | 地址是符号，不是偏移 |
| C10 | 常量被魔改后改认骨架：固定 16 字节输出按分组密码 | 输出长度固定 16 字节 | s4 :161 | source-report | 无论输入多长 | 不能推出就是标准 AES |
| C11 | 固定 32 字节输出按 256-bit 摘要骨架 | 输出长度固定 32 字节 | s4 :162 | source-report | 无论输入多长 | 未排除截断 |
| C12 | 换密钥输出变、不换则不变，用来分开加密和 hash | 是加密不是 hash | s4 :163 | source-report | 已知输入对照 | 没有样本输入 |

<a id="parameters"></a>
## 认回时用到的值

| claim_id | 结论 | quote | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|---|
| C13 | 示例异或的结果被写成标准 MD5 的 a | 0x67452301 | s1 :51 | source-report | 该行注释 | 左右操作数是教学数 |
| C14 | SHA1 第一轮常量被写成 0x5A827999，来自根号 2 | 0x5A827999 | s1 :58 | source-report | 与 C2 同一句 | 未在本篇重算 |
| C15 | 解密后的内存扫描，来源用 MD5 IV 的字节序当模式 | 01 23 45 67 89 ab cd ef fe dc ba 98 76 54 32 10 | s2 :101 | source-report | 可读内存范围 | 整段扫描函数粘在一行，本卡不重建 |
| C16 | 结构认完之后，剩下的是把魔改参数抠出来换到同结构实现 | 不影响算法类型的判断 | s4 :165 | source-report | 骨架已经分开之后 | 没有参数布局 |

## 验证与限制

- 目标 `Android SO findcrypt evasion` 的 parameters、decision-flow、risk-control 都没有命中。前一篇的常量表是另一个 target，目录里还没有那张卡，不能把这篇补进一个不存在的模块。
- `xtime` 卡和 `IDA/Windows WORD` 卡都不是藏常量。环境准备流程也不是这篇。
- 扫描和 hook 都错过时，来源没有停止条件，只有开篇那句系统化对抗不是改一处就能防住。因此不建流程。
- 没有 SO、没有 JNI_OnLoad 返回时刻的内存转储，作者称为看穿或扫到的句子保持 source-report。
