---
schema_version: 2
id: web-reverse-tencent-tdc-chaos-vm-tea-pow-reference
document_type: reference
original_date: '2025-12-24'
archived_date: '2026-10-03'
scope:
  targets: [tencent-captcha]
  client: unknown
  version: unknown
  observed_at: unknown
sources:
  - id: s1
    ref: ./tencent-tdc-slider-vmp-part2-tea-collect-pow.md#reference-extraction-211
    basis: source-report
modules:
  - name: request-chain
    anchor: request-chain
    sources: [s1]
    basis: source-report
    limits: 仅整理 CHAOS_VM 出 collect 与 pow 工作量的来源顺序；未跑 tdc.js 或 cap_union。
  - name: parameters
    anchor: parameters
    sources: [s1]
    basis: source-report
    limits: 记录 VM 寄存器角色、>>>5 与 XTEA 轮下标、collect 拼接+base64、pow md5(nonce+ans)；不收录 key、明文/密文或可运行加解密。
  - name: decision-flow
    anchor: decision-flow
    sources: [s1]
    basis: source-report
    limits: apply/call 与条件加法插桩、日志交 AI 找 key 是来源方法，不是已验证实现。
  - name: validation
    anchor: validation
    sources: [s1]
    basis: source-report
    limits: 固定 tdc.js 后正逆向互验与成果图均为作者自述；本轮无 runtime、parity 或 server-accepted。
relations:
  - type: derived_from
    target: ./tencent-tdc-slider-vmp-part2-tea-collect-pow.md#reference-extraction-211
  - type: supplements
    target: ./products/tencent-captcha.md#观察优先级
  - type: supplements
    target: ./tencent-tdc-slider-vmp-part1-env-patch-reference.md#validation
tags: [TCaptcha, TDC, CHAOS_VM, TEA, XTEA, collect, pow_answer, source-report]
---

# 腾讯 TDC CHAOS_VM 魔改 TEA collect 与 pow 参考

这张窄卡只整理来源 archive 对 **`__TENCENT_CHAOS_VM` 栈式虚拟机、条件插桩还原魔改 TEA、collect 乱码拼接后 base64，以及 `pow_answer` 的 `md5(nonce+ans)` 递增爆破**。命中特征与同轮 sess/`tdc_path`/`pow_cfg` 仍以 [腾讯 TCaptcha 产品索引](./products/tencent-captcha.md) 为准。补环境检测点见 [vmp 上篇参考](./tencent-tdc-slider-vmp-part1-env-patch-reference.md)。加法频率取 key、4 字符小端打包与 collect 再 URL 编码见 [XTEA 半纯算参考](./tencent-tdc-slider-xtea-purecalc-reference.md)。本文不提供可运行加解密或 keygen。

<a id="request-chain"></a>
## 算法串联

| claim_id | 结论 | 来源与定位 | basis | 适用范围 | 限制 |
|---|---|---|---|---|---|
| C1 | 报告称 `tdc.js` 核心是 `__TENCENT_CHAOS_STACK` 内的 `__TENCENT_CHAOS_VM` 栈式虚拟机，没有其它混淆。 | s1，「VMP结构剖析」 | source-report | 来源所见 tdc.js | 未对照当前 `tdc_path`。 |
| C2 | 报告称环境串按索引取 4 个字符 `charCodeAt`，每两组运算得到 4 位数组再 `fromCharCode` 成乱码；全部乱码拼接后 **base64** 即 `collect`。 | s1，「collect 插桩分析」收尾 | source-report | 来源 collect 路径 | 与半纯算卡的「base64 后再 URL 编码」不是同一打包描述。 |
| C3 | 报告称 `pow_answer` 是 prehandle 前缀 `p` 拼接工作量答案 `d`；`pow_calc_time` 为耗时。轨迹不校验，但可在 `setData` 前写入，坐标转换后同样切割计算。 | s1，「pow参数分析」「轨迹」 | source-report | 来源 demo | 不收录前缀/答案样值。 |

<a id="parameters"></a>
## 字段与算法角色

分开 encryption、encoding、fingerprint、token：

| 材料 | 来源描述的角色 | 类别 | 边界 |
|---|---|---|---|
| Q / U / W / c | 指令指针、指令数组、指令函数表、栈 | encoding | 另有 g 全局与 M,C,X,w 状态。 |
| 4 字符分组 | 环境串按索引切 4 字符后 `charCodeAt` | fingerprint / encoding | 不收录环境对象字段表。 |
| TEA 家族轮体 | 魔数 `2654435769`；来源称标准 `>>5` 改为 `>>>5`；key 下标 `sum&3` 与 `(sum>>11)&3` | encryption | 轮结构同 XTEA；不收录可运行 `tea_encrypt`。 |
| 动态 key | 四个字，一份 `tdc.js` 一份密钥 | encryption | 不收录日志样值或 AI 给出的 key。 |
| collect | 乱码串拼接后 base64 | encoding | 不收录明文/密文。 |
| pow_answer / pow_calc_time | `p+d`；从 0 递增直到 `md5(nonce+ans)` 等于目标哈希，默认 30 秒超时 | token / PoW | 与半纯算卡 `md5(prefix+nonce)` 拼接顺序不同；不收录 nonce/目标哈希。 |

collect 不是“加密参数”统称：它是 TDC 对环境（及可选轨迹）的编码输出。

<a id="decision-flow"></a>
## 插桩与取 key

来源把「看出算法」和「取出本轮 key」分开：

1. 在 `.apply` / `.call` 与运算指令处插桩。加法日志必须加条件，否则日志爆栈。
2. 用频繁出现的 `2654435769` 判定 TEA 家族；实测魔改是 `>>5` → `>>>5`。
3. 取 key 两条路：按算法逻辑读日志，或把日志片段交给 DeepSeek 深度思考。作者未公开自动提取。
4. 固定本轮 `tdc.js` 后用正向/逆向互验 collect。密钥随脚本变，离线固定旧脚本不够。
5. PoW：搜索 workload 字段，进入 `getWorkloadResult`；答案从 0 递增。

不要把本卡的 AI-from-logs 与半纯算卡的加法频率投票混成同一实现。

<a id="validation"></a>
## 验证与限制

- 产品卡的 `errorCode==0` 且 `ticket/randstr` 仍是验证码口径；本文没有服务端验收。
- 作者「加解密都 ok」只覆盖固定 `tdc.js` 的自述互验。
- 34 张来源图未审，不当证据。
- 不收录 Cookie、sess、key、collect 明文/密文、pow 前缀/目标哈希、可运行加解密或公众号长链。
- 轨迹「可不校验」是作者对 demo 的观察，不外推当前服务端。
