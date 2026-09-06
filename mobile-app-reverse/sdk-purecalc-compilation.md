# App SDK 纯算落盘：顶象 / 数美 / Qimei / wtoken

> 来源: workspace 吸收 `storage/sdk-storage`（已删原件）
> 原始发布时间: 2026-08 至 2026-09 源码落盘
> 归档日期: 2026-09-06
> 分类: mobile-app-reverse
>
> 四份已落到 `workspace/` 的纯协议实现：海南航空 DXRisk `riskToken` 签发、小星空数美 `deviceprofile/v4`、腾讯 Qimei REGISTER、今彩萍乡 `wtoken`。本文只保留封装链和字段生命周期。密钥、真实画像、identity 和可直接打生产的脚本留在各 workspace `source/`。

## 收录说明

对应工作树：

| 工作树 | 主题 |
|--------|------|
| `workspace/hnair-dingxiang-risktoken` | 顶象 DXRisk |
| `workspace/xiaoxingkong-shumei-dpv4` | 数美 deviceprofile/v4 |
| `workspace/tencent-qimei-pure` | 腾讯 Qimei REGISTER |
| `workspace/jincai-pingxiang-wtoken` | 今彩萍乡 wtoken |

Shein 魔改 MD5、AppsFlyer `androidevent`、抖音 `a_bogus` 已有独立条目，不在本合集重复：

- [shein x-cs-random 魔改 MD5](../signature-algorithms/xfq-crypto-notes-compilation/xfq-20260414-01.md)
- [AppsFlyer PBKDF2+AES-CBC](./xfq-android-cases-compilation/xfq-20260523-01.md)
- [抖音 a_bogus 产品](../web-reverse/products/douyin-a-bogus.md)

`localReproduced` 只表示本仓能生成形状正确的载荷。`serverAccepted` 必须来自独立 TLS 业务 readback。

## 文章目录

| 工作树 | 文章 |
|--------|------|
| hnair-dingxiang-risktoken | [顶象 DXRisk riskToken 签发链](sdk-purecalc-compilation/hnair-dingxiang-risktoken.md) |
| xiaoxingkong-shumei-dpv4 | [数美 deviceprofile/v4 封装](sdk-purecalc-compilation/xiaoxingkong-shumei-dpv4.md) |
| tencent-qimei-pure | [腾讯 Qimei REGISTER](sdk-purecalc-compilation/tencent-qimei-register.md) |
| jincai-pingxiang-wtoken | [今彩萍乡 wtoken](sdk-purecalc-compilation/jincai-pingxiang-wtoken.md) |
