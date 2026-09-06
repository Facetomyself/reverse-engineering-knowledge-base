# 哔哩哔哩：buvid、deviceid 信封、fp_local 与 sign

> 来源: GitHub xfxfxiaofeng/reverseNotes
> 原始发布时间: 2025-06（观察版本 6.28.0 / 6.68.0 / 8.48.0）
> 归档日期: 2026-09-06
> 分类: mobile-app-reverse
>
> B 站 Android 设备身份不是单一哈希。`buvid` 是前缀加 MD5 抽位；`deviceid` 是随机 AES 密钥经 RSA-PKCS#1 v1.5 包裹后再 AES 加密注册明文；`fp_local` 本地拼 MD5+时间+随机+校验和，`fp_remote` 由 fingerprint 接口回写；`sign` 在 `libbili.so` JNI 里对已填 `ts` 的 map 做加盐 MD5。盐值只在截图，正文未导出。

## 案例边界

| 项 | 内容 |
|---|---|
| 包名 | `tv.danmaku.bili` |
| 观察版本 | buvid 6.68.0；deviceid 6.28.0；fp/sign 8.48.0 |
| Native | `libbili.so`（动态注册，`JNI_OnLoad` 偏移表） |
| 不收录 | 抓包 buvid 原值、完整 fingerprint POST、截图与 hook 脚本 |

## buvid

清空存储后值不变，按设备侧生成。定位到前缀 `XY` 后拼接：

1. 对内部 `strD` 做**大写**标准 MD5
2. 取摘要的第 2、12、22 个字符（作者按 0 起始描述为「2，12，22 部分」）
3. 拼到前缀后面

摘要不可逆，协议侧只需形状一致。作者用随机 UUID 走同一抽位也能过本地对照；是否被服务端当设备锚点，原文没有 `serverAccepted` 证据。

## deviceid

注册接口正文只有 `key` 与 `content` 关键：

```text
aes_key = random_hex_upper
key     = RSA-PKCS#1_v1.5(public, aes_key)   # 填充带随机，密文不可逐字节对照
content = AES(aes_key, register_plaintext)
```

服务端先私钥解开 `key`，再解 `content`，回写 `deviceid`。PKCS#1 v1.5 导致同一明文每次 `key` 不同，验收只能解回明文，不能比密文。

`register_plaintext` 由设备字段拼成后再 `getBytes`；具体字段表在截图，未进正文。

## fp_local / fp_remote

`fp_local` 本地闭合：

1. `MD5(buvid || 品牌 || 基带版本)` 转 hex
2. 当前 Unix 秒
3. 随机 8 字节 hex
4. 自定义十六进制校验和（作者已用 Python 对上）

`fp_remote` 形状相同，但不是本地算：`POST /x/resource/fingerprint`，带 `appkey`/`ts`/`sign` 与已有 `buvid`/`fp_local`。接口返回值再写入。不要把两次抓包的 `fp_remote` 当本地可复现。

## sign

Java 层 `s` 先写入 `ts`，再 JNI 进 `libbili.so`。SO 对 map 做完后 `NewObject` 带回字符串，作者把返回值认成 `sign`。核心计算在内部哈希例程：对照后是**标准 MD5 + 盐**，不是魔改压缩函数。盐的字节只出现在截图，本篇不写猜测值。

定位路径：`Map.put("sign")` 落空 → `StringBuilder` hook 看到 native 路径 → 调栈到 `s` → `JNI_OnLoad` 表 → 入参 map / 出参 sign。

## 边界

- `sign` 的盐、`deviceid` 明文表、`fp_local` 校验和公式细节以仓库截图为准，归档只锁结构。
- 8.48.0 的 `x-bili-*-bin` / protobuf 搜索接口原文只有截图，未闭合，不收录。
