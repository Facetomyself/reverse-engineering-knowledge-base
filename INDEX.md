# 逆向知识库文章索引

> 更新于 2026-09-26 ｜ 来源: `article/`
>
> 本文件维护 canonical 入口与技术标签；合集子文章详见 [CATALOG.md](./CATALOG.md)，机器读取使用 [`catalog.json`](./catalog.json)。
>
> 新项目启动时，按主题/技术标签检索相关文章，避免重复分析。

## 按分类浏览

### 协议分析 (`article/protocols/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [mmtls-protocol-analysis.md](./protocols/mmtls-protocol-analysis.md) | yyb (应用宝) | `mmtls`, `TLS 1.3`, `ECDHE`, `PSK 0-RTT`, `AES-GCM`, `HKDF`, `腾讯私有协议`, `ShortLink`, `iLink`, `NewDNS` | 腾讯 mmtls 协议完整逆向：Record 层帧格式、ECDHE 握手、PSK 0-RTT 快速重连、密码学细节（HKDF/AES-GCM）、ShortLink 应用帧层、iLink 业务层、NewDNS 服务发现 |
| [wechat-mp-session-planes.md](./protocols/wechat-mp-session-planes.md) | weixin_download | `getmsg`, `profile_ext`, `pass_ticket`, `list_ex`, `GetA8Key`, `微信读书`, `MP_WXS_`, `uin/key`, `公众号会话` | 微信公众号五套互不续期的会话：客户端 mmtls 登录、WebView 短时 getmsg、MP 后台、微信读书 RefreshToken、原生 GetA8Key；钉错平面会把 ret=-3/验证页当成 0 篇成功 |
| [wechat-mp-http-surface.md](./protocols/wechat-mp-http-surface.md) | weixin_download | `getmsg`, `general_msg_list`, `getappmsgext`, `appmsg_comment`, `getalbum`, `__biz`, `mid`, `idx`, `scene=124` | 公众号 HTTPS 接口面：getmsg 分页与多图文 flatten、POST 阅读量、评论、合集游标；公开 URL 无登录；ret!=0 与验证页不得当成功 |

### 采集工程 (`article/collection-engineering/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [high-concurrency-http-collector-control-plane.md](./collection-engineering/high-concurrency-http-collector-control-plane.md) | psa | `代理租约`, `Sticky SID`, `Cookie 隔离`, `连接池`, `AIMD`, `congestion epoch`, `Retry-After`, `half-open`, `item deadline`, `checkpoint` | 高并发 HTTP 采集控制面：统一代理身份与连接生命周期，分离 429/403/transport 反馈，并用有界队列、分层 deadline、连接池 circuit 和固定窗口 canary 收敛长跑故障 |
| [reliable-mac-nas-spool-delivery.md](./collection-engineering/reliable-mac-nas-spool-delivery.md) | psa | `Mac mini`, `SSD spool`, `NAS mirror`, `marker`, `ACK`, `at-least-once`, `幂等`, `launchd`, `非侵入式巡检`, `GC` | Mac 热写与 NAS 交付链：本地 spool、SSH tar staging、pending/GC/ACK 重放、supervisor 完成门、安全发布与 process-crash/power-loss 边界 |
| [browser-collector-stability.md](./collection-engineering/browser-collector-stability.md) | radwell | `ruyipage`, `Firefox 151`, `MOZ_ASSERT`, `0x80000003`, `孤儿 session`, `CF 软挑战`, `IP 风控窗口`, `OOM 连锁`, `BiDi`, `多进程并发`, `spawn 子进程` | 浏览器采集器稳定性：ruyipage 定制 Firefox 断言崩溃（0x80000003）的触发条件与证据链、单出口 IP 的 CF 风控有效窗口、"崩溃残留进程累积 → 整机 OOM"的连锁机制，及 8 条并发/自愈/内存护栏改进规范 |
| [mihomo-dialer-proxy-chain.md](./collection-engineering/mihomo-dialer-proxy-chain.md) | — (GitHub 归档) | `Clash Verge`, `Mihomo`, `dialer-proxy`, `relay`, `Chain-Front`, `TUN fake-ip`, `preproxy`, `mihomo_fanout` | Mihomo 链式代理：`dialer-proxy` 替代已废弃 `relay`、Clash Verge 全局脚本的日常分流模型，以及它与采集器 `--preproxy` / 隔离 sidecar 的合同边界 |
| [weixin-http-archive-runtime.md](./collection-engineering/weixin-http-archive-runtime.md) | weixin_download | `SQLite`, `BEGIN IMMEDIATE`, `claim_token`, `heartbeat`, `durable retry`, `MCP job`, `stdio`, `Streamable HTTP` | 短时会话 HTTP 归档运行时：协议主键、短事务 claim、durable retry 不含凭证、MCP job 与文章状态分离；job completed 不等于文章成功 |

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
| [device-fingerprint-consistency-modeling.md](./anti-detection/device-fingerprint-consistency-modeling.md) | — (方法论整理) | `设备指纹`, `一致性建模`, `联合分布`, `泊松分布`, `对数正态`, `多次采集`, `APK版本`, `生命周期` | 设备指纹关键是一致性建模不是随机抖动：联合分布交叉印证、APK 自身版本面、右偏时间间隔、动态物理信号，以及多次采集的有状态演化；不收录生成代码 |
| [shuzilm-libdu-fingerprint.md](./anti-detection/shuzilm-libdu-fingerprint.md) | — (知乎 11.4.0 / libdu.so 独立分析) | `数盟`, `数字联盟`, `libdu.so`, `x-ms-id`, `cdd`, `d2api`, `vB2`, `AYk`, `deviceUniqueId` | 数盟可信 ID：注册顶层约 20–30 key、`vB2` 再嵌套到合计约 258 key，`d2api` 回 `cdd` 即业务 `x-ms-id`；对照表 366 key 含其它采集点，偏移只对知乎 11.4.0 / SDK v8.4.0 |
| [cloakbrowser-humanize-trajectory.md](./anti-detection/cloakbrowser-humanize-trajectory.md) | CloakHQ/CloakBrowser | `humanize`, `三次贝塞尔`, `ease-in-out`, `鼠标轨迹`, `过冲`, `CloakBrowser`, `Playwright` | 包装层 humanize 在进程内用三次贝塞尔、法线控制点和 burst 停顿生成鼠标样本；本机 Pro chrome.dll 不含该符号；可调用计划器在主仓 tools/cloakbrowser_human |
| [xianyu-eeid-risk-control.md](./anti-detection/xianyu-eeid-risk-control.md) | — (闲鱼 7.28.30 / SG 6.7.260202 独立分析) | `EEID`, `SecurityGuard`, `Mini 探针`, `ET 探针`, `SGEXT`, `UTDID`, `SG 文件`, `ACS-MUM`, `x-eeid`, `闲鱼` | 闲鱼 EEID：Mini 7+11 字节位图、ET 55 探针 tag、SGEXT 45 字段（`fields[4]`=`.sg` mtime）、PL CRC64 与 UTDID `Alvin2.xml`；服务端评分/EEID 生成为推测，`x-sign` HMAC-SHA1 说法与 SG 70102 四头冲突待验证 |

### 签名算法 (`article/signature-algorithms/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [qidian-fock-signature.md](./signature-algorithms/qidian-fock-signature.md) | qidian (起点读书) | `QDSign`, `Fock SDK`, `3DES-CBC`, `PKCS#7`, `QIMEI`, `certificate MD5`, `请求 canonicalization`, `重放验证`, `7大签名头` | 起点读书 QDSign 结论更新：126/126 样本验证 3DES-CBC 管道字段，纠正旧 RSA/HMAC 推测，并区分排行榜 endpoint 的头部校验边界 |
| [xfq-crypto-notes-compilation.md](./signature-algorithms/xfq-crypto-notes-compilation.md) | — (知识星球归档) | `AES`, `DES`, `3DES`, `MD5`, `SHA1`, `RC4`, `ChaCha20`, `GCM`, `魔改哈希`, `trace` | 逆向学习交流 19 篇密码算法笔记：AES/DES/流密码实现、魔改 MD5/SHA1 还原与 Java Crypto Hook，保留公式和步骤不收录附件 zip |
| [boluobao-sfsecurity-trace.md](./signature-algorithms/boluobao-sfsecurity-trace.md) | — (语雀归档) | `SFSecurity`, `mt19937`, `UUID v4`, `nonce`, `自定义编码`, `MD5`, `HashFinder`, `libsfdata.so` | 菠萝包轻小说 5.1.54：`/dev/urandom` 经 mt19937 生成 UUID v4 nonce，四段自定义编码后标准 MD5 得 `sign`；5.2.x 算法进匿名内存，不能再按映射 SO 偏移收工 |
| [mafengwo-modified-sha1-trace.md](./signature-algorithms/mafengwo-modified-sha1-trace.md) | — (语雀归档) | `SHA-1`, `HashFinder`, `Ch`, `Parity`, `Maj`, `feed-forward`, `libmfw.so` | 马蜂窝魔改 SHA1 练习稿：用 `0x80` 扫描和逐轮 `a_new` 对照找出 Ch/Parity/Maj 错位分段；闭合四类魔改（含 H2/H3 对调）见合集笔记 |
| [hangban-laes-encrypt.md](./signature-algorithms/hangban-laes-encrypt.md) | — (PDF 归档) | `LAES`, `ECB`, `PKCS7`, `T-box`, `JNI`, `libhbgjbangbang_crypto_tool.so`, `航班管家` | 航班管家 `laesEncryptStringWithBase64`：key 前 4 字节是模式头，轮密钥滚动异或，AddRoundKey 改 nibble 查表，S-box/T-box 均非标准 AES；纯算回放对齐 JNI Base64 |
| [alibaba-mtop-four-headers.md](./signature-algorithms/alibaba-mtop-four-headers.md) | alibaba-mtop-four-headers | `MTOP`, `x-sign`, `x-sgext`, `x-mini-wua`, `x-umt`, `SG 70102`, `DES-ECB`, `libsgmainso` | 阿里 App 网关四头纯算：会话画像 + `data2sign` 出 `x-sign`/`x-sgext`/`x-mini-wua`/`x-umt`；一加捕获只作 byte-exact 样本，不能凭空生成新会话 |
| [shopee-shpssdk-request-defense.md](./signature-algorithms/shopee-shpssdk-request-defense.md) | — (语雀归档) | `x-sap-ri`, `SHPSSDK`, `libshpssdk.so`, `ChaCha20`, `Salsa20`, `RC6`, `xxhash`, `mmh3`, `unidbg` | Shopee 33731 `requestDefense`：`libshpssdk.so!0x995dc` 产出 `x-sap-ri` 与四变化键；时间戳小端、九套短键、ChaCha20/RC6/Salsa20、xxhash 与自定义 Base64；截图已本地化，长值另三分支待验证 |

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
| [nuitka-onefile-payload-recovery.md](./native-analysis/nuitka-onefile-payload-recovery.md) | weixin_download | `Nuitka`, `onefile`, `RT_RCDATA`, `KAY`, `Zstandard`, `python310.dll`, `constants` | Windows Nuitka onefile：外层 RCDATA 高熵 payload（本样本 KAY+zstd）放出第二层 native 主程序；无 PYC 全集，只做 constants/协议字符串，不宣称还原源码 |

### 移动 App 逆向 (`article/mobile-app-reverse/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [app-reverse-global-map.md](./mobile-app-reverse/app-reverse-global-map.md) | — (PDF 归档) | `App逆向`, `Android请求生命周期`, `OkHttp`, `Interceptor`, `JNI`, `SO层`, `Frida`, `SSL Pinning`, `设备指纹`, `VMP` | App 逆向全局地图：从 UI/业务/网络/加密/JNI/SO/网络发送七层拆解请求生命周期，总结定位加密点、还原算法、模拟请求三步法和常见防御手段 |
| [app-reverse-environment-setup.md](./mobile-app-reverse/app-reverse-environment-setup.md) | — (PDF 归档) | `App逆向环境`, `Android`, `LDPlayer`, `MuMu`, `Magisk`, `LSPosed`, `JustTrustMe`, `Charles`, `jadx-gui`, `APKTool`, `Frida`, `证书安装` | App 逆向环境搭建：模拟器与真机选型、Root/Magisk/LSPosed、证书安装与代理配置、抓包/反编译/动态调试工具链和常见问题排查 |
| [jvm-mindmap.md](./mobile-app-reverse/jvm-mindmap.md) | — (方法论整理) | `JVM`, `ClassLoader`, `双亲委派`, `Runtime Data Area`, `PermGen`, `Metaspace`, `Heap`, `JIT`, `JNI`, `volatile` | HotSpot JVM 四块地图：类加载（加载/链接/初始化）、运行时数据区线程共享与私有划分、解释器+JIT（C1/C2）、JNI；校正原图笔误，JDK 8 PermGen→Metaspace |
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
| [protocol-admission-four-gates.md](./mobile-app-reverse/protocol-admission-four-gates.md) | tiktok-four-gate-source-study | `协议准入`, `四关`, `设备画像`, `签名拦截器`, `主机路由`, `TLS指纹`, `空成功`, `激活调用`, `registrationComplete`, `hardware-fp` | App 协议准入四关：同行设备、签名切面、主机/引导、传输指纹必须并联闭合；HTTP 200 空壳不是 serverAccepted，注册签发不等于激活。供后续纯协议 case 复用，TikTok 三源只作推导语料 |
| [protocol-register-packet-order.md](./mobile-app-reverse/protocol-register-packet-order.md) | — (方法论整理) | `纯协议`, `设备注册`, `发送顺序`, `事件包`, `日志包`, `多线程`, `SDK 状态机`, `前置身份`, `自动化`, `AppsFlyer` | 纯协议补注册不是按 HAR 串行：事件/日志走独立线程，云端身份是后续包前置条件；跟真机接近靠扣核心 SDK，上量失败多半是风控认知而不是签名 |
| [sdk-purecalc-compilation.md](./mobile-app-reverse/sdk-purecalc-compilation.md) | hnair-dingxiang-risktoken / xiaoxingkong-shumei-dpv4 / tencent-qimei-pure / jincai-pingxiang-wtoken | `DXRisk`, `riskToken`, `数美`, `deviceprofile/v4`, `Qimei`, `snowflake`, `wtoken`, `XXTEA`, `纯协议` | storage SDK 落盘提炼：顶象签发请求、数美 v4 封装、腾讯 Qimei REGISTER、今彩萍乡 wtoken；不含密钥、画像原值和可直接打生产的脚本 |
| [softard-android-reverse-compilation.md](./mobile-app-reverse/softard-android-reverse-compilation.md) | — (公众号归档) | `Android权限`, `ELF`, `ART`, `Smali`, `OLLVM`, `IDA`, `UnCrackable`, `DEX string_ids` | Softard 13 篇：权限模型、ELF/SO、ART、Smali patch、OLLVM 与 IDA 追 native 算法；不含订阅/会员推广 |
| [uiautomator-privacy-consent-tap.md](./mobile-app-reverse/uiautomator-privacy-consent-tap.md) | — (公众号归档) | `uiautomator`, `adb input tap`, `隐私协议`, `pm clear`, `设备注册`, `UI dump` | 首次启动隐私/权限弹窗：uiautomator dump 解析 bounds，对「同意/允许」中心点 `input tap`；界面问题不必先 Frida |
| [wechat-mp-oss-landscape.md](./mobile-app-reverse/wechat-mp-oss-landscape.md) | weixin_download | `wechatDownload`, `list_ex`, `wechrss`, `weread-omni`, `GetA8Key`, `WeChat-H5-DevTools`, `__biz`, `mid`, `idx` | 公众号开源库按会话平面对照：getmsg 内置浏览器发证、MP list_ex 2026-07-30 收紧、读书 /mp/chapters 与 RefreshToken、GetA8Key sidecar、WMPF H5 调试面；不收录凭证与闭源协议栈 |

### DRM 内容获取 (`article/drm-content-acquisition/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [widevine-l3-video-download.md](./drm-content-acquisition/widevine-l3-video-download.md) | ktv-smart-jp-download | `Widevine`, `L3 CDM`, `KeyDive`, `pywidevine`, `license 重放`, `PSSH`, `mp4decrypt`, `shaka-player`, `videomarket`, `CENC` | Widevine L3 视频下载七步管道：播放链路定位、manifest/PSSH 按 system ID 甄别、Android 真机 L3 CDM 自提取、pywidevine license 重放、Bento4/ffmpeg 解密合并；桌面 Firefox CDM 4.10.3050 无现成 dumper，真机自提 5 分钟闭环 |

### Web 逆向 (`article/web-reverse/`)

| 文章 | 来源项目 | 关键词 | 摘要 |
|------|----------|--------|------|
| [51job-webpack-analysis.md](./web-reverse/51job-webpack-analysis.md) | 51job-web-reverse | `Webpack 4`, `Vue 2.7`, `模块自吐`, `加密定位`, `sign`, `AES`, `SM4`, `国密`, `webpackJsonp` | 51job Webpack 模块自吐分析：1634 个 factory 模块识别、加密/签名模块定位、Vue 组件反编译、chunk 加载机制 |
| [anti-crawler-web-reverse-compilation.md](./web-reverse/anti-crawler-web-reverse-compilation.md) | — (公众号归档) | `Akamai`, `JSVMP`, `Babel AST`, `控制流平坦化`, `Chrome DevTools`, `Hook`, `反Hook` | Akamai 参数、JSVMP、AST 反混淆与 Chrome DevTools 调试对抗的 16 篇实战合集 |
| [benru-web-reverse-compilation.md](./web-reverse/benru-web-reverse-compilation.md) | — (公众号归档) | `WBI签名`, `AST`, `JS混淆`, `Node补环境`, `mitmproxy`, `动态参数`, `Webpack RPC`, `Python还原` | 本如笔记 12 篇 Web 逆向与协议恢复实战，从参数定位、反混淆和补环境延伸到 RPC 与 Python 复现 |
| [yuanrenxue-web-reverse-compilation.md](./web-reverse/yuanrenxue-web-reverse-compilation.md) | — (公众号归档) | `JS Cookie`, `参数加密`, `反调试`, `字符串混淆`, `控制流混淆`, `微信小程序`, `AI逆向` | 猿人学 7 篇 Web 与 JavaScript 逆向方法论，保留长期可复用的定位、调试和反混淆路径 |
| [products.md](./web-reverse/products.md) | — (JS终结计划课程方法论) | `风控产品`, `验证码`, `签名`, `WAF`, `反爬`, `命中索引`, `DataDome`, `Akamai`, `Kasada`, `瑞数`, `reCAPTCHA`, `Arkose Labs`, `FunCaptcha`, `同盾`, `京东`, `JCAP`, `tp=22`, `空间推理`, `h5st`, `抖音`, `阿里云验证码`, `腾讯验证码`, `网易易盾`, `NECaptcha`, `F5`, `PerimeterX`, `reese84`, `小红书`, `x-s`, `快手`, `__NS_sig3`, `MTOP` | 安全产品强制命中索引：验证码/签名/状态型链的命中特征 → 产品文档映射，含京东 JCAP `tp` 题型分流、网易易盾 jigsaw，以及小红书 xs、快手 NS 签名与阿里 MTOP H5 |
| [sign-landing-methods.md](./web-reverse/sign-landing-methods.md) | cv-cat | `纯算`, `Node vm`, `execjs`, `Frida RPC`, `a_bogus`, `x-s`, `__NS_sig3`, `h5st`, `provenance`, `canonical query` | 平台签名落地选型：宿主原语可钩则纯算，字节码 VM 用隔离出参，App Native 走实例 RPC；产品切开验收，不把 Cookie 随机串当成 serverAccepted |
| [vmp-host-primitive-to-purecalc.md](./web-reverse/vmp-host-primitive-to-purecalc.md) | cv-cat | `stack VM`, `CryptoJS.MD5`, `宿主原语`, `盐探针`, `webSignUrl` | VMP 方法论：先钩 MD5/SM3/SubtleCrypto 读明文，换 Cookie 区分常量池和会话，只移植闭合边界 |
| [material-provenance-ledger.md](./web-reverse/material-provenance-ledger.md) | cv-cat | `provenance`, `server_issued`, `unproven_synthetic`, `TTL`, `状态机` | 材料出处账本：本地可造、服务端下发、隔离程序、设备绑定；缺字段失败或回缓存，不随机占位 |
| [request-plane-failure-translation.md](./web-reverse/request-plane-failure-translation.md) | cv-cat | `请求面`, `bdturing`, `空 body`, `status_code`, `同名参数` | 一条平台请求拆成签名/会话/完整性/设备/传输；HTTP 200 和空 body 按面翻译，不同生产函数不算同一参数 |
| [purecalc-vs-oracle-cost.md](./web-reverse/purecalc-vs-oracle-cost.md) | cv-cat | `预言机`, `Brook`, `canary`, `js_security`, `53KB` | 纯算与预言机成本账：明文闭合就纯算；大段字节码跑官方脚本并写明不移植的原因，出参不得标 purecalc |
| [fail-closed-completion-gate.md](./web-reverse/fail-closed-completion-gate.md) | cv-cat | `fail-closed`, `SignerError`, `localReproduced`, `serverAccepted`, `tk03` | 缺字段、长度不对、抓包回放都在发送前失败；业务 JSON 读回才是 serverAccepted |
| [thin-wrapper-vs-purecalc.md](./web-reverse/thin-wrapper-vs-purecalc.md) | cv-cat | `execjs`, `整包`, `双写`, `完成度`, `boundary_known` | 五档完成度：边界壳、Cookie 双写、execjs 整包、隔离运行器、纯算/RPC；整包只证明参数名 |
| [endpoint-constant-table.md](./web-reverse/endpoint-constant-table.md) | cv-cat | `aid`, `page_id`, `appKey`, `version_code`, `常量表` | 端别常量表按 host 和接口填行；创作者三个 aid、直播与主站 version 不为统一抹平 |
| [session-binding-double-write.md](./web-reverse/session-binding-double-write.md) | cv-cat | `XSRF-TOKEN`, `JSESSIONID`, `ct0`, `swp_csrf_token`, `uifid` | 会话材料双写：头等于 Cookie 源字段，去掉引号或取半段，并绑对 origin |
| [isolated-node-runner-contract.md](./web-reverse/isolated-node-runner-contract.md) | cv-cat | `stdin JSON`, `形状门`, `timeout`, `不回显`, `vm.runInThisContext` | 隔离 Node 运行器合同：最后一行 JSON、长度或前缀、显式时钟、失败日志不带 Cookie |
| [capture-alignment-traps.md](./web-reverse/capture-alignment-traps.md) | cv-cat | `空值字段`, `同名 t`, `parse_qsl`, `$HE_`, `排序只用于签名` | 抓包对齐偏差：空值、同名键、保留 $ 和 Base64 填充、排序不改线上顺序、冻结头不被 Set-Cookie 覆盖 |
| [douyin-web-request-planes.md](./web-reverse/douyin-web-request-planes.md) | cv-cat | `a_bogus`, `host`, `aid`, `page_id`, `signed_url`, `bd-ticket-guard`, `check_risk_response` | 抖音 Web 七条链的真实装配：受保护 path 必须发 sign_url，评论只读票据，直播空 body 不是签名错误，创作者三个 aid 不能合并 |
| [douyin-secsdk-websign-case.md](./web-reverse/douyin-secsdk-websign-case.md) | cv-cat | `webSignUrl`, `CryptoJS.MD5`, `canonical query`, `encodeURIComponent`, `x-secsdk-web-signature` | stack VM 先钩宿主 MD5 再纯算规范化 query：原序、value 重编码、key 只解码、timestamp 追加，签完的 URL 才是线上 URL |
| [douyin-session-materials-case.md](./web-reverse/douyin-session-materials-case.md) | cv-cat | `msToken`, `x-ms-token`, `bd-ticket-guard`, `x-tt-session-dtrait`, `__ac_signature`, `provenance` | 抖音会话材料四链：mssdk 签发 msToken、只读/写入票据、按 path 重算 dtrait、acrawler 失败不写随机 Cookie |
| [tiktok-web-signing-planes.md](./web-reverse/tiktok-web-signing-planes.md) | cv-cat | `X-Bogus`, `X-Gnarly`, `X-Dynosaur`, `msToken`, `fail-closed`, `5.3.2`, `5.1.0` | TikTok HTTP 按 path 分无签、Creator 三字段和 legacy 四字段；legacy X-Bogus 是字面量 1，缺字段不回填抓包签名 |
| [tiktok-frontier-ticket-shop-case.md](./web-reverse/tiktok-frontier-ticket-shop-case.md) | cv-cat | `frontierSign`, `tt-ticket-guard`, `Shop BSID`, `oec_lucifer`, `ECDSA` | TikTok 三条旁路：16 字符 frontierSign、只重算不复放的 ticket-guard、Shop 预签 URL 必须保留 Base64 填充 |
| [xiaohongshu-assembly-case.md](./web-reverse/xiaohongshu-assembly-case.md) | cv-cat | `parameter_sources`, `HostCookieStore`, `ordered_wire_headers`, `websectiga`, `_dsf` | 小红书现行装配：六桶 provenance、DS 失败用缓存不随机、PC/Creator/蒲公英/千帆切开，body 定形后不再 json= |
| [signed-query-wire-contract.md](./web-reverse/signed-query-wire-contract.md) | cv-cat | `canonical query`, `default_headers`, `HTTP/2 cookie`, `duplicate t`, `quote` | 签完即线上：抖音两套编码、TikTok to_query、京东同名 t、快手保留 $、curl_cffi 关掉默认头 |
| [taobao-h5-mtop-lwp-case.md](./web-reverse/taobao-h5-mtop-lwp-case.md) | cv-cat | `MTOP`, `_m_h5_tk`, `12574478`, `JSONP`, `LWP`, `cntaobao` | 淘宝 H5 sign 是 token&t&appKey&data 的 MD5；私信是钉钉 LWP，仓内 goofish URL 是拷贝残留 |
| [xianyu-web-mtop-case.md](./web-reverse/xianyu-web-mtop-case.md) | cv-cat | `34839810`, `goofish`, `tfstk`, `空 sign`, `_m_h5_tk` | 闲鱼 Web 与淘宝同形 MD5，但 appKey、POST 和空 sign 换票不同；tfstk 是 Node vm，不能填进 App x-sign |
| [xianyu-android-sign-rpc-case.md](./web-reverse/xianyu-android-sign-rpc-case.md) | cv-cat | `InnerSignImpl`, `getUnifiedSign`, `21407387`, `ttid`, `g-acs` | 闲鱼 App：spawn 后 hook 一次即摘，六参 overload 出 x-sign 族；ttid/appKey 必须与被 hook 进程同源 |
| [bilibili-wbi-geetest-case.md](./web-reverse/bilibili-wbi-geetest-case.md) | cv-cat | `WBI`, `w_rid`, `wts`, `mixin`, `correspondPath`, `极验` | B 站 WBI 排序只用于签名、线上保原序；极验 w 本地算、点选另层；correspondPath 是 RSA-OAEP 续期入场券 |
| [jd-h5st-runtime-case.md](./web-reverse/jd-h5st-runtime-case.md) | cv-cat | `h5st 5.3`, `tk03`, `request_algo`, `js_security`, `searchWare`, `SHA-256` | 京东搜索：常驻 Node 跑未改 js_security，body 先 SHA-256 再签，h5st 第 4 段必须 tk03，同名 t 用键值列表发送 |
| [kuaishou-landing-case.md](./web-reverse/kuaishou-landing-case.md) | cv-cat | `__NS_hxfalcon`, `kww`, `caver`, `weapon_oracle`, `__NS_sig3` | 快手资料接口：冻结 kww、白名单 hxfalcon、query 保留 $；kwf/kws 留 Node oracle，400002 走滑块 |
| [zhihu-xzse96-execjs-case.md](./web-reverse/zhihu-xzse96-execjs-case.md) | cv-cat | `x-zse-96`, `x-zse-93`, `d_c0`, `execjs`, `tv` | 知乎评论头：整包 zhihu.js 的 tv 吃 URL 和 d_c0，x-zse-96 为 2.0_ 加 signature，不能标纯算 |
| [weibo-request-planes-case.md](./web-reverse/weibo-request-planes-case.md) | cv-cat | `XSRF-TOKEN`, `x-xsrf-token`, `X-Up-Auth`, `CRC` | 微博 PC 是 Cookie 双写，移动是另一套头，创作者上传另算文件 MD5 和自定义 CRC；weibo.js 未接入运行时 |
| [toutiao-abogus-execjs-case.md](./web-reverse/toutiao-abogus-execjs-case.md) | cv-cat | `a_bogus`, `_signature`, `get_ab`, `aid=24`, `execjs` | 头条 a_bogus 与 _signature 来自两包 execjs，feed aid=24，不是抖音 ab_pure |
| [xigua-unsigned-query-case.md](./web-reverse/xigua-unsigned-query-case.md) | cv-cat | `aid=1768`, `msToken`, `X-Bogus`, `AES-CBC` | 西瓜列表把 msToken/X-Bogus/_signature 留空；播放 AES-CBC 函数未被列表 API 调用 |
| [binance-cms-header-case.md](./web-reverse/binance-cms-header-case.md) | cv-cat | `fvideo-id`, `fvideo-token`, `csrftoken`, `BNC_FV_KEY`, `device-info` | 币安公告列表：fvideo-id 来自 Cookie，fvideo-token 吃另一个 Cookie 字段，csrftoken 为本地 md5 空串 |
| [linkedin-voyager-csrf-case.md](./web-reverse/linkedin-voyager-csrf-case.md) | cv-cat | `JSESSIONID`, `csrf-token`, `queryId`, `voyager` | 领英 csrf-token 是 JSESSIONID 去引号双写，GraphQL queryId 从当前页面 define 提取 |
| [instagram-doc-id-case.md](./web-reverse/instagram-doc-id-case.md) | cv-cat | `doc_id`, `x-ig-app-id`, `web_profile_info`, `graphql` | Instagram 从用户页 HTML 抽 app_id 和 doc_id；时间线主路径未挂 x-csrftoken 模板 |
| [x-twitter-graphql-case.md](./web-reverse/x-twitter-graphql-case.md) | cv-cat | `ct0`, `x-csrf-token`, `Bearer`, `features`, `GraphQL` | X 搜索：调用方 Bearer 加 ct0 双写，features 是写死快照，仓内无 guest 刷新和本地签名 |
| [feishu-csrf-frontier-case.md](./web-reverse/feishu-csrf-frontier-case.md) | cv-cat | `swp_csrf_token`, `x-csrf-token`, `access_key`, `msg-frontier` | 飞书网页 CSRF 与 frontier 长连分链：swp_csrf_token 来自 accounts/csrf，access_key 来自页面 JS |
| [wechat-oa-mp-cgi-case.md](./web-reverse/wechat-oa-mp-cgi-case.md) | cv-cat | `searchbiz`, `appmsgpublish`, `token`, `fakeid`, `list_ex` | 公众号后台 CGI：token 与 Cookie 外置透传，ret!=0 不是成功；公开文章 HTML 不带 token |
| [autohome-cookie-boundary-case.md](./web-reverse/autohome-cookie-boundary-case.md) | cv-cat | `JSONP`, `jsonprv`, `clubajax`, `_appid` | 汽车之家详情是 Cookie 加 JSONP 剥壳，没有本地 sign；创作者面只有时间戳和 _appid |
| [baijiahao-runtime-header-case.md](./web-reverse/baijiahao-runtime-header-case.md) | cv-cat | `window.runtime`, `uk`, `Tenger-Mhor`, `Hmery-Time`, `JSONP` | 百家号 uk 来自页面 runtime，Tenger-Mhor 等于 Cookie Hmery-Time，仓内无 gtoken 实现 |
| [browser-env-objects.md](./web-reverse/browser-env-objects.md) | — (JS终结计划课程方法论) | `补环境`, `DOM/BOM`, `浏览器对象`, `WebAPI`, `指纹`, `Worker`, `MessagePort`, `Canvas`, `WebGL`, `navigator`, `crypto` | Web 补环境浏览器对象参考：20 个 DOM/BOM/Web API 对象的检测面、常见坑与观察优先级，五维度补环境纪律 |
| [unpacked-mv3-native-updater.md](./web-reverse/unpacked-mv3-native-updater.md) | mouchenjie-ai-plugin | `MV3`, `sideload`, `自定义协议`, `PyInstaller 更新器`, `加载已解压扩展`, `渠道 zip` | 未上架 Chrome MV3 的本机更新器架构：渠道清单 + 对象存储 zip、HKCU 协议唤醒、本机进度口和打包合同，可复用到自有插件 sideload 分发 |
| [datadome-env-patch.md](./web-reverse/datadome-env-patch.md) | — (公众号归档) | `DataDome`, `plv3`, `payload`, `iframe Realm`, `OffscreenCanvas`, `jsdom`, `VM 分叉` | DataDome 无感 interstitial 补环境：jsdom+vm 跑原脚本出参，按 Realm 生命周期、Worker 异步链和 VM 第一处分叉对齐；成功口径是 redirect 后新 Session 业务 200 |
| [ai-assisted-web-reverse-compilation.md](./web-reverse/ai-assisted-web-reverse-compilation.md) | — (公众号归档) | `h5st`, `a_bogus`, `x-s`, `x-s-common`, `JSVMP`, `RSA`, `fangdir`, `X-Gnarly`, `Shein`, `Dewu`, `md5__1038` | AI辅助逆向手记 20 篇：京东 h5st v5.3、瑞数 fangdir、抖音 a_bogus、小红书 xs、Shein/得物签名与 JSVMP/RSA 方法论，目标已脱敏 |
| [koohai-reverse-notes-compilation.md](./web-reverse/koohai-reverse-notes-compilation.md) | — (公众号归档) | `KhBox`, `补环境`, `Illegal invocation`, `Canvas`, `jsdom`, `JSVMP`, `FART`, `WebView`, `IDA MD5` | 零基础爬虫第一天 17 篇：KhBox 补环境与 Node 编译、BrowserLeaks、AST/JSVMP，以及 FART/WebView/IDA 识别 MD5 |
| [aigei-safe-search-ticket-chain.md](./web-reverse/aigei-safe-search-ticket-chain.md) | aigei | `safe-search 票据链`, `icon.png 藏票据`, `搜索权限门`, `AES-ECB cnkierjj`, `N@32`, `响应体数据流`, `request-parameter-lineage`, `companion_response_audit`, `403 权限不足`, `vcode-normal` | 爱给网筛选列表翻页 403 根因：带 term 列表每页须走 icon.png 签发票据 → /f/d → 列表的搜索授权链，票据藏响应体 base64 尾部且按页绑定；边界已对齐仍非 200 时先做伴随请求响应体数据流审计 |

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
- **AES-ECB `cnkierjj` N 轮 + N@32（爱给网 /f/d v 与 icon token 同构）**: [aigei-safe-search](./web-reverse/aigei-safe-search-ticket-chain.md)
- **HMAC-SHA1 → Base64 → URL-encode（豆瓣 sig）**: [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md)
- **SHA1(android_id) 切 g0:g2:g1（数盟 AYk） / XOR+zlib d2api 信封**: [shuzilm-libdu](./anti-detection/shuzilm-libdu-fingerprint.md)
- **AES-CBC 由 uid MD5 对半作 key/iv（韩小圈 sign）**: [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md)
- **RC4/Salsa20/ChaCha20/GCM 流密码实现**: [xfq-crypto](./signature-algorithms/xfq-crypto-notes-compilation.md), [shopee-shpssdk](./signature-algorithms/shopee-shpssdk-request-defense.md)
- **RC6 / xxhash32 / mmh3 / 自定义 SHA-256 / 自定义 Base64（Shopee SHPSSDK）**: [shopee-shpssdk](./signature-algorithms/shopee-shpssdk-request-defense.md)
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
- **CRC64-ECMA PL.ck / TEA-XTEA ET 编码 / HMAC-SHA1 22 字段 INPUT（闲鱼 EEID，签名说法待验证）**: [xianyu-eeid](./anti-detection/xianyu-eeid-risk-control.md)
- **DES-ECB（x-mini-wua 15 个 8 字节块）**: [alibaba-mtop-four-headers](./signature-algorithms/alibaba-mtop-four-headers.md)
- **MD5 state1 + SHA1 x-sign / Park-Miller 交替键（SG 70102）**: [alibaba-mtop-four-headers](./signature-algorithms/alibaba-mtop-four-headers.md)
- **MD5(uifid_ts_VM_CONST_canonical_query)（抖音 webSign）**: [douyin-secsdk](./web-reverse/douyin-secsdk-websign-case.md)
- **WBI md5(sorted query + mixin) / correspondPath RSA-OAEP-SHA256**: [bilibili-wbi](./web-reverse/bilibili-wbi-geetest-case.md)
- **MTOP H5 md5(token&t&appKey&data)**: [taobao-h5](./web-reverse/taobao-h5-mtop-lwp-case.md), [xianyu-web](./web-reverse/xianyu-web-mtop-case.md)
- **ECDSA P-256 ticket-guard / AES-GCM encrypt_ticket**: [tiktok-frontier](./web-reverse/tiktok-frontier-ticket-shop-case.md), [douyin-session](./web-reverse/douyin-session-materials-case.md)
- **h5st body 预 SHA-256**: [jd-h5st-runtime](./web-reverse/jd-h5st-runtime-case.md)
- **RSA-1024 固定 0x01 填充 / 公钥 DER 锚**: [ai-assisted-web](./web-reverse/ai-assisted-web-reverse-compilation.md)
- **WBI/Base64/常见哈希与动态参数识别**: [benru-web](./web-reverse/benru-web-reverse-compilation.md), [yuanrenxue-web](./web-reverse/yuanrenxue-web-reverse-compilation.md), [yuanrenxue-app](./mobile-app-reverse/yuanrenxue-mobile-app-reverse-compilation.md)
- **MTOP H5 `_m_h5_tk` MD5 sign**: [alibaba-mtop-h5](./web-reverse/products/alibaba-mtop-h5.md), [sign-landing](./web-reverse/sign-landing-methods.md)
- **阿里 App MTOP 四头（x-sign / x-sgext / x-mini-wua / x-umt，SG 70102）**: [alibaba-mtop-four-headers](./signature-algorithms/alibaba-mtop-four-headers.md), [mtop-innersign-rpc](./mobile-app-reverse/mtop-innersign-rpc.md)
- **易盾自定义 xor-b64 / 非标准 AES / 47 维轨迹特征**: [products](./web-reverse/products.md)

### 协议
- **TLS 1.3 变体**: [mmtls](./protocols/mmtls-protocol-analysis.md)
- **PSK 0-RTT**: [mmtls](./protocols/mmtls-protocol-analysis.md)
- **自定义应用帧**: [mmtls](./protocols/mmtls-protocol-analysis.md)
- **微信公众号五套会话（WebView getmsg / MP 后台 / 微信读书 / GetA8Key / 客户端 mmtls）**: [wechat-mp-sessions](./protocols/wechat-mp-session-planes.md), [wechat-mp-oss](./mobile-app-reverse/wechat-mp-oss-landscape.md)
- **`profile_ext/getmsg` 短时 `uin/key/pass_ticket`**: [wechat-mp-sessions](./protocols/wechat-mp-session-planes.md), [wechat-mp-http](./protocols/wechat-mp-http-surface.md), [wechat-mp-oss](./mobile-app-reverse/wechat-mp-oss-landscape.md)
- **`getappmsgext` / `appmsg_comment` / `appmsgalbum getalbum`**: [wechat-mp-http](./protocols/wechat-mp-http-surface.md)
- **MP 后台 `searchbiz` / `appmsgpublish list_ex` / `free_publish`**: [wechat-mp-oss](./mobile-app-reverse/wechat-mp-oss-landscape.md)
- **微信读书 `i.weread.qq.com/mp/chapters` / `MP_WXS_` / RefreshToken**: [wechat-mp-oss](./mobile-app-reverse/wechat-mp-oss-landscape.md)
- **`GetA8Key` / `MpGetA8Key` / `X-WECHAT-KEY`**: [wechat-mp-sessions](./protocols/wechat-mp-session-planes.md), [wechat-mp-oss](./mobile-app-reverse/wechat-mp-oss-landscape.md)
- **ACE UDP 加密上报（tss_sdk_encryptpacket）**: [ace-deviceuniqueid](./anti-detection/android-ace-deviceuniqueid.md)
- **自定义 URL 协议唤醒本机更新器**: [unpacked-mv3-updater](./web-reverse/unpacked-mv3-native-updater.md)
- **safe-search 票据链 / icon.png 响应体藏票据 / 按页绑定搜索授权**: [aigei-safe-search](./web-reverse/aigei-safe-search-ticket-chain.md)
- **HTTP DNS**: [mmtls](./protocols/mmtls-protocol-analysis.md)
- **Protobuf/gRPC**: [paopao-android](./mobile-app-reverse/paopao-android-reverse-compilation.md), [yuanrenxue-app](./mobile-app-reverse/yuanrenxue-mobile-app-reverse-compilation.md)
- **App 设备注册 / 拦截器式纯协议客户端**: [protocol-admission](./mobile-app-reverse/protocol-admission-four-gates.md), [pure-protocol-sdk](./mobile-app-reverse/pure-protocol-sdk-reconstruction.md), [protocol-register-order](./mobile-app-reverse/protocol-register-packet-order.md), [kimi-ttencrypt](./mobile-app-reverse/kimi-device-register-ttencrypt.md), [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md), [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **设备注册包顺序 / 事件线程 / 日志通道 / 云端身份前置**: [protocol-register-order](./mobile-app-reverse/protocol-register-packet-order.md), [pure-protocol-sdk](./mobile-app-reverse/pure-protocol-sdk-reconstruction.md)
- **顶象 DXRisk `/udid/m1` riskToken 签发**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **数美 `deviceprofile/v4` data/tn/ep**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **闲鱼 EEID 注册 / ACS-MUM 验证 / 后续请求 `x-eeid`**: [xianyu-eeid](./anti-detection/xianyu-eeid-risk-control.md)
- **数盟 d2api/report / `cdd`=`x-ms-id` / `vB2` 画像**: [shuzilm-libdu](./anti-detection/shuzilm-libdu-fingerprint.md)
- **腾讯 snowflake Qimei REGISTER `/ola/v2`**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **B 站 buvid / deviceid RSA+AES 信封 / fp_local**: [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md)
- **字节 volces `device_register` / `tt_info` / `ttEncrypt`**: [kimi-ttencrypt](./mobile-app-reverse/kimi-device-register-ttencrypt.md)
- **App 协议准入四关（设备/签名/主机/传输 + 空壳完成门 + 引导激活）**: [protocol-admission](./mobile-app-reverse/protocol-admission-four-gates.md)
- **TikTok / TTNet `device_register` / `X-Argus` / `*-boot`（四关推导语料）**: [protocol-admission](./mobile-app-reverse/protocol-admission-four-gates.md)
- **SFSecurity（nonce/timestamp/devicetoken/sign）**: [boluobao-sfsecurity](./signature-algorithms/boluobao-sfsecurity-trace.md)
- **Shopee `x-sap-ri` / SHPSSDK requestDefense 四键头**: [shopee-shpssdk](./signature-algorithms/shopee-shpssdk-request-defense.md)
- **TLS/HTTP2 网络指纹**: [anti-crawler-risk](./anti-detection/anti-crawler-risk-control-compilation.md), [ruyi-browser](./anti-detection/ruyi-browser-anti-detection-compilation.md)
- **WBI/Protobuf/TCP/mTLS 与认证协议**: [benru-web](./web-reverse/benru-web-reverse-compilation.md), [yuanrenxue-app](./mobile-app-reverse/yuanrenxue-mobile-app-reverse-compilation.md)
- **钉钉 LWP WebSocket（淘宝/闲鱼 IM）**: [alibaba-mtop-h5](./web-reverse/products/alibaba-mtop-h5.md)
- **阿里 App MTOP 四头（SG 70102 / 会话画像 + data2sign）**: [alibaba-mtop-four-headers](./signature-algorithms/alibaba-mtop-four-headers.md)
- **淘宝/闲鱼 H5 MTOP sign 与钉钉 LWP 分链**: [taobao-h5](./web-reverse/taobao-h5-mtop-lwp-case.md), [xianyu-web](./web-reverse/xianyu-web-mtop-case.md), [alibaba-mtop-h5](./web-reverse/products/alibaba-mtop-h5.md)
- **TikTok Web 签名面 / frontierSign / Shop BSID**: [tiktok-planes](./web-reverse/tiktok-web-signing-planes.md), [tiktok-frontier](./web-reverse/tiktok-frontier-ticket-shop-case.md)
- **B 站 WBI / bili_ticket / correspondPath**: [bilibili-wbi](./web-reverse/bilibili-wbi-geetest-case.md)
- **飞书 accounts/csrf 与 msg-frontier**: [feishu-csrf](./web-reverse/feishu-csrf-frontier-case.md)
- **公众号后台 searchbiz / appmsgpublish（token 透传）**: [wechat-oa-cgi](./web-reverse/wechat-oa-mp-cgi-case.md), [wechat-mp-sessions](./protocols/wechat-mp-session-planes.md)
- **Akamai JA3/JA4/HTTP2 指纹**: [yuanrenxue-anti](./anti-detection/yuanrenxue-anti-detection-compilation.md)

### 反检测/对抗
- **WAF 绕过**: [51job-anti-detection](./anti-detection/51job-anti-detection-analysis.md)
- **设备指纹**: [51job-anti-detection](./anti-detection/51job-anti-detection-analysis.md), [pure-protocol-sdk](./mobile-app-reverse/pure-protocol-sdk-reconstruction.md), [protocol-register-order](./mobile-app-reverse/protocol-register-packet-order.md), [ace-deviceuniqueid](./anti-detection/android-ace-deviceuniqueid.md), [xfq-device-fp](./anti-detection/xfq-device-fp-compilation.md), [fp-consistency](./anti-detection/device-fingerprint-consistency-modeling.md), [shuzilm-libdu](./anti-detection/shuzilm-libdu-fingerprint.md), [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md), [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md), [protocol-admission](./mobile-app-reverse/protocol-admission-four-gates.md), [xianyu-eeid](./anti-detection/xianyu-eeid-risk-control.md)
- **阿里 SecurityGuard EEID（Mini/ET 探针 / SGEXT / SG 文件 mtime / UTDID / sgcookie）**: [xianyu-eeid](./anti-detection/xianyu-eeid-risk-control.md)
- **数盟 libdu.so 指纹对照 / `x-ms-id` 签发**: [shuzilm-libdu](./anti-detection/shuzilm-libdu-fingerprint.md)
- **指纹一致性 / 联合分布 / 分层装配**: [fp-consistency](./anti-detection/device-fingerprint-consistency-modeling.md), [protocol-admission](./mobile-app-reverse/protocol-admission-four-gates.md), [xfq-device-fp](./anti-detection/xfq-device-fp-compilation.md)
- **时间间隔分布（泊松 / 对数正态）与指纹生命周期**: [fp-consistency](./anti-detection/device-fingerprint-consistency-modeling.md)
- **数美 Java a* / Native b* 画像生命周期**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **腾讯 Qimei 设备注册纯协议**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md), [xfq-device-fp](./anti-detection/xfq-device-fp-compilation.md)
- **libmsaoaidsec 加载期检测（leave 缺失 / call_constructors 观察窗）**: [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md), [xfq-android-cases](./mobile-app-reverse/xfq-android-cases-compilation.md)
- **风控熵源 / 伪随机 / 协议指纹演进**: [xfq-device-fp](./anti-detection/xfq-device-fp-compilation.md), [fp-consistency](./anti-detection/device-fingerprint-consistency-modeling.md)
- **Widevine / deviceUniqueId / Key Attestation / Play Integrity**: [ace-deviceuniqueid](./anti-detection/android-ace-deviceuniqueid.md), [shuzilm-libdu](./anti-detection/shuzilm-libdu-fingerprint.md)
- **加固绕过 / whole-DEX 分流**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **App 壳/wrapper 命中（Jiagu/Legu/SecNeo/NIS）**: [app-protectors](./packing-bypass/app-protectors.md)
- **反调试 (ptrace/TracerPid)**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **Frida 终止链与 prctl 定位**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **方法抽取 / CodeItem 恢复**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **WebDriver/CDP 检测**: [51job-anti-detection](./anti-detection/51job-anti-detection-analysis.md), [chromium-fingerprint-compilation](./anti-detection/chromium-fingerprint-compilation.md)
- **Chromium 源码修改/指纹浏览器**: [chromium-fingerprint-compilation](./anti-detection/chromium-fingerprint-compilation.md)
- **TLS/JA3/JA4 指纹**: [chromium-fingerprint-compilation](./anti-detection/chromium-fingerprint-compilation.md), [pure-protocol-sdk](./mobile-app-reverse/pure-protocol-sdk-reconstruction.md), [protocol-admission](./mobile-app-reverse/protocol-admission-four-gates.md)
- **空成功 / HTTP 200 空壳 / 注册后激活 / 指纹与鉴权融合**: [protocol-admission](./mobile-app-reverse/protocol-admission-four-gates.md)
- **公众号 `getmsg ret=-3` / 验证页 / `list_ex ret=200013` 不得当 0 篇成功**: [wechat-mp-sessions](./protocols/wechat-mp-session-planes.md)
- **注册事件/日志通道与上量风控认知**: [protocol-register-order](./mobile-app-reverse/protocol-register-packet-order.md), [pure-protocol-sdk](./mobile-app-reverse/pure-protocol-sdk-reconstruction.md), [xfq-device-fp](./anti-detection/xfq-device-fp-compilation.md), [fp-consistency](./anti-detection/device-fingerprint-consistency-modeling.md)
- **Canvas/WebGL 指纹**: [chromium-fingerprint-compilation](./anti-detection/chromium-fingerprint-compilation.md)
- **SSL Pinning**: [app-reverse-global-map](./mobile-app-reverse/app-reverse-global-map.md), [app-reverse-environment-setup](./mobile-app-reverse/app-reverse-environment-setup.md)
- **Root/Magisk 隐藏**: [app-reverse-environment-setup](./mobile-app-reverse/app-reverse-environment-setup.md)
- **验证码与行为风控**: [anti-crawler-risk](./anti-detection/anti-crawler-risk-control-compilation.md)
- **CloakBrowser humanize 鼠标轨迹 / 包装层贝塞尔**: [cloakbrowser-humanize](./anti-detection/cloakbrowser-humanize-trajectory.md)
- **响应体藏数据 / Content-Type 语义不符 / 搜索权限门 403**: [aigei-safe-search](./web-reverse/aigei-safe-search-ticket-chain.md), [products](./web-reverse/products.md), [google-recaptcha-v3](./web-reverse/products/google-recaptcha-v3.md), [pure-protocol-sdk](./mobile-app-reverse/pure-protocol-sdk-reconstruction.md)
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
- **腾讯 (微信/应用宝)**: [mmtls](./protocols/mmtls-protocol-analysis.md), [wechat-mp-sessions](./protocols/wechat-mp-session-planes.md), [wechat-mp-oss](./mobile-app-reverse/wechat-mp-oss-landscape.md)
- **微信公众号 / mp.weixin.qq.com / 微信读书 / WMPF 内置浏览器 H5**: [wechat-mp-sessions](./protocols/wechat-mp-session-planes.md), [wechat-mp-http](./protocols/wechat-mp-http-surface.md), [wechat-mp-oss](./mobile-app-reverse/wechat-mp-oss-landscape.md), [weixin-archive-runtime](./collection-engineering/weixin-http-archive-runtime.md)
- **腾讯 ACE / Widevine DRM / libtersafe**: [ace-deviceuniqueid](./anti-detection/android-ace-deviceuniqueid.md)
- **阅文 (起点)**: [qidian-fock](./signature-algorithms/qidian-fock-signature.md), [qidian-so](./native-analysis/qidian-so-analysis.md), [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **阿里 (ACW/飞林)**: [51job-anti-detection](./anti-detection/51job-anti-detection-analysis.md)
- **360 (Jiagu)**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md), [app-protectors](./packing-bypass/app-protectors.md)
- **网易 NIS / 易盾加固（App）**: [app-protectors](./packing-bypass/app-protectors.md), [paopao-android](./mobile-app-reverse/paopao-android-reverse-compilation.md)
- **51job**: [51job-anti-detection](./anti-detection/51job-anti-detection-analysis.md), [51job-webpack](./web-reverse/51job-webpack-analysis.md)
- **CSDN/w1101662433 (fivcan)**: [chromium-fingerprint-compilation](./anti-detection/chromium-fingerprint-compilation.md)
- **Android/App 逆向**: [app-reverse-global-map](./mobile-app-reverse/app-reverse-global-map.md), [app-reverse-environment-setup](./mobile-app-reverse/app-reverse-environment-setup.md), [jvm-mindmap](./mobile-app-reverse/jvm-mindmap.md), [pure-protocol-sdk](./mobile-app-reverse/pure-protocol-sdk-reconstruction.md), [protocol-register-order](./mobile-app-reverse/protocol-register-packet-order.md), [ace-deviceuniqueid](./anti-detection/android-ace-deviceuniqueid.md), [fp-consistency](./anti-detection/device-fingerprint-consistency-modeling.md), [shuzilm-libdu](./anti-detection/shuzilm-libdu-fingerprint.md), [xfq-android-cases](./mobile-app-reverse/xfq-android-cases-compilation.md), [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md), [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md), [protocol-admission](./mobile-app-reverse/protocol-admission-four-gates.md)
- **HotSpot / JDK 8 Metaspace**: [jvm-mindmap](./mobile-app-reverse/jvm-mindmap.md)
- **AOSP / ROM 改造（CA/APatch/WebView）**: [xfq-aosp-rom](./mobile-app-reverse/xfq-aosp-rom-compilation.md)
- **知识星球：逆向学习交流**: [xfq-crypto](./signature-algorithms/xfq-crypto-notes-compilation.md), [xfq-android-cases](./mobile-app-reverse/xfq-android-cases-compilation.md), [xfq-unidbg](./native-analysis/xfq-unidbg-native-compilation.md), [xfq-aosp-rom](./mobile-app-reverse/xfq-aosp-rom-compilation.md), [xfq-device-fp](./anti-detection/xfq-device-fp-compilation.md), [xfq-tools](./mobile-app-reverse/xfq-tools-debug-compilation.md), [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md)
- **语雀 xiaofeng777/android_example**: [boluobao-sfsecurity](./signature-algorithms/boluobao-sfsecurity-trace.md), [mafengwo-sha1](./signature-algorithms/mafengwo-modified-sha1-trace.md)
- **语雀 xiayutian23/htolhb**: [shopee-shpssdk](./signature-algorithms/shopee-shpssdk-request-defense.md)
- **Shopee / SHPSSDK**: [shopee-shpssdk](./signature-algorithms/shopee-shpssdk-request-defense.md)
- **菠萝包 / SFACG**: [boluobao-sfsecurity](./signature-algorithms/boluobao-sfsecurity-trace.md)
- **马蜂窝**: [mafengwo-sha1](./signature-algorithms/mafengwo-modified-sha1-trace.md), [xfq-crypto](./signature-algorithms/xfq-crypto-notes-compilation.md), [xfq-android-cases](./mobile-app-reverse/xfq-android-cases-compilation.md)
- **陌陌**: [xfq-android-cases](./mobile-app-reverse/xfq-android-cases-compilation.md)
- **GitHub xfxfxiaofeng/reverseNotes**: [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md)
- **哔哩哔哩 / 豆瓣 / 韩小圈 / 升学e网通 / 安居客 / AppsFlyer / 陌陌**: [reversenotes-android](./mobile-app-reverse/reversenotes-android-compilation.md), [xfq-android-cases](./mobile-app-reverse/xfq-android-cases-compilation.md), [protocol-register-order](./mobile-app-reverse/protocol-register-packet-order.md)
- **macOS / NAS 采集交付**: [mac-nas-spool](./collection-engineering/reliable-mac-nas-spool-delivery.md)
- **浏览器采集器稳定性（ruyipage/Firefox 崩溃/OOM）**: [browser-collector-stability](./collection-engineering/browser-collector-stability.md)
- **Clash Verge Rev / Mihomo**: [mihomo-dialer-proxy](./collection-engineering/mihomo-dialer-proxy-chain.md)
- **Akamai**: [anti-crawler-web](./web-reverse/anti-crawler-web-reverse-compilation.md), [products](./web-reverse/products.md)
- **DataDome / Kasada / PerimeterX / F5 Shape / reese84 / Cloudflare 5s**: [products](./web-reverse/products.md), [datadome-env-patch](./web-reverse/datadome-env-patch.md)
- **Kimi / 字节 volces applog**: [kimi-ttencrypt](./mobile-app-reverse/kimi-device-register-ttencrypt.md)
- **TikTok / ByteDance musically / TTNet / metasec**: [protocol-admission](./mobile-app-reverse/protocol-admission-four-gates.md), [tiktok-planes](./web-reverse/tiktok-web-signing-planes.md), [tiktok-frontier](./web-reverse/tiktok-frontier-ticket-shop-case.md)
- **抖音 Web 请求面 / webSign / 会话材料**: [douyin-planes](./web-reverse/douyin-web-request-planes.md), [douyin-secsdk](./web-reverse/douyin-secsdk-websign-case.md), [douyin-session](./web-reverse/douyin-session-materials-case.md), [products](./web-reverse/products.md)
- **微信公众号：ai辅助逆向手记**: [ai-assisted-web](./web-reverse/ai-assisted-web-reverse-compilation.md)
- **微信公众号：零基础爬虫第一天**: [koohai-notes](./web-reverse/koohai-reverse-notes-compilation.md)
- **微信公众号：Softard（Wossoneri）**: [softard-android](./mobile-app-reverse/softard-android-reverse-compilation.md), [uiautomator-consent](./mobile-app-reverse/uiautomator-privacy-consent-tap.md)
- **航班管家 / hbgjbangbang LAES**: [hangban-laes](./signature-algorithms/hangban-laes-encrypt.md)
- **瑞数 RS6**: [products](./web-reverse/products.md)
- **爱给网（aigei.com / fd.aigei.com / GeiFileLocalStore）**: [aigei-safe-search](./web-reverse/aigei-safe-search-ticket-chain.md)
- **Google reCAPTCHA v3 / invisible reload/rresp / Node 请求面**: [google-recaptcha-v3](./web-reverse/products/google-recaptcha-v3.md), [products](./web-reverse/products.md)
- **阿里（ACW/H5Sec/BxUA/验证码/MTOP H5 / App 四头）**: [51job-anti-detection](./anti-detection/51job-anti-detection-analysis.md), [products](./web-reverse/products.md), [alibaba-mtop-h5](./web-reverse/products/alibaba-mtop-h5.md), [alibaba-mtop-four-headers](./signature-algorithms/alibaba-mtop-four-headers.md)
- **腾讯（验证码/风控）**: [mmtls](./protocols/mmtls-protocol-analysis.md), [products](./web-reverse/products.md)
- **腾讯 Qimei / 应用宝设备标识**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **顶象 DXRisk**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **数美 / 小星空**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **数盟 / 数字联盟 / libdu.so**: [shuzilm-libdu](./anti-detection/shuzilm-libdu-fingerprint.md)
- **知乎**: [shuzilm-libdu](./anti-detection/shuzilm-libdu-fingerprint.md), [zhihu-xzse96](./web-reverse/zhihu-xzse96-execjs-case.md)
- **海南航空**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **今彩萍乡**: [sdk-purecalc](./mobile-app-reverse/sdk-purecalc-compilation.md)
- **网易易盾（Web NECaptcha / App NES 加固分面）**: [products](./web-reverse/products.md), [paopao-android](./mobile-app-reverse/paopao-android-reverse-compilation.md)
- **同盾 / 京东（h5st/JCAP 滑块与 tp=22 空间推理/到家）/ 抖音（a_bogus/IM/TicketGuard）/ 饿了么 / 美团 / 小红书 xs / 快手 NS / 阿里 MTOP H5**: [products](./web-reverse/products.md), [jd-h5st-runtime](./web-reverse/jd-h5st-runtime-case.md), [kuaishou-landing](./web-reverse/kuaishou-landing-case.md), [xiaohongshu-assembly](./web-reverse/xiaohongshu-assembly-case.md)
- **闲鱼 / 淘宝 App InnerSignImpl**: [mtop-innersign-rpc](./mobile-app-reverse/mtop-innersign-rpc.md), [xianyu-android](./web-reverse/xianyu-android-sign-rpc-case.md)
- **闲鱼 App EEID / 阿里 SecurityGuard 6.7 设备风控**: [xianyu-eeid](./anti-detection/xianyu-eeid-risk-control.md), [alibaba-mtop-four-headers](./signature-algorithms/alibaba-mtop-four-headers.md)
- **闲鱼 Web / 淘宝 H5**: [xianyu-web](./web-reverse/xianyu-web-mtop-case.md), [taobao-h5](./web-reverse/taobao-h5-mtop-lwp-case.md)
- **B 站 WBI / 极验 / correspondPath**: [bilibili-wbi](./web-reverse/bilibili-wbi-geetest-case.md)
- **微博 / 头条 / 西瓜**: [weibo-planes](./web-reverse/weibo-request-planes-case.md), [toutiao-execjs](./web-reverse/toutiao-abogus-execjs-case.md), [xigua-unsigned](./web-reverse/xigua-unsigned-query-case.md)
- **币安公告头 / 领英 Voyager / Instagram doc_id / X GraphQL**: [binance-cms](./web-reverse/binance-cms-header-case.md), [linkedin-csrf](./web-reverse/linkedin-voyager-csrf-case.md), [instagram-doc](./web-reverse/instagram-doc-id-case.md), [x-graphql](./web-reverse/x-twitter-graphql-case.md)
- **飞书 CSRF / frontier**: [feishu-csrf](./web-reverse/feishu-csrf-frontier-case.md)
- **汽车之家 JSONP / 百家号 runtime 头**: [autohome-boundary](./web-reverse/autohome-cookie-boundary-case.md), [baijiahao-runtime](./web-reverse/baijiahao-runtime-header-case.md)
- **豌豆荚 / 阿里 SG 70102 四头纯算**: [alibaba-mtop-four-headers](./signature-algorithms/alibaba-mtop-four-headers.md)
- **微信公众号技术归档（反爬破解社/如意私塾/泡泡以安/本如笔记/猿人学Python/ai辅助逆向手记/零基础爬虫第一天/Softard）**: [anti-crawler-web](./web-reverse/anti-crawler-web-reverse-compilation.md), [ruyi-browser](./anti-detection/ruyi-browser-anti-detection-compilation.md), [paopao-android](./mobile-app-reverse/paopao-android-reverse-compilation.md), [benru-web](./web-reverse/benru-web-reverse-compilation.md), [benru-anti](./anti-detection/benru-anti-detection-compilation.md), [yuanrenxue-web](./web-reverse/yuanrenxue-web-reverse-compilation.md), [yuanrenxue-app](./mobile-app-reverse/yuanrenxue-mobile-app-reverse-compilation.md), [yuanrenxue-anti](./anti-detection/yuanrenxue-anti-detection-compilation.md), [ai-assisted-web](./web-reverse/ai-assisted-web-reverse-compilation.md), [koohai-notes](./web-reverse/koohai-reverse-notes-compilation.md), [softard-android](./mobile-app-reverse/softard-android-reverse-compilation.md)
- **谋臣界 / 未上架 MV3 更新器**: [unpacked-mv3-updater](./web-reverse/unpacked-mv3-native-updater.md)
- **CloakBrowser / CloakHQ humanize**: [cloakbrowser-humanize](./anti-detection/cloakbrowser-humanize-trajectory.md)

### 工具/方法
- **Webpack 模块自吐**: [51job-webpack](./web-reverse/51job-webpack-analysis.md)
- **抓包+逐字节匹配**: [mmtls](./protocols/mmtls-protocol-analysis.md)
- **IDA Pro 静态分析**: [qidian-so](./native-analysis/qidian-so-analysis.md), [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md), [ace-deviceuniqueid](./anti-detection/android-ace-deviceuniqueid.md), [hangban-laes](./signature-algorithms/hangban-laes-encrypt.md), [softard-android](./mobile-app-reverse/softard-android-reverse-compilation.md)
- **ACE TSS SDK / libtersafe 上报链**: [ace-deviceuniqueid](./anti-detection/android-ace-deviceuniqueid.md)
- **radare2 快速侦察**: [qidian-so](./native-analysis/qidian-so-analysis.md)
- **rizin + native trace 对 key（数盟 vB2 字符串 char+39 / shuffle-1）**: [shuzilm-libdu](./anti-detection/shuzilm-libdu-fingerprint.md)
- **Frida spawn / survival hook**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **panda whole-DEX**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **OkHttp 明文 Hook / 流量对齐**: [app-reverse-global-map](./mobile-app-reverse/app-reverse-global-map.md), [app-protectors](./packing-bypass/app-protectors.md)
- **FART / JDex2 / FartFixer 分流**: [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **Chromium 源码编译与修改**: [chromium-fingerprint-compilation](./anti-detection/chromium-fingerprint-compilation.md)
- **滑块缺口轮廓匹配（Canny 对洞，禁止灰度对纹理）**: [products](./web-reverse/products.md)
- **JVM 类加载 / 双亲委派 / 验证-准备-解析**: [jvm-mindmap](./mobile-app-reverse/jvm-mindmap.md)
- **JVM 运行时数据区（堆/方法区/栈/PC）**: [jvm-mindmap](./mobile-app-reverse/jvm-mindmap.md)
- **PermGen → Metaspace（JDK 8）**: [jvm-mindmap](./mobile-app-reverse/jvm-mindmap.md)
- **JIT C1/C2 / volatile 与指令重排序**: [jvm-mindmap](./mobile-app-reverse/jvm-mindmap.md)
- **JNI / Native Method Stack**: [jvm-mindmap](./mobile-app-reverse/jvm-mindmap.md)
- **App 逆向三步法**: [app-reverse-global-map](./mobile-app-reverse/app-reverse-global-map.md)
- **OkHttp/Interceptor 定位**: [app-reverse-global-map](./mobile-app-reverse/app-reverse-global-map.md), [pure-protocol-sdk](./mobile-app-reverse/pure-protocol-sdk-reconstruction.md)
- **App 纯协议 SDK 重建（HAR 语料 / algorithms / 拦截器链 / 注册完备性）**: [pure-protocol-sdk](./mobile-app-reverse/pure-protocol-sdk-reconstruction.md)
- **注册包事件驱动顺序 / 扣核心 SDK 同构**: [protocol-register-order](./mobile-app-reverse/protocol-register-packet-order.md), [pure-protocol-sdk](./mobile-app-reverse/pure-protocol-sdk-reconstruction.md)
- **设备指纹一致性建模 / 联合分布 / 右偏时间间隔 / 有状态演化**: [fp-consistency](./anti-detection/device-fingerprint-consistency-modeling.md)
- **CloakBrowser humanize 轨迹纯算（三次贝塞尔计划器）**: [cloakbrowser-humanize](./anti-detection/cloakbrowser-humanize-trajectory.md)
- **App 协议准入四关 / 空壳诊断顺序 / 全量静态普查 / 同名算法先看 MAGIC**: [protocol-admission](./mobile-app-reverse/protocol-admission-four-gates.md)
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
- **unidbg RandomFileIO 钉随机 / SearchData / memcpy + traceWrite（Shopee）**: [shopee-shpssdk](./signature-algorithms/shopee-shpssdk-request-defense.md)
- **AOSP 预置 CA / APatch / WebView 调试 ROM**: [xfq-aosp-rom](./mobile-app-reverse/xfq-aosp-rom-compilation.md)
- **trace 数据库 + MCP 证据回溯**: [ai-vmp-trace](./native-analysis/ai-assisted-vmp-trace-recovery.md)
- **Chromium/Firefox/WebKit 内核定制**: [ruyi-browser](./anti-detection/ruyi-browser-anti-detection-compilation.md)
- **AST/JS 混淆/Node 补环境/Webpack RPC**: [benru-web](./web-reverse/benru-web-reverse-compilation.md), [yuanrenxue-web](./web-reverse/yuanrenxue-web-reverse-compilation.md), [koohai-notes](./web-reverse/koohai-reverse-notes-compilation.md)
- **jsdom + vm 对齐浏览器 VM 第一处分叉**: [datadome-env-patch](./web-reverse/datadome-env-patch.md)
- **h5st / a_bogus / x-s / x-s-common / X-Gnarly 签名定位**: [ai-assisted-web](./web-reverse/ai-assisted-web-reverse-compilation.md), [products](./web-reverse/products.md)
- **FART 源码改进 / WebView 调试 / IDA 识别 MD5**: [koohai-notes](./web-reverse/koohai-reverse-notes-compilation.md), [jiagu-bypass](./packing-bypass/jiagu-bypass-analysis.md)
- **JSVMP 是否拆 opcode 的分流**: [ai-assisted-web](./web-reverse/ai-assisted-web-reverse-compilation.md)
- **风控产品强制命中分类（验证码/签名/状态型链）**: [products](./web-reverse/products.md)
- **平台签名落地分流（纯算 / Node vm / execjs 整包 / Frida RPC）**: [sign-landing](./web-reverse/sign-landing-methods.md), [thin-wrapper](./web-reverse/thin-wrapper-vs-purecalc.md)
- **VMP 钩宿主原语 / 换 Cookie 盐探针**: [vmp-host-primitive](./web-reverse/vmp-host-primitive-to-purecalc.md), [douyin-secsdk](./web-reverse/douyin-secsdk-websign-case.md)
- **材料出处账本（本地 / 服务端 / runtime / 设备）**: [provenance-ledger](./web-reverse/material-provenance-ledger.md)
- **请求面切开与失败翻译**: [plane-translation](./web-reverse/request-plane-failure-translation.md), [douyin-planes](./web-reverse/douyin-web-request-planes.md)
- **纯算 vs 预言机成本账 / navigator 与布局 canary**: [oracle-cost](./web-reverse/purecalc-vs-oracle-cost.md)
- **fail-closed 完成门（localReproduced / serverAccepted）**: [completion-gate](./web-reverse/fail-closed-completion-gate.md)
- **端别常量表（aid / appKey / version_code）**: [endpoint-constants](./web-reverse/endpoint-constant-table.md)
- **会话材料双写与 origin 绑定**: [double-write](./web-reverse/session-binding-double-write.md)
- **隔离 Node 运行器进程合同**: [node-runner](./web-reverse/isolated-node-runner-contract.md)
- **抓包对齐偏差（空值 / 同名键 / 编码 / 冻结头）**: [alignment-traps](./web-reverse/capture-alignment-traps.md), [signed-wire](./web-reverse/signed-query-wire-contract.md)
- **VMP 钩宿主 MD5 再纯算规范化 query**: [douyin-secsdk](./web-reverse/douyin-secsdk-websign-case.md)
- **签完即线上 / 头序 / HTTP/2 Cookie 拆分 / 同名键列表**: [signed-wire](./web-reverse/signed-query-wire-contract.md)
- **端点签名面 fail-closed（缺字段不回填抓包）**: [tiktok-planes](./web-reverse/tiktok-web-signing-planes.md)
- **材料 provenance 六桶 / host-only Cookie**: [xiaohongshu-assembly](./web-reverse/xiaohongshu-assembly-case.md), [douyin-session](./web-reverse/douyin-session-materials-case.md)
- **cv-cat 按站装配案例**: [sign-landing](./web-reverse/sign-landing-methods.md)
- **MTOP InnerSignImpl 实例 RPC（Hook 一次即摘）**: [mtop-innersign-rpc](./mobile-app-reverse/mtop-innersign-rpc.md)
- **会话画像 + data2sign byte-exact 对拍（SG 70102 四头）**: [alibaba-mtop-four-headers](./signature-algorithms/alibaba-mtop-four-headers.md)
- **canonical query 与 Cookie provenance**: [sign-landing](./web-reverse/sign-landing-methods.md)
- **补环境对象级参考（检测面/常见坑/观察优先级）**: [env-objects](./web-reverse/browser-env-objects.md)
- **未上架 MV3 / sideload / 自定义协议本机更新器**: [unpacked-mv3-updater](./web-reverse/unpacked-mv3-native-updater.md)
- **mitmproxy/Charles/Frida/Protobuf/iOS/Flutter 工具链**: [benru-web](./web-reverse/benru-web-reverse-compilation.md)
- **伴随请求响应体数据流审计 / companion_response_audit / 参数谱系 sourceKind 溯源**: [aigei-safe-search](./web-reverse/aigei-safe-search-ticket-chain.md), [yuanrenxue-app](./mobile-app-reverse/yuanrenxue-mobile-app-reverse-compilation.md)
- **高并发采集控制面/AIMD/half-open**: [collector-control-plane](./collection-engineering/high-concurrency-http-collector-control-plane.md)
- **Mihomo dialer-proxy / curl --preproxy / 隔离 sidecar**: [mihomo-dialer-proxy](./collection-engineering/mihomo-dialer-proxy-chain.md)
- **SSD spool/NAS mirror/marker-ACK 重放**: [mac-nas-spool](./collection-engineering/reliable-mac-nas-spool-delivery.md)
- **微信公众号开源库按会话平面分流（禁止混用 Cookie）**: [wechat-mp-sessions](./protocols/wechat-mp-session-planes.md), [wechat-mp-oss](./mobile-app-reverse/wechat-mp-oss-landscape.md)
- **内置浏览器 MITM/vConsole 收证（不触发微信）**: [wechat-mp-oss](./mobile-app-reverse/wechat-mp-oss-landscape.md)
- **WMPF 4.x H5 调试 / WeixinJSBridge Mock ≠ A8Key 签发**: [wechat-mp-oss](./mobile-app-reverse/wechat-mp-oss-landscape.md)
- **Nuitka onefile RCDATA payload / 第二层 native constants**: [nuitka-onefile](./native-analysis/nuitka-onefile-payload-recovery.md)
- **SQLite 短事务 claim / durable retry / 凭证不进队列**: [weixin-archive-runtime](./collection-engineering/weixin-http-archive-runtime.md)
- **Headless MCP stdio/Streamable HTTP 与 job 假成功**: [weixin-archive-runtime](./collection-engineering/weixin-http-archive-runtime.md)
- **Widevine L3 视频下载 / CDM 自提取 / license 重放 / mp4decrypt**: [widevine-l3-video-download](./drm-content-acquisition/widevine-l3-video-download.md)

---

## 维护规则

1. 新增文章时，在对应分类表添加一行
2. 同步更新「按技术标签检索」中的标签映射
3. 新增分类时，在 `article/` 下创建子目录 + 更新本索引
4. 来源项目列始终指向原始 workspace 项目名
5. 正文或索引变更后运行 `scripts/kb_catalog.py generate`，不要手工编辑 `CATALOG.md` / `catalog.json`
6. 提交前运行 `scripts/kb_catalog.py check` 和 `python -m unittest discover -s tests -v`
