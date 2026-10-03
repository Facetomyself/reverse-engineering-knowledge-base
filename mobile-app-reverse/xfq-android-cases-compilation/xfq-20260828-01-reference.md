---
schema_version: 2
id: kuaishou-android-whitebox-aes-families-reference
document_type: reference
original_date: '2026-08-28'
archived_date: '2026-10-02'
scope:
  targets:
    - kuaishou
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./xfq-20260828-01.md#正文"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留 48 字节白盒、两套用途、产品线差异和快影 sig3 前置哈希的说法。短字符串原值、轮密钥和 trace 步骤不收录。没有版本号。
relations:
  - type: derived_from
    target: "./xfq-20260828-01.md#正文"
tags:
  - kuaishou
  - white-box-aes
  - source-report
---

# 快手 Android：48 字节白盒的两套用途

这张卡只回答：来源把快手系 App 里的公共白盒按什么用途和产品线拆开。不提供轮密钥，也不把 Web 端 `__NS_sig3` 请求链当成同一模块。

来源没有可公开定位的原文 URL。短字符串原值不进入本卡。作者写下的「能节省几小时」只保留为 source-report。

<a id="parameters"></a>
## 参数机制

来源写快手系列有一个公共的 48 字节白盒 AES，底层接近，但 key 有两套。一套用于签名或压缩，例子是 `__NS_sig3`。另一套用于加密指纹类字段，点名的是 `deviceInfo`、`carryInfo`、`data`、`env`、`sign`。这些只是字段角色，没有样例。

产品线被拆成两组，两组都没有版本号，也没有 so 文件名：

| 产品线 | 来源对 sig3 白盒的说法 | 来源对指纹那一套的说法 |
|---|---|---|
| 主版 / 极速版 | 与指纹套不是同一把 key | 与签名套分开；短字符串不收录 |
| 快影 / 可灵 | so 和主版、极速版不一样；前置哈希是标准 SHA-256 | 被说成跟主版区别不大；短字符串不收录 |

来源给主版、极速版和快影各写了短字符串。本卡不收录这些原值。历史引用块里同一组字符串是截断的，不能拿截断片段当 key。

提取路线只被点名，没有步骤：unidbg 上做 DFA 拿轮密钥再逆推，或者 rizin 静态加 trace 找轮密钥加载。没有表、没有偏移、没有失败时怎么停。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 公共算法被说成 48 字节白盒 AES，签名/压缩和指纹加密各一套 key | s1 | source-report | 来源称为 ks 全系 | 没有版本和 so 名 |
| C2 | 快影、可灵的 so 与主版、极速版不同，sig3 前置哈希被说成标准 SHA-256 | s1 | source-report | 只覆盖来源点名的这两款 | 没写主版前置哈希的具体算法，只说不一样 |
| C3 | 指纹套在快影上被说成跟主版区别不大 | s1 | source-report | 来源的一句比较 | 没有字段级对照 |

## 验证与限制

- 没有本地 so，没有轮密钥，没有一次 trace。DFA 和 rizin 只是路线名。
- `kuaishou` 的 parameters、interfaces 近邻为空。`../../web-reverse/products/kuaishou-ns-sig.md` 的目标同名，但是 client 为 web，模块是 request-chain 和 validation，讲的是 hxfalcon / sig3 的 Web 落点。Android 白盒分套不补进那张卡。
- 正文不到五十行，没有前提、步骤、输出、验收、失败出口，不是流程。
