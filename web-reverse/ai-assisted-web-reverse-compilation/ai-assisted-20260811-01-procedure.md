---
schema_version: 2
id: rsa-spki-content-anchor-procedure
document_type: procedure
original_date: '2026-08-11'
archived_date: '2026-10-02'
scope:
  targets:
    - rsa-spki
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./ai-assisted-20260811-01.md#一通用锚公钥-der-的-algorithmidentifier"
    basis: source-report
  - id: s2
    ref: "./ai-assisted-20260811-01.md#二案例猿人学-match27-的-token"
    basis: source-report
  - id: s3
    ref: "./ai-assisted-20260811-01.md#六随机填充别指望逐字节相等"
    basis: source-report
modules:
  - name: decision-flow
    anchor: steps
    sources: [s1, s2, s3]
    basis: source-report
    limits: 锚和失败出口来自这一篇的 RSA 练习题写法。openssl 三段输出和 200/403 对照都是作者自述，本轮未重跑。
  - name: parameters
    anchor: parameters
    sources: [s1, s2]
    basis: source-report
    limits: 只保留与密钥无关的算法标识、填充类型和明文字段角色。不收录模数、完整加密实现或请求样值。
  - name: validation
    anchor: acceptance
    sources: [s1, s3]
    basis: source-report
    limits: 位长无关的中段锚可以用本地 DER 对照。随机填充不能用逐字节相等验收。作者的 HTTP 结果不是本轮证据。
relations:
  - type: derived_from
    target: "./ai-assisted-20260811-01.md#一通用锚公钥-der-的-algorithmidentifier"
tags:
  - rsa-spki
  - source-report
---

# 用 RSA 公钥的算法标识做内容锚，而不是用函数名

这篇流程解决扁平化和短函数名下怎么定位 RSA 公钥的使用点，以及定位之后哪一种验收是无效的。猿人学 match/27 是来源里的案例。不收录模数、加密实现或请求样值。

<a id="prerequisites"></a>
## 前提与输入

脚本已经长到按名字钩函数会落空：来源案例是 335KB、控制流平坦化、函数名压成一两个字母，分派是 switch 而不是带 handler 数组的 table。

先有一个“这像 RSA”的理由，再选锚。来源用的理由是输出长度像 1024 位块，并且同一页两次结果不同。不要把函数名当成前提。

若要核对锚本身，来源用 openssl 导出 1024、2048、4096 三档 DER，比较中间那一段是否与位长无关。这是锚的本地对照，不是对目标站点的请求。

<a id="steps"></a>
## 步骤与分支

| 步骤 ID | 动作 | 观察与产物 | 条件与下一步 |
|---|---|---|---|
| S1 | 用内容锚而不是函数名 | 在脚本里找 RSA AlgorithmIdentifier 的固定中段 | 命中则去 S3。只用长度头，走 F1 |
| S2 | 若脚本嵌的是 base64 而不是 hex | 按位长试两种 base64 相位 | 2048 与 4096 同一相位，1024 是另一相位。两种都不命中则走 F2，不改去猜函数名 |
| S3 | 从命中点往明文拼装走一步 | 记录明文各段和填充是否标准 | RSA 若在脚本层而分派器只拼明文，就不要再拆 VM。有多把公钥则去 S4 |
| S4 | 数内嵌公钥，并看填充是否随机 | 每把公钥分开对照；同一明文加密两次应不相等 | 随机填充禁止逐字节对抓包。把相等当成通过，走 F3。一把公钥失败就像明文拼错，走 F4 |

S2 只在存储形式是 base64 时走。hex 或 DER 直接用 S1 的中段。

<a id="parameters"></a>
## 锚和案例里的字段角色

SubjectPublicKeyInfo 里的 AlgorithmIdentifier 与模数无关。来源给出的通用 hex 锚是 `300d06092a864886f70d0101010500`。它第一次用的 `30819f300d06092a` 能命中，但只覆盖 1024 位的长度头。

base64 相位来源写成：1024 用 `MA0GCSqGSIb3DQEBAQUAA`，2048 和 4096 用 `ANBgkqhkiG9w0BAQEFAAOC`。同一思路还可换成别的算法常量：SHA-256 的 IV、SM3 的 T、MD5 的 K 表首项、AES S-box 首行，或 base64 字母表。这些是定位用的公开常量，不是密钥。

案例里的输出角色是：1024 位块、128 字节、标准 base64、PKCS #1 v1.5 type 2、PS 为非零随机字节。明文是路径、服务端时间、题号和页码的零分隔符拼接。服务端时间来自一次取时，其余被写成离线。脚本内嵌两把 1024 位公钥。分派器只拼明文，加密在脚本层。来源把同族另一题写成多一个 `$` 分隔符。模数不进入本卡。

<a id="outputs"></a>
## 输出

- 实际使用的锚，以及它是中段算法标识、长度头，还是哪一种 base64 相位。
- 命中点到明文拼装的字段顺序，和填充是不是随机的。
- 内嵌公钥的个数。来源案例是两把，并称其中一把是诱饵。不交付任一公钥的模数。

<a id="acceptance"></a>
## 验收

- 锚与位长无关：1024、2048、4096 的 DER 都含同一中段。来源用 openssl 列出了这三行。本轮未重跑 openssl。
- 随机填充的自检是两次结果不相等。相等说明填充被写死，不能当成和抓包一致。
- 来源把案例的验收写成真实请求的 200 与 403，并称这是随机填充下唯一的验收，因为不能和抓包逐字节比。这是作者自述。本轮没有发请求，不把状态码写成已验收。

<a id="failure-exits"></a>
## 失败出口

F1：锚带了某一位长专属的 DER 长度头。来源写 `30819f` 只对 1024 位有效。换成中段算法标识，不要沿用长度头。

F2：base64 锚的相位用错。1024 与 2048/4096 不是同一段。两种相位都试过仍无命中，停止这条锚，不退回按压缩函数名去钩。

F3：PKCS #1 v1.5 的 PS 是随机的，却要求离线结果和抓包逐字节相等。停掉这个验收。来源写相等反而说明填充写死了。

F4：多把公钥里用错一把，返回的是失败而不是明确的“明文错了”。来源写用错不会报组装错误，而是 403，容易被当成明文拼错。停在“哪一把是诱饵未知”，不要只改明文字段。静态看两把同长度、同指数时，来源认为静态没有优势。
