# 安卓 ACE deviceUniqueId 设备拉黑机制

> 来源: 看雪论坛 [thread-292813](https://bbs.kanxue.com/thread-292813.htm)（作者 Lun_OS；原文声明由 AI 辅助整理，数据来自真实环境 ACE 逆向）
> 原始发布时间: 2026-08-30
> 归档日期: 2026-09-03
> 分类: 反检测/风控对抗 — Android 硬件身份锚点
>
> ACE 在安卓端把设备身份钉在 Widevine `deviceUniqueId` 上。该值由 TEE / RPMB 内的 KeyBox 派生，不在普通文件系统；客户端经 Java `MediaDrm` 取样后写入 `libtersafe.so`，随常规上报加密后走 UDP。刷机、恢复出厂、改 persist MAC、清 provisioning 文件都改不掉它；只 hook Java 层会被双路径对账拆穿。完整性修复（PIF / 下发 keybox）和身份取值是正交维度。

## 适用范围

本文只归档 **设备身份硬锚点** 与 ACE 客户端上报链。它回答的是：ACE 用什么当设备 ID、这个 ID 从哪一层读出来、怎样进 native 状态、服务端可能用哪些独立证据交叉验证。

它不是改机手册，也不讨论具体游戏业务。`deviceUniqueId` 原值、完整哈希、出口 IP、Cookie 不进知识库。原文实验里的 Wi-Fi MAC 已脱敏。

相关地图：

| 主题 | 文档 |
|------|------|
| App 请求生命周期 / Interceptor | [app-reverse-global-map.md](../mobile-app-reverse/app-reverse-global-map.md) |
| 纯协议客户端与指纹语义 | [pure-protocol-sdk-reconstruction.md](../mobile-app-reverse/pure-protocol-sdk-reconstruction.md) |
| Pixel 6 / APatch 身份门 | 主仓刷机文档与 `pixel6-control` |

原文对照样本是 `libtersafe.so`（TSS SDK 7.7.38）。函数名、偏移只对应该构建，换版本先重新对符号。

## 1. 硬锚点

ACE（Anti-Cheat Expert）在安卓端判定「是不是同一台设备」时，核心硬锚点是 Widevine DRM 的 `deviceUniqueId`。

该 ID 由 TrustZone 内出厂烧录的 KeyBox 派生，不落在普通文件系统。客户端取到后与 Build、传感器等特征一并上报，服务端与历史记录绑定，形成设备级黑名单。

因为派生和存储都在 TEE / RPMB，刷机、恢复出厂、root、改系统分区通常都动不到它。Android ID、MAC、应用数据都是弱锚点，不能和它互换。

## 2. KeyBox 与对外形态

`deviceUniqueId` 在设备 provisioning 阶段由 Widevine KeyBox 建立。原文给出的出厂二进制布局：

| 字段 | 长度 | 说明 |
|------|------|------|
| Device ID | `0x20`（32 字节） | 对外 `deviceUniqueId` 的来源 |
| Device Key | `0x10`（16 字节） | 加密私钥 |
| Data | `0x48` | 附加数据 |
| Magic | `0x4` | 结构标识 |
| Checksum | `0x4` | 完整性校验 |

KeyBox 整体约 `0x80`（128 字节）。Device ID 经 Widevine 密钥派生后，对外就是 32 字节 `deviceUniqueId`。实测采样：Provider 为 Widevine L1，长度固定 32 字节 / 256 bit。

## 3. 取样到上报

### 3.1 取值链路

```text
调用方（游戏 / ROM）
  -> MediaDrm.getPropertyByteArray("deviceUniqueId")   [Java]
  -> MediaDrmService (system_server)                   [框架]
  -> libwvhidl / libwvaidl                             [native]
  -> Widevine DRM HAL（vendor 进程）                    [vendor]
  -> TEE / RPMB / KeyBox                               [硬件信任根]
客户端取到 ID
  -> 与 Build、传感器等一并上报 ACE
  -> 服务端与历史记录绑定 = 设备级黑名单
```

链路贯穿 Java、native、vendor HAL，终点是 TEE。ACE 不把某一层 API 的返回值当成唯一真值，会走端到端对照。

### 3.2 ACE 客户端封装（libtersafe.so）

对 TSS SDK 7.7.38 的 IDA 结论：

1. `libtersafe.so` 内没有 `MediaDrm` / `Widevine` / `OEMCrypto` 字符串。原始取值在 Java 层，不是 native 自己读 DRM。
2. Java 取到的 32 字节 ID 经 `TssSDKSetUserInfoWithLicense()` / `TssSDKSetUserInfo()` 写入 native 状态。
3. `TssSDKGetReportData()` / `TssSDKGetReportData4()` 收集上报数据，交给游戏回调 `tss_sdk_send_data_to_svr`（存在 `init_info`）。
4. 最终由 `tss_sdk_encryptpacket` 打包，经 `sendto` 走 UDP。ACE native 自己不持有业务 socket。

```text
Java MediaDrm.getPropertyByteArray("deviceUniqueId")
  -> 32 字节 ID
    -> TssSDKSetUserInfoWithLicense / TssSDKSetUserInfo
      -> TssSDKGetReportData / TssSDKGetReportData4
        -> 游戏回调 tss_sdk_send_data_to_svr
          -> tss_sdk_encryptpacket
            -> sendto
```

`deviceUniqueId` 跟常规心跳一起走，不是只在异常时才发。

初始化结构（`sub_50D9A0`）：

```c
struct init_info {
    uint32_t size_;                     /* 必须为 16，否则参数异常 */
    uint32_t game_id_;
    void    *tss_sdk_send_data_to_svr;  /* 游戏实现的发送回调 */
};
```

写入 native 状态的两个入口：

```c
int TssSDKSetUserInfoWithLicense(
    const char *device_unique_id,   /* Java 传入的 32 字节 ID */
    const char *license,
    uint32_t    game_id);

int TssSDKSetUserInfo(
    const char *device_unique_id,
    const char *serial_no,          /* 回退 / 附加 */
    const char *android_id);
```

单条上报字符串形态是 `{key}|desc={description}`，例如 `ms_data_crc|desc=mrpcs_data_crc_error`。`key` 是事件标识，`desc` 带文件名、错误码或规则 ID。

UDP 包（`tss_sdk_encryptpacket` @ `0x1CC704`，打包链 `sub_4B0814`）：

```c
#pragma pack(push, 1)
typedef struct {
    uint8_t  encrypt_type;  /* [0] */
    uint8_t  algo_sel;      /* [1] */
    uint16_t reserved;      /* [2-3] */
    uint32_t data_len;      /* [4-7] */
    uint32_t crc_header;    /* [8-11] */
    uint32_t flags;         /* [12-15] */
    uint8_t  payload[];     /* ZIP 压缩后的检测数据 */
    /* 尾部 CRC32 */
} ace_udp_packet;
#pragma pack(pop)
```

打包顺序：随机 8 字节密钥 → ZIP 压缩 → 「3 级 × 10 算法」选择加密 → 填头并算头 CRC → 包尾 CRC32。每次密钥不同，同一明文两次打包密文不同，解密语义不变。算法细节以该 SO 版本为准，换构建要重对。

## 4. 实测：什么变、什么不变

原文只保留与 `deviceUniqueId` 相关的对照。结论可以复用，具体设备值不能复用。

| 操作 | 弱锚点 | deviceUniqueId |
|------|--------|----------------|
| 清应用数据 / 恢复出厂 | Android ID 变 | 不变 |
| 改 persist 里的 MAC 并写回 | Wi-Fi MAC 变；persist 镜像 64 MiB | 不变 |
| 删 persist/data 下 4 个 provisioning 目录，并清空 `/data/vendor/mediadrm` 后重启 | `ay64.dat`、`ay64.dat6`、`usgtable.bin` 等上层密钥文件哈希全变 | 不变 |
| 只 hook `MediaDrm.getPropertyByteArray` | Java 调用方看到伪造值 | native / TEE 真值仍在；双路径不一致即异常 |

清 provisioning 只重生了上层密钥文件。派生 ID 的根 KeyBox 仍在 TEE，所以对外 ID 不动。MAC 是可改写弱锚点，不能拿来冒充设备身份。

## 5. 为什么普通改写无效

1. **存储**：KeyBox 在 TEE 与 RPMB 一次写入区，普通 OS 默认无写权限。
2. **派生**：L1 在 TEE 内做 key 处理与 ID 派生，离开硬件后难以伪造同一值。
3. **信任链**：provisioning 与 License Server 绑定同一 KeyBox。
4. **服务端**：ID 要过证书请求链，不是客户端单方字段。

## 6. 三条取值路径

三条路径最终都落到同一 Widevine HAL。真值应一致；不一致本身就是双路径判据。Widevine UUID 固定为 `EDEF8BA9-79D6-4ACE-A3C8-27DCD51D21ED`。

**Java**：`android.media.MediaDrm.getPropertyByteArray("deviceUniqueId")`，再 Base64。这是标准公开 API。

**NDK**：`AMediaDrm_createByUUID` + `AMediaDrm_getByteArrayProperty`，链 `mediandk`。

**HAL 直连**：不经 mediandk，对 `libwvhidl`（HIDL）或 `libwvaidl`（AIDL）调 `getPropertyByteArray`。调用方是 native 进程，绕开 Java `MediaDrmService`，用来做「独立取值」。

只改其中一条的返回值，另外两条仍应对上真值。

## 7. 服务端交叉验证

服务端不该只信客户端上报的一个字符串。原文把校验方定为服务端，把客户端（含被 hook 的进程）当不可信来源。

| 手段 | 在防什么 | 可信来源 |
|------|----------|----------|
| Java `MediaDrm` 与 native HAL 各取一次比对 | 只 hook 了 Java | 客户端 native 实测 |
| Key Attestation：Keystore 带 `attestationChallenge` 出链，服务端验 Google Hardware Attestation Root，读 `rootOfTrust.verifiedBootState` / `deviceLocked` / `verifiedBootKey` / `verifiedBootHash` | 解锁 / 刷机 / 改系统属性 | TEE 签名 + 服务端验签 |
| Play Integrity：服务端解密 verdict，看 `deviceIntegrity` 是否含 `MEETS_DEVICE_INTEGRITY` / `MEETS_STRONG_INTEGRITY` | root / 解锁 / 完整性降级 | Play 服务 + TEE |
| Widevine `securityLevel`（L1/L2/L3）与 `provisioningStatus` | DRM 链路被破坏 | Widevine HAL；单点易误伤，只作辅助 |
| `deviceUniqueId` 与 Build / SoC / GPU / 传感器校准哈希做画像对照 | 只改部分标识 | 服务端加权融合，单条不足以下判 |

Key Attestation 的要点是挑战码一次性、根证书合法、`verifiedBootState` 为锁定态。解锁 Bootloader 后状态或 boot key 哈希会变，不依赖客户端自报。

Play Integrity 令牌必须由服务端验签。客户端进程里看到的「已通过」不等于服务端看到的同一份 verdict。

## 8. 完整性修复改不了身份取值

市面常见的「补信任链」和「改设备 ID」不是同一件事。

**Play Integrity Fix 一类模块**拦的是客户端进程里的 Integrity 请求/返回，把本机看到的判定改成看起来正常，并藏 root / 模块痕迹。它只作用在客户端可见层。令牌最终要服务端解密验签；服务端独立复核时，改客户端返回值改不了签名结果。

**向本机加载一份已签发 keybox** 动的是本地信任根。它不是设备自签，而是把签发方已认可的资质放到这台机器上。服务端若只认「这份 keybox 是否仍在签发/吊销名单里」，这一维可能被弥合；是否同时核对其它环节，取决于业务。原文把它和本地自签区分开：奏效条件是签发链路被认可，且尚未吊销。

这两类手段解决的是 **环境完整性**。`deviceUniqueId` 是 **身份取值**。完整性「全绿」不改变 HAL 从 TEE KeyBox 派生出的那个 ID。

因此：

- 只 hook Java 返回值：PIF / keybox 模块不参与这次取值；native 独立路径或 provisioning 核对仍会暴露。
- 改 KeyBox 本体：在 TEE / RPMB 里，软件层模块够不到。

## 9. 和 PC 端不是同一题

| 维度 | PC ACE | 安卓 `deviceUniqueId` |
|------|--------|------------------------|
| 载体 | SMBIOS / DMI / 磁盘序列号 / MAC | TEE / RPMB / KeyBox |
| 默认可写性 | OS 可写固件表或注册表 | 专用安全硬件持有 |
| 服务端背书 | 往往停在客户端自报 | 还要过 provisioning 证书链 |

PC 上改硬件 ID 的工具不能平移到安卓这条链。

## 10. 结论

ACE 用单个 `deviceUniqueId` 做设备级拉黑，靠的不是「字段多」，而是：

1. 硬件派生，存在 TEE / RPMB，不在普通文件；
2. 客户端全链路取值，随常规上报进 native 再 UDP 加密发出；
3. 刷机常常同时碰到「ID 改不动」和「AVB / Attestation 断裂」；
4. 只改返回值，容易死在双路径、provisioning 和跨字段画像上。

对分析者的直接含义：把 Android ID、MAC、应用目录当设备身份，会和 ACE 用的硬锚点错位。协议客户端或真机实验若要声明「同一台设备」，至少要写清取样路径是 Java、NDK 还是 HAL，以及有没有和 attestation / Play Integrity 一起看。

## 参考

- Neodyme, *Diving into the depths of Widevine L3*: https://neodyme.io/de/blog/widevine_l3/
- Quarkslab, *Bypassing Android Hardware Attestation*: https://blog.quarkslab.com/bypassing-android-hardware-attestation.html
- Widevine Device Security: https://widevine.org/solutions/widevine-drm
- AOSP AVB 2.0: https://source.android.com/docs/security/features/verifiedboot/avb
- Play Integrity verdict: https://developer.android.com/google/play/integrity/verdict

## 速查

| 问题 | 先看 |
|------|------|
| 刷机 / 恢复出厂后仍被认成旧设备 | 第 1、4、5 节：ID 不在文件系统 |
| 清了 `/data/vendor/mediadrm` ID 却没变 | 第 4 节：变的是上层密钥文件 |
| 只 hook 了 `MediaDrm` 仍被打 | 第 3、6、7 节：native / HAL 第二路径 |
| PIF 全绿但仍对不上设备 | 第 8 节：完整性 ≠ 身份 |
| 上报包在哪一层发出 | 第 3.2 节：游戏回调 + `tss_sdk_encryptpacket` + UDP |
| 和纯协议指纹生成是不是一回事 | 不是。那是应用层字段规则；这是 TEE 派生的硬件 ID |
