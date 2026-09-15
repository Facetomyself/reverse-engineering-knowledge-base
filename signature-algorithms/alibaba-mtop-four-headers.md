# 阿里 SG 70102 四头纯算

> 来源: `workspace/alibaba-mtop-four-headers`（吸收 `storage/ali-algorithms.zip`）
> 原始发布时间: 2026-09-10
> 归档日期: 2026-09-15
> 分类: signature-algorithms
>
> 阿里 App 网关四头 `x-sign` / `x-sgext` / `x-mini-wua` / `x-umt` 可以纯算，但输入是一份会话画像加 `data2sign`，不是只喂请求体。一加捕获只是目前唯一 byte-exact 样本；算法层通用，不能凭空生成新会话。

## 适用边界

这是 App 网关头族，对应 `libsgmainso` 的 `SG doCommandNative 70102`。对照材料来自豌豆荚会话。与下面两条链 **不能互换**：

- Web H5 MTOP 的 query `sign`（`_m_h5_tk` MD5），见 [阿里 MTOP H5](../web-reverse/products/alibaba-mtop-h5.md)
- 未知 SG 版本上的默认路径：Hook `InnerSignImpl.getUnifiedSign` 当 RPC，见 [MTOP InnerSignImpl](../mobile-app-reverse/mtop-innersign-rpc.md)

出现这些标记时走本页：

- 请求头 `x-sign`、`x-sgext`、`x-mini-wua`、`x-umt`
- `data2sign` 形态 `{x_t}&{appkey}&{body_md5}`
- Native 侧 `doCommandNative` / `70102` / `libsgmainso`

`x-wua` / 完整 `wua` 不在本包。本页只闭合四头生成器，不是整包协议客户端。

## 四个文件

可执行实现留在工作树 `source/archives/`（restricted-local）。知识库只保留职责，不收录密钥和捕获原值。

| 文件 | 职责 |
|------|------|
| `des_ecb.py` | 标准 DES/ECB，8 字节块、无 padding。只给 `x-mini-wua` 加密那 15 个 8 字节块。跟设备无关。 |
| `four_headers.py` | 真正的四头算法。输入一份会话画像 + `data2sign`，输出 `x-sign` / `x-sgext` / `x-mini-wua` / `x-umt`。 |
| `sg_profile.py` | 会话画像。四头不是只靠 `data2sign` 就算出来的，还要 `key24` / `phase2` / `device_40`、调用计数、交替键 `k0`/`k1`、mini/sgext 模板词。`oneplus_call2()` 把一加那次真实捕获填成默认画像，方便直接验。 |
| `verify_four_headers.py` | 校验脚本。拿一加 g84 call2 当时抓到的四头真值，逐字节对一下，确认算法没写错。 |

## 为什么会出现一加

算法是通用的。目前唯一做过 byte-exact 验证的会话材料，就是那次一加捕获。没有这份样本，没法证明算出来的四头和真机一致。

它不能从任意新设备信息凭空生成一套全新会话。换设备 / 换轮次，得换 `SGProfile` 里的 `key24`、`phase2`、模板、计数这些输入；算法层不用改。

## 输入与输出

`data2sign`：

```text
{x_t}&{appkey}&{body_md5}
```

`SGProfile` 还要：

| 字段 | 角色 |
|------|------|
| `key24` | 24 字节会话材料 |
| `phase2` | 16 字节会话材料 |
| `device_40` | 40 字节设备/会话材料 |
| `call_cnt_word` / `cnt_b` | 调用计数；`advance()` 各加 1 |
| `k0` / `k1` | 交替 XOR 键 |
| mini / sgext 模板词与 ident | 展开 `x-mini-wua` / `x-sgext` 的词表、时间戳、控制字节 |

输出四个头：`x-sign`、`x-sgext`、`x-mini-wua`、`x-umt`。其中 `x-umt` 不吃 `data2sign`，只切会话材料。

## 算法骨架

```text
SGProfile + data2sign
  ├─ mini 模板 XOR → 130 字节明文
  │    └─ 16 个 8 字节块里跳过 1 块，其余 15 块标准 DES/ECB
  │    └─ 前缀 a + Base64 → x-mini-wua
  ├─ sgext 模板 XOR + ident 字符串 → 153 字节 → Base64 → x-sgext
  ├─ (key24 || phase2) 逐字节 XOR 0x27
  │    └─ 取 24 字节切片 Base64 → x-umt
  └─ state1 = bswap32(MD5(data2sign & mini && sgext))
       └─ SHA1(state1 || device_40 || 计数 || 常量 || key24^0x27||phase2)
       └─ 用 k0/k1 交替 XOR 后加版本前缀 Base64 → x-sign
```

`k0` / `k1` 不是随机数。X 链是 Park-Miller `16807` LCG（mod `2^31-1`）。B 链偶步 `*5+7`、奇步 `*3+0x13`。键值为 `((X | mask) + B) mod 0xFF`。

DES key 是 SG 侧固定 8 字节常量，不是机型字段，所以 `des_ecb.py` 与设备无关。

## 验证口径

- 离线：同一份一加 g84 call2 的 `data2sign` 与四头真值逐字节一致，才算 `localReproduced`
- 工作树 `scripts/run_smoke.py` 只报 OK / 长度，不打印头原值
- 没有独立 TLS 业务 readback，不能写 `serverAccepted`
- 把 call2 画像套到下一轮或另一台设备，对拍失败不能怪算法层

## 与 RPC 的关系

未知 SG 版本、没有会话画像、或只想先打通网关时，默认仍走 [InnerSignImpl 实例 RPC](../mobile-app-reverse/mtop-innersign-rpc.md)：Hook 一次抓住实例即摘，设备参数成套。本页是 70102 已闭合后的纯算路径，不是 RPC 的替代完成声明。

落地选型见 [平台签名落地方法](../web-reverse/sign-landing-methods.md)。

## 禁区

- 用 H5 `_m_h5_tk` MD5 `sign` 填 App 四头
- 只改 `Build.*` 或抖动真实指纹当新会话
- 把一加 `oneplus_call2()` 当通用设备生成器
- 把离线 OK 写成网关 `serverAccepted`
- 在知识库或 Git 里粘贴 `key24` / 捕获头 / DES key 原值

## 速查

| 主题 | 说明 |
|------|------|
| Native | `libsgmainso` `doCommandNative` `70102` |
| 头 | `x-sign` `x-sgext` `x-mini-wua` `x-umt` |
| 请求输入 | `{x_t}&{appkey}&{body_md5}` + 会话画像 |
| mini | 15×8 字节 DES/ECB，跳过 1 块 |
| 换机 | 换 `SGProfile`，不改算法文件 |
| 默认未知版本 | InnerSignImpl RPC |
