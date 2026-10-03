---
schema_version: 2
id: drm-videomarket-playback-boundary
document_type: reference
original_date: "2026-09-22"
archived_date: unknown
scope:
  targets: [videomarket]
  client: web
  version: "ktv-smart.jp / videomarket; source-reported 2026-09; shaka-player"
  observed_at: "2026-09-22"
sources:
  - id: s0
    ref: "./widevine-l3-video-download.md#widevine-l3-视频下载工程cdm-自提取license-重放与解密管道"
    basis: source-report
  - id: s1
    ref: "./widevine-l3-video-download.md#1-播放链路定位"
    basis: source-report
  - id: s2
    ref: "./widevine-l3-video-download.md#2-manifest-分析"
    basis: source-report
  - id: s3
    ref: "./widevine-l3-video-download.md#videomarketカンテレドーガ案例速查"
    basis: source-report
  - id: s4
    ref: "./widevine-l3-video-download.md#结论先行"
    basis: source-report
  - id: s5
    ref: "./widevine-l3-video-download.md#与既有知识的关系"
    basis: source-report
  - id: s6
    ref: "./widevine-l3-video-download.md#工具版本2026-09-实测"
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s0, s1, s3, s4]
    basis: source-report
    limits: 只记录来源描述的 URL 类别和 videomarket 顺序。不包含登录材料、ticket、challenge、device 文件或媒体解密。单站点、单次来源报告，未重放。
  - name: parameters
    anchor: parameters
    sources: [s2, s4]
    basis: source-report
    limits: 只区分公开的 DRM system ID 和来源命名的 KID 对照字段。不记录密钥字节、PSSH 样本或 license 正文。
  - name: risk-control
    anchor: risk-control
    sources: [s3, s4, s5, s6]
    basis: source-report
    limits: 出口错误码和桌面 CDM 缺口都是来源陈述。不提供代理绕过、CDM 提取或 license 重放。L3 软 device 与 ACE 卡里的 TEE KeyBox 不是同一层。
relations:
  - type: derived_from
    target: "./widevine-l3-video-download.md#1-播放链路定位"
tags: [videomarket, Widevine, PSSH, CENC, source-report]
---

# videomarket 播放链路、PSSH 选择与出口边界

这张卡只回答三件事：播放 URL 在来源里分成哪几类、Widevine 与 PlayReady 的 PSSH 如何被来源区分、非目标地区出口会先失败在哪一个错误码。CDM 提取、license 重放和媒体解密留在来源归档，不在这里写成步骤。

来源把适用边界写成自有账号已付费租赁内容的个人备份与 DRM 研究，并写明不得用于未授权内容的获取与分发。该边界是作者声明，不是本轮授权或复测。

<a id="request-chain"></a>
## 播放请求链

来源从已租赁剧集页的资源记录里分出三类 URL，并给出 videomarket 的站点顺序。license 请求发生在播放器初始化，早于人工点击。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 来源样本是日本 VOD 站点 videomarket / カンテレドーガ 的租赁剧集播放 | s0，开篇 | source-report | 该次 ktv-smart.jp 案例 | 不是全类 VOD 的普查 |
| C2 | 播放资源被分成 manifest（mpd / DASH CENC）、license 端点和 playback token API | s1，三类 URL | source-report | 来源使用的浏览器资源过滤 | 不记录过滤实现或响应体；三类分别落在相邻三行 |
| C3 | videomarket 顺序为 vm_access_token.php，然后 vm_play_token.php，然后 pf-api 的 play/streaming/web | s1，典型链路 | source-report | 来源所称 videomarket Web 播放 | 路径中的具体剧集、ticket 和返回体未收录 |
| C4 | 案例站点是 ktv-smart.jp，播放器是 shaka-player + vm-player.js | s3，案例速查 | source-report | 2026-09-22 来源 | 播放器构建号未知 |
| C5 | license 请求发生在播放器初始化 | s1，要点 | source-report | 该播放页 | 不表示此后仍可拿到同一次请求体 |

<a id="parameters"></a>
## PSSH 与 KID 字段

manifest 里可以同时出现两组 PSSH。来源要求按 system ID 选择，并把 `ContentProtection` 的 `default_KID` 当作和最终内容密钥标识交叉验证的字段。`<BaseURL>` 用来区分 on-demand 整文件和 SegmentTemplate，这只说明封装形态。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C6 | system ID edef8ba9-79d6-4ace-a3c8-27dcd51d21ed 被来源标为 Widevine；另一组是 PlayReady | s2，manifest 字段表 | source-report | 来源看到的 mpd | 不提供 PSSH 原文 |
| C7 | 来源写明用错会得到 license server 的错误，下一行文本是 E2006 failed to find any keys | s4，结论第 3 点 | source-report | 该次 license 端点 | 未重放；原因与错误码分属相邻两行 |
| C8 | ContentProtection 的 default_KID 被来源用于和最终 KID:KEY 交叉验证 | s2，manifest 字段 | source-report | 该次 manifest 对照 | 不记录任何密钥字节 |
| C9 | 来源把 shaka-player + Widevine CENC 写成这条观察的站点类型，并外推到同类 Web VOD | s4，结论第 1 点 | source-report | 作者的外推 | 材料只有 videomarket 一例，外推未验证 |

<a id="risk-control"></a>
## 出口、令牌寿命与相邻层

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C10 | 来源称日本站点对海外直连超时，对非日 IP 返回错误码 10003；播放失败应先看出口 | s4，结论第 5 点 | source-report | 该次 videomarket/CDN 观察 | 不提供可用代理或节点 |
| C11 | 案例速查把同一现象写成 errorCode 10003，并称为必须日本出口 | s3，网络条 | source-report | ktv-smart.jp 该次租赁播放 | 错误码含义没有服务端确认 |
| C12 | license ticket 被描述为一次性短时令牌 | s1，license URL 类 | source-report | 来源抓到的该类端点 | 不记录令牌值或刷新实现 |
| C13 | 来源称桌面 Firefox widevinecdm 4.10.3050 没有现成 dumper | s6，工具版本表 | source-report | 该版本号的作者检索 | 不由此推出其他提取路线 |
| C14 | 来源把本文的 L3 device 与 TEE KeyBox 分成不同层 | s5，与既有知识 | source-report | 与 ACE deviceUniqueId 档案的边界 | 不修改 ACE 卡的硬件锚点结论 |

ACE 的 Widevine `deviceUniqueId` 见 [android-ace-deviceuniqueid.md](../anti-detection/android-ace-deviceuniqueid.md)。那张卡的对象是硬件派生身份，不是本站点的播放 URL。

## 验证与限制

- 没有本地运行目录。全部结论保持 source-report。
- 不收录 CDM 文件、license 重放、内容密钥和媒体解密。来源归档里的七步管道因此不升为 procedure。
- 未知：当前 license server 是否仍返回 E2006、10003 是否稳定、manifest 是 on-demand 还是分片以外的第三种封装、登录会话字段的当前寿命。
