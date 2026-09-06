# 今彩萍乡 wtoken：0003_ 头 + 274 字节 blob

> 来源: workspace/jincai-pingxiang-wtoken
> 原始发布时间: 源码落盘
> 归档日期: 2026-09-06
> 分类: mobile-app-reverse
>
> `WTokenPure.vmpSign` 生成带固定前后缀的 token。AES/HMAC 密钥、签名 MD5 和自测 token 不进本文。

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

## 边界

- self-test 对齐 unidbg ≠ 业务 `serverAccepted`
- 默认模板是今彩萍乡包名 + MI 8 字段组，禁止拆开随机
- 实现：`workspace/jincai-pingxiang-wtoken/source/wtoken_pure.py`
