---
schema_version: 2
id: ruyi-20260526-mihuashi-ms-locator-reference
document_type: reference
original_date: '2026-05-26'
archived_date: '2026-10-02'
scope:
  targets: [mihuashi]
  client: web
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./ruyi-20260526-01.md#31-搜索-setrequestheader
    basis: source-report
  - id: s2
    ref: ./ruyi-20260526-01.md#42-确认-wasm-模块
    basis: source-report
  - id: s3
    ref: ./ruyi-20260526-01.md#43-确认时间戳的生成
    basis: source-report
  - id: s4
    ref: ./ruyi-20260526-01.md#44-确认-wasm-使用了-cryptogetrandomvalues
    basis: source-report
  - id: s5
    ref: ./ruyi-20260526-01.md#51-wasm-读取-favicon-url
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s1, s2]
    basis: source-report
    limits: 只保留设头文件、sign 函数和 wasm 模块名。不抄签名样值，也不补文末没写的算法。
  - name: parameters
    anchor: parameters
    sources: [s3, s4, s5]
    basis: source-report
    limits: 只保留秒级时间戳、随机成分和 favicon 选择器这三类来源句。随机字节和 href 不录入。
relations:
  - type: derived_from
    target: ./ruyi-20260526-01.md#42-确认-wasm-模块
tags: [mihuashi, m-s, wasm, source-report]
---

# 米画师 M-S 的定位边界

这张卡只回答：该文把请求头 M-S 定到哪一个 JS 函数和哪一个 wasm 文件，M-T 怎么从时间来，以及它把哪两项环境依赖写成签名会变或会失败。不提供签名生成步骤。

`kb_catalog.py query --target mihuashi --module parameters` 与 `--module request-chain` 都是 0。已有 WASM 卡的目标是 unknown，讲的是解密加载或版本对照，不覆盖这个站点的 sign 栈。

<a id="request-chain"></a>
## 头从哪里来

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 设头栈被写成：调用栈来自  isObject.BpF7pdk3.js  （axios 封装层） | s1，源文件第 85 行 | source-report | preview 接口上的 M-S / M-T | 日志行号没有本地 ndjson |
| C2 | 两头一起出现：确认 M-S 和 M-T 是在同一个拦截器中一起设置的 | s1，源文件第 101 行 | source-report | 同一 headers 对象 | 不是算法 |
| C3 | 首次出现被写成：M-S 的值是从  http.BzJ4_4Bj.js  的  sign  函数中产生的，而这个函数内部调用了 WASM 模块。 | s2，源文件第 124 行 | source-report | sign 的 TextDecoder.decode | 不抄 decode 字节 |
| C4 | 模块被写成：签名算法封装在 Rust 编译的 WebAssembly 模块  mhs_fe_sign_bg.DLpTGLRB.wasm  中。 | s2，源文件第 144 行 | source-report | 该 wasm 文件名 | 没有导出表 |

<a id="parameters"></a>
## 时间、随机和页面材料

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C5 | 时间头公式：M-T = Math.floor(Date.now() / 1000)  ，即秒级时间戳。 | s3，源文件第 156 行 | source-report | M-T | 不说明 M-S 的输入 |
| C6 | 来源否定纯确定性：说明签名中包含随机成分，每次签名结果不同，不是纯确定性的 HMAC。 | s4，源文件第 176 行 | source-report | getRandomValues 出现在 sign 栈上 | 没写随机字节如何拼进签名 |
| C7 | 页面材料：URL）作为签名密钥的一部分。如果在非浏览器环境中运行，没有正确的 DOM 结构，签名就会失败。 | s5，源文件第 198 行 | source-report | 选择器 link[rel*='icon'] 的 href | 具体 URL 不录入 |

## 验证与限制

第 43 行把最终目标写成用 Node.js 补环境还原签名算法。第 203 行写后续内容放在知识星球。因此没有算法、没有补环境步骤，也没有验收。31220 是作者用 trace_init 和域名挑出的主渲染进程，本轮没有日志文件。签名样值不进入本卡。
