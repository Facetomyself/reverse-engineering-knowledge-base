---
schema_version: 2
id: mobile-app-reverse-reversenotes-android-compilation-ewt360-aes-md5
document_type: reference
scope:
  targets:
  - 升学e网通 login sign/encrypted fields
  client: Android/Flutter hybrid; login path uses Java
  version: 11.2.1 source report
  observed_at: unknown
sources:
- id: s1
  ref: null
  basis: source-report
  citation: GitHub xfxfxiaofeng/reverseNotes
  reason: 原归档明确记载出处，但未提供可定位的公开来源链接；本轮只保留来源自述。
source_completeness: unknown
modules:
- name: parameters
  anchor: ewt360-sign-derivation
  sources: [s1]
  basis: source-report
  limits: salt12 值未公开且版本绑定；shared_key 不纳入本文；本轮未计算 signer 或复算密文。
- name: validation
  anchor: ewt360-runtime-boundary
  sources: [s1]
  basis: source-report
  limits: 登录页 Java 路径不能外推到所有 Flutter 接口；其它签名与运行时检测均未验证。
tags: [aes-ecb, md5, login-sign, flutter-hybrid]
original_date: 2025-07（观察版本 11.2.1）
archived_date: '2026-09-06'
---

# 升学e网通：共享 AES-ECB 与时间戳加盐 MD5

<details data-kb-history="legacy-metadata">
<summary>历史来源记录（迁移前元数据，非当前真源）</summary>
> 来源: GitHub xfxfxiaofeng/reverseNotes
> 原始发布时间: 2025-07（观察版本 11.2.1）
> 归档日期: 2026-09-06
> 分类: mobile-app-reverse
</details>
>
> `升学e网通` 登录请求头签名是 `MD5(timestamp_ms || salt)` 再转大写；`userName` / `password` / `deviceToken` / `deviceName` 共用 `EncryptUtils` 里的同一组 `AES/ECB/PKCS7Padding`。作者写明还有 x 加密的 Frida 检测，且未建号，不知道 Flutter 侧是否另有参数。本篇只锁这两条算法，不写检测绕过。

## 案例边界

| 项 | 内容 |
|---|---|
| 应用 | 升学e网通 |
| 观察版本 | 11.2.1 |
| Java | `com.mistong.android.common.utils.m`（`EncryptUtils`） |
| 网关 | `GatewayClient` OkHttp interceptor 调 `EncryptUtils` 算 sign |
| 运行时 | Flutter 混合；登录页 Presenter 仍走 Java AES |

<a id="ewt360-sign-derivation"></a>
## sign

请求头 32 hex 大写，像 MD5。算法助手明文是「毫秒时间戳 + 12 hex 盐」：

```text
sign = upper(MD5( timestamp_ms + salt12 ))
```

盐来自该版本的 `EncryptUtils`，换包要重读，不当成永久常量。

<a id="ewt360-field-encryption"></a>
### 登录字段

`userName`、`password`、`deviceToken`、`deviceName` 都是：

```text
AES/ECB/PKCS7Padding(shared_key, utf8(field)) → Base64
```

同一 `EncryptUtils.h/j` 入口。作者清数据后密文随明文变、key 不变，所以 key 是包内常量而不是会话派生。`deviceToken` 明文像 UUID。

共享 key 是该版本嵌入值，不写入本篇；复现时从 `EncryptUtils` 回读。

<a id="ewt360-runtime-boundary"></a>
## 边界

- 响应体原文写「明文返回」，没有第二层业务信封。
- Flutter 其它接口是否另有签名，作者未建号，标未验证。
- x 加密 / Frida 检测只作为运行时前提，不归档绕过。

## 提炼说明（451）
retain 既有 e 网通 login reference。
key/salt 仍不写入。
本轮不另建卡。
