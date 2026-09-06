# 陌陌 x-sign 第一参：AES-CBC 与 SHA1 拼接

> 来源: 知识星球：逆向学习交流（安居客/陌陌/马蜂窝附件笔记）
> 原始发布时间: 附件笔记（随 2025 安卓案例索引）
> 归档日期: 2026-09-06
> 分类: mobile-app-reverse
>
> 陌陌 `x-sign` 的第一参不是整包自定义算法。Java 入口 `com.immomo.momoenc.e.a` 先把一段 JSON 明文送进 `Coded.aesEncode`，底层落到 `libcoded.so` → `libmmcrypto.so` 的 AES-128-CBC；密文再 Base64。`x-sign` 本体另走标准 SHA1（明文后拼 8 字节）。本篇只记 hook 点、缓冲区形状和派生规则。不收录设备 JSON、主动调用字节数组和可直接跑的 invoke 脚本。

## 收录说明

原笔记写明：作者只闭合了 `x-sign` 第一参，其余同类 native 参数「套路一样、纯麻烦」。样本当时无抓包检测、无 Frida 检测。附件里的设备字段（`androidId` / `uid` / `mac` / `hw` 等）全部去掉。

## 案例边界

| 项 | 内容 |
|---|---|
| Java 入口 | `com.immomo.momoenc.e.a(byte[], Map, String) -> ?` |
| JNI 封装 | `com.immomo.momo.util.jni.Coded` |
| Native 名 | `a49kdEba83h(byte[] in, int inLen, byte[] keyMat, int keyMatLen, byte[] out) -> int` |
| 实现 SO | `libcoded_jni.so` 导入，`libcoded.so` 真正做 `aesEncode`；轮密钥/CBC 在 `libmmcrypto.so` |
| 加载名 | 正常路径依次 `mmcrypto` / `mmssl` / `coded` / `coded_jni`；调试开关会改走 `testcoded` |

`aesEncode` 在 `coded_jni` 里看起来是空桩，因为它是导入函数。按导入表进 `libcoded.so`，不要对着空实现猜 key 长度。

## Hook 窗口（只记点，不贴脚本）

| 点 | 观察样本 RVA | 参数形状 | 看什么 |
|---|---|---|---|
| Java `e.a` | — | `byte[]` 明文密文、`Map`、`String` | 确认 `x-sign` 第一参从这里出 |
| Java `Coded.aesEncode` / `a49kdEba83h` | — | `in, inLen, keyMat, keyMatLen, out` | `out` 有效长度是返回值 |
| `libcoded.so` `aesEncode` | `0x2EDC` | `arg0` 明文，`arg1` 明文长，`arg2` key 材料，`arg3` 材料长，`arg4` 输出 | 输出比内层 CBC 多 7 字节前缀 |
| `libcoded.so` `aesEncrypt` | `0x1C3C` | `arg0` 明文，`arg1` IV，`arg2` key，`arg3` 输出 | IV 在这一层生成/填入 |
| `libmmcrypto.so` `AES_set_encrypt_key` | `0x843A0` | `arg0` 初始 key，`arg1` key 位数，`arg2` 轮密钥 | 初始 key = `keyMat[0:16]` |
| `libmmcrypto.so` `AES_cbc_encrypt` | `0x85848` | `arg0` 明文，`arg1` 输出，`arg2` 长度，`arg3` 轮密钥，`arg4` IV | IV = `keyMat[16:32]` |

RVA 必须按当前 SO 重核。作者当时的 `onLeave` 经常打不出来，以 `onEnter` 缓冲和返回长度为准，不要把「没 leave」写成函数没跑完。

## 派生规则

```text
key     = keyMat[0:16]          # AES-128
iv      = SHA1(rand4)[:16]      # 4 字节伪随机再 SHA1，取前 16
cbc     = AES-128-CBC(plain, key, iv)
encoded = prefix7 || cbc        # aesEncode 比 aesEncrypt 多 7 字节
b64     = Base64(encoded)       # 笔记称 mzip，实为标准 Base64
```

`keyMat` 观察长度为 48：前 16 是 key，16–31 是填好的 IV，其余未参与 CBC。`rand4` 来自 `time(0)` + `srand` / `rand()+1`，作者认为可换成任意 4 字节。

## x-sign 本体与 map_id

`x-sign` 不是上面的 AES。扁平化函数在校验魔数后：

```text
SHA1( src[0:n] || uint64_from(a2) )
```

`a5 == -871603923` 时直接失败返回。其余同类 native 头作者未继续拆。

`map_id` 在 Java：

```text
t = now_ms % 1_000_000
if t < 100_000: t += 100_000
map_id = str(t) + str(randint(1000, 9999))
```

## 边界

- 第一参闭合不等于整个 `x-sign` 头已 `serverAccepted`。
- 不收录附件里的设备 JSON、主动调用字节数组和完整 Frida invoke。
- 换包先重核 `libcoded.so` / `libmmcrypto.so` 导出与 RVA，不要套观察偏移。
