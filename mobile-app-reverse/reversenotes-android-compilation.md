# reverseNotes 早期安卓案例合集

> 来源: GitHub xfxfxiaofeng/reverseNotes（知识星球「逆向学习交流」索引所称 GitHub 小号）
> 原始发布时间: 2025-04 至 2025-07
> 归档日期: 2026-09-06
> 分类: mobile-app-reverse
>
> 星球索引 [安卓逆向实战案例 文章索引](https://articles.zsxq.com/id_dipgb89z5tns.html) 写明：2025 年 4–7 月 B 站案例曾放 GitHub，后因侵权风险下架，改存小号。本合集只吸收该仓库里作者原创、算法已闭合的笔记，隐去联系方式、付费课复刻、成人/政务样本和未脱敏抓包。

## 收录说明

对照仓库 `README` 与 `3-app完整案例/1-自己分析 & 粉丝投稿`。后续星球讲义已在 [xfq-android-cases-compilation](xfq-android-cases-compilation.md)，密码学讲义在 [xfq-crypto-notes-compilation](../signature-algorithms/xfq-crypto-notes-compilation.md)，不要把两套材料混成一篇。

未收录：

- 他人付费课程目录与复刻本
- 成人 App、新华社、税务局等敏感样本
- QQ / 微信联系方式、星球导流
- 完整 Frida 过检测脚本、采集器、`node_modules`
- 截图资产和 hook 日志原文

## 文章目录（4 篇）

| 日期 | 文章 |
|------|------|
| 2025-06 | [哔哩哔哩 buvid / deviceid / fp_local / sign](reversenotes-android-compilation/bilibili-device-sign.md) |
| 2025-06 | [韩小圈 AES-CBC sign / uk / 响应解密](reversenotes-android-compilation/hanxiaoquan-aes-sign.md) |
| 2025-06 | [豆瓣 HMAC-SHA1 sig 与 MSA 定位](reversenotes-android-compilation/douban-hmac-sig.md) |
| 2025-07 | [升学e网通 AES-ECB 字段与时间戳 MD5](reversenotes-android-compilation/ewt360-aes-md5.md) |

## 索引里提到但本批不收的条目

| 条目 | 原因 |
|------|------|
| 微博 aid / s | aid 的 `data` 是 AES+Base64，key 只在截图；轻享版 `s` 为 Rust SO 不可读，极速版落到 `libnative-lib.so` 的 `aa4`，闭合式不在正文 |
| 喜马拉雅登录 | 密码进控制流混淆 SO，作者停在 unidbg 意向；`signature` 只写「SHA1(请求体 dict)」 |
| 掌上商软 | Flutter，账密明文，`sign` 未闭合 |
| 好大夫 | Frida 反调试未解决 |
| 扫盲 / Java 基础 / unidbg 模板 | 与现有环境、xfq-unidbg 合集重复 |

语雀 `xiaofeng777/android_example` 书目录在 2026-09-06 已 404；已单独归档的公开页见 [菠萝包 SFSecurity](../signature-algorithms/boluobao-sfsecurity-trace.md) 与 [马蜂窝魔改 SHA1](../signature-algorithms/mafengwo-modified-sha1-trace.md)。
