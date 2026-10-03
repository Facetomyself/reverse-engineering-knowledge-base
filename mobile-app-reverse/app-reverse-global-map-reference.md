---
schema_version: 2
id: android-app-request-lifecycle-reference
document_type: reference
original_date: '2026-07-05'
archived_date: '2026-10-02'
scope:
  targets:
    - Android app request lifecycle
  client: Android
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./app-reverse-global-map.md#一条-app-请求的完整生命周期"
    basis: source-report
  - id: s2
    ref: "./app-reverse-global-map.md#常见防御手段"
    basis: source-report
  - id: s3
    ref: "./app-reverse-global-map.md#逆向地图速查"
    basis: source-report
modules:
  - name: decision-flow
    anchor: decision-flow
    sources: [s1, s3]
    basis: source-report
    limits: 七层只是来源的坐标，不是包名、版本或调用栈证据。OkHttp 的搜索清单以第 3 章静态定位卡为准，本卡不另做接口模块。
  - name: risk-control
    anchor: risk-control
    sources: [s2, s3]
    basis: source-report
    limits: 只保留六种防御各自在检查什么。来源附带的绕过名字没有前提、输出和验收，本卡不写成步骤。
relations:
  - type: derived_from
    target: "./app-reverse-global-map.md#一条-app-请求的完整生命周期"
tags:
  - android-request-lifecycle
  - okhttp
  - jni
  - source-report
---

# App 请求从点击到发出的层级坐标

这张卡只回答：来源把一次 App 请求分成哪几层，每一层它让你先看哪里，以及它认为常见防御在检查什么。不教工具安装，也不把“模拟请求能通”写成验收。

来源没有可公开定位的原文 URL。收录说明写明本文是 PDF 和公众号正文去重后的保留本。

<a id="decision-flow"></a>
## 七层坐标

来源把点击到发出写成一条链，并写每一层都可能是突破口，也可能是防御所在：

| 阶段 | 来源说这一层做什么 | 来源给的切入 | 来源在速查表里写的防御 |
|---|---|---|---|
| UI | Activity 接收点击，调用业务 | 搜 `setOnClickListener` 找回调；这层通常没有加密 | 无 |
| 业务 | Presenter 组装参数 | 看口令是输入框明文，还是已经做过一次摘要 | 前端加密 |
| 网络 | OkHttp / Retrofit 构建 Request | 来源点名 `OkHttpClient.newCall()` | 无 |
| 加密 | Interceptor 改 Request | 搜 `intercept` 或 `addInterceptor` | 混淆代码 |
| JNI | `System.loadLibrary` 后调 native | 搜 `loadLibrary` 和 `native` 声明 | 动态注册 |
| SO | C/C++ 算法 | IDA 或 Ghidra 看导出；或在加载时看 `dlopen` | 加壳、OLLVM |
| 发出 | Socket，HTTPS 再经 TLS | 来源把网卡抓包写成少见且不是首选 | SSL Pinning |

速查表把“网络层”写了两次：一次是 OkHttp，一次是 Socket / TLS。第二行的防御才是证书锁定。

新 App 的进入顺序被写成三句：先看请求有没有签名参数；再用 jadx 搜 `sign`、`encrypt`、`loadLibrary`；然后确定加密在哪一层。这三句没有输出定义、通过条件和失败出口，所以不是流程。关键词回溯和 OkHttp 入口的细节在第 3 章静态定位卡，不在这里展开。

定位之后，来源把核心任务收成三步：加密在 Java Interceptor、在 SO，还是两层都有；算法是摘要加盐、AES-CBC，还是魔改 HMAC；再用 Python 或 Go 构造同样的头和体。它把“服务器正常返回数据”写成这一步的成功。文末另写：协议客户端不要停在模拟请求能通，HTTP 200 空壳、错机房、未激活设备要先走协议准入四关，过关后再按纯协议 SDK 重建，不要先写采集器。后一句收紧了前一句，本卡采用后一句作为边界。

<a id="risk-control"></a>
## 六种防御在检查什么

来源写逆向一个 App 时大概率会遇到其中两三种，没有样本数。

| 防御 | 来源写它在检查什么 |
|---|---|
| SSL Pinning | App 只信任特定服务器证书；代理上表现为证书错误或连接失败 |
| 参数签名 | 每个请求带 `sign`，由参数、盐和时间戳算出；服务器重算不一致就拒绝 |
| 时间戳 | 请求里的时间要落在窗口内，例子是前后 5 分钟 |
| 设备指纹 | 服务器记下 IMEI、MAC、Android ID；同一设备频繁请求可能被封 |
| SO 加壳 | 文件加密或压缩，运行时才解密；直接用 IDA 打开是无效内容 |
| VMP | 核心算法变成自定义字节码，由内置解释器执行 |

签名一节只多写了盐可能在 SO 里或每次不同。时间窗口的“5 分钟”是例子，不是测得的阈值。设备标识是字段名，不是值。

## 验证与限制

- 没有具体 App、版本或一条真实调用栈。
- 防御各节里的绕过名字是一句话，没有前提、输出、验收和失败出口。本卡不收录这些步骤。
- 协议准入的诊断步骤属于 `app-protocol-admission`，不是本目标的 decision-flow。设备画像一致性卡也是另一个目标。
- 环境搭建文里的证书安装不在本篇，本卡不补进那篇。
