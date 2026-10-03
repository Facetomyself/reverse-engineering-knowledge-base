---
schema_version: 2
id: anti-detection-android-ace-deviceuniqueid-reference
document_type: reference
original_date: '2026-08-30'
archived_date: '2026-10-02'
scope:
  targets: [android-ace]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./android-ace-deviceuniqueid.md#deviceuniqueid-reference
    basis: source-report
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1]
    basis: source-report
    limits: 仅记录来源报告中的 Java/NDK/HAL、TSS SDK 与游戏发送回调边界；未检查设备、SO、ABI 或运行时 trace。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留参数角色、长度类别和字段位置；不复制 device identity、UUID、license、账户、环境标识、密钥、样本字节或密文。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 归纳 Widevine 取值到 native/UDP 上报的来源链；没有 packet capture、解码器、回调 trace 或服务端响应。
  - name: risk-control
    anchor: risk-control
    sources: [s1]
    basis: source-report
    limits: 只记录多路径/完整性/画像交叉验证的来源边界及“单一 deviceUniqueId”与“多信号融合”的内部矛盾；不发布单字段拉黑规则或绕过方案。
relations:
  - type: derived_from
    target: ./android-ace-deviceuniqueid.md#deviceuniqueid-reference
tags: [android, ACE, Widevine, deviceUniqueId, TEE, TSS, UDP, multi-path, source-report]
---

# ACE deviceUniqueId 取值与 TSS 上报参考

这张卡从 [ACE deviceUniqueId 来源归档](./android-ace-deviceuniqueid.md#deviceuniqueid-reference)提炼设备身份取值、Java/native 交接和上报包边界。它不是设备修改手册，也不把来源文章中的“拉黑机制”措辞升级成已验证的单字段服务端规则。

<a id="interfaces"></a>
## 接口分层

来源报告把链路拆成三层：

1. Java `MediaDrm` 读取 Widevine 属性，并将结果交给 TSS SDK 的 user-info 入口。
2. NDK `MediaDrm` 与 native HAL 直连是另外两条取值路径，分别绕过不同上层；来源将多路径结果一致性视为需要检查的边界。
3. TSS SDK 通过 report-data 函数把数据交给游戏提供的发送回调；native 不被描述为直接拥有业务 socket，最终由回调侧发出 UDP。

原文还区分 `TssSDKSetUserInfoWithLicense` / `TssSDKSetUserInfo` 的参数角色，以及初始化结构中的 size、game id 和发送回调。函数名和结构布局仅对来源所称构建有效。

<a id="parameters"></a>
## 参数与数据形状

- `deviceUniqueId` 在来源报告中被描述为 Widevine/TEE/RPMB/KeyBox 链路的硬件派生身份；本卡不复制其值、哈希、UUID 或 provisioning 样本。
- Java 取值进入 TSS user-info 状态，报告事件采用 `key|desc=...` 形状提示；真实事件值、规则标识和账户材料不收录。
- 来源报告给出一个 UDP packet boundary：类型、算法选择、长度、header CRC、flags、压缩检测 payload 与尾部 CRC。它只描述字段类别和打包顺序，不提供 key、ciphertext、decoder 或 fixture。

<a id="request-chain"></a>
## 取值到上报请求链

```text
MediaDrm / NDK / native HAL
  -> Widevine HAL -> TEE/RPMB/KeyBox
  -> device identity enters TSS user-info
  -> TSS report-data
  -> game-owned send callback
  -> packet encryption/compression/CRC boundary
  -> UDP send
```

来源还报告了弱锚点、上层 provisioning 文件和硬件派生身份的对照，以及 Java-only hook 可能造成跨路径不一致。这些是作者实验的 `source-report` 结果，不是本轮复测的 reset invariant；换设备、ROM、Widevine 版本或 TSS build 必须重核。

<a id="risk-control"></a>
## 风控交叉验证边界

来源提出的候选交叉项包括 Java/native 取值一致性、Key Attestation 的 root-of-trust 字段、Play Integrity verdict、Widevine level/provisioning status，以及 Build/SoC/GPU/传感器画像。本文只把它们整理为“服务端可能组合的独立证据类别”，没有 challenge、签名 verdict、权重、拒绝响应或生产规则证据。

必须保留一个内部矛盾：文章结尾把 ACE 概括为使用单个 `deviceUniqueId` 做设备级拉黑，但前文又说服务端结合多个字段、单一信号不足。故本卡不写“改某一字段即可解除/触发拉黑”，也不将完整性修复与身份取值混为一谈。

## 证据限制

全部模块均为 `source-report`。本轮未获取设备、TEE、SO、runtime trace、UDP capture、parity fixture 或 server acceptance；公开参考链接仅作为原文 bibliography，未用来升级结论。
