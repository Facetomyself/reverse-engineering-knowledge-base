---
schema_version: 2
id: yuanrenxue-firefox-nss-clienthello-reference
document_type: reference
original_date: '2026-07-13'
archived_date: '2026-07-16'
scope:
  targets: [firefox-nss-clienthello]
  client: web
  version: requests 2.34.2; firefox capture 152.0.5; chrome 150.0.7871.115; cited source firefox 151.0.4
  observed_at: '2026-07-09'
sources:
  - id: s1
    ref: "./yuanrenxue-anti-20260713-01.md#背景科普"
    basis: source-report
  - id: s2
    ref: "./yuanrenxue-anti-20260713-01.md#38-指纹"
    basis: source-report
  - id: s3
    ref: "./yuanrenxue-anti-20260713-01.md#53-指纹"
    basis: source-report
  - id: s4
    ref: "./yuanrenxue-anti-20260713-01.md#56-总结"
    basis: source-report
  - id: s5
    ref: "./yuanrenxue-anti-20260713-01.md#0-版本信息"
    basis: source-report
  - id: s6
    ref: "./yuanrenxue-anti-20260713-01.md#51-下载firefox源码"
    basis: source-report
  - id: s7
    ref: "./yuanrenxue-anti-20260713-01.md#1-wireshark抓包"
    basis: source-report
  - id: s8
    ref: "./yuanrenxue-anti-20260713-01.md#指纹检测的流程"
    basis: source-report
modules:
  - name: risk-control
    anchor: risk-control
    sources: [s1, s8]
    basis: source-report
    limits: 只保留作者对 ClientHello 明文和改头无效的陈述。流程图点了 HTTP/2 指纹，正文没有 SETTINGS 或伪头序测量。未复现，也不覆盖 Akamai 产品卡的请求链路。
  - name: parameters
    anchor: parameters
    sources: [s2, s3, s6]
    basis: source-report
    limits: 只读归档里的对照表和符号表。不转写 JA3/JA4 原值、随机数、会话号、key share 或 ECH 载荷，也不抄整份套件序。行号未对照 151.0.4 源码包。抓包表与 5.5 发送表对 GREASE 的说法不一致。
  - name: validation
    anchor: validation
    sources: [s4, s5, s7]
    basis: source-report
    limits: 作者写稳定通过只是自述。印出的请求打到 example.com。版本表是 152.0.5，源码包写成 151.0.4。文末提示词未收录，也不构成验收。
relations:
  - type: derived_from
    target: "./yuanrenxue-anti-20260713-01.md#53-指纹"
  - type: derived_from
    target: "./yuanrenxue-anti-20260713-01.md#38-指纹"
tags: [tls, ja3, ja4, nss, firefox]
---

# Firefox NSS ClientHello 与 requests 出厂握手的字段边界

这张卡只回答：归档把 requests、Firefox、Chrome 的 ClientHello 差在哪些已命名字段上，Firefox 侧符号写在哪些 NSS 文件，以及哪些句子不能当成已验收。目标用 `firefox-nss-clienthello`，因为 `../../web-reverse/products/akamai.md` 的目标是 `akamai`，模块只有 request-chain 和 validation，只说明 TLS 层可以先于 JS 被拦截，没有这组版本钉、字段差和 NSS 符号。

不收录抓包中的指纹原值、随机数、会话号、密钥交换和 ECH 载荷，也不收录文末那条要求改到可生产的提示词。前提、可执行步骤、输出物、验收和失败出口不齐，所以不是流程。

<a id="risk-control"></a>
## 检测边界

作者写调试 Akamai 站点时，Requests 默认发包会被拦住，单纯修改请求头完全无法规避。背景段把 ClientHello 说成加密建立前的明文，并写 requests 底层是 OpenSSL，发生在 TLS 握手阶段，比 HTTP 请求还早，改 User-Agent 也没用。

同篇流程图还写了计算 HTTP/2 指纹和 Akamai SETTINGS 加伪头序，后面的抓包分析没有测量这两项。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 单纯修改请求头完全无法规避 | s1，开篇重复句 | source-report | 作者所说的 Akamai 站点与 Requests 默认发包 | 没有站点、脚本或拦截样本 |
| C2 | ClientHello 是明文，且比 HTTP 请求还早 | s1，背景科普第 1 与第 4 点 | source-report | 作者对握手顺序的说明 | 未复现握手 |
| C3 | 流程图点名计算 HTTP/2 指纹和 SETTINGS + 伪头序，后文没有对应测量 | s8，指纹检测的流程 | source-report | 该段流程图文字 | 不能当成 HTTP/2 模块 |

<a id="parameters"></a>
## 字段差与 NSS 符号

3.8 节写明：JA3 保留扩展的原始顺序，JA4 会先把扩展排序再计算。同段写 Chrome 每次请求都会重排扩展顺序，所以 JA3 每次都变，JA4 才稳定。3.3 的注写 Firefox 两次抓包扩展顺序一致，并指向 NSS 的 `enableChXtnPermutation`，说未来或打开该 pref 后顺序可能变。

对照表里作者标出的命名差，而不是整份套件序：requests 的 ALPN 是 `http/1.1`，Firefox 与 Chrome 是 `h2, http/1.1`；`encrypted_client_hello` 一列 requests 为空、浏览器为有；`application_settings` 标成 Chrome 特有；签名算法写 requests 26 个、浏览器精简 11 个；x448 群只列在 requests；requests 独有扩展写了 `encrypt_then_mac` 和 `post_handshake_auth`。3.6 的 GREASE 行是 requests 与 Firefox 为破折号、Chrome 为包含。5.5 的发送表却以 `tls13_grease` 开头。两表不能拼成一份发送序。

调用链原文是 requests → urllib3 → Python 标准库 ssl → OpenSSL，并写 urllib3 默认没有启用 encrypted_client_hello、ALPN(h2)、application_settings。`curl_cffi` 只被点名，没有版本。

5.3 符号表读到的定位：

| 要素 | 归档中的文件与符号 |
|---|---|
| ClientHello 主构造 | `security/nss/lib/ssl/ssl3con.c:5505`，`ssl3_SendClientHello()` |
| 套件序 | `security/nss/lib/ssl/sslenum.c:57`，`SSL_ImplementedCiphers[]` |
| 扩展发送表 | `security/nss/lib/ssl/ssl3ext.c:128`，`clientHelloSendersTLS[]` |
| 扩展乱序 | `ssl3ext.c:793` / `:1159`，`enableChXtnPermutation` / `tls_ClientHelloExtensionPermutationSetup()` |
| key_share | `security/manager/ssl/nsNSSIOLayer.cpp:1600`，符号格为空 |

5.4 只采用一句范围说明：`SSL_ImplementedCiphers[]` 全集的发送即此序，且 TLS 1.3 三个恒在最前。不抄后续老套件。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C4 | JA3 保留扩展的原始顺序，JA4 会先把扩展排序再计算 | s2，3.8 节区别句 | source-report | 该句对两种算法的定义 | 不记录指纹原值 |
| C5 | ALPN 行写 requests 为 http/1.1，两侧浏览器为 h2, http/1.1 | s2，3.6 表 | source-report | 版本表所钉的三次抓包 | 不是通用浏览器模板 |
| C6 | GREASE 行写 Firefox 为破折号，5.5 首项却是 tls13_grease | s2 与 s3 | source-report | 这两张归档表 | 未判定哪张是发送结果 |
| C7 | ssl3con.c:5505 的符号是 ssl3_SendClientHello() | s3，5.3 表 | source-report | 归档写下的路径和行号 | 未对照源码包 |
| C8 | nsNSSIOLayer.cpp:1600 这一行没有符号 | s3，key_share 行 | source-report | 该表单元格 | 不能补写函数名 |
| C9 | 下载段写 firefox151的版本，不是版本表里的 152.0.5 | s6，下载 firefox 源码 | source-report | 下载段原文 | 152.0.5 在版本表，见 C12，不能合成一个 NSS 版本 |

<a id="validation"></a>
## 验证与限制

版本表写 requests 2.34.2、firefox 152.0.5、chrome 150.0.7871.115、wireshark v4.6.7。抓包脚本是 `requests.get("https://example.com/")`。作者最后写用 Rust 与 PyO3 封装后，目前成功绕过 akamai 的校验，稳定过。归档没有通过条件、失败出口或对应抓包。文末提示词不进入本卡。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C10 | 抓包示例请求的是 https://example.com/ | s7，wireshark 一节 | source-report | 文中这个脚本 | 不能改写成某个 Akamai 主机 |
| C11 | 目前成功绕过akamai的校验，稳定过 | s4，5.6 总结 | source-report | 作者自述 | 没有样本，本轮未运行 |
| C12 | 版本钉是 requests 2.34.2 与 firefox 152.0.5 | s5，版本信息 | source-report | 该表 | 与 151.0.4 源码包冲突，见 C9 |
