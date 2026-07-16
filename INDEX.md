# 逆向知识库文章索引

> 自动生成于 2026-07-16 ｜ 来源: `article/`
>
> 新项目启动时，按主题/技术标签检索相关文章，避免重复分析。

## 按分类浏览

### 协议分析 (`article/protocols/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [mmtls-protocol-analysis.md](./protocols/mmtls-protocol-analysis.md) | yyb (应用宝) | `mmtls`, `TLS 1.3`, `ECDHE`, `PSK 0-RTT`, `AES-GCM`, `HKDF`, `腾讯私有协议`, `ShortLink`, `iLink`, `NewDNS` | 腾讯 mmtls 协议完整逆向：Record 层帧格式、ECDHE 握手、PSK 0-RTT 快速重连、密码学细节（HKDF/AES-GCM）、ShortLink 应用帧层、iLink 业务层、NewDNS 服务发现 |

### 反检测/风控对抗 (`article/anti-detection/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [51job-anti-detection-analysis.md](./anti-detection/51job-anti-detection-analysis.md) | 51job-web-reverse | `阿里ACW WAF`, `飞林FeiLin`, `神策SensorsData`, `Function.toString`, `debugger绕过`, `WebDriver检测`, `CDP检测`, `hook检测`, `反检测对抗矩阵` | 51job 三层风控体系全面分析：ACW WAF 检测向量、飞林设备指纹、神策行为埋点，20+ 检测向量的逐一对抗设计 |
| [chromium-fingerprint-compilation.md](./anti-detection/chromium-fingerprint-compilation.md) | — (CSDN 归档) | `Chromium编译`, `指纹浏览器`, `Canvas指纹`, `WebGL指纹`, `WebRTC`, `TLS/JA3/JA4`, `CDP绕过`, `无头检测`, `源码修改`, `BoringSSL`, `V8`, `Blink` | Chromium 源码级指纹浏览器编译全系列 (38篇)：15+ 指纹维度随机化/固定、反检测绕过 (WebDriver/CDP/无头/Selenium)、爬虫增强 (Shadow DOM/跨域iframe/CSS动画禁用)、工程化 (JWT校验/Cookie明文/任务栏徽章) |
| [anti-crawler-risk-control-compilation.md](./anti-detection/anti-crawler-risk-control-compilation.md) | — (公众号归档) | `浏览器指纹`, `验证码`, `行为风控`, `TLS指纹`, `HTTP/2指纹`, `代理检测`, `注册环境` | 浏览器、网络、验证码与行为模型的风控对抗系列，保留检测维度、定位方法和综合系统设计 |
| [ruyi-browser-anti-detection-compilation.md](./anti-detection/ruyi-browser-anti-detection-compilation.md) | — (公众号归档) | `Chromium`, `Firefox`, `WebKit`, `Canvas`, `WebGL`, `WebGPU`, `TLS`, `CDP`, `BiDi`, `RuyiTrace`, `浏览器指纹` | 97 篇浏览器内核、指纹检测、自动化对抗、论文研读与 Web 逆向工具链合集 |
| [benru-anti-detection-compilation.md](./anti-detection/benru-anti-detection-compilation.md) | — (公众号归档) | `请求头一致性`, `curl_cffi`, `TLS指纹`, `Selenium stealth`, `登录态`, `字体反爬`, `验证码`, `Canvas` | 本如笔记 8 篇反爬与反检测实战，覆盖客户端一致性、浏览器自动化伪装、字体/验证码识别和 Canvas 指纹 |
| [yuanrenxue-anti-detection-compilation.md](./anti-detection/yuanrenxue-anti-detection-compilation.md) | — (公众号归档) | `Squid`, `Cookie`, `Referer`, `响应编码`, `DNS缓存`, `Akamai`, `JA3`, `JA4`, `HTTP/2指纹` | 猿人学 8 篇请求一致性与反检测资料，从代理、会话和 DNS 管理延伸到 Akamai TLS 指纹复刻 |

### 签名算法 (`article/signature-algorithms/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [qidian-fock-signature.md](./signature-algorithms/qidian-fock-signature.md) | qidian (起点读书) | `QDSign`, `Fock SDK`, `3DES-CBC`, `PKCS#7`, `QIMEI`, `certificate MD5`, `请求 canonicalization`, `重放验证`, `7大签名头` | 起点读书 QDSign 结论更新：126/126 样本验证 3DES-CBC 管道字段，纠正旧 RSA/HMAC 推测，并区分排行榜 endpoint 的头部校验边界 |

### 加固绕过 (`article/packing-bypass/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [jiagu-bypass-analysis.md](./packing-bypass/jiagu-bypass-analysis.md) | qidian (起点读书) | `Jiagu`, `360加固`, `raise(9)`, `PR_SET_PTRACER`, `direct syscall`, `panda`, `whole-DEX`, `方法抽取`, `CodeItem`, `FART`, `JDex2`, `CDEX` | 360 Jiagu VIP 更新：区分进程存活与 Frida 持久会话，证明起点样本 DEX 原本明文，并记录 LDPlayer + panda 导出 13 DEX 的部分运行时恢复及方法抽取分流 |

### Native 分析 (`article/native-analysis/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [qidian-so-analysis.md](./native-analysis/qidian-so-analysis.md) | qidian (起点读书) | `libfock.so`, `libfockrt.so`, `ARM64`, `JNI动态注册`, `3DES-CBC`, `AES-256-CBC`, `QuickJS`, `Unicorn`, `结论纠偏` | 起点读书 Native SO 结论纠偏：126 条 QDSign 推翻 RSA/AES 归因，保留 libfock 算法能力、QuickJS runtime、Jiagu 与 DEX/SO 分工的证据边界 |
| [ai-assisted-vmp-trace-recovery.md](./native-analysis/ai-assisted-vmp-trace-recovery.md) | — (公众号归档) | `ARM64 trace`, `VMP`, `tracedb`, `MCP`, `数据流回溯`, `AES-256-CBC`, `HMAC-SHA256`, `Adjust nSign` | 以固定宽度 trace 数据库和自定义 MCP 驱动 AI，从 196GB 指令轨迹中闭合 nSign 算法证据链 |

### 移动 App 逆向 (`article/mobile-app-reverse/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [app-reverse-global-map.md](./mobile-app-reverse/app-reverse-global-map.md) | — (PDF 归档) | `App逆向`, `Android请求生命周期`, `OkHttp`, `Interceptor`, `JNI`, `SO层`, `Frida`, `SSL Pinning`, `设备指纹`, `VMP` | App 逆向全局地图：从 UI/业务/网络/加密/JNI/SO/网络发送七层拆解请求生命周期，总结定位加密点、还原算法、模拟请求三步法和常见防御手段 |
| [app-reverse-environment-setup.md](./mobile-app-reverse/app-reverse-environment-setup.md) | — (PDF 归档) | `App逆向环境`, `Android`, `LDPlayer`, `MuMu`, `Magisk`, `LSPosed`, `JustTrustMe`, `Charles`, `jadx-gui`, `APKTool`, `Frida`, `证书安装` | App 逆向环境搭建：模拟器与真机选型、Root/Magisk/LSPosed、证书安装与代理配置、抓包/反编译/动态调试工具链和常见问题排查 |
| [anti-crawler-app-reverse-series.md](./mobile-app-reverse/anti-crawler-app-reverse-series.md) | — (公众号归档) | `App逆向`, `jadx`, `Frida`, `JNI`, `SO层`, `密码算法`, `Python复现` | 从全局视角到 SO 层还原的 6 章 App 逆向入门系列 |
| [paopao-android-reverse-compilation.md](./mobile-app-reverse/paopao-android-reverse-compilation.md) | — (公众号归档) | `Frida`, `Unidbg`, `ARM64`, `JNI`, `Stalker`, `SSL Pinning`, `Protobuf`, `DEX脱壳`, `Root检测` | 67 篇 Android 抓包、密码算法、Native 模拟、Hook、反检测与脱壳系统合集 |
| [yuanrenxue-mobile-app-reverse-compilation.md](./mobile-app-reverse/yuanrenxue-mobile-app-reverse-compilation.md) | — (公众号归档) | `Token Hook`, `TCP抓包`, `Protobuf`, `双向认证`, `Android`, `iOS`, `Flutter`, `Jailbreak检测` | 猿人学 17 篇移动 App 逆向资料，覆盖认证协议、Native 参数、抓包对抗、跨平台运行时与越狱检测 |

### Web 逆向 (`article/web-reverse/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [51job-webpack-analysis.md](./web-reverse/51job-webpack-analysis.md) | 51job-web-reverse | `Webpack 4`, `Vue 2.7`, `模块自吐`, `加密定位`, `sign`, `AES`, `SM4`, `国密`, `webpackJsonp` | 51job Webpack 模块自吐分析：1634 个 factory 模块识别、加密/签名模块定位、Vue 组件反编译、chunk 加载机制 |
| [anti-crawler-web-reverse-compilation.md](./web-reverse/anti-crawler-web-reverse-compilation.md) | — (公众号归档) | `Akamai`, `JSVMP`, `Babel AST`, `控制流平坦化`, `Chrome DevTools`, `Hook`, `反Hook` | Akamai 参数、JSVMP、AST 反混淆与 Chrome DevTools 调试对抗的 16 篇实战合集 |
| [benru-web-reverse-compilation.md](./web-reverse/benru-web-reverse-compilation.md) | — (公众号归档) | `WBI签名`, `AST`, `JS混淆`, `Node补环境`, `mitmproxy`, `动态参数`, `Webpack RPC`, `Python还原` | 本如笔记 12 篇 Web 逆向与协议恢复实战，从参数定位、反混淆和补环境延伸到 RPC 与 Python 复现 |
| [yuanrenxue-web-reverse-compilation.md](./web-reverse/yuanrenxue-web-reverse-compilation.md) | — (公众号归档) | `JS Cookie`, `参数加密`, `反调试`, `字符串混淆`, `控制流混淆`, `微信小程序`, `AI逆向` | 猿人学 7 篇 Web 与 JavaScript 逆向方法论，保留长期可复用的定位、调试和反混淆路径 |

---

## 按技术标签检索

### 密码学
- **AES-GCM**: [mmtls](./protocols/mmtls-protocol-analysis.md), [qidian-fock](./signature-algorithms/qidian-fock-signature.md)
- **AES-256-CBC（libfock.so 内部能力）**: [qidian-so](./native-analysis/qidian-so-analysis.md)
- **3DES-CBC**: [qidian-fock](./signature-algorithms/qidian-fock-signature.md), [qidian-so](./native-analysis/qidian-so-analysis.md)
- **PKCS#7**: [qidian-fock](./signature-algorithms/qidian-fock-signature.md)
- **ECDHE (P-256)**: [mmtls](./protocols/mmtls-protocol-analysis.md)
- **HKDF**: [mmtls](./protocols/mmtls-protocol-analysis.md)
- **SM4 (国密)**: [51job-webpack](./web-reverse/51job-webpack-analysis.md)
- **AES/RSA/TEA/DES/MD5（Android 实战）**: [paopao-android](./mobile-app-reverse/paopao-android-reverse-compilation.md)
- **AES-256-CBC + HMAC-SHA256**: [ai-vmp-trace](./native-analysis/ai-assisted-vmp-trace-recovery.md)
- **WBI/Base64/常见哈希与动态参数识别**: [benru-web](./web-reverse/benru-web-reverse-compilation.md), [yuanrenxue-web](./web-reverse/yuanrenxue-web-reverse-compilation.md), [yuanrenxue-app](./mobile-app-reverse/yuanrenxue-mobile-app-reverse-compilation.md)

### 协议
- **TLS 1.3 变体**: [mmtls](./protocols/mmtls-protocol-analysis.md)
- **PSK 0-RTT**: [mmtls](./protocols/mmtls-protocol-analysis.md)
- **自定义应用帧**: [mmtls](./protocols/mmtls-protocol-analysis.md)
- **HTTP DNS**: [mmtls](./protocols/mmtls-protocol-analysis.md)
- **Protobuf/gRPC**: [paopao-android](./mobile-app-reverse/paopao-android-reverse-compilation.md)
- **TLS/HTTP2 网络指纹**: [anti-crawler-risk](./anti-detection/anti-crawler-risk-control-compilation.md), [ruyi-browser](./anti-detection/ruyi-browser-anti-detection-compilation.md)
- **WBI/Protobuf/TCP/mTLS 与认证协议**: [benru-web](./web-reverse/benru-web-reverse-compilation.md), [yuanrenxue-app](./mobile-app-reverse/yuanrenxue-mobile-app-reverse-compilation.md)
- **Akamai JA3/JA4/HTTP2 指纹**: [yuanrenxue-anti](./anti-detection/yuanrenxue-anti-detection-compilation.md)

### 反检测/对抗
- **WAF 绕过**: [51job-anti-detection](./anti-detection/51job-anti-detection-analysis.md)
- **设备指纹**: [51job-anti-detection](./anti-detection/51job-anti-detection-analysis.md)
- **加固绕过 / whole-DEX 分流**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **反调试 (ptrace/TracerPid)**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **Frida 终止链与 prctl 定位**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **方法抽取 / CodeItem 恢复**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **WebDriver/CDP 检测**: [51job-anti-detection](./anti-detection/51job-anti-detection-analysis.md), [chromium-fingerprint-compilation](./anti-detection/chromium-fingerprint-compilation.md)
- **Chromium 源码修改/指纹浏览器**: [chromium-fingerprint-compilation](./anti-detection/chromium-fingerprint-compilation.md)
- **TLS/JA3/JA4 指纹**: [chromium-fingerprint-compilation](./anti-detection/chromium-fingerprint-compilation.md)
- **Canvas/WebGL 指纹**: [chromium-fingerprint-compilation](./anti-detection/chromium-fingerprint-compilation.md)
- **SSL Pinning**: [app-reverse-global-map](./mobile-app-reverse/app-reverse-global-map.md), [app-reverse-environment-setup](./mobile-app-reverse/app-reverse-environment-setup.md)
- **Root/Magisk 隐藏**: [app-reverse-environment-setup](./mobile-app-reverse/app-reverse-environment-setup.md)
- **验证码与行为风控**: [anti-crawler-risk](./anti-detection/anti-crawler-risk-control-compilation.md)
- **浏览器内核级指纹与自动化对抗**: [ruyi-browser](./anti-detection/ruyi-browser-anti-detection-compilation.md)
- **Android Root/反调试/Frida 对抗**: [paopao-android](./mobile-app-reverse/paopao-android-reverse-compilation.md)
- **curl_cffi/Selenium stealth/字体与验证码/Canvas**: [benru-anti](./anti-detection/benru-anti-detection-compilation.md)
- **Cookie/Referer/代理/DNS/TLS 请求一致性**: [yuanrenxue-anti](./anti-detection/yuanrenxue-anti-detection-compilation.md)
- **Flutter/iOS Jailbreak 与抓包对抗**: [yuanrenxue-app](./mobile-app-reverse/yuanrenxue-mobile-app-reverse-compilation.md)

### 厂商/平台
- **腾讯 (微信/应用宝)**: [mmtls](./protocols/mmtls-protocol-analysis.md)
- **阅文 (起点)**: [qidian-fock](./signature-algorithms/qidian-fock-signature.md), [qidian-so](./native-analysis/qidian-so-analysis.md), [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **阿里 (ACW/飞林)**: [51job-anti-detection](./anti-detection/51job-anti-detection-analysis.md)
- **360 (Jiagu)**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **51job**: [51job-anti-detection](./anti-detection/51job-anti-detection-analysis.md), [51job-webpack](./web-reverse/51job-webpack-analysis.md)
- **CSDN/w1101662433 (fivcan)**: [chromium-fingerprint-compilation](./anti-detection/chromium-fingerprint-compilation.md)
- **Android/App 逆向**: [app-reverse-global-map](./mobile-app-reverse/app-reverse-global-map.md), [app-reverse-environment-setup](./mobile-app-reverse/app-reverse-environment-setup.md)
- **Akamai**: [anti-crawler-web](./web-reverse/anti-crawler-web-reverse-compilation.md)
- **微信公众号技术归档（反爬破解社/如意私塾/泡泡以安/本如笔记/猿人学Python）**: [anti-crawler-web](./web-reverse/anti-crawler-web-reverse-compilation.md), [ruyi-browser](./anti-detection/ruyi-browser-anti-detection-compilation.md), [paopao-android](./mobile-app-reverse/paopao-android-reverse-compilation.md), [benru-web](./web-reverse/benru-web-reverse-compilation.md), [benru-anti](./anti-detection/benru-anti-detection-compilation.md), [yuanrenxue-web](./web-reverse/yuanrenxue-web-reverse-compilation.md), [yuanrenxue-app](./mobile-app-reverse/yuanrenxue-mobile-app-reverse-compilation.md), [yuanrenxue-anti](./anti-detection/yuanrenxue-anti-detection-compilation.md)

### 工具/方法
- **Webpack 模块自吐**: [51job-webpack](./web-reverse/51job-webpack-analysis.md)
- **抓包+逐字节匹配**: [mmtls](./protocols/mmtls-protocol-analysis.md)
- **IDA Pro 静态分析**: [qidian-so](./native-analysis/qidian-so-analysis.md), [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **radare2 快速侦察**: [qidian-so](./native-analysis/qidian-so-analysis.md)
- **Frida spawn / survival hook**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **panda whole-DEX**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **FART / JDex2 / FartFixer 分流**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **Chromium 源码编译与修改**: [chromium-fingerprint-compilation](./anti-detection/chromium-fingerprint-compilation.md)
- **App 逆向三步法**: [app-reverse-global-map](./mobile-app-reverse/app-reverse-global-map.md)
- **OkHttp/Interceptor 定位**: [app-reverse-global-map](./mobile-app-reverse/app-reverse-global-map.md)
- **Android 逆向环境搭建**: [app-reverse-environment-setup](./mobile-app-reverse/app-reverse-environment-setup.md)
- **Charles/jadx/Frida 工具链**: [app-reverse-environment-setup](./mobile-app-reverse/app-reverse-environment-setup.md)
- **Babel AST/控制流反混淆**: [anti-crawler-web](./web-reverse/anti-crawler-web-reverse-compilation.md)
- **Chrome DevTools 断点/Hook/反Hook**: [anti-crawler-web](./web-reverse/anti-crawler-web-reverse-compilation.md)
- **Frida/Unidbg/Stalker/Native Hook**: [paopao-android](./mobile-app-reverse/paopao-android-reverse-compilation.md)
- **trace 数据库 + MCP 证据回溯**: [ai-vmp-trace](./native-analysis/ai-assisted-vmp-trace-recovery.md)
- **Chromium/Firefox/WebKit 内核定制**: [ruyi-browser](./anti-detection/ruyi-browser-anti-detection-compilation.md)
- **AST/JS 混淆/Node 补环境/Webpack RPC**: [benru-web](./web-reverse/benru-web-reverse-compilation.md), [yuanrenxue-web](./web-reverse/yuanrenxue-web-reverse-compilation.md)
- **mitmproxy/Charles/Frida/Protobuf/iOS/Flutter 工具链**: [benru-web](./web-reverse/benru-web-reverse-compilation.md), [yuanrenxue-app](./mobile-app-reverse/yuanrenxue-mobile-app-reverse-compilation.md)

---

## 维护规则

1. 新增文章时，在对应分类表添加一行
2. 同步更新「按技术标签检索」中的标签映射
3. 新增分类时，在 `article/` 下创建子目录 + 更新本索引
4. 来源项目列始终指向原始 workspace 项目名
