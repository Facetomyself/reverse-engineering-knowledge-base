---
schema_version: 2
id: grok-mobile-app-reverse-paopao-20260325-01
document_type: reference
original_date: "2026-03-25"
archived_date: "2026-10-02"
scope:
  targets: [tea-family]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260325-01.md#61-特征常量识别"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只记录来源写下的分组、密钥长度、轮数和 Delta 检索形式。未运行实现，不收录样本密钥。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: 区分规则是来源的识别口诀。QQ 的 16 轮只是来源陈述，填充与密钥不在本卡。
relations:
  - type: derived_from
    target: "./paopao-20260325-01.md#61-特征常量识别"
tags: [tea, xtea, xxtea]
---

# TEA 家族的识别参数

这张卡只回答一个检索问题：来源如何用分组、Delta 的几种写法，以及轮函数形状区分 TEA、XTEA 和 XXTEA。范围是这篇归档的文本。密钥提取、填充和签名重放不进入卡片。作者关于还原成功的句子保持为来源陈述。

<a id="parameters"></a>
## 规模与 Delta 检索形式

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 分组为 64 位，两个 32 位无符号整数。quote: 两个 32 位无符号整数 (v0, v1) | s1 ./paopao-20260325-01.md:78 | source-report | tea-family | 未对具体二进制计数 |
| C2 | 密钥为 128 位，四个 32 位无符号整数。quote: 四个 32 位无符号整数 (k0, k1, k2, k3) | s1 ./paopao-20260325-01.md:79 | source-report | tea-family | 不记录样本密钥 |
| C3 | 标准实现是 32 个循环，每个循环两轮。quote: 32 个循环，每个循环包含 2 轮操作 | s1 ./paopao-20260325-01.md:80 | source-report | 标准 TEA/XTEA | 魔改轮数不在本句 |
| C4 | 标准 Delta 写作 0x9E3779B9。quote: 0x9E3779B9 | s1 ./paopao-20260325-01.md:82 | source-report | TEA/XTEA/XXTEA 标准实现 | 公开算法常量 |
| C5 | 来源把补码关系写成常见伪装。quote: 二进制补码 | s1 ./paopao-20260325-01.md:171 | source-report | 编译器改写后的加法 | 未看编译输出 |
| C6 | 补码常量写作 0x61C88647。quote: 0x61C88647 | s1 ./paopao-20260325-01.md:589 | source-report | 立即数搜索 | 与加上标准 Delta 的等价是来源说法 |
| C7 | 有符号十进制写作 -1640531527，来源指向 Java。quote: -1640531527 | s1 ./paopao-20260325-01.md:590 | source-report | Java 文本搜索 | 只是显示形式 |
| C8 | 无符号十进制写作 2654435769。quote: 2654435769 | s1 ./paopao-20260325-01.md:591 | source-report | 反编译器立即数 | 来源未附截图 |
| C9 | Java 右移必须用无符号形式。quote: 必须使用 >>> (无符号右移) | s1 ./paopao-20260325-01.md:384 | source-report | Java 移植 | 只读到注释 |
| C10 | XXTEA 轮数写作 6 + 52/n。quote: 6 + 52/n | s1 ./paopao-20260325-01.md:257 | source-report | 可变分组 | n 为字数 |
| C11 | 优化表把加上标准 Delta 显示成减去补码，称为最常见伪装。quote: 最常见的"伪装" | s1 ./paopao-20260325-01.md:807 | source-report | Hex-Rays 一类输出 | 与 C5、C6 同源 |

<a id="decision-flow"></a>
## 三成员怎么分开

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C12 | XTEA 的子密钥由 sum 选择，表内写法是 key[sum & 3]。quote: key[sum & 3] | s1 ./paopao-20260325-01.md:238 | source-report | XTEA 相对 TEA | 另一下标不在这一格 |
| C13 | XTEA 的识别写法是左右移位先异或。quote: (v<<4) ^ (v>>5) | s1 ./paopao-20260325-01.md:242 | source-report | 与 TEA 的分开相加对照 | 口诀级特征 |
| C14 | 三路分开异或判为 TEA。quote: 三路分开 XOR | s1 ./paopao-20260325-01.md:731 | source-report | 来源口诀 | 不是形式证明 |
| C15 | 移位异或合并后再加 v 判为 XTEA。quote: 移位异或合并后加 v | s1 ./paopao-20260325-01.md:732 | source-report | 来源口诀 | 口诀 |
| C16 | 可变分组且相邻字交互判为 XXTEA。quote: 可变分组 + 相邻字交互 | s1 ./paopao-20260325-01.md:733 | source-report | 来源口诀 | 口诀 |
| C17 | 有左移 4 和右移 5 但 Delta 非标准值时，来源称为魔改 TEA。quote: 魔改 TEA | s1 ./paopao-20260325-01.md:734 | source-report | 常量被替换的实现 | 不能因此排除其他算法 |
| C18 | 来源把 QQ 协议写成 16 轮 TEA 加 CBC，而不是标准循环次数。quote: 16 轮 TEA 结合 CBC 模式 | s1 ./paopao-20260325-01.md:543 | source-report | 该来源对 QQ 的陈述 | 填充和密钥不在本卡，未核对实现 |

## 验证与限制

近邻查询没有 tea-family 的 parameters 或 decision-flow 卡片。腾讯滑块相关归档的目标是 tencent-captcha，不并入本卡。本卡没有密钥调度实现、填充规则或签名重放。没有本地运行证据，不能把来源里的还原成功当成已复核。
