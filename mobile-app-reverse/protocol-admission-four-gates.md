# App 协议准入四关：设备、签名、主机、传输

> 来源: 方法论整理（`workspace/tiktok-four-gate-source-study` 对照）
> 原始发布时间: 2026-09-06
> 归档日期: 2026-09-06
> 分类: 移动 App 逆向 — 协议准入四关
>
> 带设备注册、请求签名和自研网络栈的 App，业务 readback 之前必须同时闭合四关：同行一致的设备画像、拦截器式签名栈、主机/引导路由、传输指纹。HTTP 200 空壳不是 `serverAccepted`；注册签发标识不等于激活完成。TikTok 三源只作推导语料，不收录密钥或可执行签名器。

## 定位

三篇方法文档分工，不要互相替代：

| 文档 | 回答的问题 | 停在哪 |
|------|------------|--------|
| [App 逆向全局地图](./app-reverse-global-map.md) | 一次请求经过哪些层 | 知道从哪一层下手 |
| **本文（准入四关）** | 为什么「参数像了」仍没有业务数据 | 四关并联闭合，才能看 readback |
| [纯协议 SDK 重建](./pure-protocol-sdk-reconstruction.md) | 客户端目录、HAR、拦截器、注册完备性怎么建 | 可维护的协议客户端 |

后续新 case 默认顺序：

```text
全局地图定位层
        ↓
四关排除（本文）—— 空壳先归因，再改算法
        ↓
纯协议重建 —— algorithms / interceptors / apis
        ↓
采集控制面 —— 身份、连接、节奏（不是完成标准）
```

适用：Android / iOS 协议客户端、设备注册 SDK、native 签名头、自研 HTTP 栈（OkHttp 包装、Cronet、TTNet、mmtls 同类）。不适用：纯 Web JS 参数落地（走 [sign-landing-methods](../web-reverse/sign-landing-methods.md)）、单函数魔改哈希、只做加固脱壳。

Web 面和 App 面即使同厂同名，也默认不是同一套拦截器。

## 完成门（先于四关）

| 门槛 | 含义 | 不够格 |
|------|------|--------|
| `localReproduced` | 本地参数与 HAR 字节级对齐 | 公开脚本不报错、字段「看起来像」 |
| `serverAccepted` | 独立 TLS 会话拿到**非空**业务 readback | HTTP 200、空 JSON、空列表、挑战页 |
| `registrationComplete` | 干净设备走完注册 **和** 引导/激活 | 只拿到 did / iid / token 字符串 |
| `sessionConsistent` | 后续业务包的四关状态来自同一套 SDK | 换出口复用旧身份，或签名对了打错机房 |

空成功是第一诊断对象：状态码成功、body 合法、业务字段为空。它不是「再改一版签名」的信号，而是四关里至少一关没过。营销产能、公开 GitHub `sign()`、商业签名 RPC 都不能写成 `serverAccepted`。

## 四关（并联，不是流水线）

四关必须同时成立。错一关时，另外三关的工作会表现为通了但没货。

```text
关 1  设备画像 internally consistent
关 2  签名/完整性拦截器链（营销「一层/三层」通常小于真实表面）
关 3  主机与引导路由（业务 / 注册 / 指纹服务 / boot / 区域）
关 4  传输指纹（TLS/ALPN/HTTP2，不是 User-Agent）
        +
SDK 状态机（register → 引导/激活 → 配置 → 业务）
        =
才有资格看业务 readback
```

### 关 1 — 设备：同行，不编造

目标是 **catalog 行一致**，不是热门机型字符串。

| 要一致的簇 | 做法 | 禁止 |
|------------|------|------|
| Build / SoC / GPU / 内存 / 核数 / 分辨率 / Android 版本 | `hardware-fp` 锁同一行 | hybrid 拼装 |
| 运营商 / MCC-MNC / 蜂窝能力 | 与 SIM 实验对照；空值也是合法形态 | 随手填一个运营商名 |
| 传感器 / 电池 / 屏幕等 native 可读项 | 多 HAR 聚类：谁随硬件变、谁随安装变 | 把分析机上的 Frida/VPN 伪影写进生成器 |
| 持久标识 | 只使用目标自己签发或设备本地生成的值 | 编造 IMEI、serial、Android ID、MAC、Widevine `deviceUniqueId` |

指纹能加密，不等于知道该长什么样。注册失败或低权限接口异常，优先怀疑这一关，而不是签名。

### 关 2 — 签名：拦截器链，不是「N 层加密」

先画绑定对象，再还原算法。

| 常见切面 | 绑定 | 目录 |
|----------|------|------|
| 时钟头 | 秒级或毫秒时间戳 | 不单独成算法文件 |
| 设备/应用证明 | did、aid、sdk 版本、license | `interceptors/device_header.py` |
| 请求完整性 | canonical query、body 摘要、cookie | `algorithms/integrity.py` |
| 主签名 | 证明 + 完整性的密文 | `algorithms/sign.py` |
| 第二层 / 动态版本 | dyn seed、版本枚举 | `algorithms/sign3.py` 或独立文件 |
| body 封装 | gzip / MAGIC / 对称加密 | `algorithms/body_codec.py` |

规则：

1. 营销「一层 HMAC」或「三层加密」都小于真实表面。商业包装器多出来的 encrypt/decrypt/v1/v2 只当接口清单。
2. 一个头一个文件，禁止塞进 `utils.py`。
3. 公开实现与文献切片冲突时，**两边都不冻结**，用 HAR 对拍。
4. 去头实验才能证明同步强制面；「四个头都生成了」不等于四个都是门。
5. 同名算法先看包头 MAGIC / 版本字节，再选解码器。
6. 商业签名 RPC（带 API key 的远程 `gensign`）不是 `localReproduced`。
7. 密钥、XOR 表、S-box 不进知识库；版本会变，切面相对稳。

### 关 3 — 主机：按层配置，不抄域名表

对协议客户端有用的是分层，不是把静态扫到的几百个 host 写进配置。

| 层 | 问什么 | 典型失败 |
|----|--------|----------|
| 业务 API | 这个 path 落在哪组区域/分片 | 签名对了打错机房，空列表 |
| 注册 / 激活 | 签发 did 的主机 ≠ 后续业务主机 | 只打业务域名 |
| 指纹 / 风控服务 | 是否与鉴权融合 | 挡住这一层后业务签名全部失败 |
| 引导 / boot | 活配置下发前打哪几个 | 有 did 仍被当成未激活设备 |
| 遥测 | 能否与业务分离 | 把 Applog 失败当成业务失败 |
| 区域 enclave | 监管驻留 vs 全球控制面 | 用错后缀仍 200 空壳 |

静态地图纪律：

- 明文 URL、native `strings`、XOR/混淆配置要分源合并，并写清「网络栈认识」≠「运行时拨打」。
- 预发、测试、姐妹 App 域名留在能力宇宙，不进业务主机表。
- 动态 feature 和服务器下发的 TNC 不在 base APK 里，静态穷尽是假命题。

### 关 4 — 传输：握手，不是 UA

Python 默认 `requests` / 系统 OpenSSL，和 App 里的 OkHttp、Cronet、自研栈不是同一条 ClientHello。是否被校验只能用证据回答。

取证最小集：JA3 / JA4、ALPN、HTTP/2 设置帧、头部顺序。分析阶段不要让设备看见 VPN 或系统 HTTP 代理，否则生成器会把风控环境固化进去。

传输过了只说明握手像；不说明应用层注册完成。

## SDK 状态机（四关之外的第五项）

`device_id` / install token 是状态，不是「已激活」。缺引导步时，空壳优先怀疑状态机，而不是再改签名。

```text
冷启动
  -> 引导/boot（常在独立主机族）
  -> device_register / 同类签发
  -> 激活或空请求 warm-up
  -> 配置/实验拉取
  -> 低权限业务读
```

没有 HAR 不要猜具体 path。账本只强制：`registrationComplete` 必须包含引导步。只重放注册主包，一定会漏 ACK、漏延迟日志、漏 boot。

## 空壳诊断顺序

固定这个顺序，避免把四关失败都写成「签名坏了」：

```text
1. 完成门：body 是否真有业务字段？
2. 关 1：画像是否 hybrid / 被代理污染？
3. 状态机：注册之后有没有引导/激活？
4. 关 3：主机层、区域、boot 是否打对？
5. 关 4：TLS 是否像目标引擎？
6. 关 2：完整性切片、强制面、MAGIC 族是否对拍？
7. 产品保护梯度：公开对象接口 ≠ 个性化推荐；后者空壳不要回写签名
```

| 现象 | 先查 |
|------|------|
| 200 空列表 / 空 JSON | 完成门，再按上面 2–6 |
| 有 did 仍空 | 状态机 / boot |
| 签名头齐仍空 | 主机分片、enclave、TLS |
| 换机型后失败 | 关 1 hybrid |
| 挡住指纹域名后业务全死 | 指纹与鉴权融合，不能减这一层 |
| Web 接口套了 App 头 | 产品面切错 |
| 二进制 body 解不开 | 先匹配 MAGIC / 版本字节 |

## 静态全量普查（可复用，不是抽样）

对「主机有哪些、签名在哪层、native 黑盒有多大」：

1. **能力 ≠ 行为。** 代码路径存在不是这次请求发出去了。
2. **全量，不要抽样。** dex 字符串只是第一遍；Java 全树 + native `strings` + 混淆配置会差一个数量级。
3. **混淆配置按已知明文爆破。** 对 `https` / `.com` / 厂商品牌扫单字节 XOR 或短循环。
4. **引用 `file:line`，分开一、三方 SDK。** 合规监视器里的敏感 URI 不是 App 在读短信。
5. **写清盲区。** native 未反汇编、运行时解密字符串、反射、动态 feature、反编译失败方法、无抓包。
6. **镜像包先对签名证书。** 来源完整性不能替代证书真实性。

活样本进 `workspace/<项目>/` 再开 IDA / xfqtrace。反编译全集不进 Git。

## 采集控制面（准入之后）

身份、连接、节奏是另一篇文章。这里只翻译三条，避免把并发当完成标准：

| 现象 | 纪律 |
|------|------|
| 同身份连续请求 | Sticky 上允许复用连接；连接生命周期服从身份 |
| 被封 | 换 route identity（出口 + 会话），不是只换 URL |
| 核心 feed / 个性化接口更空 | 产品保护梯度；不要回写「签名又坏了」 |

详见 [high-concurrency-http-collector-control-plane](../collection-engineering/high-concurrency-http-collector-control-plane.md)。

## 本环境检查单

新样本按此打勾，缺项写进 `triage.md`，不要先写采集器。

- [ ] `hardware-fp` 锁 catalog 行（关 1）
- [ ] 干净首次开机 HAR，含冷启动到业务读的时间线（状态机）
- [ ] 签名切面拆成 algorithms/interceptors，公开实现只当假说
- [ ] 主机按层配置，静态能力宇宙与运行时拨打分开
- [ ] 传输与目标引擎对照，不用默认 Python TLS 冒充
- [ ] 二进制封装先匹配 MAGIC / 版本
- [ ] 验收看非空业务 readback
- [ ] Web 面与 App 面分仓，不混签
- [ ] 商业 RPC / 公开 keygen 不进 `localReproduced`

## 推导语料（TikTok 三源，不是模板常量）

本文从三份公开材料抽出上面的检查单。数字、域名表、头名都随版本过期；留下的是切面。

| 材料 | 抽出的方法 | 不抽出 |
|------|------------|--------|
| 销售页压缩句（空成功、四关、激活、先复用后换身份） | 完成门、并联准入、状态机、连接服从身份 | 产能百分比 |
| 公开 Mobile/Web 签名仓 | 拦截器切面、同名 ttEncrypt 不同 MAGIC、商业 RPC ≠ 本地还原、Gorgon 切片冲突要待验证 | 密钥、XOR 表、S-box、可执行签名器 |
| musically 46.0.1 静态普查 | 主机分层、XOR 配置、全量而非抽样、指纹与鉴权融合、Cronet 传输面 | 30 万 jadx 文件、隐私指控、运行时 payload |

字节对照（防混用，不是本文主算法）：

| 族 | 判别 | 去哪 |
|----|------|------|
| volces / Kimi `device_register` | MAGIC `12 39 20 20 02 03` | [kimi-device-register-ttencrypt](./kimi-device-register-ttencrypt.md) |
| 公开仓声明的另一套 TTEncrypt | MAGIC `74 63 05 10 00 00` | 先对拍再决定是否新建 case |
| 抖音 Web `a_bogus` | Web 面 | [sign-landing-methods](../web-reverse/sign-landing-methods.md) |
| App `X-Argus` 族 | Mobile 拦截器 | 本检查单关 2，活样本另开 workspace |

## 速查

| 主题 | 笔记 |
|------|------|
| 空壳 | 先完成门，再四关，最后才改算法 |
| 设备 | `hardware-fp` 同行；不编造硬件绑定 ID |
| 签名 | 切面文件化；冲突实现对拍；RPC 不是还原 |
| 主机 | 层 > 名单；boot 独立于业务 API |
| 传输 | 目标引擎的 TLS，不是 UA |
| 状态机 | did 之后还有引导 |
| 静态 | 全量 + 盲区清单 |
| 落地 | 过四关再进纯协议重建 |
