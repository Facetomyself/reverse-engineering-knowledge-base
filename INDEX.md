# 逆向知识库文章索引

> 更新于 2026-09-06 ｜ 来源: `article/`
>
> 本文件维护 canonical 入口与技术标签；合集子文章详见 [CATALOG.md](./CATALOG.md)，机器读取使用 [`catalog.json`](./catalog.json)。
>
> 新项目启动时，按主题/技术标签检索相关文章，避免重复分析。

## 按分类浏览

### 协议分析 (`article/protocols/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [mmtls-protocol-analysis.md](./protocols/mmtls-protocol-analysis.md) | yyb (应用宝) | `mmtls`, `TLS 1.3`, `ECDHE`, `PSK 0-RTT`, `AES-GCM`, `HKDF`, `腾讯私有协议`, `ShortLink`, `iLink`, `NewDNS` | 腾讯 mmtls 协议完整逆向：Record 层帧格式、ECDHE 握手、PSK 0-RTT 快速重连、密码学细节（HKDF/AES-GCM）、ShortLink 应用帧层、iLink 业务层、NewDNS 服务发现 |

### 采集工程 (`article/collection-engineering/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [high-concurrency-http-collector-control-plane.md](./collection-engineering/high-concurrency-http-collector-control-plane.md) | psa | `代理租约`, `Sticky SID`, `Cookie 隔离`, `连接池`, `AIMD`, `congestion epoch`, `Retry-After`, `half-open`, `item deadline`, `checkpoint` | 高并发 HTTP 采集控制面：统一代理身份与连接生命周期，分离 429/403/transport 反馈，并用有界队列、分层 deadline、连接池 circuit 和固定窗口 canary 收敛长跑故障 |
| [reliable-mac-nas-spool-delivery.md](./collection-engineering/reliable-mac-nas-spool-delivery.md) | psa | `Mac mini`, `SSD spool`, `NAS mirror`, `marker`, `ACK`, `at-least-once`, `幂等`, `launchd`, `非侵入式巡检`, `GC` | Mac 热写与 NAS 交付链：本地 spool、SSH tar staging、pending/GC/ACK 重放、supervisor 完成门、安全发布与 process-crash/power-loss 边界 |
| [browser-collector-stability.md](./collection-engineering/browser-collector-stability.md) | radwell | `ruyipage`, `Firefox 151`, `MOZ_ASSERT`, `0x80000003`, `孤儿 session`, `CF 软挑战`, `IP 风控窗口`, `OOM 连锁`, `BiDi`, `多进程并发`, `spawn 子进程` | 浏览器采集器稳定性：ruyipage 定制 Firefox 断言崩溃（0x80000003）的触发条件与证据链、单出口 IP 的 CF 风控有效窗口、"崩溃残留进程累积 → 整机 OOM"的连锁机制，及 8 条并发/自愈/内存护栏改进规范 |
| [mihomo-dialer-proxy-chain.md](./collection-engineering/mihomo-dialer-proxy-chain.md) | — (GitHub 归档) | `Clash Verge`, `Mihomo`, `dialer-proxy`, `relay`, `Chain-Front`, `TUN fake-ip`, `preproxy`, `mihomo_fanout` | Mihomo 链式代理：`dialer-proxy` 替代已废弃 `relay`、Clash Verge 全局脚本的日常分流模型，以及它与采集器 `--preproxy` / 隔离 sidecar 的合同边界 |

### 反检测/风控对抗 (`article/anti-detection/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [51job-anti-detection-analysis.md](./anti-detection/51job-anti-detection-analysis.md) | 51job-web-reverse | `阿里ACW WAF`, `飞林FeiLin`, `神策SensorsData`, `Function.toString`, `debugger绕过`, `WebDriver检测`, `CDP检测`, `hook检测`, `反检测对抗矩阵` | 51job 三层风控体系全面分析：ACW WAF 检测向量、飞林设备指纹、神策行为埋点，20+ 检测向量的逐一对抗设计 |
| [chromium-fingerprint-compilation.md](./anti-detection/chromium-fingerprint-compilation.md) | — (CSDN 归档) | `Chromium编译`, `指纹浏览器`, `Canvas指纹`, `WebGL指纹`, `WebRTC`, `TLS/JA3/JA4`, `CDP绕过`, `无头检测`, `源码修改`, `BoringSSL`, `V8`, `Blink` | Chromium 源码级指纹浏览器编译全系列 (38篇)：15+ 指纹维度随机化/固定、反检测绕过 (WebDriver/CDP/无头/Selenium)、爬虫增强 (Shadow DOM/跨域iframe/CSS动画禁用)、工程化 (JWT校验/Cookie明文/任务栏徽章) |
| [anti-crawler-risk-control-compilation.md](./anti-detection/anti-crawler-risk-control-compilation.md) | — (公众号归档) | `浏览器指纹`, `验证码`, `行为风控`, `TLS指纹`, `HTTP/2指纹`, `代理检测`, `注册环境` | 浏览器、网络、验证码与行为模型的风控对抗系列，保留检测维度、定位方法和综合系统设计 |
| [ruyi-browser-anti-detection-compilation.md](./anti-detection/ruyi-browser-anti-detection-compilation.md) | — (公众号归档) | `Chromium`, `Firefox`, `WebKit`, `Canvas`, `WebGL`, `WebGPU`, `TLS`, `CDP`, `BiDi`, `RuyiTrace`, `浏览器指纹` | 97 篇浏览器内核、指纹检测、自动化对抗、论文研读与 Web 逆向工具链合集 |
| [benru-anti-detection-compilation.md](./anti-detection/benru-anti-detection-compilation.md) | — (公众号归档) | `请求头一致性`, `curl_cffi`, `TLS指纹`, `Selenium stealth`, `登录态`, `字体反爬`, `验证码`, `Canvas` | 本如笔记 8 篇反爬与反检测实战，覆盖客户端一致性、浏览器自动化伪装、字体/验证码识别和 Canvas 指纹 |
| [yuanrenxue-anti-detection-compilation.md](./anti-detection/yuanrenxue-anti-detection-compilation.md) | — (公众号归档) | `Squid`, `Cookie`, `Referer`, `响应编码`, `DNS缓存`, `Akamai`, `JA3`, `JA4`, `HTTP/2指纹` | 猿人学 8 篇请求一致性与反检测资料，从代理、会话和 DNS 管理延伸到 Akamai TLS 指纹复刻 |
| [android-ace-deviceuniqueid.md](./anti-detection/android-ace-deviceuniqueid.md) | — (看雪归档) | `ACE`, `libtersafe.so`, `deviceUniqueId`, `Widevine`, `KeyBox`, `TEE`, `RPMB`, `Play Integrity`, `Key Attestation`, `TssSDKSetUserInfo` | 腾讯 ACE 安卓设备拉黑：Widevine `deviceUniqueId` 由 TEE/RPMB KeyBox 派生；Java 取样写入 TSS SDK 后 UDP 上报；刷机/清 provisioning/只 hook Java 都改不掉硬锚点 |
| [xfq-device-fp-compilation.md](./anti-detection/xfq-device-fp-compilation.md) | — (知识星球归档) | `设备指纹`, `设备注册`, `熵源`, `伪随机`, `TLS指纹`, `风控SO`, `QIMEI` | 逆向学习交流 8 篇设备指纹与风控方法论：纯协议注册思路、熵源/伪随机、协议指纹演进和风控 so 上手，不收录设备 ID 清单 |

### 签名算法 (`article/signature-algorithms/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [qidian-fock-signature.md](./signature-algorithms/qidian-fock-signature.md) | qidian (起点读书) | `QDSign`, `Fock SDK`, `3DES-CBC`, `PKCS#7`, `QIMEI`, `certificate MD5`, `请求 canonicalization`, `重放验证`, `7大签名头` | 起点读书 QDSign 结论更新：126/126 样本验证 3DES-CBC 管道字段，纠正旧 RSA/HMAC 推测，并区分排行榜 endpoint 的头部校验边界 |
| [xfq-crypto-notes-compilation.md](./signature-algorithms/xfq-crypto-notes-compilation.md) | — (知识星球归档) | `AES`, `DES`, `3DES`, `MD5`, `SHA1`, `RC4`, `ChaCha20`, `GCM`, `魔改哈希`, `trace` | 逆向学习交流 19 篇密码算法笔记：AES/DES/流密码实现、魔改 MD5/SHA1 还原与 Java Crypto Hook，保留公式和步骤不收录附件 zip |
| [boluobao-sfsecurity-trace.md](./signature-algorithms/boluobao-sfsecurity-trace.md) | — (语雀归档) | `SFSecurity`, `mt19937`, `UUID v4`, `nonce`, `自定义编码`, `MD5`, `HashFinder`, `libsfdata.so` | 菠萝包轻小说 5.1.54：`/dev/urandom` 经 mt19937 生成 UUID v4 nonce，四段自定义编码后标准 MD5 得 `sign`；5.2.x 算法进匿名内存，不能再按映射 SO 偏移收工 |
| [mafengwo-modified-sha1-trace.md](./signature-algorithms/mafengwo-modified-sha1-trace.md) | — (语雀归档) | `SHA-1`, `HashFinder`, `Ch`, `Parity`, `Maj`, `feed-forward`, `libmfw.so` | 马蜂窝魔改 SHA1 练习稿：用 `0x80` 扫描和逐轮 `a_new` 对照找出 Ch/Parity/Maj 错位分段；闭合四类魔改（含 H2/H3 对调）见合集笔记 |
| [hangban-laes-encrypt.md](./signature-algorithms/hangban-laes-encrypt.md) | — (PDF 归档) | `LAES`, `ECB`, `PKCS7`, `T-box`, `JNI`, `libhbgjbangbang_crypto_tool.so`, `航班管家` | 航班管家 `laesEncryptStringWithBase64`：key 前 4 字节是模式头，轮密钥滚动异或，AddRoundKey 改 nibble 查表，S-box/T-box 均非标准 AES；纯算回放对齐 JNI Base64 |

### 加固绕过 (`article/packing-bypass/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [jiagu-bypass-analysis.md](./packing-bypass/jiagu-bypass-analysis.md) | qidian (起点读书) | `Jiagu`, `360加固`, `raise(9)`, `PR_SET_PTRACER`, `direct syscall`, `panda`, `whole-DEX`, `方法抽取`, `CodeItem`, `FART`, `JDex2`, `CDEX` | 360 Jiagu VIP 更新：区分进程存活与 Frida 持久会话，证明起点样本 DEX 原本明文，并记录 LDPlayer + panda 导出 13 DEX 的部分运行时恢复及方法抽取分流 |
| [app-protectors.md](./packing-bypass/app-protectors.md) | ciweimao / douban-app-reverse / qidian | `Jiagu`, `Legu`, `SecNeo`, `NIS`, `libnesec`, `stub-wrapper`, `whole-dex`, `Gadget` | App 加固/wrapper 命中表：stub 明文 DEX 先官方 live，真加密才 dump；NIS abort 先看 tombstone |

### Native 分析 (`article/native-analysis/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [qidian-so-analysis.md](./native-analysis/qidian-so-analysis.md) | qidian (起点读书) | `libfock.so`, `libfockrt.so`, `ARM64`, `JNI动态注册`, `3DES-CBC`, `AES-256-CBC`, `QuickJS`, `Unicorn`, `结论纠偏` | 起点读书 Native SO 结论纠偏：126 条 QDSign 推翻 RSA/AES 归因，保留 libfock 算法能力、QuickJS runtime、Jiagu 与 DEX/SO 分工的证据边界 |
| [ai-assisted-vmp-trace-recovery.md](./native-analysis/ai-assisted-vmp-trace-recovery.md) | — (公众号归档) | `ARM64 trace`, `VMP`, `tracedb`, `MCP`, `数据流回溯`, `AES-256-CBC`, `HMAC-SHA256`, `Adjust nSign` | 以固定宽度 trace 数据库和自定义 MCP 驱动 AI，从 196GB 指令轨迹中闭合 nSign 算法证据链 |
| [xfq-unidbg-native-compilation.md](./native-analysis/xfq-unidbg-native-compilation.md) | — (知识星球归档) | `Unidbg`, `JNI`, `Gadget`, `xfqtrace`, `ELF`, `so注入`, `jnilog` | 逆向学习交流 12 篇 Unidbg/Native 笔记：调用栈、内存读写坑、JNI 注入与 xfqtrace/Gadget，不收录未开源工具本体 |

### 移动 App 逆向 (`article/mobile-app-reverse/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [app-reverse-global-map.md](./mobile-app-reverse/app-reverse-global-map.md) | — (PDF 归档) | `App逆向`, `Android请求生命周期`, `OkHttp`, `Interceptor`, `JNI`, `SO层`, `Frida`, `SSL Pinning`, `设备指纹`, `VMP` | App 逆向全局地图：从 UI/业务/网络/加密/JNI/SO/网络发送七层拆解请求生命周期，总结定位加密点、还原算法、模拟请求三步法和常见防御手段 |
| [app-reverse-environment-setup.md](./mobile-app-reverse/app-reverse-environment-setup.md) | — (PDF 归档) | `App逆向环境`, `Android`, `LDPlayer`, `MuMu`, `Magisk`, `LSPosed`, `JustTrustMe`, `Charles`, `jadx-gui`, `APKTool`, `Frida`, `证书安装` | App 逆向环境搭建：模拟器与真机选型、Root/Magisk/LSPosed、证书安装与代理配置、抓包/反编译/动态调试工具链和常见问题排查 |
| [anti-crawler-app-reverse-series.md](./mobile-app-reverse/anti-crawler-app-reverse-series.md) | — (公众号归档) | `App逆向`, `jadx`, `Frida`, `JNI`, `SO层`, `密码算法`, `Python复现` | 从全局视角到 SO 层还原的 6 章 App 逆向入门系列 |
| [paopao-android-reverse-compilation.md](./mobile-app-reverse/paopao-android-reverse-compilation.md) | — (公众号归档) | `Frida`, `Unidbg`, `ARM64`, `JNI`, `Stalker`, `SSL Pinning`, `Protobuf`, `DEX脱壳`, `Root检测` | 67 篇 Android 抓包、密码算法、Native 模拟、Hook、反检测与脱壳系统合集 |
| [yuanrenxue-mobile-app-reverse-compilation.md](./mobile-app-reverse/yuanrenxue-mobile-app-reverse-compilation.md) | — (公众号归档) | `Token Hook`, `TCP抓包`, `Protobuf`, `双向认证`, `Android`, `iOS`, `Flutter`, `Jailbreak检测` | 猿人学 17 篇移动 App 逆向资料，覆盖认证协议、Native 参数、抓包对抗、跨平台运行时与越狱检测 |
| [mtop-innersign-rpc.md](./mobile-app-reverse/mtop-innersign-rpc.md) | cv-cat | `MTOP`, `InnerSignImpl`, `getUnifiedSign`, `x-sign`, `x-sgext`, `x-mini-wua`, `Frida RPC`, `闲鱼` | 阿里系 App 网关签名默认走 InnerSignImpl 实例 RPC：Hook 一次即摘、设备参数成套、与 Web H5 `_m_h5_tk` MD5 不能互换 |
| [pure-protocol-sdk-reconstruction.md](./mobile-app-reverse/pure-protocol-sdk-reconstruction.md) | — (方法论整理) | `纯协议`, `设备注册`, `HAR 语料`, `Interceptor`, `algorithms`, `指纹语义`, `TLS/JA3`, `SDK 状态机`, `发送顺序` | App 纯协议 SDK 重建：干净首次注册 HAR、一参数一文件算法、拦截器式 apis/interceptors、多环境指纹对照，以及传输指纹 / 依赖 DAG / SDK 状态机三层注册完备性 |
| [xfq-android-cases-compilation.md](./mobile-app-reverse/xfq-android-cases-compilation.md) | — (知识星球归档) | `Unidbg`, `NS_sig3`, `白盒AES`, `小黑盒`, `趣头条`, `AppsFlyer`, `安居客 nsign`, `陌陌 x-sign`, `纯算`, `signature` | 逆向学习交流 15 篇安卓实战：快手白盒、小黑盒 hkey、马蜂窝/趣头条/安居客 nsign、陌陌 x-sign、AppsFlyer 与 unidbg 补环境；hook 点已脱敏，不含设备字段和过检测脚本 |
| [reversenotes-android-compilation.md](./mobile-app-reverse/reversenotes-android-compilation.md) | — (GitHub 归档) | `buvid`, `deviceid`, `HMAC-SHA1`, `AES-CBC`, `AES-ECB`, `libmsaoaidsec`, `B站`, `豆瓣`, `韩小圈` | 星球索引所称 GitHub 小号 reverseNotes：B 站设备信封、韩小圈 AES 头、豆瓣 HMAC sig、升学e网通 AES-ECB；不含付费课与敏感样本 |
| [xfq-aosp-rom-compilation.md](./mobile-app-reverse/xfq-aosp-rom-compilation.md) | — (知识星球归档) | `AOSP`, `APatch`, `WebView`, `系统CA`, `GMS`, `adb`, `ROM` | 逆向学习交流 13 篇 AOSP/ROM 笔记：预置 CA、APatch、WebView 调试、GMS 与 adb RSA，只保留可复用改造路径 |
| [xfq-tools-debug-compilation.md](./mobile-app-reverse/xfq-tools-debug-compilation.md) | — (知识星球归档) | `xfqtrace`, `Frida`, `Gadget`, `jadx`, `抓包`, `WebView`, `MCP` | 逆向学习交流 42 篇工具调试：xfqtrace/Frida/jadx、证书、WebView Hook 与 MCP，已去掉号池/续杯/破解版 |
| [kimi-device-register-ttencrypt.md](./mobile-app-reverse/kimi-device-register-ttencrypt.md) | — (独立分析归档) | `device_register`, `ttEncrypt`, `tt_info`, `AES-128-CBC`, `SHA512`, `volces`, `Kimi`, `JNI` | 字节系 Kimi `device_register`：query `tt_info` 与二进制 body 共用 MAGIC\|\|seed\|\|AES 封装，key/IV 由明文 seed 派生，属可逆协议封装并给出 Python 复现 |
| [sdk-purecalc-compilation.md](./mobile-app-reverse/sdk-purecalc-compilation.md) | hnair-dingxiang-risktoken / xiaoxingkong-shumei-dpv4 / tencent-qimei-pure / jincai-pingxiang-wtoken | `DXRisk`, `riskToken`, `数美`, `deviceprofile/v4`, `Qimei`, `snowflake`, `wtoken`, `XXTEA`, `纯协议` | storage SDK 落盘提炼：顶象签发请求、数美 v4 封装、腾讯 Qimei REGISTER、今彩萍乡 wtoken；不含密钥、画像原值和可直接打生产的脚本 |
| [softard-android-reverse-compilation.md](./mobile-app-reverse/softard-android-reverse-compilation.md) | — (公众号归档) | `Android权限`, `ELF`, `ART`, `Smali`, `OLLVM`, `IDA`, `UnCrackable`, `DEX string_ids` | Softard 13 篇：权限模型、ELF/SO、ART、Smali patch、OLLVM 与 IDA 追 native 算法；不含订阅/会员推广 |
| [uiautomator-privacy-consent-tap.md](./mobile-app-reverse/uiautomator-privacy-consent-tap.md) | — (公众号归档) | `uiautomator`, `adb input tap`, `隐私协议`, `pm clear`, `设备注册`, `UI dump` | 首次启动隐私/权限弹窗：uiautomator dump 解析 bounds，对「同意/允许」中心点 `input tap`；界面问题不必先 Frida |

### Web 逆向 (`article/web-reverse/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [51job-webpack-analysis.md](./web-reverse/51job-webpack-analysis.md) | 51job-web-reverse | `Webpack 4`, `Vue 2.7`, `模块自吐`, `加密定位`, `sign`, `AES`, `SM4`, `国密`, `webpackJsonp` | 51job Webpack 模块自吐分析：1634 个 factory 模块识别、加密/签名模块定位、Vue 组件反编译、chunk 加载机制 |
| [anti-crawler-web-reverse-compilation.md](./web-reverse/anti-crawler-web-reverse-compilation.md) | — (公众号归档) | `Akamai`, `JSVMP`, `Babel AST`, `控制流平坦化`, `Chrome DevTools`, `Hook`, `反Hook` | Akamai 参数、JSVMP、AST 反混淆与 Chrome DevTools 调试对抗的 16 篇实战合集 |
| [benru-web-reverse-compilation.md](./web-reverse/benru-web-reverse-compilation.md) | — (公众号归档) | `WBI签名`, `AST`, `JS混淆`, `Node补环境`, `mitmproxy`, `动态参数`, `Webpack RPC`, `Python还原` | 本如笔记 12 篇 Web 逆向与协议恢复实战，从参数定位、反混淆和补环境延伸到 RPC 与 Python 复现 |
| [yuanrenxue-web-reverse-compilation.md](./web-reverse/yuanrenxue-web-reverse-compilation.md) | — (公众号归档) | `JS Cookie`, `参数加密`, `反调试`, `字符串混淆`, `控制流混淆`, `微信小程序`, `AI逆向` | 猿人学 7 篇 Web 与 JavaScript 逆向方法论，保留长期可复用的定位、调试和反混淆路径 |
| [products.md](./web-reverse/products.md) | — (JS终结计划课程方法论) | `风控产品`, `验证码`, `签名`, `WAF`, `反爬`, `命中索引`, `DataDome`, `Akamai`, `Kasada`, `瑞数`, `reCAPTCHA`, `Arkose Labs`, `FunCaptcha`, `同盾`, `京东`, `JCAP`, `tp=22`, `空间推理`, `h5st`, `抖音`, `阿里云验证码`, `腾讯验证码`, `网易易盾`, `NECaptcha`, `F5`, `PerimeterX`, `reese84`, `小红书`, `x-s`, `快手`, `__NS_sig3`, `MTOP` | 安全产品强制命中索引：验证码/签名/状态型链的命中特征 → 产品文档映射，含京东 JCAP `tp` 题型分流、网易易盾 jigsaw，以及小红书 xs、快手 NS 签名与阿里 MTOP H5 |
| [sign-landing-methods.md](./web-reverse/sign-landing-methods.md) | cv-cat | `纯算`, `Node vm`, `execjs`, `Frida RPC`, `a_bogus`, `x-s`, `__NS_sig3`, `h5st`, `provenance`, `canonical query` | 平台签名落地选型：宿主原语可钩则纯算，字节码 VM 用隔离出参，App Native 走实例 RPC；产品切开验收，不把 Cookie 随机串当成 serverAccepted |
| [browser-env-objects.md](./web-reverse/browser-env-objects.md) | — (JS终结计划课程方法论) | `补环境`, `DOM/BOM`, `浏览器对象`, `WebAPI`, `指纹`, `Worker`, `MessagePort`, `Canvas`, `WebGL`, `navigator`, `crypto` | Web 补环境浏览器对象参考：20 个 DOM/BOM/Web API 对象的检测面、常见坑与观察优先级，五维度补环境纪律 |
| [unpacked-mv3-native-updater.md](./web-reverse/unpacked-mv3-native-updater.md) | mouchenjie-ai-plugin | `MV3`, `sideload`, `自定义协议`, `PyInstaller 更新器`, `加载已解压扩展`, `渠道 zip` | 未上架 Chrome MV3 的本机更新器架构：渠道清单 + 对象存储 zip、HKCU 协议唤醒、本机进度口和打包合同，可复用到自有插件 sideload 分发 |
| [datadome-env-patch.md](./web-reverse/datadome-env-patch.md) | — (公众号归档) | `DataDome`, `plv3`, `payload`, `iframe Realm`, `OffscreenCanvas`, `jsdom`, `VM 分叉` | DataDome 无感 interstitial 补环境：jsdom+vm 跑原脚本出参，按 Realm 生命周期、Worker 异步链和 VM 第一处分叉对齐；成功口径是 redirect 后新 Session 业务 200 |
| [ai-assisted-web-reverse-compilation.md](./web-reverse/ai-assisted-web-reverse-compilation.md) | — (公众号归档) | `h5st`, `a_bogus`, `x-s`, `x-s-common`, `JSVMP`, `RSA`, `fangdir`, `X-Gnarly`, `Shein`, `Dewu`, `md5__1038` | AI辅助逆向手记 20 篇：京东 h5st v5.3、瑞数 fangdir、抖音 a_bogus、小红书 xs、Shein/得物签名与 JSVMP/RSA 方法论，目标已脱敏 |
| [koohai-reverse-notes-compilation.md](./web-reverse/koohai-reverse-notes-compilation.md) | — (公众号归档) | `KhBox`, `补环境`, `Illegal invocation`, `Canvas`, `jsdom`, `JSVMP`, `FART`, `WebView`, `IDA MD5` | 零基础爬虫第一天 17 篇：KhBox 补环境与 Node 编译、BrowserLeaks、AST/JSVMP，以及 FART/WebView/IDA 识别 MD5 |

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
- **AES/RSA/TEA/DES/MD5（Android 实战）**: [paopao-android](./mobile-app-reverse/paopao-android-reverse-compilation.md), [xfq-crypto](./signature-algorithms/xfq-crypto-notes-compilation.md), [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md)
- **PBKDF2-SHA1 + AES-128-CBC（AppsFlyer androidevent）**: [xfq-android-cases](./mobile-app-reverse/xfq-android-cases-compilation.md)
- **MD5 一位改写 / nsign 四段拼接（安居客）**: [xfq-android-cases](./mobile-app-reverse/xfq-android-cases-compilation.md)
- **AES-128-CBC + SHA1 拼接（陌陌 x-sign 第一参）**: [xfq-android-cases](./mobile-app-reverse/xfq-android-cases-compilation.md)
- **HMAC-SHA1 → Base64 → URL-encode（豆瓣 sig）**: [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md)
- **AES-CBC 由 uid MD5 对半作 key/iv（韩小圈 sign）**: [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md)
- **RC4/Salsa20/ChaCha20/GCM 流密码实现**: [xfq-crypto](./signature-algorithms/xfq-crypto-notes-compilation.md)
- **魔改 MD5/SHA1 与 Java Crypto Hook**: [xfq-crypto](./signature-algorithms/xfq-crypto-notes-compilation.md), [mafengwo-sha1](./signature-algorithms/mafengwo-modified-sha1-trace.md)
- **mt19937 + UUID v4 nonce + 自定义编码 MD5（SFSecurity）**: [boluobao-sfsecurity](./signature-algorithms/boluobao-sfsecurity-trace.md)
- **SHA-1 轮函数错位分段 / HashFinder 0x80 扫描**: [mafengwo-sha1](./signature-algorithms/mafengwo-modified-sha1-trace.md), [xfq-crypto](./signature-algorithms/xfq-crypto-notes-compilation.md)
- **AES-256-CBC + HMAC-SHA256**: [ai-vmp-trace](./native-analysis/ai-assisted-vmp-trace-recovery.md)
- **AES-128-CBC + SHA512 KDF（ttEncrypt / device_register）**: [kimi-ttencrypt](./mobile-app-reverse/kimi-device-register-ttencrypt.md)
- **XXTEA + ZIP(raw DEFLATE)（顶象 riskToken 签发 body）**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **RSA-OAEP-SHA256 + AES-256-CBC hexdigest key（数美 deviceprofile/v4）**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **双段 AES-CBC + RSA ky + ChaCha sn（腾讯 Qimei REGISTER）**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **AES-CBC + HMAC-SHA256 + 自定义哈希（今彩萍乡 wtoken）**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **魔改 AES-like / 自定义 T-box / nibble Mix（LAES ECB）**: [hangban-laes](./signature-algorithms/hangban-laes-encrypt.md)
- **RSA-1024 固定 0x01 填充 / 公钥 DER 锚**: [ai-assisted-web](./web-reverse/ai-assisted-web-reverse-compilation.md)
- **WBI/Base64/常见哈希与动态参数识别**: [benru-web](./web-reverse/benru-web-reverse-compilation.md), [yuanrenxue-web](./web-reverse/yuanrenxue-web-reverse-compilation.md), [yuanrenxue-app](./mobile-app-reverse/yuanrenxue-mobile-app-reverse-compilation.md)
- **MTOP H5 `_m_h5_tk` MD5 sign**: [alibaba-mtop-h5](./web-reverse/products/alibaba-mtop-h5.md), [sign-landing](./web-reverse/sign-landing-methods.md)
- **易盾自定义 xor-b64 / 非标准 AES / 47 维轨迹特征**: [products](./web-reverse/products.md)

### 协议
- **TLS 1.3 变体**: [mmtls](./protocols/mmtls-protocol-analysis.md)
- **PSK 0-RTT**: [mmtls](./protocols/mmtls-protocol-analysis.md)
- **自定义应用帧**: [mmtls](./protocols/mmtls-protocol-analysis.md)
- **ACE UDP 加密上报（tss_sdk_encryptpacket）**: [ace-deviceuniqueid](./anti-detection/android-ace-deviceuniqueid.md)
- **自定义 URL 协议唤醒本机更新器**: [unpacked-mv3-updater](./web-reverse/unpacked-mv3-native-updater.md)
- **HTTP DNS**: [mmtls](./protocols/mmtls-protocol-analysis.md)
- **Protobuf/gRPC**: [paopao-android](./mobile-app-reverse/paopao-android-reverse-compilation.md), [yuanrenxue-app](./mobile-app-reverse/yuanrenxue-mobile-app-reverse-compilation.md)
- **App 设备注册 / 拦截器式纯协议客户端**: [pure-protocol-sdk](./mobile-app-reverse/pure-protocol-sdk-reconstruction.md), [kimi-ttencrypt](./mobile-app-reverse/kimi-device-register-ttencrypt.md), [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md), [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **顶象 DXRisk `/udid/m1` riskToken 签发**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **数美 `deviceprofile/v4` data/tn/ep**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **腾讯 snowflake Qimei REGISTER `/ola/v2`**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **B 站 buvid / deviceid RSA+AES 信封 / fp_local**: [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md)
- **字节 volces `device_register` / `tt_info` / `ttEncrypt`**: [kimi-ttencrypt](./mobile-app-reverse/kimi-device-register-ttencrypt.md)
- **SFSecurity（nonce/timestamp/devicetoken/sign）**: [boluobao-sfsecurity](./signature-algorithms/boluobao-sfsecurity-trace.md)
- **TLS/HTTP2 网络指纹**: [anti-crawler-risk](./anti-detection/anti-crawler-risk-control-compilation.md), [ruyi-browser](./anti-detection/ruyi-browser-anti-detection-compilation.md)
- **WBI/Protobuf/TCP/mTLS 与认证协议**: [benru-web](./web-reverse/benru-web-reverse-compilation.md), [yuanrenxue-app](./mobile-app-reverse/yuanrenxue-mobile-app-reverse-compilation.md)
- **钉钉 LWP WebSocket（淘宝/闲鱼 IM）**: [alibaba-mtop-h5](./web-reverse/products/alibaba-mtop-h5.md)
- **Akamai JA3/JA4/HTTP2 指纹**: [yuanrenxue-anti](./anti-detection/yuanrenxue-anti-detection-compilation.md)

### 反检测/对抗
- **WAF 绕过**: [51job-anti-detection](./anti-detection/51job-anti-detection-analysis.md)
- **设备指纹**: [51job-anti-detection](./anti-detection/51job-anti-detection-analysis.md), [pure-protocol-sdk](./mobile-app-reverse/pure-protocol-sdk-reconstruction.md), [ace-deviceuniqueid](./anti-detection/android-ace-deviceuniqueid.md), [xfq-device-fp](./anti-detection/xfq-device-fp-compilation.md), [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md), [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **数美 Java a* / Native b* 画像生命周期**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **腾讯 Qimei 设备注册纯协议**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md), [xfq-device-fp](./anti-detection/xfq-device-fp-compilation.md)
- **libmsaoaidsec 加载期检测（leave 缺失 / call_constructors 观察窗）**: [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md), [xfq-android-cases](./mobile-app-reverse/xfq-android-cases-compilation.md)
- **风控熵源 / 伪随机 / 协议指纹演进**: [xfq-device-fp](./anti-detection/xfq-device-fp-compilation.md)
- **Widevine / deviceUniqueId / Key Attestation / Play Integrity**: [ace-deviceuniqueid](./anti-detection/android-ace-deviceuniqueid.md)
- **加固绕过 / whole-DEX 分流**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **App 壳/wrapper 命中（Jiagu/Legu/SecNeo/NIS）**: [app-protectors](./packing-bypass/app-protectors.md)
- **反调试 (ptrace/TracerPid)**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **Frida 终止链与 prctl 定位**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **方法抽取 / CodeItem 恢复**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **WebDriver/CDP 检测**: [51job-anti-detection](./anti-detection/51job-anti-detection-analysis.md), [chromium-fingerprint-compilation](./anti-detection/chromium-fingerprint-compilation.md)
- **Chromium 源码修改/指纹浏览器**: [chromium-fingerprint-compilation](./anti-detection/chromium-fingerprint-compilation.md)
- **TLS/JA3/JA4 指纹**: [chromium-fingerprint-compilation](./anti-detection/chromium-fingerprint-compilation.md), [pure-protocol-sdk](./mobile-app-reverse/pure-protocol-sdk-reconstruction.md)
- **Canvas/WebGL 指纹**: [chromium-fingerprint-compilation](./anti-detection/chromium-fingerprint-compilation.md)
- **SSL Pinning**: [app-reverse-global-map](./mobile-app-reverse/app-reverse-global-map.md), [app-reverse-environment-setup](./mobile-app-reverse/app-reverse-environment-setup.md)
- **Root/Magisk 隐藏**: [app-reverse-environment-setup](./mobile-app-reverse/app-reverse-environment-setup.md)
- **验证码与行为风控**: [anti-crawler-risk](./anti-detection/anti-crawler-risk-control-compilation.md), [products](./web-reverse/products.md), [pure-protocol-sdk](./mobile-app-reverse/pure-protocol-sdk-reconstruction.md)
- **安全产品命中识别（DataDome/Akamai/Kasada/瑞数/reCAPTCHA/Arkose/同盾/京东/抖音/易盾/小红书/快手/MTOP 等）**: [products](./web-reverse/products.md)
- **DataDome 无感 interstitial 补环境（payload/plv3 / iframe Realm / VM 分叉）**: [datadome-env-patch](./web-reverse/datadome-env-patch.md)
- **瑞数 fangdir P-cookie / LCG / Huffman / CRC32**: [ai-assisted-web](./web-reverse/ai-assisted-web-reverse-compilation.md)
- **KhBox / Illegal invocation / Canvas 指纹补环境**: [koohai-notes](./web-reverse/koohai-reverse-notes-compilation.md)
- **网易易盾 Web 滑块（NECaptcha / validate / 同轮 token）**: [products](./web-reverse/products.md)
- **补环境浏览器对象面（DOM/BOM/WebAPI/Worker/Canvas/WebGL）**: [env-objects](./web-reverse/browser-env-objects.md)
- **浏览器内核级指纹与自动化对抗**: [ruyi-browser](./anti-detection/ruyi-browser-anti-detection-compilation.md)
- **Android Root/反调试/Frida 对抗**: [paopao-android](./mobile-app-reverse/paopao-android-reverse-compilation.md), [softard-android](./mobile-app-reverse/softard-android-reverse-compilation.md)
- **curl_cffi/Selenium stealth/字体与验证码/Canvas**: [benru-anti](./anti-detection/benru-anti-detection-compilation.md)
- **Cookie/Referer/代理/DNS/TLS 请求一致性**: [yuanrenxue-anti](./anti-detection/yuanrenxue-anti-detection-compilation.md)
- **代理租约/Sticky 会话/429 自适应并发**: [collector-control-plane](./collection-engineering/high-concurrency-http-collector-control-plane.md)
- **Clash/Mihomo 链式代理与出口身份分离**: [mihomo-dialer-proxy](./collection-engineering/mihomo-dialer-proxy-chain.md)
- **Flutter/iOS Jailbreak 与抓包对抗**: [yuanrenxue-app](./mobile-app-reverse/yuanrenxue-mobile-app-reverse-compilation.md)

### 厂商/平台
- **腾讯 (微信/应用宝)**: [mmtls](./protocols/mmtls-protocol-analysis.md)
- **腾讯 ACE / Widevine DRM / libtersafe**: [ace-deviceuniqueid](./anti-detection/android-ace-deviceuniqueid.md)
- **阅文 (起点)**: [qidian-fock](./signature-algorithms/qidian-fock-signature.md), [qidian-so](./native-analysis/qidian-so-analysis.md), [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **阿里 (ACW/飞林)**: [51job-anti-detection](./anti-detection/51job-anti-detection-analysis.md)
- **360 (Jiagu)**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md), [app-protectors](./packing-bypass/app-protectors.md)
- **网易 NIS / 易盾加固（App）**: [app-protectors](./packing-bypass/app-protectors.md), [paopao-android](./mobile-app-reverse/paopao-android-reverse-compilation.md)
- **51job**: [51job-anti-detection](./anti-detection/51job-anti-detection-analysis.md), [51job-webpack](./web-reverse/51job-webpack-analysis.md)
- **CSDN/w1101662433 (fivcan)**: [chromium-fingerprint-compilation](./anti-detection/chromium-fingerprint-compilation.md)
- **Android/App 逆向**: [app-reverse-global-map](./mobile-app-reverse/app-reverse-global-map.md), [app-reverse-environment-setup](./mobile-app-reverse/app-reverse-environment-setup.md), [pure-protocol-sdk](./mobile-app-reverse/pure-protocol-sdk-reconstruction.md), [ace-deviceuniqueid](./anti-detection/android-ace-deviceuniqueid.md), [xfq-android-cases](./mobile-app-reverse/xfq-android-cases-compilation.md), [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md), [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **AOSP / ROM 改造（CA/APatch/WebView）**: [xfq-aosp-rom](./mobile-app-reverse/xfq-aosp-rom-compilation.md)
- **知识星球：逆向学习交流**: [xfq-crypto](./signature-algorithms/xfq-crypto-notes-compilation.md), [xfq-android-cases](./mobile-app-reverse/xfq-android-cases-compilation.md), [xfq-unidbg](./native-analysis/xfq-unidbg-native-compilation.md), [xfq-aosp-rom](./mobile-app-reverse/xfq-aosp-rom-compilation.md), [xfq-device-fp](./anti-detection/xfq-device-fp-compilation.md), [xfq-tools](./mobile-app-reverse/xfq-tools-debug-compilation.md), [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md)
- **语雀 xiaofeng777/android_example**: [boluobao-sfsecurity](./signature-algorithms/boluobao-sfsecurity-trace.md), [mafengwo-sha1](./signature-algorithms/mafengwo-modified-sha1-trace.md)
- **菠萝包 / SFACG**: [boluobao-sfsecurity](./signature-algorithms/boluobao-sfsecurity-trace.md)
- **马蜂窝**: [mafengwo-sha1](./signature-algorithms/mafengwo-modified-sha1-trace.md), [xfq-crypto](./signature-algorithms/xfq-crypto-notes-compilation.md), [xfq-android-cases](./mobile-app-reverse/xfq-android-cases-compilation.md)
- **陌陌**: [xfq-android-cases](./mobile-app-reverse/xfq-android-cases-compilation.md)
- **GitHub xfxfxiaofeng/reverseNotes**: [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md)
- **哔哩哔哩 / 豆瓣 / 韩小圈 / 升学e网通 / 安居客 / AppsFlyer / 陌陌**: [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md), [xfq-android-cases](./mobile-app-reverse/xfq-android-cases-compilation.md)
- **macOS / NAS 采集交付**: [mac-nas-spool](./collection-engineering/reliable-mac-nas-spool-delivery.md)
- **浏览器采集器稳定性（ruyipage/Firefox 崩溃/OOM）**: [browser-collector-stability](./collection-engineering/browser-collector-stability.md)
- **Clash Verge Rev / Mihomo**: [mihomo-dialer-proxy](./collection-engineering/mihomo-dialer-proxy-chain.md)
- **Akamai**: [anti-crawler-web](./web-reverse/anti-crawler-web-reverse-compilation.md), [products](./web-reverse/products.md)
- **DataDome / Kasada / PerimeterX / F5 Shape / reese84 / Cloudflare 5s**: [products](./web-reverse/products.md), [datadome-env-patch](./web-reverse/datadome-env-patch.md)
- **Kimi / 字节 volces applog**: [kimi-ttencrypt](./mobile-app-reverse/kimi-device-register-ttencrypt.md)
- **微信公众号：ai辅助逆向手记**: [ai-assisted-web](./web-reverse/ai-assisted-web-reverse-compilation.md)
- **微信公众号：零基础爬虫第一天**: [koohai-notes](./web-reverse/koohai-reverse-notes-compilation.md)
- **微信公众号：Softard（Wossoneri）**: [softard-android](./mobile-app-reverse/softard-android-reverse-compilation.md), [uiautomator-consent](./mobile-app-reverse/uiautomator-privacy-consent-tap.md)
- **航班管家 / hbgjbangbang LAES**: [hangban-laes](./signature-algorithms/hangban-laes-encrypt.md)
- **瑞数 RS6**: [products](./web-reverse/products.md)
- **Google reCAPTCHA v3**: [products](./web-reverse/products.md)
- **阿里（ACW/H5Sec/BxUA/验证码/MTOP H5）**: [51job-anti-detection](./anti-detection/51job-anti-detection-analysis.md), [products](./web-reverse/products.md), [alibaba-mtop-h5](./web-reverse/products/alibaba-mtop-h5.md)
- **腾讯（验证码/风控）**: [mmtls](./protocols/mmtls-protocol-analysis.md), [products](./web-reverse/products.md)
- **腾讯 Qimei / 应用宝设备标识**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **顶象 DXRisk**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **数美 / 小星空**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **海南航空**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **今彩萍乡**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **网易易盾（Web NECaptcha / App NES 加固分面）**: [products](./web-reverse/products.md), [paopao-android](./mobile-app-reverse/paopao-android-reverse-compilation.md)
- **同盾 / 京东（h5st/JCAP 滑块与 tp=22 空间推理/到家）/ 抖音（a_bogus/IM/TicketGuard）/ 饿了么 / 美团 / 小红书 xs / 快手 NS / 阿里 MTOP H5**: [products](./web-reverse/products.md)
- **闲鱼 / 淘宝 App InnerSignImpl**: [mtop-innersign-rpc](./mobile-app-reverse/mtop-innersign-rpc.md)
- **微信公众号技术归档（反爬破解社/如意私塾/泡泡以安/本如笔记/猿人学Python/ai辅助逆向手记/零基础爬虫第一天/Softard）**: [anti-crawler-web](./web-reverse/anti-crawler-web-reverse-compilation.md), [ruyi-browser](./anti-detection/ruyi-browser-anti-detection-compilation.md), [paopao-android](./mobile-app-reverse/paopao-android-reverse-compilation.md), [benru-web](./web-reverse/benru-web-reverse-compilation.md), [benru-anti](./anti-detection/benru-anti-detection-compilation.md), [yuanrenxue-web](./web-reverse/yuanrenxue-web-reverse-compilation.md), [yuanrenxue-app](./mobile-app-reverse/yuanrenxue-mobile-app-reverse-compilation.md), [yuanrenxue-anti](./anti-detection/yuanrenxue-anti-detection-compilation.md), [ai-assisted-web](./web-reverse/ai-assisted-web-reverse-compilation.md), [koohai-notes](./web-reverse/koohai-reverse-notes-compilation.md), [softard-android](./mobile-app-reverse/softard-android-reverse-compilation.md)
- **谋臣界 / 未上架 MV3 更新器**: [unpacked-mv3-updater](./web-reverse/unpacked-mv3-native-updater.md)

### 工具/方法
- **Webpack 模块自吐**: [51job-webpack](./web-reverse/51job-webpack-analysis.md)
- **抓包+逐字节匹配**: [mmtls](./protocols/mmtls-protocol-analysis.md)
- **IDA Pro 静态分析**: [qidian-so](./native-analysis/qidian-so-analysis.md), [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md), [ace-deviceuniqueid](./anti-detection/android-ace-deviceuniqueid.md), [hangban-laes](./signature-algorithms/hangban-laes-encrypt.md), [softard-android](./mobile-app-reverse/softard-android-reverse-compilation.md)
- **ACE TSS SDK / libtersafe 上报链**: [ace-deviceuniqueid](./anti-detection/android-ace-deviceuniqueid.md)
- **radare2 快速侦察**: [qidian-so](./native-analysis/qidian-so-analysis.md)
- **Frida spawn / survival hook**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **panda whole-DEX**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **OkHttp 明文 Hook / 流量对齐**: [app-reverse-global-map](./mobile-app-reverse/app-reverse-global-map.md), [app-protectors](./packing-bypass/app-protectors.md)
- **FART / JDex2 / FartFixer 分流**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **Chromium 源码编译与修改**: [chromium-fingerprint-compilation](./anti-detection/chromium-fingerprint-compilation.md)
- **滑块缺口轮廓匹配（Canny 对洞，禁止灰度对纹理）**: [products](./web-reverse/products.md)
- **App 逆向三步法**: [app-reverse-global-map](./mobile-app-reverse/app-reverse-global-map.md)
- **OkHttp/Interceptor 定位**: [app-reverse-global-map](./mobile-app-reverse/app-reverse-global-map.md), [pure-protocol-sdk](./mobile-app-reverse/pure-protocol-sdk-reconstruction.md)
- **App 纯协议 SDK 重建（HAR 语料 / algorithms / 拦截器链 / 注册完备性）**: [pure-protocol-sdk](./mobile-app-reverse/pure-protocol-sdk-reconstruction.md)
- **SDK 纯算落盘（顶象/数美/Qimei/wtoken 封装链）**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **Android 逆向环境搭建**: [app-reverse-environment-setup](./mobile-app-reverse/app-reverse-environment-setup.md)
- **Charles/jadx/Frida 工具链**: [app-reverse-environment-setup](./mobile-app-reverse/app-reverse-environment-setup.md)
- **Babel AST/控制流反混淆**: [anti-crawler-web](./web-reverse/anti-crawler-web-reverse-compilation.md)
- **Chrome DevTools 断点/Hook/反Hook**: [anti-crawler-web](./web-reverse/anti-crawler-web-reverse-compilation.md)
- **Frida/Unidbg/Stalker/Native Hook**: [paopao-android](./mobile-app-reverse/paopao-android-reverse-compilation.md), [xfq-unidbg](./native-analysis/xfq-unidbg-native-compilation.md), [xfq-tools](./mobile-app-reverse/xfq-tools-debug-compilation.md), [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md)
- **脱敏 hook 窗口（只记点/参数形状，RVA 按当前 SO 重核）**: [xfq-android-cases](./mobile-app-reverse/xfq-android-cases-compilation.md)
- **HashFinder / Merkle-Damgård 0x80 明文扫描**: [boluobao-sfsecurity](./signature-algorithms/boluobao-sfsecurity-trace.md), [mafengwo-sha1](./signature-algorithms/mafengwo-modified-sha1-trace.md), [xfq-crypto](./signature-algorithms/xfq-crypto-notes-compilation.md)
- **逐轮差分排除魔改哈希（first mismatch round）**: [mafengwo-sha1](./signature-algorithms/mafengwo-modified-sha1-trace.md)
- **JNI_OnLoad 偏移表 / Map+StringBuilder 定位 sign**: [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md)
- **xfqtrace / Gadget / jadx 一键 Hook**: [xfq-tools](./mobile-app-reverse/xfq-tools-debug-compilation.md), [xfq-unidbg](./native-analysis/xfq-unidbg-native-compilation.md)
- **uiautomator dump + adb input tap（隐私协议/权限弹窗）**: [uiautomator-consent](./mobile-app-reverse/uiautomator-privacy-consent-tap.md)
- **ELF Section vs Segment / ART ArtMethod / Smali patch**: [softard-android](./mobile-app-reverse/softard-android-reverse-compilation.md)
- **OLLVM 控制流平坦化识别**: [softard-android](./mobile-app-reverse/softard-android-reverse-compilation.md)
- **自定义 T-box 提表后纯算（LAES）**: [hangban-laes](./signature-algorithms/hangban-laes-encrypt.md)
- **AOSP 预置 CA / APatch / WebView 调试 ROM**: [xfq-aosp-rom](./mobile-app-reverse/xfq-aosp-rom-compilation.md)
- **trace 数据库 + MCP 证据回溯**: [ai-vmp-trace](./native-analysis/ai-assisted-vmp-trace-recovery.md)
- **Chromium/Firefox/WebKit 内核定制**: [ruyi-browser](./anti-detection/ruyi-browser-anti-detection-compilation.md)
- **AST/JS 混淆/Node 补环境/Webpack RPC**: [benru-web](./web-reverse/benru-web-reverse-compilation.md), [yuanrenxue-web](./web-reverse/yuanrenxue-web-reverse-compilation.md), [koohai-notes](./web-reverse/koohai-reverse-notes-compilation.md)
- **jsdom + vm 对齐浏览器 VM 第一处分叉**: [datadome-env-patch](./web-reverse/datadome-env-patch.md)
- **h5st / a_bogus / x-s / x-s-common / X-Gnarly 签名定位**: [ai-assisted-web](./web-reverse/ai-assisted-web-reverse-compilation.md), [products](./web-reverse/products.md)
- **FART 源码改进 / WebView 调试 / IDA 识别 MD5**: [koohai-notes](./web-reverse/koohai-reverse-notes-compilation.md), [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **JSVMP 是否拆 opcode 的分流**: [ai-assisted-web](./web-reverse/ai-assisted-web-reverse-compilation.md)
- **风控产品强制命中分类（验证码/签名/状态型链）**: [products](./web-reverse/products.md)
- **平台签名落地分流（纯算 / Node vm / execjs 整包 / Frida RPC）**: [sign-landing](./web-reverse/sign-landing-methods.md)
- **MTOP InnerSignImpl 实例 RPC（Hook 一次即摘）**: [mtop-innersign-rpc](./mobile-app-reverse/mtop-innersign-rpc.md)
- **canonical query 与 Cookie provenance**: [sign-landing](./web-reverse/sign-landing-methods.md)
- **补环境对象级参考（检测面/常见坑/观察优先级）**: [env-objects](./web-reverse/browser-env-objects.md)
- **未上架 MV3 / sideload / 自定义协议本机更新器**: [unpacked-mv3-updater](./web-reverse/unpacked-mv3-native-updater.md)
- **mitmproxy/Charles/Frida/Protobuf/iOS/Flutter 工具链**: [benru-web](./web-reverse/benru-web-reverse-compilation.md), [yuanrenxue-app](./mobile-app-reverse/yuanrenxue-mobile-app-reverse-compilation.md)
- **高并发采集控制面/AIMD/half-open**: [collector-control-plane](./collection-engineering/high-concurrency-http-collector-control-plane.md)
- **Mihomo dialer-proxy / curl --preproxy / 隔离 sidecar**: [mihomo-dialer-proxy](./collection-engineering/mihomo-dialer-proxy-chain.md)
- **SSD spool/NAS mirror/marker-ACK 重放**: [mac-nas-spool](./collection-engineering/reliable-mac-nas-spool-delivery.md)

---

## 维护规则

1. 新增文章时，在对应分类表添加一行
2. 同步更新「按技术标签检索」中的标签映射
3. 新增分类时，在 `article/` 下创建子目录 + 更新本索引
4. 来源项目列始终指向原始 workspace 项目名
5. 正文或索引变更后运行 `scripts/kb_catalog.py generate`，不要手工编辑 `CATALOG.md` / `catalog.json`
6. 提交前运行 `scripts/kb_catalog.py check` 和 `python -m unittest discover -s tests -v`
