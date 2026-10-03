---
schema_version: 2
id: mobile-app-reverse-paopao-dfid-hybrid-encryption-reference
document_type: reference
original_date: '2026-03-16'
archived_date: '2026-10-01'
scope:
  targets:
    - anonymous Android music App (source report)
  client: Android app
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./paopao-android-reverse-compilation/paopao-20260316-01.md
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 仅整理匿名样本来源报告；AES key/IV 字符到字节的编码未闭合，RSA 公钥材料不完整，未独立复算。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 接口 host、精确版本与原始请求均未提供；不能当作可直接重放的接口规格。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 只记录作者报告的 AES 解密与 RSA 输出比对；原始输入输出缺失，本轮未复跑，不代表 local-parity 或 server-accepted。
tags: [android, device-registration, parameters, request-chain]
---

# 匿名 Android 音乐 App 设备注册：`p` 与请求体加密关系

本文将保留的来源 archive 中关于 dfid 注册请求的参数关系和调用链整理为检索参考。目标、版本和原始 APK/SO 均未知；所有结论均为来源作者报告，不是本轮运行时观察或独立复现。

<a id="parameters"></a>
## 参数机制

来源把 URL 参数 `p` 描述为 RSA 公钥加密结果，把请求体描述为设备指纹 JSON 经 AES-CBC 加密后的 Base64 内容。作者还报告 RSA 明文中的随机 `aes` 字段先计算 MD5 hexdigest，再按字符串切片派生 AES key 与 IV。这里保留关系，不推断 key/IV 的字节解码方式。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源称 `p` 是 RSA 加密参数，body 是 AES-CBC 加密后再 Base64 传输。 | s1，第 71–82、630–641、913–923 行 | source-report | 被匿名化的单个 Android 设备注册样本 | 请求域名和样例值已截断；不是完整接口定义或可重放样本。 |
| C2 | 作者称 RSA 明文中的随机 `aes` 字段经 MD5 hexdigest 后，前 16 字符作为 AES key、后 16 字符作为 IV。 | s1，第 687–703、937–957 行 | source-report | 来源报告描述的单次参数派生路径 | 字符串到实际 AES key/IV 字节的转换未闭合，未由本轮计算确认。 |
| C3 | 来源报告 RSA 公钥指数为 65537，并称用提取参数执行的大数模幂得到的密文与 hook 输出一致。 | s1，第 811–903、913–934 行 | source-report | 来源所述的单个样本与其捕获输出 | 完整模数依赖正文缺失的截图；无原始 hook 输出与 APK/SO hash，不能复用为当前目标的公钥或 parity 结论。 |

<a id="request-chain"></a>
## 请求链路

来源描述的局部链路是：设备指纹对象序列化为 JSON，进入 Java `j.u()` 加密入口并转入 native 实现；作者把 native 输出中的一个成员对应到 Base64 body，另一个成员对应到 URL 参数 `p`。原文还将 RSA 参数与 AES body 并列为一次设备注册 POST 请求的一部分。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | 作者描述 JSON 序列化 → Java/native 加密入口 → `p` 与请求体的映射关系。 | s1，第 95–105、209–217、219–287、412–436、906–923 行 | source-report | 匿名 Android 样本报告 | 包名、host 和版本为占位或未知；RegisterNatives 偏移依赖具体构建与 ABI，不是稳定接口。 |

<a id="validation"></a>
## 来源报告中的验证动作

本节只记录作者声称做过的检查，不能据此宣称本轮复现成功。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 作者称以捕获的 AES 参数解密请求体后恢复出设备指纹 JSON。 | s1，第 606–613 行 | source-report | 来源所述抓包与参数样本 | 解密输入、输出和对应截图未随 Markdown 提供，本轮未执行。 |
| C6 | 作者称 Python RSA 大数运算结果与 `RSA_public_encrypt` hook 输出一致。 | s1，第 894–903 行 | source-report | 来源代码与其单次 hook 样本 | 完整 hook 数据和运行环境缺失；不是本地 parity 或服务端接受证据。 |

## 未覆盖与复用边界

- 来源仅记载微信公众号名称，没有可定位的原文 URL；当前归档是本篇唯一可复查的文本依据。
- 目标 App、版本、APK/SO hash、架构及观测时间均未知。原文多处使用占位包名，图表/截图只有标题而无嵌入资源。
- AES key/IV 的编码、AES padding 与完整输入输出关系未闭合；不要猜测 hex 字符是 ASCII 还是解码后的原始字节。
- RSA modulus 汇总值不完整，算法参数和 hook 输出未经本轮复核；所有地址偏移都必须按新的二进制重新定位。
- 不复制来源样本中的设备标识、设备画像值、请求密文或密钥材料；不把该单样本外推到其他应用或当前版本。
- 本篇不定义通用操作步骤、失败出口或服务端验收流程，不作为 `procedure` 使用。
