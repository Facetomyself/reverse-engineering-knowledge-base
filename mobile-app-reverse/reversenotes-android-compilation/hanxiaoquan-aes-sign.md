# 韩小圈：AES-CBC sign、uk 与响应 data

> 来源: GitHub xfxfxiaofeng/reverseNotes
> 原始发布时间: 2025-06（观察版本 6.5.3）
> 归档日期: 2026-09-06
> 分类: mobile-app-reverse
>
> `com.babycloud.hanju` 搜索接口请求头只有会变的 `sign` 与 `uk`。`sign` 是 AES/CBC/PKCS5，key/iv 由 `uid` 的 MD5 对半切开；`uk` 是同一 `uid` 再经另一组固定 AES 得到。清数据后三套值一起变。响应 `data` 的解密 key 是 `MD5(uid || 响应 ts)`。`uid` 生成式未还原，作者用 20 位 `[0-9A-Za-z]` 随机串做了服务端抽检。

## 案例边界

| 项 | 内容 |
|---|---|
| 包名 | `com.babycloud.hanju` |
| 观察版本 | 6.5.3 |
| Java | `SignUtil` / `AesUtil`（脱壳后仍有点不进去的类，靠调栈） |
| 调栈 | `AesUtil` → `z3.d.g(SignUtil)` → `BaseSignStringRequest.getHeaders` → Volley |
| 不收录 | 算法助手日志里的设备 JSON、具体 uid、hook 过检测步骤 |

## sign

算法助手对加密面自吐：`AES/CBC/PKCS5Padding`。同一安装期内 key/iv 稳定；`pm clear` 后 key、iv、明文里的 `uid` 一起换。

派生（作者用 MD5 对上）：

```text
h = MD5(uid)          # 32 hex
sign_key = h[:16]
sign_iv  = h[16:]
sign     = AES-CBC(sign_key, sign_iv, device_json)
```

`device_json` 含时间戳、机型、`uid`、包名等。不要把某次抓包的 key/iv 当全局常量。

## uk

`uk` 的 AES key/iv **固定**（与 `sign` 那套派生值不是同一对）。输入是当前 `uid`，输出 Base64。要求与 `sign` 使用同一 `uid`。

```text
uk = AES-CBC(fixed_key, fixed_iv, uid)
```

固定 key/iv 只在截图，正文未导出。

## uid

`o6.d.e` 取出后写入 JSON。脱壳不完整，作者未能 trace 出生成式。观察：定长 20，字符集 `[0-9A-Za-z]`。用随机串替换后，作者的一次发包没有报错；这只是抽检，不是生成算法已闭合。

## 响应 data

统一解密入口不在算法助手的标准 Java Crypto 列表里。hook 到 `w.a.a`：

```text
key = MD5(uid || response_ts)
plaintext = decrypt(data, key)
```

2025-07-17 作者补记：该版本已能脱壳，协议可离线；原文只示范 RPC 调原函数，Unidbg 留给读者。本篇不收录 RPC 脚本。

## 边界

- `uid` 生成、`uk` 固定密钥、解密原语（是否也是 AES-CBC）均未在正文写死。
- 清数据必须同时换 `sign`/`uk`/`uid`，只换其中一项会形状分裂。
