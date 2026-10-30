---
schema_version: 2
id: risk-control-location
document_type: archive
original_date: unknown
archived_date: "2026-10-30"
scope:
  targets: [location-risk-control]
  client: app
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: null
    basis: source-report
    citation: 风控之关于定位
    reason: 原始材料未提供可公开定位的链接
source_completeness: partial
tags: [location, gnss, asn, imu, rtt, source-report]
---

# 风控之关于定位（来源报告）

来源标题是「风控之关于定位」。没有作者署名，也没有发表日期。它同时写手机 App 和网页请求里的经纬度。按合同 `client` 只记 `app`；网页侧只保留「请求里可以带坐标」这一限制，不另建网页目标。

本文是来源方法论的 archive，不是攻击手册，也不是 procedure。原文没有验收和失败出口。下面不新增原文没有的绕过步骤。

## 清洗与完整性说明

- 删除文中「评论一下」的互动句。没有购买或关注尾注。
- 来源把两张表拆成逐单元格。下面按表头顺序还原：第一张是「来源 / 原理 / 典型精度 / 伪造难度」，第二张是「ASN 类型 / 典型归属 / 风控含义 / 检测难度」。没有补原文没有的单元格。若列序与原意不一致，以未入库的原件为准；公开正文不写本机路径。
- 来源把代理一词写成 `V*N`，这里保持原样，不展开。
- 论文和 NIST 名称按原文保留，不编造原文没有的 URL。
- 表格缺口加上没有公开定位，完整性为 partial。文中的公里数、dB、准确率都是作者引用的来源数字，本次没有复核论文，也没有做定位实验。

## 来源正文

### 1. 基础

#### 1.1 坐标怎样被上报

作者把路径写成：原始信号 → 系统融合 → 应用读取 → 网络上报。原始信号来自 GPS 卫星、Wi-Fi 扫描、蜂窝基站编号、蓝牙信标。系统融合在 Android 上是 `LocationManager`，在 iOS 上是 Core Location；Android fused provider 会在 GPS、网络、Wi-Fi 之间选择和加权，应用通常拿到的是融合结果。应用再把坐标放进请求。

网页请求也可以带经纬度字段。那只是本篇的旁述，不单独作为 web 目标。

#### 1.2 IP 位置不是真值

作者认为「IP 反查位置对不上就是伪造」在移动网络上会大量误判。IP 地理定位返回的是带精度半径的概率区域。作者引用 2026 年一项覆盖 175 个国家、四家数据库的评估，题为 Lost in the Prefix: Revisiting IP Geolocation Accuracy Across Networks and Geographies：固定宽带城际中位误差约 3–16 公里，移动网络约 179–207 公里；移动网络中约 70% 的 IP 前缀空间跨度超过 100 公里。作者据此说，防守方不能用固定公里数一刀切；把坐标改到 IP 位置附近的粗距离检查，也过不了其余信号。

NIST SP 800-63B 把会话监测写成对 geolocation、velocity、timing、device/browser characteristics 和 IP characteristics 的持续评估。作者用它说明位置只是证据链中的一环。

#### 1.3 四类来源

| 来源 | 原理 | 典型精度 | 伪造难度 |
| --- | --- | --- | --- |
| GPS/GNSS | 接收多颗卫星信号，解算伪距 | 米级到十米级 | 应用层/系统层容易改；物理层需要软件定义无线电（SDR） |
| Wi-Fi 定位 | 扫描周围热点，比对数据库中的热点位置 | 十米到百米级 | 应用层/系统层容易改；重放信标可伪造 |
| 蜂窝基站 | 根据连接的基站编号和信号强度估算 | 百米到公里级 | 系统层可改；需要伪造基站列表 |
| IP 定位 | 根据 IP 地址反查注册地/网络出口 | 公里到百公里级 | 换代理/`V*N` 即可改变 |

作者对 SDR 的解释停在概念：调制解调尽量交给软件，硬件只做射频前端，并举 HackRF、PlutoSDR 作为通用设备例子。本文不补设备用法。

伪距是到达时间乘光速，里面混着卫星钟差、接收机钟差、电离层和对流层误差。至少同时观测 4 颗卫星，才能解三维位置和接收机钟差。GDOP 表示位置误差与测距误差的比率，PDOP 反映水平和垂直分量。卫星越挤在天空一侧，同样的测距误差被放得越大。多普勒给出伪距变化率，从而解速度。作者认为多普勒和 IMU 是独立观测，比单改一个维度更难同时自洽。

Wi-Fi 和蜂窝都是客户端报告，不是网络侧独立观测，所以可以被一起改。作者因此把后面的网络 RTT 当成独立旁证。

坐标系：全球原始输出通常是 WGS84；中国大陆地图服务常用 GCJ-02，是 WGS84 上的非线性加偏；百度再在 GCJ-02 上做成 BD09。作者写 GCJ-02 偏移约 100–700 米，且用正弦制造高频噪声，逆变换只能数值近似。比较坐标之前要先换到同一坐标系。

操作系统给出的往往已经是融合结果。作者认为融合前或融合中被动过手，防守方看到的仍可能是一套自洽的假坐标。

### 2. 检查与作者写明的盲区

作者的总述是交叉验证，并且每一项检查都依赖某个假设。下面各节里的「绕过」都是来源原文已有的说法，不是本文补充的步骤。

#### 2.1 时间与速度

作者写的宽松上界是两次位置的隐含速度不超过约 800 km/h。作者列出的失效情形是：出口靠近目标城市时速度接近零；取得凭据后延迟使用，使速度落进合理区间；向解里注入很小的漂移。引用的标题是 CSIDE 的 What Is Impossible Travel Detection and How Does It Work?，以及 Spoofing in Slow Motion: Sub-Perceptual GPS Drift Attack Detection。

残余被写成弱信号：要和设备指纹、ASN 类型、会话历史一起看。

ASN 是 BGP 里标识自治系统的编号。分配链是 IANA 到 RIR（作者举 APNIC、RIPE）再到 ISP、云厂商或机构。作者强调：请求到达时，服务器可以根据 IP 查到 ASN 和类型，这发生在浏览器指纹、JavaScript 和 TLS 握手之前；应用层伪装改不了这个 IP 实际所属的 ASN。要换成另一个 ASN，得真的从那个 ASN 的地址出去。

| ASN 类型 | 典型归属 | 风控含义 | 检测难度 |
| --- | --- | --- | --- |
| 住宅 ISP | Comcast、AT&T、电信、联通 | 看起来像家庭用户，低风险先验 | 难（住宅代理可借用真实 ISP ASN） |
| 数据中心/托管 | AWS、Google Cloud、DigitalOcean、阿里云 | 真实用户很少从云服务器浏览，高风险先验 | 易（作者写分类准确率约 95%+） |
| 移动运营商 | Verizon Wireless、T-Mobile、中国移动 | 真实用户和代理最难分，也最容易被滥用 | 极难（作者写准确率约 20–40%，并提到 CGNAT 共享 IP） |

作者还写：住宅代理价格通常是数据中心的 10–50 倍，移动代理更高；BrightData、Smartproxy 这类名字并不运营自己的 ASN，出口仍落在住宅 ISP 的 ASN 上。因此住宅 ASN 本身不是决定性信号，要和设备指纹、请求频率、行为一起看。

查询手段作者只点了名字：whois、whob、RIR 数据库（ARIN、RIPE、APNIC）、Team Cymru、IPQualityScore。用法是把 ASN 类型和声称的网络类型、ASN/IP 信誉、ASN 注册地和声称位置放在一起。一个企业风控流程被概括成：取真实 TCP 出口 IP，查 ASN、`net_type`、`proxy_type`、`risk_score`，再和用户历史基线比。新城市加新 ASN 触发二次验证；数据中心 ASN 加代理标签加跨境则被写成拒绝条件。这些阈值不是本次测量。

作者对「ASN 能不能伪造」的原话边界是：ASN 作为 BGP 属性不能在应用层改写；可以改的是流量实际从哪个出口离开，从而带上另一个 ASN。住宅代理和移动代理是借用真实运营商的 ASN。BGP 劫持被作者标成网络层攻击，不是常规位置伪造路径，并提到 RPKI 和路由监控。作者的不对称性是：可以让流量来自另一个 ASN，不能让流量来自那个 ASN 里不存在的主机。

#### 2.2 多源是否指向同一位置

作者假设 GNSS、Wi-Fi 指纹、蜂窝基站应指向同一位置。作者引用的 2026 IEEE 题名是 Multimodal Location Spoofing: Federated Detection With RAIM-Based Self-Labeling，以及 ACM WiSec 2025 的 Coordinated Position Falsification Attacks and Countermeasures for LBS。来源里已经写出的条件包括：GNSS 攻击信号需要比真实信号强约 10 dB；需要同步时钟、接近目标并估计初始位置和速度；GNSS 轨迹要和来自 WiGLE.net 一类众包库的 Wi-Fi 信标对齐。本文不把这些句子扩展成操作步骤。

作者给出的信号侧残余是：AGC 在干扰或欺骗时可能持续偏低或异常一致；C/N0 在欺骗信号里可能异常高，或多颗卫星不自然地一致，压制干扰则通常使 C/N0 偏低；多普勒可能与真实运动不一致。网络 RTT 受光速约束，不依赖客户端报告。

#### 2.3 `isMock()` 不够

作者讨论 Android `Location.isMock()` / `isFromMockProvider()`，并称之为 “security theater”。来源已点名的路径是：用 Xposed/Frida 改 `LocationManager` 的返回，或在 system server 替换位置对象，使检查看不到 mock provider。点名的项目是 android-gps-setter、Smali Patcher（XDA）、YumyHook。本文不补这些项目的用法。

A-GPS / SUPL 被写成加速首次定位的辅助通道：设备向服务器发送粗略位置和 IMSI，取星历。作者称 SUPL 的设计目标不是安全验证，并提到历史上有实现不强制 SSL、DNS 欺骗可能影响 SUPL 消息。Magisk 模块 supl-replacer 被用来说明替换 `gps.conf` 里的 SUPL 提供方在工程上可行。没有步骤。

Play Integrity 被写成硬件支持的 attestation：后端给随机 nonce，由 Google 看设备二进制、bootloader 和硬件状态后返回令牌。作者同时写了两个容易高估的点：`MEETS_STRONG_INTEGRITY` 在 Android 13+ 要求 OS 和 vendor 分区都有近期安全补丁，Android 12 及以下的「硬件支持」更弱；并且已经有隐藏 root、替换 keybox、把 attestation 转发到一台未篡改设备上的说法。因此作者把完整性证明当成高权重信号，而不是唯一门禁。keybox 和令牌原值不在来源里，这里也不写。

#### 2.4 IMU 与 GNSS

IMU 测的是设备自身加速度和角速度，不依赖外部射频。作者假设：GNSS 声称在移动时，加速度计和陀螺仪应有相应信号。引用 TRIP: Trajectory-based Recognition of Identity Proof，以及 2026 IEEE 题名 Evaluating Combinatorial Anti-Spoofing Strategies for IoT GNSS Receivers Under Dynamic Meaconing Attacks。作者认为紧密耦合架构里基于新息的统计检验能同时暴露突变和渐进欺骗。

来源已提到的对抗是模拟步态、步频和 Ornstein–Uhlenbeck 抖动，项目名 LocationSpoofer。作者的不对称性是：伪造单次读数容易，维持长期噪声谱、步态周期变异和设备间硬件差异成本高。没有新的模拟参数。

#### 2.5 轨迹像不像人

作者引用 TRIP 的特征：时间间隔过度均匀像自动化；速度–加速度相空间过于混沌或过于紧致都可能异常。重放真实轨迹时，周围群体已经变了，速度场对不齐。路网拟合、红绿灯停候和高斯噪声被写成可以让单次轨迹接近人类移动，但跨许多会话维持同一种噪声和节奏会更贵。Blackbird.ai 的 2026 年分析被用来说明发帖高峰仍会落在操作者所在时区，即使资料写了另一个地方。

#### 2.6 网络侧旁证

RTT 有光速决定的下限，可以和声称位置交叉，而且不经过客户端报告。作者写住宅代理能改出口 IP，但不能把 RTT 降到物理下限以下；Wi-Fi 信标可以重放，信号强度随距离的衰减却难在所有采样点上同时复制。来源在这一节结束，没有后文。

## 复用边界

公里数、dB、准确率、价格倍数和错误码式的拒绝条件都是作者转述，不是本库测量。坐标系、伪距、GDOP、ASN 和 RTT 下限是来源里的机制说明。没有公开链接，两张表是从拆行单元格还原的，文末停在 2.6。不能把任何一节当成当前风控规则或已验收的检测器。
