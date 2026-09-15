# 数盟 libdu.so 指纹对照表（知乎 11.4.0）

> 来源: 知乎 11.4.0 / `libdu.so` SDK v8.4.0 独立分析（rizin + HAR；Pixel 5 实验室样本）
> 原始发布时间: 2026-09
> 归档日期: 2026-09-15
> 分类: 反检测/风控对抗 — 数盟设备指纹
>
> 数盟可信 ID 的注册面很薄：顶层大约 20–30 个 key，其中一个（`vB2`）再嵌套 100–200 个 key，注册包合计约 258 key。`d2api` 回 `cdd`，就是 App 业务后续用的 `x-ms-id`。对着 `libdu.so` 跑 native trace 就能把 key 对上。本文 366 行是把 daa / dcc2 / dai / audd 以及 SO 里其它采集点顺手编进来的全表，不是注册包字段数；个别分组还没完全钉死，但不妨碍理解签发路径。实验室 `android_id` / GAID / Widevine / MAC / IMSI 原值已截断。

## 怎么用这篇

不要被 366 行吓到。业务路径是：

```text
libdu.so 采集
  -> POST .../a/d2api/report  (XOR + zlib 信封)
    -> 响应 cdd
      -> 业务请求头 x-ms-id
```

注册本身就是那 20–30 个顶层 key 加上 `vB2` 里那一大团设备画像。拿到 `cdd` 之后，后续业务只带 `x-ms-id`。trace 入口：`0x2d860` 顶层、`0x1b9bc` 身份、`0x27148` `vB2`；`vB2` 字符串在 `0x543ec`。

偏移、字符串混淆和 HAR 样例只对这份知乎 11.4.0 / SDK v8.4.0 / Pixel 5 包。换 SO 先重核 RVA，不要把表当跨版本符号表。

相关地图：

| 文档 | 回答的问题 | 停在哪 |
|------|------------|--------|
| [协议准入四关](../mobile-app-reverse/protocol-admission-four-gates.md) | 为什么参数像了仍没有业务数据 | 四关并联；空壳不是 `serverAccepted` |
| [纯协议 SDK 重建](../mobile-app-reverse/pure-protocol-sdk-reconstruction.md) | 客户端目录、HAR、拦截器怎么建 | 可维护的协议客户端 |
| [设备指纹一致性建模](./device-fingerprint-consistency-modeling.md) | 字段之间为什么必须像同一台设备 | 联合分布 / 时间间隔 / 多次采集 |
| [ACE deviceUniqueId](./android-ace-deviceuniqueid.md) | Widevine 硬锚点 | TEE / RPMB，刷机改不掉 |
| **本文（数盟对照表）** | `libdu.so` 每个 key 从哪采、注册怎么换 `x-ms-id` | key 对照；不是改机手册 |

`hardware-fp` catalog 行仍只锁 SoC / GPU / 内存 / 屏幕。数盟还会采 Widevine `deviceUniqueId`（`6yY`）、目录 mtime、传感器列表、网卡和 Magisk/Xposed 位图，那些不在 catalog 行里。

## 1. 签发

```text
POST https://global-auni.checktrustworthiness.com/a/d2api/report?v=8.1&t=a&e=2
p = MD5("com.zhihu.android.37be8a1e.v8.4.0")
body = XOR(zlib(json), type6钥匙)
resp = XOR(json)
```

type6 钥匙（SO 字面量，信封用，不是用户凭据）：

```text
9+=%^8>:oi}12q5l;]q|{2f8v>?:[ss%^&fq5$baf7fq+=d-0
```

- `cdd` = 签发的票，业务侧就是 `x-ms-id`（88 位）；prefs 用 `MD5("cdd")` 缓存。
- 信封形态：`id36 + Base64(id36 + "shu")`。
- `AYk`：`SHA1(android_id 的 ascii 小写 hex).upper()[1:19]`，再切成 `g0:g2:g1`（6+6+6）。拿去数盟换票，不是业务 ID。
- `P1J`：服务端记下的设备号，首次等于 `AYk`，之后用 d2api 响应 `o_a`。

`vB2` 字符串混淆已解：`char+39`（`>0x7e` 则 `-95`）再 shuffle-1（从两头交错）。表里密文是 HAR 原样，明文是解开后的。空密文 = 这份 Pixel 5 包没带这个键，采集仍按代码写。

## 2. 口径：258 vs 366

| 口径 | 大约数量 | 含义 |
|------|----------|------|
| 注册顶层 | 20–30 key | d2api / dcc2 外壳：身份、SDK 版本、会话序号、`vB2` 容器 |
| `vB2` 嵌套 | 100–200 key（本包标注 169） | 设备画像本体 |
| 注册包合计 | 约 258 key | 顶层 + 嵌套；拿到 `cdd` 就算注册签发 |
| 本文对照表 | 366 key | 再加上 daa / dcc2 / dai / audd、SO 静态可见但本包 HAR 没出现的键、以及其它采集点 |

「出现」列：

| 标记 | 意思 |
|------|------|
| `vB2` | 嵌在 `vB2` 画像对象里（本包 HAR 有明文） |
| `d2api` | 注册请求/响应顶层 |
| `dcc2` | 另一路包装/query 面 |
| `daa` / `dai` / `audd` | 其它接口或本地配置面 |
| `so` | SO 里看得到采集，这份 HAR 没带（空则不上报，或权限/机型没命中） |

`rG*` 22 条是 `Build` 静态 String；`R*` 251 槽是 `__system_property_get`，空不上报。这两张枚举会和 `vB2` 里的同名属性重复采（例如 `R37` / `R3d` / `R41` / `Ra` / `R53` / `R63`）。属性名按下标走 `snprintf("R%x", i)`，不要用明文去猜。

## 3. 两张枚举

**rG\*** `0x2b70c` count=22：Build 静态 String。SERIAL BOARD BOOTLOADER CPU_ABI CPU_ABI2 DEVICE DISPLAY FINGERPRINT HARDWARE HOST ID MANUFACTURER MODEL PRODUCT TAGS USER TYPE BRAND SKU ODM_SKU SOC_MANUFACTURER SOC_MODEL。

**R\*** `0x2b8f4` count=251（`0x718f4` 返回 `0xfb`）：`0x49220(i)` 跳进属性 stub，`__system_property_get`，空不上报。键名 `snprintf("R%x", i)`。`i=0x28` 额外 `strstr fingerprint`。

## 4. 采集公式（这几条最容易看错）

- `XQp`：`atoi("%ld", clock_gettime_REALTIME.tv_nsec 两次差)`，负差绕 `1e8`
- `fxb`：`time()` 跳 ≥5s → 7；否则 `(usec_delta>4 ? 1000 : 20) * tm_hour + rand()%10`
- `eTk`：`atoi("%lld", stat(apk publicSourceDir).st_size)`
- `84j`：put 组调用 `popen("date")` 再 atoi；同函数入口还有 `getpid` 的 `%lld`
- `anY`：`sprintf("%d-%02d-%02d %02d:%02d:%02d", gmtime(abs(time-uptime)))` 开机 UTC
- `pEC` / `mEC` / `0q1`：配置 JSON 的 `pEventCode` / `mEventCode` / `dna`
- `JcY`：缓存的 `gettimeofday.tv_sec`
- `Mt4`：`0x27a0c` 那个 JSONObject
- `AYk`：`SHA1(android_id ascii 小写 hex).upper()[1:19]` → `g0:g2:g1`
- `6yY`：Widevine `MediaDrm.getPropertyByteArray("deviceUniqueId")` 再 `%02x`，不是 SHA-256
- `ne8` / `pT4`：`MD5(libdu.so 文件内容)`；maps 路径和 `nativeLibraryDir` 可能不是同一个 inode，HAR 里大小写和值可以不同

## 5. 每个 key

「含义」说这个字段是什么；「指纹数据 / 采集」来自 rizin。个别 so-only 键没有 HAR 样例，分组以 SO 邻近块为准，未完全钉死的见第 6 节。

| key | 含义 | 指纹数据 | 怎么采集 | 密文样例 | 明文 | 出现 |
|---|---|---|---|---|---|---|
| `rG0` | 硬件序列号（空则不上报） | Build.SERIAL | `0x2b70c` i=0 GetStaticObjectField(Build.SERIAL)，空跳过，0x543ec |  |  | so |
| `rG1` | 主板/平台代号 | Build.BOARD | `0x2b70c` i=1 GetStaticObjectField(Build.BOARD)，空跳过，0x543ec | "6:1-.," | "redfin" | vB2 |
| `rG10` | 构建类型 user/userdebug/eng | Build.TYPE | `0x2b70c` i=16 GetStaticObjectField(Build.TYPE)，空跳过，0x543ec | ":=-;" | "user" | vB2 |
| `rG11` | 品牌 | Build.BRAND | `0x2b70c` i=17 GetStaticObjectField(Build.BRAND)，空跳过，0x543ec | "-/47/7" | "google" | vB2 |
| `rG12` | SKU | Build.SKU | `0x2b70c` i=18 GetStaticObjectField(Build.SKU)，空跳过，0x543ec | "xn!kX" | "GD1YQ" | vB2 |
| `rG13` | ODM SKU | Build.ODM_SKU | `0x2b70c` i=19 GetStaticObjectField(Build.ODM_SKU)，空跳过，0x543ec | "xn!kX" | "GD1YQ" | vB2 |
| `rG14` | SoC 厂商 | Build.SOC_MANUFACTURER | `0x2b70c` i=20 GetStaticObjectField(Build.SOC_MANUFACTURER)，空跳过，0x543ec | "5x5=7)+4" | "Qualcomm" | vB2 |
| `rG15` | SoC 型号 | Build.SOC_MODEL | `0x2b70c` i=21 GetStaticObjectField(Build.SOC_MODEL)，空跳过，0x543ec | "Wz\\tY^" | "SM7250" | vB2 |
| `rG2` | bootloader 版本 | Build.BOOTLOADER | `0x2b70c` i=2 GetStaticObjectField(Build.BOOTLOADER)，空跳过，0x543ec | "X:_ZWTXW\\UZ[_T" | "r3-0.4-8351081" | vB2 |
| `rG3` | 主 CPU ABI | Build.CPU_ABI | `0x2b70c` i=3 GetStaticObjectField(Build.CPU_ABI)，空跳过，0x543ec | "))_:>5T][" | "arm64-v8a" | vB2 |
| `rG4` | 第二 ABI（空则不上报） | Build.CPU_ABI2 | `0x2b70c` i=4 GetStaticObjectField(Build.CPU_ABI2)，空跳过，0x543ec |  |  | so |
| `rG5` | 设备代号 | Build.DEVICE | `0x2b70c` i=5 GetStaticObjectField(Build.DEVICE)，空跳过，0x543ec | "6:1-.," | "redfin" | vB2 |
| `rG6` | 显示用版本号 DISPLAY | Build.DISPLAY | `0x2b70c` i=6 GetStaticObjectField(Build.DISPLAY)，空跳过，0x543ec | "XzhxUZZhWUWYUY\\WW^" | "SQ3A.220705.003.A1" | vB2 |
| `rG7` | 整机 ROM 指纹 | Build.FINGERPRINT | `0x2b70c` i=7 GetStaticObjectField(Build.FINGERPRINT)，空跳过，0x543ec | ";/A7-73/T4--;V):--4,-.:1V6:V-:;-=,a.]1Y6YaYX^Y]V_zVxXZ… | "google/redfin/redfin:12/SQ3A.220705.003.A1/8672226:use… | vB2 |
| `rG8` | 硬件名 | Build.HARDWARE | `0x2b70c` i=8 GetStaticObjectField(Build.HARDWARE)，空跳过，0x543ec | "6:1-.," | "redfin" | vB2 |
| `rG9` | 编译主机 HOST | Build.HOST | `0x2b70c` i=9 GetStaticObjectField(Build.HOST)，空跳过，0x543ec | "])]*Z.X)W:T5" | "abfarm-01366" | vB2 |
| `rGa` | 版本 ID | Build.ID | `0x2b70c` i=10 GetStaticObjectField(Build.ID)，空跳过，0x543ec | "XzhxUZZhWUWYUY\\WW^" | "SQ3A.220705.003.A1" | vB2 |
| `rGb` | 厂商名 | Build.MANUFACTURER | `0x2b70c` i=11 GetStaticObjectField(Build.MANUFACTURER)，空跳过，0x543ec | "-n47/7" | "Google" | vB2 |
| `rGc` | 型号 | Build.MODEL | `0x2b70c` i=12 GetStaticObjectField(Build.MODEL)，空跳过，0x543ec | "\\wG14@-" | "Pixel 5" | vB2 |
| `rGd` | 产品名 | Build.PRODUCT | `0x2b70c` i=13 GetStaticObjectField(Build.PRODUCT)，空跳过，0x543ec | "6:1-.," | "redfin" | vB2 |
| `rGe` | 构建标签 user/release-keys 等 | Build.TAGS | `0x2b70c` i=14 GetStaticObjectField(Build.TAGS)，空跳过，0x543ec | ";:A--43-T)-;" | "release-keys" | vB2 |
| `rGf` | 编译用户 | Build.USER | `0x2b70c` i=15 GetStaticObjectField(Build.USER)，空跳过，0x543ec | ",)461,=:*7T1," | "android-build" | vB2 |
| `R1e` | 主机名（net.hostname） | net.hostname | `0x2b8f4` i=0x1e：0x49220(30) 取属性名，__system_property_get，空跳过，0x543ec |  |  | so |
| `R1f` | SoC 平台代号（ro.board.platform） | ro.board.platform | `0x2b8f4` i=0x1f：0x49220(31) 取属性名，__system_property_get，空跳过，0x543ec | "74<1" | "lito" | vB2 |
| `R20` | bootloader 版本（ro.boot.bootloader） | ro.boot.bootloader | `0x2b8f4` i=0x20：0x49220(32) 取属性名，__system_property_get，空跳过，0x543ec | "X:_ZWTXW\\UZ[_T" | "r3-0.4-8351081" | vB2 |
| `R23` | 设备特征（ro.build.characteristics） | ro.build.characteristics | `0x2b8f4` i=0x23：0x49220(35) 取属性名，__system_property_get，空跳过，0x543ec | ",6:7);+," | "nosdcard" | vB2 |
| `R24` | 编译 UTC（ro.build.date.utc） | ro.build.date.utc | `0x2b8f4` i=0x24：0x49220(36) 取属性名，__system_property_get，空跳过，0x543ec | "_XZ]`\\\\[YX" | "1654125938" | vB2 |
| `R25` | 编译日期（ro.build.date） | ro.build.date | `0x2b8f4` i=0x25：0x49220(37) 取属性名，__system_property_get，空跳过，0x543ec | "Y~Y-W,YGGqj={6 \| GGG_XZGaY\\ZYa" | "Wed Jun  1 23:25:38 UTC 2022" | vB2 |
| `R26` | build description（ro.build.description） | ro.build.description | `0x2b8f4` i=0x26：0x49220(38) 取属性名，__system_property_get，空跳过，0x543ec | ";:A--,3.T1-6;T)=-;4--::GGX]YYGYzYx^Z]h_UGYXYhWU^ZWW\\W… | "redfin-user 12 SQ3A.220705.003.A1 8672226 release-keys" | vB2 |
| `R27` | 显示版本号（ro.build.display.id） | ro.build.display.id | `0x2b8f4` i=0x27：0x49220(39) 取属性名，__system_property_get，空跳过，0x543ec | "XzhxUZZhWUWYUY\\WW^" | "SQ3A.220705.003.A1" | vB2 |
| `R28` | 整机 ROM 指纹（ro.build.fingerprint） | ro.build.fingerprint | `0x2b8f4` i=0x28：0x49220(40) 取属性名，__system_property_get，空跳过，0x543ec；i=0x28 额外 strstr fingerprint | ";/A7-73/T4--;V):--4,-.:1V6:V-:;-=,a.]1Y6YaYX^Y]V_zVxXZ… | "google/redfin/redfin:12/SQ3A.220705.003.A1/8672226:use… | vB2 |
| `R2a` | 编译主机（ro.build.host） | ro.build.host | `0x2b8f4` i=0x2a：0x49220(42) 取属性名，__system_property_get，空跳过，0x543ec | "])]*Z.X)W:T5" | "abfarm-01366" | vB2 |
| `R2b` | 版本 ID（ro.build.id） | ro.build.id | `0x2b8f4` i=0x2b：0x49220(43) 取属性名，__system_property_get，空跳过，0x543ec | "XzhxUZZhWUWYUY\\WW^" | "SQ3A.220705.003.A1" | vB2 |
| `R2c` | 构建类型 user/userdebug/eng（ro.build.type） | ro.build.type | `0x2b8f4` i=0x2c：0x49220(44) 取属性名，__system_property_get，空跳过，0x543ec | ":=-;" | "user" | vB2 |
| `R2f` | OpenGL ES 版本号（ro.opengles.version） | ro.opengles.version | `0x2b8f4` i=0x2f：0x49220(47) 取属性名，__system_property_get，空跳过，0x543ec | "WXX`]]" | "196610" | vB2 |
| `R30` | 主板代号（ro.product.board） | ro.product.board | `0x2b8f4` i=0x30：0x49220(48) 取属性名，__system_property_get，空跳过，0x543ec | "6:1-.," | "redfin" | vB2 |
| `R31` | 品牌（ro.product.brand） | ro.product.brand | `0x2b8f4` i=0x31：0x49220(49) 取属性名，__system_property_get，空跳过，0x543ec | "-/47/7" | "google" | vB2 |
| `R33` | 主 ABI（ro.product.cpu.abi） | ro.product.cpu.abi | `0x2b8f4` i=0x33：0x49220(51) 取属性名，__system_property_get，空跳过，0x543ec | "))_:>5T][" | "arm64-v8a" | vB2 |
| `R34` | API 等级（ro.build.version.sdk） | ro.build.version.sdk | `0x2b8f4` i=0x34：0x49220(52) 取属性名，__system_property_get，空跳过，0x543ec | "YZ" | "32" | vB2 |
| `R37` | 厂商（ro.product.manufacturer） | ro.product.manufacturer | `0x2b8f4` i=0x37：0x49220(55) 取属性名，__system_property_get，空跳过，0x543ec；另有固定键 0x49d94 同属性 | "-n47/7" | "Google" | vB2 |
| `R38` | 电话类型（1=GSM 2=CDMA）（gsm.current.phone-type） | gsm.current.phone-type | `0x2b8f4` i=0x38：0x49220(56) 取属性名，__system_property_get，空跳过，0x543ec | "X" | "1" | vB2 |
| `R3a` | 蜂窝网络类型（gsm.network.type） | gsm.network.type | `0x2b8f4` i=0x3a：0x49220(58) 取属性名，__system_property_get，空跳过，0x543ec | "ls{" | "LTE" | vB2 |
| `R3d` | 型号（ro.product.model） | ro.product.model | `0x2b8f4` i=0x3d：0x49220(61) 取属性名，__system_property_get，空跳过，0x543ec；另有固定键 0x49e0c 同属性 | "\\wG14@-" | "Pixel 5" | vB2 |
| `R41` | 系统版本号（ro.build.version.release） | ro.build.version.release | `0x2b8f4` i=0x41：0x49220(65) 取属性名，__system_property_get，空跳过，0x543ec；另有固定键 0x49e84 同属性 | "YX" | "12" | vB2 |
| `R43` | Google 客户端 ID 基（ro.com.google.clientidbase） | ro.com.google.clientidbase | `0x2b8f4` i=0x43：0x49220(67) 取属性名，__system_property_get，空跳过，0x543ec | "-)46/,7:77/1T," | "android-google" | vB2 |
| `R44` | 设备代号（ro.product.device） | ro.product.device | `0x2b8f4` i=0x44：0x49220(68) 取属性名，__system_property_get，空跳过，0x543ec | "6:1-.," | "redfin" | vB2 |
| `R45` | 是否漫游（gsm.operator.isroaming） | gsm.operator.isroaming | `0x2b8f4` i=0x45：0x49220(69) 取属性名，__system_property_get，空跳过，0x543ec | "-.;)4" | "false" | vB2 |
| `R47` | ADB 是否需授权（ro.adb.secure） | ro.adb.secure | `0x2b8f4` i=0x47：0x49220(71) 取属性名，__system_property_get，空跳过，0x543ec | "X" | "1" | vB2 |
| `R4a` | 运营商定制标记（ro.carrier） | ro.carrier | `0x2b8f4` i=0x4a：0x49220(74) 取属性名，__system_property_get，空跳过，0x543ec | "6=?6736" | "unknown" | vB2 |
| `R4f` | secure 构建（1=user）（ro.secure） | ro.secure | `0x2b8f4` i=0x4f：0x49220(79) 取属性名，__system_property_get，空跳过，0x543ec | "X" | "1" | vB2 |
| `R53` | 是否可调试（ro.debuggable） | ro.debuggable | `0x2b8f4` i=0x53：0x49220(83) 取属性名，__system_property_get，空跳过，0x543ec；另有固定键 0x49dd0 同属性 | "W" | "0" | vB2 |
| `R55` | 时区（persist.sys.timezone） | persist.sys.timezone | `0x2b8f4` i=0x55：0x49220(85) 取属性名，__system_property_get，空跳过，0x543ec | "3h:57-!:'1?+-)uV" | "America/New_York" | vB2 |
| `R63` | adbd 服务状态（init.svc.adbd） | init.svc.adbd | `0x2b8f4` i=0x63：0x49220(99) 取属性名，__system_property_get，空跳过，0x543ec；另有固定键 0x49efc 同属性 | "/:6=166" | "running" | vB2 |
| `R64` | 硬件名（ro.hardware） | ro.hardware | `0x2b8f4` i=0x64：0x49220(100) 取属性名，__system_property_get，空跳过，0x543ec | "6:1-.," | "redfin" | vB2 |
| `R9c` | 启动块设备（UFS/eMMC 节点）（ro.boot.bootdevice） | ro.boot.bootdevice | `0x2b8f4` i=0x9c：0x49220(156) 取属性名，__system_property_get，空跳过，0x543ec | "+X0,;_.[=WUWW" | "1d84000.ufshc" | vB2 |
| `R9d` | NFC 是否已初始化（nfc.initialized） | nfc.initialized | `0x2b8f4` i=0x9d：0x49220(157) 取属性名，__system_property_get，空跳过，0x543ec | "-<=:" | "true" | vB2 |
| `R9e` | UFS 容量/厂商（ro.boot.hardware.ufs） | ro.boot.hardware.ufs | `0x2b8f4` i=0x9e：0x49220(158) 取属性名，__system_property_get，空跳过，0x543ec | "6X7Y:_+n1itS" | "128GB,Micron" | vB2 |
| `Ra` | SIM 状态（gsm.sim.state） | gsm.sim.state | `0x2b8f4` i=0xa：0x49220(10) 取属性名，__system_property_get，空跳过，0x543ec；另有固定键 0x49f38 同属性 | "{huilz" | "ABSENT" | vB2 |
| `Ra1` | ABI 列表（ro.product.cpu.abilist） | ro.product.cpu.abilist | `0x2b8f4` i=0xa1：0x49220(161) 取属性名，__system_property_get，空跳过，0x543ec | "1)*:)5-]5[:T)>S_))^S>)T:15*-)" | "arm64-v8a,armeabi-v7a,armeabi" | vB2 |
| `Ra2` | 上市时 API 等级（ro.product.first_api_level） | ro.product.first_api_level | `0x2b8f4` i=0xa2：0x49220(162) 取属性名，__system_property_get，空跳过，0x543ec | "WZ" | "30" | vB2 |
| `Ra4` | USB 控制器设备名（sys.usb.controller） | sys.usb.controller | `0x2b8f4` i=0xa4：0x49220(164) 取属性名，__system_property_get，空跳过，0x543ec | "Z)+]?W,WUWWW" | "a600000.dwc3" | vB2 |
| `Ra8` | 启动原因；同函数还取 ro.boot.boottime（ro.boot.bootreason） | ro.boot.bootreason/ro.boot.boottime | `0x2b8f4` i=0xa8：0x49220(168) 取属性名，__system_property_get，空跳过，0x543ec | "WWaiss{lmah^S[XS^X^iasis}ahZSX^S_XXias{lkav]SW`^ZSaYki… | "0BLE:74,1BLL:31,1BLE:607,2BLL:135,2BLE:614,SW:10024,KL… | vB2 |
| `Ra9` | 期望基带版本（ro.build.expect.baseband） | ro.build.expect.baseband | `0x2b8f4` i=0xa9：0x49220(169) 取属性名，__system_property_get，空跳过，0x543ec | "_/]^[Y`\\_W[T_WTWiYTWYYYT[YWY" | "g7250-00202-220422-B-8489468" | vB2 |
| `Raa` | 期望 bootloader（ro.build.expect.bootloader） | ro.build.expect.bootloader | `0x2b8f4` i=0xaa：0x49220(170) 取属性名，__system_property_get，空跳过，0x543ec | "X:_ZWTXW\\UZ[_T" | "r3-0.4-8351081" | vB2 |
| `Rab` | 默认闹钟铃声文件（ro.config.alarm_alert） | ro.config.alarm_alert | `0x2b8f4` i=0xab：0x49220(171) 取属性名，__system_property_get，空跳过，0x543ec | "/i/:71U//06<1'65:7" | "Bright_morning.ogg" | vB2 |
| `Rad` | 构建 flavor（ro.build.flavor） | ro.build.flavor | `0x2b8f4` i=0xad：0x49220(173) 取属性名，__system_property_get，空跳过，0x543ec | "::--;,=.T16" | "redfin-user" | vB2 |
| `Rb0` | preview SDK 指纹（ro.build.version.preview_sdk_fingerprint） | ro.build.version.preview_sdk_fingerprint | `0x2b8f4` i=0xb0：0x49220(176) 取属性名，__system_property_get，空跳过，0x543ec | "syl" | "syl" | vB2 |
| `Rb6` | CPU id；同函数还取 ro.boot.vbmeta.digest（ro.boot.cpuid） | ro.boot.cpuid/ro.boot.vbmeta.digest | `0x2b8f4` i=0xb6：0x49220(182) 取属性名，__system_property_get，空跳过，0x543ec | "]Y`Y_-Y+-W-W]_-+\\[X\\])+)^`-)]`+_)))\\,*W-Z_++^-Z]\\^… | "22ec008c45aa9a98a5be8ce67f8b12962531442537c30daac6e7c6… | vB2 |
| `Rbd` | 是否允许 OEM 解锁（sys.oem_unlock_allowed） | sys.oem_unlock_allowed | `0x2b8f4` i=0xbd：0x49220(189) 取属性名，__system_property_get，空跳过，0x543ec | "X" | "1" | vB2 |
| `Rc` | 基带版本（gsm.version.baseband） | gsm.version.baseband | `0x2b8f4` i=0xc：0x49220(12) 取属性名，__system_property_get，空跳过，0x543ec | "_/]^[Y`\\_W[T_WTWiYTWYYYT[YWY" | "g7250-00202-220422-B-8489468" | vB2 |
| `Rd` | RIL 实现串（gsm.version.ril-impl） | gsm.version.ril-impl | `0x2b8f4` i=0xd：0x49220(13) 取属性名，__system_property_get，空跳过，0x543ec | "WxU=X)G4s+p7y5G5" | "Qualcomm RIL 1.0" | vB2 |
| `Rd0` | ODM 品牌（ro.product.odm.brand） | ro.product.odm.brand | `0x2b8f4` i=0xd0：0x49220(208) 取属性名，__system_property_get，空跳过，0x543ec | "-/47/7" | "google" | vB2 |
| `Rd2` | setupwizard 企业模式（ro.setupwizard.enterprise_mode） | ro.setupwizard.enterprise_mode | `0x2b8f4` i=0xd2：0x49220(210) 取属性名，__system_property_get，空跳过，0x543ec | "X" | "1" | vB2 |
| `Ree` | AVB 验证状态（green/orange/yellow）（ro.boot.verifiedbootstate） | ro.boot.verifiedbootstate | `0x2b8f4` i=0xee：0x49220(238) 取属性名，__system_property_get，空跳过，0x543ec | "-7/:6)" | "orange" | vB2 |
| `Rf2` | vendor 分区 AVB 状态；同函数还取 ro.boot.vbmeta.device_state（vendor.boot.verifiedbootstate） | vendor.boot.verifiedbootstate/ro.boot.vbmeta.device_state | `0x2b8f4` i=0xf2：0x49220(242) 取属性名，__system_property_get，空跳过，0x543ec | ",=-634+7" | "unlocked" | vB2 |
| `Rf3` | fastboot flash 锁（0=未锁）（ro.boot.flash.locked） | ro.boot.flash.locked | `0x2b8f4` i=0xf3：0x49220(243) 取属性名，__system_property_get，空跳过，0x543ec | "W" | "0" | vB2 |
| `02P` | WiFi 扫描/网卡组里的字段 | 网卡组 | `0x1c7d8` 与 7S2 网卡列表、jK5 BSSID、JYD 速率同组 |  |  | so |
| `0q1` | 服务端配置 JSON 的 dna | JSONObject.opt("dna") | 0x858c0 opt("dna") → 0x56f28 GetStringUTFChars，写 .bss 0x114b00。顶层 0x85960 读出来 put |  |  | so |
| `0qI` | TelephonyManager.getHwNetworkType()，读不到则不上报 | getHwNetworkType()I | 0x37d44：先 checkPermission(READ_PHONE_STATE/ACCESS_COARSE_LOCATION)，再 getServiceState / getHwNetworkType。返回 -1 跳过 put。这份 0 | 0 | 0 | vB2 |
| `0qN` | 基站位置 CellLocation | getCellLocation | `0x2fe44` ACCESS_COARSE_LOCATION 后 TelephonyManager.getCellLocation，空不上报 |  |  | so |
| `0wL` | IPv4/配置块里的字段 | 配置块 | `0x1cce4` 与 wSK 同块 put |  |  | so |
| `1yT` | GNSS 芯片型号 getGnssHardwareModelName() | LocationManager.getGnssHardwareModelName | 0x35118 getSystemService("location") 再 getGnssHardwareModelName，空不上报 |  |  | so |
| `2cO` | 当前时间 gettimeofday（秒.小数） | gettimeofday | 与 qdK 同块 put（0x206d0） | "1788760276.381891538" | "1788760276.381891538" | vB2 |
| `2CP` | 数盟会话序号 na_seq_ni | na_seq_ni | `0x27b6c` vB2 组包时带上的会话序号，不是设备指纹 |  |  | so |
| `2Lp` | 蜂窝网络类型 getNetworkType() | TelephonyManager.getNetworkType()I | `0x37c9c` checkPermission(READ_PHONE_STATE) 后 getNetworkType，-1 不上报。这份 0 | 0 | 0 | vB2 |
| `2mV` | device_label 是否带上的 0/1 | 标志 | 邻近 o_a |  |  | so |
| `2us` | Settings 一包：开发者选项/超时等 | Settings.Global/Secure 若干 getInt | `0JF`=development_settings_enabled（0x3bd08）；同块还有 stay_on_while_plugged_in、usb_mass_storage_enabled。嵌套 JSON | {"0JF": "1", "TkG": "1", "9hx": "1", "DHU": "1", "WJr":… | {"0JF": "1", "TkG": "1", "9hx": "1", "DHU": "1", "WJr":… | vB2 |
| `2wp` | 运营商数字代码 getNetworkOperator() | TelephonyManager.getNetworkOperator | 0x37954 先 getPhoneType 再 getNetworkOperator。空不上报 |  |  | so |
| `3J5` | IMEI getImei() | TelephonyManager.getImei | 0x360f4 READ_PHONE_STATE 后 getImei。不是 getPhoneType |  |  | so |
| `3k2` | 数盟会话序号 na_rseq_ni | na_rseq_ni | `0x27c18` vB2 组包会话序号 |  |  | so |
| `3Ky` | 模拟器属性探测汇总 | 蓝叠/夜神/逍遥/Droid4X 簇 | `0x27810` put，邻 AJU/ySX/GQd/wv6/OQE/fez |  |  | so |
| `3mS` | 数盟 SDK 版本 v8.4.0 | v8.4.0 | SO 字面量 v8.4.0 | "v8.4.0" | "v8.4.0" | dcc2 |
| `3pD` | Settings/config JSON 块字段 | 2us 配置 | `0x2ccb8` 与 2us Settings 包、G8U 同 JSONObject |  |  | so |
| `3q2` | CPU：/proc/cpuinfo + max_freq + 核数 | /proc/cpuinfo 对象 | 读 /proc/cpuinfo（GOT 0xbe5c0 @ 0x441f4）+ cpuinfo_max_freq，塞进 JSONObject 键 3q2 | {"7xr": "AArch64 Processor rev 14 (aarch64)", "I1g": "7… | {"7xr": "AArch64 Processor rev 14 (aarch64)", "I1g": "7… | vB2 |
| `41j` | filesDir 下 _system.dat 内容 | _system.dat | 0x18b28 与 iod/PuV/NG0/pids.o 同块读 filesDir 本地文件 |  |  | so |
| `43c` | HTTP 代理主机 | http.proxyHost | `0x3b6b8` System.getProperty("http.proxyHost")，空不上报 |  |  | so |
| `4B0` | 是否存在 /su | access(/su) | access("/su")（0x2bd7c） |  |  | so |
| `4VP` | SIM 卡状态 getSimState() | TelephonyManager.getSimState()I | 0x35ec0 getSimState。1=ABSENT，和 Ra=ABSENT 对得上 | 1 | 1 | vB2 |
| `59p` | WiFi MLO 链路列表 | getAffiliatedMloLinks / getAssociatedMloLinks | `0x3d7e4` WifiInfo 的 MLO API（WiFi 7），空不上报 |  |  | so |
| `5Nc` | 当前默认 Launcher 包名 | 混淆长串 | put 在 G8U（meminfo/StatFs）旁 0x25444 | "-+57750UU/:7-70/+46-=U))46;,=:@7-16,UU;)88" | "com.google.android.apps.nexuslauncher.home" | vB2 |
| `5y9` | 改机/Hook 包是否装了 | PackageManager 扫包 | 0x477a0：com.yztc.studio.plugin / apk008 / uwish / xposed.hook.model / apkhook 等，命中计数。这份 0 | 0 | 0 | vB2 |
| `67I` | 系统属性 ro.boot.deviceid | ro.boot.deviceid | 0x49a78 XOR 出属性名再 __system_property_get。和 selinux 只是邻块 |  |  | so |
| `6x6` | MD5(/vendor/firmware 下文件名拼接) | MD5(strcat(d_name…)) | 0x4242c：0x5683c(w3=7) 解出 `/vendor/firmware`，同样 strcat 文件名，0x4ccf4 MD5。put 0x2538c | "`\\W]`Zmm_^\\^j\\YY]jm\\XW[j^`miYWl`" | "563F7752C50C9B09E2F741F62C58F909" | vB2 |
| `6yY` | Widevine deviceUniqueId 的 hex | MediaDrm.getPropertyByteArray("deviceUniqueId") 再 %02x | 0x40864：UUID.fromString(edef8ba9-79d6-4ace-a3c8-27dcd51d21ed) → new MediaDrm → getPropertyByteArray("deviceUniqueId") → 逐字节 sprintf("%02x")。不是 SHA-256。put 0x540c0 | "cb04…" | "cb04…" | vB2 |
| `7CS` | daa 接口会话序号 aa_seq/aa_rseq | aa_seq | `0x2d3e4` daa 组包序号，不是设备指纹 |  |  | so |
| `7Gf` | Settings.Secure（无障碍/音效/息屏） | sound_effects_enabled / screen_off_timeout / accessibility_enabled | `0x3c02c` Settings$Secure.getInt，put `0x2dbd8`/`0x3c02c` |  |  | so |
| `7Hz` | uid,unix 时间 | 短 hex 混淆 | vB2 哈希类字段 | "WYW[…" | "2440…" | vB2 |
| `7Oc` | 数盟 SDK 额外版本字面量 | 字面量 | 与 3mS/AAA 一起组，不是采集指纹 |  |  | so |
| `7S2` | 网卡列表（名字/地址/DNS） | NetworkInterface | 枚举网卡填 txo/Zne/MCN。明文是 wlan0 不是安装列表；getInstalledPackages 是邻 GOT | {"0": {"txo": "W?64)", "Zne": "%#Z.Y-V__W_aXaUY^_Z,UY_a… | {"0": {"txo": "wlan0", "Zne": "[fe80::28d2:d9ff:fe9b:1b… | vB2 |
| `84j` | atoi(popen("date") 的 stdout) | date 输出 atoi | vB2 时间函数 0x21284：栈槽 84j，atoi(x22) putInt。x22 来自同组 0x458e0：popen("date","r")、fread 0x400。ctime 无前导数字时 atoi=0。同函数入口 0x45994 是 sprintf("%lld",getpid())，这份 HAR=1004 和 pid 同量级 | 1004 | 1004 | vB2 |
| `8ET` | 主板;基带版本 拼串 | BOARD + 基带 | 明文 `redfin;MPSS.HI.2.0.c8-…`。enabled_accessibility_services 是邻块 Settings，不是这个值 | "b:Z-U,].`1W6_b_t[wUzXzTUrojphUwY'UuWlUn+'_uThWwWpYhWzY… | "redfin;MPSS.HI.2.0.c8-00202-SAIPAN_GEN_PACK-1.488096.3… | vB2 |
| `90P` | Magisk/LSPosed/EdXposed 路径位图 | access() 一串 magisk/riru/lsposed 路径 | 0x47dd4：/sbin/.magisk、/sbin/magisk、/system/bin/magisk、riru_lsposed、zygisk_lsposed、taichi、dreamland、XposedBridge.jar 等。拼成两位数字。这份 vB2=00 | "WW" | "00" | vB2 |
| `9be` | SELinux enforce，读不到为 -1 | /sys/fs/selinux/enforce | fopen 该节点，读不到为 -1（0x1bea4） | -1 | -1 | vB2 |
| `9mU` | 数盟会话序号 na_rseq_ni | na_rseq_ni | `0x27bfc` vB2 组包会话序号 |  |  | so |
| `9N2` | 移动流量 rx,tx 字节 | TrafficStats.getMobileRxBytes/TxBytes | 0x3d234 sprintf("%ld,%ld", getMobileRxBytes, getMobileTxBytes)。这份 0,0=没走蜂窝 | "WWS" | "0,0" | vB2 |
| `9P6` | ARP 表：IP,MAC 分号分隔 | 长串 | put 在 Ufi 旁 0x1cadc，像安装列表或 maps | "bX^^…" | "172.…" | vB2 |
| `9pz` | 是否命中随机 MAC 占位串 | 02:00:00:0k:0f:00 | 0x17de4 拿 MAC 去比占位模板。随机化 MAC 会碰上 | "883kf" | "pD?kp" | vB2 |
| `9qW` | 扫到的 su 路径个数 | 扫 su 个数 | 扫 /system/bin/su 等，HAR=8 | 8 | 8 | dai |
| `9WL` | 虚拟机属性 vmprop.androidid | vmprop.androidid | 0x49bd4 XOR 出 vmprop.androidid 再 getprop |  |  | so |
| `AAA` | 协议小版本 v1.0 | v1.0 | SO 字面量 | "v1.0" | "v1.0" | dcc2 |
| `aart` | 数盟 prefs 时间戳 aart | prefs aart | 0x1be54 0x55708 读 nart/nirt/aart 三个 prefs 键之一 |  |  | so |
| `aFw` | stat(/data/system) 两个 timespec | %ld.%ld,%ld.%ld | 0x42b54 plaintext `/data/system`，stat，sprintf 两个 timespec。和 Bos/IJK/QNw/IAI 同格式 | "XYX[^[^WZX]Z[XZ_ZUU``[]]Y]W]]^^Y_W_`^SX" | "24401318.946667209,1788760269.334637711" | vB2 |
| `AJU` | 模拟器 phone.mechineid | phone.mechineid | `0x49430` 栈上 XOR 解密属性名再 __system_property_get/access |  |  | so |
| `anY` | 开机时刻 UTC 日期时间串 | %d-%02d-%02d %02d:%02d:%02d | 0x45758：atol(/proc/uptime 第一字段)，abs(time()-uptime)，gmtime，sprintf("%d-%02d-%02d %02d:%02d:%02d", year+1900,mon+1,mday,hour,min,sec)。putStr 0x540c0。这份 HAR 明文是 "5052"（4 位数字），和完整日期串不是同一次 x22 | "5052" | "5052" | vB2 |
| `arp` | JSONObject 解析后的 config 对象 | JSONObject | 0x2cc48 用 JSONObject.<init>(String) 解析 2us 那包 Settings |  |  | so |
| `awt` | AUTH_APP_INFO 配置串 | AUTH_APP_INFO | 0x2ce44 组 daa 时带 prefs/配置，邻 ciD、MASK_IMSI_KEY、boot_uuid |  |  | so |
| `AYk` | 用 android_id 做的设备索引，拿去数盟换票 | android_id 的 SHA1 重排 | Settings.Secure.ANDROID_ID → SHA1(ascii小写hex).upper()[1:19] 排 g0:g2:g1（0x1841c） | "XX:XX:XX" | "XX:XX:XX" | dcc2 |
| `az6` | 红手指 redf.mathinecode / ro.boot.deviceid | redf.mathinecode；ro.boot.deviceid | `0x4999c` XOR `redf.mathinecode`；`0x49a78` XOR `ro.boot.deviceid`，再 getprop |  |  | so |
| `B1q` | gettimeofday/clock 算出的整型 | gettimeofday | 0x22f30 gettimeofday + 0x84000。这份 1190，不是 selinux | 1190 | 1190 | vB2 |
| `B3k` | 开机起 elapsedRealtime | elapsedRealtime | SystemClock.elapsedRealtime | 443 | 443 | d2api |
| `B5W` | 荣耀广告 ID | hrid | 0x50d20 hrid |  |  | so |
| `B7G` | 邻区基站列表 getNeighboringCellInfo() | getNeighboringCellInfo | 0x30f00 ACCESS_COARSE_LOCATION 后 TelephonyManager.getNeighboringCellInfo | {} | {} | vB2 |
| `BAj` | 移动流量 rx,tx | TrafficStats | getMobileRxBytes/TxBytes |  |  | so |
| `BBB` | 协议小版本 v1.0 | v1.0 | SO 字面量 | "v1.0" | "v1.0" | dcc2 |
| `bf7` | 运营商数字代码 getNetworkOperator() | getNetworkOperator | 0x379fc getNetworkOperator。和 2wp 同源 API，put 点不同 | "0" | "0" | vB2 |
| `Blv` | 是否漫游 | isNetworkRoaming | TelephonyManager.isNetworkRoaming |  |  | so |
| `Bn2` | 总流量 rx,tx 字节 TrafficStats | TrafficStats | getTotalRxBytes/TxBytes | "ZZ]Y]Y^\\W[Z[`_S_W" | "322544880,9307663" | vB2 |
| `Bos` | lstat(/sdcard/Android/data/.nomedia) 两个 timespec | %ld.%ld,%ld.%ld | 0x426c4 XOR 出路径（偶 0x9d 奇 0x9b，倒序），0x11b20 lstat，sprintf 两个 timespec | "^X^^__Z_WZW\\\\X[\\[]U``U][\\[X\\\\WZW_Z__^^X^S" | "1788351569.445003877,1788351569.445003877" | vB2 |
| `box` | 空 JSON 占位 | {} | daa 空 JSONObject | {} | {} | daa |
| `c2O` | adb 开关 Settings.Global.adb_enabled | adb_enabled | 0x3bb68 Settings.Global.getInt/getString("adb_enabled")，0x1db88 putStr | "1" | "1" | vB2 |
| `cdd` | 数盟签发的 x-ms-id（88 位） | 88 位票 | d2api 响应 cdd，prefs MD5("cdd") 缓存 |  |  | so |
| `cfx` | 模拟器共享目录是否存在 | access() 模拟器 share 路径 | 0x48cb0：/mnt/shared/Sharefolder、/tiantian.conf、/mumu_hardware.conf、/Andy.conf、/mnt/windows/BstSharedFolder、/bst.conf、/ld.conf。命中计数。这份 0 | 0 | 0 | vB2 |
| `ciD` | AUTH_APP_INFO 配置 | AUTH_APP_INFO | 0x2ce74 与 awt 同段，prefs 键 AUTH_APP_INFO |  |  | so |
| `Cl5` | 本应用 base.apk 路径 | 长串 | cmP 存储块 0x2317c | "3V8,…" | "/data/app/~~…/com.zhihu.android…" | vB2 |
| `cmP` | MemTotal 字节 | meminfo 派生 | 邻近 /proc/meminfo 采集块 | 157156023 | 157156023 | vB2 |
| `CnM` | ttopenadsdk did | ttopenadsdk did | SharedPreferences |  |  | so |
| `CQH` | vivo 广告 ID | voaid | 0x50db8 |  |  | so |
| `CVi` | 魅族广告 ID | mzaid | 0x50bf0 |  |  | so |
| `CzO` | HTTP 代理端口 | http.proxyPort | 0x3b794 System.getProperty("http.proxyPort")。43c 才是 proxyHost |  |  | so |
| `d3a` | 网卡列表是否采到的 0/1 | 字面量 0/1 | 0x2d1cc 7S2 之后 put "1" 或 "0" | "0" | "0" | audd |
| `daa` | 已保存 WiFi 配置数 | WifiManager.getConfiguredNetworks().size | `0x3f6b0` 需 ACCESS_FINE_LOCATION；put `0x2cb10` |  |  | so |
| `DaF` | 系统服务探测（环境/模拟器） | ss3-4 运行时解密的服务名 | helper `0x3a89c` getSystemService + getId()I，邻 /su |  |  | so |
| `Db2` | 数盟 native 初始化写入的模式整型 | .data+0x938 | 0x82fc8 读缓存；唯一写入 0x7c08c（sem_init 那条 init 路径，w0=结构体+0x18）。这份 2 | 2 | 2 | daa |
| `Dg1` | 扫描到的 AP 个数 | getScanResults().size | WifiManager.getScanResults（GOT 0xbd9d0） |  |  | so |
| `dga` | 虚拟机属性 vmprop.ip | vmprop.ip | 0x49cb0 XOR 出 vmprop.ip 再 getprop |  |  | so |
| `dHR` | 努比亚 OAID 通道 nbaid | nbaid | 0x50c3c 厂商广告 ID 通道，内部名 nbaid |  |  | so |
| `dj3` | SIM ICCID getIccId() | SubscriptionInfo.getIccId | 0x36fdc READ_PHONE_STATE → getDefaultSubscriptionId → getActiveSubscriptionInfo → getIccId |  |  | so |
| `dLH` | boot_uuid（prefs） | boot_uuid | prefs boot_uuid / MASK_IMSI_KEY | "\|}!N…" | "\|}!N…" | audd |
| `dTr` | 一加广告 ID | onepid | 0x50ee8 |  |  | so |
| `DTV` | 系统服务探测（环境/模拟器） | ss3-6 ss3-1 | helper `0x3a7e8` getSystemService |  |  | so |
| `DUv` | 应用包名 | getPackageName | Context.getPackageName | "com.zhihu.android" | "com.zhihu.android" | dcc2 |
| `DVp` | 默认网关 IPv4 | 混淆串 | daa 明文 jjgpoklggjq；邻近 TrafficStats | "XXU^…" | "172.…" | vB2 |
| `DxD` | daa 会话序号 aa_seq | aa_seq | 0x2d448 0x55708 读 aa_rseq/aa_seq，不是设备指纹 |  |  | so |
| `e4U` | 百度 Settings 混淆键 mqBRboGZkQPcAkyk | mqBRboGZkQPcAkyk | 0x3b40c Settings 读百度存的设备 ID 键 |  |  | so |
| `E7R` | vB2 组包时 JSONObject.remove 的键 | JSONObject.remove | 0x27c1c/0x28874 组包维护字段，不是采集指纹 |  |  | so |
| `eBI` | 同 nctl 的 2 | 标志 | 邻近 cdd | "2" | "2" | d2api |
| `ED2` | 这次请求生成的 UUID | UUID | UUID.randomUUID() | "Z]))…" | "6a60…" | vB2 |
| `EIx` | prefs rec_stats | prefs rec_stats | `0x2c784` helper `0x11680`，邻 fzN/OEu |  |  | so |
| `Ell` | 本地文件 /ee02ad45 | /ee02ad45 | 0x42070 读该路径 |  |  | so |
| `eTk` | APK 文件大小 st_size | stat(publicSourceDir).st_size | 0x230d0 bl 0x51194：0x50a90 ApplicationInfo.publicSourceDir，stat，sprintf("%lld", st_size)（statbuf+0x30），atoi putInt。stat 失败这份就是 0 | 0 | 0 | vB2 |
| `EV2` | versionName | versionName | PackageInfo.versionName | "11.4.0" | "11.4.0" | dcc2 |
| `F95` | 该 helper 直接返回空 | NULL | 0x3bc20 `mov x0,xzr; ret`，当前 SDK 不上报 |  |  | so |
| `F9K` | 百度设备 ID com.baidu.deviceid | com.baidu.deviceid | 0x3b444 Settings 键 dxCRMxhQkdGePGnp / com.baidu.deviceid |  |  | so |
| `fEs` | OPPO 安全 UUID op_security_uuid | op_security_uuid | 0x3bc28 Settings 读 op_security_uuid |  |  | so |
| `fez` | 逍遥 ro.microvirt.hmac | ro.microvirt.hmac | 0x4981c 解密 ro.microvirt.hmac |  |  | so |
| `fKe` | Build.SUPPORTED_ABIS | SUPPORTED_ABIS | Build.SUPPORTED_ABIS 0x3a550 | "S)1:*5)]-[5T:>)_S))S^)>:T51-*)" | "arm64-v8a,armeabi-v7a,armeabi," | vB2 |
| `foO` | android_id | 混淆串 | mIS boot_id 旁 0x1cd4c | "___[…" | "8432…" | vB2 |
| `fPV` | 国家,语言 Locale | Locale | Locale.getCountry+getLanguage，HAR=US,en | "US,en" | "US,en" | vB2 |
| `fV5` | 华硕 OAID 通道 asaid | asaid | 0x50b58 厂商广告 ID，内部名 asaid |  |  | so |
| `fxb` | 反调试时间指纹：scale*tm_hour + rand%10 | (20或1000)*tm_hour + rand()%10 | 0x25ee8：gettimeofday、time、localtime，ldr w24,[tm,#8] 才是 hour。再用两次 gettimeofday 测延迟：time() 跳变≥5s 则固定 7；否则 (usec差>4?1000:20)*hour + rand%10，.bss 0x114944 控制 ±1。Pxm hour=1 时 20*1+4=24，对得上这份 HAR | 24 | 24 | vB2 |
| `fzN` | prefs ss2 | getSharedPreferences("ss2") | 0x2c6dc 读 ss2，这份可能是 "0" |  |  | so |
| `G6o` | device_label 包名.后缀 | 包名.后缀 | {package}.54bc01a66a | 0 | 0 | dcc2 |
| `G8U` | 内存 KB + 数据分区 GB（meminfo/StatFs） | meminfo/StatFs | /proc/meminfo + android.os.StatFs（GOT 0xbf720/0xbd948） | {"MYA": "Y^\\]^Z\\[ZWXYS_", "H4S": "]X`WY`^U[X`WU^Y[WWX… | {"MYA": "7634028,135752", "H4S": "109.107407,102.947296… | vB2 |
| `gaR` | daa 标志 | "i" | daa | "i" | "i" | daa |
| `gEd` | MD5(libreference-ril.so 文件内容)，读不到则 MD5(libc.so) | MD5(file bytes) hex %02x | 0x424ac：fopen(/system/lib/libreference-ril.so,"rb")，0x4cd2c 整文件 MD5（0x73a18 Init，分块 fread 0x400，%02x×16）。空则同样哈希 /system/lib/libc.so。不是 SHA-256（32 hex=MD5） | "8a94f33cb547655db45aca7fdf17e7e7" | "8a94f33cb547655db45aca7fdf17e7e7" | vB2 |
| `go9` | 小米健康 ID mi_health_id | mi_health_id | 0x3bbd8 Settings.Global.getString("mi_health_id") |  |  | so |
| `GQd` | 夜神 persist.nox.device_id / sys.mac.address | persist.nox.device_id；另 sys.mac.address | `0x495d4` XOR persist.nox.device_id；`0x496a8` XOR sys.mac.address |  |  | so |
| `GVp` | 渠道号 | DefaultChannel | HAR=360 | "360" | "360" | daa |
| `h6Z` | 应用显示名 | getApplicationLabel | PackageManager.getApplicationLabel | "知乎" | "知乎" | daa |
| `h8h` | longVersionCode | getLongVersionCode | PackageInfo.getLongVersionCode |  |  | so |
| `HAG` | 数盟 RSA 公钥（校/加密配置） | X.509 公钥 | SO 硬编码 1024-bit，用来校验/加密配置 | "MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBANc7lrAPh8Vki2+Gf9KQxU… | "MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBANc7lrAPh8Vki2+Gf9KQxU… | d2api |
| `hd7` | vB2 组包用的 SharedPreferences 句柄 | getSharedPreferences | 0x27c38/0x2a548 组包字段，不是传感器 |  |  | so |
| `hdw` | 华为 pps_oaid | pps_oaid | 0x3ba94 |  |  | so |
| `hgI` | 数盟 ss3-11 服务探测 | ss3-11 | 0x3a734 getSystemService 的混淆服务名 ss3-11 |  |  | so |
| `hH1` | 蓝牙地址 Settings.Secure.bluetooth_address | bluetooth_address | 0x3b8d8 Settings$Secure.getString("bluetooth_address")。不是 SQLite |  |  | so |
| `hiK` | 厂商 OAID 通道 pzid | pzid | 0x510b0 内部名 pzid |  |  | so |
| `hJ7` | 华为广告 ID | hwaid | 0x50cd4 字符串 hwaid |  |  | so |
| `hpJ` | 本地缓存的 x-ms-id | 缓存 smid | prefs 已有票，没有则空（邻近 xmid 字符串） |  |  | so |
| `I68` | 屏幕亮度 Settings.System.screen_brightness | screen_brightness | 0x3b7bc Settings.System.getInt(cr, "screen_brightness")。这份 44 | 44 | 44 | vB2 |
| `i9d` | 蓝叠 bst.machine_id 是否存在 | bst.machine_id | 0x492d4 解密属性 bst.machine_id 再 getprop/access |  |  | so |
| `IAI` | stat(/storage/emulated/0/DCIM) 两个 timespec | %ld.%ld,%ld.%ld | 0x42a18 i%3 XOR(0x8e,0x8d,0x8c) 解 24 字节路径，stat | "[X]^^_`_]Z]\\XXY\\]]UXXU]]\\YXX\\]Z]_`_^^]X[S" | "1788351561.621669764,1788351561.621669764" | vB2 |
| `IeP` | 中兴 OAID 通道 zteid | zteid | 0x50fcc 内部名 zteid |  |  | so |
| `IJK` | lstat(/storage/emulated/0) 两个 timespec | %ld.%ld,%ld.%ld | 0x427d0 XOR 出 `/storage/emulated/0`（19 字节，偶 0x93 奇 0x91，倒序） | "`X\\^Y_[_WZ^\\XX^\\_\\U`WUW^Z\\[W^WZY___[^[XS" | "1788351559.75002844,1788374300.871704259" | vB2 |
| `IJs` | 数盟私有目录 app_DUHOME | DUHOME | 0x2f654 Context 建 DUHOME，MODE_PRIVATE | "lVt,v)o< \| )kV'=8;8-):VV,W1V7+:7,56U)BU0=10" | "/data/user/0/com.zhihu.android/app_DUHOME" | vB2 |
| `iK3` | 当前网络名字 NetworkInfo.getName() | getName | 0x41a90 isConnected 后 getName |  |  | so |
| `iod` | filesDir 下 _driver.dat | _driver.dat | 0x18ab4 读本地 _driver.dat |  |  | so |
| `IOe` | OAID | oaid | oaid |  |  | so |
| `IPz` | WiFi SSID getSSID() | WifiInfo.getSSID | 0x3ca04 getSSID |  |  | so |
| `iVl` | prefs boot_uuid | boot_uuid | 0x2cef0 AUTH_APP_INFO 段里读 boot_uuid |  |  | so |
| `iWf` | d2api JSONObject 里 atoi 出来的整型标志 | atoi(组包串) | 0x2a7ac：JSONObject.put(String,long)，值=atoi(x21)。HAR=0。和 cdd/B3k/eBI/vB2 同一 0x27a0c 组包函数 | 0 | 0 | d2api |
| `iXj` | 蓝牙名称 Settings.Secure.bluetooth_name | bluetooth_name | 0x3b930 getString("bluetooth_name") |  |  | so |
| `iYB` | 网卡对象（tun0/wlan0、地址、DNS、能力） | 嵌套对象 | NetworkCapabilities 或 Display 嵌套 | {"txo": "W<6=", "Zne": "%#YXZWVUXXUUWX", "MCN": "%#_VU_… | {"txo": "tun0", "Zne": "[10.1.10.1/32]", "MCN": "[/8.8.… | vB2 |
| `iZS` | CPU 块计数 | int 0 | 3q2 对象旁 0x1e140 | 0 | 0 | vB2 |
| `J7w` | 移动数据开关 | getMobileDataEnabled | TelephonyManager.getMobileDataEnabled | 0 | 0 | vB2 |
| `JCE` | 厂商 OAID 通道 suaid | suaid | 0x50ba4 内部名 suaid |  |  | so |
| `JcY` | 第一次 gettimeofday 的 tv_sec（缓存） | gettimeofday.tv_sec | 0x86504：.bss 0x1148e0 为空才 gettimeofday，把 tv_sec 存进去。顶层 0x83084 读出来 putInt |  |  | so |
| `JEw` | /proc/self/status 的 uid/gid/groups | 混淆 | 3q2 同块 0x1e158 | "W==1O,\\dZXYWWYYZS\\POA=,W7'*)AY:Z-\\>P-GO/^1`,`d`XSWP… | "uid=10235(u0_a235) gid=10235(u0_a235) groups=10235(u0_… | vB2 |
| `JFN` | 外部存储 | 外部存储 | 0x18b38 旁 |  |  | so |
| `JIi` | WiFi 链路速率 getLinkSpeed() | getLinkSpeed()I | 0x3d764 WifiInfo.getLinkSpeed。有权限才采是因为前面 checkPermission |  |  | so |
| `jK5` | WiFi BSSID | getBSSID | WifiInfo.getBSSID |  |  | so |
| `JM9` | SHA-1(wlan0/eth0 的 MAC 文本) | SHA-1(sysfs address) | 0x1841c MessageDigest("SHA-1")；输入 0x17f3c→0x4373c 读 `/sys/class/net/wlan0/address`，空则 eth0。digest 长度 0x14 |  |  | so |
| `JPd` | SIM 运营商代码 getSimOperator，没卡 0 | getSimOperator | TelephonyManager.getSimOperator，无卡 "0" | "0" | "0" | vB2 |
| `JYD` | WiFi 速率 | link speed | getTxLinkSpeedMbps/getRxLinkSpeedMbps | 5 | 5 | vB2 |
| `jYO` | SIM 状态（Telephony/Subscription 那条） | getSimState 同源函数 | 0x35d64 getSystemService(phone / telephony_subscription_service)，函数内 getSimState。和 4VP 同一文件 |  |  | so |
| `K4N` | 酷派 OAID 通道 cpid | cpid | 0x510fc 内部名 cpid |  |  | so |
| `K5f` | MD5("%s%d%d%d", 缓存或UUID, pid, rand, tid) | MD5("%s%d%d%d") | 0x25958：%s=0x45068 拷 .bss 0x114c35（0x85dd0）；空则 0x44e7c UUID.randomUUID()/proc/sys/kernel/random/uuid；再空 0x45270。三个 %d=getpid()、rand()、gettid()。0x4ccf4 | "51BCCD3FD5ACB23974669DC5D75D4483" | "51BCCD3FD5ACB23974669DC5D75D4483" | dcc2 |
| `kAs` | OAID | oaid | oaid SDK |  |  | so |
| `KCv` | filesDir/wf562O027z/ 下的本地缓存 | %s/wf562O027z/%s | 0x51c58 getFilesDir + 该相对路径，内部名 ldck |  |  | so |
| `kd8` | device_label 是否带上 | 0/1 | dcc2 包装 | 0 | 0 | dcc2 |
| `KjD` | 三星广告 ID | ssuid | 0x51064 |  |  | so |
| `kKW` | GPS 纬度 getLatitude() | Location.getLatitude | 0x35224 ACCESS_FINE_LOCATION 后 gps/network getLatitude。不是 selinux |  |  | so |
| `Kvk` | MD5("%s%d%s", 设备缓存, pid, UUID) | MD5("%s%d%s") | 0x44f78：%s=0x85dd0 缓存，%d=getpid()，%s=0x44e7c UUID；0x4ccf4。strlen==0x20 才写入 .bss 0x114920。put 0x2c534 读缓存 | "07A3C5543A362678EA30684B42AE16AA" | "07A3C5543A362678EA30684B42AE16AA" | daa |
| `Kvr` | 基带版本 getRadioVersion | getRadioVersion | Build.getRadioVersion 0x3a424 | "_/]^[Y`\\_W[T_WTWiYTWYYYT[YWY" | "g7250-00202-220422-B-8489468" | vB2 |
| `kYm` | uname -a（内核版本） | 混淆 | QgA 旁 0x1e0fc | "[s]106+=:@)G)4G7Y+Y)W4Y0G7j;{<\|GG[^U\\Xa`XUYYaY\\[WTG… | "Linux localhost 4.19.224-g9e23c2625924-ab8577203 #1 SM… | vB2 |
| `KyU` | 采集时刻（秒.纳秒） | 定长摘要混淆 | 6yY 旁 0x26450 | "`XY^__\\_Z^]][W[Y[\\UW" | "1788760250.444635829" | vB2 |
| `kz6` | vB2 协议标志，SO 写死的 "1" | 字面量 "1" | `0x28994` putStr(kz6, 解密GOT "1")，不是采集值。组包点 0x27bc0 同样加载这对 GOT |  |  | so |
| `LAh` | Magisk/Xposed/LSPosed 等包是否装了 | PackageManager 扫包 | 0x47a14：com.topjohnwu.magisk、huskydg.magisk、xposed.installer、edxposed.manager、lsposed.manager、substrate、apk008、hidemyapplist 等。拼成 8 位数字。这份 00000000=全无。不是 ICCID | "WWWWWWWW" | "00000000" | vB2 |
| `LDA` | 设备软件版本 getDeviceSoftwareVersion() | getDeviceSoftwareVersion | 0x36028 READ_PHONE_STATE 后 getDeviceSoftwareVersion |  |  | so |
| `LkB` | 数据网络类型 getDataNetworkType() | getDataNetworkType()I | 0x36f28 READ_PHONE_STATE 后 getDataNetworkType |  |  | so |
| `LLS` | WiFi MAC（getMacAddress） | getMacAddress | WifiInfo.getMacAddress（GOT 0xbcfd8 @ 0x3ddb8）；失败用占位 94:1C:7F:73:50:6E | "20:0…" | "20:0…" | vB2 |
| `LMi` | 应用 lastUpdateTime | lastUpdateTime | PackageInfo.lastUpdateTime | 1788760216836 | 1788760216836 | dcc2 |
| `lPc` | 卡2 电话服务 phone2 | phone2 | 0x369b0 getSystemService("phone2")，READ_PHONE_STATE |  |  | so |
| `MaO` | 数盟 query 返回标志 | sdk_result | 邻近 msg/query。这份 "0" 是返回值，不是“含义就是 0” | "0" | "0" | d2api |
| `mEC` | 服务端配置 JSON 的 mEventCode | JSONObject.opt("mEventCode") | 0x86b0c opt mEventCode，写 .bss 0x114a68；0x85990 strncpy 到 0x114b10。顶层 0x854f0 读出来 putStr |  |  | so |
| `mgO` | isUserAMonkey | isUserAMonkey | ActivityManager.isUserAMonkey（GOT 0xbf128） |  |  | so |
| `mIS` | boot_id（/proc/sys/kernel/random/boot_id） | /proc/sys/kernel/random/boot_id | 读该节点（GOT 0xc0ce0 @ 0x44e68） | "Y,[)…" | "da01…" | vB2 |
| `MLz` | HOME Intent 的 resolveActivity | resolveActivity | 0x2df94 解析 HOME Intent 得到 ActivityInfo（默认桌面） |  |  | so |
| `mSa` | 厂商 OAID 通道 sanl | sanl | 0x50e50 内部名 sanl，邻 xmid 通道 |  |  | so |
| `msg` | query 入参 json | jsonB | DUHelper.query 的 {custom:""} | {"custom": ""} | {"custom": ""} | daa |
| `Mt4` | 0x27a0c 打好的 JSONObject | JSONObject | 顶层 0x2d5c8 bl 0x27a0c（里面会 put iWf/vB2/kz6/o7k 等），再 0x54688 JSONObject.put(String,Object) 挂到 Mt4 |  |  | so |
| `mw0` | IMEI TAC/厂商码 getManufacturerCode() | getManufacturerCode | 0x361fc getManufacturerCode。这份是 Pixel 5 TAC，原值已截断 | "3524…" | "3524…" | vB2 |
| `mw1` | 网卡地址 getAddress() | getAddress | 0x41ad8 isConnected 后取地址 |  |  | so |
| `My2` | 当前活动网络 getActiveNetwork() | ConnectivityManager.getActiveNetwork | 0x3e6a4 getActiveNetwork，不是 prefs udd |  |  | so |
| `mZF` | OPPO 广告 ID | opaid | 0x50e04 |  |  | so |
| `n1R` | USB 设备个数 UsbManager.getDeviceList().size() | UsbManager size | 0x380b8 getSystemService("usb") → getDeviceList HashMap.size |  |  | so |
| `NAB` | 屏幕是否亮着 PowerManager.isScreenOn() | isScreenOn()Z | 0x2f138 PowerManager.isScreenOn。这份 1=亮 | 1 | 1 | vB2 |
| `nAt` | nctl 的本地拷贝 | "2" | 从 nctl 拷；HAR 里是 "2" | "2" | "2" | dcc2 |
| `nctl` | 数盟下发的控制位 | 服务端 nctl | d2api 响应；prefs MD5("nctl")；文件 /eae6ff4a |  |  | so |
| `ne8` | MD5(libdu.so 文件内容) | MD5(libdu.so bytes) | 0x506dc：fopen("/proc/self/maps") strstr("libdu.so") 取路径；再 nativeLibraryDir+"/libdu.so"，0x4cd2c 整文件 MD5。put 0x26120 | "536e303d11e1a44ad1c0fd6da4c94d45" | "536e303d11e1a44ad1c0fd6da4c94d45" | vB2 |
| `NG0` | filesDir 下 _system.dat | _system.dat | 0x18b20 读本地 _system.dat |  |  | so |
| `ni` | 数盟会话序号 na_seq_ni | na_seq_ni | vB2 组包序号，不是设备指纹 |  |  | so |
| `Nue` | daa 标志 | "i" | daa | "i" | "i" | daa |
| `nur` | 连点器/自动脚本包是否装了 | PackageManager 扫包 | 0x46f84：repetitouch、mobileanjian、touchsprite、zidongdianji、autojs、zdanjian 等。命中计数。这份 0 | 0 | 0 | vB2 |
| `NZR` | 厂商 OAID 通道 xmid | xmid | 0x50e98 内部名 xmid。不是 HTTP 头 x-ms-id |  |  | so |
| `o5g` | 数盟 ss3 服务探测 | ss3-* | 0x2bc2c 调 0x3a7e8/0x3a7ac，邻 UbY/ss3 |  |  | so |
| `o7k` | d2api JSONObject 里 atoi 出来的整型标志 | atoi(组包串) | 0x28de0：同样 putInt atoi。HAR=1。和 o_a/hd7 同一组包段 | 1 | 1 | d2api |
| `oeH` | 厂商 OAID 通道 mtid | mtid | 0x50f80 内部名 mtid |  |  | so |
| `OEu` | prefs tra_stats | prefs tra_stats | `0x2c828` helper `0x11680` |  |  | so |
| `oJI` | 传感器列表（名/厂商/量程/功耗） | SensorList | SensorManager.getSensorList（GOT 0xbe428） | {"BAZ": {"0": {"1kt": 0, "Fxg": 1, "iPe": 142856, "PRr"… | {"BAZ": {"0": {"1kt": 0, "Fxg": 1, "iPe": 142856, "PRr"… | vB2 |
| `OQE` | Droid4X ro.droid4x.host.mac | ro.droid4x.host.mac | `0x498c0` XOR 解密再 getprop |  |  | so |
| `OW2` | 本 uid 进程列表 + pid | ps/uid | Process.myUid + 进程列表，邻近 2cO/qdK | "\\+Z7Y5WUXBS081-0:=/US);68,S:07;1S,,S1+77:5,U6B)0U1=00… | "com.zhihu.android,com.zhihu.android,com.zhihu.android:… | vB2 |
| `OWY` | Settings.System.getInt 的另一项 | Settings$System.getInt | 0x3b7f4 紧挨 I68 screen_brightness 的下一项 getInt |  |  | so |
| `ozK` | 蜂窝子类型名 | getSubtypeName | 邻近 zpA |  |  | so |
| `P1J` | 服务端记下的设备号，首次等于 AYk | o_a / AYk | 首次=AYk；之后用 d2api 响应 o_a（0x84018） | "XX:XX:XX" | "XX:XX:XX" | dcc2 |
| `p92` | IMEI/deviceId | getImei/getDeviceId | TelephonyManager |  |  | so |
| `pc4` | 系统属性 sys.usb.vserialno | sys.usb.vserialno | 0x49b30 XOR 出 sys.usb.vserialno 再 getprop |  |  | so |
| `pcJ` | 设备序列 Settings device_serial | device_serial | 0x3bc60 Settings 读 device_serial；同函数后还有 usb_mass_storage_enabled |  |  | so |
| `pEC` | 服务端配置 JSON 的 pEventCode | JSONObject.opt("pEventCode") | 0x86adc：配置 JSON（同段还有 https/type/inner/dna）opt pEventCode，写 .bss 0x114a60。顶层 0x854e4 读出来 0x540c0 putStr |  |  | so |
| `pr2` | vB2 组包会话字段 | 组包键 | 0x27bc8 与 kz6/"1"/na_rseq_ni 同一组包段 |  |  | so |
| `pT4` | MD5(libdu.so 文件内容)（与 ne8 同一函数 0x506dc） | MD5(libdu.so bytes) | 0x2479c/0x247a8 两次 0x506dc，put x22。算法/输入与 ne8 相同；这份 HAR 大小写和值不同，可能 maps 路径和 nativeLibraryDir 不是同一个 inode | "B8974D2DDA25F60CA782B9387F4F4326" | "B8974D2DDA25F60CA782B9387F4F4326" | vB2 |
| `PuV` | filesDir 下 _android.dat | _android.dat | 0x18b30 读本地 _android.dat |  |  | so |
| `PV8` | 充电时保持唤醒 stay_on_while_plugged_in | Settings.Global.stay_on_while_plugged_in | 0x3bba0 getInt("stay_on_while_plugged_in"). 7=AC/USB/WIRELESS 都开 | "7" | "7" | vB2 |
| `PWh` | 定位/电话/蓝牙权限是否授予的位图 | checkPermission 位图 | 0x2e3cc 依次 check ACCESS_FINE_LOCATION / NEARBY_WIFI_DEVICES / READ_PHONE_STATE / BLUETOOTH_SCAN。不是 signatures |  |  | so |
| `pwS` | config JSON | config JSON | `0x2cb10` 邻 daa/I68/2us |  |  | so |
| `Pxm` | ctime 风格时间串 | 混淆 | 2cO/qdK 块 0x206d0 | "]tY7W6YGGz{-k8lGGG]^XGaWXX\\a" | "Mon Sep  7 01:51:16 EDT 2026" | vB2 |
| `q6I` | 华为 pps_oaid | pps_oaid | 0x3bacc |  |  | so |
| `qdK` | 开机起 elapsedRealtimeNanos | elapsedRealtimeNanos | SystemClock.elapsedRealtimeNanos（GOT 0xbcfc8，函数 0x45594） | "386356898986106" | "386356898986106" | vB2 |
| `Qg1` | 当前时间 currentTimeMillis | currentTimeMillis | System.currentTimeMillis（GOT currentTimeMillis；put 在 0x26b20，紧挨 LMi/Zrs） | 1788760216836 | 1788760216836 | dcc2 |
| `QgA` | CPU 块计数 | int 0 | 3q2 块 0x1e0ec | 0 | 0 | vB2 |
| `qH9` | 应用 dataDir 是否可访问的 0/1 | dataDir 探测 | 0x2f4dc getApplicationInfo.dataDir，再试 %s/..，put "0" 或 "1" | "0" | "0" | vB2 |
| `QNw` | lstat(/sdcard/Android/data/com.google.android.gms) 两个 timespec | %ld.%ld,%ld.%ld | 0x428d8 i%3 XOR(0xa1,0xa0,0x9f) 解 43 字节路径 | "\\X^^[_X_WZW\\\\XZ\\Z^UW_UW]^]X_\\ZZZ_^_Z^ZXYS" | "\\X^^[_X_WZW\\\\XZ\\Z^UW_UW]^]X_\\ZZZ_^_Z^ZXYS" | vB2 |
| `QQW` | 是否连网 isConnected | isConnected | NetworkInfo.isConnected，邻近 zpA/ozK | 0 | 0 | vB2 |
| `qUM` | 当前网络是否连通 isConnected() | NetworkInfo.isConnected | 0x3f9f8 getActiveNetworkInfo().isConnected() |  |  | so |
| `QvM` | LOCAL_MAC_ADDRESS / ACCESS_FINE_LOCATION | LOCAL_MAC_ADDRESS / ACCESS_FINE_LOCATION | helper `0x3dd28`/`0x3f6b0`，put `0x1cca0` 邻 wSK |  |  | so |
| `rd` | daa 会话序号 aa_rseq | aa_rseq | daa 组包序号，不是设备指纹 |  |  | so |
| `S6e` | SELinux enforce 文件的 atoi，读不到当 1 | /sys/fs/selinux/enforce | 0x42288：读 enforce 文本 atoi，失败则返回 1。和 9be 同源文件，9be 读失败是 -1 | 1 | 1 | vB2 |
| `sAJ` | libreference-ril.so 与 libc.so 文件哈希是否都能读到 | file MD5 两个 so 的 0/1 | 0x424ac 同源：先哈希 ril so 再 libc so。sAJ 是 putInt 成败，gEd 才是 hex | 0 | 0 | vB2 |
| `SAN` | 系统 API 等级 SDK_INT | SDK_INT | Build.VERSION.SDK_INT | 32 | 32 | dcc2 |
| `SAu` | 应用签名证书 DN | 长串 | cmP 块 | "ujjuddj\"G0S1/06=1S3G-vw\|dd{Bz0G1S0/=6U1+37-5wSdGsvGd… | "CN=Zhihu, OU=zhihu.com, O=zhihu.com, L=Peking, ST=Peki… | vB2 |
| `sCc` | 屏幕是否可交互 PowerManager.isInteractive() | isInteractive()Z | 0x2f434 PowerManager.isInteractive。这份 1 | 1 | 1 | vB2 |
| `sfOo` | 本地文件 /89ca503b 的 "%s,%ld;" | /89ca503b | 0x403c8 读该路径 sprintf("%s,%ld;") | "69A5B59" | "qmmqzyn" | vB2 |
| `sJN` | getSimState 整型 | getSimState | TelephonyManager.getSimState | 1 | 1 | vB2 |
| `sKZ` | filesDir 本地 dat | 本地 dat | 0x18b14 与 _android.dat 同块 |  |  | so |
| `Slq` | prefs/文件 | prefs/文件 | `0x2c8cc` helper `0x11680` 邻 OEu/uCM |  |  | so |
| `Sxg` | config | config | `0x2cb10` 邻 daa/0wL |  |  | so |
| `szj` | 该 helper 直接返回空 | NULL | 0x3bc10 `mov x0,xzr; ret`，当前 SDK 不上报 |  |  | so |
| `T5u` | 随机 MAC 占位检测的配套字段 | :00:00:00: | 0x593c8 与 XmW 的 :00:00:00: / /89ca503b 同组 |  |  | so |
| `t7Q` | 雷电/逍遥/Windroy 等模拟器文件是否存在 | access() 模拟器 bin/so | 0x48340：/system/bin/ldinit、ldmountsf、libldutils.so、microvirt-prop、libdroid4x.so、windroyed、libnemuVMprop.so。命中计数。这份 0 | 0 | 0 | vB2 |
| `tbA` | 默认输入法 default_input_method | default_input_method | 0x3b968 Settings getString("default_input_method")；后面还有 wifi_connected_mac_randomization_enabled |  |  | so |
| `tbL` | MD5(/system/framework 下文件名拼接) | MD5(strcat(d_name…)) | 0x423a8：0x5683c(w3=7) 解出 `/system/framework`，opendir/readdir，跳过 d_name[0]=='.'，其余名字 strcat 无分隔符，0x4ccf4 MD5，%02X。put 0x252c4 | "k`W^\\_Y_[l^X[Yl`iikWWj\\\\YYZ^k_kW" | "9788E129B0C52780DD3250DBE474250D" | vB2 |
| `tcc` | HOME Intent 相关 | HOME Intent | 0x39d78 组 HOME Intent（parr2），MLz 才是 resolveActivity 结果 | {"zdH": 129, "0": {"Ggf": 1, "WTC": 818462278, "DUv": "… | {"zdH": 129, "0": {"Ggf": 1, "WTC": 818462278, "DUv": "… | dai |
| `tLE` | 百度 Settings 键 bd_setting_i | bd_setting_i | 0x3b3d4 Settings 读 bd_setting_i |  |  | so |
| `tNP` | Build.getSerial | getSerial | Build.getSerial 0x3a4ac |  |  | so |
| `tth` | SuperSU/KingRoot 等 root 包是否装了 | PackageManager 扫包 | 0x47500：eu.chainfire.supersu、noshufou.android.su、koushikdutta.superuser、kingroot、kingo.root、fox2code.mmm、vvb2060.magisk。命中计数。这份 0 | 0 | 0 | vB2 |
| `tUv` | 数盟 ss3-9 服务探测 | ss3-9 | 0x3a6f8 混淆服务名 ss3-9 |  |  | so |
| `TwQ` | 屏幕：宽高、xdpi/ydpi、density | DisplayMetrics | Display.getRealMetrics（GOT DisplayMetrics/getRealMetrics，0x2e55c） | {"1Lx": 2340, "NlZ": 1080, "NZE": 435, "zm4": 433, "AJd… | {"1Lx": 2340, "NlZ": 1080, "NZE": 435, "zm4": 433, "AJd… | vB2 |
| `Uae` | 系统服务探测（环境/模拟器） | phone/phone2 getSimState | helper `0x36384`/`0x35ec0` getSystemService("phone") / "phone2"，再 getSimState；pending 原文在此截断，个别未完全闭合 |  |  | so |
| `ubF` | 把 n_a 再带回去 | n_a 拷贝 | 把 n_a 填回去 | "QISY…" | "QISY…" | dcc2 |
| `UbY` | 数盟 ss3-3 服务探测 | ss3-3 | 0x3a770 混淆服务名 ss3-3 / ss3-19 / ss3-6 |  |  | so |
| `uCM` | 电池：状态/健康/电量/电压/温度 | 电池 Intent | ACTION_BATTERY_CHANGED 邻近 oJI/XH7 | {"pnb": 2, "I2Y": 2, "LzC": 81, "nF5": 100, "fgm": 4178… | {"pnb": 2, "I2Y": 2, "LzC": 81, "nF5": 100, "fgm": 4178… | vB2 |
| `Ufi` | 已配对蓝牙数 | bonded devices | BluetoothAdapter.getBondedDevices().size |  |  | so |
| `uG4` | WiFi MLO 链路的配套字段 | MLO | 0x1cb6c 紧挨 59p 的 getAffiliatedMloLinks |  |  | so |
| `UOv` | 时间戳（秒.纳秒） | 混淆串 | mIS/JPd 旁 | "\\XY^`_[_XZY^ZZX`]XU`" | "1788373919.613214925" | vB2 |
| `v1X` | 数盟会话序号 na_seq_ni | na_seq_ni | vB2 组包序号，不是设备指纹 |  |  | so |
| `v5q` | "0" | "0" | dcc2 | "0" | "0" | dcc2 |
| `v6Y` | libdu 标识 | 字面量 | DUHelper |  |  | so |
| `vB2` | 嵌套设备画像（169 键） | 169 键对象 | 0x27148 采集后整体 put，字符串走 0x543ec |  |  | d2api |
| `VcZ` | 联想广告 ID | laid | 0x50d6c |  |  | so |
| `VHo` | WiFi MAC getMacAddress() | WifiInfo.getMacAddress | 0x3dd28 LOCAL_MAC_ADDRESS/ACCESS_FINE_LOCATION 后 getMacAddress / 字段 mMacAddress |  |  | so |
| `VIB` | 本 uid 的 ps 计数，格式 %d,%d | Process.myUid + ps / grep u0_a%d | 0x48e40 sprintf("%d,%d", …) 并对 u0_a{uid%100000} 做 ps。这份 vB2 解开是 2,0 | "WYS" | "2,0" | vB2 |
| `vry` | 该 helper 直接返回空 | NULL | 0x3bc18 `mov x0,xzr; ret`，当前 SDK 不上报 |  |  | so |
| `vuS` | Google 广告 ID（GAID） | GAID | AdvertisingIdClient，键旁字符串 gaid（0x50c88） | "[`*Y…" | "9296…" | vB2 |
| `VUZ` | 蓝叠 nemud.player_uuid | nemud.player_uuid | 0x4938c 解密 nemud.player_uuid |  |  | so |
| `vv1` | 铃音模式 AudioManager.getRingerMode() | getRingerMode()I | 0x2f01c getSystemService("audio").getRingerMode。0静音 1振动 2正常。这份 2 | 2 | 2 | vB2 |
| `w5v` | prefs 键 pkcg | pkcg | 0x2589c 0x55708 读 pkcg | "0" | "0" | vB2 |
| `w91` | MD5(/system/fonts 下文件名拼接) | MD5(strcat(d_name…)) | 0x422e8 对 `/system/fonts` 同样 readdir+strcat（跳过 `.`/`..`），0x4ccf4 MD5。put 0x253ec | "B85239EDCACF58CE9FF740294D27D8E8" | "B85239EDCACF58CE9FF740294D27D8E8" | vB2 |
| `w97` | /dev/input/event0 与 su 路径 access() | /dev/input/event0 + /su | 0x4487c access(/dev/input/event0、/su、/system/bin/su、xbin/su、sbin/su) |  |  | so |
| `wlM` | USB 连接/adb 位图 | USB_STATE Intent extras | 0x2ece4 registerReceiver(null, USB_STATE)，getBooleanExtra("connected") 和 "adb" 拼成整型。这份 3=connected+adb | 3 | 3 | vB2 |
| `wSK` | 本机 IPv4（DhcpInfo.ipAddress） | DhcpInfo.ipAddress | WifiManager.getDhcpInfo.ipAddress（GOT getDhcpInfo/ipAddress） | "172.…" | "172.…" | vB2 |
| `wv6` | 夜神 persist.nox.wifimac | persist.nox.wifimac | 0x49778 解密 persist.nox.wifimac |  |  | so |
| `XFU` | ICCID 真值 | getSimSerialNumber | TelephonyManager |  |  | so |
| `XH7` | 电池/传感器条目数 | int 5 | uCM 旁 0x1ddec | 5 | 5 | vB2 |
| `xlR` | SIM 运营商名 | getSimOperatorName | helper 0x45a44，邻近 2wp/zP8 |  |  | so |
| `XmW` | MAC 里是否出现 :00:00:00: 占位 | :00:00:00: | 0x40360 扫地址串里的 :00:00:00: 模式 |  |  | so |
| `XQp` | 两次 clock_gettime(CLOCK_REALTIME) 的 tv_nsec 差 | nsec delta | 0x452ec：clock_gettime(0) → time()/malloc/snprintf 扔掉 → 再 clock_gettime(0)。Δnsec<0 则绕 1e8。sprintf("%ld") 再 atoi putInt。HAR=14642ns。顶层 0x2dc5c 会再用同名键 put atoi(getpid())，vB2 里这份是 nsec | 14642 | 14642 | vB2 |
| `xRD` | 流量/计数快照 CSV | 逗号分隔整数 | cmP 块 0x2317c，像 TrafficStats 快照 | "163863,107,613913,0,75668,11,633156,0,368185,111," | "npkionkiddmndinkmddnimiididppkhnikdipnohkqidhdnki" | vB2 |
| `xsh` | 中兴广告 ID | zteid | 0x50fcc |  |  | so |
| `xuV` | IPhoneSubInfo 订阅者信息 | getSubscriberInfo | 0x37838 READ_PHONE_STATE 后 getSubscriberInfo()Lcom/android/internal/telephony/IPhoneSubInfo |  |  | so |
| `XVe` | 时间差 ms | currentTimeMillis 差值 | GOT currentTimeMillis xref 0x775d8 旁键 XVe |  |  | so |
| `y0N` | 系统服务探测（环境/模拟器） | ss3-3 ss3-19 | helper `0x3a770` getSystemService |  |  | so |
| `y5W` | 本地 prefs 里的 boot_times 字符串 | SharedPreferences "boot_times" | 0x25d28 helper 0x55708 读 key boot_times，0x540c0 putStr。这份 "1" | "1" | "1" | d2api |
| `Yko` | IMSI | getSubscriberId | TelephonyManager.getSubscriberId |  |  | so |
| `ySX` | 蓝叠 bst.config.machineId | bst.config.machineId | `0x49500` XOR 解密再 getprop |  |  | so |
| `Z2w` | 另一块 .bss 缓存串，空则不上报 | .bss 0x114c75 via 0x85e1c | 0x43690 拷 0x85e1c 缓存。和 6yY 不是同一条：6yY 才是现场采的 Widevine hex |  |  | so |
| `z4e` | WiFi state（3=已开启） | getWifiState | WifiManager.getWifiState（GOT 0xc0f00 @ 0x3ecb4） | 3 | 3 | vB2 |
| `z4m` | 无障碍服务列表 + 厂商包名 | enabled_accessibility_services | 0x3b4b4 getString("enabled_accessibility_services")，并探 com.hihonor.awareness / com.huawei.hiai / com.miui.securitycenter |  |  | so |
| `zc7` | Xposed 四位检测串 | /proc/self/maps + XposedBridge.jar | 0x48230：maps 里搜 xposed、access(XposedBridge.jar)、FindClass(IXposedHookLoadPackage)。拼成 4 位。这份 0000 | "0000" | "0000" | vB2 |
| `ZCk` | 数美设备 ID Settings com.shumei.deviceid | com.shumei.deviceid | 0x3b2e0 Settings$System.getString("com.shumei.deviceid") |  |  | so |
| `ZIG` | 移动数据开关 getMobileDataEnabled() | getMobileDataEnabled()Z | 0x3fcd0 ConnectivityManager.getMobileDataEnabled |  |  | so |
| `zP8` | MEID getMeid() | TelephonyManager.getMeid | 0x37c00 getMeid，空不上报 |  |  | so |
| `zpA` | 网络类型名 getTypeName | getTypeName | NetworkInfo.getTypeName（GOT 0xbf0a0），HAR=WIFI | "WIFI" | "WIFI" | vB2 |
| `Zrs` | versionCode | versionCode | PackageInfo.versionCode | 40408 | 40408 | dcc2 |
| `ZtU` | 系统服务探测（环境/模拟器） | ss3-5 | helper `0x3a860` getSystemService + getId |  |  | so |
| `zUN` | 当前输入法 ComponentName | Settings | 邻近 8ET | "l+t7p56U1/<7)7s/U46-1U<))64,U:,7710,<U-156<8==8<651-U<… | "com.google.android.inputmethod.latin/com.android.input… | vB2 |
| `zvW` | MD5(内嵌 64×64 PNG 转 RGB_565 后的像素) | MD5(copyPixelsToBuffer) | 0x4641c：NewByteArray(0x116) 填 .rodata 0x88fa0 的 PNG（IHDR 64x64），decodeByteArray → copy(RGB_565) → copyPixelsToBuffer → 0x4cf90 MD5 %02x | "X`ZZ\\).*Y]^^`Y`YZ-.`.)+W.-*,)`][" | "93ab6722e9a0ed946abfcff39972f531" | vB2 |
| `ZZA` | 虚拟网卡/存储路径 access() 命中数，<1 不上报 | access(tun0/ppp0/tap0/…) | 0x424f0 XOR 出路径再 access()：/sys/class/net/tun0、ppp0、tap0，以及 /sdcard/Android/data/.nomedia、/storage/emulated/0/DCIM 等；还 stat /data/system 和 shared_prefs。返回值≥1 才 putInt。不是“含义 0”——这份返回 0 所以是 0 | 0 | 0 | dcc2 |

共 366 个 key。实验室设备原值已截断；ROM / Build / 目录名 MD5 / 内嵌 PNG MD5 这类可复现的对照样例保留。

## 6. 未完全钉死的项

够理解签发和采集面，但下面几条不要写成已闭合：

- `Uae` 的采集串在 pending 里被截断，只恢复到 `getSystemService("phone"/"phone2")` + `getSimState`。
- `IJs` 的「出现」列被密文里的 `|` 吃掉，归档时按邻近有 HAR 的路径键补成 `vB2`，待下一份包复核。
- `R25` 同样被密文 `|` 拆列，出现面按 `R24`/`R26` 补成 `vB2`。
- 约 160 个 `so` 键在这份 Pixel 5 HAR 里是空的：代码会采，空则不上报。不要把「表里有键」写成「注册包一定带」。
- `daa` / `dcc2` / `dai` / `audd` 与 `vB2` 的边界是按 HAR 出现面标的，个别会话序号、prefs、配置块可能还有串组。
- `pT4` 与 `ne8` 算法相同但 HAR 值不同，原文已标可能是两条路径的 inode 差，未再验证。
- 厂商 OAID 通道（`asaid` / `hwaid` / `opaid` / `xmid` 等）只确认内部名和 put 点，本包多数没带值。

本文不是改机手册，也不给可打生产的注册客户端。`cdd` 是签发票，不是激活；空 body / HTTP 200 空壳仍不是 `serverAccepted`。
