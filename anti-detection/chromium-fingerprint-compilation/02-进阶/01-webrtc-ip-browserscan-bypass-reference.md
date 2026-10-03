---
schema_version: 2
id: chromium-webrtc-ice-json-reference
document_type: reference
original_date: unknown
archived_date: '2026-10-02'
scope:
  targets: [chromium-webrtc-ice]
  client: chromium
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./01-webrtc-ip-browserscan-bypass.md#四核心逻辑"
    basis: unknown
  - id: s2
    ref: "./01-webrtc-ip-browserscan-bypass.md#五修改源码"
    basis: unknown
  - id: s3
    ref: "./01-webrtc-ip-browserscan-bypass.md#八过browserleaks"
    basis: unknown
  - id: s4
    ref: "./01-webrtc-ip-browserscan-bypass.md#七测试成果"
    basis: unknown
modules:
  - name: interfaces
    anchor: interfaces
    sources: [s1, s2, s3]
    basis: unknown
    limits: 只记录作者点名的 ICE 四个成员、SDP getter 和 renderer 命令行转发。不复写替换函数。Chromium 版本未知。
  - name: parameters
    anchor: parameters
    sources: [s2, s3]
    basis: unknown
    limits: 只保留开关名和“有开关才替换、否则原样返回”的分支。不记录地址字面量或正则文本。
  - name: risk-control
    anchor: risk-control
    sources: [s1, s3]
    basis: unknown
    limits: BrowserScan 与 BrowserLeaks 的差异是作者对两份读取面的说明，不是本轮抓到的页面脚本。
  - name: validation
    anchor: validation
    sources: [s4, s3]
    basis: unknown
    limits: “已经过了”和截图都是作者自述。本轮未看图、未编译、未访问这些站点。
relations:
  - type: derived_from
    target: "./01-webrtc-ip-browserscan-bypass.md#四核心逻辑"
tags: [chromium, webrtc, ice-candidate, unknown]
---

# Chromium ICE JSON 与 SDP 的地址接缝

这张卡检索的是：为什么作者认为只改 ICE candidate 对象会在 BrowserScan 上失效，以及后来又把哪几个读取面和哪一个进程边界算进同一开关。不提供可编译替换，不记录任何地址样值。

<a id="interfaces"></a>
## 接口边界

作者把 BrowserScan 路径定在 `JSON.stringify(evt.candidate)`，并写明 Chromium 用 `RTCIceCandidate::toJSONForBinding` 实现这次序列化。随后打开的文件是 `\third_party\blink\renderer\modules\peerconnection\rtc_ice_candidate.cc`。粘贴片段改了四个成员：`candidate()`、`address()`、`relatedAddress()` 和 `toJSONForBinding`。`toJSONForBinding` 里只有 `candidate` 字段走替换；`sdpMid`、`sdpMLineIndex` 和 `usernameFragment` 仍从原来的 platform 对象写入。

BrowserLeaks 一节另开 `/third_party/blink/renderer/modules/peerconnection/rtc_session_description.cc`，对象是 `RTCSessionDescription::sdp()`。

开关若只加在浏览器进程，渲染进程读不到。作者因此在 `\content\browser\renderer_host\render_process_host_impl.cc` 里，当浏览器进程带有该开关时，用 `AppendSwitchASCII` 抄到 renderer 的命令行。

<a id="parameters"></a>
## 开关

开关名是 `webrtc-ip`。作者的辅助函数在 `HasSwitch("webrtc-ip")` 时替换输入中的地址形态文本，否则返回原字符串。同一开关名出现在 ICE 文件和 SDP 文件。本卡不记录示例地址，也不记录正则。

<a id="risk-control"></a>
## 两条读取面

作者写，先前改 `evt.candidate` 的值，一旦包上 `JSON.stringify()` 就好像失效。这是 BrowserScan 这一节的核心，不是对 BrowserLeaks 的结论。BrowserLeaks 被单独放到 SDP getter。检测样例同时注册了 `icecandidate` 监听和 `onicecandidate`；监听回调的形参是 `evt`，其中一行却写了 `event.candidate`。这只说明样例文本不可直接当采集脚本。

<a id="validation"></a>
## 验证边界

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C16 | 作者把 BrowserScan 写成检测站点 | 来源第 241 行 | unknown | 作者列出的 URL | 本轮未访问 |
| C17 | 作者把 Pixelscan 写成检测站点 | 来源第 242 行 | unknown | 作者列出的 URL | 本轮未访问 |
| C19 | 作者称 BrowserScan 的 WebRTC 检测已经可以通过 | s4，来源第 255 行 | unknown | 作者当时的构建和截图 | 不是本轮观察；图未审 |
| C20 | 作者称 Pixelscan 的指定结果也通过了 | s4，来源第 258 行 | unknown | 同上 | 图未审 |
| C18 | 若以前改过 WebRTC，作者只提示可能要还原 | s4，来源第 247 行 | unknown | 作者的前置提醒 | 没有失败时的停止条件 |

前提是读者已经能独立编译一个指纹浏览器。文末没有把“站点仍显示原地址”定义成失败出口，Chromium 版本也未给出，所以不建 procedure。全部结论停留在 source-report；本轮没有运行观察。
