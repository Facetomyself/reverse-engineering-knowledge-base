---
schema_version: 2
id: mcc-sign-url-ios-reference
document_type: reference
original_date: '2020-06-02'
archived_date: '2026-10-02'
scope:
  targets:
    - MCCSignURLManager
  client: iOS
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: "./yuanrenxue-app-20200602-01.md#app爬虫-某app-ios版逆向过程"
    basis: source-report
modules:
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 只保留 _r 与 sign 的组成关系。key 和盐的原值不收录，因此本卡不能直接算出 sign。
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 函数链和 0xc4ed40 来自来源那次砸壳后的 IDA 映像，不保证换包后的偏移仍相同。
relations:
  - type: derived_from
    target: "./yuanrenxue-app-20200602-01.md#app爬虫-某app-ios版逆向过程"
tags:
  - ios-sign
  - md5
  - source-report
---

# 某汽车 iOS：sign 与 _r 的函数链

这张卡只回答：来源把 sign 和 `_r` 追到了哪些方法，以及两条参数如何组成。产品名在正文里只有「某汽车」。key 和盐的原值不进入本卡。

<a id="parameters"></a>
## _r 和 sign 的组成

抓包时 `_r` 为 32 位，sign 为 34 位，sign 末两位不变。来源当时猜测 sign 是 32 位 MD5 再加字符串 `01`。修改参数后重放，返回的是 url 签名错误。

`_r` 后来被写成随机 UUID 再做 MD5。

sign 收在 `SignUrl0`。入参 1 是不含 sign 的请求内容。入参 2 是 key 经过 base64decode 等步骤得到的固定字符串，来源称它是 MD5 的盐。收口句是：入参 1 与入参 2 做 MD5，再与 `01` 拼接。来源称两张图与抓包一致。图不是可抄写的输入输出。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | _r 为 32 位，sign 为 34 位且末两位不变 | s1 第 55 行「32位数的“_r”参数(可能为MD5加密)以及34位数的sign参数」 | source-report | 来源的两次抓包 | 此时还是猜测 |
| C2 | _r 是随机 UUID 的 MD5 | s1 第 108 行「“_r”参数是随机生成的UUID经过MD5加密得到」 | source-report | useBasicParam 那个方法 | 没有 UUID 的版本说明 |
| C3 | sign 为 MD5(入参1+入参2) 再拼 01 | s1 第 151 行「SignUrl0的入参1+入参2经MD5加密后与“01”拼接得到」 | source-report | SignUrl0 | 盐的原值不收录 |
| C4 | 入参 2 是 key 转换后的固定字符串 | s1 第 143 行「参数2为key值经过base64decode等步骤转换而来的固定字符串」 | source-report | 来源的断点 | 转换步骤没有展开 |

<a id="request-chain"></a>
## 从 ttDna 到 SignUrl0

砸壳工具是 frida-iOS-dump，反编译是 IDA64 7.0，Hook 是 objection 1.9.1，断点是 LLDB 加 debugserver。来源称 `sign` 干扰太多，改搜 `ttDna`，只有一条命中，进入 `-[CBDBaseApi extraParams]`。objection 的返回值含抓包字段但不完整。

第一条堆栈地址 `0xc4ed40` 加上来源写的 IDA 头部偏移 `0x100000000`，得到 `0x100c4ed40`，落在 `-[MCCBaseApi buildFullUrl:]`。来源称这里的返回值与抓包 URL 一致，完整 URL 由该函数拼出，再调用 `+[MCCURLManager buildUrlString:withParams:sign:]`。这个实现来自 `-[MCCURLManager buildUrlString:withParams:sign:useBasicParam:usePublicParam:]`，`_r` 在此出现。

sign 继续到 `+[MCCSignURLManager signUrl1:withKey:]`。来源称 objection 看到的差别只是多了 sign，因此 sign 在此生成，同时也看到了 key。伪代码中 `SignUrl1` 调用 `SignUrl0`，`SignUrl0` 被认成 MD5。断点打在 `SignUrl0` 的入参上。

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 入口字符串是 ttDna，函数是 CBDBaseApi extraParams | s1 第 64 行「关键字“ttDna”」；第 71 行「-[CBDBaseApi extraParams]」 | source-report | 该次砸壳二进制 | 字符串窗口只在图里 |
| C6 | 堆栈 0xc4ed40 落到 MCCBaseApi buildFullUrl: | s1 第 78 行「0xc4ed40 + IDA64头部偏移量 0x100000000 = 0x100c4ed40」 | source-report | 来源的 IDA 映像 | 不是跨版本偏移 |
| C7 | URL 拼装进入 MCCURLManager，再进入带 useBasicParam 的方法 | s1 第 90 行「+[MCCURLManager buildUrlString:withParams:sign:]」 | source-report | 该伪代码 | 参数字典没有逐项列出 |
| C8 | sign 生成点被写成 MCCSignURLManager signUrl1:withKey: | s1 第 112 行「+[MCCSignURLManager signUrl1:withKey:]」 | source-report | 该 Hook | key 原值不收录 |

## 验证与限制

key、盐和完整查询串都不在本卡。来源没有写出签名不一致时的停止条件，不建流程。本次没有运行 objection、IDA 或 LLDB。
