# 升学e网通：共享 AES-ECB 与时间戳加盐 MD5

> 来源: GitHub xfxfxiaofeng/reverseNotes
> 原始发布时间: 2025-07（观察版本 11.2.1）
> 归档日期: 2026-09-06
> 分类: mobile-app-reverse
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

## sign

请求头 32 hex 大写，像 MD5。算法助手明文是「毫秒时间戳 + 12 hex 盐」：

```text
sign = upper(MD5( timestamp_ms + salt12 ))
```

盐来自该版本的 `EncryptUtils`，换包要重读，不当成永久常量。

## 登录字段

`userName`、`password`、`deviceToken`、`deviceName` 都是：

```text
AES/ECB/PKCS7Padding(shared_key, utf8(field)) → Base64
```

同一 `EncryptUtils.h/j` 入口。作者清数据后密文随明文变、key 不变，所以 key 是包内常量而不是会话派生。`deviceToken` 明文像 UUID。

共享 key 是该版本嵌入值，不写入本篇；复现时从 `EncryptUtils` 回读。

## 边界

- 响应体原文写「明文返回」，没有第二层业务信封。
- Flutter 其它接口是否另有签名，作者未建号，标未验证。
- x 加密 / Frida 检测只作为运行时前提，不归档绕过。
