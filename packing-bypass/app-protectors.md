# App 加固产品命中

> 来源: reverse_ENV App 主线（ciweimao / 豆瓣 / 起点）
> 原始发布时间: 2026-08-29
> 归档日期: 2026-08-29
> 分类: packing-bypass
>
> App 壳与 wrapper 的命中特征 → `protectorKind` → `apk_case.py next`。只做观察顺序，不替代当前样本的 DEX 计数、tombstone 和官方 live。

## 用途

指纹出现壳 so、Stub Application、NIS wrapper 或「业务类在 Manifest 里、jadx 里没有」时，先命中本表，再写 `contracts/auto-decision-facts.json` 的 `protectorKind`。不要用厂商名推断代际。

Web 风控产品走 `article/web-reverse/products.md`。本表只覆盖 Android 加固 / wrapper。

## 命中纪律

- marker 是 triage，不是版本证明。
- Application 是 stub/wrapper **且** 目标族拦截器已在明文 DEX → `stub-wrapper`，先官方 live / 纯算。
- 目标族不在静态 DEX → `whole-dex` 或方法抽取，再 dump。
- 映射到壳 so 不是 abort 帧；先 tombstone。
- debug 重签包不能当壳完整性单变量。

## 产品一览

| 产品 | 命中特征 | protectorKind | 下一步 |
|------|----------|---------------|--------|
| 360 Jiagu | `libjiagu` / `libjgdtc`、`StubApp` / `StubApplication` | 明文 DEX 多 → `stub-wrapper`；族缺失 → `whole-dex` | 起点样本曾是明文 DEX + panda 部分恢复。细节：[jiagu-bypass-analysis.md](./jiagu-bypass-analysis.md) |
| 腾讯 Legu | `libshell`、`TxAppEntry` | 族缺失才 `whole-dex` | decode 后看业务类是否已在 DEX |
| 梆梆 / SecNeo | `libSecShell` / `libDexHelper` / `libsecexe`、`apkwrapper` | 静态 DEX 很少 → `whole-dex` | 刺猬猫 2.9.365：包内 1 DEX，Pixel 6 panda 43 DEX。禁止 LDPlayer x86 so |
| 网易 NIS / 易盾加固 | `com.netease.nis.wrapper`、`libnesec.so` | 常为 `stub-wrapper` | 豆瓣 Frodo：20 DEX 明文拦截器 + `app_process32` canary。Frida 挂不上才考虑 Gadget 重签。对照泡泡易盾笔记 |
| 爱加密 Ijiami | `libexec`、`SuperApplication` | 族缺失 → `whole-dex` | 不要把 Application 名写成已脱壳 |
| 方法抽取 / 空方法体 | DEX 骨架在、方法体空 | `method-extract` | Pixel 6 `dump-device-dex.ps1 -Mode extract`；禁止 FART ROM |
| VMP / Dex2C | 方法跳解释器或 native 声明 | `vmp` / `dex2c` | `native-reverse`，不要反复 panda |

## 观察顺序

1. `fingerprint.sh`：壳 marker、DEX 数、ABI（32-bit-only 记 `apkAbi32Only`）。
2. `decode.ps1`：目标族拦截器/签名是否已在 jadx。
3. 进程能活则先该族官方 live；TLS 解不了用 `okhttp-plain.js`。
4. 闪退：tombstone pc/lr，不要把 `libnesec` 映射写成直接 abort。
5. 族缺失再 dump；设备目录有 DEX 仍要 panda，除非 `deviceDexComplete`。

## 使用边界

- 一份 panda `complete-enough` 不是完整脱壳。
- NIS 与 Web 易盾滑块不是同一产品面。
- Gadget 重签只在 `fridaAttachFailed` 且 `wantGadget` 时作为活取降级。
