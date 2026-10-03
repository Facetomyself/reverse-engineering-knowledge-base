---
schema_version: 2
id: web-reverse-tencent-tdc-xtea-half-purecalc-reference
document_type: reference
original_date: '2026-08-13'
archived_date: '2026-10-03'
scope:
  targets: [tencent-captcha]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./tencent-tdc-slider-xtea-purecalc.md#reference-extraction-208
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅整理 collect 半纯算串联与 jsdom 现取边界；未跑 tdc.js、jsdom、OpenCV 或 cap_union。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 记录 XTEA 结构、打包、动态 key 投票与字段角色；不收录 key、pow 前缀/目标哈希、collect 明文/密文或可运行加解密。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: handler 插桩、频率取 key、24 排列试解与多尺度模板匹配是来源方法，不是已验证实现。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 半纯算与作者成果图均为自述；本轮无 runtime、parity 或 server-accepted。
relations:
  - type: derived_from
    target: ./tencent-tdc-slider-xtea-purecalc.md#reference-extraction-208
  - type: supplements
    target: ./products/tencent-captcha.md#观察优先级
tags: [TCaptcha, TDC, XTEA, collect, jsvmp, pow_answer, TM_CCOEFF_NORMED, source-report]
---

# 腾讯 TDC collect XTEA 半纯算参考

这张窄卡只整理来源 archive 对 **动态 `tdc.js` 中 collect 的 XTEA 判定、加法频率取 key、明文 4 字符小端打包，以及 cd/sd 与 eks 仍靠 jsdom 现取** 的半纯算边界。命中特征、同轮 sess/`tdc_path`/`pow_cfg` 与 `ticket/randstr` 口径仍以 [腾讯 TCaptcha 产品索引](./products/tencent-captcha.md) 为准。補环境检测点见 [vmp 上篇](./tencent-tdc-slider-vmp-part1-env-patch.md)；CHAOS_VM 与 `>>>5` 魔改 TEA 见 [vmp 下篇](./tencent-tdc-slider-vmp-part2-tea-collect-pow.md)。本文不替代产品卡，也不提供可运行 keygen。

<a id="request-chain"></a>
## 半纯算串联

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 报告称入口是 `cap_union_prehandle` 后跟栈到 `window.TDC.getData(!0)`；`tdc.js` 每次动态下发，密钥在字节码里，离线固定脚本不够。 | s1，「说在最前面」与抓包三步 | source-report | 来源所述 TCaptcha 滑块 | 未取当前 `tdc_path`。 |
| C2 | 报告把「算法纯、解题真、指纹补」拆开：XTEA/打包/取 key 本地实现，缺口 CV、轨迹、PoW 自算，`cd/sd` 与 `eks` 仍要 jsdom 跑本轮 tdc。 | s1，「密钥」节半纯算说明、`## eks` | source-report | 作者半纯算方案 | 环境不同会改变密文；不是纯离线。 |
| C3 | 报告称 `collect` 在 XTEA 密文字符串之后还要空格补齐到 8 的倍数、小端拆字节、base64、再 URL 编码才进校验体。 | s1，「collect加密参数制作」 | source-report | 来源打包链 | 不收录 quote 安全集或样值。 |
| C4 | 报告称 `eks = TDC.getInfo().info`，与 key 一样每轮现取；`ans` 只需缺口 x。 | s1，「eks」「ans」 | source-report | 来源校验字段 | 坐标参考系仍见产品卡。 |

<a id="parameters"></a>
## 字段与算法角色

分开 encryption、encoding、fingerprint、token：

| 材料 | 来源描述的角色 | 类别 | 边界 |
|---|---|---|---|
| collect 明文 | 环境+轨迹拼成的长串，切 4 字符一块 | fingerprint / encoding | 不收录明文或 `"cd"` 后的字段表。 |
| v0/v1 | 4 字符小端打包成两个 32 位字 | encoding | 第 1 字节最低 8 位。 |
| XTEA 轮体 | 内层 `((x<<4)^(x>>5))+x`，key 下标 `sum&3` 与 `(sum>>11)&3` | encryption | 标准 TEA 是分开的 `(v<<4)+k` / `(v>>5)+k`，不用 sum 现算下标。魔数仍是 `0x9E3779B9`。 |
| 密文块 | 32 轮后两字小端拆 4 字节再 `fromCharCode` 拼接 | encoding | 日志样值不收录。 |
| 动态 key | 四个 32 位字，随本轮 `tdc.js` 变 | encryption | 不收录候选值或排列结果。 |
| pow_answer | prehandle `pow_cfg` 前缀拼 nonce，直到 `md5(prefix+nonce)` 等于配置中的目标哈希 | token / PoW | 与下篇 `md5(nonce+ans)` 拼接顺序不同；不收录 prefix/md5 样值。 |
| eks | tdc 黑盒令牌，绑本轮环境 | token | 离线纯算不出来。 |

<a id="decision-flow"></a>
## 插桩、取 key 与缺口

来源把「看出算法」和「取出本轮 key」分开。检索时按下列顺序，不要从最终 collect 反推：

1. 只在 `TDC.getData` 窗口打开日志。handler 插桩：函数调用、方法调用（字符串方法白名单）、加法、载入常量碰到 delta 时点火记录位运算。
2. 用 `<<4` 与 `>>5` 直接异或再加自身、以及 `(sum>>11)&3` 判定 XTEA，而不是标准 TEA。
3. 明文路径：`slice(0,4)` 切块 → `charCodeAt` → 小端打包。油猴/包装 `slice` 只为看明文，不是发布脚本。
4. 取 key：加法两边若一侧属于 33 个合法 `i*DELTA`（0…32 轮），另一侧投票；去掉 DELTA 取频次前 4；24 种排列解密 collect，明文开头附近出现 `"cd"` 即定序。解出后按最后一个 `}` 去掉空格填充。
5. 缺口：sprite 按 alpha 抠实体，mask + `erode` 后多尺度 `TM_CCOEFF_NORMED`，搜索限制在 `track_limit`；答案 x = 命中位置减去实体相对方框的左边空白。轨迹是起点按下 + 后续 `[dx,dy,dt]`，ease-out 后写回明文模板再加密。

<a id="validation"></a>
## 验证与限制

- 产品卡的 `errorCode==0` 且 `ticket/randstr` 仍是验证码口径；本文没有服务端验收。
- 作者「没法纯算」针对动态 key 与指纹 API，不把成果图升级为本轮 runtime。
- 10 张来源图未审，不当证据。
- 不收录 Cookie、sess、key、pow 前缀/目标哈希、collect 明文/密文、jsdom 目标 URL 或可运行加解密。
- 与 [vmp 下篇](./tencent-tdc-slider-vmp-part2-tea-collect-pow.md) 的 CHAOS_VM / `>>>5` / 日志交 AI 找 key 是另一套方法，不要混成同一实现。
