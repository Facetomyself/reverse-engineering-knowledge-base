---
schema_version: 2
id: paopao-20260302-protocol-fingerprint-reference
document_type: reference
original_date: '2026-03-02'
archived_date: '2026-10-02'
scope:
  targets:
    - ja3
    - peetprint
    - tcp-fingerprint
    - http2-fingerprint
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./paopao-20260302-01.md#ja3-指纹的原理"
    basis: source-report
  - id: s2
    ref: "./paopao-20260302-01.md#11-tcpip-协议栈指纹"
    basis: source-report
  - id: s3
    ref: "./paopao-20260302-01.md#http2-指纹"
    basis: source-report
  - id: s4
    ref: "./paopao-20260302-01.md#tls-对抗grease-机制与底层库魔改"
    basis: source-report
  - id: s5
    ref: "./paopao-20260302-01.md#22-主动一致性检测"
    basis: source-report
  - id: s6
    ref: "./paopao-20260302-01.md#34-自动化工具痕迹检测"
    basis: source-report
  - id: s7
    ref: "./paopao-20260302-01.md#ja3-的局限与演进"
    basis: source-report
  - id: s8
    ref: "./paopao-20260302-01.md#33-用户输入与行为分析"
    basis: source-report
  - id: s9
    ref: "./paopao-20260302-01.md#26-时间和时区"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1, s2, s3, s7]
    basis: source-report
    limits: 只保留来源对 JA3 拼接、peetprint 排序、TCP 选项顺序和 HTTP/2 帧特征的描述。未复算哈希，未转写 SETTINGS 数值。
  - name: risk-control
    anchor: risk-control
    sources: [s1, s4, s6, s8]
    basis: source-report
    limits: 握手暴露、GREASE、uTLS、UA 与内核标记、hidden 输入和 isTrusted 都是来源陈述。不提供改浏览器或发送输入事件的步骤。
  - name: validation
    anchor: validation
    sources: [s5, s7, s9]
    basis: source-report
    limits: JA3 对扩展顺序敏感、matchMedia、NaN 字节和 IP/时区都未在本轮执行。粘连函数不当成可运行探针。
  - name: interfaces
    anchor: interfaces
    sources: [s4, s7]
    basis: source-report
    limits: 在线入口和 BoringSSL/uTLS 只是来源点名。OpenSSL 源文件清单不转入。
relations:
  - type: derived_from
    target: "./paopao-20260302-01.md#ja3-指纹的原理"
tags:
  - ja3
  - peetprint
  - tcp-fingerprint
  - http2-fingerprint
  - source-report
---

# JA3、TCP 选项顺序与 HTTP/2 被动指纹

这张卡只回答：来源如何描述 JA3、peetprint、TCP/IP 栈指纹，以及它称为 Akamai Hash 的 HTTP/2 被动指纹，各自看哪些字段；它又把哪些不一致写成暴露。不提供改库或伪造输入的步骤。

Canvas、字体、WebGL 的对象模型仍以 `browser-fingerprint` 的检测面为准。navigator 与事件对象的语义仍以对应对象卡为准。Akamai Bot Manager 的请求链和验收口径仍以产品卡为准；本卡不使用 target `akamai`，避免和那两块模块叠在一起。

来源没有可公开定位的原文 URL。是否成立只到作者自述。示例扩展 ID、SETTINGS 数值和 OpenSSL 源文件清单不进入本卡。

<a id="parameters"></a>
## 参数机制

来源从 Client Hello 取五类字段，拼成字符串再算 MD5，并称之为 JA3。它同时写明做风控时可以只看具体值。

> JA3 从 Client Hello 中收集了更多信息，提取以下 5 个关键字段：

>     TLSVersion, Ciphers, Extensions, EllipticCurves, EllipticCurvePointFormats

> 将这些字段的值拼接成字符串，再计算 MD5 哈希值，即可得到一个稳定的客户端指纹。不过在做风控时关注具体值就好，不一定非要算 hash。

五类名字是 TLSVersion、Ciphers、Extensions、EllipticCurves、EllipticCurvePointFormats。JA3S 被写成看 Server Hello，更多用于识别服务端资产，没有字段表。

扩展顺序被写成会改变 JA3 Hash，尽管来源也写 RFC 认为顺序不影响握手语义。peetprint 被写成多收一些信息，并且先把扩展顺序规范化（排序）再算。

> 因此社区提出了  ** peetprint  ** 等优化方案——分析更多信息，并将扩展顺序规范化（排序）后再算指纹。

TCP/IP 侧，来源点名 IHL、TTL、初始窗口、DF，以及 MSS、Window Scale、SACK、Timestamp 等选项。它把选项排列顺序写成极强的操作系统指纹。TTL 默认值写成 Windows 128、Linux/macOS 64，并写明会随跳数减小。

>   * ** TTL（Time To Live）  ** ：不同操作系统的默认 TTL 值不同（Windows 默认 128，Linux/macOS 默认 64）。虽然 TTL 会随路由跳数递减，但结合其他特征仍具参考价值，易受路由等影响。

>   * ** TCP 选项字段（Options）  ** ：如 MSS（最大报文段长度）、Window Scale（窗口缩放因子）、SACK（选择性确认）、Timestamp（时间戳）等。  ** 这些选项的排列顺序（Options Order）是极强的操作系统指纹  ** ，不同内核实现中选项的排列顺序几乎是固定的。

HTTP/1 的头顺序被写成 RFC 不严格规定，但客户端拼接顺序几乎固定。HTTP/2 里，Cookie 多次出现还是用逗号合成一次，被写成一个指纹点；来源说浏览器多半是前者。

HTTP/2 被动指纹被来源称为 Akamai Hash：连接建立时的协商帧默认值和顺序，拼接后再哈希。伪头顺序单独算一个识别点。它点名四块：

> ` ），它们的顺序也是一个识别点。HTTP 头字段的顺序一直是个指纹识别点，而伪头进一步增加了辨识维度。

| 来源叫法 | 来源写成的识别点 |
|---|---|
| 伪头顺序 | `:scheme`、`:method`、`:authority`、`:path` 的顺序 |
| SETTINGS | 连接初期 SETTINGS 默认值的组合 |
| WINDOW_UPDATE | 初始帧的策略和 Increment Size |
| PRIORITY | 优先级帧、权重和依赖树 |

>   * ** SETTINGS 帧参数  ** ：连接建立时客户端发送的 SETTINGS 帧宣告其配置（如  ` SETTINGS_HEADER_TABLE_SIZE  ` 、  ` SETTINGS_MAX_CONCURRENT_STREAMS  ` 、  ` SETTINGS_INITIAL_WINDOW_SIZE  ` 等），这些默认值组合构成了强指纹

>   * ** WINDOW_UPDATE 帧  ** ：不同客户端在连接初始阶段发送 WINDOW_UPDATE 帧的策略和步长（Increment Size）不同

> 还有优先级帧（PRIORITY Frame）和帧里的优先级字段，流的优先级权重和依赖树结构各浏览器的实现逻辑差异巨大，都得认真对比。

<a id="risk-control"></a>
## 对照时来源说风控看什么

协议层的价值被放在握手，而不是页面脚本。来源称 WAF 或 CDN 在连接建立时就能看到；Python `requests` 或 Go 原生 HTTP 库，即使 JS 环境伪造完整，也会在握手暴露。

> 协议层指纹的核心价值在于：  ** 在建立网络连接的瞬间即可被服务端或中间设备（如 WAF、CDN）观测到  ** 。这意味着，如果攻击者使用 Python

> ` requests  ` 或 Go 原生 HTTP 库，即使伪造了完美的 JS 环境，也会在握手阶段暴露身份。

对抗被分成白名单（模拟真实指纹）和黑名单（只挡明显错误的握手）。来源说成熟做法是前者。Chrome 从 110 起默认 GREASE，用随机扩展顺序去撞服务端实现错误；它点名除 `pre_shared_key` 必须最后外，扩展顺序可以变。ALPS 被写成 OpenSSL 没有的扩展。

> Chrome 从 110 版开始默认启用 GREASE 机制（参见 TLS 中的 GREASE 机制），通过随机化扩展顺序（TLS RFC 4.2 规定除

> ` pre_shared_key  ` 必须是最后一个外，不同类型的扩展顺序任意）来尽快发现服务端 TLS 实施错误。

库被点了三条路，这里只保留来源的定性：换成 BoringSSL；用 Go 的 uTLS；或者改 OpenSSL。uTLS 被写成实质上只发 fake 包，功能没做完，服务端再主动识别仍会对不上。改 OpenSSL 的源文件清单不在本卡。

>   * ** 专用对抗库  ** ：使用 Go 语言的 uTLS 库，专为对抗指纹而生。不过它实质上只是能发一些 fake 包，实际并未实现功能，如果服务端再主动识别依然得露馅儿

应用层不一致只保留来源写明「立刻暴露」的对照，不重列 navigator 字段表。`typeof window.InstallTrigger !== 'undefined'` 为真，而 UA 声称 Chrome，被写成伪造。IP 在美国而时区在中国，被写成直接露馅。页面处于 `hidden` 时仍有点击或输入，被写成极可能是自动化。

> > ** 举例  ** ：风控脚本在页面加载时执行  ` typeof window.InstallTrigger !== 'undefined'  `

> > Chrome，就立刻暴露了伪造。

> 因此，风控脚本可以这样利用：如果检测到用户在页面处于  ` hidden  ` 状态时仍然在执行点击、输入等操作，那么这极可能是自动化行为。另外  `

`isTrusted` 被写成只读。来源称用 `EventTarget.dispatchEvent()` 生成的事件，该属性一定是 false；又称 CDP Input 事件上该值是 true，并且 JS 层改不了它。本卡只记录这个对照，不写如何发送 Input 事件或如何改浏览器。

> 属性一定会是  ` false  ` **。

> > DevTools Protocol）发出的 Input 事件，其  ` isTrusted  ` 值是  ` true  ` ！

`navigator.webdriver` 被写成默认 false，并称按 W3C，被自动化时要设为 true。可见性、精度时间和若干自动化属性名出现在后文清单里；删除属性的句子不转成步骤。

<a id="validation"></a>
## 来源用来核对「像不像」的口径

JA3 的已知裂口被写成：扩展顺序一变，哈希就变，所以不能只存一张哈希。peetprint 用排序来躲这个裂口。TTL 不能单独当操作系统结论，因为跳数会把它减小。

>   1. RFC 规定 TLS 扩展的顺序不影响握手语义，但  ** 扩展顺序的改变会导致 JA3 Hash 发生变化  **

主动一致性里，来源用和声明宽高严格相等的媒体查询去对 `matchMedia`。返回 false 被写成渲染引擎的尺寸和 JS 暴露的尺寸不符。

> Queries）的底层逻辑。通过构造严格匹配当前声明尺寸的媒体查询，若  ` matchMedia  ` 返回  ` false  `

> ，说明底层渲染引擎的真实尺寸与 JS 暴露的尺寸不符：

CPU 架构被写成看 NaN 的底层字节，经共享缓冲区的 `Float32Array` 与 `Uint8Array` 读取。来源注释把第 4 字节说成 ARM 与 x86 两个特征值（注释中的常量是 127 和 255）。函数体粘在同一行，本卡不把它当可运行探针。

> 不同 CPU 架构在处理浮点数  ` NaN  ` （Not a Number）时，其底层二进制字节表示存在差异。通过  ` Float32Array  `

媒体类型不按支持与否的布尔值区分，而来源说 `canPlayType()` 返回 `probably`、`maybe` 或空串，并可用 audio、video、MediaSource、MediaRecorder 四个入口交叉。对照表不整表抄入。

`speechSynthesis.getVoices()` 的语音包名称、以及 `getEngine()` 返回 80 之后的 CSS/API 打分，是后文的平台矩阵。矩阵按来源自己的布尔组合计分，没有版本范围，不转入。九种异常文本的 SHA-256 同样没有基准值。

IP 与时区的一句是：

> 比如 IP 是美国，时区却是中国，直接露馅：

IANA 名来自 `Intl.DateTimeFormat().resolvedOptions().timeZone`。没有偏移阈值。

<a id="interfaces"></a>
## 来源点名的入口和库

在线入口被点名为：

>   * tls.peet.ws

>   * browserleaks

>   * scrapfly.io

库的名字是 BoringSSL 与 uTLS。OpenSSL 只作为来源说要替换或改动的对象出现，不附源文件和改法。

>   * ** 替换底层库  ** ：将 OpenSSL 替换为 Google 维护的  ** BoringSSL  **

这些站点没有在本轮请求。作者写的 scapy 或 Wireshark 体验句没有形成单独接口。

## 验证与限制

- 没有 JA3、peetprint 或 HTTP/2 帧的当前版本对照，也没有 TCP 选项顺序的抓包。
- 没有本地执行，没有回显响应，没有站点接受或拒绝记录。
- navigator、screen、事件、电池、网络和媒体设备的字段清单不在本卡重列。
- 下篇才写的 Canvas、字体、WebGL、WebGPU、WebAudio 不在本文件。
- 改 OpenSSL、删除自动化属性、发送 CDP Input 都没有验收和失败出口，所以不是流程卡。
- 示例扩展 ID 已省略。
