# 方法论：纯算还是预言机，先写成本账

> 来源: `workspace/cv-cat`（KuaiShou-Spider `weapon_oracle.py`、JdApis h5st 三段式、TiktokApis frontier/Shop、DouYin_Spider acrawler）
> 原始发布时间: 2026-09-23
> 归档日期: 2026-09-24
> 分类: web-reverse
>
> 能在请求边界读到明文和标准原语，就纯算。字节码大、变体多、或出参只在 cookie 边界闭合，就用隔离程序当预言机，并在账本上写明为什么不移植。预言机出参的 provenance 是 runtime，不能标 purecalc。

宿主原语路径见 [VMP 钩原语](./vmp-host-primitive-to-purecalc.md)。

## 成本账怎么填

对每个参数问四件事：输入是否已在请求边界闭合、原语是不是标准库、移植量、失败时能不能安全降级。

| 参数 | 对照仓的选择 | 原因 |
|------|----------------|------|
| 抖音 `x-secsdk-web-signature` | 纯算规范化 + 标准 MD5 | MD5 入口已经给出明文 |
| 抖音 `a_bogus` | 纯算模块 `ab_pure` | 查询边界闭合。字母表仍会过期，不入库 |
| 快手 `__NS_sig3` / `__NS_hxfalcon` | 纯算 | 输入是 query+body 的 JS 值语义，引擎是压缩 AST，不是大段字节码 |
| 快手 `kwfv1` / `kwscode` | Node 跑官方脚本 | kwf 约 53KB 字节码，kws 约 48KB 乘多个变体。`/s/w/c` 换到当次 `fpUrl`/`signUrl` 再跑 |
| 京东 h5st | 常驻 Node 跑未改的 `js_security_v3_0.1.6.js` | 库 232KB，冷启动 1 到 2 秒，签名本身是毫秒级。没有把 algo 拆成 Python |
| 抖音 `__ac_signature` | Node 页面 VM | 出参在 Cookie 边界。strict 失败不造签名 |
| TikTok HTTP `X-Gnarly` | Python 纯算 | 两代编码器分开，缺字段失败 |
| TikTok frontierSign / Shop BSID | 各自的 Node runner | 官方 SDK 不改；长度合同分别是 16 和 382 |
| 闲鱼 `tfstk`、小红书 `websectiga` | Node vm | 服务端程序或页面脚本，零宿主纯算不成立 |
| 知乎 `x-zse-96`、头条 `a_bogus` | execjs 整包 | 只证明参数名和调用边界，不算纯算完成 |

预言机的最短路径是「和浏览器同源同算法」，不是「看起来像」。快手注释写明：本地脚本算出来的 `kwfv1` 不是服务端下发的字符串，但纯 Python 移植字节码成本极高，所以跑官方脚本。

## 预言机也有验收

隔离执行不是把脚本丢进空 Node。快手 `weapon_oracle.py` 修过两个 canary：

1. `navigator.platform` / `userAgent` / `appCodeName` 在真实浏览器上是 getter-only。脚本写入标记串再读回。普通对象字面量会被真写进去，VM 就走异常分支，`kwscode` 里出现非 hex。
2. `div` 设 `height:20px` 挂到 `body` 后，`offsetHeight` 应为 20。未挂载是 0。

`did` 必须和 Cookie 一致，因为 `kwfv1` 明文里带它。过期的 `signUrl` 不能拿历史 `kws-N-*.js` 去签。

京东侧的验收是 h5st 第 4 段以 `tk03` 开头。`tk04` / `tk06` 是库的本地兜底。warmup 重签直到 tk03，而不是把第一次出参当完成。

## 伪代码

```text
decide(param):
    if host_primitive_plaintext_closed(param):
        return purecalc(canonical_rules_only)
    if decompile_size_small and fixtures_match:
        return purecalc
    return oracle(official_script, canaries, fresh_urls)

run_oracle(script, inputs):
    require canaries_pass                 # navigator writable, layout
    require inputs.sign_url is this round
    out = node(script, inputs, timeout)
    require shape(out)                    # length, prefix, hex
    tag provenance = runtime
    if fail:
        raise                             # no random fallback

label:
    purecalc 只覆盖已闭合边界
    oracle 出参永远不是 purecalc
```

## 账本里要写的一句

每个参数一行：`落地 = purecalc | oracle | execjs_bundle | rpc`，加上「为什么不移植」和「完成门」。快手把 53KB 字节码留在 Node，就是这句。写成 purecalc 会让下一轮把 oracle 失败当成算法回归。
