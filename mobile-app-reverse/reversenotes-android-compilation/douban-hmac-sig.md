# 豆瓣：HMAC-SHA1 sig、udid 与 MSA 定位

> 来源: GitHub xfxfxiaofeng/reverseNotes
> 原始发布时间: 2025-06（观察版本 7.98.0 / 对照 7.0.1）
> 归档日期: 2026-09-06
> 分类: mobile-app-reverse
>
> 豆瓣 `com.douban.frodo` 短评接口的 `sig` 先像 Base64，解码后 20 字节，是 HMAC-SHA1 再 URL-encode，不是裸 SHA1(时间戳)。7.98.0 对加密 hook 会在 `libmsaoaidsec.so` 加载期闪退，作者改用 7.0.1 对照把 HMAC 明文钩出来。`udid` 是对 UUID（或任意串）做 SHA1 再 hex。本篇只归档检测面定位和签名结构，不收录替换检测函数的脚本。

## 案例边界

| 项 | 内容 |
|---|---|
| 包名 | `com.douban.frodo` |
| 观察版本 | 7.98.0（有 MSA）；对照 7.0.1（可 hook Java Crypto） |
| 检测 SO | `libmsaoaidsec.so`（删掉则无法启动） |
| 不收录 | dlopen/constructor 替换脚本、滑块登录采集链、未脱敏 cookie |

## MSA 定位（不是绕过步骤）

7.98.0 上：改内存函数就闪退；不 hook 则正常。hook `dlopen` / `android_dlopen_ext` 时，`libmsaoaidsec.so` 有 enter 无 leave，说明检测发生在加载/构造期。SO 不能删。作者把后续工作放到 `call_constructors` / `JNI_OnLoad` 观察窗口。可复用的判断是：

- 先确认闪退是否对齐某个 SO 的 leave 缺失
- 再决定换低版本对照，还是只做静态/低版本 hook

不要把「换 7.0.1」写成 7.98.0 已过检测。

## sig

- 同时变的只有时间戳时，`sig` 跟着变
- Base64 可解码，20 字节 → HMAC-SHA1 摘要长度
- `SHA1(timestamp)` 对不上
- 7.98.0 上通用加密 hook 触发 MSA；7.0.1 上 hook `hmacsha1` 后，抓包里的 `sig` 实际是 **URL-encode 后的 Base64**
- 输入包括 path 的 encode、时间戳，以及 decode/encodePath 链上的另外两路字符串

HMAC key 与完整 canonical 串只在截图和加密网站对照里，正文没有导出。归档结论停在「HMAC-SHA1 → Base64 → URL-encode」，不编造 key。

## udid

形如 40 hex。不是 SharedPreferences 里现成的设备号：取不到历史值时用 UUID，再 SHA1，再 hex。作者认为服务端不会反查明文。换随机串再 SHA1 也能得到合法形状。

## 边界

- 7.98.0 的 `sig` 是否与 7.0.1 同一 canonical，原文用低版本 hook 反推，没有在 7.98.0 上独立闭合。
- 腾讯滑块登录、`authorization`、`spmid` 属于会话/业务链，不进本篇。
