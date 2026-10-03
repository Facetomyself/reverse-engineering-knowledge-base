---
schema_version: 2
id: chromium-blink-webrtc-candidate-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-blink-webrtc-candidate]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./05-webrtc-ip-randomization.md#二webrtc指纹原理"
    basis: unknown
  - id: s2
    ref: "./05-webrtc-ip-randomization.md#四编译chromium源码来随机webrtc的返回值"
    basis: unknown
  - id: s3
    ref: "./05-webrtc-ip-randomization.md#3编译"
    basis: unknown
  - id: s4
    ref: "./05-webrtc-ip-randomization.md#五还有高手"
    basis: unknown
  - id: s5
    ref: "./05-webrtc-ip-randomization.md#三通过webrtc获取自己的局域网ip"
    basis: unknown
modules:
  - name: parameters
    anchor: parameters
    sources: [s2]
    basis: unknown
    limits: 只读到 candidate() 的替换文本。合成地址字面量不转写。未编译，未抓 ICE。
  - name: risk-control
    anchor: risk-control
    sources: [s1, s3, s5]
    basis: unknown
    limits: 真实 IP 是否仍可被探测是作者陈述。返回空或替换都会破坏部分 WebRTC，这是作者的副作用说明。
  - name: validation
    anchor: validation
    sources: [s3, s4]
    basis: unknown
    limits: browserleaks 已隐藏和 browserscan 仍泄露都是作者自述，本轮没有复访。截图不转写。
relations:
  - type: derived_from
    target: "./05-webrtc-ip-randomization.md#替换为"
tags: [chromium, blink, webrtc]
---

# Chromium Blink ICE candidate 返回值替换

这张卡只定位 `RTCIceCandidate::candidate()` 被换成合成字符串这一处。近邻查询没有目标为 webrtc 或 chromium-blink-webrtc-candidate 的参考卡。合集首页还提到 SDP 替换，本篇没有 `rtc_session_description.cc`。

编译前提被推到另一篇文章。作者同时写下“某一页已隐藏”和“另一页仍能拿到”，所以不能把本篇收成已验收流程。

<a id="parameters"></a>
## 参数机制

文件是 `third_party/blink/renderer/modules/peerconnection/rtc_ice_candidate.cc`。替换文本把 `platform_candidate_->Candidate()` 注释掉，`candidate()` 改为 `return String(generateRandomIP());`。辅助函数签名是 `std::string generateRandomIP()`。函数体里的地址字面量不转写；这里只记录返回值不再是平台 candidate。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 打开的文件是 third_party/blink/renderer/modules/peerconnection/rtc_ice_candidate.cc | s2，打开文件那一行 | unknown | 本篇点名的路径 | 无版本号 |
| C2 | 原返回被写成 //return platform_candidate_->Candidate(); | s2，替换函数 | unknown | 归档中的替换文本 | 未对照上游源码行 |
| C3 | 新返回是 return String(generateRandomIP()); | s2，替换函数 | unknown | 该 return 语句 | 不记录合成地址字面量 |
| C4 | 辅助函数以 std::string generateRandomIP() 开头 | s2，替换文本 | unknown | 函数签名 | 函数体字面量不转写 |

<a id="risk-control"></a>
## 检测面与副作用

作者把 WebRTC 指纹里最有用的部分写成获取用户的真是 IP，并写即使用户使用 VPN 或代理、隐藏公网 IP，也依旧能够被探测到。控制台脚本用 `let ipRegex = /([0-9]{1,3}(\.[0-9]{1,3}){3})/;` 从 candidate 字符串取点分地址。作者写网站从 `evt.candidate.candidate` 取值，所以直接篡改这个返回值。返回空也可以，两种方式都相当于禁用部分 WebRTC，可能导致 WebRTC 不可用。

示例输出行是打码地址，不转写。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 作者把有用信息写成获取用户的真是IP，并称隐藏公网 IP 后也依旧能够被探测到 | s1，指纹原理 | unknown | 作者对 WebRTC 指纹的定义 | 错字保留；未验证 VPN 场景 |
| C6 | 脚本用 let ipRegex = /([0-9]{1,3}(\.[0-9]{1,3}){3})/; 从 candidate 取地址 | s5，控制台脚本 | unknown | 归档中的这段脚本 | 不是唯一的 ICE 解析写法 |
| C7 | 作者写既然网站从evt.candidate.candidate里获取我们的ip，就篡改返回值；返回空可能导致webRTC不可用 | s3，编译后的注意 | unknown | 作者对这两处副作用的说明 | 未实测通话是否失败 |

<a id="validation"></a>
## 验证与限制

作者称再次访问 browserleaks 的 WebRTC 页后，真实 IP 已被隐藏。下一段又称还有其他网站可以获取真实 IP，并点名 browserscan。两句都只引用作者原话。配图没有可引用正文。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C8 | 再次访问 browserleaks 的 WebRTC 页后，作者写发现真实ip已被隐藏 | s3 | unknown | 作者对这一页的自述 | 本轮未复访 |
| C9 | 作者接着点名 https://www.browserscan.net/ 仍能拿到真实 IP | s4 | unknown | 作者点名的另一页 | 与 C8 并列，不能合成“已经隐藏” |
