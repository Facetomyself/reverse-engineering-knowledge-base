---
schema_version: 2
id: ruyi-20260404-fingerprin-tv-reference
document_type: reference
original_date: '2026-04-04'
archived_date: '2026-10-02'
scope:
  targets: [fingerprin-tv]
  client: smart-tv
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260404-01.md#三种指纹技术
    basis: source-report
  - id: s2
    ref: ./ruyi-20260404-01.md#三种指纹的互补性
    basis: source-report
  - id: s3
    ref: ./ruyi-20260404-01.md#核心发现
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留三类指纹的构成和 20 次交集。不抄示例域名、包长或 JA3 原值。
  - name: risk-control
    anchor: risk-control
    sources: [s3]
    basis: source-report
    limits: 唯一率和平台差异只对文中的启动窗口、实验室流量有效。防御效果来源写明没测。
  - name: decision-flow
    anchor: decision-flow
    sources: [s2, s3]
    basis: source-report
    limits: 只保留组合优先和 DBF 不可用时的后备。没有部署验收，不能当成流程。
relations:
  - type: derived_from
    target: ./ruyi-20260404-01.md#三种指纹技术
tags: [fingerprin-tv, source-report]
---

# FingerprinTV 的三种流量指纹边界

这篇卡检索的是：该文转述的智能电视实验里，三种指纹各由什么组成、组合后能区分到哪一步、什么时候不能沿用。不提供采集脚本。

<a id="parameters"></a>
## 三种指纹是什么

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 域名指纹是集合：DBF就是一个App在启动时连接的所有域名的集合。 | s1，源文件第 72 行 | source-report | App 启动连接 | 示例域名不在本卡 |
| C2 | 稳定域名要取交集：对每个App重复启动20次，取所有次启动中都出现的域名的交集 | s1，源文件第 84 行 | source-report | 来源的 20 次启动 | 不是通用阈值 |
| C3 | 包对指纹的元素：数据包的大小和方向的二元组序列 | s1，源文件第 88 行 | source-report | 域名不可见时的流量形态 | 示例包长不在本卡 |
| C4 | TLS 指纹先按连接做 JA3：TBF使用JA3哈希（把TLS版本、密码套件、扩展、椭圆曲线、椭圆曲线点格式五个字段拼接后做MD5）作为每个连接的TLS指纹，然后 | s1，源文件第 107 行 | source-report | 启动时各条 TLS 连接 | 不是浏览器指纹随机化笔记；无原始哈希 |

<a id="risk-control"></a>
## 组合后能区分什么

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | Fire TV 的组合结果：DBF + TBF的组合在Fire TV上达到89%的唯一识别率。 | s3，源文件第 187 行 | source-report | 文中启动阶段的实验室流量 | 不是家庭网络复测 |
| C6 | 同一 App 换平台会换 TLS 库：不同平台使用不同的TLS库（Apple TV用Apple的Security.framework，Fire TV用Android的BoringSSL，Roku用自己的TLS实现），导致JA3指纹不同。 | s3，源文件第 214 行 | source-report | 文中的跨平台 App | 没有 JA3 原值 |
| C7 | Roku 会把 App 流量揉在一起：Roku的SDK层代理了大量网络请求，使得不同App的流量模式趋同。 | s3，源文件第 252 行 | source-report | 文中 Roku 唯一率偏低的原因 | 不是代理效果测量 |
| C8 | 窗口只有启动：每次只采集120秒的流量，而且是从App启动开始计时。 | s3，源文件第 235 行 | source-report | 这篇实验的采集窗 | 不能识别 App 内换内容 |

<a id="decision-flow"></a>
## 何时组合

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C9 | 不单押一种：不依赖单一指纹类型，而是组合使用。 | s2，源文件第 119 行 | source-report | 三种指纹都可观察时 | 没有防御验收 |
| C10 | 域名不可见时的后备：TBF仍然能达到65-70%，这是一个有价值的后备方案。 | s3，源文件第 192 行 | source-report | 上一行所说的 DBF 不可用场景 | 65-70% 是来源转述 |

## 验证与限制

目录里没有同名的 `fingerprin-tv`、`ja3` 或 `smart-tv` 模块。本卡不覆盖浏览器 ClientHello 随机化。采集管线、示例域名、包长、广告用途和电视遥控自动化都不在本卡。实验室单设备、4 周稳定性和防御效果均按来源写成未完成或不足。数字保持 source-report。
