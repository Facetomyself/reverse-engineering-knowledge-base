---
schema_version: 2
id: mobile-app-reverse-paopao-protobuf-analysis-reference
document_type: reference
scope:
  targets: [protobuf-analysis]
  client: android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./paopao-android-reverse-compilation/paopao-20260401-01.md#reference-extraction-108
    basis: source-report
modules:
  - name: parameters
    anchor: wire-format
    sources: [s1]
    basis: source-report
    limits: 仅整理来源报告中的 field number、wire type、Varint/ZigZag、length-delimited 与外层帧边界；没有目标业务字段、加密参数、接口样例或可复用 payload。
  - name: request-chain
    anchor: analysis-chain
    sources: [s1]
    basis: source-report
    limits: 这是通用分析链而非 PaoPao 请求链；没有 endpoint、HTTP method、headers、APK/SO、抓包或业务响应，不能据此构造或重放请求。
  - name: validation
    anchor: evidence-boundary
    sources: [s1]
    basis: source-report
    limits: 仅记录 raw decode、schema inference 与 Hook 观察之间的证据分层；没有 fixture、local parity、运行日志、业务读回或 server acceptance。
relations:
  - type: derived_from
    target: ./paopao-android-reverse-compilation/paopao-20260401-01.md#reference-extraction-108
tags: [protobuf, wire-format, varint, schema-recovery, frida, source-report]
---

# Android Protobuf 分析边界参考

这是一张中性 `source-report` reference。它从泡泡以安的 Protobuf 连载中提炼二进制字段边界、schema 推断和动态观察层，服务于“先确认格式、再判断类型、最后核对运行时边界”的检索；它不代表来源文章对应某个已识别的 PaoPao 接口，也不提供请求复现或加密/风控方案。

<a id="wire-format"></a>
## Wire Format 与参数边界

来源报告把字段表示为 `Tag + Value`，其中 `Tag = (field_number << 3) | wire_type`。常见 wire type 包括 Varint、64-bit、length-delimited 和 32-bit；Varint 的延续位与 ZigZag 只说明字节如何解释，不能单独确定业务字段类型。

length-delimited 的字节可能是 string、bytes、嵌套 message 或 packed repeated。`protoc --decode_raw` 得到的 field number 和原始值，是 wire-level 观察；字段名、`int32`/`sint32`/`uint32`、repeated/map/oneof 等 schema 语义需要生成代码、descriptor、多个样本或其他独立材料。gRPC 外层帧、压缩和自定义加密/序列化也应作为独立层登记，不能把外层 bytes 直接当成 Protobuf 字段。

上面的区分是来源报告的分析边界，不是当前目标的协议合同。文中示例为教学样例，本卡不复制请求样值、字段业务含义或目标 `.proto`。

<a id="analysis-chain"></a>
## 通用分析链与观察层

来源文章给出的可检索链路可以压缩为：

```text
静态/流量特征 → raw wire decode → schema/type inference
  → Message/parse/field-writer 观察 → 与传输 bytes 分层对照
```

- 静态侧可先查生成类、`writeTo` / `parseFrom`、field-number 常量、protobuf runtime、descriptor 或 Native 字符串；这些只是定位线索，不是某个 APK 的确认结果。
- 只有网络 bytes 时，可对多个样本做形状对照，再把推断回到生成代码、descriptor 或运行时调用点；启发式类型判断不能替代 schema 证据。
- 动态侧可区分 Message 级序列化/反序列化、parse 边界和 `CodedOutputStream` 字段写入层。类加载、重载和实现分支需按目标运行时单独核对，不能把示例 Hook 当成通用脚本。
- Lite/Nano、缺 descriptor、Native C++、外层压缩/加密和自定义序列化应进入不同分支；来源没有证明这些分支属于 PaoPao 构建。

这条链只描述分析材料如何逐层收窄，不等于业务请求的发送顺序、字段生产顺序或服务器验收顺序。

<a id="evidence-boundary"></a>
## 证据分层与限制

| 观察层 | 可以保留的最小结论 | 不能直接推出 |
|---|---|---|
| Wire bytes / `decode_raw` | 某段字节可按候选 wire type 解释 | 字段名、业务语义、加密前明文或接口可用 |
| 生成类 / `writeTo` / descriptor | 某个构建材料提供字段类型线索 | 当前版本、当前请求或服务端接受 |
| Message/parse/field Hook | 某次运行边界出现了待审查对象或字节 | 完整请求链、重放能力、风控规则 |
| 客户端字段修改示例 | 来源提出客户端篡改的防守提醒 | PaoPao 存在漏洞、服务器校验规则或业务授权结果 |

本卡及来源 archive 均为 `source-report`。本轮没有 APK、DEX、SO、Protobuf capture、Frida session、生成 `.proto`、运行日志或服务端 response；没有执行代码、设备、网络请求、local parity 或业务读回。因此它是格式与观察边界参考，不是 procedure、risk-control、签名器、replay recipe 或 server-accepted 结论。
