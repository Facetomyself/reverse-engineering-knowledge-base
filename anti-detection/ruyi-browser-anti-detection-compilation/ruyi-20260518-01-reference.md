---
schema_version: 2
id: phish-fingerprint-2fa-reference
document_type: reference
original_date: '2026-05-18'
archived_date: '2026-10-02'
scope:
  targets: [phish-fingerprint-2fa]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260518-01.md#十这篇对反爬和风控有什么启发
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只保留“指纹可被任意网页采集、不能单独跳过 2FA、历史 IP 挡住其余站点”的转述。不写采集、复刻或伪造步骤。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留 14 个匿名站点的属性类别计数。没有字段值、绘制参数或音频参数。
relations:
  - type: derived_from
    target: ./ruyi-20260518-01.md#十这篇对反爬和风控有什么启发
tags: [phish-fingerprint, 2fa, source-report]
---

# 浏览器指纹不能单独跳过 2FA

这篇卡检索的是：笔记转述的 USENIX Security 2022 论文里，用浏览器指纹记住设备并少弹 2FA 时，边界划在哪里。不提供采集或伪造做法。

<a id="risk-control"></a>
## 认证边界

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 这些信号不是网站独占的。任何网页，只要能跑JavaScript，都能采集。 | s1，源文件第 96 行 | source-report | 登录风控里用到的浏览器指纹信号 | 不是当前站点实测 |
| C2 | 9个可以被这种方式绕过2FA | s1，源文件第 46–47 行 | source-report | 笔记中 14 个新设备会触发 2FA 的站点 | 站点匿名 |
| C3 | 这5个网站要求登录设备的IP地址也要匹配历史IP，或者至少要来自很接近的位置。 | s1，源文件第 208 行 | source-report | 未被写成绕过的那 5 个站点 | 转发头试验不在本卡 |
| C4 | 浏览器指纹不能当秘密。它不是密码，不是硬件密钥，不是WebAuthn私钥。 | s1，源文件第 300 行 | source-report | 笔记第十节的结论 | 没有实现 |
| C5 | 最好的方向不是“记住浏览器指纹”，而是设备绑定和抗钓鱼2FA，比如FIDO2/WebAuthn。 | s1，源文件第 306 行 | source-report | 笔记点名的高价值服务方向 | 没有 WebAuthn 流程 |

<a id="parameters"></a>
## 依赖了哪一类属性

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | 12/14个网站使用指纹判断设备是否已知 | s1，源文件第 224 行 | source-report | 人工深测的 14 个站点 | 匿名样本 |
| C7 | 8个依赖基础指纹，比如navigator、window等属性 | s1，源文件第 225–227 行 | source-report | 同上 | 不列字段值 |
| C8 | 6个使用更高级的Canvas/WebGL和字体 | s1，源文件第 226 行 | source-report | 同上 | 没有绘制参数 |
| C9 | 2个还使用AudioContext指纹。 | s1，源文件第 227 行 | source-report | 同上 | 没有音频参数 |

## 验证与限制

`browser-fingerprint`、`web-audio`、`window` 的已有卡片只写宿主对象语义，不包含这组“记住设备 / 跳过 2FA”的计数。`webauthn` 与 `2fa` 没有卡片。第二、三节的三步叙述和第 209 行的转发头试验不进入本卡。效果数字保持 source-report。
