# Widevine L3 视频下载工程：CDM 自提取、license 重放与解密管道

> 来源: `workspace/ktv-smart-jp-download`
> 原始发布时间: 2026-09-22
> 归档日期: 2026-09-22
> 分类: drm-content-acquisition
>
> 从一次日本 VOD 站点（videomarket / カンテレドーガ）租赁剧集的本地化下载中提炼：
> 浏览器播放链路定位、Android 真机 L3 CDM 自提取、pywidevine license 重放、Bento4/ffmpeg
> 解密合并的完整可复用管道。工具全部为公开 DRM 研究/测试工具（KeyDive、pywidevine、
> mp4decrypt），适用边界是自有账号已付费租赁内容的个人备份与 DRM 安全研究，
> 不得用于未授权内容的获取与分发。

## 结论先行

1. **Widevine L3 内容下载是一条七步管道**，每步都有成熟工具：播放链路定位（浏览器
   抓包）→ manifest/PSSH 提取 → L3 CDM device 自提取（Android 真机 + KeyDive）→
   license 请求重放（pywidevine）→ content key 获取 → 加密媒体下载 → mp4decrypt +
   ffmpeg 合并。整条链路对任何用 `shaka-player + Widevine CENC` 的 Web VOD 站点适用。
2. **不要试图提取桌面浏览器 CDM**。Firefox 的 `widevinecdm.dll` 4.10.3050（2024+ 版本）
   没有现成 dumper；正确的路径是用自己的 Android 真机（root + frida）提取 L3 CDM，
   5 分钟内完成，产出 `.wvd` 直接被 pywidevine 消费。
3. **PSSH 必须按 system ID 选**：manifest 里常混着 PlayReady（`9a04f079-...`）和
   Widevine（`edef8ba9-...`）两组 PSSH，用错会得到 license server 的
   `E2006 failed to find any keys`。
4. **license 重放不需要抓浏览器的 challenge**：只要 license URL + 自己的 device，
   pywidevine 可以自产 challenge；带 UA/Referer 即可过大多数 wvks 类端点。
5. **网络出口质量是第一道坎**：日本站点对海外直连超时、对非日 IP 返回错误码 10003。
   播放失败先查代理节点的连通性，再查 DRM 本身。

## 七步管道

```
[1] 播放链路定位          浏览器抓包: token API → streaming API → manifest → license
[2] manifest 分析          mpd 结构 (on-demand vs segment)、PSSH、KID、分片 URL
[3] L3 CDM 自提取         Android 真机 (root+frida) + KeyDive → client_id.bin/private_key.pem/.wvd
[4] license 重放          pywidevine: 自产 challenge → POST license server → parse → KID:KEY
[5] 加密媒体下载          curl 带 UA/Referer 拉分片 (on-demand 单文件最省事)
[6] 解密                  mp4decrypt --key KID:KEY
[7] 合并                  ffmpeg -c copy
```

### [1] 播放链路定位

用浏览器打开已租赁剧集页，从 `performance.getEntriesByType('resource')` 过滤
`videomarket|mpd|m3u8|license|wvks|drm` 关键字，拿到三类 URL：

- **manifest**：`*.mpd`（DASH CENC）——media 本体入口
- **license**：`wvks.*.jp/?ticket=<hex>` 或含 `license` 的端点——key 发放处，ticket 是一次性短时令牌
- **playback token API**：站点自身的 token 发放接口（POST，带登录 cookie）——license URL 里的 ticket 由它签发

典型链路（videomarket）：`vm_access_token.php` → `vm_play_token.php` → `pf-api.*/v1/play/*/streaming/web`
（返回 manifest URL + license ticket）→ 播放器 shaka 拉 manifest → EME 流程请求 license。

要点：license 请求发生在播放器初始化时（页面 init 即触发，早于任何人工点击），
事后抓包拿不到 body 没关系——**重放阶段不需要浏览器的 challenge**。

### [2] manifest 分析

```bash
curl -x http://127.0.0.1:<proxy> -H "Referer: <site>" -H "User-Agent: <Firefox UA>" \
  -o manifest.mpd "<manifest url>"
```

必查字段：

| 字段 | 作用 |
|------|------|
| `ContentProtection` 的 `default_KID` | 与最终 KID:KEY 交叉验证 |
| `cenc:pssh`（可能有 2 组） | 按 system ID 区分：`edef8ba9-79d6-4ace-a3c8-27dcd51d21ed` 才是 Widevine |
| `<BaseURL>` | **on-demand**（每个 Representation 一个完整 mp4）还是 SegmentTemplate（分片）——前者下载一步到位 |
| Representation 的 height/bandwidth/codec | 选画质档位 |

PSSH 判别脚本（base64 解码后看 12:28 字节的 system ID）：

```python
import base64, re
raw = base64.b64decode(pssh_b64)
sysid = raw[12:28]
# edef8ba979d64acea3c827dcd51d21ed => Widevine
# 9a04f07998404286ab92e65be0885f95 => PlayReady
```

### [3] L3 CDM 自提取（KeyDive + Android 真机）

前提：root 的 Android 设备（Pixel 6 实测通过）+ frida-server 运行中 + adb 连接。

```bash
# 隔离 venv（keydive 会拉低 protobuf 版本，勿污染主 venv）
python -m venv keydive-venv
keydive-venv/Scripts/pip install keydive pywidevine
# ADB 需在 PATH
export PATH="/path/to/adb:$PATH"
keydive -w -o runtime/cdm > keydive.log 2>&1 &
```

坑位（实测）：

1. **KeyDive 的 `-a player` 自动模式会卡在 GitHub 下载 Kaltura 测试 APK**（直连 SSL
   中断）。解法：手动 `curl` 下载 APK + `adb install`，然后不带 `-a` 跑纯 hook 模式。
2. **app 内按钮（Provision/Refresh/Test DRM Playback）自动化不稳定**（FAB 菜单
   PopupWindow 点击时灵时不灵）。**触发 DRM 播放的最简单方法：设备 Chrome 打开
   `https://bitmovin.com/demos/drm`**——页面加载即触发 MediaDrm session，hook 立即
   拦截到 keybox + RSA private key，全程无需 UI 操作。
3. **KeyDive 输出经管道会被全缓冲**，实时状态看不了。用 `> file 2>&1` 直写文件。
4. KeyDive 会在 hook 层面禁用 `liboemcrypto.so`（L3 化），frida 进程退出即恢复，
   不留残留改动；验证：`file /vendor/lib64/liboemcrypto.so` 仍是正常 ELF。
5. 设备需能访问 license/CDN（海外）：`adb reverse tcp:8085 tcp:<本机clash>` +
   `settings put global http_proxy 127.0.0.1:8085`。

成功标志：日志出现 `Exporting file: ...client_id.bin` / `private_key.pem` / `*.wvd`。

### [4] license 重放（pywidevine）

```python
from pywidevine.device import Device
from pywidevine.cdm import Cdm
from pywidevine.pssh import PSSH
import requests

device = Device.load("xxx_l3.wvd")
cdm = Cdm.from_device(device)
session = cdm.open()
challenge = cdm.get_license_challenge(session, PSSH(PSSH_B64))
resp = requests.post(
    "https://wvks.example.jp/?ticket=<ticket>",
    data=challenge,
    headers={
        "User-Agent": "<Firefox UA>",
        "Referer": "<site>/",
        "Content-Type": "application/octet-stream",
    }, timeout=30)
cdm.parse_license(session, resp.content)
for k in cdm.get_keys(session):
    print(k.kid, k.key.hex())
```

坑位：

- **PSSH 选错 → `HTTP 400 {Code: "E2006", Message: "failed to find any keys"}`**：
  用了 PlayReady PSSH 的典型症状。换 system ID 为 `edef8ba9` 的那组。
- ticket 有短时效：从播放页 performance 里抓到的 ticket，重放要快（分钟级）。
  过期就重新加载播放页拿新 ticket。
- 若 server 校验浏览器环境（如 EME 的 service certificate），先用服务证书：
  `cdm.set_service_certificate(session, cdm.sign_service_certificate(session, cert))`。
- 输出里 `00000000-...` 的 key 是 session key，真正的 content key 的 KID 应与
  manifest `default_KID` 一致。

### [5]-[7] 下载、解密、合并

```bash
# on-demand 结构：整文件下载（Referer 必带，Akamai 类 CDN 会校验）
curl -x http://127.0.0.1:<proxy> -H "Referer: <site>/" -H "User-Agent: <Firefox UA>" \
  -o enc.mp4 "<base>/<file>.mp4"

mp4decrypt --key <KID_HEX>:<KEY_HEX> enc.mp4 dec.mp4   # Bento4
ffmpeg -y -i video-dec.mp4 -i audio-dec.mp4 -c copy -movflags +faststart out.mp4
```

工具获取：Bento4 官方 zip（bok.net）自带 `mp4decrypt.exe`；ffmpeg 用 BtbN win64-gpl
静态构建。两者都放项目 `tools/` 下，不进系统。

## videomarket（カンテレドーガ）案例速查

- 站点：ktv-smart.jp；视频服务商 videomarket；播放器 shaka-player + vm-player.js
- 播放链路：`/store/api/vm_access_token.php` → `/store/api/vm_play_token.php`（POST
  JSON，带登录 cookie）→ `pf-api.videomarket.jp/v1/play/ktv/streaming/web` →
  manifest `vmdash-cenc.akamaized.net/.../abr/<storyId>/<r>/<hash>_A-SD.mpd` +
  license `wvks.videomarket.jp/?ticket=<hex>`
- 剧集页 `movie.php?id=A<storyId><ep>999H01`；manifest 内 `default_KID` 与
  `cenc:pssh`（Widevine 组）带 `product_code` JSON
- 下载 URL：manifest 的 `<BaseURL>` 拼 CDN 目录前缀，带 `Referer: https://ktv-smart.jp/`
- 画质档：A-0..A-4 视频（240p~480p）+ A-0/A-1/A-3 音频（48k~192k），on-demand 单文件
- 网络：必须日本出口（非日 IP 报 errorCode 10003）；直连超时是 CDN 屏蔽海外，
  经代理即可
- 会话：登录 cookie `Authlogin` 为会话级，浏览器退出即失效；租赁记录绑定账号，
  重新登录后恢复

## 工具版本（2026-09 实测）

| 工具 | 版本 | 说明 |
|------|------|------|
| KeyDive | 3.0.6 | Android L3 CDM 提取；SDK>33 需 frida-server ≥16.6 |
| frida | 17.15.3 | 本机客户端 + Pixel 6 server（Android 15 / API 35 通过） |
| pywidevine | 最新 | device 加载 + challenge/license |
| Bento4 | 1.6.0-641 | mp4decrypt / mp4dump |
| ffmpeg | master-win64-gpl | 合并用 `-c copy` 即可 |
| Widevine CDM (设备) | 19.0.1 (Pixel 6) | 提取产出 L3 wvd；桌面 Firefox 4.10.3050 无现成 dumper |

## 与既有知识的关系

- 设备指纹/KeyBox 话题（Widevine `deviceUniqueId` 的 TEE/RPMB 锚点）见
  `anti-detection/android-ace-deviceuniqueid.md`——本文提取的 L3 device 与 TEE KeyBox
  是不同层面，L3 软解 device 不含硬件锚点。
- 浏览器采集器稳定性（ruyipage 多实例长跑）见
  `collection-engineering/browser-collector-stability.md`——本流程单实例短会话，
  不触发其崩溃条件。
- 代理出口管理见 `collection-engineering/mihomo-dialer-proxy-chain.md` 与
  proxy-usage skill。
