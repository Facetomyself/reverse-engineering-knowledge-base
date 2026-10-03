---
schema_version: 2
id: mobile-app-reverse-sdk-purecalc-compilation-jincai-pingxiang-wtoken
document_type: reference
scope:
  targets:
  - 今彩萍乡 WTokenPure.vmpSign
  client: Android SDK/native-backed pure calculation
  version: sample-bound; exact target build unknown
  observed_at: unknown
sources:
- id: s1
  ref: null
  basis: source-report
  citation: 本地项目分析材料（定位不公开）
  reason: 出处来自原归档来源字段；本地路径已省略，原始材料未随本文公开，本轮未重跑来源实验。
source_completeness: unknown
modules:
- name: parameters
  anchor: jincai-wtoken-shape
  sources: [s1]
  basis: source-report
  limits: 274 字节 blob、字段顺序和 token 形状来自来源报告；敏感常量和完整实现不在正文。
- name: validation
  anchor: jincai-server-boundary
  sources: [s1]
  basis: source-report
  limits: 正文明确 self-test 不等于 serverAccepted；本轮未执行服务端验收。
tags: [wtoken, 274-byte-blob, xxtea-boundary]
original_date: 源码落盘
archived_date: '2026-09-06'
---

# 今彩萍乡 wtoken：0003_ 头 + 274 字节 blob

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: workspace/jincai-pingxiang-wtoken
> 原始发布时间: 源码落盘
> 归档日期: 2026-09-06
> 分类: mobile-app-reverse
</details>
>
> `WTokenPure.vmpSign` 生成带固定前后缀的 token。AES/HMAC 密钥、签名 MD5 和自测 token 不进本文。

<a id="jincai-wtoken-shape"></a>
## 格式

```text
0003_ || timestamp_low40_hex || header_byte || final48_hex || Base64(blob_cipher) || _fHx8
```

blob 固定 274 字节：固定前缀 + little-endian `front_word_u32` + 固定中段 + nibble-swap 后的包名/应用名/版本/SDK/品牌/型号/Android/device/签名 MD5/动态尾。

## 摘要链（形状）

```text
msg = input_text || "&22be_" || blob || "&" || ts_hex
state = custom_32bit_hash(msg)
msg40 = 五个状态字拼成的 40 hex
stage0 = 4 字节前缀 || HMAC-SHA256(msg40)[:20]
header 变换 -> AES-CBC(blob)
```

密钥材料按样本绑定，换包必须从当前 so 回读。

<a id="jincai-server-boundary"></a>
## 边界

- self-test 对齐 unidbg ≠ 业务 `serverAccepted`
- 默认模板是今彩萍乡包名 + MI 8 字段组，禁止拆开随机
- 实现：`workspace/jincai-pingxiang-wtoken/source/wtoken_pure.py`

## 提炼说明（457）
retain 既有今彩萍乡 wtoken 形状 reference。
密钥按样本绑定，不写入。
本轮不另建卡。
