# 腾讯 Qimei REGISTER：route15 之后才是 ky/pms/sn

> 来源: workspace/tencent-qimei-pure
> 原始发布时间: 2026-08-10 源码
> 归档日期: 2026-09-06
> 分类: mobile-app-reverse
>
> 应用宝风控设备标识的纯协议 REGISTER。无 JAR、无 Frida、无执行 so。不收录 appKey、静态 AES、RSA 公钥、identity 和 zip 口令。

## 流程

```text
随机 phone_guid / android_id / Luhn IMEI
  -> body：f3 QmUin JSON、f5 环境串、f7 双路魔改 SHA256、f12 设备 JSON、f18 192 字节
  -> route15 = len-field(header) || len-field(body)
  -> 外层 JSON：cpt / ky / pms / tm / nn / sn / ext
  -> POST snowflake /ola/v2
  -> 会话 AES 解 data -> q16 / q36
```

离线 `demo.py` 只证明能生成外层 JSON。`serverAccepted` 必须来自 snowflake 业务 readback。

## 外层加密（形状）

| 字段 | 作用 |
|------|------|
| `pms` | 两段 AES-CBC-PKCS7：先静态 key/IV，再包 5 字节前缀后用会话 key/IV |
| `ky` | RSA PKCS1v15 包裹会话 key\|\|IV |
| `sn` | MD5(canonical) 再与 ChaCha 混合；内嵌 `realtime_us % 1_000_000` |
| `nn` | 16 位小写 hex nonce |
| `ext` | 含 app_key 的紧凑 JSON |

`f7`：`canonical = f5||os||app_key||sdk||app_version`，偶数字节/奇数字节分两路 digest，再按 `second[first[i] & 0x1F]` 抽成 hex。salt 不进本文。

## JCE 边界

`mayyb.py` 只把 qimei36 token 编成 JCE（external id 17/19）。不含应用宝 AUTH/SEARCH 传输层。

源码里的 `libqimei.so+0x...` 是溯源注释，实现路径不读 so。

## 边界

- 换包先换 appKey / 证书材料，不要抄静态 AES
- `identity.json` 含 qimei/android_id/IMEI，只留 workspace
- 实现：`workspace/tencent-qimei-pure/source/`
